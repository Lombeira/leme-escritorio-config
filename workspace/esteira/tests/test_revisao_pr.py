"""Revisão de PR de terceiros: pedido, worktree destacado (repo git local), achados contra o diff e publicação.
O gh é simulado (nenhuma chamada ao GitHub); git só em repositórios temporários, sem push."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, commit, git, identidade  # noqa: E402

P = Placar("test_revisao_pr")
PATCH = "@@ -1,3 +1,4 @@\n ctx\n-old\n+new\n+new2\n ctx2"
ARQ = "src/x.tsx"


def cp(cmd, rc=0, out="", err=""):
    return subprocess.CompletedProcess(cmd, rc, stdout=out, stderr=err)


class GhFalso:
    """Responde aos comandos gh que a esteira usa; o resto vai para o subprocess protegido."""

    def __init__(self, m):
        self.real, self.posts, self.resp_422, self.prs = m.subprocess.run, [], False, {870: "OPEN", 12: "OPEN"}
        m.subprocess.run = self

    def __call__(self, cmd, *a, **k):
        if cmd[:3] == ["gh", "pr", "view"] and "-R" in cmd:
            n = int(cmd[3])
            if n not in self.prs:
                return cp(cmd, 1, err="GraphQL: Could not resolve to a PullRequest")
            return cp(cmd, 0, json.dumps({"title": "Melhora X", "author": {"login": "fulano"}, "state": self.prs[n]}))
        if cmd[:3] == ["gh", "pr", "checkout"]:
            return cp(cmd, 1, err="a branch do PR foi apagada")  # força o caminho pull/<n>/head
        if cmd[:3] == ["gh", "pr", "view"] and "baseRefName" in cmd:
            return cp(cmd, 0, "main\n")
        if cmd[:2] == ["gh", "api"] and cmd[3:4] and "/files" in cmd[3]:
            linhas = [json.dumps({"filename": ARQ, "patch": PATCH}), json.dumps({"filename": "bin/logo.png", "patch": None})]
            return cp(cmd, 0, "\n".join(linhas) + "\n")
        if cmd[:2] == ["gh", "api"] and cmd[2].endswith("/reviews"):
            corpo = json.load(open(cmd[cmd.index("--input") + 1]))
            self.posts.append((cmd[2], corpo))
            if self.resp_422 and corpo["comments"]:
                return cp(cmd, 1, err="HTTP 422: Unprocessable Entity")
            return cp(cmd, 0, json.dumps({"html_url": "https://github.com/leme-tech/leme-app/pull/870#pullrequestreview-1"}))
        return self.real(cmd, *a, **k)


def pedido(m, nome, dados):
    (m.FILA / nome).write_text(json.dumps(dados))


def erro_de(m, nome):
    return next(m.PROCESSADOS.glob(f"*-{nome}.erro"), None)


BASE = {"key": "PR-870", "url": "https://github.com/leme-tech/leme-app/pull/870", "repo": "leme-app", "numero": 870,
        "por": "glauco"}


def valida_pedido():
    with ambiente() as (m, T):
        GhFalso(m)
        v = m.valida_pedido_pr
        P.confere("recusa PR fora da leme-tech", not v({**BASE, "url": "https://github.com/outra/leme-app/pull/870"})[0])
        P.confere("recusa key que não bate com o número", not v({**BASE, "key": "PR-1"})[0])
        P.confere("recusa repo com caractere inválido", not v({**BASE, "repo": "../x"})[0])
        P.confere("recusa número inválido", not v({**BASE, "numero": "abc"})[0])
        ok, _, dados = v(BASE)
        P.confere("PR válido: summary com título e autor", ok and dados["summary"] == "Melhora X (de @fulano)", dados)
        P.confere("PR-leme-app-870 também vale", v({**BASE, "key": "PR-leme-app-870"})[0])
        P.confere("outro repo exige PR-<repo>-<n>", not v({**BASE, "key": "PR-12", "repo": "leme-core", "numero": 12,
                                                         "url": "https://github.com/leme-tech/leme-core/pull/12"})[0]
                  and v({**BASE, "key": "PR-leme-core-12", "repo": "leme-core", "numero": 12,
                         "url": "https://github.com/leme-tech/leme-core/pull/12"})[0])
        r = v({**BASE, "key": "PR-404", "numero": 404, "url": "https://github.com/leme-tech/leme-app/pull/404"})
        P.confere("PR inexistente no GitHub é recusado", not r[0] and "não achei" in r[1], r)


def diff_do_pr():
    with ambiente() as (m, T):
        GhFalso(m)
        mapa = m.linhas_comentaveis("leme-app", 870)
        P.confere("linhas comentáveis do hunk (lado novo e antigo, inclusive contexto)",
                  mapa[ARQ] == {"RIGHT": {1, 2, 3, 4}, "LEFT": {1, 2, 3}} and mapa["bin/logo.png"] == {"RIGHT": set(), "LEFT": set()},
                  mapa)
        ok, fora = m.separa_por_diff([{"arquivo": ARQ, "linha": "2"}, {"arquivo": ARQ, "linha": 2, "lado": "LEFT"},
                                      {"arquivo": ARQ, "linha": 5}, {"arquivo": "outro.ts", "linha": 1},
                                      {"arquivo": ARQ, "linha": 1, "lado": "MEIO"}], mapa)
        P.confere("separa_por_diff aceita linha em texto e lado LEFT, recusa fora do diff/lado inválido",
                  [(c["linha"], c["lado"]) for c in ok] == [(2, "RIGHT"), (2, "LEFT")] and len(fora) == 3, (ok, fora))
        m.subprocess.run = lambda cmd, *a, **k: cp(cmd, 1, err="HTTP 404")
        m.transiciona("PR-1", "fila", "rodando", por_despachante=True, tipo="revisao_pr")
        m.atualiza_campos("PR-1", repo="leme-app", numero=1)
        r = m.publica_review_pr("PR-1", [], "resumo")
        P.confere("gh falhou ao ler o diff: não publica e diz o motivo", not r[0] and "não consegui ler" in r[1], r)


def fluxo():
    with ambiente() as (m, T):
        gh = GhFalso(m)
        origin = T / "origin-app"
        origin.mkdir()
        git("-C", origin, "init", "-q", "-b", "main")
        commit(origin, "a.txt", "1", "1")
        git("-C", origin, "checkout", "-q", "-b", "feat")
        commit(origin, ARQ, "novo\n", "pr")
        cabeca_pr = git("-C", origin, "rev-parse", "HEAD")
        git("-C", origin, "update-ref", "refs/pull/870/head", cabeca_pr)
        git("-C", origin, "checkout", "-q", "main")
        m.REPO_APP.parent.mkdir(parents=True)
        git("clone", "-q", origin, m.REPO_APP)
        identidade(m.REPO_APP)
        K = "PR-870"
        d = m.Despachante()
        pedido(m, "pr1.json", {**BASE, "acao": "revisar_pr", "comentario": "foco em acessibilidade", "em": 1})
        d.processa_fila()
        est, it = m.le_json(m.caminho_estado(K)), m.le_json(m.caminho_interno(K), {})
        P.confere("card criado como revisao_pr na fila", est["tipo"] == "revisao_pr" and est["etapa"] == "fila"
                  and est["repo"] == "leme-app" and est["numero"] == 870 and est["pr_url"] == BASE["url"], est)
        P.confere("foco guardado no pedido", it["pendente"].get("foco") == "foco em acessibilidade")
        pedido(m, "pr2.json", {**BASE, "acao": "revisar_pr", "em": 2})
        d.processa_fila()
        P.confere("revisar_pr de PR que já está na esteira é recusado", erro_de(m, "pr2.json"))
        it.pop("pendente")
        m.escreve_json(m.caminho_interno(K), it)  # não dispara o manager

        ok_w, msg = m.prepara_worktree_pr(K)
        wt = m.worktree(K)
        P.confere("worktree do PR preparado pelo fallback pull/870/head", ok_w, msg)
        P.confere("worktree fica em repos/leme-app/.worktrees", wt == m.WORKTREES / K)
        br = git("-C", wt, "branch", "--show-current") if wt.exists() else "?"
        P.confere("HEAD destacado no commit do PR, sem branch local",
                  ok_w and br == "" and git("-C", wt, "rev-parse", "HEAD") == cabeca_pr, br)
        est = m.le_json(m.caminho_estado(K))
        P.confere("estado registra base e HEAD destacado", est.get("base") == "main"
                  and est.get("branch", "").startswith("PR #870 (destacado em "), est.get("branch"))

        m.transiciona(K, "review", "rodando", agente="reviewer")
        (m.CARDS / K / "review.md").write_text("**Veredito: NEEDS CHANGES**\n")
        (m.CARDS / K / "achados.json").write_text(json.dumps([
            {"id": "a1", "severidade": "should", "arquivo": ARQ, "linha": 2, "lado": "RIGHT", "texto": "texto do modelo a1"},
            {"id": "a2", "severidade": "nit", "arquivo": ARQ, "linha": 99999, "lado": "RIGHT", "texto": "fora do diff"}]))
        m.transiciona(K, "validacao", "aguardando_humano", resumo="review: 0 🔴, 1 🟡, 1 ⚪")
        r = m.valida_achados(K)
        P.confere("achado fora do diff saiu do achados.json", [a["id"] for a in m.le_json(m.CARDS / K / "achados.json")] == ["a1"], r)
        P.confere("e virou texto no review.md", "fora do diff" in (m.CARDS / K / "review.md").read_text())

        aprovar = {"key": K, "acao": "aprovar", "por": "glauco", "em": 5, "resumo": "Valeu pelo PR! Dois pontos abaixo.",
                   "comentarios": [{"id": "a1", "arquivo": ARQ, "linha": 2, "lado": "RIGHT", "texto": "TEXTO EDITADO PELO GLAUCO"},
                                   {"id": "x9", "arquivo": ARQ, "linha": 99999, "lado": "RIGHT", "texto": "esse não cabe"}]}
        pedido(m, "ap.json", aprovar)
        d.processa_fila()
        c = gh.posts[-1][1] if gh.posts else {}
        P.confere("UM review, event COMMENT, no PR certo", len(gh.posts) == 1 and c["event"] == "COMMENT"
                  and gh.posts[0][0] == "repos/leme-tech/leme-app/pulls/870/reviews")
        P.confere("body = resumo exato", c.get("body") == "Valeu pelo PR! Dois pontos abaixo.")
        P.confere("inline com o texto EXATO do pedido (não o do achados.json)",
                  c.get("comments") == [{"path": ARQ, "line": 2, "side": "RIGHT", "body": "TEXTO EDITADO PELO GLAUCO"}])
        est = m.le_json(m.caminho_estado(K))
        P.confere("concluido, publicado, review_url", est["etapa"] == "concluido" and est["publicado"] is True
                  and est["review_url"].endswith("#pullrequestreview-1"))
        P.confere("recusado listado no resumo e no estado", "99999" in est["resumo"]
                  and [x["id"] for x in est["comentarios_recusados"]] == ["x9"], est["resumo"])

        def volta_para_validacao():
            m.transiciona(K, "fila", "rodando", por_despachante=True)
            m.transiciona(K, "review", "rodando")
            m.transiciona(K, "validacao", "aguardando_humano")
        volta_para_validacao()
        gh.posts.clear()
        gh.resp_422 = True
        pedido(m, "ap2.json", {**aprovar, "em": 6})
        d.processa_fila()
        est = m.le_json(m.caminho_estado(K))
        P.confere("422: tentou com comentários e depois só o resumo", len(gh.posts) == 2 and gh.posts[1][1]["comments"] == []
                  and est["etapa"] == "concluido", est["resumo"])
        gh.resp_422 = False

        volta_para_validacao()
        gh.posts.clear()
        pedido(m, "ap3.json", {"key": K, "acao": "aprovar", "por": "glauco", "em": 7})
        d.processa_fila()
        est = m.le_json(m.caminho_estado(K))
        e = erro_de(m, "ap3.json")
        P.confere("aprovar sem resumo e sem comentário: nada publicado, pedido recusado",
                  not gh.posts and e and "nada para publicar" in e.read_text() and est["etapa"] == "validacao"
                  and "falha ao publicar" in est["resumo"], e and e.read_text())

        pedido(m, "dv1.json", {"key": K, "acao": "devolver", "por": "glauco", "em": 8})
        d.processa_fila()
        P.confere("devolver sem comentário é recusado", erro_de(m, "dv1.json"))
        pedido(m, "dv2.json", {"key": K, "acao": "devolver", "por": "glauco", "em": 9, "comentario": "olhar o hook useX"})
        d.processa_fila()
        P.confere("devolver com comentário vira revisar de novo com foco",
                  (m.le_json(m.caminho_interno(K)).get("pendente") or {}).get("foco") == "olhar o hook useX")
        disparos = []
        m.subprocess.Popen = lambda cmd, **kw: (disparos.append(cmd), type("Pf", (), {"pid": 0, "poll": lambda s: None})())[1]
        d.agenda()
        est = m.le_json(m.caminho_estado(K))
        P.confere("revisar de novo: despachante leva a review e passa o foco no prompt",
                  est["etapa"] == "review" and disparos and "Foco pedido: olhar o hook useX" in disparos[-1][-1], est["etapa"])
        d.rodando.clear()
        m.transiciona(K, "validacao", "aguardando_humano")
        pedido(m, "dv3.json", {"key": K, "acao": "devolver", "por": "feda", "em": 10, "comentario": "Não publicar"})
        d.processa_fila()
        est = m.le_json(m.caminho_estado(K))
        P.confere("'Não publicar' conclui sem publicar", est["etapa"] == "concluido" and est["publicado"] is False)

        ok_l, msg_l = m.limpa_card(K, "glauco")
        P.confere("limpar remove o worktree do PR e a pasta do card", ok_l and not wt.exists() and not (m.CARDS / K).exists(),
                  msg_l)
        linha = json.loads(m.ARQUIVO.read_text().splitlines()[-1])
        P.confere("limpar registra o card no arquivo.jsonl", linha["key"] == K and linha["etapa_final"] == "concluido")


def outro_repo():
    with ambiente() as (m, T):
        GhFalso(m)
        K = "PR-leme-core-12"
        m.transiciona(K, "fila", "rodando", por_despachante=True, tipo="revisao_pr")
        m.atualiza_campos(K, repo="leme-core", numero=12)
        P.confere("worktree de outro repo fica em repos/<repo>/.worktrees", m.worktree(K) == m.ROOT / "repos/leme-core/.worktrees" / K)
        ok, msg = m.prepara_worktree_pr(K)
        clones = [c for c in m.subprocess.bloqueados if c[:2] == ["git", "clone"]]
        P.confere("repo ausente: o clone do GitHub é barrado no teste e o preparo falha com motivo",
                  not ok and "clone de leme-tech/leme-core falhou" in msg and len(clones) == 1, msg)


P.grupo("valida_pedido_pr", valida_pedido)
P.grupo("diff do PR", diff_do_pr)
P.grupo("fluxo completo da revisão", fluxo)
P.grupo("PR de outro repo", outro_repo)
P.fim()
