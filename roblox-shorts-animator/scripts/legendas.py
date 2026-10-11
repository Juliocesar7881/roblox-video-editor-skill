"""Word-by-word captions from ElevenLabs timings, plus original countdown badges.

  python legendas.py badges            -> assets/contagem-1.png ... contagem-5.png
  from legendas import legendas_falas  -> lista de captions para a timeline do renderizador
"""
import re, sys, unicodedata
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def _norm(w):
    w = unicodedata.normalize('NFD', w.upper())
    return re.sub(r'[^A-Z0-9]', '', ''.join(c for c in w if unicodedata.category(c) != 'Mn'))


def legendas_falas(falas, inicios, destaques=(), max_palavras=3, max_letras=16, folga=0.12):
    """falas: itens de falas.json; inicios: {id: segundo em que a fala comeca no video final}.
    destaques: palavras/expressoes que ficam em amarelo (*...*). Devolve captions estilo 'legenda'."""
    alvo = {_norm(w) for d in destaques for w in d.split()}
    caps = []
    for f in falas:
        base = inicios[f['id']]
        grupo = []

        def fechar(prox_inicio):
            if not grupo:
                return
            texto = ' '.join(f'*{g["w"].upper()}*' if _norm(g['w']) in alvo else g['w'].upper() for g in grupo)
            texto = texto.replace('* *', ' ')  # palavras destacadas vizinhas viram um bloco so
            fim = min(grupo[-1]['end'] + folga, prox_inicio) if prox_inicio is not None else grupo[-1]['end'] + folga
            caps.append({'start': round(base + grupo[0]['start'], 3), 'end': round(base + max(fim, grupo[0]['start'] + 0.25), 3),
                         'text': texto, 'style': 'legenda'})
            grupo.clear()

        for i, w in enumerate(f['palavras']):
            letras = sum(len(g['w']) + 1 for g in grupo) + len(w['w'])
            if grupo and (len(grupo) >= max_palavras or letras > max_letras):
                fechar(w['start'])
            grupo.append(w)
            if re.search(r'[.!?,]$', w['w']):
                prox = f['palavras'][i + 1]['start'] if i + 1 < len(f['palavras']) else None
                fechar(prox)
        fechar(None)
    return caps



def legendas_karaoke(falas, inicios, max_palavras=3, max_letras=18, folga=0.15):
    """Estilo dos Shorts de referencia: grupos de 2-3 palavras em branco com contorno escuro, e a
    palavra que esta sendo falada em amarelo. Uma caption por palavra (mesmo grupo, destaque muda);
    so a primeira de cada grupo tem 'entrada' (fade/pop rapido)."""
    caps = []
    for f in falas:
        base = inicios[f['id']]
        ws = f['palavras']
        grupos, g = [], []
        for i, w in enumerate(ws):
            letras = sum(len(x['w']) + 1 for x in g) + len(w['w'])
            if g and (len(g) >= max_palavras or letras > max_letras):
                grupos.append(g); g = []
            g.append(w)
            if re.search(r'[.!?]$', w['w']) and i + 1 < len(ws):
                grupos.append(g); g = []
        if g:
            grupos.append(g)
        for gi, g in enumerate(grupos):
            fim_grupo = g[-1]['end'] + folga
            if gi + 1 < len(grupos):
                fim_grupo = min(fim_grupo, grupos[gi + 1][0]['start'])
            for wi, w in enumerate(g):
                ini = w['start']
                fim = g[wi + 1]['start'] if wi + 1 < len(g) else fim_grupo
                texto = ' '.join(f'*{x["w"].upper()}*' if xi == wi else x['w'].upper() for xi, x in enumerate(g))
                caps.append({'start': round(base + ini, 3), 'end': round(base + max(fim, ini + 0.08), 3),
                             'text': texto, 'style': 'karaoke', **({'entrada': True} if wi == 0 else {})})
    return caps

def badges():
    from PIL import Image, ImageDraw, ImageFont
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name in ['ariblk.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf']:
        try:
            font = ImageFont.truetype(name, 250)
            break
        except OSError:
            font = ImageFont.load_default()
    for n in range(1, 6):
        img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((24, 24, 488, 488), fill='#1B2A4A', outline='#FFFFFF', width=26)
        d.ellipse((70, 70, 442, 442), outline='#47C8FF', width=10)
        d.text((256, 262), str(n), font=font, fill='#FFFFFF', anchor='mm', stroke_width=10, stroke_fill='#0B1428')
        img.save(ASSETS / f'contagem-{n}.png')
    print(ASSETS)


if __name__ == '__main__':
    if sys.argv[1:] == ['badges']:
        badges()
    else:
        print(__doc__)
