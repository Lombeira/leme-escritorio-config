# Prompt para o escritório: mudanças no contrato da esteira (07/11/2026)

Cole o bloco abaixo na sessão que mexe no código do escritório.

---

A esteira de agentes da Leme mudou desde o contrato original. O escritório lê e escreve arquivos em `~/workspace/.escritorio/`; nada mudou nos caminhos de `pendencias.json`, `fila/`, `permissoes/` e `respostas/`. Implemente o que segue, sem mudar o formato dos arquivos que o escritório já escreve.

## 1. Etapa nova: `review` (sala "review")

O ciclo agora é `triagem → front → review → qa → validacao → pr → concluido`.
- Em `review`, a esteira roda o `/review` do leme-app sobre o diff do card. Se achar blocker ou should-fix, o card volta para `front` e passa pelo review de novo (até 2 voltas).
- **Sala de cada etapa: mapeie pela `etapa` do `estado.json`, não pelo `room:` do agente.** Os agentes do review (`reviewer`, `review-validator`) vêm do repo do leme-app e não têm `room:`. Mapeamento:

| etapa | sala |
|---|---|
| `fila` | fila (ou nenhuma) |
| `triagem` | triagem |
| `front`, `devolvido` | front |
| `review` | review |
| `qa` | qa |
| `validacao`, `pr`, `concluido` | manager |
| `inviavel`, `erro` | mostrar como bloqueado, na sala da última etapa do `historico` |

## 2. Campos novos no `estado.json`

Todos opcionais: cards antigos podem não ter. Trate ausente como 0 ou nulo.
- `voltas_review` (int): quantas vezes o review mandou de volta ao front (máx. 2). Mostre junto do `voltas_qa`.
- `custo_usd` (float): custo equivalente de API acumulado do card (não é cobrança; mede o peso no limite de uso).
- `custo_por_setor` (objeto): `{"triagem": 0.58, "front": 1.36, "review": 0.00, "qa": 2.85, "manager": 0.69}`.
- `merged_em` (string ISO 8601): quando o PR foi mergeado na main. Ausente = PR ainda aberto.

## 3. Custo por setor ao longo do tempo: `.escritorio/custos.jsonl`

Uma linha JSON por execução e por agente, só acrescentada (append):
`{"em": <epoch>, "card": "LM-2680", "execucao": "triagem|aprovar|devolver|retomar", "agente": "qa", "setor": "qa", "modelo": "claude-opus-5-5", "custo_usd": 2.8512}`
- `setor` ∈ `triagem`, `front`, `review`, `qa`, `manager`. Agrupe por `setor` (e por período) para o painel de custo; `modelo` permite comparar Opus e Sonnet.
- A divisão entre setores é estimativa; o total por execução bate com o oficial.

## 4. Cards concluídos não podem sumir

Hoje o card some da tela ao chegar em `concluido`, e o link do PR se perde. Mantenha os concluídos visíveis (sugestão: 24 h depois do `atualizado`, ou até `merged_em`), mostrando `pr_url` como link clicável e, se houver, "mergeado em <merged_em>".

## 5. Ações da fila

Escritas pelo escritório em `fila/*.json` (formato já existente):
- `triagem`: card novo, ou card em `inviavel`, `erro`, `concluido`, ou **escalado** (`qa`/`review` com status `aguardando_humano`).
- `aprovar`: só card em `validacao` com `aguardando_humano`.
- `devolver` (exige `comentario`): card em `validacao`, **ou escalado** em `qa`/`review` com `aguardando_humano`. Mostre o botão Devolver também nesses casos.
- `retomar` (botão "Retomar esta etapa"): card em `erro` (refaz a última etapa do `historico`, inclui `review`) **ou** card em `front` com `aguardando_humano` (o agente parou pedindo algo; o `resumo` diz o quê, ex.: "preciso de: ..."). Mostre o botão nos dois casos.
- `atualizar_pendencias` (botão ↻): sem `key`.
- `remover_anexo` (`{"acao":"remover_anexo","key","arquivo","por"}`): apaga `cards/<KEY>/anexos/<arquivo>` e o anexo não volta nos próximos downloads (continua no Jira). `arquivo` é só o nome, sem pasta. Vale um botão de lixeira em cada anexo listado; com o card rodando, a esteira avisa no `resumo` que o agente pode já ter lido.
- `limpar` (`key`) e `faxina` (sem `key`): só quando o humano pede; nada é limpo sozinho.
Pedido rejeitado vai para `fila/processados/` com um arquivo `<nome>.erro` ao lado explicando o motivo: vale mostrar isso ao usuário.

## 6. Textos que valem destaque

- `resumo` muda a cada passo (ex.: "push: rodando a suíte", "abrindo o PR", "PR aberto: <url>"). Mostre sempre o mais recente.
- Card `inviavel`: o `resumo` vem no formato `"<tipo>: <motivo> | destrava: <o que destrava>"`, com tipo ∈ `backend-pendente`, `sem-design`, `regra-indefinida`, `depende-de-card`, `outro-repo`, `escopo-grande`, `outro`. Vale mostrar o tipo como etiqueta. O mesmo texto é comentado automaticamente no card do Jira.
- `preview_url` só existe em card com critério visual, na validação (`http://192.168.1.173:530x/`). Card sem preview se valida pelo diff e pelas evidências.

## 7. Arquivos do card (`cards/<KEY>/`), para links ou visualização

`triagem.md`, `implementacao.md`, **`review.md`** (novo: veredito e achados por severidade 🔴/🟡/⚪), `qa.md`, `evidencias/*.png` e **`evidencias/*.txt`** (critério não visual: comando e saída), **`aprendizados-qa.md`** (novo). Não exponha `push.log`, `.interno.json` nem `.lock`.

## 8. Vagas e anexos

- `.escritorio/config.json` com `{"max_ativos": 2}` define quantos cards rodam ao mesmo tempo; o despachante lê a cada ciclo, sem reiniciar. Se quiser, o escritório pode mostrar/editar esse número.
- `cards/<KEY>/anexos/`: anexos do card no Jira, baixados pela esteira (vale listar como links no card).

## 9. Funcionários na tela: um por card rodando

A esteira roda até `max_ativos` cards ao mesmo tempo (`.escritorio/config.json`, hoje 2). Não é um funcionário fixo por sala:
- Mostre **um funcionário por card com `status: rodando`**, na sala da `etapa` (mapeamento da seção 1), com a `key` no crachá e o `agente` do `estado.json` como papel (`triador`, `front-dev`, `reviewer`, `qa`).
- Dois cards podem estar na **mesma sala** (ex.: dois front-devs), cada um no seu worktree.
- Card com `aguardando_humano` não ocupa vaga: pode aparecer parado/esperando na sala, mas não trabalhando.
- O manager de cada card é opcional na tela (ex.: uma sala de coordenação com um avatar por card rodando).
- O review dispara vários revisores em paralelo por alguns minutos; se quiser mostrar isso, o detalhe por subagente não está no `estado.json` (só o `agente` principal da etapa).

## 10. Revisão de PR de terceiros (`tipo: "revisao_pr"`)

- Pedido: `{"acao":"revisar_pr","key":"PR-<repo>-<n>","url":"https://github.com/leme-tech/<repo>/pull/<n>","repo","numero","comentario"(foco opcional),"por"}`. Só leme-tech.
- **Chave: `PR-<repo>-<n>`, com `<repo>` exatamente como no link do GitHub** (minúsculo, mantendo hífen e ponto): `PR-leme-app-870`, `PR-leme-core-883`, `PR-leme.tec.br-12`. Não mude a caixa nem troque ponto por hífen: a esteira confere a chave contra `repo` e `numero` e recusa (com `.erro` dizendo o formato certo) qualquer variação. O card fica em `cards/PR-<repo>-<n>/`. (`PR-<n>` sem repo ainda é aceito só para o leme-app, por compatibilidade.)
- Repos com review hoje: leme-app (`/review`), leme-core e leme-assistant (`/review-repo`, checklists em `esteira/review/<repo>/`). Repo sem checklist (ex.: leme.tec.br) vai para `erro` com o resumo "sem checklist de review para <repo>".
- `estado.json` ganha `tipo: "revisao_pr"`, `pr_url`, `repo`, `numero`, `base`, `publicado` (null/true/false) e, depois de publicar, `review_url`. `summary` = título do PR + autor.
- Etapas: `fila → review → validacao (aguardando_humano) → concluido`. Sem front nem QA, e nada no Jira (a chave não é card do Jira).
- Na validação, mostre o `review.md` e os achados de `cards/PR-<repo>-<n>/achados.json` (`[{"id","severidade":"blocker"|"should"|"nit","arquivo","linha","lado":"RIGHT"|"LEFT","trecho","texto"}]`, todos com linha no diff do PR), cada um com checkbox e texto editável.
- **Publicar no GitHub** = `{"acao":"aprovar","key","comentarios":[{"id","arquivo","linha","lado","texto"}],"resumo","por"}`: o despachante posta UM review COMMENT com `body` = `resumo` exato e os comentários inline com o `texto` exato que veio no pedido (nunca o do `achados.json`). Linhas fora do diff ficam de fora e o `resumo` do card lista as recusadas (também em `comentarios_recusados` no `estado.json`).
- **Não publicar** = `devolver` com `comentario: "não publicar"`. `devolver` com outro comentário revisa de novo usando o comentário como foco.
- Se a publicação falhar, o card fica em `validacao`, o `resumo` diz o motivo e o pedido vira `.erro`; dá para clicar de novo.
- `limpar` remove o worktree do PR como nos outros cards.

## 11. Só para informação (não precisa implementar)

- A esteira move o status do card no Jira sozinha: Desenvolvendo (front), Revisando Código (review até PR aberto), Testando (PR mergeado).
- `pendencias.json` agora traz só cards da sprint ativa.
- Reiniciar o despachante não derruba card em andamento: o novo processo adota os managers vivos.

## 12. Redator: rascunho de card novo acende o robô dele

O rascunho de card novo é escrito pelo agente `redator` (sala `triagem`), que a esteira roda como sessão própria (`claude -p --agent redator`), não como subagente. Por isso hoje a mesa dele fica dormindo e quem acende é o robô do manager/esteira.

- Para cada `novos/<id>/` com `estado.json` em `status: "rascunhando"` (e sem `descartado`), mostrar um funcionário `redator` na sala triagem, `working`, com o resumo do pedido (`pedido.json` → `texto`, encurtado) como detalhe.
- Quando o status sair de `rascunhando` (vai para `rascunho` ou `erro`), o funcionário some e a mesa volta a dormir.
- Sessões headless que tenham agente não devem acender o robô "esteira". O transcript traz, logo no começo, uma linha `{"type": "agent-setting", "agentSetting": "<nome>", "sessionId": "..."}`; se esse nome for de uma mesa, a sessão conta como trabalho dessa mesa (vale também para `--agent manager`).
- Se o redator já aparece como funcionário por causa do `rascunhando`, esconder a mesa `d:redator` (mesma regra do `rolesComCard` da seção 9), para não mostrar dois redatores.
- Opcional: com esse mesmo `agentSetting`, mostrar a ação atual do redator ("Lendo pedido.json", "Escrevendo rascunho.json"), como já é feito com os subagentes.

Conferido na esteira (07/11/2026): o `agent-setting` aparece em todas as sessões `--agent` (`manager` e `redator`) em `~/.claude/projects/-home-leme-workspace/<sessionId>.jsonl`, exatamente nesse formato. Sessões `claude -p` **sem** `--agent` (ex.: calibrações de review rodadas à mão) não têm essa linha: devem continuar caindo no robô "esteira".
