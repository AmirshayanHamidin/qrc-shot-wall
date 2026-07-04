# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-04, scheduled session)

Repo: github.com/AmirshayanHamidin/qrc-shot-wall. **The README is ground truth for what is done; where this file lags, trust the README.**

Benchmarks **B1–B13 complete and pushed** (see README + `results/`). Highlights: the shot wall (B2),
the parameter-free measurement-wall law (B5, R²=0.991, QPU-validated), gate noise as effective
shots with mapped limits (B6–B8), pilot-run margin estimation (B9), retraining as load-bearing
(B10), second task family (B11), IPS topology design rule (B12) with small-margin scope
correction (B13). **PREPRINT.md consolidated (v0.2). RELATED_WORK.md literature pass done
(2026-07-04)** — preprint Related-work section populated with verified citations.
**AUDITS.md started** — B13 independently re-implemented and CONFIRMED (2026-07-03).
**B5 audit (2026-07-04, earlier session): DISCREPANCY** — headline R²=0.991/1.3 pp not
reproducible from committed code; law survives at R²≈0.92–0.94 / MAE 3.6 pp; prediction-
generator script missing from `src/`. README/PREPRINT/RELATED_WORK now quote audited numbers.

Note: older entries below the log used a different B6–B11 numbering (pre-consolidation);
the README's B1–B13 numbering is canonical.

## HARD GUARDRAILS (never violate)

1. **NEVER submit jobs to real IBM hardware** — the free QPU budget is nearly spent (484/600s).
   Do not read or use `ibm_token.txt`. Simulation only (numpy engine + qiskit-aer).
2. Only work inside this outputs folder and the qrc-shot-wall GitHub repo. No other accounts,
   sites, purchases, emails, or messages.
3. Every claim gets an honesty section. Failed hypotheses are reported as failures.
4. Keep runs within the 45s bash-call limit (chunk long computations).
5. If GitHub push isn't possible in this session, save everything locally and log it under
   "Pending push" below; do not retry endlessly.

## Method rules

- One pre-stated falsifiable hypothesis per benchmark; fit/holdout splits where fitting occurs.
- Reuse the engine: `src/qrc_law.py` (build/eval phases), density-matrix numpy for speed.
- Write results as `results/RESULTS_<NAME>.md` + raw JSON + figure PNG.
- Update the "Log" section of this file after each work session.

## Queue (work top-down)

- [x] Small-margin regime sweep — DONE 2026-07-03 (`results/RESULTS_SMALLMARGIN.md`, B13).
- [x] PREPRINT.md consolidation — DONE 2026-07-03 (v0.1); v0.2 2026-07-04 (related work added).
- [x] RELATED_WORK.md literature pass — DONE 2026-07-04. Positioning of B1–B13 vs prior art;
      closest neighbours: Mujal et al. npj QI 9,16 (2023) and Ahmed/Tennie/Magri QMI 7,31 (2025).
      Key takeaway logged: B2's strategy set *includes* the literature's main mitigation
      proposal (SVD truncation), strengthening the wall claim. No contradicting or
      anticipating prior art found within the stated search limits (see honesty section).
- [ ] **B5 restoration (top priority, from the 2026-07-04 audit).** Consolidation, not a new
      benchmark: commit a prediction-generator script that produces `law_theory.json`-style
      pred from the documented formula; re-run the 150-cell grid with ≥8 documented sampling
      seeds; update RESULTS_LAW.md's headline to the re-run numbers; note the provenance issue
      in its honesty section. Until then, audited numbers (R²≈0.92–0.94, 3.6 pp) are canonical.
- [ ] **AUDIT MODE (standing default).** Do not invent new benchmarks.
      Pick the least-recently-audited benchmark, re-run its key numbers from repo code, check
      every claim in its write-up, append an AUDITS.md entry (confirmed/discrepancy, numbers
      side by side). Audited so far: B13 (2026-07-03, CONFIRMED), B5 (2026-07-04, DISCREPANCY).
      Suggested order: B6 and B11 next (they quote/build on B5's figures), then B2, B10, B12.
- [ ] (Deferred, needs Amirshayan's sign-off: third task family for the within-task IPS
      confirmation; injection-scheme sweep; anything requiring hardware.)

## Log

- 2026-07-03 03:00 — Agenda created. Self-calibration benchmark started in live session.
- 2026-07-03 12:30 — Agenda moved into repo root so scheduled runs can fetch it.
- 2026-07-03 — (multiple sessions) B7–B13 landed; PREPRINT.md v0.1 consolidated; AUDITS.md
  created with B13 independent re-implementation (CONFIRMED).
- 2026-07-04 — Scheduled session: RELATED_WORK.md literature pass (~8 targeted searches,
  verified citations only; unverified author lists omitted). PREPRINT.md Related-work
  placeholder replaced (v0.2). Agenda brought back in sync with README (it had gone stale
  at the B6-era numbering). Post-push, discovered the same-day B5 audit (DISCREPANCY) via the
  repo page — first push had propagated the 0.991 headline; second push same session corrected
  PREPRINT (v0.3), RELATED_WORK, README (B5 paragraph + Start-here) to audited numbers.
  Next run: B5 restoration item above, or audit B6/B11.

## Pending push

(none)
