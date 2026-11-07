#!/usr/bin/env python3
"""PreToolUse: trava operações git/gh/terraform perigosas antes de o Claude executá-las.

Bloqueia só o que ALTERA. Ler, procurar ou escrever sobre um assunto nunca é bloqueado:
trava que barra leitura ensina a reescrever o comando para escapar dela.

deny  -> operação proibida; o Claude explica e o usuário decide.
ask   -> escrita nas próprias travas ou em gitconfig; o usuário confirma.
É cinto de segurança, não sandbox: um script em arquivo passa por fora daqui.
A camada seguinte é o pre-push global (dono root) e, no GitHub, branch protection.
"""
import json
import os
import re
import shlex
import subprocess
import sys

WORKSPACE_BARE = "/home/leme/git/workspace.git"
PROTECTED_BRANCHES = {"main", "master"}
PROTECTED_ENV_PREFIXES = ("GIT_CONFIG", "LEME_HUMAN_PUSH")
PROTECTED_GIT_KEYS = ("core.hookspath", "include.path")
PROTECTED_GIT_KEY_PREFIXES = ("includeif.",)
GUARD_PATH_FRAGMENTS = (
    "/.claude/settings.json",
    "/.claude/settings.local.json",
    "/.claude/hooks/",
    "/.gitconfig",
    "/.config/git/",
    "/.git/config",
    "/.git/hooks/",
    "/leme-git-guard/",
)
TERRAFORM_READONLY = {"init", "validate", "fmt", "plan", "version", "providers", "show",
                      "output", "graph", "get", "console", "metadata", "-version", "-help"}
TERRAFORM_READONLY_SUB = {"state": {"list", "show", "pull"}, "workspace": {"list", "show"}}

SUFFIX = (
    "\nNão tente contornar esta trava (outro comando, script em arquivo, alias, variável de ambiente). "
    "Explique ao usuário o que você queria fazer e por quê, e deixe ele decidir. Push sensível quem faz é ele."
)


def out(reason, decision):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": "TRAVA LEME: " + reason + (SUFFIX if decision == "deny" else ""),
    }}, ensure_ascii=False))
    sys.exit(0)


def deny(reason):
    out(reason, "deny")


def ask(reason):
    # Sem humano para responder (claude -p da esteira), pedir confirmação vira negação.
    if os.environ.get("ESTEIRA_HEADLESS") == "1":
        out(reason + " (sessão da esteira, sem humano: negado)", "deny")
    out(reason, "ask")


def resolve(path, cwd):
    return os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))


ESTEIRA_ROOT = "/home/leme/workspace/"
ESTEIRA_PREFIXOS = (
    ESTEIRA_ROOT + ".escritorio/fila/",
    ESTEIRA_ROOT + ".escritorio/permissoes/",
    ESTEIRA_ROOT + ".escritorio/respostas/",  # o modelo não pode aprovar a própria permissão
    ESTEIRA_ROOT + "esteira/",
    ESTEIRA_ROOT + ".claude/agents/",
)
ESTEIRA_CONTROLE_CARD = {"estado.json", ".interno.json", ".lock"}


def is_esteira_path(p):
    """Controle da esteira: fila, código, agentes e os arquivos de estado de cada card.
    Os arquivos de trabalho do card (triagem.md, qa.md, evidencias/) ficam livres."""
    if p.startswith(ESTEIRA_PREFIXOS):
        return True
    if p.startswith(ESTEIRA_ROOT + ".escritorio/cards/"):
        return os.path.basename(p.rstrip("/")) in ESTEIRA_CONTROLE_CARD
    if p.startswith(ESTEIRA_ROOT + ".escritorio/novos/"):
        # o redator só escreve rascunho.json; confirmar (final.json) é do humano
        return os.path.basename(p.rstrip("/")) in ("final.json", "estado.json", "pedido.json", "descartado")
    return False


def is_guard_path(path, cwd):
    p = resolve(path, cwd) + "/"
    return any(f in p for f in GUARD_PATH_FRAGMENTS) or is_esteira_path(p)


def protected_env(name):
    return name.startswith(PROTECTED_ENV_PREFIXES)


def protected_git_key(key):
    k = key.lower()
    return k in PROTECTED_GIT_KEYS or k.startswith(PROTECTED_GIT_KEY_PREFIXES)


def split_commands(cmd):
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()\n")
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        tokens = list(lex)
    except ValueError:
        tokens = cmd.split()
    cur = []
    for t in tokens:
        if t and set(t) <= set(";&|()\n"):
            if cur:
                yield cur
            cur = []
        else:
            cur.append(t)
    if cur:
        yield cur


def git_out(args, cwd):
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ""


def strip_redirects(argv, cwd):
    """Remove redirecionamentos do argv; pede confirmação se algum escreve numa trava."""
    clean, i = [], 0
    while i < len(argv):
        t = argv[i]
        m = re.match(r"^(\d*|&)(>>?|>\|)(.*)$", t)
        if m:
            target = m.group(3)
            if not target and i + 1 < len(argv):
                i += 1
                target = argv[i]
            if target and not target.startswith("&") and is_guard_path(target, cwd):
                ask(f"redirecionamento escreve em {target}, que faz parte das travas ou da config do git/Claude Code.")
            i += 1
            continue
        if re.match(r"^\d*<", t):
            if t.rstrip("0123456789") in ("<", "<<", "<<<") and i + 1 < len(argv):
                i += 1
            i += 1
            continue
        clean.append(t)
        i += 1
    return clean


def check_file_writes(prog, args, cwd):
    files = [a for a in args if not a.startswith("-")]
    if not files:
        return
    if prog in ("cp", "mv", "install", "ln", "rsync"):
        targets = files[-1:] if prog in ("cp", "install", "ln", "rsync") else files
    elif prog == "sed":
        if not any(a == "-i" or a.startswith("-i") or a.startswith("--in-place") for a in args):
            return
        targets = files[1:]
    elif prog in ("rm", "rmdir", "chmod", "chown", "chgrp", "truncate", "tee", "touch", "unlink", "shred"):
        targets = files
    elif prog in ("python", "python3", "perl", "ruby", "node", "dd"):
        targets = files
    else:
        return
    for t in targets:
        if is_guard_path(t, cwd):
            ask(f"{prog} altera {t}, que faz parte das travas ou da config do git/Claude Code.")


def check_push(args, cwd):
    flags_with_value = {"--repo", "--receive-pack", "--exec", "-o", "--push-option", "--recurse-submodules"}
    positional, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a == "--":
            continue
        if a.startswith("--"):
            name = a.split("=", 1)[0]
            if name in ("--force", "--force-with-lease", "--force-if-includes"):
                deny(f"git push com {name} (force push).")
            if name in ("--delete", "--prune", "--mirror", "--all"):
                deny(f"git push com {name} (apaga ou sobrescreve refs no remoto).")
            if name in flags_with_value and "=" not in a:
                skip = True
            continue
        if a.startswith("-") and len(a) > 1:
            if "f" in a[1:]:
                deny(f"git push {a} (force push).")
            if "d" in a[1:]:
                deny(f"git push {a} (deleção de branch remota).")
            if a == "-o":
                skip = True
            continue
        positional.append(a)

    refspecs = positional[1:]
    for r in refspecs:
        if r.startswith("+"):
            deny(f"refspec '{r}' com + (force push).")
        if ":" in r:
            deny(f"refspec '{r}' com ':' (destino explícito ou deleção).")
        if r.removeprefix("refs/heads/") in PROTECTED_BRANCHES:
            deny(f"push direto para {r}.")
    if not refspecs:
        branch = git_out(["branch", "--show-current"], cwd)
        if branch in PROTECTED_BRANCHES:
            remote = positional[0] if positional else "origin"
            url = git_out(["remote", "get-url", remote], cwd) or remote
            if os.path.realpath(url) != os.path.realpath(WORKSPACE_BARE):
                deny(f"push sem refspec estando na branch {branch} (vai para {branch} do remoto).")


def check_git_config(args):
    value_opts = {"-f", "--file", "--blob", "--type", "--default", "--comment", "--value", "--fixed-value"}
    read_flags = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--get-color", "--get-colorbool",
                  "-l", "--list", "--show-origin", "--show-scope", "--name-only"}
    write_flags = {"--unset", "--unset-all", "--replace-all", "--add", "--rename-section", "--remove-section",
                   "--edit", "-e"}
    positional, flags, skip = [], set(), False
    for a in args:
        if skip:
            skip = False
            continue
        if a.startswith("-"):
            name = a.split("=", 1)[0]
            flags.add(name)
            if name in value_opts and "=" not in a:
                skip = True
            continue
        positional.append(a)

    sub = positional[0] if positional else ""
    if sub in ("get", "list"):
        return
    if sub in ("set", "unset"):
        keys, write = positional[1:2], True
    elif sub == "edit" or flags & {"--edit", "-e"}:
        deny("git config edit (abre a config inteira para edição, inclusive core.hooksPath).")
    elif sub in ("rename-section", "remove-section") or flags & {"--rename-section", "--remove-section"}:
        names = positional[1:] if sub in ("rename-section", "remove-section") else positional
        if any(n.lower().split(".")[0] in ("core", "include", "includeif") for n in names):
            deny("git config renomeia ou remove a seção que contém core.hooksPath/include.")
        return
    elif flags & read_flags:
        return
    elif flags & write_flags or len(positional) >= 2:
        keys, write = positional[:1], True
    else:
        return
    if write and any(protected_git_key(k) for k in keys):
        deny(f"git config altera {keys[0]} (desligaria ou desviaria os hooks do git).")


def check_git(argv_rest, cwd):
    args = list(argv_rest)
    gcwd = cwd
    while args and args[0].startswith("-"):
        opt = args.pop(0)
        if opt == "-C" and args:
            gcwd = resolve(args.pop(0), gcwd)
        elif opt == "-c" and args:
            kv = args.pop(0)
            if protected_git_key(kv.split("=", 1)[0]):
                deny(f"git -c {kv.split('=', 1)[0]} (sobrescreve os hooks do git só neste comando).")
        elif opt.startswith("--config-env"):
            kv = opt.split("=", 1)[1] if "=" in opt else (args.pop(0) if args else "")
            if protected_git_key(kv.split("=", 1)[0]):
                deny("git --config-env em core.hooksPath/include.")
        elif opt in ("--git-dir", "--work-tree", "--namespace") and args:
            args.pop(0)
    if not args:
        return
    sub, rest = args[0], args[1:]
    if "--no-verify" in rest and sub in ("commit", "push", "merge", "rebase", "am", "cherry-pick", "revert", "pull"):
        deny(f"git {sub} --no-verify (pula os hooks do git).")
    if sub == "commit" and any(re.match(r"^-[A-Za-z]*n", a) and not a.startswith("--") for a in rest):
        deny("git commit -n (equivale a --no-verify, pula os hooks).")
    if sub == "push":
        check_push(rest, gcwd)
    elif sub == "config":
        check_git_config(rest)
    elif sub in ("checkout", "restore", "rm", "mv", "apply") and any(is_guard_path(a, gcwd) for a in rest if not a.startswith("-")):
        ask(f"git {sub} altera arquivo das travas ou da config do Claude Code.")


def check_gh(args):
    if args[:2] == ["repo", "delete"]:
        deny("gh repo delete.")
    # Na esteira, comentar/revisar no GitHub é só do despachante, depois da aprovação humana.
    if os.environ.get("ESTEIRA_HEADLESS") == "1":
        if args[:2] in (["pr", "review"], ["pr", "comment"], ["issue", "comment"]):
            deny(f"gh {' '.join(args[:2])} na sessão da esteira: publicar no GitHub é do despachante, "
                 "depois que o humano aprova no escritório.")
        if args[:1] == ["api"] and any(re.search(r"/(reviews|comments)(/|$)", a) for a in args[1:]):
            deny("gh api em reviews/comments na sessão da esteira: publicar no GitHub é do despachante.")
    if args[:2] == ["pr", "merge"] and "--admin" in args:
        deny("gh pr merge --admin (pula branch protection).")
    if args[:1] == ["api"]:
        method = None
        for i, a in enumerate(args):
            if a in ("-X", "--method") and i + 1 < len(args):
                method = args[i + 1]
            elif a.startswith("--method="):
                method = a.split("=", 1)[1]
            elif a.startswith("-X") and len(a) > 2:
                method = a[2:]
        if method and method.upper() in ("DELETE", "PATCH", "PUT"):
            deny(f"gh api com método {method.upper()}.")


def check_terraform(args):
    rest = [a for a in args if not a.startswith("-chdir")]
    sub = rest[0] if rest else ""
    if sub in TERRAFORM_READONLY:
        return
    if sub in TERRAFORM_READONLY_SUB:
        op = rest[1] if len(rest) > 1 else ""
        if op in TERRAFORM_READONLY_SUB[sub]:
            return
        deny(f"terraform {sub} {op} altera estado. Neste servidor terraform é só plan/validate/fmt/show.")
    deny(f"terraform {sub or '(sem subcomando)'}. Neste servidor terraform é só plan/validate/fmt/show; apply e afins mexem na infra de produção.")


def check_simple(argv, cwd):
    argv = strip_redirects(argv, cwd)
    while argv and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", argv[0]):
        name = argv[0].split("=", 1)[0]
        if protected_env(name):
            deny(f"define {name} (reservado: injeção de config do git ou push humano).")
        argv = argv[1:]
    while argv and os.path.basename(argv[0]) in ("sudo", "env", "command", "nohup", "time", "exec", "nice", "xargs"):
        wrapper = os.path.basename(argv[0])
        argv = argv[1:]
        while argv and (argv[0].startswith("-") or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", argv[0])):
            tok = argv.pop(0)
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok) and protected_env(tok.split("=", 1)[0]):
                deny(f"define {tok.split('=', 1)[0]} (reservado).")
            if wrapper == "env" and tok in ("-u", "--unset") and argv:
                if protected_env(argv[0]):
                    deny(f"env -u {argv[0]} (desliga a injeção do hooksPath da trava).")
                argv.pop(0)
            elif wrapper == "env" and tok.startswith(("-u", "--unset=")) and protected_env(tok.split("=", 1)[-1].removeprefix("-u")):
                deny("env -u em variável reservada.")
    if not argv:
        return cwd
    prog = os.path.basename(argv[0])
    args = argv[1:]

    if prog == "cd":
        return resolve(args[0], cwd) if args else os.path.expanduser("~")
    if prog in ("export", "declare", "typeset", "readonly", "local", "unset"):
        for a in args:
            if protected_env(a.split("=", 1)[0]):
                deny(f"{prog} {a.split('=', 1)[0]} (variável reservada das travas).")
        return cwd
    if prog in ("bash", "sh", "zsh", "dash") and "-c" in args:
        i = args.index("-c")
        if i + 1 < len(args):
            check_command(args[i + 1], cwd)
        return cwd
    if prog == "eval":
        check_command(" ".join(args), cwd)
        return cwd

    if prog == "git":
        check_git(args, cwd)
    elif prog == "gh":
        check_gh(args)
    elif prog in ("terraform", "tofu"):
        check_terraform(args)
    else:
        check_file_writes(prog, args, cwd)
    return cwd


def check_command(cmd, cwd):
    for argv in split_commands(cmd):
        cwd = check_simple(argv, cwd)


def main():
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    cwd = data.get("cwd") or os.getcwd()
    if tool == "Bash":
        check_command(inp.get("command", ""), cwd)
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = inp.get("file_path") or inp.get("notebook_path") or ""
        if path and is_guard_path(path, cwd):
            ask(f"edição de {path}, que faz parte das travas ou da config do git/Claude Code.")
    sys.exit(0)


if __name__ == "__main__":
    main()
