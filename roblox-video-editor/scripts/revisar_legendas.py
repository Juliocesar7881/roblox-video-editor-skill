"""Automatic caption review: renders only the subtitles of an output, frame by frame, and reports
the defects a viewer would notice.

  python revisar_legendas.py timeline.json [--saida nome.mp4] [--fps 30]

Checks
  * eventos sobrepostos (duas legendas ao mesmo tempo = linha duplicada / legenda pulando)
  * destaque rapido demais (palavra amarela por menos de 0,12 s = pisca)
  * mais de uma linha de texto na metade de baixo no mesmo quadro (legenda quebrando em duas linhas ou
    empilhada; um titulo no alto da tela nao conta)
  * texto encostando na borda (cortado)
  * legenda ao mesmo tempo que um sticker/selo na faixa da legenda
  * legenda atravessando um corte de camera ("cortes" na saida): ela anunciaria o que ainda nao
    apareceu na tela (o certo e a tela ficar sem legenda ate o corte)
Exit code 1 when anything is found, so it can gate a render.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from media_utils import ffmpeg  # noqa: E402
from renderizar import make_ass, native_resolution, FONTES, filter_path  # noqa: E402
from media_utils import probe  # noqa: E402

FAIXA = (0.62, 0.78)  # faixa vertical (fracao da altura) onde ficam as legendas karaoke/legenda


def faixas_de_texto(linhas_com_texto, gap=3):
    bandas, ini, ult = [], None, None
    for y in np.nonzero(linhas_com_texto)[0]:
        if ini is None:
            ini = ult = y
        elif y - ult > gap:
            bandas.append((ini, ult)); ini = ult = y
        else:
            ult = y
    if ini is not None:
        bandas.append((ini, ult))
    return [b for b in bandas if b[1] - b[0] >= 4]


def revisar(spec_path, saida=None, fps=30, largura=360):
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding='utf-8-sig'))
    outputs = [o for o in spec['outputs'] if saida is None or o['name'] == saida]
    problemas = []
    for o in outputs:
        caps = sorted(o.get('captions', []), key=lambda c: c['start'])
        nome = o['name']
        # 1) Tempo: sobreposicao e destaque curto.
        for a, b in zip(caps, caps[1:]):
            if a['end'] > b['start'] + 1e-6 and a.get('style') == b.get('style'):
                problemas.append(f'{nome} {b["start"]:.2f}s: legendas sobrepostas ({(a["end"] - b["start"]) * 1000:.0f} ms) '
                                 f'"{a["text"]}" x "{b["text"]}"')
        for c in caps:
            if '*' in str(c['text']) and c['end'] - c['start'] < 0.12:
                problemas.append(f'{nome} {c["start"]:.2f}s: destaque de {(c["end"] - c["start"]) * 1000:.0f} ms (pisca) "{c["text"]}"')
        # 1b) Legenda atravessando corte: comeca mais de 0,2 s antes e termina mais de 0,2 s depois.
        for corte in o.get('cortes', []):
            for c in caps:
                if c['start'] < corte - 0.2 and c['end'] > corte + 0.2:
                    problemas.append(f'{nome} {corte:.2f}s: legenda "{c["text"]}" atravessa o corte de camera')
        # 2) Legenda junto com sticker/selo na faixa da legenda.
        for ov in o.get('overlays', []):
            a, b = ov['at'], ov['at'] + ov['duration']
            topo = ov.get('y', .3)
            if topo < FAIXA[1] and topo + .2 > FAIXA[0]:
                for c in caps:
                    if c['start'] < b and c['end'] > a:
                        problemas.append(f'{nome} {max(a, c["start"]):.2f}s: legenda "{c["text"]}" junto com '
                                         f'{Path(ov["file"]).name} na faixa da legenda')
        if not caps:
            continue
        # 3) Imagem: renderiza so as legendas sobre preto e procura linhas duplicadas e cortes.
        total = max(c['end'] for c in caps) + 0.2
        if 'resolution' in o:
            w, h = o['resolution']
        else:
            ref = spec.get('primary_source') or o['clips'][0]['source']
            ref = Path(ref) if Path(ref).is_absolute() else spec_path.parent / ref
            w, h = native_resolution(probe(ref), o['format'] == 'short')
        alt = round(largura * h / w / 2) * 2
        with tempfile.TemporaryDirectory() as td:
            ass = Path(td) / 'l.ass'
            make_ass(ass, caps, w, h, total, False)
            cmd = [ffmpeg(), '-v', 'error', '-f', 'lavfi', '-i', f'color=c=black:s={w}x{h}:r={fps}:d={total:.3f}',
                   '-vf', f"ass=filename='{filter_path(ass)}':fontsdir='{filter_path(FONTES)}',scale={largura}:{alt},format=gray",
                   '-f', 'rawvideo', '-pix_fmt', 'gray', '-']
            raw = subprocess.run(cmd, capture_output=True, check=True).stdout
        quadros = np.frombuffer(raw, np.uint8).reshape(-1, alt, largura)
        abertos = {}
        for i, q in enumerate(quadros):
            t = i / fps
            texto = q > 150  # miolo branco/amarelo; o contorno escuro some no fundo preto
            achados = []
            bandas = faixas_de_texto(texto[alt // 2:].any(axis=1))
            if len(bandas) > 1:
                achados.append(f'{len(bandas)} linhas de legenda ao mesmo tempo')
            colunas = np.nonzero(texto.any(axis=0))[0]
            if len(colunas) and (colunas[0] <= 1 or colunas[-1] >= largura - 2):
                achados.append('legenda encostando na borda (cortada)')
            for chave in achados:
                abertos.setdefault(chave, [t, t])[1] = t
            for chave in [k for k in abertos if k not in achados]:
                a, b = abertos.pop(chave)
                problemas.append(f'{nome} {a:.2f}-{b:.2f}s: {chave}')
        for chave, (a, b) in abertos.items():
            problemas.append(f'{nome} {a:.2f}-{b:.2f}s: {chave}')
    return problemas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('timeline', type=Path)
    ap.add_argument('--saida')
    ap.add_argument('--fps', type=int, default=30)
    a = ap.parse_args()
    problemas = revisar(a.timeline, a.saida, a.fps)
    for p in problemas:
        print('[legenda]', p)
    print(f'[legenda] total {len(problemas)} problema(s)')
    sys.exit(1 if problemas else 0)


if __name__ == '__main__':
    main()
