"""Alternativa ao YouTube Studio: envia e agenda o lote pela YouTube Data API v3 (só se o usuário pedir).

  python youtube_api.py conectar pt|es        o PRÓPRIO usuário faz o login no navegador (um token por canal)
  python youtube_api.py agendar LOTE [--canal pt|es]   envia cada item 'pendente' de agenda.json

Requer credentials/client_secret.json (projeto do usuário no Google Cloud, OAuth "App para computador")
e pip install google-api-python-client google-auth-oauthlib. Projetos não verificados pelo Google
têm os envios travados como privados até passarem na auditoria: avise o usuário.
Agendamento: privacyStatus "private" + publishAt (UTC); o YouTube publica sozinho no horário.
"""
import argparse, datetime as dt, json, sys, time
from pathlib import Path

CRED = Path(__file__).resolve().parent.parent / 'credentials'
ESCOPOS = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']
CATEGORIA = {'Entretenimento': '24', 'Jogos': '20', 'Educação': '27'}


def servico(canal):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    tok = CRED / f'token-{canal}.json'
    if not tok.exists():
        raise SystemExit(f'sem {tok.name}: rode "python youtube_api.py conectar {canal}" (o usuário faz o login)')
    cr = Credentials.from_authorized_user_file(str(tok), ESCOPOS)
    if not cr.valid:
        cr.refresh(Request())
        tok.write_text(cr.to_json(), encoding='utf-8')
    return build('youtube', 'v3', credentials=cr)


def conectar(a):
    from google_auth_oauthlib.flow import InstalledAppFlow
    seg = CRED / 'client_secret.json'
    if not seg.exists():
        raise SystemExit(f'coloque o client_secret.json do Google Cloud em {seg}')
    cr = InstalledAppFlow.from_client_secrets_file(str(seg), ESCOPOS).run_local_server(port=0)
    (CRED / f'token-{a.canal}.json').write_text(cr.to_json(), encoding='utf-8')
    canal = servico(a.canal).channels().list(part='snippet', mine=True).execute()['items'][0]['snippet']['title']
    print(f'conectado ao canal "{canal}" para {a.canal}')


def agendar(a):
    from googleapiclient.http import MediaFileUpload
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import lote
    c = lote.config()
    pasta = Path(a.lote).resolve()
    agenda = json.loads((pasta / 'agenda.json').read_text(encoding='utf-8'))
    for canal, itens in agenda['canais'].items():
        if a.canal and canal != a.canal:
            continue
        yt = servico(canal)
        for it in itens:
            if it['status'] == 'agendado':
                continue
            quando = dt.datetime.fromisoformat(it['publish_at']).astimezone(dt.timezone.utc)
            corpo = {'snippet': {'title': it['titulo'], 'description': it['descricao'], 'tags': it['tags'],
                                 'categoryId': CATEGORIA.get(c['categoria'], '24'), 'defaultLanguage': canal,
                                 'defaultAudioLanguage': canal},
                     'status': {'privacyStatus': 'private', 'publishAt': quando.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                'selfDeclaredMadeForKids': c['feito_para_criancas']}}
            try:
                req = yt.videos().insert(part='snippet,status', body=corpo,
                                         media_body=MediaFileUpload(it['video'], mimetype='video/mp4', resumable=True))
                resp = None
                while resp is None:
                    _, resp = req.next_chunk()
                it['status'], it['link'] = 'agendado', f'https://youtube.com/shorts/{resp["id"]}'
            except Exception as e:  # segue para o próximo e relata no fim
                it['status'], it['erro'] = 'erro', str(e)[:300]
            (pasta / 'agenda.json').write_text(json.dumps(agenda, ensure_ascii=False, indent=1), encoding='utf-8')
            print(canal, it['n'], it['quando'], it['status'], it.get('link') or it.get('erro'))
            time.sleep(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('conectar'); s.add_argument('canal', choices=['pt', 'es'])
    s = sub.add_parser('agendar'); s.add_argument('lote'); s.add_argument('--canal', choices=['pt', 'es'])
    a = ap.parse_args()
    CRED.mkdir(exist_ok=True)
    {'conectar': conectar, 'agendar': agendar}[a.cmd](a)


if __name__ == '__main__':
    main()
