#!/usr/bin/env bash
# Roda todos os test_*.py desta pasta (cada um isolado numa pasta temporária) e mostra o resumo por arquivo.
# Uso: ./rodar.sh [-v]   (-v mostra a saída inteira de cada arquivo; sem -v, só as falhas)
set -u
DIR=$(cd "$(dirname "$0")" && pwd)
VERBOSO=0; [ "${1:-}" = "-v" ] && VERBOSO=1
falhou=0; resumo=()
cd "${TMPDIR:-/tmp}" || exit 2   # cwd neutro: nenhum teste depende do diretório atual
for t in "$DIR"/test_*.py; do
  nome=$(basename "$t")
  saida=$(python3 -I "$t" 2>&1); rc=$?
  linha=$(grep '^RESUMO ' <<<"$saida" | tail -1)
  if [ "$VERBOSO" = 1 ]; then echo "$saida"; elif [ $rc -ne 0 ]; then grep -E '^(FALHA|Traceback|  File|[A-Za-z]+Error)' <<<"$saida"; fi
  if [ $rc -ne 0 ]; then falhou=1; resumo+=("FALHA $nome: ${linha#RESUMO * }${linha:+ }(rc=$rc)"); else resumo+=("ok    $nome: ${linha#RESUMO * }"); fi
done
echo; echo "== resumo"; printf '%s\n' "${resumo[@]}"
exit $falhou
