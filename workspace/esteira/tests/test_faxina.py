"""Faxina e limpar card. O /tmp da faxina é trocado por uma pasta dentro da temporária (o real nunca é varrido)."""
import json
import os
import pathlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, commit, git, leva, repo_com_origin  # noqa: E402

P = Placar("test_faxina")


def velho(p, dias, conteudo="x" * 50000):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(conteudo)
    t = time.time() - dias * 86400
    os.utime(p, (t, t))
    return p


def envelhece(p, dias):
    t = time.time() - dias * 86400
    os.utime(p, (t, t))


def faxina():
    with ambiente() as (m, T):
        tmp_falso = T / "tmp"
        tmp_falso.mkdir()
        m.Path = lambda *a: tmp_falso if a == ("/tmp",) else pathlib.Path(*a)
        log_velho, log_novo = velho(m.LOGS / "LM-9-1-triagem.log", 40), velho(m.LOGS / "LM-8-1-triagem.log", 5)
        desp = velho(m.LOGS / "despachante.log", 40)
        proc_velho = velho(m.PROCESSADOS / "1-glauco-triagem-LM-9.json", 40)
        perm_velha = velho(m.ESC / "permissoes" / "sessao-velha.json", 1)
        perm_nova = velho(m.ESC / "permissoes" / "sessao-nova.json", 0)
        velho(m.ESC / "respostas" / "sessao-nova.json", 0)
        resp_orfa = velho(m.ESC / "respostas" / "sem-par.json", 0)
        lixo = velho(tmp_falso / "esteira-teste-velho" / "lixo.bin", 3)
        envelhece(lixo.parent, 3)
        tmux = velho(tmp_falso / "tmux-teste-velho" / "sock", 3)
        envelhece(tmux.parent, 3)
        recente = velho(tmp_falso / "pasta-com-coisa-nova" / "velho.txt", 3)
        velho(recente.parent / "novo.txt", 0)
        envelhece(recente.parent, 3)
        removidos, liberado = m.faxina("glauco")
        for p, deve_ficar, nome in [
                (log_novo, True, "log de 5 dias fica"), (log_velho, False, "log de 40 dias sai"),
                (desp, True, "despachante.log nunca sai"), (proc_velho, False, "processado de 40 dias sai"),
                (perm_velha, False, "permissão de 1 dia sai"), (perm_nova, True, "permissão recente com resposta fica"),
                (resp_orfa, False, "resposta sem permissão sai"),
                (lixo.parent, False, "sobra velha em /tmp sai"), (tmux.parent, True, "tmux-* em /tmp é protegido"),
                (recente.parent, True, "pasta em /tmp com arquivo novo dentro fica")]:
            P.confere(nome, p.exists() == deve_ficar, "existe" if p.exists() else "removido")
        P.confere("liberado conta os bytes removidos", liberado >= 5 * 50000, m.mb(liberado))
        P.confere("systemctl de previews não roda de verdade",
                  any(c[:2] == ["systemctl", "--user"] for c in m.subprocess.bloqueados))


def faxina_worktree_sem_card():
    with ambiente() as (m, T):
        m.Path = lambda *a: (T / "tmp-vazio") if a == ("/tmp",) else pathlib.Path(*a)
        (T / "tmp-vazio").mkdir()
        O = T / "origin-app"
        O.mkdir()
        git("-C", O, "init", "-q", "-b", "main")
        commit(O, "a.txt", "1", "1")
        m.REPO_APP.parent.mkdir(parents=True)
        git("clone", "-q", O, m.REPO_APP)
        limpo, sujo = m.WORKTREES / "LM-70", m.WORKTREES / "LM-71"
        git("-C", m.REPO_APP, "worktree", "add", "-q", "-b", "LM-70-x", limpo, "origin/main")
        git("-C", m.REPO_APP, "worktree", "add", "-q", "-b", "LM-71-y", sujo, "origin/main")
        (sujo / "a.txt").write_text("mudança não commitada")
        removidos, _ = m.faxina("feda")
        P.confere("worktree sem card e limpo sai, com a branch local", not limpo.exists()
                  and not git("-C", m.REPO_APP, "branch", "--list", "LM-70-x"))
        P.confere("worktree sem card com mudança fica (MANTIDO)", sujo.exists()
                  and any(r.startswith("MANTIDO") and "LM-71" in r for r in removidos), removidos)


def limpar_card():
    with ambiente() as (m, T):
        pedidos = m.ROOT / "notes" / "pedidos"
        pedidos.mkdir(parents=True)
        K = "LM-50"
        leva(m, K, "triagem")
        P.confere("limpar recusa card rodando", not m.limpa_card(K, "glauco")[0])
        m.transiciona(K, "inviavel", "aguardando_humano")
        (pedidos / f"{K}-validar.md").write_text("---\nstatus: aberto\n---\n")
        velho(m.LOGS / f"{K}-1-triagem.log", 0)
        ok, msg = m.limpa_card(K, "glauco")
        P.confere("limpar inviável sem worktree: apaga pasta e logs", ok and not (m.CARDS / K).exists()
                  and not list(m.LOGS.glob(f"{K}-*.log")), msg)
        P.confere("limpar fecha pedidos abertos", "status: fechado" in (pedidos / f"{K}-validar.md").read_text())
        linha = json.loads(m.ARQUIVO.read_text().splitlines()[-1])
        P.confere("arquivo.jsonl guarda o resumo do card", linha["key"] == K and linha["etapa_final"] == "inviavel"
                  and linha["por"] == "glauco")
        P.confere("card inexistente: recusa", not m.limpa_card("LM-NADA", "glauco")[0])

        O, R = repo_com_origin(T, "app2")
        K2 = "LM-51"
        leva(m, K2, "triagem")
        m.transiciona(K2, "erro", "falhou", resumo="x")
        wt = m.WORKTREES / K2
        wt.parent.mkdir(parents=True, exist_ok=True)
        git("-C", R, "worktree", "add", "-q", "-b", "LM-51-z", wt, "origin/main")
        commit(wt, "novo.txt", "x", "commit local não enviado")
        ok, msg = m.limpa_card(K2, "glauco")
        P.confere("worktree com commit fora do remoto: não limpa", not ok and "commit(s) que não estão no remoto" in msg
                  and wt.exists() and (m.CARDS / K2).exists(), msg)
        m.atualiza_campos(K2, merged_em="2026-11-07T03:00:00Z")
        ok, msg = m.limpa_card(K2, "glauco")
        P.confere("PR mergeado: limpa mesmo com commit local", ok and not wt.exists() and not (m.CARDS / K2).exists(), msg)


P.grupo("faxina", faxina)
P.grupo("faxina: worktrees sem card", faxina_worktree_sem_card)
P.grupo("limpar card", limpar_card)
P.fim()
