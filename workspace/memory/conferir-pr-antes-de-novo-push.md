---
name: conferir-pr-antes-de-novo-push
description: empurrar commit para branch cujo PR já foi mergeado deixa o trabalho órfão — conferir o estado do PR antes de cada push
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bfe7450d-9a3a-4bb0-876c-25f2bcc1d511
  modified: 2026-09-26T14:40:42.733Z
---

Antes de empurrar mais commits para uma branch que já tem PR aberto, **conferir
se o PR ainda está aberto**: `gh pr view <n> --json state --jq .state`.

Em 06/09/2026 isso custou duas perdas na mesma sessão. O **#617** foi mergeado
às 14h49 com apenas o primeiro commit; os três seguintes — foram empurrados depois
e ficaram órfãos. Só apareceram porque o Glauco perguntou "o botão de ver
resultado ainda tá lá, em qual caso a gente mostra?". O **#619** foi mergeado no
meio de outro trabalho e a branch foi apagada; o push seguinte a **recriou**, com
um commit solto em cima.

**Why:** o Glauco mergeia rápido e do celular, no meio da conversa. A branch some
junto com o merge, e o push não falha — ele recria a branch ou empilha commits
num PR fechado, calado. O trabalho fica no remoto e nunca chega na `main`.

Em 26/09/2026 aconteceu de novo, com a regra já escrita: a checagem
(`gh pr list --head <branch> --state all`) e o push foram no **mesmo comando**,
então o push saiu antes de alguém ler o `MERGED` do #722. E um `gh pr list`
anterior, só com PRs abertos, tinha sido lido como "a branch não tem PR".

**How to apply:** conferir o estado do PR antes do push, **numa chamada separada,
e ler o resultado antes de empurrar**. Branch sem PR aberto não quer dizer sem
PR: usar `--state all`. Se já mergeou, cortar
branch nova da `origin/main` atualizada e `git cherry-pick` os commits órfãos —
esperar conflito de import, porque a `main` andou. E avisar o Glauco quando
empurrar algo para uma branch cujo PR pode já ter entrado. Ver
[[validate-fixes-empirically]].
