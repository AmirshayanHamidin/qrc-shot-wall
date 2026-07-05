# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-04, evening scheduled session)

Repo: github.com/AmirshayanHamidin/qrc-shot-wall. **The README is ground truth for what is done; where this file lags, trust the README.**

Benchmarks **B1–B13 complete and pushed** (see README + `results/`). Highlights: the shot wall (B2),
the parameter-free measurement-wall law (B5, R²=0.991, QPU-validated), gate noise as effective
shots with mapped limits (B6–B8), pilot-run margin estimation (B9), retraining as load-bearing
(B10), second task family (B11), IPS topology design rule (B12) with small-margin scope
correction (B13). **PREPRINT.md consolidated (v0.2). RELATED_WORK.md literature pass done
(2026-07-04)** — preprint Related-work section populated with verified citations.
**AUDITS.md started** — B13 independently re-implemented and CONFIRMED (2026-07-03).
**B5 audit (2026-07-04, earlier session): DISCREPANCY** — headline R²=0.991/1.3 pp not
reproducible from committed code. **B5 RESTORATION DONE (2026-07-04, later session):**
canonical generator committed (`src/qrc_law_predict.py`, convention pinned), 150-cell grid
re-run with 8 documented seeds (`src/qrc_law_rerun.py`, per-seed cells in
`results/law_rerun.json`). Restored headline: **R²=0.939 (0.944 noise-corr.), MAE 3.3 pp,
bias −1.0 pp**; 8-seed noise floor 0.9 pp. RESULTS_LAW.md rewritten around the restored
numbers + provenance note; README/PREPRINT (v0.4)/AUDITS updated in the same batch.

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
6. **CACHE-BUST EVERY FETCH.** raw.githubusercontent.com serves stale CDN copies to fresh
   sessions (three B13 duplications so far, incl. one accidental overwrite of a file of
   record). Before choosing a work mode: (a) fetch README/agenda with `?cb=<timestamp>`
   appended, AND (b) load github.com/AmirshayanHamidin/qrc-shot-wall/commits/main in the
   browser and confirm the fetched content mentions the latest commits. If the two disagree,
   trust the commits page and re-fetch pinned to the HEAD SHA.

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
- [x] **B5 restoration — DONE 2026-07-04.** Generator committed (`src/qrc_law_predict.py`),
      8-seed re-run (`results/law_rerun.json`), RESULTS_LAW.md headline replaced
      (R²=0.939/0.944, MAE 3.3 pp), provenance note added, README/PREPRINT/AUDITS synced.
      Leftovers folded into audit mode: 30 regression cells not re-run;
      `figures/qrc_law.png` still shows the original run (regenerate from law_rerun.json).
- [ ] **AUDIT MODE (standing default).** Do not invent new benchmarks.
      Pick the least-recently-audited benchmark, re-run its key numbers from repo code, check
      every claim in its write-up, append an AUDITS.md entry (confirmed/discrepancy, numbers
      side by side). Audited so far: B13 (2026-07-03, CONFIRMED; +2026-07-04 same-convention
      repros #2 and #3, see AUDITS.md addenda), B5 (2026-07-04, DISCREPANCY → RESTORED
      same day). Suggested order: B6 and B11 next (they quote/build on B5's figures), then
      B2, B10, B12. Also open: B5 regression cells (30) re-run; regenerate
      figures/qrc_law.png from law_rerun.json.
- [ ] (Deferred, needs Amirshayan's sign-off: third task family for the within-task IPS
      confirmation; injection-scheme sweep; anything requiring hardware.)

## Program 2 — third-party replication audits (VAR)

Goal: make replication a routine, logged, public pass. Each scheduled Program 2 run picks ONE
published, small-scale, CPU-reproducible ML claim (public code+data, permissive access),
pre-registers the expected number and tolerance in writing BEFORE running, reproduces it in the
sandbox, and publishes `audits/AUDIT_<paper-or-repo>.md` with claim, source, tolerance, reproduced
number, verdict (CONFIRMED / DISCREPANCY / COULD-NOT-RUN), environment, and an honesty section.
Verdicts are about numbers, never accusations; unexplained gaps default to environment differences.

**RESOLVED (2026-07-05, same day):** the missing `PROTOCOL.md` flagged by run #1 was committed
by Amirshayan later that morning (VAR v1.0, six rules). Program 2 runs now follow it directly.
Run #1's compliance was checked retroactively: rules 1, 2, 5, 6 held; rule 4 N/A for replication
audits; rule 3 (code lives in the repo) was initially violated — the reproduction script sat in
ephemeral session storage — and was corrected the same session (`audits/audit_run.py`).

### Program 2 method rules

- **Two-commit pre-registration (MANDATORY from audit #2, adopted 2026-07-05 after human review
  of audit #1):** commit the audit file with the pre-registration section and an EMPTY results
  section BEFORE any experiment runs; commit results in a separate later commit. The ordering
  must be provable from commit history alone, with nobody's testimony required. Audit #1 landed
  both in one commit (`d19a3e9`) — order was verified by A.H. against the session transcript and
  signed off (see the audit's Rule 6 sign-off section), but that required a witness; this rule
  removes the need for one.

### Completed audits

- [x] **2026-07-05 — Fashion-MNIST paper benchmark, Table 3 (arXiv:1708.07747)**
      (`audits/AUDIT_fashion-mnist-benchmark.md`). Two rows, pre-registered tolerance ±0.005.
      k-NN (distance, k=5, p=2): published 0.852, reproduced **0.8535 — CONFIRMED**.
      GaussianNB: published 0.511, reproduced **0.5703 — DISCREPANCY** (+5.9 pp, favorable
      direction; post-hoc probe shows the row is fragile to the implementation's variance floor —
      4 pp swing across var_smoothing 1e-11…1e-5 — while the discretion-free k-NN row reproduces
      to 0.15 pp after nine years of sklearn releases). Takeaway: within one published table,
      reproducibility tracks how much numerical discretion the algorithm leaves the library.

### Queue (candidate targets for future runs)

- [ ] Another Table 3 row from the same paper with a different discretion profile
      (e.g. LogisticRegression C=1 ovr → 0.842, or DecisionTree entropy/depth-10 → 0.798 with
      seed variance) — tests the "discretion predicts drift" reading of audit #1.
- [ ] scikit-learn's own documented example numbers (digits SVC report, LFW eigenfaces table).
- [ ] A published UCI-scale ablation row from a widely cited repo README.

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
- 2026-07-04 (later scheduled session) — Started from a stale CDN README (pre-B13) and
  independently re-implemented B13 before discovering the published version — numbers
  reproduced exactly; logged as an AUDITS.md addendum, nothing overwritten. Then executed
  the real queue top: **B5 restoration** (generator committed, 8-seed 150-cell re-run,
  R²=0.939/MAE 3.3 pp, RESULTS_LAW.md rewritten, README/PREPRINT v0.4/AUDITS synced).
  Next run: audit B6 or B11 (audit mode); optional: regenerate qrc_law.png, B5 regression
  cells. Practical note for future sessions: ALWAYS cache-bust raw.githubusercontent
  fetches (append `?cb=<date>`) — stale CDN copies have now caused duplicate B13 work twice.
- 2026-07-04 (evening scheduled session) — **Stale-cache incident #3 + repair.** Session
  fetched README/agenda without a cache-buster, received a pre-B13 CDN copy (which also hid
  the anti-stale rule added after incident #2), concluded the small-margin sweep was still
  queued, and re-implemented B13 (own pre-registration written before running; its pooled H1
  failed and H2/H3 held, consistent with the published verdicts; numbers matched the
  2026-07-03 audit implementation to reported precision — same natural seed convention).
  Commit `a2ed28d` briefly overwrote `src/qrc_smallmargin.py` and added a stray fig script
  before the published B13 was discovered via the repo pages. **Repaired same session:**
  published code restored byte-for-byte from `97319c2`, fig script replaced with a
  provenance stub, AUDITS.md second addendum appended, and the cache-bust rule promoted to
  HARD GUARDRAIL 6. No results/figures/JSON files of record were touched. Next run: audit
  B6 or B11 (audit mode); optional: regenerate qrc_law.png, B5 regression cells re-run.

- 2026-07-05 (scheduled session, Program 2 run #1) — First third-party replication audit landed:
  Fashion-MNIST paper Table 3 (see Program 2 section above and `audits/AUDIT_fashion-mnist-benchmark.md`).
  Methodology extracted from the repo's `benchmark/runner.py` (StandardScaler fit on train — an
  easy-to-miss detail without which neither row is meaningful); data MD5-verified; pre-registration
  written before any run. Also discovered and flagged: the Program 2 task file's PROTOCOL.md does
  not exist in the repo. Program 1 (B1–B13) untouched this session; its audit queue (B6/B11 next,
  qrc_law.png regeneration, B5 regression cells) remains as listed above.

## Pending push

(none)
