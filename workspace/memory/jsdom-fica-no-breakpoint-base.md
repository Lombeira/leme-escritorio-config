---
name: jsdom-fica-no-breakpoint-base
description: Nos testes o Chakra fica no breakpoint base (celular) e mock de matchMedia não muda isso
metadata: 
  node_type: memory
  type: project
  originSessionId: 7318648c-dfec-4dac-a19d-e921cedc2419
  modified: 2026-09-08T17:38:47.190Z
---

No jsdom nenhuma media query casa, então `useBreakpointValue({ base: X, md: Y })`
devolve sempre o valor de `base` — todo teste de página roda na versão **celular**
da tela. Mocar `window.matchMedia` para casar `min-width` **não** resolve: o
`useMediaQuery` do Chakra só atualiza pelo evento `change`, e um mock estático
nunca o dispara.

**Why:** medido em 08/09/2026 tentando testar as setas de semana de Conteúdos,
que só existem no desktop (`viewType === "calendar" && !isMobile`). O botão nunca
renderizou, mesmo com o mock de viewport.

**How to apply:** escolha a asserção pelo que a versão celular renderiza (em
Conteúdos, o seletor de dia em vez do seletor de semana) e exercite a mesma
função pelo caminho do celular. Se o comportamento só existe no desktop, diga que
ficou sem cobertura automatizada em vez de fabricar um mock que não funciona.
Ver [[lottie-derruba-teste-de-pagina]] para a outra armadilha do mesmo ambiente.
