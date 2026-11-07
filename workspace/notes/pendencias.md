# Pendências do setup do workspace

Atualizado em 06/11/2026.

## Repos do time (PR quando der, nada bloqueando)

- [ ] Skill `ship` do leme-app: tirar a dependência de "SSH quebrado" (era o notebook) e o push por `HEAD:refs/heads/<branch>`. Enquanto isso, o `CLAUDE.md` do workspace orienta push por SSH.
- [ ] README do leme-app diz que o pre-push roda só Biome, mas desde 27/10 ele roda `pnpm test` também (vale o hook).
- [ ] leme-app não tem `CLAUDE.md`; o que hoje está espalhado nas skills e no README poderia ter um resumo lá.
- [ ] `/home/lombeira/...` hardcoded na skill `solve-card` e no `.claude/settings.json` do leme-app.
- [ ] **PRs do time sobre Node** (o Glauco leva para a Feda; não abrir pela esteira). Medido em 06/11/2026 num worktree limpo da main: no Node 26, **137 falhas em 88 arquivos** (`localStorage` nativo do Node sobrepõe o do jsdom); no Node 24.22.1, **0 falhas em 3345 testes**.
  - [ ] (a) `.nvmrc` com `24` no leme-app e o workflow do CI com `node-version-file: .nvmrc` em vez de `lts/*`, para CI, máquinas e esteira ficarem na mesma versão. Com o `.nvmrc`, a esteira passa a ler a versão do repo sozinha.
  - [ ] (b) CI rodando os testes unitários. Hoje só o pre-push roda, então a main não tem garantia de suíte verde.
  - [ ] (c) Setup do vitest compatível com Node 26 (remover o `localStorage` nativo antes do jsdom), para o time poder subir de versão depois.
- [ ] Skill `video-maker` duplicada no leme-app e no leme-videos, já divergentes. A completa é a do leme-videos; remover a cópia do leme-app.

## Documentação do leme-assistant (achado na mineração do checklist, 07/11/2026)

- [ ] README atrasado: diz 4 perguntas simultâneas e 1 por pessoa (código: 20 e 2), 2 ferramentas (hoje 6), que o modelo não vê texto livre (desde o PR #10 vê, com nomes mascarados); tabela de eventos SSE sem `file`, `chart`, `conversation`, `message`.
- [ ] ADR-0001 ainda "Proposto" e desatualizado: não registra o texto de anotação indo para a Anthropic (PR #10), as imagens (PR #26) nem o aviso no Slack com nomes de alunos (PR #24) no mapeamento da LGPD.
- [ ] Grant em `persons.birth_date` (para calcular idade) contradiz a documentação que diz que nascimento não passa.
- O repo nunca teve review humana: a revisão da esteira (`/review-repo`) é hoje o único olhar além do autor.

## Landing (leme.tec.br): problemas que já existem (achados na mineração do checklist, 07/11/2026)

Conferidos por mim: 1, 2, 3 e 4. Os outros vêm do relatório do agente (build e `curl` no site no ar) e valem confirmar antes de virar card.
- [ ] **Número de alunos errado na calculadora do VAAR** (informação ao cliente): `CalculadoraVAAR.tsx:95` mostra "~N alunos" calculado como `valor / 341`. Acrelândia: 1.502.649 / 341 = ~4.407 alunos; a planilha teria 2.054 (o agente mediu ~2,3x a mais na mediana).
- [ ] **Sem sitemap nem robots**: `/sitemap-index.xml` e `/robots.txt` dão 404; falta `site` no `astro.config`. Nenhuma página com Open Graph nem canonical.
- [ ] **Âncora `/#solucoes` quebrada** no menu e no breadcrumb das páginas de solução: a seção com `id="solucoes"` só existe em `/institucional`, não na home.
- [ ] **Rodapé com links `href="#"`** (inclusive Política de privacidade, Termos de uso e LGPD).
- [ ] 3 links internos de posts apontam para URLs do site antigo (404).
- [ ] `/institucional` parece ter conteúdo de exemplo: fotos de `i.pravatar.cc` e números sem fonte ("98% frequência").
- [ ] `update-vaar.py` divergente do `update-vaar.mjs`; `.xlsx` da raiz desatualizados; `src/data/posts.ts` (1.291 linhas) sem uso.
- [ ] Home carrega 588 KB de JS (o `vaar.json` inteiro vai junto) e uma imagem de 1,7 MB exibida em 300 px.
- [ ] Pre-commit baixa a planilha a cada commit e falha sem rede; os PRs #36 e #37 usaram `--no-verify` (que a trava do workspace bloqueia).
- O repo nunca teve review humana: as 17 reviews são de IA ("Julius AI"). A `/review-repo` passa a ser o único olhar além do autor.

## Servidor

- [ ] Docker rootless para o usuário `leme`, quando alguém precisar rodar o leme-core daqui (precisa de `apt` com sudo). Não colocar o `leme` no grupo `docker`: equivale a root.
- [ ] leme-assistant é Python com `uv`; instalar o `uv` sem sudo quando for trabalhar nele.
- [ ] Node: instalado 26.12.0 porque a LTS atual (26.13.0, de 28/10) tinha menos de duas semanas. Atualizar depois de 11/11 com `fnm install 26.13.0 && fnm default 26.13.0`.

## GitHub

- [ ] Token fine-grained do `gh` vence em 90 dias (por volta de 04/02/2027). Ele vê os 17 repos da org; o Glauco decidiu não restringir.
- [ ] (Opcional) Ruleset na org `leme-tech` bloqueando force push e deleção e exigindo PR na main. É a única trava que fecha o `--no-verify` dentro de script e o Husky no terminal humano. Só o Glauco consegue (o token não tem Administration).

## Obsidian no PC

- [x] Obsidian no PC sincronizando nos dois sentidos (06/11/2026). O acesso usa a chave `lombeira@White-Wolf` (o PC do Glauco), única no `authorized_keys` do `leme`.
- [ ] O bare (`~/git/workspace.git`) recusa force push e deleção (`receive.denyNonFastForwards`, `receive.denyDeletes`), mas isso não foi testado: as travas do Claude barram o teste, de propósito.

## Backup

Hoje o único lugar com o histórico completo é o disco do servidor (`~/git/workspace.git` e `~/workspace`). Os repos de código estão no GitHub; o que não tem cópia é o workspace (memória, notas, config).

Opções, todas sem expor nada para a internet:

1. **O clone do PC já é um backup.** Depois do setup do Obsidian, o PC tem o histórico inteiro do git. Custo zero. Limite: se uma nota for apagada, o sync apaga nos dois lados (o histórico continua tendo a versão antiga, mas é preciso saber recuperar).
2. **Segundo disco ou HD externo no servidor**, com um `git bundle` ou `git clone --mirror` diário do bare. Precisa de sudo uma vez para montar o disco e liberar um agendamento para o `leme` (cron, ou `loginctl enable-linger leme` para timer do systemd).
3. **NAS ou outra máquina da rede**, recebendo `git push --mirror` por SSH. Fica em outro hardware, mesma casa.
4. **Cópia fora de casa criptografada**, com `restic` ou `borg` para um HD que sai de casa, ou para armazenamento em nuvem. Só conexão de saída, criptografada antes de sair; não abre porta. É a única opção que sobrevive a incêndio ou roubo, mas os dados (cifrados) saem de casa: decisão sua.

Sugestão: 1 agora (já vem com o Obsidian) e 2 ou 3 quando der, com 4 se quiser proteção fora de casa.
