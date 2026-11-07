---
name: qr-link-precisa-esquema-minusculo
description: "QR só vira link na câmera do celular com esquema em minúscula; caixa alta é lida como texto. Segmentar byte+alfanumérico evita subir a versão do código"
metadata:
  type: project
---

**Testado em Android, 03/09/2026.** Um QR com `HTTPS://APP.LEME.TEC.BR/...` em caixa
alta é lido pela câmera nativa mas entregue como **texto**, não vira link. O padrão
diz que o esquema é insensível a caixa; a câmera não liga para o padrão. Precisa ser
`https://` minúsculo.

**O conflito:** minúscula não existe no modo alfanumérico do QR (`0-9 A-Z $%*+-./: `),
então cai no modo byte, 8 bits por caractere contra 5,5. Isso sobe a versão do código
e encolhe o módulo impresso (em 26mm de papel, v4 dá 0,788mm e v5 dá 0,703mm).

**A saída:** um QR aceita segmentos com modos diferentes. `https://host/` em byte, o
resto do caminho em MAIÚSCULA no alfanumérico. Fica na mesma versão que o payload todo
em caixa alta, e o link sai de graça. No leme-app isso está em `sheetQrSegments()`.

**Query string é a armadilha óbvia e cara:** `?`, `&` e `=` também caem no modo byte.
Dados vão em segmento de caminho, nunca em query.

**Host muda a densidade:** `app.leme.tec.br` dá v4 e `app.homolog-leme.tec.br` dá v5
com o mesmo payload. Homolog é o teste mais duro: se ler lá, lê em produção.

**Why:** atribuí uma falha de leitura à caixa alta antes de medir, e a causa real era
outra: o payload era montado com `window.location.origin`, que não existe em render de
servidor, e o QR saía sem host.

**How to apply:** ao gerar QR com link, esquema e host em minúscula num segmento byte,
resto em maiúscula alfanumérica, sem query string. Nunca montar URL de QR com
`window.location.origin`. Ver [[validate-fixes-empirically]].
