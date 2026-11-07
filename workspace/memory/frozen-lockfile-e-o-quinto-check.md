---
name: frozen-lockfile-e-o-quinto-check
description: editar package.json sem regenerar o lock quebra a pipe; os quatro checks locais não pegam porque node_modules já existe
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bfe7450d-9a3a-4bb0-876c-25f2bcc1d511
  modified: 2026-09-06T17:21:10.128Z
---

Ao editar o `package.json` à mão, rodar **`pnpm install --frozen-lockfile`** como
quinto check, junto de biome, tsc, vitest e build.

Em 06/09/2026 movi o `@techstark/opencv-js` para `devDependencies` editando só o
`package.json`. Os quatro checks deram verde e o PR entrou; a pipeline quebrou em
PRE_BUILD com `ERR_PNPM_OUTDATED_LOCKFILE`, exit 1.

**Why:** `--frozen-lockfile` é o padrão em CI e é o que o `buildspec.yml` roda.
Local, com o `node_modules` já populado, `pnpm install` nunca chega a cobrar a
consistência entre `package.json` e `pnpm-lock.yaml` — é exatamente o buraco
entre "passa na minha máquina" e "passa na pipe".

**How to apply:** depois de mexer no `package.json`, `pnpm install --lockfile-only`
para regenerar e `pnpm install --frozen-lockfile` para conferir por exit code.
Cuidado ao cortar branch: se a `origin/main` local estiver velha, o lock vem sem
correções recentes e o check falha por outro motivo — fetchar antes. Ver
[[conferir-pr-antes-de-novo-push]].
