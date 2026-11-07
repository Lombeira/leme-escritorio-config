---
name: screenshots-sao-opcionais
description: Screenshots em PR são opcionais no leme-app; não pedir nem lembrar o usuário de anexar prints
metadata: 
  node_type: memory
  type: feedback
  originSessionId: cf136f37-7e93-4584-a3b1-0412ba3e00e5
  modified: 2026-08-08T18:26:15.782Z
---

Screenshots em PR do `leme-app` são **opcionais**. Não pedir, não cobrar e não repetir lembrete sobre
anexar prints — nem quando o diff mexe em UI, nem no fechamento do `/ship`.

**Why:** o `pull_request_template.md` tem uma seção "Screenshots" e o `/ship` mandava avisar o usuário
sempre que houvesse mudança visual, repetindo no passo de confirmação. Na prática isso virou ruído em
todo PR. O usuário disse explicitamente em 08/08/2026: "deixe claro pra skills que as screenshots são
opcionais e você não precisa solicitar elas toda hora".

**How to apply:** preencher a seção do template com algo honesto — `N/A`, ou uma linha descrevendo a
mudança visual — e seguir em frente. Se um revisor pedir print em um PR específico, aquilo é uma
conversa daquele PR, não uma regra a reintroduzir na skill. Escopo da LM-2146.
