# AnimKit — referência rápida

`ReplicatedStorage.AnimKit` (ModuleScript; conteúdo em `luau/AnimKit.lua`, instalado pelo pipeline do `studio_runscript.py montar --kit`).

## Constantes

| Nome | Padrão | Uso |
|---|---|---|
| `K.VERTICAL` | `true` | Câmera deitada 90°: o 9:16 usa o viewport inteiro; `captura_janela.processar` desvira. |
| `K.FOV` | 50 | Campo de visão **horizontal** do vídeo vertical final. |
| `K.CABECA` | 1.45 | Escala da cabeça clássica (as referências usam cabeça maior que o padrão 1.25). |
| `K.CORES` | amarelo/azul royal/verde | Skin das referências. |
| `K.ALTURA_RAIZ` / `ALTURA_SENTADO` / `ALTURA_DEITADO` | 3 / 1.55 / 0.55 | Centro do HumanoidRootPart acima do chão, do assento ou do chão deitado. |
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
| `K.criarNoob(nome, CFrame, {pele=, camisa=, calca=})` | Noob R6 com a skin das referências e rosto de desenho numa placa soldada à frente da cabeça. |
| `K.escorregador(nome, {topo=, dir=, comprimento=, queda=, cor=, corBorda=, largura=, segmentos=, curva=})` | Escada, plataforma, rampa reta ou em espiral e bordas. Guarda os **pontos de assento** (superfície + altura sentado, na normal da rampa) em `Caminho`. |

## Atuação (modo play, no `cena.lua`)

| Função | Uso |
|---|---|
| `K.rosto(noob, expr, t)` | `normal`, `feliz`, `surpreso`, `medo` (suor), `grito` (boca aberta com língua), `nervoso` (dentes cerrados + suor), `confiante` (pálpebra baixa + sorriso), `bravo`, `duvida`, `tonto` (pupilas desencontradas), `apertado` (olhos >_<). |
| `K.olhar(noob, dx, dy)` | Pupilas: −1 a 1. |
| `K.piscar(noob)` | Piscadas automáticas. |
| `K.anim(noob, nome, {loop=, velocidade=, fade=, manter=})` | Animações R6 oficiais: `idle`, `andar`, `correr`, `pular`, `cair`, `escalar`, `sentar`, `acenar`, `apontar`, `rir`, `comemorar`, `dancar`... |
| `K.mover(noob, Vector3, t, anim)` | Anda/corre até o destino, com os pés no piso (a altura vem de `K.chao`). |
| `K.deslizar(noob, K.caminho(modelo), t)` | Desce sentado, inclinado junto com a rampa. Use uma parte dos pontos para "travar" no meio. |
| `K.voar(noob, destino, altura, t, voltas, anim, aoPousar)` | Arco com cambalhotas; o callback roda depois do último quadro do voo (use para pôr a pose de pouso). |
| `K.tremer(noob, t, amp)` / `K.poeira(pos, n)` | Tremedeira e nuvem de poeira. |
| `K.camera.rosto(noob, dist, fovH, {lado=, altura=, queixo=, t=})` | Close pela cabeça real: cabeça no terço de cima. `t` faz travelling. |
| `K.camera.corte(pos, alvo, fovH, cima)` / `K.camera.mover(pos, alvo, t, fovH, estilo, cima)` | Corte e travelling; `cima` define o "para cima" do quadro (ex.: `V(0,0,1)` para filmar de cima alguém deitado). |
| `K.camera.seguir(parte, deslocamento, t)` | Segue mantendo o deslocamento. Cada corte novo cancela o movimento anterior. |
| `K.camera.tremor(i, t)` / `K.camera.soco(i, t)` | Tremida e zoom-soco na própria câmera. |
| `K.rodar(eventos, duracao)` | Esconde a interface, prepara o primeiro quadro (eventos com t ≤ 0), espera, mostra o flash magenta, dispara os eventos e, no fim, outro flash e `K.encerrar()` (o servidor do pipeline encerra o Play). |

Eventos com t ≤ 0 só preparam o primeiro quadro; movimento começa em t ≥ 0,05.
