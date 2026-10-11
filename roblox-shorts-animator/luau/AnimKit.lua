-- AnimKit: kit de cutscene para Shorts verticais feitos no Roblox Studio.
-- Instale como ModuleScript "AnimKit" em ReplicatedStorage.
--   * Modo edicao (execute_luau): criarNoob, bloco, escorregador, visual -> montam a cena e ficam salvos no place.
--   * Modo play (LocalScript em StarterPlayerScripts): rosto, anim, mover, deslizar, voar, camera, rodar.
-- A camera filma "deitada" (VERTICAL = true): o quadro 9:16 usa o viewport inteiro e o
-- gravar_studio.py desvira o video depois. O flash magenta marca o t=0 e a area do viewport.

local AnimKit = {}

local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

AnimKit.VERTICAL = true
AnimKit.ALTURA_RAIZ = 3 -- R6 em pe: centro do HumanoidRootPart acima da sola dos pes
AnimKit.ALTURA_SENTADO = 1.55 -- R6 sentado: centro do HumanoidRootPart acima do assento
AnimKit.ALTURA_DEITADO = 0.55 -- R6 deitado de costas: centro do tronco acima do chao
AnimKit.ATRASO = 0.8 -- segundos entre o flash magenta e o t=0 da timeline
AnimKit.FOV = 50 -- campo de visao HORIZONTAL do video vertical final, em graus

-- Skin das referencias: amarelo forte, azul royal e verde vivo.
AnimKit.CORES = {
	pele = Color3.fromRGB(245, 212, 34),
	camisa = Color3.fromRGB(18, 62, 222),
	calca = Color3.fromRGB(58, 172, 62),
}

-- Animacoes R6 publicadas pela propria Roblox (livres para qualquer jogo).
AnimKit.ANIM = {
	idle = 180435571, andar = 180426354, correr = 180426354, pular = 125750702, cair = 180436148,
	escalar = 180436334, sentar = 178130996, acenar = 128777973, apontar = 128853357,
	rir = 129423131, comemorar = 129423030, dancar = 182435998, dancar2 = 182436842, dancar3 = 182436935,
}

local function tween(obj, t, props, estilo, direcao)
	local tw = TweenService:Create(obj, TweenInfo.new(t, estilo or Enum.EasingStyle.Quad, direcao or Enum.EasingDirection.Out), props)
	tw:Play()
	return tw
end
AnimKit.tween = tween

--------------------------------------------------------------------------------------------
-- Montagem (modo edicao)
--------------------------------------------------------------------------------------------

function AnimKit.bloco(props)
	local p = Instance.new("Part")
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Material = props.Material or Enum.Material.SmoothPlastic
	for k, v in pairs(props) do
		if k ~= "Parent" then
			p[k] = v
		end
	end
	p.Parent = props.Parent or workspace
	return p
end

-- Rosto de desenho no estilo das referencias: olhos ovais grandes com contorno grosso, pupilas
-- pretas sem brilho, sobrancelhas grossas, bochechas, gota de suor, olhos apertados (>_<) e bocas.
-- Fica numa placa transparente soldada na frente da cabeca classica: uma SurfaceGui na propria
-- cabeca ficaria escondida dentro da malha arredondada.
AnimKit.CABECA = 1.45 -- escala da cabeca classica (1.25 = padrao do Roblox; as referencias usam cabeca maior)
AnimKit.ROSTO_TAM = 1.2 -- largura/altura da placa do rosto com a cabeca padrao (studs)
AnimKit.ROSTO_Y = 0.02 -- deslocamento vertical da placa em relacao ao centro da cabeca
AnimKit.ROSTO_Z = 0.62 -- distancia da placa ao centro da cabeca, para a frente (cabeca padrao)

local PRETO, BRANCO = Color3.new(0, 0, 0), Color3.new(1, 1, 1)
local ROSA = Color3.fromRGB(255, 120, 140)
local OLHO = { x = { E = 0.365, D = 0.635 }, y = 0.46, w = 0.25, h = 0.38 }
local BOCA_Y = 0.8

local function frame(nome, pai, cor, pos, tam, z, raio)
	local f = Instance.new("Frame")
	f.Name = nome
	f.BackgroundColor3 = cor
	f.BorderSizePixel = 0
	f.AnchorPoint = Vector2.new(0.5, 0.5)
	f.Position = pos
	f.Size = tam
	f.ZIndex = z or 1
	if raio then
		local c = Instance.new("UICorner")
		c.CornerRadius = raio == true and UDim.new(1, 0) or UDim.new(raio, 0)
		c.Parent = f
	end
	f.Parent = pai
	return f
end

local function contorno(f, esp, cor)
	local s = Instance.new("UIStroke")
	s.Thickness = esp
	s.Color = cor or PRETO
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = f
	return s
end

local function vazio(nome, pai, pos, tam, z)
	local f = frame(nome, pai, PRETO, pos, tam, z)
	f.BackgroundTransparency = 1
	return f
end

local function rostoGui(noob)
	local head = noob.Head
	for _, d in ipairs(head:GetChildren()) do
		if d:IsA("Decal") then d:Destroy() end
	end
	local velha = noob:FindFirstChild("RostoPlaca")
	if velha then velha:Destroy() end
	local placa = Instance.new("Part")
	placa.Name = "RostoPlaca"
	local k = AnimKit.CABECA / 1.25
	placa.Size = Vector3.new(AnimKit.ROSTO_TAM * k, AnimKit.ROSTO_TAM * k, 0.05)
	placa.Transparency = 1
	placa.CanCollide = false
	placa.CanQuery = false
	placa.CanTouch = false
	placa.Massless = true
	placa.CastShadow = false
	placa.Anchored = false
	placa.CFrame = head.CFrame * CFrame.new(0, AnimKit.ROSTO_Y * k, -AnimKit.ROSTO_Z * k)
	local solda = Instance.new("WeldConstraint")
	solda.Part0 = head
	solda.Part1 = placa
	solda.Parent = placa
	placa.Parent = noob

	local gui = Instance.new("SurfaceGui")
	gui.Name = "RostoGui"
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 260
	gui.LightInfluence = 0.12
	gui.Parent = placa

	for _, lado in ipairs({ "E", "D" }) do
		local x = OLHO.x[lado]
		local olho = frame("Olho" .. lado, gui, BRANCO, UDim2.fromScale(x, OLHO.y), UDim2.fromScale(OLHO.w, OLHO.h), 2, true)
		contorno(olho, 9)
		frame("Pupila", olho, PRETO, UDim2.fromScale(0.5, 0.56), UDim2.fromScale(0.32, 0.36), 3, true)
		-- Olho apertado (>_<): dois tracos que se encontram do lado de dentro.
		local fechado = vazio("Fechado" .. lado, gui, UDim2.fromScale(x, OLHO.y), UDim2.fromScale(OLHO.w, OLHO.h), 2)
		fechado.Visible = false
		local sinal = lado == "E" and 1 or -1
		for i, dy in ipairs({ -0.14, 0.14 }) do
			local t = frame("Traco" .. i, fechado, PRETO, UDim2.fromScale(0.5, 0.5 + dy), UDim2.fromScale(0.85, 0.1), 4, true)
			t.Rotation = (i == 1 and 26 or -26) * sinal
		end
		frame("Palpebra" .. lado, gui, AnimKit.CORES.pele, UDim2.fromScale(x, OLHO.y - OLHO.h / 2), UDim2.fromScale(OLHO.w + 0.05, 0), 5)
		frame("Sobrancelha" .. lado, gui, PRETO, UDim2.fromScale(x, OLHO.y - OLHO.h / 2 - 0.075), UDim2.fromScale(0.25, 0.058), 6, true)
		local boch = frame("Bochecha" .. lado, gui, Color3.fromRGB(255, 140, 105), UDim2.fromScale(lado == "E" and 0.2 or 0.8, 0.665),
			UDim2.fromScale(0.1, 0.066), 4, 0.35)
		boch.BackgroundTransparency = 0.08
	end

	-- Bocas: so uma visivel por vez.
	local bocas = vazio("Bocas", gui, UDim2.fromScale(0.5, 0.5), UDim2.fromScale(1, 1), 2)
	local p = UDim2.fromScale(0.5, BOCA_Y)
	frame("o", bocas, PRETO, p, UDim2.fromScale(0.1, 0.11), 3, true)
	frame("reta", bocas, PRETO, p, UDim2.fromScale(0.17, 0.032), 3, true)
	local grito = frame("grito", bocas, Color3.fromRGB(20, 8, 8), UDim2.fromScale(0.5, BOCA_Y + 0.01), UDim2.fromScale(0.2, 0.25), 3, true)
	frame("Lingua", grito, ROSA, UDim2.fromScale(0.5, 0.8), UDim2.fromScale(0.52, 0.26), 4, true)
	local lingua = frame("lingua", bocas, Color3.fromRGB(20, 8, 8), p, UDim2.fromScale(0.15, 0.085), 3, 0.4)
	contorno(lingua, 4)
	frame("Lingua", lingua, ROSA, UDim2.fromScale(0.5, 0.72), UDim2.fromScale(0.72, 0.56), 4, 0.5)
	local dentes = frame("dentes", bocas, BRANCO, p, UDim2.fromScale(0.23, 0.12), 3, 0.32)
	contorno(dentes, 7)
	frame("Linha", dentes, Color3.fromRGB(70, 70, 70), UDim2.fromScale(0.5, 0.5), UDim2.fromScale(0.86, 0.06), 4, true)
	for _, nome in ipairs({ "sorriso", "aberto" }) do
		local larg = nome == "sorriso" and 0.2 or 0.26
		local alt = nome == "sorriso" and 0.075 or 0.12
		local caixa = vazio(nome, bocas, UDim2.fromScale(0.5, BOCA_Y - 0.01), UDim2.fromScale(larg, alt), 3)
		caixa.ClipsDescendants = true
		local meia = frame("Meia", caixa, Color3.fromRGB(20, 8, 8), UDim2.fromScale(0.5, 0), UDim2.fromScale(1, 2), 4, true)
		if nome == "aberto" then
			frame("Lingua", meia, ROSA, UDim2.fromScale(0.5, 0.86), UDim2.fromScale(0.55, 0.2), 5, true)
		end
	end
	for _, b in ipairs(bocas:GetChildren()) do
		b.Visible = b.Name == "reta"
	end

	local suor = frame("Suor", gui, Color3.fromRGB(125, 205, 245), UDim2.fromScale(0.85, 0.36), UDim2.fromScale(0.075, 0.13), 7, true)
	contorno(suor, 4, Color3.fromRGB(25, 90, 160))
	suor.Rotation = -8
	suor.Visible = false
	return gui
end

-- Chao: so pecas com o atributo Piso = true (marque chao, patios, plataformas). Assim o noob
-- nunca afunda na areia nem "pisa" em baloes, rampas ou nuvens que estejam por cima.
function AnimKit.piso(parte)
	parte:SetAttribute("Piso", true)
	return parte
end

function AnimKit.chao(pos)
	local pisos = {}
	for _, d in ipairs(workspace:GetDescendants()) do
		if d:IsA("BasePart") and d:GetAttribute("Piso") then
			pisos[#pisos + 1] = d
		end
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = pisos
	local r = workspace:Raycast(Vector3.new(pos.X, 400, pos.Z), Vector3.new(0, -800, 0), params)
	return r and r.Position.Y or 0
end

-- CFrame em pe exatamente sobre o chao em (x, z), olhando para 'olhar' (so a direcao horizontal conta).
function AnimKit.emPe(pos, olhar)
	local p = Vector3.new(pos.X, AnimKit.chao(pos) + AnimKit.ALTURA_RAIZ, pos.Z)
	if olhar then
		local alvo = Vector3.new(olhar.X, p.Y, olhar.Z)
		if (alvo - p).Magnitude > 0.01 then
			return CFrame.lookAt(p, alvo)
		end
	end
	return CFrame.new(p)
end

-- Deitado de costas no chao, cabeca apontando para 'cabeca' (direcao horizontal).
function AnimKit.deitado(pos, cabeca)
	local p = Vector3.new(pos.X, AnimKit.chao(pos) + AnimKit.ALTURA_DEITADO, pos.Z)
	return CFrame.lookAt(p, p + Vector3.yAxis, cabeca or Vector3.zAxis)
end

-- Noob classico R6 com a skin das referencias: cabeca classica do Roblox, rosto de desenho,
-- braços e cabeca amarelos, tronco azul e pernas verdes. cf = posicao/orientacao inicial.
function AnimKit.criarNoob(nome, cf, cores)
	cores = cores or {}
	local desc = Instance.new("HumanoidDescription")
	local pele = cores.pele or AnimKit.CORES.pele
	desc.HeadColor = pele
	desc.LeftArmColor = pele
	desc.RightArmColor = pele
	desc.TorsoColor = cores.camisa or AnimKit.CORES.camisa
	desc.LeftLegColor = cores.calca or AnimKit.CORES.calca
	desc.RightLegColor = cores.calca or AnimKit.CORES.calca
	local model = Players:CreateHumanoidModelFromDescription(desc, Enum.HumanoidRigType.R6)
	model.Name = nome
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Shirt") or d:IsA("Pants") or d:IsA("ShirtGraphic") or d:IsA("Accessory") then
			d:Destroy()
		end
	end
	local hum = model:FindFirstChildOfClass("Humanoid")
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	hum.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOff
	if not hum:FindFirstChildOfClass("Animator") then
		Instance.new("Animator").Parent = hum
	end
	local animate = model:FindFirstChild("Animate")
	if animate then animate:Destroy() end
	model.HumanoidRootPart.Anchored = true
	local k = AnimKit.CABECA / 1.25
	local malha = model.Head:FindFirstChildOfClass("SpecialMesh")
	if malha then malha.Scale = Vector3.new(AnimKit.CABECA, AnimKit.CABECA, AnimKit.CABECA) end
	local neck = model.Torso:FindFirstChild("Neck")
	if neck then
		-- A cabeca maior sobe junto, apoiada nos ombros.
		neck.C1 = CFrame.new(0, -0.5 * k, 0) * (neck.C1 - neck.C1.Position)
	end
	model:PivotTo(cf)
	rostoGui(model)
	model.Parent = workspace
	return model
end

-- Escorregador: escada + rampa inclinada (ou curva) + bordas. Devolve os pontos do caminho de descida.
-- opts: topo (Vector3 do topo), dir (Vector3 horizontal), comprimento, queda, cor, corBorda, largura, segmentos, curva (graus totais)
function AnimKit.escorregador(nome, opts)
	local pasta = Instance.new("Model")
	pasta.Name = nome
	pasta.Parent = workspace
	local largura = opts.largura or 6
	local segs = opts.segmentos or 10
	local dir = (opts.dir or Vector3.new(0, 0, -1)).Unit
	local curva = math.rad(opts.curva or 0)
	local topo = opts.topo
	-- Pontos de assento: superficie (meia espessura 0.3) + altura do noob sentado, na normal da rampa.
	local pontos = { topo + Vector3.new(0, 0.3 + AnimKit.ALTURA_SENTADO, 0) }
	local pos = topo
	local passoH = opts.comprimento / segs
	local passoV = opts.queda / segs
	for i = 1, segs do
		local d = CFrame.Angles(0, curva / segs * (i - 0.5), 0):VectorToWorldSpace(dir)
		local a = pos
		local b = pos + d * passoH - Vector3.new(0, passoV, 0)
		local meio = (a + b) / 2
		local cf = CFrame.lookAt(meio, b)
		AnimKit.bloco({ Name = "Rampa" .. i, Parent = pasta, Size = Vector3.new(largura, 0.6, (b - a).Magnitude + 0.15),
			CFrame = cf, Color = opts.cor, Material = Enum.Material.SmoothPlastic })
		for _, s in ipairs({ -1, 1 }) do
			AnimKit.bloco({ Name = "Borda", Parent = pasta, Size = Vector3.new(0.5, 1.6, (b - a).Magnitude + 0.15),
				CFrame = cf * CFrame.new(s * (largura / 2 + 0.25), 0.7, 0), Color = opts.corBorda or Color3.new(1, 1, 1) })
		end
		pontos[#pontos + 1] = b + cf.UpVector * (0.3 + AnimKit.ALTURA_SENTADO)
		pos = b
	end
	-- Plataforma e escada no topo.
	-- Plataforma do topo: o assento do primeiro ponto fica sobre ela (topo da plataforma = topo.Y + 0.3).
	AnimKit.bloco({ Name = "Plataforma", Parent = pasta, Size = Vector3.new(largura + 2, 0.8, 6),
		CFrame = CFrame.lookAt(topo - dir * 3 - Vector3.new(0, 0.1, 0), topo - dir * 3 - Vector3.new(0, 0.1, 0) + dir), Color = opts.corBorda or Color3.new(1, 1, 1) })
	local degraus = math.floor(topo.Y / 1.2)
	for i = 1, degraus do
		local y = topo.Y - i * 1.2
		AnimKit.bloco({ Name = "Degrau", Parent = pasta, Size = Vector3.new(largura, 0.5, 1.4),
			CFrame = CFrame.lookAt(Vector3.new(topo.X, y, topo.Z) - dir * (6 + i * 1.1), Vector3.new(topo.X, y, topo.Z)), Color = opts.cor })
	end
	for _, s in ipairs({ -1, 1 }) do
		AnimKit.bloco({ Name = "Pilar", Parent = pasta, Size = Vector3.new(1, topo.Y, 1),
			CFrame = CFrame.new(topo - dir * 3 + CFrame.lookAt(Vector3.zero, dir):VectorToWorldSpace(Vector3.new(s * (largura / 2 + 0.5), 0, 0)) - Vector3.new(0, topo.Y / 2, 0)),
			Color = opts.corBorda or Color3.new(1, 1, 1) })
	end
	local caminho = Instance.new("StringValue")
	caminho.Name = "Caminho"
	local enc = {}
	for _, p in ipairs(pontos) do enc[#enc + 1] = string.format("%.3f,%.3f,%.3f", p.X, p.Y, p.Z) end
	caminho.Value = table.concat(enc, ";")
	caminho.Parent = pasta
	return pasta, pontos
end

function AnimKit.caminho(modelo)
	local pts = {}
	for trio in string.gmatch(modelo.Caminho.Value, "[^;]+") do
		local x, y, z = string.match(trio, "([^,]+),([^,]+),([^,]+)")
		pts[#pts + 1] = Vector3.new(tonumber(x), tonumber(y), tonumber(z))
	end
	return pts
end

-- Visual de desenho: luz forte, cores saturadas, ceu limpo.
function AnimKit.visual()
	local L = game:GetService("Lighting")
	-- Technology so pode ser trocado por plugin/Studio; no RunScript vem do arquivo do place.
	pcall(function() L.Technology = Enum.Technology.Future end)
	L.Brightness = 3
	L.ClockTime = 13.5
	L.GlobalShadows = true
	L.EnvironmentDiffuseScale = 1
	L.EnvironmentSpecularScale = 0.6
	L.Ambient = Color3.fromRGB(110, 110, 120)
	L.OutdoorAmbient = Color3.fromRGB(150, 150, 160)
	for _, nome in ipairs({ "AK_Cor", "AK_Bloom", "AK_Atmos" }) do
		local o = L:FindFirstChild(nome)
		if o then o:Destroy() end
	end
	local cc = Instance.new("ColorCorrectionEffect")
	cc.Name = "AK_Cor"
	cc.Saturation = 0.35
	cc.Contrast = 0.12
	cc.Brightness = 0.03
	cc.Parent = L
	local bl = Instance.new("BloomEffect")
	bl.Name = "AK_Bloom"
	bl.Intensity = 0.4
	bl.Size = 24
	bl.Threshold = 1.6
	bl.Parent = L
	local at = Instance.new("Atmosphere")
	at.Name = "AK_Atmos"
	at.Density = 0.25
	at.Haze = 0.6
	at.Color = Color3.fromRGB(200, 225, 255)
	at.Parent = L
	Players.CharacterAutoLoads = false
end

--------------------------------------------------------------------------------------------
-- Atuacao (modo play)
--------------------------------------------------------------------------------------------

-- Expressoes calibradas pelos quadros das referencias.
-- olho/pupila: escala; palpebra: fracao do olho coberta; sobE/sobD: rotacao das sobrancelhas
-- (negativo na esquerda = ponta de dentro para cima, cara de preocupado); sobY: deslocamento;
-- boca: nome da boca; suor; fechado: olhos >_<; tonto: pupilas desencontradas.
local EXPR = {
	normal = { olho = 1, pupila = 1, palpebra = 0, sobE = -3, sobY = 0, boca = "reta" },
	feliz = { olho = 0.92, pupila = 1.08, palpebra = 0, sobE = -8, sobY = -0.02, boca = "aberto" },
	surpreso = { olho = 1.12, pupila = 0.74, palpebra = 0, sobE = 0, sobY = -0.05, boca = "o" },
	medo = { olho = 1.1, pupila = 0.7, palpebra = 0, sobE = -17, sobY = -0.03, boca = "lingua", suor = true },
	grito = { olho = 1.13, pupila = 0.64, palpebra = 0, sobE = -19, sobY = -0.04, boca = "grito", suor = true },
	nervoso = { olho = 1.04, pupila = 0.82, palpebra = 0, sobE = -15, sobY = -0.02, boca = "dentes", suor = true },
	confiante = { olho = 0.95, pupila = 1.05, palpebra = 0.36, sobE = 13, sobY = 0.01, boca = "sorriso" },
	bravo = { olho = 0.95, pupila = 1, palpebra = 0.26, sobE = 24, sobY = 0.03, boca = "reta" },
	duvida = { olho = 1, pupila = 0.9, palpebra = 0.1, sobE = -20, sobD = -6, sobY = -0.01, boca = "reta" },
	tonto = { olho = 1.05, pupila = 0.58, palpebra = 0.12, sobE = -10, sobY = 0, boca = "o", suor = true, tonto = true },
	apertado = { olho = 1, pupila = 1, palpebra = 0, sobE = 18, sobY = 0.02, boca = "grito", suor = true, fechado = true },
}
AnimKit.EXPRESSOES = EXPR

local function gui(noob)
	return noob.RostoPlaca.RostoGui
end

function AnimKit.rosto(noob, expr, t)
	local e = EXPR[expr] or error("expressao desconhecida: " .. tostring(expr))
	t = t or 0.12
	local g = gui(noob)
	for _, lado in ipairs({ "E", "D" }) do
		local x = OLHO.x[lado]
		local olho = g["Olho" .. lado]
		local h = OLHO.h * e.olho
		olho.Visible = not e.fechado
		g["Fechado" .. lado].Visible = e.fechado == true
		tween(olho, t, { Size = UDim2.fromScale(OLHO.w * e.olho, h) }, Enum.EasingStyle.Back)
		tween(olho.Pupila, t, { Size = UDim2.fromScale(0.32 * e.pupila, 0.36 * e.pupila) })
		if e.tonto then
			tween(olho.Pupila, t, { Position = lado == "E" and UDim2.fromScale(0.35, 0.36) or UDim2.fromScale(0.66, 0.74) })
		end
		local topo = OLHO.y - h / 2
		tween(g["Palpebra" .. lado], t, { Position = UDim2.fromScale(x, topo + h * e.palpebra / 2),
			Size = UDim2.fromScale(OLHO.w * e.olho + 0.05, h * e.palpebra + (e.palpebra > 0 and 0.01 or 0)) })
		local rot = lado == "E" and e.sobE or -(e.sobD or e.sobE)
		tween(g["Sobrancelha" .. lado], t, { Rotation = rot, Position = UDim2.fromScale(x, topo - 0.075 + e.sobY) })
	end
	for _, b in ipairs(g.Bocas:GetChildren()) do
		b.Visible = b.Name == e.boca
	end
	g.Suor.Visible = e.suor == true
end

-- Direcao do olhar: dx/dy de -1 a 1.
function AnimKit.olhar(noob, dx, dy, t)
	local g = gui(noob)
	for _, lado in ipairs({ "E", "D" }) do
		tween(g["Olho" .. lado].Pupila, t or 0.15, { Position = UDim2.fromScale(0.5 + 0.2 * dx, 0.56 + 0.17 * dy) })
	end
end

-- Piscadas automaticas enquanto a cena roda.
function AnimKit.piscar(noob)
	task.spawn(function()
		while noob.Parent do
			task.wait(2.2 + math.random() * 2.5)
			local g = gui(noob)
			for _, lado in ipairs({ "E", "D" }) do
				local olho = g["Olho" .. lado]
				if olho.Visible then
					local s = olho.Size
					tween(olho, 0.06, { Size = UDim2.new(s.X.Scale, 0, 0.025, 0) })
					task.delay(0.1, function() tween(olho, 0.07, { Size = s }) end)
				end
			end
		end
	end)
end

local cacheAnim = setmetatable({}, { __mode = "k" })
function AnimKit.anim(noob, nome, opcoes)
	opcoes = opcoes or {}
	local animator = noob:FindFirstChildOfClass("Humanoid"):FindFirstChildOfClass("Animator")
	cacheAnim[noob] = cacheAnim[noob] or {}
	local tracks = cacheAnim[noob]
	if not opcoes.manter then
		for n, tr in pairs(tracks) do
			if n ~= nome and tr.IsPlaying then tr:Stop(opcoes.fade or 0.15) end
		end
	end
	local tr = tracks[nome]
	if not tr then
		local a = Instance.new("Animation")
		a.AnimationId = "rbxassetid://" .. tostring(AnimKit.ANIM[nome] or nome)
		tr = animator:LoadAnimation(a)
		tracks[nome] = tr
	end
	tr.Looped = opcoes.loop ~= false
	tr:Play(opcoes.fade or 0.15, 1, opcoes.velocidade or 1)
	return tr
end

local function raiz(noob) return noob.HumanoidRootPart end

-- Anda/corre ate cf (CFrame ou Vector3) em t segundos.
function AnimKit.mover(noob, destino, t, animNome)
	local r = raiz(noob)
	if typeof(destino) == "Vector3" then
		-- Pes sempre no chao: a altura vem do piso, nao do numero passado.
		local dir = (destino - r.Position) * Vector3.new(1, 0, 1)
		destino = AnimKit.emPe(destino, destino + (dir.Magnitude > 0.01 and dir or r.CFrame.LookVector))
	end
	if animNome ~= false then AnimKit.anim(noob, animNome or "andar") end
	local tw = tween(r, t, { CFrame = destino }, Enum.EasingStyle.Linear)
	if animNome ~= false then
		tw.Completed:Connect(function() AnimKit.anim(noob, "idle") end)
	end
	return tw
end

-- Percorre uma lista de pontos (ex.: AnimKit.caminho(escorregador)) em t segundos, sentado.
function AnimKit.deslizar(noob, pontos, t, anim, aoTerminar)
	local r = raiz(noob)
	local total = 0
	for i = 2, #pontos do total += (pontos[i] - pontos[i - 1]).Magnitude end
	AnimKit.anim(noob, anim or "sentar")
	task.spawn(function()
		for i = 2, #pontos do
			local delta = pontos[i] - pontos[i - 1]
			local seg = delta.Magnitude
			local frente = delta.Unit
			-- Normal da rampa: o noob senta inclinado junto com a descida, sem afundar nem flutuar.
			local lado = frente:Cross(Vector3.yAxis)
			local cima = lado.Magnitude > 0.01 and lado.Unit:Cross(frente) or Vector3.yAxis
			local cf = CFrame.lookAt(pontos[i], pontos[i] + frente, cima)
			local tw = tween(r, t * seg / total, { CFrame = cf }, Enum.EasingStyle.Linear)
			tw.Completed:Wait()
		end
		if aoTerminar then aoTerminar() end
	end)
end

-- Voo em arco (parabola) ate destino, com giro opcional (voltas).
function AnimKit.voar(noob, destino, altura, t, voltas, anim, aoPousar)
	local r = raiz(noob)
	local a = r.Position
	local orient = r.CFrame - r.Position
	AnimKit.anim(noob, anim or "cair")
	local t0 = os.clock()
	local con
	con = RunService.RenderStepped:Connect(function()
		local k = math.clamp((os.clock() - t0) / t, 0, 1)
		local p = a:Lerp(destino, k) + Vector3.new(0, 4 * altura * k * (1 - k), 0)
		r.CFrame = CFrame.new(p) * orient * CFrame.Angles(math.pi * 2 * (voltas or 0) * k, 0, 0)
		if k >= 1 then
			con:Disconnect()
			if aoPousar then aoPousar() end
		end
	end)
end

-- Nuvem de poeira (pouso, tombo). Textura de fumaca embutida no Studio.
function AnimKit.poeira(pos, quantidade)
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.Transparency = 1
	p.Size = Vector3.new(1, 1, 1)
	p.CFrame = CFrame.new(pos)
	local e = Instance.new("ParticleEmitter")
	e.Texture = "rbxasset://textures/particles/smoke_main.dds"
	e.Color = ColorSequence.new(Color3.fromRGB(235, 225, 205))
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1.2), NumberSequenceKeypoint.new(1, 4.5) })
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.15), NumberSequenceKeypoint.new(1, 1) })
	e.Lifetime = NumberRange.new(0.6, 1.1)
	e.Speed = NumberRange.new(6, 12)
	e.SpreadAngle = Vector2.new(180, 25)
	e.Drag = 4
	e.Rate = 0
	e.Parent = p
	p.Parent = workspace
	e:Emit(quantidade or 24)
	task.delay(2, function() p:Destroy() end)
end

-- Tremedeira (medo/frio) do corpo todo por t segundos.
function AnimKit.tremer(noob, t, amp)
	local r = raiz(noob)
	local base = r.CFrame
	local t0 = os.clock()
	local con
	con = RunService.RenderStepped:Connect(function()
		local k = os.clock() - t0
		r.CFrame = base * CFrame.new(math.sin(k * 60) * (amp or 0.08), 0, 0)
		if k >= t then r.CFrame = base; con:Disconnect() end
	end)
end

--------------------------------------------------------------------------------------------
-- Camera
--------------------------------------------------------------------------------------------

local cam = {}
AnimKit.camera = cam
local tremorAtual = CFrame.new()
local seguindo = nil

local function fovReal(fovH)
	fovH = fovH or AnimKit.FOV
	if AnimKit.VERTICAL then
		return fovH -- camera deitada: o eixo vertical do viewport vira o horizontal do video
	end
	return math.deg(2 * math.atan(math.tan(math.rad(fovH) / 2) * 16 / 9))
end

local function aplicar(cf)
	local c = workspace.CurrentCamera
	local final = cf * tremorAtual
	if AnimKit.VERTICAL then
		final = final * CFrame.Angles(0, 0, math.rad(90))
	end
	c.CFrame = final
end

local base = CFrame.new()
local geracao = 0 -- cada corte/movimento novo cancela o anterior
local function cfOlhando(pos, alvo, cima)
	return CFrame.lookAt(pos, alvo, cima or Vector3.yAxis)
end

-- cima: vetor que deve ficar para cima no quadro (ex.: plano de cima de alguem deitado).
function cam.corte(pos, alvo, fovH, cima)
	geracao += 1
	seguindo = nil
	base = cfOlhando(pos, alvo, cima)
	workspace.CurrentCamera.FieldOfView = fovReal(fovH)
	aplicar(base)
end

-- Travelling suave de onde esta ate pos/alvo.
function cam.mover(pos, alvo, t, fovH, estilo, cima)
	geracao += 1
	local minha = geracao
	seguindo = nil
	local de, para = base, cfOlhando(pos, alvo, cima)
	local f0, f1 = workspace.CurrentCamera.FieldOfView, fovReal(fovH)
	local t0 = os.clock()
	local con
	con = RunService.RenderStepped:Connect(function()
		if geracao ~= minha then con:Disconnect(); return end
		local k = math.clamp((os.clock() - t0) / t, 0, 1)
		local e = TweenService:GetValue(k, estilo or Enum.EasingStyle.Sine, Enum.EasingDirection.InOut)
		base = de:Lerp(para, e)
		workspace.CurrentCamera.FieldOfView = f0 + (f1 - f0) * e
		if k >= 1 then con:Disconnect() end
	end)
end

-- Segue uma parte mantendo o deslocamento (no espaco do mundo) por t segundos.
function cam.seguir(parte, deslocamento, t, olharAcima)
	geracao += 1
	local fim = os.clock() + (t or math.huge)
	seguindo = { parte = parte, desl = deslocamento, fim = fim, acima = olharAcima or Vector3.new(0, 1, 0) }
end

-- Enquadra o rosto do noob pela posicao real da cabeca: cabeca no terco de cima do quadro
-- vertical, um pouco de tronco embaixo. dist em studs; lado desloca para a direita (+) ou esquerda;
-- altura sobe/desce a camera em relacao aos olhos; t > 0 faz travelling ate o enquadramento.
function cam.rosto(noob, dist, fovH, opcoes)
	opcoes = opcoes or {}
	local h = noob.Head
	local cf = h.CFrame
	local frente = (cf.LookVector * Vector3.new(1, 0, 1))
	frente = frente.Magnitude > 0.1 and frente.Unit or cf.LookVector
	local pos = h.Position + frente * dist + cf.RightVector * (opcoes.lado or 0) + Vector3.new(0, opcoes.altura or -0.15, 0)
	local alvo = h.Position - Vector3.new(0, (opcoes.queixo or 0.42) * AnimKit.CABECA / 1.25, 0)
	if opcoes.t and opcoes.t > 0 then
		cam.mover(pos, alvo, opcoes.t, fovH, opcoes.estilo)
	else
		cam.corte(pos, alvo, fovH)
	end
end

function cam.tremor(intensidade, t)
	local t0 = os.clock()
	local con
	con = RunService.RenderStepped:Connect(function()
		local k = os.clock() - t0
		local dec = math.max(0, 1 - k / t)
		local a = (intensidade or 0.4) * dec
		tremorAtual = CFrame.new(math.noise(k * 25, 1) * a, math.noise(k * 25, 2) * a, 0) * CFrame.Angles(0, 0, math.noise(k * 20, 3) * a * 0.05)
		if k >= t then tremorAtual = CFrame.new(); con:Disconnect() end
	end)
end

-- Zoom-soco: FOV fecha rapido e volta.
function cam.soco(intensidade, t)
	local c = workspace.CurrentCamera
	local f = c.FieldOfView
	c.FieldOfView = f * (1 - (intensidade or 0.25))
	tween(c, t or 0.3, { FieldOfView = f }, Enum.EasingStyle.Quad)
end

-- Only the playing client drives the camera; requiring the kit in edit mode must stay side-effect free.
if RunService:IsClient() and RunService:IsRunning() then
	RunService:BindToRenderStep("AnimKitCamera", Enum.RenderPriority.Camera.Value + 1, function()
		if workspace.CurrentCamera.CameraType ~= Enum.CameraType.Scriptable then return end
		if seguindo then
			if os.clock() > seguindo.fim then
				seguindo = nil
			else
				local p = seguindo.parte.Position
				base = CFrame.lookAt(p + seguindo.desl, p + seguindo.acima)
			end
		end
		aplicar(base)
	end)
end

--------------------------------------------------------------------------------------------
-- Relogio da cena
--------------------------------------------------------------------------------------------

local function flash(t)
	local pg = Players.LocalPlayer:WaitForChild("PlayerGui")
	local g = Instance.new("ScreenGui")
	g.Name = "AnimKitFlash"
	g.IgnoreGuiInset = true
	g.DisplayOrder = 1e6
	g.ScreenInsets = Enum.ScreenInsets.None
	local f = Instance.new("Frame")
	f.Size = UDim2.fromScale(1, 1)
	f.BackgroundColor3 = Color3.fromRGB(255, 0, 255)
	f.BorderSizePixel = 0
	f.Parent = g
	g.Parent = pg
	task.delay(t, function() g:Destroy() end)
end

local function esconderInterface()
	local SG = game:GetService("StarterGui")
	pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.All, false) end)
	for _ = 1, 20 do
		if pcall(function() SG:SetCore("TopbarEnabled", false) end) then break end
		task.wait(0.1)
	end
end

-- eventos: { {t = 0.0, f = function() ... end}, ... }  (t em segundos desde o t=0 da timeline)
-- duracao: tempo total da cena; um segundo flash magenta marca o fim.
function AnimKit.rodar(eventos, duracao)
	esconderInterface()
	workspace.CurrentCamera.CameraType = Enum.CameraType.Scriptable
	table.sort(eventos, function(a, b) return a.t < b.t end)
	-- Primeiro quadro ja enquadrado (evita a camera padrao no inicio da gravacao).
	for _, e in ipairs(eventos) do
		if e.t <= 0 then task.spawn(e.f) end
	end
	task.wait(1.5)
	flash(0.3)
	task.wait(AnimKit.ATRASO)
	local t0 = os.clock()
	local i = 1
	while eventos[i] and eventos[i].t <= 0 do i += 1 end
	local con
	con = RunService.Heartbeat:Connect(function()
		local agora = os.clock() - t0
		while eventos[i] and eventos[i].t <= agora do
			task.spawn(eventos[i].f)
			i += 1
		end
		if agora >= duracao then
			con:Disconnect()
			flash(0.3)
			task.delay(0.8, AnimKit.encerrar)
		end
	end)
end

-- Ends an automated play session (gravacao): the server Script installed by the pipeline
-- listens to ReplicatedStorage.AnimKitFim and calls StudioTestService:EndTest.
function AnimKit.encerrar()
	local ev = game:GetService("ReplicatedStorage"):FindFirstChild("AnimKitFim")
	if ev then
		ev:FireServer("ok")
	end
end

return AnimKit
