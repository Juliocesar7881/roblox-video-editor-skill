"""Entrega os MP4 do lote ao YouTube Studio aberto no Chrome do usuário, sem limite de tamanho.

  python servidor_envio.py LOTE [--porta 8768]

A ferramenta de upload do navegador só aceita arquivos de até 10 MB e os Shorts têm 20–45 MB. Este servidor
escuta só em 127.0.0.1 e só responde à origem https://studio.youtube.com (CORS + Private Network Access), com os
MP4 finais listados na agenda.json do lote: GET /video/NN devolve o MP4 do vídeo NN. Na janela de envio do Studio,
o JavaScript de references/youtube-studio.md busca o arquivo daqui e o coloca no campo de arquivo (DataTransfer).
Nada sai do computador por este servidor: quem envia para o YouTube é o próprio Studio, na conta do usuário.
"""
import argparse, http.server, json, socketserver
from pathlib import Path

ORIGEM = 'https://studio.youtube.com'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lote')
    ap.add_argument('--porta', type=int, default=8768)
    a = ap.parse_args()
    lote = Path(a.lote).resolve()
    agenda = json.loads((lote / 'agenda.json').read_text(encoding='utf-8'))
    videos = {it['n']: Path(it['video']) for it in agenda['itens']}
    # Metadados de cada vídeo para preencher o formulário do Studio direto da agenda (sem digitar à mão).
    metas = {it['n']: {k: it[k] for k in ('titulo', 'descricao', 'tags', 'data_studio', 'hora_studio')} | {'arquivo': Path(it['video']).name}
             for it in agenda['itens']}

    class Handler(http.server.BaseHTTPRequestHandler):
        def _cors(self):
            if self.headers.get('Origin') == ORIGEM:
                self.send_header('Access-Control-Allow-Origin', ORIGEM)
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                self.send_header('Vary', 'Origin')

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            partes = self.path.strip('/').split('/')
            if partes == ['ping']:
                corpo = b'ok'
                tipo = 'text/plain'
            elif len(partes) == 2 and partes[0] == 'meta' and partes[1] in metas:
                corpo = json.dumps(metas[partes[1]], ensure_ascii=False).encode('utf-8')
                tipo = 'application/json; charset=utf-8'
            elif len(partes) == 2 and partes[0] == 'video' and partes[1] in videos and videos[partes[1]].exists():
                corpo = videos[partes[1]].read_bytes()
                tipo = 'video/mp4'
            else:
                self.send_response(404)
                self._cors()
                self.end_headers()
                return
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', tipo)
            self.send_header('Content-Length', str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def log_message(self, fmt, *args):
            print('[envio]', fmt % args, flush=True)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', a.porta), Handler) as srv:
        print(f'servindo {len(videos)} vídeos de {lote.name} em http://127.0.0.1:{a.porta}/video/NN (só para {ORIGEM})', flush=True)
        srv.serve_forever()


if __name__ == '__main__':
    main()
