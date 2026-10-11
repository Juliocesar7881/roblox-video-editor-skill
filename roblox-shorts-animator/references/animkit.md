# AnimKit — referência rápida

`ReplicatedStorage.AnimKit` (ModuleScript; conteúdo em `luau/AnimKit.lua`, instalado pelo pipeline do `studio_runscript.py montar --kit`).

## Constantes

| Nome | Padrão | Uso |
|---|---|---|
| `K.VERTICAL` | `true` | Câmera deitada 90°: o 9:16 usa o viewport inteiro; `captura_janela.processar` desvira. |
| `K.FOV` | 50 | Campo de visão **horizontal** do vídeo vertical final. |
| `K.CABECA` | 1.3 | `HeadScale` do Humanoid R15 (cabeça clássica maior, como nas referências). |
| `K.CORES` | amarelo/azul royal/verde | Skin das referências. |
| `K.ALTURA_RAIZ` / `ALTURA_SENTADO` / `ALTURA_DEITADO` | 3.41 / 1.32 / 0.95 | R15 medido: centro do HumanoidRootPart acima do chão (idle), do assento (sentar + pernas esticadas) e do chão deitado. `ELEVACAO_PASSO` corrige andar/correr. |
| `K.ATRASO` | 0.8 | Segundos entre o flash magenta e o t=0 da timeline. |
| `K.MARCAS` | 5 | Segundos entre as marcas de sincronia (retângulo magenta no alto do viewport, na faixa que a gravação corta). `captura_janela.processar` mede quando elas aparecem e corrige o atraso do Roblox: cortes e boca caem no quadro planejado. |
| `K.ROSTO_TAM` / `ROSTO_LUZ` / `ROSTO_FAIXA` | 1.0 / 0.8 / {0.08, 0.9} | Placa do rosto (frente inteira da cabeça), quanto a luz da cena age no desenho e a faixa vertical desenhada (usada pela auditoria de câmera). |
| `K.MARGEM_TOPO` | 0.075 | Faixa de cima do viewport cortada na gravação (igual a `captura_janela.processar`). |
| `K.FAIXA_LEGENDA` | {0.665, 0.75} | Faixa do vídeo ocupada pela legenda karaokê; o rosto não pode ficar nela. |

## Montagem (modo edição, no `cenario.lua`)

| Função | Uso |
|---|---|
| `K.visual()` | Cores saturadas, bloom, atmosfera; desliga `CharacterAutoLoads`. |
| `K.bloco{Size=, CFrame=, Color=, Material=, Name=, Parent=}` | Part ancorada lisa. |
| `K.piso(parte)` | Marca a peça como chão (atributo `Piso`). **Marque todo chão, pátio e plataforma onde alguém pisa.** |
| `K.chao(pos)` | Altura do piso marcado em (x, z) por raycast que só enxerga pisos. |
| `K.emPe(pos, olharPara)` | CFrame em pé exatamente sobre o piso (y de `pos` é ignorado). |
| `K.deitado(pos, direcaoCabeca)` | Deitado de costas sobre o piso, rosto para cima. |
| `K.criarNoob(nome, CFrame, {pele=, camisa=, calca=})` | Noob **R15** (juntas AnimationConstraint) com a skin das referências; tira a textura de rosto padrão e monta o rosto de desenho numa placa soldada à frente da cabeça, depois de a escala da cabeça ser aplicada. Rosto medido nas referências do cliente: olhos ovais altos (0,25 × 0,46 da cabeça) com vão de 0,08 entre eles, contorno grosso, pupila estreita com brilho, sobrancelhas grossas, bochechas, gota de suor verde-água e boca escura com língua. Elipses de verdade com `rbxasset://textures/whiteCircle.png` (vem com o Studio) e luz da cena no desenho. |
| `K.escorregador(nome, {topo=, dir=, comprimento=, queda=, cor=, corBorda=, largura=, segmentos=, curva=})` | Escada, plataforma, rampa reta ou em espiral e bordas. Guarda os **pontos de assento** (superfície + altura sentado, na normal da rampa) em `Caminho`. |

## Atuação (modo play, no `cena.lua`)

| Função | Uso |
|---|---|
| `K.rosto(noob, expr, t)` | `normal`, `feliz` (sorriso "D"), `surpreso`, `medo` (suor), `grito` (boca aberta com língua), `nervoso` (dentes cerrados + suor), `confiante` (sobrancelhas descendo + sorriso), `bravo`, `duvida` (uma sobrancelha), `tonto` (pupilas girando), `apertado` (olhos >_<), `nocaute` (olhos X). Um controlador por quadro junta expressão, piscada, olhar e fala (sem tweens brigando). |
| `K.olhar(noob, dx, dy, t)` | Pupilas: −1 a 1. |
| `K.piscar(noob)` | Piscadas automáticas: o olho (e a pupila) achata até quase fechar e volta em 0,16 s, como nas referências. |
| `K.anim(noob, nome, {loop=, velocidade=, fade=, manter=})` | Pacote Cartoony (`idle`, `idle2`, `andar`, `correr`, `pular`, `cair`, `escalar`, `nadar`), Levitation (`flutuar`, `voarPose`, `superpulo`) e emotes R15 (`sentar`, `acenar`, `apontar`, `rir`, `comemorar`, `dancar`). `K.preCarregar(noob)` antes da cena. |
| `K.falar(noob, envelope, fps)` | Boca de fala guiada pelo volume real da voz (string de dígitos 0–9 por quadro, de `scripts/envelope_boca.py`): fechada + 3 aberturas escuras (língua nas maiores), cada uma por pelo menos 60 ms, e sobrancelhas que sobem na ênfase. Volta para a boca da expressão no fim. |
| `K.pose(noob, nome)` | Pose fixa por cima da animação girando os encaixes das juntas (`sentadoReto`, `bracosPraCima` ou tabela própria); `nil` desfaz. `K.sentarEm`/`K.deslizar` usam `sentadoReto`. |
| `K.mover(noob, Vector3, t, anim)` | Anda/corre até o destino, com os pés no piso (a altura vem de `K.chao`). |
| `K.deslizar(noob, K.caminho(modelo), t, anim, aoTerminar)` | Desce sentado com as pernas esticadas, inclinado com a rampa desde o primeiro quadro, guiado pelo relógio (termina exatamente em `t`). Use uma parte dos pontos para "travar" no meio. Passe `t = T_fim - K.tempo()` para terminar num tempo da timeline. |
| `K.voar(noob, destino, altura, t, voltas, anim, aoPousar)` | Arco com rolamentos laterais (o rosto continua para a câmera da frente); com destino `CFrame` (`K.deitado`) termina na pose de pouso; o callback roda no pouso real. Encadeado depois de `K.deslizar`, use `t = T_pouso - K.tempo()` (atrasos de quadro não se somam). No pouso, troque para `idle` (sem animação o R15 deitado abre os braços em T) e faça o corte da câmera ali dentro com `K.cortarPara`. |
| `K.tremer(noob, t, amp)` / `K.poeira(pos, n)` | Tremedeira e nuvem de poeira. |
| `K.camera.rosto(noob, dist, fovH, {lado=, altura=, queixo=, t=})` | Close pela cabeça real: cabeça no terço de cima. `t` faz travelling. |
| `K.camera.corte(pos, alvo, fovH, cima)` / `K.camera.mover(pos, alvo, t, fovH, estilo, cima)` | Corte e travelling; `cima` define o "para cima" do quadro (ex.: `V(0,0,1)` para filmar de cima alguém deitado). |
| `K.camera.seguir(parte, deslocamento, t, mira)` | Segue mantendo o deslocamento e olhando para `parte + mira` (padrão `V(0, 1, 0)`). Seguindo `noob.Head`, use `mira = V(0, -1.5, 0)` (abaixo da cabeça): o rosto fica no terço de cima, fora da legenda. Cada corte novo cancela o movimento anterior. |
| `K.camera.tremor(i, t)` / `K.camera.soco(i, t)` | Tremida e zoom-soco na própria câmera. |
| `K.cortarPara(noob, cf, anim, camera, {pose=})` | Corte com teletransporte sem o quadro do "noob na pose velha no lugar novo": troca a animação ainda no plano antigo, espera o Animator aplicá-la (1 quadro) e só então muda de lugar e chama `camera()`. Use em todo corte que muda o noob de lugar. |
| `K.foco(parte)` | Foco do desfoque de fundo (`AK_Foco`, criado por `K.visual`): segue a parte a cada quadro (closes com fundo bem desfocado, como nas referências). |
| `K.rodar(eventos, duracao)` | Esconde a interface, prepara o primeiro quadro (eventos com t ≤ 0), espera, mostra o flash magenta, dispara os eventos e, no fim, outro flash e `K.encerrar()` (o servidor do pipeline encerra o Play). |

Eventos com t ≤ 0 só preparam o primeiro quadro; movimento começa em t ≥ 0,05.

## Auditorias (obrigatórias antes de gravar)

| Função | Uso |
|---|---|
| `K.auditar(noob)` | Colisões: partes do corpo dentro do chão/objetos, com tempo e peça (`[auditoria]`). |
| `K.auditarCamera(noob, minimo)` | Regra nº 1, medida no quadro final 9:16 (`K.noVideo` refaz os cortes da gravação), logo depois da câmera em cada quadro: rosto pequeno, de costas, de perfil (> 0,5 s), fora do quadro, cortado na borda (> 0,2 s) ou na faixa da legenda (> 0,3 s) (`[camera]`). Com `K.AUDITORIA_DETALHE`, imprime `[camera-detalhe]` a cada 0,5 s (faixa do rosto e centro no vídeo). |
| `K.inserto(true/false)` | Marca planos sem o protagonista (ex.: mostrar as opções). |
