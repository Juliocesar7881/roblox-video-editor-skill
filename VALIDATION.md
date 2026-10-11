# Validação antes da publicação

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
