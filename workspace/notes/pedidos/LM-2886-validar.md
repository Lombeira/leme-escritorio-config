---
card: LM-2886
status: fechado
fechado_em: 2026-11-11 18:59 (aprovado)
reaberto_em: 2026-11-11 18:58 (volta da devolução da Feda)
pr: https://github.com/leme-tech/leme-app/pull/882
---
# LM-2886: validar a visão da gestão da escola no Analytics do Mapa (PR 1 de 4), rodada 2

**PR:** https://github.com/leme-tech/leme-app/pull/882

**Link:** http://192.168.1.173:5301/ (ou `ssh -L 5301:localhost:5301 leme@192.168.1.173` e `http://localhost:5301/`). O preview vem do worktree, aponta para homolog e cai ao sair da validação ou em 24 h.
- Para ver a visão da escola: abra `/dashboard/flag-lab` e force `is-mapa-analytics-gestao-enabled` = `[{"id":"<id da escola>","name":"<nome>"}]` (a flag está vazia no GrowthBook). Depois entre como gestão (ou admin sem preview), ligue o modo análise e abra `/dashboard/mapa/pedagogical-map`. O QA usou a "Escola teste da Feda", que tem mapa e provas lidas.
- Para ver as turmas como botões: escola fora da flag (ou professor), sem turma no header; escolha a escola pelos botões da tela.
- Worktree: `repos/leme-app/.worktrees/LM-2886`
- Branch: `LM-2886-frontend-analytics-do-mapa-visao-da` @ `1f46b59f` (5 commits, só local, sem push)
- Diff: `git -C repos/leme-app/.worktrees/LM-2886 diff origin/main...HEAD` (20 arquivos)
- Evidências: `.escritorio/cards/LM-2886/evidencias/` (rodada 2 com prefixo `r2-`). Review: READY na rodada 5 (`.escritorio/cards/LM-2886/review.md`); na rodada 4 houve 1 should-fix de acessibilidade, corrigido. Fica 1 nit opcional (`MapaSchoolsPicker`, `flatMap` + `find` por id).

## O que mudou desde a devolução
Comentário da Feda: cards fora do padrão e desproporcionais; ao escolher a escola pelo botão a tela pedia turma no header, e ela quer as turmas também como botões.
- **Cards da escola no padrão da plataforma:** "Progresso do mapa", "Turmas da escola" e "% de acerto por habilidade" usam a casca dos cards do analytics de Conteúdos (ícone, título e descrição; raio, borda e sombra iguais, medidos pelo QA). Progresso e Turmas ficam lado a lado em duas colunas iguais e com a mesma altura (542x518 px em 1440x900); lista longa rola dentro do card (até 420px) e entra no Tab com anel de foco. O % da turma usa o mesmo selo da visão do professor.
- **Turmas como botões:** quando a tela pede turma, as turmas do ano aparecem como botões, no mesmo visual do picker de escola (que virou o componente genérico `MapaChoicePicker`; a tela de escola ficou igual). A lista e a escolha vêm do mesmo hook do seletor de turma do header (`useClassroomChoice`, extraído do `classroom-menu.tsx`): o header mostra a turma na hora e sai o mesmo `Filter Applied` de turma.
- Verificações do dev: biome, tsc e testes relacionados passando (288 testes em `pedagogical-map-v2`, Menus, picker e Layout, mais 4 novos em `index.class-picker.test.tsx`). Nenhum teste existente mudou. A suíte inteira roda no pre-push.

## O que já vinha da rodada 1 (resumo do implementacao.md)
- Flag `is-mapa-analytics-gestao-enabled`; visão para gestão com modo análise e escola na flag; professor e preview de professor na tela de hoje.
- Progresso com bolinha verde/laranja/vermelha/cinza, turmas do menor para o maior %, mapa de calor sem clique, filtros Ano/Área/Mapa em cascata, estados de carregando, sem mapa, sem respostas e 403, erro de filtro com "Tentar de novo" e "Limpar filtros".
- Eventos `Feature Viewed`, `Filter Applied`, `Empty State Viewed no_data`, sem dado de aluno nem nome de professor.
- Escopo: só o PR 1; LM-2896 (drawers de preenchimento e turma), LM-2897 (drawer da habilidade) e LM-2898 (aba Alunos e toggle) ficam para os próximos cards.

## Resultado do QA (rodada 2): APROVADO

| # | Critério | Resultado |
|---|---|---|
| D1 | Cards no padrão de Conteúdos, proporcionais, lista rola no card, Tab com anel | APROVADO |
| D2 | Turmas como botões depois da escola; clique seleciona no header e segue; `Filter Applied` de turma | APROVADO (admin com escola fora da flag: 16 botões; professor: 3) |
| 1 | Gestão na flag vê os três blocos sem turma | APROVADO (diretor com resposta simulada; admin com dado real) |
| 2 | Escola fora da flag: tela de hoje | APROVADO (mais os botões de turma, pedido da Feda) |
| 3 | Professor: tela de hoje, na flag e fora | APROVADO (idem) |
| 4 | Preview do admin | APROVADO |
| 5 | Trocar escola zera os filtros | APROVADO |
| 6 | Cascata do Ano | APROVADO |
| 7 | Filtros combinados e "Atualizando os resultados…" | APROVADO |
| 8 | Faixas do progresso | APROVADO |
| 9 | "Ainda não feito" | APROVADO |
| 10 | Ordem das turmas | APROVADO |
| 11 | Mapa de calor sem Diagnóstica | APROVADO |
| 12 | Estados vazio, sem mapa e 403 | APROVADO (sem respostas e 403 simulados) |
| 27 | `Feature Viewed` | APROVADO |
| 28 | `Filter Applied` e `Empty State Viewed` | APROVADO |
| 29 | Visão do professor igual | APROVADO (parcial: trilha e "Rota da turma" abrem depois do botão; drawers e questão não percorridos) |
| 30 | `git grep` da flag e do evento | APROVADO |

## O que validar / decidir
1. **Visual novo dos cards da escola** e proporção entre eles (prints `r2-D1-*`).
2. **Dois padrões de card no Mapa:** a escola agora usa a casca de Conteúdos, mas a visão do professor continua no `AnalyticsCard` antigo (raio maior). Igualar o professor ficou fora para não mexer no critério 29; se quiser tudo igual, vira card à parte ou outra volta.
3. **Botões de turma para todo mundo** que cai na tela "Selecione uma turma" (professor e gestão fora da flag), não só para a gestão. Escola com muitas turmas vira grade de 3 colunas, sem busca. Os botões aparecem depois que o header escolhe o ano sozinho; até lá fica o aviso.
4. **Visão do professor com turma escolhida** (critério 29): drawers e questão não foram percorridos pelo QA.
5. Pendentes da rodada 1 que continuam: textos com filtro ativo ("Ainda não há resultados com esses filtros.", "Nenhuma prova do mapa com esses filtros."), % arredondado para baixo (79,9% vira "79%"), `vi.mock` do hook da flag no `index.test.tsx`, dois toasts duplicados no 403, "Limpar filtros" sem `Filter Applied`, falta de conta de diretor com dados em homolog.
