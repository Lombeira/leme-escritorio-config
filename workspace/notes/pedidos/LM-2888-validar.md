---
status: fechado
fechado_em: 2026-11-13 12:28 (aprovado)
card: LM-2888
---
# LM-2888: novo filtro "Imagem" (com/sem imagem) no banco de itens

**Abrir:** http://192.168.1.173:5301/dashboard/mapa/questions
**Entrar com:** a conta de teste de ADMIN do qa.env (nunca a senha) ou a sua
**Celular:** não se aplica (banco de itens é desktop)

## Decida antes de aprovar
- Rótulos e posição do select: o card não define. Ficou "Imagem" (padrão), "Com imagem", "Sem imagem", como 7º select depois de "Autor". Trocar custa uma linha.
- Observação do QA, anterior ao card: dois filtros trocados com milissegundos de diferença (por script) perdem o primeiro. Com um intervalo normal funciona. Não vira card por enquanto.

## Como validar (uns 4 minutos)
1. Abra o banco de itens → **deve aparecer:** na barra de filtros um select "Imagem" depois de "Autor", alinhado aos outros, sem quebrar a linha (print: `evidencias/1-select-imagem.png`)
2. Escolha "Com imagem" → **deve aparecer:** só questões com imagem; a URL ganha `?hasImage=1` (print: `evidencias/2-com-imagem.png`)
3. Escolha "Sem imagem" → **deve aparecer:** só questões sem imagem (print: `evidencias/3-sem-imagem.png`)
4. Volte para "Imagem" → **deve aparecer:** a lista completa, sem `hasImage` na URL (print: `evidencias/4-padrao.png`)
5. Escolha "Com imagem" + Dificuldade "Fácil" → **deve aparecer:** 36 cards e "36 de 36 questões" (print: `evidencias/5-imagem-mais-dificuldade.png`)
6. Copie a URL e abra em outra aba → **deve aparecer:** select já em "Com imagem" e lista filtrada
7. Aperte F5 com o filtro ativo → **deve aparecer:** o filtro continua

## Não precisa conferir
- O QA já provou pela API que "com" (378) + "sem" (173) = 551 itens, o total sem filtro.
- Registro do filtro no plano de métricas (`has_image`) conferido por comando.
- Console do navegador sem erros.

## Detalhes técnicos
- Commit único: `feat(questions): filtro por imagem no banco de itens [LM-2888]`; sem commit `[kb]` na branch.
- Review rodada 1: READY, sem blocker nem should-fix; um nit opcional (ternário aninhado em `src/pages/questions/index.tsx:75-76`).
- QA: 8 de 8 critérios APROVADOS (`qa.md`). Detalhes em `implementacao.md`.
