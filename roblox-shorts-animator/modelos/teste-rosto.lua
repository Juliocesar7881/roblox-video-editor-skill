-- Teste do rosto v2 e da sincronia da gravacao: close passando por todas as expressoes, fala com
-- envelope real e cortes de camera em tempos exatos (2,0 / 6,0 / 9,0 s) para medir o atraso.
local RS = game:GetService("ReplicatedStorage")
local K = require(RS:WaitForChild("AnimKit"))
local noob = workspace:WaitForChild("Noob")
local raiz = noob:WaitForChild("HumanoidRootPart")
local cam = K.camera
local inicio = raiz.CFrame
K.piscar(noob)
K.preCarregar(noob)
K.foco(noob.Head)
K.anim(noob, "idle", {fade = 0})

local ev = {
	{t = 0, f = function()
		raiz.CFrame = inicio
		K.rosto(noob, "normal")
		cam.rosto(noob, 4.2, 36, {altura = -0.4, queixo = 0.1})
	end},
	{t = 0.3, f = function()
		K.falar(noob, "000025777876446999986788767888888788998667898752355444210000000000", 30)
	end},
	{t = 2.0, f = function()
		cam.rosto(noob, 4.6, 38, {lado = 1.6, altura = -0.2, queixo = 0.1})
	end},
}
local lista = { "surpreso", "medo", "grito", "nervoso", "feliz", "sorrindo", "confiante", "bravo", "duvida", "tonto", "apertado", "nocaute", "normal" }
for i, nome in ipairs(lista) do
	ev[#ev + 1] = {t = 2.2 + (i - 1) * 0.8, f = function() K.rosto(noob, nome) end}
end
ev[#ev + 1] = {t = 6.0, f = function()
	cam.rosto(noob, 3.6, 34, {lado = -1.2, altura = -0.5, queixo = 0.1})
	K.olhar(noob, -0.7, 0.2)
end}
ev[#ev + 1] = {t = 9.0, f = function()
	cam.rosto(noob, 5.5, 40, {altura = -0.3, queixo = 0.1})
	K.olhar(noob, 0, 0)
	K.falar(noob, "000135656787667778888887667787777642000001355566555544577877666554100000000000001356666776667888999", 30)
end}
K.rodar(ev, 12.5)
