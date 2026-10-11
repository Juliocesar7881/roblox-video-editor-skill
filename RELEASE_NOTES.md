Skills de Roblox para Claude: edição de gameplay (`roblox-video-editor`) e **nova** criação de Shorts animados no Roblox Studio (`roblox-shorts-animator`).

## v1.3.0 — Shorts animados no Roblox Studio
- `/roblox-shorts-animator`: da ideia ao MP4. Roteiro no formato "qual X…? escolhe rápido + reviravolta", voz Roger (ElevenLabs), cena no Studio, gravação, edição e textos de publicação.
- Controle do Studio pela tarefa oficial `-task RunScript` (sem MCP, sem cliques); Play automático via `StudioTestService`, que encerra sozinho.
- Gravação só da janela do Studio (Windows Graphics Capture), mesmo atrás de outras janelas; sincronia e recorte automáticos por flash magenta; câmera "deitada" para o 9:16 sair nítido em 1080×1920 a 60 fps.
- AnimKit (Luau): noob com a skin das referências, rosto de desenho com 11 expressões, chão por raycast só em pisos marcados (os pés nunca afundam), escorregadores com assento na superfície da rampa, voo com pouso, poeira, câmera de close pela cabeça real.
- Voz: `tts_elevenlabs.py` (chave de API com tempos por palavra) ou site do ElevenLabs + `alinhar_falas.py` (Whisper local).
- Modelo completo do piloto "Qual escorregador é o mais rápido?" em `roblox-shorts-animator/modelos/`.

## Editor de gameplay
- Renderizador: modo `"entrega": "shorts"`, faixa de voz com a música abaixando sozinha, legendas `legenda` palavra a palavra com `*destaque*` amarelo.
- Sticker `linhas-velocidade` desaconselhado; para velocidade, use tremida e zoom.

**Download único:** `roblox-video-editor-completo.zip`. Extraia, execute `python install.py` e invoque `/roblox-video-editor` ou `/roblox-shorts-animator`.
