"""Gera studio/cena.lua (LocalScript) e tempos.json do Short "Quanta aura preciso pra passar por essa porta?".

  python gerar_cena.py [--idioma pt|es] [--sem-auditoria] [--estimado]
A timeline vem dos tempos reais das falas (falas/ ou falas-es/). Farmar aura = fazer o "six seven"
com as maos (AnimKit.sixSeven), uma mao por palavra, no instante exato da voz.
"""
import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def estimar(roteiro, chave='texto'):
    falas = []
    for f in roteiro['falas']:
        ws, t = [], 0.0
        for w in f[chave].split():
            d = 0.12 + 0.055 * len(w)
            ws.append({'w': w, 'start': round(t, 3), 'end': round(t + d, 3)})
            t += d + (0.25 if re.search(r'[.!?,]$', w) else 0.04)
        falas.append({'id': f['id'], 'texto': f[chave], 'duracao': round(ws[-1]['end'], 3), 'palavras': ws, 'arquivo': None})
    return falas


def palavras(fala, alvo):
    """Inicios de todas as palavras que contem 'alvo' (sem pontuacao, minusculas)."""
    return [w['start'] for w in fala['palavras'] if alvo in re.sub(r'[^\w]', '', w['w'].lower())]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--estimado', action='store_true')
    ap.add_argument('--sem-auditoria', action='store_true', help='gravacao final: sem o custo da auditoria')
    ap.add_argument('--idioma', default='pt')
    a = ap.parse_args()
    roteiro = json.loads((HERE / 'roteiro.json').read_text(encoding='utf-8'))
    suf = '' if a.idioma == 'pt' else f'-{a.idioma}'
    chave = 'texto' if a.idioma == 'pt' else f'texto_{a.idioma}'
    falas = estimar(roteiro, chave) if a.estimado else json.loads((HERE / f'falas{suf}' / 'falas.json').read_text(encoding='utf-8'))
    F = {f['id']: f for f in falas}
    d = lambda i: F[i]['duracao']
    fim_palavra = lambda i: F[i]['palavras'][-1]['end']

    ini = {}
    ini['01'] = 0.3
    ini['02'] = ini['01'] + d('01') + 0.25
    ini['03'] = ini['02'] + d('02') + 0.3
    medidor1 = ini['03'] + fim_palavra('03') + 0.15      # insert: 0 -> 67
    ini['04'] = medidor1 + 0.95
    medidor2 = ini['04'] + fim_palavra('04') + 0.1        # insert: 67 -> 999 (trava)
    ini['05'] = medidor2 + 1.3
    ini['06'] = ini['05'] + d('05') + 0.3
    medidor3 = ini['06'] + fim_palavra('06') + 0.3        # insert: 999 -> infinito
    abre = medidor3 + 1.0                                 # porta abre sozinha atras dele
    ini['07'] = abre + 0.9
    fim = round(ini['07'] + d('07') + 1.3, 3)

    cporta = ini['01'] + palavras(F['01'], 'porta' if a.idioma == 'pt' else 'puerta')[0] - 0.05
    facil = ini['02'] + palavras(F['02'], 'cil')[0]
    six3, seven3 = ini['03'] + palavras(F['03'], 'six')[0], ini['03'] + palavras(F['03'], 'seven')[0]
    six4 = [ini['04'] + t for t in palavras(F['04'], 'six')]
    seven4 = [ini['04'] + t for t in palavras(F['04'], 'seven')]
    six6, seven6 = ini['06'] + palavras(F['06'], 'six')[0], ini['06'] + palavras(F['06'], 'seven')[0]
    # Todos os cortes de camera (a legenda nunca atravessa um corte nem entra num inserto).
    cortes = sorted([cporta, ini['02'] - 0.05, ini['03'] - 0.05, medidor1, medidor2, ini['05'] - 0.06, medidor3, abre - 0.05,
                     ini['07'] - 0.05, six6 - 0.04] + [t - 0.04 for t in six4])

    ev = []
    E = lambda t, corpo: ev.append(f'\t{{t = {t:.3f}, f = function()\n{corpo}\n\tend}},')
    # Gancho: close baixo, curioso, olhando para cima (a placa da porta atras dele).
    E(0, '''		raiz.CFrame = inicio
		K.anim(noob, "idle", {fade = 0})
		K.rosto(noob, "surpreso", 0)
		K.olhar(noob, 0.4, -0.8, 0)
		cam.rosto(noob, 4.4, 36, {altura = -0.4, queixo = 0.3})''')
    E(0.6, '		cam.rosto(noob, 4.0, 35, {altura = -0.35, queixo = 0.3, t = 1.4})')
    # Na palavra "porta": a porta VIP e a placa AURA >= 1000, de baixo (camera entre ele e a porta).
    E(cporta, '		K.inserto(true)\n		cam.corte(V(8, 7.8, 7.2), V(8, 7.8, 20), 58)\n		cam.mover(V(8, 7.8, 8.2), V(8, 7.8, 20), 1.0, 56)')
    # "Mil de aura?!" espantado; "Facil..." confiante.
    E(ini['02'] - 0.05, '''		K.inserto(false)
		K.rosto(noob, "surpreso")
		K.olhar(noob, 0, 0)
		cam.rosto(noob, 4.0, 35, {lado = -0.6, altura = 0.25})''')
    E(facil - 0.05, '''		K.rosto(noob, "confiante")
		cam.rosto(noob, 3.6, 34, {lado = -0.6, altura = 0.25, t = 1.2})''')
    # Fala 03: six seven lento, plano medio de frente (bracos inteiros no quadro).
    E(ini['03'] - 0.05, '''		K.rosto(noob, "confiante")
		cam.rosto(noob, 6.4, 44, {altura = 0.2})
		K.sixSeven(noob, 0, 0.2)''')
    E(six3 - 0.04, '		K.sixSeven(noob, 1, 0.16)\n		aura(Color3.fromRGB(170, 90, 255), 6)')
    E(seven3 - 0.04, '		K.sixSeven(noob, -1, 0.16)')
    E(medidor1, '''		K.inserto(true)
		cam.corte(V(19, 7.4, 12.6), V(19, 7.4, 20), 38)
		medidor(67, 0.5, Color3.fromRGB(170, 90, 255))''')
    # Fala 04: um corte por "six seven" (frente baixo, lado esquerdo, lado direito), aura crescendo.
    angulos = ['cam.rosto(noob, 5.6, 44, {altura = -0.4})',
               'cam.rosto(noob, 6.4, 34, {lado = -3.6, altura = 1.6})',
               'cam.rosto(noob, 6.4, 34, {lado = 3.6, altura = 1.6})']
    E(ini['04'] - 0.06, '''		K.rosto(noob, "feliz")
		K.sixSeven(noob, 0, 0.05)''')
    for k, (t6, t7) in enumerate(zip(six4, seven4)):
        E(t6 - 0.04, f'''		K.inserto(false)
		{angulos[k % 3]}
		K.sixSeven(noob, 1, 0.1)
		aura(Color3.fromRGB(170, 90, 255), {10 + 8 * k})''')
        # O medidor no fundo dos angulos laterais sobe ao vivo a cada "six seven".
        E(t7 - 0.04, f'''		K.sixSeven(noob, -1, 0.1)
		medidor({67 + 200 * (k + 1)}, 0.3, Color3.fromRGB(170, 90, 255))''')
    E(medidor2, '''		K.inserto(true)
		K.sixSeven(noob, 0, 0.15)
		cam.corte(V(19, 7.4, 12.6), V(19, 7.4, 20), 38)
		medidor(999, 0.75, Color3.fromRGB(170, 90, 255))''')
    # Fala 05: travou em 999.
    E(ini['05'] - 0.06, '''		K.inserto(false)
		K.sixSeven(noob, nil)
		K.anim(noob, "idle", {fade = 0.05})
		K.rosto(noob, "grito")
		aura(Color3.fromRGB(170, 90, 255), 4)
		cam.rosto(noob, 3.6, 33, {altura = 0.25})''')
    # Fala 06: "So mais um..." decidido; SIX SEVEN final com soco de camera e aura dourada.
    E(ini['06'] - 0.05, '''		K.rosto(noob, "bravo")
		K.olhar(noob, 0, 0)
		cam.rosto(noob, 4.2, 35, {altura = 0.25})
		cam.rosto(noob, 3.4, 32, {altura = 0.25, t = 1.4})''')
    E(six6 - 0.04, '''		K.rosto(noob, "feliz")
		cam.rosto(noob, 5.8, 46, {altura = -0.8})
		K.sixSeven(noob, 1, 0.1)''')
    E(seven6 - 0.04, '''		K.sixSeven(noob, -1, 0.1)
		cam.soco(0.16, 0.35)
		aura(Color3.fromRGB(255, 200, 40), 40)''')
    E(medidor3, '''		K.inserto(true)
		K.sixSeven(noob, nil)
		K.anim(noob, "idle", {fade = 0.05})
		cam.corte(V(19, 7.4, 12.6), V(19, 7.4, 20), 38)
		medidor(99999, 0.5, Color3.fromRGB(255, 200, 40))''')
    # A porta abre sozinha: mesmo enquadramento do inserto da palavra "porta", agora com a luz de dentro.
    E(abre - 0.05, '''		cam.corte(V(8, 7.8, 7.2), V(8, 7.8, 20), 58)
		cam.mover(V(8, 7.6, 8.4), V(8, 7.4, 20), 1.0, 54)''')
    E(abre + 0.15, '		abrirPorta(0.7)')
    # Fala 07: aura maxima, comemora.
    E(ini['07'] - 0.05, '''		K.inserto(false)
		K.rosto(noob, "feliz")
		K.olhar(noob, 0, 0)
		K.anim(noob, "comemorar", {loop = false})
		cam.rosto(noob, 5.2, 42, {altura = 0.1})''')

    # Boca guiada pela voz real: um envelope por fala, comecando junto com o audio.
    if not a.estimado:
        sys.path.insert(0, str(Path.home() / '.claude' / 'skills' / 'roblox-shorts-animator' / 'scripts'))
        from envelope_boca import envelope
        for f in falas:
            env = envelope(HERE / f'falas{suf}' / f['arquivo'])
            E(ini[f['id']], f'		K.falar(noob, "{env}", 30)')

    lua = f'''-- Gerado por gerar_cena.py ({a.idioma}). Duracao {fim:.2f}s.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local K = require(RS:WaitForChild("AnimKit"))
local noob = workspace:WaitForChild("Noob")
local raiz = noob:WaitForChild("HumanoidRootPart")
local cam = K.camera
local V = Vector3.new
local inicio = raiz.CFrame
local porta = workspace:WaitForChild("Porta")
local tela = workspace:WaitForChild("Medidor"):WaitForChild("Tela")

-- Medidor de aura: conta ate o valor, barra e cor (99999 = infinito).
local valorAtual = 0
function medidor(alvo, t, cor)
	local de = valorAtual
	valorAtual = alvo
	local t0 = os.clock()
	local con
	con = RunService.Heartbeat:Connect(function()
		local k = math.clamp((os.clock() - t0) / t, 0, 1)
		local v = math.floor(de + (alvo - de) * k + 0.5)
		if alvo >= 99999 then v = math.floor(de + (2000 - de) * k + 0.5) end
		tela.Valor.Text = alvo >= 99999 and k >= 1 and "∞" or tostring(v)
		tela.Valor.TextColor3 = cor
		tela.Trilho.Barra.BackgroundColor3 = cor
		tela.Trilho.Barra.Size = UDim2.fromScale(math.clamp(math.abs(v) / 1000, 0, 1), 1)
		if k >= 1 then con:Disconnect() end
	end)
end

-- Aura em volta do noob (particulas); nil apaga.
local emissor = Instance.new("ParticleEmitter")
emissor.Texture = "rbxasset://textures/particles/sparkles_main.dds"
emissor.Rate = 0
emissor.Lifetime = NumberRange.new(0.6, 1.1)
emissor.Speed = NumberRange.new(1.5, 3)
emissor.SpreadAngle = Vector2.new(180, 180)
emissor.Size = NumberSequence.new({{NumberSequenceKeypoint.new(0, 0.7), NumberSequenceKeypoint.new(1, 0)}})
emissor.LightEmission = 1
emissor.Parent = raiz
function aura(cor, taxa)
	if not cor then emissor.Rate = 0 return end
	emissor.Color = ColorSequence.new(cor)
	emissor.Rate = taxa or 15
end

-- Porta abre para dentro girando na dobradica.
function abrirPorta(t)
	local h = porta:GetAttribute("Dobradica")
	local cf0 = porta.CFrame
	local rel = CFrame.new(h):Inverse() * cf0
	local t0 = os.clock()
	local con
	con = RunService.Heartbeat:Connect(function()
		local k = math.clamp((os.clock() - t0) / t, 0, 1)
		local e = TweenService:GetValue(k, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		porta.CFrame = CFrame.new(h) * CFrame.Angles(0, math.rad(-100 * e), 0) * rel
		if k >= 1 then con:Disconnect() end
	end)
end

K.piscar(noob)
K.preCarregar(noob)
K.foco(noob.Head)
K.anim(noob, "idle", {{fade = 0}})
''' + ('' if a.sem_auditoria else 'K.AUDITORIA_DETALHE = true\nK.auditar(noob)\nK.auditarCamera(noob)\n') + '''
K.rodar({
''' + '\n'.join(ev) + f'''
}}, {fim})
'''
    (HERE / 'studio' / f'cena{suf}.lua').write_text(lua, encoding='utf-8')
    tempos = {'falas': ini, 'cporta': cporta, 'facil': facil, 'six3': six3, 'seven3': seven3, 'six4': six4, 'seven4': seven4,
              'six6': six6, 'seven6': seven6, 'medidor1': medidor1, 'medidor2': medidor2, 'medidor3': medidor3, 'abre': abre,
              'cortes': cortes, 'fim': fim, 'estimado': a.estimado}
    (HERE / f'tempos{suf}.json').write_text(json.dumps(tempos, indent=1), encoding='utf-8')
    print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in tempos.items() if k != 'falas'}))


if __name__ == '__main__':
    main()
