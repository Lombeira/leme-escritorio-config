---
name: s3-no-scan-e-so-auditoria
description: "No leme-core, o upload para o S3 antes do Textract no scan de cartão-resposta é imposição do fornecedor; a ordem é load-bearing e não pode ser invertida no scan() atual"
metadata:
  type: project
---

No `EvaluationSheetUseCase::scan()` do leme-core, `saveImage()` roda **antes** de
`scanAnswers()`, e não por escolha de arquitetura: o `TextractEvaluationSheetScanRepository`
chama o Textract com `'S3Object' => ['Bucket' => ..., 'Name' => $s3Path]`, ou seja, o
arquivo **precisa** estar no bucket antes da chamada.

**Why:** o instinto é tratar o S3 como requisito do fluxo e reaproveitar o `scan()` para
qualquer leitor novo. Mas para um leitor que lê a imagem em processo, o S3 é só
auditoria (pai contesta nota, leitor erra em campo e se reproduz com a foto), não
pré-requisito. Hoje, se o S3 tossir, o scan falha e o professor não recebe nada, mesmo
com a foto legível.

**How to apply:** nunca inverter a ordem dentro do `scan()` atual: o Textract
receberia um caminho de S3 que ainda não existe e o fluxo quebra inteiro. Leitor que
não depende do Textract ganha **use case próprio**, não flag dentro do atual, e grava
no S3 depois de ler, de preferência fora do caminho crítico via `dispatch` (a fila SQS
e o target `worker` do Dockerfile já existem).
