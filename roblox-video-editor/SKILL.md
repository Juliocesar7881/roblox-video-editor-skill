---
name: roblox-video-editor
description: "Edite gameplay de Roblox em um video YouTube 16:9 e pelo menos dois Shorts 9:16, com humor infantil, cortes, zooms, VFX, legendas animadas, efeitos sonoros e musica licenciada."
---

# Editor de gameplay Roblox

Transforme gravações brutas em entretenimento infantil em português brasileiro. Entregue **um vídeo horizontal 16:9 e pelo menos dois Shorts verticais 9:16**, mais outros Shorts quando existirem boas histórias independentes. Renderize arquivos reais; um roteiro ou uma lista de cortes não encerra o trabalho quando há ferramentas de execução. Esta skill é independente do modelo escolhido no Claude.

## Ambiente e biblioteca

O usuário precisa somente invocar esta skill e fornecer a gameplay acessível. Faça preparação, seleção, edição e exportação sem pedir que ele escreva timeline, selecione músicas ou escolha parâmetros técnicos. Leia [config.json](config.json); `config.local.json`, quando existir, sobrescreve somente os valores locais. Prioridade da biblioteca: caminho informado na tarefa, configuração local, configuração pública relativa à pasta da skill. Nunca dependa de um caminho privado de quem criou a skill.

Crie uma pasta nova de projeto em `entregas/<nome-da-gameplay>-<data-hora>` no workspace para análise, decisões de edição e exportações; preserve o bruto. Escolha nomes claros para o longo e os Shorts. Assuma português brasileiro e as preferências desta skill quando o usuário não fornecer outras.

A instalação completa já inclui **185 áudios** em `assets/biblioteca-audio`: 85 efeitos fornecidos/convertidos, seis efeitos originais, 36 músicas licenciadas completas e 36 trechos, mais 11 músicas fornecidas e 11 trechos. Use essa biblioteca diretamente; não peça downloads separados. Execute `python scripts/preparar_ambiente.py` para aproveitar/verificar o cache existente. Se os 78 áudios de origem verificada estiverem ausentes, ele pode baixá-los/prepará-los novamente com o manifesto `assets/audio-manifest.json`. Arquivos fornecidos ausentes devem ser recuperados do pacote completo; o script não inventa links para eles. Os 107 arquivos fornecidos/derivados continuam com licença comercial pendente no catálogo.

Em Claude web, caminhos `C:`/`D:` não são acessíveis: use os arquivos anexados/expostos à sessão. Nunca alegue que leu ou editou um arquivo que não consegue acessar. Se a gravação não estiver acessível, peça somente o vídeo ou seu caminho acessível e deixe o fluxo preparado.

Requer Python 3.10+, FFmpeg com libx264/libass/libmp3lame e Pillow. Os scripts usam FFmpeg do PATH ou `imageio-ffmpeg`. Para preparação, `python -m pip install imageio-ffmpeg pillow`; transcrição local opcional usa `faster-whisper` e pode baixar um modelo. Não depende de API paga nem de serviço de transcrição. Execute `--help` nos scripts para conferir argumentos.

## Escolher a história a partir do vídeo

1. Leia [references/edicao.md](references/edicao.md). Analise a **gravação inteira**, seja ela de três minutos, uma hora ou outra duração. Use `scripts/analisar_gameplay.py VIDEO --out PROJETO/analise --proxy`; para gravações longas, aumente `--interval` na primeira passada. O script cria quadros com timestamps, proxy opcional, áudio e pistas de silêncio. Use `--start/--end --interval 1` para examinar candidatos em detalhe. Os tempos registrados são do original.
2. Assista aos candidatos em movimento e ouça o áudio, incluindo o contexto anterior e posterior. Transcreva se houver fala; corrija nomes do jogo e nunca invente diálogos. Miniaturas, silêncio, detecção de movimento e volume não provam que um trecho é divertido. Se a ferramenta não permitir assistir/escutar, declare a limitação; não apresente seleção semântica como verificada.
3. Salve `momentos.json` com início/fim no original, evento observado, fala relevante, motivo de escolha, necessidade de contexto e potencial para longo/Short. Encontre objetivos, tentativas, erros engraçados, perseguições, sustos leves, descobertas, reviravoltas e vitórias. Remova carregamentos, deslocamentos repetitivos, tentativas idênticas e pausas que não servem à piada.
4. Construa o longo com gancho, objetivo simples, progressão e recompensa final. O tempo final depende do material: nunca estique um bruto curto para bater oito minutos. Cada Short precisa de gancho, contexto, acontecimento e desfecho próprios. Faça pelo menos dois, mesmo que usem perspectivas e montagens diferentes de um mesmo acontecimento; evite duplicatas quase idênticas. Se a gravação for vazia/corrompida e tornar isso impossível, explique o impedimento concreto e solicite outra gravação.

## Edição, direitos e renderização

Use música de fundo em **todos** os vídeos, ajustando energia à cena e abaixando durante falas. Leia [references/audio-licencas.md](references/audio-licencas.md) antes de selecionar áudio. Consulte `catalogo.json` da biblioteca para duração, clima, licença, origem e créditos. Use `scripts/selecionar_musicas.py --library BIBLIOTECA --format long --mood CLIMA` para considerar o histórico de exportações e variar trilhas; a versão curta de uma música conta como a mesma composição. Prefira músicas diferentes entre o longo e os Shorts e troque trilhas em mudanças de capítulo. Repetição só quando servir a uma piada, continuidade ou identidade do canal, nunca como escolha automática de todo vídeo.

Os efeitos fornecidos e convertidos e as músicas pessoais são preferências do usuário; porém a procedência comercial desses arquivos não foi comprovada. Em prévias podem ser usados após escuta e revisão infantil. Na versão destinada à monetização, use os seis efeitos originais ou áudios cuja licença tenha sido comprovada e registrada. Não confunda uma cópia MP3 com permissão de uso.

Aplique cortes orientados ao acontecimento, punch-ins e zooms suaves, freeze/replay pontual quando melhorar uma piada, legendas de falas realmente presentes, setas, selos e confetes em momentos relevantes. Os cinco PNG em `assets/overlays/` são desenhos geométricos originais. Não cubra personagem, placar ou objetivo. Sons de memes com palavrão, material sexual, gritos excessivos ou sustos agressivos não combinam com o público infantil. O arquivo `im-fast-as-f-boi.mp3` requer atenção específica; prefira substituí-lo.

Leia [references/timeline.md](references/timeline.md) e crie `timeline.json` com todos os outputs. Renderize com:

```text
python scripts/renderizar.py PROJETO/timeline.json --out PROJETO/exportados --library CAMINHO/biblioteca-audio
```

Use `--preview` somente para prévias: ele permite efeitos não verificados e coloca marca de licença pendente. Não entregue essas prévias como prontas para monetização. O renderizador cobre cortes, enquadramento por clipe, zoom progressivo, mute de palavrões, legendas ASS animadas, PNG com fade/movimento, trilha, ducking, SFX e normalização em duas passadas. Tracking que muda durante um clipe exige subdividir a cena e atualizar `center`; não há rastreamento automático. Slow motion, replay/freeze avançado, composição com fundo desfocado, transições complexas e VFX adicionais exigem comandos FFmpeg ou outra ferramenta de edição além deste renderizador; implemente-os quando servirem à cena e verifique a sincronização.

## Entrega e verificação

Detecte as dimensões e o FPS da gravação principal com `probe` antes de editar. **A resolução de entrega segue a fonte, sempre, nos dois formatos.** Para gameplay 16:9, o longo conserva largura e altura exatas; o Short usa as mesmas dimensões invertidas: 1920×1080 → 1920×1080 e 1080×1920; 2560×1440 → 2560×1440 e 1440×2560; 3840×2160 → 3840×2160 e 2160×3840. Não reduza 1440p/4K a 1080p nem faça upscale da tela de entrega para uma classe maior. Não use a palavra “2K” para adivinhar dimensões: leia os números do arquivo. O renderizador calcula automaticamente e rejeita dimensões/FPS diferentes em exportações finais. Uma prévia pode ser menor, identificada como prévia.

Em fontes fora de 16:9, preserve a maior dimensão e complete o canvas na proporção de entrega; prefira padding/composição para preservar conteúdo. FPS final segue o FPS real da gravação, incluindo 29.97/59.94; não converter 30 para 60. O campo `primary_source` pode identificar a gameplay principal se houver clipes auxiliares. Exporte H.264 MP4, yuv420p, AAC estéreo 48 kHz, faststart, intermediários sem perdas adicionais e compressão final de alta qualidade (CRF16 padrão). Reenquadramento, zoom, troca de proporção e exportação com compressão não garantem pixels idênticos ao bruto: a regra preserva o nível de resolução e o FPS, não inventa detalhe. Em Shorts, reenquadre avatar e ação ou use composição alternativa quando crop remover informação essencial.

O script verifica duração, decodificação e licenças dos áudios cadastrados, mas isso **não substitui assistir e ouvir** o resultado. Revise cortes, falas, cronologia, legibilidade, enquadramento vertical, níveis, trechos musicais repetidos e início/fim de cada arquivo. Verifique dimensões e FPS; avalie loudness e true peak do arquivo final. Corrija problemas antes de encerrar.

Entregue os MP4, `momentos.json`, `timeline.json`, relatório breve de revisão e um `.txt` por vídeo com título, descrição e créditos **apenas das músicas realmente usadas**. Informe o que foi verificado e qualquer licença ou revisão pendente. Não prometa viralização, ausência absoluta de Content ID ou aprovação de monetização. Conteúdo direcionado a crianças deve ser sinalizado corretamente na publicação; não mude o público para tentar aumentar receita. Não publique automaticamente: esta skill prepara conteúdo local.
