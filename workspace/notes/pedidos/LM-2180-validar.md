---
card: LM-2180
status: fechado
fechado_em: 2026-11-07 11:49 (aprovado)
pr: https://github.com/leme-tech/leme-app/pull/872
rodada: 2 (depois da devolução de 07/11 11:15)
---
# LM-2180: validar o PDF de conteúdos no layout do exemplo

**PR:** https://github.com/leme-tech/leme-app/pull/872

**Link:** http://192.168.1.173:5301/dashboard/contents, aba Análises. É o preview do worktree com a API de homolog; cai quando o card sai da validação ou depois de 24 h.
- Worktree: `repos/leme-app/.worktrees/LM-2180`
- Branch: `LM-2180-imprimir-conteudos-por-periodo-pdf` @ `823fda66`, só local e sem push
- Diff: `git -C repos/leme-app/.worktrees/LM-2180 diff -M origin/main`
- Lado a lado do exemplo com o PDF gerado: `.escritorio/cards/LM-2180/evidencias/9-lado-a-lado-exemplo-x-pdf.png`
- PDFs gerados pelo QA: `.escritorio/cards/LM-2180/evidencias/pdfs/`

## O que validar (foco na devolução)
Você devolveu pedindo que o PDF ficasse parecido com o exemplo do card. O front usou como referência o `anexos/conteudo-pdf-exemplo.pdf`. O mock PNG não foi baixado, então ninguém o comparou.
1. **Header:** título "Conteúdos lançados" em negrito; embaixo, Escola e Turma numa linha e Disciplina e Período na outra, fechando com uma linha escura. Não tem logo nem assinatura, porque o exemplo também não tem.
2. **Dias:** cada um numa faixa cinza ("Seg, 04/11/2024").
3. **Conteúdo:** barra cinza à esquerda. A disciplina aparece numa etiqueta cinza, só em "Todas as disciplinas". Depois vêm o título em negrito, "Prof. Nome" em cinza escuro e as habilidades BNCC em etiquetas com borda.
4. **Rodapé:** uma linha e, à direita, "Gerado em dd/MM/yyyy HH:mm · Página N de T".
5. **Diferenças conhecidas em relação ao exemplo** (decida se alguma importa):
   - Não sai "(substituto)" ao lado do professor, porque a API de conteúdos não informa isso. Para sair, precisa de um campo novo no backend.
   - Dentro do dia, a ordem é por disciplina e depois por data de criação. No exemplo, Matemática vem antes de Língua Portuguesa.
   - A fonte é Helvetica, a padrão do gerador. O exemplo usa Arial.
   - Na turma da NILVA (2024), os códigos BNCC vêm só no texto da descrição, sem o campo estruturado, e por isso as etiquetas não aparecem. Na Escola teste da Feda elas aparecem.
6. O modal não mudou. O que você já viu na rodada anterior continua valendo: botão desabilitado sem turma, a janela trava durante a geração, período vazio mostra aviso.

Dados que o QA usou: o DIRETOR na escola NILVA CAZETO KFOURI, turma "6º Ano A - Manhã", nov/2024. A PROFESSORA na Escola teste da Feda, turma A, ago a nov/2026.

## Implementação (resumo desta volta)
- `contents-pdf.ts`: o layout foi refeito seguindo o exemplo. As cores e medidas foram tiradas do próprio PDF de exemplo, rasterizado. Dados, ordem, paginação e nome do arquivo não mudaram (commit `f8a088e9`).
- Correção do review (`823fda66`): a faixa do dia não fica mais sozinha no pé da página. A reserva de espaço agora é uma constante compartilhada, e um teste novo varre 93 alturas de página (ele falhava antes do fix).
- Os riscos da rodada anterior continuam: emoji some do PDF; não há limite de período (LM-2820); pode haver conflito com o LM-2785 em `analytics-view.tsx`; e o ORDER BY do `searchByClass` no core não inclui `classrooms.subject_id`, o que pede um card de backend (se quiser, eu escrevo o texto).

## Review: READY (rodada 4)
- **Rodada 3** (layout novo): 1 should-fix, a reserva de espaço do dia. Resolvido no `823fda66`.
- **Rodada 4:** sem blocker e sem should-fix.
- **Nits que ficaram (opcionais), em `contents-pdf.ts`:** a escala de fontes está dividida entre `SIZE` e `SMALL`; o padding do chip e o `2.4` são literais; `buildContentsPdf` é longo (~234 linhas); o header usa arrays paralelos; e há números sem nome no teste novo.
- Detalhes em `.escritorio/cards/LM-2180/review.md`.

## QA (rodada 3): APROVADO
Desktop 1440x900, commit `823fda66`.

| # | Critério | Resultado |
|---|---|---|
| 1 | Sem turma, botão visível e desabilitado | APROVADO |
| 2 | Modal abre com disciplina e período da tela | APROVADO |
| 3 | Até antes de De bloqueia e mostra a mensagem | APROVADO |
| 4 | Disciplinas da turma + "Todas"; datas livres | APROVADO |
| 5 | Matemática no período: PDF correto (4 páginas, layout novo) | APROVADO |
| 6 | DIRETOR com "Todas": etiqueta de disciplina em cada conteúdo (13 páginas) | APROVADO |
| 7 | PROFESSOR com "Todas": só as dele (15 conteúdos em 4 disciplinas) | APROVADO |
| 8 | Período vazio: aviso e nada baixa | APROVADO |
| 9 | Rodapé "Gerado em · Página N de T"; header do exemplo, sem logo nem assinatura | APROVADO (PDFs de 3, 4, 13 e 26 páginas) |
| 10 | Loading durante a geração e erro sem travar | APROVADO |

O QA também conferiu, nos 4 PDFs, que a barra lateral continua quando o conteúdo passa para a página seguinte e que nenhuma página termina com a faixa de um dia sozinha. Quadro completo em `.escritorio/cards/LM-2180/qa.md`.
