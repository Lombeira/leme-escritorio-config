"""Cards criados pela esteira no Jira (simulado): quebra.json da triagem e depois.json do card concluído."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente  # noqa: E402

P = Placar("test_quebra_depois")
CAMPOS_ORIG = {"issuetype": {"id": "10004"}, "parent": {"key": "LM-9"}, "labels": ["frontend"],
               "assignee": {"accountId": "acc-feda"}, "priority": {"name": "Medium"},
               "customfield_10020": [{"id": 2073, "state": "active"}],
               "description": {"type": "doc", "version": 1,
                               "content": [{"type": "paragraph", "content": [{"type": "text", "text": "original"}]}]}}


def card(m, key, etapa):
    m.escreve_json(m.CARDS / key / "estado.json", {**m.estado_novo(key), "etapa": etapa})
    m.escreve_json(m.CARDS / key / ".interno.json", {})


def criados(chamadas):
    return [c for c in chamadas if c[0] == "POST" and c[1] == "issue"]


def quebra():
    with ambiente() as (m, T):
        card(m, "LM-1", "front")
        chamadas, n, falhar = [], [100], {"em": None}

        def jira_req(caminho, metodo="GET", corpo=None):
            chamadas.append((metodo, caminho, corpo))
            if falhar["em"] is not None and metodo == "POST" and caminho == "issue" and len(criados(chamadas)) == falhar["em"]:
                falhar["em"] = None
                chamadas.pop()
                raise RuntimeError("Jira caiu")
            if metodo == "GET":
                return {"fields": CAMPOS_ORIG}
            if metodo == "POST" and caminho == "issue":
                n[0] += 1
                return {"key": f"LM-{n[0]}"}
            return {}
        m.jira_req = jira_req
        desc = "## O que fazer\n- drawer X com o texto exato do card\n\n## Critérios de aceite\n- Dado A, então B.\n- Dado C, então D."
        q = {"este_card": "base e visão Turmas (critérios 1 a 12)", "partes": [
            {"id": "p2", "titulo": "[Frontend] Tema: drawer da turma", "depende_de": ["este"], "descricao": desc},
            {"id": "p3", "titulo": "[Frontend] Tema: drawer da habilidade", "depende_de": ["p2"], "descricao": desc},
            {"id": "p4", "titulo": "[Frontend] Tema: aba Alunos", "depende_de": ["este"], "descricao": desc}]}
        d = m.Despachante()
        (m.CARDS / "LM-1" / "quebra.json").write_text(json.dumps(q))
        falhar["em"] = 2
        d.processa_quebras()
        P.confere("Jira cai no meio: 1 criado, sem concluir",
                  len(criados(chamadas)) == 1 and not m.le_json(m.caminho_interno("LM-1"))["quebra"].get("concluida"))
        d.processa_quebras()
        cs = criados(chamadas)
        P.confere("retoma sem duplicar: 3 cards no total", len(cs) == 3, len(cs))
        f = cs[0][2]["fields"]
        P.confere("parte herda tipo, épico, responsável, label, prioridade e sprint",
                  f["issuetype"]["id"] == "10004" and f["parent"]["key"] == "LM-9" and f["assignee"]["accountId"] == "acc-feda"
                  and f["labels"] == ["frontend"] and f["customfield_10020"] == 2073 and f["priority"]["name"] == "Medium", f)
        txt = json.dumps(f["description"], ensure_ascii=False)
        P.confere("descrição da parte cita o original como link e traz o texto",
                  "browse/LM-1" in txt and "drawer X com o texto exato" in txt)
        put = [c for c in chamadas if c[0] == "PUT"]
        nota = json.dumps(put[0][2]["fields"]["description"], ensure_ascii=False) if put else ""
        P.confere("original anotado uma vez, parte 1 de 4, original preservado",
                  len(put) == 1 and "parte 1 de 4" in nota and '"original"' in nota and "browse/LM-102" in nota
                  and 'browse/LM-1"' not in nota)
        pares = sorted((x["inwardIssue"]["key"], x["outwardIssue"]["key"]) for x in (c[2] for c in chamadas if c[1] == "issueLink"))
        P.confere("vínculos: LM-1 bloqueia p2 e p4, p2 bloqueia p3",
                  pares == sorted([("LM-1", "LM-101"), ("LM-101", "LM-102"), ("LM-1", "LM-103")]), pares)
        P.confere("estado mostra as partes", [p["key"] for p in m.le_json(m.caminho_estado("LM-1"))["quebra"]]
                  == ["LM-101", "LM-102", "LM-103"])
        antes = len(chamadas)
        d.processa_quebras()
        P.confere("rodar de novo não faz nada", len(chamadas) == antes)
        for ruim, nome in ((dict(q, partes=[dict(q["partes"][0], titulo="sem prefixo")]), "título sem [Frontend]"),
                           (dict(q, partes=[dict(q["partes"][0], depende_de=["p9"])]), "dependência inexistente"),
                           (dict(q, partes=[dict(q["partes"][0], descricao="curta")]), "descrição curta"),
                           (dict(q, partes=q["partes"] * 2), "partes demais")):
            (m.CARDS / "LM-1" / "quebra.json").write_text(json.dumps(ruim))
            m.escreve_json(m.caminho_interno("LM-1"), {})
            antes = len(chamadas)
            logs_antes = (m.LOGS / "despachante.log").read_text().count("quebra recusada")
            d.processa_quebras()
            d.processa_quebras()
            logs = (m.LOGS / "despachante.log").read_text().count("quebra recusada")
            P.confere(f"recusa {nome} sem chamar o Jira, e loga uma vez", len(chamadas) == antes and logs - logs_antes == 1,
                      (len(chamadas) - antes, logs - logs_antes))


def depois():
    with ambiente() as (m, T):
        card(m, "LM-1", "validacao")
        ch, n = [], [200]

        def jira_req(c, metodo="GET", corpo=None):
            ch.append((metodo, c, corpo))
            if metodo == "GET":
                return {"fields": CAMPOS_ORIG}
            if c == "issue":
                n[0] += 1
                return {"key": f"LM-{n[0]}"}
            return {}
        m.jira_req = jira_req
        pend = []
        m.atualiza_pendencias = lambda: (pend.append(1), (True, "ok"))[1]
        desc = "## O que fazer\n- corrigir o parser em scripts/lib/x.ts:6 como o review sugeriu\n\n## Critérios de aceite\n- Dado A, então B."
        (m.CARDS / "LM-1" / "depois.json").write_text(json.dumps({"cards": [
            {"titulo": "[Frontend] Tema: corrigir parser", "descricao": desc},
            {"titulo": "[Frontend] Tema: aviso", "descricao": desc, "depende_deste": False}]}))
        d = m.Despachante()
        d.processa_depois()
        P.confere("em validação ainda não cria nada", not ch)
        m.atualiza_campos("LM-1", etapa="concluido")
        d.processa_depois()
        P.confere("concluído sem PR também não cria", not ch)
        m.atualiza_campos("LM-1", pr_url="https://github.com/x/pull/1")
        d.processa_depois()
        cs = [c for c in ch if c[1] == "issue"]
        links = [c[2] for c in ch if c[1] == "issueLink"]
        P.confere("concluído com PR: cria os 2 cards", len(cs) == 2, len(cs))
        P.confere("herda os campos do original", cs and cs[0][2]["fields"]["parent"]["key"] == "LM-9"
                  and cs[0][2]["fields"]["customfield_10020"] == 2073)
        P.confere("descrição diz de onde veio", cs and "Ficou para depois no" in json.dumps(cs[0][2]["fields"]["description"],
                                                                                          ensure_ascii=False))
        P.confere("só o que depende ganha vínculo (LM-1 bloqueia LM-201)",
                  [(x["inwardIssue"]["key"], x["outwardIssue"]["key"]) for x in links] == [("LM-1", "LM-201")], links)
        P.confere("estado lista os cards criados", [c["key"] for c in m.le_json(m.caminho_estado("LM-1"))["depois"]]
                  == ["LM-201", "LM-202"])
        P.confere("pendências atualizadas depois de criar", pend == [1])
        antes = len(ch)
        d.processa_depois()
        P.confere("não duplica", len(ch) == antes)
        m.escreve_json(m.caminho_interno("LM-1"), {})
        (m.CARDS / "LM-1" / "depois.json").write_text(json.dumps({"cards": [{"titulo": "sem prefixo", "descricao": desc}]}))
        antes = len(ch)
        d.processa_depois()
        d.processa_depois()
        log = (m.LOGS / "despachante.log").read_text()
        P.confere("inválido é recusado sem chamar o Jira, loga uma vez", len(ch) == antes and log.count("para depois recusados") == 1)
        P.confere("valida_depois: mais de 4 cards", m.valida_depois({"cards": [{"titulo": "[Frontend] xxxxx", "descricao": desc}] * 5})
                  == "mais de 4 cards")


P.grupo("quebra de card grande", quebra)
P.grupo("o que ficou para depois", depois)
P.fim()
