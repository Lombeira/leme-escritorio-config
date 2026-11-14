# Aprendizados do QA da esteira

Copiado pelo despachante no fim de cada card. O que valer para todos vai para `esteira/qa/CONHECIMENTO.md` (curadoria com o Claude interativo).

## LM-2800 (07/11/2026 01:18)

# Aprendizados do QA (LM-2800)

- Flags do GrowthBook vêm de `https://cdn.growthbook.io/api/features/sdk-PfBA0nDoUz18QDn8`; `ouvirFlags` do kit não captura nada. Para simular cenário sem tocar em dados: depois do login, `localStorage.setItem("leme:gb-overrides", JSON.stringify({IsMapaLemeEnabled:[{id,name}], "is-mapa-v2-enabled":[...]}))` e `page.goto` de novo. `[]` em `is-mapa-v2-enabled` força o V1.
- Homolog em 07/11/2026: ADMIN vê 60 escolas, 9 com Mapa (Faino 41a3e682-39a9-4edd-a201-ef787ddabb82, Escola teste da Feda ebac582b-e871-4214-a916-0b38f59360ca, 6 de Pompéu, EMEF Todos a bordo!). PROFESSOR: 5 escolas, só Faino e Feda com Mapa; ZEZE SALLES 3ff69be6-2c6b-486f-b418-a8d450c5bc5f sem Mapa. DIRETOR: 1 escola sem Mapa. Nenhum usuário tem exatamente 1 escola com Mapa.
- Seletor do topo: botão com o nome da escola abre `[role=dialog]` com 3 botões (escola, turma, período). Turmas são `getByRole("option")` (o `<select>` "Dados reais" também aparece como option; ignore). Botão do topo: `getByRole("button",{name:/nome da escola/}).first()`. Menu lateral: `getByRole("link",{name:"Mapa",exact:true})`.
- Escrita rápida: as variáveis QA_* não persistem entre chamadas Bash; usar `qa-scripts/env.sh`. Scripts desta rodada: `r2.mjs` (entradas), `ciclo.mjs` (ciclo da frase), `main.mjs` (regressão).
- Faltou no kit: helper de override de flags e de abrir o seletor de escola/turma.
- Dados criados: nenhum.

## LM-2180 (07/11/2026 01:58)

# Aprendizados do QA (LM-2180)

- Analytics em Conteúdos: não é aba. O alternador é um `[role=switch]` no header (ao lado do sino). Depois dele aparece "Selecione a matéria" (menu), o período e o botão "Imprimir conteúdos". Pelo escopo da URL (`school/year/class`) a turma entra direto.
- Modal "Imprimir conteúdos": `getByRole("dialog")`, a disciplina é um `<select>` nativo (`selectOption({label})`), De/Até têm label e aceitam `pressSequentially` só com dígitos (máscara). O download usa `page.waitForEvent("download")`. Nome do arquivo `conteudos_<turma>_<disciplina>_<de>_<ate>.pdf`.
- Verificar PDF: `pdftotext -layout` funciona (poppler está instalado); `pdfinfo` dá as páginas.
- Dados de homolog com conteúdo (a resposta de `GET v2/classes/{id}/contents` é um array puro, não `{data}`; datas via `startDate/endDate`; sem datas só vem uma janela recente):
  - DIRETOR (Paula Portolani) só tem a escola NILVA CAZETO KFOURI (`e8893b5a-2222-4483-b6fd-6786a460ad05`). Turma `910151d8-d8cb-403e-8654-c2e1770c4d10` (6º A, ano 2024 `f2cd8ca0-fcdf-4cca-af8a-950ce77005eb`): 8 disciplinas, 56 conteúdos em nov/2024 (todos os anos de 2026 estão vazios para o DIRETOR).
  - PROFESSOR (Fernanda Guerra) não tem a NILVA na lista de escolas (a API deixa consultar, mas a tela rejeita o escopo). Melhor turma: Escola teste da Feda (`ebac582b-e871-4214-a916-0b38f59360ca`), ano `1de13c22-759e-4d5a-9e8e-160f81c46ea4`, turma A `bc5cbf7f-6e14-4f32-ac32-39fe1a83437e` (ago a nov/2026): ADMIN vê 50 conteúdos / 8 disciplinas, PROFESSOR vê 15 / 4. Serve para testar recorte por professor.
- Nada foi criado em homolog.
- Armadilha: variáveis `QA_*` do shell não persistem entre chamadas de Bash; exporte no mesmo comando do `node`.
- Faltou no kit: helper para ligar o modo Análises e para ler o texto de PDF. O `lib.mjs` deste card (`qa-scripts/`) tem `irAnalises` com escopo por env.

## LM-2800 (07/11/2026 10:56)

# Aprendizados do QA (LM-2800)

- Flags do GrowthBook vêm de `https://cdn.growthbook.io/api/features/sdk-PfBA0nDoUz18QDn8`; `ouvirFlags` do kit não captura nada. Para simular cenário sem tocar em dados: depois do login, `localStorage.setItem("leme:gb-overrides", JSON.stringify({IsMapaLemeEnabled:[{id,name}], "is-mapa-v2-enabled":[...]}))` e `page.goto` de novo. `[]` em `is-mapa-v2-enabled` força o V1.
- Homolog em 07/11/2026: ADMIN vê 60 escolas, 9 com Mapa (Faino 41a3e682-39a9-4edd-a201-ef787ddabb82, Escola teste da Feda ebac582b-e871-4214-a916-0b38f59360ca, 6 de Pompéu, EMEF Todos a bordo!). PROFESSOR: 5 escolas, só Faino e Feda com Mapa; ZEZE SALLES 3ff69be6-2c6b-486f-b418-a8d450c5bc5f sem Mapa. DIRETOR: 1 escola sem Mapa. Nenhum usuário tem exatamente 1 escola com Mapa.
- Seletor do topo: botão com o nome da escola abre `[role=dialog]` com 3 botões (escola, turma, período). Turmas são `getByRole("option")` (o `<select>` "Dados reais" também aparece como option; ignore). Botão do topo: `getByRole("button",{name:/nome da escola/}).first()`. Menu lateral: `getByRole("link",{name:"Mapa",exact:true})`.
- Escrita rápida: as variáveis QA_* não persistem entre chamadas Bash; usar `qa-scripts/env.sh`. Scripts desta rodada: `r2.mjs` (entradas), `ciclo.mjs` (ciclo da frase), `main.mjs` (regressão).
- Faltou no kit: helper de override de flags e de abrir o seletor de escola/turma.
- Dados criados: nenhum.

## Rodada 3 (visual)
- Tema escuro: `localStorage.setItem("chakra-ui-color-mode","dark")` depois do login e `goto` de novo funciona.
- O aviso é `<output>` (role status); conferir texto com `page.locator("output").filter({hasText:"Abrimos o Mapa"})` e `.locator("strong")` para o nome. Botões da lista: pegar por `locator("button")` filtrando o texto; o seletor `xpath //p[contains(.,'Estas escolas')]/following::button` não acha mais nada com o layout novo.
- `qa-scripts/qa.json` criado (base 5301). Scripts da rodada: `r3.mjs a|b|c` (listas, 360, avisos) e `r3b.mjs` (medidas e clique).
- Admin com flags reais: 9 escolas em grade 3x3 de 323 px a 1440 px; a 1100 px a grade é de 2 colunas.
- Dados criados: nenhum.

## LM-2813 (07/11/2026 11:09)

# Aprendizados do QA (LM-2813)

- Caminho até a gaveta de resultados do Mapa (V2): ADMIN, `/dashboard/mapa/pedagogical-map?school=ebac582b-e871-4214-a916-0b38f59360ca&year=1de13c22-759e-4d5a-9e8e-160f81c46ea4&class=d18e5d86-ec6c-41ea-9c7b-ab54e27940c2` (Escola teste da Feda, 5º Ano A - Manhã, 2º Semestre). Clicar em "Língua Portuguesa · Diagnóstica Inicial" abre o painel lateral; botão "Ver resultados" abre a gaveta (abas Resultados, Descritores, Visão geral, não são role=tab: usar getByText exact).
- Essa diagnóstica tem 6 alunos "Aluno Cenário 5A 0x", Q1..Q5 com descritores 5LE2.6 e 5LE1.1. Nenhuma questão sem descritor em homolog: para ver "—", interceptar GET `v2/learning-maps/.../exams/...` com page.route e anular `learningTarget`.
- Tabela da gaveta só rola na horizontal em viewport estreito (600 px); a 1440 cabe tudo.
- Tooltip Chakra tem role="tooltip"; usar `page.getByRole("tooltip")` e boundingBox. Com o modal aberto, getByText pega primeiro o elemento do painel atrás: escopar em `.chakra-modal__body`.
- O "cartão existente de descritor" (DescriptorCard) está no painel lateral, não na aba Descritores da gaveta.
- Seletor da linha de descritores: `thead tr:nth-child(2) > *` (índices 2.. são as questões).
- Falta no kit: helper para abrir a gaveta de resultados do Mapa.

## LM-2180 (07/11/2026 11:46)

# Aprendizados do QA (LM-2180)

- Analytics em Conteúdos: não é aba. O alternador é um `[role=switch]` no header (ao lado do sino). Depois dele aparece "Selecione a matéria" (menu), o período e o botão "Imprimir conteúdos". Pelo escopo da URL (`school/year/class`) a turma entra direto.
- Modal "Imprimir conteúdos": `getByRole("dialog")`, a disciplina é um `<select>` nativo (`selectOption({label})`), De/Até têm label e aceitam `pressSequentially` só com dígitos (máscara). O download usa `page.waitForEvent("download")`. Nome do arquivo `conteudos_<turma>_<disciplina>_<de>_<ate>.pdf`.
- Verificar PDF: `pdftotext -layout` funciona (poppler está instalado); `pdfinfo` dá as páginas.
- Dados de homolog com conteúdo (a resposta de `GET v2/classes/{id}/contents` é um array puro, não `{data}`; datas via `startDate/endDate`; sem datas só vem uma janela recente):
  - DIRETOR (Paula Portolani) só tem a escola NILVA CAZETO KFOURI (`e8893b5a-2222-4483-b6fd-6786a460ad05`). Turma `910151d8-d8cb-403e-8654-c2e1770c4d10` (6º A, ano 2024 `f2cd8ca0-fcdf-4cca-af8a-950ce77005eb`): 8 disciplinas, 56 conteúdos em nov/2024 (todos os anos de 2026 estão vazios para o DIRETOR).
  - PROFESSOR (Fernanda Guerra) não tem a NILVA na lista de escolas (a API deixa consultar, mas a tela rejeita o escopo). Melhor turma: Escola teste da Feda (`ebac582b-e871-4214-a916-0b38f59360ca`), ano `1de13c22-759e-4d5a-9e8e-160f81c46ea4`, turma A `bc5cbf7f-6e14-4f32-ac32-39fe1a83437e` (ago a nov/2026): ADMIN vê 50 conteúdos / 8 disciplinas, PROFESSOR vê 15 / 4. Serve para testar recorte por professor.
- Nada foi criado em homolog.
- Armadilha: variáveis `QA_*` do shell não persistem entre chamadas de Bash; exporte no mesmo comando do `node`.
- Faltou no kit: helper para ligar o modo Análises e para ler o texto de PDF. O `lib.mjs` deste card (`qa-scripts/`) tem `irAnalises` com escopo por env.

## Rodada 3 (07/11/2026)
- O worktree do card fica em `~/workspace/repos/leme-app/.worktrees/<KEY>`, não em `.escritorio/worktrees`. Sem `qa.json` o kit cai no caminho errado e dá "Cannot find module @playwright/test"; gravar `qa.json` com o worktree certo.
- `qa-scripts/main.mjs DIRETOR|PROFESSOR` refaz os critérios 2 a 10 em ~3 min; para PROFESSOR exportar `QA_ESC`, `QA_ANO`, `QA_TURMA` da Escola teste da Feda (IDs acima), senão o botão fica desabilitado (turma do DIRETOR). `c1.mjs` faz o critério 1.
- Para comparar PDFs: `pdftoppm -r 80 -png` e juntar com PIL (`python3 -I`) funciona; a varredura de dia órfão sai de `pdftotext -layout` separando por `\f`.
- A turma da NILVA (2024) não tem `bnccs` estruturado (códigos só no texto); para ver as etiquetas BNCC use a Escola teste da Feda.
- Nada foi criado em homolog.

## LM-2806 (07/11/2026 12:07)

# Aprendizados QA LM-2806
- Escolas do ADMIN com 2024/2025/2026 (bom para testar ano do topo): ZEZE SALLES `3ff69be6-2c6b-486f-b418-a8d450c5bc5f`; anos 2025=`5f0ecf80-68d9-4355-ab13-7b0960f62d29`, 2026=`0722495c-3cfc-436a-93a4-7352e46fb60d`. `urlEscopo` funciona com ela.
- Escola Municipal Faino (2 anos) não aparece no combobox do ADMIN e a URL com `?school=` dela é descartada: não serve de massa.
- Modo análise da Frequência: `/dashboard/frequency?school=..&year=..&analytics=1`.
- PROFESSOR não acessa Turmas (redireciona para home); modal de faltas só com ADMIN/gestão.
- Seletores do modal: `getByRole("dialog")`; mês = `getByLabel("Mês",{exact:true})` (sem exact pega o radio "Por Mês"); ano = `getByLabel("Ano",{exact:true})`.
- Seletor de escola: clicar em "Selecione a escola", digitar no placeholder "Nome da escola".
- Kit: faltou helper de "abrir escola por nome" e de listar escolas com vários anos (usei v2/schools/<id>/school-years).

## LM-2858 (07/11/2026 13:17)

# Aprendizados QA (LM-2858)
- Anotações com tiptap = Conteúdos (`/dashboard/contents`, drawer "Novo conteúdo"). Marque "Ver todas as turmas", clique num card "Sem conteúdo cadastrado", editor `.ProseMirror`, título `input[name=title]` (`getByLabel("Título")` é ambíguo com o botão de formatação). Fechar o drawer: botão "Fechar".
- PDF: botão "Imprimir conteúdos" só existe no modo analytics (switch no cabeçalho da página de conteúdos); modal tem "Gerar PDF" e dispara download. `pdftotext` existe no servidor.
- Banco de questões (`/dashboard/mapa/questions`) é só ADMIN; professor é jogado para /dashboard/home. Botão "Nova questão".
- Turma da Tunada da Feda onde o professor atua: `d577aa27-3fc6-457e-80ce-63ebe88f5c60` (1º Ano A - Manhã); a turma AEE na URL é substituída para o professor.
- Token no `localStorage` chave `leme-token`; apagar e navegar leva a `/?redirect=`.
- `/qr-code` na primeira carga em dev pode levar mais de 4 s para redirecionar; espere 8 s.
- Digitação rápida logo após clique na toolbar perde caracteres; use `keyboard.type` com delay e Ctrl+B.
- `ERR_NETWORK_CHANGED` no console é ruído da rede do servidor.

## LM-2859 (07/11/2026 13:47)

nada novo (card só de CI; critérios por git grep, git diff e pnpm audit no worktree, sem preview).

## LM-2860 (07/11/2026 14:25)

# Aprendizados QA LM-2860
- Preview 5301 pode estar fora do ar ao começar (ECONNREFUSED): subi com `pnpm exec vite --host 127.0.0.1 --port 5301 --strictPort` no worktree (node 24 via fnm). Vale o manager conferir antes de chamar o QA.
- Contexto inseguro: headless em 127.0.0.1 é seguro. Simular com `context.addInitScript(() => Object.defineProperty(Crypto.prototype, "randomUUID", { value: undefined }))` (o kit poderia ter um `semRandomUUID(context)`).
- Trilhas: `/dashboard/mapa/learning-tracks?school=<id>`. "Nova trilha" abre drawer; ano é `<select>` nativo (`selectOption({label:"5º Ano"})`); "Continuar" leva ao passo 2 (etapas). Editar: clicar no nome, "Editar etapas"; trilha com cartões respondidos (ex. "Teste trilha refac", Escola teste da Feda) mostra aviso com botão "Editar mesmo assim".
- Arrastar avaliação: mouse.down/move em passos/up funciona (dnd); contador "1 AVALIAÇÕES" por etapa serve de asserção.
- Banco de questões: `/dashboard/mapa/questions`; "Nova questão" e, no card, clicar e "Editar". "Adicionar alternativa" sai de 4 para 5 e some (máximo 5). Contar `getByText("Comentário (uso interno)")` = número de alternativas.
- Capitão: `/dashboard/capitao-leme`, textarea "Pergunte ao Capitão…", input file para imagem; a resposta vem rápido.

## LM-2884 (10/11/2026 14:15)

# Aprendizados QA LM-2884

- `/foto` abre com PROFESSOR logado, sem escolher escola. Modo "live" quando existe `navigator.mediaDevices.getUserMedia`; em Chromium headless existe.
- Câmera: lançar o Chromium com `--use-fake-device-for-media-stream --use-fake-ui-for-media-stream` (vídeo verde, videoWidth 2480). `abrirNavegador` do kit não aceita args de launch: escrevi o login à mão (faltou `args` no kit). Depois do login, `addInitScript` vale para o próximo `goto`.
- Negar câmera: sobrescrever `getUserMedia` com uma flag `window.__deny` que lança `DOMException("", "NotAllowedError")`; virar para false e clicar "Tentar novamente" prova o critério 4 sem reload.
- QR no vídeo: `qrcode-generator` do node_modules do worktree gera a matriz em Node; no navegador, canvas 720x1024 + `captureStream(15)` no lugar do getUserMedia. Payload: `<origem minúscula>/F/E/<UUID sem hífen em maiúsculas>/<página>/<HASH>` (E = cartão-resposta, S = socio). Lido em poucos segundos e navega para `/foto/notas?...`.
- `salvarPrint` com fullPage em tela recém-carregada saiu em branco uma vez (desktop, spinner): use `{ paginaInteira: false }` e espere ~500 ms.
- Não foi criado dado em homolog.

## LM-2822 (10/11/2026 14:28)

# Aprendizados do QA (LM-2822)

- Grade horária: rota `/dashboard/timetable?school=&year=&class=`. Aulas são `.rbc-event` (texto "07:00 – 07:50 / Disciplina / Professor"). Drawer: título "Alterar aula" / "Nova aula"; campos `getByLabel("Professor(a)")` (select nativo), "Dia da semana" (select), "Início"/"Fim" (input time), "Turma" (desabilitado na visão por turma); Disciplina é Menu do Chakra (clicar no botão e `menuitem`).
- Visão por professor: botão "Por turma" -> menuitem "Por professor", depois "Selecione o Professor". Clicar em aula não abre nada nessa visão; só "Nova aula" abre o drawer, com professor travado.
- API: `v2/years/{ano}/classes` lista as turmas; `v2/classes/{id}/classrooms` lista aulas (`classrooms`); `POST v2/classrooms` cria aula (`classId, dayOfWeek, startedAt, endedAt, subjectId, teacherId`). Regras do servidor: 422 "Professor já possui aula nesse horário" e 422 de sobreposição na mesma turma.
- Tunada da Feda, ano `1210f4eb...`: turmas A de 1º/2º/3º ano (`d577aa27`, `142e514f`, `5c369e2e`), grade de 07:00 às 11:30 cheia, uma aula por professor por horário. Depois das 11:30 os professores ficam livres, bom para criar massa. Fernanda Guerra (`48f1107e`) tem Arte na turma `d577aa27` ter 11:30-12:00 (serve de conflito para o C6). Fábio Moreira (`db96d710`) está livre para virar "B".
- Rota de troca em lote (`PUT v2/classes/{id}/subjects/{id}/teacher`) existe em homolog.
- Toasts do Chakra aparecem duplicados no DOM; usar `new Set` ao ler `[role=status]`. Print logo após clicar no diálogo pega o fade-out.
- Console tem sempre um `ERR_CONNECTION_REFUSED` (ruído do preview).
- Massa criada: ver qa.md. A grade da turma `142e514f` foi alterada (Arte toda do Fábio Moreira, etc.).
- Faltou no kit: helper de toast e de abrir aula da grade (deixei em qa-scripts/lib.mjs).

## LM-2819 (10/11/2026 14:56)

# Aprendizados do QA (LM-2819, rodada 2)

- Dados criados em homolog (Tunada da Feda, turma AEE A `f0391ad6-...`): Helena Albuquerque `6cc5bc58-5991-49ba-b2c0-96b902652bf1` com 14 anotações "QA ..." (categorias 1, 2, 4, 5; de 15/07 a 05/11/2026; uma de 20/09 a 25/09 com data de término; duas em 30/10). Serve para qualquer teste de anotações/impressão. Marina Braga (turma AEE B) tem 3; os demais alunos das AEE têm 0.
- Alunos da turma: `GET v2/classes/<turma>/students`. Anotações: `GET v2/annotations/student/<id>?perPage=100` (devolve array direto). Categorias: `GET v2/annotations/categories` (7 incluindo "Atendimento AEE"). Não existe `v2/students` por escola.
- Criar anotação pela API: `POST /api/v2/annotations` com FormData (`categoryId`, `date` Y-m-d, `studentId`, `content`, `endDate` opcional), 200.
- Abrir a ficha: `/dashboard/students?school&year&class`, clicar no nome, `getByRole("tab",{name:/Anotações/})`. Menu: botão "Mais ações das anotações", item "Imprimir anotações"; esperar o `menuitem` (`waitFor`) antes de checar visibilidade. Modal: `getByRole("dialog",{name:/Imprimir anotações/})`; checkboxes precisam de `{force:true}`; DateInput: `getByPlaceholder("dd/mm/aaaa")` com `click`, `fill("")`, `pressSequentially("dd/mm/aaaa")`, `blur`.
- O modal fecha depois de gerar o PDF com sucesso: reabra para testar o cenário seguinte. Download: `page.waitForEvent("download")` junto do clique, `saveAs` em pasta própria (`downloads/`), `pdftotext -layout` e `pdftoppm` existem no servidor.
- Ruído de console em homolog: ERR_CONNECTION_REFUSED do GrowthBook `/sub/` e do crazyegg.
- Falta no kit: helper de download de PDF e de abrir a ficha do aluno.

## LM-2801 (10/11/2026 16:29)

# Aprendizados do QA (LM-2801)

- Análise de frequência: o interruptor de "modo análise" fica no cabeçalho (`header [role=switch], label:has(input[type=checkbox])`, primeiro). NÃO persiste entre `page.goto`: clicar depois de cada carga.
- Turma com faltas (só 2º Semestre, só Arte; 15 alunos): Escola teste da Feda `ebac582b-e871-4214-a916-0b38f59360ca`, ano `1de13c22-759e-4d5a-9e8e-160f81c46ea4`, "1º Ano A - Manhã" `bc5cbf7f-6e14-4f32-ac32-39fe1a83437e`. As turmas 2º Ano A (`34baec6b-...`) e 3º Ano B (`837485ed-...`) não têm faltas (servem para o estado sem faltas).
- Matérias do ADMIN nessa turma: Aprofundamento, Arte, Artesanato, Artes Marciais, Capoeira, Educação Física, Matemática, Multidisciplinar (só Arte tem faltas). O PROFESSOR vê só Arte e Multidisciplinar e não tem faltas em nenhuma: falta massa para "nas suas aulas de {matéria}".
- O PROFESSOR só tem turmas na Escola teste da Feda; ZEZE Salles, Melo Martins e Tunada da Feda vêm sem turma/ano habilitados para ele.
- Popover do Chakra: `[role=dialog]` com botão "Entendi"; gatilho `button` "Como calculamos?" logo depois do título (xpath following). Menus do Chakra deixam vários `[role=menu]` vazios no DOM; filtrar os com texto.
- Mapa V2: precisa escolher turma e período (menu mostra só "2º Semestre") para renderizar conteúdo.
- Kit: faltou um helper para ligar o modo análise e escolher turma/matéria. Scripts reaproveitáveis em `cards/LM-2801/qa-scripts/` (`lib.mjs`, `gestao.mjs`, `mat.mjs`, `resto.mjs`).

## Complemento (rodada 2)
- Professor de teste na turma 1º Ano A - Manhã (Escola teste da Feda, turma bc5cbf7f-6e14-4f32-ac32-39fe1a83437e) leciona Arte (classroom 5b77b626-6d77-47ad-b8e6-a7dcdecedaec, terças) e Multidisciplinar (2dde8b34-ddd0-4512-a68b-ce8bf1379b38, segundas). Ver as aulas do dia: GET v2/classes/<turma>/absences/<yyyy-mm-dd> (422 em dia sem aula dele).
- Lançar falta pela API: PATCH v2/classes/<turma>/absences/ com {date, studentId, classroomId, absent:true}, logado como PROFESSOR e só em dia com aula dele. Criada: Levi Ackerman Guerra Lomenha, 10/11/2026, Arte. Reversível com absent:false.
- Scripts reaproveitáveis em cards/LM-2801/qa-scripts: dia2.mjs (aulas do dia), falta.mjs, c5.mjs.

## LM-2885 (10/11/2026 18:10)

# Aprendizados QA LM-2885

- O preview 127.0.0.1:5301 pode estar fora do ar quando o QA começa. Subi `eval "$(fnm env)"; pnpm exec vite --host 127.0.0.1 --port 5301 --mode homolog` no worktree (nohup, log em /tmp) e funcionou. Não use `pkill -f "vite ..."` dentro da mesma chamada Bash: o padrão casa com o próprio shell e mata a chamada (exit 144).
- Rota da Base: `/dashboard/knowledge-base`. Com `urlEscopo` (Tunada da Feda + turma AEE A) o escopo já vem pela URL. O `goto` do Playwright com `urlEscopo` já devolve URL absoluta (não concatenar com BASE).
- As categorias da lista são recolhidas: para abrir um guia, digite o título em `getByPlaceholder("Procurar um assunto...")` e clique no texto exato. No mobile existem dois inputs com esse placeholder: use `.first()`.
- Cartão do tour: `section` com "Passo N de M". Botão: "Me mostre como fazer" (button ou link).
- Cadeado: `[aria-label="Sua rede não tem este módulo"]`. Só existe para módulo "gestao" (nenhum guia é "mapa"). Cenário sem gestão: `forcarFlags(page, {"restrict-to-map-only": true})` (12 cadeados em "frequência"). Sem AEE: `forcarFlags(page, {"is-aee-enabled": []})`.
- Não há seletor de perfil na Base: a visão muda com o papel logado (ADMIN vê mais itens que PROFESSOR/DIRETOR).
- Critério com cópia temporária do `knowledge-base.data.json`: o dev server recarrega ao salvar; use try/finally com cópia em /tmp para reverter. Id do artigo do Doc é derivado do título: para simular renome, troque `id` e `title`.
- `pnpm check:tutorials` regrava `tutorials.status.json`, mas sem diferença no git. `pnpm knip` imprime o banner da API várias vezes e sai 0.
- Ruído de console: ERR_CONNECTION_REFUSED de growthbook (SSE) e crazyegg.
- Faltou no kit: helper para abrir artigo da Base por título e para subir o preview quando cai.

## LM-2886 (11/11/2026 18:14)

# Aprendizados do QA do LM-2886

- **Flag nova sem GrowthBook:** `forcarFlags(page, { "is-mapa-analytics-gestao-enabled": [{id,name}] })` basta. Para o Mapa V2 de outra escola (ex.: Faino, que é V1 de verdade), force também `"is-mapa-v2-enabled": [...lerFlags()["is-mapa-v2-enabled"], escola]` e, para diretor, `IsMapaLemeEnabled`. Sem isso a Faino abre a tela V1 ("Visão de Analytics em construção").
- **Modo análise:** o único `input[type=checkbox]` do header; `checked` = modo normal. Clique com `{force:true}` quando estiver marcado.
- **Seleção de escola do admin:** ao abrir `/dashboard/mapa/pedagogical-map` aparece lista de botões com o nome da escola; clique nela.
- **Preview de papel:** botão `getByLabel("Ferramentas internas")` (ícone de chave no topo da sidebar), itens "Professor(a)", "Coordenador(a)", "Diretor(a)", "SME". Depois de um preview o menu não reabriu de forma confiável: escolha um papel por sessão.
- **Menus de filtro (BaseMenu do Chakra):** itens têm `role=menuitem`; Escape deixa o menu "aberto" sem estar visível, então clique fora (`mouse.click(1300,60)`) em vez de Escape.
- **Eventos do Amplitude:** em dev o app faz `console.group("📊 <evento>")` + `console.table(props)`. No Playwright o tipo é `startGroup` e o `table` tem o objeto em `args()[0].jsonValue()` (formato `{prop:{valor,origem}}`). Não há POST para amplitude.com no preview.
- **Dados:** Escola teste da Feda `ebac582b-e871-4214-a916-0b38f59360ca` tem 7 mapas, 55 provas e 14 turmas com resposta (endpoint `v2/analytics/learning-maps?schoolId=`); 16 provas com "Ainda não feito", 54,8% numa prova (laranja), 33% numa (vermelha). Nilva Cazeto (única escola do DIRETOR) = `e8893b5a-2222-4483-b6fd-6786a460ad05`, sem mapa (resposta real vazia). DIRETOR recebe 403 ao pedir escola alheia (ex.: Faino) direto na API.
- **Cenários sem dado real** (sem respostas, 403, 80% com 40/30/2/8, turma com 0 respostas): `page.route(/v2\/analytics\/learning-maps(\?|$)/)` com `route.fetch()` e corpo alterado; está em `qa-scripts/c12.mjs`.
- **Armadilha de ambiente:** um `python3` no meio do comando disparou a trava do hook e abortou o comando inteiro (o arquivo do heredoc anterior não foi criado). Não misturar python na mesma chamada.
- **Kit:** faltam helpers para ligar o modo análise, escolher escola pelo picker e capturar eventos do console; estão em `qa-scripts/lib.mjs` deste card.

## LM-2886 (11/11/2026 18:58)

# Aprendizados do QA do LM-2886

- **Flag nova sem GrowthBook:** `forcarFlags(page, { "is-mapa-analytics-gestao-enabled": [{id,name}] })` basta. Para o Mapa V2 de outra escola (ex.: Faino, que é V1 de verdade), force também `"is-mapa-v2-enabled": [...lerFlags()["is-mapa-v2-enabled"], escola]` e, para diretor, `IsMapaLemeEnabled`. Sem isso a Faino abre a tela V1 ("Visão de Analytics em construção").
- **Modo análise:** o único `input[type=checkbox]` do header; `checked` = modo normal. Clique com `{force:true}` quando estiver marcado.
- **Seleção de escola do admin:** ao abrir `/dashboard/mapa/pedagogical-map` aparece lista de botões com o nome da escola; clique nela.
- **Preview de papel:** botão `getByLabel("Ferramentas internas")` (ícone de chave no topo da sidebar), itens "Professor(a)", "Coordenador(a)", "Diretor(a)", "SME". Depois de um preview o menu não reabriu de forma confiável: escolha um papel por sessão.
- **Menus de filtro (BaseMenu do Chakra):** itens têm `role=menuitem`; Escape deixa o menu "aberto" sem estar visível, então clique fora (`mouse.click(1300,60)`) em vez de Escape.
- **Eventos do Amplitude:** em dev o app faz `console.group("📊 <evento>")` + `console.table(props)`. No Playwright o tipo é `startGroup` e o `table` tem o objeto em `args()[0].jsonValue()` (formato `{prop:{valor,origem}}`). Não há POST para amplitude.com no preview.
- **Dados:** Escola teste da Feda `ebac582b-e871-4214-a916-0b38f59360ca` tem 7 mapas, 55 provas e 14 turmas com resposta (endpoint `v2/analytics/learning-maps?schoolId=`); 16 provas com "Ainda não feito", 54,8% numa prova (laranja), 33% numa (vermelha). Nilva Cazeto (única escola do DIRETOR) = `e8893b5a-2222-4483-b6fd-6786a460ad05`, sem mapa (resposta real vazia). DIRETOR recebe 403 ao pedir escola alheia (ex.: Faino) direto na API.
- **Cenários sem dado real** (sem respostas, 403, 80% com 40/30/2/8, turma com 0 respostas): `page.route(/v2\/analytics\/learning-maps(\?|$)/)` com `route.fetch()` e corpo alterado; está em `qa-scripts/c12.mjs`.
- **Armadilha de ambiente:** um `python3` no meio do comando disparou a trava do hook e abortou o comando inteiro (o arquivo do heredoc anterior não foi criado). Não misturar python na mesma chamada.
- **Kit:** faltam helpers para ligar o modo análise, escolher escola pelo picker e capturar eventos do console; estão em `qa-scripts/lib.mjs` deste card.

## Rodada 2 (devolução da Feda)
- **Preview pode estar morto no início da rodada** (nada em 5301, `ERR_CONNECTION_REFUSED`). `esteira-preview start <KEY>` sobe de novo na mesma porta em ~15 s.
- **Escolher turma sem header:** com flag `[]` (ou professor), `abrirMapa` + clicar na escola pelo picker mostra `main button` com as turmas; o primeiro botão é a turma. Admin na Feda: 16 turmas; professor: 3 (1º Ano A, 2º Ano A, 3º Ano B manhã). Turma "1º Ano A - Manhã" da Feda = `bc5cbf7f-6e14-4f32-ac32-39fe1a83437e`.
- **Referência de card da plataforma:** Conteúdos com turma escolhida e modo normal (`checked`); cards têm raio 12px, borda 1px rgb(226,232,240), sombra `rgba(15,23,42,.08) 0 2px 8px`, padding 20px. Chegar lá pelo picker do Mapa e pelo link "Conteúdos" (ir por URL perde a escola).
- **Regiões roláveis:** `page.getByRole("region", {name: "Turmas da escola"})`, `.focus()` e ArrowDown rolam (scrollTop 0 para 120). Ler `document.activeElement.scrollTop` logo depois do Tab não funcionou; usar o locator. A partir de "Todos os mapas" são 1 Tab até a lista de Progresso e 2 até a de Turmas.
- **Reuso:** `qa-scripts/r2-*.mjs` são cópias dos scripts da rodada 1 com prefixo r2- nos prints (sed no `salvarPrint`). Evitar `require` em .mjs (quebrou o log final do `filtros`).
- **Kit:** ainda falta helper para "escolher escola pelo picker" e capturar eventos do console (`qa-scripts/lib.mjs`).

## LM-2898 (11/11/2026 19:52)

# Aprendizados do QA (LM-2898)

- A flag `is-mapa-analytics-gestao-enabled` não existe no GrowthBook de homolog (`lerFlags()` devolve undefined). Use `forcarFlags(page, {"is-mapa-analytics-gestao-enabled":[{id:"ebac582b-e871-4214-a916-0b38f59360ca",name:"Escola teste da Feda"}]})` e abra `/dashboard/mapa/pedagogical-map?school=<id>`. O ano entra sozinho.
- Modo análise: o switch no cabeçalho (`[role=switch],input[type=checkbox]`, `click({force:true})`). O toggle Turmas/Alunos é `getByText("Alunos",{exact:true}).last()`. Filtros são `Menu` do Chakra: `getByRole("button",{name:"Todos os anos"})` e depois `getByRole("menuitem")`.
- Escola teste da Feda: 91 alunos em 16 turmas ("Aluno Cenário XX nn" e alunos com nome real na turma 1º Ano A). Elizabeth (`86032357-1e20-4c89-a541-cd13fbffea7e`, 1º Ano A) tem prova com `present:false` ("Faltou") e `present:null` ("Cartão não lido"): serve para o drawer. Nenhum aluno tem answers=0; use `page.route` e `route.fetch()` para alterar a resposta.
- Mock de 403/404 precisa levar `statusCode` no corpo (`{statusCode:403,message}`): o interceptor do axios rejeita com o corpo, e sem isso a tela mostra a mensagem genérica. O core real devolve assim.
- Eventos do Amplitude: o preview não tem chave, nada sai pela rede. O log fica no console (`startGroup` "📊 Nome" + `console.table`); leia com `m.args()[0].jsonValue()`.
- Professor (Fernanda) na Escola teste da Feda, 1º Ano A: só tem dado com a trilha "Trilha Teste da Feda - V2" (a trilha padrão vem vazia). Troque pelo menu do filtro de mapa.
- Alunos reentrando na aba refaz `learning-maps/students` (staleTime 0); isso não é o endpoint de visão geral.
- Kit: faltou helper para o modo análise e para ler eventos de analytics do console.

## LM-2896 (11/11/2026 20:38)

# Aprendizados do QA (LM-2896)

- A flag `is-mapa-analytics-gestao-enabled` não existe no CDN de homolog (lerFlags devolve undefined). Use `forcarFlags(page, {"is-mapa-analytics-gestao-enabled": [{id,name}]})` com a Escola teste da Feda (`ebac582b-...`). O hook é `useMapaAnalyticsGestaoSchools`.
- Modo análise: clicar em `[data-tour="modo-analise"]` (click force). Para PROFESSOR, a URL ganha `analytics=1`; escolher a turma pelo botão do seletor na tela (ex.: "3º Ano B - Manhã").
- Visão da gestão (ADMIN) em `/dashboard/mapa/pedagogical-map?school=<id>`: linhas de prova e de turma são `main button`; drawer é `getByRole("dialog")`; o botão X é o primeiro `button` do dialog.
- Dados da Escola teste da Feda (via API `v2/analytics/learning-maps?schoolId=`): turmas 1º A `bc5cbf7f-6e14-4f32-ac32-39fe1a83437e` (tem 3 provas sem resposta e questões "sem presença": bom para "Sem resultados ainda"), 3º B `837485ed-d030-4731-8213-7bb87a36d596` (3 provas, todas com resposta). Prova parcial: "Leitura e Escrita · Nível Basilar · 1º Ano" (54%; turma A com 14 pendentes, turma C com 1 ausente). Nenhuma turma sem aluno ativo existe: para esse caso, `page.route` em `**/learning-maps/attendance*` zerando `students`.
- 403/404 também por `page.route` (nenhum usuário ADMIN/DIRETOR de teste cai em turma de outra escola). Esses erros geram AxiosError no console: é esperado.
- Faino (`41a3e682-...`) é Mapa V1: não tem a tela de habilidade/questão do professor V2. Para regressão do professor V2 usar a Escola teste da Feda.
- Seletores com `getByRole("button").filter({hasText})` dão strict mode violation no drawer da turma (barras e questões repetem o nome da prova): filtrar também por "Escola" para a barra.
- "Faltou" aparece em caixa alta por CSS; `innerText` devolve maiúsculo, regex precisa de `i`.
- Perdi tempo com o modo análise e com seletores; o kit poderia ter `ligarModoAnalise(page)`.

## LM-2901 (11/11/2026 20:51)

# Aprendizados do QA (LM-2901)

- Rota da Base de Conhecimento: `/dashboard/knowledge-base` (não `/base-de-conhecimento`, que dá "Não encontramos...").
- `pnpm test scripts --run` falha (opção desconhecida); usar `CI=1 pnpm test scripts`.
- Guia de tour: link "Como criar uma turma" (artigo `como-criar-turmas`, categoria "Turmas, horários e calendário"), botão "Me mostre como fazer" leva a /dashboard/classes. Funciona com ADMIN sem escola selecionada.
- Mobile (390): abrir a lista com `getByLabel("Mostrar a lista")`, expandir a categoria com `getByRole("button", { name: "Turmas, horários e calendário" })` e clicar no guia.
- Editar o JSON no teste: `knowledge-base.data.json` é `{title, categories:[{articles:[...]}]}`; o Vite recarrega sozinho. Reescrever com JSON.stringify gera diff enorme de formatação; restaurar com `git checkout` do arquivo e de `src/pages/knowledge-base/tutorials.status.json` (o check:tutorials reescreve).
- `check:tutorials` sai 1 com Doc de 5 passos e com negrito inexistente; a mensagem fica antes da lista "Telas do menu sem tutorial", então não use `tail` curto.
- Console tem sempre `ERR_CONNECTION_REFUSED` (recurso externo) na Base; ruído.
- Faltou: um jeito de selecionar escola pelo kit para testar cadeado de módulo e AEE na Base; e uma instância de main para baseline.

## LM-2904 (11/11/2026 22:05)

nada novo

## LM-2897 (11/11/2026 22:32)

# Aprendizados QA LM-2897
- A flag `is-mapa-analytics-gestao-enabled` NÃO existe no GrowthBook de homolog (lerFlags não a traz). Cenário se monta com forcarFlags(page, {"is-mapa-analytics-gestao-enabled":[S],"is-mapa-v2-enabled":[S],IsMapaLemeEnabled:[S]}) com S={id:"ebac582b-e871-4214-a916-0b38f59360ca",name:"Escola teste da Feda"}, logado como ADMIN. Depois ir a `/dashboard/mapa/pedagogical-map?school=<id>`.
- Modo análise: clicar no switch do header (`header [role=switch]` com force:true).
- Escola teste da Feda tem 72 células no heatmap (`button:has-text('questõ')`); a 12ª (EF01MA19, 58%, 3 questões) tem 4 turmas e 3 questões numa prova (bom para CA 2/3/4). A 1ª (5G1.7, 0%) tem 1 turma. Filtro Ano é menu (`menuitem` "1º Ano" = classLevelIds=8).
- Professor (Fernanda Guerra) na Feda: 1º Ano A não tem resultado; "3º Ano B - Manhã" tem (célula 2LE1.2, questão com classId).
- 404 do drawer: mockar com page.route e corpo {"statusCode":404,...}; sem `statusCode` no corpo cai na mensagem genérica (o interceptor rejeita com o corpo).
- `ERR_CONNECTION_REFUSED` no console aparece sempre, em qualquer tela (ruído do ambiente).
- Kit: faltaria um helper para ligar o modo análise e forçar flags de escola.

## LM-2903 (12/11/2026 11:07)

# Aprendizados QA LM-2903
- Base de Conhecimento: `/dashboard/knowledge-base`. Balão do tour: `[aria-label="Passo a passo na tela"]` (botões Próximo/Voltar/Sair/Concluir, texto "Passo N de M"). Botão "Me mostre como fazer" abre o tour e navega para a rota do guia.
- PROFESSOR recebe "Esta função não é para o seu tipo de acesso" nos guias de coordenação; use ADMIN para o tour.
- Celular (390): categorias vêm recolhidas; clicar o botão `/^Alunos\s*\d+$/` expande. O título da categoria é CSS uppercase (getByText exato em caixa alta falha).
- Passar escola pela URL (`?school=`) basta para o tour; Tunada da Feda (AEE) mostra guias de AEE, ZEZE SALLES não.
- ADMIN vê 9 guias em Alunos, PROFESSOR 7.
- Cadeado: ícone `svg.lucide-lock`; não achei escola de teste sem gestão para exercitar.
- Para comparar com main falta uma segunda instância do preview.

## LM-2890 (12/11/2026 16:18)

# Aprendizados QA LM-2890

- Admin em `/dashboard/mapa/exams` (sem escola selecionada) já lista avaliações V2; não precisa de escopo na URL.
- `GET v2/exams?per_page=100&page=1` via `api()` devolve `knowledgeGroups`. Casos prontos: "acacad" (só Linguagens, id 6075cd8e-a845-4030-8093-60a99451bd88), "Alvo 1 - Teste da Feda" (Linguagens, Matemática), "Teste 2" (Pendente, sem área, id 67e398d8-4572-48ef-b886-25171a691e78).
- Busca: placeholder "Buscar por título da avaliação...". Colunas fixas Ações/Nome: comparar `getBoundingClientRect().left` do `th` e do `td` depois de rolar o contêiner com scrollLeft.
- Kit: `abrirNavegador({largura:390,altura:844})` serve direto para o celular.

## LM-2834 (12/11/2026 16:24)

# Aprendizados QA LM-2834
- Rotas do leme-core são `v2/...`: `GET v2/classes/{id}/students` lista alunos com `attributes`; `classes/{id}` sem v2 dá 404. Tela de alunos: `/dashboard/students?school=&year=&class=`, botão "Novo aluno", clicar no nome abre o drawer; aba "Pessoal" > "Editar dados pessoais"; salvar é "Salvar" (criar) / "Salvar alterações".
- Selects do form de aluno são `select[name=hasX]` nativos; use `selectOption({label})`. Valor null aparece como "Selecione" (igual aos 8 antigos).
- Criar aluno exige CPF válido, nome, nascimento, Número na chamada (selectOption index 1), Início da matrícula (dd/mm/aaaa); sexo e raça via getByLabel. Turma vem do escopo da URL.
- Editar só o Complemento de aluno sem endereço dá 422 ("cidade obrigatória"): preencher o endereço inteiro (CEP, Rua, N°, Bairro, Cidade, UF).
- Massa: aluno "QA LM2834 Teste 84765" (turma AEE A, Tunada da Feda) com booleanos variados; João Nogueira (`a1fb960e-d966-4d8e-bf14-af47677a001c`) é aluno com todos os atributos null.
- Faltou no kit: helper de CPF válido e de captura de POST/PATCH.

## LM-2891 (12/11/2026 19:56)

# Aprendizados do QA (LM-2891)

- O preview `:5301` pode estar fora do ar com o card em `etapa: erro`. Dá para subir `pnpm exec vite --host 127.0.0.1 --port 5391 --strictPort` no worktree (tem `.env` e `node_modules`) e apontar o `qa.json` para ele. Não use `pkill -f` com o texto do próprio comando: mata o shell da chamada (exit 144); guarde o PID.
- Diagramador: `/dashboard/mapa/exams/:id/diagramador`. A capa é `.exam-cover`; a linha da área é `.exam-cover__subject` (some quando em branco). As questões resolvem uma a uma (`GET v2/question-bank-items/:id`): espere `!innerText.includes("indisponível")` e mais ~2,5 s, senão a capa sai incompleta. Remover questão: `aria-label="Remover questão"`. Adicionar: botão "Adicionar" > gaveta (checkbox na linha) > "Aplicar à avaliação". Editar na tela não grava até clicar Salvar. A aba da capa é "Capa" (role tab).
- Criar avaliação por API (ADMIN): `POST v2/exams` com `{name, description, classLevelId: 12, stage: 4}` (12 = 5º Ano; stage: 1 Diagnóstica, 2 Basilar, 3 Intermediária, 4 Alvo); depois `POST v2/exams/:id/layout` com `header`/`page` copiados de um `GET .../layout` existente (ex.: `f5a8cbdf-49e2-48d9-af75-359b3325ffdc`) e `questions[{questionBankItemId, questionBankItemVersion:1, position, columnSpan:1, pageBreakBefore:false, hideSupportText:false, imageScalePercent:100, imageAlign:"center"}]`. Ambos dão 201. Não testei DELETE.
- Banco de questões (homolog, 12/11/2026): só Arte (1 questão, área Linguagens), Língua Portuguesa (Linguagens) e Matemática (Matemática); nenhuma disciplina sem área. IDs: LP 5º Ano `65413c87-9f32-473d-81b8-217949fb2b10`, `665b19fd-d766-4600-9d28-3650601073bf`; Mat 5º Ano `3f8b2431-3312-4cb1-b023-f58a51b097fe`, `9959b2b6-c3de-4f07-95a8-677e02300998`; Arte `c81c86fb-9ede-479f-8e82-64990046690e`. `v2/subjects` lista Artesanato (id 26), mas sem questão no banco.
- Simular dado que não existe: `context.route(/\/api\/v2\/(question-bank-items|exams)/, ...)` com `route.fetch()` e `route.fulfill({ response, json })` reescrevendo `subject.knowledgeGroup = null`. Funciona e não grava nada.
- `/dashboard/mapa/exams/:id/imprimir` exige `learningMapId` + turma com alunos + emissão de cartões (trava a avaliação); sem isso a capa nunca tem questões. Teste de impressão precisa de mapa V2 com cartões já emitidos, ou de OK do Glauco para emitir em escola de teste.
- Massa criada: avaliações "QA LM-2891 lp / lpmatarte / arte / mat" (5º Ano, Alvo); IDs em `cards/LM-2891/qa-scripts/exames.json`.
- Kit: faltou helper para esperar o diagramador pronto e para interceptar/reescrever respostas da API.

## LM-2927 (12/11/2026 20:07)

# Aprendizados QA LM-2927
- Link de suporte: `window.open` / `<a target=_blank>` para `api.whatsapp.com/send?phone=55011955031171&text=...`. Para ler: `context.route(/wa\.me|whatsapp\.com/, fulfill)` + `context.waitForEvent("page")`, depois `new URL(pop.url()).searchParams.get("text")`.
- Na sidebar o item MenuLabels.Duvidas aparece como "Ajuda" (rodapé, abaixo de "Base de Conhecimento"). No desktop o menu do avatar só tem Perfil/Tema/Sair; "Ajuda" do avatar só existe no mobile (390): abrir com `.avatar-menu`.
- `selectedSchool` só existe com `?school=` na URL ou após escolher no seletor do topo (ex.: `/dashboard/timetable`; a home não tem seletor). Seletor: botão "Selecione a escola" + campo `getByPlaceholder("Nome da escola")` (busca por "ã" funciona; "ç" e "&" não acham escola no admin).
- Escolas: Escola teste da Feda `ebac582b-e871-4214-a916-0b38f59360ca`; EMEF Melo Martins `7447820d-02d3-4d6a-a2a3-d60453e71b0d` (professor); EMEI JOÃO SERRA HORAMOS FILHO `4a6b80ee-0487-4fc1-ae60-af38e205b437` (admin, tem acento).
- Aviso "Esta função ainda não está liberada" da Base de Conhecimento: não consegui provocar com ADMIN + forcarFlags (`restrict-to-map-only`, `IsMapaLemeEnabled: []`). Falta uma conta secretario ou escola sem Mapa de teste; o kit também não tem papel SECRETARIO.
- Perdi chamadas descobrindo seletores; um helper `capturarWhatsapp(context, acao)` no kit ajudaria.

## LM-2888 (12/11/2026 20:14)

# Aprendizados QA LM-2888

- O preview indicado (5302) estava fora do ar. Alternativa: `cd <worktree> && ./node_modules/.bin/vite --host 127.0.0.1 --port 5392 --strictPort` (o `.env` do worktree já tem o proxy /api). Derrubar pelo PID (`ss -ltnp`); `pkill -f` com o texto do comando mata o próprio shell.
- Banco de itens: rota `/dashboard/mapa/questions` (não `/questoes`). ADMIN acessa.
- Selects da barra: `getByLabel("Filtrar por <matriz|disciplina|ano/série|dificuldade|status|autor|imagem>")`; `selectOption` funciona. Dificuldade: Fácil=1, Intermediária=2, Difícil=3.
- API `GET /api/v2/question-bank-items?page=&perPage=12` devolve array puro (sem total): paginar até página curta. Homolog em 12/11/2026: 551 itens, 378 com imagem, 173 sem; Fácil: 103 (88 com imagem).
- Contador "X de Y questões" = itens carregados (carrega 3 páginas sozinho), não o total do servidor.
- Dois selectOption seguidos sem pausa perdem o primeiro filtro na URL; esperar ~3 s.
- Faltou no kit: helper para subir/derrubar preview quando a porta não responde.

## LM-2889 (13/11/2026 14:17)

# Aprendizados QA LM-2889

- Rota do Banco de questões: `/dashboard/mapa/questions` (não `/dashboard/questions`, que dá 404). ADMIN vê direto, sem escopo de escola.
- Dados criados em homolog (ADMIN): questões "QA LM-2889 com ERER" (hoje sem tag) e "QA LM-2889 sem tag" (hoje com ERER), Rascunho v1, Maternal 2 / Educação Física / SAEB BNCC 5ED1.2. Buscar por "QA LM-2889" para achar. Tag ERER tem id 1 (`?tagId=1`).
- Criar questão pela tela: Matriz, Disciplina e Descritor são react-select (ids `#matriz-select`, `#disciplina-select`, `#learning-target-select`): clicar no input e `ArrowDown` + `Enter` (`getByRole("option")` pega o `<option>` oculto do select nativo). Ano e Dificuldade são `<select>` nativos (`#ano-serie-select`, `#dificuldade-select`, `selectOption({index})`). Título via placeholder "A pintura"; enunciado e alternativas são 10 `[contenteditable]` (índice 0 texto base, 1 enunciado, depois alternativa/comentário alternados); marcar correta: `getByLabel("Marcar Alternativa A como correta").check({force:true})`.
- Editar: card > drawer > "Editar" > "Salvar alterações" > diálogo "Deseja continuar?" (role `dialog`, não `alertdialog`) > "Confirmar".
- Filtros: `getByLabel("Filtrar por tag")`, `getByLabel(/Filtrar por dificuldade/i)` (selects nativos); contador `getByText(/de \d+ questões/)`. Visão lista: botão com tooltip "Visualizar em lista".
- O kit poderia ter um helper `criarQuestao`; o lib.mjs deste card (`qa-scripts/lib.mjs`) serve de base.

## LM-2928 (13/11/2026 14:34)

# Aprendizados QA (LM-2928)

- Turma de teste: Escola teste da Feda `ebac582b-e871-4214-a916-0b38f59360ca`, ano `1de13c22-759e-4d5a-9e8e-160f81c46ea4`, 1º Ano A `bc5cbf7f-6e14-4f32-ac32-39fe1a83437e` (PROFESSOR). Mapa "Trilha Teste da Feda - V2" (`17a81553...`): Linguagens 14 alunos (5/5/4 por faixa), Matemática 7 abaixo de 50%. Nenhum aluno sem nota, nenhuma habilidade com mais de 2 questões abaixo de 50% ou acima de 70% (varredura da API em qa-scripts/d8.mjs). Faltam dados para "retomar", "domina" e "quem não fez".
- Analytics da turma: URL com school/year/class, depois clicar `[data-tour=modo-analise]`. A trilha padrão ("Trilha de Alfabetização") é vazia; trocar para "Trilha Teste da Feda - V2" no segundo seletor.
- Player de vídeo: marcadores das cenas são botões pelo nome (Turma, Como foi, ...). Pausar e saltar deixa animações paradas (mostra "0%" ou cena vazia); espere tocando uns 4 s antes de ler/printar.
- Visão da escola (gestão) não abre para ADMIN sem a flag: `forcarFlags(page, {"is-mapa-analytics-gestao-enabled":[{id:ESC,name:"..."}]})` (a flag não aparece em lerFlags). Abas "Turmas/Alunos/Correção/Vídeo" são texto, não role=tab.
- Tema escuro: `context.addInitScript` com localStorage `chakra-ui-color-mode=dark` antes da navegação (recarregar depois quebra o estado do seletor).
- Amplitude não aparece como POST na rede do navegador; critério de evento fica por teste/código.
- Faltou no kit: helper de "entrar no analytics da turma" e de tocar/pausar o player.
