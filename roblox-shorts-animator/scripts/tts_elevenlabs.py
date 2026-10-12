"""Generate each line of a script with ElevenLabs and keep word timings for captions.

The API key is read only from the ELEVENLABS_API_KEY environment variable; it is never
written to disk or printed. Voices are resolved by name (e.g. "Roger") so a changed voice
id fails loudly instead of silently using another voice.
"""
import argparse, base64, json, os, sys, urllib.error, urllib.request
from pathlib import Path

API = 'https://api.elevenlabs.io/v1'


def request(path, body=None, key=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'application/json'},
                                 method='POST' if body is not None else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', 'replace')[:500]
        raise SystemExit(f'ElevenLabs respondeu {e.code} em {path}: {detail}')


def resolve_voice(name, key):
    voices = request('/voices', key=key)['voices']
    hits = [v for v in voices if v['name'].lower().split(' - ')[0].strip() == name.lower()]
    if not hits:
        hits = [v for v in voices if v['name'].lower().startswith(name.lower())]
    if not hits:
        raise SystemExit(f'Voz "{name}" nao encontrada na conta. Disponiveis: ' + ', '.join(sorted(v['name'] for v in voices)))
    return hits[0]['voice_id'], hits[0]['name']


def words_from_alignment(al, offset=0.0):
    """Group character timings into words: [{'w','start','end'}] (seconds)."""
    words, cur, start, end = [], '', None, None
    for ch, s, e in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if ch.isspace():
            if cur:
                words.append({'w': cur, 'start': round(start + offset, 3), 'end': round(end + offset, 3)})
            cur, start = '', None
            continue
        if start is None:
            start = s
        cur += ch; end = e
    if cur:
        words.append({'w': cur, 'start': round(start + offset, 3), 'end': round(end + offset, 3)})
    return words


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('roteiro', type=Path, help='JSON: {"vozes": {"noob": "Roger"}, "falas": [{"id": "01", "personagem": "noob", "texto": "..."}]}')
    ap.add_argument('--out', type=Path, required=True, help='pasta das falas (mp3 + falas.json)')
    ap.add_argument('--modelo', default='eleven_multilingual_v2')
    ap.add_argument('--listar-vozes', action='store_true')
    ap.add_argument('--idioma', default='pt', help='pt usa "texto"; outro idioma usa "texto_<idioma>" (ex.: texto_es), mesma voz')
    args = ap.parse_args()
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key and sys.platform == 'win32':
        # setx writes the user environment; already-running apps only see it after a restart.
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as k:
                key = winreg.QueryValueEx(k, 'ELEVENLABS_API_KEY')[0]
        except OSError:
            key = None
    if not key:
        raise SystemExit('Defina a variavel de ambiente ELEVENLABS_API_KEY (ex.: setx ELEVENLABS_API_KEY sua_chave) e abra um terminal novo.')
    if args.listar_vozes:
        for v in request('/voices', key=key)['voices']:
            print(v['voice_id'], v['name'], v.get('labels', {}))
        return
    spec = json.loads(args.roteiro.read_text(encoding='utf-8'))
    args.out.mkdir(parents=True, exist_ok=True)
    voice_ids = {p: resolve_voice(n, key) for p, n in spec['vozes'].items()}
    settings = spec.get('voice_settings', {'stability': 0.35, 'similarity_boost': 0.8, 'style': 0.45, 'use_speaker_boost': True})
    result = []
    chave = 'texto' if args.idioma == 'pt' else f'texto_{args.idioma}'
    for fala in spec['falas']:
        fala = dict(fala, texto=fala[chave])
        vid, vname = voice_ids[fala['personagem']]
        dest = args.out / f'fala-{fala["id"]}.mp3'
        meta = args.out / f'fala-{fala["id"]}.json'
        if dest.exists() and meta.exists() and json.loads(meta.read_text(encoding='utf-8')).get('texto') == fala['texto']:
            data = json.loads(meta.read_text(encoding='utf-8'))  # reuse: same text, no new credits spent
        else:
            r = request(f'/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128',
                        {'text': fala['texto'], 'model_id': args.modelo, 'voice_settings': fala.get('voice_settings', settings)}, key)
            dest.write_bytes(base64.b64decode(r['audio_base64']))
            al = r.get('alignment') or r.get('normalized_alignment')
            data = {'id': fala['id'], 'personagem': fala['personagem'], 'voz': vname, 'texto': fala['texto'],
                    'arquivo': dest.name, 'duracao': round(al['character_end_times_seconds'][-1], 3),
                    'palavras': words_from_alignment(al)}
            meta.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        result.append(data)
        print(f'{fala["id"]} {vname}: {data["duracao"]:.2f}s  {fala["texto"]}', flush=True)
    (args.out / 'falas.json').write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
