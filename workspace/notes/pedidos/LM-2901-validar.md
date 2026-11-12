---
card: LM-2901
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/885
fechado_em: 2026-11-11 21:22 (aprovado)
---
# LM-2901: validar a parte 1 da Base de Conhecimento ("Ler do Doc")

**PR:** https://github.com/leme-tech/leme-app/pull/885

**Link:** http://192.168.1.173:5302/base-de-conhecimento (ou, em contexto seguro, `ssh -L 5302:localhost:5302 leme@192.168.1.173` e `http://localhost:5302/base-de-conhecimento`). O preview vem do worktree, aponta para homolog e cai ao sair da validação ou em 24 h.
- Worktree: `repos/leme-app/.worktrees/LM-2901`
- Branch: `LM-2901-frontend-base-de-conhecimento-todo-o` @ `8d936dea`, só local e sem push. São 3 commits: `efd9b8eb`, `dab7429e` e `8d936dea`.
- Diff: `git -C repos/leme-app/.worktrees/LM-2901 diff origin/main...HEAD`, com 20 arquivos, quase tudo em `scripts/`, `src/constants/knowledge-base*` e `src/pages/knowledge-base/`.
- Triagem, implementação, review e QA: `.escritorio/cards/LM-2901/` (`triagem.md`, `implementacao.md`, `review.md`, `review-r1.md`, `review-r2.md`, `qa.md`, `evidencias/`).

## O card foi quebrado
A re-triagem saiu VIÁVEL, com o card quebrado em duas partes (`.escritorio/cards/LM-2901/quebra.json`):
- **Este PR (LM-2901), parte 1, "Ler do Doc":** o parser do "Passo a passo", o `articleId` nas dúvidas, a mescla com o texto do código como reserva, o tour que some quando o par ou a contagem quebra, e o `check:tutorials` com as três proteções.
- **Fica para o próximo card (p2):** colar o texto no Google Doc (precisa de permissão de edição, versão nomeada e aviso à Let e ao CS) e tirar o texto de `tutorials.ts` e `faq.ts`. Depende deste PR mergeado.

## O que mudou (resumo do implementacao.md)
**Para quem usa, nada.** O Doc ainda não tem nenhum "Passo a passo", então o `generate:kb` gera um `knowledge-base.data.json` idêntico ao de hoje e o tour roda com o texto do código.

Quando o Doc tiver a seção:
- **Leitura:** cada item da lista numerada vira um passo. A 1ª linha é o título, o resto é o texto (com o negrito preservado). "No celular: …" vira o texto do celular e "No celular: não tem" vira `mobile: null`. A seção termina no próximo título ou no primeiro parágrafo fora da lista. Seção sem item legível conta como sem seção.
- **Mesmo número de passos que o código:** o balão e o artigo usam o texto do Doc, e o código continua dando o alvo, a rota e o clique. Sem "No celular:" no Doc, vale o `mobile` do código.
- **Número diferente:** o artigo mostra os passos do Doc e só some o "Me mostre como fazer". O "Ir para …" continua e a página nunca fica em branco.
- **`check:tutorials`:** falha e nomeia o guia quando a contagem não bate, quando um guia ou dúvida tem `articleId` sem artigo no Doc, ou quando um negrito sumiu da tela. Problema de pareamento não entra no `tutorials.status.json`, para a página não dizer "Esta tela mudou" quando quem mudou foi o Doc.
- `scripts/**/*.test.ts` entrou no `vite.config.ts` e no `knip.json`, senão o `pnpm test scripts` não acha os testes.

## QA: APROVADO (rodada 1)

| # | Critério | Resultado | Observação |
|---|---|---|---|
| 1 | Parser do "Passo a passo" (teste novo) | APROVADO | 11 testes de scripts passam |
| 2 | `pnpm generate:kb` | APROVADO | exit 0, JSON idêntico, 0 `"steps"` |
| 3 | `pnpm check:tutorials` na main atual | APROVADO | exit 0, status.json sem diff |
| 4 | Testes do check (contagem, par, negrito) | APROVADO | teste unitário cobre os três casos. Com o JSON editado à mão, a contagem e o negrito também saíram com exit 1, nomeando o guia |
| 5 | `git grep articleId src/constants/faq.ts` | APROVADO | aparece só a linha da interface, porque nenhuma dúvida tem artigo no Doc hoje |
| 6 | Tour com o texto de hoje, desktop e celular | APROVADO | "Como criar uma turma" com o texto do código |
| 7 | JSON editado: Doc com 6 passos usa o texto do Doc; com 5 tira o botão | APROVADO | o celular usa o `mobile` do Doc. Com 5 passos, o artigo carrega e o "Ir para Turmas" continua |
| 8 | Busca, cadeado, AEE, perfil, categorias | APROVADO com ressalva | 3 perfis, 8 categorias, busca "turma" com 37 resultados. Cadeado e AEE não foram exercitados na tela (sem escola selecionada), e o diff não toca essa lógica |
| 9 | `pnpm export:kb-docs --check` | APROVADO | exit 0, 66 artigos |

## O que validar
1. Abrir um guia de tour (ex.: "Como criar uma turma") e clicar em "Me mostre como fazer": o texto tem que ser o de hoje, no computador e no celular.
2. Se quiser ver o caminho do Doc: editar à mão o `src/constants/knowledge-base.data.json` do worktree, como descrito em "Como testar" do `implementacao.md`, e depois `git checkout` do arquivo.
3. Busca, cadeado por módulo e AEE com uma escola selecionada, porque o QA não exercitou esses dois na tela.

## Pendências conhecidas (não bloqueiam)
- **🟡 Should-fix do review que ficou aberto** (passou do limite de 2 voltas): `scripts/lib/passo-a-passo.ts:6`. Uma sublista numerada com recuo dentro de um passo vira passos extras, e aí a contagem não bate, o tour desliga e o check culpa a contagem. Não está confirmado que o export do Google gere esse formato, e hoje o Doc nem tem a seção. Dá para corrigir neste PR com uma devolução, ou deixar para a parte 2.
- **A seção vazia agora passa calada:** se o Doc tiver um "Passo a passo" que não dá para ler, ninguém fica sabendo. Um aviso que não falha o `generate:kb` resolveria, mas está fora do escopo.
- **O formato real do export do Google para item com quebra de linha não foi visto,** porque o Doc ainda não tem a seção. Na parte 2, conferir a saída do `generate:kb` no primeiro guia colado.
- **Na parte 2, as 17 dúvidas e os 24 guias sem `articleId` precisam ganhar o campo** ao virar artigo no Doc.
- **Nits do review** (estilo, opcionais): estão em `review-r1.md`, `review-r2.md` e `review.md`.
