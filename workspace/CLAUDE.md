# Leme

Workspace da Leme (Leme Educação) no homelab do Glauco. A Leme faz uma plataforma pedagógica para redes públicas de ensino: professores, escolas e secretarias (SME) usam para turmas, conteúdos, anotações, avaliações, mapa de aprendizagem e analytics.

## Repos (`repos/`, fora do git do workspace)

| Repo | O que é | Rodar / testar aqui |
|---|---|---|
| `leme-app` | Front autenticado (React + Vite, Chakra migrando para Tailwind). `app.leme.tec.br` | `pnpm install`, `pnpm dev` (aponta para homolog). Antes de PR: `pnpm biome check ./src && pnpm tsc -p tsconfig.app.json --noEmit && pnpm knip && pnpm test && pnpm build` |
| `leme-core` | Backend principal (PHP 8.2, Laravel 11, DDD). Gestão acadêmica, escolas, usuários | Tudo via `make` e Docker, que **não roda neste servidor**. Leia `AGENTS.md` e `.github/copilot-instructions.md` antes de mexer |
| `leme-assistant` | Assistente de dados interno (FastAPI + Claude, SQL na réplica, só `@leme.tec.br`) | `uv sync`; `uv run ruff check . && uv run pytest` (precisa de Postgres; ver README). `uv` ainda não instalado |
| `terraform-infra` | Infra AWS (ECS, RDS, pipelines), ambientes `qa` e `prod` | Só `terraform validate`/`fmt` (`init -backend=false`). Nunca apply daqui |
| `leme-videos` | Vídeos da Leme em HyperFrames (HTML + GSAP para MP4) | Skill `/video-maker`, a partir da raiz do repo |
| `leme.tec.br` | Landing page (Astro) | `npm install`, `npm run dev` / `npm run build` |

Detalhe de um repo só vai no `CLAUDE.md`/`AGENTS.md` daquele repo. Skills e agents do front vivem em `repos/leme-app/.claude/`.

## Regras do workspace

- **Isolamento:** nada de Ubersuggest/NP Digital aqui. É outro trabalho do Glauco e não se mistura.
- **Rede:** o servidor só é acessível pela rede de casa. Nenhum serviço escuta porta na rede, **exceto os previews de validação da esteira** (faixa 5301-5309, só na rede de casa, vida limitada: caem ao sair da validação ou após 24 h). Nada de túnel, ngrok, cloudflared, Remote Control ou bot. Fora da esteira, dev server só em `localhost`; o Glauco acessa com `ssh -L` do PC.
- **Sem sudo.** Se algo precisar de root ou `apt`, passar o comando exato para o Glauco rodar.
- **`memory/` vs `notes/`:** as duas sincronizam com o Obsidian do PC via `~/git/workspace.git` (hooks SessionStart/Stop).
  - `memory/`: memória do Claude. Um aprendizado por arquivo, com frontmatter, indexado no `MEMORY.md`. Aprendizado, não andamento de feature.
  - `notes/`: segundo cérebro do Glauco (`inbox/`, `reunioes/`, `decisoes/`, `projetos/`). Texto livre, não segue as regras da memória.
- **Nunca** colocar segredo (token, senha, chave) em `memory/` ou `notes/`.
- **Escrita fora do workspace** (Jira, Confluence, Amplitude, GitHub) só com OK do Glauco. Exceções aprovadas: a esteira comenta sozinha no card do Jira o impedimento de uma triagem INVIÁVEL (e liga com vínculo Blocks os cards citados no "O que destrava", exceto épico); quebra card grande demais para um PR em cards novos (mesmo tipo, épico, responsável e sprint), anotando o escopo no card original e ligando os vínculos; cria card para o que ficou para depois num card concluído com PR (mesmos campos, vínculo Blocks); e move o status do card conforme a etapa (Desenvolvendo desde a triagem, inclusive inviável com flag de impedimento; Revisando Código; Testando no merge; só em card que está em Tarefas pendentes, Desenvolvendo ou Revisando Código; quem faz é o despachante, não o modelo), abre o PR depois da aprovação humana no escritório, no atender review (só `leme-app` e `leme.tec.br`) faz push normal na branch do PR e responde as threads com o texto aprovado, também só depois da aprovação no escritório, e o QA cria dados de teste em homolog, só em escola de teste (regras em `esteira/qa/CONHECIMENTO.md`).
- **Trabalho grande vai em fases:** no fim de cada fase, mostrar o que foi feito e esperar o OK.
- Falar em português. Evitar travessão nos textos.

## Convenções de código (todos os repos)

- Conventional commits. O card vai no título do PR (`[LM-<n>] ...`), não no nome da branch, e não se renomeia branch de PR aberto.
- Comentário só para armadilha e porquê medido; mirar 8 a 10% de linhas.
- Provar que o fix funcionou antes de declarar pronto. Em trabalho visual, quem valida é o Glauco no browser dele; suíte inteira só antes do commit.
- Conferir o estado do PR (`gh pr view <n> --json state`, em chamada separada) antes de cada push.
- `main` é homolog; produção sai depois de validar lá.
- Os detalhes e o porquê de cada regra estão em `memory/`.

## Travas de git e GitHub

Existem travas que rodam fora do Claude: hook PreToolUse (`.claude/hooks/guard.py`) e um `pre-push` global com dono root (`~/.local/share/leme-git-guard`). Elas bloqueiam só o que altera: force push, deleção de branch, push em main/master, `--no-verify`, mudança de `core.hooksPath`, `gh repo delete`, `gh pr merge --admin`, `gh api` com DELETE/PATCH/PUT e terraform fora de plan/validate/fmt/show. Ler e escrever sobre esses assuntos é livre.

- Nunca tente contornar uma trava: nada de outro comando, script em arquivo, alias, variável de ambiente ou edição das travas.
- Bloqueou: explique ao Glauco o que queria fazer e por quê, e ele decide.
- Push sensível quem faz é o Glauco (`LEME_HUMAN_PUSH=1` é só dele).

## Neste servidor

- Push é por SSH normal: `git push -u origin <branch>`. A skill `ship` do leme-app manda usar HTTPS com o token do `gh` porque o SSH do notebook antigo não funcionava; aqui isso não vale, e o refspec `HEAD:refs/heads/...` dela é barrado pela trava.
- Terraform: sem credencial de nuvem no servidor, e não se coloca nenhuma; um apply errado mexe na infra de produção.
- Ferramentas sem sudo em `~/.local/bin`: `gh`, `terraform` (1.15.8), `node`/`npm`/`pnpm` via fnm (`~/.local/share/fnm`). Não há Docker utilizável (o `leme` não está no grupo `docker`, de propósito).
- Esteira de agentes (triador, front-dev, qa, manager): código em `esteira/`, desenho em `esteira/DESENHO.md`, dados em `.escritorio/` (fora do git).
- Mudou `esteira/bin/esteira` ou o `guard.py`: rodar `bash esteira/tests/rodar.sh` antes de reiniciar o despachante. Regra nova ganha caso em `esteira/tests/`, sempre pelo `_carrega.py` (pasta temporária, rede e subprocess bloqueados): teste nunca toca a `.escritorio` real.
- MCPs do projeto (`.mcp.json`): Atlassian (`leme-tec`) e Amplitude. IDs em `memory/ids-das-integracoes.md`.
