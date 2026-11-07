#!/usr/bin/env bash
# Stop: se memory/ ou notes/ mudaram, commit + pull --rebase + push.
# Também reenvia commits locais que ficaram pendentes de uma tentativa anterior.
set -u
input=$(cat)
# Evita loop: se este hook já bloqueou o Stop neste turno, não repete.
[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0
source "$(dirname "$0")/lib.sh"

bloqueia() {
  jq -n --arg r "SYNC DO WORKSPACE FALHOU: $1
Avise o usuário agora, mostrando esse erro e o estado do repo (git status, git log --oneline -5). Não use --force, não descarte mudanças, não tente resolver o conflito sem o OK dele." \
    '{decision: "block", reason: $r}'
  exit 0
}

[ "$(git branch --show-current)" = "main" ] || exit 0
rebase_em_andamento && bloqueia "há um rebase em andamento em ~/workspace; não commitei nada."

if [ -n "$(git status --porcelain -- memory notes)" ]; then
  git_tenta git add -A -- memory notes >/dev/null; [ $? -eq 75 ] && exit 0
  files=$(git diff --cached --name-only -- memory notes)
  if [ -n "$files" ]; then
    n=$(wc -l <<<"$files")
    if [ "$n" -le 3 ]; then
      msg="sync: $(paste -sd, <<<"$files" | sed 's/,/, /g')"
    else
      msg="sync: $n arquivos"
    fi
    out=$(git_tenta git commit -q -m "$msg" -- memory notes); rc=$?
    [ $rc -eq 75 ] && exit 0
    [ $rc -ne 0 ] && bloqueia "git commit falhou: $out"
  fi
fi

# Só sincroniza se houver algo local para enviar.
if git rev-parse -q --verify '@{u}' >/dev/null 2>&1; then
  git fetch -q origin 2>/dev/null
  [ "$(git rev-list --count '@{u}..HEAD')" -gt 0 ] || exit 0
  sync_pull || bloqueia "$SYNC_ERRO"
  out=$(git push -q 2>&1) || bloqueia "git push falhou: $out"
else
  out=$(git push -q -u origin main 2>&1) || bloqueia "git push falhou: $out"
fi
exit 0
