# Regras de produção (incorporadas de eibrunoruan/roblox-shorts-generator)

Regras do sistema do amigo do usuário, adaptadas a esta skill. Valem para todo Short animado.

## Personagem e atuação
- Noob clássico R15: cabeça e braços amarelos, torso azul, pernas verdes; rosto de desenho com olhos ovais grandes, contorno grosso, pupilas pequenas, sobrancelhas grossas e boca grande de susto com língua.
- Movimentos básicos com os pacotes oficiais do Roblox (Cartoony para locomoção, Levitation para flutuar, emotes R15). Não inventar poses de locomoção.
- **A boca mexe com a voz real** (`K.falar` com o envelope do MP3). Nunca uma fala com a boca parada.
- Nada de tremedeira na contagem. Reação = expressão + olhar + animação, não tremor.
- Toda transição de animação precisa ser limpa: revisar os quadros antes, durante e depois de cada troca ("animações perdidas" são defeito).

## Câmera — regra nº 1: o rosto é o protagonista
- Cabeça com pelo menos 10% da altura do quadro (close 22–26%, plano médio 14%, aberto 10%), olhos no terço superior.
- Câmera no máximo 45° fora do olhar do personagem; nunca de costas sem motivo narrativo. Calcular a câmera pela direção real da cabeça (`LookVector`), não por um deslocamento fixo no mundo.
- Cada acontecimento importante termina num close de reação de pelo menos 1 s.
- Objetos, efeitos e legendas não cobrem olhos e boca por mais de 0,3 s. A legenda karaokê ocupa ~0,665–0,72 da altura: o rosto inteiro (sobrancelha até o fim da boca de grito) fica acima disso. `K.auditarCamera` mede no quadro final (com os cortes da gravação) e acusa "rosto na faixa da legenda" e "rosto cortado na borda". Câmera seguindo (`cam.seguir`) mira **abaixo** da cabeça (`V(0, -1.5, 0)` no 4º argumento); mirando acima, o rosto desce para a legenda.
- Planos sem o protagonista (mostrar as opções) são insertos curtos, marcados com `K.inserto(true)`.
- `K.auditarCamera` precisa terminar com zero problemas, junto com `K.auditar` (colisões).

## Rosto (feedback do cliente: "o rosto tá diferente", "o olho tá muito colado")
- Igual às referências: olhos ovais altos (altura ~1,85× a largura, cada um ~0,25 da largura da cabeça) com um vão visível entre eles (~0,08), contorno preto grosso, pupila preta estreita com brilho, sobrancelhas grossas logo acima dos olhos (nunca na borda de cima da cabeça), bochechas rosadas, gota de suor verde-água e boca escura com língua rosa.
- O desenho recebe a luz da cena (o branco do olho escurece na sombra junto com a cabeça); nada de peças da cor da pele por cima do rosto (ficam com outra luz e aparecem como faixas).
- Animação do rosto como nas referências: piscada que achata o olho, pupilas olhando em volta, sobrancelhas que sobem na ênfase da fala e boca em poucas aberturas firmes (sem tremer).

## Transições (feedback: "as transições ficaram meio cagadas, parece bug")
- Corte seco, sem flash branco nem efeito no corte. Na troca de lugar, o primeiro quadro do plano novo já tem a pose certa (`K.cortarPara`).
- Movimento encadeado (descida → voo → pouso) termina no tempo da timeline; o corte do pouso acontece no pouso real.
- Sincronia de quadro: boca, cortes e efeitos sonoros no mesmo quadro (marcas de sincronia na gravação).

## Colisões em 5 tempos
1. Ameaça (≥ 0,6 s): o obstáculo aparece antes, com close no rosto.
2. Aceleração (0,4–0,8 s): personagem e obstáculo no mesmo quadro.
3. Contato real (2–4 quadros): encosta de verdade, squash, freeze curto, tremor e efeito sonoro só a partir daí.
4. Grudado/escorrega (0,5–1 s).
5. Consequência: cai com gravidade real; nada de flutuar parado depois do impacto.

## Fala, voz e continuidade
- Voz do Noob: Roger padrão do ElevenLabs (ID `CwhRBWXzGAHq8TQ4Fs17`), idioma **Portuguese** confirmado nas configurações antes de gerar; conferir o ID, não só o nome (existe outro "Roger").
- A fala de intenção vem antes da ação; a reação começa no acontecimento (grito quando o monstro aparece, dano no contato).
- Sem gagueira nem sotaque estrangeiro: corrigir o áudio de origem; a legenda certa não conserta uma fala errada.
- Medir as falas primeiro, depois ajustar o tempo da ação.

## Legendas
- Uma ideia por vez ("O VERMELHO," some → "O AZUL..." some → "OU O AMARELO GIGANTE?"), na pausa a tela fica limpa.
- Lilita One branca, contorno `#10283E`, sombra deslocada para baixo, palavra falada em `#FFE54F`, números em ciano; entrada elástica de cada grupo; área segura inferior, sem cobrir o rosto.

## Montagem e som
- Contador completo de 5 s depois de "Escolhe rápido!", com tique de relógio e música de puzzle durante a decisão; música animada na comemoração.
- Efeito sonoro em toda ação (passo, pulo, whoosh, impacto, tombo), escolhido pelo acontecimento e com procedência registrada. Escorregar = som de atrito no plástico (`escorregar-trava`/`escorregar-rapido`), com o rangido/lançamento no instante exato da parada/saída.
- Nenhum efeito por cima de fala: whoosh, rufar e buzzer terminam antes da palavra ou entram na pausa.
- Não impor corte a cada 1–2 s; mover a câmera quando a história pedir.

## Imagem
- 1080×1920, bitrate ≥ 12 Mbps (CRF ≤ 18), sem interface do Studio/Roblox, sem cursor, sem bordas.
- Cenário vivo e com textura (nuvens, árvores, flores, props); iluminação Future, Atmosphere, Bloom, ColorCorrection e SunRays.
