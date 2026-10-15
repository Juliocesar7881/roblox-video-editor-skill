"""Lote de Shorts de Roblox: 7 vídeos inéditos em português, SEO do YouTube e agenda no canal BRUNOBLOX.

  python lote.py novo [--data AAAA-MM-DD]          cria entregas/lote-AAAAMMDD com 7 projetos vazios
  python lote.py historico                        registro de roteiros + premissas em entregas/ (originalidade)
  python lote.py produzir LOTE [--so N ...]        roda fazer_short.py em cada projeto e anota o roteiro no registro
  python lote.py registrar LOTE                   anota no registro da skill os roteiros produzidos do lote
  python lote.py metadados LOTE                   publicacao.json / publicacao.txt validados para o YouTube
  python lote.py painel LOTE                      revisao.html: os vídeos com título, descrição, tags e horário
  python lote.py agenda LOTE [--inicio AAAA-MM-DD] agenda.json: 1 vídeo por dia às 09:00, a partir de amanhã
  python lote.py marcar LOTE N STATUS [--link URL] registra o resultado do agendamento no Studio
  python lote.py status LOTE                      resumo: produzido, metadados, agendado
Configuração em config.json (sobreposta por config.local.json).
"""
import argparse, datetime as dt, html, json, re, shutil, subprocess, sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

AQUI = Path(__file__).resolve().parent
SKILL = AQUI.parent
SKILLS = SKILL.parent
ANIMADOR = SKILLS / 'roblox-shorts-animator'
REGISTRO = ANIMADOR / 'historico' / 'roteiros.md'


def config():
    c = json.loads((SKILL / 'config.json').read_text(encoding='utf-8'))
    local = SKILL / 'config.local.json'
    if local.exists():
        extra = json.loads(local.read_text(encoding='utf-8'))
        for k, v in extra.items():
            if isinstance(v, dict) and isinstance(c.get(k), dict):
                c[k] = {**c[k], **v}
            else:
                c[k] = v
    return c


def caminho(p):
    return Path(p).expanduser()


def ler(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def gravar(p, dados):
    Path(p).write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding='utf-8')


def projetos(lote):
    return sorted(p for p in Path(lote).iterdir() if p.is_dir() and re.match(r'^\d\d-', p.name))


# ---------------------------------------------------------------- novo / historico / registrar

def cmd_novo(a):
    c = config()
    data = a.data or dt.date.today().isoformat()
    lote = caminho(c['pasta_entregas']) / f'lote-{data.replace("-", "")}'
    if lote.exists():
        raise SystemExit(f'{lote} já existe')
    lote.mkdir(parents=True)
    for i in range(1, c['videos_por_lote'] + 1):
        p = lote / f'{i:02d}-a-definir'
        (p / 'studio').mkdir(parents=True)
        (p / 'falas').mkdir()
        shutil.copy2(ANIMADOR / 'assets' / 'base.rbxlx', p / 'studio' / 'base.rbxlx')
    # Base comum das cenas e edições (timeline pelas falas reais, ajudantes Luau, cenário, legendas e efeitos).
    for f in (SKILL / 'modelos' / 'lote-base').glob('*'):
        shutil.copy2(f, lote / f.name)
    gravar(lote / 'lote.json', {'criado': data, 'videos': c['videos_por_lote'], 'status': {}})
    print(lote)
    print('Renomeie cada pasta NN-a-definir para NN-<tema> ao escrever o roteiro.')


def cmd_historico(a):
    c = config()
    if REGISTRO.exists():
        print(REGISTRO.read_text(encoding='utf-8'))
    registrados = REGISTRO.read_text(encoding='utf-8') if REGISTRO.exists() else ''
    extras = []
    for base in c['pastas_historico']:
        base = caminho(base)
        if not base.exists():
            continue
        for r in sorted(base.rglob('roteiro.json')):
            if f'<!-- {r.parent.name} -->' in registrados:
                continue
            try:
                rot = ler(r)
            except Exception:
                continue
            orig = r.parent / 'originalidade.json'
            premissa = ler(orig).get('premissa') if orig.exists() else None
            falas = ' / '.join(f.get('texto', '') for f in rot.get('falas', [])[:4])
            extras.append(f'- {r.parent.relative_to(base.parent)}: {rot.get("titulo", "?")}\n'
                          f'  premissa: {premissa or "(sem originalidade.json)"}\n  falas: {falas[:220]}')
    if extras:
        print(f'\n{len(extras)} roteiros em entregas/ ainda fora do registro (em produção ou abandonados):\n' + '\n'.join(extras))
    print('\nModelos da skill (só infraestrutura, nunca a história):',
          ', '.join(p.name for p in (ANIMADOR / 'modelos').iterdir() if p.is_dir()))


def registrar(projs):
    projs = [p for p in projs if (p / 'roteiro.json').exists()]
    if projs:
        subprocess.run([sys.executable, ANIMADOR / 'scripts' / 'registrar_roteiro.py', *map(str, projs)], check=False)


def cmd_registrar(a):
    lote = Path(a.lote).resolve()
    registrar([p for p in projetos(lote) if _video_pronto(p)])


# ---------------------------------------------------------------- produzir

def cmd_produzir(a):
    lote = Path(a.lote).resolve()
    estado = ler(lote / 'lote.json')
    fs = ANIMADOR / 'scripts' / 'fazer_short.py'
    for p in projetos(lote):
        n = p.name[:2]
        if a.so and n not in a.so:
            continue
        faltam = [f for f in ('roteiro.json', 'originalidade.json', 'gerar_cena.py', 'montar_edicao.py', 'studio/cenario.lua')
                  if not (p / f).exists()]
        if faltam:
            print(f'[{n}] pulado: falta {", ".join(faltam)}')
            estado['status'][n] = {'producao': 'incompleto', 'faltam': faltam}
            continue
        if _video_pronto(p) and not a.refazer:
            print(f'[{n}] já pronto')
            estado['status'][n] = {'producao': 'pronto'}
            registrar([p])
            continue
        print(f'[{n}] produzindo {p.name} ...', flush=True)
        with open(p / 'producao.log', 'w', encoding='utf-8') as log:
            subprocess.run([sys.executable, fs, str(p)], stdout=log, stderr=subprocess.STDOUT)
        fim = (p / 'producao.log').read_text(encoding='utf-8', errors='replace').strip().splitlines()[-1:]
        # O fazer_short termina conferindo publicacao.txt, que o 'metadados' escreve depois: vale o MP4 final.
        estado['status'][n] = {'producao': 'pronto' if _video_pronto(p) else 'erro', 'ultima_linha': fim[0] if fim else ''}
        print(f'[{n}] {estado["status"][n]["producao"]}: {estado["status"][n]["ultima_linha"]}')
        if _video_pronto(p):
            registrar([p])  # roteiro anotado no registro da skill: nenhum vídeo futuro repete a ideia
        gravar(lote / 'lote.json', estado)
    gravar(lote / 'lote.json', estado)


def _video_pronto(p):
    rot = ler(p / 'roteiro.json')
    return bool(rot.get('arquivo')) and (p / 'final-pt' / rot['arquivo']).exists()


# ---------------------------------------------------------------- metadados

def _creditos(p):
    arq = sorted((p / 'final-pt').glob('*-creditos.txt'))
    return arq[0].read_text(encoding='utf-8').strip() if arq else ''


def _tags_validas(tags):
    """YouTube: soma dos caracteres das tags <= 500 (tag com espaço conta 2 a mais), sem < >."""
    saida, total = [], 0
    for t in dict.fromkeys(t.strip().lstrip('#') for t in tags if t.strip()):
        t = re.sub(r'[<>]', '', t)
        custo = len(t) + (2 if ' ' in t else 0) + 1
        if total + custo > 480:
            break
        saida.append(t)
        total += custo
    return saida


def cmd_metadados(a):
    c = config()
    lote = Path(a.lote).resolve()
    problemas = []
    for p in projetos(lote):
        rot = ler(p / 'roteiro.json')
        arquivo = rot.get('arquivo')
        video = p / 'final-pt' / arquivo if arquivo else None
        titulo = (rot.get('titulo_youtube') or rot.get('titulo') or '').strip()
        if '#shorts' not in titulo.lower():
            titulo = f'{titulo} #shorts #roblox'
        descricao = (rot.get('descricao') or '').strip()
        hashtags = rot.get('hashtags') or []
        creditos = _creditos(p)
        corpo = '\n\n'.join(x for x in [descricao, ' '.join(h if h.startswith('#') else '#' + h for h in hashtags),
                                        'Música:\n' + creditos if creditos else '', 'Voz: ElevenLabs (voz "Roger").'] if x)
        tags = _tags_validas(rot.get('tags') or [])
        meta = {'video': str(video) if video else None, 'titulo': titulo, 'descricao': corpo, 'tags': tags,
                'feito_para_criancas': c['feito_para_criancas'], 'categoria': c['categoria'],
                'idioma': c['canal']['idioma_video']}
        erros = []
        if not video or not video.exists():
            erros.append('MP4 final não encontrado')
        if len(titulo) > 100:
            erros.append(f'título com {len(titulo)} caracteres (máx. 100)')
        if 'roblox' not in titulo.lower():
            erros.append('título sem "ROBLOX" (palavra-chave principal do canal)')
        if not descricao:
            erros.append('sem descrição no roteiro')
        if len(corpo) > 5000:
            erros.append('descrição com mais de 5000 caracteres')
        if re.search(r'[<>]', titulo + corpo):
            erros.append('título/descrição com < ou > (o YouTube recusa)')
        if len(tags) < 12:
            erros.append(f'só {len(tags)} tags (use 15–20: amplas de Roblox + tema)')
        if not creditos:
            erros.append('créditos da música não encontrados (render em final-pt/)')
        meta['erros'] = erros
        gravar(p / 'publicacao.json', meta)
        texto = f'TÍTULO:\n{titulo}\n\nDESCRIÇÃO:\n{corpo}\n\nTAGS:\n{", ".join(tags)}\n'
        (p / 'publicacao.txt').write_text(texto, encoding='utf-8')
        problemas += [f'{p.name}: {e}' for e in erros]
    print('\n'.join(problemas) if problemas else f'metadados OK ({len(projetos(lote))} arquivos publicacao.json)')
    sys.exit(1 if problemas else 0)


# ---------------------------------------------------------------- painel de revisão

def cmd_painel(a):
    lote = Path(a.lote).resolve()
    agenda = ler(lote / 'agenda.json') if (lote / 'agenda.json').exists() else None
    quando = {it['n']: it['quando'] for it in agenda['itens']} if agenda else {}
    cards = []
    for p in projetos(lote):
        mp = p / 'publicacao.json'
        if not mp.exists():
            continue
        m = ler(mp)
        rel = Path(m['video']).relative_to(lote).as_posix() if m.get('video') else ''
        q = quando.get(p.name[:2], '')
        erros = ''.join(f'<li>{html.escape(e)}</li>' for e in m.get('erros', []))
        cards.append(f'''<article><video src="{html.escape(rel)}" controls preload="metadata"></video>
<div><p class="meta">{p.name}{' · ' + html.escape(q) if q else ''}</p>
<h2>{html.escape(m['titulo'])}</h2><pre>{html.escape(m['descricao'])}</pre>
<p class="tags">{html.escape(', '.join(m['tags']))}</p>{f'<ul class="erro">{erros}</ul>' if erros else ''}</div></article>''')
    pagina = f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisão do lote</title><style>
:root{{--bg:#f7f5ff;--card:#fff;--tx:#1d1b2e;--mut:#6b6880;--err:#c62828}}
@media (prefers-color-scheme:dark){{:root{{--bg:#15131f;--card:#211e30;--tx:#eeeaff;--mut:#a29fbb;--err:#ff8a80}}}}
body{{background:var(--bg);color:var(--tx);font:15px system-ui,sans-serif;margin:0;padding:16px}}
h1{{font-size:20px}} article{{display:flex;gap:16px;background:var(--card);border-radius:12px;padding:12px;margin:0 0 14px}}
video{{width:200px;aspect-ratio:9/16;border-radius:8px;background:#000;flex:none}} h2{{font-size:16px;margin:4px 0}}
pre{{white-space:pre-wrap;font:13px system-ui;margin:6px 0}} .meta,.tags{{color:var(--mut);font-size:13px}} .erro{{color:var(--err)}}
@media (max-width:600px){{article{{flex-direction:column}} video{{width:100%}}}}</style>
<h1>Revisão do lote {html.escape(lote.name)} — {len(cards)} vídeos</h1>
<p>Um vídeo por dia às 09:00 no canal BRUNOBLOX. A thumbnail fica por conta do dono do canal.</p>{''.join(cards)}'''
    (lote / 'revisao.html').write_text(pagina, encoding='utf-8')
    print(lote / 'revisao.html')


# ---------------------------------------------------------------- agenda

def cmd_agenda(a):
    c = config()
    lote = Path(a.lote).resolve()
    try:
        fuso = ZoneInfo(c['fuso'])
    except ZoneInfoNotFoundError:  # Windows sem o pacote tzdata: Brasília não tem horário de verão desde 2019
        if c['fuso'] != 'America/Sao_Paulo':
            raise SystemExit('instale o fuso: pip install tzdata')
        fuso = dt.timezone(dt.timedelta(hours=-3), 'BRT')
    agora = dt.datetime.now(fuso)
    inicio = dt.date.fromisoformat(a.inicio) if a.inicio else agora.date() + dt.timedelta(days=1)
    ps = projetos(lote)
    # Um vídeo por dia em cada horário de config['horarios'] (09:00), a partir de amanhã; se o lote tiver mais
    # vídeos que o normal (7), a agenda segue nos dias seguintes.
    slots, d = [], 0
    while len(slots) < len(ps):
        dia = inicio + dt.timedelta(days=d)
        for h in c['horarios']:
            hh, mm = map(int, h.split(':'))
            quando = dt.datetime(dia.year, dia.month, dia.day, hh, mm, tzinfo=fuso)
            if quando > agora + dt.timedelta(minutes=30) and len(slots) < len(ps):
                slots.append(quando)
        d += 1
    itens = []
    for p, quando in zip(ps, slots):
        m = ler(p / 'publicacao.json')
        if m.get('erros'):
            raise SystemExit(f'{p.name}: metadados com erro ({"; ".join(m["erros"])}); rode metadados de novo')
        itens.append({'n': p.name[:2], 'projeto': p.name, 'quando': quando.strftime('%Y-%m-%d %H:%M'),
                      'data_studio': quando.strftime('%d/%m/%Y'), 'hora_studio': quando.strftime('%H:%M'),
                      'publish_at': quando.isoformat(), 'video': m['video'], 'titulo': m['titulo'],
                      'descricao': m['descricao'], 'tags': m['tags'], 'status': 'pendente', 'link': None})
    canal = c['canal']
    agenda = {'fuso': c['fuso'], 'gerado': agora.isoformat(timespec='minutes'),
              'canal': f'{canal["nome"]} ({canal["handle"]})', 'feito_para_criancas': c['feito_para_criancas'],
              'categoria': c['categoria'], 'idioma': canal['idioma_video'], 'itens': itens}
    gravar(lote / 'agenda.json', agenda)
    print(f'Canal {agenda["canal"]} — {"feito para crianças" if c["feito_para_criancas"] else "não é para crianças"}, '
          f'{c["categoria"]}, {canal["idioma_video"]}')
    for it in itens:
        print(f'  {it["quando"]}  {it["projeto"]}  {it["titulo"]}')


def cmd_marcar(a):
    lote = Path(a.lote).resolve()
    agenda = ler(lote / 'agenda.json')
    for it in agenda['itens']:
        if it['n'] == a.n.zfill(2):
            it['status'] = a.status
            if a.link:
                it['link'] = a.link
            gravar(lote / 'agenda.json', agenda)
            print(f'{it["n"]}: {a.status} {a.link or ""}')
            return
    raise SystemExit('vídeo não encontrado na agenda')


def cmd_status(a):
    lote = Path(a.lote).resolve()
    agenda = ler(lote / 'agenda.json') if (lote / 'agenda.json').exists() else {'itens': []}
    st = {it['n']: it for it in agenda['itens']}
    for p in projetos(lote):
        rot = ler(p / 'roteiro.json') if (p / 'roteiro.json').exists() else {}
        pronto = bool(rot.get('arquivo')) and (p / 'final-pt' / rot['arquivo']).exists()
        meta = (p / 'publicacao.json').exists()
        ag = st.get(p.name[:2])
        print(f'{p.name.ljust(32)} {"vídeo" if pronto else "-----"} {"meta" if meta else "----"} '
              f'{(ag["status"] + " " + ag["quando"] + (" " + ag["link"] if ag.get("link") else "")) if ag else ""}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('novo'); s.add_argument('--data')
    sub.add_parser('historico')
    s = sub.add_parser('produzir'); s.add_argument('lote'); s.add_argument('--so', nargs='+'); s.add_argument('--refazer', action='store_true')
    s = sub.add_parser('registrar'); s.add_argument('lote')
    s = sub.add_parser('metadados'); s.add_argument('lote')
    s = sub.add_parser('painel'); s.add_argument('lote')
    s = sub.add_parser('agenda'); s.add_argument('lote'); s.add_argument('--inicio')
    s = sub.add_parser('marcar'); s.add_argument('lote'); s.add_argument('n')
    s.add_argument('status', choices=['agendado', 'erro', 'pendente']); s.add_argument('--link')
    s = sub.add_parser('status'); s.add_argument('lote')
    a = ap.parse_args()
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
