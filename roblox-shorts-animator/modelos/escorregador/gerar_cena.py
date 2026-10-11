"""Gera studio/cena.lua (LocalScript) e tempos.json a partir dos tempos das falas.

  python gerar_cena.py            usa falas/falas.json (ElevenLabs)
  python gerar_cena.py --estimado tempos estimados pelo texto (ensaio sem voz)
"""
import argparse, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def estimar(roteiro):
    falas = []
    for f in roteiro['falas']:
        ws, t = [], 0.0
        for w in f['texto'].split():
            d = 0.12 + 0.055 * len(w)
            ws.append({'w': w, 'start': round(t, 3), 'end': round(t + d, 3)})
            t += d + (0.25 if re.search(r'[.!?,]$', w) else 0.04)
        falas.append({'id': f['id'], 'texto': f['texto'], 'duracao': round(ws[-1]['end'], 3), 'palavras': ws, 'arquivo': None})
    return falas


def palavra(fala, alvo):
    for w in fala['palavras']:
        if alvo in w['w'].lower():
            return w['start']
    raise KeyError(alvo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--estimado', action='store_true')
    a = ap.parse_args()
    roteiro = json.loads((HERE / 'roteiro.json').read_text(encoding='utf-8'))
    falas = estimar(roteiro) if a.estimado else json.loads((HERE / 'falas' / 'falas.json').read_text(encoding='utf-8'))
    F = {f['id']: f for f in falas}
    ini = {}
    t = 0.3
    ini['01'] = t; t += F['01']['duracao'] + 0.2
    ini['02'] = t; t += F['02']['duracao'] + 0.15
    ini['03'] = t; t += F['03']['duracao'] + 0.1
    contagem = t; t += 5.0
    ini['04'] = t + 0.1; t = ini['04'] + F['04']['duracao']
    corrida = ini['04'] + 0.5
    topo_vermelho = t + 0.05
    trava = topo_vermelho + 2.0
    ini['05'] = trava + 0.2; t = ini['05'] + F['05']['duracao']
    ini['06'] = t + 0.3; t = ini['06'] + F['06']['duracao']
    topo_amarelo = t + 0.05
    ini['07'] = topo_amarelo + 1.0; t = ini['07'] + F['07']['duracao']
    descida = t + 0.05
    ini['08'] = descida + 0.45
    voo = descida + 2.2
    pouso = voo + 1.6
    ini['09'] = max(pouso + 0.75, ini['08'] + F['08']['duracao'] + 0.2); t = ini['09'] + F['09']['duracao']
    fim = round(t + 0.6, 3)
    cv = ini['02'] + palavra(F['02'], 'vermelho') - 0.05
    ca = ini['02'] + palavra(F['02'], 'azul') - 0.05
    cm = ini['02'] + palavra(F['02'], 'amarelo') - 0.05

    ev = []
    E = lambda t, corpo: ev.append(f'\t{{t = {t:.3f}, f = function()\n{corpo}\n\tend}},')
    # Gancho: close baixo, surpreso, olhando para cima.
    E(0, '''		raiz.CFrame = inicio
		K.anim(noob, "idle")
		K.rosto(noob, "surpreso", 0)
		K.olhar(noob, 0, -0.8, 0)
		cam.rosto(noob, 4.8, 36, {altura = -0.6, queixo = 0.28})''')
    E(0.6, '		cam.rosto(noob, 3.9, 34, {altura = -0.5, queixo = 0.28, t = 1.6})')
    # Fala 02: um corte por escorregador, no instante da palavra.
    E(ini['02'] - 0.05, '		K.rosto(noob, "duvida")')
    E(cv, '		cam.corte(V(-14, 4.5, -11), V(-22, 6.5, 9), 58)\n		cam.mover(V(-15, 4.2, -9), V(-22, 6.5, 9), 1.1, 54)')
    E(ca, '		cam.corte(V(3, 6, -9), V(-6, 10, 22), 64)\n		cam.mover(V(3, 8, -7), V(-6, 12, 22), 1.2, 62)')
    E(cm, '		cam.corte(V(30, 3, -24), V(24, 10, 20), 58)\n		cam.mover(V(30, 5, -26), V(24, 50, 64), 1.6, 60)')
    # Fala 03 e contagem: noob grande na frente, os tres escorregadores atras.
    E(ini['03'] - 0.05, '''		K.rosto(noob, "medo")
		K.olhar(noob, 0, 0, 0.1)
		cam.corte(V(0, 4.0, -19.2), V(0, 7.2, 10), 66)
		cam.mover(V(0, 4.1, -18.2), V(0, 7.2, 10), 2.4, 64)''')
    E(contagem, '		K.tremer(noob, 4.9, 0.06)')
    for k in range(10):
        dx = -1 if k % 2 == 0 else 1
        E(contagem + k * 0.5 + 0.05, f'		K.olhar(noob, {dx}, -0.25, 0.1)')
    E(contagem + 2.5, '''		K.rosto(noob, "nervoso")
		cam.rosto(noob, 4.2, 36, {altura = -0.3})
		cam.rosto(noob, 3.4, 33, {altura = -0.3, t = 2.4})''')
    # Fala 04: escolhe o vermelho e sai correndo.
    E(ini['04'] - 0.05, '''		K.rosto(noob, "confiante")
		K.olhar(noob, -0.6, 0)
		K.anim(noob, "apontar", {loop = false})
		cam.rosto(noob, 4.4, 38, {lado = 1.2, altura = -0.4})''')
    E(corrida, '''		K.mover(noob, V(-21, 3, -6), 1.1, "correr")
		cam.seguir(raiz, V(7, 2.5, -8), 1.3)''')
    # No topo do vermelho: desce devagar ate travar.
    E(topo_vermelho, '''		raiz.CFrame = CFrame.lookAt(e1[1], e1[1] + V(0, 0, -1))
		K.rosto(noob, "feliz")
		K.deslizar(noob, meio1, 2.0)
		cam.seguir(raiz, V(8, 2.2, -5), 2.3)''')
    E(trava, '''		K.anim(noob, "sentar")
		K.rosto(noob, "duvida")
		cam.rosto(noob, 5.2, 38, {lado = 0.9, altura = 0.15, queixo = 0.3})''')
    E(ini['05'] + 0.1, '		K.olhar(noob, 0.2, 0.9)')
    # Fala 06: o amarelo gigante.
    E(ini['06'] - 0.05, '''		raiz.CFrame = K.emPe(V(22.5, 0, -18), V(24.5, 0, -26))
		K.anim(noob, "idle")
		K.rosto(noob, "medo")
		K.olhar(noob, 0.3, -1)
		cam.corte(V(21, 2.4, -25), V(24.5, 9, 6), 60)
		cam.mover(V(21.2, 2.2, -24.2), V(24.5, 12, 6), 1.6, 58)''')
    E(topo_amarelo, '''		raiz.CFrame = CFrame.lookAt(e3[1], e3[1] + V(0, 0, -1))
		K.anim(noob, "sentar")
		K.rosto(noob, "medo")
		K.olhar(noob, 0, 1)
		cam.corte(e3[1] + V(2.5, 5.5, 7), e3[1] + V(0, -26, -42), 62)''')
    E(ini['07'] - 0.15, '''		K.rosto(noob, "confiante")
		K.olhar(noob, 0, 0)
		cam.rosto(noob, 4.4, 40, {lado = 1.3, altura = 0.1})''')
    # Descida rapida, grito e voo com cambalhotas.
    E(descida, '''		K.deslizar(noob, e3, 2.2)
		cam.seguir(raiz, V(9, 3.5, -8), 2.25)''')
    E(ini['08'] - 0.1, '		K.rosto(noob, "grito")\n		K.olhar(noob, 0, 0)')
    E(voo, '''		local pouso = K.deitado(V(24, 0, -60), V(0, 0, 1))
		K.voar(noob, pouso.Position, 11, 1.6, 2, "cair", function()
			for _, tr in ipairs(noob.Humanoid.Animator:GetPlayingAnimationTracks()) do tr:Stop(0) end
			raiz.CFrame = pouso
			K.poeira(V(24, K.chao(V(24, 0, -60)) + 0.3, -60), 30)
			K.rosto(noob, "apertado", 0.05)
			cam.tremor(0.8, 0.5)
		end)
		cam.seguir(raiz, V(9.5, 2.5, 3.5), 1.6)''')
    E(pouso + 0.05, '		cam.corte(V(33, 3, -50), V(24, 1.2, -60), 58)')
    E(pouso + 0.6, '''		K.rosto(noob, "tonto")
		local c = noob.Head.Position
		cam.corte(c + V(0, 5.2, -0.2), c, 40, V(0, 0, 1))
		cam.mover(c + V(0, 4.3, -0.2), c, 2.2, 38, nil, V(0, 0, 1))''')
    E(ini['09'] + 0.2, '		K.olhar(noob, -0.4, 0.3)')

    lua = f'''-- Gerado por gerar_cena.py ({'estimado' if a.estimado else 'tempos do ElevenLabs'}). Duracao {fim:.2f}s.
local RS = game:GetService("ReplicatedStorage")
local K = require(RS:WaitForChild("AnimKit"))
local noob = workspace:WaitForChild("Noob")
local raiz = noob:WaitForChild("HumanoidRootPart")
local cam = K.camera
local V = Vector3.new
local e1 = K.caminho(workspace:WaitForChild("Escorregador1"))
local e3 = K.caminho(workspace:WaitForChild("Escorregador3"))
local inicio = raiz.CFrame
local meio1 = {{}}
for i = 1, 5 do meio1[i] = e1[i] end
K.piscar(noob)

K.rodar({{
''' + '\n'.join(ev) + f'''
}}, {fim})
'''
    (HERE / 'studio' / 'cena.lua').write_text(lua, encoding='utf-8')
    tempos = {'falas': ini, 'contagem': contagem, 'trava': trava, 'pouso': pouso, 'voo': voo,
              'descida': descida, 'topo_vermelho': topo_vermelho, 'topo_amarelo': topo_amarelo,
              'corrida': corrida, 'cortes_opcoes': [cv, ca, cm], 'fim': fim, 'estimado': a.estimado}
    (HERE / 'tempos.json').write_text(json.dumps(tempos, indent=1), encoding='utf-8')
    print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in tempos.items() if k != 'falas'}))


if __name__ == '__main__':
    main()
