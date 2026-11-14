---
status: aberto
card: LM-2889
---
# LM-2889: o banco de questões ganhou o campo Tags (ERER) no formulário, nos cards, na lista, no detalhe e no filtro

**Abrir:** http://192.168.1.173:5302/dashboard/mapa/questions
**Entrar com:** a conta de teste de administrador do qa.env (nunca a senha)

## Decida antes de aprovar
- **Campo Tags como checkbox:** hoje o cadastro só tem a tag ERER, então usei checkbox (multi-seleção). Alternativa: select de valor único. Trocar custa pouco, mas mexe em formulário e testes.
- **Detalhe sem tag mostra "Sem tags"** em vez de esconder o campo. Esconder é trivial de trocar.
- **Texto do aviso de versão:** o aviso ao salvar agora diz "Alterações numa questão publicada, exceto nas tags, criam uma nova versão dela", porque mudar só a tag não cria versão. Não detectei "só tag" no front, pois quem decide é o backend.
- **Texto antigo (já existia):** o aviso diz "questão publicada" mesmo para rascunho. Não mexi.

## Como validar (uns 8 minutos)
1. Clique em **Nova questão** → **deve aparecer:** o campo "Tags" abaixo de Dificuldade, com a opção "ERER" (print: `evidencias/1-form-nova-questao.png`)
2. Preencha os campos obrigatórios (ex.: Maternal 2, Educação Física, Fácil), marque ERER e salve → **deve aparecer:** o card da questão com o chip "ERER"; ao abrir, "Tags: ERER" (print: `evidencias/6a-detalhe-erer.png`)
3. Em Editar nessa questão, desmarque ERER e salve → **deve aparecer:** "Sem tags" no detalhe e checkbox desmarcado ao reabrir a edição (print: `evidencias/3a-detalhe-apos-remover.png`)
4. Numa questão sem tag, Editar, marque só ERER e salve → **deve aparecer:** ERER no detalhe e a versão continua "Versão 1" (print: `evidencias/4-detalhe-tag-adicionada-v1.png`)
5. Troque para a visão em lista → **deve aparecer:** coluna "Tags" depois de Dificuldade, com o chip ou vazia (print: `evidencias/5-listagem-lista.png`)
6. Na barra de filtros, escolha "Tag" = ERER (fica depois de "Autor") → **deve aparecer:** só questões com ERER e o contador "1 de 1 questões"; voltar para "Tag" vazio traz "24 de 24" (print: `evidencias/7a-filtro-tag-erer.png`)
7. Combine Tag = ERER com Dificuldade → **deve aparecer:** resultado respeitando os dois (Fácil: 1; Difícil: 0)
8. Crie uma questão sem marcar tag → **deve aparecer:** "Questão criada com sucesso.", sem erro

Dados de teste em homolog: "QA LM-2889 com ERER" e "QA LM-2889 sem tag" (rascunhos).

## Não precisa conferir
- Que tag não entra na checagem de metadados incompletos nem exige o campo (testes cobrem).
- Evento de analytics `filter_applied` com `filter_name: tag` (teste unitário).
- Celular: banco de questões é desktop, não testado.

## Detalhes técnicos
- Review: 3 rodadas; rodada 3 READY (0 blockers, 0 should-fix, 2 nits: `?? []` inalcançável em `question-input-to-payload.ts:59` e tipo de opção repetido em `curriculum-api.ts:32`).
- QA: APROVADO nos 9 critérios (desktop, ADMIN); Disciplina não foi combinada separadamente (depende de Matriz), Dificuldade prova a soma de filtros.
- Commits: `feat(questions): tags no banco de questões`, `refactor(questions): QuestionTagBadges e fieldset nas tags`, `fix(questions): texto de versão...`. Commits `[kb]` removidos; a branch não toca na Base de Conhecimento.
- Checks do front-dev: biome, tsc e vitest dos arquivos relacionados passaram.
- Detalhes em `cards/LM-2889/implementacao.md`, `review.md` e `qa.md`.
