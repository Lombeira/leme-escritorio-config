---
name: permissionrequest-hook-comportamento
description: "Como o hook PermissionRequest do Claude Code se comporta de verdade (testado em 06/11/2026, v2.1.319): corre em paralelo com a pergunta do terminal, dispara no claude -p, e CLAUDE_CODE_SESSION_ATTENDED separa interativo de headless"
metadata:
  type: reference
---

Medido no workspace com o hook `.claude/hooks/permissao.py` (aprovação pelo escritório). A
documentação não cobre estes pontos:

- **Interativo:** a pergunta aparece no terminal **ao mesmo tempo** que o hook roda. Vale a
  primeira resposta (terminal ou escritório); o terminal não fica travado esperando o hook.
- **`claude -p`:** o `PermissionRequest` **dispara** quando a ferramenta não está no
  `allowedTools`. Hook que sai sem decisão = negado (não há humano).
- **Detectar o modo:** `CLAUDE_CODE_SESSION_ATTENDED=1` e `CLAUDE_CODE_ENTRYPOINT=cli` no
  interativo; `0` e `sdk-cli` no `claude -p`. A doc não lista essas variáveis.
- **Entrada:** sem `tool_use_id`; tem `session_id`, `cwd`, `tool_name`, `tool_input`,
  `permission_suggestions`.

**Why:** a doc só descreve a corrida "quem decide primeiro" para o `canUseTool` do SDK; sem o
teste, a suposição natural seria limitar a espera do hook no interativo para não travar o
terminal, o que era desnecessário.

**How to apply:** ao mexer em hooks de permissão, não reduzir o timeout do interativo por
medo de travar o terminal. Se a versão do Claude Code mudar muito, refazer o teste. Ver
[[validate-fixes-empirically]].
