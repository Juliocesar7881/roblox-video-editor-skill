Skills de Roblox para Claude: edição de gameplay (`roblox-video-editor`) e **nova** criação de Shorts animados no Roblox Studio (`roblox-shorts-animator`).

## v1.11.1 — originalidade obrigatória e gravação mais robusta
- Todo vídeo novo com ideia e roteiro inéditos: consultar o histórico em `entregas/`, registrar `originalidade.json` e usar os modelos só como infraestrutura (SKILL.md das duas skills).
- Gravação: guarda de tempo no flash final (objetos magenta do cenário não encerram a captura antes da hora); `studio_runscript.py` lê a saída do Studio direto do processo, com o arquivo como reserva.
- `fazer_bilingue.py`: confere a duração do `cena.mp4` antes de editar; auditoria com problema sempre bloqueia a gravação, e saída não capturada só passa com `--sem-confirmar-auditoria`.
- `renderizar.py`: grafo do FFmpeg passado direto em `-filter_complex`.

## v1.11.0 — espanhol automático, gesto six seven e placas sem nada na frente
- `scripts/fazer_bilingue.py PROJETO`: faz o Short nos dois idiomas numa rodada só (auditoria zerada, gravação com regravação se perder quadros, edição, revisão de legendas, render) e só termina com os dois MP4; `--so-conferir` acusa entrega sem o espanhol. O SKILL.md manda fazer o espanhol junto, sem esperar pedido.
- `K.sixSeven(noob, lado)`: gesto "six seven" com as mãos, uma mão por palavra, sincronizado com a voz (Transform nas juntas depois do Animator).
- Legendas: a sobra de uma frase termina no corte de câmera (não entra no plano seguinte nem num inserto) e sobra curta demais vira parte do destaque anterior.
- `scripts/receptor_falas.py`: recebe os áudios da aba do ElevenLabs por uma página local quando o Chrome bloqueia vários downloads (sem mexer na configuração do navegador).
- Modelo `modelos/aura-six-seven/` (porta VIP, medidor de aura, six seven): placa na frente das colunas, stickers fora da placa e do rosto, insertos do medidor e da porta abrindo.

## v1.10.0 — todo Short em português e espanhol
- Regra fixa: todo Short sai em duas versões, português e espanhol, com a mesma voz (Roger); cada idioma com falas, gravação, legendas e publicação próprias.
- `--idioma es` em `tts_elevenlabs.py`, `alinhar_falas.py`, `gerar_cena.py` e `montar_edicao.py` (pastas e arquivos `-es`); roteiro com `texto_es`, `titulo_es`, `arquivo_es`; legendas sabem as palavras de ligação do espanhol.

## v1.9.0 — rosto idêntico ao Short de referência e legenda esperando o corte
- Rosto refeito a partir do Short de referência do cliente ("O CHÃO VIROU LAVA NO ROBLOX", BRUNOBLOX): olhos ovais altos quase encostando, branco creme, pupila estreita com brilho, sobrancelhas grossas inclinadas, suor ciano ao lado do olho; bocas como no vídeo (oval preta alta com língua ao falar/gritar, traço branco no neutro, boca aberta com dentes na alegria, olhos X no nocaute). As caretas da v1.8 saíram; os nomes delas viraram apelidos.
- Legenda: o corte para a opção volta para a palavra ("amarelo") e a frase que começa antes ("ou o amarelo gigante?") só aparece no corte, com a tela sem legenda até o escorregador aparecer.
- Mantidos da v1.8: noob em proporção padrão, sem sticker de gotas.

## v1.8.0 — caretas da skill de referência, noob em proporção certa e legenda junto do corte
- Rosto trocado pelas caretas da skill eibrunoruan/roblox-shorts-generator (Expressions.lua + SpeechMouth.lua portados sem mudanças): `curious`, `panic`, `angry`, `eat`, `hurt`, `relief`, `greedy`, `disgust`, `neutral`, com estouro na troca, piscada, sobrancelhas balançando e boca de fala; os nomes antigos viraram apelidos.
- Gota de suor escorrendo do rosto (careta `panic`) no lugar do sticker de gotas solto na tela.
- Noob com as cores e as proporções do noob da skill de referência (cabeça padrão): as pernas não parecem mais minúsculas.
- Legendas: o corte para cada opção entra no começo da frase dela e nenhum grupo de legenda atravessa um corte (`cortes=`); `revisar_legendas.py` acusa legenda atravessando corte.
- Câmeras dos planos abertos aproximadas para o rosto continuar com ≥ 8% da altura com a cabeça padrão.

## v1.7.0 — rosto igual às referências, cortes limpos e sincronia de quadro
- Rosto novo, medido nas referências do cliente: olhos ovais altos e separados (antes encostavam), elipses de verdade (textura `whiteCircle.png` do Studio), pupila estreita com brilho, sobrancelhas grossas, boca escura com língua, gota de suor verde-água, olhos X de nocaute, e desenho com a luz da cena (sem a faixa amarela da pálpebra antiga).
- Animação do rosto num controlador único por quadro: piscada que achata o olho, sobrancelhas que sobem na ênfase da fala, boca em 4 aberturas firmes; antes os tweens de piscar e de expressão brigavam e podiam travar o olho.
- Sincronia: o gravador agora carimba cada quadro na hora da captura (o vídeo saía ~0,14 s adiantado: boca abrindo antes da voz, efeitos atrasados) e marcas de sincronia na faixa cortada do viewport medem e corrigem o atraso do Roblox. Cortes a ±2 quadros do planejado.
- Cortes sem bug: `K.cortarPara` (nada do noob na pose antiga por um quadro no lugar novo), descida já inclinada no primeiro quadro, pouso em `idle` (sem pose T) com o corte dentro do pouso, movimentos encadeados terminando nos tempos da timeline, sem flash branco nos cortes.
- Fundo desfocado nos closes (`K.foco`), plano de baixo para cima no escorregador gigante, cena de teste do rosto em `modelos/teste-rosto.lua`.

## v1.6.0 — legendas sem bugs, som de escorregador e rosto fora da legenda
- Legendas karaokê corrigidas: nunca duas ao mesmo tempo (cada evento com posição fixa e sem sobreposição), palavras curtas acendem junto com a vizinha (nada de destaque piscando), pausas sem destaque, fade curto na saída, tamanho medido na referência.
- Novo `roblox-video-editor/scripts/revisar_legendas.py`: renderiza só as legendas e aponta sobreposição, destaque piscando, legenda em duas linhas, texto cortado e legenda junto com sticker/selo. Obrigatório antes da versão final.
- Sons originais de escorregador (`scripts/criar_sfx_escorregador.py`, sintetizados, uso comercial livre): `escorregar-trava` (atrito que para com rangido de borracha aos 2,0 s), `escorregar-rapido` (atrito acelerando + lufada no lançamento aos 2,2 s), `escorregar-curto` e `apito-escorregador` (apito de desenho descendo). Receita conferida com classificador AudioSet ("Scrape", "Squeak", "Whoosh").
- Auditoria de câmera mede no quadro final (com os cortes da gravação), logo depois da câmera em cada quadro, e acusa "rosto na faixa da legenda" e "rosto cortado na borda"; `cam.seguir` aceita mira abaixo da cabeça.
- Piloto corrigido: rosto no terço de cima na descida e no escorregador vermelho, pouso visto de cima com o rosto à mostra, legendas fora da contagem, efeitos fora das falas.

## v1.5.0 — regras do roblox-shorts-generator, pacote de animação e boca falando
- Regras de produção do sistema de eibrunoruan/roblox-shorts-generator incorporadas (`references/regras-producao.md`): rosto como protagonista, colisões em 5 tempos, voz Roger com ID e idioma conferidos, contagem de 5 s, legendas, qualidade de imagem.
- Noob em R15 com os pacotes oficiais do Roblox: Cartoony (locomoção), Levitation e emotes R15; cabeça clássica maior via `HeadScale`; suporte a juntas `AnimationConstraint`.
- Boca sincronizada com a voz real (`K.falar` + `scripts/envelope_boca.py`).
- Auditoria de câmera (`K.auditarCamera`): rosto pequeno, de costas, de perfil ou fora do quadro; `K.inserto` para planos sem o protagonista.
- Sem tremedeira na contagem; voo com rolamento lateral (rosto para a câmera); descida guiada pelo relógio; pose sentado com pernas esticadas (`K.pose`).
- Corrigido: tabelas fracas que perdiam animações e poses ("animações perdidas"); rosto montado antes da escala da cabeça.
- Legendas "uma ideia por vez" com divisão equilibrada que nunca termina em artigo; Lilita One (OFL) com a receita do amigo: contorno `#10283E`, sombra para baixo, destaque `#FFE54F`, números em ciano, entrada elástica, encolhe se não couber.

## v1.4.0 — animação sem bugs e legendas no estilo das referências
- Auditoria automática no Studio (`K.auditar`): detecta, com tempo e peça, qualquer parte do corpo entrando no chão ou em objetos; a skill exige corrigir até zerar antes de gravar.
- Corrigido: noob enterrado no chão (o rig do Roblox vinha com a cabeça como PrimaryPart), pernas atravessando rampas nas dobras, pose sentada misturando com a em pé, passada de corrida, voo saindo da rampa, animações tocando antes de carregar.
- Novo estilo de legenda `karaoke`: 2–3 palavras, Fredoka One branca com contorno azul-marinho e sombra, palavra falada em amarelo, entrada com fade rápido (copiado dos Shorts de referência).
- Gravação sem cursor do mouse e sem os botões do Roblox.

## v1.3.0 — Shorts animados no Roblox Studio
- `/roblox-shorts-animator`: da ideia ao MP4. Roteiro no formato "qual X…? escolhe rápido + reviravolta", voz Roger (ElevenLabs), cena no Studio, gravação, edição e textos de publicação.
- Controle do Studio pela tarefa oficial `-task RunScript` (sem MCP, sem cliques); Play automático via `StudioTestService`, que encerra sozinho.
- Gravação só da janela do Studio (Windows Graphics Capture), mesmo atrás de outras janelas; sincronia e recorte automáticos por flash magenta; câmera "deitada" para o 9:16 sair nítido em 1080×1920 a 60 fps.
- AnimKit (Luau): noob com a skin das referências, rosto de desenho com 11 expressões, chão por raycast só em pisos marcados (os pés nunca afundam), escorregadores com assento na superfície da rampa, voo com pouso, poeira, câmera de close pela cabeça real.
- Voz: `tts_elevenlabs.py` (chave de API com tempos por palavra) ou site do ElevenLabs + `alinhar_falas.py` (Whisper local).
- Modelo completo do piloto "Qual escorregador é o mais rápido?" em `roblox-shorts-animator/modelos/`.

## Editor de gameplay
- Renderizador: modo `"entrega": "shorts"`, faixa de voz com a música abaixando sozinha, legendas `legenda` palavra a palavra com `*destaque*` amarelo.
- Sticker `linhas-velocidade` desaconselhado; para velocidade, use tremida e zoom.

**Download único:** `roblox-video-editor-completo.zip`. Extraia, execute `python install.py` e invoque `/roblox-video-editor` ou `/roblox-shorts-animator`.
