---
card: LM-2822
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/878
fechado_em: 2026-11-10 15:19 (aprovado)
---
# LM-2822: validar a pergunta de troca do professor nas demais aulas da turma e disciplina

**PR:** https://github.com/leme-tech/leme-app/pull/878

**Link:** http://192.168.1.173:5302/ → Grade horária, visão por turma. É o preview do worktree com a API de homolog e cai quando o card sai da validação ou depois de 24 h. O QA usou a escola Tunada da Feda, turma 2º Ano A - Manhã.
- Worktree: `repos/leme-app/.worktrees/LM-2822`
- Branch: `LM-2822-frontend-grade-horaria-ao-trocar-o` @ `c0afe631`, só local e sem push
- Diff: `git -C repos/leme-app/.worktrees/LM-2822 diff origin/main`
- Evidências: `.escritorio/cards/LM-2822/evidencias/`
- Review: READY na rodada 2. A rodada 1 pediu 2 should-fix (toast duplo e try aninhado), corrigidos. Restam 3 nits (`.escritorio/cards/LM-2822/review.md`)
- Backend: a rota `PUT v2/classes/{classId}/subjects/{subjectId}/teacher` veio do LM-2808 (o LM-2823 foi marcado como duplicata) e já está em homolog: deu 200 e 422 no QA

## O que mudou
Na visão por turma, quando a edição de uma aula troca o professor, "Salvar alterações" abre um `ConfirmationModal` antes de salvar. O título é "Trocar o professor nas demais aulas?" e a descrição é "Deseja trocar de {antigo} para {novo} também nas outras aulas de {disciplina} desta turma?". O texto foi ajustado pelo dev para não afirmar que existem outras aulas, já que o front não sabe disso.
- **"Só esta aula":** faz o PUT de sempre e fecha o drawer.
- **"Trocar em todas":** chama a rota de troca em lote com `{ fromTeacherId, toTeacherId }`. Se outro campo também mudou, salva antes a aula com o professor antigo (sem toast) e faz o lote por último. O drawer só fecha se tudo der certo. No erro aparece só o toast do servidor e o drawer fica aberto.
- **X ou Esc:** não salvam nada.
- **Sem diálogo:** criação de aula, visão por professor e edição sem troca de professor.

Para separar "Só esta aula" de fechar, o `ConfirmationModal` compartilhado ganhou uma prop opcional `onCancel`. Os usos atuais não mudam. A mutation de update ganhou `silent` para não mostrar o toast de sucesso.

## QA: APROVADO (9 de 9)
| # | Critério | Resultado |
|---|---|---|
| 1 | Trocar só o professor abre o diálogo com "Só esta aula" e "Trocar em todas" | APROVADO |
| 2 | "Trocar em todas" sem conflito troca todas as aulas de A para B e persiste após recarregar | APROVADO |
| 3 | Aula de um terceiro professor C continua com C | APROVADO |
| 4 | "Só esta aula" troca só a aula aberta | APROVADO |
| 5 | X ou Esc não salvam e o drawer fica aberto com o professor escolhido | APROVADO |
| 6 | Conflito do B em outra turma: toast do servidor, nada muda, drawer aberto | APROVADO |
| 7 | Alterar só o horário salva direto, sem diálogo | APROVADO |
| 8 | Visão por professor: nenhum diálogo | APROVADO com ressalva: nessa visão, clicar numa aula não abre o drawer (já era assim). O QA testou só "Nova aula" com o professor travado, e a edição está coberta por teste unitário |
| 9 | "Nova aula" com professor salva direto | APROVADO |

Massa criada pelo QA na turma 2º Ano A: as aulas de Arte ficaram todas com o Fábio Moreira, a Educação Física de terça 07:00 também, e a Língua Portuguesa de quinta começa às 07:05. Os IDs estão no `qa.md`.

## O que validar
1. Na grade da turma, abrir uma aula, trocar só o professor e salvar. Conferir se o texto e os botões do diálogo estão bons.
2. "Trocar em todas": todas as aulas daquela disciplina com o professor antigo passam para o novo, e as de outro professor ficam como estavam.
3. "Só esta aula": só a aula aberta muda.
4. Trocar o professor e o horário juntos e escolher "Trocar em todas": deve aparecer um toast só.
5. Fechar o diálogo com X ou Esc: nada é salvo.

## Pontos de atenção
- **Não atômico:** com outro campo alterado e "Trocar em todas", se o PUT da aula passar e o lote falhar (ex.: conflito no novo horário), a aula fica com os outros campos salvos e o professor antigo. A triagem já previa isso. Numa nova tentativa, o PUT se repete com os mesmos dados (nit ERR-03, vale citar no PR).
- **Pergunta sempre:** o diálogo aparece mesmo quando a turma não tem outras aulas daquela disciplina, porque o front não tem essa contagem.
- **Cache já existente:** o PUT de "Só esta aula" (fluxo antigo) não invalida a grade por professor. Ficou fora do escopo.
