# Timeline executável

O Claude faz a seleção criativa e escreve a timeline. O renderizador não analisa o humor nem cria automaticamente as histórias. Leia `scripts/renderizar.py --help`.

`source` de cada clipe é absoluto ou relativo ao JSON. `file` de music/SFX é relativo à biblioteca; `file` de overlays é absoluto ou relativo ao JSON. Windows aceita caminhos com `/`; nunca monte uma linha de shell a partir de textos de legenda. Saída existente não é sobrescrita: escolha outra pasta de exportação.

Estrutura ilustrativa: substitua os tempos e caminhos com os da gravação observada. Não renderize este exemplo sem adaptar o conteúdo.

```json
{
  "library": "biblioteca-audio",
  "primary_source": "gameplay.mp4",
  "outputs": [
    {
      "name": "youtube-longo.mp4",
      "format": "long",
      "fps": 30,
      "clips": [
        {"source": "gameplay.mp4", "in": 40, "out": 46, "zoom": [1, 1.12], "center": [0.5, 0.5]},
        {"source": "gameplay.mp4", "in": 10, "out": 30, "framing": "fit", "audio_gain_db": 0, "mute": [[5.2, 5.6]]},
        {"source": "gameplay.mp4", "in": 46, "out": 70, "center": [0.5, 0.5]}
      ],
      "music": [{"file": "musicas/longos/jaunty-gumption.mp3", "at": 0, "gain_db": -23}],
      "sfx": [{"file": "efeitos/originais-livres/impacto-original.mp3", "at": 4.1, "duration": 0.6, "gain_db": -12}],
      "captions": [{"start": 0.2, "end": 2.0, "text": "QUASE!"}],
      "overlays": [{"file": "seta.png", "at": 3, "duration": 0.8, "x": 0.55, "y": 0.3, "width": 0.12, "bob": true}]
    },
    {
      "name": "short-01.mp4", "format": "short", "fps": 30,
      "clips": [{"source": "gameplay.mp4", "in": 32, "out": 46, "center": [0.6, 0.5], "zoom": [1, 1.1]}],
      "music": [{"file": "musicas/curtos/monkeys-spinning-monkeys-short.mp3", "gain_db": -23}],
      "captions": [{"start": 0.2, "end": 2, "text": "ESSA FOI POR POUCO!"}]
    },
    {
      "name": "short-02.mp4", "format": "short", "fps": 30,
      "clips": [{"source": "gameplay.mp4", "in": 54, "out": 70, "center": [0.4, 0.5]}],
      "music": [{"file": "musicas/curtos/carefree-short.mp3", "gain_db": -23}],
      "captions": [{"start": 0.2, "end": 2, "text": "AGORA VAI!"}]
    }
  ]
}
```

## Semântica dos campos

- `in/out`: segundos no vídeo **original**, não no proxy nem no render. Cada clipe mantém velocidade normal. A duração de saída é a soma de `out-in`.
- `center`: dois números de 0 a 1. Eles posicionam a janela entre a borda esquerda/superior (0) e direita/inferior (1); 0.5 centraliza. Não são coordenadas absolutas do personagem. Divida o clipe para seguir mudanças de posição e confira os quadros resultantes.
- `zoom`: `[inicio,fim]` entre 1 e 2, linear. No renderizador, aplica-se depois do crop inicial. Mantenha zooms moderados para evitar pixelização.
- `framing`: `crop` preenche o formato cortando bordas; `fit` preserva o quadro com barras escuras e não aceita zoom. Para fundo desfocado ou layout duplo, prepare um clipe composto com FFmpeg e o use como fonte.
- `mute`: pares de segundos relativos ao clipe, para silenciar fala imprópria. `audio_gain_db` ajusta o áudio da gameplay naquele clipe. Música dentro da gameplay deve ser analisada independentemente da licença da trilha adicionada.
- `music`: obrigatório em cada output. `at`, `duration` e `offset` são segundos; `at` é na timeline final, `offset` na gravação musical. Sem `at`, começa em zero; sem `duration`, dura até o fim do vídeo. A gravação é repetida se necessário: revise a emenda e use crossfade próprio se audível. Para mudança de música, crie entradas com durações e sobreposição/fades pertinentes.
- `sfx`: mesma convenção de tempos. Sem duration, o arquivo acaba naturalmente, mas prefira informar sua duração real para controlar a cauda. Todos os áudios precisam estar cadastrados e conservar o hash registrado.
- `captions`: `start/end` na timeline final; `text` é texto simples, sem comandos ASS. Anime os rótulos com entrada suave. Citações precisam coincidir com áudio real; rótulos de reação não representam transcrição.
- `overlays`: PNG transparente, `at/duration` na timeline final. `x/y` de 0 a 1 posicionam o canto superior esquerdo como fração do quadro; `width` é fração da largura. Garanta que o PNG caiba no quadro. `bob` liga movimento suave. Os PNG originais estão em `assets/overlays`.
- `resolution`: omita para calcular automaticamente a partir da gravação principal. Um bruto 2560×1440 gera longo 2560×1440 e Shorts 1440×2560. Valores explícitos diferentes da fonte são rejeitados nas exportações finais; só prévias marcadas podem usar resolução menor. `fps`: omita para preservar o FPS da fonte; alterações no FPS são rejeitadas no final. `primary_source`: opcional, define qual gameplay determina resolução/FPS; sem ele, vale a primeira fonte do longo. `crf`: 16 padrão; menores valores aumentam tamanho, não recuperam detalhe perdido.

O áudio é mixado com música reduzida por sidechain a partir do som da gameplay. Se a gameplay tiver ambiente constantemente alto, ajuste ganho e parâmetros para não manter a música permanentemente abafada. A normalização final usa duas passadas com alvo -14 LUFS/-1.5 dBTP; não torna gravações ruins limpas.

Uma renderização pode usar bastante disco: os clipes intermediários usam H.264 CRF0 e áudio PCM em MKV para evitar perdas entre etapas; a exportação final usa CRF16. Os temporários são removidos após cada output; a fonte permanece intacta. Verifique espaço antes de um projeto longo, especialmente 1440p/4K. Os logs são gravados ao lado dos MP4. O script permite uma biblioteca comercial verificada e gera créditos; ele não verifica a licença do vídeo original ou de overlays externos. O histórico `historico-musicas.json` registra títulos realmente exportados para que projetos futuros possam variar a trilha.
