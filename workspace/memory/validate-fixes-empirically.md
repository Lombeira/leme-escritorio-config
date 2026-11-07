---
name: validate-fixes-empirically
description: Glauco wants fixes proven to work before they are declared done or written into shared tooling
metadata: 
  node_type: memory
  type: feedback
  originSessionId: de64fa62-4730-4014-a61f-439207ac7fca
  modified: 2026-08-07T20:29:18.428Z
---

When a fix is based on a plausible-but-unverified hypothesis, confirm it empirically with Glauco
**before** declaring success or baking it into shared tooling (skills, configs, docs).

**Why:** on 2026-08-07, a Jira card created by `/create-jira-card` didn't show on the delivery board.
The first fix (adding the active sprint) was reasoned from real evidence but only addressed half the
cause — the card was still invisible because its status wasn't mapped to a board column. It was
reported as fixed anyway. Glauco caught it and asked to validate together before changing anything.
Writing an unverified fix into a skill multiplies the error across every future run.

**How to apply:** state the hypothesis and the evidence for it, propose the cheapest test that would
disprove it, run the test, and wait for confirmation before editing shared files. Distinguish "the API
call succeeded" from "the outcome the user wanted happened" — response payloads often omit the fields
that matter, so verify with an independent read. See [[jql-status-nome-nao-resolve]].
