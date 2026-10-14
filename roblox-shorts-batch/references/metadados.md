# Título, descrição e tags (YouTube Shorts)

Escreva no `roteiro.json` de cada vídeo, nos dois idiomas:

| campo | português | espanhol | regra |
|---|---|---|---|
| título | `titulo_youtube` (ou `titulo`) | `titulo_youtube_es` (ou `titulo_es`) | até ~60 caracteres antes do `#shorts` (o script acrescenta), com 1–2 emojis; pergunta ou exclamação curiosa; sem clickbait falso |
| descrição | `descricao` | `descricao_es` | 2–3 frases: o que acontece (sem contar o final) + pergunta para comentar |
| hashtags | `hashtags` | `hashtags_es` | 3–5, a primeira `#shorts`; ex.: `#roblox #robloxbrasil #noob` / `#roblox #robloxespañol #noob` |
| tags | `tags` | `tags_es` | 10–15 tags: tema do vídeo, `roblox`, `noob`, `shorts`, `desenho animado`, `infantil`, nome dos objetos; o script corta em ~480 caracteres |

O espanhol é latino neutro (`farmear`, `paraguas`, `impermeable`), não tradução palavra por palavra: título e descrição precisam soar naturais para uma criança do México ou da Argentina.

`python scripts/lote.py metadados LOTE` monta `publicacao-pt.json` / `publicacao-es.json` (e os `.txt`) com:
- título + `#shorts`;
- descrição + hashtags + créditos da música (lidos de `final-*/…-creditos.txt`, gerados pelo renderizador) + "Voz: ElevenLabs (voz Roger)";
- tags validadas (sem `<` `>`, sem repetir, dentro do limite);
- `feito_para_criancas: true` e a categoria do `config.json`.
O comando sai com erro (e lista o que falta) se faltar MP4, descrição, créditos ou tags, ou se o título passar de 100 caracteres.

Uso comercial da voz do ElevenLabs exige plano pago na conta usada: deixe isso claro para o usuário, sem insistir.
