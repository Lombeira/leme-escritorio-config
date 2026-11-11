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
