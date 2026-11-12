---
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/886
fechado_em: 2026-11-11 22:07 (aprovado)
card: LM-2904
---
# LM-2904: validar

**PR:** https://github.com/leme-tech/leme-app/pull/886

Sem preview: os 5 critérios são não visuais. Valide pelo diff (commit `69044fc1` na branch `LM-2904-frontend-base-de-conhecimento-leitor-do`) e pelas evidências em `.escritorio/cards/LM-2904/evidencias/`.

## O que mudou
- `scripts/lib/passo-a-passo.ts`: linha numerada com mais recuo que o primeiro item vira texto do passo atual, não passo novo. `parseSteps` devolve `undefined` sem a seção e `[]` com seção sem item legível.
- `scripts/generate-knowledge-base.ts`: seção ilegível não grava `steps` e emite `console.warn` com o título do artigo, sem falhar.
- 3 testes novos; os 6 antigos intactos.

## QA (APROVADO, por comando)
| # | Critério | Resultado |
|---|---|---|
| 1 | Sublista fica no texto da 1ª etapa (2 etapas) | APROVADO |
| 2 | Seção ilegível avisa com o nome do artigo | APROVADO |
| 3 | Sem lançar; sem aviso se não há seção ou é legível | APROVADO |
| 4 | Casos antigos passam (9/9) | APROVADO |
| 5 | `pnpm check:tutorials` código 0 | APROVADO |

## Review: READY
0 blockers, 0 should-fix, 6 nits (não corrigidos): ver `.escritorio/cards/LM-2904/review.md`.

## Para citar no PR
O Google Doc atual não tem sublista numerada (o `generate:kb` real não mudou o JSON nem avisou), então o recuo seguiu o exemplo do card.
O caso antigo "seção sem item legível" agora imprime o aviso no stderr do vitest (só ruído).
