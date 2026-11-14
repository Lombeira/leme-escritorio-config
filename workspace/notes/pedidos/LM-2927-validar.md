---
status: fechado
fechado_em: 2026-11-13 12:32 (aprovado)
card: LM-2927
---
# LM-2927: o "Ajuda" abre o WhatsApp já com e-mail, cargo, escola e navegador de quem pediu

**Abrir:** http://192.168.1.173:5301/dashboard/home?school=ebac582b-e871-4214-a916-0b38f59360ca
**Entrar com:** a conta de teste de professor do qa.env (e a de admin para o passo 4)
**Celular:** F12 → ícone de celular → largura 390 (passo 1)

## Decida antes de aprovar
- **Teste do aviso "função bloqueada" não feito (dispensado pela Feda):** o link "equipe da Leme" desse aviso usa o mesmo código dos outros pontos, mas ninguém clicou nele. Ficou sem prova por falta de conta de SME sem Mapa Leme.
- **Escola vem do seletor.** Na home sem escola escolhida (a home não tem seletor), a linha Escola some, mesmo o professor tendo escola. Alternativa: usar a lista de escolas do usuário; custa um ajuste pequeno no hook.
- **Sem escola, a linha é omitida** (em vez de "Escola: não informada").
- **O item do menu da sidebar aparece como "Ajuda"** na tela, não "Dúvidas".

## Como validar (uns 5 minutos)
1. No celular (390), toque no ícone redondo do topo → **Ajuda** → **deve aparecer:** WhatsApp em nova aba com "Olá! Preciso de ajuda com a plataforma Leme.", E-mail, Cargo: Professor(a), Escola: Escola teste da Feda, Navegador e "Minha dúvida:" (print: `evidencias/1-prof-mobile-avatar-menu.png`)
2. No desktop, rodapé da sidebar → **Ajuda** → **deve aparecer:** a mesma mensagem (print: `evidencias/1-prof-escola-sidebar.png`)
3. Em Horários (`/dashboard/timetable`), escolha "EMEF Melo Martins" no seletor e clique em Ajuda → **deve aparecer:** "Escola: EMEF Melo Martins" (print: `evidencias/3-prof-escola-selecionada.png`)
4. Com a conta admin, em `/dashboard/home` sem escola, clique em Ajuda → **deve aparecer:** E-mail, Cargo: Admin e Navegador, sem linha de Escola e sem "undefined" (print: `evidencias/4-admin-sidebar.png`)
5. Deslogado, na tela de login, clique em Ajuda → **deve aparecer:** só a saudação e "Minha dúvida:" (print: `evidencias/5-login-ajuda.png`)
6. Admin, em Horários, escolha "EMEI JOÃO SERRA HORAMOS FILHO" e clique em Ajuda → **deve aparecer:** o nome com acentos corretos no WhatsApp (print: `evidencias/6-admin-escola-acentuada.png`)

## Não precisa conferir
- Codificação de "&" e "ç": coberta por teste automático (não havia escola assim nos seletores).
- Secretario: mesmo caminho do admin no código, sem conta para testar.
- Sem erro no console em nenhum fluxo.

## Detalhes técnicos
- Commit `4374e53d`. Mensagem montada em `src/constants/help-link.ts`, hook `useHelpLink`, usado no menu do avatar, sidebar, aviso da Base de Conhecimento e login (só saudação).
- Review: READY (rodada 2; o should-fix sobre `summarizeBrowser` era falso positivo, knip sai 0). Restam só nits.
- QA: critérios 1 a 6 aprovados; 7 sem evidência (dispensado pela Feda).
- Checks: biome e tsc ok.
