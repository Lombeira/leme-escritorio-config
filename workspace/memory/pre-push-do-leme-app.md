---
name: pre-push-do-leme-app
description: "O pre-push do leme-app (Husky) roda Biome --write, faz git add . sem commitar e roda a suíte inteira; push demora e deixa mudança staged"
metadata:
  type: project
---

O `.husky/pre-push` do leme-app roda `biome check --write` e `biome format --write` em
`./src`, depois **`git add .`** sem commitar, e por fim `biome check` e `pnpm test`
(a suíte inteira). O `post-commit` gera a knowledge base e cria um commit `[kb]` sozinho.

**Why:** o push leva o tempo da suíte inteira, e se o Biome reformatar algo, a correção
fica staged no working tree, fora do commit que foi enviado. O `.env` está no
`.gitignore`, então o `git add .` não o pega (conferido em 06/11/2026).

**How to apply:** rodar `pnpm biome check ./src --write` antes de commitar, para o
pre-push não ter o que reformatar. Depois de um push, olhar o `git status`: se houver
mudança staged do Biome, ela precisa de um commit próprio. Esperar o commit `[kb]`
depois de cada commit. Os hooks só rodam depois de `pnpm install` (o `prepare` liga os
hooks do Husky). Ver [[biome-checks-test-files]].
