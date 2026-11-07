# Revisão das memórias do notebook

Feita em 06/11/2026. 33 memórias em `_import/memoria-notebook/`: 30 vieram para `memory/` (2 delas reescritas só com a lição), 3 ficaram de fora, e 2 memórias novas nasceram da revisão.

Critério (seu, 06/11): memória guarda aprendizado; andamento de feature não entra.

## Trazidas sem mudança de conteúdo (20)

validate-fixes-empirically, biome-checks-test-files, screenshots-sao-opcionais, tailwind-fora-de-layer-por-causa-do-chakra, emotion-vence-tailwind-em-componente-chakra, campo-chakra-focado-cobre-botao-sobreposto, tooltip-centralizado-na-borda-estica-documento, unspoken-punctuation-nao-pontua-pt-br, marcus-perrout-saiu-da-empresa, info-errada-na-tela-e-bug, banco-de-questoes-e-desktop, escopo-na-url-existe-para-link-compartilhado, jql-status-nome-nao-resolve, fernanda-guerra-contribui-no-leme-app, frozen-lockfile-e-o-quinto-check, worktree-precisa-de-install-proprio, lottie-derruba-teste-de-pagina, jsdom-fica-no-breakpoint-base, tela-que-abria-so-por-clique, renomear-branch-fecha-pr

Em várias só corrigi links quebrados (`validate-fixes-empiricamente`, `leme-jira-board-visibility`, `create-jira-card`, `LM-2146`).

## Adaptadas (8)

| Memória | O que mudou |
|---|---|
| glauco-valida-visual-no-browser-dele | Dev server roda no servidor só em `localhost`; você acessa por `ssh -L` do PC. Tirada menção ao OMR |
| sem-acesso-painel-sentry | Sentry agora consta como descontinuado |
| ci-do-leme-app-nao-roda | Tirado "workflow só sobe por SSH" (limitação do notebook) e a branch de OMR |
| all-aboard-e-mensal | Tirado o caminho `~/Leme/all-aboard/` do notebook |
| vite-worker-iife-precisa-query-worker | Tirada a parte do worker do OMR; ficou a regra geral |
| codigo-quase-sem-comentario | Tirados os exemplos do OMR; linha do índice corrigida (estava com números errados) |
| conferir-pr-antes-de-novo-push | Tirados os exemplos do OMR |
| amplitude-graficos-exemplo-nao-contam-cota | Tirado link para a memória da folha v2 |

## Reescritas só com a lição (2)

| Memória | O que ficou |
|---|---|
| qr-link-precisa-esquema-minusculo | Regra de `https://` minúsculo, segmentação byte+alfanumérico, nada de query string, não usar `window.location.origin`. Saiu a métrica do piloto |
| s3-no-scan-e-so-auditoria | Ordem S3 antes do Textract é load-bearing no `scan()`; leitor novo ganha use case próprio. Saiu o plano da rota OMR |

## Novas (2)

| Memória | Origem |
|---|---|
| main-e-homolog | Lição extraída da folha v2: main é homolog, prod sai depois; não propor flag só para isso |
| memoria-guarda-aprendizado-nao-progresso | Seu critério desta revisão |

## Descartadas (3)

| Memória | Motivo |
|---|---|
| git-ssh-broken-use-gh-token | Específica do notebook. O fato do `pre-push` que estagia o `.env` fica para conferir na Fase 3 |
| omr-spike-substituindo-textract | Era andamento de feature. A lição que valia (Textract) foi para `s3-no-scan-e-so-auditoria` |
| folha-v2-moldura-no-bloco | Era andamento de feature. A lição que valia foi para `main-e-homolog` |

## Para conferir na Fase 3, com os repos clonados

- O hook `pre-push` do leme-app faz `git add .` e estagia o `.env`? (fato que estava na memória descartada do SSH)
- Versão do Biome e se o bug do `files.ignore` continua.
- Se o Chakra já saiu (LM-2209); se sim, as memórias de Tailwind e Chakra viram obsoletas.
- Estado atual do CI do leme-app (`gh run list`).
- Skills citadas nas memórias (`/ship`, `/create-jira-card`, `unit-test`) e onde elas vivem.
