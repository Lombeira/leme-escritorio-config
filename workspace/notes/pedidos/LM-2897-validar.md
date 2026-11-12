---
status: aberto
card: LM-2897
---
# LM-2897: validar

**Preview:** http://192.168.1.173:5301/ (flag `is-mapa-analytics-gestao-enabled` não existe no GrowthBook de homolog: o QA a forçou no navegador; modo análise ligado em `/dashboard/mapa/pedagogical-map`, como diretor/coordenador)

**Branch:** `LM-2897-frontend-analytics-do-mapa-gestao-drawer` (commits `b660a01f`, `bea01e79`, `2f6c50ec`)

## O que foi feito
Drawer da habilidade na visão da gestão: clicar numa célula do mapa de calor abre o drawer com % e nº de questões, abas Turmas (intervalo min–max e lista por professor) e Questões (agrupadas por prova; clicar abre o QuestionPanel ao lado, sempre com `schoolId`, nunca `classId`), estado 404 e eventos Amplitude. Extraídos `QuestionSideBySide` e `QuestionRowButton` (reuso, também usados no drawer do professor).

## QA: 8/8 APROVADO
Detalhes e prints em `.escritorio/cards/LM-2897/qa.md` e `evidencias/`.

## Atenção
- Visão do professor foi tocada pela extração dos componentes; a comparação do QA foi só visual. Confira o passo 8 do `implementacao.md` (lado a lado em ≥992px no drawer do professor não é coberto por teste).
- Eventos levam o id da habilidade/questão (conteúdo), sem aluno nem professor. Se a regra for nenhum id, é só retirar.
- Intervalo arredondado: 49,6% e 50,4% aparecem como "Varia de 50% a 50%".
- Review: READY após 2 voltas; 2 nits em `school-scores.ts` não tratados.
