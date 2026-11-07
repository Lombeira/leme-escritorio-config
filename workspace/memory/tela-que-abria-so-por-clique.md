---
name: tela-que-abria-so-por-clique
description: Passar estado de tela para a URL expõe toda a janela de hidratação que o clique escondia; auditar antes de shippar
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7318648c-dfec-4dac-a19d-e921cedc2419
  modified: 2026-09-08T18:33:01.910Z
---

Ao levar para a query string um estado que antes só existia por clique (drawer,
filtro, modo), **audite tudo que roda na montagem antes de abrir o PR**. O clique
acontecia segundos depois do load, com a página inteira hidratada; o link põe o
mesmo código dentro da janela de hidratação, onde o escopo é stub e os efeitos de
limpeza ainda vão rodar.

**Why:** em 08/09/2026 isso quebrou o homolog três vezes seguidas no mesmo PR de
Conteúdos (LM-2380): (1) `formatClassName` recebeu a turma só de `{ id }` e a
tela caiu no error boundary; (2) a consulta de BNCC sem matéria entrou na rajada
de load e estourou o timeout de 10s; (3) o efeito que larga os filtros ao trocar
de visão rodava na montagem e apagava o que o link acabou de trazer. A suíte
passou nas três porque o fixture do teste era mais hidratado que a realidade.

**How to apply:** antes de shippar, liste o que roda na montagem e responda três
perguntas — quem lê objeto do escopo assumindo campo além do `id`? qual
requisição dispara sem o pré-requisito estar preenchido? qual efeito **limpa**
estado e roda sem ser numa transição real? Depois abra a URL nova no browser e
confira: erro no console, aba de rede sem requisição de param vazio, e F5
preservando o que o link trouxe. Ver [[validate-fixes-empirically]] e
[[info-errada-na-tela-e-bug]].
