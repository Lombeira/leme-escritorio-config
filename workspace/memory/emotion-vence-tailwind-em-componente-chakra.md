---
name: emotion-vence-tailwind-em-componente-chakra
description: Passar className do Tailwind para um componente do Chakra não funciona — o Emotion injeta depois e vence
metadata: 
  node_type: memory
  type: project
  originSessionId: a99388fe-98a6-4c2c-95d6-18c161a3896b
  modified: 2026-08-13T15:19:06.880Z
---

No leme-app, `className` do Tailwind **não tem efeito** sobre um componente que
ainda é do Chakra. Medido: `<DownloadIcon className="size-8 text-gray-500" />`
(de `@chakra-ui/icons`) renderiza 16px na cor herdada.

**Why:** o Emotion injeta o estilo do componente num `<style>` no fim do
`<head>`, depois da folha do Tailwind. Como as duas classes têm a mesma
especificidade (0,1,0), quem vem por último na folha ganha. Não é o mesmo
problema de `@layer` (esse é [[tailwind-fora-de-layer-por-causa-do-chakra]]) —
aqui os dois estão fora de layer e a ordem de injeção é que decide.

**How to apply:** durante a migração, uma conversão só pode aplicar classe do
Tailwind depois que o elemento **deixa de ser** um componente do Chakra. Ao
converter, checar de onde o símbolo foi importado, não como ele se chama: o
mesmo nome (`DownloadIcon`) vem do `@chakra-ui/icons` num arquivo e do
`lucide-react` em outro. E confirmar com `getComputedStyle` no navegador —
`tsc`, Biome e a suíte unitária passam todos com o estilo descartado.
