---
name: main-e-homolog
description: "Na Leme, main é homolog: merge na main já vai para homologação, e produção só sai depois de validar lá; não propor feature flag só para isso"
metadata:
  type: project
---

Na Leme, a `main` é o ambiente de **homologação**. Produção é um release separado, que
só sai depois de a mudança ser validada em homolog. Por isso o Glauco às vezes tira
feature flag de propósito: as partes de uma feature sobem juntas para a main e são
testadas em homolog antes do release.

**Why:** em 27/10/2026 ele removeu a flag de uma feature de impressão e leitura de
propósito. Propor flag de novo seria retrabalho e ignora como o deploy funciona.

**How to apply:** não sugerir feature flag apenas para "proteger a main"; perguntar
antes. Lembrar que mergear na main tem efeito em homolog. Ver
[[qr-link-precisa-esquema-minusculo]] (homolog também tem host diferente).
