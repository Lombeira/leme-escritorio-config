---
status: fechado
fechado_em: 2026-11-14 16:58 (aprovado)
pr: https://github.com/leme-tech/leme-app/pull/897
card: LM-2928
---
# LM-2928: professor ganha o botão "Resumo em vídeo" na visão da turma do Analytics do Mapa

**PR:** https://github.com/leme-tech/leme-app/pull/897

**Abrir:** http://192.168.1.173:5301/ → Mapa Pedagógico → ligar o modo Analytics → escolher uma turma e a trilha com resultados
**Entrar com:** a conta de teste de PROFESSOR do qa.env (Escola teste da Feda, 1º Ano A - Manhã, trilha "Trilha Teste da Feda - V2"). Para ver todas as cenas, use uma conta ADMIN na mesma escola: 4º Ano A - Manhã (retomar, domina) e 2º Ano B - Tarde (quem não fez)
**Celular:** F12 → ícone de celular → largura 390

## Decida antes de aprovar
- Textos das cenas: o card só deu exemplos, então os títulos e frases seguem o tom do vídeo da gestão. Trocar é só mexer no texto.
- Botão na barra de filtros, no padrão do "Diagnóstico da turma" da Frequência.
- Corte de 70% sem arredondar: aluno com 69,8% aparece como "70%" na lista da tela, mas fica fora de "70% ou mais" e de Destaques (o mesmo vale para habilidade com 69,6%). Arredondar mudaria a regra do card; deixei como está.
- Card empilhado sobre o LM-2886 (#890): o PR só vai para a main depois que ele entrar, ou sai com base na branch dele.
- Vira card depois: nada previsto. Os 8 nits do review (pequenas repetições de código) ficaram de fora.

## Como validar (uns 8 minutos)
1. Entre como professor, abra Analytics na turma 1º Ano A - Manhã, Linguagens → **deve aparecer:** o botão "Resumo em vídeo" (ícone de play) na barra de filtros. O vídeo não abre sozinho (print: `evidencias/1a-botao-barra-filtros.png`)
2. Clique no botão → **deve aparecer:** o player no lugar dos cards, com as cenas da turma. "Voltar ao painel" traz os cards de volta como estavam (print: `evidencias/cena-claro-1440-1.png`)
3. Toque o vídeo e compare "Como a turma foi" com a tela → **deve aparecer:** média 56% e 5 / 5 / 4 alunos (abaixo de 50%, 50 a 69%, 70% ou mais), igual à tela (print: `evidencias/5-como-foi-media.png`)
4. Na cena "Quem precisa de atenção", em Matemática → **deve aparecer:** 6 nomes do menor para o maior acerto e "e mais 1 aluno" (print: `evidencias/8-atencao-e-mais-1-aluno.png`)
5. Como ADMIN, 4º Ano A - Manhã, abra o vídeo → **deve aparecer:** cena "O que retomar" com 4 habilidades (código, descrição, etapa), em Matemática "Destaques" com 3 alunos e "O que a turma já domina" com 4 habilidades (print: `evidencias/q4m-cena-4-Retomar.png`)
6. Como ADMIN, 2º Ano B - Tarde → **deve aparecer:** "3 alunos não fizeram as provas" com os 3 nomes (print: `evidencias/q2b-cena-11-Nofizeram.png`)
7. Com o vídeo aberto, troque a área, as provas ou a trilha → **deve aparecer:** o vídeo fecha e o botão volta (print: `evidencias/11-provas-fechou.png`)
8. Na trilha "Trilha de Alfabetização" (sem resultado), mesma turma → **deve aparecer:** nenhum botão, sem erro (print: `evidencias/2-vazio-sem-botao.png`). Repita no celular e no tema escuro (prints: `evidencias/cena-claro-390-*.png`, `evidencias/13-escuro-*`)

## Não precisa conferir
- Textos sem "score", "percentil" ou "descritor", porcentagem inteira, plural certo (conferido por busca no texto das cenas).
- Evento `play_video` com `pedagogical_map_analytics` (conferido no código e no teste).
- Vídeo da gestão continua tocando igual (testes de regressão e uma passada na escola de teste).
- Com o player pausado, "Como foi" mostra "0%" e algumas cenas saem vazias: é só a animação parada, tocando aparece certo.

## Detalhes técnicos
- Commits do card: 07667eec (extrai peças comuns do vídeo), 2245aefa (vídeo da turma), 84d82ee3 (testes de retomar, domina e quem não fez); base: 004bf2ce e bde966b4 do LM-2886.
- Review: READY, 0 blockers, 0 should-fix, 8 nits (review.md).
- QA rodada 2: APROVADO nos 14 critérios (qa.md). Não visto: "e mais N" em "Quem não fez" (nenhuma turma tem mais de 6 sem nota; regra igual à da cena Atenção, que passou).
- Branch sem commits `[kb]`.
