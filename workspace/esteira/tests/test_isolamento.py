"""O próprio isolamento do _carrega: caminhos na pasta temporária e mundo externo bloqueado."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Bloqueado, Placar, ambiente, carrega, limpa, repo_com_origin  # noqa: E402

P = Placar("test_isolamento")


def caminhos():
    m, T = carrega()
    try:
        fora = [n for n, v in vars(m).items() if isinstance(v, Path) and not str(v).startswith(str(T))]
        P.confere("toda constante Path do módulo aponta para a pasta temporária", not fora, fora)
        P.confere("pasta temporária tem o prefixo esteira-teste-", T.name.startswith("esteira-teste-"))
    finally:
        limpa(T)
    P.confere("limpa apaga a pasta temporária", not T.exists())


def bloqueios():
    with ambiente() as (m, T):
        for cmd in (["gh", "pr", "view", "1"], ["systemctl", "--user", "is-active", "x"], ["claude", "-p", "oi"],
                    ["pnpm", "install"], ["git", "-C", "/home/leme/workspace", "status"], ["git", "status"],
                    ["git", "-C", str(T), "push", "origin", "x"], ["git", "clone", "git@github.com:leme-tech/x.git", str(T / "x")]):
            r = m.subprocess.run(cmd, capture_output=True, text=True)
            P.confere(f"bloqueado: {' '.join(cmd)[:60]}", r.returncode == 127 and r.stderr == "bloqueado no teste")
        try:
            m.subprocess.Popen(["claude", "-p"])
            P.confere("Popen bloqueado", False)
        except Bloqueado:
            P.confere("Popen bloqueado", True)
        for nome, chama in (("urlopen", lambda: m.urllib.request.urlopen("https://leme-tec.atlassian.net")),
                            ("jira_req", lambda: m.jira_req("issue/LM-1")), ("slack_get", lambda: m.slack_get("x")),
                            ("anexa_arquivos", lambda: m.anexa_arquivos("LM-1", []))):
            try:
                chama()
                P.confere(f"{nome} bloqueado", False)
            except Bloqueado:
                P.confere(f"{nome} bloqueado", True)
        O, R = repo_com_origin(T)
        r = m.subprocess.run(["git", "-C", str(R), "fetch", "-q", "origin"], capture_output=True)
        P.confere("git fetch de origin local dentro da pasta temporária passa", r.returncode == 0, r.stderr)
        import subprocess as sp
        sp.run(["git", "-C", str(R), "remote", "set-url", "origin", "git@github.com:leme-tech/x.git"], check=True)
        r = m.subprocess.run(["git", "-C", str(R), "fetch", "-q", "origin"], capture_output=True)
        P.confere("git fetch de origin remoto é bloqueado", r.returncode == 127)


P.grupo("caminhos", caminhos)
P.grupo("bloqueios", bloqueios)
P.fim()
