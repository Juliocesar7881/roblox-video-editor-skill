# Formato dos Shorts animados

Extraído de três Shorts de referência do usuário (25 s, 9:16, 30 fps, noob amarelo/azul/verde com rosto de olhos grandes, legendas palavra a palavra com palavra-chave em amarelo).

## Estrutura (~25 s)

| Tempo | Bloco | O que acontece |
|---|---|---|
| 0–2 s | Gancho | Pergunta direta com o desafio: "Qual X …?". Close médio no noob, já com expressão (surpreso/medo). |
| 2–6 s | Opções | "O 1, o 2 ou o 3?" (ou cores). Um corte rápido por opção, câmera mostrando cada uma. Termina com "**Escolhe rápido!**". |
| 6–11 s | Contagem | Selo 5→4→3→2→1 (1 s cada) em plano aberto mostrando as três opções; noob olhando de um lado para o outro, suando. Som a cada número. |
| 11–20 s | Tentativas | Ele escolhe uma ("Vou na vermelha!"), algo inesperado acontece (reação: "Uma batata?!"). Pode tentar a segunda. Closes de reação com rosto exagerado. |
| 20–25 s | Reviravolta | O final que contradiz a expectativa (a "ondinha", "tem que pagar", tombo). Último quadro com reação forte; corte seco. |

O vídeo não termina com despedida: acaba no pico da piada (favorece o replay). Frases de 2–5 palavras, uma ideia por fala.

## Linguagem visual

- Cortes a cada 1–2,5 s, alternando plano aberto (cenário + opções), médio (corpo) e close (rosto). Câmera baixa (abaixo dos olhos) deixa o noob e os objetos grandiosos.
- Rosto: sempre reagindo. `surpreso` no gancho, `medo` + suor na contagem, `confiante` ao escolher ("eu sou muito bom"), `tonto`/`medo` na reviravolta. Pupilas olhando para o que ele cita.
- Cenário colorido e saturado, objetos grandes e simples, céu limpo. Nada de interface do Roblox na tela.
- Números das opções visíveis no cenário (placas 1, 2, 3 ou cores fortes) para a criança escolher junto.

## Áudio

- Voz do noob (Roger, ElevenLabs) clara e na frente; música de fundo baixa e animada.
- SFX em quase todo evento: whoosh nos cortes, pop nas legendas de reação, tique/ding a cada número da contagem, impacto/boing/pum nas quedas, aplausos ou "erro" na reviravolta.

## Roteiro (`roteiro.json`)

```json
{
  "titulo": "QUAL ESCORREGADOR É O MAIS RÁPIDO?",
  "vozes": {"noob": "Roger"},
  "destaques": ["MAIS RÁPIDO", "VERMELHO", "AZUL", "AMARELO", "RÁPIDO"],
  "falas": [
    {"id": "01", "personagem": "noob", "texto": "Qual escorregador é o mais rápido?"},
    {"id": "02", "personagem": "noob", "texto": "O vermelho, o azul ou o amarelo? Escolhe rápido!"}
  ],
  "planos": [
    {"fala": "01", "camera": "close baixo no noob", "rosto": "surpreso", "acao": "olha para cima"}
  ]
}
```
