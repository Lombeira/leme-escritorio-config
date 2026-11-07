---
name: renomear-branch-fecha-pr
description: Renomear no GitHub a branch de um PR aberto fecha o PR em vez de levá-lo junto; não reabre sem recriar o nome antigo
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4d261852-d881-4adb-915e-4f403312d844
  modified: 2026-10-27T15:58:04.126Z
---

Em 27/10/2026, `gh api -X POST repos/leme-tech/leme-core/branches/<branch>/rename` na branch do PR #854 (aberto) **fechou o PR** — o GitHub tratou a branch antiga como apagada. `gh pr reopen` falhou ("Could not open the pull request") até a branch ser recriada com o nome antigo no mesmo commit; aí reabriu.

**Why:** o link do PR já estava com o revisor (conversa no Slack); um PR novo perderia o contexto da revisão.

**How to apply:** não renomear branch de PR aberto para seguir o padrão `LM-<n>-…`. O número do card vai no título do PR (`[LM-<n>] …`), que basta para a convenção e para a integração do Jira. Se precisar mesmo, abrir PR novo e linkar o antigo — nunca renomear por baixo. Relacionado: [[conferir-pr-antes-de-novo-push]].
