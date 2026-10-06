# Roblox Video Editor — skill para Claude

Envie uma gameplay bruta e peça `/roblox-video-editor`: o Claude analisa a gravação, monta um vídeo YouTube 16:9 e pelo menos dois Shorts 9:16, com humor infantil, cortes, zooms, legendas animadas, efeitos visuais, SFX e música de fundo. A seleção e o timing são feitos pelo Claude; os scripts preparam a biblioteca e renderizam as decisões de edição.

## Instalar uma vez

Com Python 3.10+ instalado, baixe ou clone este repositório e execute:

```sh
python install.py
```

Isso instala a skill em `~/.claude/skills/roblox-video-editor` e suas dependências. Para instalar só em um projeto:

```sh
python install.py --project CAMINHO_DO_PROJETO
```

Depois abra Claude Code com acesso à pasta da gameplay e envie:

```text
/roblox-video-editor Edite esta gameplay: CAMINHO_DO_VIDEO.
Entregue o longo e pelo menos dois Shorts, com humor infantil e música variada.
```

Você não precisa escrever uma timeline nem selecionar trilhas. Na primeira utilização, a skill prepara automaticamente a biblioteca licenciada; nas seguintes reutiliza os arquivos. Esse preparo baixa aproximadamente 250 MB e precisa de acesso à internet. Para uso sem rede, baixe a biblioteca pública nas [Releases](https://github.com/Juliocesar7881/roblox-video-editor-skill/releases), extraia e informe seu caminho.

Em Claude web, importe o ZIP da skill nas configurações de Skills e habilite execução de código. O arquivo da gameplay precisa estar anexado ou acessível ao ambiente; importar uma skill não dá acesso aos discos do seu computador. A duração/tamanho aceitos e a possibilidade de download/renderização dependem do ambiente e do plano. Para gameplay longa e 1440p/4K, prefira Claude Code local. Esta skill é independente da versão do modelo.

## Resolução segue a gravação

| Gameplay 16:9 | Vídeo longo | Shorts 9:16 |
|---|---|---|
| 1280×720 | 1280×720 | 720×1280 |
| 1920×1080 | 1920×1080 | 1080×1920 |
| 2560×1440 | 2560×1440 | 1440×2560 |
| 3840×2160 | 3840×2160 | 2160×3840 |

O FPS também segue a fonte. As exportações finais rejeitam mudanças de resolução/FPS; prévias identificadas podem ser menores. Em gravações fora de 16:9, conserva-se a maior dimensão e completa-se a proporção com composição/padding. Crop, zoom e troca de proporção requerem reenquadramento: preservar o nível de resolução não significa que os pixels permaneçam idênticos ao original. O pipeline usa intermediários H.264 CRF0/PCM e uma exportação MP4 H.264 CRF16/AAC de alta qualidade.

## Biblioteca e variação musical

- **36 músicas completas**, cobrindo comédia, aventura, arcade, exploração, fundo calmo e mistério leve.
- **36 trechos para Shorts**, derivados das mesmas músicas com fades.
- **6 efeitos sintetizados originais**: ding, sucesso, erro, whoosh, impacto e boing.
- **5 sobreposições originais**: seta, check, erro, explosão cartoon e confete.

O histórico de exportações registra músicas usadas. O seletor considera o clima, evita as últimas oito exportações quando há alternativas e prefere faixas menos usadas. As versões longa e curta contam como a mesma composição. Não há promessa de viralização ou de tendência atual.

As músicas são de Kevin MacLeod, obtidas do [site do autor](https://incompetech.com/music/royalty-free/licenses/) sob [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): uso comercial e redistribuição são permitidos com atribuição, link da licença e indicação de alterações. Cada exportação produz os créditos das faixas realmente utilizadas; coloque-os na descrição do YouTube.

O pacote pessoal de memes/músicas do criador não é redistribuído neste repositório. Para usar seu próprio pacote, configure uma biblioteca local com catálogo e comprovantes de licença. O renderizador permite arquivos não verificados somente em prévias identificadas. Licença musical não garante aprovação da monetização nem ausência de reivindicações equivocadas de Content ID.

## Execução e verificação

Requer Python, Pillow e FFmpeg com libx264/libass/libmp3lame. O instalador usa `imageio-ffmpeg` quando FFmpeg não está no PATH. Transcrição local com `faster-whisper` é opcional; não há dependência obrigatória de API paga.

O código verifica arquivos de áudio por hash, direitos cadastrados, dimensões, FPS, duração e decodificação completa das exportações. A skill orienta revisão visual e auditiva antes da entrega. Os testes de ferramenta usam vídeos sintéticos; isso não equivale a uma avaliação editorial de gameplay real.

```sh
python -m unittest discover -s tests
```

Código e instruções: [MIT](LICENSE). Música: CC BY 4.0, conforme [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Os efeitos e sobreposições originais podem ser usados comercialmente sem atribuição obrigatória.
