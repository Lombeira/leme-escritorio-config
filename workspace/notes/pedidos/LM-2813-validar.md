---
card: LM-2813
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/871
fechado_em: 2026-11-07 11:15 (aprovado)
---
# LM-2813: validar o tooltip do descritor nos resultados do mapa
**PR:** https://github.com/leme-tech/leme-app/pull/871

**Link:** http://192.168.1.173:5301/ → Mapa de aprendizagem, gaveta de resultados de uma avaliação, aba "Resultados". É o preview do worktree com a API de homolog e cai quando o card sai da validação ou depois de 24 h. O QA usou a Escola teste da Feda, turma 5º Ano A - Manhã, diagnóstica de Língua Portuguesa.
- Worktree: `repos/leme-app/.worktrees/LM-2813`
- Branch: `LM-2813-frontend-tolltip-no-resultado-do-mapa` @ `c995dbf6`, só local e sem push
- Diff: `git -C repos/leme-app/.worktrees/LM-2813 diff origin/main`
- Evidências: `.escritorio/cards/LM-2813/evidencias/`
- Review: READY na rodada 1, sem achados (`.escritorio/cards/LM-2813/review.md`)

## O que mudou
No cabeçalho da tabela de resultados, o código do descritor (a linha abaixo de Q1, Q2, ...) ganhou um `Tooltip` do Chakra com a descrição completa. Ele segue o padrão do `descriptor-card` e usa o `TOOLTIP_KEEP_IN_VIEWPORT` que o projeto já tem, para não esticar o documento nas colunas da ponta. Sem descritor, a célula continua com "—" e sem tooltip. Com descrição vazia, nenhum balão aparece. Foram 3 testes novos em `evaluations-results-drawer.test.tsx`.

## O que validar
1. Passar o mouse no código do descritor de Q1: a descrição completa aparece depois de uns 200 ms e some quando o mouse sai.
2. Fazer o mesmo em Q1 e depois em Q2: cada coluna mostra a descrição da própria questão.
3. Rolar a tabela na horizontal (é mais fácil numa janela estreita) e passar o mouse na primeira e na última coluna: o balão tem que aparecer inteiro, sem barra de scroll extra na página.
4. O tooltip do cartão de descritor no painel lateral continua igual.

## Resultado do QA: APROVADO

| # | Critério | Resultado | Observação |
|---|---|---|---|
| 1 | Hover mostra a descrição e some ao tirar o mouse | APROVADO | Q1: "Inferir informações implícitas em textos." |
| 2 | Cada coluna mostra a própria descrição | APROVADO | Q2: "Identificar a ideia central do texto." |
| 3 | "—" sem tooltip | APROVADO | Homolog não tem questão sem descritor, então o QA simulou isso interceptando a resposta da API. |
| 4 | Ponta da tabela rolada: balão inteiro, sem scroll extra | APROVADO | Em 600x800, o balão ficou dentro da janela e o documento continuou com 600x800. Ele cobre só o rótulo "Qn" do cabeçalho e não cobre a primeira linha de alunos. |
| 5 | Tooltip do cartão existente sem regressão | APROVADO | Cartão do painel lateral (DescriptorCard). |

## Fora do escopo (anotado pela triagem e pela implementação)
- O mesmo padrão sem tooltip aparece em `student-answers-drawer.tsx` (v1/v2) e em `evaluation-diagnosis/scenes.tsx`. Se quiser cobrir esses lugares, dá para abrir outro card.
- O código do descritor não recebe foco pelo teclado nem abre no toque, igual ao cartão que já existia.
