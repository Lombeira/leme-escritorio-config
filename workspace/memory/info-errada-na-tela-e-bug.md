---
name: info-errada-na-tela-e-bug
description: "Tela que afirma algo falso é bug, mesmo quando a feature que resolveria nunca existiu"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 05b81162-5b74-4c30-9d49-4c3bc9b1c917
  modified: 2026-08-17T19:39:35.002Z
---

Ao triar report no leme-app, separar "faltou feature" de "a tela afirma algo falso". Ausência de informação é melhoria; afirmação incorreta é bug, mesmo que a feature que a evitaria nunca tenha existido. O teste: existe alguma versão da spec em que essa string é a correta naquele estado? Se não, é bug.

**Why:** Glauco aplicou isso contra o meu próprio hedge — eu havia argumentado que o "Obrigado por hoje" no meio da aula era bug (afirmação falsa), e em seguida tratei "Aula em andamento num feriado" como risco aceitável. É o mesmo defeito; classificar diferente era incoerência minha. O custo de deixar passar não é a feature faltando, é o usuário parar de confiar no alerta inclusive quando ele está certo.

**How to apply:** Verificar se o defeito é separável da feature — geralmente dá para parar de mentir sem construir nada novo, e isso vira um card pequeno que sobe antes. Aceitar que o critério faz o escopo crescer; é consequência esperada, não motivo para relaxar o critério. Ver [[validate-fixes-empirically]] para a prova de que o fix pegou o caso reportado.
