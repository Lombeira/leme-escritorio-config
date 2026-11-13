---
status: fechado
fechado_em: 2026-11-12 17:19 (aprovado)
card: LM-2890
---
# LM-2890: a lista de avaliações V2 ganha a coluna "Área do conhecimento"

**Abrir:** http://192.168.1.173:5301/dashboard/mapa/exams
**Entrar com:** sua conta (o QA usou ADMIN)
**Celular:** F12 → ícone de celular → largura 390

## Decida antes de aprovar
- **Várias áreas aparecem separadas por vírgula** ("Linguagens, Matemática"), não como etiquetas. O card não definia; etiquetas não cabiam nos 200 px da coluna. Trocar depois mexe só num arquivo.

## Como validar (uns 4 minutos)
1. Abra o link acima → **deve aparecer** a coluna **ÁREA DO CONHECIMENTO** entre **ETAPA** e **DIAGRAMAÇÃO**. (print: `evidencias/1-tabela-desktop.png`)
2. Ache a avaliação **"Alvo 1 - Teste da Feda"** → na coluna nova, **deve aparecer** "Linguagens, Matemática", cada área uma vez só.
3. Ache **"acacad"** → **deve aparecer** só "Linguagens". (print: `evidencias/2-so-linguagens.png`)
4. Ache **"Teste 2"** (está Pendente, sem área) → a célula da coluna nova **deve ficar vazia**, sem traço. (print: `evidencias/4-sem-area.png`)
5. Role a tabela para o lado → **AÇÕES** e **NOME** ficam parados e os títulos continuam alinhados com as linhas. (print: `evidencias/1b-tabela-rolada.png`)
6. Busque um nome que não existe → **deve aparecer** a mensagem de lista vazia ocupando a largura toda. (print: `evidencias/6b-filtro-vazio.png`)
7. No celular (390): os cartões com área mostram **"Área do conhecimento"** e os nomes; o cartão **"Teste 2"** não mostra essa linha. (prints: `evidencias/5-mobile.png`, `evidencias/5b-mobile-sem-area.png`)

## Não precisa conferir
- Ordenação por Nome, Ano Escolar, Etapa e Criado em (o QA conferiu; a coluna nova não ordena, de propósito).
- Tipos, larguras e testes automáticos (o QA conferiu por comando; 40 testes relacionados passaram).

## Detalhes técnicos
- **QA: APROVADO (7/7)**, desktop 1440x900 e celular 390x844, console sem erros. Filtros de Ano e Etapa não foram exercitados além da busca (o código deles não mudou). Quadro completo e prints: `.escritorio/cards/LM-2890/qa.md` e `evidencias/`.
- **Review: READY.** 0 blockers, 0 should-fix, 4 nits não corrigidos (`areasDoConhecimento` chamada duas vezes por cartão, `!isMobile` redundante, índice `[4]` no teste, falta de comentário na largura).
- **Front-dev:** biome, tsc e 40 testes relacionados passaram.
- Commit na branch: `64c65bd1` (a coluna). O `[kb]` que o hook tinha posto foi tirado em 12/11 (o Doc reorganizado entra com o LM-2903).
