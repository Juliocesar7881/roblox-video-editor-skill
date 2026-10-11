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
AnimKit.ALTURA_RAIZ = 3.41 -- R15 (Cartoony idle): centro do HumanoidRootPart acima da sola dos pes (medido)
AnimKit.ALTURA_SENTADO = 1.32 -- R15 'sentar' + pose sentadoReto: centro do HumanoidRootPart acima do assento (medido 1.27)
AnimKit.ELEVACAO_PASSO = { andar = -0.15, correr = -0.19 } -- Cartoony: o pe de apoio fica acima do nivel parado (medido)
AnimKit.ALTURA_DEITADO = 0.95 -- R15 deitado de costas sem animacao: centro acima do chao (medido 0.91)
AnimKit.ATRASO = 0.8 -- segundos entre o flash magenta e o t=0 da timeline
AnimKit.FOV = 50 -- campo de visao HORIZONTAL do video vertical final, em graus
AnimKit.MARGEM_TOPO = 0.075 -- faixa de cima do viewport cortada na gravacao (= margem_topo do captura_janela.processar)
AnimKit.FAIXA_LEGENDA = { 0.665, 0.75 } -- faixa do video (fracao da altura) das legendas karaoke (texto ~0,665-0,72)

-- Skin das referencias: amarelo forte, azul royal e verde vivo.
AnimKit.CORES = {
	pele = Color3.fromRGB(255, 215, 54),
	camisa = Color3.fromRGB(35, 110, 242),
	calca = Color3.fromRGB(99, 190, 67),
}

-- Animacoes R6 publicadas pela propria Roblox (livres para qualquer jogo).
-- Rig R15 com os pacotes oficiais do Roblox (Cartoony para locomocao, Levitation para flutuar) e
-- emotes R15 da Roblox. Todos publicados pela conta Roblox: tocam em qualquer place.
AnimKit.ANIM = {
	idle = 742637544, idle2 = 742638445, andar = 742640026, correr = 742638842, pular = 742637942,
	cair = 742637151, escalar = 742636889, nadar = 742639220,
	flutuar = 616006778, voarPose = 616013216, superpulo = 616115533,
	sentar = 2506281703, acenar = 507770239, apontar = 507770453, rir = 507770818,
	comemorar = 507770677, dancar = 507771019,
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

-- Rosto: as mesmas caretas da skill eibrunoruan/roblox-shorts-generator (studio/src/Expressions.lua
-- e SpeechMouth.lua), portadas sem mudar desenho, cores, tamanhos nem animacao: tela 600x300 na
-- frente da cabeca (FixedSize), olhos com contorno, pupila com brilho, sobrancelhas em traco,
-- bochechas, boca escura com lingua/dentes, gota de suor que ESCORRE pelo rosto, olhos X de dor.
-- Fica numa placa soldada na frente da cabeca (mesma area da frente da cabeca), que a auditoria
-- de camera usa para medir o rosto.
AnimKit.CABECA = 1.0 -- escala da cabeca R15: a do noob padrao, como na skill de referencia
AnimKit.ROSTO_TAM = 1.0 -- placa do rosto, em fracao da largura/altura da cabeca (frente inteira)
AnimKit.ROSTO_Y = 0.0 -- deslocamento vertical da placa, em fracao da altura da cabeca
AnimKit.ROSTO_Z = 0.5 -- distancia da placa ao centro, em fracao da profundidade da cabeca
-- Faixa vertical do desenho na tela (de cima): sobrancelhas ate o fim da boca aberta.
AnimKit.ROSTO_FAIXA = { 0.06, 0.94 }

local TINTA = Color3.fromRGB(24, 20, 32)
local BRANCO_R = Color3.fromRGB(255, 253, 247)
local ROSA_R = Color3.fromRGB(255, 109, 137)

local function oval(pai, x, y, largura, altura, cor, borda)
	local item = Instance.new("Frame")
	item.AnchorPoint = Vector2.new(0.5, 0.5)
	item.Position, item.Size = UDim2.fromOffset(x, y), UDim2.fromOffset(largura, altura)
	item.BorderSizePixel, item.BackgroundColor3 = 0, cor or TINTA
	item.Parent = pai
	local canto = Instance.new("UICorner")
	canto.CornerRadius = UDim.new(1, 0)
	canto.Parent = item
	if borda then
		local traco = Instance.new("UIStroke")
		traco.Color, traco.Thickness = TINTA, borda
		traco.Parent = item
	end
	return item
end

local function linha(pai, a, b, largura, cor)
	local delta = b - a
	local item = oval(pai, (a.X + b.X) / 2, (a.Y + b.Y) / 2, delta.Magnitude + 1, largura or 6, cor)
	item.Rotation = math.deg(math.atan2(delta.Y, delta.X))
	return item
end

local function rostoGui(noob)
	local head = noob.Head
	for _, d in ipairs(head:GetChildren()) do
		if d:IsA("Decal") then d:Destroy() end
	end
	-- Cabecas R15 atuais trazem o rosto padrao na textura e controles faciais: sem textura e com os
	-- controles fora, so a careta aparece (a malha fica em repouso, sem deformar o desenho).
	if head:IsA("MeshPart") then pcall(function() head.TextureID = "" end) end
	local controles = head:FindFirstChildOfClass("FaceControls")
	if controles then pcall(function() controles:Destroy() end) end
	local velha = noob:FindFirstChild("RostoPlaca")
	if velha then velha:Destroy() end
	local placa = Instance.new("Part")
	placa.Name = "RostoPlaca"
	placa.Size = Vector3.new(head.Size.X * AnimKit.ROSTO_TAM, head.Size.Y * AnimKit.ROSTO_TAM, 0.05)
	placa.Transparency = 1
	placa.CanCollide = false
	placa.CanQuery = false
	placa.CanTouch = false
	placa.Massless = true
	placa.CastShadow = false
	placa.Anchored = false
	placa.CFrame = head.CFrame * CFrame.new(0, AnimKit.ROSTO_Y * head.Size.Y, -AnimKit.ROSTO_Z * head.Size.Z - 0.01)
	placa:SetAttribute("FaixaTopo", AnimKit.ROSTO_FAIXA[1])
	placa:SetAttribute("FaixaBase", AnimKit.ROSTO_FAIXA[2])
	local solda = Instance.new("WeldConstraint")
	solda.Part0 = head
	solda.Part1 = placa
	solda.Parent = placa
	placa.Parent = noob

	local gui = Instance.new("SurfaceGui")
	gui.Name = "RostoGui"
	gui.Face = Enum.NormalId.Front
	gui.AlwaysOnTop = false
	gui.ZOffset = 0.03
	gui.CanvasSize = Vector2.new(600, 300)
	gui.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize
	gui.LightInfluence = 0
	gui.Parent = placa
	local tela = Instance.new("Frame")
	tela.Name = "Tela"
	tela.Size, tela.BackgroundTransparency = UDim2.fromOffset(300, 150), 1
	tela.Parent = gui
	local escala = Instance.new("UIScale")
	escala.Scale = 2
	escala.Parent = tela
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
	local model = Players:CreateHumanoidModelFromDescription(desc, Enum.HumanoidRigType.R15)
	model.Name = nome
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Shirt") or d:IsA("Pants") or d:IsA("ShirtGraphic") or d:IsA("Accessory") then
			d:Destroy()
		end
	end
	-- Cabeca classica maior: o Humanoid R15 reaplica a propria escala, entao usa o HeadScale dele.
	local escala = model:FindFirstChildOfClass("Humanoid"):FindFirstChild("HeadScale")
	if escala then escala.Value = AnimKit.CABECA end
	local hum = model:FindFirstChildOfClass("Humanoid")
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	hum.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOff
	if not hum:FindFirstChildOfClass("Animator") then
		Instance.new("Animator").Parent = hum
	end
	local animate = model:FindFirstChild("Animate")
	if animate then animate:Destroy() end
	model.HumanoidRootPart.Anchored = true
	-- O Roblox cria o rig com a CABECA como PrimaryPart: sem isto, PivotTo poe a cabeca no ponto
	-- pedido e o corpo fica 1,5 stud enterrado no chao.
	model.PrimaryPart = model.HumanoidRootPart
	model.WorldPivot = model.HumanoidRootPart.CFrame
	model:PivotTo(cf)
	-- O HeadScale so e aplicado depois que o modelo entra no mundo: o rosto e montado depois,
	-- senao a placa fica do tamanho da cabeca antiga, escondida dentro da cabeca nova.
	model.Parent = workspace
	local t0 = os.clock()
	while model.Head.Size.X < 1.16 * AnimKit.CABECA * 0.98 and os.clock() - t0 < 3 do task.wait() end
	model:PivotTo(cf)
	rostoGui(model)
	return model
end

-- Escorregador: escada + rampa inclinada (ou curva) + bordas. Devolve os pontos do caminho de descida.
-- opts: topo (Vector3 do topo), dir (Vector3 horizontal), comprimento, queda, cor, corBorda, largura, segmentos, curva (graus totais)
-- Normal "para cima" de uma superficie que desce na direcao d (perpendicular a d, sem inclinar para o lado).
local function normalDe(d)
	local lado = d:Cross(Vector3.yAxis)
	if lado.Magnitude < 1e-3 then return Vector3.yAxis end
	return lado.Unit:Cross(d).Unit
end
AnimKit.normalDe = normalDe

function AnimKit.escorregador(nome, opts)
	local pasta = Instance.new("Model")
	pasta.Name = nome
	pasta.Parent = workspace
	local largura = opts.largura or 6
	local segs = opts.segmentos or 10
	local dir = (opts.dir or Vector3.new(0, 0, -1)).Unit
	local curva = math.rad(opts.curva or 0)
	local topo = opts.topo
	-- Juntas da linha central e direcoes dos trechos; os assentos sao calculados no fim.
	local juntas, dirs = { topo }, {}
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
		juntas[#juntas + 1] = b
		dirs[#dirs + 1] = (b - a).Unit
		pos = b
	end
	-- Saida plana no pe do escorregador: as pernas esticadas nao batem no chao no fim da descida.
	local saida = opts.saida or 5
	if saida > 0 then
		local d = CFrame.Angles(0, curva, 0):VectorToWorldSpace(dir)
		local b = pos + d * saida
		local cf = CFrame.lookAt((pos + b) / 2, b)
		AnimKit.bloco({ Name = "Saida", Parent = pasta, Size = Vector3.new(largura, 0.6, saida + 0.15), CFrame = cf,
			Color = opts.cor, Material = Enum.Material.SmoothPlastic })
		for _, sl in ipairs({ -1, 1 }) do
			AnimKit.bloco({ Name = "Borda", Parent = pasta, Size = Vector3.new(0.5, 1.6, saida + 0.15),
				CFrame = cf * CFrame.new(sl * (largura / 2 + 0.25), 0.7, 0), Color = opts.corBorda or Color3.new(1, 1, 1) })
		end
		juntas[#juntas + 1] = b
		dirs[#dirs + 1] = d
	end
	-- Assento em cada junta: na normal da bissetriz entre o trecho que chega e o que sai, assim as
	-- pernas nunca entram na rampa nas dobras (topo -> rampa, rampa -> saida plana).
	local pontos = {}
	for i, j in ipairs(juntas) do
		local dentro = dirs[i - 1] or (dirs[1] * Vector3.new(1, 0, 1)).Unit
		local fora = dirs[i] or dentro
		-- Nas dobras a ponta das pernas (2 studs a frente) desce ~2*sen(angulo/2): folga extra ali.
		local extra = 0
		if i > 1 then
			local ang = math.acos(math.clamp(dentro:Dot(fora), -1, 1))
			extra = 1.3 * math.sin(ang / 2)
		end
		pontos[i] = j + normalDe((dentro + fora).Unit) * (0.3 + AnimKit.ALTURA_SENTADO + extra)
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
	for _, nome in ipairs({ "AK_Cor", "AK_Bloom", "AK_Atmos", "AK_Foco" }) do
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
	-- Fundo desfocado como nas referencias; o foco segue a cabeca (AnimKit.foco) a cada quadro.
	local dof = Instance.new("DepthOfFieldEffect")
	dof.Name = "AK_Foco"
	dof.FarIntensity = 0.4
	dof.NearIntensity = 0
	dof.FocusDistance = 8
	dof.InFocusRadius = 6
	dof.Parent = L
	Players.CharacterAutoLoads = false
end

--------------------------------------------------------------------------------------------
-- Atuacao (modo play)
--------------------------------------------------------------------------------------------

-- Caretas da skill de referencia (nomes dela) e os nomes antigos do kit como apelidos.
local CARETAS = { curious = true, panic = true, angry = true, eat = true, hurt = true, relief = true,
	greedy = true, disgust = true, neutral = true }
local APELIDOS = { normal = "neutral", feliz = "relief", surpreso = "curious", medo = "panic", grito = "panic",
	nervoso = "panic", confiante = "greedy", bravo = "angry", duvida = "curious", tonto = "hurt",
	apertado = "hurt", nocaute = "hurt", nojo = "disgust", comer = "eat", curioso = "curious" }
AnimKit.CARETAS = CARETAS
AnimKit.APELIDOS = APELIDOS

local faces = {} -- noob -> estado (tabela forte)

local function estadoDe(noob)
	local e = faces[noob]
	if not e then
		local agora = os.clock()
		e = { nome = "neutral", desenhado = nil, t0 = agora, reacao = agora, olhar = Vector2.zero,
			olharAtual = Vector2.zero, fala = nil }
		faces[noob] = e
	end
	return e
end

-- Desenha a careta (so ao trocar de emocao, nunca a cada quadro). Copia de Expressions:draw.
local function desenhar(e, tela, name)
	for _, child in ipairs(tela:GetChildren()) do
		if not child:IsA("UIScale") then child:Destroy() end
	end
	e.eyes, e.brows = {}, {}
	e.mouth, e.sweat, e.teeth, e.tongue = nil, nil, nil, nil
	for _, x in ipairs({ 65, 235 }) do oval(tela, x, 87, 24, 10, ROSA_R).BackgroundTransparency = 0.42 end
	for index, x in ipairs({ 103, 197 }) do
		if name == "hurt" then
			linha(tela, Vector2.new(x - 21, 32), Vector2.new(x + 21, 72), 9)
			linha(tela, Vector2.new(x + 21, 32), Vector2.new(x - 21, 72), 9)
		elseif name == "disgust" then
			linha(tela, Vector2.new(x - 25, 50), Vector2.new(x + 25, 64), 9)
		else
			local size = name == "panic" and Vector2.new(74, 68) or Vector2.new(62, 54)
			local eye = oval(tela, x, 55, size.X, size.Y, BRANCO_R, 4)
			eye.ClipsDescendants = true
			local pupil = oval(eye, 0, 0, name == "panic" and 13 or 22, name == "panic" and 17 or 29)
			pupil.Position = UDim2.fromScale(0.5, 0.55)
			local shine = oval(pupil, 0, 0, 5, 7, BRANCO_R)
			shine.Position = UDim2.fromScale(0.32, 0.25)
			table.insert(e.eyes, { item = eye, pupil = pupil, size = size })
		end
		local slope = (name == "disgust" or name == "angry" or name == "greedy") and (index == 1 and 16 or -16)
			or (index == 1 and -12 or 12)
		local brow = linha(tela, Vector2.new(x - 28, 13 - slope / 2), Vector2.new(x + 28, 13 + slope / 2), 7)
		table.insert(e.brows, { item = brow, angle = brow.Rotation, x = x })
	end
	local sizes = {
		angry = Vector2.new(88, 44), panic = Vector2.new(82, 50), eat = Vector2.new(94, 40), hurt = Vector2.new(100, 38),
		curious = Vector2.new(40, 32), relief = Vector2.new(108, 38), greedy = Vector2.new(124, 50),
		disgust = Vector2.new(83, 12), neutral = Vector2.new(70, 26),
	}
	e.mouthSize = sizes[name] or sizes.curious
	e.mouth = oval(tela, 150, 113, e.mouthSize.X, e.mouthSize.Y, TINTA)
	e.mouth.ClipsDescendants = true
	if name == "panic" or name == "angry" or name == "eat" or name == "hurt" then
		e.tongue = oval(e.mouth, 0, 0, e.mouthSize.X * 0.55, 20, ROSA_R)
		e.tongue.Position = UDim2.fromScale(0.5, 0.96)
	end
	if name == "eat" or name == "relief" or name == "hurt" or name == "neutral" or name == "greedy" then
		local grin = name == "relief" or name == "greedy"
		e.teeth = oval(e.mouth, 0, 0, e.mouthSize.X - 12, grin and 26 or 11, BRANCO_R)
		e.teeth.Position = UDim2.fromScale(0.5, grin and 0.42 or 0.05)
	end
	if name == "panic" or name == "disgust" then
		e.sweat = oval(tela, 252, 34, 14, 27, Color3.fromRGB(91, 211, 255), 2)
		e.sweat.Rotation = -20
	end
	if name == "hurt" then
		for _, x in ipairs({ 64, 236 }) do
			linha(tela, Vector2.new(x - 8, 80), Vector2.new(x - 3, 94), 3, Color3.fromRGB(230, 86, 97))
			linha(tela, Vector2.new(x + 3, 78), Vector2.new(x + 8, 92), 3, Color3.fromRGB(230, 86, 97))
		end
	end
end

-- Anima a careta a cada quadro. Copia de Expressions:set + SpeechMouth.frame, mais o olhar do kit.
local function atualizarRosto(noob, e, dt)
	local placa = noob:FindFirstChild("RostoPlaca")
	local g = placa and placa:FindFirstChild("RostoGui")
	local tela = g and g:FindFirstChild("Tela")
	if not tela then return end
	local name = e.nome
	if e.desenhado ~= name then
		desenhar(e, tela, name)
		e.desenhado = name
	end
	local agora = os.clock()
	local elapsed, reactionTime = agora - e.t0, agora - e.reacao
	-- Estouro inicial seguido de acomodacao, sem piscar o rosto original.
	tela.UIScale.Scale = 2 * (1 + math.sin(reactionTime * 19) * math.exp(-reactionTime * 8) * 0.1)
	local blinkPhase = elapsed % 3.7
	local blink = blinkPhase > 3.48 and blinkPhase < 3.7 and math.sin((blinkPhase - 3.48) / 0.22 * math.pi) ^ 2 or 0
	if name == "panic" then blink = 0 end
	e.olharAtual += (e.olhar - e.olharAtual) * (1 - math.exp(-dt / 0.08))
	for index, eye in ipairs(e.eyes) do
		local height = eye.size.Y * (1 - blink * 0.94)
		eye.item.Size = UDim2.fromOffset(eye.size.X, height)
		local shift = name == "panic" and math.sin(elapsed * 13) * 0.12 or math.sin(elapsed * 1.8) * 0.06
		eye.pupil.Position = UDim2.fromScale(0.5 + shift + 0.2 * e.olharAtual.X,
			(name == "eat" and 0.72 or 0.55) + 0.15 * e.olharAtual.Y)
		if name == "curious" then eye.item.Rotation = (index == 1 and -1 or 1) * (8 + math.sin(elapsed * 2) * 4) end
	end
	for index, brow in ipairs(e.brows) do
		brow.item.Rotation = brow.angle + math.sin(elapsed * 3 + index) * (name == "panic" and 9 or 4)
	end
	local chew = name == "eat" and 0.72 + math.sin(elapsed * 14) * 0.28 or 1
	local scream = name == "panic" and 1 + math.sin(elapsed * 8) * 0.12 or 1
	e.mouth.Size = UDim2.fromOffset(e.mouthSize.X * scream, e.mouthSize.Y * chew * scream)
	if e.sweat then
		local slide = (elapsed * 1.4) % 1
		e.sweat.Position = UDim2.fromOffset(252, 27 + slide * 42)
		e.sweat.BackgroundTransparency = slide ^ 3
	end
	-- Fala (SpeechMouth.frame): a boca abre com o volume real da voz, a 30 quadros por segundo.
	if e.fala then
		local f = (agora - e.fala.t0) * e.fala.fps
		local i = math.floor(f) + 1
		if i > #e.fala.env then
			e.fala = nil
		else
			local a = (tonumber(e.fala.env:sub(i, i)) or 0) / 9
			local b = (tonumber(e.fala.env:sub(i + 1, i + 1)) or 0) / 9
			local volume = math.clamp((a + (b - a) * (f % 1)) * e.fala.abertura, 0, 1)
			local open = volume > 0.02 and math.clamp(volume * 1.5, 0, 1) ^ 0.75 or 0
			local resting = name == "panic" and 20 or name == "greedy" and 34 or 7
			e.mouth.Size = UDim2.fromOffset(math.max(e.mouthSize.X, 68) * (0.92 + 0.08 * open), resting + 56 * open)
			if e.teeth then
				e.teeth.Size = UDim2.fromOffset(math.max(e.mouthSize.X, 68) - 12, open > 0.02 and 8 or 5)
				e.teeth.Position = UDim2.fromScale(0.5, 0.08)
			end
		end
	end
end

-- So o cliente em Play anima o rosto; montar a cena no modo edicao fica sem efeitos colaterais.
if RunService:IsClient() and RunService:IsRunning() then
	RunService:BindToRenderStep("AnimKitRosto", Enum.RenderPriority.Camera.Value + 3, function(dt)
		for noob, e in pairs(faces) do
			if noob.Parent then
				atualizarRosto(noob, e, dt)
			else
				faces[noob] = nil
			end
		end
	end)
end

-- Troca a careta: nomes da skill de referencia (curious, panic, angry, eat, hurt, relief, greedy,
-- disgust, neutral) ou os apelidos antigos do kit (normal, feliz, medo, grito, bravo...).
function AnimKit.rosto(noob, expr)
	local nome = CARETAS[expr] and expr or APELIDOS[expr]
	if not nome then error("expressao desconhecida: " .. tostring(expr)) end
	local e = estadoDe(noob)
	if e.nome ~= nome then
		e.nome = nome
		e.reacao = os.clock()
	end
	noob:SetAttribute("Expressao", nome)
end

-- Sincronia labial: env e uma string de digitos 0-9 (volume da voz, um por quadro a 'fps'),
-- calculada do MP3 real da fala (scripts/envelope_boca.py).
function AnimKit.falar(noob, env, fps, abertura)
	local e = estadoDe(noob)
	e.fala = { env = env, fps = fps or 30, abertura = abertura or 1, t0 = os.clock() }
end

-- Direcao do olhar: dx/dy de -1 a 1 (soma ao movimento proprio das pupilas da careta).
function AnimKit.olhar(noob, dx, dy)
	estadoDe(noob).olhar = Vector2.new(dx, dy)
end

-- A piscada ja faz parte da careta (a cada 3,7 s, menos em panic); mantido por compatibilidade.
function AnimKit.piscar(noob)
	estadoDe(noob)
end

-- Pose fixa por cima das animacoes (ex.: sentado com as pernas esticadas para a frente, para
-- escorregar). juntas = { NomeDoMotor6D = CFrame } aplicado como Transform a cada quadro; as
-- outras juntas continuam com a animacao que estiver tocando. nil remove.
local poses = {} -- tabela forte: com chaves fracas o Roblox pode coletar o proxy da Instance e perder a entrada
AnimKit.POSES = {
	sentadoReto = {
		LeftHip = CFrame.Angles(math.rad(90), 0, math.rad(-4)), RightHip = CFrame.Angles(math.rad(90), 0, math.rad(4)),
		LeftKnee = CFrame.new(), RightKnee = CFrame.new(), LeftAnkle = CFrame.Angles(math.rad(-15), 0, 0), RightAnkle = CFrame.Angles(math.rad(-15), 0, 0),
		LeftShoulder = CFrame.Angles(math.rad(25), 0, math.rad(-35)), RightShoulder = CFrame.Angles(math.rad(25), 0, math.rad(35)),
	},
	bracosPraCima = {
		LeftShoulder = CFrame.Angles(math.rad(150), 0, math.rad(-20)), RightShoulder = CFrame.Angles(math.rad(150), 0, math.rad(20)),
		LeftElbow = CFrame.Angles(math.rad(20), 0, 0), RightElbow = CFrame.Angles(math.rad(20), 0, 0),
	},
}
-- No R15 o Humanoid recalcula o C0 de cada junta a partir do encaixe (RigAttachment) da peca de
-- cima e o Animator so escreve Transform: a pose gira esse encaixe e a animacao continua por cima.
local encOriginal = {} -- tabela forte: com chaves fracas o Roblox pode coletar o proxy da Instance e perder a entrada
function AnimKit.pose(noob, nome)
	local tabela = nome and (type(nome) == "table" and nome or AnimKit.POSES[nome]) or {}
	for _, m in ipairs(noob:GetDescendants()) do
		-- Rigs atuais usam AnimationConstraint (Attachment0 na peca de cima); os antigos, Motor6D.
		local enc
		if m:IsA("AnimationConstraint") then
			enc = m.Attachment0
		elseif m:IsA("Motor6D") and m.Part0 then
			enc = m.Part0:FindFirstChild(m.Name .. "RigAttachment")
		end
		if enc then
			encOriginal[enc] = encOriginal[enc] or enc.CFrame
			enc.CFrame = tabela[m.Name] and encOriginal[enc] * tabela[m.Name] or encOriginal[enc]
		end
	end
	poses[noob] = nome
end

local cacheAnim = {} -- tabela forte: com chaves fracas o Roblox pode coletar o proxy da Instance e perder a entrada
function AnimKit.anim(noob, nome, opcoes)
	opcoes = opcoes or {}
	-- Pose fixa (ex.: pernas esticadas) so vale junto da animacao para a qual foi feita.
	if nome ~= "sentar" and not opcoes.manterPose and poses[noob] then AnimKit.pose(noob, nil) end
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
	local sobe = AnimKit.ELEVACAO_PASSO[animNome or "andar"] or 0
	if animNome ~= false then AnimKit.anim(noob, animNome or "andar", { fade = 0.08 }) end
	-- O ciclo de passada desce o pe abaixo do nivel parado: o corpo sobe um pouco enquanto anda.
	r.CFrame = r.CFrame + Vector3.new(0, sobe, 0)
	local tw = tween(r, t, { CFrame = destino + Vector3.new(0, sobe, 0) }, Enum.EasingStyle.Linear)
	if animNome ~= false then
		tw.Completed:Connect(function()
			-- Primeiro a perna sai da passada (pose aplicada no proximo quadro), depois o corpo desce.
			AnimKit.anim(noob, "idle", { fade = 0 })
			RunService.Heartbeat:Wait()
			r.CFrame = r.CFrame - Vector3.new(0, sobe, 0)
		end)
	end
	return tw
end

-- Percorre uma lista de pontos (ex.: AnimKit.caminho(escorregador)) em t segundos, sentado.
function AnimKit.deslizar(noob, pontos, t, anim, aoTerminar)
	local r = raiz(noob)
	local total = 0
	for i = 2, #pontos do total += (pontos[i] - pontos[i - 1]).Magnitude end
	AnimKit.anim(noob, anim or "sentar", { fade = 0 })
	if (anim or "sentar") == "sentar" then AnimKit.pose(noob, "sentadoReto") end
	task.spawn(function()
		-- Orientacao em cada ponto = bissetriz dos trechos vizinhos: o corpo ja chega inclinado certo
		-- em cada dobra e as pernas acompanham a superficie.
		local function cfPonto(i)
			local dentro = i > 1 and (pontos[i] - pontos[i - 1]).Unit or nil
			local fora = i < #pontos and (pontos[i + 1] - pontos[i]).Unit or nil
			local d = ((dentro or fora) + (fora or dentro)).Unit
			return CFrame.lookAt(pontos[i], pontos[i] + d, normalDe(d))
		end
		-- Guiado pelo relogio (nao por tweens encadeados): termina exatamente em t segundos, sem o
		-- atraso de um quadro por trecho que deixava o pouso fora do tempo planejado.
		local acum = { 0 }
		for i = 2, #pontos do acum[i] = acum[i - 1] + (pontos[i] - pontos[i - 1]).Magnitude end
		local cfs = {}
		for i = 1, #pontos do cfs[i] = cfPonto(i) end
		local t0 = os.clock()
		-- Primeira posicao ja no assento inclinado, no mesmo quadro do corte (sem um quadro sentado reto).
		r.CFrame = cfs[1]
		local con
		con = RunService.Heartbeat:Connect(function()
			local k = math.clamp((os.clock() - t0) / t, 0, 1)
			local d = k * total
			local i = 2
			while i < #pontos and acum[i] < d do i += 1 end
			local seg = acum[i] - acum[i - 1]
			local u = seg > 0 and (d - acum[i - 1]) / seg or 1
			r.CFrame = cfs[i - 1]:Lerp(cfs[i], u)
			if k >= 1 then
				con:Disconnect()
				if aoTerminar then aoTerminar() end
			end
		end)
	end)
end

-- Voo em arco (parabola) ate destino, com giro opcional (voltas).
-- Senta o noob num ponto de assento (ex.: K.caminho(escorregador)[1]) olhando para 'frente'.
-- A pose sentada entra sem mistura: as pernas esticadas nunca aparecem atravessando o assento.
function AnimKit.sentarEm(noob, ponto, frente)
	AnimKit.anim(noob, "sentar", { fade = 0 })
	AnimKit.pose(noob, "sentadoReto")
	-- A pose so e aplicada no proximo quadro: espera um quadro antes de mover o corpo para o assento.
	RunService.Heartbeat:Wait()
	raiz(noob).CFrame = CFrame.lookAt(ponto, ponto + (frente or Vector3.new(0, 0, -1)))
end

-- Corte para outro lugar com outra animacao, sem o quadro do "noob sentado no lugar novo": o
-- Animator so aplica a animacao (e a pose) no passo seguinte. Troca agora, ainda no plano antigo
-- (a tela nao muda nesse quadro), e so no quadro seguinte muda o noob de lugar e corta a camera.
-- camera: funcao com os cortes/movimentos do plano novo.
function AnimKit.cortarPara(noob, cf, anim, camera, opcoes)
	opcoes = opcoes or {}
	AnimKit.anim(noob, anim, { fade = 0, loop = opcoes.loop })
	if opcoes.pose then AnimKit.pose(noob, opcoes.pose) end
	RunService.Heartbeat:Wait()
	raiz(noob).CFrame = cf
	if camera then camera() end
end

-- Carrega todas as animacoes antes da cena: na primeira vez que uma animacao toca ela ainda esta
-- baixando e o boneco fica alguns quadros na pose errada (pernas atravessando rampas, por exemplo).
function AnimKit.preCarregar(noob, nomes)
	local animator = noob:FindFirstChildOfClass("Humanoid"):FindFirstChildOfClass("Animator")
	local lista = {}
	for _, nome in ipairs(nomes or { "idle", "andar", "correr", "sentar", "cair", "apontar", "acenar", "comemorar", "rir" }) do
		local a = Instance.new("Animation")
		a.AnimationId = "rbxassetid://" .. tostring(AnimKit.ANIM[nome] or nome)
		lista[#lista + 1] = a
	end
	pcall(function() game:GetService("ContentProvider"):PreloadAsync(lista) end)
	for i, a in ipairs(lista) do
		local tr = animator:LoadAnimation(a)
		tr:Play(0, 0.001)
		task.wait()
		tr:Stop(0)
	end
end

-- destino: Vector3 ou CFrame. Com CFrame (ex.: K.deitado), as cambalhotas acabam aos 75% do voo e o
-- corpo gira suavemente ate a pose final: nunca chega em pe no chao (o que enfiaria as pernas na terra).
function AnimKit.voar(noob, destino, altura, t, voltas, anim, aoPousar)
	local r = raiz(noob)
	local a = r.Position
	local orient = r.CFrame - r.Position
	local final = typeof(destino) == "CFrame" and (destino - destino.Position) or nil
	local alvo = typeof(destino) == "CFrame" and destino.Position or destino
	-- A pose de queda (pernas esticadas) so entra depois que ele ja subiu: saindo sentado de uma
	-- rampa, trocar a pose no chao enfiaria as pernas na saida.
	local trocou = false
	local t0 = os.clock()
	local con
	con = RunService.RenderStepped:Connect(function()
		local k = math.clamp((os.clock() - t0) / t, 0, 1)
		if not trocou and k >= 0.15 then
			trocou = true
			AnimKit.anim(noob, anim or "cair", { fade = 0.1 })
		end
		local p = a:Lerp(alvo, k) + Vector3.new(0, 4 * altura * k * (1 - k), 0)
		local rot
		if final then
			-- Cambalhotas so depois de ganhar altura (de 15% a 75% do voo).
			local giro = math.clamp((k - 0.15) / 0.6, 0, 1)
			-- Rolamento em volta do eixo da frente: o rosto continua virado para a camera da frente.
			rot = orient * CFrame.Angles(0, 0, math.pi * 2 * (voltas or 0) * giro)
			if k > 0.75 then
				local e = TweenService:GetValue((k - 0.75) / 0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
				rot = rot:Lerp(final, e)
			end
		else
			rot = orient * CFrame.Angles(0, 0, math.pi * 2 * (voltas or 0) * k)
		end
		r.CFrame = CFrame.new(p) * rot
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
	local dof = game:GetService("Lighting"):FindFirstChild("AK_Foco")
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
		-- Foco na cabeca do protagonista: closes com o fundo bem desfocado, planos abertos menos.
		dof = dof or game:GetService("Lighting"):FindFirstChild("AK_Foco")
		if dof and AnimKit._foco and AnimKit._foco.Parent then
			local d = (workspace.CurrentCamera.CFrame.Position - AnimKit._foco.Position).Magnitude
			dof.FocusDistance = d
			dof.InFocusRadius = math.clamp(d * 0.45, 2.5, 30)
		end
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
	-- O cursor do mouse e desenhado dentro do viewport e apareceria na gravacao.
	pcall(function() game:GetService("UserInputService").MouseIconEnabled = false end)
	local SG = game:GetService("StarterGui")
	pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.All, false) end)
	for _ = 1, 20 do
		if pcall(function() SG:SetCore("TopbarEnabled", false) end) then break end
		task.wait(0.1)
	end
end

-- eventos: { {t = 0.0, f = function() ... end}, ... }  (t em segundos desde o t=0 da timeline)
-- duracao: tempo total da cena; um segundo flash magenta marca o fim.
-- Marca de sincronia: um retangulo magenta no alto do viewport, na faixa que a gravacao corta
-- (botoes do Roblox). Acende no mesmo passo dos eventos da cena, entao o quadro em que ela aparece
-- na gravacao mede o atraso real entre agendar e aparecer (captura_janela.medir_sincronia).
AnimKit.MARCAS = 5 -- segundos entre marcas de sincronia (0 desliga)
local function marca(t)
	local pg = Players.LocalPlayer:WaitForChild("PlayerGui")
	local g = Instance.new("ScreenGui")
	g.Name = "AnimKitMarca"
	g.IgnoreGuiInset = true
	g.DisplayOrder = 1e6
	g.ScreenInsets = Enum.ScreenInsets.None
	local f = Instance.new("Frame")
	f.AnchorPoint = Vector2.new(0.5, 0)
	f.Position = UDim2.new(0.5, 0, 0, 2)
	f.Size = UDim2.new(0, 160, 0, 14)
	f.BackgroundColor3 = Color3.fromRGB(255, 0, 255)
	f.BorderSizePixel = 0
	f.Parent = g
	g.Parent = pg
	task.delay(t, function() g:Destroy() end)
end

function AnimKit.rodar(eventos, duracao)
	esconderInterface()
	workspace.CurrentCamera.CameraType = Enum.CameraType.Scriptable
	if AnimKit.MARCAS and AnimKit.MARCAS > 0 then
		for tm = 0.5, duracao - 0.2, AnimKit.MARCAS do
			eventos[#eventos + 1] = { t = tm, f = function() marca(0.12) end }
		end
	end
	table.sort(eventos, function(a, b) return a.t < b.t end)
	-- Primeiro quadro ja enquadrado (evita a camera padrao no inicio da gravacao).
	for _, e in ipairs(eventos) do
		if e.t <= 0 then task.spawn(e.f) end
	end
	task.wait(1.5)
	flash(0.3)
	task.wait(AnimKit.ATRASO)
	local t0 = os.clock()
	AnimKit._t0 = t0
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
			if AnimKit._relatorio then AnimKit._relatorio() end
			task.delay(0.8, AnimKit.encerrar)
		end
	end)
end

-- Tempo da timeline em segundos (-1 antes do inicio).
function AnimKit.tempo()
	return AnimKit._t0 and (os.clock() - AnimKit._t0) or -1
end

-- Auditoria automatica: 20 vezes por segundo verifica, com a geometria exata, se alguma parte do
-- corpo (encolhida 0.12 stud de cada lado, para tolerar o contato) entra no chao ou em qualquer
-- objeto solido. No fim imprime "[auditoria]" com cada intervalo de tempo e o objeto atravessado;
-- o pipeline le essas linhas e a cena deve ser corrigida ate nao sobrar nenhuma.
function AnimKit.auditar(noob, folga)
	folga = folga or 0.12
	local pasta = Instance.new("Folder")
	pasta.Name = "AuditoriaSondas"
	pasta.Parent = workspace
	local sondas = {}
	for _, parte in ipairs(noob:GetDescendants()) do
		if parte:IsA("BasePart") and parte.Name ~= "HumanoidRootPart" and parte.Name ~= "RostoPlaca" then
			local s = Instance.new("Part")
			s.Anchored = true
			s.CanCollide = false
			s.CanQuery = false
			s.CanTouch = false
			s.Transparency = 1
			s.Parent = pasta
			sondas[#sondas + 1] = { parte = parte, sonda = s }
		end
	end
	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { noob, pasta }
	local abertos, achados = {}, {}
	local prox = 0
	local con = RunService.Heartbeat:Connect(function()
		local t = AnimKit.tempo()
		if t < 0 or os.clock() < prox then return end
		prox = os.clock() + 0.05
		local agora = {}
		for _, item in ipairs(sondas) do
			local parte = item.parte
			local tam = parte.Size
			if parte.Name == "Head" then
				local m = parte:FindFirstChildOfClass("SpecialMesh")
				tam = m and Vector3.new(1, 1, 1) * 0.95 * m.Scale.X or parte.Size * 0.95
			end
			item.sonda.Size = Vector3.new(math.max(0.05, tam.X - 2 * folga), math.max(0.05, tam.Y - 2 * folga), math.max(0.05, tam.Z - 2 * folga))
			item.sonda.CFrame = parte.CFrame
			for _, outro in ipairs(workspace:GetPartsInPart(item.sonda, params)) do
				if outro.Transparency < 0.95 and outro.CanCollide then
					local chave = parte.Name .. " x " .. outro:GetFullName()
					if not agora[chave] and not abertos[chave] and AnimKit.AUDITORIA_DETALHE then
						local r = noob.HumanoidRootPart
						print(string.format("[auditoria-detalhe] t=%.2f %s raiz=(%.2f,%.2f,%.2f) frente=(%.2f,%.2f,%.2f) parte=(%.2f,%.2f,%.2f) cima=(%.2f,%.2f,%.2f)",
							t, chave, r.Position.X, r.Position.Y, r.Position.Z, r.CFrame.LookVector.X, r.CFrame.LookVector.Y, r.CFrame.LookVector.Z,
							parte.Position.X, parte.Position.Y, parte.Position.Z, parte.CFrame.UpVector.X, parte.CFrame.UpVector.Y, parte.CFrame.UpVector.Z))
					end
					agora[chave] = true
				end
			end
		end
		for chave in pairs(agora) do
			if not abertos[chave] then abertos[chave] = { t, t } else abertos[chave][2] = t end
		end
		for chave, faixa in pairs(abertos) do
			if not agora[chave] then
				achados[#achados + 1] = { chave = chave, a = faixa[1], b = faixa[2] }
				abertos[chave] = nil
			end
		end
	end)
	AnimKit._relatorio = function()
		con:Disconnect()
		for chave, faixa in pairs(abertos) do
			achados[#achados + 1] = { chave = chave, a = faixa[1], b = faixa[2] }
		end
		table.sort(achados, function(x, y) return x.a < y.a end)
		for _, f in ipairs(achados) do
			print(string.format("[auditoria] %.2f-%.2fs %s", f.a, f.b, f.chave))
		end
		print(string.format("[auditoria] total %d problema(s)", #achados))
		pasta:Destroy()
	end
end

-- Planos sem o protagonista (ex.: mostrar cada opcao) sao marcados como inserto: a auditoria de
-- camera nao cobra rosto neles.
function AnimKit.inserto(ligado)
	AnimKit._inserto = ligado and true or false
end

-- Ponto do viewport -> posicao no video final (0..1 a partir da esquerda e de cima), refazendo o
-- que captura_janela.processar faz: corta a faixa de cima do viewport (botoes do Roblox), desvira
-- a camera deitada (transpose=2: a coluna da direita do viewport vira a linha de cima do video) e
-- corta o 9:16 no centro. As auditorias medem no quadro que vai para o video, nao no viewport.
local function noVideo(p, vp)
	local corte = vp.Y * AnimKit.MARGEM_TOPO
	local x, y, largo, alto
	if AnimKit.VERTICAL then
		x, y, largo, alto = p.Y - corte, vp.X - p.X, vp.Y - corte, vp.X
	else
		x, y, largo, alto = p.X, p.Y - corte, vp.X, vp.Y - corte
	end
	local tw, th = largo, alto
	if alto * 9 >= largo * 16 then th = largo * 16 / 9 else tw = alto * 9 / 16 end
	return (x - (largo - tw) / 2) / tw, (y - (alto - th) / 2) / th
end
AnimKit.noVideo = noVideo

-- Auditoria de camera (regra no 1: o rosto e o protagonista). 10 vezes por segundo projeta a
-- cabeca no quadro final e mede o tamanho dela (fracao da altura do video) e o angulo entre a
-- camera e o olhar. Fora de insertos reporta: "rosto pequeno" (< minimo), "de costas" (> 100 graus),
-- "de perfil" (> 60 graus por mais de 0,5 s), "rosto fora do quadro", "rosto cortado na borda"
-- (parte da cabeca fora do 9:16 por mais de 0,2 s) e "rosto na faixa da legenda" (olhos/boca atras
-- das legendas por mais de 0,3 s: a regra e rosto no terco de cima; mire abaixo da cabeca).
function AnimKit.auditarCamera(noob, minimo)
	minimo = minimo or 0.08
	local abertos, achados = {}, {}
	local prox = 0
	-- Mede logo depois da camera do kit (prioridade Camera + 1) no mesmo quadro: no Heartbeat a camera
	-- ainda estaria um quadro atrasada e, com o Studio em segundo plano (poucos FPS), um noob rapido
	-- pareceria fora do lugar.
	local NOME = "AnimKitAuditoriaCamera"
	RunService:BindToRenderStep(NOME, Enum.RenderPriority.Camera.Value + 2, function()
		local t = AnimKit.tempo()
		if t < 0 or os.clock() < prox then return end
		prox = os.clock() + 0.1
		local agora = {}
		if not AnimKit._inserto then
			local cam = workspace.CurrentCamera
			local h = noob.Head
			local vp = cam.ViewportSize
			local function video(cf)
				local p, naFrente = cam:WorldToViewportPoint(cf.Position)
				local x, y = noVideo(p, vp)
				return Vector2.new(x, y), naFrente
			end
			local function dentro(p, folga)
				return p.X >= -folga and p.X <= 1 + folga and p.Y >= -folga and p.Y <= 1 + folga
			end
			-- Distancia no video medida em alturas do quadro (x e y sao normalizados por lados diferentes).
			local function emAltura(a, b)
				return Vector2.new((a.X - b.X) * 9 / 16, a.Y - b.Y).Magnitude
			end
			local s = h.Size / 2
			local centro, naFrente = video(h.CFrame)
			local topo, base = video(h.CFrame * CFrame.new(0, s.Y, 0)), video(h.CFrame * CFrame.new(0, -s.Y, 0))
			local esq, dir = video(h.CFrame * CFrame.new(-s.X, 0, 0)), video(h.CFrame * CFrame.new(s.X, 0, 0))
			-- Maior lado da cabeca na tela (altura ou largura): numa cambalhota/rolamento a cabeca fica
			-- de lado e so a altura subestimaria o tamanho do rosto.
			local fracao = math.max(emAltura(topo, base), emAltura(esq, dir))
			local paraCamera = (cam.CFrame.Position - h.Position).Unit
			local ang = math.deg(math.acos(math.clamp(h.CFrame.LookVector:Dot(paraCamera), -1, 1)))
			if not naFrente or not dentro(centro, 0) then
				agora["rosto fora do quadro"] = true
			else
				if not (dentro(topo, 0.01) and dentro(base, 0.01) and dentro(esq, 0.01) and dentro(dir, 0.01)) then
					agora["rosto cortado na borda"] = true
				end
				if fracao < minimo then agora[string.format("rosto pequeno (< %d%%)", minimo * 100)] = true end
				if ang > 100 then agora["de costas"] = true elseif ang > 60 then agora["de perfil"] = true end
				-- Desenho do rosto inteiro (a placa: sobrancelhas ate o fim da boca de grito) contra a faixa
				-- das legendas, com folga para o zoom que a edicao aplica nas cenas de acao.
				local placa = noob:FindFirstChild("RostoPlaca")
				if placa and ang <= 100 then
					-- So a area desenhada (sobrancelha ate o fim da boca de grito), nao a placa inteira.
					local h = placa.Size.Y
					local cima = (0.5 - (placa:GetAttribute("FaixaTopo") or 0)) * h
					local baixo = (0.5 - (placa:GetAttribute("FaixaBase") or 1)) * h
					local a, b = video(placa.CFrame * CFrame.new(0, cima, 0)), video(placa.CFrame * CFrame.new(0, baixo, 0))
					local f0, f1 = AnimKit.FAIXA_LEGENDA[1], AnimKit.FAIXA_LEGENDA[2]
					if math.max(a.Y, b.Y) > f0 and math.min(a.Y, b.Y) < f1 then
						agora["rosto na faixa da legenda"] = true
					end
					if AnimKit.AUDITORIA_DETALHE and t >= (AnimKit._proxDetalheCam or 0) then
						AnimKit._proxDetalheCam = t + 0.5
						print(string.format("[camera-detalhe] %.2fs rosto %.3f-%.3f centro %.3f,%.3f tamanho %.3f viewport %dx%d",
							t, math.min(a.Y, b.Y), math.max(a.Y, b.Y), centro.X, centro.Y, fracao, vp.X, vp.Y))
					end
				end
			end
		end
		for chave in pairs(agora) do
			if not abertos[chave] then abertos[chave] = { t, t } else abertos[chave][2] = t end
		end
		for chave, faixa in pairs(abertos) do
			if not agora[chave] then
				achados[#achados + 1] = { chave = chave, a = faixa[1], b = faixa[2] }
				abertos[chave] = nil
			end
		end
	end)
	local anterior = AnimKit._relatorio
	AnimKit._relatorio = function()
		if anterior then anterior() end
		RunService:UnbindFromRenderStep(NOME)
		for chave, faixa in pairs(abertos) do
			achados[#achados + 1] = { chave = chave, a = faixa[1], b = faixa[2] }
		end
		table.sort(achados, function(x, y) return x.a < y.a end)
		local n = 0
		-- Passagens curtas nao contam (virar a cabeca, cruzar a faixa da legenda num movimento);
		-- costas e rosto fora contam sempre. Amostras a cada 0,1 s: b - a mede a duracao menos 0,1 s.
		local curto = { ["de perfil"] = 0.5, ["rosto na faixa da legenda"] = 0.3, ["rosto cortado na borda"] = 0.2 }
		for _, f in ipairs(achados) do
			if f.b - f.a + 0.1 > (curto[f.chave] or 0) then
				n += 1
				print(string.format("[camera] %.2f-%.2fs %s", f.a, f.b, f.chave))
			end
		end
		print(string.format("[camera] total %d problema(s)", n))
	end
end

-- Parte em que a camera foca (normalmente noob.Head); nil volta o foco fixo.
function AnimKit.foco(parte)
	AnimKit._foco = parte
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
