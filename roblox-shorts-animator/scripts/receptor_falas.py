"""Receptor local: a aba do ElevenLabs abre http://127.0.0.1:PORTA/receber.html e manda os audios por
postMessage; a pagina (mesma origem do servidor) faz POST /salvar e o arquivo vai para PASTA.
Escuta so em 127.0.0.1. Uso: python receptor2.py PASTA [porta]"""
import re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PASTA = Path(sys.argv[1])
PORTA = int(sys.argv[2]) if len(sys.argv) > 2 else 8766
PASTA.mkdir(parents=True, exist_ok=True)

PAGINA = b"""<!doctype html><meta charset="utf-8"><title>Receptor de falas</title>
<body style="font:20px sans-serif;padding:30px"><h2>Receptor de falas (local)</h2><pre id="log"></pre>
<script>
const log = m => document.getElementById('log').textContent += m + '\\n';
window.addEventListener('message', async ev => {
  if (ev.origin !== 'https://elevenlabs.io') return;
  const {nome, blob} = ev.data || {};
  if (!nome || !(blob instanceof Blob)) return;
  const r = await fetch('/salvar?nome=' + encodeURIComponent(nome), {method: 'POST', body: blob});
  log(nome + ' ' + blob.size + ' bytes: ' + (r.ok ? 'salvo' : 'erro'));
  ev.source && ev.source.postMessage({salvo: nome, ok: r.ok}, ev.origin);
});
log('pronto');
if (window.opener) window.opener.postMessage({receptorPronto: true}, 'https://elevenlabs.io');
</script>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path != '/receber.html':
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(PAGINA)

    def do_POST(self):
        nome = parse_qs(urlparse(self.path).query).get('nome', [''])[0]
        if urlparse(self.path).path != '/salvar' or not re.fullmatch(r'[\w\-]+\.mp3', nome):
            self.send_response(400); self.end_headers(); return
        dados = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        (PASTA / nome).write_bytes(dados)
        print('salvo', nome, len(dados), flush=True)
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok')

    def log_message(self, *a):
        pass


HTTPServer(('127.0.0.1', PORTA), H).serve_forever()
