---
name: lottie-derruba-teste-de-pagina
description: Teste de página no jsdom quebra na importação do lottie-web; mocar todo @components/Animations/* da árvore
metadata: 
  node_type: memory
  type: project
  originSessionId: 7318648c-dfec-4dac-a19d-e921cedc2419
  modified: 2026-09-08T17:38:40.858Z
---

Qualquer `@components/Animations/*` que use `lottie-web` estoura **na importação**
dentro do jsdom (`TypeError: Cannot set properties of null (setting 'fillStyle')`,
porque `canvas.getContext` devolve `null`) e o React desmonta a árvore inteira —
o teste falha com "Unable to find element" em vez de apontar a causa.

**Why:** o erro aparece longe da causa. Em `src/pages/contents/index.test.tsx`
foram três iterações para achar os três culpados, um por vez, conforme cada
ramo da árvore renderizava: `congrats` (página), `not-found` (empty state) e
`no-results` (visão de calendário).

**How to apply:** antes de rodar um teste de página novo, `grep -rn "Animations"`
nos componentes que a página monta — incluindo os filhos que só aparecem depois
da API resolver — e `vi.mock` cada um devolvendo `() => null`. O mesmo vale para
`react-confetti-boom`. Ver [[jsdom-fica-no-breakpoint-base]] para a outra
armadilha do mesmo ambiente.
