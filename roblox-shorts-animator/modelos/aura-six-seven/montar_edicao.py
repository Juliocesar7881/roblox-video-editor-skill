"""Monta timeline-edicao.json (renderizador da skill roblox-video-editor) para o Short animado.

  python montar_edicao.py [--estimado] [--previa]
Usa cena.mp4 (gravado no Studio), tempos.json (gerar_cena.py) e as falas (ElevenLabs ou estimadas).
"""
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = Path.home() / '.claude' / 'skills'
sys.path.insert(0, str(SKILLS / 'roblox-shorts-animator' / 'scripts'))
from legendas import legendas_karaoke  # noqa: E402
sys.path.insert(0, str(HERE))
from gerar_cena import estimar  # noqa: E402

LIB = SKILLS / 'roblox-video-editor' / 'assets' / 'biblioteca-audio'
OV = (SKILLS / 'roblox-video-editor' / 'assets' / 'overlays').as_posix() + '/'
BADGE = (SKILLS / 'roblox-shorts-animator' / 'assets').as_posix() + '/'
CC = 'efeitos/capcut-convertidos/'
OL = 'efeitos/originais-livres/'
FX = {
    'whoosh': [CC + 'eem mp3-1.mp3', CC + 'eem mp3-4.mp3', CC + 'eem mp3-15.mp3', CC + 'eem mp3-5.mp3'],
    'pop': [CC + 'eem mp3-18.mp3', CC + 'eem mp3-24.mp3', CC + 'eem mp3-26.mp3', CC + 'eem mp3-19.mp3'],
    'clique': [CC + 'eem mp3-12.mp3', CC + 'eem mp3-6.mp3'],
    'ding': [CC + 'eem mp3-16.mp3', CC + 'eem mp3-31.mp3'],
    'impacto': [CC + 'em mp3-7.mp3', CC + 'eem mp3-55.mp3'],
    'explosao': [CC + 'em mp3-8.mp3'],
    'soco': [CC + 'em mp3-3.mp3', CC + 'em mp3-5.mp3'],
    'boing': [CC + 'eem mp3-68.mp3', CC + 'eem mp3-63.mp3'],
    'erro': [CC + 'eem mp3-57.mp3'],
    'erro_curto': [OL + 'erro-original.mp3'],
    'apito': [CC + 'eem mp3-35.mp3'],
    'coracao': [CC + 'eem mp3-43.mp3'],
    'timpano': [CC + 'eem mp3-45.mp3'],
    'trombone': [CC + 'eem mp3-37.mp3'],
    'engracado': [CC + 'eem mp3-60.mp3'],
    'brilho': [CC + 'eem mp3-52.mp3', CC + 'eem mp3-34.mp3'],
    'aplausos': [CC + 'eem mp3-40.mp3'],
}
GAIN = {'whoosh': -10, 'pop': -11, 'clique': -11, 'ding': -11, 'impacto': -4, 'explosao': -5, 'soco': -6,
        'boing': -9, 'erro': -10, 'apito': -11, 'coracao': -12, 'timpano': -8, 'trombone': -9, 'engracado': -11, 'erro_curto': -11, 'brilho': -12, 'aplausos': -14}
_uso = {}


def sfx(cat, at, gain=None, dur=None, pitch=None):
    lista = FX[cat]
    i = _uso.get(cat, 0); _uso[cat] = i + 1
    row = {'file': lista[i % len(lista)], 'at': round(at, 3), 'gain_db': GAIN[cat] if gain is None else gain}
    if dur: row['duration'] = dur
    if pitch: row['pitch'] = pitch
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--estimado', action='store_true')
    ap.add_argument('--previa', action='store_true')
    ap.add_argument('--cena', default='cena.mp4')
    ap.add_argument('--saida', default='timeline-edicao.json')
    ap.add_argument('--nome', default=None)
    ap.add_argument('--idioma', default='pt', help='pt ou es: falas-es/, tempos-es.json, cena-es.mp4, timeline-edicao-es.json')
    a = ap.parse_args()
    roteiro = json.loads((HERE / 'roteiro.json').read_text(encoding='utf-8'))
    suf = '' if a.idioma == 'pt' else f'-{a.idioma}'
    if suf:
        a.cena = a.cena if a.cena != 'cena.mp4' else f'cena{suf}.mp4'
        a.saida = a.saida if a.saida != 'timeline-edicao.json' else f'timeline-edicao{suf}.json'
    a.nome = a.nome or roteiro.get('arquivo' if a.idioma == 'pt' else f'arquivo_{a.idioma}', 'short' + suf + '.mp4')
    T = json.loads((HERE / f'tempos{suf}.json').read_text(encoding='utf-8'))
    falas = estimar(roteiro) if a.estimado else json.loads((HERE / f'falas{suf}' / 'falas.json').read_text(encoding='utf-8'))
    F = {f['id']: f for f in falas}
    ini = T['falas']
    fim = T['fim']

    # A legenda so entra no corte (porta e cada angulo do six seven): nada escrito antes da coisa aparecer.
    cortes = T['cortes']
    captions = legendas_karaoke(falas, ini, cortes=cortes)
    voice = [] if a.estimado else [{'file': f'falas{suf}/{F[i]["arquivo"]}', 'at': round(ini[i], 3), 'gain_db': 0} for i in ini]
    S, E, O = [], [], []

    def palavra(fid, *trechos):
        """Instante (no video) da primeira palavra da fala que contem um dos trechos."""
        for w in F[fid]['palavras']:
            if any(t in w['w'].lower() for t in trechos):
                return ini[fid] + w['start']
        return None

    # Gancho: pop na entrada, plim em "aura", corte seco para a porta com whoosh + zoom-soco.
    S.append(sfx('pop', 0.05))
    t = palavra('01', 'aura')
    if t is not None:
        S.append(sfx('ding', t))
    S.append(sfx('whoosh', T['cporta'] - 0.05))
    E.append({'type': 'punch', 'at': round(T['cporta'], 3), 'intensity': 0.14, 'duration': 0.3})
    # "Mil de aura?!": zoom-soco no espanto; "Facil...": clique confiante.
    E.append({'type': 'punch', 'at': round(ini['02'] + 0.05, 3), 'intensity': 0.16, 'duration': 0.3})
    S.append(sfx('boing', ini['02'] + F['02']['palavras'][2]['end'], gain=-12))
    S.append(sfx('clique', T['facil'], gain=-10))
    # Six seven lento: um pop por mao, aura roxa acendendo; insert do medidor 0 -> 67.
    S.append(sfx('pop', T['six3'], pitch=1.0))
    S.append(sfx('pop', T['seven3'], pitch=1.25))
    E.append({'type': 'punch', 'at': round(T['seven3'], 3), 'intensity': 0.08, 'duration': 0.25})
    S.append(sfx('whoosh', T['medidor1'] - 0.03, gain=-12, dur=0.4))
    S.append(sfx('ding', T['medidor1'] + 0.45))
    # Six seven rapido: whoosh em cada corte de angulo, pop por mao, zoom-soco no "seven".
    for k, (t6, t7) in enumerate(zip(T['six4'], T['seven4'])):
        S.append(sfx('whoosh', t6 - 0.06, gain=-13, dur=0.3, pitch=[1.0, 1.1, 0.9][k % 3]))
        S.append(sfx('pop', t6, pitch=1.0 + 0.1 * k))
        S.append(sfx('pop', t7, pitch=1.25 + 0.1 * k))
        E.append({'type': 'punch', 'at': round(t7, 3), 'intensity': 0.07 + 0.02 * k, 'duration': 0.22})
    # Medidor sobe ate 999 com brilho... e trava: erro curto.
    m2 = T['medidor2']
    S.append(sfx('whoosh', m2 - 0.03, gain=-12, dur=0.4))
    S.append(sfx('brilho', m2 + 0.05, dur=0.75))
    S.append(sfx('erro_curto', m2 + 0.85))
    E.append({'type': 'zoom', 'at': round(m2 + 0.8, 3), 'duration': 0.45, 'intensity': 0.08})
    # "Novecentos e noventa e nove?!": close com zoom e musiquinha engracada depois.
    E.append({'type': 'zoom', 'at': round(ini['05'], 3), 'duration': 1.5, 'intensity': 0.1})
    O.append({'file': OV + 'interrogacao.png', 'at': round(ini['05'] + 0.1, 3), 'duration': 1.6, 'x': 0.62, 'y': 0.12, 'width': 0.3})
    t_en = ini['05'] + F['05']['duracao'] + 0.02
    S.append(sfx('engracado', t_en, dur=round(max(0.3, ini['06'] - t_en), 3)))
    # "So mais um..." com rufar; SIX SEVEN final: impacto, explosao, flash e tremida, aura dourada.
    S.append(sfx('timpano', ini['06'] + 0.1, dur=round(max(0.3, T['six6'] - ini['06'] - 0.15), 3)))
    S.append(sfx('whoosh', T['six6'] - 0.06, pitch=1.15))
    S.append(sfx('pop', T['six6'], pitch=1.1))
    s7 = T['seven6']
    S.append(sfx('impacto', s7))
    S.append(sfx('explosao', s7 + 0.03, gain=-9))
    E += [{'type': 'punch', 'at': round(s7, 3), 'intensity': 0.28, 'duration': 0.4},
          {'type': 'shake', 'at': round(s7, 3), 'duration': 0.6, 'intensity': 1.4},
          {'type': 'flash', 'at': round(s7, 3), 'color': 'branco', 'intensity': 0.45, 'duration': 0.1}]
    O.append({'file': OV + 'boom.png', 'at': round(s7 + 0.02, 3), 'duration': 0.7, 'x': 0.02, 'y': 0.36, 'width': 0.36})
    # Stickers nunca em cima da placa AURA >= 1000 (alto do quadro) nem do rosto.
    # Medidor vai a infinito; a porta abre sozinha com a luz de dentro.
    m3 = T['medidor3']
    S.append(sfx('brilho', m3 + 0.05, dur=1.0))
    S.append(sfx('ding', m3 + 0.5, pitch=1.3))
    S.append(sfx('whoosh', T['abre'] + 0.15, pitch=0.8))
    E.append({'type': 'flash', 'at': round(T['abre'] + 0.5, 3), 'color': 'branco', 'intensity': 0.3, 'duration': 0.15})
    O.append({'file': OV + 'wow.png', 'at': round(T['abre'] + 0.45, 3), 'duration': 0.9, 'x': 0.64, 'y': 0.4, 'width': 0.32})
    # Final: "Aura maxima!", aplausos e confete nos lados (a placa AURA >= 1000 no alto e o rosto no meio ficam limpos).
    t = palavra('07', 'xima')
    E.append({'type': 'punch', 'at': round(t if t is not None else ini['07'], 3), 'intensity': 0.16, 'duration': 0.3})
    t_fim = ini['07'] + F['07']['duracao']
    S.append(sfx('aplausos', t_fim + 0.05))
    for x in (0.0, 0.62):
        O.append({'file': OV + 'confete.png', 'at': round(t_fim, 3), 'duration': round(fim - t_fim - 0.05, 3), 'x': x, 'y': 0.1, 'width': 0.38})

    # Musica: fundo calmo; o funk entra no six seven e volta na comemoracao.
    g = -24 if voice else -20
    m_a, m_b, m_c = ini['03'] - 0.1, ini['05'] - 0.1, s7
    musica = [{'file': 'musicas/curtos/monkeys-spinning-monkeys-short.mp3', 'at': 0, 'gain_db': g, 'duration': round(m_a, 3)},
              {'file': 'musicas/curtos/funkorama-short.mp3', 'at': round(m_a, 3), 'gain_db': -19, 'duration': round(m_b - m_a, 3)},
              {'file': 'musicas/curtos/monkeys-spinning-monkeys-short.mp3', 'at': round(m_b, 3), 'gain_db': g, 'offset': round(m_a, 3),
               'duration': round(m_c - m_b, 3)},
              {'file': 'musicas/curtos/funkorama-short.mp3', 'at': round(m_c, 3), 'gain_db': -19, 'offset': round(m_b - m_a, 3)}]
    out = {'name': a.nome, 'format': 'short', 'clips': [{'source': a.cena, 'in': 0, 'out': round(fim - 0.02, 3), 'framing': 'crop'}],
           'music': musica, 'voice': voice, 'sfx': S, 'effects': E, 'captions': captions, 'overlays': O,
           'cortes': [round(c, 3) for c in cortes]}
    if a.previa:
        out['resolution'] = [540, 960]
        out['fps'] = 30
    spec = {'library': LIB.as_posix(), 'entrega': 'shorts', 'primary_source': a.cena, 'outputs': [out]}
    (HERE / a.saida).write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{a.saida}: {fim:.1f}s | {len(S)} sfx ({len(S) / fim * 60:.0f}/min) | {len(E)} efeitos | {len(O)} stickers | {len(captions)} legendas | voz: {len(voice)} falas')


if __name__ == '__main__':
    main()
