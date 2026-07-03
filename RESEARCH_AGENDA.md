# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-03, scheduled run)

Repo: github.com/AmirshayanHamidin/qrc-shot-wall. **The README is ground truth** for
what is done; this file is the forward queue. Benchmarks 1–13 complete and pushed.
Note: the benchmark numbering in older versions of this file (B6–B11 as planned items)
is obsolete — the program evolved differently; trust the README's numbering.

Current state of the science: shot wall established (B1–B2), task-shape (B3), live QPU
validation done historically (0.886 on ibm_marrakesh — budget now nearly spent, hence
guardrail 1), measurement-wall law (B5) + gate-noise extension (B6) + its limits
(B7–B8) + usability at scale (B9) + retraining caveat (B10), external validity on
Mackey-Glass (B11), topology/IPS design rule (B12), and B13 (this run): the IPS rule
is **within-task only** — pre-registered pooled bar failed honestly (ρ=+0.07 vs B12's
+0.90); star advantage shrinks to n.s.; "avoid all-to-all" transfers.

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

## Queue (work top-down; mark DONE with date)

- [x] **Small-margin regime sweep (B13).** DONE 2026-07-03. B12's topology sweep re-run
      on the Mackey-Glass family. H1 pooled bar FAILED (honest negative); within-task
      IPS effect strong (post-hoc); star edge n.s.; all-to-all robustly worst.
      → results/RESULTS_SMALLMARGIN.md, results/smallmargin_law.json,
      figures/qrc_smallmargin.png, src/qrc_smallmargin.py.
- [ ] **PREPRINT.md consolidation.** Draft `PREPRINT.md` at repo root: abstract, the
      13-benchmark narrative arc (wall → law → limits → design), law derivation sketch,
      honest-negative ledger (B7, B8-partial, B11-H2-partial, B12-H2, B13-H1),
      limitations, future work. This is the arXiv skeleton. Confirmatory items to flag
      as open: within-task IPS rule on a third task family; reseeded topology sweep.
- [ ] **RELATED_WORK.md literature pass.** Position against published QRC/shot-noise
      literature (web search allowed; cite properly; no paywalled quoting). Candidate
      anchors: QRC reviews, finite-sampling noise analyses, quantum-advantage-under-
      measurement papers. Map each of our 13 benchmarks to nearest prior art and state
      what is new. Feed directly into PREPRINT.md's related-work section.
- [ ] (then) **AUDIT MODE** per the standing task instructions: least-recently-audited
      benchmark first, re-run key numbers from repo code, push AUDITS.md entries.

## Log

- 2026-07-03 03:00 — Agenda created. B6 (old numbering) started in the live session.
- 2026-07-03 12:30 — Agenda moved into repo root so scheduled runs can fetch it.
- 2026-07-03 (scheduled run) — **B13 small-margin sweep completed and pushed.** Pipeline
  verified against B12's published star-L1/parity3 IPS (exact match). 120 cells.
  Pre-registered H1 falsified as registered (pooled ρ=+0.07, p=0.75 @250 shots);
  within-task-standardized pooled ρ=+0.82 (post-hoc, labeled); H2 literal pass but
  star-vs-chain/ring n.s. (Wilcoxon p≈0.1–0.2), star-vs-all2all significant (p=0.002).
  README B13 section added; limitations updated. Next queue item: PREPRINT.md.

## Pending push

(none)
