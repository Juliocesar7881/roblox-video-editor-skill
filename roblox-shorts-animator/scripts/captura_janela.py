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
        self.ff = subprocess.Popen([ff, '-hide_banner', '-v', 'error', '-y',
                                    '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{w}x{h}',
                                    '-use_wallclock_as_timestamps', '1', '-i', '-',
                                    '-fps_mode', 'cfr', '-r', str(self.fps), *enc, '-pix_fmt', 'yuv420p',
                                    str(self.saida)], stdin=subprocess.PIPE)
        threading.Thread(target=self._escritor, daemon=True).start()

    def _escritor(self):
        while True:
            item = self.q.get()
            if item is None:
                break
            try:
                self.ff.stdin.write(memoryview(item))
                self.escritos += 1
            except OSError:
                break

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
        if not self.flash2_visto and agora - self.t_flash1 > 2.0 and magenta_mask(crop[::10, ::10]).mean() > 0.6:
            self.flash2_visto = True
            self.t_flash2 = agora
            self.log(f'flash final em {agora - self.t_flash1:.2f}s')
            threading.Timer(0.6, self.fim.set).start()
        try:
            # The capture buffer is reused after this callback: always copy.
            self.q.put_nowait(np.array(crop, copy=True, order='C'))
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
            time.sleep(0.2)
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


def processar(viewport_mp4, saida, atraso, duracao, largura=1080, fps=60, deitada=True, margem_topo=0.075):
    """viewport (camera deitada) -> clipe vertical 9:16 a partir do t=0 da timeline.
    margem_topo: faixa de cima do viewport com os botoes do Roblox (logo e menu), que nao podem ser
    escondidos no jogo; e cortada antes de virar o video."""
    from media_utils import probe
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
