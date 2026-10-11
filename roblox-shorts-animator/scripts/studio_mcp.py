"""Minimal stdio client for Roblox Studio's built-in MCP server (StudioMCP.exe).

Lets scripts (or Claude through Bash) call Studio tools without the MCP client being loaded
in the current Claude session:

  python studio_mcp.py tools
  python studio_mcp.py call list_roblox_studios
  python studio_mcp.py call execute_luau --json '{"code": "print(1+1)"}'
  python studio_mcp.py luau arquivo.lua [--contexto edit|client|server]
  python studio_mcp.py capture saida.png

The Studio id is filled in automatically when a tool asks for `studio_id`.
"""
import argparse, base64, json, os, subprocess, sys, threading, queue
from pathlib import Path

BAT = Path(os.environ.get('LOCALAPPDATA', '')) / 'Roblox' / 'mcp.bat'


def studio_mcp_exe():
    """StudioMCP.exe of the installed Studio (the path mcp.bat points to)."""
    import re
    if BAT.exists():
        for path in re.findall(r'"([^"]+StudioMCP\.exe)"', BAT.read_text(errors='replace')):
            if Path(path).exists():
                return path
    versions = sorted((Path(os.environ.get('LOCALAPPDATA', '')) / 'Roblox' / 'Versions').glob('*/StudioMCP.exe'),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    if not versions:
        raise SystemExit('StudioMCP.exe nao encontrado: atualize o Roblox Studio.')
    return str(versions[0])


class Client:
    def __init__(self):
        self.p = subprocess.Popen([studio_mcp_exe()], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, bufsize=0)
        self.q = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        self.n = 0
        self.call_raw('initialize', {'protocolVersion': '2025-06-18', 'capabilities': {},
                                     'clientInfo': {'name': 'roblox-shorts-animator', 'version': '1.0'}})
        self._send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        self._tools = None
        self._studio = None

    def _reader(self):
        for line in self.p.stdout:
            line = line.strip()
            if line:
                try:
                    self.q.put(json.loads(line))
                except json.JSONDecodeError:
                    pass

    def _send(self, msg):
        self.p.stdin.write((json.dumps(msg) + '\n').encode())
        self.p.stdin.flush()

    def call_raw(self, method, params, timeout=180):
        self.n += 1
        mid = self.n
        self._send({'jsonrpc': '2.0', 'id': mid, 'method': method, 'params': params})
        while True:
            msg = self.q.get(timeout=timeout)
            if msg.get('id') == mid:
                if 'error' in msg:
                    raise RuntimeError(json.dumps(msg['error'], ensure_ascii=False))
                return msg['result']

    def tools(self):
        if self._tools is None:
            self._tools = {t['name']: t for t in self.call_raw('tools/list', {})['tools']}
            if not self._tools:
                raise SystemExit('O Studio nao esta conectado ao MCP. No Studio: Assistant > ... > Manage MCP Servers > '
                                 'ligue "Enable Studio as MCP server".')
        return self._tools

    def studio_id(self):
        if self._studio is None:
            res = self.call_raw('tools/call', {'name': 'list_roblox_studios', 'arguments': {}})
            text = ''.join(c.get('text', '') for c in res.get('content', []))
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = text
            ids = []
            if isinstance(data, list):
                ids = [d.get('studio_id') or d.get('id') for d in data if isinstance(d, dict)]
            elif isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        ids += [d.get('studio_id') or d.get('id') for d in v if isinstance(d, dict)]
            ids = [i for i in ids if i]
            if not ids:
                raise RuntimeError('Nenhum Studio conectado ao MCP: ' + text[:500])
            self._studio = ids[0]
        return self._studio

    def call(self, name, args=None, timeout=300):
        args = dict(args or {})
        schema = self.tools().get(name, {}).get('inputSchema', {})
        if 'studio_id' in schema.get('properties', {}) and 'studio_id' not in args:
            args['studio_id'] = self.studio_id()
        return self.call_raw('tools/call', {'name': name, 'arguments': args}, timeout)

    def close(self):
        try:
            self.p.stdin.close()
            self.p.terminate()
        except OSError:
            pass


def show(res, image_out=None):
    for c in res.get('content', []):
        if c.get('type') == 'text':
            print(c['text'])
        elif c.get('type') == 'image':
            path = Path(image_out or 'captura.png')
            path.write_bytes(base64.b64decode(c['data']))
            print('imagem salva em', path)
    if res.get('isError'):
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('tools')
    c = sub.add_parser('call'); c.add_argument('nome'); c.add_argument('--json', default='{}'); c.add_argument('--imagem')
    l = sub.add_parser('luau'); l.add_argument('arquivo', type=Path); l.add_argument('--contexto', default=None)
    s = sub.add_parser('capture'); s.add_argument('saida', type=Path); s.add_argument('--json', default='{}')
    a = ap.parse_args()
    cli = Client()
    try:
        if a.cmd == 'tools':
            for name, t in cli.tools().items():
                print(f'- {name}: {t.get("description", "")[:160]}')
                print('    args:', json.dumps(t.get('inputSchema', {}).get('properties', {}), ensure_ascii=False)[:400])
        elif a.cmd == 'call':
            show(cli.call(a.nome, json.loads(a.json)), a.imagem)
        elif a.cmd == 'luau':
            args = {'code': a.arquivo.read_text(encoding='utf-8')}
            props = cli.tools()['execute_luau'].get('inputSchema', {}).get('properties', {})
            if a.contexto:
                key = next((k for k in props if k in ('context', 'datamodel', 'data_model', 'target')), 'context')
                args[key] = a.contexto
            show(cli.call('execute_luau', args))
        elif a.cmd == 'capture':
            show(cli.call('screen_capture', json.loads(a.json)), a.saida)
    finally:
        cli.close()


if __name__ == '__main__':
    main()
