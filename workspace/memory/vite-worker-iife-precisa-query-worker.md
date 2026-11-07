---
name: vite-worker-iife-precisa-query-worker
description: "No leme-app, worker instanciado com new URL() morre em dev por causa do worker.format iife; só ?worker empacota nos dois modos"
metadata: 
  node_type: memory
  type: project
  originSessionId: 16a21161-9322-46df-94ab-c8846a1a2609
  modified: 2026-09-04T21:11:29.595Z
---

O `vite.config.ts` fixa `worker.format: "iife"` (por causa do `importScripts` do
opencv.js). Com isso, `new Worker(new URL("./x.js", import.meta.url))` funciona
no build mas quebra em `pnpm dev`: o dev server serve o arquivo cru com
`?worker_file&type=classic`, e qualquer `import` dentro dele vira
`Uncaught SyntaxError: Cannot use import statement outside a module`. O worker
morre no load, o `onerror` dispara e, se houver fallback, tudo volta calado para
a main thread. Verificado em 04/09/2026 com curl no dev server.

A forma que empacota nos dois modos é `import W from "./x.js?worker"` +
`new W()`.

**Por quê:** o sintoma não aparece no build nem nos testes (jsdom não tem
Worker), só em dev — e como o fallback é silencioso, dá para medir performance e
concluir que o worker "não adiantou nada" sem perceber que ele nunca rodou.

**Como aplicar:** ao criar worker novo no leme-app, use `?worker`. Se um worker
existente usa `new URL()`, ele está morto em dev; conferir isso antes de investigar
bug que só aparece rodando local. Ver [[validate-fixes-empirically]].
