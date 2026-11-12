---
card: LM-2896
status: fechado
fechado_em: 2026-11-11 21:21 (aprovado)
pr: https://github.com/leme-tech/leme-app/pull/884
---
# LM-2896: validar Analytics do Mapa (gestão): drawer de preenchimento e drawer da turma
**PR:** https://github.com/leme-tech/leme-app/pull/884

**Link:** http://192.168.1.173:5301/dashboard/mapa/pedagogical-map (preview do worktree, aponta para homolog; cai ao sair da validação ou em 24 h)
- Worktree: `repos/leme-app/.worktrees/LM-2896`
- Branch: `LM-2896-frontend-analytics-do-mapa-gestao-drawer` @ `ba3833fa` (só local, sem push), 3 commits, 24 arquivos
- Diff: `git -C repos/leme-app/.worktrees/LM-2896 diff -M origin/main...HEAD`
- Evidências: `.escritorio/cards/LM-2896/evidencias/`; QA completo em `.escritorio/cards/LM-2896/qa.md`; review em `.escritorio/cards/LM-2896/review.md`

## Antes de abrir: ligar a flag
A flag `is-mapa-analytics-gestao-enabled` **não existe no GrowthBook de homolog**, então a visão da gestão não aparece sozinha. Logado como ADMIN, com a **Escola teste da Feda** selecionada, rode no console do navegador e a página recarrega com a flag:

```js
localStorage.setItem("leme:gb-overrides", JSON.stringify({ "is-mapa-analytics-gestao-enabled": ["ebac582b-e871-4214-a916-0b38f59360ca"] })); location.reload();
```

Vale só no seu navegador e não grava nada. Para desfazer: `localStorage.removeItem("leme:gb-overrides")`.

## O que foi feito
- **Escopo da questão:** `useMapAnalyticsQuestion` recebe `{ classId }` (turma) ou `{ schoolId, classLevelIds? }` (escola), nunca os dois juntos (o back dá 422).
- **Drawer de preenchimento** (clique numa prova em "Progresso do mapa"): título com a prova, "{x}% dos cartões já lidos na escola", uma linha por turma com % lido e, ao expandir, "Pendente (n)" e "Já leu o cartão (n)" com a etiqueta "Faltou" nos ausentes.
- **Drawer da turma** (clique em "Turmas da escola"): título com a turma, professores no subtítulo, "Turma x%" e "Média da escola y%", "Acertos por prova" com uma barra por prova (filtro local, sem chamada nova) e a lista de questões da mais errada para a menos errada. Clicar numa questão alarga o drawer e abre a questão ao lado (chamada com `classId`, sem `schoolId`).
- **Tracking:** `"class"` entrou em `ENTITY_TYPES`; `trackEntityDetailsViewed` leva só tipo, id da prova/turma/questão e `entry_point`.
- **Volta do review (rodada 1, 3 should-fix):** a questão aberta fecha ao trocar o filtro de prova; reabrir a mesma turma volta limpa (o reset acontece ao abrir, nada pisca ao fechar); `ExamBars`/`Bar` e `QuestionList` saíram para `class-exam-bars.tsx` e `class-question-list.tsx`. Rodada 2: READY.
- Verificações do front-dev: biome, tsc e `vitest related` (51 testes) ok. Suíte inteira roda no pre-push.

## Resultado do QA: APROVADO (16 de 16)

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Clique na prova abre drawer médio, título = prova, subtítulo "x% dos cartões já lidos" | APROVADO | `1-drawer-preenchimento.png` |
| 2 | Uma linha por turma com nome e % lido | APROVADO | `1-drawer-preenchimento.png` |
| 3 | Expandir turma: Pendente (n), Já leu o cartão (n), "Faltou" | APROVADO | `3-turmas-expandidas.png` |
| 4 | Turma sem aluno ativo: "Nenhum aluno ativo nesta turma." | APROVADO (resposta simulada) | `4-turma-sem-aluno-resposta-simulada.png` |
| 5 | Clique na turma: título = turma, subtítulo = professores | APROVADO | `5-6-drawer-turma.png` |
| 6 | Turma x% / Média da escola y%, barras por prova, lista em % crescente | APROVADO | `5-6-drawer-turma.png`, `8-sem-resultados.png` |
| 7 | Questão: prova, nível, %, descritor, enunciado | APROVADO | `5-6-drawer-turma.png` |
| 8 | Prova sem resposta: "Sem resultados ainda" | APROVADO | `8-sem-resultados.png` |
| 9 | Filtro por prova e "Ver todas as provas", sem chamada nova | APROVADO | `9-mostrando-so-a-prova.png`, `9-filtro-por-prova.png` |
| 10 | Questão ao lado (desktop), drawer largo, `classId` sem `schoolId` | APROVADO | `10-questao-lado-a-lado.png` |
| 11 | Mensagens de 403 e 404 | APROVADO (respostas forçadas) | `11a-403-preenchimento.png`, `11b-404-turma.png`, `11c-403-turma.png` |
| 12 | Fecham no X e fora; 360 px em tela cheia; alvos >= 40 px | APROVADO | `12-mobile-preenchimento.png`, `12-mobile-turma.png` |
| 13 | Regressão do professor: habilidade e questão só com `classId` | APROVADO | `13-prof-habilidade.png`, `13-prof-questao.png` |
| 14 | Tracking sem dado de aluno/professor | APROVADO | `14-tracking.txt` |
| 15 | `"class"` em `ENTITY_TYPES` | APROVADO | `15-entity-type.txt` |
| 16 | Escopo nunca manda `classId` e `schoolId` juntos | APROVADO | `16-scope.txt` |

## O que validar
1. **Drawer de preenchimento:** em "Progresso do mapa", clique numa prova com leitura parcial (ex.: "Leitura e Escrita · Nível Basilar · 1º Ano", 54%). Confira o % do subtítulo contra a linha, as cores das turmas e a lista expandida.
2. **Drawer da turma:** em "Turmas da escola", abra o 3º Ano B. Confira os números, as barras, a ordem das questões e o filtro por prova (o "Mostrando só a prova" e o "Ver todas").
3. **Questão ao lado:** clique numa questão, veja o drawer alargar, troque o filtro de prova (a questão tem que fechar), feche e reabra a mesma turma (tem que voltar limpa).
4. **Celular (360 px):** os dois drawers em tela cheia.

## Ressalvas
- Critérios 4 e 11 foram provados com resposta alterada no navegador (não há turma vazia nem turma de outra escola acessível em homolog). Está provado que a tela mostra as mensagens, não o comportamento do back.
- Para a regressão do professor, o QA usou a Escola teste da Feda (a Faino está no Mapa V1).
- Nits do review que ficaram de fora (opcionais): prop `empty` do `StudentGroup` (`attendance-drawer.tsx:142`) poderia ser `emptyMessage`; a linha da questão repete o hover/foco do `ROW_BUTTON_STYLE`; falta um `getQuestionExamKey` ao lado do `getExamKey`.
- O comentário de `ENTITY_TYPES` diz "Nunca o id dela", mas o `entity_id` já carrega ids de prova, turma e questão (padrão anterior). Não há id de aluno ou professor.
