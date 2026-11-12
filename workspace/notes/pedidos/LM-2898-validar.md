---
card: LM-2898
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/883
fechado_em: 2026-11-11 19:54 (aprovado)
preview: http://192.168.1.173:5301/
branch: LM-2898-frontend-analytics-do-mapa-gestao-aba
---

# LM-2898: validar aba Alunos e drawer do aluno (Analytics do Mapa, gestão)

**PR:** https://github.com/leme-tech/leme-app/pull/883

**Preview:** http://192.168.1.173:5301/ (homolog; cai ao sair da validação ou em 24 h)

Re-triagem depois que a flag de impedimento saiu: o LM-2886 (PR #882) já está na main, então o card ficou VIÁVEL.

## O que foi feito

Commits `72568dd0`, `54961868` e `47a43c29` na branch do card, ainda sem push.

- **Toggle "Turmas | Alunos"** (novo) no canto direito da barra de filtros da visão da escola. A aba Alunos mostra o card "Alunos da escola" com a turma em cada linha, o resumo (média da escola, abaixo de 50%, sem presença) e a busca por nome.
- **Ordem da lista:** do menor para o maior % de acerto. Quem não tem resposta vai para o fim, depois de "Sem resultados ainda".
- **Mapa de calor:** é o mesmo nas duas abas. Trocar de aba não chama de novo o endpoint de visão geral, só `learning-maps/students`.
- **Drawer do aluno** (`school-student-drawer.tsx`, à parte do drawer do professor porque o endpoint 6 não permite escolher provas): mostra "Aluno × turma", "Faltou" (`present: false`), "Cartão não lido" (`present: null`) e "Acertou x de y" nos descritores. Tem textos próprios para 403 e 404.
- **Medição:** `Tab Selected` e `Entity Details Viewed` (`entity_type: student`), sem id, nome, turma ou % do aluno. Um teste garante isso.
- **Professor:** `StudentListCard` recebe os textos por prop. Os blocos do `StudentDrawer` foram extraídos para reaproveitar, sem mudar o comportamento, e um teste de regressão do professor passa.
- **Contrato com o core:** o drawer não manda `schoolId` nem ano, e o nome da turma com ano ("1º ano A") vem das turmas do endpoint principal.
- **Review** (3 rodadas, `cards/LM-2898/review.md`): saiu READY.
  - Corrigido: um refetch que falha não troca mais a lista nem o drawer pela mensagem de erro.
  - Corrigido: "Faltou" e "Cartão não lido" agora vêm de um `status`, não da comparação de texto.
  - Ficaram nits sem bloqueio: textos repetidos, um ternário no `emptyMessage` e o cast de `statusCode`.

## QA: APROVADO (desktop 1440x900, admin na Escola teste da Feda)

| # | Critério | Resultado | Observação |
|---|---|---|---|
| 1 | Toggle Alunos: card, turma por linha, resumo, busca; Turmas volta | APROVADO | Média 57%, abaixo de 50%: 35 de 91, sem presença 0 |
| 2 | `answers = 0` no fim com "Sem resultados ainda"; ordem crescente | APROVADO | Homolog não tem aluno com 0; 3 zerados por mock |
| 3 | Busca filtra sem mudar a ordem | APROVADO | "cenário 2b" mostra os 6 alunos, em ordem |
| 4 | Heatmap igual; toggle não refaz a visão geral | APROVADO | Só `learning-maps/students` ao reentrar em Alunos |
| 5 | Ano, Área, Mapa mantêm o mesmo recorte | APROVADO | Mesmos `classLevelIds`/`knowledgeGroupIds`/`learningMapIds` |
| 6 | Drawer "Aluno × turma" com % de `class` | APROVADO | Turma 55% = 565/1026 |
| 7 | Faltou, Cartão não lido, "Acertou x de y" | APROVADO | Bate com `present` e `correct`/`questions` |
| 8 | 403 e 404 do detalhe | APROVADO | Por mock, com o corpo real do core |
| 9 | Eventos sem dado de aluno | APROVADO | Pelo console (preview sem chave do Amplitude) |
| 10 | Professor igual ao de hoje | APROVADO | Fernanda, 1º Ano A, trilha Teste da Feda |

Prints em `~/workspace/.escritorio/cards/LM-2898/evidencias/`.

## O que validar no browser

1. Admin numa escola com Mapa, modo análise: alternar Turmas/Alunos, buscar e abrir um aluno.
2. No drawer: "Aluno × turma", "Faltou" e "Cartão não lido" por prova, "Acertou x de y".
3. Como professor: a lista e o drawer continuam iguais aos de hoje.

## Pontos de atenção

- **Flag:** `is-mapa-analytics-gestao-enabled` não existe no GrowthBook de homolog. O QA forçou a flag por override só no navegador. Para ver a tela no preview, alguém precisa criar a flag e incluir a escola, ou usar o mesmo override.
- **Visual:** o card "Alunos da escola" usa a casca do card do professor (título maior). Ele fica diferente dos outros cards da tela da escola, e não mexi para não alterar o professor.
- **Texto:** a aba Habilidades do drawer reaproveita "provas selecionadas na página", do professor. Na escola o recorte vem de Ano, Área e Mapa. Não é falso, mas pode ganhar texto próprio.
- **Refetch:** quando um refetch falha com dados na tela, nada avisa que eles podem estar desatualizados. Seria uma mudança à parte.
