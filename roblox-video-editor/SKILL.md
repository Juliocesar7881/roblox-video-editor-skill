---
name: roblox-video-editor
description: "Edite gameplay de Roblox em um video YouTube 16:9 e pelo menos dois Shorts 9:16 no estilo infantil EXAGERADO: muitos efeitos sonoros (socos, impactos, boings, whooshes), zoom-soco, tremida, flash, camera lenta, congelamento, replay, stickers de quadrinho, legendas gigantes coloridas e musica licenciada."
---

# Editor de gameplay Roblox — estilo infantil exagerado

Transforme gravações brutas em entretenimento infantil em português brasileiro. Entregue **um vídeo horizontal 16:9 e pelo menos dois Shorts verticais 9:16**, mais outros Shorts quando existirem boas histórias independentes. Renderize arquivos reais; um roteiro ou uma lista de cortes não encerra o trabalho quando há ferramentas de execução. Esta skill é independente do modelo escolhido no Claude.

**O público é criança. A edição precisa ser exagerada, barulhenta e cheia de reação.** Edição discreta, com poucos efeitos, é considerada falha desta skill. Leia [references/edicao.md](references/edicao.md) antes de montar qualquer timeline: ele define as metas mínimas de densidade e as receitas por tipo de momento.

## Ambiente e biblioteca

O usuário precisa somente invocar esta skill e fornecer a gameplay acessível. Faça preparação, seleção, edição e exportação sem pedir que ele escreva timeline, selecione músicas ou escolha parâmetros técnicos. Leia [config.json](config.json); `config.local.json`, quando existir, sobrescreve somente os valores locais. Prioridade da biblioteca: caminho informado na tarefa, configuração local, configuração pública relativa à pasta da skill. Nunca dependa de um caminho privado de quem criou a skill.

Crie uma pasta nova de projeto em `entregas/<nome-da-gameplay>-<data-hora>` no workspace para análise, decisões de edição e exportações; preserve o bruto. Assuma português brasileiro e as preferências desta skill quando o usuário não fornecer outras.

A instalação inclui **193 áudios** em `assets/biblioteca-audio`. Para a edição, os importantes são os **83 efeitos sonoros liberados para vídeo final**: 77 efeitos do CapCut (`efeitos/capcut-convertidos`, declarados livres de direitos pelo proprietário do repositório) e 6 originais sintetizados. Eles estão catalogados por categoria: `soco`, `impacto`, `explosao`, `whoosh`, `boing`, `pop`, `pum`, `clique`, `ding`, `campainha`, `erro`, `aplausos`, `vinheta`, `grito`, `bicho-engracado`, `assobio`, `deslizar`, `grunhido`, `batida`, `sucesso`. Use `python scripts/selecionar_sfx.py --library BIBLIOTECA` para ver as categorias e `--categoria soco --timeline PROJETO/timeline.json` para receber sons ainda pouco usados na timeline. As 36 músicas de Kevin MacLeod (CC BY 4.0) e seus 36 trechos são as trilhas liberadas. Os 16 memes de `efeitos/fornecidos` e as 22 músicas pessoais continuam com licença não comprovada: só servem em prévia.

Execute `python scripts/preparar_ambiente.py` para verificar o cache. Requer Python 3.10+, FFmpeg com libx264/libass/libmp3lame e Pillow. Os scripts usam FFmpeg do PATH ou `imageio-ffmpeg` (`python -m pip install imageio-ffmpeg pillow`). Transcrição local opcional usa `faster-whisper`. Não depende de API paga. Execute `--help` nos scripts para conferir argumentos.

Em Claude web, caminhos `C:`/`D:` não são acessíveis: use os arquivos anexados/expostos à sessão. Nunca alegue que leu ou editou um arquivo que não consegue acessar. Se a gravação não estiver acessível, peça somente o vídeo ou seu caminho acessível.

## Escolher a história a partir do vídeo

1. Analise a **gravação inteira** com `scripts/analisar_gameplay.py VIDEO --out PROJETO/analise --proxy`; para gravações longas, aumente `--interval` na primeira passada. Depois examine candidatos com `--start/--end --interval 1` ou extraia quadros a 4 fps do proxy. Os tempos registrados são do original.
2. Marque **cada evento cômico ou de ação com o tempo exato do contato** (soco que acerta, queda que bate no chão, explosão, escorregão), porque cada um vai receber som, zoom e sticker naquele quadro. Assista aos candidatos em movimento e ouça o áudio. Transcreva se houver fala; nunca invente diálogos. Se a ferramenta não permitir assistir/escutar, declare a limitação.
3. Salve `momentos.json` com início/fim no original, tempos de impacto, evento observado, fala relevante, motivo e potencial para longo/Short. Procure: socos, quedas, tombos, escorregões, explosões, sustos leves, perseguições, poderes, vitórias, falhas e repetições engraçadas. Remova carregamentos, deslocamentos repetitivos e pausas sem piada. Texto em outra língua gravado no bruto (título, chamada final) deve ser cortado.
4. Construa o longo com gancho forte nos primeiros 3–5 s, objetivo simples, progressão e recompensa final. Nunca estique um bruto curto. Cada Short precisa de gancho em até 1 s, contexto, acontecimento e desfecho. Faça pelo menos dois com histórias diferentes (ex.: briga, piores quedas, ranking "qual é o melhor").

## Edição, direitos e renderização

Leia [references/timeline.md](references/timeline.md) e crie `timeline.json` com todos os outputs. O renderizador suporta:
- **Por clipe**: corte, enquadramento/`center`, zoom progressivo, `speed` (0.25–4: câmera lenta ou acelerado), `freeze` (congela o último quadro por N s), `reverse` (rebobinar, até 3 s), mute.
- **Efeitos de câmera na timeline** (`effects`): `punch` (zoom-soco no impacto), `zoom` (aproxima e segura na reação), `shake` (tremida) e `flash` (clarão colorido). Cada efeito pode trazer seu próprio `sfx`.
- **Legendas** com estilos `fala` (embaixo, branca), `grito` (gigante no centro, amarela, entra pulando e inclinada) e `titulo` (topo), cores `amarelo`, `vermelho`, `verde`, `azul`, `rosa`, `laranja`, `roxo`, `branco`, e `sfx` próprio.
- **Stickers** PNG originais em `assets/overlays/`: `pow`, `bam`, `boom`, `tum`, `wow` (UAU!), `oops` (OPS!), `kkkk`, `interrogacao` (?!), `estrelas-tontas`, `raio`, `suor`, `linhas-velocidade`, `explosao-cartoon`, `erro`, `check`, `seta`, `confete`. Cada um pode ter `sfx` próprio.
- **SFX** com `pitch` (0.5–2) para variar o mesmo som; o volume (`gain_db`) é o pico desejado do efeito, já compensado pelo pico de cada arquivo.

Use música de fundo em **todos** os vídeos, trocando a trilha a cada capítulo/jogo. Use `scripts/selecionar_musicas.py --library BIBLIOTECA --format long --mood CLIMA` para variar trilhas entre exportações; prefira músicas diferentes entre o longo e os Shorts. Leia [references/audio-licencas.md](references/audio-licencas.md) antes de escolher áudio.

Não cubra o personagem nem o objetivo com sticker ou legenda. Evite palavrão, sustos agressivos, humilhação de jogadores e alegações de Robux grátis. Grito (`categoria grito`) só curto e em volume moderado.

Renderize primeiro uma prévia rápida (copie a timeline com `resolution` pequena, `fps` 30 e use `--preview`), revise os quadros e só então a versão final:

```text
python scripts/renderizar.py PROJETO/timeline.json --out PROJETO/exportados --library CAMINHO/biblioteca-audio
```

`--preview` permite áudio não verificado e coloca marca de licença pendente; não entregue prévias como prontas para monetização.

## Entrega e verificação

Detecte dimensões e FPS da gravação antes de editar. **A resolução de entrega segue a fonte, sempre, nos dois formatos**: 1920×1080 → 1920×1080 e 1080×1920; 2560×1440 → 2560×1440 e 1440×2560; 3840×2160 → 3840×2160 e 2160×3840. Não reduza nem faça upscale de classe. O FPS final segue o real da gravação (inclusive 29.97/59.94). O renderizador calcula e rejeita divergências nas exportações finais. Em fontes fora de 16:9, preserve a maior dimensão e complete com padding/composição. Exporte H.264 MP4, yuv420p, AAC 48 kHz, faststart, CRF16.

O `relatorio-render.json` informa `sfx_por_minuto`, `sfx_distintos`, `efeitos_visuais`, `legendas` e `stickers` de cada vídeo. **Confira as metas de densidade de [references/edicao.md](references/edicao.md) nesse relatório; se ficar abaixo, adicione efeitos e renderize de novo.** Revise cortes, sincronização dos sons com os impactos, legibilidade, enquadramento vertical, níveis, loudness (~-14 LUFS) e true peak (< -1.5 dBTP) de cada arquivo. O relatório não substitui assistir e ouvir.

Entregue os MP4, `momentos.json`, `timeline.json`, relatório breve de revisão e um `.txt` por vídeo com título, descrição e créditos **das músicas realmente usadas** (CC BY exige crédito). Informe o que foi verificado e o que falta. Não prometa viralização, ausência absoluta de Content ID ou aprovação de monetização. Conteúdo direcionado a crianças deve ser sinalizado corretamente na publicação. Não publique automaticamente: esta skill prepara conteúdo local.
