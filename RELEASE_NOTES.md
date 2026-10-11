Skills de Roblox para Claude: edição de gameplay (`roblox-video-editor`) e **nova** criação de Shorts animados no Roblox Studio (`roblox-shorts-animator`).

## v1.6.0 — legendas sem bugs, som de escorregador e rosto fora da legenda
- Legendas karaokê corrigidas: nunca duas ao mesmo tempo (cada evento com posição fixa e sem sobreposição), palavras curtas acendem junto com a vizinha (nada de destaque piscando), pausas sem destaque, fade curto na saída, tamanho medido na referência.
- Novo `roblox-video-editor/scripts/revisar_legendas.py`: renderiza só as legendas e aponta sobreposição, destaque piscando, legenda em duas linhas, texto cortado e legenda junto com sticker/selo. Obrigatório antes da versão final.
- Sons originais de escorregador (`scripts/criar_sfx_escorregador.py`, sintetizados, uso comercial livre): `escorregar-trava` (atrito que para com rangido de borracha aos 2,0 s), `escorregar-rapido` (atrito acelerando + lufada no lançamento aos 2,2 s), `escorregar-curto` e `apito-escorregador` (apito de desenho descendo). Receita conferida com classificador AudioSet ("Scrape", "Squeak", "Whoosh").
- Auditoria de câmera mede no quadro final (com os cortes da gravação), logo depois da câmera em cada quadro, e acusa "rosto na faixa da legenda" e "rosto cortado na borda"; `cam.seguir` aceita mira abaixo da cabeça.
- Piloto corrigido: rosto no terço de cima na descida e no escorregador vermelho, pouso visto de cima com o rosto à mostra, legendas fora da contagem, efeitos fora das falas.

## v1.5.0 — regras do roblox-shorts-generator, pacote de animação e boca falando
- Regras de produção do sistema de eibrunoruan/roblox-shorts-generator incorporadas (`references/regras-producao.md`): rosto como protagonista, colisões em 5 tempos, voz Roger com ID e idioma conferidos, contagem de 5 s, legendas, qualidade de imagem.
- Noob em R15 com os pacotes oficiais do Roblox: Cartoony (locomoção), Levitation e emotes R15; cabeça clássica maior via `HeadScale`; suporte a juntas `AnimationConstraint`.
- Boca sincronizada com a voz real (`K.falar` + `scripts/envelope_boca.py`).
- Auditoria de câmera (`K.auditarCamera`): rosto pequeno, de costas, de perfil ou fora do quadro; `K.inserto` para planos sem o protagonista.
- Sem tremedeira na contagem; voo com rolamento lateral (rosto para a câmera); descida guiada pelo relógio; pose sentado com pernas esticadas (`K.pose`).
- Corrigido: tabelas fracas que perdiam animações e poses ("animações perdidas"); rosto montado antes da escala da cabeça.
- Legendas "uma ideia por vez" com divisão equilibrada que nunca termina em artigo; Lilita One (OFL) com a receita do amigo: contorno `#10283E`, sombra para baixo, destaque `#FFE54F`, números em ciano, entrada elástica, encolhe se não couber.

## v1.4.0 — animação sem bugs e legendas no estilo das referências
- Auditoria automática no Studio (`K.auditar`): detecta, com tempo e peça, qualquer parte do corpo entrando no chão ou em objetos; a skill exige corrigir até zerar antes de gravar.
- Corrigido: noob enterrado no chão (o rig do Roblox vinha com a cabeça como PrimaryPart), pernas atravessando rampas nas dobras, pose sentada misturando com a em pé, passada de corrida, voo saindo da rampa, animações tocando antes de carregar.
- Novo estilo de legenda `karaoke`: 2–3 palavras, Fredoka One branca com contorno azul-marinho e sombra, palavra falada em amarelo, entrada com fade rápido (copiado dos Shorts de referência).
- Gravação sem cursor do mouse e sem os botões do Roblox.

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
