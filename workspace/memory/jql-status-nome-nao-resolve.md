---
name: jql-status-nome-nao-resolve
description: "No Jira do leme-tec, JQL com status por nome (\"Tarefas pendentes\") retorna 0; verificar board por ID do status"
metadata: 
  node_type: memory
  type: project
  originSessionId: a78cefaf-7387-4e04-b108-b83e591c76d3
  modified: 2026-09-03T16:42:09.349Z
---

No `leme-tec.atlassian.net`, filtrar JQL por nome de status não resolve: `project = LM AND status = "Tarefas pendentes"` retorna **0 resultados** para o projeto inteiro, mesmo com cards nesse status. Trocar pelo ID funciona: `status = 10003` devolve os cards normalmente. Verificado em 03/09/2026 ao criar a LM-2346.

**Why:** o passo de verificação do `/create-jira-card` monta a query com o nome do status. Sem saber disso, o zero-resultado parece "o card não está no board" e viraria um relato falso de falha — exatamente o oposto do que aquele passo existe para evitar.

**How to apply:** ao conferir visibilidade no board 2, use o ID do status, não o nome. IDs conhecidos: `10003` Tarefas pendentes, `10008` Desenvolvendo, `10009` Em andamento (não mapeado em coluna nenhuma). A cláusula `sprint in openSprints()` funciona normal e pode ficar por nome. Ver [[validate-fixes-empirically]].

Cards criados para outra pessoa ficam em **Tarefas pendentes**, não em Desenvolvendo — `10003` é coluna mapeada no board (categoria "Itens Pendentes"), então o card aparece; mover pra Desenvolvendo diria que alguém já está mexendo, o que é [[info-errada-na-tela-e-bug]] aplicado ao board.
