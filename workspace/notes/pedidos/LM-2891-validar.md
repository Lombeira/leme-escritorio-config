---
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/891
fechado_em: 2026-11-13 12:31 (aprovado)
card: LM-2891
---
# LM-2891: a capa da avaliação mostra a área do conhecimento (ex.: "Linguagens") em vez da disciplina

**PR:** https://github.com/leme-tech/leme-app/pull/891

**Abrir:** http://192.168.1.173:5302/dashboard/mapa/exams/e59acd86-c620-485e-9def-f0f817e6fb8c/diagramador
**Entrar com:** a conta de teste de ADMIN do qa.env (nunca a senha)

## Decida antes de aprovar
- A área **substitui** a disciplina na linha da capa (alternativa: manter a disciplina e pôr uma segunda linha com a área).
- Prova com mais de uma área, ou com uma questão sem área misturada às outras: linha em branco, para a capa nunca afirmar uma área que não vale para toda a prova. Alternativa: ignorar as questões sem área.
- **Impressão não validada pelo QA:** a tela de impressão só monta a capa com cartões já emitidos, e o QA não emitiu em homolog (efeito sem volta). Confira o passo 5 abaixo.
- Homolog não tem disciplina sem área; os casos 3 e 4 foram simulados no navegador do QA.

## Como validar (uns 8 minutos)
1. Abra a avaliação "QA LM-2891 lp" (só Língua Portuguesa) → **deve aparecer:** na capa, a linha abaixo do título diz "Linguagens" (antes: "Língua Portuguesa") (print: `evidencias/1-lp-diagramador-linguagens.png`)
2. Em Questões > Adicionar, marque a questão de Matemática "Quanto Iara vai pagar pelos patins?" e aplique → **deve aparecer:** a linha fica em branco; ao remover essa questão (lixeira), volta "Linguagens" sem recarregar (prints: `2a-...`, `2b-...`)
3. Abra "QA LM-2891 lpmatarte" (LP + Matemática + Arte) → **deve aparecer:** linha em branco e instruções "5 questões, sendo 2 de Língua Portuguesa, 2 de Matemática e 1 de Arte" (print: `3-lpmatarte-diagramador-semarea.png`)
4. Na lista de questões, veja os chips e o filtro "Disciplina" → **deve aparecer:** ainda Língua Portuguesa, Matemática e Arte, nunca "Linguagens" (prints: `6a`, `6b`, `6c`)
5. **Impressão (não coberta pelo QA):** no Mapa, imprima uma prova só de Língua Portuguesa para uma turma → **deve aparecer:** a capa impressa com "Linguagens", igual ao preview.
6. Aba "Capa" do painel esquerdo → **deve aparecer:** "Área: área do conhecimento das questões" (print: `7a-aba-capa.png`)

## Não precisa conferir
- Casos de questão sem área (nenhuma aparece como "null"/"undefined"): o QA simulou no navegador e passou.
- Testes e checagem de tipos da correção da aba da capa.

## Detalhes técnicos
- Commits: `db6cd94f` (capa mostra a área) e `3e8ab3f3` (aba da capa); sem commit `[kb]` na branch. Regra "uma área só, senão vazio" numa função compartilhada (`coverAreaOf`) entre diagramador e impressão.
- Review (2 rodadas): READY. Sobram só 4 nits (renomear `subject` para `area`, JSDoc, if/else sem bloco, questão carregando não entra na conta), sem PR próprio.
- QA: critérios 1, 2, 3, 4, 6, 7 e a aba da capa aprovados; o 5 ficou sem evidência pelo motivo acima, não por defeito. `exam-print/index.tsx:209` e `exam-layout/index.tsx:514` usam a mesma função.
- A folha de respostas (`answer-sheets/services/knowledge-area.ts`) segue listando disciplinas: fora do escopo.
- Avaliações de teste "QA LM-2891 ..." ficaram em homolog (escola de teste).
