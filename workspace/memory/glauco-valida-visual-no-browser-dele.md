---
name: glauco-valida-visual-no-browser-dele
description: "Glauco valida no browser dele primeiro; Playwright não, e a suíte só imediatamente antes de commitar"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fc4e9dac-67f7-48e3-aeec-a5f2d79f93cb
  modified: 2026-09-08T16:33:23.613Z
---

Em trabalho visual/de layout no leme-app, não usar Playwright pra conferir o
resultado: o Glauco valida ele mesmo no browser dele.

**No homelab (desde 06/11/2026):** o dev server roda aqui no servidor, escutando só em
`localhost` (a regra de não expor porta na rede só abre exceção para os previews da esteira, faixa 5301-5309). O Glauco acessa do PC
com túnel SSH, por exemplo `ssh -L 5173:localhost:5173 leme-lab`, e abre
`http://localhost:5173`. Ao subir o dev server, informar a porta e o comando do túnel. E a suíte de testes roda **uma
vez, imediatamente antes de commitar** — não ao terminar cada ajuste, não pra "confirmar que ficou
bom". A ordem é: edito → `tsc` → devolvo pra ele olhar → ele aprova → aí sim suíte + build + lint,
e commit.

**Why:** são 1500 testes e ~40s por rodada. Em 2026-08-31 eu rodava Playwright e `vitest` entre
cada passo e ele interrompeu duas vezes. Em 2026-09-08 repeti: rodei a suíte seis vezes seguidas
ajustando o mesmo componente, ele interrompeu de novo — "torna a sessão insuportável", "eu já
falei isso várias vezes". "Terminei a mudança" não é o fim; o fim é ele ter validado.

**How to apply:** durante o trabalho, só `tsc` (segundos) e `biome check --write` no arquivo
tocado. Explicar o que mudou e onde (arquivo:linha) e devolver. Medição via browser só quando ele
pedir, ou quando a pergunta for numérica e ele não tiver como responder olhando — aí é melhor
mandar um snippet de console pra ele do que abrir Playwright (foi assim que se resolveu a altura
do filtro e o cabeçalho grudado). Isso não afrouxa [[validate-fixes-empirically]]: continua
valendo não declarar pronto sem prova — a diferença é que aqui quem produz a prova é ele, não eu.
Se um teste falhar intermitente, não gastar rodadas de suíte inteira
pra caracterizar: rodar só aquele arquivo.

**Exceção (06/11/2026):** o agente `qa` da esteira usa Playwright headless de propósito,
para testar cada critério de aceite e guardar evidência. A regra acima vale para o trabalho
interativo com o Glauco, não para a esteira.
