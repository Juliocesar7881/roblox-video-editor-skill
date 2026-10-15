"""Base comum das cenas do lote: timeline a partir das falas reais, eventos Luau, boca guiada pela voz,
ajudantes Luau (mover/escalar/arremessar/soldar/partículas) e montagem do cenário.

Uso dentro de NN-projeto/gerar_cena.py:
    import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from comum import Cena
    c = Cena(__file__)
    ... c.ini['01'] = 0.3 ... c.E(t, 'lua') ... c.corte(t)
    c.escrever(fim, lua_extra='', tempos={...})
"""
import argparse, json, re, sys, unicodedata
from pathlib import Path

LOTE = Path(__file__).resolve().parent
SKILL = Path.home() / '.claude' / 'skills' / 'roblox-shorts-animator'
sys.path.insert(0, str(SKILL / 'scripts'))


def norm(t):
    t = unicodedata.normalize('NFKD', t)
    t = ''.join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r'[^a-z0-9]', '', t.lower())


def estimar(roteiro, chave='texto'):
    falas = []
    for f in roteiro['falas']:
        ws, t = [], 0.0
        for w in f[chave].split():
            d = 0.12 + 0.055 * len(w)
            ws.append({'w': w, 'start': round(t, 3), 'end': round(t + d, 3)})
            t += d + (0.25 if re.search(r'[.!?,]$', w) else 0.04)
        falas.append({'id': f['id'], 'texto': f[chave], 'duracao': round(ws[-1]['end'], 3), 'palavras': ws,
                      'arquivo': None})
    return falas


class Cena:
    def __init__(self, arquivo):
        ap = argparse.ArgumentParser()
        ap.add_argument('--estimado', action='store_true')
        ap.add_argument('--sem-auditoria', action='store_true')
        ap.add_argument('--idioma', default='pt')
        self.a = ap.parse_args()
        self.proj = Path(arquivo).resolve().parent
        self.idioma = self.a.idioma
        self.suf = '' if self.idioma == 'pt' else f'-{self.idioma}'
        self.roteiro = json.loads((self.proj / 'roteiro.json').read_text(encoding='utf-8'))
        chave = 'texto' if self.idioma == 'pt' else f'texto_{self.idioma}'
        if self.a.estimado:
            self.falas = estimar(self.roteiro, chave)
        else:
            self.falas = json.loads((self.proj / f'falas{self.suf}' / 'falas.json').read_text(encoding='utf-8'))
        self.F = {f['id']: f for f in self.falas}
        self.ini = {}
        self.ev = []
        self.cortes = []
        montar_cenario(self.proj)

    # ---- tempos das falas
    def d(self, i):
        return self.F[i]['duracao']

    def fim_fala(self, i):
        return self.ini[i] + self.F[i]['palavras'][-1]['end']

    def w(self, i, *alvos, n=0, fim=False):
        """Instante absoluto da n-ésima palavra da fala i que contém um dos alvos (sem acento)."""
        achou = []
        for p in self.F[i]['palavras']:
            if any(norm(a) in norm(p['w']) for a in alvos):
                achou.append(p)
        if not achou:
            raise KeyError(f'{alvos} não está na fala {i}: {[p["w"] for p in self.F[i]["palavras"]]}')
        p = achou[min(n, len(achou) - 1)]
        return self.ini[i] + (p['end'] if fim else p['start'])

    def opcao(self, k):
        """Palavra da opção k (roteiro['opcoes'][idioma][k]) na fala 02."""
        return self.w('02', self.roteiro['opcoes'][self.idioma][k])

    # ---- eventos
    def E(self, t, corpo):
        self.ev.append((t, corpo))

    def corte(self, t):
        self.cortes.append(t)
        return t

    def ate_corte(self, t, folga=0.05):
        """Duração de um travelling/zoom que começa em t e termina antes do próximo corte (registre os cortes antes)."""
        prox = min([c for c in self.cortes if c > t + 0.01] or [t + 99])
        return round(max(0.2, prox - t - folga), 3)

    def conferir_movimentos(self, fim):
        """Recusa travelling de câmera (cam.mover / cam.rosto com t) que um corte interrompe antes de terminar."""
        cortes = sorted(self.cortes) + [fim]
        erros = []
        for t, corpo in self.ev:
            for dur in _duracoes_camera(corpo):
                prox = next((c for c in cortes if c > t + 0.01), fim)
                if t + dur > prox + 0.02:
                    erros.append(f'travelling em {t:.2f}s dura {dur:.2f}s mas o corte vem em {prox:.2f}s '
                                 f'(use c.ate_corte({t:.2f}) = {max(0.2, prox - t - 0.05):.2f})')
        for e in erros:
            print('[movimento]', e)
        if erros:
            raise SystemExit(f'{len(erros)} movimento(s) de câmera cortado(s) antes de terminar (acima)')

    def escrever(self, fim, lua_extra='', tempos=None):
        self.conferir_movimentos(fim)
        if not self.a.estimado:
            from envelope_boca import envelope
            for f in self.falas:
                env = envelope(self.proj / f'falas{self.suf}' / f['arquivo'])
                self.E(self.ini[f['id']], f'\t\tK.falar(noob, "{env}", 30)')
        evs = '\n'.join(f'\t{{t = {t:.3f}, f = function()\n{c}\n\tend}},' for t, c in sorted(self.ev, key=lambda x: x[0]))
        auditoria = '' if self.a.sem_auditoria else 'K.AUDITORIA_DETALHE = true\nK.auditar(noob)\nK.auditarCamera(noob)\n'
        lua = (f'-- Gerado por gerar_cena.py ({self.idioma}). Duração {fim:.2f}s.\n' + LUA_COMUM + '\n' + lua_extra + '\n'
               + 'K.piscar(noob)\nK.preCarregar(noob)\nK.foco(noob.Head)\nK.anim(noob, "idle", {fade = 0})\n'
               + auditoria + 'K.rodar({\n' + evs + f'\n}}, {fim:.3f})\n')
        (self.proj / 'studio' / f'cena{self.suf}.lua').write_text(lua, encoding='utf-8')
        dados = {'falas': self.ini, 'cortes': sorted(round(c, 3) for c in self.cortes), 'fim': round(fim, 3),
                 'estimado': self.a.estimado}
        dados.update(tempos or {})
        (self.proj / f'tempos{self.suf}.json').write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding='utf-8')
        print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in dados.items() if k != 'falas'},
                         ensure_ascii=False))


def _args(texto, ini):
    """Argumentos de nível zero de uma chamada que começa em texto[ini] (logo depois do '(')."""
    nivel, atual, args = 0, '', []
    for ch in texto[ini:]:
        if ch in '({[':
            nivel += 1
        elif ch in ')}]':
            if nivel == 0:
                args.append(atual.strip())
                return args
            nivel -= 1
        if ch == ',' and nivel == 0:
            args.append(atual.strip())
            atual = ''
        else:
            atual += ch
    return args


def _duracoes_camera(corpo):
    """Durações numéricas dos travellings de câmera num evento Luau (cam.mover 3º argumento, cam.rosto {t = ...})."""
    out = []
    for m in re.finditer(r'cam\.mover\(', corpo):
        a = _args(corpo, m.end())
        if len(a) >= 3:
            try:
                out.append(float(a[2]))
            except ValueError:
                pass
    for m in re.finditer(r'cam\.rosto\(', corpo):
        a = _args(corpo, m.end())
        if len(a) >= 4:
            t = re.search(r'(?<![A-Za-z_])t\s*=\s*([\d.]+)', a[3])
            if t:
                out.append(float(t.group(1)))
    return out


def montar_cenario(proj):
    corpo = proj / 'studio' / 'cenario_corpo.lua'
    if corpo.exists():
        cab = (LOTE / 'cenario_comum.lua').read_text(encoding='utf-8')
        (proj / 'studio' / 'cenario.lua').write_text(cab + '\n' + corpo.read_text(encoding='utf-8') + '\nprint("cenario ok")\n',
                                                    encoding='utf-8')


LUA_COMUM = r'''
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local K = require(RS:WaitForChild("AnimKit"))
local noob = workspace:WaitForChild("Noob")
local raiz = noob:WaitForChild("HumanoidRootPart")
local cam = K.camera
local V = Vector3.new
local C = Color3.fromRGB
local CF = CFrame.new
local ANG = CFrame.Angles
local rad = math.rad
local inicio = raiz.CFrame
local function W(nome) return workspace:WaitForChild(nome) end

-- Animação por quadro: f(k, e) com k de 0 a 1 em t segundos (e = k suavizado).
local function animar(t, f, estilo, direcao)
	local t0 = os.clock()
	local con
	con = RunService.Heartbeat:Connect(function()
		local k = math.clamp((os.clock() - t0) / math.max(t, 0.001), 0, 1)
		local e = TweenService:GetValue(k, estilo or Enum.EasingStyle.Sine, direcao or Enum.EasingDirection.InOut)
		f(k, e)
		if k >= 1 then con:Disconnect() end
	end)
	return con
end

local function pivo(obj) return obj:IsA("Model") and obj:GetPivot() or obj.CFrame end
local function porPivo(obj, cf) if obj:IsA("Model") then obj:PivotTo(cf) else obj.CFrame = cf end end

-- Move (e gira) um modelo ou peça até 'para' (CFrame) em t segundos.
function mover(obj, para, t, estilo, direcao)
	local de = pivo(obj)
	return animar(t, function(k, e) porPivo(obj, de:Lerp(para, e)) end, estilo, direcao)
end

-- Escala de um modelo (Model:ScaleTo) até 'fator' (absoluto) em t segundos.
function escalar(m, fator, t, estilo, direcao)
	local de = m:GetScale()
	return animar(t, function(k, e) m:ScaleTo(math.max(0.001, de + (fator - de) * e)) end, estilo or Enum.EasingStyle.Back,
		direcao or Enum.EasingDirection.Out)
end

-- Arremesso em arco até 'destino' (Vector3) com 'altura' extra no meio, girando 'voltas'.
function arco(obj, destino, altura, t, voltas, aoChegar)
	local de = pivo(obj)
	local a = de.Position
	local rot = de - de.Position
	return animar(t, function(k)
		local p = a:Lerp(destino, k) + V(0, 4 * altura * k * (1 - k), 0)
		porPivo(obj, CF(p) * rot * ANG(rad(360 * (voltas or 0) * k), 0, 0))
		if k >= 1 and aoChegar then aoChegar() end
	end, Enum.EasingStyle.Linear)
end

-- Solda um modelo/peça numa parte do corpo, na posição atual (ou em 'cf' relativo à parte).
local soldas = {}
function soldar(obj, parte, cf)
	local base = obj:IsA("Model") and obj.PrimaryPart or obj
	if cf then porPivo(obj, parte.CFrame * cf) end
	base.Anchored = false
	local w = Instance.new("WeldConstraint")
	w.Part0, w.Part1 = parte, base
	w.Parent = base
	soldas[obj] = w
end
function soltar(obj)
	local base = obj:IsA("Model") and obj.PrimaryPart or obj
	local cf = pivo(obj)
	if soldas[obj] then soldas[obj]:Destroy() soldas[obj] = nil end
	base.Anchored = true
	porPivo(obj, cf)
end

-- Mostra/esconde (transparência) guardando a original.
local transp0 = {}
function mostrar(obj, visivel, t)
	local partes = obj:IsA("BasePart") and { obj } or {}
	for _, p in ipairs(obj:GetDescendants()) do if p:IsA("BasePart") then partes[#partes + 1] = p end end
	for _, p in ipairs(partes) do
		if transp0[p] == nil then transp0[p] = p:GetAttribute("Transp0") or p.Transparency end
		local alvo = visivel and transp0[p] or 1
		if t and t > 0 then
			TweenService:Create(p, TweenInfo.new(t), { Transparency = alvo }):Play()
		else
			p.Transparency = alvo
		end
		for _, d in ipairs(p:GetChildren()) do
			if d:IsA("Decal") or d:IsA("Texture") then d.Transparency = visivel and 0 or 1 end
			if d:IsA("SurfaceGui") then d.Enabled = visivel end
		end
	end
end

-- Muda a cor de todas as peças (ou só das de nome 'filtro') em t segundos.
function pintar(obj, cor, t, filtro)
	local partes = obj:IsA("BasePart") and { obj } or {}
	for _, p in ipairs(obj:GetDescendants()) do if p:IsA("BasePart") then partes[#partes + 1] = p end end
	for _, p in ipairs(partes) do
		if not filtro or p.Name == filtro then
			TweenService:Create(p, TweenInfo.new(t or 0.3), { Color = cor }):Play()
		end
	end
end

-- Explosão de partículas (cor, quantidade) num ponto.
function estouro(pos, cor, n, tam, vel, textura)
	local p = Instance.new("Part")
	p.Anchored, p.CanCollide, p.CanQuery, p.Transparency = true, false, false, 1
	p.Size = V(1, 1, 1)
	p.CFrame = CF(pos)
	local e = Instance.new("ParticleEmitter")
	e.Texture = textura or "rbxasset://textures/particles/sparkles_main.dds"
	e.Color = typeof(cor) == "ColorSequence" and cor or ColorSequence.new(cor or Color3.new(1, 1, 1))
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, tam or 0.8), NumberSequenceKeypoint.new(1, 0) })
	e.Lifetime = NumberRange.new(0.5, 1.0)
	e.Speed = NumberRange.new(vel or 8, (vel or 8) * 1.6)
	e.SpreadAngle = Vector2.new(180, 180)
	e.Acceleration = V(0, -12, 0)
	e.LightEmission = 0.5
	e.Rate = 0
	e.Parent = p
	p.Parent = workspace
	e:Emit(n or 30)
	task.delay(2.5, function() p:Destroy() end)
end

-- Emissor contínuo preso a uma peça; devolve o emissor (Rate = 0 desliga).
function emissor(parte, cor, taxa, tam, vel, textura)
	local e = Instance.new("ParticleEmitter")
	e.Texture = textura or "rbxasset://textures/particles/sparkles_main.dds"
	e.Color = typeof(cor) == "ColorSequence" and cor or ColorSequence.new(cor or Color3.new(1, 1, 1))
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, tam or 0.6), NumberSequenceKeypoint.new(1, 0) })
	e.Lifetime = NumberRange.new(0.6, 1.1)
	e.Speed = NumberRange.new(vel or 2, (vel or 2) * 1.5)
	e.SpreadAngle = Vector2.new(180, 180)
	e.LightEmission = 0.6
	e.Rate = taxa or 15
	e.Parent = parte
	return e
end

-- Passos sem girar o corpo (continua de frente para a câmera).
function passo(dx, dz, t, anim)
	local de = raiz.CFrame
	local para = de + V(dx, 0, dz)
	K.anim(noob, anim or "andar", {fade = 0.1})
	return animar(t, function(k, e)
		raiz.CFrame = de:Lerp(para, e)
		if k >= 1 then K.anim(noob, "idle", {fade = 0.15}) end
	end)
end

-- Pulinho no lugar (comemorar, susto).
function pulo(altura, t)
	local de = raiz.CFrame
	return animar(t, function(k) raiz.CFrame = de + V(0, 4 * altura * k * (1 - k), 0) end, Enum.EasingStyle.Linear)
end
'''
