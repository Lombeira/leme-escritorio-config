---
card: LM-2857
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/867
---
# LM-2857: validar renomeação dos agentes de review

**PR:** https://github.com/leme-tech/leme-app/pull/867 (aberto em 06/11/2026, 23:07)

**Link:** sem preview (card só com critérios não visuais). Validar pelo diff e pelas evidências.
- Worktree: `repos/leme-app/.worktrees/LM-2857`
- Branch: `LM-2857-renomear-agentes-de-review-do-leme-app` @ `512fd945` (só local, sem push)
- Diff: `git -C repos/leme-app/.worktrees/LM-2857 diff -M origin/main`
- Evidências: `.escritorio/cards/LM-2857/evidencias/`

## Implementação (resumo)
- `.claude/agents/leme-code-reviewer.md` virou `reviewer.md` (`name: reviewer`), e `leme-review-validator.md` virou `review-validator.md` (`name: review-validator`). Via `git mv`; no corpo só muda o `name:`.
- Referências atualizadas em `review/SKILL.md` (l. 65, 96, 97), `review/checklist.md` (l. 3, 83, 108) e `review-refresh/SKILL.md` (l. 143).
- Troca só dos nomes exatos com prefixo `leme-`; a palavra "reviewer" no texto ficou intocada. 5 arquivos, todos em `.claude/`.
- Risco: quem rodar `/review` num checkout anterior ao merge não acha os agentes novos (vai na descrição do PR).

## QA (rodada 1): APROVADO

| # | Critério | Resultado |
|---|---|---|
| 1 | `git grep` dos nomes antigos sem nenhuma linha | APROVADO |
| 2 | `.claude/agents` tem só `review-validator.md` e `reviewer.md` | APROVADO |
| 3 | `name:` dos agentes são `reviewer` e `review-validator` | APROVADO |
| 4 | `subagent_type` do `/review` bate com os `name:` (l. 65 e 97) | APROVADO |
| 5 | 3 citações de `reviewer.md` apontam para arquivo existente | APROVADO |
| 6 | Agentes aparecem como rename (99%), corpo só muda no `name:` | APROVADO |
| 7 | Diff só em `.claude/` (5 arquivos) | APROVADO |
