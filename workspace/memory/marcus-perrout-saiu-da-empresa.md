---
name: marcus-perrout-saiu-da-empresa
description: Marcus Perrout não trabalha mais na Leme; a conta dele no Jira segue ativa e cards antigos aparecem como se tivessem dono
metadata: 
  node_type: memory
  type: project
  originSessionId: 152a3490-fc96-460c-8008-4f38a71e173a
  modified: 2026-08-17T16:32:10.798Z
---

Marcus Perrout (accountId `712020:4949c860-c354-4074-b06f-3233e0101415`) saiu da Leme — confirmado pelo Glauco em 17/08/2026. A conta Atlassian dele continua com `"active": true`, então cards antigos aparecem com avatar e nome normais, como se tivessem dono ativo.

**Why:** sugeri mover um card dele para "Desenvolvendo" achando que era trabalho parado — teria criado um card fantasma no board de delivery com a foto de quem não está mais lá. O dado do Jira não denuncia a saída.

**How to apply:** ao encontrar um card órfão ou parado, checar quem é o assignee antes de propor mexer no status. Card de pessoa que saiu se resolve com fechamento/reatribuição, não com transição de coluna. Em 17/08/2026 o rastro dele foi limpo: LM-704 fechado como obsoleto (fora de validade, ~70 sprints de carry-over) e LM-595, LM-514, LM-690, LM-346 reatribuídos ao Glauco. Ver [[jql-status-nome-nao-resolve]] para as regras do board 2.
