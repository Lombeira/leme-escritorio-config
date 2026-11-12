"""Cards novos pelo escritório (confirmar_card) e sugestões do ouvidor (aprovar, ignorar, duplicada, descartar).
Tudo com fixtures criadas aqui; nada vem da .escritorio real."""
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente  # noqa: E402

P = Placar("test_novos_e_sugestoes")
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


def pedido(m, nome, dados):
    (m.FILA / nome).write_text(json.dumps(dados))


def erro_de(m, nome):
    return next(m.PROCESSADOS.glob(f"*-{nome}.erro"), None)


def jira_que_cria(enviados, key):
    def jira_req(caminho, metodo="GET", corpo=None):
        if caminho.startswith("search/jql"):
            return {"issues": [{"fields": {"customfield_10020": [{"id": 2073, "state": "active", "boardId": 2}]}}]}
        enviados.append((caminho, metodo, corpo))
        return {"key": key}
    return jira_req


def sugestao_fixture(m, sid, texto="A Letícia não acha o menu de transferência de turma"):
    pasta = m.SUGESTOES / sid
    pasta.mkdir(parents=True)
    (pasta / "print-1.png").write_bytes(PNG)
    m.escreve_json(pasta / "sugestao.json", {
        "id": sid, "canal": "suporte", "autor": "Fulana (SME)", "criado": 1794159357,
        "permalink": "https://leme.slack.com/archives/C000TESTE/p1794159357611118",
        "texto_original": texto, "ts_slack": "1794159357.611118",
        "sugestao": {"tipo": "bug", "titulo": "[Frontend] Turmas: transferência some", "descricao": "## Passos\n1. abrir",
                     "responsavel": "feda", "motivo": "relato de bug"},
        "duplicata_de": None, "duplicata_titulo": None, "prints": ["print-1.png", "../fora.png"]})
    m.escreve_json(pasta / "estado.json", {"status": "sugerida"})
    return pasta


def confirmar_card():
    with ambiente() as (m, T):
        NID = "n1794062000000a1b2"
        pasta = m.NOVOS / NID
        pasta.mkdir(parents=True)
        (pasta / "print.png").write_bytes(PNG)
        m.escreve_json(pasta / "pedido.json", {"texto": "relato", "imagens": ["print.png", "../x.png"]})
        rascunho = {"titulo": "[Frontend] Turmas: botão de salvar não responde",
                    "descricao": "## Contexto\nNo cadastro de turma o botão **Salvar** não faz nada.\n\n## Passos\n1. abrir\n2. salvar",
                    "tipo": "bug", "responsavel": "glauco"}
        m.escreve_json(pasta / "rascunho.json", rascunho)
        m.escreve_json(pasta / "final.json", {**rascunho, "por": "glauco", "em": 1})
        enviados, anexos = [], []
        m.jira_req = jira_que_cria(enviados, "LM-9999")

        class R:
            status = 200
            def __enter__(s): return s
            def __exit__(s, *a): return False
        m.anexa_arquivos = m.anexa_arquivos_real
        m.urllib.request.urlopen = lambda req, timeout=0: (anexos.append((req.full_url, dict(req.headers), req.data)), R())[1]
        pend = []
        m.atualiza_pendencias = lambda: (pend.append(1), (True, "13 cards"))[1]
        d = m.Despachante()
        pedido(m, "c1.json", {"acao": "confirmar_card", "novo": NID, "por": "glauco", "em": 2})
        d.processa_fila()
        est = m.le_json(pasta / "estado.json")
        P.confere("estado criado com key e url", est["status"] == "criado" and est["key"] == "LM-9999"
                  and est["url"] == "https://leme-tec.atlassian.net/browse/LM-9999", est)
        f = enviados[0][2]["fields"] if enviados else {}
        P.confere("POST em issue", enviados and enviados[0][:2] == ("issue", "POST"))
        P.confere("tipo Bug (10007)", f.get("issuetype") == {"id": "10007"})
        P.confere("responsável = accountId do Glauco", f.get("assignee", {}).get("accountId") == m.CONTA_JIRA["glauco"])
        P.confere("sprint ativa", f.get("customfield_10020") == 2073)
        P.confere("label pelo prefixo [Frontend]", f.get("labels") == ["frontend"])
        P.confere("título exato do humano", f.get("summary") == rascunho["titulo"])
        P.confere("descrição em ADF, com negrito", f.get("description", {}).get("type") == "doc"
                  and f["description"]["content"][0]["type"] == "heading"
                  and '"strong"' in json.dumps(f["description"]))
        hdr = {k.lower(): v for k, v in anexos[0][1].items()} if anexos else {}
        P.confere("só o print válido anexado (multipart, no-check)",
                  len(anexos) == 1 and anexos[0][0].endswith("/issue/LM-9999/attachments")
                  and hdr.get("x-atlassian-token") == "no-check" and b'filename="print.png"' in anexos[0][2]
                  and b"x.png" not in anexos[0][2], anexos and anexos[0][0])
        P.confere("pendências atualizadas", pend == [1])
        pedido(m, "c2.json", {"acao": "confirmar_card", "novo": NID, "por": "glauco", "em": 3})
        d.processa_fila()
        e = erro_de(m, "c2.json")
        P.confere("segundo confirmar é recusado (sem duplicar)", e and "já foi criado" in e.read_text() and len(enviados) == 1,
                  e and e.read_text().strip())
        (pasta / "descartado").write_text("")
        pedido(m, "c3.json", {"acao": "novo_card", "novo": NID, "por": "glauco", "em": 4})
        d.processa_fila()
        e = erro_de(m, "c3.json")
        P.confere("pasta descartada é ignorada", e and "descartado" in e.read_text())
        pedido(m, "c4.json", {"acao": "confirmar_card", "novo": "../cards", "por": "glauco", "em": 5})
        d.processa_fila()
        P.confere("id de pasta inválido é recusado", erro_de(m, "c4.json"))
        pedido(m, "c5.json", {"acao": "confirmar_card", "novo": NID, "por": "outro", "em": 6})
        d.processa_fila()
        P.confere("confirmar sem por válido é recusado", erro_de(m, "c5.json"))


def confirmar_sem_tipo_valido():
    with ambiente() as (m, T):
        NID = "n1794062000001"
        pasta = m.NOVOS / NID
        pasta.mkdir(parents=True)
        m.escreve_json(pasta / "final.json", {"titulo": "[Frontend] x", "descricao": "y", "tipo": "epico", "responsavel": "glauco"})
        enviados = []
        m.jira_req = jira_que_cria(enviados, "LM-1")
        pedido(m, "c.json", {"acao": "confirmar_card", "novo": NID, "por": "glauco", "em": 1})
        m.Despachante().processa_fila()
        est = m.le_json(pasta / "estado.json")
        P.confere("tipo inválido: estado erro, sem chamar o Jira", est["status"] == "erro" and not enviados
                  and "inválido" in est["motivo"], est)


def sugestoes():
    with ambiente() as (m, T):
        (m.ROOT / "memory").mkdir(parents=True)
        (m.ROOT / "memory" / "MEMORY.md").write_text("# Memory Index\n")
        s1 = sugestao_fixture(m, "s1794159357611118822")
        s2 = sugestao_fixture(m, "s1794159400000000abc")
        enviados, anexos = [], []
        m.jira_req = jira_que_cria(enviados, "LM-9998")
        m.anexa_arquivos = lambda key, arqs: anexos.append((key, [a.name for a in arqs]))
        d = m.Despachante()
        pedido(m, "a.json", {"acao": "sugestao_aprovar", "sugestao": s1.name, "titulo": "TÍTULO EDITADO",
                             "descricao": "## Passos\n1. abrir", "tipo": "bug", "responsavel": "feda", "por": "glauco", "em": 1})
        d.processa_fila()
        est = m.le_json(s1 / "estado.json")
        f = enviados[0][2]["fields"] if enviados else {}
        P.confere("aprovar: criado com key e url", est["status"] == "criado" and est["key"] == "LM-9998", est)
        P.confere("título exato do pedido", f.get("summary") == "TÍTULO EDITADO")
        texto = json.dumps(f.get("description"), ensure_ascii=False)
        P.confere("origem do Slack com link na descrição", "Slack #suporte" in texto and '"type": "link"' in texto
                  and "p1794159357611118" in texto)
        P.confere("só o print de dentro da pasta é anexado", anexos == [("LM-9998", ["print-1.png"])], anexos)
        P.confere("sprint ativa e responsável", f.get("customfield_10020") == 2073
                  and f.get("assignee", {}).get("accountId") == m.CONTA_JIRA["feda"])
        pedido(m, "b.json", {"acao": "sugestao_aprovar", "sugestao": s1.name, "titulo": "x", "descricao": "y", "tipo": "bug",
                             "responsavel": "feda", "por": "glauco", "em": 2})
        d.processa_fila()
        P.confere("aprovar de novo é recusado (sem duplicar card)", erro_de(m, "b.json") and len(enviados) == 1)
        pedido(m, "c.json", {"acao": "sugestao_ignorar", "sugestao": s2.name, "comentario": "transferência já resolvida no LM-2847",
                             "por": "feda", "em": 3})
        d.processa_fila()
        mem = m.MEMORIA_OUVIDOR.read_text()
        P.confere("ignorar: estado e motivo", m.le_json(s2 / "estado.json")
                  == {"status": "ignorada", "motivo": "transferência já resolvida no LM-2847"})
        P.confere("motivo na memória, sem o texto da mensagem",
                  "transferência já resolvida" in mem and "Letícia" not in mem and "menu" not in mem.split("**How to apply:**")[1], mem)
        P.confere("memória indexada no MEMORY.md uma vez",
                  (m.ROOT / "memory" / "MEMORY.md").read_text().count("ouvidor-o-que-nao-sugerir") == 1)
        s3 = sugestao_fixture(m, "s1794155999999dupl")
        pedido(m, "s.json", {"acao": "sugestao_ignorar", "sugestao": s3.name, "comentario": "  ", "por": "feda", "em": 4})
        d.processa_fila()
        P.confere("ignorar sem motivo é recusado", erro_de(m, "s.json") and m.le_json(s3 / "estado.json")["status"] == "sugerida")
        n_antes = len(enviados)
        pedido(m, "d.json", {"acao": "sugestao_duplicada", "sugestao": s3.name, "key": "LM-2847", "por": "glauco", "em": 5})
        d.processa_fila()
        est = m.le_json(s3 / "estado.json")
        P.confere("duplicada: estado com key e url, sem comentar (opção desligada)",
                  est == {"status": "duplicada", "key": "LM-2847", "url": "https://leme-tec.atlassian.net/browse/LM-2847"}
                  and len(enviados) == n_antes, est)
        s4 = sugestao_fixture(m, "s1794155999999dup2")
        m.escreve_json(m.CONFIG_ESTEIRA, {"comentar_duplicata": True})
        pedido(m, "e.json", {"acao": "sugestao_duplicada", "sugestao": s4.name, "key": "LM-2847", "por": "glauco", "em": 6})
        d.processa_fila()
        P.confere("duplicada com comentar_duplicata: comenta no card existente",
                  enviados[-1][:2] == ("issue/LM-2847/comment", "POST"), enviados[-1][:2])
        s5 = sugestao_fixture(m, "s1794155999999dup3")
        pedido(m, "f.json", {"acao": "sugestao_duplicada", "sugestao": s5.name, "key": "OUTRO-1", "por": "glauco", "em": 7})
        d.processa_fila()
        P.confere("duplicada com key fora do LM é recusada", erro_de(m, "f.json"))
        pedido(m, "g.json", {"acao": "sugestao_aprovar", "sugestao": "../sugestoes", "titulo": "x", "descricao": "y",
                             "por": "glauco", "em": 8})
        d.processa_fila()
        P.confere("id de sugestão inválido é recusado", erro_de(m, "g.json"))


def descartar():
    with ambiente() as (m, T):
        s = sugestao_fixture(m, "s1794159357611118822")
        d = m.Despachante()
        pedido(m, "a.json", {"acao": "sugestao_descartar", "sugestao": s.name, "por": "glauco", "em": 1})
        d.processa_fila()
        P.confere("descartar: estado descartada, sem comentário", m.le_json(s / "estado.json")
                  == {"status": "descartada", "comentario": None})
        P.confere("descartar não ensina o ouvidor (memória não criada)", not m.MEMORIA_OUVIDOR.exists())
        pedido(m, "b.json", {"acao": "sugestao_ignorar", "sugestao": s.name, "comentario": "x", "por": "glauco", "em": 2})
        d.processa_fila()
        P.confere("ignorar depois de descartar é recusado", erro_de(m, "b.json")
                  and "já resolvida (descartada)" in erro_de(m, "b.json").read_text())
        P.confere("memória continua sem nada", not m.MEMORIA_OUVIDOR.exists())


P.grupo("confirmar card novo", confirmar_card)
P.grupo("confirmar card com tipo inválido", confirmar_sem_tipo_valido)
P.grupo("sugestões: aprovar, ignorar, duplicada", sugestoes)
P.grupo("sugestões: descartar", descartar)
P.fim()
