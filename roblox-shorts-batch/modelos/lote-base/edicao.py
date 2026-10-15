"""Base comum das edições do lote (montar_edicao.py de cada projeto).

    import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from edicao import Edicao
    ed = Edicao(__file__)            # lê --idioma, tempos{suf}.json, falas{suf}/falas.json
    ed.legendas()                    # karaokê, nunca atravessando os cortes de tempos['cortes']
    ed.sfx('whoosh', t); ed.punch(t); ed.sticker('boom', t, 0.8, x, y, w); ed.contagem(t0)
    ed.musica('happy-alley-short.mp3')
    ed.escrever()
"""
import argparse, collections, json, sys
from pathlib import Path

LOTE = Path(__file__).resolve().parent
SKILLS = Path.home() / '.claude' / 'skills'
sys.path.insert(0, str(SKILLS / 'roblox-shorts-animator' / 'scripts'))
from legendas import legendas_karaoke  # noqa: E402

LIB = SKILLS / 'roblox-video-editor' / 'assets' / 'biblioteca-audio'
OV = (SKILLS / 'roblox-video-editor' / 'assets' / 'overlays').as_posix() + '/'
BADGE = (SKILLS / 'roblox-shorts-animator' / 'assets').as_posix() + '/'
CC = 'efeitos/capcut-convertidos/'
OL = 'efeitos/originais-livres/'
# Listas escolhidas de ouvido nos vídeos anteriores (ordem de rodízio); o resto vem do catálogo por categoria.
FX = {
    'whoosh': [CC + 'eem mp3-1.mp3', CC + 'eem mp3-4.mp3', CC + 'eem mp3-15.mp3', CC + 'eem mp3-5.mp3'],
    'pop': [CC + 'eem mp3-18.mp3', CC + 'eem mp3-24.mp3', CC + 'eem mp3-26.mp3', CC + 'eem mp3-19.mp3'],
    'clique': [CC + 'eem mp3-12.mp3', CC + 'eem mp3-6.mp3'],
    'ding': [CC + 'eem mp3-16.mp3', CC + 'eem mp3-31.mp3'],
    'brilho': [CC + 'eem mp3-52.mp3', CC + 'eem mp3-34.mp3'],
    'impacto': [CC + 'em mp3-7.mp3', CC + 'eem mp3-55.mp3'],
    'explosao': [CC + 'em mp3-8.mp3', CC + 'eem mp3-50.mp3'],
    'soco': [CC + 'em mp3-3.mp3', CC + 'em mp3-5.mp3'],
    'boing': [CC + 'eem mp3-68.mp3', CC + 'eem mp3-63.mp3', OL + 'boing-original.mp3'],
    'erro': [CC + 'eem mp3-57.mp3'],
    'erro_curto': [OL + 'erro-original.mp3'],
    'apito': [CC + 'eem mp3-35.mp3'],
    'coracao': [CC + 'eem mp3-43.mp3'],
    'timpano': [CC + 'eem mp3-45.mp3'],
    'trombone': [OL + 'trombone-curto.mp3'],
    'trombone_longo': [CC + 'eem mp3-37.mp3'],
    'engracado': [CC + 'eem mp3-60.mp3'],
    'aplausos': [CC + 'eem mp3-40.mp3', CC + 'eem mp3-54.mp3'],
    'sucesso': [OL + 'sucesso-original.mp3'],
    'harpa': [CC + 'eem mp3-32.mp3'],
    'pizzicato': [CC + 'eem mp3-33.mp3'],
    'apito_desce': [OL + 'apito-escorregador.mp3'],
    'escorregar': [OL + 'escorregar-curto.mp3', OL + 'escorregar-rapido.mp3'],
    'pum': [CC + 'eem mp3-51.mp3'],
    'campainha': [CC + 'eem mp3-23.mp3'],
    'grunhido': [CC + 'eem mp3-67.mp3'],
    'bicho': [CC + 'eem mp3-29.mp3'],
    # Originais do lote (criar_sfx_extras.py): cascata de dominó, onda do mar, espuma, vento, apito subindo,
    # jato de mangueira e regador.
    'domino': [OL + 'domino-cascata.mp3'],
    'onda': [OL + 'onda-mar.mp3'],
    'espuma': [OL + 'espuma-borbulha.mp3'],
    'vento': [OL + 'vento-forte.mp3'],
    'apito_sobe': [OL + 'apito-sobe.mp3'],
    'jato': [OL + 'jato-agua.mp3'],
    'regador': [OL + 'regador-gotas.mp3'],
    # Água e fim curtos (criar_sfx_agua.py): tocam inteiros, sem precisar cortar.
    'respingo': [OL + 'respingo-curto.mp3'],
    'mergulho': [OL + 'mergulho.mp3'],
    'bolhas': [OL + 'bolhas-curtas.mp3'],
    'boing_curto': [OL + 'boing-original.mp3'],
}
# Só sons contínuos (texturas/loops) podem ser encurtados com 'dur', e sempre com fade longo. Os outros tocam
# inteiros: efeito cortado no meio é proibido (o cliente reprovou).
CORTAVEIS = {'coracao', 'domino', 'vento', 'jato', 'regador', 'espuma', 'escorregar'}
GAIN = {'whoosh': -10, 'pop': -11, 'clique': -11, 'ding': -11, 'brilho': -12, 'impacto': -5, 'explosao': -7, 'soco': -7,
        'boing': -10, 'erro': -11, 'erro_curto': -11, 'apito': -12, 'coracao': -12, 'timpano': -9, 'trombone': -10,
        'engracado': -11, 'aplausos': -14, 'sucesso': -10, 'harpa': -12, 'pizzicato': -12, 'apito_desce': -13,
        'escorregar': -11, 'pum': -12, 'campainha': -12, 'grunhido': -12, 'bicho': -12,
        'domino': -15, 'onda': -9, 'espuma': -13, 'vento': -14,
        'apito_sobe': -13, 'jato': -15, 'regador': -15, 'respingo': -10, 'mergulho': -8, 'bolhas': -13,
        'trombone_longo': -10, 'boing_curto': -11}


class Edicao:
    def __init__(self, arquivo):
        ap = argparse.ArgumentParser()
        ap.add_argument('--idioma', default='pt')
        ap.add_argument('--previa', action='store_true')
        self.a = ap.parse_args()
        self.proj = Path(arquivo).resolve().parent
        self.idioma = self.a.idioma
        self.suf = '' if self.idioma == 'pt' else f'-{self.idioma}'
        self.roteiro = json.loads((self.proj / 'roteiro.json').read_text(encoding='utf-8'))
        self.T = json.loads((self.proj / f'tempos{self.suf}.json').read_text(encoding='utf-8'))
        self.falas = json.loads((self.proj / f'falas{self.suf}' / 'falas.json').read_text(encoding='utf-8'))
        self.F = {f['id']: f for f in self.falas}
        self.ini = self.T['falas']
        self.fim = self.T['fim']
        self.S, self.E, self.O, self.captions, self.music = [], [], [], [], []
        self._uso = collections.Counter()
        self.avisos = []
        cat = json.loads((LIB / 'catalogo.json').read_text(encoding='utf-8'))
        self.duracoes = {a['path']: float(a['duration_seconds']) for a in cat['assets']}

    def w(self, i, *alvos, n=0, fim=False):
        from comum import norm
        achou = [p for p in self.F[i]['palavras'] if any(norm(a) in norm(p['w']) for a in alvos)]
        if not achou:
            return None
        p = achou[min(n, len(achou) - 1)]
        return self.ini[i] + (p['end'] if fim else p['start'])

    def fim_fala(self, i):
        return self.ini[i] + self.F[i]['palavras'][-1]['end']

    # ---- áudio
    def sfx(self, cat, at, gain=None, dur=None, pitch=None):
        """Efeito sonoro. Toca INTEIRO; 'dur' só vale para os sons contínuos de CORTAVEIS (com fade longo).
        Efeito que não cabe até o fim do vídeo é erro (escrever() recusa): escolha um som mais curto ou adiante-o."""
        lista = FX[cat]
        i = self._uso[cat]
        self._uso[cat] += 1
        at = max(0.0, at)
        arquivo = lista[i % len(lista)]
        inteiro = self.duracoes.get(arquivo, 0) / (pitch or 1)
        row = {'file': arquivo, 'at': round(at, 3), 'gain_db': GAIN[cat] if gain is None else gain}
        if dur and dur < inteiro - 0.02:
            if cat in CORTAVEIS:
                row['duration'] = round(max(0.05, dur), 3)
                row['fade_out'] = round(min(0.6, max(0.25, dur * 0.4)), 3)
                inteiro = dur
            else:
                self.avisos.append(f'{cat} em {at:.2f}s: dur={dur:.2f} ignorado, o som toca inteiro ({inteiro:.2f}s)')
        if pitch:
            row['pitch'] = pitch
        if at + inteiro > self.fim - 0.02:
            self.avisos.append(f'ERRO {cat} em {at:.2f}s ({inteiro:.2f}s) seria cortado pelo fim do vídeo ({self.fim:.2f}s)')
        if at < self.fim - 0.05:
            self.S.append(row)
        return row

    def musica(self, nome, gain=-24, at=0.0, duracao=None, offset=None):
        row = {'file': f'musicas/curtos/{nome}', 'at': round(at, 3), 'gain_db': gain, 'fade_out': 1.2}
        if duracao:
            row['duration'] = round(duracao, 3)
        if offset:
            row['offset'] = round(offset, 3)
        self.music.append(row)

    # ---- imagem
    def punch(self, at, intensidade=0.12, dur=0.3):
        self.E.append({'type': 'punch', 'at': round(at, 3), 'intensity': intensidade, 'duration': dur})

    def zoom(self, at, dur=1.4, intensidade=0.1):
        self.E.append({'type': 'zoom', 'at': round(at, 3), 'duration': dur, 'intensity': intensidade})

    def shake(self, at, dur=0.5, intensidade=1.0):
        self.E.append({'type': 'shake', 'at': round(at, 3), 'duration': dur, 'intensity': intensidade})

    def flash(self, at, cor='branco', intensidade=0.4, dur=0.12):
        self.E.append({'type': 'flash', 'at': round(at, 3), 'color': cor, 'intensity': intensidade, 'duration': dur})

    def sticker(self, nome, at, dur, x, y, largura, bob=True):
        row = {'file': OV + f'{nome}.png', 'at': round(at, 3), 'duration': round(dur, 3), 'x': x, 'y': y, 'width': largura}
        if not bob:
            row['bob'] = False
        self.O.append(row)

    def contagem(self, t0, x=0.39, y=0.6, largura=0.22):
        """Selos 5-4-3-2-1 com clique, coração acelerado e zoom-soco leve (sem tremida)."""
        self.sfx('coracao', t0, dur=5.0)
        for n in range(5):
            t = t0 + n
            self.O.append({'file': BADGE + f'contagem-{5 - n}.png', 'at': round(t, 3), 'duration': 0.95,
                           'x': x, 'y': y, 'width': largura, 'bob': False})
            self.sfx('clique', t, gain=-9)
            self.punch(t, 0.05, 0.25)
        self.contagem_t0 = t0

    # ---- legendas
    def legendas(self):
        self.captions = legendas_karaoke(self.falas, self.ini, cortes=self.T['cortes'])
        t0 = getattr(self, 'contagem_t0', None)
        if t0 is not None:  # nada de legenda junto com os selos da contagem (mesma faixa da tela)
            self.captions = [c for c in self.captions if not (t0 <= c['start'] < t0 + 5)]
            for c in self.captions:
                if c['start'] < t0 < c['end']:
                    c['end'] = round(t0, 3)
                    c['saida'] = True
        return self.captions

    def conferir(self):
        """Recusa a edição com efeito cortado pelo fim do vídeo ou zoom/soco atravessando um corte de câmera."""
        cortes = sorted(self.T['cortes']) + [self.fim]
        for e in self.E:
            if e['type'] in ('zoom', 'punch'):
                prox = next((c for c in cortes if c > e['at'] + 0.01), self.fim)
                if e['at'] + e['duration'] > prox + 0.02:
                    self.avisos.append(f"ERRO {e['type']} em {e['at']:.2f}s ({e['duration']:.2f}s) atravessa o corte de {prox:.2f}s")
        for a in self.avisos:
            print('[edicao]', a)
        erros = [a for a in self.avisos if a.startswith('ERRO')]
        if erros:
            raise SystemExit(f'{len(erros)} problema(s) na edição (acima): nada de efeito cortado no meio nem zoom cortado')

    def escrever(self):
        self.conferir()
        if not self.captions:
            self.legendas()
        nome = self.roteiro['arquivo' if self.idioma == 'pt' else f'arquivo_{self.idioma}']
        cena = f'cena{self.suf}.mp4'
        out = {'name': nome, 'format': 'short', 'clips': [{'source': cena, 'in': 0, 'out': round(self.fim - 0.02, 3), 'framing': 'crop'}],
               'music': self.music, 'voice': [{'file': f'falas{self.suf}/{self.F[i]["arquivo"]}', 'at': round(self.ini[i], 3), 'gain_db': 0}
                                              for i in self.ini],
               'sfx': sorted(self.S, key=lambda r: r['at']), 'effects': self.E, 'captions': self.captions, 'overlays': self.O,
               'cortes': self.T['cortes']}
        if self.a.previa:
            out['resolution'] = [540, 960]
            out['fps'] = 30
        spec = {'library': LIB.as_posix(), 'entrega': 'shorts', 'primary_source': cena, 'outputs': [out]}
        saida = self.proj / f'timeline-edicao{self.suf}.json'
        saida.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'{saida.name}: {self.fim:.1f}s | {len(self.S)} sfx ({len(self.S) / self.fim * 60:.0f}/min) | {len(self.E)} efeitos | '
              f'{len(self.O)} stickers | {len(self.captions)} legendas')
