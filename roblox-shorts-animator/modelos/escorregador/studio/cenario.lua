-- Cenario do piloto "Qual escorregador e o mais rapido?" (modo edicao, via execute_luau).
local RS = game:GetService("ReplicatedStorage")
local K = require(RS:WaitForChild("AnimKit"):Clone())

for _, nome in ipairs({ "Cenario", "Noob", "Escorregador1", "Escorregador2", "Escorregador3" }) do
	local o = workspace:FindFirstChild(nome)
	if o then o:Destroy() end
end
K.visual()

local cen = Instance.new("Model")
cen.Name = "Cenario"
cen.Parent = workspace

local base = workspace:FindFirstChild("Baseplate")
if base then
	base.Color = Color3.fromRGB(96, 196, 72)
	base.Material = Enum.Material.Grass
	K.piso(base)
	local tex = base:FindFirstChildOfClass("Texture")
	if tex then tex:Destroy() end
else
	K.piso(K.bloco({ Name = "Chao", Parent = cen, Size = Vector3.new(800, 4, 800), CFrame = CFrame.new(0, -2, 0),
		Color = Color3.fromRGB(96, 196, 72), Material = Enum.Material.Grass }))
end
-- Caminho de areia na frente dos escorregadores.
K.piso(K.bloco({ Name = "Patio", Parent = cen, Size = Vector3.new(90, 0.2, 40), CFrame = CFrame.new(0, 0.1, -12),
	Color = Color3.fromRGB(255, 214, 140), Material = Enum.Material.Sand }))

-- 1: vermelho curto e reto | 2: azul em espiral | 3: amarelo gigante.
local _, e1 = K.escorregador("Escorregador1", { topo = Vector3.new(-22, 10, 18), dir = Vector3.new(0, 0, -1),
	comprimento = 18, queda = 9.3, cor = Color3.fromRGB(235, 45, 45), corBorda = Color3.fromRGB(255, 255, 255), segmentos = 8 })
local _, e2 = K.escorregador("Escorregador2", { topo = Vector3.new(0, 17, 22), dir = Vector3.new(0, 0, -1),
	comprimento = 44, queda = 16.3, cor = Color3.fromRGB(40, 120, 255), corBorda = Color3.fromRGB(255, 255, 255),
	segmentos = 28, curva = 360 })
local _, e3 = K.escorregador("Escorregador3", { topo = Vector3.new(24, 48, 64), dir = Vector3.new(0, 0, -1),
	comprimento = 74, queda = 47.3, cor = Color3.fromRGB(255, 205, 30), corBorda = Color3.fromRGB(255, 120, 0),
	segmentos = 18, largura = 7 })

-- Placas com os numeros 1, 2 e 3.
local function placa(n, pos, cor)
	local p = K.bloco({ Name = "Placa" .. n, Parent = cen, Size = Vector3.new(5, 5, 0.6), CFrame = CFrame.new(pos),
		Color = cor })
	local poste = K.bloco({ Name = "Poste", Parent = cen, Size = Vector3.new(0.6, pos.Y, 0.6),
		CFrame = CFrame.new(pos.X, pos.Y / 2 - 2.5, pos.Z + 0.4), Color = Color3.fromRGB(90, 60, 40) })
	local g = Instance.new("SurfaceGui")
	g.Face = Enum.NormalId.Front
	g.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	g.PixelsPerStud = 60
	g.LightInfluence = 0
	g.Parent = p
	local t = Instance.new("TextLabel")
	t.Size = UDim2.fromScale(1, 1)
	t.BackgroundTransparency = 1
	t.Text = tostring(n)
	t.TextScaled = true
	t.Font = Enum.Font.FredokaOne
	t.TextColor3 = Color3.new(1, 1, 1)
	local st = Instance.new("UIStroke")
	st.Thickness = 8
	st.Color = Color3.new(0, 0, 0)
	st.Parent = t
	t.Parent = g
	-- A frente da Part (Front = -Z) ja aponta para a camera, que fica em -Z.
	return p, poste
end
placa(1, Vector3.new(-30, 9, 4), Color3.fromRGB(235, 45, 45))
placa(2, Vector3.new(-9, 9, 4), Color3.fromRGB(40, 120, 255))
placa(3, Vector3.new(14, 9, 4), Color3.fromRGB(255, 170, 0))

-- Arvores e nuvens.
local function arvore(pos, s)
	K.bloco({ Name = "Tronco", Parent = cen, Size = Vector3.new(1.6, 6, 1.6) * s, CFrame = CFrame.new(pos + Vector3.new(0, 3 * s, 0)),
		Color = Color3.fromRGB(120, 80, 45), Material = Enum.Material.Wood })
	local copa = K.bloco({ Name = "Copa", Parent = cen, Size = Vector3.new(7, 7, 7) * s, CFrame = CFrame.new(pos + Vector3.new(0, 8 * s, 0)),
		Color = Color3.fromRGB(60, 170, 60) })
	copa.Shape = Enum.PartType.Ball
end
for _, a in ipairs({ { -48, 30, 1.2 }, { -55, -5, 1 }, { 50, 20, 1.3 }, { 58, -10, 1 }, { -40, 60, 1.5 }, { 5, 85, 1.6 }, { 52, 95, 1.4 } }) do
	arvore(Vector3.new(a[1], 0, a[2]), a[3])
end
local rng = Random.new(7)
for i = 1, 14 do
	local c = K.bloco({ Name = "Nuvem", Parent = cen, Size = Vector3.new(rng:NextNumber(14, 26), rng:NextNumber(4, 7), rng:NextNumber(8, 14)),
		CFrame = CFrame.new(rng:NextNumber(-140, 140), rng:NextNumber(70, 110), rng:NextNumber(60, 200)),
		Color = Color3.new(1, 1, 1), CastShadow = false })
	c.Material = Enum.Material.SmoothPlastic
end
-- Baloes coloridos (como nas referencias).
local corBal = { Color3.fromRGB(255, 70, 90), Color3.fromRGB(70, 200, 255), Color3.fromRGB(255, 220, 40), Color3.fromRGB(120, 230, 90), Color3.fromRGB(200, 110, 255) }
for i = 1, 14 do
	local x = -42 + i * 6 + rng:NextNumber(-1.5, 1.5)
	local z = 30 + rng:NextNumber(-4, 8)
	local alt = rng:NextNumber(14, 24)
	local b = K.bloco({ Name = "Balao", Parent = cen, Size = Vector3.new(3.2, 3.2, 3.2), CFrame = CFrame.new(x, alt, z),
		Color = corBal[i % #corBal + 1] })
	b.Shape = Enum.PartType.Ball
	K.bloco({ Name = "Cordao", Parent = cen, Size = Vector3.new(0.08, alt - 1.6, 0.08), CFrame = CFrame.new(x, (alt - 1.6) / 2, z),
		Color = Color3.fromRGB(240, 240, 240) })
end
-- Blocos coloridos de playground no fundo.
local cores = { Color3.fromRGB(255, 90, 160), Color3.fromRGB(120, 220, 255), Color3.fromRGB(255, 230, 80), Color3.fromRGB(170, 110, 255) }
for i = 1, 10 do
	K.bloco({ Name = "Cubo", Parent = cen, Size = Vector3.new(4, 4, 4), CFrame = CFrame.new(-60 + i * 12, 2, 40 + (i % 3) * 6) * CFrame.Angles(0, math.rad(i * 17), 0),
		Color = cores[i % #cores + 1] })
end

-- Noob na frente do escorregador azul, olhando para a camera (-Z).
-- Em pe sobre a areia (o chao vem do raycast nos pisos: os pes nunca afundam).
K.criarNoob("Noob", K.emPe(Vector3.new(0, 0, -12), Vector3.new(0, 0, -20)))
print("cenario ok", #e1, #e2, #e3)
