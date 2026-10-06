"""First-use setup: fetch licensed music from author and prepare short excerpts."""
import argparse, hashlib, json, shutil, urllib.request
from pathlib import Path
from media_utils import run

SKILL=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--library',type=Path)
    ap.add_argument('--title',action='append',help='Prepare selected music titles plus original SFX; default: all music')
    args=ap.parse_args()
    config=json.loads((SKILL/'config.json').read_text(encoding='utf-8'))
    if (SKILL/'config.local.json').exists():
        config.update(json.loads((SKILL/'config.local.json').read_text(encoding='utf-8')))
    lib=args.library or Path(config['library_root'])
    lib=(lib if lib.is_absolute() else SKILL/lib).resolve()
    lib.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((SKILL/'assets/audio-manifest.json').read_text(encoding='utf-8'))
    entries={}
    if (lib/'catalogo.json').exists():
        entries={r['path']:r for r in json.loads((lib/'catalogo.json').read_text(encoding='utf-8'))['assets']}
    # Full recordings must precede their excerpts.
    rows=sorted([r for r in manifest['assets'] if not args.title or r['type']=='sfx' or r.get('title') in args.title],key=lambda a:a.get('version')=='short-excerpt')
    if args.title and not any(r['type']=='music' for r in rows):
        raise ValueError('Titulo inexistente no manifesto')
    for row in rows:
        row=dict(row); dest=lib/row['path']; dest.parent.mkdir(parents=True,exist_ok=True)
        existing=entries.get(row['path'])
        digest=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        if dest.exists() and existing and digest(dest)==existing['sha256']:
            continue
        if row.get('bundled_file'):
            shutil.copy2(SKILL/row.pop('bundled_file'),dest)
        elif row.get('version')=='full':
            url=row['download_url']
            if not url.startswith('https://incompetech.com/music/royalty-free/mp3-royaltyfree/'):
                raise ValueError('Unapproved music origin')
            temp=dest.with_suffix('.part')
            with urllib.request.urlopen(url,timeout=120) as response, temp.open('wb') as f:
                shutil.copyfileobj(response,f)
            if digest(temp)!=row['sha256']:
                temp.unlink()
                raise ValueError(f'A gravação mudou na fonte; revise antes de usar: {url}')
            temp.replace(dest)
        else:
            full=next(r for r in rows if r.get('title')==row['title'] and r.get('version')=='full')
            length=min(48.,full['duration_seconds']-row['excerpt_start']-.2)
            run(['-ss',row['excerpt_start'],'-i',lib/full['path'],'-t',length,'-af',
                 f'afade=t=in:d=0.04,afade=t=out:st={length-.3}:d=0.3','-codec:a','libmp3lame','-q:a','2',dest])
            # Encoders can differ by platform. Verify the recording; hash the derived asset locally.
        row['sha256']=digest(dest); row['bytes']=dest.stat().st_size
        entries[row['path']]=row
        if row.get('attribution'):
            credits=lib/'licencas'; credits.mkdir(exist_ok=True)
            (credits/(Path(row['path']).stem+'-credito.txt')).write_text(row['attribution'],encoding='utf-8')
        (lib/'catalogo.json').write_text(json.dumps({'verified_date':manifest['verified_date'],'assets':list(entries.values())},ensure_ascii=False,indent=2),encoding='utf-8')
        print('Ready:',row['path'],flush=True)
    (lib/'catalogo.json').write_text(json.dumps({'verified_date':manifest['verified_date'],'assets':list(entries.values())},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Biblioteca pronta: {len(entries)} arquivos em {lib}')

if __name__=='__main__':main()
