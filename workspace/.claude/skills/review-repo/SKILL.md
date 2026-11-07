---
name: review-repo
description: Code review de um diff em repo da Leme que não é o leme-app (leme-core, leme-assistant...), no mesmo desenho da /review do leme-app - 3 lentes em paralelo, validação independente de cada achado e corte por confiança - usando o checklist do repo em esteira/review/<repo>/checklist.md. Só leitura; não corrige nem posta.
---

# Review de repo (leme-core, leme-assistant, ...)

Use para revisar um diff de um repo da Leme que **não** é o leme-app (o leme-app tem a `/review` própria). Argumentos: `REPO_NOME` (ex.: `leme-core`), `REPO` (caminho absoluto da raiz ou do worktree), `RANGE` (ex.: `origin/main...HEAD`) e, opcional, um `FOCO` pedido pelo humano.

## Passo 1: preparar

- Checklist: `~/workspace/esteira/review/<REPO_NOME>/checklist.md`. Se não existir, diga isso e pare: sem checklist o review sai genérico.
- `git -C $REPO fetch -q origin` e confira a base do range. Lista de arquivos: `git -C $REPO diff --name-only $RANGE`. Inclua o não commitado só se houver (`git -C $REPO status --porcelain`).
- Diff vazio: diga e pare.

## Passo 2: três lentes em paralelo

Dispare **na mesma mensagem** três subagentes `reviewer-repo` (Agent tool), um por lente, passando a cada um: lente, `REPO_NOME`, `REPO`, `RANGE`, a lista de arquivos, o caminho do checklist e o `FOCO`. Modelo por lente:

| Lente | `model` |
|---|---|
| `correctness` | `opus` |
| `reuse-architecture` | `sonnet` |
| `readability` | `sonnet` |

## Passo 3: juntar

- Deduplicar por `arquivo:linha` + ID da regra.
- Duas lentes no mesmo `arquivo:linha` (regras diferentes): mantenha os dois IDs e suba a confiança um degrau (50→75, 75→100).
- Fica a maior severidade do local.

## Passo 4: validar cada achado (paralelo)

Para cada achado, um subagente `review-validator-repo` (Agent tool, `model: haiku`), em paralelo (em lotes se forem muitos), com: ID + regra em uma linha, `arquivo:linha`, afirmação, correção, `REPO`, `RANGE`, caminho do checklist, confiança do revisor. `validated: false` descarta (guarde o motivo); `true` mantém com a confiança do validador.

## Passo 5: corte e apresentação

- 🔴 Blockers ficam com confiança **≥ 50** (os de 50 marcados *(precisa confirmar)*); 🟡 e ⚪ só com **≥ 75**.
- Apresente por severidade, cada linha com `arquivo:linha`, IDs, confiança final, problema em uma linha e a correção. Depois uma linha de **Cobertura** (quantos cada lente levantou, quantos o validador derrubou e por quê, quantos o corte suprimiu) e exatamente um veredito:
  - `Veredito: READY` (sem blocker, no máximo nits), ou
  - `Veredito: NEEDS CHANGES (N blockers, M should-fix)`.

## Regras

- **Não corrija** nada e **não poste** em lugar nenhum: é uma checagem local.
- Não amplie o escopo para linhas que o diff não mudou.
- O checklist é curado no workspace (`esteira/review/`); achado recorrente que não está lá vale uma linha em "Lacunas" no fim, para a próxima curadoria.
