# Validação antes da publicação

## v1.6.0 (11 de outubro de 2026)

- 27 testes passaram, incluindo: legendas do piloto sem sobreposição e sem destaque < 0,16 s; `revisar_legendas.py` acusando sobreposição, pisca, quebra em duas linhas e legenda junto com selo; rangido do `escorregar-trava` terminando aos 2,0 s e silêncio depois; a conta de posição da auditoria de câmera batendo (±1%) com um marcador processado de verdade por `captura_janela.processar`.
- Piloto: `[auditoria] total 0`, `[camera] total 0` (rosto entre 0,30 e 0,49 da altura nas cenas de ação), `[legenda] total 0`; quadros revisados a cada 0,5 s e nas trocas de palavra; 1080×1920, 60 fps, −14,1 LUFS, pico −1,9 dBTP; atrito −17 LUFS contra falas de −11 a −13 LUFS; Whisper transcreve todas as falas (trecho a trecho).

## v1.5.0 (11 de outubro de 2026)

- 23 testes passaram, incluindo legendas "uma ideia por vez" ("O VERMELHO," / "O AZUL..." / "OU O AMARELO GIGANTE?"; "ACHEI NA RUA," / "TODO ESSE OVO" / "PRA UM PINTINHO?!"), envelope da boca em áudio sintético e as APIs R15/auditorias.
- Studio: as 17 animações dos pacotes (Cartoony, Levitation, emotes R15) carregaram no Play; alturas de pose medidas (idle 3,41; sentado com pernas esticadas 1,27; deitado 0,91).
- Piloto refeito em R15: `[auditoria] total 0` e `[camera] total 0`; boca abrindo nas 9 falas; quadros revisados a cada 0,4 s; 1080×1920, 60 fps, −14,0 LUFS, pico −1,9 dBTP.


## v1.4.0 — auditoria de animação e legendas karaokê (11 de outubro de 2026)

- 20 testes passaram (`python -m unittest discover -s tests`), incluindo agrupamento karaokê idêntico à referência ("MANO, OLHA O" / "TAMANHO DESSE OVO!"), fonte Fredoka One embutida e as APIs de auditoria do AnimKit.
- Piloto refeito: a auditoria encontrou 27 contatos do corpo com chão/rampas (causa principal: rig com a cabeça como PrimaryPart, deixando o corpo 1,5 stud enterrado); após as correções, `[auditoria] total 0 problema(s)` em todo o vídeo.
- Gravação final sem cursor do mouse e sem os botões do Roblox (faixa cortada); legendas comparadas lado a lado com o Short de referência.


## v1.3.0 — Shorts animados (11 de outubro de 2026)

- `python -m unittest discover -s tests`: 17 testes passaram (pipeline do Studio, AnimKit, legendas, alinhamento de voz, processamento da captura, render com voz e modo shorts).
- Piloto real "Qual escorregador é o mais rápido?": Roblox Studio 0.742 aberto pelo `-task RunScript`, cena de 33 s gravada só pela janela (1.894 quadros capturados, 0 descartados), vídeo final 1080×1920 a 60 fps, −14,0 LUFS, pico −1,9 dBTP.
- Voz Roger (ElevenLabs v4) gerada pelo site com o usuário logado; as 9 falas conferidas por transcrição Whisper; o áudio final transcrito confirma a voz audível por cima da música e dos efeitos.
- Quadros revisados a cada 0,6 s: pés sempre sobre o piso, closes com a cabeça inteira, pouso com poeira.


## v1.2.0 — edição exagerada (7 de outubro de 2026)

Executado localmente com FFmpeg 7.1 e Python 3.12.

- `python -m unittest discover -s tests`: 11 testes passaram, incluindo uma renderização real de vídeo sintético (longo + 2 Shorts) com `speed`, `freeze`, `reverse`, `punch`, `shake`, `flash`, `zoom`, legendas `grito`/`titulo` com cor e `sfx`, sticker com `sfx` e `pitch`.
- Verificação SHA-256 dos **193 áudios** do catálogo: passou. 155 liberados para vídeo final (72 músicas/trechos CC BY + 77 efeitos do CapCut declarados livres pelo proprietário + 6 originais); 38 continuam só para prévia.
- Os 77 efeitos do CapCut foram classificados com o modelo AudioSet AST (MIT/ast-finetuned-audioset-10-10-0.4593): nenhum com fala detectada (probabilidade de fala < 0,09 em todos); dois gritos marcados com aviso. A classificação é automática; escuta humana continua recomendada.
- Corrigido: `reverse` em gameplay sem áudio consumia memória sem limite (fonte de silêncio infinita + `areverse`) e podia travar o computador. Agora a fonte de silêncio é finita e o silêncio não é invertido; o teste de renderização cobre esse caso.
- Gameplay real (Roblox, 2560×1440, 60 fps, sem áudio): prévia 640×360 e exportação final 1440p60 de um longo de 3:33 e três Shorts, com 56 efeitos sonoros por minuto no longo e 63–106 nos Shorts. Quadros revisados a cada 0,5–1 s.

Não foi feita revisão auditiva integral nem teste de invocação dentro do Claude.

## v1.1.0 (6 de outubro de 2026)

- Decodificação completa e verificação SHA-256 dos 185 áudios: passou.
- Exportação de um longo 1920×1080 e dois Shorts 1080×1920, com legendas, zoom, PNG sobreposto, música, SFX e ducking: passou.
- Mixagem final próxima de −14 LUFS, com true peak abaixo de −1.5 dBTP: passou.
- Exportação de fonte 2560×1440 a 60 FPS em longo 2560×1440 e dois Shorts 1440×2560, preservando 60 FPS: passou.
- Tentativas de reduzir 1440p para 1080p ou mudar 60 para 30 FPS na exportação final: rejeitadas.
- Fonte sem áudio, muting, enquadramento por clipe, crédito da música usada e decodificação completa dos MP4: passou.
- Áudio sem licença comercial liberada em exportação final: rejeitado. Modo de prévia com marcação: passou.
- Histórico musical e preferência por composições não usadas recentemente: passou.
- Download real de música do autor, extração do trecho e nova execução aproveitando o cache: passou.
- Instalação do pacote completo com acesso à rede bloqueado: passou.
