---
card: LM-2885
status: fechado
fechado_em: 2026-11-10 18:23 (aprovado)
rodada: 1
pr: https://github.com/leme-tech/leme-app/pull/881
---
# LM-2885: validar a Base de Conhecimento com o Google Doc na frente (um PR só, substitui o #853)
**PR:** https://github.com/leme-tech/leme-app/pull/881

**Link:** http://192.168.1.173:5301/dashboard/knowledge-base. É o preview do worktree, com a API de homolog. Ele cai quando o card sai da validação ou depois de 24 h.
- Worktree: `repos/leme-app/.worktrees/LM-2885`
- Branch: `LM-2885` @ `eccd16a1`, com 20 commits à frente da `origin/main`, só local e sem push
- Diff: `git -C repos/leme-app/.worktrees/LM-2885 diff origin/main...HEAD`

## O que foi feito (resumo do implementacao.md)

Foi um PR só, como a feda decidiu. A branch `LM-2885` traz a `feat/kb-mapa-de-fluxos` (PR #853) atualizada com a main, e por cima vêm o "Doc na frente" e os MDs do Capitão. A branch da Fernanda e o PR #853 não foram tocados. **O PR novo vai dizer que substitui o #853 e que os commits vieram da branch da Fernanda. Fechar o #853 fica com vocês.**

- **O que veio do #853:** os 13 commits entraram por cherry-pick, com a autoria da Fernanda preservada. Foram 4 conflitos em 3 arquivos (`package.json` duas vezes, `AnnotationTab/index.tsx` e `frequency/special-education/index.tsx`). Em todos ficou a versão da main, acrescentando só o script ou o `data-tour` que a branch trazia. Teve ainda um conflito que o git não acusou: a dúvida "Por que a tela de Frequência está vazia?" citava uma mensagem que a main tirou, e foi reescrita com o que a tela mostra hoje.
- **Doc na frente:**
  - O guia que tem artigo no Doc mostra o texto do Doc no lugar das etapas.
  - Os 5 artigos substituídos também mostram o texto do Doc.
  - "Me mostre como fazer", perfis, cadeado, AEE e as etapas do tour continuam vindo do código.
  - Se o Doc não tiver o artigo ou trocar o título dele, o guia volta para o texto do código, e o artigo do Doc vira um artigo comum no fim da lista, sem tour.
  - Quando o texto é do Doc, saíram da página a seção "Vídeo e mais detalhes" e a frase "Texto conferido com a plataforma em…".
- **MDs do Capitão:** o `export-kb-docs` segue a mesma regra, e o `docs/knowledge-base/` foi regerado.
- **Correções do review** (3 rodadas, terminou em READY):
  - O logout agora zera o tour e a busca da Base.
  - O cartão do tour aceita foco com uma gaveta aberta.
  - A regra "quem fica fora da lista", os títulos dos artigos montados e o mapa do Doc ficaram num lugar só, compartilhado pela página e pelo export.
  - Saíram dois exports sem uso, e o `pnpm knip` sai 0.
- **Não mexemos** no `generate-knowledge-base.ts`, no Google Doc nem em sincronização agendada.

## QA (APROVADO, rodada 1)

| # | Critério | Resultado | Observação |
|---|---|---|---|
| 1 | PR #853 não-rascunho | SUBSTITUÍDO | Por decisão humana. No lugar dele: `pnpm knip` sai 0 |
| 2 | Sem conflito com origin/main | APROVADO | `merge-tree`: 0 conflitos |
| 3 | Base e guia abrem, passo a passo, tour | APROVADO | "Como transferir um aluno": tour inicia |
| 4 | Guia pareado mostra o Doc e mantém o tour | APROVADO | "Como criar uma turma" |
| 5 | 5 substituídos mostram o Doc | APROVADO | 4 conferidos na tela; o de avaliações só pelo MD e pela regra |
| 6 | Guia sem Doc mostra o código | APROVADO | |
| 7 | Artigo novo e título trocado no Doc | APROVADO | Com cópia temporária do JSON, revertida depois; não quebra |
| 8 | Busca por termo só do Doc | APROVADO | "Secretaria Escolar Digital" |
| 9 | Cadeado e AEE | APROVADO | Simulado com flag forçada, não com rede real sem o módulo |
| 10 | Perfis, categorias, tour desktop/390px | APROVADO | Não há seletor de perfil; a lista muda com o usuário logado |
| 11 | `pnpm check:tutorials` | APROVADO | exit 0 |
| 12 | `export:kb-docs` sem diferença, `--check` 0 | APROVADO | 66 artigos |
| 13 | MDs com o texto do Doc | APROVADO | 6 pares conferidos |
| 14 | `--check` acusa MD desatualizado | APROVADO | exit 1 apontando `tutorial-criar-turma.md` |

Evidências em `.escritorio/cards/LM-2885/evidencias/`.

## O que validar no browser

1. Abrir "Como criar uma turma": o corpo tem que ser o texto do Doc, e "Me mostre como fazer" tem que iniciar o tour.
2. Em "Primeiros passos", abrir os artigos substituídos (Base de Conhecimento, Onde fica cada coisa, Configurações, Quem pode fazer o quê): o texto tem que ser o do Doc.
3. Abrir um guia sem Doc ("Como transferir um aluno"): as etapas numeradas têm que continuar.
4. Busca, cadeado, AEE e o tour em celular (~390px) têm que funcionar como no rascunho.

## Para decidir / ficar de olho

- **Os MDs do Capitão ficam para trás depois de cada edição no Doc.** O post-commit atualiza só o `knowledge-base.data.json`, então o Capitão lê texto velho até alguém rodar `pnpm export:kb-docs`. O CI não quebra por isso. O conserto, fora deste card, seria o `.husky/post-commit` rodar também o export.
- **Acessibilidade:** nas etapas dentro de gaveta (`save-annotation`, `save-event`, `student-create-save`), o leitor de tela não enxerga o cartão do tour, e o Tab não chega nele a partir da gaveta. Com mouse e toque funciona. Resolver exige refazer a montagem do tour.
- **Leitura do critério 11:** as etapas dos guias continuam sendo conferidas, porque o tour usa esse texto. Deixou de ser cobrado só o texto do código dos artigos que o Doc substitui. O QA concorda com essa leitura.
- A descrição de uma linha abaixo do título do guia continua vindo do código, mesmo quando o corpo é do Doc.
- O Doc usa negrito como ênfase e tem erros de digitação (ex.: "**Para voc**ê"). A Base mostra o texto como está, por regra.
- Os 13 commits da Fernanda mantêm as mensagens originais, sem `[LM-2885]`. O card vai no título do PR.
- Nits do review que ficaram (não obrigatórios): comentários acima da meta em `knowledge-base.ts`, `check-tutorials.ts`, `modules.ts` e `structure.ts`; o `ArticleContent.tsx` passou de 584 linhas; e o `sentenceCase` está em `types.ts`. Detalhes em `.escritorio/cards/LM-2885/review.md`.
- Observação do QA: ao iniciar o tour de "Como criar uma turma", a escola selecionada volta para "Selecione a escola". Parece ser o desenho do tour.
- Se der para fazer agora, a proposta de comentário no Jira (precisa do seu OK) é: "Feito num PR só, que substitui o #853 (commits da branch feat/kb-mapa-de-fluxos da Fernanda). Sem sincronização agendada; o Doc segue sincronizando no commit."
