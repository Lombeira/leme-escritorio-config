---
card: LM-2806
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/873
fechado_em: 2026-11-07 12:16 (aprovado)
---
# LM-2806: validar Relatório de Faltas abrindo no mês e ano atuais
**PR:** https://github.com/leme-tech/leme-app/pull/873

**Link:** http://192.168.1.173:5301/ (preview do worktree, aponta para homolog; cai ao sair da validação ou em 24 h). Abra Turmas, escolha uma escola e clique em "Relatório de Faltas"; ou Frequência com `?analytics=1`.
- Worktree: `repos/leme-app/.worktrees/LM-2806`
- Branch: `LM-2806-frontend-relatorio-de-faltas-mes-e-ano` @ `65925303` (só local, sem push)
- Diff: `git -C repos/leme-app/.worktrees/LM-2806 diff origin/main...HEAD`
- Review (rodada 1): READY, sem achados. `.escritorio/cards/LM-2806/review.md`
- Evidências: `.escritorio/cards/LM-2806/evidencias/` (`dbg.png` e `2-frequencia-antes.png` são de depuração, ignorar)
- Escola de teste com vários anos letivos: ZEZE SALLES PROFA EMEF (2024, 2025, 2026)

## O que validar
1. Modal abre em Novembro / 2026 (mês e ano atuais), não mais em Setembro / 2025, em Turmas e em Frequência (análise).
2. Com o ano letivo do topo em 2025, o Ano vem 2025 e o Mês continua Novembro. **Premissa a confirmar:** o card não define a regra; se o PO preferir outro mês (ex.: último mês do ano letivo), muda só uma linha.
3. Trocar mês/ano e gerar manda os valores escolhidos; cancelar e reabrir volta ao padrão.

## Resumo da implementação
`src/components/AbsenceReportModal/index.tsx`: saíram `useState(9)` e `useState(2025)`. O estado guarda só a escolha do usuário (`monthOverride`, `yearOverride`), e o valor exibido/enviado é derivado a cada render: `mês = escolha ?? mês corrente`, `ano = escolha ?? ano letivo do topo ?? ano corrente`. Derivar em render cobre o ano do topo que chega depois da montagem (a URL traz só o id). Abrir o modal zera a escolha anterior.
Teste novo `index.test.tsx` com relógio falso (5 casos; 4 falham contra o código antigo). Biome, tsc e testes relacionados passaram (Node 24).

Fora do escopo, anotado: apagar o campo Ano envia `year=0` (já acontecia); `MONTHS` local duplica `@constants/months` (formato "09" diferente, mexeria no evento de analytics).

## QA (rodada 1): APROVADO
| # | Critério | Resultado | O que apareceu |
|---|---|---|---|
| 1 | Turmas, "Por Mês" | APROVADO | Novembro / 2026 |
| 2 | Frequência (análise) | APROVADO | Novembro / 2026 |
| 3 | Ano do topo 2025 | APROVADO | Novembro / 2025, `month=11&year=2025` |
| 4 | Gerar sem mexer | APROVADO | `month=11&year=2026` |
| 5 | Março / 2024 | APROVADO | `month=3&year=2024` |
| 6 | Cancelar e reabrir | APROVADO | volta a Novembro / 2026 |
| 7 | Celular 390px | APROVADO | mesmos valores e requisições |
| 8 | `git grep` dos valores fixos | APROVADO | nenhuma linha |

Sem erro de console. Nenhum dado criado em homolog. Obs. lateral do QA (não relacionada): o seletor de escola do ADMIN não lista a "Escola Municipal Faino", que existe na API.
