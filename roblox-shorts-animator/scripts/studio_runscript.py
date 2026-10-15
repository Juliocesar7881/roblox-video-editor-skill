"""Run a Luau pipeline in a fresh Roblox Studio window (official `-task RunScript`) and record it.

No MCP or clicks needed: Studio opens the local place, runs the script in edit mode with
command-bar permissions, the script can start Play mode (StudioTestService:ExecutePlayModeAsync),
and `-quitAfterExecution` closes that Studio window when the script returns. The user's other
Studio windows are left alone.

  python studio_runscript.py montar --kit --cenario cenario.lua --cena cena.lua --saida pipeline.lua [--play]
  python studio_runscript.py rodar pipeline.lua --place base.rbxlx [--gravar bruto.mp4] [--max 240]
"""
import argparse, ctypes, os, re, subprocess, sys, threading, time
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'roblox-video-editor' / 'scripts'))
from media_utils import ffmpeg  # noqa: E402,F401

KIT = Path(__file__).resolve().parents[1] / 'luau' / 'AnimKit.lua'


def studio_exe():
    bat = Path(os.environ.get('LOCALAPPDATA', '')) / 'Roblox' / 'mcp.bat'
    if bat.exists():
        for path in re.findall(r'"([^"]+)StudioMCP\.exe"', bat.read_text(errors='replace')):
            exe = Path(path) / 'RobloxStudioBeta.exe'
            if exe.exists():
                return exe
    found = sorted((Path(os.environ.get('LOCALAPPDATA', '')) / 'Roblox' / 'Versions').glob('*/RobloxStudioBeta.exe'),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    if not found:
        raise SystemExit('Roblox Studio nao encontrado.')
    return found[0]


def long_string(text):
    n = 1
    while ']' + '=' * n + ']' in text:
        n += 1
    return f'[{"=" * n}[\n{text}]{"=" * n}]'


def set_source(parent_expr, cls, name, source):
    return f'''do
	local parent = {parent_expr}
	local s = parent:FindFirstChild("{name}")
	if s then s:Destroy() end
	s = Instance.new("{cls}")
	s.Name = "{name}"
	s.Source = {long_string(source)}
	s.Parent = parent
	print("[pipeline] {name} instalado")
end
'''


SERVIDOR = '''local STS = game:GetService("StudioTestService")
local ev = game:GetService("ReplicatedStorage"):WaitForChild("AnimKitFim")
local terminou = false
ev.OnServerEvent:Connect(function(_, msg)
	if terminou then return end
	terminou = true
	print("[pipeline] cena terminou:", msg)
	task.wait(0.3)
	STS:EndTest(msg or "ok")
end)
task.delay(%d, function()
	if not terminou then
		terminou = true
		warn("[pipeline] tempo esgotado")
		STS:EndTest("timeout")
	end
end)
'''


def montar(a):
    parts = ['-- Pipeline gerado por studio_runscript.py montar\nprint("[pipeline] inicio")\n']
    if a.kit:
        parts.append(set_source('game:GetService("ReplicatedStorage")', 'ModuleScript', 'AnimKit', KIT.read_text(encoding='utf-8')))
    if a.cenario:
        parts.append('do\n' + a.cenario.read_text(encoding='utf-8') + '\nend\nprint("[pipeline] cenario montado")\n')
    if a.cena:
        parts.append(set_source('game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")', 'LocalScript', 'Cena',
                                a.cena.read_text(encoding='utf-8')))
    if a.play:
        parts.append('''do
	local RS = game:GetService("ReplicatedStorage")
	local old = RS:FindFirstChild("AnimKitFim")
	if old then old:Destroy() end
	local ev = Instance.new("RemoteEvent")
	ev.Name = "AnimKitFim"
	ev.Parent = RS
end
''')
        parts.append(set_source('game:GetService("ServerScriptService")', 'Script', 'AnimKitServidor', SERVIDOR % a.timeout))
        parts.append('''print("[pipeline] iniciando play")
-- Starting Play right after the place opens can end the test at once; wait and retry.
task.wait(4)
for tentativa = 1, 3 do
	local t0 = os.clock()
	local ok, res = pcall(function() return game:GetService("StudioTestService"):ExecutePlayModeAsync({}) end)
	print(string.format("[pipeline] play terminou (tentativa %d, %.1fs):", tentativa, os.clock() - t0), ok, res)
	if res ~= nil or os.clock() - t0 > 8 then break end
	task.wait(3)
end
''')
    parts.append('print("[pipeline] fim")\n')
    a.saida.write_text('\n'.join(parts), encoding='utf-8')
    print('pipeline:', a.saida, f'{a.saida.stat().st_size} bytes')


# --- Windows helpers: keep the recorded Studio window maximized and on top ---------------------
user32 = ctypes.windll.user32 if sys.platform == 'win32' else None


def windows_of(pid):
    found = []
    if not user32:
        return found
    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def cb(hwnd, _):
        p = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            area = (rect.right - rect.left) * (rect.bottom - rect.top)
            found.append((area, hwnd, buf.value))
        return True
    user32.EnumWindows(proc(cb), 0)
    return sorted(found, reverse=True)


def studio_window(pid, timeout=60):
    """Main Studio window of this process (largest visible 'Roblox Studio' window)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        for area, hwnd, title in windows_of(pid):
            if 'Roblox Studio' in title and area > 600_000:
                return hwnd, title
        time.sleep(0.25)
    return None, None


def mandar_para_tras(hwnd):
    """Keep the recording Studio behind the user's windows (capture works while covered)."""
    if not user32:
        return
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    HWND_BOTTOM = wintypes.HWND(1)
    user32.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)  # NOSIZE|NOMOVE|NOACTIVATE


def rodar(a):
    exe = studio_exe()
    out_log = a.pipeline.with_suffix('.saida.log')
    if out_log.exists():
        out_log.unlink()
    log = lambda m: print(f'[{time.strftime("%H:%M:%S")}] {m}', flush=True)
    if user32:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # pixels reais
    args = [str(exe), '-task', 'RunScript', '-localPlaceFile', str(a.place.resolve()),
            '-runScriptFile', str(a.pipeline.resolve()), '-outputFile', str(out_log.resolve()), '-quitAfterExecution']
    t0 = time.time()
    # Capture stdout/stderr directly instead of relying on -outputFile which may not work
    studio = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              encoding='utf-8', errors='replace', bufsize=1)
    log(f'Studio iniciado (pid {studio.pid})')
    meta = None

    # Start reading output in background thread
    import threading
    output_lines = []
    def read_output():
        for line in studio.stdout:
            output_lines.append(line.rstrip())
            # Print important lines immediately
            if any(k in line for k in ['[pipeline]', '[auditoria]', '[camera]', 'error', 'Error', 'warn']):
                print(line.rstrip(), flush=True)

    reader_thread = threading.Thread(target=read_output, daemon=True)
    reader_thread.start()

    if a.gravar:
        from captura_janela import Gravador
        hwnd, title = studio_window(studio.pid)
        if not hwnd:
            log('janela do Studio nao apareceu; sem gravacao')
        else:
            log(f'gravando somente a janela "{title}"')
            if a.atras:
                time.sleep(1.5)
                mandar_para_tras(hwnd)
            g = Gravador(hwnd, a.gravar, fps=a.fps, log=log)
            # Passa duração esperada da cena para guarda temporal do flash2
            try:
                import json, re
                pipeline_text = a.pipeline.read_text(encoding='utf-8')
                m = re.search(r'K\.rodar\([^,]+,\s*([\d.]+)\)', pipeline_text)
                if m:
                    g.duracao_esperada = float(m.group(1))
                    log(f'duracao_esperada={g.duracao_esperada:.1f}s para guarda temporal')
            except Exception as e:
                log(f'aviso: nao foi possivel extrair duracao_esperada: {e}')
            meta = g.gravar(timeout=a.max)
            log(f'gravacao: {meta}')
            if g.t_flash1 is None and studio.poll() is None:
                # O Play nao comecou (sem flash inicial): nao adianta esperar mais; quem chamou tenta de novo.
                log('sem flash inicial: o Play nao comecou; fechando o Studio desta gravacao')
                studio.kill()
    try:
        studio.wait(timeout=a.max)
    except subprocess.TimeoutExpired:
        log('tempo maximo atingido; fechando o Studio desta gravacao')
        studio.kill()

    # Wait for reader thread to finish
    reader_thread.join(timeout=2)

    log(f'Studio terminou em {time.time() - t0:.1f}s (codigo {studio.returncode})')

    # Print captured output
    if output_lines:
        print('\n'.join(output_lines), flush=True)
    elif out_log.exists():
        # Fallback to file if stdout capture failed
        text = out_log.read_text(encoding='utf-8', errors='replace')
        tail = a.pipeline.read_text(encoding='utf-8').rstrip()[-120:]
        print(text.split(tail, 1)[-1].strip() if tail in text else text)
    else:
        print('(sem output capturado do Studio)')

    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    m = sub.add_parser('montar')
    m.add_argument('--kit', action='store_true')
    m.add_argument('--cenario', type=Path)
    m.add_argument('--cena', type=Path)
    m.add_argument('--play', action='store_true')
    m.add_argument('--timeout', type=int, default=120, help='segundos maximos do play antes de encerrar')
    m.add_argument('--saida', type=Path, required=True)
    r = sub.add_parser('rodar')
    r.add_argument('pipeline', type=Path)
    r.add_argument('--place', type=Path, required=True)
    r.add_argument('--gravar', type=Path)
    r.add_argument('--fps', type=int, default=60)
    r.add_argument('--max', type=int, default=240)
    r.add_argument('--frente', dest='atras', action='store_false', help='nao manda o Studio para tras das outras janelas')
    a = ap.parse_args()
    {'montar': montar, 'rodar': rodar}[a.cmd](a)


if __name__ == '__main__':
    main()
