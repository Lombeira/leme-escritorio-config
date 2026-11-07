---
name: codigo-quase-sem-comentario
description: "leme-app tem mediana 0% de comentário e p90 15,6%; escrever acima disso faz o Glauco parar para limpar"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bfe7450d-9a3a-4bb0-876c-25f2bcc1d511
  modified: 2026-09-04T11:23:53.780Z
---

O leme-app tem **mediana 0%** de linhas de comentário por arquivo e **p90 de
15,6%** (medido em 581 arquivos de `src`, ignorando testes). Vale nos dois repos.

Em 04/09/2026 o Glauco parou para limpar comentários de arquivos que eu
escrevi — estavam em **27–28%**, quase o dobro do p90. Ele perguntou se o build
não cortava; corta (só `/*!` de licença sobrevive), mas o custo nunca foi bytes.

**Why:** prosa demais é ruído e vira trabalho de limpeza para ele. Mas nesta
mesma sessão vários bugs voltaram porque a razão de uma linha não estava escrita
em lugar nenhum.

**How to apply:** mirar em **8–10%**, não em zero. Comenta só armadilha: o que
alguém "simplificaria" e reintroduziria o bug, e o porquê de um número medido em
campo. Não comenta o que o nome já diz, não escreve docstring que reexplica a
assinatura, e não repete o título do `it` dentro do teste. Ver
[[validate-fixes-empirically]].
