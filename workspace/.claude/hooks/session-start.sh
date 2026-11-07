#!/usr/bin/env bash
# SessionStart: traz o que foi editado no Obsidian (git pull --rebase).
set -u
cat >/dev/null
source "$(dirname "$0")/lib.sh"

avisa() {
  jq -n --arg m "SYNC DO WORKSPACE: $1" \
    '{systemMessage: $m, hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: ($m + "\nAvise o usuário disso logo no início da resposta, antes de qualquer outra coisa.")}}'
  exit 0
}

[ "$(git branch --show-current)" = "main" ] || avisa "~/workspace não está na branch main; não fiz pull."
rebase_em_andamento && avisa "já existe um rebase em andamento em ~/workspace; não fiz pull."
sync_pull || avisa "$SYNC_ERRO"
exit 0
