# Como criar as 10 ideias do lote

Cada lote tem **10 histórias inéditas**. Antes de escrever, rode `python scripts/lote.py historico` e leia todas as premissas que aparecem: nenhuma das 10 pode repetir premissa, objetivo, mecânica, sequência de tentativas ou reviravolta de um vídeo anterior, de um modelo da skill ou de outro vídeo do mesmo lote. Trocar cor, objeto, nome ou título da mesma brincadeira **não** é ideia nova.

## O que todas têm em comum (o estilo da skill)
- Noob R15 da skill, rosto do Short de referência, voz Roger em português e espanhol.
- Gancho em até 2 s com uma pergunta ou situação absurda; falas curtas; 25–35 s.
- Uma escolha com cortes secos nas opções e contagem 5-4-3-2-1 em boa parte dos vídeos (não em todos: varie).
- Reviravolta boba e leve no fim. Humor físico, caretas, efeitos sonoros exagerados.
- **Muitas cores**: céu azul, gramado vivo, props saturados (vermelho, amarelo, azul, verde, rosa, roxo), confete, balões, luzes neon. Nada de cenário cinza ou vazio.
- Infantil: sem violência, sustos pesados, humilhação, palavrões, Robux grátis, links ou pedidos de dados; sem personagens, marcas ou músicas de terceiros.

## Variar dentro do lote
Distribua os 10 vídeos por eixos diferentes. Não use o mesmo eixo mais de 2 vezes no lote:
- **Clima e natureza**: chuva, vento, neve, arco-íris, vulcão de brinquedo.
- **Comida e cozinha**: bolo gigante, pizza, sorvete que derrete, pipoca.
- **Esporte e brincadeira**: chute a gol, basquete, pula-corda, esconde-esconde, cabo de guerra.
- **Escola e casa**: lição, despertador, banho, arrumar o quarto, mochila.
- **Animais e pets**: cachorro, gato, pato, peixinho (sempre feitos de blocos, sem personagens de terceiros).
- **Objetos mágicos**: botão misterioso, controle remoto, caixa surpresa, lâmpada.
- **Transporte**: carrinho, balão, foguete de papelão, skate, trem.
- **Festa e música**: aniversário, dança, show, presente.
- **Tamanho e física**: encolher/crescer, gravidade, ímã, mola.
- **Profissões de faz de conta**: cozinheiro, bombeiro, astronauta, mágico.

Formatos de história (alterne):
1. "Qual X ...?" com 3 opções, contagem e a escolhida dando errado de um jeito bobo.
2. Tentativas em sequência (1ª falha, 2ª falha, a 3ª funciona do jeito mais inesperado).
3. Problema que persegue o noob e ele tenta fugir.
4. Desafio cronometrado com números na tela.
5. Antes/depois: o noob faz algo e o resultado é exagerado.

## Registro
Para cada vídeo, `originalidade.json` com `premissa`, `objetivo`, `mecanica`, `tentativas`, `reviravolta`, `projetos_comparados` e `diferenca_dos_anteriores`. Verifique de novo antes de gerar as vozes e antes de gravar.

## Cenas que a skill já faz bem (use para variar sem inventar mecânica impossível)
Correr/andar (`K.mover`), cortes de lugar (`K.cortarPara`), escorregar (`K.deslizar`), voar/cair (`K.voar` + `K.deitado`), gesto com as mãos (`K.sixSeven`), objetos voando com tween, partículas (chuva, brilho, confete), portas/placas/medidores com SurfaceGui, caretas (`K.rosto`). Uma ideia que precisa de algo novo (nadar, dirigir de verdade) custa muito mais tempo de cena: prefira representar com cortes e objetos.
