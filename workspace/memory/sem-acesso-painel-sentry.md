---
name: sem-acesso-painel-sentry
description: "Sentry foi descontinuado na Leme e o time não tem acesso ao painel; não propor usar nem revogar credencial"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1d5001ab-d954-47b4-904d-5b34b47fbafc
  modified: 2026-08-09T14:48:51.454Z
---

O Sentry foi **descontinuado** na Leme (confirmado pelo Glauco em 06/11/2026). Antes
disso o time já tinha perdido o acesso ao painel (confirmado em 09/08/2026, na LM-2151,
que removeu os resíduos de configuração do Sentry do front-end).

**Why:** o `SENTRY_AUTH_TOKEN` antigo segue válido do lado do Sentry enquanto a
organização existir, e ninguém consegue revogá-lo. Follow-up de "revogar o token" é
inexequível.

**How to apply:** não propor Sentry como ferramenta de observabilidade nem revogação ou
rotação de credencial dele. Se aparecer resíduo de Sentry em código ou config, é para
remover. Isso vale só para o Sentry: New Relic (LM-2150) e Cypress Cloud (LM-2152) tinham
follow-ups de rotação de chave a confirmar separadamente.
