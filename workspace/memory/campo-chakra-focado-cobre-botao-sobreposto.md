---
name: campo-chakra-focado-cobre-botao-sobreposto
description: Input/Textarea do Chakra em foco ganha zIndex 1 e engole o clique de botão absoluto sobreposto
metadata: 
  node_type: memory
  type: project
  originSessionId: fbf6bce5-cd38-42e4-9d46-c56e2364db34
  modified: 2026-09-07T17:31:56.787Z
---

No leme-app, um botão `position="absolute"` por cima de um `Input`/`Textarea` do
Chakra **para de receber clique quando o campo está focado**. Tirar o foco do
campo e o mesmo botão volta a clicar. Confirmado no tema:
`@chakra-ui/theme/dist/esm/components/input.mjs` tem
`_focusVisible: { zIndex: 1, ... }` no `field` da variante `outline`, e o
`textareaTheme` reaproveita esse `field` inteiro.

**Why:** o `baseStyle` do campo já é `position: relative`, então com `zIndex: 1`
no foco ele passa a pintar acima do botão irmão, que tem `z-index: auto`. O anel
de foco é que motiva esse `zIndex` no Chakra (para passar por cima de campos
vizinhos num `InputGroup`), mas ele leva o campo inteiro para cima junto.

**How to apply:** botão sobreposto a campo do Chakra precisa de `zIndex` **maior
que 1**. jsdom resolve a classe do Emotion, então isso é testável de verdade:
`Number(window.getComputedStyle(button).zIndex)` com `toBeGreaterThan(1)` —
reprova sem o `zIndex` e aprova com ele. Vale como sintoma diagnóstico também:
"só clica quando o campo não está focado" é empilhamento, não handler. Parente
de [[emotion-vence-tailwind-em-componente-chakra]] no tema de estilo do Chakra
vencendo o que se escreve por fora.
