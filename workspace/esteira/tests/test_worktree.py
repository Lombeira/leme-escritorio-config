"""Worktree do card em repositórios git temporários (origin local, sem push): foto dos versionados, nome da branch,
preparo do worktree (pnpm simulado) e atualização na re-triagem."""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, commit, git, identidade, repo_com_origin  # noqa: E402

P = Placar("test_worktree")


def pnpm_falso(m, chamadas, rc=0):
    real = m.subprocess.run

    def run(cmd, *a, **k):
        if cmd[:1] == ["pnpm"]:
            chamadas.append((cmd, k.get("cwd")))
            return subprocess.CompletedProcess(cmd, rc, stdout="", stderr="")
        return real(cmd, *a, **k)
    m.subprocess.run = run


def foto():
    with ambiente() as (m, T):
        wt = m.WORKTREES / "K"
        wt.mkdir(parents=True)
        git("-C", wt, "init", "-q")
        identidade(wt)
        (wt / ".gitignore").write_text("node_modules/\n")
        commit(wt, "a.ts", "x\n", "a")
        (wt / ".git/info/exclude").write_text("test-results/\nplaywright-report/\n")
        base = m.foto_versionados("K")
        P.confere("foto existe para worktree presente", base and base.count(":") == 2, base)
        P.confere("sem worktree: foto None", m.foto_versionados("NAO-EXISTE") is None)

        def caso(nome, faz, desfaz, deve_mudar):
            faz()
            mudou = m.foto_versionados("K") != base
            desfaz()
            P.confere(nome, mudou == deve_mudar, "muda a foto" if mudou else "foto igual")
        caso("arquivo NOVO não versionado muda a foto", lambda: (wt / "novo.ts").write_text("y"),
             lambda: (wt / "novo.ts").unlink(), True)
        caso("edição em arquivo versionado muda a foto", lambda: (wt / "a.ts").write_text("z\n"),
             lambda: (wt / "a.ts").write_text("x\n"), True)
        for pasta, arq, por in (("test-results", "r.json", "exclude"), ("playwright-report", "i.html", "exclude"),
                                ("node_modules", "p.js", ".gitignore")):
            caso(f"artefato em {pasta}/ ({por}) não muda a foto",
                 lambda: ((wt / pasta).mkdir(), (wt / pasta / arq).write_text("{}")), lambda: shutil.rmtree(wt / pasta), False)
        P.confere("foto volta a ser a mesma depois de desfazer", m.foto_versionados("K") == base)

        leva_k = "K"
        m.transiciona(leva_k, "fila", "rodando", por_despachante=True)
        m.transiciona(leva_k, "triagem", "rodando")
        (wt / "a.ts").write_text("editado pela triagem\n")
        try:
            m.transiciona(leva_k, "front", "rodando")
            recusou = False
        except m.TransicaoInvalida as e:
            recusou = "alterou arquivos versionados" in str(e)
        est = m.le_json(m.caminho_estado(leva_k))
        P.confere("triagem que edita versionado: transição recusada e card vai para erro",
                  recusou and est["etapa"] == "erro", est["resumo"])


def nome_branch():
    with ambiente() as (m, T):
        casos = [("LM-2857", "Renomear agentes de review do leme-app para reviewer e review-validator",
                  "LM-2857-renomear-agentes-de-review-do-leme-app"),
                 ("LM-2834", "[Frontend] Campo de deficiência intelectual", "LM-2834-frontend-campo-de-deficiencia"),
                 ("LM-1", "Ação rápida", "LM-1-acao-rapida"),
                 ("LM-2", "", "LM-2"),
                 ("LM-3", "a" * 60, "LM-3-" + "a" * 40)]
        for key, summary, esperado in casos:
            obtido = m.nome_branch(key, summary)
            P.confere(f"nome_branch({key}, {summary[:30]!r}) = {esperado}", obtido == esperado, obtido)


def prepara():
    with ambiente() as (m, T):
        origin = T / "origin-app"
        origin.mkdir()
        git("-C", origin, "init", "-q", "-b", "main")
        commit(origin, ".env.example", "VITE_APP_LEME_API_URL=https://api\nVITE_APP_AMPLITUDE_KEY=segredo\n", "1")
        m.REPO_APP.parent.mkdir(parents=True)
        git("clone", "-q", origin, m.REPO_APP)
        commit(origin, "b.txt", "2", "2")  # o clone fica atrás: o preparo precisa do fetch
        K = "TESTE-W"
        m.transiciona(K, "fila", "rodando", summary="Teste de worktree da esteira", por_despachante=True)
        chamadas = []
        pnpm_falso(m, chamadas)
        ok, msg = m.prepara_worktree(K)
        wt = m.worktree(K)
        P.confere("preparo ok", ok, msg)
        P.confere("HEAD == origin/main (depois do fetch)", ok and git("-C", wt, "rev-parse", "HEAD") == git("-C", origin, "rev-parse", "main"))
        P.confere("branch pelo summary", ok and git("-C", wt, "branch", "--show-current") == "TESTE-W-teste-de-worktree-da-esteira")
        P.confere("estado.branch gravado", m.le_json(m.caminho_estado(K)).get("branch") == "TESTE-W-teste-de-worktree-da-esteira")
        exclude = (m.REPO_APP / ".git/info/exclude").read_text()
        P.confere("artefatos de teste no info/exclude", "test-results/" in exclude and "playwright-report/" in exclude)
        env = (wt / ".env").read_text() if ok else ""
        P.confere(".env gerado do .env.example sem a chave do Amplitude",
                  "VITE_APP_LEME_API_URL=https://api" in env and "VITE_APP_AMPLITUDE_KEY=\n" in env and "segredo" not in env, env)
        P.confere("pnpm install --frozen-lockfile no worktree", chamadas == [(["pnpm", "install", "--frozen-lockfile"], wt)], chamadas)
        P.confere("worktree limpo além do .env gerado",
                  ok and set(git("-C", wt, "status", "--porcelain").split()) <= {"??", ".env"})
        ok2, msg2 = m.prepara_worktree(K)
        P.confere("2ª chamada reaproveita", ok2 and "reaproveitado" in msg2, msg2)

        K2 = "TESTE-X"
        m.transiciona(K2, "fila", "rodando", summary="outra", por_despachante=True)
        git("-C", m.REPO_APP, "branch", "TESTE-X-outra")
        ok3, msg3 = m.prepara_worktree(K2)
        P.confere("branch já existe sem worktree: não reaproveita sozinho", not ok3 and "já existe sem worktree" in msg3, msg3)

        K3 = "TESTE-Y"
        m.transiciona(K3, "fila", "rodando", summary="pnpm quebra", por_despachante=True)
        pnpm_falso(m, [], rc=1)
        ok4, msg4 = m.prepara_worktree(K3)
        P.confere("pnpm install falhou: preparo falha com motivo", not ok4 and "pnpm install" in msg4, msg4)
        P.confere("segundo worktree não duplica o exclude", (m.REPO_APP / ".git/info/exclude").read_text().count("test-results/") == 1)

        git("-C", m.REPO_APP, "remote", "set-url", "origin", T / "nao-existe")
        K4 = "TESTE-Z"
        m.transiciona(K4, "fila", "rodando", summary="sem rede", por_despachante=True)
        ok5, msg5 = m.prepara_worktree(K4)
        P.confere("fetch falhou: preparo falha antes de criar worktree", not ok5 and "fetch" in msg5 and not m.worktree(K4).exists(), msg5)


def retriagem():
    with ambiente() as (m, T):
        O, R = repo_com_origin(T)
        W = T / "wt"
        git("-C", R, "worktree", "add", "-q", "-b", "card", W, "origin/main")
        identidade(W)
        commit(O, "a.txt", "2", "2")
        m.worktree = lambda key: W
        r = m.atualiza_worktree_triagem("LM-1")
        P.confere("worktree limpo: ff para origin/main", r == "atualizado para origin/main" and (W / "a.txt").read_text() == "2", r)
        commit(O, "package.json", "{}", "deps")
        chamadas = []
        pnpm_falso(m, chamadas)
        r = m.atualiza_worktree_triagem("LM-1")
        P.confere("mudou package.json: ff e pnpm install", r == "atualizado para origin/main" and len(chamadas) == 1, (r, chamadas))
        commit(O, "a.txt", "3", "3")
        commit(W, "b.txt", "x", "local")
        r = m.atualiza_worktree_triagem("LM-1")
        P.confere("worktree com commit próprio: não mexe", r.startswith("worktree tem commit próprio") and (W / "a.txt").read_text() == "2", r)
        (W / "b.txt").write_text("y")
        r = m.atualiza_worktree_triagem("LM-1")
        P.confere("worktree com mudança: não mexe", r.startswith("worktree com mudança"), r)


def versao_node():
    with ambiente() as (m, T):
        wt = T / "wt"
        wt.mkdir()
        P.confere("sem .nvmrc: versão padrão da esteira", m.versao_node(wt) == m.NODE_PADRAO)
        (wt / ".node-version").write_text("v22.1.0\n")
        P.confere(".node-version sem o v", m.versao_node(wt) == "22.1.0")
        (wt / ".nvmrc").write_text("24\n")
        P.confere(".nvmrc tem prioridade", m.versao_node(wt) == "24")


P.grupo("foto dos versionados", foto)
P.grupo("nome da branch", nome_branch)
P.grupo("prepara_worktree", prepara)
P.grupo("atualiza_worktree_triagem", retriagem)
P.grupo("versão do Node do worktree", versao_node)
P.fim()
