---
status: fechado
fechado_em: 2026-11-12 17:22 (aprovado)
card: LM-2834
---
# LM-2834: validar campo "Deficiência intelectual?"

**Preview:** http://192.168.1.173:5302/ (rede de casa, cai ao sair da validação ou após 24 h)

## O que mudou
- Select novo "Deficiência intelectual?" (Sim / Não / Não informado) na seção "Diversidade cognitiva e funcional" do aluno, depois de "Possui deficiência?". Valor null nunca vira false.
- Aba de dados pessoais mostra o campo; payload do POST e PATCH leva `attributes.hasIntellectualDisability`.
- O select de alergia ficou em meia linha, para os seis selects fecharem em três pares.
- Refactor do review: helper `nullableBooleanSelect()` no schema, aplicado também aos 8 booleanos antigos (comportamento idêntico, QA conferiu).
- Backend já pronto (LM-2693).

## Quadro do QA (APROVADO, 7/7 + extra)
| # | Critério | Resultado |
|---|---|---|
| 1 | Select na seção, padrão dos vizinhos | APROVADO |
| 2 | Criar com Sim, POST true, reabrir | APROVADO |
| 3 | Editar para Não, PATCH false | APROVADO |
| 4 | Aluno com true abre em Sim | APROVADO |
| 5 | Aluno null mantém null | APROVADO |
| 6 | Aba Pessoal sem quebrar a grade | APROVADO |
| 7 | git grep do campo | APROVADO |
| extra | 8 booleanos antigos seguem salvando | APROVADO |

Observação: o select novo abre mostrando "Selecione" (valor vazio, enviado como null), igual aos vizinhos.

## Atenção
- O commit `[kb]` que o hook tinha posto na branch foi tirado em 12/11 (o Doc reorganizado entra com o LM-2903). Commits do card: `7dc96fe4` e `b42962eb` (o mesmo `ace62b29` de antes, reaplicado sem o `[kb]`; código idêntico).
- QA criou dados em homolog (escola Tunada da Feda, turma AEE A): aluno "QA LM2834 Teste 84765" e endereço de João Nogueira preenchido.

Review: 2 rodadas, READY. Nada para virar card depois.
