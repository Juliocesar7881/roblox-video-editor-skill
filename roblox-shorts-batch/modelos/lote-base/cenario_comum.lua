-- Cabeçalho comum dos cenários do lote (modo edição). Cada projeto acrescenta o próprio corpo
-- (studio/cenario_corpo.lua) e o comum.py junta os dois em studio/cenario.lua.
local RS = game:GetService("ReplicatedStorage")
local K = require(RS:WaitForChild("AnimKit"):Clone())
local V = Vector3.new
local C = Color3.fromRGB
local CF = CFrame.new
local ANG = CFrame.Angles
local rad = math.rad

-- Limpa o que uma execução anterior deixou (tudo que o cenário cria fica em pastas/modelos com nome).
for _, o in ipairs(workspace:GetChildren()) do
	if o:GetAttribute("DoLote") or o.Name == "Noob" then o:Destroy() end
end
K.visual()

local cen = Instance.new("Model")
cen.Name = "Cenario"
cen:SetAttribute("DoLote", true)
cen.Parent = workspace

-- Peça básica. props: Name, Size, CFrame, Color, Material, Shape, Parent (cen por padrão),
-- Transparency, colide (false = atravessável e fora da auditoria), sombra.
local function peca(nome, tam, cf, cor, mat, forma, pai, colide)
	local b = K.bloco({ Name = nome, Parent = pai or cen, Size = tam, CFrame = cf, Color = cor,
		Material = mat or Enum.Material.SmoothPlastic })
	if forma then b.Shape = forma end
	if colide == false then
		b.CanCollide = false
	end
	return b
end
local function bola(nome, d, pos, cor, mat, pai, colide)
	return peca(nome, V(d, d, d), CF(pos), cor, mat, Enum.PartType.Ball, pai, colide)
end
-- Cilindro em pé (o eixo do cilindro do Roblox é X: gira 90 graus em Z).
local function cilindro(nome, altura, diametro, pos, cor, mat, pai, colide)
	return peca(nome, V(altura, diametro, diametro), CF(pos) * ANG(0, 0, rad(90)), cor, mat, Enum.PartType.Cylinder, pai, colide)
end
-- Esfera achatada/esticada (malha de esfera numa peça de tamanho 'escala').
local function elipse(nome, escala, cf, cor, mat, pai, colide)
	local p = peca(nome, escala, cf, cor, mat, nil, pai, colide)
	local m = Instance.new("SpecialMesh")
	m.MeshType = Enum.MeshType.Sphere
	m.Parent = p
	return p
end
-- Texto numa face (SurfaceGui), Fredoka branco com contorno.
local function texto(parte, conteudo, cor, contorno, face)
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
	t.Font = Enum.Font.FredokaOne
	t.TextColor3 = cor or Color3.new(1, 1, 1)
	local s = Instance.new("UIStroke")
	s.Thickness = 6
	s.Color = contorno or Color3.new(0, 0, 0)
	s.Parent = t
	t.Parent = g
	return g, t
end
-- Modelo com PrimaryPart ancorada e as outras peças soldadas nela (move tudo junto com PivotTo).
local function modelo(nome, pai)
	local m = Instance.new("Model")
	m.Name = nome
	m:SetAttribute("DoLote", true)
	m.Parent = pai or workspace
	return m
end
local function fechar(m, primaria, colide)
	m.PrimaryPart = primaria
	for _, p in ipairs(m:GetDescendants()) do
		if p:IsA("BasePart") then
			if colide == false then p.CanCollide = false end
			if p ~= primaria then
				local w = Instance.new("WeldConstraint")
				w.Part0, w.Part1 = primaria, p
				w.Parent = p
				p.Anchored = false
			end
		end
	end
	primaria.Anchored = true
	return m
end

-- Natureza colorida.
local function arvore(pos, s, corCopa)
	peca("Tronco", V(1.6, 6, 1.6) * s, CF(pos + V(0, 3 * s, 0)), C(120, 80, 45), Enum.Material.Wood)
	bola("Copa", 7 * s, pos + V(0, 8 * s, 0), corCopa or C(70, 185, 70))
	bola("Copa2", 4.5 * s, pos + V(1.8 * s, 10 * s, 0.8 * s), corCopa or C(90, 200, 80))
end
local CORES_FLOR = { C(255, 90, 140), C(255, 220, 60), C(160, 110, 255), C(255, 140, 50), C(80, 180, 255) }
local function flores(n, x0, x1, z0, z1, semente, evitar)
	local rng = Random.new(semente or 3)
	for i = 1, n do
		local x, z = rng:NextNumber(x0, x1), rng:NextNumber(z0, z1)
		if not (evitar and evitar(x, z)) then
			cilindro("Caule", 0.6, 0.12, V(x, 0.5, z), C(60, 150, 60), nil, cen, false)
			bola("Flor", 0.6, V(x, 0.9, z), CORES_FLOR[i % #CORES_FLOR + 1], nil, cen, false)
		end
	end
end
local function nuvensBrancas(n, semente)
	local rng = Random.new(semente or 11)
	for i = 1, n do
		local p = V(rng:NextNumber(-150, 150), rng:NextNumber(55, 95), rng:NextNumber(70, 220))
		for j = 0, 2 do
			bola("Nuvem", rng:NextNumber(10, 16), p + V(j * 7 - 7, rng:NextNumber(-1, 2), rng:NextNumber(-2, 2)), Color3.new(1, 1, 1), nil, cen, false).CastShadow = false
		end
	end
end
local function predios(n, z, semente)
	local cores = { C(255, 120, 160), C(110, 200, 255), C(255, 210, 90), C(150, 230, 120), C(255, 150, 70), C(190, 140, 255) }
	local rng = Random.new(semente or 5)
	for i = 1, n do
		local h = rng:NextNumber(16, 34)
		local x = -70 + i * (140 / n)
		local p = peca("Predio", V(12, h, 10), CF(x, h / 2, z + (i % 2) * 5), cores[i % #cores + 1])
		for y = 4, h - 3, 5 do
			for _, dx in ipairs({ -3, 3 }) do
				peca("Janela", V(2.6, 2.6, 0.3), CF(x + dx, y, z + (i % 2) * 5 - 5.1), C(170, 225, 255), Enum.Material.Glass, nil, cen, false)
			end
		end
	end
end
local function gramado(tam, cor, pos)
	local base = workspace:FindFirstChild("Baseplate")
	if base then
		base.Color = cor or C(110, 200, 80)
		base.Material = Enum.Material.Grass
		K.piso(base)
		local tex = base:FindFirstChildOfClass("Texture")
		if tex then tex:Destroy() end
	end
	return K.piso(peca("Gramado", V(tam or 120, 0.2, tam or 120), CF(pos or V(0, 0.1, 0)), cor or C(110, 200, 80), Enum.Material.Grass))
end

-- ===================================================================== corpo do projeto
