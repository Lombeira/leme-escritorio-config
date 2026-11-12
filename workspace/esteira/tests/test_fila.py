"""Despachante consumindo a fila: aprovar, atualizar_pendencias, retomar, triagem (responsável no Jira) e remover_anexo."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, leva, recusa  # noqa: E402

P = Placar("test_fila")


def pedido(m, nome, dados):
    (m.FILA / nome).write_text(json.dumps(dados))


def erro_de(m, nome):
    return next(m.PROCESSADOS.glob(f"*-{nome}.erro"), None)


class ProcFalso:
    pid = 0

    def __init__(self, rc=None):
        self.rc = rc

    def poll(self):
        return self.rc


def popen_que_registra(lista):
    def popen(cmd, **kw):
        lista.append((cmd, kw.get("env", {})))
        return ProcFalso(None)
    return popen


def aprovar():
    with ambiente() as (m, T):
        K = "TESTE-9"
        leva(m, K, "triagem", "front", "review", "qa")
        m.transiciona(K, "validacao", "aguardando_humano")
        d = m.Despachante()
        disparados = []
        m.subprocess.Popen = popen_que_registra(disparados)
        pedido(m, "a.json", {"key": K, "acao": "aprovar", "por": "glauco", "em": 1})
        d.processa_fila()
        d.agenda()
        est = m.le_json(m.caminho_estado(K))
        P.confere("aprovar pela fila: despachante leva a pr", est["etapa"] == "pr" and "aprovado por glauco" in est["resumo"],
                  f"{est['etapa']} / {est['resumo']}")
        P.confere("manager disparado com ESTEIRA_HEADLESS=1 e ESTEIRA_CARD",
                  disparados and disparados[-1][1].get("ESTEIRA_HEADLESS") == "1"
                  and disparados[-1][1].get("ESTEIRA_CARD") == K)
        P.confere("disparo é o preparar-e-rodar da própria esteira (não claude direto)",
                  disparados and disparados[-1][0][3:5] == ["preparar-e-rodar", K], disparados and disparados[-1][0][:5])
        pedido(m, "b.json", {"key": K, "acao": "aprovar", "por": "intruso", "em": 2})
        d.processa_fila()
        P.confere("pedido com por fora de glauco/feda é rejeitado", erro_de(m, "b.json"))
        (m.FILA / "c.json").write_text("{ruim")
        d.processa_fila()
        P.confere("JSON inválido é rejeitado", erro_de(m, "c.json") and "JSON inválido" in erro_de(m, "c.json").read_text())


def atualizar_pendencias():
    with ambiente() as (m, T):
        d = m.Despachante()
        for n in range(3):
            pedido(m, f"atu{n}.json", {"acao": "atualizar_pendencias", "por": "feda", "em": n})
        pedido(m, "atu-sem-por.json", {"acao": "atualizar_pendencias", "em": 9})
        chamadas = []
        m.atualiza_pendencias = lambda: (chamadas.append(1), (True, "26 cards"))[1]
        d.processa_fila()
        nomes = sorted(p.name for p in m.PROCESSADOS.iterdir())
        P.confere("3 pedidos juntos -> REST roda uma vez só", len(chamadas) == 1, f"{len(chamadas)} chamada(s)")
        P.confere("os 3 vão para processados/ sem .erro",
                  sum(1 for n in nomes if n.endswith(".json") and "atu" in n and "sem-por" not in n) == 3
                  and not any(n.endswith(".erro") and "sem-por" not in n for n in nomes), nomes)
        P.confere("pedido sem 'por' é rejeitado com .erro", any(n.endswith("atu-sem-por.json.erro") for n in nomes))
        P.confere("fila vazia depois do ciclo", not list(m.FILA.glob("*.json")))
        pedido(m, "atu-falha.json", {"acao": "atualizar_pendencias", "por": "glauco", "em": 20})
        (m.ESC / "pendencias.json").write_text('{"updated": 111, "items": []}')
        m.atualiza_pendencias = lambda: (False, "REST do Jira falhou: HTTPError 401")
        d.processa_fila()
        e = erro_de(m, "atu-falha.json")
        P.confere("REST falhou -> processados/ com .erro e motivo", e and "401" in e.read_text(), e and e.read_text())
        P.confere("pendencias.json anterior preservado", m.le_json(m.ESC / "pendencias.json")["updated"] == 111)


def retomar():
    with ambiente() as (m, T):
        est = lambda k: m.le_json(m.caminho_estado(k))
        K = "LM-9"
        leva(m, K, "triagem", "front", "review", "qa")
        m.transiciona(K, "validacao", "aguardando_humano")
        m.transiciona(K, "pr", "rodando", resumo="aprovado por glauco", por_despachante=True)
        m.transiciona(K, "pr", "falhou", resumo="pre-push barrou: 136 testes")
        d = m.Despachante()
        d.rodando = {K: (ProcFalso(0), m.agora(), open(T / "vazio.log", "w"))}
        d.colhe()
        e = est(K)
        P.confere("pr falhou vira erro ao fim da execução, com o motivo", e["etapa"] == "erro" and "136 testes" in e["resumo"],
                  e["resumo"])
        r = recusa(m, K, "pr", "rodando")
        P.confere("modelo não sai do erro sozinho (erro -> pr pelo CLI)", r and "só o despachante" in r, r)
        pedido(m, "r.json", {"key": K, "acao": "retomar", "por": "glauco", "em": 1})
        d.processa_fila()
        pend = (m.le_json(m.caminho_interno(K), {}) or {}).get("pendente", {})
        P.confere("retomar aceito, alvo pelo historico = pr", pend.get("etapa") == "pr", pend)
        cmds = []
        m.subprocess.Popen = popen_que_registra(cmds)
        d.agenda()
        e = est(K)
        P.confere("despachante devolve o card a pr/rodando, sem triagem", e["etapa"] == "pr" and e["status"] == "rodando",
                  e["resumo"])
        P.confere("prompt diz a etapa a refazer", cmds and "Etapa a refazer: pr" in cmds[-1][0][-1]
                  and "retomar" in cmds[-1][0][-1])
        P.confere("pendente consumido e pid gravado", "pendente" not in m.le_json(m.caminho_interno(K), {})
                  and "pid" in m.le_json(m.caminho_interno(K), {}))
        d.rodando.clear()
        pedido(m, "r2.json", {"key": K, "acao": "retomar", "por": "feda", "em": 2})
        d.processa_fila()
        P.confere("retomar em card que não está em erro é rejeitado", erro_de(m, "r2.json"))
        K2 = "LM-7"
        leva(m, K2, "triagem", "front")
        m.transiciona(K2, "front", "aguardando_humano", resumo="falta o anexo")
        pedido(m, "r3.json", {"key": K2, "acao": "retomar", "por": "glauco", "em": 3})
        d.processa_fila()
        P.confere("retomar em front parado esperando humano: alvo front",
                  (m.le_json(m.caminho_interno(K2), {}).get("pendente") or {}).get("etapa") == "front")


def triagem_e_responsavel():
    with ambiente() as (m, T):
        jira = {"LM-1": None, "LM-2": {"displayName": "Fernanda Guerra"}}
        puts = []

        def jira_req(caminho, metodo="GET", corpo=None):
            key = caminho.split("/")[1].split("?")[0]
            if key == "LM-3":
                raise RuntimeError("Jira fora do ar")
            if metodo == "PUT":
                puts.append((key, caminho, corpo))
                jira[key] = {"displayName": "Glauco"}
                return {}
            return {"fields": {"assignee": jira[key]}}
        m.jira_req = jira_req
        m.escreve_json(m.ESC / "pendencias.json", {"items": [{"key": "LM-1", "summary": "Resumo do 1", "assignee": ""}]})
        d = m.Despachante()
        for i, k in enumerate(("LM-1", "LM-2", "LM-3")):
            pedido(m, f"t{i}.json", {"key": k, "acao": "triagem", "por": "glauco", "em": i})
        d.processa_fila()
        logs = (m.LOGS / "despachante.log").read_text()
        glauco = m.CONTA_JIRA["glauco"]
        P.confere("sem responsável: PUT só no LM-1, com o accountId de quem pediu",
                  puts == [("LM-1", "issue/LM-1/assignee", {"accountId": glauco})], puts)
        P.confere("estado do LM-1 fica com assignee glauco e summary das pendências",
                  m.le_json(m.caminho_estado("LM-1"))["assignee"] == "glauco"
                  and m.le_json(m.caminho_estado("LM-1"))["summary"] == "Resumo do 1")
        P.confere("já tinha responsável: mantido, sem troca", "LM-2: responsável no Jira: mantido Fernanda Guerra" in logs)
        P.confere("Jira fora do ar não trava a triagem", "LM-3: responsável no Jira: falhou" in logs)
        P.confere("os 3 aceitos na fila", all(m.le_json(m.caminho_estado(k))["etapa"] == "fila" for k in ("LM-1", "LM-2", "LM-3")))
        pedido(m, "t9.json", {"key": "LM-1", "acao": "triagem", "por": "glauco", "em": 9})
        d.processa_fila()
        P.confere("triagem de card que já está na fila é rejeitada", erro_de(m, "t9.json"))


def remover_anexo():
    with ambiente() as (m, T):
        anexos = [{"id": "1", "filename": "exemplo.pdf", "size": 3, "content": "https://x/1"},
                  {"id": "2", "filename": "mock-velho.png", "size": 3, "content": "https://x/2"}]
        m.jira_req = lambda caminho, *a, **k: {"fields": {"attachment": anexos}}

        class R:
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return b"abc"
        m.urllib.request.urlopen = lambda req, timeout=0: R()
        K = "TESTE-1"
        leva(m, K, "triagem", "front")
        r1 = m.baixa_anexos(K)
        P.confere("baixa os 2 anexos", (m.CARDS / K / "anexos/exemplo.pdf").exists()
                  and (m.CARDS / K / "anexos/mock-velho.png").exists(), r1)
        d = m.Despachante()

        def remover(nome, arq):
            pedido(m, nome, {"acao": "remover_anexo", "key": K, "arquivo": arq, "por": "glauco", "em": 1})
        remover("r1.json", "mock-velho.png")
        d.processa_fila()
        P.confere("anexo removido do disco", not (m.CARDS / K / "anexos/mock-velho.png").exists())
        P.confere("o outro anexo continua", (m.CARDS / K / "anexos/exemplo.pdf").exists())
        interno = m.le_json(m.caminho_interno(K))
        P.confere("entrou na lista de ignorados", interno.get("anexos_ignorados") == ["mock-velho.png"],
                  interno.get("anexos_ignorados"))
        P.confere("card rodando: aviso no resumo", "pode já ter lido" in m.le_json(m.caminho_estado(K))["resumo"])
        m.transiciona(K, "erro", "falhou", resumo="teste")
        pedido(m, "ret.json", {"acao": "retomar", "key": K, "por": "glauco", "em": 2})
        d.processa_fila()
        P.confere("retomar aceito", (m.le_json(m.caminho_interno(K)).get("pendente") or {}).get("acao") == "retomar")
        r2 = m.baixa_anexos(K)
        P.confere("removido não volta no download seguinte", not (m.CARDS / K / "anexos/mock-velho.png").exists()
                  and "ignorado" in r2, r2)
        for nome, arq, motivo in (("r2.json", "nao-existe.pdf", "não existe"), ("r3.json", "../estado.json", "inválido"),
                                  ("r4.json", "sub/x.png", "inválido"), ("r5.json", ".interno.json", "inválido")):
            remover(nome, arq)
            d.processa_fila()
            e = erro_de(m, nome)
            P.confere(f"recusa {arq!r} com .erro", e and motivo in e.read_text(), e and e.read_text().strip())
        P.confere("estado.json e .interno.json intactos depois das recusas",
                  m.caminho_estado(K).exists() and m.caminho_interno(K).exists())


P.grupo("aprovar pela fila", aprovar)
P.grupo("atualizar_pendencias", atualizar_pendencias)
P.grupo("retomar", retomar)
P.grupo("triagem e responsável no Jira", triagem_e_responsavel)
P.grupo("remover_anexo", remover_anexo)
P.fim()
