---
card: LM-2800
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/870
---
# LM-2800: validar Mapa mostrando as escolas que têm o Mapa (volta: tapa visual)

**PR:** https://github.com/leme-tech/leme-app/pull/870

**Link:** http://192.168.1.173:5301/dashboard/mapa/pedagogical-map (preview do worktree, aponta para homolog; cai ao sair da validação ou em 24 h)
- Worktree: `repos/leme-app/.worktrees/LM-2800`
- Branch: `LM-2800-frontend-mapa-mostrar-as-escolas-que-tem` @ `9362dac8` (só local, sem push)
- Diff desta volta: `git -C repos/leme-app/.worktrees/LM-2800 diff b951fb5e..HEAD`; diff inteiro: `git -C repos/leme-app/.worktrees/LM-2800 diff -M origin/main`
- Evidências novas: `.escritorio/cards/LM-2800/evidencias/r3-*.png`

## Por que voltou
Você devolveu: "Apesar do card descrever como queria, eu achei que ficou bem grosseiro! Eu acho que falta um tapa visual!". A funcionalidade não mudou; esta volta mexeu só no visual da lista e do aviso.

## O que validar
1. **Lista de escolas** (professor com 2 escolas com Mapa, admin com 9), V1 e V2:
   - Agora é uma coluna centralizada: ilustração menor, título centralizado e os botões em grade (1 coluna no celular, até 2 a partir de 768 px, até 3 a partir de 1280 px).
   - Cada botão (ainda o `SecondaryButton`) tem ícone de escola num círculo azul claro e o nome em semibold; o município do admin fica em cinza embaixo.
   - O admin com 9 escolas vê uma grade 3x3 em vez de 9 linhas.
   - Prints: `r3-lista-v1-professor.png`, `r3-lista-v1-admin.png`, `r3-lista-professor-360.png`.
2. **Aviso "Abrimos o Mapa da escola X."**: saiu a faixa azul forte de largura toda. Agora é uma caixa compacta centralizada, azul clara com borda fina (mesmo estilo do alerta de próxima aula da Home), com o ícone do Mapa e o nome da escola em negrito. Prints: `r3-aviso-v1.png`, `r3-aviso-v2.png`, `r3-aviso-v1-escuro.png`.
3. **Pontos para decidir no olho:**
   - Em tela larga, a disposição virou grade em vez do padrão em linha de "Hoje você dá aula em:" da Frequência (o botão é o mesmo). O critério 5 falava desse padrão.
   - No tema escuro a borda do aviso fica azul claro (sem par escuro), como nos alertas da Home.
   - O aviso deixou de ser `role="alert"` e virou `<output>` (`role="status"`, mais discreto). Pode não ser anunciado por leitor de tela ao aparecer (achado do review abaixo do corte, só informativo).

Para ver o aviso, simule uma escola com Mapa só: no console, `localStorage["leme:gb-overrides"]` com `IsMapaLemeEnabled` só com a Faino, logado como professor, com a "Escola teste da Feda" no topo. Passo a passo em `implementacao.md`, rodada 4, "Como testar".

## Implementação (resumo)
- **Rodada 4 (`7ce184bf`):** tapa visual em `MapaSchoolsPicker` (grade, ícones, hierarquia de texto) e no aviso (callout compacto). Os textos dos critérios continuam exatos; os testes passaram a conferir o texto inteiro do aviso, porque o nome em negrito divide a frase.
- **Rodada 5 (`9362dac8`):** o aviso foi para o próprio componente, `src/components/MapaSchoolSwitchNotice/` (achado do review).
- O resto vale como antes: hook `useMapaLemeSchoolChoice` no V1 e no V2, store do aviso alimentado pelo Layout, `no_permission` virou `school_without_map` no Mapa (quebra a série desse evento no Amplitude), clique registra `switch_school`, sem requisição nova.

## Review: READY (rodada 5)
- **Rodada 4:** 1 should-fix (dois componentes no mesmo arquivo), resolvido na rodada 5.
- **Nits que ficaram:** ternário aninhado no `emptyStateReason`; comentário do `school_without_map` em `tracking-plan.ts:590`; comentário duplicado no V2; papel `status` no aviso (abaixo do corte).
- Detalhes em `.escritorio/cards/LM-2800/review.md`.

## QA (rodada 3): APROVADO

| # | Critério | Resultado |
|---|---|---|
| 1 | Uma escola com Mapa: troca e frase "Abrimos o Mapa da escola X." (simulado; texto do elemento inteiro exato, nome em `<strong>`) | APROVADO |
| 2 | 2+ escolas com Mapa: lista só com elas (professor 2, admin 9) | APROVADO |
| 3 | Clicar numa escola troca a escola, limpa turma e ano e segue o fluxo | APROVADO |
| 4 | Município só para admin (coordenação e direção sem conta) | APROVADO |
| 5 | 360 px empilhado em largura total; desktop em grade 3x3 com 9 escolas, sem ocupar a tela toda | APROVADO |
| 6 | Sem "permissão", "acesso" ou "negado" | APROVADO |
| 7 | Critérios 1 a 3 iguais em V1 e V2 | APROVADO |
| 8 | `no_permission` some do Mapa | APROVADO |
| 9 | `school_without_map` no tracking-plan e nas duas páginas | APROVADO |
| 10 | Nenhuma requisição nova (pelo diff) | APROVADO |

Console sem erros e sem "Maximum update depth exceeded"; sem rolagem horizontal em 1440, 1100 e 360 px. Observações do QA: nomes em CAIXA ALTA do admin quebram em 2 ou 3 linhas (cartões da linha ficam com a mesma altura); em 360 px a lista do admin dá uns 1250 px de rolagem; a lista em tema escuro não foi capturada; a troca pelo seletor do topo segue coberta só por teste unitário.

## Proposta para o Jira (não enviada, precisa do seu OK)
Comentário no LM-2800: "Implementado no front, sem backend novo. Atenção: no Mapa, o motivo de tela vazia do analytics mudou de `no_permission` para `school_without_map`, então a série antiga para nesse evento. Falta em homolog um usuário com exatamente uma escola com Mapa para testar a troca automática com dados reais."
