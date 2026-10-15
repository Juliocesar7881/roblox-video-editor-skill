"""Anota cada Short produzido no registro da skill (historico/roteiros.md), para nenhum vídeo futuro repetir a ideia.

  python registrar_roteiro.py PROJETO [PROJETO ...]

Lê roteiro.json e originalidade.json de cada projeto e acrescenta uma linha com a data, o título, a premissa,
as tentativas e o final (reviravolta). Projeto já registrado (mesmo nome de pasta) é ignorado. Sem
originalidade.json, resume pelas falas. Antes de escrever um roteiro novo, leia o registro inteiro.
"""
import datetime as dt
import json
import sys
from pathlib import Path

REGISTRO = Path(__file__).resolve().parent.parent / 'historico' / 'roteiros.md'
SECAO = '## Feitos com a skill'


def resumo(proj):
    rot = json.loads((proj / 'roteiro.json').read_text(encoding='utf-8'))
    orig = proj / 'originalidade.json'
    o = json.loads(orig.read_text(encoding='utf-8')) if orig.exists() else {}
    titulo = (rot.get('titulo') or proj.name).strip()
    data = dt.date.fromtimestamp((proj / 'roteiro.json').stat().st_mtime).isoformat()
    tentativas = o.get('tentativas')
    if isinstance(tentativas, list):
        tentativas = '; '.join(str(t) for t in tentativas)
    partes = [f'premissa: {o["premissa"]}' if o.get('premissa') else '',
              f'tentativas: {tentativas}' if tentativas else '',
              f'final: {o["reviravolta"]}' if o.get('reviravolta') else '']
    partes = [p for p in partes if p]
    if not partes:
        falas = ' / '.join(f.get('texto', '') for f in rot.get('falas', []))
        partes = [f'falas: {falas[:240]}']
    return f'- {data} · {titulo} — ' + ' | '.join(partes) + f' <!-- {proj.name} -->'


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    texto = REGISTRO.read_text(encoding='utf-8') if REGISTRO.exists() else ''
    if SECAO not in texto:
        raise SystemExit(f'{REGISTRO} sem a seção "{SECAO}"')
    novas = []
    for arg in sys.argv[1:]:
        proj = Path(arg).resolve()
        if not (proj / 'roteiro.json').exists():
            print(f'{proj.name}: sem roteiro.json, ignorado')
            continue
        if f'<!-- {proj.name} -->' in texto:
            print(f'{proj.name}: já registrado')
            continue
        novas.append(resumo(proj))
        print(f'{proj.name}: registrado')
    if novas:
        # As linhas novas entram no fim da seção "Feitos com a skill" (antes da próxima seção).
        ini = texto.index(SECAO) + len(SECAO)
        prox = texto.find('\n## ', ini)
        fim = len(texto) if prox < 0 else prox
        bloco = texto[ini:fim].rstrip('\n')
        texto = texto[:ini] + bloco + '\n' + '\n'.join(novas) + '\n' + texto[fim:]
        REGISTRO.write_text(texto, encoding='utf-8')


if __name__ == '__main__':
    main()
