"""Install the portable skills in Claude Code without requiring GitHub credentials."""
import argparse, re, shutil, subprocess, sys
from pathlib import Path

REGISTRO = Path('roblox-shorts-animator/historico/roteiros.md')
SECAO = '## Feitos com a skill'


def merge_registry(old, new):
 """Keep the script entries written locally (registrar_roteiro.py) that the repository copy does not have yet."""
 marcas = set(re.findall(r'<!-- (.+?) -->', new))
 extras = [l for l in old.splitlines() if l.startswith('- ') and (m := re.search(r'<!-- (.+?) -->', l)) and m.group(1) not in marcas]
 if not extras or SECAO not in new:
  return new
 ini = new.index(SECAO) + len(SECAO)
 prox = new.find('\n## ', ini)
 fim = len(new) if prox < 0 else prox
 return new[:ini] + new[ini:fim].rstrip('\n') + '\n' + '\n'.join(extras) + '\n' + new[fim:]


def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--project',type=Path,help='Install into this project instead of user skills')
 ap.add_argument('--skip-deps',action='store_true',help='Use dependencies already present')
 args=ap.parse_args()
 repo=Path(__file__).resolve().parent
 base=(args.project.resolve() if args.project else Path.home())/'.claude/skills'
 skills=['roblox-video-editor','roblox-shorts-animator','roblox-shorts-batch']
 for name in skills:
  dest=base/name
  if dest.exists() and not (dest/'.installed-by-roblox-video-editor').exists():
   raise SystemExit(f'Skill existente nao gerenciada por este instalador: {dest}. Preserve-a antes de instalar.')
 if not args.skip_deps:
  subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','-r',str(repo/'requirements.txt')],check=True)
 registro_local=(base/REGISTRO).read_text(encoding='utf-8') if (base/REGISTRO).exists() else ''
 for name in skills:
  dest=base/name
  shutil.copytree(repo/name,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','config.local.json','credentials'))
  (dest/'.installed-by-roblox-video-editor').write_text('Portable install; preserves local config and downloaded audio on updates.\n',encoding='utf-8')
 # O registro de roteiros cresce a cada video produzido: nao perde as linhas locais ao atualizar a skill.
 if registro_local and (base/REGISTRO).exists():
  (base/REGISTRO).write_text(merge_registry(registro_local,(base/REGISTRO).read_text(encoding='utf-8')),encoding='utf-8')
 print(f'Skills instaladas em {base}: '+', '.join(skills))
 print('No Claude Code: /roblox-video-editor + caminho da gameplay, /roblox-shorts-animator + ideia do Short, ou /roblox-shorts-batch para o lote da semana.')

if __name__=='__main__':main()
