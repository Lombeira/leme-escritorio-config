"""Guard (PreToolUse) protege o controle da esteira e libera os arquivos de trabalho do card.
Só alimenta o guard com JSON pelo stdin: nenhum dos comandos dos casos é executado."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar  # noqa: E402

P = Placar("test_guard")
GUARD = "/home/leme/workspace/.claude/hooks/guard.py"
W = "/home/leme/workspace"
C = f"{W}/.escritorio/cards/LM-1"
PROTEGE, LIVRE = "protege", "livre"
CASOS = [
    ("Write", f"{C}/estado.json", PROTEGE),
    ("Edit", f"{C}/.interno.json", PROTEGE),
    ("Write", f"{W}/.escritorio/fila/aprovar-LM-1.json", PROTEGE),
    ("Write", f"{W}/.escritorio/respostas/x.json", PROTEGE),
    ("Write", f"{W}/.escritorio/sugestoes/s1/estado.json", PROTEGE),
    ("Write", f"{W}/.escritorio/novos/n1/final.json", PROTEGE),
    ("Edit", f"{W}/esteira/bin/esteira", PROTEGE),
    ("Write", f"{W}/.claude/agents/manager.md", PROTEGE),
    ("Edit", f"{W}/.claude/hooks/guard.py", PROTEGE),
    ("Bash", f"echo '{{}}' > {C}/estado.json", PROTEGE),
    ("Bash", f"cp /tmp/x.json {W}/.escritorio/fila/", PROTEGE),
    ("Bash", f"mv {W}/.escritorio/fila/a.json /tmp/", PROTEGE),
    ("Bash", f"sed -i s/a/b/ {W}/esteira/bin/esteira", PROTEGE),
    ("Bash", f"rm {C}/.interno.json", PROTEGE),
    ("Bash", f"cd {W}/.escritorio && rm fila/a.json", PROTEGE),
    ("Write", f"{C}/triagem.md", LIVRE),
    ("Write", f"{C}/implementacao.md", LIVRE),
    ("Write", f"{C}/qa.md", LIVRE),
    ("Write", f"{C}/review.md", LIVRE),
    ("Write", f"{C}/evidencias/1-login.png", LIVRE),
    ("Write", f"{W}/.escritorio/novos/n1/rascunho.json", LIVRE),
    ("Bash", f"cat {C}/estado.json", LIVRE),
    ("Bash", f"ls {W}/.escritorio/fila/", LIVRE),
    ("Bash", "esteira-estado LM-1 front rodando --agente front-dev", LIVRE),
    ("Write", f"{W}/repos/leme-app/.claude/agents/reviewer.md", LIVRE),
]
# (comando, decisão interativa, decisão na esteira): travas de git/gh que não dependem de caminho
CASOS_GH = [
    ("gh api repos/leme-tech/leme-app/pulls/870/reviews --method POST --input x.json", "allow", "deny"),
    ("gh pr comment 870 --body oi", "allow", "deny"),
    ("gh api repos/leme-tech/leme-app/pulls/870/files", "allow", "allow"),
    ("gh api -X DELETE repos/leme-tech/leme-app/git/refs/heads/x", "deny", "deny"),
    ("gh repo delete leme-tech/x", "deny", "deny"),
    ("git push --force origin LM-1-x", "deny", "deny"),
    ("git push origin HEAD:refs/heads/main", "deny", "deny"),
    ("git commit --no-verify -m x", "deny", "deny"),
    ("git -c core.hooksPath=/dev/null commit -m x", "deny", "deny"),
    ("GIT_CONFIG_COUNT=1 git status", "deny", "deny"),
]


def decide(tool, inp, cwd, headless):
    env = {k: v for k, v in os.environ.items() if k != "ESTEIRA_HEADLESS"}
    if headless:
        env["ESTEIRA_HEADLESS"] = "1"
    r = subprocess.run([sys.executable, "-I", GUARD], input=json.dumps({"tool_name": tool, "tool_input": inp, "cwd": cwd}),
                       capture_output=True, text=True, env=env, cwd=cwd, timeout=30)
    if r.returncode != 0:
        return f"rc={r.returncode}: {r.stderr.strip()[:200]}"
    return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] if r.stdout.strip() else "allow"


def casos(cwd):
    for modo, headless in (("interativo", False), ("esteira (ESTEIRA_HEADLESS=1)", True)):
        protegido = "deny" if headless else "ask"
        for tool, alvo, tipo in CASOS:
            inp = {"command": alvo} if tool == "Bash" else {"file_path": alvo}
            esperado = protegido if tipo == PROTEGE else "allow"
            obtido = decide(tool, inp, cwd, headless)
            P.confere(f"[{modo}] {tool} {alvo.replace(W, '~/workspace')[:90]} -> {esperado}", obtido == esperado, obtido)
        for cmd, inter, esteira in CASOS_GH:
            esperado = esteira if headless else inter
            obtido = decide("Bash", {"command": cmd}, cwd, headless)
            P.confere(f"[{modo}] {cmd[:90]} -> {esperado}", obtido == esperado, obtido)


def principal():
    cwd = tempfile.mkdtemp(prefix="esteira-teste-")
    try:
        casos(cwd)
    finally:
        shutil.rmtree(cwd, ignore_errors=True)


P.grupo("guard", principal)
P.fim()
