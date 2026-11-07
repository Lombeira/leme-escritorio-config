---
card: LM-2859
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/875
fechado_em: 2026-11-07 13:48 (aprovado)
---
# LM-2859: validar Security Audit do PR bloqueando a partir de severidade baixa

**PR:** https://github.com/leme-tech/leme-app/pull/875

**Link:** sem preview (card só com critérios não visuais; validar pelo diff e pelas evidências)
- Worktree: `repos/leme-app/.worktrees/LM-2859`
- Branch: `LM-2859-frontend-pipeline-do-pr-nao-bloqueia-com` @ `5a170be4` (só local, sem push)
- Diff: `git -C repos/leme-app/.worktrees/LM-2859 diff origin/main...HEAD`
- Evidências: `.escritorio/cards/LM-2859/evidencias/`
- Review: READY, sem achados (`.escritorio/cards/LM-2859/review.md`)

## O que mudou
- `.github/workflows/ci.yml`: job `audit` (`name: Security Audit`, mantido para não quebrar o check obrigatório) passa de `pnpm audit --prod --audit-level=critical` para `--audit-level=low`; step renomeado para `pnpm audit (prod, low)`.
- `.github/workflows/security-audit.yml` (relatório semanal): de `--audit-level=high` para `--audit-level=low`; job e step renomeados para `pnpm audit (prod, low)`.
- `--prod` mantido: dependências de desenvolvimento continuam fora (a triagem assumiu isso; se quiser incluir, devolva o card).

## Riscos
- Qualquer advisory novo de severidade baixa numa dependência de produção reprova todos os PRs até alguém atualizar a dependência. É o pedido, mas vale o time saber.
- O job semanal mudou de nome; só roda por cron/dispatch, mas filtro ou alerta pelo nome antigo precisaria de ajuste.
- Tornar `Security Audit` obrigatório na proteção da `main` é configuração do GitHub, fora do repo: fica para você conferir nas settings.

## QA (rodada 1): APROVADO

| # | Critério | Resultado | Observação |
|---|---|---|---|
| 1 | ci.yml sem `critical`; job roda `--audit-level=low` | APROVADO | ci.yml:156 com `low`; grep por critical sem resultado |
| 2 | security-audit.yml com `low`; name do job/step sem high/critical | APROVADO | job e step `pnpm audit (prod, low)` |
| 3 | `pnpm audit --prod --audit-level=low` sai 0 | APROVADO | "No known vulnerabilities found", exit=0 |
| 4 | diff só em `.github/workflows/`; job continua `Security Audit` | APROVADO | 2 arquivos; ci.yml:140 `name: Security Audit` |
