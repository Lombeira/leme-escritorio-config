---
name: escopo-na-url-existe-para-link-compartilhado
description: "escola/turma/ano vivem na query string por causa de compartilhamento de link, não por conveniência de estado"
metadata: 
  node_type: memory
  type: project
  originSessionId: 84c935c9-fd4d-45e7-8729-be6243d5c9d0
  modified: 2026-09-02T12:31:04.503Z
---

Escola, turma, ano **e o modo analytics** ficam na query string do leme-app
porque o requisito de produto é **compartilhar link**: alguém manda a URL de uma
página já filtrada e quem recebe abre na mesma visão. Não é uma escolha de
arquitetura de estado. O analytics entrou porque, segundo o Glauco, são as telas
mais compartilháveis da aplicação — é onde estão os dados que importam.

**Why:** em 02/09/2026 o Glauco pediu para revisar o mecanismo e reforçou que o
motivo de a feature ter nascido era esse, e que ele nunca funcionou de verdade
para quem recebia o link deslogado — os guards jogavam para `/` e descartavam
path e query. Sem essa intenção registrada, qualquer refactor "limpa" o escopo
para localStorage ou store em memória e mata o requisito de novo.

**How to apply:** propostas que tirem o escopo da URL estão erradas por padrão —
confirme antes. E qualquer caminho novo que expulse o usuário para o login
(guard de rota, 401 no interceptor) tem que preservar `pathname + search` no
`?redirect=`, senão o link compartilhado quebra exatamente para quem chega
deslogado. Ver [[info-errada-na-tela-e-bug]] e [[validate-fixes-empirically]].
