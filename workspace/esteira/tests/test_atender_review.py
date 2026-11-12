"""Atender review de PR (AR-<repo>-<n>): pedido, transições, worktree na branch do PR, threads, aprovação e respostas.
O gh é simulado; git só em repositórios temporários, sem push."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, commit, git, identidade, recusa  # noqa: E402

P = Placar("test_atender_review")
URL = "https://github.com/leme-tech/leme.tec.br/pull/38"
BASE = {"key": "AR-leme.tec.br-38", "url": URL, "repo": "leme.tec.br", "numero": 38, "por": "glauco"}
K = BASE["key"]


def cp(cmd, rc=0, out="", err=""):
    return subprocess.CompletedProcess(cmd, rc, stdout=out, stderr=err)


class GhFalso:
    def __init__(self, m, estado="OPEN", fork=False, branch="feat/equidade"):
        self.real, self.respostas, self.installs = m.subprocess.run, [], []
        self.estado, self.fork, self.branch = estado, fork, branch
        m.subprocess.run = self

    def __call__(self, cmd, *a, **k):
        if cmd[:3] == ["gh", "pr", "view"]:
            return cp(cmd, 0, json.dumps({"title": "Landing equidade", "author": {"login": "fer"}, "state": self.estado,
                                          "headRefName": self.branch, "isCrossRepository": self.fork}))
        if cmd[:3] == ["gh", "api", "graphql"]:
            nos = [{"id": "T1", "isResolved": False, "isOutdated": False, "path": "src/a.tsx", "line": 10, "originalLine": 10,
                    "comments": {"nodes": [{"databaseId": 111, "author": {"login": "glauco"}, "body": "conta errada",
                                            "createdAt": "2026-11-10T10:00:00Z"}]}},
                   {"id": "T2", "isResolved": True, "isOutdated": False, "path": "src/b.tsx", "line": 3, "originalLine": 3,
                    "comments": {"nodes": [{"databaseId": 222, "author": {"login": "glauco"}, "body": "ok",
                                            "createdAt": "2026-11-10T10:00:00Z"}]}},
                   {"id": "T3", "isResolved": False, "isOutdated": True, "path": "src/c.tsx", "line": None, "originalLine": 7,
                    "comments": {"nodes": [{"databaseId": 333, "author": {"login": "glauco"}, "body": "LGPD?",
                                            "createdAt": "2026-11-10T10:00:00Z"}]}}]
            return cp(cmd, 0, json.dumps({"data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": nos}}}}}))
        if cmd[:4] == ["gh", "api", "--method", "POST"] and cmd[4].endswith("/replies"):
            self.respostas.append((int(cmd[4].split("/comments/")[1].split("/")[0]), cmd[cmd.index("-f") + 1][5:]))
            return cp(cmd, 0, "{}")
        if cmd and cmd[0] in ("npm", "pnpm"):
            self.installs.append(cmd)
            Path(k["cwd"], "node_modules").mkdir(exist_ok=True)
            return cp(cmd, 0)
        return self.real(cmd, *a, **k)


def pedido(m, nome, dados):
    (m.FILA / nome).write_text(json.dumps(dados))


def erro_de(m, nome):
    return next(m.PROCESSADOS.glob(f"*-{nome}.erro"), None)


def valida():
    with ambiente() as (m, T):
        gh = GhFalso(m)
        v = m.valida_pedido_ar
        ok, _, dados = v(BASE)
        P.confere("PR aberto do leme.tec.br é aceito, com a branch", ok and dados["branch"] == "feat/equidade", dados)
        P.confere("leme-app também vale", v({**BASE, "key": "AR-leme-app-38", "repo": "leme-app",
                                            "url": "https://github.com/leme-tech/leme-app/pull/38"})[0])
        r = v({**BASE, "key": "AR-leme-core-38", "repo": "leme-core", "url": "https://github.com/leme-tech/leme-core/pull/38"})
        P.confere("leme-core é recusado (só front)", not r[0] and "só vale para" in r[1], r)
        P.confere("key tem que ser AR-<repo>-<n>", not v({**BASE, "key": "PR-leme.tec.br-38"})[0])
        P.confere("url fora da leme-tech é recusada", not v({**BASE, "url": "https://github.com/outra/leme.tec.br/pull/38"})[0])
        gh.estado = "MERGED"
        P.confere("PR mergeado é recusado", not v(BASE)[0])
        gh.estado, gh.fork = "OPEN", True
        P.confere("PR de fork é recusado", not v(BASE)[0])
        gh.fork, gh.branch = False, "main"
        P.confere("PR com branch main é recusado", not v(BASE)[0])


def transicoes():
    with ambiente() as (m, T):
        m.transiciona(K, "fila", "rodando", por_despachante=True, tipo="atender_review")
        P.confere("fila -> front", recusa(m, K, "front", "rodando") is None)
        P.confere("front -> review não existe no atender review", recusa(m, K, "review", "rodando") is not None)
        P.confere("front -> validacao", recusa(m, K, "validacao", "aguardando_humano") is None)
        P.confere("agente não sai da validação sozinho (pr)", recusa(m, K, "pr", "rodando") is not None)
        P.confere("agente não encerra da validação (concluido)", recusa(m, K, "concluido", "concluido") is not None)
        P.confere("despachante leva para pr (aprovado)", recusa(m, K, "pr", "rodando", por_despachante=True) is None)
        P.confere("pr -> concluido pelo manager", recusa(m, K, "concluido", "concluido") is None)
        P.confere("atender review não mexe no status do Jira", m.status_jira_desejado(m.le_json(m.caminho_estado(K))) is None)


def fila_e_aprovacao():
    with ambiente() as (m, T):
        gh = GhFalso(m)
        d = m.Despachante()
        pedido(m, "a1.json", {**BASE, "key": "AR-leme-core-38", "repo": "leme-core",
                              "url": "https://github.com/leme-tech/leme-core/pull/38", "acao": "atender_review", "em": 1})
        d.processa_fila()
        P.confere("pedido do leme-core rejeitado na fila", erro_de(m, "a1.json") is not None)
        pedido(m, "a2.json", {**BASE, "acao": "atender_review", "em": 2})
        d.processa_fila()
        est, it = m.le_json(m.caminho_estado(K)), m.le_json(m.caminho_interno(K), {})
        P.confere("card criado como atender_review na fila, com branch e repo",
                  est["tipo"] == "atender_review" and est["etapa"] == "fila" and est["branch"] == "feat/equidade"
                  and est["repo"] == "leme.tec.br" and it["pendente"]["acao"] == "atender_review", (est, it))
        pedido(m, "a3.json", {**BASE, "acao": "atender_review", "em": 3})
        d.processa_fila()
        P.confere("segundo pedido com o card em andamento é rejeitado", erro_de(m, "a3.json") is not None)
        it.pop("pendente")
        m.escreve_json(m.caminho_interno(K), it)
        m.transiciona(K, "front", "rodando")
        m.transiciona(K, "validacao", "aguardando_humano")
        pedido(m, "ap1.json", {"key": K, "acao": "aprovar", "por": "feda", "em": 4,
                               "respostas": [{"responder_a": 111, "texto": "Corrigido em abc123."}]})
        d.processa_fila()
        it = m.le_json(m.caminho_interno(K), {})
        P.confere("aprovar guarda as respostas com o texto exato e agenda o push",
                  it["respostas_aprovadas"] == [{"responder_a": 111, "texto": "Corrigido em abc123."}]
                  and it["pendente"]["acao"] == "aprovar", it)
        P.confere("nada postado no GitHub na hora da aprovação", gh.respostas == [])
        it.pop("pendente")
        it.pop("respostas_aprovadas")
        m.escreve_json(m.caminho_interno(K), it)
        m.escreve_json(m.CARDS / K / "respostas.json", [{"responder_a": 111, "acao": "corrigido", "texto": "do json"}])
        pedido(m, "ap2.json", {"key": K, "acao": "aprovar", "por": "feda", "em": 5})
        d.processa_fila()
        it = m.le_json(m.caminho_interno(K), {})
        P.confere("aprovar sem respostas no pedido usa as mostradas (respostas.json)",
                  it["respostas_aprovadas"] == [{"responder_a": 111, "texto": "do json"}], it)
        it.pop("pendente")
        m.escreve_json(m.caminho_interno(K), it)
        pedido(m, "dv1.json", {"key": K, "acao": "devolver", "por": "feda", "em": 6})
        d.processa_fila()
        P.confere("devolver sem comentário é rejeitado", erro_de(m, "dv1.json") is not None)
        pedido(m, "dv2.json", {"key": K, "acao": "devolver", "por": "feda", "comentario": "refaz a thread 1", "em": 7})
        d.processa_fila()
        it = m.le_json(m.caminho_interno(K), {})
        P.confere("devolver com comentário agenda refazer", it["pendente"]["acao"] == "devolver"
                  and it["pendente"]["comentario"] == "refaz a thread 1", it)
        it.pop("pendente")
        m.escreve_json(m.caminho_interno(K), it)
        pedido(m, "dv3.json", {"key": K, "acao": "devolver", "por": "feda", "comentario": "não publicar", "em": 8})
        d.processa_fila()
        P.confere("'não publicar' encerra sem push", m.le_json(m.caminho_estado(K))["etapa"] == "concluido")


def worktree_e_threads():
    with ambiente() as (m, T):
        gh = GhFalso(m)
        origin = T / "origin-landing"
        origin.mkdir()
        git("-C", origin, "init", "-q", "-b", "main")
        commit(origin, "a.txt", "1", "1")
        git("-C", origin, "checkout", "-q", "-b", "feat/equidade")
        commit(origin, "src/a.tsx", "v1\n", "pr")
        git("-C", origin, "checkout", "-q", "main")
        repo = m.ROOT / "repos" / "leme.tec.br"
        repo.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "-q", origin, repo)
        identidade(repo)
        m.transiciona(K, "fila", "rodando", por_despachante=True, tipo="atender_review")
        m.atualiza_campos(K, tipo="atender_review", repo="leme.tec.br", numero=38, branch="feat/equidade", pr_url=URL)
        ok, msg = m.prepara_worktree_ar(K)
        wt = m.worktree(K)
        P.confere("worktree criado na pasta do repo da landing", ok and wt == repo / ".worktrees" / K, (ok, msg, wt))
        P.confere("worktree na branch do PR (mesmo nome do remoto)",
                  git("-C", wt, "rev-parse", "--abbrev-ref", "HEAD") == "feat/equidade")
        P.confere("branch acompanha origin/feat/equidade",
                  git("-C", wt, "rev-parse", "--abbrev-ref", "@{upstream}") == "origin/feat/equidade")
        P.confere("install do repo rodou (npm ci)", gh.installs and gh.installs[0][:2] == ["npm", "ci"], gh.installs)
        th = m.le_json(m.CARDS / K / "threads.json")
        P.confere("threads.json só com as não resolvidas, com o id para responder",
                  [t["responder_a"] for t in th] == [111, 333] and th[1]["desatualizada"] and th[1]["linha"] == 7, th)
        git("-C", origin, "checkout", "-q", "feat/equidade")
        commit(origin, "src/a.tsx", "v2\n", "autor do PR mexeu")
        git("-C", origin, "checkout", "-q", "main")
        m.prepara_worktree_ar(K)
        P.confere("reprepara traz o commit novo do autor (ff)", (wt / "src/a.tsx").read_text() == "v2\n")
        P.confere("install não roda de novo com node_modules", len(gh.installs) == 1, gh.installs)
        commit(wt, "src/a.tsx", "corrigido\n", "fix: review")
        git("-C", origin, "checkout", "-q", "feat/equidade")
        commit(origin, "src/z.tsx", "z\n", "mais um do autor")
        git("-C", origin, "checkout", "-q", "main")
        ok, _ = m.prepara_worktree_ar(K)
        P.confere("com commit nosso ainda não enviado, não mexe no worktree",
                  ok and (wt / "src/a.tsx").read_text() == "corrigido\n" and not (wt / "src/z.tsx").exists())


def respostas():
    with ambiente() as (m, T):
        gh = GhFalso(m)
        m.transiciona(K, "fila", "rodando", por_despachante=True, tipo="atender_review")
        m.atualiza_campos(K, tipo="atender_review", repo="leme.tec.br", numero=38, branch="feat/equidade", pr_url=URL)
        m.busca_threads(K)
        postadas, falhas = m.posta_respostas(K, [{"responder_a": 111, "texto": "  Corrigido em abc123.  "},
                                                 {"responder_a": 222, "texto": "thread resolvida"},
                                                 {"responder_a": 333, "texto": ""}])
        P.confere("posta só em thread aberta, com o texto exato (sem espaços nas pontas)",
                  gh.respostas == [(111, "Corrigido em abc123.")] and postadas == [111], gh.respostas)
        P.confere("thread resolvida vira falha, texto vazio é ignorado", [f["responder_a"] for f in falhas] == [222], falhas)
        d = m.Despachante()
        it = m.le_json(m.caminho_interno(K), {})
        it["respostas_aprovadas"] = [{"responder_a": 333, "texto": "Precisa de decisão de vocês."}]
        m.escreve_json(m.caminho_interno(K), it)
        d.posta_respostas_aprovadas(K)
        d.posta_respostas_aprovadas(K)
        est = m.le_json(m.caminho_estado(K))
        P.confere("respostas aprovadas postadas uma vez só", gh.respostas[1:] == [(333, "Precisa de decisão de vocês.")]
                  and est["respostas_postadas"] == 1, (gh.respostas, est.get("respostas_postadas")))


for titulo, fn in (("valida pedido", valida), ("transições", transicoes), ("fila e aprovação", fila_e_aprovacao),
                   ("worktree e threads", worktree_e_threads), ("respostas nas threads", respostas)):
    P.grupo(titulo, fn)
P.fim()
