"""Jira (simulado): status segue a etapa, merge leva a Testando, flag e comentário do impedimento, vínculos Blocks."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, leva  # noqa: E402

P = Placar("test_jira")
NOME = {"10003": "Tarefas pendentes", "10008": "Desenvolvendo", "10007": "Revisando Código", "10005": "Testando"}


def status_segue_etapa():
    with ambiente() as (m, T):
        jira = {"LM-1": "10003", "LM-2": "10005"}
        movimentos, puts = [], []

        def jira_req(caminho, metodo="GET", corpo=None):
            key = caminho.split("/")[1].split("?")[0]
            if metodo == "GET":
                return {"fields": {"status": {"id": jira[key], "name": NOME[jira[key]]}}}
            if metodo == "PUT":
                puts.append((key, corpo))
                return {}
            alvo = {v: k for k, v in m.JIRA_TRANSICAO.items()}[corpo["transition"]["id"]]
            movimentos.append((key, jira[key], alvo))
            jira[key] = alvo
            return {}
        m.jira_req = jira_req
        m.pr_mergeado = lambda url: "2026-11-07T03:00:00Z"
        d = m.Despachante()

        def passo(k, etapa, **kw):
            m.transiciona(k, etapa, kw.pop("status", "rodando"), **kw)
            d.ultimo_merge = 0
            d.sincroniza_jira()
            return jira[k]

        K = "LM-1"
        leva(m, K, "triagem")
        seq = [("front", {}, "10008"), ("review", {}, "10007"), ("front", {"com_achados": True}, "10008"),
               ("review", {}, "10007"), ("qa", {}, "10007"), ("validacao", {"status": "aguardando_humano"}, "10007"),
               ("pr", {"por_despachante": True}, "10007"),
               ("concluido", {"status": "concluido", "pr_url": "https://github.com/x/pull/1"}, "10005")]
        obtidos = [(e, NOME[passo(K, e, **kw)]) for e, kw, _ in seq]
        esperados = [(e, NOME[s]) for e, _, s in seq]
        P.confere("Jira acompanha a etapa (concluído com PR mergeado vai a Testando)", obtidos == esperados, obtidos)
        P.confere("merge registrado no estado", m.le_json(m.caminho_estado(K)).get("merged_em") == "2026-11-07T03:00:00Z")
        n = len(movimentos)
        d.sincroniza_jira()
        P.confere("ciclo repetido não chama transição de novo", len(movimentos) == n)
        P.confere("5 transições no total (qa/validacao/pr já estavam em Revisando)", n == 5, movimentos)

        K2 = "LM-2"
        leva(m, K2, "triagem")
        passo(K2, "front")
        P.confere("card que o time já levou para Testando não é mexido",
                  not [x for x in movimentos if x[0] == K2]
                  and "não mexi: está em Testando" in (m.LOGS / "despachante.log").read_text())

        K3 = "LM-3"
        jira[K3] = "10008"
        leva(m, K3, "triagem")
        m.transiciona(K3, "inviavel", "aguardando_humano")
        it = m.le_json(m.caminho_interno(K3))
        m.escreve_json(m.caminho_interno(K3), {**it, "flag_por_esteira": True})
        d.sincroniza_jira()
        P.confere("inviável com flag da esteira: flag fica", not [p for p in puts if p[0] == K3])
        m.transiciona(K3, "fila", "rodando", por_despachante=True)
        m.transiciona(K3, "triagem", "rodando")
        m.transiciona(K3, "front", "rodando")
        d.sincroniza_jira()
        P.confere("saiu do inviável: a esteira tira a flag que ela pôs",
                  [p for p in puts if p[0] == K3] == [(K3, {"fields": {m.JIRA_CAMPO_FLAG: None}})]
                  and "flag_por_esteira" not in m.le_json(m.caminho_interno(K3)), puts)


def comentario_impedimento():
    with ambiente() as (m, T):
        K = "LM-2"
        leva(m, K, "triagem")
        (m.CARDS / K / "triagem.md").write_text(
            "# LM-2\n\n**Veredito:** INVIÁVEL\n\n## Impedimento\n**Tipo:** `backend-pendente`\n"
            "**Motivo:** o core não tem PATCH /questions/{id}/draft (procurei em routes/api.php na origin/main; épico LM-2800)\n"
            "**O que destrava:** endpoint no leme-core (LM-2856)\n")
        m.transiciona(K, "inviavel", "aguardando_humano", resumo="backend-pendente: ...")
        comentarios = []

        class Resp:
            status = 201
            def __enter__(s): return s
            def __exit__(s, *a): return False

        def urlopen(req, timeout=0):
            comentarios.append((req.full_url, req.get_method(), json.loads(req.data)))
            return Resp()
        m.urllib.request.urlopen = urlopen
        chamadas, links = [], []

        def jira_req(caminho, metodo="GET", corpo=None):
            chamadas.append((metodo, caminho, corpo))
            if metodo == "POST" and caminho == "issueLink":
                links.append({"type": {"name": "Blocks"}, "inwardIssue": corpo["inwardIssue"]})
                return {}
            if metodo == "PUT":
                return {}
            if caminho.startswith(f"issue/{K}?fields=issuelinks"):
                return {"fields": {"issuelinks": list(links)}}
            if caminho == "issue/LM-2856?fields=issuetype":
                return {"fields": {"issuetype": {"name": "Tarefa"}}}
            if caminho.startswith(f"issue/{K}/comment"):
                return {"comments": []}
            if caminho.startswith(f"issue/{K}?fields=description"):
                return {"fields": {"description": None, "status": {"id": "10008"}, "assignee": None,
                                   "issuelinks": list(links), m.JIRA_CAMPO_FLAG: [{"value": "Impediment"}]}}
            if caminho == "issue/LM-2856?fields=status":
                return {"fields": {"status": {"id": "10008"}}}
            raise AssertionError(f"chamada inesperada: {metodo} {caminho}")
        m.jira_req = jira_req
        d = m.Despachante()
        d.comenta_impedimento(K)
        P.confere("postou 1 comentário no card certo", len(comentarios) == 1
                  and comentarios[0][0].endswith("/issue/LM-2/comment") and comentarios[0][1] == "POST", comentarios)
        corpo = json.dumps(comentarios[0][2], ensure_ascii=False) if comentarios else ""
        P.confere("comentário tem tipo, motivo e o que destrava",
                  all(x in corpo for x in ("backend-pendente", "PATCH /questions", "browse/LM-2856")), corpo[:300])
        P.confere("comentário começa com 🤖 (a re-triagem ignora)", "🤖 Triagem automática" in corpo)
        P.confere("flag de impedimento ligada no Jira",
                  ("PUT", f"issue/{K}", {"fields": {m.JIRA_CAMPO_FLAG: [{"value": "Impediment"}]}}) in chamadas)
        post_links = [c[2] for c in chamadas if c[1] == "issueLink"]
        P.confere("vínculo só com o card do 'O que destrava' (não o épico do Motivo), bloqueador em inwardIssue",
                  post_links == [{"type": {"name": "Blocks"}, "inwardIssue": {"key": "LM-2856"},
                                  "outwardIssue": {"key": K}}], post_links)
        it = m.le_json(m.caminho_interno(K))
        P.confere("interno marca flag_por_esteira, comentário e foto com o bloqueador aberto",
                  it.get("flag_por_esteira") and it.get("comentario_inviavel_em")
                  and it.get("foto_inviavel", {}).get("bloqueios_abertos") == ["LM-2856"], it)
        n = len(comentarios)
        d.comenta_impedimento(K)
        P.confere("não repete o comentário na mesma triagem", len(comentarios) == n)


def comentario_falha():
    with ambiente() as (m, T):
        K = "LM-4"
        leva(m, K, "triagem")
        m.transiciona(K, "inviavel", "aguardando_humano", resumo="sem motivo no arquivo")
        chamadas = []
        m.jira_req = lambda c, metodo="GET", corpo=None: chamadas.append((metodo, c))
        m.Despachante().comenta_impedimento(K)  # urlopen bloqueado: o POST falha
        it = m.le_json(m.caminho_interno(K))
        P.confere("comentário falhou: sem flag, sem marca, tenta de novo depois",
                  not chamadas and "comentario_inviavel_em" not in it and "flag_por_esteira" not in it, (chamadas, it))
        P.confere("sem triagem.md: motivo vem do resumo", m.impedimento_de(K, m.le_json(m.caminho_estado(K)))["motivo"]
                  == "sem motivo no arquivo")


P.grupo("status do Jira segue a etapa", status_segue_etapa)
P.grupo("comentário do impedimento", comentario_impedimento)
P.grupo("comentário do impedimento: falha de rede", comentario_falha)
P.fim()
