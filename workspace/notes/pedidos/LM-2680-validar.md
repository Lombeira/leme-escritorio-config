---
card: LM-2680
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/869
---
# LM-2680: validar status do aluno que saiu da turma em Agendamentos e na Frequência do AEE

**PR:** https://github.com/leme-tech/leme-app/pull/869

**Link:** http://192.168.1.173:5301/ (preview na rede de casa, cai ao sair da validação ou após 24 h)

> **Atenção: o login no preview deve dar 404.** O worktree não tem `.env` (só `.env.example`), então o Vite sobe com `VITE_APP_LEME_API_URL` indefinido e o `POST /auth/login` sai fora do proxy `/api`. O QA só conseguiu testar porque reescreveu as chamadas no navegador (`qa-scripts/browser.mjs`). O código do card não tem nada a ver com isso; é falha do `esteira-preview`/worktree. Se não der para logar, valide pelas evidências e pelo diff, ou rode o worktree em localhost com o seu `.env` + `ssh -L`.

- Worktree: `repos/leme-app/.worktrees/LM-2680`
- Branch: `LM-2680-aee-mostrar-o-status-do-aluno` @ `1beead18` (só local, sem push)
- Diff: `git -C repos/leme-app/.worktrees/LM-2680 diff -M origin/main`
- Evidências: `.escritorio/cards/LM-2680/evidencias/`
- Massa em homolog: escola "Tunada da Feda", turma "1º Ano AEE A - Manhã". Dalila Xavier (Remanejado), Antônio Batista (Abandono), Yuri Carvalho Jr. (Ativo). Frequência em 06/11/2026.

## O que mudou (resumo do implementacao.md)

- **Agendamentos** (`src/pages/timetable/special-education/index.tsx`): quem saiu da turma (qualquer status fora de Ativo/Aprovado, via `hasLeftTheClass`; status nulo continua ativo) fica com a linha acinzentada, igual à Frequência regular, com o status ao lado do nome e a coluna fixa do nome também cinza. Tooltip: "<Nome> saiu da turma (<Status>). Não é possível adicionar atendimento." Sem "+" nas células, atendimentos só para consulta (não abrem edição), fora do select de "Novo atendimento" (que fica desabilitado se não houver aluno ativo). No celular: card cinza, "Status · N atendimentos", sem "Adicionar atendimento".
- **Frequência AEE** (`src/pages/frequency/special-education/index.tsx`): saiu o `TRANSFERRED_STATUS` e o "transferido" fixo (errado para Remanejado). A linha fica cinza, com tooltip "O status desse estudante é: X", a coluna Falta mostra o status real e a contagem ignora essas linhas.
- **Compartilhado** (`src/components/Table/mobile-card-list.tsx`): props opcionais `isMuted`/`mutedBg`; sem elas, nada muda nas outras telas.
- 10 testes novos (5 por tela).

## Resultado do QA (rodada 1): APROVADO

| # | Critério | Resultado |
|---|---|---|
| 1 | Agenda desktop: linha acinzentada igual à Frequência regular, status ao lado do nome | APROVADO |
| 2 | Sem "+" para quem saiu; "+" mantido no Ativo | APROVADO |
| 3 | Tooltip com o motivo | APROVADO |
| 4 | "Novo atendimento": quem saiu fora do select | APROVADO |
| 5 | Atendimentos de quem saiu só para consulta; Ativo abre drawer | APROVADO |
| 6 | Celular: card acinzentado, com status, sem "Adicionar atendimento" | APROVADO |
| 7 | Frequência: linha cinza, status no lugar do checkbox, fora da contagem | APROVADO |
| 8 | Outro status de saída (Abandono) igual; Ativo com checkbox | APROVADO (caso Aprovado não visto no navegador, sem massa) |
| 9 | Ativo: nada muda | APROVADO |
| 10 | De volta a Ativo: sinalização some | APROVADO, **simulado** (o produto não tem caminho para reativar; status reescrito só nas respostas da API) |
| 11 | Sem `TRANSFERRED_STATUS` | APROVADO |
| 12 | Helpers compartilhados nas duas pastas | APROVADO |
| 13 | biome, tsc, knip e test (408 arquivos, 3355 testes, Node 24) | APROVADO |

## O que validar

- O cinza da coluna fixa do nome ao rolar de lado e o contraste do status no tema escuro (o jsdom não calcula layout).
- O texto do tooltip da agenda (proposta da triagem, pode ser ajustado).
- Se o critério 10 simulado é suficiente.

## Observações

- Avisos `validateDOMNesting` no celular já existiam antes do commit (estrutura igual no `HEAD~1`).
- Massa criada em homolog não é reversível (matrículas do AEE A ficam como estão).
- Risco para o PR: quando o LM-2679 (backend) encerrar as recorrências futuras de quem saiu, a agenda pode parar de mostrar esses atendimentos e o critério 5 passa a depender do back.

## Proposta para o Jira (só com seu OK; nada foi escrito)

Comentário opcional no LM-2680: "Front pronto para homolog: aluno que saiu da turma aparece acinzentado com o status em Agendamentos e na Frequência do AEE, sem ações. Não há fluxo no produto para reativar aluno; se for desejado, vale card próprio."
