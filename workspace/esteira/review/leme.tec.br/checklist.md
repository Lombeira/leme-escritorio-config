# Checklist de review: leme.tec.br (rascunho)

Os revisores por lente aplicam as regras abaixo às linhas alteradas de um diff do
`leme-tech/leme.tec.br`, a landing page pública da Leme (Astro 6 + ilhas React + Tailwind 4 + MDX,
publicada em S3/CloudFront pelo `buildspec.yml`).

**Formato:** cada regra é `[ID] <sev> sinal → correção`. Os IDs são estáveis: não renumerar.
Categoria nova entra no fim.

**Severidade padrão (`<sev>`):** o revisor usa a severidade da regra, a não ser que o caso peça
outra (nesse caso, uma linha com o motivo no achado):
- 🔴 **blocker**: quebra a página ou um caminho do visitante (CTA, âncora, link), mostra informação
  errada ao cliente (valor do VAAR, número, prazo, portaria) ou expõe segredo.
- 🟡 **should-fix**: convenção ou manutenção que o time cobra ou que o repo segue de forma consistente.
- ⚪ **nit**: opcional, baixo risco.

**Lente (`Lens:` no cabeçalho de cada categoria):** três revisores em paralelo, cada um com um
conjunto disjunto de categorias:
- `correctness`: DATA, CONTENT, LINK, BUILD.
- `reuse-architecture`: COMP, PERF, SEO.
- `readability`: COPY, A11Y.

**Escopo:** só o que a máquina não pega. O repo **não tem lint nem formatter** (sem Biome, ESLint ou
Prettier; o estilo mistura tab e 2 espaços, aspas simples e duplas: não cobrar). O que o
`astro build` já barra não entra: tipo do TypeScript (`astro/tsconfigs/strict`), import quebrado,
frontmatter de post fora do schema zod de `src/content.config.ts` (campo obrigatório faltando, tipo
errado). Atenção: o build **não** pega caminho de imagem em string (`cover`), prop desconhecida em
componente MDX, âncora sem alvo, nem link interno quebrado.

**Origem de cada regra** (entre colchetes no fim):
- `[doc]`: documentação do repo (hoje só o README do template do Astro: nenhuma regra sai dele);
- `[código]`: código, configuração, scripts ou dados do próprio repo (arquivo citado);
- `[PR #n]`: descrição do PR escrita pelo autor (não é review; ver Proveniência);
- `[commit <hash>]`: commit que corrigiu o problema que a regra previne;
- `[workspace]`: `CLAUDE.md` do workspace (convenções que valem para todos os repos).

---

## ⚠️ Proveniência: ler antes de confiar numa regra

**Faixa coberta: PRs `#1`–`#37`**, lidos em 07/11/2026: 35 mergeados (`#1`–`#35`) e 2 abertos
(`#36`, `#37`, autor `app/claude`, posts de blog pedidos pelo Slack). Mais os 86 commits de
`git log` da `main` (até `41d21ba`).

O que existe no corpus:
- **0 comentários inline** (`pulls/<n>/comments`) em todos os 37 PRs.
- **17 reviews** (`pulls/<n>/reviews`), todas da conta `Lombeira`: 16 são texto gerado por IA
  ("🤖 Code Review", "🤖 Julius AI", em `#1`–`#8`, `#12`–`#19`) e 1 é ação administrativa sem
  conteúdo ("Review pendente anterior — submetendo para liberar", `#5`). Tratadas como bot.
- **1 comentário de conversa** (`issues/11/comments`), também "🤖 Julius AI". Tratado como bot.
- Autores dos PRs: `Lombeira` (30), `GustavoFaino` (5, `#29`–`#33`, ajustes de pipeline e PRs de
  teste), `app/claude` (2). Nenhum PR teve review de outra pessoa.

**Consequência: nenhuma regra deste arquivo vem de review humana.** Comentários humanos de review
lidos: **0**. As regras vêm do código, das descrições dos PRs e, principalmente, dos commits e PRs
`fix:` (o que o time precisou corrigir depois). Sugestões das reviews de IA **não** viraram regra
por si só; quando uma regra coincide com uma delas, a base citada é outra (código, commit, PR).
Quando aparecer review de verdade, refazer o levantamento a partir do `#38`.

**Medições feitas para este rascunho** (só leitura, cópia do repo no scratchpad): `astro build`
(35 páginas, avisos de sitemap e de import sem uso), conferência de âncoras e links internos no
`dist/`, `curl -I` no site no ar, e comparação de `src/data/vaar.json` com
`potencial-recebimento-vaar.xlsx`.

---

## DATA — dados e números mostrados ao cliente
Lens: `correctness`. Fluxo do VAAR: planilha Google (`SHEET_ID` em `scripts/update-vaar.mjs`) →
`npm run update-vaar` → `src/data/vaar.json` (gerado) → `CalculadoraVAAR.tsx`. O pre-commit do
Husky roda o script e faz `git add src/data/vaar.json` em **todo** commit. As planilhas `.xlsx` da
raiz não são lidas por nenhum script.

- [DATA-01] 🔴 `src/data/vaar.json` alterado à mão, ou campo novo no JSON sem mudança no
  `update-vaar.mjs` → o arquivo é gerado: mudar a planilha ou o script e regenerar com
  `npm run update-vaar`; o PR cola o resumo que o script imprime (total, recebidos, potenciais).
  *Ex.: PR #10 documenta 5.568 municípios = 3.024 recebidos + 2.544 potenciais.*
  `[código: scripts/update-vaar.mjs, .husky/pre-commit]` `[PR #10]`
- [DATA-02] 🟡 Diff em `vaar.json` num PR que não é de dados (o hook regenera e adiciona sozinho
  quando a planilha mudou) → tirar do PR e abrir um PR de dados à parte, com o resumo de DATA-01.
  Commit feito sem o hook (sem rede, 403 na planilha) não mexe em `vaar.json` e diz isso no PR.
  `[código: .husky/pre-commit]` `[PR #36, #37]`
- [DATA-03] 🔴 Mudança no `update-vaar.mjs` (coluna, parse, regra recebido/potencial) que segue em
  frente quando a coluna some ou o valor não parseia (`parseBRL` devolve `0`; `row["Valor potencial"]`
  ausente vira `0` e a calculadora mostra "Quero receber os R$ 0 potenciais") → falhar alto
  (`process.exit(1)`) em coluna ausente ou valor inválido, e comparar as contagens com a rodada
  anterior antes de commitar. `[código: scripts/update-vaar.mjs, CalculadoraVAAR.tsx]` `[PR #10]`
- [DATA-04] 🔴 Número derivado digitado à mão ao lado do dado de origem, ou texto fixo que depende
  do dado → calcular a partir do dado ou conferir no PR, e mudar junto quando o dado muda.
  *Ex.: `evolucao='+21%'` com `diag1={55.6} diag2={67.3}` em `ImpactBarChart`; "5.568 municípios",
  "VAAR 2026", "Complementação VAAR — 2026" e "Fonte: Portaria Interministerial MEC/MF nº 14, de 29
  de dezembro de 2025" fixos no `CalculadoraVAAR.tsx`, independentes do `vaar.json`.*
  `[código: ConversaoHome.tsx, CalculadoraVAAR.tsx]` `[PR #10]`
- [DATA-05] 🔴 Estimativa mostrada como dado (constante mágica aplicada a um valor e exibida como
  número do município) → usar o dado da fonte ou não mostrar. *Ex.: `alunosEst = valor / 341`
  ("~N alunos · aprox. R$ 341/aluno"): a planilha tem `Alunos` e `Valor/aluno` reais e a estimativa
  erra muito (ver Problemas, item 1).* `[código: CalculadoraVAAR.tsx, potencial-recebimento-vaar.xlsx]`
- [DATA-06] 🟡 Data ou moeda formatada com `toLocaleString`/`toLocaleDateString`/`Intl` ou com
  getters de hora local (`getDate`, `getMonth`) em componente hidratado → formatação determinística
  em UTC, como `formatDate` (`getUTC*` + `MESES_PT`) e `formatBRL` (separador fixo). O HTML do build
  (Node) e a hidratação (browser) não podem divergir, e `'2026-04-14'` em fuso -3 vira dia 13.
  `[commit 41d21ba]` `[código: BlogIndex.tsx, BlogPost.tsx, CalculadoraVAAR.tsx]`

## CONTENT — posts do blog (`src/content/blog/*.mdx`)
Lens: `correctness`. Posts falam de VAAR, FUNDEB, Saeb, PNE, portarias e prazos para secretarias:
erro de fato é informação errada ao cliente.

- [CONTENT-01] 🔴 Número, valor, prazo, portaria, resolução ou nota técnica no post sem link para a
  fonte primária (gov.br, Inep, FNDE, DOU), ou conferido só em fonte secundária sem dizer isso no PR
  → link primário no texto; o PR lista o que foi conferido e onde, e o que ficou de fora por falta
  de fonte (como o `#36` fez com VAAF-MIN/VAAT-MIN e o `#37` com as faixas do Selo).
  `[PR #36, #37]` `[código: posts linkam gov.br/inep/fnde]`
- [CONTENT-02] 🟡 Post sobre política pública ou financiamento sem registro de quem aprovou o
  conteúdo → registrar no PR a revisão editorial ("Aprovado por ... via Slack", "Escrito em
  colaboração com ..."). `[PR #24, #25]`
- [CONTENT-03] 🟡 `cover` apontando para arquivo que não existe (o build não pega: é string) →
  imagem em `public/blog/<slug>/cover.<ext>` e `cover: '/blog/<slug>/cover.<ext>'`; sem capa, tirar a
  linha e deixar só o `coverGradient`. `[commit dc2dc2f]` `[PR #36]` `[código: content.config.ts]`
- [CONTENT-04] 🟡 Componente MDX com prop errada, em especial `<Callout type=...>` → `variant`
  (`info | warning | success`); prop desconhecida é ignorada sem erro e cai no padrão `info`.
  `[PR #37]` `[código: Callout.tsx]`
- [CONTENT-05] 🔴 Link interno do post com URL absoluta do site antigo (`https://www.leme.tec.br/...`)
  ou slug digitado de memória → caminho `/blog/<slug>` conferido contra os arquivos de
  `src/content/blog/` (ou `/`, `/#calculadora`, `/solucoes/<slug>`). *Hoje há 3 quebrados (404 no ar),
  ver Problemas.* `[código]`
- [CONTENT-06] ⚪ `featured: true` ou ordenação manual para fixar um post no destaque → o destaque é
  o post mais recente; a ordem é `date` decrescente, com `date` em `'AAAA-MM-DD'`.
  `[PR #35]` `[commit 3452adf]`

## LINK — CTAs, âncoras e links
Lens: `correctness`. Metade dos `fix:` do repo é link ou botão que não levava a lugar nenhum.

- [LINK-01] 🔴 Botão ou link sem destino (`href="#"`, `<a>`/`<Button>` sem `href`, `onClick` vazio) →
  destino real ou remover o elemento. *Ex.: "Agendar demonstração" sem `href` (PR #21), "Ver todos
  os módulos" sem página (removido no PR #21), "Conhecer a equipe" sem `href` (PR #22).*
  `[PR #13, #21, #22]` `[commit 4657a48]`
- [LINK-02] 🔴 Âncora (`#x`, `/#x`) sem `id="x"` na seção de destino → pôr o `id` na `<section>`
  raiz e conferir no `dist/` ou no browser. *Ex.: `/#calculadora` usado no blog (PR #26), `#equipe`
  (PR #22); `/#solucoes` está quebrado hoje.* `[PR #22, #26]`
- [LINK-03] 🟡 Link externo com `target="_blank"` sem `rel="noopener noreferrer"` → os dois juntos,
  como os 15 usos atuais e o `ExternalLink` dos posts. `[código: ExternalLink.tsx e componentes]`

## BUILD — publicação, cache e hooks
Lens: `correctness`.

- [BUILD-01] 🔴 Mudança no `buildspec.yml` que publica HTML com cache longo, ou tira/estreita a
  invalidação do CloudFront → todo HTML (inclusive `*/index.html` de `blog/`, `solucoes/`,
  `quem-somos/`...), sitemap e robots com `no-cache` e invalidados; `max-age=31536000` só para o que
  tem hash (`_astro/*`). *O problema original: site desatualizado depois do deploy (PR #9); o
  `--exclude "index.html"` atual só casa com o da raiz.* `[PR #9, #30]` `[commit d0a82f9]`
- [BUILD-02] 🟡 PR sem dizer que `npm run build` passou, ou que acrescenta warning novo no build
  (import sem uso, integração pulada) → rodar e citar o resultado e o número de páginas no PR.
  `[PR #36, #37]` `[workspace: provar que funcionou]`
- [BUILD-03] ⚪ PR de teste de pipeline (`test: editado readme`, "teste de cacheamento", "testando
  notificação slack") mergeado na `main` → testar a pipeline sem merge de commit vazio no site
  publicado. `[PR #29, #32, #33]`

## COMP — componentes, reuso e estilo
Lens: `reuse-architecture`.

- [COMP-01] 🟡 URL de agendamento do HubSpot
  (`https://meetings.hubspot.com/isaac-barbieri?uuid=...`) digitada de novo → constante única
  importada (hoje são 9 cópias em 5 arquivos); trocar o link de demo não pode depender de achar
  todas. `[PR #13, #21]` `[commit 4657a48]`
- [COMP-02] 🟡 Vídeo do YouTube com `<iframe>` direto, ou facade copiada → reaproveitar o
  `YoutubeFacade` (thumbnail + botão branco; iframe só no clique). *O PR #20 trocou o iframe do PR #18
  por facade copiando a de `ConversaoHome.tsx`; hoje há duas.* `[PR #18, #20]`
- [COMP-03] 🟡 Cor solta (hex, `orange-*`/`amber-*` novos como cor de marca) → tokens do `@theme` em
  `src/styles/global.css`: `leme`, `leme-dark`, `leme-light`, `leme-lighter`, mais a escala `slate`.
  `[código: global.css]` `[commit 8f76b12]`
- [COMP-04] 🟡 Link com aparência de botão feito com `<Button onClick>` ou `<a>` dentro de
  `<button>` → `<Button asChild><a href=...></a></Button>`, como os 15 usos atuais.
  `[código: components/ui/button.tsx e usos; botões dos PRs #13 e #15]`
- [COMP-05] ⚪ Função utilitária duplicada (`formatDate` + `MESES_PT` em `BlogIndex.tsx` e
  `BlogPost.tsx`; `formatBRL` com regex repetida) → um lugar só em `src/lib/utils.ts`.
  `[código]` `[commit 41d21ba]`

## PERF — peso da página
Lens: `reuse-architecture`.

- [PERF-01] 🟡 Componente novo hidratado sem precisar, ou `client:load` abaixo da dobra → sem diretiva
  se não tem interação (como o `Footer`), `client:visible` se está abaixo da dobra (como
  `/institucional`). Não importar `vaar.json` em mais nenhuma ilha: ele já põe a home em 588 KB de JS.
  `[código: pages/*.astro]` `[build: _astro/ConversaoHome.*.js]`
- [PERF-02] 🟡 Imagem nova em `public/` pesada para o tamanho exibido (PNG/JPG de centenas de KB a MB)
  → redimensionar e comprimir (webp, como `logo-leme.webp`/`logo-leme-opt.png`) e pôr
  `width`/`height` no `<img>`; imagem no corpo do post em Markdown já passa pelo otimizador do Astro.
  *Ex.: `educadora-sem-fundo.png` tem 1,7 MB e aparece com 300 px; capas de post de 1,8 a 2,5 MB.*
  `[código: public/]` `[PR #20]`
- [PERF-03] ⚪ `<img>` fora da primeira dobra sem `loading="lazy"` → `loading="lazy"`, como as
  thumbnails das facades. `[código: ImpactVideos.tsx, ConversaoHome.tsx]` `[PR #20]`

## SEO — head das páginas
Lens: `reuse-architecture`. Não há layout compartilhado: cada página em `src/pages/` escreve o
próprio `<head>`.

- [SEO-01] 🟡 Página nova sem o `<head>` padrão das outras → `<html lang="pt-BR">`, `charset`,
  `viewport`, favicon/apple-touch-icon/manifest, `<title>` próprio no formato "<assunto> — Leme" e
  `<meta name="description">` próprio (post usa `excerpt`; solução usa `tagline`).
  `[código: as 7 páginas de src/pages]`
- [SEO-02] 🟡 Rota renomeada ou removida (post, solução, página) sem tratar a URL antiga → manter o
  slug ou criar redirect, e corrigir os links internos que apontavam para ela (CONTENT-05). *Os 3
  links quebrados de hoje são URLs do site anterior.* `[código]`

## COPY — texto visível
Lens: `readability`.

- [COPY-01] 🟡 Travessão (—) em texto visível do corpo da página → dois-pontos, vírgula ou ponto.
  O LM-1806 limpou a home; os `<title>` ("... — Leme") ficaram como estão e não se cobram.
  `[PR #16]` `[commit 424ea27]` `[workspace: evitar travessão]`
- [COPY-02] ⚪ Frase reescrita que perde o sentido ou repete termo → reler a frase inteira depois da
  troca. *Ex.: "transforma dados educacionais em ação pedagógica e ação pedagógica em resultados
  mensuráveis" (commit 424ea27).* `[commit 424ea27]`

## A11Y — acessibilidade
Lens: `readability`.

- [A11Y-01] 🟡 `<img>` informativa sem `alt` descritivo, decorativa sem `alt=""`, ou ícone decorativo
  sem `aria-hidden="true"` → seguir o padrão atual (as 18 `<img>` têm `alt`; texturas e capas com
  `alt=""`; ícones do lucide com `aria-hidden`). `[código]`
- [A11Y-02] 🟡 Elemento clicável que não é `<button>`/`<a>` (`div onClick`) → `<button type="button">`
  com rótulo; `div` não recebe foco nem Enter. *Hoje as duas facades de vídeo são `div onClick`.*
  `[código: ImpactVideos.tsx, ConversaoHome.tsx]`
- [A11Y-03] ⚪ Página nova escrita à mão sem o skip-link "Ir para o conteúdo principal" + `<main
  id="main">` → copiar das páginas atuais (11 das 35 têm; o template de post não tem). `[código]`
- [A11Y-04] ⚪ `title`/`alt` repetido em itens diferentes ("Caso de impacto" nos 3 vídeos) → texto que
  diferencie cada um (município, assunto). `[código: ImpactVideos.tsx]`

---

## Lacunas

1. **Nenhuma review humana no corpus** (37 PRs, 0 comentários humanos). Severidades inferidas dos
   `fix:` e do impacto no cliente. Refazer a partir do `#38` quando houver revisor.
2. **README é o template do Astro.** Não documenta o fluxo planilha → script → `vaar.json`, o hook,
   o deploy nem o padrão de post. Várias regras daqui (DATA-01..03, CONTENT-01..04) deveriam estar lá.
3. **Sem lint/formatter.** Imports sem uso só aparecem como warning do Vite no build; nada barra.
4. **SEC sem regra.** Não há segredo, `.env`, `import.meta.env`, analytics nem pixel no código; o
   `.env` está no `.gitignore`. O único ID externo é o da planilha pública do VAAR. Se entrar
   analytics, formulário ou chave, criar a categoria SEC.
5. **Formulário e contato:** não há formulário; todo contato é o link de agendamento do HubSpot
   (COMP-01). Não há regra de LGPD de coleta porque não há coleta.
6. **OG/canonical/sitemap:** não há prática no repo para virar regra (nenhuma página tem Open Graph
   nem canonical, e o sitemap nunca foi gerado). Ficou em Problemas; quando o time decidir o padrão,
   vira SEO-03.
7. **Cache no ar não bate com o `buildspec.yml`:** o `curl -I` de hoje não mostra `Cache-Control`
   nem em `/index.html`. O CloudFront do site não está no `terraform-infra`. BUILD-01 vale pelo
   que o buildspec manda; o comportamento real precisa de alguém com acesso ao console.
8. **Qual planilha é a fonte?** O script lê a planilha Google; os `.xlsx` da raiz são cópias antigas
   (ver Problemas, item 10). Não há regra sobre eles até o time decidir se ficam.
9. **`main` aqui vai direto para o site público?** O workspace diz que `main` é homolog nos apps; o
   buildspec deste repo publica no bucket sem etapa de homolog visível. Não confirmado.

## Problemas que já existem hoje no repo (para o time, não são regra)

1. 🔴 **Estimativa de alunos errada na calculadora do VAAR.** `alunosEst = valor / 341` e o texto
   "aprox. R$ 341/aluno" aparecem para todo município. Comparado com a coluna `Alunos` de
   `potencial-recebimento-vaar.xlsx`, a estimativa é **2,3× o número real na mediana** (p10 1,12×,
   p90 2,51×). Ex.: Acrelândia/AC aparece com ~4.407 alunos; a planilha tem 2.054. O valor/aluno
   real dos que receberam tem mediana ~R$ 698, não R$ 341. Desde o commit `8f76b12` a linha aparece
   também para os valores potenciais. (DATA-05)
2. 🔴 **Sitemap e robots não existem.** `astro.config.mjs` não tem `site`, o `@astrojs/sitemap` pula
   ("requires the `site` astro.config option. Skipping"), e no ar `/sitemap-index.xml` e `/robots.txt`
   dão 404. Nenhuma página tem `og:*`, `twitter:*` nem `canonical`: compartilhar um post no
   WhatsApp/LinkedIn não traz imagem nem descrição controlada.
3. 🔴 **Âncora `/#solucoes` quebrada**: usada no breadcrumb de `SolutionPage.tsx` e no "Ver visão
   geral" do menu (`Navbar.tsx`), mas nenhuma seção da home tem `id="solucoes"`. (LINK-02)
4. 🔴 **3 links internos de posts dão 404 no ar** (URLs do site antigo):
   `equidade-na-educacao-condicionalidade-3-vaar-fundeb.mdx` → `/blog/como-usar-dados-para-gestao-de-escola-publicas`
   (o slug certo é `...-de-escolas-publicas`) e `/dashboard`;
   `ferramentas-juridicas-para-qualidade-dos-fornecedores-na-dispensa-de-licitacao.mdx` →
   `/blog/como-contratar-um-software-de-gestao-educacional-via-dispensa-de-licitacao-um-guia-pratico-...`
   (o slug atual é `como-contratar-um-software-de-gestao-educacional-via-dispensa-de-licitacao`). (CONTENT-05)
5. 🔴 **Rodapé com 9 links `href="#"` em todas as páginas**, incluindo "Política de privacidade",
   "Termos de uso", "LGPD", "Segurança", "Como contratar" e "Suporte". Em `/institucional`, também
   "Fale com nosso time" (FAQ) e "Saber mais" (Features). (LINK-01)
6. 🟡 **`/institucional` (link "Sobre nós" do rodapé) parece conteúdo de exemplo:** depoimentos com
   foto aleatória de `i.pravatar.cc` e números sem fonte ("98% frequência média", "8.0 nota média",
   "+50 municípios", "frequência subiu 4 pontos"). Conferir se nomes, cargos e números são reais;
   se não forem, é informação errada ao cliente.
7. 🟡 **Cache do deploy:** no `buildspec.yml`, `--exclude "index.html"` só exclui o da raiz, então
   `blog/index.html`, cada post e as outras páginas sobem com `max-age=31536000`, e a invalidação
   cobre só `/index.html`. Pelo buildspec, post corrigido ou lista do blog podem ficar velhos no
   navegador por até um ano (ver Lacunas 7). (BUILD-01)
8. 🟡 **Pre-commit depende de rede:** todo commit baixa a planilha; sem acesso (403) o commit falha,
   e os PRs `#36`/`#37` usaram `--no-verify`, que a trava do workspace bloqueia. Pensar em rodar o
   script só quando o PR é de dados (ou em CI), não em todo commit. (DATA-02)
9. 🟡 **`scripts/update-vaar.py` divergente e perigoso:** descarta quem tem valor 0 (os 2.544
   potenciais) e não grava `tipo`; se alguém rodar, a calculadora perde metade dos municípios e
   mostra os recebidos com o rótulo "Valor potencial". Não é usado pelo `package.json`: remover.
10. 🟡 **`.xlsx` da raiz desatualizados e sem uso:** nenhum script lê. `potencial-recebimento-vaar.xlsx`
    está sem valor potencial para 92 municípios do RJ que têm valor no `vaar.json` (Angra dos Reis,
    Araruama, Barra Mansa...). O cabeçalho da coluna de potencial nessa cópia é a URL da planilha,
    não "Valor potencial".
11. 🟡 **Fonte única para dois tipos de valor:** o rodapé do card cita "Portaria Interministerial
    MEC/MF nº 14" também quando o valor é potencial, que vem de uma coluna da planilha da Leme e não da
    portaria. Conferir se a fonte do potencial precisa aparecer separada.
12. 🟡 **Peso da home:** `ConversaoHome` hidratada com `client:load` gera 588 KB de JS (inclui o
    `vaar.json` inteiro). `educadora-sem-fundo.png` (1,7 MB) é exibida a 300 px. `educadora.png`
    (5,9 MB), `logo-leme.png` e `hi-res-symbol.png` não são usados e sobem para o bucket. Capas de
    post de até 2,5 MB.
13. 🟡 **`src/data/posts.ts` (1.291 linhas) é código morto:** nenhum import; os posts vêm da
    coleção `blog` desde `fbd603b`. Risco de alguém editar o arquivo errado.
14. 🟡 **Vídeos não abrem por teclado:** as duas facades (`ImpactVideos.tsx` e `ConversaoHome.tsx`)
    são `div onClick` duplicadas; os 3 vídeos de impacto têm o mesmo título "Caso de impacto".
15. ⚪ Travessões no texto da calculadora, que está na home (`CalculadoraVAAR.tsx`, linhas 172-173 e
    374); frase "ação pedagógica e ação pedagógica" na seção da metodologia.
16. ⚪ `<Callout type="info">` duas vezes em `condicionalidade-iii-vaar-mudancas-2025-2026.mdx`:
    funciona só porque o padrão do `variant` é `info`. Um link interno de post (`ExternalLink` é
    aplicado a todo `<a>` do MDX) também abre em aba nova.
17. ⚪ Warnings do build: `Zap` e `useMotionValue` importados sem uso em `ConversaoHome.tsx`.
