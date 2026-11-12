"""Fim de execução: custo, aprendizados do QA, vagas (max_ativos) e timeout com SIGKILL (leva ~30 s)."""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _carrega import Placar, ambiente, leva  # noqa: E402

P = Placar("test_colhe")


def custo():
    with ambiente() as (m, T):
        K = "LM-5"
        leva(m, K, "triagem", "front")
        log = T / "run.log"
        log.write_text('{"type":"system"}\n{"type":"result","total_cost_usd":1.234,"num_turns":9,'
                       '"modelUsage":{"claude-x":{"costUSD":1.234}}}\n')
        d = m.Despachante()
        d.registra_custo(K, log)
        d.registra_custo(K, log)
        est = m.le_json(m.caminho_estado(K))
        P.confere("custo_usd acumula as 2 execuções (arredondado a cada uma)", est["custo_usd"] == 2.46, est["custo_usd"])
        P.confere("sem transcrição: custo do modelo vai todo para o manager",
                  est.get("custo_por_setor") == {"manager": 2.46}, est.get("custo_por_setor"))
        linhas = (m.ESC / "custos.jsonl").read_text().splitlines()
        P.confere("custos.jsonl ganha uma linha por execução", len(linhas) == 2 and json.loads(linhas[0])["card"] == K)
        sem = T / "sem.log"
        sem.write_text('{"type":"system"}\n')
        d.registra_custo(K, sem)
        P.confere("log sem result: não mexe no custo e avisa no log",
                  m.le_json(m.caminho_estado(K))["custo_usd"] == 2.46
                  and "custo da execução não encontrado" in (m.LOGS / "despachante.log").read_text())


def aprendizados():
    with ambiente() as (m, T):
        K = "LM-5"
        leva(m, K, "triagem")
        (m.CARDS / K / "aprendizados-qa.md").write_text("- login do PROFESSOR cai em /dashboard/home\n")
        d = m.Despachante()
        d.copia_aprendizados(K)
        d.copia_aprendizados(K)
        destino = m.ROOT / "notes/projetos/esteira/aprendizados-qa.md"
        texto = destino.read_text()
        P.confere("copiado para notes/projetos/esteira uma vez só", texto.count(f"## {K}") == 1 and "PROFESSOR" in texto, texto)
        P.confere("arquivo novo ganha cabeçalho", texto.startswith("# Aprendizados do QA da esteira"))
        (m.CARDS / K / "aprendizados-qa.md").write_text("- outro aprendizado\n")
        d.copia_aprendizados(K)
        P.confere("conteúdo novo é copiado de novo", destino.read_text().count(f"## {K}") == 2)


def vagas():
    with ambiente() as (m, T):
        P.confere("sem config: sem limite", m.max_ativos() == m.SEM_LIMITE)
        for valor, esperado in ((2, 2), ("3", 3), (0, m.SEM_LIMITE), ("x", m.SEM_LIMITE), (-5, 1)):
            m.escreve_json(m.CONFIG_ESTEIRA, {"max_ativos": valor})
            P.confere(f"max_ativos={valor!r} -> {esperado}", m.max_ativos() == esperado, m.max_ativos())
        m.escreve_json(m.CONFIG_ESTEIRA, {"max_ativos": 1})
        K = "LM-6"
        leva(m, K, "triagem", "front", "review", "qa")
        m.transiciona(K, "validacao", "aguardando_humano")
        d = m.Despachante()
        d.rodando = {"LM-OUTRO": None}
        (m.FILA / "a.json").write_text(json.dumps({"key": K, "acao": "aprovar", "por": "glauco", "em": 1}))
        d.processa_fila()
        P.confere("sem vaga: aprovar fica aguardando_vaga, visível no estado",
                  (m.le_json(m.caminho_estado(K)).get("aguardando_vaga") or {}).get("acao") == "aprovar")
        d.agenda()
        P.confere("sem vaga: agenda não dispara", m.le_json(m.caminho_estado(K))["etapa"] == "validacao")


def timeout_sigkill():
    with ambiente() as (m, T):
        K = "TESTE-8"
        leva(m, K, "triagem")
        teimoso = subprocess.Popen([sys.executable, "-I", "-c",
                                    "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(600)"],
                                   start_new_session=True)
        try:
            time.sleep(1)
            d = m.Despachante()
            d.rodando = {K: (teimoso, m.agora() - 10, open(os.devnull, "w"))}
            m.TIMEOUT_EXECUCAO_S = 5
            t0 = time.time()
            d.colhe()
            est = m.le_json(m.caminho_estado(K))
            P.confere("processo que ignora SIGTERM foi morto", teimoso.poll() is not None,
                      f"rc={teimoso.returncode}, {time.time() - t0:.0f} s")
            P.confere("morto por SIGKILL", teimoso.returncode == -signal.SIGKILL, teimoso.returncode)
            P.confere("card foi para erro por timeout", est["etapa"] == "erro" and "timeout" in est["resumo"], est["resumo"])
            P.confere("saiu da lista de rodando", K not in d.rodando)
        finally:
            if teimoso.poll() is None:
                teimoso.kill()
                teimoso.wait()


P.grupo("custo da execução", custo)
P.grupo("aprendizados do QA", aprendizados)
P.grupo("vagas (max_ativos)", vagas)
P.grupo("timeout: SIGTERM ignorado vira SIGKILL", timeout_sigkill)
P.fim()
