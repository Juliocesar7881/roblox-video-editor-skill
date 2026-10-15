---
name: roblox-shorts-batch
description: "Lote semanal de Shorts animados de Roblox: 7 histórias inéditas, coloridas e engraçadas, em português (7 MP4), com título, descrição, hashtags e tags com SEO no padrão do canal, e agendamento no YouTube Studio do Chrome do usuário no canal BRUNOBLOX (@eibrunoruan): um vídeo por dia às 9:00 (Brasília) nos 7 dias seguintes. Anota cada roteiro no registro da skill para nunca repetir. Use para 'gerar lote', 'fazer os vídeos da semana', 'fazer 7 vídeos', 'agende os shorts'."
---

# Lote semanal de Shorts de Roblox

Produz **7 Shorts inéditos em português** com a skill `roblox-shorts-animator` (voz Roger), escreve título,
descrição e tags com SEO no padrão do BRUNOBLOX e agenda tudo no **canal BRUNOBLOX (@eibrunoruan)** pelo YouTube
Studio no Chrome do usuário: **um vídeo por dia às 09:00 (Brasília) nos próximos 7 dias** (rodou dia 15 → dias 16 a
22, sempre 09:00). Não há mais versão em espanhol nem canal ES. A thumbnail fica com o dono do canal. Configuração em
`config.json`.

Leia antes: o SKILL.md da `roblox-shorts-animator` (todas as regras de produção, auditorias, rosto, legendas, sons e
originalidade valem para cada vídeo), o registro de roteiros
[roblox-shorts-animator/historico/roteiros.md](../roblox-shorts-animator/historico/roteiros.md),
[references/ideias.md](references/ideias.md), [references/metadados.md](references/metadados.md) e
[references/youtube-studio.md](references/youtube-studio.md).

## Fluxo

1. **Lote novo**: `python scripts/lote.py novo` → `entregas/lote-AAAAMMDD/` com `01-a-definir` … `07-a-definir` (cada um com `studio/base.rbxlx` e `falas/`) e a base comum das cenas.
2. **7 ideias inéditas**: `python scripts/lote.py historico` mostra o registro de tudo o que já foi feito (inclusive o que o BRUNOBLOX publicou por fora da skill) e os roteiros em `entregas/`. Escreva as 7 seguindo [ideias.md](references/ideias.md): eixos diferentes, formatos alternados, muitas cores, reviravolta boba e leve. Nada idêntico nem parecido com o registro. Mostre a lista curta ao usuário e siga (ele pode trocar alguma). Renomeie as pastas para `NN-<tema>`.
3. **Roteiro de cada vídeo** (`roteiro.json`, como na `roblox-shorts-animator`, só português) com os campos do YouTube com SEO: `titulo_youtube`, `descricao`, `hashtags`, `tags` ([metadados.md](references/metadados.md)). `originalidade.json` em cada pasta.
4. **Vozes de uma vez**: no ElevenLabs (Roger de **Minhas Vozes**, grátis, modelo Eleven v4, idioma Automático), gere todas as falas do lote, cada uma começando com `[Brazilian Portuguese accent]` (sem isso às vezes sai sotaque espanhol; o cliente quer português do Brasil, nunca de Portugal) e use a versão `eleven_v4` de cada geração (a `eleven_v4_exp` fica de reserva). Capture pelo **Histórico** e mande para as pastas com `roblox-shorts-animator/scripts/receptor_falas.py` (o Chrome bloqueia vários downloads). Antes, confira os créditos restantes (~1 crédito por caractere; ≈ 2.000 para 7 vídeos de 8 falas). Se não der, diga quantos vídeos cabem e pergunte se faz parte agora. Depois `alinhar_falas.py` em cada `falas/`.
5. **Cena de cada vídeo**: `studio/cenario_corpo.lua`, `gerar_cena.py`, `montar_edicao.py` próprios (adapte a infraestrutura dos modelos, nunca a história). O `novo` copia para o lote a base comum de [modelos/lote-base](modelos/lote-base): `comum.py` (classe `Cena`: timeline pelas falas reais com `c.w(fala, 'palavra')`, eventos Luau, boca pela voz e ajudantes `mover/escalar/arco/soldar/mostrar/pintar/estouro/emissor/passo/pulo`), `cenario_comum.lua` (peças, bolas, cilindros em pé, elipses, modelos soldados, árvores, flores, nuvens, prédios, gramado; o `comum.py` junta com o `cenario_corpo.lua` de cada vídeo) e `edicao.py` (classe `Edicao`: efeitos por categoria — inclusive os originais `domino`, `onda`, `espuma`, `vento`, `apito_sobe`, `jato`, `regador` —, música, zoom/punch/tremida/flash, stickers, contagem 5-4-3-2-1 e legendas karaokê que nunca atravessam cortes). Auditoria de colisões e de câmera zerada; grave uma prévia e revise a folha de quadros de cada um (enquadramento dos insertos, objeto principal inteiro no quadro, nada cobrindo texto do cenário) **antes** de produzir. O que a auditoria não vê e já apareceu:
   - objeto não colidível entre a câmera e o rosto (espuma, maçã na mão, pernas do noob num inserto de chão): olhe a folha;
   - `K.inserto(false)` de um corte com `K.cortarPara` vai **dentro** da função da câmera, senão o quadro do corte acusa "rosto fora do quadro";
   - coisa larga no 9:16 (arco-íris, abóbora ao lado da casa) fica fina no meio do quadro: aproxime, ponha em profundidade e use câmera baixa;
   - porta/janela numa superfície curva (abóbora gigante) precisa ser calculada contra a casca, senão some dentro dela;
   - torre ou objeto balançando: câmera com `cam.seguir` e balanço para longe dos sólidos;
   - objeto preso na mão do noob **sentado**: não use solda na mão (a pose das pernas se desfaz e elas entram no chão); faça o objeto seguir as mãos a cada quadro;
   - travelling/zoom cortado antes de terminar (ex.: inserto curto da pizza com zoom de 1,2 s): use `c.ate_corte(t)` como duração e alongue o plano se ficar curto — o `escrever()` recusa a cena;
   - efeito sonoro cortado no meio (`dur` curto num som longo, ou som passando do fim do vídeo): toque o som inteiro ou troque por um curto — o `edicao.py` recusa;
   - objeto pendurado (isca, pesca) longe do rosto ou na frente da boca: confira na folha de quadros; linha de pesca passando perto da câmera vira uma faixa branca.
6. **Produção**: `python scripts/lote.py produzir LOTE` roda o `fazer_short.py` de cada projeto (auditoria, gravação, edição, legendas, render), um por vez, sem parar o lote se um falhar, e **anota cada vídeo pronto no registro de roteiros**; `--so 03 07` refaz só esses. Gravações no Studio são sequenciais (~4 min por vídeo): rode em segundo plano e acompanhe pelo `lote.json`.
7. **Revisão**: confira cada vídeo como na `roblox-shorts-animator` (folha de quadros, cortes, loudness ~−14 LUFS e pico < −1,5 dBTP, Whisper). Depois `python scripts/lote.py metadados LOTE` (tem que sair "metadados OK"), `python scripts/lote.py agenda LOTE` e `python scripts/lote.py painel LOTE` (`revisao.html`).
8. **Agendar no BRUNOBLOX**: siga [youtube-studio.md](references/youtube-studio.md) no Chrome do usuário — canal BRUNOBLOX (@eibrunoruan), cada vídeo com título, descrição, tags, "não é conteúdo para crianças", idioma Português (Brasil), categoria Jogos, data da `agenda.json` às 09:00. Envio pelo `servidor_envio.py` (os MP4 passam de 10 MB). A hora se escolhe **clicando na opção "09:00"** da lista (digitada, o Studio salva 00:00) e cada agendamento se confere na janela "Video scheduled" antes do próximo. Marque cada resultado com `lote.py marcar`. No fim, `lote.py status` e os links. Se a agenda foi gerada em outro dia, rode `lote.py agenda` de novo antes (sempre começa no dia seguinte).

## Regras
- Pedir para rodar o lote autoriza agendar **aquele** lote no BRUNOBLOX. Nada vai para outro canal (o BRUNOBLOX ESP foi abandonado). Nunca digite senhas; se o Studio pedir login ou verificação, pare e peça ao usuário.
- Nunca reutilize uma história do registro, de um modelo ou do mesmo lote (`historico` antes de escrever). Todo vídeo produzido entra no registro.
- Sem Robux grátis de verdade, links, sustos pesados, humilhação ou palavrões; sem personagens, marcas ou músicas de terceiros.
- Público no YouTube: "não é conteúdo para crianças", como os outros Shorts do canal (escolha do dono). Se ele mudar de ideia, troque `feito_para_criancas` no `config.json`.
- Uso comercial da voz do ElevenLabs exige plano pago na conta usada: avise uma vez, sem insistir.
- A API do YouTube (`scripts/youtube_api.py`) é só alternativa, se o usuário pedir.
