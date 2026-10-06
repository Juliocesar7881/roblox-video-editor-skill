# Biblioteca e uso comercial

Verificação inicial: 6 de outubro de 2026. O arquivo `biblioteca-audio/catalogo.json` registra SHA-256, duração, fonte e licença. O CSV permite consultar a biblioteca em uma planilha. As cópias e conversões preservam os arquivos de origem.

| Pasta | Conteúdo | Situação comercial |
|---|---|---|
| `efeitos/fornecidos` | 16 MP3 indicados pelo usuário | Licença não comprovada |
| `efeitos/capcut-convertidos` | 69 áudios extraídos dos vídeos | Licença não comprovada |
| `efeitos/originais-livres` | ding, sucesso, erro, whoosh, impacto, boing sintetizados neste projeto | Sem samples de terceiros; uso comercial permitido |
| `musicas/longos` | 36 gravações completas de Kevin MacLeod | CC BY 4.0 com crédito |
| `musicas/curtos` | 36 trechos de aproximadamente 30–48 s dessas gravações | Mesma licença; indicar edição |
| `musicas/longos/fornecidas` | 11 músicas pessoais copiadas sem alterações | Licença não comprovada |
| `musicas/curtos/fornecidas` | 11 trechos das músicas pessoais | Licença não comprovada |

As versões curtas são recortes com fade, não composições diferentes nem loops perfeitos. Ouça o ponto de repetição e use crossfade ou outra parte se necessário. Nos longos, alterne músicas conforme a cena; uma faixa cômica curta não precisa tocar repetida por vinte minutos.

O repositório/pacote completo inclui **todos os 185 áudios**, por solicitação expressa do usuário. A instalação copia a biblioteca inteira para a skill e funciona sem download adicional de música. O manifesto de recuperação mantém somente os 78 arquivos de origem verificada; o catálogo da biblioteca contém todos. A publicação dos 85 efeitos e das 11 músicas pessoais com 11 trechos não muda suas licenças: os 107 arquivos continuam marcados como não verificados, sem inferir permissão comercial ou de redistribuição. Nomes como Wii Party, New Donk City e Homage não constituem licença.

## Evitar repetição

O renderizador registra títulos usados em `historico-musicas.json` após uma exportação final bem-sucedida. O seletor prioriza adequação ao clima, músicas ausentes das últimas oito exportações e menor contagem total de usos. Longa e curta contam como a mesma música. Leia as sugestões e escolha após ouvir; não trate o ranking como decisão editorial pronta. Evite a mesma faixa no longo e nos dois Shorts de uma entrega quando houver alternativas adequadas. Use duas ou mais faixas em vídeos longos com capítulos distintos, sem trocar de música no meio de uma frase. Se não houver alternativas adequadas, uma repetição é melhor do que uma música que destrói o clima da cena.

## Licenças

Baixamos diretamente do [catálogo do autor](https://incompetech.com/music/royalty-free/music.html), com os detalhes por ISRC e a licença indicada na página oficial. A [página de licenciamento](https://incompetech.com/music/royalty-free/licenses/) informa que a opção gratuita exige crédito. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) permite uso comercial e adaptações com atribuição, link da licença e indicação de alterações. As cópias das páginas, do texto jurídico e dos registros das faixas estão em `biblioteca-audio/licencas`.

Para cada música usada, inclua título, Kevin MacLeod, link da página da faixa, link CC BY 4.0 e nota de cortes/fades/ajuste de volume/sincronização. Use os arquivos `*-credito.txt` ou o campo `attribution`. Não atribua a licença da música ao vídeo inteiro: ter música CC BY não obriga colocar sua gameplay sob Creative Commons.

Os memes fornecidos podem conter áudios de jogos, programas, falas ou gravações de terceiros. Não inferir licença pelo nome, duração, site que oferece download ou popularidade. Os convertidos `eem mp3-*` mantêm seus nomes porque ainda precisam de escuta para identificação. Marque tags após ouvir; não invente o conteúdo. Antes de habilitar comercialmente um efeito externo, obtenha licença da fonte/titular, salve a comprovação, registre requisitos de crédito e atualize o catálogo e o hash. Na falta de comprovação, substitua pelo efeito original apropriado.

Sugestões de função para os arquivos fornecidos, **a confirmar por escuta**, antes de usá-los numa prévia ou de comprovar sua licença:

| Arquivos | Função editorial provável | Alternativa original |
|---|---|---|
| `correct (MAIN INTRO SOUND).mp3`, `ding.mp3`, `collectpin.mp3`, `lego-star-wars-minikit-collect-sound.mp3` | intro curta, acerto, coleta ou vitória | `sucesso-original.mp3` ou `ding-original.mp3` |
| `error.mp3`, `minecraft-villager.mp3` | erro, dúvida ou reação | `erro-original.mp3` |
| `vine-boom.mp3`, `metal-pipe.mp3`, `punch-gaming-sound.mp3` | surpresa, impacto ou falha cômica | `impacto-original.mp3` |
| `running-sound.mp3`, `im-fast-as-f-boi.mp3` | corrida; a fala com palavrão deve ser substituída no conteúdo infantil | `whoosh-original.mp3` com música de aventura |
| `weeeeeeeeee.mp3`, `faaah.mp3`, `fahhh-pump-sound.mp3` | salto ou reação vocal, dependendo do áudio real | `boing-original.mp3` |
| `chicken-on-tree-screaming.mp3`, `family-feud-good-answer.mp3` | reação exagerada ou aprovação; revisar volume e conteúdo | `boing-original.mp3` ou `sucesso-original.mp3` |

Um áudio licenciado pode receber uma reivindicação equivocada de Content ID; nenhum pacote garante receita ou ausência absoluta de reivindicações. O YouTube explica que [conteúdo royalty-free/Creative Commons pode ser monetizado quando a licença permite uso comercial](https://support.google.com/youtube/answer/2490020). Para gravações próprias, verifique também música dentro do jogo, rádio de jogadores e direitos do conteúdo de origem. Silencie trechos duvidosos em vez de alterar pitch para tentar evitar detecção.

Conteúdo deliberadamente infantil precisa da configuração de público adequada. O YouTube informa que [vídeos marcados para crianças não recebem anúncios personalizados](https://support.google.com/youtube/answer/9713557); anúncios contextuais podem existir. Isso muda a receita possível e não é resolvido pela licença musical.

## Seleção e mixagem

Monkeys Spinning Monkeys, Fluffing a Duck, Happy Boy Theme: piadas leves. Sneaky Snitch e Scheming Weasel: travessura/tentativa. Investigations: descoberta/mistério suave. Pixelland e Jaunty Gumption: obby/aventura. Hyperfun: corrida cômica. Carefree e Wallpaper: exploração e fala. Local Forecast - Elevator: espera cômica curta. Essas são escolhas de clima, sem validação de tendência viral atual.

Comece com trilha aproximadamente 18–26 dB abaixo do nível máximo do arquivo, ajuste pelo ouvido e use ducking durante voz. SFX devem realçar o evento, sem esconder palavras nem produzir sustos por volume. Mire mix integrado perto de -14 LUFS e true peak abaixo de -1.5 dBTP como ponto de partida; não são exigências de upload. O script usa normalização em duas passadas e AAC; meça novamente o arquivo final porque a codificação pode alterar picos.
