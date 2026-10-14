# Agendar no YouTube Studio (Chrome do usuário)

Só depois que o usuário revisar e disser **"agende"** (é a autorização para publicar/agendar aquele lote; vale só para ele). Use o Chrome do usuário (ferramentas `mcp__claude-in-chrome__*`), já logado na conta Google dele. Nunca digite senha: se pedir login, pare e peça para ele entrar.

`python scripts/lote.py agenda LOTE` gera `agenda.json`: para cada canal (`pt` e `es`), 10 itens com `video`, `titulo`, `descricao`, `tags`, `data_studio` (dd/mm/aaaa), `hora_studio` (HH:MM, horário de Brasília). Mostre a tabela ao usuário antes de começar.

## Para cada canal
1. Abra `https://studio.youtube.com`. Confira o canal ativo (avatar no canto superior direito → nome do canal). Se não for o de `nomes_canais[idioma]`, troque em avatar → **Trocar de conta** / **Alternar conta**. Nomes dos canais em `config.local.json` (`canais.pt.nome`, `canais.es.nome`); se estiverem vazios, pergunte ao usuário qual canal é de cada idioma e grave lá.
2. Confira o fuso do canal (Configurações → Geral → fuso / país): os horários da agenda são de Brasília. Se o canal estiver em outro fuso, avise antes de agendar.

## Para cada vídeo (status `pendente` na agenda)
1. **Criar → Enviar vídeos**. Envie o MP4 com `file_upload` no `input[type=file]` da janela de envio (caminho absoluto de `video`).
2. **Detalhes**: título (apague o nome do arquivo que o Studio preenche e cole `titulo`), descrição (`descricao`).
3. **Público**: "Sim, é conteúdo para crianças" / "Sí, es contenido para niños".
4. **Mostrar mais**: tags (`tags`, separadas por vírgula), idioma do vídeo (`canais.<idioma>.idioma_video`), categoria (`config.categoria`).
5. **Avançar** até **Visibilidade**. Escolha **Programar** / **Agendar**, preencha a data (`data_studio`) e a hora (`hora_studio`; se a lista só aceitar intervalos de 15 min, 12:15 e 17:15 existem).
6. Confira na tela: título, "feito para crianças", data e hora. Só então clique **Programar**. Copie o link do vídeo da janela final.
7. `python scripts/lote.py marcar LOTE <pt|es> <NN> agendado --link <url>`. Erro → `marcar ... erro` e siga para o próximo; no fim, relate os que falharam.

## Cuidados
- Um envio por vez; espere o processamento terminar antes de fechar a janela (o agendamento só vale com o vídeo enviado).
- O Studio às vezes pede verificação de telefone para recursos avançados ou mostra "limite diário de envios": pare e avise o usuário (não tente contornar).
- Não aceite termos, não mude configurações do canal e não ative monetização sem o usuário pedir.
- No fim: `python scripts/lote.py status LOTE` e a lista dos 20 links para o usuário.

## Alternativa sem navegador (API do YouTube)
`scripts/youtube_api.py` envia e agenda pela YouTube Data API (`privacyStatus: private` + `publishAt`). Exige projeto no Google Cloud com OAuth criado pelo próprio usuário, e projetos não verificados têm os envios travados como privados até passarem na auditoria do Google. Use só se o usuário pedir.
