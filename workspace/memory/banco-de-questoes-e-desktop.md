---
name: banco-de-questoes-e-desktop
description: Banco de questões / Gestão de Itens é usado quase só no desktop; trade-off de mobile ali não é bloqueio
metadata: 
  node_type: memory
  type: project
  originSessionId: 60bdd2b9-5c92-4b42-be57-f86cc2598360
  modified: 2026-08-31T18:38:34.100Z
---

Na experiência do banco de questões (`/dashboard/mapa/questions`, "Gestão de Itens") o público quase não usa mobile — confirmado pelo Glauco em 31/08/2026, ao aceitar uma barra de filtros fixa que ocupa ~250px (mais de um terço da área útil) em 390×844.

**Why:** é tela de admin, gated por papel e pela flag `IsMapaLemeEnabled`, usada para curar itens — não é o fluxo de professor no celular. O resto do app não segue essa regra: mobile é tratado a sério lá (ex.: LM-2309, "Ajustes de UI mobile").

**How to apply:** ao decidir layout nessa tela, otimize para desktop e não sacrifique a experiência larga para caber no celular. Continua valendo medir e dizer o número quando o custo em mobile for grande — o Glauco quer o dado, só não trata como bloqueio aqui. Não estenda isso para telas de professor/aluno sem perguntar.

Relacionado: [[info-errada-na-tela-e-bug]], [[validate-fixes-empirically]]
