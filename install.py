"""Install the portable skill in Claude Code without requiring GitHub credentials."""
import argparse, shutil, subprocess, sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--project',type=Path,help='Install into this project instead of user skills')
 ap.add_argument('--skip-deps',action='store_true',help='Use dependencies already present')
 args=ap.parse_args()
 repo=Path(__file__).resolve().parent
 base=(args.project.resolve() if args.project else Path.home())/'.claude/skills'
 dest=base/'roblox-video-editor'
 marker=dest/'.installed-by-roblox-video-editor'
 if dest.exists() and not marker.exists():
  raise SystemExit(f'Skill existente nao gerenciada por este instalador: {dest}. Preserve-a antes de instalar.')
 if not args.skip_deps:
  subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','-r',str(repo/'requirements.txt')],check=True)
 shutil.copytree(repo/'roblox-video-editor',dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','config.local.json'))
 marker.write_text('Portable install; preserves local config and downloaded audio on updates.\n',encoding='utf-8')
 print(f'Skill instalada: {dest}\nNo Claude Code: /roblox-video-editor + caminho da gameplay.\nA biblioteca de audio incluida acompanha a instalacao.')

if __name__=='__main__':main()
