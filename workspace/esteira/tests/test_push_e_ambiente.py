"""Subagente em primeiro plano nos claude -p (o de segundo plano morre aos 600 s) e fila do push (uma suíte por vez)."""
import io
import json
import os
import subprocess as sp
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, leva  # noqa: E402

P = Placar("test_push_e_ambiente")


class ProcFalso:
    pid = 0

    def poll(self):
        return None


def ambiente_do_manager():
    with ambiente() as (m, T):
        P.confere("env_claude desliga tarefas em segundo plano",
                  m.env_claude().get("CLAUDE_CODE_DISABLE_BACKGROUND_TASKS") == "1")
        K = "TESTE-1"
        leva(m, K, "triagem", "front", "review", "qa")
        m.transiciona(K, "validacao", "aguardando_humano")
        disparos = []
        m.subprocess.Popen = lambda cmd, **kw: (disparos.append(kw.get("env", {})), ProcFalso())[1]
        (m.FILA / "a.json").write_text(json.dumps({"key": K, "acao": "aprovar", "por": "feda", "em": 1}))
        d = m.Despachante()
        d.processa_fila()
        d.agenda()
        env = disparos[-1] if disparos else {}
        P.confere("manager disparado com CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1",
                  env.get("CLAUDE_CODE_DISABLE_BACKGROUND_TASKS") == "1", sorted(env)[:5])
        P.confere("e mantém ESTEIRA_HEADLESS e ESTEIRA_CARD",
                  env.get("ESTEIRA_HEADLESS") == "1" and env.get("ESTEIRA_CARD") == K)
        fonte = Path(m.__file__ if hasattr(m, "__file__") else "/home/leme/workspace/esteira/bin/esteira").read_text()
        P.confere("nenhum Popen de claude monta o ambiente com env_systemd direto",
                  'env = env_systemd()\n        env["ESTEIRA_HEADLESS"]' not in fonte)


def prepara_card(m, T, K):
    leva(m, K, "triagem", "front", "review", "qa")
    m.atualiza_campos(K, branch=f"{K}-x")
    m.worktree(K).mkdir(parents=True, exist_ok=True)
    (m.CARDS / K).mkdir(parents=True, exist_ok=True)


def script_do_push(m, T, K):
    capturado = []
    m.subprocess.run = lambda cmd, *a, **kw: (capturado.append(cmd), sp.CompletedProcess(cmd, 0 if cmd[0] == "systemd-run" else 3, "", ""))[1]
    with redirect_stdout(io.StringIO()):
        rc = m.cmd_push(["iniciar", K])
    cmd = next(c for c in capturado if c[0] == "systemd-run")
    i = cmd.index("bash")
    return rc, cmd[i:]


def fila_do_push():
    with ambiente() as (m, T):
        for K in ("TESTE-2", "TESTE-3"):
            prepara_card(m, T, K)
        rc, bash2 = script_do_push(m, T, "TESTE-2")
        _, bash3 = script_do_push(m, T, "TESTE-3")
        P.confere("iniciar sobe a unidade", rc == 0)
        P.confere("push passa pelo flock com a trava em .escritorio/push.lock",
                  "flock" in bash2[2] and bash2[-1] == str(m.ESC / "push.lock"), bash2)
        # git falso: registra início e fim; se as duas suítes se sobrepuserem, os intervalos se cruzam
        bindir, marcas = T / "bin", T / "marcas.txt"
        bindir.mkdir()
        (bindir / "git").write_text(f'#!/bin/bash\necho "ini $(date +%s.%N)" >> {marcas}\nsleep 1\n'
                                    f'echo "fim $(date +%s.%N)" >> {marcas}\necho saida-do-push\n')
        (bindir / "git").chmod(0o755)
        env = {**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}"}
        procs = [sp.Popen(b, env=env) for b in (bash2, bash3)]
        for p in procs:
            p.wait(timeout=30)
        linhas = [ln.split() for ln in marcas.read_text().splitlines()]
        P.confere("as duas suítes rodaram em sequência (ini, fim, ini, fim)",
                  [x[0] for x in linhas] == ["ini", "fim", "ini", "fim"], linhas)
        log2 = (m.CARDS / "TESTE-2" / "push.log").read_text()
        P.confere("log começa com a linha da fila e traz a saída do push",
                  log2.startswith("na fila do push desde") and "saida-do-push" in log2, log2)
        P.confere("rc do push é gravado", (m.CARDS / "TESTE-2" / "push.rc").read_text().strip() == "0")


def esperar_na_fila():
    with ambiente() as (m, T):
        K = "TESTE-4"
        prepara_card(m, T, K)
        (m.CARDS / K / "push.log").write_text("na fila do push desde 10:00:00\n")
        out = io.StringIO()
        t0 = time.time()
        with redirect_stdout(out):
            rc = m.cmd_push(["esperar", K, "--max", "0"])
        P.confere("esperar na fila sai com 2 e diz 'na fila'", rc == 2 and "na fila" in out.getvalue(), out.getvalue())
        P.confere("esperar respeita --max 0", time.time() - t0 < 10)
        (m.CARDS / K / "push.log").write_text("na fila do push desde 10:00:00\n🔍 Running Biome checks...\n")
        out = io.StringIO()
        with redirect_stdout(out):
            rc = m.cmd_push(["esperar", K, "--max", "0"])
        P.confere("com a suíte já rodando diz 'ainda rodando'", rc == 2 and "ainda rodando" in out.getvalue(),
                  out.getvalue())


P.grupo("ambiente do manager", ambiente_do_manager)
P.grupo("fila do push", fila_do_push)
P.grupo("esperar na fila", esperar_na_fila)
P.fim()
