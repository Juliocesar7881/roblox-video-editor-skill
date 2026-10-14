"""Lote de Shorts de Roblox: 10 videos inéditos em português e espanhol, metadados do YouTube e agenda.

  python lote.py novo [--data AAAA-MM-DD]          cria entregas/lote-AAAAMMDD com 10 projetos vazios
  python lote.py historico                        premissas de todos os Shorts já feitos (originalidade)
  python lote.py produzir LOTE [--so N ...]        roda fazer_bilingue.py em cada projeto (PT e ES)
  python lote.py metadados LOTE                   publicacao-pt.json / -es.json validados para o YouTube
  python lote.py painel LOTE                      revisao.html: os 20 vídeos com título, descrição e tags
  python lote.py agenda LOTE [--inicio AAAA-MM-DD] agenda.json: 2 por dia (12:15 e 17:15) por 5 dias, por canal
  python lote.py marcar LOTE CANAL N STATUS [--link URL]   registra o resultado do agendamento no Studio
  python lote.py status LOTE                      resumo: produzido, metadados, agendado
Configuração em config.json (sobreposta por config.local.json, que guarda os nomes dos canais).
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
IDIOMAS = ('pt', 'es')
SUF = {'pt': '', 'es': '-es'}


def config():
    c = json.loads((SKILL / 'config.json').read_text(encoding='utf-8'))
    local = SKILL / 'config.local.json'
    if local.exists():
        extra = json.loads(local.read_text(encoding='utf-8'))
        for k, v in extra.items():
            if isinstance(v, dict) and isinstance(c.get(k), dict):
                for k2, v2 in v.items():
                    c[k][k2] = {**c[k].get(k2, {}), **v2} if isinstance(v2, dict) else v2
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


# ---------------------------------------------------------------- novo / historico

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
        (p / 'falas-es').mkdir()
        shutil.copy2(ANIMADOR / 'assets' / 'base.rbxlx', p / 'studio' / 'base.rbxlx')
    gravar(lote / 'lote.json', {'criado': data, 'videos': c['videos_por_lote'], 'status': {}})
    print(lote)
    print('Renomeie cada pasta NN-a-definir para NN-<tema> ao escrever o roteiro.')


def cmd_historico(a):
    c = config()
    vistos = []
    for base in c['pastas_historico']:
        base = caminho(base)
        if not base.exists():
            continue
        for r in sorted(base.rglob('roteiro.json')):
            try:
                rot = ler(r)
            except Exception:
                continue
            orig = r.parent / 'originalidade.json'
            premissa = ler(orig).get('premissa') if orig.exists() else None
            falas = ' / '.join(f.get('texto', '') for f in rot.get('falas', [])[:4])
            vistos.append(f'- {r.parent.relative_to(base.parent)}: {rot.get("titulo", "?")}\n'
                          f'  premissa: {premissa or "(sem originalidade.json)"}\n  falas: {falas[:220]}')
    print(f'{len(vistos)} Shorts já roteirizados:\n' + '\n'.join(vistos))
    print('\nModelos da skill (só infraestrutura, nunca a história):',
          ', '.join(p.name for p in (ANIMADOR / 'modelos').iterdir() if p.is_dir()))


# ---------------------------------------------------------------- produzir

def cmd_produzir(a):
    lote = Path(a.lote).resolve()
    estado = ler(lote / 'lote.json')
    fb = ANIMADOR / 'scripts' / 'fazer_bilingue.py'
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
        if _videos_prontos(p) and not a.refazer:
            print(f'[{n}] já pronto (PT e ES)')
            estado['status'][n] = {'producao': 'pronto'}
            continue
        print(f'[{n}] produzindo {p.name} ...', flush=True)
        with open(p / 'bilingue.log', 'w', encoding='utf-8') as log:
            r = subprocess.run([sys.executable, fb, str(p)], stdout=log, stderr=subprocess.STDOUT)
        fim = (p / 'bilingue.log').read_text(encoding='utf-8', errors='replace').strip().splitlines()[-1:]
        # O fazer_bilingue termina conferindo publicacao*.txt, que o 'metadados' escreve depois: vale o MP4 final.
        estado['status'][n] = {'producao': 'pronto' if _videos_prontos(p) else 'erro', 'ultima_linha': fim[0] if fim else ''}
        print(f'[{n}] {estado["status"][n]["producao"]}: {estado["status"][n]["ultima_linha"]}')
        gravar(lote / 'lote.json', estado)
    gravar(lote / 'lote.json', estado)


def _videos_prontos(p):
    rot = ler(p / 'roteiro.json')
    return all(rot.get(k) and (p / f'final-{i}' / rot[k]).exists() for i, k in (('pt', 'arquivo'), ('es', 'arquivo_es')))


# ---------------------------------------------------------------- metadados

def _creditos(p, idioma):
    arq = sorted((p / f'final-{idioma}').glob('*-creditos.txt'))
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
    lote = Path(a.lote).resolve()
    problemas = []
    for p in projetos(lote):
        rot = ler(p / 'roteiro.json')
        for idioma in IDIOMAS:
            s = SUF[idioma]
            k = (lambda campo: campo) if idioma == 'pt' else (lambda campo: f'{campo}_{idioma}')
            arquivo = rot.get(k('arquivo'))
            video = p / f'final-{idioma}' / arquivo if arquivo else None
            titulo = (rot.get(k('titulo_youtube')) or rot.get(k('titulo')) or '').strip()
            if '#shorts' not in titulo.lower():
                titulo = f'{titulo} #shorts'
            descricao = (rot.get(k('descricao')) or '').strip()
            hashtags = rot.get(k('hashtags')) or []
            creditos = _creditos(p, idioma)
            voz = 'Voz: ElevenLabs (voz "Roger").' if idioma == 'pt' else 'Voz: ElevenLabs (voz "Roger").'
            corpo = '\n\n'.join(x for x in [descricao, ' '.join(h if h.startswith('#') else '#' + h for h in hashtags),
                                            ('Música:\n' if idioma == 'pt' else 'Música:\n') + creditos if creditos else '', voz] if x)
            meta = {'video': str(video) if video else None, 'titulo': titulo, 'descricao': corpo,
                    'tags': _tags_validas(rot.get(k('tags')) or []), 'feito_para_criancas': config()['feito_para_criancas'],
                    'categoria': config()['categoria'], 'idioma': idioma}
            erros = []
            if not video or not video.exists():
                erros.append('MP4 final não encontrado')
            if len(titulo) > 100:
                erros.append(f'título com {len(titulo)} caracteres (máx. 100)')
            if not descricao:
                erros.append('sem descrição no roteiro (descricao / descricao_es)')
            if len(corpo) > 5000:
                erros.append('descrição com mais de 5000 caracteres')
            if re.search(r'[<>]', titulo + corpo):
                erros.append('título/descrição com < ou > (o YouTube recusa)')
            if len(meta['tags']) < 5:
                erros.append('menos de 5 tags')
            if not creditos:
                erros.append('créditos da música não encontrados (render em final-*/)')
            meta['erros'] = erros
            gravar(p / f'publicacao-{idioma}.json', meta)
            rotulos = ('TÍTULO', 'DESCRIÇÃO', 'TAGS') if idioma == 'pt' else ('TÍTULO', 'DESCRIPCIÓN', 'ETIQUETAS')
            texto = f'{rotulos[0]}:\n{titulo}\n\n{rotulos[1]}:\n{corpo}\n\n{rotulos[2]}:\n{", ".join(meta["tags"])}\n'
            (p / f'publicacao{s}.txt').write_text(texto, encoding='utf-8')
            problemas += [f'{p.name} {idioma}: {e}' for e in erros]
    print('\n'.join(problemas) if problemas else f'metadados OK ({2 * len(projetos(lote))} arquivos publicacao-pt/es.json)')
    sys.exit(1 if problemas else 0)


# ---------------------------------------------------------------- painel de revisão

def cmd_painel(a):
    lote = Path(a.lote).resolve()
    agenda = ler(lote / 'agenda.json') if (lote / 'agenda.json').exists() else None
    quando = {}
    if agenda:
        for canal, itens in agenda['canais'].items():
            for it in itens:
                quando[(canal, it['n'])] = it['quando']
    cards = []
    for p in projetos(lote):
        for idioma in IDIOMAS:
            mp = p / f'publicacao-{idioma}.json'
            if not mp.exists():
                continue
            m = ler(mp)
            rel = Path(m['video']).relative_to(lote).as_posix() if m.get('video') else ''
            q = quando.get((idioma, p.name[:2]), '')
            erros = ''.join(f'<li>{html.escape(e)}</li>' for e in m.get('erros', []))
            cards.append(f'''<article><video src="{html.escape(rel)}" controls preload="metadata"></video>
<div><p class="meta">{p.name} · {idioma.upper()}{' · ' + html.escape(q) if q else ''}</p>
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
<p>Depois de assistir, diga <b>"agende"</b> para agendar tudo no YouTube Studio.</p>{''.join(cards)}'''
    (lote / 'revisao.html').write_text(pagina, encoding='utf-8')
    print(lote / 'revisao.html')


# ---------------------------------------------------------------- agenda

def cmd_agenda(a):
    c = config()
    lote = Path(a.lote).resolve()
    try:
        fuso = ZoneInfo(c['fuso'])
    except ZoneInfoNotFoundError:  # Windows sem o pacote tzdata: Brasilia nao tem horario de verao desde 2019
        if c['fuso'] != 'America/Sao_Paulo':
            raise SystemExit('instale o fuso: pip install tzdata')
        fuso = dt.timezone(dt.timedelta(hours=-3), 'BRT')
    agora = dt.datetime.now(fuso)
    inicio = dt.date.fromisoformat(a.inicio) if a.inicio else agora.date() + dt.timedelta(days=1)
    slots = []
    for d in range(c['dias']):
        dia = inicio + dt.timedelta(days=d)
        for h in c['horarios']:
            hh, mm = map(int, h.split(':'))
            quando = dt.datetime(dia.year, dia.month, dia.day, hh, mm, tzinfo=fuso)
            if quando > agora + dt.timedelta(minutes=30):
                slots.append(quando)
    ps = projetos(lote)
    if len(slots) < len(ps):
        raise SystemExit(f'só {len(slots)} horários para {len(ps)} vídeos')
    agenda = {'fuso': c['fuso'], 'gerado': agora.isoformat(timespec='minutes'), 'canais': {}}
    for idioma in IDIOMAS:
        itens = []
        for p, quando in zip(ps, slots):
            m = ler(p / f'publicacao-{idioma}.json')
            if m.get('erros'):
                raise SystemExit(f'{p.name} {idioma}: metadados com erro ({"; ".join(m["erros"])}); rode metadados de novo')
            itens.append({'n': p.name[:2], 'projeto': p.name, 'quando': quando.strftime('%Y-%m-%d %H:%M'),
                          'data_studio': quando.strftime('%d/%m/%Y'), 'hora_studio': quando.strftime('%H:%M'),
                          'publish_at': quando.isoformat(), 'video': m['video'], 'titulo': m['titulo'],
                          'descricao': m['descricao'], 'tags': m['tags'], 'status': 'pendente', 'link': None})
        canal = c['canais'][idioma]
        agenda['canais'][idioma] = itens
        agenda.setdefault('nomes_canais', {})[idioma] = canal.get('nome') or f'(defina canais.{idioma}.nome em config.local.json)'
    gravar(lote / 'agenda.json', agenda)
    for idioma, itens in agenda['canais'].items():
        print(f'Canal {idioma.upper()} — {agenda["nomes_canais"][idioma]}')
        for it in itens:
            print(f'  {it["quando"]}  {it["projeto"]}  {it["titulo"]}')


def cmd_marcar(a):
    lote = Path(a.lote).resolve()
    agenda = ler(lote / 'agenda.json')
    for it in agenda['canais'][a.canal]:
        if it['n'] == a.n.zfill(2):
            it['status'] = a.status
            if a.link:
                it['link'] = a.link
            gravar(lote / 'agenda.json', agenda)
            print(f'{a.canal} {it["n"]}: {a.status} {a.link or ""}')
            return
    raise SystemExit('vídeo não encontrado na agenda')


def cmd_status(a):
    lote = Path(a.lote).resolve()
    agenda = ler(lote / 'agenda.json') if (lote / 'agenda.json').exists() else {'canais': {}}
    st = {(c, it['n']): it for c, its in agenda['canais'].items() for it in its}
    for p in projetos(lote):
        linha = [p.name.ljust(32)]
        for idioma in IDIOMAS:
            rot = ler(p / 'roteiro.json') if (p / 'roteiro.json').exists() else {}
            arq = rot.get('arquivo' if idioma == 'pt' else f'arquivo_{idioma}')
            pronto = bool(arq) and (p / f'final-{idioma}' / arq).exists()
            meta = (p / f'publicacao-{idioma}.json').exists()
            ag = st.get((idioma, p.name[:2]))
            linha.append(f'{idioma}: {"vídeo" if pronto else "-----"} {"meta" if meta else "----"} '
                         f'{(ag["status"] + " " + ag["quando"]) if ag else ""}')
        print(' | '.join(linha))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('novo'); s.add_argument('--data')
    sub.add_parser('historico')
    s = sub.add_parser('produzir'); s.add_argument('lote'); s.add_argument('--so', nargs='+'); s.add_argument('--refazer', action='store_true')
    s = sub.add_parser('metadados'); s.add_argument('lote')
    s = sub.add_parser('painel'); s.add_argument('lote')
    s = sub.add_parser('agenda'); s.add_argument('lote'); s.add_argument('--inicio')
    s = sub.add_parser('marcar'); s.add_argument('lote'); s.add_argument('canal', choices=IDIOMAS); s.add_argument('n')
    s.add_argument('status', choices=['agendado', 'erro', 'pendente']); s.add_argument('--link')
    s = sub.add_parser('status'); s.add_argument('lote')
    a = ap.parse_args()
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
