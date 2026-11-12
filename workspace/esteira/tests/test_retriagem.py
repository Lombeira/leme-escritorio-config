"""Re-triagem dos inviáveis (checa_inviaveis) contra um Jira simulado: flag, comentários, responsável e bloqueadores."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, recusa  # noqa: E402

P = Placar("test_retriagem")
VEREDITO = 1794000000
GLAUCO = {"accountId": "712020:a024ec0f-673e-4078-b1d0-24d95e1a9157", "displayName": "Glauco"}
FEDA = {"accountId": "70121:1c6ec806-32f9-4739-b34e-674ab9d6b852", "displayName": "Fernanda Guerra"}
GUSTAVO = {"accountId": "999:gustavo", "displayName": "Gustavo Faino"}


def adf(t):
    return {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": t}]}]}


def com(i, quem, texto, quando="2026-11-07T10:00:00.000-0300"):
    return {"id": i, "author": {"displayName": quem}, "body": adf(texto), "created": quando, "updated": quando}


class Cenario:
    def __init__(self, m):
        self.m, self.JIRA, self.OUTROS = m, {}, {}
        m.jira_req = self.jira_req
        self.d = m.Despachante()

    def jira_req(self, caminho, metodo="GET", corpo=None):
        key = caminho.split("/")[1].split("?")[0]
        if key not in self.JIRA:
            return {"fields": {"status": {"id": self.OUTROS.get(key, "10008")}}}
        j = self.JIRA[key]
        if "/comment" in caminho:
            return {"comments": j["coms"]}
        nome = {"10005": "Testando", "10006": "Aguardando Release"}.get(j["status"], "Desenvolvendo")
        return {"fields": {"description": adf(j["desc"]), "status": {"id": j["status"], "name": nome},
                           "assignee": j.get("resp"),
                           "issuelinks": [{"type": {"name": "Blocks"}, "inwardIssue": {"key": b}} for b in j.get("bloq", [])],
                           self.m.JIRA_CAMPO_FLAG: [{"value": "Impediment"}] if j["flag"] else None}}

    def card(self, key, com_foto=True):
        m = self.m
        p = m.CARDS / key
        p.mkdir()
        m.escreve_json(p / "estado.json", {**m.estado_novo(key, "teste"), "etapa": "inviavel", "status": "aguardando_humano",
                                           "historico": [{"etapa": "inviavel", "em": VEREDITO}]})
        (p / "triagem.md").write_text("Veredito: INVIÁVEL\n**Motivo:** falta endpoint X\n")
        self.JIRA[key] = {"desc": "Descrição original\nlinha 2", "status": "10008", "flag": True,
                          "coms": [com("1", "Leme bot", "🤖 Triagem automática da esteira Leme: este card não pode seguir agora.")]}
        m.escreve_json(p / ".interno.json", {"flag_por_esteira": True})
        if com_foto:
            self.d.fotografa_inviavel(key)

    def roda(self):
        self.d.ultima_retriagem = 0
        self.d.checa_inviaveis()

    def etapa(self, k):
        return self.m.le_json(self.m.caminho_estado(k))["etapa"]

    def interno(self, k):
        return self.m.le_json(self.m.caminho_interno(k))

    def mexe_foto(self, k, fn):
        iv = self.interno(k)
        fn(iv["foto_inviavel"])
        self.m.escreve_json(self.m.caminho_interno(k), iv)


def flag_e_comentarios():
    with ambiente() as (m, T):
        c = Cenario(m)
        c.card("LM-1")
        P.confere("foto guardada no veredito", c.interno("LM-1").get("foto_inviavel", {}).get("flag") is True)
        c.roda()
        P.confere("sem mudança: continua inviável", c.etapa("LM-1") == "inviavel")
        c.JIRA["LM-1"]["coms"].append(com("2", "Leme bot", "🤖 Triagem automática: outro impedimento"))
        c.roda()
        P.confere("comentário da esteira (🤖) não dispara", c.etapa("LM-1") == "inviavel")
        c.JIRA["LM-1"]["coms"].append(com("3", "Fernanda Guerra", "Contexto: o endpoint X está sendo feito."))
        c.JIRA["LM-1"]["desc"] = "Descrição original\nlinha 2 com a regra definida"
        c.roda()
        P.confere("comentário humano + descrição, com flag: não dispara", c.etapa("LM-1") == "inviavel")
        c.JIRA["LM-1"]["coms"].append(com("4", "Glauco", "Endpoint X em homolog.", "2026-11-08T10:00:00.000-0300"))
        c.roda()
        P.confere("segundo comentário, flag ainda lá: não dispara", c.etapa("LM-1") == "inviavel")
        c.JIRA["LM-1"]["flag"] = False
        c.roda()
        it, mud = c.interno("LM-1"), (m.CARDS / "LM-1" / "mudancas.md").read_text()
        P.confere("flag tirada dispara a re-triagem", c.etapa("LM-1") == "fila" and it["pendente"]["acao"] == "triagem"
                  and it["pendente"]["por"] == "esteira")
        P.confere("mudancas.md acumula os 2 comentários e o diff, sem o do robô",
                  "sendo feito" in mud and "Endpoint X em homolog" in mud and "+linha 2 com a regra definida" in mud
                  and "outro impedimento" not in mud, mud[:400])
        P.confere("triagem anterior preservada",
                  (m.CARDS / "LM-1" / "triagem-anterior.md").read_text().startswith("Veredito: INVIÁVEL"))
        resumo = m.le_json(m.caminho_estado("LM-1"))["resumo"]
        P.confere("resumo diz o que mudou", "flag de impedimento tirada" in resumo and "2 comentário(s)" in resumo, resumo)

        c.card("LM-2")
        c.JIRA["LM-2"]["flag"] = False
        c.roda()
        P.confere("só flag tirada (sem comentário) dispara", c.etapa("LM-2") == "fila")
        P.confere("mudancas.md explica que flag não libera sozinha",
                  "não** libera o card sozinho" in (m.CARDS / "LM-2" / "mudancas.md").read_text())

        c.card("LM-5", com_foto=False)
        c.JIRA["LM-5"]["coms"].append(com("5", "Glauco", "antes do veredito", "2026-11-01T10:00:00.000-0300"))
        c.JIRA["LM-5"]["coms"].append(com("6", "Glauco", "depois do veredito", "2026-11-08T10:00:00.000-0300"))
        c.roda()
        P.confere("sem foto e com flag: não dispara, base fica no veredito", c.etapa("LM-5") == "inviavel")
        c.JIRA["LM-5"]["flag"] = False
        c.roda()
        mud = (m.CARDS / "LM-5" / "mudancas.md").read_text()
        P.confere("sem foto: flag tirada dispara com só os comentários de depois do veredito",
                  c.etapa("LM-5") == "fila" and "depois do veredito" in mud and "antes do veredito" not in mud)


def resolvido_fora_e_intervalo():
    with ambiente() as (m, T):
        c = Cenario(m)
        c.card("LM-7")
        c.JIRA["LM-7"]["status"] = "10005"
        c.JIRA["LM-7"]["flag"] = False
        c.roda()
        P.confere("card levado para Testando no Jira vira concluido (resolvido fora)",
                  c.etapa("LM-7") == "concluido"
                  and "resolvido fora da esteira (Jira: Testando)" in m.le_json(m.caminho_estado("LM-7"))["resumo"])
        c.card("LM-9")
        c.JIRA["LM-9"]["status"] = "10006"
        c.roda()
        P.confere("Aguardando Release também, mesmo com a flag ainda lá", c.etapa("LM-9") == "concluido")
        c.card("LM-10")
        P.confere("agente não consegue concluir inviável", recusa(m, "LM-10", "concluido", "concluido", resumo="x"))
        c.card("LM-8")
        c.JIRA["LM-8"]["flag"] = False
        c.d.ultima_retriagem = m.agora()
        c.d.checa_inviaveis()
        P.confere("dentro do intervalo não consulta de novo", c.etapa("LM-8") == "inviavel")
        m.escreve_json(m.CONFIG_ESTEIRA, {"retriagem_horas": 0})
        c.roda()
        P.confere("retriagem_horas 0 desliga", c.etapa("LM-8") == "inviavel")
        m.CONFIG_ESTEIRA.unlink()
        it = c.interno("LM-8")
        m.escreve_json(m.caminho_interno("LM-8"), {**it, "pendente": {"acao": "triagem", "por": "glauco", "em": 1}})
        c.roda()
        P.confere("inviável com pedido pendente não é re-triado por cima", c.etapa("LM-8") == "inviavel")


def responsavel():
    with ambiente() as (m, T):
        c = Cenario(m)
        c.card("LM-20")
        c.JIRA["LM-20"]["resp"] = GUSTAVO
        c.JIRA["LM-20"]["flag"] = False
        c.roda()
        P.confere("responsável mudou para alguém de fora: não re-tria", c.etapa("LM-20") == "inviavel")
        c.roda()
        c.roda()
        logs = (m.LOGS / "despachante.log").read_text()
        P.confere("avisa no log uma vez só", logs.count("LM-20: re-triagem pulada") == 1, logs.count("LM-20: re-triagem pulada"))
        c.JIRA["LM-20"]["resp"] = FEDA
        c.roda()
        P.confere("voltou para alguém da esteira: re-tria", c.etapa("LM-20") == "fila")
        c.card("LM-21")
        c.JIRA["LM-21"]["resp"] = GLAUCO
        c.mexe_foto("LM-21", lambda f: f.update(assignee=None))
        c.JIRA["LM-21"]["resp"] = FEDA
        c.JIRA["LM-21"]["flag"] = False
        c.roda()
        P.confere("troca entre Glauco e Feda: re-tria normal", c.etapa("LM-21") == "fila")
        c.card("LM-22")
        c.JIRA["LM-22"]["resp"] = GUSTAVO
        c.mexe_foto("LM-22", lambda f: f.pop("assignee"))
        c.roda()
        P.confere("foto antiga sem responsável: base vira o atual, sem pular",
                  c.interno("LM-22")["foto_inviavel"]["assignee"] == "999:gustavo" and c.etapa("LM-22") == "inviavel")
        c.JIRA["LM-22"]["flag"] = False
        c.roda()
        P.confere("já era de fora no veredito e tirou a flag: re-tria (não mudou)", c.etapa("LM-22") == "fila")


def bloqueadores():
    with ambiente() as (m, T):
        c = Cenario(m)
        c.card("LM-30")
        c.JIRA["LM-30"]["bloq"] = ["LM-500", "LM-501"]
        c.OUTROS.update({"LM-500": "10008", "LM-501": "10007"})
        c.d.fotografa_inviavel("LM-30")
        P.confere("foto registra os bloqueios abertos", c.interno("LM-30")["foto_inviavel"]["bloqueios_abertos"]
                  == ["LM-500", "LM-501"])
        c.OUTROS["LM-500"] = "10005"
        c.roda()
        P.confere("só um dos dois resolvido: não dispara", c.etapa("LM-30") == "inviavel")
        c.OUTROS["LM-501"] = "10006"
        c.roda()
        mud = (m.CARDS / "LM-30" / "mudancas.md").read_text()
        P.confere("todos resolvidos: re-tria, com a flag ainda lá",
                  c.etapa("LM-30") == "fila" and "bloqueio resolvido: LM-500, LM-501" in m.le_json(m.caminho_estado("LM-30"))["resumo"]
                  and "## Bloqueio resolvido" in mud)
        m.escreve_json(m.caminho_estado("LM-30"), {**m.le_json(m.caminho_estado("LM-30")), "etapa": "inviavel",
                                                   "status": "aguardando_humano"})
        iv = c.interno("LM-30")
        iv.pop("pendente", None)
        m.escreve_json(m.caminho_interno("LM-30"), iv)
        c.d.fotografa_inviavel("LM-30")
        c.roda()
        P.confere("deu inviável de novo: não re-tria em laço", c.etapa("LM-30") == "inviavel")
        c.card("LM-31")
        c.JIRA["LM-31"]["bloq"] = ["LM-502"]
        c.OUTROS["LM-502"] = "10005"
        c.mexe_foto("LM-31", lambda f: f.pop("bloqueios_abertos"))
        c.roda()
        P.confere("foto antiga: bloqueador já resolvido desbloqueia", c.etapa("LM-31") == "fila")
        c.card("LM-32")
        c.roda()
        P.confere("card sem bloqueador continua parado", c.etapa("LM-32") == "inviavel")


P.grupo("flag e comentários", flag_e_comentarios)
P.grupo("resolvido fora, intervalo e pendente", resolvido_fora_e_intervalo)
P.grupo("responsável no Jira", responsavel)
P.grupo("bloqueadores", bloqueadores)
P.fim()
