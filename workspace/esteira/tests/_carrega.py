"""Carrega o despachante da esteira isolado numa pasta temporária.

carrega() devolve (m, T): o módulo com toda constante de caminho dentro de T e com rede, Jira, Slack,
systemd, gh, claude e push bloqueados. Teste que precisa de uma resposta do "mundo" troca a função
do módulo (m.jira_req, m.le_env, ...) ou o m.subprocess.run, que já é o protegido.
"""
import importlib.machinery
import importlib.util
import itertools
import os
import shutil
import subprocess as _sp
import sys
import tempfile
import traceback
import urllib.request
from contextlib import contextmanager
from pathlib import Path

ESTEIRA = "/home/leme/workspace/esteira/bin/esteira"
_n = itertools.count()


class Bloqueado(RuntimeError):
    pass


def _bloqueia(nome):
    def f(*a, **k):
        raise Bloqueado(f"{nome} bloqueado no teste")
    return f


def _urlopen_bloqueado(*a, **k):
    raise Bloqueado("rede bloqueada no teste (urlopen)")


urllib.request.urlopen = _urlopen_bloqueado  # o processo de teste inteiro fica sem rede HTTP


def _dentro(p, T):
    try:
        Path(os.path.abspath(p)).relative_to(T)
        return True
    except ValueError:
        return False


class SubprocessProtegido:
    """No lugar do módulo subprocess dentro da esteira. Só git local dentro de T passa; o resto
    (gh, systemctl, systemd-run, claude, pnpm, fnm, git push/clone/ls-remote) volta rc=127 ou levanta."""
    GIT_OK = {"init", "config", "add", "commit", "rev-parse", "diff", "status", "fetch", "merge", "worktree",
              "branch", "checkout", "rev-list", "log", "update-ref", "show"}

    def __init__(self, T):
        self._T = Path(T)
        self.bloqueados = []

    def __getattr__(self, nome):  # constantes e classes (PIPE, STDOUT, CompletedProcess, TimeoutExpired...)
        return getattr(_sp, nome)

    def _permitido(self, cmd, kw):
        if isinstance(cmd, (str, bytes)) or not cmd or os.path.basename(str(cmd[0])) != "git":
            return False
        args, alvo = [str(a) for a in cmd[1:]], kw.get("cwd")
        while args and args[0].startswith("-"):
            op = args.pop(0)
            if op == "-C" and args:
                alvo = args.pop(0)
        if alvo is None or not _dentro(alvo, self._T) or not args or args[0] not in self.GIT_OK:
            return False
        if args[0] == "fetch":  # só de origin local, dentro de T
            url = _sp.run(["git", "-C", str(alvo), "remote", "get-url", "origin"], capture_output=True,
                          text=True).stdout.strip()
            return bool(url) and _dentro(url, self._T)
        return True

    def run(self, cmd, *a, **kw):
        if self._permitido(cmd, kw):
            return _sp.run(cmd, *a, **kw)
        self.bloqueados.append(cmd)
        texto = kw.get("text") or kw.get("encoding") or kw.get("universal_newlines")
        vazio = "" if texto else b""
        erro = "bloqueado no teste" if texto else b"bloqueado no teste"
        if kw.get("check"):
            raise _sp.CalledProcessError(127, cmd, vazio, erro)
        return _sp.CompletedProcess(cmd, 127, stdout=vazio, stderr=erro)

    def Popen(self, cmd, *a, **kw):
        self.bloqueados.append(cmd)
        raise Bloqueado(f"Popen bloqueado no teste: {str(cmd)[:120]}")

    call = check_call = check_output = getoutput = getstatusoutput = _bloqueia("subprocess")


def carrega():
    T = Path(tempfile.mkdtemp(prefix="esteira-teste-")).resolve()
    nome = f"esteira_teste_{os.getpid()}_{next(_n)}"
    loader = importlib.machinery.SourceFileLoader(nome, ESTEIRA)
    spec = importlib.util.spec_from_loader(nome, loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)

    m.HOME = T / "home"
    m.ROOT = T / "ws"
    m.ESC = m.ROOT / ".escritorio"
    m.CARDS, m.FILA = m.ESC / "cards", m.ESC / "fila"
    m.PROCESSADOS = m.FILA / "processados"
    m.LOGS = T / "logs"
    m.REPO_APP = m.ROOT / "repos" / "leme-app"
    m.WORKTREES = m.REPO_APP / ".worktrees"
    m.CONFIG = T / "config"
    m.CONFIG_ESTEIRA = m.ESC / "config.json"
    m.ARQUIVO = m.ESC / "arquivo.jsonl"
    m.NOVOS = m.ESC / "novos"
    m.SLACK_DIR = m.ESC / "slack"
    m.SLACK_ENTRADA, m.SLACK_DECISOES = m.SLACK_DIR / "entrada", m.SLACK_DIR / "decisoes"
    m.SLACK_INDICE, m.SLACK_ESTADO = m.SLACK_DIR / "indice.json", m.ESC / "slack-estado.json"
    m.SUGESTOES = m.ESC / "sugestoes"
    m.MEMORIA_OUVIDOR = m.ROOT / "memory" / "ouvidor-o-que-nao-sugerir.md"
    m.PROJETO_CLAUDE = T / "claude-projects"
    m.FNM_DIR = T / "fnm"
    fora = [n for n, v in vars(m).items() if isinstance(v, Path) and not _dentro(v, T)]
    if fora:  # constante nova no código que este carregador não conhece: melhor parar do que tocar no real
        shutil.rmtree(T, ignore_errors=True)
        raise RuntimeError(f"constantes de caminho fora da pasta temporária: {fora}")
    for d in (m.CARDS, m.PROCESSADOS, m.LOGS):
        d.mkdir(parents=True, exist_ok=True)

    m.subprocess = SubprocessProtegido(T)
    urllib.request.urlopen = _urlopen_bloqueado  # m.urllib é o módulo global: desfaz o mock de um ambiente anterior
    m.preview_ativo = lambda key: False
    m.preview_stop = lambda key: m.atualiza_campos(key, preview_url=None)
    m.preview_start = _bloqueia("preview_start")
    m.jira_req = _bloqueia("jira_req")
    m.slack_get = _bloqueia("slack_get")
    m.slack_baixa = _bloqueia("slack_baixa")
    m.anexa_arquivos_real = m.anexa_arquivos  # o real só sai pela rede via urlopen, que também está bloqueado
    m.anexa_arquivos = _bloqueia("anexa_arquivos")
    m.atualiza_pendencias = lambda: (True, "pendências (mock)")
    m.le_env = lambda caminho: {"ATLASSIAN_SITE": "leme-tec.atlassian.net", "ATLASSIAN_EMAIL": "teste@exemplo",
                                "ATLASSIAN_TOKEN": "falso"}
    m.pr_mergeado = lambda url: None
    m.pr_mergeado_da_branch = lambda branch: None
    m.bin_node = _bloqueia("bin_node (fnm/npm)")
    m.path_com_node = lambda wt: "/usr/local/bin:/usr/bin:/bin"
    m.manager_vivo = lambda key: None
    return m, T


def limpa(T):
    shutil.rmtree(T, ignore_errors=True)


@contextmanager
def ambiente():
    m, T = carrega()
    try:
        yield m, T
    finally:
        limpa(T)


class Placar:
    def __init__(self, nome):
        self.nome, self.ok, self.tot = nome, 0, 0

    def confere(self, caso, cond, detalhe=""):
        self.tot += 1
        self.ok += bool(cond)
        print(("OK    " if cond else "FALHA ") + caso + (f"  [{str(detalhe)[:300]}]" if detalhe and not cond else ""),
              flush=True)

    def grupo(self, titulo, fn):
        """Roda um grupo de casos; exceção conta como uma FALHA e não derruba os outros grupos."""
        print(f"== {titulo}", flush=True)
        try:
            fn()
        except Exception as e:
            self.confere(f"{titulo}: terminou sem exceção", False, f"{e!r}")
            traceback.print_exc()

    def fim(self):
        print(f"RESUMO {self.nome}: {self.ok}/{self.tot} ok", flush=True)
        sys.exit(0 if self.tot and self.ok == self.tot else 1)


def recusa(m, *a, **k):
    """None se a transição passou; o texto da TransicaoInvalida se foi recusada."""
    try:
        m.transiciona(*a, **k)
        return None
    except m.TransicaoInvalida as e:
        return str(e)


def leva(m, key, *etapas, **kw):
    """Cria o card na fila (pelo despachante) e passa pelas etapas com status rodando."""
    m.transiciona(key, "fila", "rodando", por_despachante=True, **kw)
    for e in etapas:
        m.transiciona(key, e, "rodando")


def git(*args, cwd=None):
    return _sp.run(["git", *map(str, args)], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def repo_com_origin(T, nome="repo"):
    """origin (repo normal, branch main, 1 commit) + clone. Tudo local em T, sem push."""
    origin, clone = T / f"{nome}-origin", T / nome
    origin.mkdir(parents=True)
    git("-C", origin, "init", "-q", "-b", "main")
    commit(origin, "a.txt", "1", "1")
    git("clone", "-q", origin, clone)
    identidade(clone)
    return origin, clone


def identidade(repo):
    git("-C", repo, "config", "user.email", "teste@exemplo")
    git("-C", repo, "config", "user.name", "teste")


def commit(repo, arq, texto, msg):
    identidade(repo)
    (Path(repo) / arq).parent.mkdir(parents=True, exist_ok=True)
    (Path(repo) / arq).write_text(texto)
    git("-C", repo, "add", ".")
    git("-C", repo, "commit", "-qm", msg)
