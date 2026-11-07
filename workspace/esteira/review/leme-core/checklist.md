# Checklist de review: leme-core

Os revisores de cada lente aplicam as regras abaixo às linhas alteradas de um diff do `leme-tech/leme-core`
(PHP 8.2, Laravel 11, DDD + Clean Architecture).

**Formato:** cada regra é `[ID] <sev> sinal → correção`. Os IDs são estáveis: nunca renumere. Regra nova
entra no fim da categoria, com o próximo número.

**Severidade padrão (`<sev>`):** o revisor usa a severidade da regra, a não ser que o caso concreto peça
outra (aí justifica em uma linha):
- 🔴 **blocker**: correção, ou a mudança quebra comportamento (inclui furo de acesso e dado de aluno exposto).
- 🟡 **should-fix**: convenção que o time cobra de forma consistente.
- ⚪ **nit**: opcional, baixo impacto.

**Lentes (`Lens:` em cada categoria):** a review roda três revisores em paralelo, cada um dono de um
conjunto disjunto de categorias, e cada um aplica **só** as categorias com a sua lente:
- `correctness`: ACCESS, VALIDATION, SQL, MIGRATION, TEST.
- `reuse-architecture`: DDD, DOMAIN, API, REUSE, DOCS.
- `readability`: NAMING, CLEAN.

**Escopo:** só o que lint, formatter e PHPStan não pegam de forma determinística. Formatação, linha em
branco, ordem de import e tipo faltando não entram aqui.

**Fonte da verdade:** `.github/copilot-instructions.md` (chamado aqui de *copilot-instr*), `AGENTS.md`,
`.github/agents/review.agent.md` (*review.agent*), `docs/context/*.md` e `docs/adr/`. Quando uma regra
repete um desses arquivos, ela aponta para ele em vez de copiar tudo; este checklist guarda a prioridade e
os exemplos. Se `copilot-instr` e `AGENTS.md` divergirem, vale o `AGENTS.md` (ele mesmo diz isso; ver MIG-01).

---

## ⚠️ Proveniência: leia antes de confiar numa frequência

**Faixa coberta: `#1` a `#883`, todos os 857 PRs mergeados** (raspados em 07/11/2026 via
`gh api .../pulls/<n>/comments` e `.../reviews`).

- Depois de tirar bots (`[bot]`, Copilot, github-actions) e respostas do autor do PR, sobram **85
  comentários** de conta humana em **25 PRs**.
- Desses, **6 são reviews "🤖 Julius AI"** postadas pela conta `Lombeira` (#509, #514 ×3, #515, #516):
  texto gerado por IA, tratado aqui como bot e **fora das frequências**.
- Mais 2 são só aprovação sem conteúdo (#70 "Top", #823 "LGTM!").
- Ficam **77 comentários humanos acionáveis em 19 PRs**, de três revisores: `fainohub` (49, PRs
  #66 a #126, o começo do repo), `GustavoFaino` (16, #807 a #883) e `Lombeira` (14, #863 a #883).
- A amostra é **pequena e concentrada**: #66 (14), #77 (10), #807 (9), #883 (6), #863 (6). Entre #127 e
  #806 não há nenhum comentário humano inline; a maior parte dos PRs é merge sem thread.
- O Copilot comenta muito nos PRs recentes. Não entra nas contagens, mas quando um humano **endossou** um
  comentário dele isso está citado (ex.: #872).

Leia as frequências como "o que apareceu nesta amostra", não como peso real. Regra marcada *(doc)* vem só
da documentação do repo: não é errada, só não foi confirmada por review humana. Não a retire por falta de
ocorrência.

---

## DDD: camadas e onde mora cada responsabilidade
Lens: `reuse-architecture`. Ver *copilot-instr* §Arquitetura e §Ao gerar código, e *review.agent* §Arquitetura.

- [DDD-01] 🔴 Regra de negócio, decisão de domínio ou montagem de erro dentro de Controller → Controller só
  faz Request → UseCase → Response; a regra vai para o UseCase ou para a entidade. *(doc: copilot-instr
  regras 2 e 5; review.agent lista como bloqueante)*
- [DDD-02] 🟡 Controller ou UseCase autentica por conta própria (`$this->authUseCase->authenticate($request->token())`,
  parâmetro `$userToken`) ou injeta `UserUseCase`/`AuthUseCase` só para saber quem é o usuário → o Request
  estende `AbstractRequest`, que já traz o id do usuário autenticado; o UseCase recebe `string $userId`. Se
  a regra depende do papel, passe o `userId` no contrato e resolva o papel no repositório.
  *(4 comentários em 3 PRs. #94: "Estendendo da classe AbstractRequest vc já consegue pegar o Id do usuário
  e não precisa autenticar via token"; #126: "Vc pode só passar o userId no contrato e buscar a role desse
  user no repositório, assim não precisa chamar o UserUseCase em outros serviços")*
- [DDD-03] 🟡 `new` de implementação concreta dentro de UseCase (`new emailService(new awsSes)`), classe
  "service" intermediária só para escolher implementação, ou interface de repositório fora de
  `Domain/Repository` → interface em `{Module}/Domain/Repository`, implementação em `Infrastructure`,
  injeção pelo construtor e binding no `{Module}ServiceProvider`. Falta de binding é 🔴 (quebra em runtime).
  *(4 comentários, #66: "Aqui vc pode usar inversão de dependência, recebendo o UserEmailRepository no
  construtor, ai vc não precisa dar um new"; "Da pra colocar essa interface em User/Domain/Repository já que
  é um contrato para um repositório")*
- [DDD-04] 🔴 Transação (`beginTransaction`, `DB::transaction`) aberta em UseCase ou Controller, ou endpoint
  que grava em mais de um passo fora de uma transação única → a transação pertence ao método do repositório
  da operação composta; valide as regras de negócio antes de abrir. *(doc: copilot-instr §Atomicidade)*
- [DDD-05] 🟡 UseCase devolvendo array formatado para o front (`label`, `options`, estrutura de tela) ou
  chamando outro UseCase para compor a resposta HTTP → UseCase devolve entidade de domínio; quando o
  endpoint agrega dados de vários UseCases, o Controller chama cada um e entrega as entidades ao Response.
  *(doc: review.agent §Arquitetura, listado como bloqueante lá)*
- [DDD-06] 🟡 UseCase de update que faz `findById` de novo depois de persistir → devolva a entidade mutada
  em memória. Exceção: create com associações que não estão em memória. *(doc: copilot-instr §Padrão de
  Retorno, regra 12)*
- [DDD-07] 🟡 Import novo que cria dependência entre módulos num ciclo que ainda não existe (ou `Shared`
  importando de módulo) → inverter a dependência ou mover o contrato. Já existem Academic ↔ School,
  Academic ↔ Notification, Exam ↔ LearningMap, User ↔ School: não crie outros. *(doc: docs/context/modulos.md)*

## DOMAIN: entidades, coleções e value objects
Lens: `reuse-architecture`.

- [DOMAIN-01] 🟡 Lista de entidades como `array` (atributo, retorno de UseCase, PHPDoc `Foo[]`) → classe
  plural que estende `Illuminate\Support\Collection` (`Bnccs`, `EducationalTypes`), como
  `App\Shared\Domain\Entity\ClassLevels`. Confira também que o `Collection` importado é o do Laravel.
  *(3 comentários em 3 PRs. #807: "De preferência, utilizar uma classe que estende
  Illuminate\Support\Collection... 'Bnccs extends Collection'"; #877: "eu trocaria o retorno de array para
  uma extensão de Collection 'EducationalTypes'"; #81: import de `Barryvdh\...\Collection` por engano)*
- [DOMAIN-02] 🟡 Entidade guardando primitivo onde já existe enum/VO no domínio (`string $subjectId` em vez
  de `Subject`) → tipar com o VO; a factory converte com `Subject::from($data['subjectId'])`.
  *(3 comentários, #81: "Utilizar o objeto de valor que tem dentro do domínio")*
- [DOMAIN-03] 🟡 Atributo sem o qual a entidade não existe declarado como nullable, ou atributo novo fora
  do construtor (`private ?string $x = null;` setado depois) → obrigatório e não nulo no construtor, junto
  dos demais. *(2 comentários em 2 PRs. #81: "acho que esses atributos são obrigatórios, sem eles não temos
  uma aula"; #826: "vale incluir $notifiedByUserName dentro do construtor junto com os outros atributos,
  para manter o padrão")*
- [DOMAIN-04] 🟡 Array associativo com os campos explicados em comentário, passado entre camadas → montar
  entidade ou VO. *(1 comentário, #867: "ele tem o mal costume de colocar arrays e comentar quais os campos
  deles, ao invés de montar entidades")*
- [DOMAIN-05] 🟡 Exceção de negócio genérica (`RuntimeException`, `Exception`) fora de repositório DB →
  `{Descritivo}Exception` estendendo `App\Shared\Domain\Exception\DomainException`. *(doc: copilot-instr
  §Padrões; review.agent lista como bloqueante)*
- [DOMAIN-06] ⚪ Retorno `?Entity` em método que nunca devolve `null` (lança exceção quando não acha) →
  tirar o `?` do tipo. *(1 comentário, #77: "Aqui nunca vai ser retornado nulo, sempre a entidade ou uma
  exception")*

## ACCESS: autorização, LGPD e superfície de ataque
Lens: `correctness`.

- [ACCESS-01] 🔴 Endpoint ou UseCase que lê ou grava dado de turma ou de aluno (inclusive dado derivado,
  como o tipo de ensino AEE) sem checar se o usuário pode ver a turma → chamar
  `ClassAccessPolicy::canView($user, $class)` antes de qualquer consulta e lançar
  `ForbiddenClassAccessException` (403); testar a negação por papel. Para conteúdo, `ContentAccessPolicy`.
  Nunca regra "professor da turma" ad hoc nem Gate/Policy do Laravel no Controller.
  *(ADR-0001 e AGENTS.md. #872: o revisor endossou o comentário do Copilot pedindo `ClassAccessPolicy` no
  `findAvailableCategories` com "Incluindo essa validação já daria para fazer o merge")*
- [ACCESS-02] 🔴 Diff que afrouxa checagem de acesso existente (remove policy, amplia papel, troca turma
  por escola) sem ADR → exigir ADR. *(doc: AGENTS.md §Nunca; ADR-0001 descarta "liberar por escola")*
- [ACCESS-03] 🔴 `userId` lido do body ou da query → vem do header `X-User-Id` via `AbstractRequest`.
  Rota nova fora do grupo com middleware `auth` → mover para dentro. *(doc: review.agent §Segurança)*
- [ACCESS-04] 🔴 Log, exceção ou chamada externa com nome, CPF, e-mail ou outro dado de aluno; dado
  pessoal real em teste, seed ou fixture → só ids internos no log (com prefixo do fluxo, ex. `[SED Sync]`)
  e dados fictícios de `database/seeders/Development/` e `tests/Support/`. *(doc: AGENTS.md §Nunca;
  docs/context/testes-e-instrumentacao.md)*
- [ACCESS-05] 🟡 Response que expõe mais do aluno do que a tela usa → listagem com aluno devolve `id`,
  `name`, `number`, `status` (copilot-instr regra 14); endpoint de analytics devolve só `id` e `name`
  (exceção do AGENTS.md). *(doc)*
- [ACCESS-06] 🟡 Endpoint novo de upload ou de escrita barata sem `throttle` nem limite por usuário →
  propor `->middleware('throttle:...')`. Costuma não travar o PR, mas tem que ser registrado.
  *(1 comentário, #883: "qualquer pessoa logada pode chamar isso em loop e encher o bucket, porque não tem
  `throttle`... Fica pra discussão, não precisa travar o PR")*
- [ACCESS-07] 🔴 Backend grava uma URL de arquivo que veio do cliente sem conferir que aponta para o nosso
  bucket e para a pasta da entidade (ex. `annotations/`) → validar prefixo/host antes de gravar.
  *(1 comentário, #883: "o back precisa checar se ela aponta pro nosso bucket, dentro de `annotations/`.
  Senão o cliente manda qualquer URL e a gente grava")*
- [ACCESS-08] ⚪ Upload gravado no S3 antes de existir a entidade dona, sem limpeza de órfãos → registrar
  card; o caminho combinado é gravar em `<entidade>/tmp` com lifecycle e mover ao associar.
  *(2 comentários no mesmo thread, #883: "se a pessoa sobe e desiste... o arquivo fica no S3 pra sempre";
  resposta: card LM-2846)*

## VALIDATION: Form Requests e entrada
Lens: `correctness`.

- [VALID-01] 🔴 Controller recebendo `Illuminate\Http\Request` ou `FormRequest` direto → classe
  `{Action}{Entity}Request extends AbstractRequest`, mesmo com `rules()` vazio, com getters tipados
  (`code(): string`) para os parâmetros. *(2 comentários em 2 PRs. #94: "Precisa dar um extends da classe
  ...AbstractRequest.php que já traz o id do usuário autenticado"; #77: "Outra abordagem seria criar uma
  request customizada pra isso SearchBnccRequest"; regra em copilot-instr §Padrões)*
- [VALID-02] 🔴 `page`/`perPage` sem `min:1` e sem teto, ou teto com número literal → `perPage` com
  `'max:'.self::MAX_PER_PAGE` e `page` com `'max:'.$this->maxPage($this->perPage())`, sempre com `numeric`
  junto do `min` (senão o Laravel compara tamanho de string). `perPage` negativo ou nulo vira "sem limite"
  (`limit()` ignora valor < 0 e `limit(null)`), e `page` grande demais estoura o offset. Ao corrigir uma
  listagem, alinhe as irmãs no mesmo PR.
  *(3 comentários em 2 PRs. #863: "`?perPage=-1` devolve todas as linhas, e `?perPage=99999999` faz o
  mesmo"; #867: "Este request ficou de fora do alinhamento que o PR fez nos outros: o `page` aqui não tem o
  `maxPage()`"; regra em AGENTS.md)*
- [VALID-03] 🔴 Campo de enum validado só como inteiro, ou com faixa escrita à mão (`min:1|max:9`), e
  convertido depois com `::from()` → `ValueError` vira 500. Validar com `Rule::enum(X::class)` ou
  `in:` derivado de `array_column(X::cases(), 'value')`. *(1 comentário, #863: "`?subjectId=99`... o
  `ContentController` chama `Subject::from(99)`, que lança `ValueError`. O `ExceptionHandler` transforma
  isso em 500"; regra em copilot-instr §Padrões)*
- [VALID-04] 🔴 `::tryFrom()` em valor que já foi validado no Request, sem tratar o `null` → `::from()`.
  `tryFrom` só com `?? throw new XNotFoundException()`. *(doc: review.agent, listado como bloqueante)*
- [VALID-05] 🟡 Regra de inteiro ou limite diferente da usada nos requests irmãos (`integer` + `(int)` num,
  `INTEGER_RULE` + `toInteger()` no outro; `max:365` contra `MAX_DAYS_RANGE`) → usar as constantes e
  helpers do `AbstractRequest`, iguais em todo o módulo. *(1 comentário, #867)*
- [VALID-06] ⚪ Regex de validação ancorado com `$` → `\z` (ou modificador `D`); `$` aceita `"1\n"`.
  *(1 comentário, #863)*

## API: contrato HTTP e rotas
Lens: `reuse-architecture`.

- [API-01] 🟡 Create em `PUT` (ou verbo trocado) → `POST` para criar, `PUT`/`PATCH` para atualizar.
  *(2 comentários, #99: "Os creates devem ser posts")*
- [API-02] 🟡 Rota fora do padrão de recurso: prefixo no singular, sufixo de chave (`{id}/id`,
  `{code}/code`), sub-recurso em grupo próprio (`classrooms/class/{classId}`), prefixo genérico
  (`template`) → recurso no plural, sub-recurso aninhado (`/v2/classes/{id}/classrooms`), prefixo que diz o
  contexto (`notifications/emails/templates`). *(4 comentários em 3 PRs. #77: "podemos mudar o grupo pra
  deixar sempre no plural os recursos de API"; #82: "Esse da pra jogar dentro do grupo de class... O
  endpoint vai ficar `/v2/classes/{id}/classrooms`"; #69)*
- [API-03] 🟡 Filtro opcional de listagem como segmento de path, ou obrigatório/validado com tamanho mínimo
  → query param opcional (`/v2/bnccs?code=XPTO`); sem filtro, lista tudo. *(3 comentários, #77: "Acho que
  não precisamos adicionar essa validação, se ele não enviar nenhum código listamos tudo... O código fica
  como opcional para filtrar")*
- [API-04] 🟡 Campo na resposta que o front não usa naquela tela ou que já sabe (ele mesmo enviou) →
  remover. Listagem não carrega detalhe que o front busca ao abrir o item. *(2 comentários, #807: "faz
  sentido remover o bncc nessa listagem"; "daria para remover o campo 'period', em teoria o front já sabe
  esse dado"; ADR-0002 segue a mesma linha: um endpoint por tela ou ação)*
- [API-05] 🔴 Controller montando resposta de erro à mão (`response()->json(['statusCode' => 422, ...])`)
  → lançar a `DomainException` e deixar o `ExceptionHandler` formatar. *(doc: copilot-instr regra 13)*
- [API-06] 🟡 Opções de enum (`options`, `labels`) dentro da resposta de listagem → endpoint próprio de
  opções, declarado antes das rotas com `{id}` no grupo. *(doc: copilot-instr regra 15)*
- [API-07] 🟡 Response sem `fromEntity()`, ou coleção serializada inline → `{Entity}Response::fromEntity()`
  e `{Entities}Response::fromEntity()` delegando para o singular. *(doc: copilot-instr §Padrões)*

## SQL: repositórios DB e performance
Lens: `correctness`.

- [SQL-01] 🔴 Escrita no banco sem o padrão `try { beginTransaction ... commit } catch (Throwable) {
  rollBack; throw new DBException('Erro ao {verbo} {entidade}', 500, $e) }`, ou com `transaction(closure)`
  ou `RuntimeException` → aplicar o padrão de *copilot-instr* §Transações. *(doc)*
- [SQL-02] 🔴 `->delete()` em tabela com soft-delete, ou leitura sem `->whereNull('<tabela>.deleted_at')`
  → `update(['deleted_at' => now()])` e filtro em toda leitura. *(doc: review.agent, bloqueante. #126
  mostra o filtro em uso no `DBClassroomRepository`)*
- [SQL-03] 🔴 Query dentro de loop, ou número de queries que cresce com o volume (N+1); agregação feita em
  PHP sobre o resultado de várias queries → join/agregação em SQL, número de queries fixo e testado.
  *(doc: review.agent §Performance; AGENTS.md; ADR-0002 descarta "reaproveitar o aggregate em loop" por
  custo O(provas × alunos × questões))*
- [SQL-04] 🟡 Leitura pesada (analytics, relatório) na conexão principal ou sem retry → conexão
  `leme-db-replica` com retry, como em `DBContentAnalyticsRepository::retryReplicaQuery()`. *(doc: AGENTS.md,
  ADR-0002)*
- [SQL-05] 🟡 Filtro condicional montado com `if` solto sobre o builder (`if (! $x) { $q->where(...) }`) →
  `->when($cond, fn ($q) => $q->where(...))`. *(1 comentário com suggestion, #126; regra em copilot-instr
  §Padrões de Repositório)*
- [SQL-06] 🔴 Parâmetro de limite que chega `null` do Controller e sobrescreve o default do UseCase
  (`limit(null)` = sem limite) → não repassar `null` explícito, ou aplicar o default no Request.
  *(1 comentário, #863: "sem `perPage`, os alertas de nota passam `null` explicitamente... Isso sobrescreve
  o default `= 10`, e `limit(null)` significa sem limite")*
- [SQL-07] 🟡 Eloquent Model ou SQL raw onde o Query Builder resolve → Query Builder no repositório DB.
  *(doc: copilot-instr §Estilo; review.agent)*

## MIGRATION
Lens: `correctness`.

- [MIG-01] 🔴 Migration existente alterada → nova migration. Mudança de schema sem migration, ou migration
  sem o ticket no nome do arquivo → criar com o ticket (ex.
  `2026_10_23_120000_add_position_to_learning_map_exam_lm2704.php`). O schema base é do leme-api; as do core
  vão para `core_migrations`. *(doc: AGENTS.md. Atenção: o copilot-instr ainda diz "Sem migrations no
  core"; está desatualizado e vale o AGENTS.md)*
- [MIG-02] 🟡 Coluna nova obrigatória em tabela com dados, sem backfill → migration com backfill no padrão
  do exemplo `..._lm2704.php`. *(doc: AGENTS.md §Exemplos)*

## TEST
Lens: `correctness`. Regras completas em *copilot-instr* §Testes e `docs/context/testes-e-instrumentacao.md`.

- [TEST-01] 🔴 Teste que passa pelo motivo errado (o 422 sai por outro campo, a asserção não isola o que o
  nome diz) → payload válido trocando só o campo sob teste e `assertJsonValidationErrors('<campo>')` ou
  `assertJsonPath('message', ...)`. *(1 comentário, #883: "Esse teste tá passando por tabela 🙃 O 422 sai
  de qualquer jeito, porque o payload não tem nenhum campo obrigatório da anotação")*
- [TEST-02] 🔴 Teste que fixa como válido o comportamento que é o próprio bug (`-1`/`0` aceitos para
  `perPage`, `null` como default sem limite) → mover para o lado dos inválidos junto com o fix.
  *(2 comentários, #863)*
- [TEST-03] 🟡 Mock que recebe argumentos sem `->with(...)`, ou factory com `Mockery::type('array')` /
  matcher que olha só um campo → `->with(...)` em todo mock (inclusive nos chamados antes da exceção) e
  `Mockery::on(fn ($d) => ...)` com todos os campos relevantes; `array_key_exists` para `present|nullable`.
  *(doc: copilot-instr §Regras de mock. É o tema mais frequente do Copilot nos PRs recentes, ex. #877)*
- [TEST-04] 🟡 Feature nova ou alterada sem os dois níveis: Unit do UseCase (caminho feliz, cada exceção,
  cada parâmetro opcional) e Feature do Controller (200, vazio, 404, 401/403, 409, um 422 por campo
  obrigatório, por enum inválido e por `present|nullable` ausente) → completar. Cenário de spec sem teste é
  🔴 pelo review.agent. *(doc)*
- [TEST-05] 🟡 SQL novo ou alterado testado só com repositório mockado → teste com banco real em
  `tests/Feature/<Módulo>/Persistence/`, apontando a réplica para a conexão principal, e contagem de queries
  quando a leitura é pesada (mais harness em `harness/<feature>/`). *(doc: testes-e-instrumentacao.md)*
- [TEST-06] 🔴 Teste ou ambiente de teste que chama integração real (SED, Herby, Twilio, SendGrid, Slack,
  S3) ou lê config do `.env` local → mock e `.env.testing` versionado com valores fictícios.
  *(1 comentário, #882: "o Laravel lê o `.env` local... local e CI rodam com configs diferentes"; regra em
  AGENTS.md)*
- [TEST-07] ⚪ Teste novo com `/** @test */` ou sem `Mockery::close()` no tearDown → `#[Test]` e tearDown.
  *(doc)*

## REUSE
Lens: `reuse-architecture`.

- [REUSE-01] 🟡 Regra recriada à mão quando já existe helper no domínio (`in_array($user->role(), [...])`
  em vez de `$role->isTeacher()`; busca linear numa coleção indexada) → usar o que existe; procurar antes
  em `Shared` e no repositório irmão. *(3 comentários em 2 PRs. #126: "Tem uma função dentro da role,
  isTeacher da pra usar ela pra simplificar esse código"; #827: "daria para simplificar com:
  $sender = ... $senders->get($sentByUserId)")*
- [REUSE-02] 🟡 String repetida (pasta do storage, chave de config) mesmo depois de criar a constante →
  todos os usos passam pela constante. *(1 comentário, #883: "a `STORAGE_FOLDER` nasceu, mas o `create()` e
  o `delete()` ainda têm `\"annotations/\"` escrito na mão")*

## DOCS: spec e documentação de contexto
Lens: `reuse-architecture`.

- [DOCS-01] 🟡 Feature criada ou alterada sem criar/atualizar `specs/{module}/{feature}.md` (ou spec com
  versão antiga acumulada, seção duplicada) → spec só com o estado atual, a partir de `specs/_template.md`.
  *(doc: copilot-instr regra 11)*
- [DOCS-02] 🟡 PR que muda arquitetura, convenção ou módulo sem atualizar `AGENTS.md` e `docs/context/`
  → atualizar junto. Decisão de acesso ou de desenho de endpoint sem ADR → ADR em `docs/adr/`. *(doc:
  AGENTS.md)*

## NAMING
Lens: `readability`. Glossário em `docs/context/modulos.md`.

- [NAMING-01] 🟡 Entidade, campo ou classe nova com nome que não espelha o glossário ou a entidade
  equivalente de outro módulo (`BnccSkill`, `Hability`, `LessonSlot`, `bnccId` para código) → usar o nome
  do domínio (`Bncc`, `ClassroomSlot`, `code`). Termos reservados (`period` = período letivo, `class` =
  turma, `classroom` = aula) não podem ganhar outro sentido.
  *(6 comentários em 2 PRs. #807: "Vale renomear para algo do tipo 'ClassroomSlot' para manter o padrão
  de nome que usamos para representar uma aula"; "vale renomear 'period', pois é um nome interno que
  utilizamos para períodos letivos"; #75: "Alterar em todo lugar que chama Hability para Bncc")*
- [NAMING-02] 🟡 Request/Response cujo nome não diz qual endpoint atende, ou que não forma par com o irmão
  (`ContentsAnalyticsResponse` ao lado de `ContentAnalyticsListRequest`; `ContentAnalyticsRequest` usado no
  `getIndicators`), ou nome abstrato (`indicators`) → `{Nome}ListRequest`/`{Nome}ListResponse`, nome que
  diz o que a tela é (`dashboard` é o termo já usado). *(2 comentários, #807)*
- [NAMING-03] 🟡 Método de UseCase/repositório com nome que não segue o padrão (`findByBncc`,
  `indexByCode`) → `findById`, `findByCode` para um; `search`/`index` para listagem filtrada.
  *(4 comentários em 2 PRs, #75 e #77, todos com suggestion)*
- [NAMING-04] 🟡 Classe de infraestrutura nomeada pelo fornecedor sem o contrato (`SendGrid`, `awsSes`,
  `emailServiceRepository`) → `{Fornecedor}{Contrato}` implementando a interface do Domain
  (`SendGridUserEmailRepository implements UserEmailRepository`); DB: `DB{Entity}Repository`.
  *(3 comentários, #66)*
- [NAMING-05] ⚪ Campo de resposta genérico (`cause`, `proposal`) ou diferente entre GET e PATCH da mesma
  feature → nome específico e igual nos dois. *(doc: copilot-instr regra 16)*

## CLEAN: código morto e ruído
Lens: `readability`.

- [CLEAN-01] 🟡 Método, factory, request ou classe adicionada sem nenhum uso (`git grep` só acha a
  declaração) → remover, ou tirar do PR. *(5 comentários em 4 PRs. #807: "Não encontrei um uso desse
  método, daria para remover"; #863: "nenhum controller o usa... Dá para tirar do PR ou apagar a classe";
  #91, #94)*
- [CLEAN-02] 🟡 Código comentado ou `TODO` deixado no diff → remover. *(2 comentários, #66: "Remover
  comentários")*
- [CLEAN-03] ⚪ Comentário inline que só repete o código ou compensa código confuso → apagar e conferir se
  o código continua claro sem ele; se não, refatorar (nomes, entidade). Mira do time: comentário só para
  armadilha e porquê. *(1 comentário, #867: "uma coisa que o Claude gosta de fazer é compensar código
  confuso com comentários... olhar onde que o Claude comentou e ver se o código perde a clareza quando
  removo ele")*
- [CLEAN-04] ⚪ Mudança fora do escopo do card que aumenta o diff sem teste → tirar do PR ou abrir card.
  *(1 comentário, #863)*

---

## Lacunas

Temas que o time provavelmente cobra, mas que a amostra de review humana não mostrou (ficam só com base na
documentação, ou nem isso):

- **N+1 e contagem de queries**: está em AGENTS.md, ADR-0002 e no harness, mas nenhum humano apontou N+1 num
  diff. SQL-03 é só doc.
- **Migrations**: nenhum comentário humano sobre migration, backfill ou índice. MIG-* são só doc; índice
  faltando nem tem regra.
- **Transação e soft-delete** (SQL-01, SQL-02): regra forte na doc, zero ocorrência em review humana.
- **Cobertura de teste por camada** e `->with()` nos mocks: quem cobra hoje é o Copilot; humanos não
  comentaram.
- **Concorrência** (race em find-or-create, jobs da SED): só apareceu numa review Julius AI (#509), que não
  conta.
- **Segredo/config ausente** (JWT secret nulo): idem, só Julius (#514).
- **Jobs, filas e idempotência** de importação (SED, Herby) e **relatórios** (Report): sem nenhum
  comentário.
- **Versionamento e quebra de contrato** com o leme-app (campo renomeado ou removido): nenhum caso.
- Entre #127 e #806 não há review humana inline; o padrão do time nesse período não está representado.
