# LM-2903: script que preenche o Manual de uso

Gerado do código do leme-app (`origin/main`): 18 artigos ganham "Passo a passo", mais 24 guias e 17 dúvidas novos, 252 etapas. Validado com o leitor do próprio app numa simulação: 42/42 guias com etapas idênticas ao código e 17/17 dúvidas.

> **Versão 4 (12/11):** reorganiza o Doc nas 8 categorias do app (os 23 artigos atuais são movidos, sem mudar o texto). Para conferir no editor: Ctrl+F `nas 8 categorias do app`. Apague as cópias "ENSAIO" antigas e rode o ensaio de novo com este código.

## Como rodar (uns 5 minutos)

1. Logado na conta que **edita** o Doc "Manual de uso", abra https://script.google.com e clique em **Novo projeto**.
2. Apague o que vier no editor, cole **todo** o bloco de código abaixo e salve (Ctrl+S).
3. Na barra de cima, escolha a função **`ensaio`** e clique em **Executar**. Na primeira vez o Google pede autorização (Docs e Drive): aceite.
4. No **Registro de execução** aparece "ENSAIO PRONTO. Mande este link: ...". **Mande o link para o Claude.** O Doc de verdade não foi tocado: o ensaio mexe só numa cópia.
5. Depois do OK do Claude: avise a Let e o CS e rode a função **`aplicar`** no mesmo editor. Ela guarda um backup do Doc antes de preencher, e se for rodada duas vezes não duplica nada.

## Script

```javascript
/**
 * Reorganiza o "Manual de uso" nas 8 categorias do app e preenche com o texto do código (LM-2903).
 * - Os 23 artigos que já existem são MOVIDOS para a categoria do app, com todo o conteúdo (texto,
 *   imagens, tabelas), sem mudar uma letra. 18 deles ganham o "Passo a passo" no fim.
 * - 24 guias e 17 dúvidas que só existiam no código entram como artigos novos.
 * - O que vem antes da primeira categoria (título, sumário) fica como está.
 * O Doc novo é montado no fim e só depois a parte antiga sai: se der erro no meio, nada se perde.
 *
 * 1) ensaio(): faz uma CÓPIA, reorganiza a cópia e mostra o link no registro. Mande o link.
 * 2) Depois do OK, aplicar(): guarda um BACKUP e reorganiza o Doc de verdade.
 * Depois, no Doc: clique no sumário e no ícone de atualizar (ele aponta para os títulos antigos).
 */
const DOC_ID = "1RYVeg7km-6PIZbq4sEGQaAMp_Iw-3_uF8PusJrRFJTY";
const QUEBRA = "\n"; // quebra de linha DENTRO do item (Shift+Enter): medido no ensaio, o export recua a continuação
const H = DocumentApp.ParagraphHeading;
const T = DocumentApp.ElementType;

function ensaio() {
  const copia = DriveApp.getFileById(DOC_ID).makeCopy("Manual de uso - ENSAIO da colagem " + carimbo());
  try {
    copia.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  } catch (e) {
    Logger.log("Não consegui deixar a cópia aberta por link. Abra a cópia e deixe 'qualquer pessoa com o link: leitor'.");
  }
  const r = preencher(DocumentApp.openById(copia.getId()));
  Logger.log("ENSAIO PRONTO. Mande este link: " + copia.getUrl());
  Logger.log(r);
}

function aplicar() {
  const backup = DriveApp.getFileById(DOC_ID).makeCopy("Manual de uso - BACKUP antes da colagem " + carimbo());
  Logger.log("Backup do Doc original: " + backup.getUrl());
  const r = preencher(DocumentApp.openById(DOC_ID));
  Logger.log("DOC REORGANIZADO. " + r + " Agora atualize o sumário do Doc (clique nele, ícone de atualizar).");
}

function carimbo() {
  return Utilities.formatDate(new Date(), "America/Sao_Paulo", "dd/MM/yyyy HH:mm");
}

function ehTitulo(el) {
  if (el.getType() !== T.LIST_ITEM) return null;
  const h = el.asListItem().getHeading();
  if (h === H.HEADING1) return "categoria";
  if (h === H.HEADING2 || h === H.HEADING3) return "artigo";
  return null;
}

function preencher(doc) {
  const body = doc.getBody();
  if (/^\s*Passo a passo\s*$/m.test(body.getText())) {
    throw new Error("Este documento já tem 'Passo a passo': a reorganização já foi feita. Nada foi alterado.");
  }

  // 1) Mapeia os artigos atuais: título -> elementos do conteúdo. Confere tudo antes de mexer.
  const blocos = {};
  let primeiraCat = -1, atual = null;
  for (let i = 0; i < body.getNumChildren(); i++) {
    const el = body.getChild(i), tipo = ehTitulo(el);
    if (tipo === "categoria") { if (primeiraCat < 0) primeiraCat = i; atual = null; continue; }
    if (primeiraCat < 0) continue; // título e sumário: ficam como estão
    if (tipo === "artigo") {
      atual = el.asListItem().getText().trim();
      if (blocos[atual]) throw new Error("Artigo repetido no Doc: " + atual + ". Nada foi alterado.");
      blocos[atual] = [];
      continue;
    }
    if (!atual) {
      if (el.getText && el.getText().trim()) throw new Error("Texto fora de artigo depois de uma categoria: \"" + el.getText().slice(0, 60) + "\". Nada foi alterado.");
      continue;
    }
    if ([T.PARAGRAPH, T.LIST_ITEM, T.TABLE].indexOf(el.getType()) < 0) {
      throw new Error("Elemento que eu não sei mover (" + el.getType() + ") em \"" + atual + "\". Nada foi alterado.");
    }
    blocos[atual].push(el);
  }
  if (primeiraCat < 0) throw new Error("Não achei as categorias do Doc. Nada foi alterado.");
  const noPlano = [];
  PLANO.forEach(c => c.itens.forEach(it => { if (it.tipo === "mover") noPlano.push(it.titulo); }));
  const semArtigo = noPlano.filter(t => !blocos[t]);
  const semLugar = Object.keys(blocos).filter(t => noPlano.indexOf(t) < 0);
  if (semArtigo.length) throw new Error("Não achei no Doc (nada foi alterado): " + semArtigo.join(" | "));
  if (semLugar.length) throw new Error("Artigos do Doc sem lugar no plano (nada foi alterado): " + semLugar.join(" | "));

  // 2) Monta o Doc novo no fim, nas categorias do app.
  const n0 = body.getNumChildren();
  const sep = () => body.appendParagraph("").setHeading(H.NORMAL);
  const titulo = (texto, nivel, lista) => {
    const li = body.appendListItem(texto);
    li.setHeading(nivel);
    if (lista) li.setListId(lista);
    li.setGlyphType(DocumentApp.GlyphType.NUMBER);
    li.setNestingLevel(0);
    return li;
  };
  let listaCat = null, etapas = 0, movidos = 0;
  PLANO.forEach(c => {
    sep();
    const ci = titulo(c.categoria, H.HEADING1, listaCat);
    if (!listaCat) listaCat = ci;
    sep();
    let listaArt = null;
    c.itens.forEach(it => {
      const ai = titulo(it.titulo, H.HEADING2, listaArt);
      if (!listaArt) listaArt = ai;
      sep();
      if (it.tipo === "mover") {
        blocos[it.titulo].forEach(el => {
          const t = el.getType();
          if (t === T.PARAGRAPH) body.appendParagraph(el.copy());
          else if (t === T.LIST_ITEM) body.appendListItem(el.copy());
          else body.appendTable(el.copy());
        });
        movidos++;
        if (it.passos) { anexaPassos(body, it.passos); etapas += it.passos.length; }
      } else if (it.tipo === "guia") {
        escreve(body.appendParagraph("").setHeading(H.NORMAL), it.descricao);
        anexaPassos(body, it.passos);
        etapas += it.passos.length;
      } else {
        anexaBlocos(body, it.blocos);
      }
      sep();
    });
  });

  // 3) Só agora a parte antiga sai (de trás para frente, para os índices não mudarem).
  for (let i = n0 - 1; i >= primeiraCat; i--) body.removeChild(body.getChild(i));
  return movidos + " artigos movidos, " + etapas + " etapas, " + PLANO.length + " categorias.";
}

function anexaPassos(body, passos) {
  body.appendParagraph("").setHeading(H.NORMAL);
  escreve(body.appendParagraph("").setHeading(H.NORMAL), "**Passo a passo**");
  let lista = null;
  passos.forEach(linhas => {
    const li = body.appendListItem("");
    li.setHeading(H.NORMAL);
    if (lista) li.setListId(lista); else lista = li;
    li.setGlyphType(DocumentApp.GlyphType.NUMBER);
    li.setNestingLevel(0);
    escreve(li, linhas.join(QUEBRA));
  });
  body.appendParagraph("").setHeading(H.NORMAL);
}

function anexaBlocos(body, blocos) {
  let lista = null, glyph = null;
  blocos.forEach(b => {
    if (b.tipo === "p") {
      lista = null;
      escreve(body.appendParagraph("").setHeading(H.NORMAL), b.texto);
      return;
    }
    const g = b.tipo === "num" ? DocumentApp.GlyphType.NUMBER : DocumentApp.GlyphType.BULLET;
    if (glyph !== g) lista = null;
    if (!lista) body.appendParagraph("").setHeading(H.NORMAL);
    const li = body.appendListItem("");
    li.setHeading(H.NORMAL);
    if (lista) li.setListId(lista); else lista = li;
    li.setGlyphType(g);
    li.setNestingLevel(0);
    glyph = g;
    escreve(li, b.texto);
  });
}

/** Texto com **negrito** do código vira negrito de verdade no Docs. */
function escreve(el, md) {
  const partes = md.split("**");
  const plano = partes.join("");
  if (!plano) return;
  el.setText(plano);
  const t = el.editAsText();
  t.setBold(0, plano.length - 1, false);
  let pos = 0;
  partes.forEach((p, k) => {
    if (k % 2 === 1 && p.length) t.setBold(pos, pos + p.length - 1, true);
    pos += p.length;
  });
}

const PLANO = [
 {
  "categoria": "PRIMEIROS PASSOS",
  "itens": [
   {
    "tipo": "mover",
    "titulo": "Apresentação",
    "passos": null
   },
   {
    "tipo": "mover",
    "titulo": "Visão Geral",
    "passos": null
   },
   {
    "tipo": "guia",
    "titulo": "Como entrar na plataforma",
    "descricao": "Entre com o seu e-mail e a sua senha, e veja o que fazer se esquecer a senha.",
    "passos": [
     [
      "Escreva seu e-mail",
      "Na caixinha **Email**, escreva o e-mail do seu cadastro. Pode usar letras maiúsculas ou minúsculas: a plataforma acerta para você."
     ],
     [
      "Escreva sua senha",
      "Na caixinha **Senha**, escreva a sua senha. Para conferir o que escreveu, clique no desenho de um olho."
     ],
     [
      "Entre",
      "Clique em **Acessar**. Se faltar alguma coisa, a tela avisa embaixo da caixinha, por exemplo: **É necessário preencher a senha**."
     ],
     [
      "Entrou por um link?",
      "Se você abriu um endereço da plataforma sem ter entrado, vai aparecer **Faça login para continuar**. Depois de entrar, você vai direto para a página daquele endereço."
     ],
     [
      "Esqueceu a senha?",
      "Clique em **Esqueci minha senha** e siga o passo a passo para criar uma nova."
     ],
     [
      "Precisa de ajuda?",
      "Clique em **Ajuda** para conversar com o suporte pelo WhatsApp."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Esqueci minha senha: como criar uma nova",
    "descricao": "Peça o e-mail de recuperação, crie a nova senha e entre de novo, mesmo sem estar conectada.",
    "passos": [
     [
      "Peça a recuperação",
      "Na tela de entrada, clique em **Esqueci minha senha**."
     ],
     [
      "Escreva o e-mail",
      "Na tela **Esqueceu sua senha?**, escreva o e-mail do seu cadastro e clique em **Redefinir senha**."
     ],
     [
      "Leia o aviso",
      "A plataforma volta para a tela de entrada e mostra: **Se uma conta estiver registrada com este endereço de e-mail, você receberá instruções para redefinir sua senha.** Esse aviso não diz se o e-mail está cadastrado ou não."
     ],
     [
      "Abra o e-mail que chegou",
      "Abra o e-mail que você recebeu e clique no botão ou no endereço que vem nele, para criar a nova senha. Se não funcionar, peça outro em **Esqueci minha senha**."
     ],
     [
      "Crie a nova senha",
      "Na tela **Crie uma senha que será usada para acessar o sistema**, escreva a **Senha:** e repita em **Confirme sua senha:**. Ela precisa ter pelo menos 8 caracteres, com uma letra minúscula, uma maiúscula e um número."
     ],
     [
      "Salve",
      "Clique em **Redefinir senha**. Vai aparecer o aviso **Senha criada com sucesso** e a plataforma volta para a tela de entrada."
     ],
     [
      "Entre com a nova senha",
      "Na tela de entrada, escreva o seu e-mail e a nova senha. A plataforma não entra sozinha depois de criar a senha."
     ],
     [
      "Já estava conectada?",
      "Se você abrir o e-mail com a plataforma já aberta e conectada, ela leva você direto para o painel, sem mostrar a tela de criar senha. Nesse caso, clique em **Sair**, no menu da sua foto, e abra o e-mail de novo."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como trocar a minha senha",
    "descricao": "Troque a senha de acesso à plataforma, sem precisar pedir ajuda a ninguém.",
    "passos": [
     [
      "Abra o menu da sua foto",
      "No alto da tela, clique no seu nome para abrir o menu. No celular, toque na sua foto."
     ],
     [
      "Abra o perfil",
      "No menu, clique em **Perfil**."
     ],
     [
      "Abra a guia de segurança",
      "Vai abrir uma janelinha por cima. Nela, clique na guia **Segurança**."
     ],
     [
      "Escreva as senhas",
      "Escreva a **Senha atual**. Depois escreva a **Nova senha** e repita a nova em **Confirmar nova senha**. A nova senha precisa ter pelo menos 8 caracteres, com uma letra minúscula, uma maiúscula e um número."
     ],
     [
      "Salve",
      "Clique no botão azul **Alterar senha**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Senha alterada com sucesso**. A janelinha fecha sozinha."
     ]
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "O que significa cada desenho da plataforma?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Alguns botões da plataforma têm só um desenho, sem nada escrito. Veja o que cada um faz:"
     },
     {
      "tipo": "bullet",
      "texto": "*Botão azul com um sinal de +*: serve para criar uma coisa nova (uma turma, um aluno, uma aula...)."
     },
     {
      "tipo": "bullet",
      "texto": "*Botão azul sem desenho* (como **Salvar**): guarda o que você escreveu."
     },
     {
      "tipo": "bullet",
      "texto": "*Botão vermelho com o desenho de uma lixeira*: serve para excluir. Pense bem antes de apertar: o que é excluído não volta."
     },
     {
      "tipo": "bullet",
      "texto": "*Lápis*: serve para mudar (editar) o que já está escrito."
     },
     {
      "tipo": "bullet",
      "texto": "*Três pontinhos*: abrem uma lista com outras opções, como transferir um aluno."
     },
     {
      "tipo": "bullet",
      "texto": "*Olho*, ao lado da senha: mostra o que você está digitando, para você conferir. Aperte de novo para esconder. Quando está mostrando, aparece **Ocultar senha**; quando está escondendo, aparece **Mostrar senha**."
     },
     {
      "tipo": "bullet",
      "texto": "*Seta para baixo ao lado de uma caixa*: a caixa abre uma lista. Escolha uma das opções."
     },
     {
      "tipo": "bullet",
      "texto": "*Chave com o desenho de um gráfico*, no alto da tela: liga e desliga o modo análise, que mostra gráficos."
     },
     {
      "tipo": "p",
      "texto": "Os avisos aparecem no canto de baixo da tela e somem sozinhos depois de alguns segundos. *Verde* quer dizer que deu certo. *Vermelho* quer dizer que não deu certo: leia o que está escrito e tente de novo."
     }
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Configurações e recursos",
    "passos": null
   },
   {
    "tipo": "mover",
    "titulo": "Perfis e Permissões",
    "passos": null
   }
  ]
 },
 {
  "categoria": "EQUIPE E ESCOLAS",
  "itens": [
   {
    "tipo": "mover",
    "titulo": "Como cadastrar usuários",
    "passos": [
     [
      "Escolha a escola",
      "Olhe a caixinha do alto da tela. Confira se a escola está certa. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se a escola está certa. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra a tela de cadastro",
      "Clique no botão azul **Novo usuário**, que tem um sinal de + ao lado do texto."
     ],
     [
      "Escreva o e-mail",
      "Comece pelo **Email**. Se a pessoa já tem cadastro na rede, os dados dela aparecem sozinhos quando você sai da caixinha."
     ],
     [
      "Preencha o resto",
      "Preencha **Nome completo**, **Cargo**, o telefone, a **Data de nascimento**, o **Sexo** e a **Raça/etnia**. CPF e RG são opcionais. As opções de **Cargo** dependem do seu acesso."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Usuário criado com sucesso**. A lista é atualizada. A pessoa passa a fazer parte da equipe da escola e poderá entrar na plataforma com o e-mail cadastrado."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como editar ou excluir uma pessoa da equipe",
    "descricao": "Corrija os dados de alguém da equipe ou tire essa pessoa da escola.",
    "passos": [
     [
      "Escolha a escola",
      "Olhe a caixinha do alto da tela. Confira se a escola está certa. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se a escola está certa. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra o cadastro",
      "Na lista, clique na linha da pessoa.",
      "No celular: Na lista, toque no nome da pessoa."
     ],
     [
      "Mude os dados",
      "Na guia **Pessoal**, mude o que precisar. As guias **Turmas** e **Formação** são só para consultar: nelas não dá para colocar a pessoa em uma turma."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar alterações**. Vai aparecer um aviso verde: **Usuário atualizado com sucesso**.",
      "No celular: Toque no botão azul **Salvar**. Vai aparecer um aviso verde: **Usuário atualizado com sucesso**."
     ],
     [
      "Para excluir",
      "No cadastro da pessoa, clique no botão vermelho **Excluir usuário**, que tem o desenho de uma lixeira.",
      "No celular: No cadastro da pessoa, toque no botão vermelho **Excluir**, que tem o desenho de uma lixeira."
     ],
     [
      "Confirme",
      "Leia o aviso: **Deleção de usuários é uma ação irreversível, tem certeza que deseja continuar?** Depois de excluir, não tem como voltar atrás. Para seguir, clique em **Deletar**. Vai aparecer um aviso verde: **Usuário deletado da escola com sucesso**."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como criar uma nova senha para alguém da equipe",
    "descricao": "Defina uma nova senha para alguém da equipe que perdeu o acesso.",
    "passos": [
     [
      "Escolha a escola",
      "Olhe a caixinha do alto da tela. Confira se a escola está certa. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se a escola está certa. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra o cadastro",
      "Na lista, clique na linha da pessoa.",
      "No celular: Na lista, toque no nome da pessoa."
     ],
     [
      "Resete a senha",
      "No alto da tela que abriu do lado, clique em **Resetar senha**. Esse botão só existe para quem já está cadastrada."
     ],
     [
      "Confirme",
      "Clique em **Resetar**. A própria tela explica: **Uma nova senha será definida para esse usuário e enviada por e-mail**."
     ],
     [
      "Confira",
      "Vai aparecer um aviso verde: **Senha resetada com sucesso**. Quem é da Secretaria de Educação vê a nova senha na própria tela, com a dica **Copie agora: ela some ao fechar esta gaveta.** Para os outros acessos, a senha vai só por e-mail."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como cadastrar uma escola",
    "descricao": "Cadastre uma escola da rede. O endereço aparece sozinho a partir do CEP.",
    "passos": [
     [
      "Abra a tela de cadastro",
      "Clique no botão azul **Nova escola**, que tem um sinal de + ao lado do texto."
     ],
     [
      "Diga qual é a escola",
      "Escreva o **Nome da escola**, com pelo menos 4 letras. O **INEP** é opcional."
     ],
     [
      "Escreva o CEP",
      "Escreva o **CEP**. Quando você completar os 8 números, a plataforma preenche sozinha a rua, o bairro, a cidade e o estado. Se o CEP não existir, vai aparecer **CEP não encontrado**."
     ],
     [
      "Complete o endereço",
      "Confira **Rua**, **Número**, **Bairro**, **Cidade** e **Estado**. O **Número** precisa ser preenchido quando a rua está preenchida."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Escola criada com sucesso!**"
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como editar ou excluir uma escola",
    "descricao": "Corrija os dados de uma escola ou exclua o cadastro dela.",
    "passos": [
     [
      "Abra a escola",
      "Na lista, clique na linha da escola. As escolas que aparecem mais apagadas não abrem para você editar."
     ],
     [
      "Mude os dados",
      "Mude o que precisar e clique no botão azul **Salvar alterações**. Vai aparecer um aviso verde: **Escola atualizada com sucesso!**",
      "No celular: Mude o que precisar e toque no botão azul **Salvar**. Vai aparecer um aviso verde: **Escola atualizada com sucesso!**"
     ],
     [
      "Para excluir",
      "No cadastro da escola, clique no botão vermelho **Excluir escola**, que tem o desenho de uma lixeira.",
      "No celular: No cadastro da escola, toque no botão vermelho **Excluir**, que tem o desenho de uma lixeira."
     ],
     [
      "Confirme",
      "Leia o aviso: **Deleção de escolas é uma ação irreversível, tem certeza que deseja continuar?** Depois de excluir, não tem como voltar atrás. Para seguir, clique em **Deletar**. Vai aparecer um aviso verde: **Escola deletada com sucesso!**"
     ]
    ]
   }
  ]
 },
 {
  "categoria": "TURMAS, HORÁRIOS E CALENDÁRIO",
  "itens": [
   {
    "tipo": "mover",
    "titulo": "Como criar turmas",
    "passos": [
     [
      "Escolha a escola",
      "No alto da tela, veja qual escola está escolhida. Se ainda não escolheu, escolha agora. Sem a escola, o botão de criar não funciona.",
      "No celular: No alto da tela, toque na caixinha da escola e veja qual está escolhida. Se ainda não escolheu, escolha agora. Sem a escola, o botão de criar não funciona."
     ],
     [
      "Confira o ano letivo",
      "Se a escola tem mais de um ano letivo, confira o ano na caixa ao lado do seu nome. Se tem um ano só, ele já vem escolhido.",
      "No celular: Se a escola tem mais de um ano letivo, confira o ano no menu da sua foto, no alto da tela. Se tem um ano só, ele já vem escolhido."
     ],
     [
      "Abra a tela de cadastro",
      "Clique no botão azul **Nova turma**, que tem um sinal de + ao lado do texto."
     ],
     [
      "Preencha os dados",
      "Vai abrir uma tela nova do lado. Preencha **Nome da turma**, **Capacidade** (um número de 1 a 100), **Nível**, **Horário** e **Tipo educacional**. Todas as linhas são obrigatórias."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Turma criada com sucesso!** A turma já fica na lista da escola."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como cadastrar a grade horária",
    "passos": [
     [
      "Escolha a escola e a turma",
      "No alto da tela, veja qual escola e qual turma estão escolhidas. A tela só deixa criar aulas quando o ano letivo está escolhido.",
      "No celular: No alto da tela, toque na caixinha da escola e da turma e veja as duas. A tela só deixa criar aulas quando o ano letivo está escolhido."
     ],
     [
      "Abra a tela de cadastro",
      "Clique no botão azul **Nova aula**, que tem um sinal de + ao lado do texto."
     ],
     [
      "Escolha disciplina e professor",
      "Vai abrir uma tela nova do lado, com o título **Nova aula**. A **Turma** já vem escolhida. Escolha a **Disciplina** e o **Professor(a)**."
     ],
     [
      "Defina o horário",
      "Em **Horário**, escolha o **Dia da semana** e escreva **Início** e **Fim**. Cada aula pode durar no máximo uma hora. Para colocar mais linhas de horário, use **Adicionar horário**. Para repetir a aula em vários dias de uma vez, escolha **Dias da semana** (de segunda a sexta) ou **Todos os dias** (de segunda a sábado)."
     ],
     [
      "Validade, se precisar",
      "Deixe **Válido a partir de** e **Válido até** em branco. Assim, a aula vale em qualquer semana."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Dados criados com sucesso**. Se você criou várias aulas de uma vez, o aviso será **Aulas criadas com sucesso**. A aula já aparece na grade."
     ],
     [
      "Ver por professor",
      "Você também pode ver a grade **Por professor**. Nesse modo, o botão **Nova aula** só fica disponível depois que você escolhe o professor."
     ],
     [
      "Por que a grade importa",
      "As matérias de Conteúdos, Notas e Avaliações vêm da grade horária da turma. Sem aula cadastrada, essas telas ficam sem matéria. Se a Frequência disser que não há aula num dia, confira também a grade."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como editar ou excluir uma aula da grade",
    "descricao": "Mude o professor, a disciplina ou o horário de uma aula, ou exclua a aula.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "No alto da tela, veja qual escola e qual turma estão escolhidas.",
      "No celular: No alto da tela, toque na caixinha da escola e da turma e veja as duas."
     ],
     [
      "Abra a aula",
      "Na grade, clique no quadrinho da aula. Vai abrir uma tela nova do lado, com o título **Alterar aula**.",
      "No celular: Na grade, toque no quadrinho da aula. Vai abrir uma tela nova, com o título **Alterar aula**."
     ],
     [
      "Altere os dados",
      "Mude o que precisar e clique no botão azul **Salvar alterações**. Vai aparecer um aviso verde: **Dados Atualizados com sucesso**.",
      "No celular: Mude o que precisar e toque no botão azul **Salvar**. Vai aparecer um aviso verde: **Dados Atualizados com sucesso**."
     ],
     [
      "Mudar de dia ou horário",
      "No computador, também dá para arrastar o quadrinho da aula para outro dia ou outro horário.",
      "No celular: não tem"
     ],
     [
      "Para excluir",
      "Na tela da aula, clique no botão vermelho **Excluir aula**, que tem o desenho de uma lixeira.",
      "No celular: Na tela da aula, toque no botão vermelho **Excluir**, que tem o desenho de uma lixeira."
     ],
     [
      "Confirme",
      "Vai abrir uma janelinha por cima com este aviso: **Deleção de aulas é uma ação irreversível, tem certeza que deseja continuar?** Depois de excluir, não tem como voltar atrás. Para seguir, clique em **Deletar**. Vai aparecer um aviso verde: **Dados excluídos com sucesso**."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como cadastrar um atendimento na agenda do AEE",
    "descricao": "Monte a agenda semanal de atendimentos do AEE (Atendimento Educacional Especializado): aluno, professor, dia e horário.",
    "passos": [
     [
      "Escolha a turma de AEE",
      "No alto da tela, escolha a escola e a turma de AEE (Atendimento Educacional Especializado). O nome do item do menu vai mudar para Agendamentos.",
      "No celular: No alto da tela, toque na caixinha da escola e da turma e escolha a turma de AEE (Atendimento Educacional Especializado)."
     ],
     [
      "Abra a tela de cadastro",
      "Clique no botão azul **Novo atendimento**, que tem um sinal de + ao lado do texto. Se a turma ainda não tem alunos, o botão não funciona.",
      "No celular: Toque em **Novo atendimento** ou, no quadrinho do aluno, em **Adicionar atendimento**."
     ],
     [
      "Preencha",
      "Vai abrir uma tela nova do lado. Escolha o **Aluno**, o **Professor** e o **Dia da semana**. Depois escreva **Início** e **Fim**. **O atendimento se repete toda semana nesse dia.** Pode ser de segunda a sexta e dura no máximo uma hora."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Vai aparecer um aviso verde: **Atendimento adicionado**."
     ],
     [
      "Se o professor já atende o aluno",
      "Se o mesmo professor já atende esse aluno naquele horário, vai aparecer o aviso **Atendimento repetido**. Só continue em **Cadastrar mesmo assim** se for isso mesmo que você quer."
     ],
     [
      "Editar ou remover",
      "Para editar, clique no atendimento na agenda. Depois de **Salvar alterações**, vai aparecer o aviso **Atendimento atualizado**. Para tirar da agenda, abra o atendimento, clique em **Remover atendimento** e depois em **Remover**. Vai aparecer o aviso **Atendimento removido**."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como cadastrar o sábado letivo",
    "passos": [
     [
      "Escolha a escola e a turma",
      "No alto da tela, veja qual escola e qual turma do sábado letivo estão escolhidas.",
      "No celular: No alto da tela, toque na caixinha da escola e da turma e veja as duas."
     ],
     [
      "Abra a tela de cadastro",
      "Clique no botão azul **Nova aula**, que tem um sinal de + ao lado do texto."
     ],
     [
      "Escolha o dia",
      "Em **Dia da semana**, escolha **Sábado**."
     ],
     [
      "Informe a data",
      "Em **Válido a partir de** e **Válido até**, escreva a data do sábado letivo nas duas linhas. A aula só aparece na grade da semana desse sábado."
     ],
     [
      "Complete a aula",
      "Escolha a **Disciplina**, o **Professor(a)** e o horário, do mesmo jeito que em Como cadastrar uma aula na grade horária."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como criar eventos no calendário",
    "passos": [
     [
      "Escolha a escola",
      "No alto da tela, veja qual escola e qual ano letivo estão escolhidos. Sem eles, a tela só mostra um aviso pedindo que você escolha.",
      "No celular: No alto da tela, toque na caixinha da escola e veja qual está escolhida. Sem ela, a tela só mostra um aviso pedindo que você escolha."
     ],
     [
      "Abra a tela de cadastro",
      "Clique no botão azul **Novo evento**, que tem um sinal de + ao lado do texto."
     ],
     [
      "Tipo e datas",
      "Vai abrir uma tela nova do lado. Escolha o tipo em **Selecione o evento**. Depois escolha as datas em **Data de início** e **Data de término**. Se o evento dura um dia só, marque **Evento com duração de um dia?**"
     ],
     [
      "Dia letivo",
      "Em **Dia letivo**, escolha **Letivo** ou **Não letivo**."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa.",
      "No celular: Toque no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Evento criado com sucesso**. O evento entra no mês com a cor do tipo e a indicação **Letivo** ou **Não letivo**. No celular, ele vira uma barra colorida: toque nela para abrir.",
      "No celular: Pronto! Vai aparecer um aviso verde: **Evento criado com sucesso**. O evento vira uma barra colorida no mês: toque nela para abrir."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como editar ou excluir um evento do calendário",
    "descricao": "Corrija um evento que você já criou, ou exclua o evento.",
    "passos": [
     [
      "Escolha a escola",
      "No alto da tela, veja qual escola e qual ano letivo estão escolhidos.",
      "No celular: No alto da tela, toque na caixinha da escola e veja qual está escolhida."
     ],
     [
      "Abra o evento",
      "No calendário, clique no evento. Vai abrir uma tela nova do lado, com o título **Editar evento**.",
      "No celular: Toque na barra colorida do evento. Vai abrir uma tela nova, com o título **Editar evento**."
     ],
     [
      "Altere e salve",
      "Mude o que precisar e clique no botão azul **Salvar alterações**. Vai aparecer um aviso verde: **Evento atualizado com sucesso**.",
      "No celular: Mude o que precisar e toque no botão azul **Salvar**. Vai aparecer um aviso verde: **Evento atualizado com sucesso**."
     ],
     [
      "Para excluir",
      "Não dá para excluir pela tela de edição. Clique em **Eventos**, na barra. Procure o evento na lista e clique no desenho de uma lixeira (**Deletar evento**)."
     ],
     [
      "Confirme",
      "Vai abrir uma janelinha por cima pedindo a confirmação. Depois de excluir, não tem como voltar atrás. Para seguir, clique em **Deletar**. Vai aparecer um aviso verde: **Evento deletado com sucesso**."
     ]
    ]
   }
  ]
 },
 {
  "categoria": "ALUNOS",
  "itens": [
   {
    "tipo": "mover",
    "titulo": "Como cadastrar os alunos",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra a tela de cadastro",
      "Clique em **Novo aluno**: é o botão azul com um sinal de + ao lado do texto. Ele só aparece com uma turma escolhida e numa escola que você pode editar."
     ],
     [
      "Documentos e dados",
      "Vai abrir uma tela nova do lado, chamada **Cadastrar estudante**. Preencha o **CPF**, o **Nome completo**, a **Data de nascimento**, o **Sexo** e a **Raça/etnia**. Todos são obrigatórios."
     ],
     [
      "Matrícula",
      "Em **Matrícula**, escolha o **Número na chamada**. Só aparecem números livres. Escolha também a data de início. A escola e a turma já vêm preenchidas."
     ],
     [
      "O que é opcional",
      "Endereço e as outras partes são opcionais. Se você digitar o **CEP**, a plataforma preenche rua, bairro, cidade e estado. Se preencher o **RG**, passam a ser obrigatórias a data de emissão e a UF."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Estudante criado(a) com sucesso!** A lista da turma é atualizada e o aluno entra como Ativo."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como transferir um aluno para outra escola",
    "descricao": "Passe um aluno para outra escola, escolhendo a turma onde ele vai ficar, e veja quando usar o remanejamento.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra o menu do aluno",
      "Na linha do aluno, clique nos três pontinhos (⋯), do lado direito. Só funciona para aluno cuja situação é Ativo ou Aprovado. Essa coluna só aparece nas escolas que você pode editar."
     ],
     [
      "Escolha a transferência",
      "Na lista que abriu, clique em **Transferir para**."
     ],
     [
      "Escolha o destino",
      "Escolha a escola para onde o aluno vai e, depois, a turma. Só aparecem as escolas que você pode editar."
     ],
     [
      "Confirme",
      "Vai abrir uma janelinha por cima, pedindo a confirmação. Clique em **Transferir**."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Aluno transferido com sucesso**"
     ],
     [
      "Mudar de turma na mesma escola",
      "Para mudar o aluno de turma dentro da mesma escola, use **Remanejar para**, na mesma lista. Atenção: a mudança acontece assim que você clica na turma, sem pedir confirmação."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como mudar o número de chamada do aluno",
    "descricao": "A lista de chamada segue o número de cada aluno. Para mudar a posição dele, mude o número.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra a ficha do aluno",
      "Na lista, clique na linha do aluno para abrir a ficha dele."
     ],
     [
      "Abra a guia Pessoal",
      "Na ficha, abra a guia **Pessoal**."
     ],
     [
      "Comece a editar",
      "Clique em **Editar dados pessoais**. Esse botão só aparece nas escolas que você pode editar."
     ],
     [
      "Escolha o número",
      "Na caixa **Número na chamada**, escolha o novo número. Só aparecem números livres, de 1 a 50. Para trocar dois alunos de lugar, mude primeiro um deles para um número livre."
     ],
     [
      "Salve",
      "Clique em **Salvar alterações**.",
      "No celular: Toque no botão azul **Salvar**."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Estudante atualizado(a) com sucesso!**"
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como mudar a situação do aluno",
    "descricao": "Aprove, reprove ou reclassifique um aluno, e veja o que acontece com a matrícula dele.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra o menu do aluno",
      "Na linha do aluno, clique nos três pontinhos (⋯), do lado direito. Só funciona para aluno cuja situação é Ativo ou Aprovado."
     ],
     [
      "Aprovar ou reprovar",
      "Na lista que abriu, clique em **Aprovado** ou em **Reprovado**."
     ],
     [
      "Informe a data e avance",
      "Escreva a data em que a matrícula termina e clique em **Avançar**. A própria tela lembra: só marque depois que todos os resultados finais estiverem fechados."
     ],
     [
      "Escolha o que fazer no próximo ano",
      "Na segunda etapa, escolha **Sim, criar matrícula no próximo ano** (e a turma) ou **Não, apenas aprovar**, e clique em **Confirmar**. Para reprovar, a opção é **Não, apenas reprovar**. Se a escola ainda não tem o ano seguinte cadastrado, vai aparecer o aviso **Próximo ano letivo não encontrado. Não é possível criar matrícula automaticamente.**"
     ],
     [
      "Reclassificar",
      "Para reclassificar, clique em **Reclassificado**, escreva a data, escolha a turma em **Selecione a turma de destino** e clique em **Reclassificar**. A própria tela explica que a matrícula antiga é encerrada e o aluno recebe uma nova."
     ],
     [
      "Outras situações",
      "As outras situações da lista pedem só a data em que a matrícula termina e um clique em **Finalizar**."
     ],
     [
      "Confira",
      "Vai aparecer um aviso verde: **Aluno aprovado com sucesso**, **Aluno reprovado com sucesso** ou **Aluno reclassificado com sucesso**. O aluno continua na lista, com a etiqueta da nova situação. A linha fica esmaecida, menos para Aprovado."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como enviar um aluno para o AEE (Atendimento Educacional Especializado)",
    "descricao": "Matricule um aluno numa turma de AEE sem tirar a matrícula dele da turma regular.",
    "passos": [
     [
      "Escolha a turma do aluno",
      "No topo da tela, confira a escola e a turma regular do aluno. Não escolha a turma de AEE."
     ],
     [
      "Abra o menu do aluno",
      "Na linha do aluno, clique nos três pontinhos (⋯), do lado direito. Só funciona para aluno cuja situação é Ativo ou Aprovado."
     ],
     [
      "Escolha o AEE",
      "Na lista que abriu, clique em **Enviar para AEE**. Essa opção só aparece se a escola tem uma turma de AEE no ano escolhido."
     ],
     [
      "Escolha a turma de AEE",
      "Na lista, escolha a turma de AEE do aluno."
     ],
     [
      "Confira",
      "Vai aparecer um aviso dizendo que o aluno foi enviado para a turma. A matrícula dele na turma regular continua ativa: o AEE é uma matrícula a mais."
     ],
     [
      "Se aparecer um aviso",
      "A plataforma avisa se o aluno já está nessa turma ou em outra turma de AEE. Se a turma não tiver número de chamada livre, vai aparecer o aviso **Esta turma de AEE não tem número de chamada livre**."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como cadastrar na turma de AEE (Atendimento Educacional Especializado) um aluno que já existe",
    "descricao": "Use os dados de um aluno já cadastrado na escola, em vez de escrever tudo de novo.",
    "passos": [
     [
      "Escolha a turma de AEE",
      "No topo da tela, confira a escola e a turma de AEE.",
      "No celular: No topo, toque nas caixinhas onde se escolhe a escola e a turma e confira a turma de AEE."
     ],
     [
      "Abra a tela de cadastro",
      "Clique em **Novo aluno**: é o botão azul com um sinal de + ao lado do texto."
     ],
     [
      "Digite o CPF",
      "Na parte **Documentos**, digite o **CPF** inteiro. Se já existe um aluno com esse CPF na escola, a plataforma avisa e mostra o botão **Usar os dados dele(a)**."
     ],
     [
      "Use os dados",
      "Clique em **Usar os dados dele(a)**. A tela de cadastro se preenche com os dados da pessoa. O **Número na chamada** e o início da matrícula ficam em branco, porque são desta turma."
     ],
     [
      "Número de chamada",
      "Escolha o **Número na chamada**. Só aparecem números livres."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Vai aparecer um aviso verde: **Estudante criado(a) com sucesso!**"
     ],
     [
      "Se você não usou os dados",
      "Se você salvar com um CPF que já existe, sem usar os dados dele(a), a plataforma pergunta em **Aluno já cadastrado**. A própria tela avisa que salvar atualiza o cadastro da pessoa em todas as turmas em que ela está matriculada. Só siga em **Salvar mesmo assim** se for isso mesmo."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como cadastrar um familiar do aluno",
    "descricao": "Registre os responsáveis e os contatos da família, na ficha do aluno.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra a ficha do aluno",
      "Na lista, clique no aluno (pode ser em qualquer parte da linha dele). A ficha dele vai abrir.",
      "No celular: Na lista, toque no nome do aluno. A ficha dele vai abrir."
     ],
     [
      "Abra a guia Família",
      "Na ficha, abra a guia **Família**."
     ],
     [
      "Novo familiar",
      "Clique em **Novo familiar**. Esse botão só aparece nas escolas que você pode editar."
     ],
     [
      "Preencha os dados",
      "Em **Dados pessoais** e **Contato**, preencha nome, data de nascimento, sexo, CPF, estado civil, grau de parentesco, telefone e e-mail. Todos são obrigatórios. O **Endereço (opcional)** pode ficar em branco."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Vai aparecer um aviso verde: **Familiar cadastrado com sucesso!**"
     ],
     [
      "Editar ou excluir",
      "Para mudar um dado, clique no lápis (**Editar familiar**) do familiar. Para remover, abra a edição e clique no botão vermelho, com uma lixeira, **Excluir familiar**."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como ver o histórico de matrículas de um aluno",
    "descricao": "Veja as escolas e as turmas por onde o aluno passou, na ficha dele.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra a ficha do aluno",
      "Na lista, clique no aluno (pode ser em qualquer parte da linha dele). A ficha dele vai abrir.",
      "No celular: Na lista, toque no nome do aluno. A ficha dele vai abrir."
     ],
     [
      "Abra a guia Matrícula",
      "Na ficha, abra a guia **Matrícula**."
     ],
     [
      "Leia o histórico",
      "Cada matrícula mostra a **Escola**, o **Tipo de ensino** e o **Início**. As que já terminaram mostram também o **Fim**. A mais recente fica aberta. Se aparecer **Nenhuma matrícula encontrada**, o aluno ainda não tem nenhum registro."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como emitir o questionário socioeconômico",
    "descricao": "Monte e imprima as folhas do questionário socioeconômico da turma, uma para cada aluno.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Marque os alunos",
      "Na primeira coluna da lista, marque os alunos. Para marcar a turma toda, clique em **Selecionar**, no alto dessa coluna."
     ],
     [
      "Abra o menu",
      "Clique em **Socioeconômico**. Se nenhuma turma estiver escolhida, o botão fica desativado, sem poder ser apertado."
     ],
     [
      "Gere os formulários",
      "Na lista que abriu, clique em **Gerar formulários**. Se nenhum aluno estiver marcado, essa opção fica desativada."
     ],
     [
      "Imprima",
      "Quando as folhas estiverem prontas, clique em **Imprimir**. Imprima em papel A4, no tamanho real (100%), sem ajustar à página."
     ],
     [
      "Depois de preenchidos",
      "Quando as folhas voltarem preenchidas, volte à tela de Alunos e use **Ler formulários preenchidos**, que fica no menu **Socioeconômico**, para fotografar cada folha."
     ]
    ]
   }
  ]
 },
 {
  "categoria": "ROTINA EM SALA DE AULA",
  "itens": [
   {
    "tipo": "mover",
    "titulo": "Como lançar frequência",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Confira o dia",
      "Olhe o dia no calendário. Ele já vem com a data de hoje. Não dá para escolher um dia que ainda não chegou."
     ],
     [
      "Marque só as faltas",
      "Na tabela, cada linha é um aluno e cada coluna é uma aula. Marque só quem faltou. Quem você não marcar conta como presente. A própria tela avisa: **Marque apenas as faltas. Campos desmarcados são considerados presença.**",
      "No celular: Cada aluno aparece num cartão. Toque no nome dele para abrir. Marque só as faltas. Se você não marcar nada, o aluno conta como presente."
     ],
     [
      "Falta no dia inteiro",
      "Se o aluno faltou o dia inteiro, marque a coluna **Dia todo**. Se ele faltou só em uma aula, marque apenas essa aula.",
      "No celular: Se o aluno faltou o dia inteiro, marque **Todas as aulas**. Se ele faltou só em uma matéria, marque apenas essa matéria."
     ],
     [
      "Salva sozinho",
      "Você não precisa apertar nenhum botão para salvar. O computador guarda sozinho cada marcação. Vai aparecer um aviso verde: **Falta salva com sucesso**"
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como lançar a frequência de uma turma de AEE",
    "descricao": "No Atendimento Educacional Especializado (AEE), a falta é marcada por atendimento. Só aparecem os alunos que têm atendimento no dia.",
    "passos": [
     [
      "Escolha a turma de AEE",
      "No alto da tela, escolha a escola e a turma de AEE (Atendimento Educacional Especializado). O menu passa a mostrar só as telas do AEE.",
      "No celular: No alto da tela, toque na caixinha de escola e turma e escolha a turma de AEE (Atendimento Educacional Especializado). O menu passa a mostrar só as telas do AEE."
     ],
     [
      "Entenda a tabela",
      "A tabela mostra os atendimentos do dia, com **Aluno**, **Professor**, **Horário** e **Falta**. Quem não tem atendimento nesse dia não aparece. A professora vê só os atendimentos dela."
     ],
     [
      "Confira o dia",
      "Olhe a data no calendário. Ela já vem com a data de hoje. Não dá para escolher um dia que ainda não chegou."
     ],
     [
      "Marque só as faltas",
      "Marque **Falta** só nos alunos que faltaram. Quem você não marcar conta como presente. A própria tela avisa: **Marque apenas as faltas. Campos desmarcados são considerados presença.**"
     ],
     [
      "Salva sozinho",
      "Você não precisa apertar nenhum botão para salvar. O computador guarda sozinho cada marcação. Ao marcar, vai aparecer o aviso **Falta registrada**. Ao desmarcar, **Presença registrada**. Se não salvar, clique em **Tentar de novo**."
     ],
     [
      "Se a tela estiver vazia",
      "Para a professora, vai aparecer **Você não tem atendimento neste dia.** Para a direção e a coordenação, **Nenhum atendimento agendado para este dia.** A agenda de atendimentos é cadastrada em Agendamentos."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como criar conteúdos",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra o formulário",
      "Clique no botão azul **Adicionar**. Ele fica desativado se você não escolheu uma turma. Para professora, também fica desativado se **Ver todas as turmas** estiver marcado. Na tela que mostra a semana (com os dias lado a lado), você também pode clicar numa aula marcada como **Sem conteúdo cadastrado**. Assim, a data, a matéria e a aula já vêm preenchidas."
     ],
     [
      "Preencha",
      "Na tela de cadastro, preencha a **Data**, a **Matéria**, as aulas, o **Título** e a **Descrição**. É preciso marcar pelo menos uma aula. A descrição precisa ter pelo menos 4 letras."
     ],
     [
      "Opcionais",
      "Se quiser, escolha o código da **BNCC** ou marque **Educação étnico-racial**. Você também pode anexar uma imagem ou um PDF de até 7 MB."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa. No computador, também dá para apertar as teclas Ctrl e Enter juntas.",
      "No celular: Toque no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Conteúdo criado com sucesso**"
     ],
     [
      "Saiu sem salvar?",
      "Não se preocupe: o que você escreveu fica guardado neste aparelho. Quando voltar, vai aparecer o aviso **Texto não salvo**. Aperte **Continuar** para seguir de onde parou."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como editar ou excluir um conteúdo",
    "descricao": "Corrija um conteúdo que já foi registrado. Também dá para excluir, duplicar ou copiar para outra turma.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra o conteúdo",
      "Clique no conteúdo. Ele aparece num quadradinho (um cartão) ou, na tela da semana, como uma aula. Ele abre primeiro só para você ler.",
      "No celular: Toque no conteúdo. Ele aparece num quadradinho (um cartão) ou como uma aula. Ele abre primeiro só para você ler."
     ],
     [
      "Edite",
      "Clique em **Editar**."
     ],
     [
      "Salve",
      "Mude o que precisar e clique no botão azul **Salvar alterações**. Vai aparecer um aviso verde: **Conteúdo atualizado com sucesso**",
      "No celular: Mude o que precisar e toque no botão azul **Salvar**. Vai aparecer um aviso verde: **Conteúdo atualizado com sucesso**"
     ],
     [
      "Para excluir",
      "Na tela de edição, clique no botão vermelho **Excluir**. Leia o aviso com calma: **Deleção de conteúdos é uma ação irreversível, tem certeza que deseja continuar?** Depois de excluir, não tem como voltar atrás. Para seguir, clique em **Deletar**. Vai aparecer um aviso verde: **Conteúdo deletado com sucesso**",
      "No celular: Na tela de edição, toque no botão vermelho **Excluir**. Leia o aviso com calma: **Deleção de conteúdos é uma ação irreversível, tem certeza que deseja continuar?** Depois de excluir, não tem como voltar atrás. Para seguir, toque em **Deletar**. Vai aparecer um aviso verde: **Conteúdo deletado com sucesso**"
     ],
     [
      "Cuidado com os três pontinhos do cartão",
      "Atenção! Quando os conteúdos aparecem em quadradinhos (cartões), cada um tem os três pontinhos (⋯), que abrem uma lista de opções. Ali também existe **Excluir**, mas esse apaga o conteúdo na hora, sem perguntar nada, e não tem como voltar atrás. Por isso, prefira excluir pelo caminho acima."
     ],
     [
      "Duplicar e copiar",
      "Na lista dos três pontinhos do cartão, **Duplicar** faz uma cópia na mesma turma. **Copiar para** leva o conteúdo para outra turma. O anexo não vai junto na cópia."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como marcar um conteúdo como conferido",
    "descricao": "A direção e a coordenação conferem o conteúdo que a professora registrou, e ela vê o selo de conferido.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra o conteúdo",
      "Clique no conteúdo. Ele aparece num quadradinho (um cartão) ou, na tela da semana, como uma aula. Assim ele abre para você ler.",
      "No celular: Toque no conteúdo. Ele aparece num quadradinho (um cartão) ou como uma aula. Assim ele abre para você ler."
     ],
     [
      "Marque",
      "Na janelinha do conteúdo, clique em **Marcar como conferido**. Esse botão só aparece para quem não é professora ou professor."
     ],
     [
      "Confira",
      "Vai aparecer um aviso verde: **Marcação salva com sucesso** O botão passa a mostrar **conferido por** e o seu nome, e o conteúdo ganha o selo de conferido. A professora vê o selo, mas não vê o botão."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como criar anotações",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra a ficha do aluno",
      "Na lista, clique no aluno (pode ser em qualquer parte da linha dele). A ficha dele vai abrir.",
      "No celular: Na lista, toque no nome do aluno. A ficha dele vai abrir."
     ],
     [
      "Abra a nova anotação",
      "A guia **Anotações** já abre primeiro. Clique no botão azul **Nova anotação**. Se o aluno ainda não tem nenhuma, o botão se chama **Criar anotação**."
     ],
     [
      "Preencha",
      "Escolha o **Tipo de anotação**, confira a **Data** e escreva a **Descrição**, com pelo menos 4 letras. Se o tipo for **Justificar falta**, você pode marcar **Justificar falta com duração de um dia**. Ou, se preferir, informe a **Data de término**."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Anotação criada com sucesso** Se você é da direção ou da coordenação, pode clicar em **Marcar como conferido**, no cartão da anotação."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como enviar notificações das anotações criadas para o responsável?",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra a ficha do aluno",
      "Na lista, clique no aluno (pode ser em qualquer parte da linha dele). A ficha dele vai abrir.",
      "No celular: Na lista, toque no nome do aluno. A ficha dele vai abrir."
     ],
     [
      "Envie pelo cartão",
      "Na guia **Anotações**, no cartão da anotação, clique em **Enviar para whatsapp**. Esse botão só aparece enquanto a anotação está **Sem notificação**."
     ],
     [
      "Confira a mensagem",
      "Vai abrir uma janelinha por cima, com a pergunta **Deseja notificar os pais?** Nela você vê como a mensagem vai ficar: um texto automático, a sua anotação e um aviso no final. Se a anotação for grande demais, a janela avisa que o resto não vai ser enviado."
     ],
     [
      "Envie",
      "Clique no botão azul **Enviar**. Vai aparecer um aviso verde: **Notificação enviada com sucesso**"
     ],
     [
      "Depois do envio",
      "O cartão passa a mostrar **Familiar Notificado**, e o botão some. Na primeira vez, a família pode precisar ativar as notificações. Veja a dúvida sobre o que o responsável vê."
     ]
    ]
   }
  ]
 },
 {
  "categoria": "AVALIAÇÕES E NOTAS",
  "itens": [
   {
    "tipo": "mover",
    "titulo": "Como criar avaliações",
    "passos": null
   },
   {
    "tipo": "mover",
    "titulo": "Como criar avaliação somativa",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Escolha o período",
      "Na caixinha **Selecione um Período**, escolha o período. Se a escola tem só um, ele já vem escolhido."
     ],
     [
      "Escolha a matéria",
      "Na caixinha **Selecione a matéria**, escolha a matéria. O tipo já vem como **Somativa**. Se faltar o período ou a matéria, a lista fica vazia e você não vai ver a avaliação que criar."
     ],
     [
      "Abra a tela de cadastro",
      "Clique em **Nova avaliação**. O botão fica apagado, sem poder apertar, se faltar a escola, a turma ou as matérias da turma."
     ],
     [
      "Preencha",
      "Preencha o **Título** e a **Descrição**, os dois com pelo menos 4 letras. Preencha também a **Data** e a **Matéria**. O **Peso da avaliação (opcional)** vai de 1 a 10. Se você deixar em branco, vale 1. Se aparecer a opção **Incluir peso na avaliação**, marque-a para digitar o peso."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Pronto! Vai aparecer um aviso verde: **Avaliação criada com sucesso** A avaliação só entra na tabela se a **Matéria** da tela de cadastro for a mesma que você escolheu nas caixinhas do alto."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como lançar as notas de uma avaliação",
    "descricao": "Digite a nota de cada aluno numa avaliação. Não existe botão de salvar: o computador guarda sozinho.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Escolha o período",
      "Na caixinha **Selecione um Período**, escolha o período."
     ],
     [
      "Escolha a matéria",
      "Na caixinha **Selecione a matéria**, escolha a matéria. O tipo precisa estar em **Somativa**."
     ],
     [
      "Digite as notas",
      "Na coluna da avaliação, digite a nota de cada aluno, de 0 a 10. Pode usar vírgula ou ponto. Para registrar zero, digite 0: a linha vazia fica de fora da média.",
      "No celular: As avaliações aparecem uma de cada vez. Use as setas ou deslize o dedo até chegar na avaliação certa. Depois, digite a nota na linha, de 0 a 10. Para registrar zero, digite 0: a linha vazia fica de fora da média."
     ],
     [
      "O computador guarda sozinho",
      "Aqui não existe botão de salvar. Quando você para de digitar, o computador guarda a nota sozinho. Vai aparecer um aviso verde: **Notas atualizadas com sucesso!** Se alguma nota não for guardada, a linha fica vermelha e aparece **Não salvou. Digite de novo.** É só digitar de novo."
     ],
     [
      "A média",
      "A coluna **Média** só mostra o resultado: você não digita nela. Ela fica verde quando a média é 5 ou mais, e vermelha quando é menor que 5."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como editar ou excluir uma avaliação",
    "descricao": "Corrija o título, a data ou o peso de uma avaliação. Ou exclua a avaliação, se precisar.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Escolha o período",
      "Na caixinha **Selecione um Período**, escolha o período."
     ],
     [
      "Escolha a matéria",
      "Na caixinha **Selecione a matéria**, escolha a matéria."
     ],
     [
      "Abra a avaliação",
      "Clique no título da avaliação, no alto da coluna dela."
     ],
     [
      "Salve",
      "Mude o que precisar e clique no botão azul **Salvar alterações**. Vai aparecer um aviso verde: **Avaliação atualizada com sucesso**"
     ],
     [
      "Para excluir",
      "Na tela de cadastro, clique no botão vermelho **Excluir avaliação**, o que tem uma lixeira. Leia o aviso com calma: **Ao excluir essa avaliação, quaisquer notas lançadas serão perdidas. Deseja continuar?** Depois de excluir, não tem como voltar atrás. Para seguir, clique em **Deletar**. Nenhum aviso aparece: a avaliação só some da lista."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como criar avaliação diagnóstica",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Escolha o tipo",
      "Na caixinha do tipo, escolha **Diagnóstica**. As caixinhas de período e de matéria vão sumir, e isso é normal."
     ],
     [
      "Abra a tela de cadastro",
      "Clique em **Nova avaliação**."
     ],
     [
      "Data e modelo",
      "Vai abrir uma tela nova do lado, chamada **Nova avaliação diagnóstica**. Em **Selecione uma data**, escolha a data (não pode ser uma data que ainda vai chegar). Em **Selecione o modelo**, escolha o modelo."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar**. Ele só fica disponível depois que você escolhe a data e o modelo. Vai aparecer um aviso verde: **Avaliação diagnóstica criada com sucesso**"
     ],
     [
      "Lance as hipóteses",
      "Clique no cartão da avaliação. Para cada aluno, escolha a **Hipótese** na lista que abre quando você aperta a setinha. Cada escolha é guardada na hora, sem precisar de botão."
     ],
     [
      "Para excluir",
      "Dentro da avaliação, clique em **Excluir avaliação**. Vai aparecer o aviso **Deleção de avaliação diagnóstica é uma ação irreversível, tem certeza que deseja continuar?** Depois de excluir, não tem como voltar atrás. Também não dá para mudar a data nem o modelo depois: só dá para lançar hipóteses ou excluir."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como lançar notas",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Escolha a matéria",
      "Veja se a guia **Notas** está escolhida. Depois, na caixinha da matéria, escolha a matéria que você quer."
     ],
     [
      "Digite as notas",
      "Na linha do aluno, digite a nota na coluna do período (bimestre ou trimestre). Pode usar vírgula ou ponto, de 0 a 10.",
      "No celular: No cartão do aluno, digite a nota na linha do período (bimestre ou trimestre). Pode usar vírgula ou ponto, de 0 a 10."
     ],
     [
      "O computador guarda sozinho",
      "Aqui não existe botão de salvar. Quando você para de digitar, o computador guarda a nota sozinho. Vai aparecer um aviso verde: **Notas atualizadas com sucesso!**"
     ],
     [
      "Se não guardar",
      "Se alguma nota não for guardada, a linha fica vermelha e aparece o aviso **Não salvou. Digite de novo.** É só digitar a nota mais uma vez."
     ],
     [
      "Ajuste a média final",
      "Para ajustar a média final de um aluno, clique na média dele e digite o valor. Depois, clique em **Salvar média final**.",
      "No celular: não tem"
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como registrar o total de aula dada",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Escolha a matéria",
      "Em **Selecione uma matéria**, escolha a matéria. Sem ela, a tabela não aparece. O registro vale para cada matéria, uma de cada vez."
     ],
     [
      "Abra o período",
      "No alto da tabela, clique no nome do período (bimestre ou trimestre)."
     ],
     [
      "Preencha",
      "Digite as **Aulas previstas** e as **Aulas dadas**. Você precisa preencher as duas."
     ],
     [
      "Salve",
      "Clique no botão azul **Salvar alterações**. Ele só fica disponível depois que você preenche alguma coisa."
     ],
     [
      "Confira",
      "Vai aparecer um aviso verde: **Estimativa de aulas atualizadas com sucesso** O número de aulas dadas passa a aparecer no alto do período, no Consolidado."
     ]
    ]
   }
  ]
 },
 {
  "categoria": "ACOMPANHAR E RELATÓRIOS",
  "itens": [
   {
    "tipo": "mover",
    "titulo": "Modo análise",
    "passos": [
     [
      "Escolha a escola",
      "Olhe a caixinha do alto da tela. Confira se a escola está certa. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se a escola está certa. Se ainda não escolheu, escolha agora."
     ],
     [
      "Ligue o modo análise",
      "No alto da tela, ligue a chave de ligar e desligar que tem o desenho de um gráfico. Ela aparece nas telas que têm análise: Frequência, Conteúdos, Avaliações, Consolidado, Equipe e Alunos."
     ],
     [
      "Veja o que mudou",
      "A tela deixa de mostrar o dia a dia e passa a mostrar gráficos e painéis. O menu mostra só as partes que têm análise. Alguns painéis dependem dos dados da sua escola e podem aparecer vazios.",
      "No celular: A tela deixa de mostrar o dia a dia e passa a mostrar gráficos e painéis. O menu de baixo mostra só Frequência, Alunos, Avaliações e Consolidado. Alguns painéis dependem dos dados da sua escola e podem aparecer vazios."
     ],
     [
      "Para voltar",
      "Desligue a mesma chave. A tela volta a mostrar o dia a dia."
     ]
    ]
   },
   {
    "tipo": "guia",
    "titulo": "Como ver as análises de um aluno",
    "descricao": "Abra a guia Análises na ficha do aluno e escolha a disciplina e o período.",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra a ficha do aluno",
      "Na lista, clique no aluno (pode ser em qualquer parte da linha dele). A ficha dele vai abrir.",
      "No celular: Na lista, toque no nome do aluno. A ficha dele vai abrir."
     ],
     [
      "Abra a guia Análises",
      "Na ficha do aluno, clique na guia **Análises**."
     ],
     [
      "Escolha o que ver",
      "Use as caixas **Todas disciplinas** e **Todos os períodos** para escolher a disciplina e o período. O painel muda sozinho."
     ],
     [
      "Se o painel não aparecer",
      "Se aparecer **O painel de análises não retornou dados para este aluno**, veja se existem notas lançadas no Consolidado. Se aparecer **Não foi possível carregar o painel de análises**, tente de novo mais tarde. Esse painel depende do acesso da sua escola."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como gerar o consolidado da turma",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Abra o Consolidado",
      "Nas caixinhas do alto da tela de Alunos, clique no botão **Consolidado**, ao lado de **Socioeconômico**. Ele só fica disponível depois que você escolhe uma turma."
     ],
     [
      "Escolha o período",
      "Na lista que abriu, clique no período que você quer."
     ],
     [
      "Gere o relatório",
      "Na janelinha **Consolidado** que abriu por cima, clique em **Gerar consolidado do período** (só o período que você escolheu) ou em **Gerar consolidado geral** (a turma toda)."
     ],
     [
      "Abra o arquivo",
      "O relatório abre numa janela nova, por cima. Se nada abrir, pode ser que o seu navegador esteja impedindo janelas novas. Peça ajuda à coordenação da escola ou aperte **Ajuda**, no menu. Se algo der errado, vai aparecer um aviso vermelho: **Erro ao buscar relatório**."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Como acessar o boletim do aluno",
    "passos": [
     [
      "Escolha a escola e a turma",
      "Olhe as caixinhas do alto da tela. Confira se a escola e a turma estão certas. Se ainda não escolheu, escolha agora.",
      "No celular: No alto da tela, toque na caixa que mostra a escola e a turma. Confira se as duas estão certas. Se ainda não escolheu, escolha agora."
     ],
     [
      "Marque os alunos",
      "Marque os alunos na primeira coluna da lista. Para marcar a turma toda, clique em **Selecionar**, no alto dessa coluna."
     ],
     [
      "Gere o boletim",
      "Clique no botão **Boletim**. Ele só fica disponível depois que você escolhe uma turma e marca pelo menos um aluno."
     ],
     [
      "Abra o arquivo",
      "O boletim abre numa janela nova, por cima. Se nada abrir, pode ser que o seu navegador esteja impedindo janelas novas. Peça ajuda à coordenação da escola ou aperte **Ajuda**, no menu. Se algo der errado, vai aparecer um aviso vermelho: **Erro ao buscar relatório**."
     ]
    ]
   },
   {
    "tipo": "mover",
    "titulo": "Relatório de Frequência",
    "passos": [
     [
      "Escolha a escola",
      "No alto da tela, confira se a escola está certa. O botão do relatório só fica disponível depois que você escolhe a escola.",
      "No celular: No alto da tela, toque na caixinha da escola e confira se ela está certa. O botão do relatório só fica disponível depois que você escolhe a escola."
     ],
     [
      "Abra o relatório",
      "Clique no botão **Relatório de Faltas**."
     ],
     [
      "Escolha o filtro",
      "Em **Tipo de Filtro**, escolha **Por Mês**, **Por Período** ou **Por Ano Letivo**. Depois preencha o que a tela pedir. Se escolher **Por Mês**, olhe a caixinha **Ano**: nem sempre ela vem com o ano atual."
     ],
     [
      "Gere",
      "Clique no botão **Gerar relatório**."
     ],
     [
      "Confira",
      "Vai aparecer um aviso verde: **Relatório gerado com sucesso!** O arquivo abre numa janela nova, por cima. Se nada abrir, pode ser que o seu navegador esteja impedindo janelas novas. Peça ajuda à coordenação da escola ou aperte **Ajuda**, no menu."
     ]
    ]
   }
  ]
 },
 {
  "categoria": "DÚVIDAS FREQUENTES",
  "itens": [
   {
    "tipo": "duvida",
    "titulo": "Onde eu lanço as notas?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "No menu, a tela das notas se chama **Consolidado**, e não \"Notas\". É lá que você lança a nota de cada aluno, em cada período (bimestre ou trimestre)."
     },
     {
      "tipo": "p",
      "texto": "Ao abrir o **Consolidado**, veja se a guia **Notas** está escolhida. As outras guias, **Faltas** e **Outros**, mostram outras informações da turma."
     },
     {
      "tipo": "p",
      "texto": "O passo a passo está em \"Como lançar as notas do período\"."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que não vejo Frequência, Conteúdos, Avaliações e Consolidado no menu?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Frequência, Conteúdos, Avaliações e Consolidado fazem parte de uma parte da plataforma que a sua prefeitura contratou junto com a Leme. Se a sua rede não tem essa parte, essas telas não aparecem no menu."
     },
     {
      "tipo": "p",
      "texto": "Se a escola escolhida no alto da tela não tem essa parte, a tela mostra **Essa escola não possui módulo de gestão!**"
     },
     {
      "tipo": "p",
      "texto": "Quem decide contratar é a Secretaria de Educação do município. Fale com ela para saber mais."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Onde fica a escolha do ano letivo?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "A escolha do ano letivo só aparece quando a escola tem mais de um ano cadastrado. Se tem um ano só, ele já vem escolhido e você não precisa fazer nada."
     },
     {
      "tipo": "p",
      "texto": "Quando aparece, fica ao lado do seu nome, no alto da tela. No celular, fica dentro do menu da sua foto."
     },
     {
      "tipo": "p",
      "texto": "No computador, ela não aparece na tela inicial."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que voltei para a tela de entrada?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Quando o seu acesso termina, aparece o aviso **Sua sessão expirou! Por favor faça login novamente** e a plataforma volta para a tela de entrada. É só entrar de novo com o seu e-mail e a sua senha."
     },
     {
      "tipo": "p",
      "texto": "Se você tinha aberto um endereço da plataforma, depois de entrar você vai direto para a página dele."
     },
     {
      "tipo": "p",
      "texto": "Se a plataforma abrir com um acesso que não dá mais para continuar, aparece **Não foi possível retomar sua sessão. Faça login novamente.**"
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Qual é a diferença entre avaliação somativa e diagnóstica?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Em **Avaliações**, o tipo é **Somativa** ou **Diagnóstica**. Não existe um tipo formativo nessa tela."
     },
     {
      "tipo": "p",
      "texto": "**Somativa**: tem título, descrição, data e peso. Cada aluno recebe uma nota de 0 a 10, e a plataforma mostra a média."
     },
     {
      "tipo": "p",
      "texto": "**Diagnóstica**: você escolhe um modelo pronto e uma data. A data não pode ser futura. Depois, para cada aluno, você registra uma hipótese, escolhendo numa lista do modelo."
     },
     {
      "tipo": "p",
      "texto": "Os passo a passos estão em \"Como criar uma avaliação somativa\" e \"Como criar uma avaliação diagnóstica\"."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Criei uma avaliação e ela não aparece na lista. O que fazer?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "A lista de avaliações só aparece quando você escolhe **Selecione um Período** e **Selecione a matéria**, nas caixinhas do alto da tela. Escolha as duas."
     },
     {
      "tipo": "p",
      "texto": "Veja também a matéria que você usou na tela de cadastro. A avaliação nova entra na matéria que você escolheu nela."
     },
     {
      "tipo": "p",
      "texto": "Se for diferente da matéria das caixinhas do alto, ela não aparece na tabela que você está vendo."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que o botão Salvar não funciona?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Nas telas de cadastro da plataforma, o botão **Salvar** só fica disponível depois que você muda ou preenche alguma coisa."
     },
     {
      "tipo": "p",
      "texto": "Se ele está cinza, escreva ou mude algo e ele fica disponível."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que os três pontinhos do aluno estão cinza ou não aparecem?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Os três pontinhos, na linha do aluno, só funcionam para aluno cuja situação é Ativo ou Aprovado."
     },
     {
      "tipo": "p",
      "texto": "Além disso, a coluna com esses pontinhos só aparece para a direção e a coordenação, no computador, em escolas que você pode editar e fora de turmas de AEE."
     },
     {
      "tipo": "p",
      "texto": "É por essa lista de opções que se transfere o aluno, se remaneja ou se muda a situação dele."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que um aluno aparece apagadinho na lista?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "A linha do aluno fica mais clara quando a situação dele não é Ativo nem Aprovado. Por exemplo, depois de uma transferência ou de uma reclassificação."
     },
     {
      "tipo": "p",
      "texto": "Ele continua na lista, para você consultar."
     },
     {
      "tipo": "p",
      "texto": "Para ver a situação e desde quando ela vale, passe o mouse sobre a linha."
     },
     {
      "tipo": "p",
      "texto": "Aluno aprovado continua com a linha normal."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que não consigo cadastrar ou editar nesta escola?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Cadastrar aluno, editar dados pessoais e cadastrar familiar só aparecem nas escolas que o seu usuário pode editar. Na lista de escolas, as que não abrem para edição aparecem mais claras."
     },
     {
      "tipo": "p",
      "texto": "A tela não explica o motivo."
     },
     {
      "tipo": "p",
      "texto": "Se você precisa editar e não consegue, fale com a Secretaria de Educação do seu município."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "O que o responsável vê ao ativar as notificações do WhatsApp?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Esta é a tela que o responsável abre para ativar as notificações do WhatsApp. Ela mostra **Acompanhe a jornada do seu filho em tempo real!** e, num cartão, **Ativar Notificações do WhatsApp**. No cartão há um único botão: **Quero receber notificações**."
     },
     {
      "tipo": "p",
      "texto": "A tela explica o que o responsável vai receber:"
     },
     {
      "tipo": "bullet",
      "texto": "anotações em tempo real;"
     },
     {
      "tipo": "bullet",
      "texto": "acompanhamento de progresso, com notas, frequência e desempenho;"
     },
     {
      "tipo": "bullet",
      "texto": "avisos importantes."
     },
     {
      "tipo": "p",
      "texto": "Ela também avisa que, ao ativar, o responsável concorda em receber mensagens por WhatsApp sobre o acompanhamento escolar."
     },
     {
      "tipo": "p",
      "texto": "Depois de tocar no botão, aparece **Consentimento Ativado!** Se algo der errado, a tela pede para tentar de novo mais tarde."
     },
     {
      "tipo": "p",
      "texto": "Não é preciso entrar com e-mail nem senha."
     },
     {
      "tipo": "p",
      "texto": "Se o botão não ficar disponível, o endereço que o responsável recebeu veio incompleto. Peça um novo a quem enviou."
     },
     {
      "tipo": "p",
      "texto": "Não existe botão para recusar. Quem não quiser receber, basta não ativar."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que a tela de Frequência está vazia?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "A tela de Frequência só mostra a tabela quando há turma, alunos e aula no dia. No lugar da tabela, aparece uma mensagem que diz o que falta:"
     },
     {
      "tipo": "bullet",
      "texto": "**Selecione uma escola nos filtros!** ou **Selecione uma turma nos filtros!**: escolha a escola e a turma nas caixinhas do alto da tela."
     },
     {
      "tipo": "bullet",
      "texto": "**Não tem aula**, seguido de \"hoje\" ou \"nesse dia\" e do nome do evento: no Calendário existe um evento marcando aquele dia como não letivo. O botão **Ver a última aula** leva para o último dia com aula. Se o dia deveria ter aula, a direção e a coordenação corrigem o evento no Calendário."
     },
     {
      "tipo": "bullet",
      "texto": "**Nenhum estudante encontrado**: a turma ainda não tem alunos matriculados."
     },
     {
      "tipo": "bullet",
      "texto": "**Você não tem aula nesta turma** (para a professora): a Grade horária não tem aula sua nessa turma nesse dia. A tela mostra as turmas em que você dá aula nesse dia, para trocar com um toque, e o botão **Ver a última aula**."
     },
     {
      "tipo": "bullet",
      "texto": "**Essa escola não possui turmas cadastradas nesse dia.** (para a direção e a coordenação): em geral, a Grade horária da turma não tem aula nesse dia da semana."
     },
     {
      "tipo": "p",
      "texto": "Se o dia está certo, peça à direção e à coordenação da escola para conferir a Grade horária."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que não aparecem aulas ou matérias em Conteúdos?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Em Conteúdos, as matérias e as aulas vêm da Grade horária da turma. Quando algo não aparece, a tela diz o motivo:"
     },
     {
      "tipo": "bullet",
      "texto": "**Você não ministra aulas nesse dia!**: na lista de conteúdos, essa mensagem aparece quando a turma ainda não tem nenhuma matéria na Grade horária. Ela não aparece só quando o dia está sem aula."
     },
     {
      "tipo": "bullet",
      "texto": "Ao criar um conteúdo, a tela de cadastro avisa o que falta, nesta ordem: **Escolha a data para ver as aulas.**, **Dia não letivo**, **Você não tem aulas nesta turma neste dia.**, **Escolha a matéria para ver as aulas.** e **Não há aulas desta matéria neste dia.**"
     },
     {
      "tipo": "bullet",
      "texto": "**Esta aula já tem conteúdo**: a aula aparece apagada porque já tem um conteúdo registrado. Para usá-la, edite ou exclua o conteúdo que já existe."
     },
     {
      "tipo": "p",
      "texto": "Se faltam aulas ou matérias, peça à direção e à coordenação da escola para conferir a Grade horária da turma."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que a matéria não aparece em Notas e em Avaliações?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Em Notas (o Consolidado) e em Avaliações, a lista de matérias vem da Grade horária da turma. Se a turma não tem aula cadastrada, não há matéria para escolher."
     },
     {
      "tipo": "bullet",
      "texto": "**É necessário escolher uma matéria nos filtros!**: escolha a matéria. Se a turma tem só uma, ela já vem escolhida."
     },
     {
      "tipo": "bullet",
      "texto": "Quando a turma tem só uma matéria, o botão da matéria fica apagado. Isso é normal: ela já está escolhida."
     },
     {
      "tipo": "bullet",
      "texto": "O botão **Nova avaliação** fica apagado se a turma não tem nenhuma matéria na grade."
     },
     {
      "tipo": "p",
      "texto": "Se a lista de matérias está vazia, peça à direção e à coordenação da escola para cadastrar as aulas da turma na Grade horária."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que a turma sumiu quando troquei a escola ou o ano?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "Quando você troca a escola, a turma e o ano que estavam escolhidos são limpos. Quando você troca o ano, a turma é limpa."
     },
     {
      "tipo": "p",
      "texto": "Por isso a turma some. É só escolher de novo em **Selecione a Turma**."
     },
     {
      "tipo": "p",
      "texto": "A lista de turmas depende da escola e do ano escolhidos. Se uma turma que você espera não aparece, veja se o ano letivo escolhido é o certo."
     },
     {
      "tipo": "p",
      "texto": "Se a lista fica vazia, a tela mostra **Nenhuma turma encontrada**."
     },
     {
      "tipo": "p",
      "texto": "Uma matéria escolhida em outra tela também pode sumir ao trocar de turma, quando a turma nova não tem aquela matéria na grade."
     }
    ]
   },
   {
    "tipo": "duvida",
    "titulo": "Por que não aparece a opção Enviar para AEE?",
    "blocos": [
     {
      "tipo": "p",
      "texto": "A opção **Enviar para AEE** só aparece quando tudo isto é verdade:"
     },
     {
      "tipo": "bullet",
      "texto": "você é da direção ou da coordenação, está no computador, e a escola é uma que você pode editar;"
     },
     {
      "tipo": "bullet",
      "texto": "a escola tem o AEE ativado e uma turma de AEE no ano escolhido;"
     },
     {
      "tipo": "bullet",
      "texto": "você está numa turma que não é de AEE;"
     },
     {
      "tipo": "bullet",
      "texto": "a situação do aluno é Ativo ou Aprovado."
     },
     {
      "tipo": "p",
      "texto": "O aluno enviado para o AEE não sai da turma dele. A matrícula regular continua ativa, e o AEE é uma matrícula a mais."
     }
    ]
   }
  ]
 }
];
```
