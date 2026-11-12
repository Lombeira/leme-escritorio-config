"""Máquina de estados do card (transiciona): quem pode mover, review, voltas, PR, inviável e pedidos de validação."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, leva, recusa  # noqa: E402

P = Placar("test_estado")


def humano_x_despachante():
    with ambiente() as (m, T):
        K = "TESTE-9"
        r = recusa(m, K, "fila", "rodando")
        P.confere("CLI não cria card na fila", r and "só o despachante" in r, r)
        leva(m, K, "triagem", "front", "review", "qa")
        m.transiciona(K, "validacao", "aguardando_humano")
        r = recusa(m, K, "pr", "rodando")
        P.confere("manager não se aprova (validacao -> pr)", r and "só o despachante" in r, r)
        r = recusa(m, K, "devolvido", "rodando")
        P.confere("manager não se devolve (validacao -> devolvido)", r and "só o despachante" in r, r)
        P.confere("manager não recoloca na fila", recusa(m, K, "fila", "rodando") is not None)
        r = recusa(m, K, "validacao", "rodando")
        P.confere("validacao exige aguardando_humano", r and "exige status" in r, r)
        P.confere("etapa desconhecida é recusada", "desconhecida" in (recusa(m, K, "xpto", "rodando") or ""))


def front_passa_pelo_review():
    with ambiente() as (m, T):
        K = "LM-5"
        leva(m, K, "triagem", "front")
        r = recusa(m, K, "qa", "rodando")
        P.confere("front -> qa direto é recusado (toda mudança passa pelo review)", r and "não permitida" in r, r)


def review():
    with ambiente() as (m, T):
        est = lambda k: m.le_json(m.caminho_estado(k))
        K = "LM-1"
        leva(m, K, "triagem", "front")
        m.transiciona(K, "review", "rodando", agente="reviewer")
        P.confere("review -> front sem --com-achados é recusado", "com-achados" in (recusa(m, K, "front", "rodando") or ""))
        for _ in range(2):
            m.transiciona(K, "front", "rodando", com_achados=True)
            m.transiciona(K, "review", "rodando")
        P.confere("voltas_review conta", est(K)["voltas_review"] == 2, est(K)["voltas_review"])
        P.confere("3ª volta do review é recusada",
                  "limite de 2 voltas do review" in (recusa(m, K, "front", "rodando", com_achados=True) or ""))
        m.transiciona(K, "review", "aguardando_humano", resumo="blocker depois de 2 voltas")
        P.confere("escalado no review não vai para qa", "escalado" in (recusa(m, K, "qa", "rodando") or ""))
        P.confere("escalado no review: devolver só pelo despachante",
                  "só o despachante" in (recusa(m, K, "devolvido", "rodando") or ""))
        m.transiciona(K, "devolvido", "rodando", por_despachante=True)
        P.confere("devolver zera voltas_review", est(K)["voltas_review"] == 0)
        m.transiciona(K, "front", "rodando")
        m.transiciona(K, "review", "rodando")
        m.transiciona(K, "qa", "rodando")
        P.confere("review READY -> qa", est(K)["etapa"] == "qa")
        K2 = "LM-2"
        leva(m, K2, "triagem", "front", "review")
        r = recusa(m, K2, "devolvido", "rodando", por_despachante=True)
        P.confere("review -> devolvido sem estar escalado é recusado", r and "escalado" in r, r)


def voltas_qa():
    with ambiente() as (m, T):
        K = "LM-3"
        leva(m, K, "triagem", "front", "review", "qa")
        P.confere("qa -> front exige --reprovado", "reprovado" in (recusa(m, K, "front", "rodando") or ""))
        for _ in range(2):
            m.transiciona(K, "front", "rodando", reprovado=True)
            m.transiciona(K, "review", "rodando")
            m.transiciona(K, "qa", "rodando")
        r = recusa(m, K, "front", "rodando", reprovado=True)
        P.confere("3ª volta do QA é recusada", r and "limite de 2 voltas do QA" in r, r)


def retomar_e_erro():
    with ambiente() as (m, T):
        K = "LM-9"
        leva(m, K, "triagem", "front", "review", "qa")
        m.transiciona(K, "erro", "falhou", resumo="x")
        r = recusa(m, K, "qa", "rodando")
        P.confere("modelo não sai do erro sozinho", r and "só o despachante" in r, r)
        P.confere("etapa_para_retomar: caiu no qa -> qa", m.etapa_para_retomar(m.le_json(m.caminho_estado(K))) == "qa")
        P.confere("etapa_para_retomar: caiu no review -> review",
                  m.etapa_para_retomar({"historico": [{"etapa": "review"}, {"etapa": "erro"}]}) == "review")
        P.confere("etapa_para_retomar: devolvido volta como front",
                  m.etapa_para_retomar({"historico": [{"etapa": "devolvido"}, {"etapa": "erro"}]}) == "front")
        P.confere("etapa_para_retomar: só fila -> None",
                  m.etapa_para_retomar({"historico": [{"etapa": "fila"}, {"etapa": "erro"}]}) is None)


def revisao_pr():
    with ambiente() as (m, T):
        K = "PR-870"
        m.transiciona(K, "fila", "rodando", por_despachante=True, tipo="revisao_pr")
        r = recusa(m, K, "front", "rodando")
        P.confere("PR não vai para front", r and "não permitida" in r and "revisão de PR" in r, r)
        m.transiciona(K, "review", "rodando", agente="reviewer")
        m.transiciona(K, "validacao", "aguardando_humano")
        r = recusa(m, K, "concluido", "concluido")
        P.confere("modelo não publica/conclui revisão de PR sozinho", r and "só o despachante" in r, r)
        P.confere("Jira ignora card de PR", m.status_jira_desejado(m.le_json(m.caminho_estado(K))) is None)


def inviavel():
    with ambiente() as (m, T):
        K = "LM-10"
        leva(m, K, "triagem")
        m.transiciona(K, "inviavel", "aguardando_humano")
        r = recusa(m, K, "concluido", "concluido", resumo="x")
        P.confere("agente não conclui inviável", r and "só o despachante" in r, r)
        m.transiciona(K, "concluido", "concluido", por_despachante=True)
        P.confere("despachante conclui inviável (resolvido fora)", m.le_json(m.caminho_estado(K))["etapa"] == "concluido")


def pedidos_de_validacao():
    with ambiente() as (m, T):
        pedidos = m.ROOT / "notes" / "pedidos"
        pedidos.mkdir(parents=True)
        for k, destino, motivo in (("LM-1", "devolvido", "devolvido"), ("LM-2", "pr", "aprovado"),
                                   ("LM-3", "erro", "card foi para erro")):
            arq = pedidos / f"{k}-validar.md"
            arq.write_text(f"---\ncard: {k}\nStatus: aberto\n---\n# {k}\n")
            leva(m, k, "triagem", "front", "review", "qa")
            m.transiciona(k, "validacao", "aguardando_humano")
            aberto = "Status: aberto" in arq.read_text()
            m.transiciona(k, destino, "falhou" if destino == "erro" else "rodando", por_despachante=True, resumo="x")
            texto = arq.read_text()
            P.confere(f"{k}: pedido aberto em validacao fecha ao sair para {destino} ({motivo})",
                      aberto and "status: fechado" in texto and f"({motivo})" in texto and "aberto" not in texto, texto)
        outro = pedidos / "LM-4-validar.md"
        outro.write_text("---\nStatus: aberto\n---\n")
        leva(m, "LM-4", "triagem", "front")
        P.confere("card que não passou pela validação não fecha pedido", "aberto" in outro.read_text())


P.grupo("humano x despachante", humano_x_despachante)
P.grupo("front passa pelo review", front_passa_pelo_review)
P.grupo("review na máquina de estados", review)
P.grupo("voltas do QA", voltas_qa)
P.grupo("erro e retomar", retomar_e_erro)
P.grupo("revisão de PR", revisao_pr)
P.grupo("inviável", inviavel)
P.grupo("pedidos de validação (notes/pedidos)", pedidos_de_validacao)
P.fim()
