---
name: tailwind-fora-de-layer-por-causa-do-chakra
description: "No leme-app os utilitários do Tailwind precisam ficar fora de @layer enquanto o Chakra existir, senão o CSSReset dele vence"
metadata: 
  node_type: memory
  type: project
  originSessionId: a99388fe-98a6-4c2c-95d6-18c161a3896b
  modified: 2026-08-13T13:12:35.722Z
---

Enquanto o `ChakraProvider` estiver montado, `src/styles/tailwind.css` precisa
importar `theme.css`, `preflight.css` e `utilities.css` separadamente, deixando
**`utilities.css` sem `layer()`**. O `@import "tailwindcss"` de uma linha só
coloca tudo em `@layer utilities`.

**Why:** o `CSSReset` do Chakra injeta regras sem layer nenhum — entre elas
`button { background: transparent; padding: 0 }` e `a { color: inherit }`. CSS
não-layered vence qualquer coisa dentro de `@layer`, independentemente de
especificidade. Com o import padrão, `px-4` ou `bg-blue-500` num `<button>`
simplesmente não têm efeito: a classe aparece no DOM, a regra existe na folha, e
o estilo computado continua sendo o do reset. Não dá erro nem aviso.

**How to apply:** ao migrar qualquer elemento para uma tag que o reset do Chakra
estiliza (`a`, `button`, `table`, `textarea`, `img`, `hr`, `fieldset`), conferir
o **estilo computado** no navegador, não só o `className`. Quando o Chakra sair
(fase 12 do LM-2209), isso pode voltar a ser `@import "tailwindcss"` numa linha.

Relacionado: [[validate-fixes-empirically]] — este achado só apareceu porque a
paridade do `Button` foi medida com `getComputedStyle` em vez de conferida no
olho.
