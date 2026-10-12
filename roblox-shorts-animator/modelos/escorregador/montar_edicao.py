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
    # Escorregador (sons originais da skill, sincronizados com K.deslizar): o "trava" para com um rangido
    # exatamente 2,0 s depois do inicio; o "rapido" acelera por 2,2 s e solta o ar no lancamento.
    'escorregar_trava': [OL + 'escorregar-trava.mp3'],
    'escorregar_rapido': [OL + 'escorregar-rapido.mp3'],
    'apito_desce': [OL + 'apito-escorregador.mp3'],
}
GAIN = {'whoosh': -10, 'pop': -11, 'clique': -11, 'ding': -11, 'impacto': -4, 'explosao': -5, 'soco': -6,
        'boing': -9, 'erro': -10, 'apito': -11, 'coracao': -12, 'timpano': -8, 'trombone': -9, 'engracado': -11, 'erro_curto': -11,
        'escorregar_trava': -11, 'escorregar_rapido': -10, 'apito_desce': -14}
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

    # A legenda da opcao so entra no corte para ela (sem texto ate o escorregador aparecer).
    captions = legendas_karaoke(falas, ini, cortes=T['cortes_opcoes'])
    # Nada de legenda junto com os selos da contagem (mesma faixa da tela): corta o que invadir.
    c0, c1 = T['contagem'], T['contagem'] + 5
    captions = [c for c in captions if not (c0 <= c['start'] < c1)]
    for c in captions:
        if c['start'] < c0 < c['end']:
            c['end'] = round(c0, 3)
            c['saida'] = True
    voice = [] if a.estimado else [{'file': f'falas{suf}/{F[i]["arquivo"]}', 'at': round(ini[i], 3), 'gain_db': 0} for i in ini]
    S, E, O = [], [], []

    # Gancho: pop na entrada e zoom-soco na palavra "rapido".
    S.append(sfx('pop', 0.05))
    try:
        rap = ini['01'] + next(w['start'] for w in F['01']['palavras'] if 'pido' in w['w'].lower())
        E.append({'type': 'punch', 'at': round(rap, 3), 'intensity': 0.16, 'duration': 0.3})
        S.append(sfx('ding', rap))
    except StopIteration:
        pass
    # Um corte seco por opcao, com whoosh (sem flash: piscada branca no corte parecia bug).
    for k, c in enumerate(T['cortes_opcoes']):
        S.append(sfx('whoosh', c, pitch=[1.0, 1.1, 0.9][k]))
    # Rufar curto: termina antes de "Escolhe rapido!" (nenhum efeito por cima da fala).
    t_tim = T['cortes_opcoes'][2] + 0.25
    S.append(sfx('timpano', t_tim, dur=round(min(1.88, ini['03'] - t_tim), 3)))
    # "Escolhe rapido!" + contagem 5-4-3-2-1 com coracao acelerado.
    S.append(sfx('whoosh', ini['03'] - 0.3, gain=-12, dur=0.35))  # pico no corte e some antes de "Escolhe"
    # Sem tremida na contagem (pedido): so o zoom-soco leve em cada numero.
    c0 = T['contagem']
    S.append(sfx('coracao', c0, dur=5.0))
    for n in range(5):
        t = c0 + n
        O.append({'file': BADGE + f'contagem-{5 - n}.png', 'at': round(t, 3), 'duration': 0.95,
                  'x': 0.39, 'y': 0.6, 'width': 0.22, 'bob': False})
        S.append(sfx('clique', t, gain=-9))
        E.append({'type': 'punch', 'at': round(t, 3), 'intensity': 0.05, 'duration': 0.25})
    # Escolhe o vermelho e corre.
    S.append(sfx('pop', ini['04']))
    S.append(sfx('whoosh', T['corrida'] + 0.1, pitch=1.15))
    # Desce o vermelho (atrito no plastico) e trava com rangido de borracha bem no T['trava'].
    S.append(sfx('escorregar_trava', T['trava'] - 2.0))
    # "Ue... [bzt] travei?": o erro entra na pausa entre as duas palavras (o buzzer longo do CapCut,
    # no instante da trava, cobria o "Ue").
    w05 = F['05']['palavras']
    bzt = ini['05'] + w05[0]['end'] + 0.02
    S.append(sfx('erro_curto', bzt, dur=round(max(0.25, ini['05'] + w05[1]['start'] - bzt + 0.08), 3)))
    E.append({'type': 'zoom', 'at': round(T['trava'], 3), 'duration': 1.6, 'intensity': 0.12})
    O.append({'file': OV + 'interrogacao.png', 'at': round(T['trava'] + 0.1, 3), 'duration': 1.4, 'x': 0.62, 'y': 0.16, 'width': 0.3})
    S.append(sfx('engracado', ini['05'] + F['05']['duracao'] + 0.05))
    # O amarelo gigante.
    S.append(sfx('whoosh', ini['06'] - 0.05))
    S.append(sfx('timpano', ini['06'] + 0.1, gain=-9))
    # Sem sticker de gotas solto na tela: a gota de suor escorre do proprio rosto (careta 'panic').
    S.append(sfx('whoosh', T['topo_amarelo'], pitch=1.1))
    S.append(sfx('pop', ini['07']))
    # Descida (atrito acelerando + ar no lancamento), grito, voo com apito descendo e pouso.
    S.append(sfx('escorregar_rapido', T['voo'] - 2.2))
    # Velocidade na descida: tremida leve continua + zoom (sem linhas desenhadas por cima).
    E.append({'type': 'shake', 'at': round(T['descida'] + 0.2, 3), 'duration': 1.9, 'intensity': 0.35})
    E.append({'type': 'zoom', 'at': round(T['descida'] + 0.2, 3), 'duration': 1.9, 'intensity': 0.08})
    S.append(sfx('apito_desce', T['pouso'] - 1.42))
    E.append({'type': 'zoom', 'at': round(T['voo'], 3), 'duration': 1.4, 'intensity': 0.1})
    p = T['pouso']
    S.append(sfx('impacto', p))
    S.append(sfx('explosao', p + 0.03, gain=-8))
    S.append(sfx('boing', p + 0.35))
    E += [{'type': 'punch', 'at': round(p, 3), 'intensity': 0.3, 'duration': 0.4},
          {'type': 'shake', 'at': round(p, 3), 'duration': 0.6, 'intensity': 1.6},
          {'type': 'flash', 'at': round(p, 3), 'color': 'branco', 'intensity': 0.5, 'duration': 0.1}]
    O.append({'file': OV + 'boom.png', 'at': round(p, 3), 'duration': 0.8, 'x': 0.08, 'y': 0.12, 'width': 0.42})
    O.append({'file': OV + 'estrelas-tontas.png', 'at': round(p + 0.65, 3), 'duration': fim - p - 0.7, 'x': 0.22, 'y': 0.1, 'width': 0.56})
    # Final: "pelo menos foi rapido..." + trombone triste.
    S.append(sfx('trombone', ini['09'] + F['09']['duracao'] - 0.4, dur=max(0.5, fim - (ini['09'] + F['09']['duracao'] - 0.4))))

    musica = [{'file': 'musicas/curtos/monkeys-spinning-monkeys-short.mp3', 'at': 0, 'gain_db': -24 if voice else -20}]
    out = {'name': a.nome, 'format': 'short', 'clips': [{'source': a.cena, 'in': 0, 'out': round(fim - 0.02, 3), 'framing': 'crop'}],
           'music': musica, 'voice': voice, 'sfx': S, 'effects': E, 'captions': captions, 'overlays': O,
           'cortes': [round(c, 3) for c in T['cortes_opcoes']]}
    if a.previa:
        out['resolution'] = [540, 960]
        out['fps'] = 30
    spec = {'library': LIB.as_posix(), 'entrega': 'shorts', 'primary_source': a.cena, 'outputs': [out]}
    (HERE / a.saida).write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{a.saida}: {fim:.1f}s | {len(S)} sfx ({len(S) / fim * 60:.0f}/min) | {len(E)} efeitos | {len(O)} stickers | {len(captions)} legendas | voz: {len(voice)} falas')


if __name__ == '__main__':
    main()
