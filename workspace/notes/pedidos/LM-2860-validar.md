---
card: LM-2860
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/876
fechado_em: 2026-11-07 14:25 (aprovado)
---
# LM-2860: validar builder de trilhas (e alternativas/Capitão) abrindo o app por http://IP
**PR:** https://github.com/leme-tech/leme-app/pull/876

**Link:** http://192.168.1.173:5301/ (preview na rede de casa, por IP: é contexto inseguro de verdade, `window.isSecureContext === false`, então reproduz o cenário do bug)
- Worktree: `repos/leme-app/.worktrees/LM-2860`
- Branch: `LM-2860-frontend-builder-de-trilhas-quebra-ao` @ `1187bf2a` (só local, sem push)
- Diff: `git -C repos/leme-app/.worktrees/LM-2860 diff origin/main...HEAD` (9 arquivos, +97 −12)
- Evidências: `.escritorio/cards/LM-2860/evidencias/`
- Review: READY, 0 blockers, 0 should-fix, 2 nits não corrigidos (`.escritorio/cards/LM-2860/review.md`)

## O que mudou
- `src/utils/create-id.ts` (novo): `createId()` usa `crypto.randomUUID()` quando existe; senão monta um UUID v4 com `crypto.getRandomValues` (que existe em contexto inseguro) e, sem `crypto` nenhum, com `Math.random`.
- `src/utils/create-id.test.ts` (novo): 4 testes (com `randomUUID`, sem `randomUUID`, sem `crypto`).
- Os 8 usos de `crypto.randomUUID` em código de produção passam a usar `createId()`:
  - store `useLearningTracksBuilder` (2x; o `generateTempId` saiu),
  - banco de questões: `question-create-drawer`, `question-edit-drawer`, `question-bank-item-to-draft`, `local-storage-questions`,
  - Capitão Leme: `use-capitao-chat`, `images.ts`.
- Escopo: a triagem incluiu alternativas de questão e Capitão (mesmo bug, mesmo helper). Se preferir separar, é só devolver pedindo para tirar.
- Fora do escopo: outras APIs que só existem em contexto seguro (`navigator.clipboard`, câmera/OMR) podem continuar falhando por IP.

## O que validar
Pelo link acima (http://IP), com o console aberto:
1. Trilhas de aprendizagem → criar trilha nova: o builder abre com as etapas, sem `crypto.randomUUID is not a function`.
2. Editar uma trilha existente: etapas com avaliações vinculadas aparecem; arrastar/adicionar avaliação funciona.
3. Banco de questões (tela larga): criar questão e adicionar alternativas; editar questão e adicionar alternativa.
4. Capitão Leme: mandar mensagem (e anexar imagem).

## QA (rodada 1): APROVADO
Contexto inseguro simulado com `addInitScript` removendo `Crypto.prototype.randomUUID` (o preview do QA era em 127.0.0.1, que conta como seguro). Escola teste da Feda, usuário ADMIN. Nada salvo em homolog; só ficou uma conversa "QA LM-2860 teste de mensagem oi" no histórico do Capitão do admin.

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Nenhum `crypto.randomUUID` fora do helper | APROVADO | evidencias/1-grep-randomuuid.txt |
| 2 | `createId` nos 8 pontos | APROVADO | evidencias/2-grep-createid.txt |
| 3 | Teste do helper (4 testes) | APROVADO | evidencias/3-vitest-create-id.txt |
| 4 | Criar trilha sem `randomUUID` | APROVADO | evidencias/4-criar-trilha-etapas.png |
| 5 | Editar trilha, adicionar avaliação | APROVADO | evidencias/5-editar-trilha-etapas.png, 5b-avaliacao-adicionada-etapa.png |
| 6 | Banco de questões: alternativas em criar e editar | APROVADO | evidencias/6a-criar-questao-alternativas.png, 6b-editar-questao-alternativa.png |
| 7 | Capitão: mensagem e imagem | APROVADO | evidencias/7-capitao-mensagem-imagem.png |
| 8 | Regressão em contexto seguro | APROVADO | evidencias/8-4-criar-trilha-etapas.png, 8-5-editar-trilha-etapas.png, 8-5b-avaliacao-adicionada-etapa.png |

## Nits do review (não corrigidos, opcionais)
- `src/utils/create-id.ts:6`: o fallback com `Math.random` não diz que é último recurso e não criptográfico.
- `src/utils/create-id.test.ts:14/29/36`: o `vi.stubGlobal("crypto", ...)` se repete em três testes.
