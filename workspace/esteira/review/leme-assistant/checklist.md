# Checklist de review — leme-assistant (rascunho)

Os revisores por lente aplicam as regras abaixo às linhas alteradas de um diff do
`leme-tech/leme-assistant` (FastAPI + Claude, SQL na réplica, MVP só para `@leme.tec.br`).

**Formato:** cada regra é `[ID] <sev> sinal → correção`. Os IDs são estáveis: não renumerar.
Categoria nova entra no fim.

**Severidade padrão (`<sev>`):** o revisor usa a severidade da regra, a não ser que o caso peça
outra (nesse caso, uma linha com o motivo no achado):
- 🔴 **blocker**: vaza dado de aluno ou da equipe, fura um limite (consultas, tempo, linhas,
  concorrência, usuário de banco) ou quebra o comportamento.
- 🟡 **should-fix**: convenção ou manutenção que o repo segue de forma consistente.
- ⚪ **nit**: opcional, baixo risco.

**Lente (`Lens:` no cabeçalho de cada categoria):** três revisores em paralelo, cada um com um
conjunto disjunto de categorias:
- `correctness`: PRIV, SQL, AUTH, LIMIT, LOG, PROMPT.
- `reuse-architecture`: VIEW, MIG, TOOL, TEST.
- `readability`: DOC.

**Escopo:** só o que o lint não pega. O CI roda `ruff check` (regras `E, F, I, B, UP`, sem `E501`
e `B008`) e `ruff format --check`: formatação, ordem de import, variável sem uso, `B`/`UP` já
estão cobertos e não entram aqui.

**Origem de cada regra** (entre colchetes no fim):
- `[doc]`: `README.md` ou `docs/adr/0001-assistente-de-dados-com-llm.md`;
- `[código]`: código, testes ou comentários do próprio repo (arquivo citado);
- `[PR #n]`: descrição ou comentário **do autor** no PR (não é review; ver Proveniência);
- `[workspace]`: `CLAUDE.md` do workspace (convenções que valem para todos os repos).

---

## ⚠️ Proveniência — ler antes de confiar numa regra

**Faixa coberta: PRs `#1`–`#26`.** Todos os 25 PRs mergeados (`#1`–`#17`, `#19`–`#26`) e também o
`#18` (aberto, pausado), lidos em 07/11/2026.

O que existe no corpus:
- **0 comentários inline** (`pulls/<n>/comments`) e **0 reviews** (`pulls/<n>/reviews`) em todos os
  26 PRs. Nenhum bot também.
- **8 comentários de conversa** (`issues/<n>/comments`), em `#1`, `#3`, `#6`, `#16`, `#18` (3) e `#22`.
  Todos do **autor dos PRs** (`Lombeira`, Glauco), com assinatura do Claude Code: são atualizações e
  correções do próprio PR, não review de outra pessoa.
- Os 26 PRs têm um autor só e foram mergeados sem review.

**Consequência: nenhuma regra deste arquivo vem de review humana.** Comentários humanos de review
lidos: **0**. Todas as regras vêm da documentação, do código/testes e das descrições e comentários
do autor nos PRs, e cada uma diz de onde veio. As citações `PR #n` são a prova de que a regra é
praticada no repo (o autor fez assim e explicou por quê), não de que um revisor cobrou. Quando
aparecer review de verdade, rodar o levantamento de novo a partir do `#27`.

---

## PRIV — privacidade e LGPD
Lens: `correctness`. O fluxo de dados está no ADR-0001: o que vai e o que não vai para a Anthropic.

- [PRIV-01] 🔴 Um caminho novo ou alterado põe no retorno ao modelo (`outcome["content"]`,
  `result_for_model`, `tool_result`, `build_messages`, system prompt) o nome de aluno ou da equipe:
  coluna `aluno_nome`/`usuario_nome`, resultado de `Database.names`, `class_students`, ou qualquer
  saída de `assistant_private.*` que traga nome → o nome só vai para a tela, no evento SSE `names`;
  o modelo recebe só o id e cita `«aluno:<uuid>»` / `«professor:<uuid>»`.
  *Ex.: `buscar_aluno`/`buscar_equipe` devolvem só ids (PR #17); a planilha manda nomes só no
  evento `names` (PR #5).* `[doc]` `[código: agent.py, tests/test_end_to_end.py]` `[PR #5, #17]`
- [PRIV-02] 🔴 Coluna nova numa view de `assistant.*`, ou `GRANT SELECT (col)` novo para
  `leme_assistant` no fim de `migrations/views.sql`, com nome, CPF, documento, data de nascimento
  crua, contato, endereço, texto livre ou dado de saúde/deficiência → não expor. `persons.birth_date`
  é liberada ao leitor só porque `fn_matriculas` calcula `idade`; a view nunca devolve a data.
  Texto e nome só saem por função `SECURITY DEFINER` de `assistant_private` (ver VIEW-03).
  *Ex.: PR #12 liberou 128 colunas em 27 tabelas e testou `permission denied` em `persons.name`,
  `persons.cpf`, `annotations.content`; PR #17: "sem nome, e-mail ou senha" em `users`.*
  `[doc: ADR "O que não vai"]` `[código: views.sql cabeçalho, test_migrations.py]` `[PR #12, #17]`
- [PRIV-03] 🔴 Texto livre (anotação ou outra fonte nova) chega ao modelo sem passar por
  `student_name_masker` com os alunos das turmas envolvidas, ou sem o corte de
  `annotation_max_chars` → mascarar como `ler_anotacoes` faz (`class_students` → `student_name_masker`
  → corte), e na tela mandar o texto original **sem receita** (`recipe: None`), para ele não ser
  salvo no histórico (`artifact_from_event` só guarda o que tem receita).
  *Ex.: PR #10 (nome completo, primeiro + último, primeiro nome com maiúscula, repetido vira
  `[aluno]`).* `[código: agent.py, masking.py, main.py]` `[PR #10]`
- [PRIV-04] 🔴 Ferramenta que manda linhas para a tela (planilha, gráfico ou nova) devolve ao modelo
  as linhas, os ids das linhas ou os nomes → o modelo recebe só contagem, colunas e um resumo; as
  linhas vão no evento (`file`, `chart`). A descrição da ferramenta no `TOOLS` tem que continuar
  dizendo a verdade sobre isso.
  *Ex.: PR #5 ("O modelo recebe só a contagem e as colunas"), PR #6 (gráfico: "o modelo recebe só
  um resumo").* `[código: agent.py, test_end_to_end.py]` `[PR #5, #6]`
- [PRIV-05] 🔴 Dado novo saindo do serviço para terceiro (novo fornecedor de IA ou roteador, novo
  webhook, novo tipo de conteúdo para a Anthropic, como foram as imagens) sem decisão registrada →
  parar e pedir decisão do Glauco; atualizar o ADR-0001 (o que vai e o que não vai) e o mapeamento
  da LGPD no mesmo PR.
  *Ex.: PR #3 adiou o modelo roteador por ser "mais um fornecedor recebendo as perguntas (LGPD)";
  PR #26 (imagens podem ter nome de aluno) diz que "precisa entrar no mapeamento da LGPD"; PR #24
  (Slack com nomes) registrou a decisão na descrição.* `[doc: ADR "Consequências"]` `[PR #3, #24, #26]`
- [PRIV-06] 🟡 Linhas de resultado, nomes ou imagem gravados em `assistant_app` (`add_message`,
  `save_feedback`, `save_chart`, migration nova) → o banco do Capitão guarda só texto, receitas
  (SQL + configuração) e, nas avaliações, a cópia de pergunta/resposta/consultas; imagem vira a nota
  `[N imagens enviadas]`. Sobe para 🔴 se gravar nome de aluno.
  `[código: migrations/0001_app_tables.sql, main.py question_record]` `[PR #6, #26]`
- [PRIV-07] 🔴 Regra de dados de crianças e adolescentes enfraquecida ou removida do prompt: não
  atribuir condição que os dados não registram, AEE nunca vira deficiência ou diagnóstico,
  desigualdade não prova causa, aviso para grupo com menos de 5 alunos, "possíveis casos" com data
  e trecho nas anotações → manter; mudança aqui é decisão de produto, não ajuste de prompt.
  `[código: prompt.py "Regras que valem sempre", "Anotações", "AEE"]` `[PR #10]`

## SQL — consulta gerada pelo modelo
Lens: `correctness`. O `sql_guard` é a primeira barreira; a definitiva é o usuário `leme_assistant`.

- [SQL-01] 🔴 SQL vindo do modelo, de receita assinada ou de gráfico salvo chega a
  `Database.run_select` sem passar por `validate_select(sql, ALLOWED_VIEWS)` → validar sempre, em
  todo caminho, mesmo com a assinatura válida.
  *Ex.: PR #6: "toda execução passa de novo pelo sql_guard e pelo usuário somente-leitura"
  (`run_recipe`, `chart_points`).* `[doc]` `[código: agent.py, main.py run_recipe]` `[PR #6]`
- [SQL-02] 🔴 Afrouxar `sql_guard.py`: tirar nó de `BLOCKED_NODES`, prefixo de
  `BLOCKED_FUNCTION_PREFIXES`, aceitar schema além de `assistant`, catálogo, `assistant_private`,
  ou a chamada `(schema.f()).coluna` → não afrouxar; se for preciso, justificar e cobrir com caso
  novo em `test_rejects_anything_else`.
  *Ex.: PR #12 fechou a brecha de função com schema que passava pelo filtro.*
  `[código: sql_guard.py, tests/test_sql_guard.py]` `[PR #12]`
- [SQL-03] 🔴 Método novo em `Database` (ou qualquer uso do pool do leitor) executa sem
  `_read_only` (transação `READ ONLY`, `statement_timeout` local, `search_path = assistant`), ou
  executa SQL do modelo por fora de `run_select` (que embrulha em `SELECT * FROM (...) LIMIT n+1`)
  → usar `async with pool.connection() as conn, conn.transaction(): await self._read_only(conn)` e
  `run_select`. `[código: db.py]`
- [SQL-04] 🔴 Valor vindo do modelo ou do request interpolado em SQL (f-string, `format`, `%`), ou
  parâmetro de função privada sem validação → placeholder do psycopg; ids conferidos com
  `UUID_PATTERN`, datas com `DATE_PATTERN`, `LIKE` com `\`, `%` e `_` escapados, números com `int()`.
  *Ex.: `_annotation_filters` recusa `"1; drop table"` (teste em `test_end_to_end.py`).*
  `[código: db.py, agent.py _annotation_filters]`

## AUTH — acesso
Lens: `correctness`. Só e-mail `@leme.tec.br`; dentro do time não há recorte por escola (ADR).

- [AUTH-01] 🔴 Rota nova sem `Depends(current_user)` (a única exceção é `/health`) → exigir
  sessão. `[código: main.py]`
- [AUTH-02] 🔴 Checagem de domínio trocada por `endswith`, substring, papel `admin` ou lista
  embutida; ou `jwt.decode` sem `algorithms=["HS256"]` e `require: exp, id, email` → comparar o
  domínio exato depois do último `@` contra `ALLOWED_EMAIL_DOMAINS`; papel `admin` não basta,
  porque admin de escola não entra.
  *Ex.: `test_rejects_lookalike_domain` (`evil-leme.tec.br`) e `test_rejects_school_admin_outside_team_domain`.*
  `[doc: ADR]` `[código: auth.py, tests/test_limits_auth.py]`
- [AUTH-03] 🔴 Consulta nova ou alterada em `store.py` sem filtrar por `user_id` (ou sem
  `owns_*` antes), ou rota que devolve 403 para recurso de outra pessoa → toda leitura e escrita em
  `assistant_app` é da própria pessoa; recurso alheio ou inexistente responde 404.
  *Ex.: PR #6 (conversas e gráficos), PR #9 (layout ignora id alheio), PR #11 (painéis), PR #24
  (avaliar resposta alheia dá 404), todos com teste e2e de "outra pessoa recebe 404".*
  `[código: store.py, test_end_to_end.py]` `[PR #6, #9, #11, #24]`
- [AUTH-04] 🔴 Salvar ou rodar receita sem `RecipeSigner.verify`, ou aceitando SQL/`kind` vindo
  direto do corpo do request → só receita assinada pelo servidor; `kind` em `query|file|chart`;
  `POST /charts` só aceita `chart`. `[código: recipes.py, main.py]` `[PR #6]`
- [AUTH-05] 🟡 Rota de revisão (casos de 👎, ou dado de várias pessoas) sem `is_reviewer` → 403
  para quem não está em `REVIEWER_EMAILS`. `[código: main.py list_feedback]` `[PR #24]`

## LIMIT — limites de consulta, tempo, linhas e concorrência
Lens: `correctness`. Valores atuais em `config.py`: 8 chamadas de ferramenta e 120 s por pergunta;
5 s e 200 linhas por consulta (100 voltam ao modelo); planilha 5.000 linhas e 15 s; gráfico 2.000
linhas; anotações 300 e 1.000 caracteres cada; 20 perguntas simultâneas por processo, 2 por pessoa.

- [LIMIT-01] 🔴 Ferramenta nova ou ramo novo em `Assistant.run`/`_run_tool` que não conta em
  `tool_calls`, chama o modelo sem passar pela checagem de `deadline`, ou ignora o
  `tool_choice: none` depois do limite → toda chamada de ferramenta conta para
  `max_queries_per_question` e o loop respeita `max_question_seconds`. `[doc]` `[código: agent.py]`
- [LIMIT-02] 🔴 Resultado sem teto de linhas (`fetchall` sem `LIMIT`, ferramenta nova sem
  `max_rows`, função privada sem `p_limite`) ou timeout maior que 5 s fora da planilha → usar os
  limites de `Settings`; só a exportação usa `export_statement_timeout_ms`. Mudar o limite do
  usuário de banco (`ALTER ROLE ... statement_timeout`) é 🔴 também.
  `[doc]` `[código: db.py, config.py, sql/role.sql]` `[PR #5]`
- [LIMIT-03] 🔴 Rota que chama o modelo sem `ConcurrencyLimiter.acquire`, ou `acquire` sem
  `release` no `finally` e no `BackgroundTask` → seguir o padrão do `/ask`; a vaga também expira
  pelo `ttl_seconds` (`max_question_seconds + 30`).
  *Ex.: PR #4 (trava por vaga: liberar uma pergunta não libera a outra da mesma pessoa).*
  `[código: limits.py, main.py ask]` `[PR #4]`
- [LIMIT-04] 🟡 Campo novo de request sem teto (`max_length`, `ge`/`le`, tamanho de imagem) →
  limitar no modelo Pydantic, como `question` (2.000), `history` (20), `images` (4 × 5 MB),
  `comment` (1.000), títulos (120), layout (500 itens). `[código: main.py]` `[PR #26]`
- [LIMIT-05] 🟡 Mudança de `db_pool_max_size`, número de tasks ou `CONNECTION LIMIT` sem conferir
  que pool × tasks no deploy cabe no limite do `leme_assistant` (5 em `sql/role.sql`) → ajustar os
  dois juntos e dizer no PR.
  *Ex.: PR #23: em QA o leitor bateu no limite de 5 conexões durante o deploy.* `[código: sql/role.sql]` `[PR #4, #23]`
- [LIMIT-06] 🟡 Erro de banco numa ferramenta nova sobe como exceção ou volta cru ao modelo → pegar
  `psycopg.Error`, devolver `is_error` e passar por `_error_message` (o timeout vira
  `TIMEOUT_MESSAGE`, que manda refazer com recorte menor).
  `[código: agent.py, tests/test_agent_errors.py]` `[PR #20]`

## LOG — o que entra no log
Lens: `correctness`.

- [LOG-01] 🔴 Log (`logger.*`, `print`, mensagem de exceção logada) com o texto da pergunta, linhas
  de resultado, nomes, texto de anotação, termo de busca de `buscar_aluno`/`buscar_equipe`, imagem ou
  histórico → logar só quem perguntou, hash da pergunta, SQL, duração, linhas e tokens.
  *Ex.: `QueryLog` grava `sql=None` nas buscas por nome e na leitura de anotações; a pergunta entra
  como `question_sha1` e `question_chars`.* `[doc: README "Log", ADR]` `[código: main.py, agent.py]`
- [LOG-02] 🟡 Caminho novo que executa SQL fora do `/ask` (receita, exportação, gráfico salvo) sem
  linha JSON de auditoria com `user_id`, SQL e linhas; ou dado novo da pergunta logado numa linha à
  parte → uma linha `assistant_question` por pergunta (campo novo entra nela, como `images` no
  PR #26) e `assistant_recipe_run` para receitas.
  *Ex.: PR #5: "cada exportação entra no log da pergunta".* `[código: main.py]` `[PR #5, #26]`

## PROMPT — system prompt e ferramentas
Lens: `correctness`. Regras de dados de crianças estão em PRIV-07.

- [PROMPT-01] 🟡 Mudança no formato do marcador de nome (`«aluno:<uuid>»`, `«professor:<uuid>»`)
  no prompt ou nas descrições das ferramentas sem mudar junto `feedback.NAME_MARKER`, o masker e o
  front (leme-app) → mudar tudo no mesmo par de PRs. A instrução tem que dizer as aspas `« »`
  explicitamente.
  *Ex.: PR #23: a primeira versão nova escrevia `aluno:<id>` sem aspas e a tela não trocava pelo nome.*
  `[código: prompt.py, feedback.py, masking.py]` `[PR #23]`
- [PROMPT-02] 🟡 Regra de sigilo do sistema removida ou contradita (o prompt manda citar view,
  coluna, SQL, id, ferramenta ou modelo de IA na resposta) → manter; é a primeira camada, a barreira
  real é o usuário de banco. `[código: prompt.py]` `[PR #3]`
- [PROMPT-03] 🟡 Mudança de prompt sem medição com o Claude real nas perguntas de
  `evals/perguntas.json` (`scripts/avaliar_prompt.py`) ou numa tabela antes × depois na descrição →
  medir e pôr o resultado no PR; o fake (`tests/fake_anthropic.py`) não testa comportamento do modelo.
  `[código: evals/, scripts/avaliar_prompt.py]` `[PR #3, #7, #23]` `[workspace: provar que funcionou]`
- [PROMPT-04] 🟡 Regra de negócio nova no prompt (como contar faltas, acerto do mapa, rede =
  município) sem a fonte no core ou sem conferência com a tela → dizer de qual tela/repositório do
  core a regra veio e como foi conferida.
  *Ex.: PR #16 (1.402 de 1.402 batem), PR #21 (528 de 528), PR #22 (`DBDashboardAbsencesRepository`).*
  `[PR #16, #19, #21, #22]`

## VIEW — views, funções e catálogo
Lens: `reuse-architecture`. Fonte: cabeçalho de `migrations/views.sql`, `leme_assistant/prompt.py`.

- [VIEW-01] 🟡 View nova, renomeada ou com coluna mudada sem atualizar, no mesmo PR:
  `ALLOWED_VIEWS`, `CATALOG` (colunas na mesma ordem da view) e a lista `DROP VIEW IF EXISTS` do
  topo de `views.sql` → atualizar os três. `test_catalog_matches_views` e
  `test_views_are_reapplied_on_every_run` pegam no CI; o revisor aponta antes.
  `[doc: README]` `[código: tests/test_migrations.py]`
- [VIEW-02] 🟡 View criada direto sobre tabela do core (`CREATE VIEW assistant.x AS SELECT ... FROM
  public...`) → casca sobre `assistant_private.fn_<view>()`, `LANGUAGE sql STABLE`, sem
  `SECURITY DEFINER`, para nenhuma migration do core ser travada pelo assistente.
  `test_core_migrations_are_never_blocked_by_the_assistant` pega no CI.
  `[código: views.sql cabeçalho, test_migrations.py]` `[PR #1, #12]`
- [VIEW-03] 🔴 `SECURITY DEFINER` numa `fn_<view>` (contorna os grants por coluna e expõe tudo o
  que o dono lê), ou função privada nova com nome/texto sem `SET search_path = pg_catalog, pg_temp`,
  sem filtro obrigatório (ids, turma, padrão) ou sem parâmetro de limite → `SECURITY DEFINER` só nas
  funções de nome e texto de `assistant_private`, sempre com `search_path` fixo, filtro e limite;
  `REVOKE EXECUTE ... FROM PUBLIC` continua no fim. `[código: views.sql]` `[PR #12]`
- [VIEW-04] 🟡 Função passa a ler tabela ou coluna nova do core sem: `GRANT SELECT (col)` para
  `leme_assistant` e a tabela no `REVOKE` do fim de `views.sql`; a tabela em `sql/role.sql` **e**
  `sql/grant_colunas_leitor.sql` (`WITH GRANT OPTION` para o dono); uma seção "Antes do merge" no PR
  dizendo em quais ambientes o runbook já rodou → incluir tudo. Sem o runbook, o `check_reader` para
  o deploy (a versão anterior fica no ar), mas o deploy trava.
  *Ex.: PR #10, #12, #16, #17, #21.* `[código: migrate.py check_reader, sql/]` `[PR #10, #12, #14, #16, #17, #21]`
- [VIEW-05] 🟡 Coluna de view existente removida ou renomeada → manter a antiga e criar a nova;
  gráficos salvos guardam o SQL e quebram.
  *Ex.: PR #16 manteve `respostas_avaliacoes.etapa`; PR #21 juntou as duas origens "com as mesmas
  colunas".* `[PR #16, #21]`
- [VIEW-06] 🟡 Função nova sem `deleted_at IS NULL` nas tabelas do core que têm a coluna, ou com
  regra de contagem diferente da tela correspondente → filtrar apagados e copiar a regra da tela
  (ver PROMPT-04). `[código: views.sql]` `[PR #16, #21]`
- [VIEW-07] 🟡 Descrição no `CATALOG` que não bate com o dado (origem, quem lança, unidade, quando
  usar) → corrigir; o modelo decide a consulta por ela.
  *Ex.: comentário do autor no PR #22: `faltas_consolidadas` dizia "lançados manualmente", mas é
  resumo recalculado pelo back.* `[PR #16, #22]`
- [VIEW-08] 🟡 View ou consulta pesada (faltas, conteúdos, `generate_series`, junção de calendário)
  sem medição como `leme_assistant`, com o corte de 5 s, em QA ou prod → medir e pôr o tempo no PR;
  se não couber em 5 s, não entra (cálculo noturno é outra decisão).
  *Ex.: PR #18 pausado porque escola e rede estouravam 5 s em prod; PR #20 e #21 com tempos medidos.*
  `[PR #18, #20, #21]`

## MIG — migrations, runbooks e deploy
Lens: `reuse-architecture`.

- [MIG-01] 🟡 Edição de `migrations/NNNN_*.sql` que já foi aplicada → arquivo novo com o próximo
  número; o `migrate` aplica cada um uma vez só (`assistant_meta.schema_migrations`). Só
  `views.sql` é reaplicado a cada deploy. `[código: migrate.py]` `[PR #1]`
- [MIG-02] 🔴 Senha, URL com senha ou token em `sql/`, `.env.example`, `buildspec-ci.yml` (fora
  das credenciais fictícias do CI) ou fixture → senhas vão por `psql -v` e Secrets Manager.
  `[código: sql/role.sql cabeçalho]` `[workspace: nunca segredo em arquivo versionado]`
- [MIG-03] 🔴 Grant cruzando usuários: `leme_assistant` ganhando acesso a `assistant_app` ou
  `assistant_meta`, `leme_assistant_app` ganhando `assistant`, `assistant_private` ou `public`, ou
  qualquer um ganhando escrita fora do próprio schema → cada usuário só no que é dele.
  `[código: sql/role.sql, sql/role_app.sql]` `[PR #6]`
- [MIG-04] 🟡 `migrate.py` mudando a ordem: `views.sql`, `GRANT_READER` e `check_reader` têm que
  ficar na mesma transação, com `SET LOCAL ROLE leme_assistant`, para a falha desfazer a troca e
  parar o deploy → manter. `[código: migrate.py, test_deploy_stops_and_keeps_the_previous_views...]` `[PR #14]`
- [MIG-05] 🟡 `/health` voltando a `SELECT 1` ou deixando de ler uma view como o leitor → manter a
  leitura de `assistant.disciplinas`, para o ECS não promover task sem acesso. `[código: main.py]` `[PR #14]`
- [MIG-06] 🟡 Banco do histórico (`APP_DATABASE_URL`) virando dependência obrigatória (o serviço
  cai sem ele) → `open_store` devolve `None`, as rotas usam `require_store` (503) e o `/ask` segue
  sem salvar. `[código: main.py, test_limits_auth.py]` `[PR #6]`

## TOOL — ferramentas do modelo e eventos
Lens: `reuse-architecture`.

- [TOOL-01] 🟡 Ferramenta nova sem o conjunto completo: entrada em `TOOLS`, ramo em `_run_tool`
  validando tipos (`isinstance`) e devolvendo `is_error`, método no `DataSource` (Protocol) e no
  `Database`, roteiro em `tests/fake_anthropic.py` e o nome no conjunto conferido em
  `test_answers_with_real_query_names_and_streamed_text` → incluir todos. `[código: agent.py, tests/]`
- [TOOL-02] 🟡 Busca de nomes, máscara ou mensagem de erro reimplementada → usar
  `Database.names(collect_uuids(result))`, `student_name_masker` e `_error_message`.
  `[código: db.py, masking.py, agent.py]`
- [TOOL-03] 🟡 Evento SSE novo ou campo novo num evento sem atualizar a tabela de eventos do README
  e sem decidir se vai para o histórico (`artifact_from_event`: só o que tem receita) → atualizar e
  decidir de forma explícita. *Ex.: PR #24 guarda `query_error` mas não o devolve no histórico.*
  `[doc: README "API"]` `[código: main.py]` `[PR #24]`

## TEST — testes
Lens: `reuse-architecture`.

- [TEST-01] 🔴 Mudança num caminho por onde dado de pessoa pode chegar ao modelo (ferramenta,
  função privada, texto livre, imagem) sem teste e2e que confere `fake_anthropic.requests_seen` e
  afirma que nenhum nome aparece no que foi enviado ao modelo → escrever o teste; o ADR cita esse
  teste como controle. `[doc: ADR "Nomes"]` `[código: test_end_to_end.py]` `[PR #5, #10, #17]`
- [TEST-02] 🔴 `tests/fixtures/core_dev.sql.gz` alterado sem `scripts/refresh_ci_fixture.sh` (que
  sanitiza senhas, tokens, hashes e CPFs) → regenerar pelo script e dizer no PR que a busca por
  segredos voltou vazia. `[código: scripts/refresh_ci_fixture.sh]` `[PR #15]`
- [TEST-03] 🟡 Mudança em `sql_guard.py` sem caso novo em `test_accepts_reads_over_catalog_views`
  ou `test_rejects_anything_else` → cobrir os dois lados. `[código: tests/test_sql_guard.py]` `[PR #12]`
- [TEST-04] 🟡 Variável de ambiente nova de teste de banco sem entrar no `buildspec-ci.yml`, ou teste
  de banco sem `skipif` pela variável → o CI precisa rodar tudo, e localmente sem banco o teste é
  pulado. `[doc: README "Testes"]` `[código: buildspec-ci.yml]` `[PR #15]`
- [TEST-05] 🟡 Teste e2e que reusa `user_id` de outro teste (fica dependente de ordem, do limite por
  pessoa ou de dado da rodada anterior) → `user_id` próprio por teste.
  *Ex.: PR #10: o teste do painel falhava na segunda rodada local.* `[código: test_end_to_end.py]` `[PR #10]`
- [TEST-06] ⚪ Teste novo de proteção (permissão, checagem do deploy) sem dizer no PR que ele falha
  sem a correção → mostrar que falha sem e passa com.
  *Ex.: PR #13 ("sem o grant: 9 testes falham"), PR #14 ("com a checagem desligada, esse teste falha").*
  `[PR #13, #14]` `[workspace: provar que funcionou]`

## DOC — documentação e legibilidade
Lens: `readability`.

- [DOC-01] 🟡 PR que muda limite, ferramenta, evento, usuário de banco ou o que vai para a
  Anthropic/terceiros sem atualizar README e ADR-0001 → atualizar no mesmo PR (ver Lacunas: hoje os
  dois estão atrás do código). `[doc]` `[PR #4, #10, #24, #26]`
- [DOC-02] 🟡 Regra repetida em dois lugares do prompt, ou fora da camada certa (regras que valem
  sempre, recorte, como consultar, por assunto, formato, catálogo) → um lugar só, na camada certa.
  `[código: prompt.py]` `[PR #23]`
- [DOC-03] ⚪ Comentário que repete o código ou narra o óbvio; densidade acima de ~10% → comentário
  só para armadilha e porquê medido (como o docstring de `ConcurrencyLimiter` e de `check_reader`).
  `[workspace: 8 a 10% de comentário]`
- [DOC-04] ⚪ Mensagem para a pessoa (`HTTPException`, evento `error`, texto devolvido ao modelo
  para ele repassar) em inglês ou com termo técnico → português, linguagem de escola, dizendo o que
  fazer ("Tente um recorte menor"). `[código: main.py, agent.py, limits.py]`
- [DOC-05] ⚪ Nome de ferramenta, parâmetro de ferramenta, view ou coluna de view em inglês → o que
  o modelo vê é em português (`consultar_sql`, `eixo_x`, `turma_id`); o código interno segue em
  inglês. `[código: agent.py, views.sql]`

---

## Lacunas

1. **Nenhuma review humana no corpus.** 26 PRs, 0 comentários inline, 0 reviews; os 8 comentários
   são do próprio autor. Nenhuma regra tem frequência de review; as severidades são inferidas da
   documentação. Refazer quando houver revisores (a partir do `#27`).
2. **README atrasado em relação ao código** (DOC-01 já seria achado hoje):
   - limites: README diz "no máximo 4 perguntas simultâneas por processo e uma por pessoa"; o código
     e o `.env.example` têm 20 e 2 desde o PR #4;
   - diagrama "loop do Claude com 2 ferramentas"; hoje são 6 (`consultar_sql`, `gerar_planilha`,
     `gerar_grafico`, `buscar_aluno`, `buscar_equipe`, `ler_anotacoes`);
   - "o modelo só enxerga as views... que não têm... texto livre de aluno": desde o PR #10 o texto das
     anotações vai ao modelo (mascarado), e desde o PR #26 vão imagens que podem ter nome;
   - "SELECT nesses schemas": desde o PR #12 o leitor também lê colunas de `public` por grant de
     coluna (inclusive `persons.birth_date`, para calcular idade);
   - a tabela de eventos SSE não tem `file`, `chart`, `conversation` nem `message`.
3. **ADR-0001 atrasado** (status ainda "Proposto"): diz que "texto de anotação" não vai para a
   Anthropic (o PR #10 manda mascarado); não registra as imagens (PR #26, que pede o mapeamento da
   LGPD), nem o aviso no Slack com nomes de alunos (PR #24, decisão registrada só na descrição do PR).
   PRIV-05 cobre o caso novo, mas os três casos atuais ainda não estão no ADR.
4. **Nome que a própria pessoa escreve** na pergunta ou no histórico (`history` vem do cliente) vai
   ao modelo sem máscara. Não há regra no código nem na documentação; não virou regra aqui.
5. **`max_queries_per_question` conta todas as ferramentas**, não só consultas, e o README fala em
   "8 consultas". O comportamento está coberto em LIMIT-01, mas a semântica não está documentada.
6. **Teto efetivo de concorrência** é `max_concurrent_questions × réplicas` (docstring de `limits.py`);
   não há regra para quem muda o número de tasks no terraform-infra.
7. **Sem teste** para: `max_queries_per_question` e `max_question_seconds` no loop do agente; teto de
   `max_rows_to_model`; ausência de pergunta/nomes no log (LOG-01 depende só de review).
8. **Severidades de VIEW-01, VIEW-02 e VIEW-04** ficaram em 🟡 porque o CI (`test_migrations.py`) e o
   `check_reader` pegam o erro antes do ar. Se o CI deixar de rodar os testes de banco, sobem para 🔴.
9. Regras de comportamento do modelo (PROMPT-03, PROMPT-04) dependem de medição com o Claude real,
   que o CI não faz; `evals/perguntas.json` tem 10 perguntas e não roda automaticamente.
