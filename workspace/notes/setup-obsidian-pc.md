# Setup do Obsidian no PC (Windows)

Objetivo: o vault do Obsidian no PC é um clone do `~/workspace` do servidor. Você edita no Obsidian, o plugin Git sincroniza com `leme-lab:git/workspace.git`, e o Claude no servidor puxa no início de cada sessão e envia `memory/` e `notes/` no fim de cada resposta.

Tudo pela rede de casa. Nada passa pelo GitHub.

## 1. Git for Windows

No PowerShell:

```powershell
winget install --id Git.Git -e
```

Feche e abra o PowerShell de novo e confira com `git --version`.

## 2. Chave SSH do PC

O Windows 10/11 já traz o cliente OpenSSH. No PowerShell:

```powershell
ssh-keygen -t ed25519 -C "pc-windows-leme-lab" -f "$HOME\.ssh\id_ed25519_leme_lab"
```

Pode deixar sem passphrase (Enter duas vezes); a chave só abre o usuário `leme` do servidor, que não tem sudo. Se preferir com passphrase, o Obsidian Git vai precisar do ssh-agent do Windows rodando.

Mostre a pública:

```powershell
Get-Content "$HOME\.ssh\id_ed25519_leme_lab.pub"
```

**Cole essa linha no chat do Claude no servidor.** Ele adiciona em `~/.ssh/authorized_keys` do `leme`.

## 3. `Host leme-lab` no `~/.ssh/config` do Windows

Abra (ou crie) o arquivo `C:\Users\<voce>\.ssh\config`, sem extensão:

```powershell
notepad "$HOME\.ssh\config"
```

Conteúdo:

```
Host leme-lab
  HostName 192.168.1.173
  User leme
  IdentityFile ~/.ssh/id_ed25519_leme_lab
  IdentitiesOnly yes
```

Teste (na primeira vez ele pergunta se confia no servidor: responda `yes`):

```powershell
ssh leme-lab "echo ok"
```

Tem que aparecer `ok`, sem pedir senha.

## 4. Clonar o vault

```powershell
cd $HOME\Documents
git clone leme-lab:git/workspace.git leme-workspace
cd leme-workspace
git config user.name "Glauco (PC)"
git config user.email "glauco.lomenha@leme.tec.br"
```

O nome "Glauco (PC)" deixa claro no histórico o que veio do Obsidian e o que veio do servidor ("Leme bot").

O repo já traz um `.gitattributes` com quebra de linha LF, então o Windows não vai converter os arquivos.

## 5. Abrir como vault

No Obsidian: **Open folder as vault** e escolha `Documents\leme-workspace`.

O `.obsidian/` já vem com a config compartilhada (`repos/` e `_import/` excluídos da busca). O que o Obsidian cria sozinho (`workspace.json`, cache, plugins instalados) fica fora do git.

## 6. Plugin Obsidian Git

1. **Settings > Community plugins > Turn on community plugins.**
2. **Browse**, procure **Git** (autor Vinzent), **Install** e **Enable**.
3. Em **Settings > Git**, ajuste:

| Opção | Valor |
|---|---|
| Pull on startup | ligado |
| Auto commit-and-sync interval (minutes) | `5` |
| Auto pull interval (minutes) | `5` |
| Sync method | **Rebase** |
| Push on commit-and-sync | ligado |
| Pull on commit-and-sync | ligado |
| Commit message on auto commit-and-sync | `vault: {{date}}` |

Ligar o plugin muda o `.obsidian/community-plugins.json`. Isso é esperado e vai no próximo commit.

Teste: crie uma nota em `notes/inbox/`, rode **Ctrl+P > Git: Commit-and-sync**, e peça ao Claude no servidor para conferir se ela chegou.

## 7. Se der conflito

Conflito só acontece quando você e o Claude mexem **no mesmo trecho do mesmo arquivo** entre dois syncs. É raro, porque o Claude escreve quase sempre em `memory/` e você em `notes/`.

Quando acontecer, o plugin avisa e lista os arquivos em conflito. Dentro deles aparecem marcadores assim:

```
a versão do outro lado
```

1. Abra cada arquivo listado, fique com o texto certo e **apague as três linhas de marcador**.
2. **Ctrl+P > Git: Commit-and-sync.**

Se não souber o que escolher ou se travar no meio de um rebase, abra o **Git Bash** na pasta do vault e rode:

```bash
git status
git rebase --abort   # só se o status disser que há um rebase em andamento
```

Isso volta ao estado antes do sync, sem perder nada. Depois peça ajuda ao Claude no servidor.

**Nunca use force push nem "discard changes" para sair de um conflito.** O repo do servidor recusa force push e deleção de branch de qualquer jeito; se o push for recusado, é sinal de que falta um pull, não de que precisa forçar.

Do lado do servidor, se o Claude encontrar conflito ele aborta o rebase, não força nada e te avisa na hora.
