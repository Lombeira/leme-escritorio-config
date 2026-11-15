---
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/895
fechado_em: 2026-11-14 16:22 (aprovado)
card: LM-2889
---
# LM-2889: Banco de questões ganha a tag "ERER" (cadastro, listagem, detalhe e filtro)

**PR:** https://github.com/leme-tech/leme-app/pull/895

**Abrir:** http://192.168.1.173:5302/dashboard/mapa/questions
**Entrar com:** a conta de teste de ADMIN do qa.env (ou a sua, se tiver acesso ao Banco de questões)
**Celular:** não se aplica (banco de questões é desktop)

## Decida antes de aprovar
- O card não dizia onde ficava a tag. Escolhi: no formulário, um bloco "Tags" com caixinha "ERER" abaixo de Dificuldade (como só existe ERER, não é select). Alternativa: select de valor único. Trocar custa pouco.
- Chip "ERER" nos cards e coluna "Tags" na lista; no detalhe, "Sem tags" quando vazio.
- Filtro "Tag" é de valor único, depois de "Autor".
- Mudar só a tag **não cria nova versão**; os textos de edição agora dizem isso ("exceto nas tags").

## Como validar (uns 5 minutos)
1. Banco de questões → **Nova questão** → **deve aparecer:** bloco "Tags" com a caixa "ERER" abaixo de Dificuldade (print: `evidencias/r2-1-form-tags.png`)
2. Preencha os campos, marque ERER e salve → **deve aparecer:** a questão na lista com o chip "ERER" (print: `evidencias/r2-2a-form-erer.png`, `evidencias/r2-5a-cards.png`)
3. Abra a questão → **deve aparecer:** "Tags: ERER" (print: `evidencias/r2-6a-detalhe-erer.png`)
4. Editar a questão, desmarque ERER, salve e confirme → **deve aparecer:** "Sem tags" no detalhe (print: `evidencias/r2-3c-detalhe-sem-tag.png`)
5. Editar uma questão sem tag, marque só ERER e salve → **deve aparecer:** a tag no detalhe e a versão continua a mesma (ex.: "Versão 1") (print: `evidencias/r2-4b-detalhe-tag-v1.png`)
6. Troque para a visão em lista → **deve aparecer:** coluna "Tags" com ERER, vazia nas questões sem tag (print: `evidencias/r2-5b-lista.png`)
7. Nos filtros, escolha **Tag = ERER** → **deve aparecer:** só questões com ERER e o contador "X de Y questões" ajustado; limpar o filtro volta à lista completa (prints: `evidencias/7a-filtro-tag-erer.png`, `7b-filtro-tag-limpo.png`)
8. Combine Tag = ERER com Dificuldade → **deve aparecer:** só as que atendem aos dois (prints: `evidencias/8a-...`, `8b-...`)
9. Crie uma questão sem marcar tag → **deve aparecer:** "Questão criada com sucesso." (sem erro)

## Não precisa conferir
- Combinação Tag + Disciplina (o QA provou a combinação com Dificuldade).
- Testes automatizados, lint e tipos: o review deu READY.
- Questões de teste "QA LM-2889 ..." ficaram em homolog, em Rascunho.

## Detalhes técnicos
- QA rodada 2: APROVADO nos 9 critérios, console sem erros (`qa.md`).
- Review rodada 3: READY, 0 blockers, 0 should-fix, 2 nits (fallback `?? []` inalcançável em `question-input-to-payload.ts:59`; tipo de opção repetido em `curriculum-api.ts:32`).
- 3 commits na branch; sem commit `[kb]`.
- Achado lateral, pré-existente: o diálogo de confirmação diz "questão publicada" mesmo para Rascunho.
