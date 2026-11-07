# Conhecimento de QA da esteira (leme-app em homolog)

Leia antes de escrever qualquer script. Curado pelo Glauco com o Claude interativo; os agentes não editam este arquivo. Aprendizado novo vai em `cards/<KEY>/aprendizados-qa.md` (ver o agente `qa`).

## Como rodar

- Scripts em `~/workspace/.escritorio/cards/<KEY>/qa-scripts/`, nunca no worktree.
- Configuração: grave uma vez `qa-scripts/qa.json` com `{"base": "<url do preview>", "worktree": "<worktree do card>", "card": "<KEY>"}` e rode `cd qa-scripts && node script.mjs`. Variáveis `QA_*` também funcionam, mas **não persistem entre chamadas** da ferramenta Bash.
- Use o kit: `import { abrirNavegador, salvarPrint, urlEscopo, loginApi, api, lerFlags, forcarFlags } from "/home/leme/workspace/esteira/qa/kit.mjs";`
- O Chromium (headless shell 145) já está instalado em `~/.cache/ms-playwright`. Não rode `playwright install`.

## Login

- Pela tela: `abrirNavegador({ papel })` preenche `Email`, `Senha` e clica em `Acessar`, e espera a URL `/dashboard` por até 60 s (a primeira carga do Vite em dev é lenta).
- Pela API: `loginApi(papel)` faz `POST /api/auth/login` pelo proxy `/api` do dev server e devolve o token. `api(token)("rota")` chama o leme-core de homolog. Use para achar ou conferir dados sem gastar passos de tela.
- Papéis: `ADMIN`, `PROFESSOR`, `DIRETOR` (contas em `~/.config/leme-escritorio/qa.env`, mesma senha). Nunca imprima a senha.

## Escopo pela URL

Escola, ano e turma vão na query string: `urlEscopo("/dashboard/timetable", { escola, ano, turma })` gera `?school=&year=&class=`. Abrir a tela já com o escopo poupa os cliques nos seletores.

## Dados de homolog conhecidos

Achados pelo QA do LM-2680 (06/11/2026). Confira com `api()` se ainda existem antes de depender deles.

| O quê | ID |
|---|---|
| Escola com turmas AEE | `3b7edca2-99bc-4e29-92ae-165fe39c8c94` |
| Ano letivo dessa escola | `1210f4eb-9cfa-475b-b285-5d89f277dd6f` |
| Turma AEE A | `f0391ad6-b1bf-4d79-a246-2a70c59a9d8d` |
| Turma AEE B | `25b66340-6869-459f-b1b2-d031ba2b3c0e` |

- A escola acima é a **"Tunada da Feda"**, escola de teste da Feda, na flag `is-aee-enabled`. Turma "1º Ano AEE A - Manhã".
- Massa usada no LM-2680 (já existe, reaproveite): **Dalila Xavier** (Remanejado do AEE A para o AEE B, atendimentos terça 09:00 e sexta 08:00), **Antônio Batista** (Abandono desde 06/11/2026, sexta 10:00), **Yuri Carvalho Jr.** (Ativo, sexta 14:00). Professor dos atendimentos: Caio Nogueira.
- **Não existe caminho para voltar um aluno a Ativo:** o menu de ações fica desabilitado para quem saiu e o leme-core não tem endpoint de reativação (o terminate só aceita os status 4, 6 e 8). Saída de aluno em homolog é definitiva.

## Criar dados de teste (liberado)

O QA pode criar a massa que precisar em **homolog**, em **escola de teste** (como a "Tunada da Feda"): matricular, criar atendimento, remanejar, encerrar aluno. Liberado pelo Glauco em 06/11/2026.
- Só pelo preview da esteira, que aponta para homolog. Nunca em produção.
- Reaproveite a massa que já existe (tabela acima) antes de criar outra.
- Registre no `qa.md` e no `aprendizados-qa.md` o que criou (quem, onde, IDs), para o próximo QA reaproveitar.
- Lembre que algumas ações não têm volta (saída de aluno é definitiva).

## Flags

- O GrowthBook decide telas inteiras (ex.: `is-aee-enabled`, `IsMapaLemeEnabled`, `is-mapa-v2-enabled`). Se uma tela não aparece, confira a flag antes de concluir que é bug.
- **Ler as flags reais:** `await lerFlags()` (busca no CDN de homolog/dev). Não tente ouvir a rede da página: o SDK usa cache e outra URL.
- **Simular um cenário que não existe em homolog:** depois do login, `await forcarFlags(page, { ... })`. Vale só naquele navegador e não grava nada. Prefira isso a criar dado quando o cenário depende só de flag.

## Mapa (pedagógico)

- Rota única `/dashboard/mapa/pedagogical-map`; V1 ou V2 depende de a escola selecionada estar em `is-mapa-v2-enabled` (hoje: Escola teste da Feda e EMEIEF Conceição Evaristo). `forcarFlags(page, { "is-mapa-v2-enabled": [] })` força o V1.
- Link do menu: `getByRole("link", { name: "Mapa", exact: true })`. Em 360 px a navegação vira barra inferior.
- Homolog (07/11/2026): ADMIN vê 60 escolas, 9 com Mapa (entre elas Faino `41a3e682-39a9-4edd-a201-ef787ddabb82` e Escola teste da Feda `ebac582b-e871-4214-a916-0b38f59360ca`, 6 de Pompéu e EMEF Todos a bordo!). PROFESSOR tem 5 escolas: Faino e Escola teste da Feda com Mapa; ZEZE SALLES `3ff69be6-2c6b-486f-b418-a8d450c5bc5f`, Tunada da Feda e Melo Martins sem. DIRETOR: 1 escola (Nilva Cazeto, sem Mapa).
- **Nenhum usuário tem exatamente 1 escola com Mapa:** para esse cenário, use `forcarFlags` com `IsMapaLemeEnabled` de uma escola só.

## Armadilhas e orçamento

- **Orçamento:** ~40 chamadas de ferramenta por card. Se passar disso sem fechar os critérios, pare e escreva no `qa.md` o que travou (ambiente, dado faltando, flag). Depurar ambiente indefinidamente não é trabalho do QA.
- **Não rode a suíte do vitest** nem build/lint: isso é do front-dev e do pre-push. Critério não visual se testa com o comando do próprio critério.
- Console: `React Router Future Flag Warning` e avisos `Not implemented` do jsdom são ruído conhecido, não reprovam. Na agenda AEE mobile, dois `validateDOMNesting` (`<p>` dentro de `<p>`) do `MobileCardList` já existiam antes do LM-2680.
- Preview com login dando 404: o worktree está sem `.env` (`VITE_APP_LEME_API_URL=/api`). A esteira cria o `.env` desde 06/11/2026; se acontecer, é ambiente: reporte, não contorne reescrevendo requisições.
- Evidência visual: `salvarPrint(page, "<n>-<slug>")` grava em `evidencias/`. Sem print, critério visual não aprova.
