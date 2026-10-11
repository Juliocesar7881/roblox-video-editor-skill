"""Mouth envelope for lip-sync: the real voice volume of a line, one digit (0-9) per video frame.

  python envelope_boca.py falas/fala-01.mp3 [--fps 30]
  from envelope_boca import envelope  ->  '0013678875420...'

The AnimKit (K.falar) opens the speaking mouth from these digits, so the mouth moves exactly when
the voice is loud and closes in pauses.
"""
import argparse, subprocess, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'roblox-video-editor' / 'scripts'))
from media_utils import ffmpeg  # noqa: E402


def envelope(caminho, fps=30, taxa=16000, piso_db=-42.0):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', str(caminho), '-f', 'f32le', '-ac', '1', '-ar', str(taxa), '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    passo = taxa // fps
    n = max(1, int(np.ceil(len(x) / passo)))
    x = np.pad(x, (0, n * passo - len(x)))
    rms = np.sqrt(np.mean(x.reshape(n, passo) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    topo = np.percentile(db, 95)
    # Range of ~30 dB below the loud parts maps to an open mouth; below the floor it stays closed.
    v = np.clip((db - max(piso_db, topo - 30)) / max(1e-6, topo - max(piso_db, topo - 30)), 0, 1)
    # Light smoothing (a mouth cannot snap open/closed in 1 frame) while keeping syllable pulses.
    v = np.convolve(v, [0.25, 0.5, 0.25], mode='same')
    return ''.join(str(int(round(a * 9))) for a in v)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('audio', type=Path)
    ap.add_argument('--fps', type=int, default=30)
    a = ap.parse_args()
    print(envelope(a.audio, a.fps))


if __name__ == '__main__':
    main()
