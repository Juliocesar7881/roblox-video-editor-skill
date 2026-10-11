"""Suggest commercially cleared SFX for a category, preferring sounds the timeline has used least."""
import argparse, collections, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--library', type=Path, required=True)
    ap.add_argument('--categoria', help='soco, impacto, explosao, whoosh, boing, pop, pum, ding, erro, vinheta... (omita para listar categorias)')
    ap.add_argument('--timeline', type=Path, help='timeline.json em construcao; sons ja usados vao para o fim da lista')
    ap.add_argument('--count', type=int, default=6)
    ap.add_argument('--max-duracao', type=float, default=None)
    args = ap.parse_args()
    rows = [r for r in json.loads((args.library / 'catalogo.json').read_text(encoding='utf-8'))['assets']
            if r['type'] == 'sfx' and r.get('commercial_allowed')]
    if not args.categoria:
        cats = collections.Counter(r.get('category', '?') for r in rows)
        print(json.dumps(dict(cats.most_common()), ensure_ascii=False, indent=2))
        return
    used = collections.Counter()
    if args.timeline and args.timeline.exists():
        spec = json.loads(args.timeline.read_text(encoding='utf-8-sig'))
        for o in spec.get('outputs', []):
            for group in ('sfx', 'captions', 'effects', 'overlays'):
                for row in o.get(group, []):
                    f = row.get('file') if group == 'sfx' else row.get('sfx')
                    if f:
                        used[f] += 1
    pick = [r for r in rows if r.get('category') == args.categoria
            and (args.max_duracao is None or r['duration_seconds'] <= args.max_duracao)]
    pick.sort(key=lambda r: (used[r['path']], r['duration_seconds']))
    print(json.dumps([{'file': r['path'], 'duracao': r['duration_seconds'], 'tags': r.get('tags', []),
                       'usos_na_timeline': used[r['path']], 'aviso': r.get('child_content_warning')}
                      for r in pick[:max(1, args.count)]], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
