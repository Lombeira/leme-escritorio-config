---
name: leme-app-suite-quebra-no-node-26
description: "leme-app: suíte unitária quebra no Node 26 (localStorage nativo x jsdom); usar 24 até o PR (c) das pendências"
metadata:
  type: project
---

A suíte unitária do leme-app quebra no Node 26: o `localStorage` nativo do Node sobrepõe o
do jsdom e os testes caem com `localStorage.clear/getItem/setItem` indefinido. Medido em
06/11/2026 num worktree limpo da main: Node 26, 137 falhas em 88 arquivos; Node 24.22.1,
0 falhas em 3345 testes.

**Why:** o CI usa `lts/*` (virou 26 em 28/10) mas não roda testes unitários, só o pre-push
roda; por isso o CI fica verde e o push do LM-2857 pela esteira caiu no pre-push.

**How to apply:** usar Node 24 (padrão do fnm e `NODE_PADRAO` da esteira) até sair o PR (c)
de `notes/pendencias.md` (setup do vitest compatível com Node 26). Push que falhar no
pre-push com erro de `localStorage` é ambiente, não o card. Ver [[pre-push-do-leme-app]].
