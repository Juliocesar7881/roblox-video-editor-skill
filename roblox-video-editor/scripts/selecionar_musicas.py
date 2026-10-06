"""Suggest licensed tracks that fit a mood and avoid recent repetition."""
import argparse, collections, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--library',type=Path,required=True)
    ap.add_argument('--format',choices=['long','short'],default='long')
    ap.add_argument('--mood',default='')
    ap.add_argument('--count',type=int,default=5)
    args=ap.parse_args()
    rows=json.loads((args.library/'catalogo.json').read_text(encoding='utf-8'))['assets']
    history=args.library/'historico-musicas.json'
    used=json.loads(history.read_text(encoding='utf-8')) if history.exists() else []
    counts=collections.Counter(t for export in used for t in export['titles'])
    recent={t for export in used[-8:] for t in export['titles']}
    version='full' if args.format=='long' else 'short-excerpt'
    candidates=[r for r in rows if r['type']=='music' and r.get('commercial_allowed') and r.get('version')==version]
    # Mood suitability precedes rotation; a tense cue should not win just because unused.
    candidates.sort(key=lambda r:(args.mood.lower() not in r.get('mood','').lower(),r['title'] in recent,counts[r['title']],r['title']))
    print(json.dumps([{'file':r['path'],'title':r['title'],'mood':r.get('mood'),
          'recently_used':r['title'] in recent,'prior_uses':counts[r['title']]} for r in candidates[:max(1,args.count)]],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
