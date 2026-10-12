"""Produz o Short nos dois idiomas de uma vez (portugues e espanhol, mesma voz) e so termina com os dois MP4.

  python fazer_bilingue.py PROJETO [--idiomas pt es] [--so-conferir]

Para cada idioma do roteiro (roteiro.json "idiomas", padrao pt e es), dentro de PROJETO:
  1. alinha as falas se falas{suf}/falas.json nao existir (alinhar_falas.py);
  2. gera a cena e roda a auditoria no Studio: precisa dar total 0 em [auditoria] e [camera];
  3. grava (sem auditoria), regravando se a captura perder quadros, e processa para cena{suf}.mp4;
  4. monta a edicao (montar_edicao.py --idioma), revisa as legendas (total 0) e renderiza em final-{idioma}/;
  5. copia o MP4 final para a raiz do projeto.
No fim confere: cada idioma tem o MP4 final e publicacao{suf}.txt. Falta algo -> sai com erro e diz o que.
O projeto precisa ter gerar_cena.py e montar_edicao.py com --idioma (como os modelos da skill) e
falas{suf}/fala-XX.mp3 de cada idioma (ElevenLabs, voz Roger; so o idioma muda).
--so-conferir: so a conferencia final (nao grava nada).
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EDITOR = AQUI.parent.parent / 'roblox-video-editor' / 'scripts'
QUADROS_MIN_POR_S = 50  # captura abaixo disso (GPU ocupada) e regravada


def rodar(cmd, cwd, **kw):
    print('>', ' '.join(str(c) for c in cmd), flush=True)
    return subprocess.run([str(c) for c in cmd], cwd=cwd, text=True, encoding='utf-8', errors='replace', **kw)


def auditar(proj, suf):
    rodar([sys.executable, AQUI / 'studio_runscript.py', 'montar', '--kit', '--cenario', 'studio/cenario.lua',
           '--cena', f'studio/cena{suf}.lua', '--play', '--saida', f'studio/pipeline{suf}.lua'], proj, check=True,
          capture_output=True)
    r = rodar([sys.executable, AQUI / 'studio_runscript.py', 'rodar', f'studio/pipeline{suf}.lua', '--place', 'studio/base.rbxlx'],
              proj, capture_output=True, timeout=600)
    linhas = [l for l in r.stdout.splitlines() if l.startswith(('[auditoria]', '[camera]'))]
    print('\n'.join(linhas[-12:]))
    totais = [int(m.group(1)) for l in linhas for m in [re.search(r'total (\d+)', l)] if m]
    return len(totais) == 2 and sum(totais) == 0


def gravar(proj, idioma, suf):
    tempos = json.loads((proj / f'tempos{suf}.json').read_text(encoding='utf-8'))
    rodar([sys.executable, 'gerar_cena.py', '--idioma', idioma, '--sem-auditoria'], proj, check=True, capture_output=True)
    rodar([sys.executable, AQUI / 'studio_runscript.py', 'montar', '--kit', '--cenario', 'studio/cenario.lua',
           '--cena', f'studio/cena{suf}.lua', '--play', '--saida', f'studio/pipeline{suf}.lua'], proj, check=True,
          capture_output=True)
    minimo = QUADROS_MIN_POR_S * tempos['fim']
    for tentativa in range(1, 5):
        rodar([sys.executable, AQUI / 'studio_runscript.py', 'rodar', f'studio/pipeline{suf}.lua', '--place', 'studio/base.rbxlx',
               '--gravar', f'studio/viewport{suf}.mp4', '--frente'], proj, capture_output=True, timeout=600)
        n = json.loads((proj / 'studio' / f'viewport{suf}.json').read_text(encoding='utf-8'))['recebidos']
        print(f'{idioma}: tentativa {tentativa}, {n} quadros (minimo {minimo:.0f})')
        if n >= minimo:
            break
    else:
        raise SystemExit(f'{idioma}: captura sempre abaixo de {minimo:.0f} quadros (GPU ocupada?)')
    sys.path.insert(0, str(AQUI))
    import captura_janela
    captura_janela.processar(str(proj / 'studio' / f'viewport{suf}.mp4'), str(proj / f'cena{suf}.mp4'), 0.8, tempos['fim'])
    rodar([sys.executable, 'gerar_cena.py', '--idioma', idioma], proj, check=True, capture_output=True)  # volta a cena com auditoria


def editar(proj, idioma, suf):
    rodar([sys.executable, 'montar_edicao.py', '--idioma', idioma], proj, check=True)
    tl = f'timeline-edicao{suf}.json'
    r = rodar([sys.executable, EDITOR / 'revisar_legendas.py', tl], proj, capture_output=True)
    print(r.stdout.strip())
    if r.returncode:
        raise SystemExit(f'{idioma}: legendas com problema (acima); corrija e rode de novo')
    saida = proj / f'final-{idioma}'
    if saida.exists():
        shutil.rmtree(saida)
    rodar([sys.executable, EDITOR / 'renderizar.py', tl, '--out', saida.name], proj, check=True)
    nome = json.loads((proj / tl).read_text(encoding='utf-8'))['outputs'][0]['name']
    shutil.copy2(saida / nome, proj / nome.upper().replace('.MP4', '.mp4'))


def conferir(proj, roteiro, idiomas):
    faltando = []
    for idioma in idiomas:
        suf = '' if idioma == 'pt' else f'-{idioma}'
        nome = roteiro.get('arquivo' if idioma == 'pt' else f'arquivo_{idioma}')
        if not nome or not (proj / f'final-{idioma}' / nome).exists():
            faltando.append(f'{idioma}: MP4 final ({nome or "arquivo" + suf + " no roteiro"})')
        if not (proj / f'publicacao{suf}.txt').exists():
            faltando.append(f'{idioma}: publicacao{suf}.txt')
    return faltando


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('projeto', type=Path)
    ap.add_argument('--idiomas', nargs='+')
    ap.add_argument('--so-conferir', action='store_true')
    a = ap.parse_args()
    proj = a.projeto.resolve()
    roteiro = json.loads((proj / 'roteiro.json').read_text(encoding='utf-8'))
    idiomas = a.idiomas or roteiro.get('idiomas') or ['pt', 'es']
    if 'pt' not in idiomas or 'es' not in idiomas:
        print('AVISO: todo Short sai em portugues E espanhol; idiomas pedidos:', idiomas)
    if not a.so_conferir:
        for idioma in idiomas:
            suf = '' if idioma == 'pt' else f'-{idioma}'
            pasta = proj / f'falas{suf}'
            if not list(pasta.glob('fala-*.mp3')):
                raise SystemExit(f'{idioma}: faltam as falas em {pasta.name}/ (ElevenLabs, voz Roger, idioma {idioma})')
            if not (pasta / 'falas.json').exists():
                rodar([sys.executable, AQUI / 'alinhar_falas.py', '--idioma', idioma, 'roteiro.json', pasta.name], proj, check=True)
            rodar([sys.executable, 'gerar_cena.py', '--idioma', idioma], proj, check=True)
            if not auditar(proj, suf):
                raise SystemExit(f'{idioma}: auditoria da cena nao zerou (acima); corrija gerar_cena.py/cenario e rode de novo')
            gravar(proj, idioma, suf)
            editar(proj, idioma, suf)
    faltando = conferir(proj, roteiro, idiomas)
    if faltando:
        print('ENTREGA INCOMPLETA:\n  ' + '\n  '.join(faltando))
        sys.exit(1)
    print('Entrega completa:', ', '.join(idiomas))


if __name__ == '__main__':
    main()
