---
card: LM-2858
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/874
fechado_em: 2026-11-07 13:32 (aprovado)
---
# LM-2858: validar zerar vulnerabilidades do pnpm audit no leme-app

**PR:** https://github.com/leme-tech/leme-app/pull/874

**Link:** abra em contexto seguro: `ssh -L 5301:localhost:5301 leme@192.168.1.173` e depois `http://localhost:5301/`. O endereço pela rede (http://192.168.1.173:5301/) também funciona, mas nele Trilhas, Banco de questões e Capitão Leme quebram, e quebram igual na main (ver abaixo). O preview vem do worktree, aponta para homolog e cai ao sair da validação ou em 24 h.
- Worktree: `repos/leme-app/.worktrees/LM-2858`
- Branch: `LM-2858` @ `07bb136a` (só local, sem push). É o mesmo commit da validação anterior, porque a volta 2 não mudou código.
- Diff: `git -C repos/leme-app/.worktrees/LM-2858 diff origin/main` (só `package.json`, `pnpm-lock.yaml`, `src/main.tsx`, `src/router/index.tsx`)
- Evidências: `.escritorio/cards/LM-2858/evidencias/`. Review: READY nas rodadas 1 e 2, sem achados (`.escritorio/cards/LM-2858/review.md`)

## Resposta à devolução (erro em Trilhas) e à pergunta "onde a gente usa crypto.randomUUID"
O erro não vem do card. O navegador só oferece `crypto.randomUUID` em contexto seguro (HTTPS ou localhost). Pelo IP da rede em HTTP ela não existe, e as telas que a chamam no render caem no "Algo deu errado nesta tela". Homolog e produção usam HTTPS, então lá nada quebra. O mesmo acontece com a main servida pelo IP.

| Onde | Tela | Efeito em HTTP pelo IP |
|---|---|---|
| `src/store/useLearningTracksBuilder/index.ts:9` | Trilhas: abrir ou criar trilha | Derruba a tela (reproduzido) |
| `src/pages/questions/components/question-create-drawer.tsx:58` | Banco de questões: a página toda, porque a gaveta de criar fica montada | Derruba a página (leitura do código) |
| `src/pages/questions/services/question-bank-item-to-draft.ts:72` | Banco de questões: editar questão | Derruba a tela (leitura do código) |
| `src/pages/questions/components/question-edit-drawer.tsx:89` | Editar questão: adicionar alternativa | Só a ação falha |
| `src/pages/capitao-leme/hooks/use-capitao-chat.ts:130` | Capitão Leme: enviar pergunta / abrir conversa salva | Enviar derruba a tela; abrir só falha |
| `src/pages/capitao-leme/images.ts:38` | Capitão Leme: anexar imagem | Só a ação falha |
| `src/pages/questions/services/local-storage-questions.ts:70` | nenhuma (código sem uso) | nenhum |
| `navigator.clipboard` em `team-members/.../new-password-field.tsx:46` | Membros: copiar senha | Só a ação falha |
| `navigator.mediaDevices` em `components/PhotoUpload/index.tsx:93,183` | Foto pela câmera | Só a ação falha, com mensagem de erro |

A tabela completa está em `.escritorio/cards/LM-2858/implementacao.md`, seção "Volta 2".

**Proposta (não faz parte deste card):** abrir um card próprio no leme-app, "Gerar ids locais sem depender de contexto seguro". A ideia é um helper `generateId()` que usa `crypto.getRandomValues` quando `crypto.randomUUID` não existe e substitui as 6 chamadas. O texto do card, com os critérios de aceite, está na mesma seção. O Jira é só leitura para a esteira: se for para criar, quem cria é você.

## O que mudou (igual à validação anterior)
- `pnpm audit` zerado em produção **e** em dev. Antes eram 82 em prod (25 high) e 153 com dev (1 critical, do vitest). Agora as quatro invocações dão "No known vulnerabilities found".
- Duas majors:
  - **react-router-dom 6 para 7.18.5** (produção). A 6.x não tem correção para os advisories GHSA-wrjc-x8rr-h8h6 (open redirect) e GHSA-337j-9hxr-rhxg. Em `src` só saíram as flags `future`, que já estavam ligadas e viraram padrão.
  - **vite 5 para 6.4.5** (build e dev). A 5 não tem patch para os advisories do dev server. Parou na 6 porque a 7 muda o target de navegadores do build.
- Na mesma major: axios 1.21, dompurify 3.4.17, tiptap 3.33, vitest/coverage 4.1.12, knip 6.44, sharp 0.35.5, tsx 4.23.
- 16 `pnpm.overrides` para transitivas, cada um preso na major atual. `clear-any-console` ficou fixado em 1.16.2.

## Resultado do QA (rodada 1: APROVADO, segue valendo porque o commit é o mesmo)
| # | Critério | Resultado | O que foi visto |
|---|---|---|---|
| 1 | `pnpm audit --prod` | APROVADO | limpo, exit 0 |
| 2 | `--audit-level=high` e `critical` | APROVADO | ambos exit 0 |
| 3 | `pnpm audit` com dev | APROVADO | limpo, sem exceções |
| 4 | `pnpm install --frozen-lockfile` | APROVADO | exit 0 |
| 5 | `git diff origin/main --stat` | APROVADO | só os 4 arquivos acima |
| 6 | Home, turma, editor tiptap, banco de questões, PDF | APROVADO | editor salva e reabre igual; banco abre com tabela; PDF baixa; console limpo |
| 7 | Navegação, voltar, `?redirect=` | APROVADO | deslogado vai para `/?redirect=...` e volta com escopo; voltar ok; NoMatch e `/qr-code` → `/foto` ok |
| 8 | Chamadas autenticadas, troca de escola | APROVADO | nenhuma resposta >= 400; sem token leva ao login com `?redirect=` |

O QA rodou em `127.0.0.1` (contexto seguro), e por isso Trilhas funcionou nos testes dele. Na volta 1, o front-dev clicou nas 20 linhas de Trilhas em contexto seguro e todas abriram.

## O que validar (pelo `http://localhost:5301` via `ssh -L`)
1. Trilhas: clicar numa linha da tabela abre a gaveta sem erro.
2. Navegar como de costume (Home, turma, anotações com o editor, banco de questões no desktop, PDF de conteúdos) e conferir que o console não tem erro novo.
3. Abrir deslogado um link profundo com escola/ano/turma: tem que ir para o login e voltar para a mesma URL com o escopo.
4. Trocar de escola e turma: sem 401.

## Pontos de atenção
- **Ainda não rodaram:** `pnpm build`, `knip` e a suíte inteira. Eles rodam no pre-push e no CI depois da aprovação.
- **Node do pipeline:** o react-router 7 exige Node >= 20, e o `buildspec.yml` não fixa versão.
- **Não testado pelo QA:** upload de anexo e foto de gabarito com arquivo.
- **PDF:** entre um trecho normal e um em negrito o espaço sumiu. Pode já acontecer na main.
- **Dado criado em homolog:** conteúdo "QA2858 teste" (Arte, 03/11), escola Tunada da Feda.
