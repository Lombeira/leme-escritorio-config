---
card: LM-2801
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/879
fechado_em: 2026-11-10 16:32 (aprovado)
---
# LM-2801: validar "Como calculamos?" nos números da análise de frequência

**PR:** https://github.com/leme-tech/leme-app/pull/879

**Link:** http://192.168.1.173:5301/dashboard/frequency (preview do worktree, aponta para homolog; cai ao sair da validação ou em 24 h). Ligar o modo análise.
- Worktree: `repos/leme-app/.worktrees/LM-2801`
- Branch: `LM-2801-frontend-como-calculamos-explicar-a` @ `46b539f7` (só local, sem push)
- Diff: `git -C repos/leme-app/.worktrees/LM-2801 diff origin/main...HEAD`
- Evidências: `.escritorio/cards/LM-2801/evidencias/`; QA em `.escritorio/cards/LM-2801/qa.md`; review em `.escritorio/cards/LM-2801/review.md`
- Turma com dado: "1º Ano A - Manhã" da Escola teste da Feda (faltas só no 2º Semestre, em Arte).

## O que foi feito (resumo do implementacao.md)
- Botão "Como calculamos?" ao lado dos títulos "Faltas por aluno" e "Evolução temporal de faltas", que abre um popover (Chakra) com título, até 4 linhas e o botão "Entendi" em largura total.
- Textos montados por uma função pura (`src/pages/frequency/analytics-explanations.ts`), que varia com Dias/Aulas, matéria ou todas, período ou ano letivo, professor ou gestão, e Período/Mês na média da turma.
- `ChartWrapper` ganhou a prop opcional `titleAction`. Sem a prop, as outras telas ficam iguais.
- Dois `feature_name` novos no tracking plan (`frequency_explanation_absences_per_student`, `frequency_explanation_class_average`), com `Feature Viewed` ao abrir.
- Review: 2 rodadas. Na 1ª saiu um should-fix (o número mágico `1000` no lugar de `ALL_SUBJECTS_OPTION.id`), que foi corrigido. Ficaram 4 nits opcionais em `review.md`.

## Quadro do QA (APROVADO)
| # | Critério | Resultado |
|---|---|---|
| 1 | "Faltas por aluno", Dias, matéria e período: título e 4 linhas, datas dd/mm | APROVADO |
| 2 | Aulas: "contam 3 aulas" | APROVADO |
| 3 | Troca de período; "Todos os períodos" vira "no ano letivo" | APROVADO |
| 4 | "Todas as Matérias" vira "em todas as matérias" | APROVADO |
| 5 | Professor: "nas suas aulas de Arte" / "nas suas aulas"; gestão nunca vê "suas aulas" | APROVADO (2ª rodada, com dado criado) |
| 6 | "Evolução temporal de faltas": média da turma com Período/Mês e Dias/Aulas | APROVADO |
| 7 | Celular 390x844: "Entendi" 286x40 px, fecha pelo botão e ao tocar fora | APROVADO |
| 8 | Sem botão em "Dias com falta", vídeos e turma sem faltas; sem termos proibidos | APROVADO |
| 9 | Outra tela com `ChartWrapper` (Mapa V2) sem botão | APROVADO (layout só a olho) |
| 10 | `git grep` de termos proibidos vazio | APROVADO |
| 11 | Feature names em `FEATURE_NAMES` e `FEATURE_LABELS` | APROVADO |

## Pontos para você olhar
1. **Data ausente na primeira abertura:** com Dias e Todas as Matérias, logo ao abrir, a linha vem sem "de dd/mm a dd/mm", porque o período veio da URL só com o id. As datas aparecem depois de escolher uma matéria ou trocar para Aulas. Não aparece "undefined". O QA tratou isso como esperado (é o tratamento de risco da triagem), mas vale ver se te incomoda.
2. **Visual do popover no celular:** o QA mediu o botão, mas a aparência contra o CSSReset e o Tailwind é com você.
3. **Mapa V2 / analytics do mapa:** confirmar que o cabeçalho dos gráficos não mudou.
4. Amplitude (`Feature Viewed`) não foi testado pelo QA (não era critério).

## Dado de teste criado em homolog
O QA lançou uma falta em Arte para Levi Ackerman Guerra Lomenha em 10/11/2026, na turma 1º Ano A - Manhã da Escola teste da Feda, como PROFESSOR. Dá para desfazer com `absent:false` (script em `.escritorio/cards/LM-2801/qa-scripts/falta.mjs`).

## Jira (proposta, só com o seu OK)
- O LM-2789 continua ligado como Blocks ao LM-2801, mas a descrição do card diz que não depende dele. Sugestão: remover o vínculo ou comentar no card: "O LM-2801 não depende do LM-2789: a presença por exceção já é a regra atual e o alerta de frequência esquecida não muda nenhuma conta."
