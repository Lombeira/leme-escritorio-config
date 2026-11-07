---
name: worktree-precisa-de-install-proprio
description: node_modules simbolizado do worktree principal mente — branches longas do leme-app divergem no package.json
metadata:
  type: project
---

Worktree novo do leme-app precisa do próprio `pnpm install --frozen-lockfile`. Simbolizar o `node_modules` do worktree principal parece atalho e passa a maior parte dos checks, mas as branches longas divergem no `package.json`: a `style/poc-visual-standardization` tirou o `@reactour/tour`, então rodar o `tsc` da `main` contra aquele `node_modules` deu `Cannot find module '@reactour/tour'` em `src/components/Tour/steps.tsx` e no `useOnboardingTour.ts`.

**Why:** o erro se disfarça de bug no código, não de ambiente errado — e um subconjunto de testes que não importa o pacote ausente passa, o que dá falsa confiança.

**How to apply:** ao criar worktree para validar algo em cima da `main`, instale nele antes de rodar tsc/test/build; se for simbolizar de propósito, compare `package.json` das duas branches primeiro. Vale para o [[validate-fixes-empirically]].
