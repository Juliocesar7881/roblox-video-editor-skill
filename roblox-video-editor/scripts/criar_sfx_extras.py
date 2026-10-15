"""More original sound effects, synthesized from scratch (no third-party samples).

  python criar_sfx_extras.py     -> efeitos/originais-livres/{domino-cascata,onda-mar,espuma-borbulha,vento-forte,
                                    apito-sobe,jato-agua,regador-gotas}.mp3
                                    and updates catalogo.json / catalogo.csv / audio-manifest.json

  domino-cascata   12 s  plastic tiles knocking each other, ~28 per second (cut it with 'duration')
  onda-mar         3,6 s sea wave: swell (1,2 s), crash at 1,3 s, foam receding
  espuma-borbulha  4,0 s fizzing foam with bubbles popping (science-fair volcano, soap)
  vento-forte      4,0 s steady strong wind with gusts (fan, storm)
  apito-sobe       1,5 s cartoon slide whistle going UP (something growing, inflating, rising)
  jato-agua        3,0 s garden hose spray: hissing jet with pressure flutter and droplets
  regador-gotas    2,5 s watering can: soft trickle with drops plinking on the soil
"""
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import criar_sfx_escorregador as base  # noqa: E402

SR = base.SR


def _banda(x, f0, f1, ordem=2):
    return sosfilt(butter(ordem, [f0, f1], 'band', fs=SR, output='sos'), x)


def _baixa(x, f, ordem=2):
    return sosfilt(butter(ordem, f, 'low', fs=SR, output='sos'), x)


def _alta(x, f, ordem=2):
    return sosfilt(butter(ordem, f, 'high', fs=SR, output='sos'), x)


def clique_plastico(rng):
    n = int(.035 * SR)
    t = np.arange(n) / SR
    ruido = rng.standard_normal(n) * np.exp(-t / .0025)
    corpo = sum(a * np.sin(2 * np.pi * f * (1 + rng.uniform(-.04, .04)) * t) * np.exp(-t / d)
                for f, a, d in ((2250, 1, .012), (3480, .6, .008), (5200, .3, .005)))
    baque = .5 * np.sin(2 * np.pi * 310 * t) * np.exp(-t / .006)
    return .6 * _alta(ruido, 1200) + corpo * .5 + baque


def domino_cascata(rng):
    dur = 12.0
    y = np.zeros(int(dur * SR))
    t = .02
    while t < dur - .05:
        c = clique_plastico(rng)
        base._somar(y, c, t, rng.uniform(.65, 1.0))
        t += (1 / 28) * rng.uniform(.8, 1.2)
    return base.normalizar(y)


def onda_mar(rng):
    dur = 3.6
    n = int(dur * SR)
    t = np.arange(n) / SR
    branco = rng.standard_normal(n)
    rosa = np.cumsum(branco)
    rosa = _alta(rosa - np.mean(rosa), 30)
    rosa /= base._pico(rosa)
    # Crescendo grave da onda se formando (abre o filtro), quebra em 1,3 s, espuma voltando.
    swell = _baixa(rosa, 700) * np.interp(t, [0, 1.25, 1.35, 2.2, 3.6], [0, .8, 1, .5, 0])
    quebra = _banda(branco, 300, 6000) * np.interp(t, [0, 1.25, 1.32, 1.9, 2.6], [0, 0, 1, .35, 0])
    espuma = _alta(branco, 2500) * np.interp(t, [0, 1.4, 1.8, 3.4, 3.6], [0, 0, .35, .12, 0])
    return base.normalizar(.9 * swell / base._pico(swell) + .9 * quebra / base._pico(quebra) + .5 * espuma / base._pico(espuma))


def espuma_borbulha(rng):
    dur = 4.0
    n = int(dur * SR)
    t = np.arange(n) / SR
    chiado = _banda(rng.standard_normal(n), 3000, 9000) * np.interp(t, [0, .25, 3.5, 4.0], [0, 1, 1, 0])
    y = .35 * chiado / base._pico(chiado)
    tb = 0.03
    while tb < dur - .1:
        m = int(.03 * SR)
        tt = np.arange(m) / SR
        f0 = rng.uniform(600, 1700)
        bolha = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.5 * tt / .03)) / SR) * np.exp(-tt / .008)
        base._somar(y, bolha, tb, rng.uniform(.2, .55))
        tb += rng.exponential(1 / 22)
    return base.normalizar(y)


def vento_forte(rng):
    dur = 4.0
    n = int(dur * SR)
    t = np.arange(n) / SR
    branco = rng.standard_normal(n)
    # Banda que passeia entre 450 e 1100 Hz (assobio do vento) + rajadas lentas.
    a = _banda(branco, 350, 900)
    b = _banda(branco, 700, 1500)
    mistura = np.interp(np.sin(2 * np.pi * .35 * t + 1), [-1, 1], [0, 1])
    rajada = .65 + .35 * np.sin(2 * np.pi * .6 * t) * np.sin(2 * np.pi * .23 * t + .5)
    env = np.interp(t, [0, .3, 3.6, 4.0], [0, 1, 1, 0]) * rajada
    y = (a * (1 - mistura) + b * mistura) * env
    return base.normalizar(y)


def apito_sobe(rng):
    return base.normalizar(base.apito(1.5, 380, 1700, rng))


def jato_agua(rng):
    dur = 3.0
    n = int(dur * SR)
    t = np.arange(n) / SR
    branco = rng.standard_normal(n)
    chiado = _banda(branco, 1800, 8000)
    corpo = _banda(branco, 400, 1600)
    tremor = 1 + .18 * np.sin(2 * np.pi * 9 * t) * np.sin(2 * np.pi * 1.3 * t + 1)
    env = np.interp(t, [0, .06, 2.8, 3.0], [0, 1, 1, 0]) * tremor
    y = (.8 * chiado / base._pico(chiado) + .45 * corpo / base._pico(corpo)) * env
    tb = .05
    while tb < dur - .1:  # respingos: estalinhos agudos e curtos
        m = int(.012 * SR)
        tt = np.arange(m) / SR
        g = _banda(rng.standard_normal(m), 2500, 9000) * np.exp(-tt / .003)
        base._somar(y, g / base._pico(g), tb, rng.uniform(.15, .4))
        tb += rng.exponential(1 / 30)
    return base.normalizar(y)


def regador_gotas(rng):
    dur = 2.5
    n = int(dur * SR)
    t = np.arange(n) / SR
    fio = _banda(rng.standard_normal(n), 900, 4000)
    env = np.interp(t, [0, .1, 2.2, 2.5], [0, 1, 1, 0]) * (1 + .25 * np.sin(2 * np.pi * 6 * t))
    y = .35 * fio / base._pico(fio) * env
    tb = .05
    while tb < dur - .1:  # gotas pingando na terra
        m = int(.06 * SR)
        tt = np.arange(m) / SR
        f0 = rng.uniform(900, 2200)
        gota = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 1.2 * tt / .06)) / SR) * np.exp(-tt / .012)
        base._somar(y, gota, tb, rng.uniform(.25, .6))
        tb += rng.exponential(1 / 14)
    return base.normalizar(y)


base.SONS = {
    'domino-cascata': (domino_cascata, 'domino', ['Domino', 'Clicking', 'Plastic', 'Tap']),
    'onda-mar': (onda_mar, 'onda', ['Ocean', 'Waves, surf', 'Splash']),
    'espuma-borbulha': (espuma_borbulha, 'espuma', ['Bubbling', 'Fizz', 'Liquid']),
    'vento-forte': (vento_forte, 'vento', ['Wind', 'Gust', 'Howl']),
    'apito-sobe': (apito_sobe, 'apito_sobe', ['Slide whistle', 'Cartoon', 'Rise', 'Grow']),
    'jato-agua': (jato_agua, 'jato', ['Water', 'Spray', 'Hose']),
    'regador-gotas': (regador_gotas, 'regador', ['Water', 'Drip', 'Pour']),
}

if __name__ == '__main__':
    base.main()
