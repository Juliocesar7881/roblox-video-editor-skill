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

## Montagem (modo edição, no `cenario.lua`)

| Função | Uso |
|---|---|
| `K.visual()` | Cores saturadas, bloom, atmosfera; desliga `CharacterAutoLoads`. |
| `K.bloco{Size=, CFrame=, Color=, Material=, Name=, Parent=}` | Part ancorada lisa. |
| `K.piso(parte)` | Marca a peça como chão (atributo `Piso`). **Marque todo chão, pátio e plataforma onde alguém pisa.** |
| `K.chao(pos)` | Altura do piso marcado em (x, z) por raycast que só enxerga pisos. |
| `K.emPe(pos, olharPara)` | CFrame em pé exatamente sobre o piso (y de `pos` é ignorado). |
| `K.deitado(pos, direcaoCabeca)` | Deitado de costas sobre o piso, rosto para cima. |
| `K.criarNoob(nome, CFrame, {pele=, camisa=, calca=})` | Noob **R15** (juntas AnimationConstraint) com a skin das referências; tira a textura de rosto padrão e monta o rosto de desenho numa placa soldada à frente da cabeça, depois de a escala da cabeça ser aplicada. |
| `K.escorregador(nome, {topo=, dir=, comprimento=, queda=, cor=, corBorda=, largura=, segmentos=, curva=})` | Escada, plataforma, rampa reta ou em espiral e bordas. Guarda os **pontos de assento** (superfície + altura sentado, na normal da rampa) em `Caminho`. |

## Atuação (modo play, no `cena.lua`)

| Função | Uso |
|---|---|
| `K.rosto(noob, expr, t)` | `normal`, `feliz`, `surpreso`, `medo` (suor), `grito` (boca aberta com língua), `nervoso` (dentes cerrados + suor), `confiante` (pálpebra baixa + sorriso), `bravo`, `duvida`, `tonto` (pupilas desencontradas), `apertado` (olhos >_<). |
| `K.olhar(noob, dx, dy)` | Pupilas: −1 a 1. |
| `K.piscar(noob)` | Piscadas automáticas. |
| `K.anim(noob, nome, {loop=, velocidade=, fade=, manter=})` | Pacote Cartoony (`idle`, `idle2`, `andar`, `correr`, `pular`, `cair`, `escalar`, `nadar`), Levitation (`flutuar`, `voarPose`, `superpulo`) e emotes R15 (`sentar`, `acenar`, `apontar`, `rir`, `comemorar`, `dancar`). `K.preCarregar(noob)` antes da cena. |
| `K.falar(noob, envelope, fps)` | Boca de fala guiada pelo volume real da voz (string de dígitos 0–9 por quadro, de `scripts/envelope_boca.py`). Volta para a boca da expressão no fim. |
| `K.pose(noob, nome)` | Pose fixa por cima da animação girando os encaixes das juntas (`sentadoReto`, `bracosPraCima` ou tabela própria); `nil` desfaz. `K.sentarEm`/`K.deslizar` usam `sentadoReto`. |
| `K.mover(noob, Vector3, t, anim)` | Anda/corre até o destino, com os pés no piso (a altura vem de `K.chao`). |
| `K.deslizar(noob, K.caminho(modelo), t, anim, aoTerminar)` | Desce sentado com as pernas esticadas, inclinado com a rampa, guiado pelo relógio (termina exatamente em `t`). Use uma parte dos pontos para "travar" no meio. |
| `K.voar(noob, destino, altura, t, voltas, anim, aoPousar)` | Arco com rolamentos laterais (o rosto continua para a câmera da frente); com destino `CFrame` (`K.deitado`) termina na pose de pouso; o callback roda no pouso real. |
| `K.tremer(noob, t, amp)` / `K.poeira(pos, n)` | Tremedeira e nuvem de poeira. |
| `K.camera.rosto(noob, dist, fovH, {lado=, altura=, queixo=, t=})` | Close pela cabeça real: cabeça no terço de cima. `t` faz travelling. |
| `K.camera.corte(pos, alvo, fovH, cima)` / `K.camera.mover(pos, alvo, t, fovH, estilo, cima)` | Corte e travelling; `cima` define o "para cima" do quadro (ex.: `V(0,0,1)` para filmar de cima alguém deitado). |
| `K.camera.seguir(parte, deslocamento, t)` | Segue mantendo o deslocamento. Cada corte novo cancela o movimento anterior. |
| `K.camera.tremor(i, t)` / `K.camera.soco(i, t)` | Tremida e zoom-soco na própria câmera. |
| `K.rodar(eventos, duracao)` | Esconde a interface, prepara o primeiro quadro (eventos com t ≤ 0), espera, mostra o flash magenta, dispara os eventos e, no fim, outro flash e `K.encerrar()` (o servidor do pipeline encerra o Play). |

Eventos com t ≤ 0 só preparam o primeiro quadro; movimento começa em t ≥ 0,05.

## Auditorias (obrigatórias antes de gravar)

| Função | Uso |
|---|---|
| `K.auditar(noob)` | Colisões: partes do corpo dentro do chão/objetos, com tempo e peça (`[auditoria]`). |
| `K.auditarCamera(noob, minimo)` | Regra nº 1: rosto pequeno, de costas, de perfil (> 0,5 s) ou fora do quadro (`[camera]`). |
| `K.inserto(true/false)` | Marca planos sem o protagonista (ex.: mostrar as opções). |
