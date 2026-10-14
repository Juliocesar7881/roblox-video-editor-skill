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



FUNCAO = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das', 'no', 'na', 'nos', 'nas', 'e', 'ou',
          'que', 'em', 'pra', 'pro', 'com', 'por', 'se', 'eu', 'vou', 'é', 'tá', 'ta', 'mais', 'meu', 'minha',
          # espanhol (versao ES de todo Short)
          'el', 'la', 'los', 'las', 'un', 'una', 'del', 'al', 'y', 'en', 'con', 'me', 'mi', 'es', 'más', 'voy', 'muy'}


def _norm_palavra(w):
    return re.sub(r'[^\wÀ-ÿ]', '', w.lower())


def legendas_karaoke(falas, inicios, max_palavras=4, max_letras=24, folga=0.15, pausa=0.28,
                     minimo=0.16, pausa_destaque=0.1, cortes=()):
    """Estilo dos Shorts de referencia, "de pouco em pouco": cada grupo e uma ideia curta (quebra em
    virgula, reticencias, ? e !, e nunca termina em artigo/preposicao), some antes do proximo e,
    nas pausas da fala, a tela fica sem legenda. Dentro do grupo a palavra falada fica amarela
    (numeros em ciano, NAO em coral). Os eventos de um grupo nunca se sobrepoem; o primeiro tem
    'entrada' (entrada elastica) e o ultimo 'saida' (fade curto).
    cortes: tempos (no video final) dos cortes de camera. Um grupo que comecaria antes de um corte e
    terminaria depois dele so aparece NO corte (a tela fica sem legenda ate la): a legenda nunca
    anuncia o que ainda nao apareceu (ex.: "OU O AMARELO GIGANTE?" so quando o amarelo aparece)."""
    def custo(pedaco):
        letras = sum(len(x['w']) for x in pedaco) + len(pedaco) - 1
        if len(pedaco) > max_palavras or (letras > max_letras and len(pedaco) > 1):
            return float('inf')
        c = 2.0 + 0.5 * (len(pedaco) - 3) ** 2  # prefere grupos de ~3 palavras e menos grupos
        c += 0.5 * max(0, letras - 18)  # acima de ~18 letras a legenda teria de encolher
        if len(pedaco) > 1 and _norm_palavra(pedaco[-1]['w']) in FUNCAO:
            c += 10  # nunca terminar em "O", "NO", "OU"...
        if all(_norm_palavra(x['w']) in FUNCAO for x in pedaco):
            c += 10  # nem um grupo so de palavras de ligacao
        return c

    def dividir(frase):
        # Programacao dinamica: melhor divisao da frase em pedacos validos.
        n = len(frase)
        melhor = [0.0] + [float('inf')] * n
        corte = [0] * (n + 1)
        for j in range(1, n + 1):
            for i in range(max(0, j - max_palavras), j):
                c = melhor[i] + custo(frase[i:j])
                if c < melhor[j]:
                    melhor[j], corte[j] = c, i
        partes, j = [], n
        while j > 0:
            partes.insert(0, frase[corte[j]:j]); j = corte[j]
        return partes

    caps = []
    for f in falas:
        base = inicios[f['id']]
        ws = f['palavras']
        # 1) frases: quebram em pontuacao e nas pausas da fala; 2) frases longas viram pedacos.
        frases, g = [], []
        for i, w in enumerate(ws):
            g.append(w)
            prox = ws[i + 1] if i + 1 < len(ws) else None
            pontuado = re.search(r'[,.!?…]$', w['w'])
            pausou = prox is not None and prox['start'] - w['end'] > pausa
            if prox is not None and (pontuado or pausou):
                frases.append(g); g = []
        if g:
            frases.append(g)
        grupos = [p for frase in frases for p in dividir(frase)]
        for gi, g in enumerate(grupos):
            fim_grupo = g[-1]['end'] + folga
            if gi + 1 < len(grupos):
                fim_grupo = min(fim_grupo, grupos[gi + 1][0]['start'])
            eventos = _eventos_do_grupo(g, fim_grupo, minimo, pausa_destaque)
            # Corte no meio do grupo: o grupo so entra no corte (sem legenda antes dele).
            # Corte nos ultimos instantes do grupo e da frase seguinte: o grupo nao espera por ele
            # (so termina no corte, mais abaixo), senao ficaria um fiapo de 50 ms piscando.
            dentro = [c - base for c in cortes if base + g[0]['start'] + 0.05 < c < base + g[-1]['end'] - 0.15]
            if dentro:
                c = max(dentro)
                eventos = [ev for ev in eventos if ev['fim'] > c + 0.02]
                if eventos:
                    eventos[0]['ini'] = max(eventos[0]['ini'], c)
                    # Sobra curta de um destaque anterior ao corte nao pisca: junta com o seguinte.
                    while len(eventos) > 1 and eventos[0]['fim'] - eventos[0]['ini'] < minimo:
                        eventos[1]['ini'] = eventos[0]['ini']
                        del eventos[0]
                    for i, ev in enumerate(eventos):
                        ev['entrada'] = i == 0
            for ev in eventos:
                caps.append({'start': round(base + ev['ini'], 3), 'end': round(base + ev['fim'], 3),
                             'text': ev['texto'], 'style': 'karaoke', 'highlight': ev['cor'],
                             **({'entrada': True} if ev['entrada'] else {}),
                             **({'saida': True} if ev['saida'] else {})})
    # A sobra de uma frase (texto branco depois da ultima palavra) tambem nao atravessa um corte:
    # termina no corte, e a frase seguinte entra no plano novo.
    for c in caps:
        corte = [x for x in cortes if c['start'] + 0.02 < x < c['end']]
        if corte and c.get('saida'):
            c['end'] = round(min(corte), 3)
    # Sobra branca curta demais (< minimo) antes do corte pisca: o destaque anterior fica ate o fim.
    caps.sort(key=lambda c: c['start'])
    for i in range(len(caps) - 1, 0, -1):
        c, ant = caps[i], caps[i - 1]
        if (c.get('saida') and not c.get('entrada') and c['end'] - c['start'] < minimo
                and abs(ant['end'] - c['start']) < 0.005 and not ant.get('saida')):
            ant['end'] = c['end']
            ant['saida'] = True
            del caps[i]
    # Garantia final: nenhuma legenda invade a seguinte (duas ao mesmo tempo = linha duplicada).
    caps.sort(key=lambda c: c['start'])
    for a, b in zip(caps, caps[1:]):
        if a['end'] > b['start']:
            a['end'] = b['start']
    return [c for c in caps if c['end'] - c['start'] >= 0.02]


def _eventos_do_grupo(g, fim_grupo, minimo, pausa_destaque):
    """Divide o tempo do grupo em eventos sem sobreposicao: em cada um, a(s) palavra(s) falada(s)
    ficam amarelas; entre palavras (pausa) e depois da ultima, nenhuma fica (como na referencia).
    Palavras faladas rapido demais (< minimo) sao destacadas junto com a vizinha, sem piscar."""
    unidades = [[i] for i in range(len(g))]

    def dur(u):
        return g[u[-1]]['end'] - g[u[0]]['start']

    while len(unidades) > 1:
        curtos = [k for k, u in enumerate(unidades) if dur(u) < minimo]
        if not curtos:
            break
        k = curtos[0]
        if k + 1 < len(unidades) and (k == 0 or dur(unidades[k + 1]) <= dur(unidades[k - 1])):
            j = k + 1
        else:
            j = k - 1
        a, b = sorted((k, j))
        unidades[a] = unidades[a] + unidades[b]
        del unidades[b]

    def texto(u):
        partes = []
        for i, w in enumerate(g):
            p = w['w'].upper()
            if u and i in u and (i - 1) not in u:
                p = '*' + p
            if u and i in u and (i + 1) not in u:
                p = p + '*'
            partes.append(p)
        return ' '.join(partes)

    def cor(u):
        palavras = [_norm_palavra(g[i]['w']) for i in u]
        if any(re.search(r'\d', p) for p in palavras):
            return 'ciano'
        if any(p in ('não', 'nao') for p in palavras):  # 'no' fica fora: em portugues e "no" de "vou no"
            return 'coral'
        return 'ouro'

    eventos = []
    for k, u in enumerate(unidades):
        ini = g[u[0]]['start'] if k else g[0]['start']
        prox = g[unidades[k + 1][0]]['start'] if k + 1 < len(unidades) else fim_grupo
        fim = min(g[u[-1]]['end'], prox)
        if prox - fim < pausa_destaque:
            fim = prox  # pausa curta: o destaque fica ate a proxima palavra (sem piscar branco)
        if eventos and eventos[-1]['fim'] < ini:
            eventos[-1]['fim'] = ini
        eventos.append({'ini': ini, 'fim': fim, 'texto': texto(u), 'cor': cor(u)})
        if fim < prox:
            eventos.append({'ini': fim, 'fim': prox, 'texto': texto(None), 'cor': 'ouro'})
    eventos = [e for e in eventos if e['fim'] - e['ini'] >= 0.02]
    for i, e in enumerate(eventos):
        e['entrada'] = i == 0
        e['saida'] = i == len(eventos) - 1
    return eventos

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
