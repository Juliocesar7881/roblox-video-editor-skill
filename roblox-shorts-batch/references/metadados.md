# Título, descrição e tags com SEO (YouTube Shorts, canal BRUNOBLOX)

Escreva no `roteiro.json` de cada vídeo. O padrão vem dos Shorts que mais deram visualização no BRUNOBLOX
(confira de novo no Studio de vez em quando: Conteúdo → Shorts, ordene por visualizações):

- "QUAL TSUNAMI VAI ME PEGAR?! 🌊😂 #Shorts" (27 mil), "O BACON ROUBOU O OVO PROIBIDO! 🥚😱" (27 mil),
  "NÃO PISE NA COR ERRADA NO ROBLOX! 😱🌈" (26 mil), "QUAL ESCORREGADOR É O MAIS RÁPIDO?" (26 mil),
  "O CHÃO VIROU LAVA NO ROBLOX!" (15 mil), "APERTEI OS 5 BOTÕES DO ROBLOX… DEU RUIM! 😱" (10 mil).

| campo | onde | regra |
|---|---|---|
| título | `titulo_youtube` | CAIXA ALTA; a palavra-chave **ROBLOX** no título ("... NO ROBLOX?!", "... DO ROBLOX… DEU RUIM!"); pergunta ou exclamação curiosa ("QUAL...?!", "QUANTOS...?!", "... DEU RUIM!"); 2 emojis; termine com `#shorts #roblox`; até ~70 caracteres antes das hashtags (máx. 100 no total); sem clickbait falso (o vídeo tem que entregar o que o título promete) |
| descrição | `descricao` | 1ª linha = gancho com as opções/tentativas e emojis (é o que aparece no feed); 2ª = o que acontece sem contar o final, com "Roblox" e "Noob" escritos; 3ª = pergunta para comentar ("Comenta qual você escolheria! 👇"); 4ª = "Se inscreve no BRUNOBLOX pra ver um vídeo novo de Roblox todo dia! 🔔". Sem links. |
| hashtags | `hashtags` | `#Roblox #Shorts #Noob #RobloxBrasil` + 1 do tema (ex.: `#CasteloDeAreia`) |
| tags | `tags` | 15–20: amplas (`roblox`, `roblox shorts`, `roblox brasil`, `roblox português`, `noob`, `noob roblox`, `roblox engraçado`, `humor roblox`, `animação roblox`, `shorts`) + 6–8 do tema (o que a pessoa digitaria: "castelo de areia", "qual castelo aguenta a onda", "onda gigante"...) + `desafio roblox`. O script corta em ~480 caracteres |

`python scripts/lote.py metadados LOTE` monta `publicacao.json` e `publicacao.txt` com:
- título (+ `#shorts #roblox` se faltar);
- descrição + hashtags + créditos da música (lidos de `final-pt/…-creditos.txt`, gerados pelo renderizador; a licença
  CC BY exige o crédito) + "Voz: ElevenLabs (voz Roger)";
- tags validadas (sem `<` `>`, sem repetir, dentro do limite);
- público, categoria e idioma do `config.json`: **não é conteúdo para crianças** (como os outros Shorts do canal;
  decisão do dono em 15/10/2026), categoria **Jogos** (no Studio em inglês: Gaming), idioma **Português (Brasil)**.
O comando sai com erro (e lista o que falta) se faltar MP4, descrição, créditos, "ROBLOX" no título, se houver menos
de 12 tags ou se o título passar de 100 caracteres.

A thumbnail **não** é feita pela skill: o dono do canal coloca depois.

Uso comercial da voz do ElevenLabs exige plano pago na conta usada: deixe isso claro para o usuário, sem insistir.
