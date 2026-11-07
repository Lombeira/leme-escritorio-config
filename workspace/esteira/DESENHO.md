# Esteira de agentes: desenho (aprovado em 06/11/2026)

## Peças

| Peça | O que é | Onde |
|---|---|---|
| 4 agentes | `triador`, `front-dev`, `qa`, `manager` | `.claude/agents/` |
| `despachante.py` | loop Python (só stdlib), sem Claude, que lê `fila/` e dispara o manager | `esteira/bin/` |
| `pendencias.py` | busca no Jira via REST a cada 5 min, sem Claude | `esteira/bin/` |
| `esteira-estado` | CLI que valida transição e grava `estado.json` de forma atômica | `esteira/bin/` |
| `esteira-preview` | sobe e derruba o dev server de um card como unidade do systemd | `esteira/bin/` |
| units do systemd `--user` | `leme-despachante.service`, `leme-pendencias.timer` e `leme-preview-<KEY>.service` (transitória) | `~/.config/systemd/user/` |

O código fica versionado em `esteira/`. Os dados de execução ficam em `~/workspace/.escritorio/` (fora do git) e os logs em `~/.escritorio-logs/`.

## Ciclo do despachante (a cada 10 s)

1. **Fila.** Para cada `fila/*.json` em ordem de `em`:
   - valida o schema; se inválido, move para `processados/` com `<arquivo>.erro` explicando;
   - `triagem`: aceita se o card não existe, ou se está em `inviavel`, `erro` ou `concluido`. Cria ou zera o `estado.json` com `etapa: fila`;
   - `aprovar` e `devolver`: aceita só se o card está em `validacao` com `aguardando_humano`. Fora disso, rejeita com `.erro`;
   - move para `fila/processados/`.
2. **Agenda.** Se há menos de 2 cards com execução em andamento (card esperando humano não ocupa vaga), pega o próximo pendente (FIFO) e roda:
   `claude -p --agent manager --permission-mode acceptEdits --allowedTools <lista> --disallowedTools <escritas do Jira> "<KEY> <ação> <comentário>"`
   com `cwd=~/workspace`, stdout e stderr em `~/.escritorio-logs/<KEY>-<epoch>.log`.
3. **Fim de execução.** Quando o processo termina e `estado.status` ainda é `rodando`, grava `etapa: erro`, `status: falhou` e `resumo: "manager terminou sem fechar a etapa"`.
4. **Timeout.** Uma execução passa de 2 h: SIGTERM no grupo de processos; se não sair em 30 s, SIGKILL no grupo. O card vai para `erro` com `resumo: "timeout de 120 min"` e a vaga é liberada.
5. **Reinício.** Ao subir, card `rodando` sem processo vivo vira `erro: "despachante reiniciou no meio"`. Nada é retomado sozinho.

**Nunca há retry automático.** Erro para o card. O humano recoloca na fila com `triagem`.

## Máquina de estados (`esteira-estado` recusa o resto)

```
fila -> triagem -> inviavel (aguardando_humano)                         [fim, humano pode reenviar]
                -> front -> qa -> front (voltas_qa +1, máx. 2)
                                -> qa aguardando_humano (3ª reprovação: escala; sai só por devolver ou triagem)
                                -> validacao (aguardando_humano)
validacao --aprovar--> pr -> concluido
validacao --devolver-> devolvido -> front -> qa -> ...
qualquer etapa -> erro (falhou)
```

`historico` ganha uma entrada a cada transição. `atualizado` é o epoch da última escrita.

## Travas fora do modelo

- **Jira só leitura:** o `claude -p` sobe com `--disallowedTools` em todas as ferramentas de escrita do Atlassian (`createJiraIssue`, `editJiraIssue`, `addCommentToJiraIssue`, `transitionJiraIssue`, `addWorklogToJiraIssue`, `createIssueLink`, `createConfluencePage`, `updateConfluencePage` e os comentários do Confluence).
- **Etapa só pelo CLI:** o `estado.json` muda só pelo `esteira-estado`, que conta voltas e recusa transição inválida.
- **Git:** as travas atuais continuam valendo (PreToolUse e pre-push global). Push de branch e `gh pr create` passam; force, deleção e push em main não.
- **Aprovação e fila:** `validacao -> pr`, `validacao -> devolvido`, `qa(escalado) -> devolvido` e qualquer `-> fila` só o despachante faz (função Python ao consumir a fila). O `esteira-estado` recusa essas transições vindas do modelo.
- **Guard da esteira:** `fila/`, `estado.json`, `.interno.json`, `esteira/` e `.claude/agents/` são negados para Write/Edit/Bash do modelo na sessão da esteira (`ESTEIRA_HEADLESS=1`) e pedem confirmação na sessão interativa.
- **Card nasce de main limpa:** o despachante (subcomando `preparar-e-rodar`, antes de virar o `claude -p`) faz `git fetch origin`, `git worktree add -b <KEY>-<slug> .worktrees/<KEY> origin/main`, põe `test-results/` e `playwright-report/` no `info/exclude` e roda `pnpm install --frozen-lockfile`. Falha no preparo vira `erro` com o motivo.
- **Agentes que não editam:** ao entrar em `triagem` ou `qa`, o `esteira-estado` guarda HEAD, hash do `git diff HEAD` e hash do `git status --porcelain` (pega arquivo novo; respeita `.gitignore` e o `info/exclude` dos artefatos de teste). Na saída da etapa compara; se mudou, o card vai para `erro`. Evidências e scripts do QA ficam em `.escritorio/cards/<KEY>/`, nunca no worktree.

## Preview de validação

- `esteira-preview start <KEY> [--rede]` escolhe a primeira porta livre de 5301 a 5309 e roda `systemd-run --user --unit leme-preview-<KEY> pnpm dev --host <h> --port <p>` no worktree. Grava `preview_url` no estado.
- Sem `--rede` (para o QA) escuta em `127.0.0.1`; com `--rede` (validação humana), em `0.0.0.0`.
- O preview cai sozinho: ao sair de `validacao` (aprovado ou devolvido), ao sair de `qa` para outra coisa que não `validacao`, em `erro`/`concluido`/`inviavel`, e após 24 h (`RuntimeMaxSec` da unidade). O despachante varre a cada ciclo e limpa `preview_url` de preview expirado.

## pendencias.json

O `leme-pendencias.timer` roda a cada 5 min:
- JQL: `assignee in (Glauco, Feda/Fernanda Guerra por accountId) AND statusCategory != Done`, via REST (`/rest/api/3/search/jql`) com e-mail e token de API lidos de `~/.config/leme-escritorio/atlassian.env` (permissão 600);
- escreve `pendencias.json` de forma atômica (arquivo temporário + rename);
- se falhar, mantém o arquivo anterior e registra no log.

## Precisa de sudo (você roda)

- `sudo loginctl enable-linger leme`: os serviços do usuário sobrevivem ao logout.
- As dependências de sistema do Chromium para o Playwright. O comando exato sai de `pnpm exec playwright install-deps --dry-run` quando chegar a hora.
