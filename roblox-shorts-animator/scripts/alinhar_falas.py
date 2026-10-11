"""Word timings for voice lines that came without timestamps (e.g. downloaded from the ElevenLabs web app).

  python alinhar_falas.py PROJETO/roteiro.json PROJETO/falas
Expects falas/fala-XX.mp3 for every line of the script. Transcribes each file locally with
faster-whisper (word timestamps), checks the words against the script and writes falas/falas.json
in the same format tts_elevenlabs.py produces. The script text is kept for captions; Whisper only
provides the timing. Lines whose transcription diverges from the script are reported.
"""
import argparse, difflib, json, re, subprocess, sys, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'roblox-video-editor' / 'scripts'))
from media_utils import ffmpeg  # noqa: E402


def norm(t):
    t = unicodedata.normalize('NFD', t.lower())
    return re.sub(r'[^a-z0-9 ]', '', ''.join(c for c in t if unicodedata.category(c) != 'Mn'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('roteiro', type=Path)
    ap.add_argument('pasta', type=Path)
    ap.add_argument('--modelo', default='small')
    ap.add_argument('--voz', default='Roger (ElevenLabs)')
    a = ap.parse_args()
    import numpy as np
    from faster_whisper import WhisperModel
    rot = json.loads(a.roteiro.read_text(encoding='utf-8'))
    model = WhisperModel(a.modelo, device='cpu', compute_type='int8')
    ff = ffmpeg()
    out, avisos = [], []
    for f in rot['falas']:
        mp3 = a.pasta / f'fala-{f["id"]}.mp3'
        if not mp3.exists():
            raise SystemExit(f'Falta {mp3}')
        raw = subprocess.run([ff, '-v', 'error', '-i', str(mp3), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'],
                             capture_output=True, check=True).stdout
        audio = np.frombuffer(raw, np.float32)
        segs, _ = model.transcribe(audio, language=rot.get('idioma', 'pt'), word_timestamps=True, vad_filter=False)
        ws = [{'w': w.word.strip(), 'start': round(w.start, 3), 'end': round(w.end, 3)} for s in segs for w in s.words]
        texto = re.sub(r'\[[^\]]*\]', '', f['texto']).strip()
        tokens = texto.split()
        ouvido = ' '.join(w['w'] for w in ws)
        sim = difflib.SequenceMatcher(None, norm(texto), norm(ouvido)).ratio()
        if sim < 0.75:
            avisos.append(f'{f["id"]}: roteiro "{texto}" x ouvido "{ouvido}" ({sim:.0%})')
        if ws and len(tokens) == len(ws):
            palavras = [{'w': t, 'start': x['start'], 'end': x['end']} for t, x in zip(tokens, ws)]
        else:
            # Whisper merged/split words: spread the script words over the spoken interval.
            ini, fim = (ws[0]['start'], ws[-1]['end']) if ws else (0.0, len(audio) / 16000)
            total = sum(len(t) for t in tokens) or 1
            palavras, t0 = [], ini
            for t in tokens:
                d = (fim - ini) * len(t) / total
                palavras.append({'w': t, 'start': round(t0, 3), 'end': round(t0 + d, 3)}); t0 += d
        out.append({'id': f['id'], 'personagem': f.get('personagem', 'noob'), 'voz': a.voz, 'texto': texto,
                    'arquivo': mp3.name, 'duracao': round(len(audio) / 16000, 3), 'palavras': palavras})
        print(f'{f["id"]} {out[-1]["duracao"]:.2f}s  {ouvido}', flush=True)
    (a.pasta / 'falas.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    for w in avisos:
        print('ATENCAO:', w)
    if avisos:
        sys.exit(2)


if __name__ == '__main__':
    main()
