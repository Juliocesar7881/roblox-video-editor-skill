"""Install the AnimKit, build a scene and set the cutscene LocalScript in the open Roblox Studio place.

  python instalar_no_studio.py --animkit                       (ReplicatedStorage.AnimKit)
  python instalar_no_studio.py --cenario PROJETO/studio/cenario.lua   (roda em modo edicao)
  python instalar_no_studio.py --cena PROJETO/studio/cena.lua         (StarterPlayerScripts.Cena)
Os tres podem ir juntos, nessa ordem.
"""
import argparse, re
from pathlib import Path
from studio_mcp import Client, show

KIT = Path(__file__).resolve().parents[1] / 'luau' / 'AnimKit.lua'


def long_string(text):
    """Luau long-bracket literal that cannot be closed by the text itself."""
    n = 1
    while ']' + '=' * n + ']' in text:
        n += 1
    eq = '=' * n
    return f'[{eq}[\n{text}]{eq}]'


def set_source(parent_expr, cls, name, source):
    return f'''
local parent = {parent_expr}
local s = parent:FindFirstChild("{name}")
if s and not s:IsA("{cls}") then s:Destroy(); s = nil end
if not s then s = Instance.new("{cls}"); s.Name = "{name}"; s.Parent = parent end
local src = {long_string(source)}
local ok, err = pcall(function() s.Source = src end)
if not ok then
	local SES = game:GetService("ScriptEditorService")
	SES:UpdateSourceAsync(s, function() return src end)
end
print("{name} instalado:", #src, "caracteres")
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--animkit', action='store_true')
    ap.add_argument('--cenario', type=Path)
    ap.add_argument('--cena', type=Path)
    a = ap.parse_args()
    cli = Client()
    try:
        if a.animkit:
            show(cli.call('execute_luau', {'code': set_source('game:GetService("ReplicatedStorage")', 'ModuleScript', 'AnimKit',
                                                                KIT.read_text(encoding='utf-8'))}))
        if a.cenario:
            show(cli.call('execute_luau', {'code': a.cenario.read_text(encoding='utf-8')}))
        if a.cena:
            show(cli.call('execute_luau', {'code': set_source('game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")',
                                                                'LocalScript', 'Cena', a.cena.read_text(encoding='utf-8'))}))
    finally:
        cli.close()


if __name__ == '__main__':
    main()
