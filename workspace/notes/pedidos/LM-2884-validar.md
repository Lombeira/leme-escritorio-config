---
card: LM-2884
status: fechado
pr: https://github.com/leme-tech/leme-app/pull/880
fechado_em: 2026-11-10 15:32 (aprovado)
---
# LM-2884: validar câmera abrindo e "Tentar novamente" no /foto

**PR:** https://github.com/leme-tech/leme-app/pull/880

**Link:** http://192.168.1.173:5301/foto (preview na rede de casa)
- **Atenção à câmera:** por `http://IP` o navegador não libera a câmera (fora de contexto seguro não existe `navigator.mediaDevices`), então o `/foto` vai cair direto no erro. Para ver a câmera de verdade, use o Chrome do PC com `ssh -L 5301:127.0.0.1:5301` e abra `http://localhost:5301/foto`, que conta como contexto seguro.
- Worktree: `repos/leme-app/.worktrees/LM-2884`
- Branch: `LM-2884` @ `3918b6e7` (só local, sem push)
- Diff: `git -C repos/leme-app/.worktrees/LM-2884 diff origin/main...HEAD` (4 arquivos, +444 −36)
- Evidências: `.escritorio/cards/LM-2884/evidencias/`
- Review: 3 rodadas. Foi para o QA no limite de 2 voltas com **1 should-fix pendente** (detalhe abaixo, em `.escritorio/cards/LM-2884/review.md`).

## O que mudou
- **Câmera abrindo:** a área escura do `/foto` mostra um spinner e "Abrindo a câmera..." até chegar o primeiro quadro. Depois aparece "Aponte para o QR code no topo da folha", como antes.
- **Câmera que não abre:** em vez de cair direto em "Tirar foto da folha", a tela mostra um aviso vermelho com "Tentar novamente", e logo abaixo o "Tirar foto da folha". Quem tenta de novo não precisa recarregar a página. O texto do aviso depende da causa:
  - Navegador recusou a câmera: "A câmera não abriu. Confira se o navegador tem permissão...".
  - A câmera abriu mas não mostrou imagem: "A câmera abriu, mas não mostrou imagem. Tente de novo ou tire uma foto da folha.". Nesse caso a câmera é desligada e a luz apaga.
- **Toasts:** o `/foto` não mostra mais os toasts da câmera, porque o aviso na tela já explica (`{ silent: true }`). O cartão-resposta e o questionário usam o mesmo hook, `useCameraStream`, e continuam como antes, com toast e stream aberto.
- **Arquivos:**
  - `src/hooks/omr/use-camera-stream.ts`: novos `isShowing`, `retry`, `failure` e as opções `silent` e `releaseOnFailure`.
  - `src/pages/answer-sheet-photo/components/sheet-qr-scanner.tsx`.
  - Testes dos dois.
- **Fora do escopo:** a causa real da demora em Pompéu continua desconhecida. O card melhora o feedback, não a velocidade, e a resolução pedida em `portrait-camera.ts` não foi mexida, porque não há medição.

## QA: APROVADO

Câmera simulada no Chromium headless (fake device e `getUserMedia` mocado), conta PROFESSOR, nenhum dado criado.

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Spinner + "Abrindo a câmera..." antes do primeiro quadro | APROVADO | 1-abrindo-desktop.png, 1-abrindo-mobile.png |
| 2 | Com imagem, o indicador some e volta o "Aponte para o QR code" | APROVADO | 2-exibindo-desktop.png, 2-exibindo-mobile.png |
| 3 | Permissão negada: erro + "Tentar novamente" + "Tirar foto da folha", sem toast | APROVADO | 3-camera-negada.png |
| 4 | Liberar e "Tentar novamente": volta ao leitor sem recarregar | APROVADO | 4-tentar-novamente.png |
| 5 | Fluxo normal lê o QR e navega para a folha | APROVADO (QR com folha fictícia, não testado com folha real de turma de teste) | 5-antes-leitura.png, 5-depois-leitura.png |

O QA não reproduziu no browser o caminho em que a câmera abre sem imagem. Só os testes automáticos cobrem esse caso.

## O que validar
1. No Chrome do PC, por `localhost` (via `ssh -L`), com a câmera liberada: o spinner aparece rapidinho, a imagem entra e um QR de cartão-resposta de turma de teste leva para a folha.
2. Nas configurações do site, bloquear a câmera e recarregar: deve aparecer o aviso com "Tentar novamente" e nenhum toast. Depois liberar a câmera e tocar "Tentar novamente": a câmera volta sem recarregar a página.
3. Se puder, conferir que a leitura pelo cartão-resposta ou pelo questionário continua igual, com o toast ao bloquear a câmera.
4. Pelo IP (link acima), no celular: o aviso aparece, e "Tirar foto da folha" funciona como saída.

## Pendências do review (não corrigidas, limite de voltas)
- 🟡 `src/hooks/omr/use-camera-stream.ts:259`: o hook ainda devolve `hasFailed`, que nenhum código de produção lê (só os testes). Sugestão: remover do retorno e, nos testes, derivar de `failure`. É limpeza de API, sem efeito na tela. Dá para pedir na devolução, ou deixar.
- ⚪ 6 nits suprimidos (nomes, tamanho de comentário, ternário grande no JSX, foco depois de "Tentar novamente"), listados em `review.md`.

## Outros riscos anotados pelo front-dev
- O aviso de "não abriu" cobre toda recusa do navegador: permissão negada, câmera em uso por outro app e aparelho sem câmera. O texto manda conferir a permissão, como conselho, sem afirmar que a causa é essa.
- Numa rodada dos testes relacionados saiu 1 falha que não foi identificada, e as três rodadas seguintes passaram limpas. Pode ser instabilidade, e a suíte inteira roda no pre-push.

## Jira (proposta, só se você aprovar)
Comentário sugerido no LM-2884: "Melhoramos o feedback da câmera no /foto: agora aparece 'Abrindo a câmera...' enquanto ela inicia e, se não abrir, um aviso com 'Tentar novamente' sem recarregar a página. A causa da demora em Pompéu ainda não foi medida; se continuar lento, vale um card para investigar com o aparelho de lá."
