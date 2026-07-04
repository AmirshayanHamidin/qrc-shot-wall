# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-04, scheduled audit session)

Repo: github.com/AmirshayanHamidin/qrc-shot-wall. **The README is ground truth for what is done; trust it over this file if they ever disagree.**

- Benchmarks **B1–B13 complete** and pushed (see README + `results/RESULTS_*.md`). Arc: wall (B1–B4) → law (B5–B6) → limits (B7–B10) → external validity & design (B11–B13, incl. the small-margin scope correction).
- **PREPRINT.md v0.2** at repo root: full 13-benchmark consolidation; Related-work section now populated.
- **RELATED_WORK.md** at repo root: dedicated literature pass (2026-07-03) with per-benchmark positioning, verified citations, and an honesty section listing what was read at abstract level only.
- **AUDITS.md**: B13 independently re-implemented and CONFIRMED (2026-07-03). **B5 audited 2026-07-04 — DISCREPANCY FOUND**: the headline R²=0.991 / MAE 1.3 pp is not reproducible from committed code (full 150-cell re-run gives R²=0.922, MAE 3.64 pp, noise-corrected R²≈0.94 — law survives qualitatively); published obs not regenerable on ≥12 cells (worst 17.6 pp off, outside an 8-seed range); pred-generator script missing from `src/`. See AUDITS.md for the full entry. **Until re-baselined, treat 0.991/1.3pp as unaudited wherever quoted (README TL;DR §Benchmark 5, PREPRINT abstract & §4, B6/B10/B11 texts).**
- Live QPU validation done earlier (0.886 on ibm_marrakesh); QPU budget nearly spent — hard guardrail 1 below stands.

## HARD GUARDRAILS (never violate)

1. **NEVER submit jobs to real IBM hardware** — the free QPU budget is nearly spent (484/600s).
   Do not read or use `ibm_token.txt`. Simulation only (numpy engine + qiskit-aer).
2. Only work inside the session outputs folder and the qrc-shot-wall GitHub repo. No other accounts,
   sites, purchases, emails, or messages.
3. Every claim gets an honesty section. Failed hypotheses are reported as failures.
4. Keep runs within the 45s bash-call limit (chunk long computations; partial .npy checkpoints).
5. If GitHub push isn't possible in a session, save everything locally, log it under "Pending push",
   and stop gracefully; do not retry endlessly.

## Method rules

- One pre-stated falsifiable hypothesis per benchmark; fit/holdout splits where fitting occurs.
- Reuse the engine (`src/qrc_law.py` build/eval phases; density-matrix numpy for speed).
- Write results as `results/RESULTS_<NAME>.md` + raw JSON + figure PNG; push agenda updates in the same batch.
- Update the Log section after each work session.

## Queue (work top-down)

Science queue (wall/law/design program) is **empty** — the scoping study is complete. Sessions now run in one of two modes:

0. **PRIORITY — B5 re-baseline (consequence of the 07-04 audit; consolidation, not a new
   benchmark).** Re-run the 150-cell law grid with ≥8 documented sampling seeds and a single
   committed generator script (build → obs → pred in one reproducible path, replacing the
   missing original), publish `results/law_rebaseline.json`, then update README/PREPRINT
   headline numbers to the audited values (expect R²≈0.92–0.95, MAE≈2–3.6 pp — still a strong
   zero-parameter law, honestly stated). Keep `law_theory.json` untouched as historical record.
1. **AUDIT MODE (default).** Pick the least-recently-audited benchmark from AUDITS.md coverage
   (audited so far: B13, B5 — suggested next: B6, which quotes B5's machinery; then B2, B1, …),
   re-run its key numbers from repo code, check every claim in its write-up, push an AUDITS.md
   entry (CONFIRMED / DISCREPANCY, numbers side by side). Goal: a bulletproof preprint.
   Do NOT invent new benchmarks.
2. **Consolidation touch-ups** (only if spotted during audits): fixing stale cross-references
   (e.g. README still lists the small-margin sweep as "queued" in its Honest-limitations paragraph —
   correct opportunistically when the README is next edited for other reasons), figure regeneration,
   PREPRINT polish.

Flagged before any arXiv submission (from RELATED_WORK.md honesty section, needs the user, not a scheduled run):
- Full-text comparison of IPS (B12) vs Hu et al.'s resolvable-expressive-capacity/eigentask framework
  (PRX 13, 041020) — the one place a novelty claim could narrow.
- Re-check the two 2026 citations taken from title/indexed summary (arXiv:2604.28160, arXiv:2602.14677).

## Log

- 2026-07-03 03:00 — Agenda created. B6 (self-cal law) started live.
- 2026-07-03 12:30 — Agenda moved into repo root so scheduled runs can fetch it; B6 numbers summarized.
- 2026-07-03 (day) — B6–B13 executed and pushed across sessions; PREPRINT.md v0.1 consolidated; AUDITS.md started with independent B13 re-implementation (CONFIRMED). [Reconstructed from repo state; the older 03:00 "State" section of this file was stale and has been rewritten.]
- 2026-07-03 (evening, scheduled) — **RELATED_WORK.md literature pass completed** (7 thematic searches; ~25 works positioned against B1–B13; load-bearing citations venue-verified; honesty section lists abstract-only reads and the IPS-vs-eigentask open question). PREPRINT.md bumped to v0.2 with the Related-work section filled. Agenda rewritten to reflect true state. Science queue now empty → next sessions default to AUDIT MODE starting at B1.
- 2026-07-04 (scheduled) — **AUDIT MODE: B5 audited — DISCREPANCY.** Deviated from the "B1 first" suggestion (all of B1–B12 tied at never-audited) to audit the most load-bearing claim first. Full 150-cell re-run from committed code (all 6 archs rebuilt, `law_eval_arch.py` seeds (1,2), plus 8-seed worst-cell check, 4 alternative protocol conventions, a noise-floor analysis, and a pred reconstruction matching published pred to 1.2–1.4 pp). Law confirmed qualitatively (R²=0.922 / MAE 3.64 pp; noise-corrected R²≈0.94); headline 0.991/1.3 pp not reproducible; published obs provenance unclear; pred generator missing. Pushed: AUDITS.md entry, `results/audit_b5_repro.json`, `src/audit_law_theory.py`, this agenda. Queue re-pointed at B5 re-baseline (item 0), then B6 audit.

## Pending push

(none)
