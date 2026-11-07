---
name: biome-checks-test-files
description: "No leme-app, `pnpm biome check ./src` reprova formatação de arquivos *.test.tsx apesar do files.ignore do biome.json"
metadata: 
  node_type: memory
  type: project
  originSessionId: 15c463a7-19aa-486b-87cf-b4037748187e
  modified: 2026-08-08T15:52:04.340Z
---

Em `leme-app`, `pnpm biome check ./src` **verifica a formatação de arquivos `*.test.tsx`**, mesmo com
`files.ignore: ["**/*.test.{ts,tsx}", ...]` em `biome.json`. Observado em 2026-08-08 (Biome 1.9.4):
ao criar `src/pages/contents/components/Form/bncc-select.test.tsx`, o check reprovou com um erro de
`format` nesse arquivo. A regra de *lint* de fato não roda nos testes — `linter.ignore` usa padrões
explícitos (`**/*.test.tsx`), sem chaves. A causa provável é que `files.ignore` não expande
`{ts,tsx}` nessa versão.

**Why:** a skill `unit-test` afirma que os testes ficam fora do linter *e* do formatador; isso vale
só para o linter. Confiar nisso faz o CI (`pnpm biome check ./src`) quebrar depois de escrever um teste.

**How to apply:** depois de criar ou editar qualquer `*.test.tsx`, rode `pnpm biome check ./src --write`
antes de commitar. Vale também [[validate-fixes-empirically]] — foi rodando o check que isso apareceu.
