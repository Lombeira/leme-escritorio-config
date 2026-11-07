---
name: ids-das-integracoes
description: "IDs fixos das integrações da Leme: cloudId do Jira/Confluence (leme-tec) e appIds dos projetos do Amplitude (prod, QA/DEV, Lovable)"
metadata:
  type: reference
---

MCPs configurados no `.mcp.json` do workspace (OAuth, conta glauco.lomenha@leme.tec.br):

- **Atlassian**, site `leme-tec.atlassian.net`, cloudId `9d7c6df0-2d10-4af2-b5b0-0bc6bf22e15f`.
  Jira (projeto `LM`) e Confluence. IDs de status em [[jql-status-nome-nao-resolve]].
- **Amplitude**, org `leme-tec` (Leme Educação, id 289248, plano starter).
  Projetos: `616682` Leme Educação (produção), `617768` Leme Educação QA & DEV, `900256` Leme Lovable.

**How to apply:** passar esses IDs direto nas ferramentas em vez de descobrir de novo.
Análise de uso real é no `616682`; teste de evento novo é no `617768`. Cota de gráficos
do plano starter: ver [[amplitude-graficos-exemplo-nao-contam-cota]].
