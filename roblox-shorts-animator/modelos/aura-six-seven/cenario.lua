-- Cenario "Quanta aura preciso pra passar por essa porta?" (modo edicao).
-- Placas so com numeros e a palavra AURA: servem para a versao em portugues e em espanhol.
local RS = game:GetService("ReplicatedStorage")
local K = require(RS:WaitForChild("AnimKit"):Clone())

for _, nome in ipairs({ "Cenario", "Noob", "Porta", "Medidor", "Oculos", "Corrente", "Caixa" }) do
	local o = workspace:FindFirstChild(nome)
	if o then o:Destroy() end
end
K.visual()
game:GetService("Lighting").ClockTime = 15.5

local cen = Instance.new("Model")
cen.Name = "Cenario"
cen.Parent = workspace
local V = Vector3.new
local C = Color3.fromRGB

local base = workspace:FindFirstChild("Baseplate")
if base then
	base.Color = C(96, 196, 72)
	base.Material = Enum.Material.Grass
	K.piso(base)
	local tex = base:FindFirstChildOfClass("Texture")
	if tex then tex:Destroy() end
end
-- Praca de pedra clara e tapete vermelho ate a porta.
K.piso(K.bloco({ Name = "Praca", Parent = cen, Size = V(70, 0.2, 50), CFrame = CFrame.new(0, 0.1, 0),
	Color = C(222, 220, 214), Material = Enum.Material.Slate }))
K.piso(K.bloco({ Name = "Tapete", Parent = cen, Size = V(6, 0.06, 20), CFrame = CFrame.new(8, 0.2, 9),
	Color = C(205, 30, 45), Material = Enum.Material.Fabric }))

-- Fachada do clube VIP: parede roxa, moldura dourada e a porta (dobradica na esquerda).
K.bloco({ Name = "Fachada", Parent = cen, Size = V(46, 26, 2), CFrame = CFrame.new(4, 13, 21),
	Color = C(240, 226, 200), Material = Enum.Material.SmoothPlastic })
-- Rodape escuro, faixa neon roxa no alto e janelas: fundo com detalhe nos closes (nao uma parede chapada).
K.bloco({ Name = "Rodape", Parent = cen, Size = V(46, 1.2, 2.2), CFrame = CFrame.new(4, 0.6, 20.9), Color = C(90, 70, 60) })
K.bloco({ Name = "Neon", Parent = cen, Size = V(46, 0.8, 2.3), CFrame = CFrame.new(4, 16.5, 20.8), Color = C(170, 80, 255),
	Material = Enum.Material.Neon })
for _, x in ipairs({ -14, -7, 24 }) do
	for _, y in ipairs({ 6, 12, 20 }) do
		K.bloco({ Name = "Janela", Parent = cen, Size = V(4, 3.4, 0.3), CFrame = CFrame.new(x, y, 19.95), Color = C(120, 200, 255),
			Material = Enum.Material.Glass })
	end
end
-- Colunas fora da placa (2,5 a 13,5) e do medidor (16 a 22): nada na frente do texto.
for _, x in ipairs({ 1.4, 14.6 }) do
	K.bloco({ Name = "Coluna", Parent = cen, Size = V(1.4, 15, 0.8), CFrame = CFrame.new(x, 7.5, 19.75), Color = C(255, 255, 250),
		Material = Enum.Material.Marble })
end
for _, f in ipairs({ { V(0.8, 10, 1), V(4.6, 5, 19.9) }, { V(0.8, 10, 1), V(11.4, 5, 19.9) }, { V(7.6, 0.8, 1), V(8, 10.2, 19.9) } }) do
	K.bloco({ Name = "Moldura", Parent = cen, Size = f[1], CFrame = CFrame.new(f[2]), Color = C(255, 196, 40),
		Material = Enum.Material.Metal })
end
-- Luz dourada do lado de dentro: aparece quando a porta abre (atras dela, na frente da fachada).
K.bloco({ Name = "LuzDentro", Parent = cen, Size = V(6, 9.6, 0.1), CFrame = CFrame.new(8, 4.9, 19.98), Color = C(255, 214, 110),
	Material = Enum.Material.Neon })
local porta = K.bloco({ Name = "Porta", Parent = workspace, Size = V(6, 9.6, 0.5), CFrame = CFrame.new(8, 4.9, 19.85),
	Color = C(150, 20, 60), Material = Enum.Material.SmoothPlastic })
porta:SetAttribute("Dobradica", V(5, 4.9, 19.85))
local macaneta = K.bloco({ Name = "Macaneta", Parent = porta, Size = V(0.5, 0.5, 0.5), CFrame = CFrame.new(10.2, 4.8, 19.5),
	Color = C(255, 210, 60), Material = Enum.Material.Metal })
macaneta.Shape = Enum.PartType.Ball
local solda = Instance.new("WeldConstraint")
solda.Part0, solda.Part1 = porta, macaneta
solda.Parent = porta
macaneta.Anchored = false

local function texto(parte, face, conteudo, cor, contorno, fonte)
	local g = Instance.new("SurfaceGui")
	g.Face = face or Enum.NormalId.Front
	g.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	g.PixelsPerStud = 50
	g.LightInfluence = 0
	g.Parent = parte
	local t = Instance.new("TextLabel")
	t.Name = "Texto"
	t.Size = UDim2.fromScale(1, 1)
	t.BackgroundTransparency = 1
	t.Text = conteudo
	t.TextScaled = true
	t.Font = fonte or Enum.Font.FredokaOne
	t.TextColor3 = cor or Color3.new(1, 1, 1)
	local s = Instance.new("UIStroke")
	s.Thickness = 6
	s.Color = contorno or Color3.new(0, 0, 0)
	s.Parent = t
	t.Parent = g
	return g, t
end

-- Placa grande em cima da porta: AURA >= 1000. Fica NA FRENTE das colunas (frente em z 19,0 contra
-- 19,35 das colunas): de nenhum angulo a coluna passa na frente do texto.
local placa = K.bloco({ Name = "PlacaAura", Parent = cen, Size = V(11, 3.4, 0.6), CFrame = CFrame.new(8, 13.2, 19.3),
	Color = C(20, 14, 40), Material = Enum.Material.Neon })
texto(placa, Enum.NormalId.Front, "AURA ≥ 1000", C(255, 220, 80), C(120, 40, 200))

-- Medidor de aura (atualizado pela cena): numero grande + barra.
local medidor = K.bloco({ Name = "Medidor", Parent = workspace, Size = V(6, 4.4, 0.6), CFrame = CFrame.new(19, 7.5, 19.7),
	Color = C(20, 14, 40), Material = Enum.Material.SmoothPlastic })
do
	local g = Instance.new("SurfaceGui")
	g.Name = "Tela"
	g.Face = Enum.NormalId.Front
	g.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	g.PixelsPerStud = 60
	g.LightInfluence = 0
	g.Parent = medidor
	local titulo = Instance.new("TextLabel")
	titulo.Name = "Titulo"
	titulo.Size = UDim2.fromScale(1, 0.28)
	titulo.BackgroundTransparency = 1
	titulo.Text = "AURA"
	titulo.TextScaled = true
	titulo.Font = Enum.Font.FredokaOne
	titulo.TextColor3 = C(200, 160, 255)
	titulo.Parent = g
	local valor = Instance.new("TextLabel")
	valor.Name = "Valor"
	valor.Position = UDim2.fromScale(0, 0.26)
	valor.Size = UDim2.fromScale(1, 0.46)
	valor.BackgroundTransparency = 1
	valor.Text = "0"
	valor.TextScaled = true
	valor.Font = Enum.Font.FredokaOne
	valor.TextColor3 = Color3.new(1, 1, 1)
	local s = Instance.new("UIStroke")
	s.Thickness = 5
	s.Parent = valor
	valor.Parent = g
	local trilho = Instance.new("Frame")
	trilho.Name = "Trilho"
	trilho.Position = UDim2.fromScale(0.08, 0.78)
	trilho.Size = UDim2.fromScale(0.84, 0.13)
	trilho.BackgroundColor3 = C(60, 50, 90)
	trilho.BorderSizePixel = 0
	trilho.Parent = g
	local barra = Instance.new("Frame")
	barra.Name = "Barra"
	barra.Size = UDim2.fromScale(0, 1)
	barra.BackgroundColor3 = C(170, 90, 255)
	barra.BorderSizePixel = 0
	barra.Parent = trilho
end
K.bloco({ Name = "PosteMedidor", Parent = cen, Size = V(0.6, 5.3, 0.6), CFrame = CFrame.new(19, 2.65, 19.9), Color = C(255, 196, 40),
	Material = Enum.Material.Metal })

-- Cordoes VIP dos dois lados do tapete.
for _, x in ipairs({ 4.2, 11.8 }) do
	for i, z in ipairs({ 4, 9, 14 }) do
		K.bloco({ Name = "PosteVIP", Parent = cen, Size = V(0.5, 3, 0.5), CFrame = CFrame.new(x, 1.5, z), Color = C(255, 196, 40),
			Material = Enum.Material.Metal })
		if i < 3 then
			K.bloco({ Name = "Cordao", Parent = cen, Size = V(0.25, 0.25, 5), CFrame = CFrame.new(x, 2.4, z + 2.5), Color = C(200, 20, 50),
				Material = Enum.Material.Fabric })
		end
	end
end

-- Arredores: arvores, postes de luz, predios coloridos, nuvens.
local function arvore(pos, s)
	K.bloco({ Name = "Tronco", Parent = cen, Size = V(1.6, 6, 1.6) * s, CFrame = CFrame.new(pos + V(0, 3 * s, 0)),
		Color = C(120, 80, 45), Material = Enum.Material.Wood })
	local copa = K.bloco({ Name = "Copa", Parent = cen, Size = V(7, 7, 7) * s, CFrame = CFrame.new(pos + V(0, 8 * s, 0)),
		Color = C(60, 170, 60) })
	copa.Shape = Enum.PartType.Ball
end
for _, a in ipairs({ { -30, 18, 1.2 }, { -38, -4, 1 }, { 36, 14, 1.2 }, { 40, -8, 1 }, { -22, 34, 1.4 }, { 30, 34, 1.3 } }) do
	arvore(V(a[1], 0, a[2]), a[3])
end
local coresPredio = { C(255, 120, 160), C(110, 200, 255), C(255, 210, 90), C(150, 230, 120), C(255, 150, 70) }
for i = 1, 8 do
	local h = 18 + (i * 7) % 16
	K.bloco({ Name = "Predio", Parent = cen, Size = V(12, h, 10), CFrame = CFrame.new(-52 + i * 13, h / 2, 46 + (i % 2) * 6),
		Color = coresPredio[i % #coresPredio + 1] })
end
for _, x in ipairs({ -18, 22 }) do
	K.bloco({ Name = "Poste", Parent = cen, Size = V(0.5, 9, 0.5), CFrame = CFrame.new(x, 4.5, 12), Color = C(60, 60, 70), Material = Enum.Material.Metal })
	local l = K.bloco({ Name = "Luz", Parent = cen, Size = V(1.4, 1.4, 1.4), CFrame = CFrame.new(x, 9.4, 12), Color = C(255, 240, 180),
		Material = Enum.Material.Neon })
	l.Shape = Enum.PartType.Ball
end
local rng = Random.new(11)
for i = 1, 12 do
	K.bloco({ Name = "Nuvem", Parent = cen, Size = V(rng:NextNumber(14, 26), rng:NextNumber(4, 7), rng:NextNumber(8, 14)),
		CFrame = CFrame.new(rng:NextNumber(-140, 140), rng:NextNumber(60, 100), rng:NextNumber(60, 200)), Color = Color3.new(1, 1, 1),
		CastShadow = false })
end

-- Noob no tapete, entre os cordoes VIP, de costas para a porta e de frente para a camera (-Z).
K.criarNoob("Noob", K.emPe(V(8, 0, 6), V(8, 0, -10)))
print("cenario ok")
