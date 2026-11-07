#!/usr/bin/env python3
"""Aprovação de permissões pelo escritório (escritorio.casa).

  permissao.py pedido   -> hook PermissionRequest: publica o pedido e espera a resposta
  permissao.py limpa    -> hooks PostToolUse, PostToolUseFailure e Stop: apaga sobras da sessão

Contrato (pastas em ~/workspace/.escritorio/):
  permissoes/<id>.json  escrito aqui, lido pelo escritório
  respostas/<id>.json   escrito pelo escritório: {"id","decisao":"allow"|"deny","por","motivo","em"}
O guard impede o modelo de escrever nessas pastas; este hook roda fora do modelo.
"""
import json
import os
import re
import secrets
import sys
import time
from pathlib import Path

ESC = Path.home() / "workspace" / ".escritorio"
PERMISSOES = ESC / "permissoes"
RESPOSTAS = ESC / "respostas"
ESPERA_HEADLESS_S = 9 * 60
ESPERA_INTERATIVA_S = 9 * 60  # ajustado depois do teste (b)
ID_OK = re.compile(r"^[A-Za-z0-9_-]{6,80}$")


def headless():
    return os.environ.get("ESTEIRA_HEADLESS") == "1" or os.environ.get("CLAUDE_CODE_SESSION_ATTENDED") != "1"


def escreve_atomico(caminho, dados):
    tmp = caminho.with_name(f".{caminho.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, caminho)


def apaga(*caminhos):
    for c in caminhos:
        try:
            c.unlink()
        except FileNotFoundError:
            pass


def resumo_de(ferramenta, entrada):
    if ferramenta == "Bash":
        return entrada.get("description") or (entrada.get("command") or "")[:120]
    for campo in ("file_path", "notebook_path", "url", "path", "pattern", "query"):
        if entrada.get(campo):
            return f"{ferramenta}: {entrada[campo]}"[:200]
    return ferramenta


def detalhe_de(ferramenta, entrada):
    if ferramenta == "Bash":
        texto = entrada.get("command") or ""
    elif entrada.get("file_path"):
        texto = entrada["file_path"]
    else:
        texto = json.dumps(entrada, ensure_ascii=False)
    return texto[:2000]


def pedido(dados):
    sessao = str(dados.get("session_id") or "sem-sessao")
    pid = f"{re.sub(r'[^A-Za-z0-9_-]', '', sessao)[:36]}-{int(time.time())}-{secrets.token_hex(4)}"
    if not ID_OK.match(pid):
        return
    ferramenta = dados.get("tool_name") or "?"
    entrada = dados.get("tool_input") or {}
    perm, resp = PERMISSOES / f"{pid}.json", RESPOSTAS / f"{pid}.json"
    try:
        PERMISSOES.mkdir(parents=True, exist_ok=True)
        escreve_atomico(perm, {
            "id": pid,
            "session_id": sessao,
            "agente": dados.get("agent_type"),
            "card": os.environ.get("ESTEIRA_CARD") or None,
            "ferramenta": ferramenta,
            "resumo": resumo_de(ferramenta, entrada),
            "detalhe": detalhe_de(ferramenta, entrada),
            "cwd": dados.get("cwd"),
            "criado": int(time.time()),
        })
        limite = time.time() + (ESPERA_HEADLESS_S if headless() else ESPERA_INTERATIVA_S)
        while time.time() < limite:
            if resp.exists():
                try:
                    r = json.loads(resp.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    time.sleep(0.2)  # escritório ainda escrevendo
                    continue
                if r.get("decisao") == "allow":
                    decisao = {"behavior": "allow"}
                else:
                    decisao = {"behavior": "deny", "message": r.get("motivo") or "negado pelo escritório"}
                print(json.dumps({"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": decisao}},
                                 ensure_ascii=False))
                return
            time.sleep(1)
        # timeout: sem decisão (interativo cai na pergunta normal; headless nega)
    finally:
        apaga(perm, resp)


def limpa(dados):
    sessao = str(dados.get("session_id") or "")
    if not sessao or not PERMISSOES.exists():
        return
    for arq in PERMISSOES.glob("*.json"):
        try:
            if json.loads(arq.read_text(encoding="utf-8")).get("session_id") == sessao:
                apaga(arq, RESPOSTAS / arq.name)
        except (json.JSONDecodeError, OSError):
            continue


def main():
    try:
        dados = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "pedido":
        pedido(dados)
    elif modo == "limpa":
        limpa(dados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
