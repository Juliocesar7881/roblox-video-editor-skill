---
name: roblox-shorts-batch
description: "Lote semanal de Shorts animados de Roblox: 10 histórias inéditas, coloridas e infantis, cada uma em português e espanhol (20 MP4), com título, descrição, hashtags e tags prontos para o YouTube Shorts, painel de revisão e, quando o usuário disser 'agende', agendamento no YouTube Studio do Chrome dele: canal PT e canal ES, 2 por dia (12:15 e 17:15, Brasília) nos próximos 5 dias. Use para 'gerar lote', 'fazer 10 vídeos', 'vídeos da semana', 'agende os shorts'."
---

# Lote semanal de Shorts de Roblox

Produz **10 Shorts inéditos** com a skill `roblox-shorts-animator` (cada um em português e espanhol, mesma voz Roger), prepara os metadados do YouTube e, **só depois que o usuário revisar e disser "agende"**, agenda tudo no YouTube Studio pelo Chrome dele: **canal em português** e **canal em espanhol**, cada um com 2 vídeos por dia (**12:15 e 17:15**, horário de Brasília) nos **próximos 5 dias**. Configuração em `config.json` (nomes dos canais em `config.local.json`, que não vai para o GitHub).

Leia antes: o SKILL.md da `roblox-shorts-animator` (todas as regras de produção, auditorias, rosto, legendas, sons e originalidade valem para cada vídeo do lote), [references/ideias.md](references/ideias.md), [references/metadados.md](references/metadados.md) e [references/youtube-studio.md](references/youtube-studio.md).

## Fluxo

1. **Lote novo**: `python scripts/lote.py novo` → `entregas/lote-AAAAMMDD/` com `01-a-definir` … `10-a-definir` (cada um já com `studio/base.rbxlx`, `falas/`, `falas-es/`).
2. **10 ideias inéditas**: `python scripts/lote.py historico` lista as premissas de todos os Shorts já feitos. Escreva as 10 seguindo [ideias.md](references/ideias.md): eixos diferentes (clima, comida, esporte, escola, animais, objetos mágicos, transporte, festa, tamanho, profissões), formatos alternados, muitas cores, reviravolta boba e leve. Mostre a lista das 10 premissas ao usuário em uma tabela curta e siga (ele pode trocar alguma). Renomeie as pastas para `NN-<tema>`.
3. **Roteiro de cada vídeo** (`roteiro.json`, bilíngue, como na `roblox-shorts-animator`) com os campos do YouTube: `titulo_youtube`/`titulo_youtube_es` (opcional, senão `titulo`), `descricao`/`descricao_es`, `hashtags`/`hashtags_es`, `tags`/`tags_es` ([metadados.md](references/metadados.md)). `originalidade.json` em cada pasta.
4. **Vozes de uma vez**: no ElevenLabs (Roger de **Minhas Vozes**, grátis), gere todas as falas em português do lote, troque **Idioma → Espanhol** e gere todas em espanhol. Capture pelo **Histórico** e mande para as pastas com `roblox-shorts-animator/scripts/receptor_falas.py` (o Chrome bloqueia vários downloads). Antes, confira os créditos restantes: um lote usa ~1 crédito por caractere de fala, nos dois idiomas (≈ 6.000 para 10 vídeos de 8 falas). Se não der, diga quantos vídeos cabem e pergunte se faz parte agora. Depois `alinhar_falas.py` em cada `falas/` e `falas-es/`.
5. **Cena de cada vídeo**: `studio/cenario.lua`, `gerar_cena.py`, `montar_edicao.py` próprios (adapte a infraestrutura dos modelos, nunca a história). Auditoria de colisões e de câmera zerada em PT e ES; revise a folha de quadros de cada um (enquadramento dos insertos, objeto principal inteiro no quadro, nada cobrindo texto do cenário) **antes** de gravar.
6. **Produção**: `python scripts/lote.py produzir LOTE` roda o `fazer_bilingue.py` de cada projeto (auditoria, gravação, edição, legendas, render dos dois idiomas), um por vez, sem parar o lote se um falhar; `--so 03 07` refaz só esses. Gravações no Studio são sequenciais e levam ~3 min por idioma; um lote inteiro leva horas: rode em segundo plano e acompanhe pelo `lote.json`.
7. **Revisão**: confira cada vídeo como na `roblox-shorts-animator` (folha de quadros, cortes, loudness, Whisper). Depois `python scripts/lote.py metadados LOTE` (tem que sair "metadados OK") e `python scripts/lote.py agenda LOTE` (calcula os horários) e `python scripts/lote.py painel LOTE` → `revisao.html` com os 20 vídeos, títulos, descrições, tags e horários. Entregue o painel ao usuário e **pare**: diga que vai agendar quando ele responder "agende".
8. **"agende"**: siga [youtube-studio.md](references/youtube-studio.md) no Chrome do usuário: canal PT com os 10 vídeos em português, canal ES com os 10 em espanhol, cada um com título, descrição, tags, "feito para crianças", data e hora da `agenda.json`. Marque cada resultado com `lote.py marcar`. No fim, `lote.py status` e os links. Se a agenda foi gerada em outro dia, rode `lote.py agenda` de novo antes (os horários sempre começam no dia seguinte).

## Regras
- O "agende" do usuário autoriza **aquele lote**. Sem ele, nada é enviado ao YouTube. Nunca digite senhas; se o Studio pedir login ou verificação, pare e peça ao usuário.
- Nunca reutilize uma história de lote anterior, de modelo ou do mesmo lote (`historico` antes de escrever).
- Conteúdo infantil: marque "feito para crianças"; nada de Robux grátis, links, sustos, humilhação; sem personagens/marcas/músicas de terceiros.
- Uso comercial da voz do ElevenLabs exige plano pago na conta usada: avise uma vez, sem insistir.
- A API do YouTube (`scripts/youtube_api.py`) é só alternativa, se o usuário pedir (exige projeto Google Cloud dele e auditoria do Google para os vídeos não ficarem privados).
