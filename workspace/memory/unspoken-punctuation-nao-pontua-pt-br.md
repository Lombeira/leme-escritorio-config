---
name: unspoken-punctuation-nao-pontua-pt-br
description: unspokenPunctuation do Chrome não produz nenhum sinal em pt-BR; pontuação do ditado é feita em código
metadata: 
  node_type: memory
  type: project
  originSessionId: fbf6bce5-cd38-42e4-9d46-c56e2364db34
  modified: 2026-09-07T18:01:54.661Z
---

Medido em 07/09/2026, no Chrome do Glauco (tem a propriedade — o teste
`"unspokenPunctuation" in new webkitSpeechRecognition()` deu `true`):
`SpeechRecognition.unspokenPunctuation` **não produz um único sinal em pt-BR**.
Frase longa com pausa nítida, `continuous: true`, rodada com `true` e com
`false`: os dois resultados vieram sem pontuação alguma. A atribuição foi
removida do `useSpeechRecognition`; quem pontua é `applySpokenPunctuation`, por
comando falado ("vírgula", "ponto final").

**Why:** a propriedade infere por pausa e prosódia, e a cobertura do modelo do
Google por idioma não acompanha a existência da API. Ter a propriedade não é ter
a feature — foi o que me fez errar duas vezes: primeiro supondo que o Chrome era
antigo, depois aceitando um veredito de script que comparava as strings inteiras
e acusou "funciona" quando o que mudou foram as palavras transcritas, não os
sinais.

**How to apply:** para testar reconhecimento de fala, comparar **só a
pontuação** (`texto.replace(/[^,.;:!?…]/g, "")`), nunca o texto inteiro — o
reconhecedor varia as palavras entre rodadas e mascara o resultado. E frase de
três palavras não serve: sem pausa real não há prosódia para inferir. Se algum
dia valer testar de novo, o `CLEANUP` do `applySpokenPunctuation` já desmancha
pontuação duplicada, então ligar de volta é só uma linha. Relacionado:
[[validate-fixes-empirically]].
