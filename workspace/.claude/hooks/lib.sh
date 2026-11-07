# Funções comuns dos hooks de sync do workspace.
cd "${CLAUDE_PROJECT_DIR:-$HOME/workspace}" || exit 0

# Várias sessões (a interativa e os managers da esteira) sincronizam o mesmo repo:
# um sync por vez, senão dois commits simultâneos batem no index.lock.
mkdir -p "$HOME/.cache"
exec 9>"$HOME/.cache/leme-workspace-sync.lock"
flock -w 120 9 || exit 0

# Lock do git ocupado (outro git rodando no workspace): espera até 30 s. Se continuar,
# pula este sync sem falhar; o próximo Stop/SessionStart tenta de novo. Lock com mais de
# 10 min é provavelmente resto de um git que morreu: avisa em vez de pular calado.
lock_git="$(git rev-parse --git-path index.lock 2>/dev/null)"
for _ in $(seq 30); do [ -e "$lock_git" ] || break; sleep 1; done
if [ -e "$lock_git" ]; then
  if [ $(( $(date +%s) - $(stat -c %Y "$lock_git") )) -gt 600 ]; then
    jq -n --arg m "SYNC DO WORKSPACE: $lock_git existe há mais de 10 min (git que morreu?). Sync pulado. Confira se nenhum git está rodando e apague o arquivo." '{systemMessage: $m}'
  fi
  exit 0
fi

# Roda um comando git; se bater em index.lock, espera e tenta de novo (até 5 vezes).
git_tenta() {
  local out i
  for i in 1 2 3 4 5; do
    if out=$("$@" 2>&1); then printf '%s' "$out"; return 0; fi
    grep -q 'index.lock' <<<"$out" || { printf '%s' "$out"; return 1; }
    sleep 2
  done
  printf '%s' "$out"
  return 75  # lock persistente: quem chama pula o sync
}

rebase_em_andamento() {
  [ -d "$(git rev-parse --git-path rebase-merge)" ] || [ -d "$(git rev-parse --git-path rebase-apply)" ]
}

# Faz pull --rebase --autostash. Em conflito, aborta o rebase (o abort devolve
# o autostash) e retorna 1 com o detalhe em $SYNC_ERRO. Nunca força nada.
sync_pull() {
  local out rc
  out=$(git_tenta git pull --rebase --autostash); rc=$?
  [ $rc -eq 75 ] && exit 0  # lock do git persistente: pula este sync sem falhar
  if [ $rc -ne 0 ]; then
    if rebase_em_andamento; then
      git rebase --abort >/dev/null 2>&1
      SYNC_ERRO="conflito no git pull --rebase; rodei git rebase --abort, nada foi descartado e os commits locais continuam só locais. Saída do git: $out"
    else
      SYNC_ERRO="git pull --rebase falhou (rc=$rc). Saída do git: $out"
    fi
    return 1
  fi
  if grep -qi "autostash resulted in conflicts" <<<"$out"; then
    SYNC_ERRO="o pull funcionou, mas reaplicar as mudanças não commitadas (autostash) deu conflito. Elas estão salvas no git stash; o working tree tem marcadores de conflito. Saída do git: $out"
    return 1
  fi
  return 0
}
