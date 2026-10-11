# Critérios de montagem — estilo infantil exagerado

## Metas mínimas de densidade

Edição para criança é exagerada. Estes números são o **mínimo**; confira-os no `relatorio-render.json` e renderize de novo se ficar abaixo.

| Medida | Shorts | Longo |
|---|---|---|
| Efeitos sonoros (`sfx_por_minuto`) | ≥ 30 (um a cada ~2 s) | ≥ 18 (um a cada ~3 s) |
| Efeitos de câmera (`punch`, `zoom`, `shake`, `flash`) | ≥ 1 a cada 3 s | ≥ 1 a cada 5 s |
| Stickers | ≥ 1 a cada 5 s | ≥ 1 a cada 8 s |
| Legendas `grito`/`titulo` | ≥ 1 a cada 5 s | ≥ 1 a cada 7 s |
| Sons distintos (`sfx_distintos`) | ≥ 10 | ≥ 25 |
| Maior plano sem nenhum evento | ≤ 3 s | ≤ 6 s |

Todo acontecimento visível ganha som: soco, queda, pulo, teia, poder, dinheiro, cura, inimigo aparecendo, troca de cena. Silêncio de efeitos por vários segundos parece vídeo "parado" para criança.

## Receitas por momento

Os tempos de impacto vêm de quadros a 4 fps ou mais; o som precisa bater no quadro do contato, não "perto".

- **Soco / acerto**: `soco` no contato (troque o arquivo a cada golpe e varie `pitch` entre 0.9 e 1.2) + `punch` 0.25–0.35 centrado no golpe + `shake` 0.3 s + sticker `pow`/`bam`/`tum` por 0.6 s ao lado do personagem. Opcional: `flash` branco de 0.08 s.
- **Combo / golpe final**: o último golpe é maior: `impacto` ou `explosao` + `shake` intensidade 1.5 + legenda `grito` "COMBO!" ou "K.O.!" com `pop`.
- **Queda / tombo / escorregão**: `whoosh` ou `assobio` com `pitch` 0.8 durante a queda → `impacto` no chão + `punch` + `shake` + sticker `estrelas-tontas` → clipe seguinte com `freeze` 0.6–1.0 s e legenda `grito` ("POUSO PERFEITO?", "KKKKK") + `boing` ou `pum` → **replay** dos últimos 1–2 s com `speed` 0.5, legenda `titulo` "REPLAY" e `whoosh`.
- **Explosão / poder / ataque especial**: `explosao` + `flash` amarelo ou branco + `shake` 1.5 + sticker `boom` ou `raio` + legenda `grito`.
- **Susto / surpresa / vilão aparece**: `zoom` segurando 1 s no ponto + sticker `interrogacao` + som de `vinheta` curta, `campainha` ou `grunhido` + legenda `grito` "?!" ou "O QUE É ISSO?!".
- **Falha / erro bobo**: `erro` + sticker `erro` ou `oops` + legenda `grito` vermelha "QUASE!"/"OPS!" + `reverse` de 1 s (rebobina) e repete a cena.
- **Vitória / recompensa / dinheiro**: `sucesso`, `ding` ou `aplausos` + `confete` ou `check` + legenda `grito` verde.
- **Correndo / voando rápido**: `speed` 1.5–2 + sticker `linhas-velocidade` + `whoosh`.
- **Constrangimento / tensão**: sticker `suor` + `clique` ou `pop` + `zoom` lento.
- **Troca de cena / capítulo**: `whoosh` + `flash` branco 0.1 s + legenda `titulo` ("JOGO 2") com `ding` ou `pop`.
- **Toda legenda `grito`** ganha um `pop` ou `clique` na entrada (campo `sfx` da própria legenda).

Varie: nunca use o mesmo arquivo de efeito duas vezes seguidas e use `scripts/selecionar_sfx.py --timeline` para escolher os menos usados. Sons de `vinheta` são jingles de 2–6 s: use como "trilha de piada" pontual, abaixando a música (`gain_db` da música −22 a −24) enquanto tocam.

## Mixagem

Música de fundo em `gain_db` −17 a −20 (com a fonte sem fala) ou −22 a −24 (com fala). Efeitos: `gain_db` é o pico desejado do som (o renderizador compensa o volume de cada arquivo): socos −6 a −4, explosões e impactos −4 a −2, whoosh/pop/clique −10 a −8, grito −12. A normalização final mira −14 LUFS e true peak abaixo de −1.5 dBTP.

## Seleção e narrativa

Analise começo, meio e fim; não escolha apenas os primeiros minutos. Prefira eventos com surpresa, reação, risco compreensível ou recompensa. Uma falha precisa de uma tentativa visível; uma vitória precisa de um objetivo estabelecido. Mantenha o mínimo de contexto para a criança entender.

No longo, comece com 3–5 s do momento mais forte (gancho) e uma legenda `titulo` com a promessa do vídeo. Um bruto de 3 minutos pode produzir 1–3 minutos; um de 10–30 minutos, 4–12; um de uma hora, 8–20. São referências, não metas de preenchimento. Termine com chamada de comentário ("QUAL FOI O MELHOR? COMENTA!").

Nos Shorts, o gancho entra no primeiro segundo: comece no meio da ação, com legenda `grito` e som. Prefira 20–45 s. O segundo Short precisa de gancho e desfecho diferentes do primeiro; não recicle a mesma montagem.

`momentos.json` pode ser uma lista de registros com `source`, `in`, `out`, `impactos` (lista de tempos no original), `evento`, `fala`, `contexto`, `motivo`, `uso`, `revisao_visual`, `revisao_audio`. Documente fatos observados.

## Ritmo e animação

Cortes a cada 2–4 s nos Shorts e 3–6 s no longo, removendo o intervalo antes/depois da ação, mas preservando a preparação da piada. Varie plano normal, `zoom` de clipe 1.08–1.3, `punch` nos impactos e close pontual. Replay de 0.5–2 s deixa claro que é repetição (legenda "REPLAY"). Câmera lenta precisa preservar fala inteligível ou usar só efeitos/música.

Stickers entram ao lado do personagem, nunca em cima dele, e somem em 0.5–1.2 s. Em Shorts 1080×1920, preserve margem superior de ~150 px, inferior de 350–430 px e lateral direita de 160 px para a interface do YouTube; para stickers use `x` entre 0.05 e 0.6 e `width` 0.25–0.35.

## Adequação infantil

Sem voz, conte a história com acontecimentos visuais e legendas de reação. Evite palavrões, duplo sentido, humilhação de jogadores, sustos sonoros agressivos, pedidos de dados pessoais e alegações de Robux grátis. Corte ou silencie palavrões do original. Exagero é de comédia (som, zoom, sticker), não de volume: nenhum efeito deve estourar acima do resto da mixagem.

## Revisão

Assista a cada exportação ou inspecione quadros a cada 0,5–1 s se houver limite de ferramentas, conferindo se cada impacto tem som, zoom/tremida e sticker no quadro certo. Ouça fala/música/SFX juntos. Confira as metas de densidade no `relatorio-render.json`. Se não conseguir revisar, registre a revisão como pendente.
