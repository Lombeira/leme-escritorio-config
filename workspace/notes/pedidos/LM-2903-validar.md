---
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/888
fechado_em: 2026-11-12 16:05 (aprovado)
card: LM-2903
---
# LM-2903: validar Base de Conhecimento lendo o texto do Doc

**PR:** https://github.com/leme-tech/leme-app/pull/888

**Preview:** http://192.168.1.173:5301/ (rede de casa, cai ao sair da validação ou em 24 h)

## Resumo
O texto dos 42 guias e das 17 dúvidas agora vem só do Google Doc "Manual de uso" (já preenchido). `tutorials.ts` e `faq.ts` guardam só alvo do tour, perfis, módulo e AEE. Guia ou dúvida sem par no Doc sai da lista (e dos MDs do Capitão) em vez de aparecer em branco; `check:tutorials` acusa. Commits locais: 95c9b1f4, 89b503a8, 94f32f64.

## Decisão para você
- O título dos guias passou a vir do Doc (o CA2 não deixa `title` no código). 16 guias antigos mudam de título (ex.: "Como criar uma turma" vira "Como criar turmas"; "Como gerar o Relatório de Faltas" vira "Relatório de Frequência") e os 18 antigos perderam a linha de descrição sob o título. Se preferir manter o título no código, o CA2 precisa ser revisto.

## Correções que ficam no Doc (Let / CS), não no código
- 4 citações a títulos que não existem mais na tela: dúvida das notas ("Como lançar as notas do período" agora é "Como lançar notas"), dúvida somativa x diagnóstica (2 citações) e passo 5 do sábado letivo.
- Dúvida "O que significa cada desenho" tem asteriscos literais ("\*Lápis\*:").

## QA: APROVADO (7/7)
| # | Critério | Resultado |
|---|---|---|
| 1 | generate:kb + check:tutorials | APROVADO (42 guias ok) |
| 2 | sem texto em tutorials.ts | APROVADO |
| 3 | "Passo a passo" no JSON | APROVADO (42) |
| 4 | export:kb-docs --check | APROVADO (66 artigos) |
| 5 | guia novo + "Me mostre como fazer" (desktop e 390x844) | APROVADO |
| 6 | dúvida "Onde eu lanço as notas?" | APROVADO |
| 7 | busca, AEE, categorias | APROVADO, com ressalva: cadeado não visto na tela e "igual à main" só pelo diff |

Review: 2 rodadas, READY. Nits abertos (não bloqueiam): `conferir-doc.ts` não acusa guia com `route` sem `steps`; reflow do cabeçalho e `artigoDeDuvida` em `export-kb-docs.ts`; `flatMap` com formas diferentes em `tutorials.ts`/`faq.ts`; cabeçalho de `tutorials.ts`.

Evidências: .escritorio/cards/LM-2903/qa.md e evidencias/. Obs.: o professor não roda o tour dos guias de coordenação (aviso esperado); QA usou ADMIN.
