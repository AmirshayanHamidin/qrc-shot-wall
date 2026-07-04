# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-03, scheduled run #2)

Repo: github.com/AmirshayanHamidin/qrc-shot-wall. **The README is ground truth** for
what is done; this file is the forward queue. Benchmarks 1–13 complete and pushed.
**PREPRINT.md (arXiv skeleton) now drafted at repo root** — abstract, 4-act narrative,
law derivation sketch, honest-negative ledger, limitations, future work. Its related-work
section is a placeholder pending the RELATED_WORK.md pass (next queue item).
**AUDITS.md started**: B13 independently re-implemented and CONFIRMED (see log).

Current state of the science: shot wall established (B1–B2), task-shape (B3), live QPU
validation done historically (0.886 on ibm_marrakesh — budget now nearly spent, hence
guardrail 1), measurement-wall law (B5) + gate-noise extension (B6) + its limits
(B7–B8) + usability at scale (B9) + retraining caveat (B10), external validity on
Mackey-Glass (B11), topology/IPS design rule (B12), scope-corrected to within-task
at small margins (B13, independently audited).

## HARD GUARDRAILS (never violate)

1. **NEVER submit jobs to real IBM hardware** — the free QPU budget is nearly spent
   (484/600s). Do not read or use `ibm_token.txt`. Simulation only (numpy engine +
   qiskit-aer).
2. Only work inside the session outputs folder and the qrc-shot-wall GitHub repo. No
   other accounts, sites, purchases, emails, or messages.
3. Every claim gets an honesty section. Failed hypotheses are reported as failures.
4. Keep runs within the 45s bash-call limit (chunk long computations; partial .npy/.json).
5. If GitHub push isn't possible in this session, save everything locally and log it
   under "Pending push" below; do not retry endlessly.

## Method rules

- One pre-stated falsifiable hypothesis per benchmark, written down (script header
  and/or writeup) BEFORE running; fit/holdout splits where fitting occurs.
- Verify any re-transcribed pipeline against published repo numbers before trusting it
  (B13 pattern: reproduce a B12 IPS value to machine precision first).
- Post-hoc analyses are allowed but must be labeled post-hoc everywhere they appear.
- Write results as `results/RESULTS_<NAME>.md` + raw JSON + figure PNG; update README
  (new benchmark section + limitations) and this agenda in the same push batch.
- **Fresh-session cache warning (learned this run):** raw.githubusercontent.com can
  serve a stale README to a new session. Before choosing a work item, cache-bust
  (append `?nc=<random>`) and/or check for the newest expected files (e.g. does
  results/RESULTS_<latest>.md 404?). A stale README this run nearly caused a duplicate
  B13; the duplicate was converted into an independent-reproduction audit (AUDITS.md).

## Queue (work top-down; mark DONE with date)

- [x] **Small-margin regime sweep (B13).** DONE 2026-07-03 (run #1). Honest negative at
      the registered pooled bar; within-task IPS effect strong (post-hoc); star edge
      n.s.; all-to-all robustly worst. → results/RESULTS_SMALLMARGIN.md.
- [x] **PREPRINT.md consolidation.** DONE 2026-07-03 (run #2). Drafted at repo root:
      abstract, 13-benchmark narrative in 4 acts (wall → law → limits → design), law
      derivation sketch, honest-negative ledger (B5v1, B7, B8, B11-H2, B12-H2, B13-H1),
      limitations, future work. Related-work section left as an explicit placeholder.
- [ ] **RELATED_WORK.md literature pass.** Position against published QRC/shot-noise
      literature (web search allowed; cite properly; no paywalled quoting). Candidate
      anchors: QRC reviews, finite-sampling noise analyses, quantum-advantage-under-
      measurement papers. Map each of our 13 benchmarks to nearest prior art and state
      what is new. Then merge citations into PREPRINT.md §Related work.
- [ ] (then) **AUDIT MODE** per the standing task instructions: least-recently-audited
      benchmark first, re-run key numbers from repo code, push AUDITS.md entries.
      B13 already audited (2026-07-03, CONFIRMED); B1–B12 unaudited — start from B1/B2.

## Log

- 2026-07-03 03:00 — Agenda created. B6 (old numbering) started in the live session.
- 2026-07-03 12:30 — Agenda moved into repo root so scheduled runs can fetch it.
- 2026-07-03 (scheduled run #1) — **B13 small-margin sweep completed and pushed.**
  Pipeline verified against B12's published star-L1/parity3 IPS (exact match). 120
  cells. Pre-registered H1 falsified as registered (pooled ρ=+0.07, p=0.75 @250 shots);
  within-task-standardized pooled ρ=+0.82 (post-hoc, labeled); H2 literal pass but
  star-vs-chain/ring n.s., star-vs-all2all significant (p=0.002). README B13 section
  added; limitations updated.
- 2026-07-03 (scheduled run #2) — **PREPRINT.md drafted and pushed** (topmost queue
  item). Also: session started from a stale cached README (pre-B13) and independently
  re-implemented B13 before discovering the published version — converted into the
  first **AUDITS.md** entry: B13 **CONFIRMED** end-to-end (pooled H1 failure, within-task
  ρ +0.72…+0.90 @250, star mean 0.789 vs published 0.784, all2all deficit +5.0 vs
  +4.9 pp, exact-span 0.961–1.000 identical; independent code, different sampling
  seeds; published JSON left untouched as file of record). Cache-warning added to
  method rules. Next: RELATED_WORK.md.

## Pending push

(none — pending this session's batch: PREPRINT.md, AUDITS.md, RESEARCH_AGENDA.md)
