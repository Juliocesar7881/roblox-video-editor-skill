"""Short original water and comic sounds, synthesized from scratch (no third-party samples).

  python criar_sfx_agua.py     -> efeitos/originais-livres/{respingo-curto,mergulho,bolhas-curtas,trombone-curto}.mp3
                                  and updates catalogo.json / catalogo.csv / audio-manifest.json

Every sound here ends by itself (fade built in), so it can play whole instead of being cut with 'duration':
  respingo-curto  0,6 s small splash: plop + short spray (bobber, something dropping in the water)
  mergulho        1,4 s big splash: deep thump, crash and droplets settling (someone falling in a lake)
  bolhas-curtas   1,2 s bubbles rising and popping, fading out (something under the water)
  trombone-curto  2,0 s comic "wah wah wah waaah" fail sting with vibrato on the last note
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import criar_sfx_escorregador as base  # noqa: E402
from criar_sfx_extras import _alta, _baixa, _banda  # noqa: E402

SR = base.SR


def _plop(f0, f1, dur, decai):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decai)


def _spray(dur, rng, f0=1500, f1=8000, ataque=.01):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = _banda(rng.standard_normal(n), f0, f1)
    return x / base._pico(x) * np.interp(t, [0, ataque, dur * .3, dur], [0, 1, .45, 0])


def _gotas(y, inicio, fim, taxa, rng, ganho=(.15, .4)):
    tb = inicio
    while tb < fim:
        m = int(.05 * SR)
        tt = np.arange(m) / SR
        f0 = rng.uniform(900, 2400)
        g = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 1.5 * tt / .05)) / SR) * np.exp(-tt / .01)
        base._somar(y, g, tb, rng.uniform(*ganho) * max(0.0, 1 - (tb - inicio) / max(fim - inicio, 1e-3)))
        tb += rng.exponential(1 / taxa)


def respingo_curto(rng):
    y = np.zeros(int(.6 * SR))
    base._somar(y, _plop(420, 160, .14, .045), 0, .9)
    base._somar(y, .5 * _spray(.45, rng), .01)
    _gotas(y, .08, .5, 28, rng)
    return base.normalizar(y)


def mergulho(rng):
    dur = 1.4
    y = np.zeros(int(dur * SR))
    n = int(.5 * SR)
    t = np.arange(n) / SR
    grave = _baixa(rng.standard_normal(n), 180) * np.exp(-t / .12)
    base._somar(y, grave / base._pico(grave), 0, .9)
    base._somar(y, _plop(260, 90, .3, .09), 0, .7)
    base._somar(y, .8 * _spray(1.0, rng, 700, 7000, .02), .02)
    _gotas(y, .2, 1.3, 22, rng, (.1, .3))
    t = np.arange(len(y)) / SR
    y *= np.interp(t, [0, 1.1, dur], [1, 1, 0])
    return base.normalizar(y)


def bolhas_curtas(rng):
    dur = 1.2
    y = np.zeros(int(dur * SR))
    tb = .02
    while tb < dur - .08:
        m = int(.04 * SR)
        tt = np.arange(m) / SR
        f0 = rng.uniform(350, 900)
        b = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 3 * tt / .04)) / SR) * np.exp(-tt / .012)
        base._somar(y, b, tb, rng.uniform(.25, .6) * (1 - tb / dur))
        tb += rng.exponential(1 / 16)
    t = np.arange(len(y)) / SR
    chiado = _alta(rng.standard_normal(len(y)), 3000)
    y += .06 * chiado / base._pico(chiado) * np.interp(t, [0, .1, .9, dur], [0, 1, .4, 0])
    return base.normalizar(y)


def trombone_curto(rng):
    # Quatro notas descendo (wah wah wah waaah), timbre metálico abafado; a última com vibrato e queda.
    notas = [(.0, .34, 311), (.4, .34, 294), (.8, .34, 277), (1.2, .8, 262)]
    y = np.zeros(int(2.0 * SR))
    for ini, dur, f in notas:
        n = int(dur * SR)
        t = np.arange(n) / SR
        vib = 1 + (.03 * np.sin(2 * np.pi * 6 * t) * np.clip(t / .25, 0, 1) if dur > .5 else 0)
        queda = 1 - (.06 * np.clip((t - .45) / .35, 0, 1) if dur > .5 else 0)
        fase = 2 * np.pi * np.cumsum(f * vib * queda) / SR
        som = sum(np.sin(k * fase) / k ** .9 for k in range(1, 9))
        # "Wah": filtro abrindo e fechando (surdina).
        abre = np.interp(t, [0, .06, dur * .6, dur], [.2, 1, .7, .3])
        som = _baixa(som * abre, 1800) * np.interp(t, [0, .03, dur - .08, dur], [0, 1, .85, 0])
        base._somar(y, som / base._pico(som), ini, .8)
    return base.normalizar(y)


base.SONS = {
    'respingo-curto': (respingo_curto, 'respingo', ['Splash', 'Water', 'Plop']),
    'mergulho': (mergulho, 'mergulho', ['Splash', 'Water', 'Dive', 'Fall']),
    'bolhas-curtas': (bolhas_curtas, 'bolhas', ['Bubbles', 'Underwater', 'Liquid']),
    'trombone-curto': (trombone_curto, 'trombone', ['Trombone', 'Fail', 'Cartoon', 'Sad']),
}

if __name__ == '__main__':
    base.main()
