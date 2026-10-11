# Timeline executável

O Claude faz a seleção criativa e escreve a timeline. O renderizador não analisa o humor nem cria automaticamente as histórias. Leia `scripts/renderizar.py --help`.

`source` de cada clipe é absoluto ou relativo ao JSON. `file` de música/SFX (inclusive o campo `sfx` de legendas, efeitos e stickers) é relativo à biblioteca; `file` de stickers é absoluto ou relativo ao JSON. Windows aceita caminhos com `/`; nunca monte uma linha de shell a partir de textos de legenda. Saída existente não é sobrescrita: escolha outra pasta de exportação.

Dica: com timelines grandes, escreva um pequeno gerador em Python que recebe eventos no **tempo da fonte** (o quadro do soco no original) e converte para o tempo final somando as durações dos clipes anteriores (`(out-in)/speed + freeze`). Assim cada som cai no quadro certo mesmo depois de reordenar cortes.

Estrutura ilustrativa: substitua tempos e caminhos pelos da gravação observada.

```json
{
  "library": "biblioteca-audio",
  "primary_source": "gameplay.mp4",
  "outputs": [
    {
      "name": "short-01.mp4", "format": "short",
      "clips": [
        {"source": "gameplay.mp4", "in": 32.0, "out": 36.5, "center": [0.45, 0.5]},
        {"source": "gameplay.mp4", "in": 36.5, "out": 37.2, "center": [0.45, 0.5], "freeze": 0.8},
        {"source": "gameplay.mp4", "in": 35.4, "out": 37.0, "center": [0.45, 0.5], "speed": 0.5, "zoom": [1.1, 1.3]}
      ],
      "music": [{"file": "musicas/curtos/hyperfun-short.mp3", "gain_db": -18}],
      "sfx": [
        {"file": "efeitos/capcut-convertidos/em mp3-3.mp3", "at": 1.2, "gain_db": -5, "pitch": 1.1},
        {"file": "efeitos/capcut-convertidos/eem mp3-46.mp3", "at": 4.0, "gain_db": -8, "pitch": 0.8},
        {"file": "efeitos/capcut-convertidos/em mp3-7.mp3", "at": 4.9, "gain_db": -3}
      ],
      "effects": [
        {"type": "punch", "at": 1.2, "intensity": 0.3, "center": [0.45, 0.5]},
        {"type": "shake", "at": 1.2, "duration": 0.3},
        {"type": "shake", "at": 4.9, "duration": 0.5, "intensity": 1.5},
        {"type": "flash", "at": 4.9, "color": "branco"},
        {"type": "zoom", "at": 5.2, "duration": 0.8, "intensity": 0.25, "sfx": "efeitos/capcut-convertidos/eem mp3-48.mp3"}
      ],
      "captions": [
        {"start": 0.0, "end": 1.8, "text": "ELE VAI APANHAR?!", "style": "grito", "sfx": "efeitos/capcut-convertidos/eem mp3-18.mp3"},
        {"start": 5.0, "end": 6.0, "text": "POUSO PERFEITO?", "style": "grito", "color": "vermelho"},
        {"start": 6.0, "end": 7.6, "text": "REPLAY", "style": "titulo", "sfx": "efeitos/capcut-convertidos/eem mp3-1.mp3"}
      ],
      "overlays": [
        {"file": "assets/overlays/pow.png", "at": 1.2, "duration": 0.6, "x": 0.55, "y": 0.2, "width": 0.3},
        {"file": "assets/overlays/estrelas-tontas.png", "at": 5.0, "duration": 1.0, "x": 0.3, "y": 0.35, "width": 0.4, "bob": false}
      ]
    }
  ]
}
```

## Semântica dos campos

### Clipes
- `in/out`: segundos no vídeo **original**, não no proxy nem no render.
- `speed`: 0.25–4 (padrão 1). 0.5 = câmera lenta; 2 = acelerado. A duração de saída é `(out-in)/speed`. Áudio da gameplay acompanha (atempo).
- `freeze`: 0–4 s. Congela o último quadro do clipe e soma esse tempo à saída (ótimo com legenda `grito` e som).
- `reverse`: `true` toca o trecho de trás para frente ("rebobinar"); no máximo 3 s de fonte.
- `center`: dois números de 0 a 1 que posicionam a janela de crop (0.5 centraliza). Não são coordenadas do personagem. Divida o clipe para seguir mudanças de posição.
- `zoom`: `[inicio,fim]` entre 1 e 2, linear durante o clipe, aplicado depois do crop.
- `framing`: `crop` preenche o formato cortando bordas; `fit` preserva o quadro com barras e não aceita zoom.
- `mute`: pares de segundos relativos ao clipe na fonte, para silenciar fala imprópria. `audio_gain_db` ajusta o áudio da gameplay no clipe.

### Efeitos de câmera (`effects`) — tempo final
- `punch`: zoom-soco instantâneo que volta suavemente. `intensity` 0.02–1 (padrão 0.28 = 28% de zoom), `duration` padrão 0.35 s, `center` [x,y] para onde o zoom mira.
- `zoom`: aproxima, segura e solta. `intensity` padrão 0.2, `duration` padrão 1.2 s, `center`.
- `shake`: tremida que diminui até parar. `intensity` 0.1–3 (padrão 1), `duration` padrão 0.45 s.
- `flash`: clarão de tela. `color` `branco`/`amarelo`/`vermelho`/`preto`, `intensity` 0.05–1 (opacidade, padrão 0.75), `duration` padrão 0.12 s.
- Todos aceitam `sfx` (+ `sfx_gain_db`, `sfx_pitch`), tocado em `at`.
- Efeitos sobrepostos se somam; legendas e stickers não tremem nem dão zoom.

### Áudio
- `music`: obrigatório em cada output. `at`, `duration` e `offset` em segundos (`offset` na gravação musical). A gravação repete se necessário. Para trocar de música, crie entradas com durações e sobreposição de ~0.3 s.
- `sfx`: `at` no tempo final; `gain_db` = pico desejado do efeito em dBFS antes da normalização (padrão −8; o renderizador compensa o volume de cada arquivo pelo `peak_db` do catálogo); `pitch` 0.5–2 muda tom e duração juntos (desenho animado); `duration` opcional corta a cauda. Todos os áudios precisam estar no catálogo com o hash registrado.

### Legendas (`captions`) — tempo final
- `start/end`, `text` (texto simples; `\n` quebra linha).
- `style`: `fala` (embaixo, branca, para fala real), `grito` (gigante no centro, amarela, entra pulando e inclinada, para reações), `titulo` (topo, para capítulo/promessa/REPLAY).
- `color`: `amarelo`, `vermelho`, `verde`, `azul`, `rosa`, `laranja`, `roxo`, `branco`.
- `sfx` opcional, tocado em `start`.
- Citações precisam coincidir com áudio real; rótulos de reação não representam transcrição.

### Stickers (`overlays`) — tempo final
- PNG transparente; `at/duration`; `x/y` de 0 a 1 = canto superior esquerdo como fração do quadro; `width` = fração da largura; `bob` (padrão true) faz o sticker balançar. `sfx` opcional.
- PNG originais em `assets/overlays` (veja a lista no SKILL.md). Garanta que o sticker caiba no quadro e não cubra o personagem.

### Output
- `resolution`: omita para calcular a partir da gravação principal. Valores diferentes da fonte só em prévias. `fps`: omita para preservar o FPS da fonte. `primary_source`: define a gameplay de referência. `crf`: 16 padrão.

O áudio é mixado com música reduzida por sidechain a partir do som da gameplay. A normalização final mira −14 LUFS e true peak −1.5 dBTP (com margem para o AAC). Os intermediários usam H.264 CRF0 e PCM em MKV; verifique espaço em disco em projetos 1440p/4K. Os logs ficam ao lado dos MP4. `relatorio-render.json` traz a densidade de efeitos de cada vídeo para conferir as metas de `edicao.md`.
