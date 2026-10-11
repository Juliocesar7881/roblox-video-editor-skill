"""Original slide sound effects, synthesized from scratch (no third-party samples).

  python criar_sfx_escorregador.py          -> efeitos/originais-livres/escorregar-*.mp3, apito-escorregador.mp3
                                              and updates catalogo.json / catalogo.csv / audio-manifest.json

Sounds (timed for AnimKit.deslizar, which moves at constant speed and stops/launches exactly at t)
  escorregar-rapido   2,7 s  clothes rubbing a plastic slide, speeding up for 2,2 s, then the launch whoosh
                             (place it at the start of a 2,2 s K.deslizar that ends in K.voar)
  escorregar-trava    2,2 s  steady slide that grabs and stops with a rubber squeak ending exactly at 2,0 s
                             (place it at the start of a 2,0 s K.deslizar that gets stuck)
  escorregar-curto    1,0 s  short slide / slip
  apito-escorregador  1,4 s  cartoon slide whistle going down (falls, flights)

Recipe (checked with an AudioSet classifier: friction -> "Scrape", stop -> "Squeak", not noise/explosion):
narrow-band noise (~0,3 octave) that brightens with speed, stick-slip micro-grains, the hollow resonance of
the plastic body and a 17-45 Hz chatter; the squeak is a short rough tone (~1,3 kHz rising 40%); the
launch is a soft 0,6 s air sweep ("Whoosh", not "Whip"); the whistle has breath and a chiff ("Boing"-like).
"""
import csv, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, iirpeak, lfilter, sosfilt, stft, istft

sys.path.insert(0, str(Path(__file__).resolve().parent))
from media_utils import ffmpeg  # noqa: E402

SR = 44100
SKILL = Path(__file__).resolve().parents[1]
LIB = SKILL / 'assets' / 'biblioteca-audio'
DEST = LIB / 'efeitos' / 'originais-livres'
BUNDLED = SKILL / 'assets' / 'audio-original'
MODOS = ((520, 1), (1130, .8), (1900, .6), (2950, .45))  # ressonancias do corpo oco de plastico


def chaves(tempos, valores):
    """Keyframed envelope as a function of a time array (linear interpolation)."""
    return lambda t: np.interp(t, tempos, valores)


def _pico(x):
    return np.max(np.abs(x)) + 1e-12


def _passa_alta(x, f):
    return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)


def _moldar(x, centro, larg):
    """Band of width larg (octaves, gaussian) centred at centro(t), applied in the STFT domain."""
    f, t, Z = stft(x, SR, nperseg=1024, noverlap=768)
    F = np.maximum(f, 20.0)[:, None]
    _, y = istft(Z * np.exp(-0.5 * (np.log2(F / centro(t)[None, :]) / larg) ** 2), SR, nperseg=1024, noverlap=768)
    return y[:len(x)]


def _graos(n, taxa, rng, decai=.0012):
    """Stick-slip: Poisson train of tiny noise grains (taxa per second)."""
    imp = (rng.random(n) < np.clip(taxa / SR, 0, 1)) * rng.uniform(.25, 1, n)
    ker = np.exp(-np.arange(int(decai * 8 * SR)) / (decai * SR))
    return np.convolve(imp, ker)[:n] * rng.standard_normal(n)


def friccao(dur, vel, amp, rng, c0=1600, c1=2740, larg=.31, graos=.53, corpo=.41, escala=1.33, m0=17.5, m1=45.7,
            prof=.68, hp=250):
    """Clothes/skin rubbing plastic. vel(t) 0..1 brightens the band (c0 -> c1 Hz), speeds up the grains and
    the chatter (m0 -> m1 Hz); amp(t) is the loudness envelope (0 = silence)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    v = vel(t)
    base = ((1 - graos) * _passa_alta(rng.standard_normal(n), hp)
            + graos * 3 * _passa_alta(_graos(n, 200 + 1500 * v, rng), hp))
    x = _moldar(base, lambda tt: c0 * (c1 / c0) ** np.interp(tt, t, v), larg)
    cx = sum(g * lfilter(*iirpeak(f * escala, 10, fs=SR), base) for f, g in MODOS)
    x = x / _pico(x) + corpo * cx / _pico(cx)
    tremor = 1 - prof * (.5 + .5 * np.sin(2 * np.pi * np.cumsum(m0 + (m1 - m0) * v) / SR))
    return x * tremor * amp(t)


def rangido(dur=.13, f0=1320, subida=1.42, harm=5, rug=52):
    """Rubber squeak: short rough tone that jumps up ~40% and settles back a little."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur
    f1 = f0 * subida
    f = np.where(u < .4, f0 + (f1 - f0) * u / .4, f1 - (f1 - f0) * .5 * (u - .4) / .6)
    fase = 2 * np.pi * np.cumsum(f) / SR
    tom = sum(np.sin(h * fase) / h for h in range(1, harm + 1)) * (.6 + .4 * np.sign(np.sin(2 * np.pi * rug * t)))
    env = np.clip(np.minimum(t / .01, (dur - t) / .04), 0, 1)
    return sosfilt(butter(2, [600, 8000], 'band', fs=SR, output='sos'), tom) * env


def lufada(dur, rng, f0=400, f1=1200, f2=500, larg=1.2, pico=.45):
    """Air whoosh: wide noise band that sweeps up and back down, with smooth (sin^2) swell and fade."""
    t = np.arange(int(dur * SR)) / SR
    x = _moldar(rng.standard_normal(len(t)), chaves([0, dur * pico, dur], [f0, f1, f2]), larg)
    sobe = np.sin(np.pi / 2 * np.clip(t / (dur * pico), 0, 1)) ** 2
    desce = np.sin(np.pi / 2 * np.clip((dur - t) / (dur * (1 - pico)), 0, 1)) ** 2
    return x * np.where(t < dur * pico, sobe, desce)


def apito(dur, f_ini, f_fim, rng):
    """Cartoon slide whistle going down: breathy tone with a chiff at the start and vibrato."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur
    f = f_ini * (f_fim / f_ini) ** (u ** 0.85)
    f = f * (1 - .05 * np.exp(-t / .04)) * (1 + .012 * np.sin(2 * np.pi * 5.5 * t))
    fase = 2 * np.pi * np.cumsum(f) / SR
    tom = np.sin(fase) + .3 * np.sin(2 * fase) + .05 * np.sin(3 * fase)
    sopro = _moldar(rng.standard_normal(n), lambda tt: np.interp(tt, t, f), .18)
    chiff = _moldar(rng.standard_normal(n), lambda tt: np.interp(tt, t, f) * 1.5, .8)
    env = np.clip(np.minimum(t / .025, (dur - t) / .16), 0, 1)
    return (tom * .9 + .45 * sopro / _pico(sopro) + .5 * chiff / _pico(chiff) * np.exp(-t / .05)) * env


def normalizar(x, pico_db=-1.0):
    x = x - np.mean(x)
    fade = int(.005 * SR)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    return x / _pico(x) * 10 ** (pico_db / 20)


def _somar(y, x, inicio, ganho=1.0):
    i = int(inicio * SR)
    y[i:i + len(x)] += ganho * x[:len(y) - i]


def escorregar_rapido(rng):
    y = np.zeros(int(2.7 * SR))
    atrito = friccao(2.2, chaves([0, 2.2], [.2, 1]), chaves([0, .08, 2.1, 2.2], [0, .45, 1, 0]), rng)
    _somar(y, atrito, 0)
    for t0, f0 in [(.62, 1150), (1.38, 1300)]:  # a pele "canta" no plastico de vez em quando
        r = rangido(.1, f0)
        _somar(y, r, t0, .25 * _pico(atrito) / _pico(r))
    w = lufada(.6, rng)
    _somar(y, w, 2.05, .9 * _pico(atrito) / _pico(w))  # pico do ar logo depois do lancamento (2,2 s)
    return normalizar(y)


def escorregar_trava(rng):
    y = np.zeros(int(2.2 * SR))
    atrito = friccao(2.0, chaves([0, 1.75, 2.0], [.75, .75, .25]),
                     chaves([0, .06, 1.75, 1.95, 2.0], [0, .85, .85, .3, 0]), rng)
    _somar(y, atrito, 0)
    nhec = rangido(.15, 1320)
    _somar(y, nhec, 2.0 - len(nhec) / SR, .9 * _pico(atrito) / _pico(nhec))
    return normalizar(y)


def escorregar_curto(rng):
    return normalizar(friccao(1.0, chaves([0, 1], [.6, 1]), chaves([0, .04, .8, 1], [0, 1, .8, 0]), rng))


SONS = {
    'escorregar-rapido': (escorregar_rapido, 'escorregar', ['Slide', 'Scrape', 'Friction', 'Whoosh', 'rapido']),
    'escorregar-trava': (escorregar_trava, 'escorregar', ['Slide', 'Scrape', 'Friction', 'Squeak', 'trava']),
    'escorregar-curto': (escorregar_curto, 'escorregar', ['Slide', 'Scrape', 'Friction']),
    'apito-escorregador': (lambda rng: normalizar(apito(1.4, 1650, 430, rng)), 'apito', ['Slide whistle', 'Cartoon']),
}


def exportar(nome, x):
    DEST.mkdir(parents=True, exist_ok=True)
    mp3 = DEST / f'{nome}.mp3'
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run([ffmpeg(), '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                    '-c:a', 'libmp3lame', '-q:a', '2', str(mp3)], input=pcm, check=True)
    return mp3


def pico_db(arquivo):
    s = subprocess.run([ffmpeg(), '-hide_banner', '-nostdin', '-i', str(arquivo), '-af', 'volumedetect', '-f', 'null', '-'],
                       capture_output=True, text=True, errors='replace').stderr
    return float(re.search(r'max_volume: (-?[\d.]+) dB', s)[1])


def duracao(arquivo):
    s = subprocess.run([ffmpeg(), '-hide_banner', '-i', str(arquivo)], capture_output=True, text=True, errors='replace').stderr
    h, m, x = re.search(r'Duration: (\d+):(\d+):([\d.]+)', s).groups()
    return round(int(h) * 3600 + int(m) * 60 + float(x), 2)


def main():
    cat_path = LIB / 'catalogo.json'
    cat = json.loads(cat_path.read_text(encoding='utf-8'))
    man_path = SKILL / 'assets' / 'audio-manifest.json'
    man = json.loads(man_path.read_text(encoding='utf-8'))
    for i, (nome, (gerar, categoria, tags)) in enumerate(SONS.items()):
        mp3 = exportar(nome, gerar(np.random.default_rng(1000 + i)))
        rel = f'efeitos/originais-livres/{mp3.name}'
        dados = mp3.read_bytes()
        reg = {'path': rel, 'duration_seconds': duracao(mp3), 'sha256': hashlib.sha256(dados).hexdigest(),
               'bytes': len(dados), 'type': 'sfx', 'origin': 'original procedural synthesis',
               'license_status': 'original-generated', 'commercial_allowed': True, 'content_review': 'instrumental',
               'peak_db': pico_db(mp3), 'category': categoria, 'tags': tags}
        cat['assets'] = [r for r in cat['assets'] if r['path'] != rel] + [reg]
        BUNDLED.mkdir(parents=True, exist_ok=True)
        shutil.copy2(mp3, BUNDLED / mp3.name)
        man['assets'] = [r for r in man['assets'] if r['path'] != rel] + [{
            'path': rel, 'duration_seconds': reg['duration_seconds'], 'sha256': reg['sha256'], 'bytes': reg['bytes'],
            'type': 'sfx', 'license_status': 'original-generated', 'commercial_allowed': True, 'content_review': 'instrumental',
            'distribution_allowed': True, 'bundled_file': f'assets/audio-original/{mp3.name}'}]
        print(f'{rel}: {reg["duration_seconds"]} s, pico {reg["peak_db"]} dB')
    cat_path.write_text(json.dumps(cat, ensure_ascii=False, indent=2), encoding='utf-8')
    man_path.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding='utf-8')
    with open(LIB / 'catalogo.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['path', 'type', 'category', 'duration_seconds', 'license_status', 'commercial_allowed', 'title', 'mood',
                    'bpm', 'peak_db', 'tags', 'sha256'])
        for r in cat['assets']:
            w.writerow([r['path'], r['type'], r.get('category', ''), r['duration_seconds'], r['license_status'],
                        r.get('commercial_allowed', False), r.get('title', ''), r.get('mood', ''), r.get('bpm', ''),
                        r.get('peak_db', ''), '|'.join(r.get('tags', [])), r['sha256']])


if __name__ == '__main__':
    main()
