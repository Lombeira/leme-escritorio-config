---
name: tooltip-centralizado-na-borda-estica-documento
description: Tooltip do Chakra com placement centralizado em elemento na borda da viewport estica o documento e cria duas barras de scroll
metadata: 
  node_type: memory
  type: project
  originSessionId: fbf6bce5-cd38-42e4-9d46-c56e2364db34
  modified: 2026-09-07T18:41:42.722Z
---

No leme-app, `<Tooltip placement="top">` num elemento encostado na borda direita
da viewport **estica o documento** em vez de trazer o tooltip para dentro:
aparecem barra de scroll horizontal **e** vertical na página inteira. Visto no
botão de ditado, que fica na borda direita do campo — e num drawer a borda
direita do campo é a borda direita da viewport.

**Why:** o tooltip é portalizado e posicionado pelo Popper. Com placement
centralizado (`top`, `bottom`), metade da largura dele cai fora da viewport, e o
`preventOverflow` padrão do Chakra não segura contra o documento. Drawer é onde
isto mais acontece, e o app usa drawer em quase toda edição.

**How to apply:** usar o alinhamento pela borda (`top-end`, `bottom-end`) para o
tooltip crescer para dentro. Vale a regra: elemento sobreposto na direita de um
campo nunca leva tooltip centralizado. Não é testável em jsdom — as rects são
zeradas, então não há overflow para detectar, e um teste de placement só
afirmaria a prop. É verificação no navegador. Parente de
[[campo-chakra-focado-cobre-botao-sobreposto]]: os dois são o mesmo padrão de
botão sobreposto a campo do Chakra dando errado por motivo diferente.
