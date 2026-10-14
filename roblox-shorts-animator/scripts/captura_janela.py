"""Record only one window (Windows Graphics Capture) between the AnimKit's two magenta flashes.

Nothing else on the screen is captured, and the window may sit behind other windows. The first
flash gives the viewport rectangle and t=0; frames are cropped to that viewport and streamed to
FFmpeg with wall-clock timestamps; the second flash marks the end.
"""
import json, queue, subprocess, sys, threading, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'roblox-video-editor' / 'scripts'))
from media_utils import ffmpeg  # noqa: E402


def magenta_mask(bgra):
    b, g, r = bgra[..., 0], bgra[..., 1], bgra[..., 2]
    return (r > 215) & (g < 60) & (b > 215)


class Gravador:
    def __init__(self, hwnd, saida, fps=60, log=print):
        self.hwnd, self.saida, self.fps, self.log = hwnd, Path(saida), fps, log
        self.regiao = None
        self.t_flash1 = self.t_flash2 = None
        self.recebidos = self.escritos = self.descartados = 0
        self.q = queue.Queue(maxsize=4)
        self.ff = None
        self.fim = threading.Event()
        self.flash2_visto = False

    # -- FFmpeg -------------------------------------------------------------------------------
    def _abrir_ffmpeg(self, w, h):
        enc = ['-c:v', 'h264_nvenc', '-preset', 'p6', '-tune', 'hq', '-rc', 'vbr', '-cq', '15', '-b:v', '0']
        ff = ffmpeg()
        if 'h264_nvenc' not in subprocess.run([ff, '-hide_banner', '-encoders'], capture_output=True, text=True).stdout:
            enc = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14']
        # Taxa fixa com o tempo de CAPTURA de cada quadro (ver _escritor). Antes o FFmpeg carimbava o
        # tempo na hora em que lia o pipe (-use_wallclock_as_timestamps): os quadros que chegavam
        # enquanto ele abria ficavam espremidos e o video saia ~0,14 s adiantado em relacao ao flash
        # (boca abrindo antes da voz, efeitos atrasados).
        self.ff = subprocess.Popen([ff, '-hide_banner', '-v', 'error', '-y',
                                    '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{w}x{h}', '-r', str(self.fps),
                                    '-i', '-', *enc, '-pix_fmt', 'yuv420p', str(self.saida)], stdin=subprocess.PIPE)
        self.escritor = threading.Thread(target=self._escritor, daemon=True)
        self.escritor.start()

    def _escritor(self):
        # Reamostra para taxa fixa: o quadro de saida k (t0 + k/fps, t0 = quadro do flash) mostra o
        # ultimo quadro capturado ate esse instante; quadros que faltaram viram repeticao do anterior.
        passo = 1.0 / self.fps
        ultimo = proximo = None
        while True:
            item = self.q.get()
            if item is None:
                break
            t, quadro = item
            try:
                if ultimo is None:
                    proximo = t
                else:
                    while proximo < t:
                        self.ff.stdin.write(memoryview(ultimo))
                        self.escritos += 1
                        proximo += passo
                ultimo = quadro
            except OSError:
                return
        if ultimo is not None:
            try:
                self.ff.stdin.write(memoryview(ultimo))
                self.escritos += 1
            except OSError:
                pass

    # -- Captura ------------------------------------------------------------------------------
    def _quadro(self, buf):
        agora = time.perf_counter()
        self.recebidos += 1
        if self.regiao is None:
            small = buf[::12, ::12]
            m = magenta_mask(small)
            if m.mean() > 0.12:
                ys, xs = np.nonzero(m)
                y0, y1 = max(0, ys.min() * 12 - 12), min(buf.shape[0], ys.max() * 12 + 24)
                x0, x1 = max(0, xs.min() * 12 - 12), min(buf.shape[1], xs.max() * 12 + 24)
                full = magenta_mask(buf[y0:y1, x0:x1])
                fy, fx = np.nonzero(full)
                y0, y1, x0, x1 = y0 + fy.min(), y0 + fy.max() + 1, x0 + fx.min(), x0 + fx.max() + 1
                # Inset 2 px against anti-aliased borders; even sizes for the encoder.
                x0 += 2; y0 += 2; x1 -= 2; y1 -= 2
                x1 = x0 + (x1 - x0) // 2 * 2
                y1 = y0 + (y1 - y0) // 2 * 2
                self.regiao = tuple(int(v) for v in (x0, y0, x1, y1))
                self.t_flash1 = agora
                self.log(f'flash inicial: viewport {x1 - x0}x{y1 - y0} em ({x0},{y0})')
                self._abrir_ffmpeg(x1 - x0, y1 - y0)
            else:
                return
        x0, y0, x1, y1 = self.regiao
        if buf.shape[0] < y1 or buf.shape[1] < x1:
            return  # janela redimensionada no meio da gravacao: ignora o quadro
        crop = buf[y0:y1, x0:x1]
        # Guarda temporal: ignora magenta antes de 80% da duração esperada para evitar
        # falso positivo com objetos magenta do cenário (ex: poção perto da câmera).
        duracao_esperada = getattr(self, 'duracao_esperada', None)
        tempo_minimo = (duracao_esperada * 0.8) if duracao_esperada else 2.0
        if not self.flash2_visto and agora - self.t_flash1 > tempo_minimo and magenta_mask(crop[::10, ::10]).mean() > 0.6:
            self.flash2_visto = True
            self.t_flash2 = agora
            self.log(f'flash final em {agora - self.t_flash1:.2f}s')
            threading.Timer(0.6, self.fim.set).start()
        try:
            # The capture buffer is reused after this callback: always copy.
            self.q.put_nowait((agora, np.array(crop, copy=True, order='C')))
        except queue.Full:
            self.descartados += 1

    def gravar(self, timeout):
        from windows_capture import WindowsCapture
        cap = WindowsCapture(cursor_capture=False, draw_border=False, window_hwnd=self.hwnd,
                             minimum_update_interval=max(1, int(1000 / self.fps) - 2))

        @cap.event
        def on_frame_arrived(frame, control):
            if self.fim.is_set():
                control.stop()
                return
            self._quadro(frame.frame_buffer)

        @cap.event
        def on_closed():
            self.fim.set()

        ctrl = cap.start_free_threaded()
        self.fim.wait(timeout)
        try:
            ctrl.stop()
        except Exception:
            pass
        if self.ff:
            self.q.put(None)
            self.escritor.join(timeout=60)
            try:
                self.ff.stdin.close()
            except OSError:
                pass
            self.ff.wait(timeout=120)
        meta = {'saida': str(self.saida), 'regiao': self.regiao, 'recebidos': self.recebidos,
                'escritos': self.escritos, 'descartados': self.descartados,
                'duracao_cena': round(self.t_flash2 - self.t_flash1, 3) if self.t_flash2 else None}
        self.saida.with_suffix('.json').write_text(json.dumps(meta, indent=1), encoding='utf-8')
        return meta


def latencia_medida(viewport_mp4, atraso, duracao):
    """Atraso do Roblox entre agendar algo e o quadro aparecer (camera, rosto, flash), medido pelo flash
    final: ele e agendado em t0 + duracao e o gravador anota quando ele chegou. Compensar isso poe os
    cortes e a boca no quadro planejado (sem isso ficavam ~3 quadros atrasados)."""
    meta = Path(viewport_mp4).with_suffix('.json')
    try:
        real = json.loads(meta.read_text(encoding='utf-8'))['duracao_cena']
    except (OSError, KeyError, ValueError, TypeError):
        return 0.0
    if real is None:
        return 0.0
    return min(0.2, max(-0.1, real - (atraso + duracao)))


def medir_sincronia(viewport_mp4, atraso, duracao, intervalo=5.0, primeira=0.5):
    """Atraso real entre o Roblox agendar algo e o quadro aparecer, medido pelas marcas magenta que o
    K.rodar acende no alto do viewport (faixa cortada no video final) em t = 0,5; 5,5; 10,5... da
    timeline. Devolve a mediana (segundos) ou None se a gravacao nao tiver marcas."""
    from media_utils import probe
    info = probe(viewport_mp4)
    w = info['width']
    taxa = info.get('fps') or 60
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', str(viewport_mp4), '-vf',
                          f'crop=120:8:{(w - 120) // 2}:4,scale=12:2', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True).stdout
    q = np.frombuffer(raw, np.uint8)
    if not len(q):
        return None
    q = q.reshape(-1, 2, 12, 3).astype(int)
    acesa = ((q[..., 0] > 170) & (q[..., 1] < 100) & (q[..., 2] > 170)).mean(axis=(1, 2)) > 0.6
    inicios = [i / taxa for i in range(1, len(acesa)) if acesa[i] and not acesa[i - 1]]
    atrasos = []
    t = primeira
    while t < duracao - 0.2:
        esperado = atraso + t
        perto = [x for x in inicios if abs(x - esperado) < 0.3]
        if perto:
            atrasos.append(min(perto, key=lambda x: abs(x - esperado)) - esperado)
        t += intervalo
    if len(atrasos) < 2:
        return None
    return float(np.median(atrasos))


def processar(viewport_mp4, saida, atraso, duracao, largura=1080, fps=60, deitada=True, margem_topo=0.075,
              compensar=True):
    """viewport (camera deitada) -> clipe vertical 9:16 a partir do t=0 da timeline.
    margem_topo: faixa de cima do viewport com os botoes do Roblox (logo e menu), que nao podem ser
    escondidos no jogo; e cortada antes de virar o video. compensar: soma ao atraso a latencia medida
    pelas marcas de sincronia (medir_sincronia) ou, sem marcas, pelo flash final (latencia_medida)."""
    from media_utils import probe
    if compensar:
        lat = medir_sincronia(viewport_mp4, atraso, duracao)
        if lat is None:
            lat = latencia_medida(viewport_mp4, atraso, duracao)
        atraso += min(0.2, max(-0.1, lat))
    info = probe(viewport_mp4)
    w, h = info['width'], info['height']
    corte = int(h * margem_topo) // 2 * 2
    vf = [f'crop={w}:{h - corte}:0:{corte}'] if corte else []
    h -= corte
    if deitada:
        vf.append('transpose=2')
        w, h = h, w
    tw, th = (w, round(w * 16 / 9 / 2) * 2) if h * 9 >= w * 16 else (round(h * 9 / 16 / 2) * 2, h)
    vf += [f'crop={tw}:{th}', f'scale={largura}:{round(largura * 16 / 9 / 2) * 2}:flags=lanczos', f'fps={fps}', 'setsar=1', 'format=yuv420p']
    subprocess.run([ffmpeg(), '-hide_banner', '-v', 'error', '-y', '-ss', f'{atraso:.3f}', '-i', str(viewport_mp4),
                    '-t', f'{duracao:.3f}', '-vf', ','.join(vf), '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '14',
                    str(saida)], check=True)
