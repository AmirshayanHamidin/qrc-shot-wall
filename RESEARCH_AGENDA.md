# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-06, Program 2b run #6 scheduled session)

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
- [x] **2026-07-05 — Fashion-MNIST paper Table 3, LogisticRegression row (run #2)**
      (`audits/AUDIT_fashion-mnist-logreg.md`). First audit under the two-commit rule:
      pre-registration commit `788f890` provably precedes the results commit. C=1 ovr l1:
      published 0.842, reproduced **0.8395 — CONFIRMED** (drift −0.25 pp, bar ±0.005); the
      pre-registered secondary prediction (drift strictly between k-NN's 0.15 pp and
      GaussianNB's 5.9 pp) **held**. Two infra-forced, labelled amendments (45 s per-process
      cap): tol=1e-2 instead of the registered 1e-4 default (quantified: 0.02 pp movement
      1e-2→1e-3 on the full pipeline) and per-class ovr assembly (validated against the
      internal multiclass path: 98.9% prediction agreement, no sign flips). "Discretion
      predicts drift" is now 3/3 across rows: k-NN 0.15 pp < LogReg 0.25 pp < GaussianNB 5.9 pp.

- [x] **2026-07-05 — scikit-learn 1.8 docs, digits SVC classification report (run #3)**
      (`audits/AUDIT_sklearn-digits-svc.md` + `audits/audit_digits_svc_run.py`). Two-commit rule:
      pre-registration `b22be5d` provably precedes results `b9e481a`. Published 0.97 (899 test
      samples): reproduced **0.9689 (871/899) — CONFIRMED**; all 33 printed report numbers
      identical at 2 dp across a 1.8.0 -> 1.7.2 version gap (1.8.0 not installable in sandbox;
      pre-declared). Zero-discretion anchor: "discretion predicts drift" now 4/4 —
      docs-SVC ~0.00 pp < k-NN 0.15 pp < LogReg 0.25 pp < GaussianNB 5.9 pp (first point digits,
      others Fashion-MNIST).

- [x] **2026-07-05 — Breiman (2001) "Random Forests", Table 2 ionosphere row, Forest-RI (run #4)**
      (`audits/AUDIT_breiman2001-rf-ionosphere.md` + `audits/audit_rf_ionosphere_run.py` +
      `audits/rf_iono_raw.json`). Two-commit rule: pre-registration `717ce63` provably precedes
      results `bdb2248`. First cross-implementation target (Breiman's 2001 Fortran CART ->
      scikit-learn 1.7.2, a 25-year gap) and first target older than the auditing library:
      Single Input (F=1) published 7.5% -> reproduced **6.69%**; Selection published 7.1% ->
      reproduced **6.36%** — **CONFIRMED** (pre-registered bar ±1.5 pp, both columns, and robust
      across all 3 master seeds; the paper's Selection < Single Input ordering also reproduces).
      Secondary prediction held: drift 0.74–0.81 pp lands between LogReg (0.25) and GaussianNB
      (5.9) — "discretion predicts drift" now 5/5, with cross-implementation+seed discretion
      priced at ~0.8 pp.

- [x] **2026-07-05 — Breiman (2001) Table 2, sonar row, Forest-RI (Program 2b confirmatory audit #1)**
      (`audits/AUDIT_breiman2001-rf-sonar.md` + `audits/audit_rf_sonar_run.py` + `audits/rf_sonar_raw.json`).
      First audit under `audits/PREREG_DRIFT.md` (registered this session BEFORE the audit): blind
      discretion rubric scored **2/5** in the pre-registration commit `babcc6a`, results in `0ad7fad`.
      Single Input published 18.0 -> reproduced **18.19**; Selection published 15.9 -> **17.86**
      (seed 0 primary; pre-registered bar ±2.0 pp) — **CONFIRMED** on all 3 master seeds. Program 2b
      standardized drift (3-seed mean |repro−pub|): **0.59 / 0.94 pp**. Honest caveat: seed-0 Selection
      used 98% of the bar (see the audit's honesty section).

- [x] **2026-07-05 — Gorman & Sejnowski (1988) sonar backprop MLP, aspect-angle-independent 12/24
      hidden rows (Program 2b confirmatory audit #2)** (`audits/AUDIT_gorman1988-sonar-mlp.md` +
      `audits/audit_mlp_sonar_run.py` + `audits/mlp_sonar_raw.json`). Two-commit rule: blind rubric
      **3/5** pre-registered with an empty results section BEFORE results were published (see the
      audit's ordering caveat: prereg ran before any code in the session-local clone; on the remote
      both commits land in this session's batch, prereg first). Oldest target yet (1988, 38-year
      gap), first neural-network family point, same dataset as audit #1 (within-dataset discretion
      contrast). Published 84.7 / 84.5 -> reproduced **75.96 / 75.58** (seed 0; pre-registered bar
      ±5.0 pp) — **DISCREPANCY** on both rows, all 3 seeds; bar not moved. Standardized drift
      (3-seed): **8.95 / 10.35 pp**. Candidate mechanisms (honesty section): sklearn cannot honor
      the paper's squared-error-with-0.2-margin loss, ±0.3 uniform init, 2-unit output coding, or
      per-pattern updates; reproduced ~76% ≈ the paper's own no-hidden-unit row (77.1%), consistent
      with systematic under-training by modern defaults. The 1988 claim is not challenged — its
      *portability* to library defaults is what the drift prices (~9–10 pp at rubric 3/5).

- [x] **2026-07-05 — Hsu, Chang & Lin, "A Practical Guide to SVC", Appendix A.1, svmguide1
      (Program 2b confirmatory audit #3)** (`audits/AUDIT_hsu2003-svmguide1-svc.md` +
      `audits/audit_svmguide1_run.py` + `audits/svmguide1_raw.json`). Two-commit rule:
      pre-registration `098cc566` provably precedes results. Blind rubric scored per column:
      unscaled/scaled-defaults **2/5**, C=2 gamma=2 **1/5** (lowest-discretion confirmatory
      target yet; first kernel-SVM family point). Published 66.925 / 96.15 / 96.875 ->
      reproduced **66.925 / 96.150 / 96.875** (seed 0; pre-registered bar ±2.0 pp) —
      **CONFIRMED**, drift **0.000 pp** on all three columns and all 3 master seeds (exact
      match of the printed counts 2677/3846/3875 of 4000; sklearn SVC wraps LIBSVM — the
      same-engine caveat is in the audit's honesty section).

- [x] **2026-07-06 — LeCun, Bottou, Bengio & Haffner (1998), Fig. 9 "Linear" row, MNIST 12.0%
      (Program 2b audit #4)** (`audits/AUDIT_lecun1998-mnist-linear.md` + pinned runner
      `audits/audit_mnist_linear_run.py`). Two-commit rule: pre-registration `515ce8d` (blind rubric
      **5/5** — first score-5 target) provably precedes everything. **COULD-NOT-RUN**: the pinned
      sklearn-defaults SGD fit is an atomic ≥113 s per class (tol never triggers; 1000-epoch
      trajectory) and this sandbox kills every process at tool-call end, so no faithful execution
      fits the 45 s cap. No reproduced number was ever observed (block is outcome-independent);
      contributes NO drift point, does not count toward n. Full probe evidence and the rejected
      sparse-representation shortcut (numerically divergent regime) in the audit's honesty section.

- [x] **2026-07-06 — Same claim via the paper's other stated route, "directly solving linear
      systems" (Program 2b confirmatory audit #5)** (`audits/AUDIT_lecun1998-mnist-linear-lsq.md` +
      `audits/audit_mnist_linear_lsq_run.py` + `audits/mnist_linear_lsq_raw.json`). Two-commit rule:
      pre-registration `cb9f5b7` precedes results. Blind rubric **2/5**. Published 12.0 ->
      reproduced **13.96** (1,396/10,000 errors; 3 replicates bit-identical, deterministic Cholesky)
      — drift **1.96 pp**, inside the pre-registered ±2.0 pp bar: **CONFIRMED, marginally (98% of
      the bar)**. Largest score-2 drift so far -> logged as mild evidence AGAINST the hypothesis at
      the low-discretion end. First linear-model/1990s family point.

- [x] **2026-07-06 — Breiman (2001) Table 2, "One Tree" column, ionosphere + sonar rows (Program 2b
      confirmatory audit #6)** (`audits/AUDIT_breiman2001-rf-onetree.md` + `audits/audit_rf_onetree_run.py`
      + `audits/rf_onetree_raw.json`). Two-commit rule: prereg `1021e13` web-committed to the remote BEFORE
      any reproduction code ran; results `2fa11ff`. Blind rubric **3/5** — first score-3 point outside the
      neural-network family; measurand is the paper's OOB individual-tree error at the best Forest-RI setting.
      Published 12.7 / 31.7 -> reproduced **13.88 / 33.17** (seed 0; pre-registered bar ±3.0 pp) — **CONFIRMED**
      on all 3 master seeds. Standardized drift (3-seed): **1.08 / 1.34 pp**. The audit's secondary prediction
      FAILED: both score-3 drifts sit below the largest score-2 drift (1.96 pp) — logged as evidence against
      the hypothesis in the mid-score range (see the audit's honesty section).

- [x] **2026-07-06 — Aeberhard, Coomans & de Vel (1992), wine dataset leave-one-out results, LDA/QDA/1NN
      rows (Program 2b confirmatory audit #7)** (`audits/AUDIT_aeberhard1992-wine-loo.md` +
      `audits/audit_wine_loo_run.py` + `audits/wine_loo_raw.json`). Two-commit rule: prereg `d60a39f`
      web-committed to the remote (verified byte-identical, 7080 B) BEFORE any reproduction code ran.
      Blind rubric **2/5 per row** — first discriminant-analysis family points, first fully deterministic
      (no-RNG) pipeline, first dataset-documentation claim class (UCI `wine.names` quoting Tech. Rep.
      92-02; provenance caveat in the audit's honesty item 1). Published 98.9 / 99.4 / 96.1 (% correct,
      LOO, z-transformed) -> reproduced **98.876 / 99.438 / 95.506** (pre-registered bar ±1.5 pp) —
      **CONFIRMED**; LDA and QDA match the published LOO error counts EXACTLY (2 and 1 of 178) across a
      34-year gap; 1NN differs by one LOO case. Standardized drift (3 seeds bit-identical): **0.02 /
      0.04 / 0.59 pp**. Secondary prediction HELD (all ≤ 1.96 pp). Sensitivity checks: scaler scope and
      priors numerically inert; raw features collapse 1NN to 76.97 (the z-transform qualifier is
      load-bearing exactly where the rubric said).

- [x] **2026-07-06 — Sigillito, Wing, Hutton & Baker (1989) ionosphere linear perceptron + Aha 1NN
      (Program 2b confirmatory audit #8)** (`audits/AUDIT_sigillito1989-ionosphere-perc-1nn.md` +
      `audits/audit_iono_perc1nn_run.py` + `audits/iono_perc1nn_raw.json`). Two-commit rule: prereg
      `e5decc2` web-committed to the remote (verified byte-identical, 8333 B) BEFORE any reproduction
      code existed. **First EXECUTED score-5 point** (the prior score-5, audit #4, was infra-blocked):
      blind rubric **5/5** for the paper's gradient-trained linear unit (primary source PDF fetched and
      read this session — JHU APL Technical Digest 10(3)), **2/5** for the 1NN dataset-doc row. Published
      90.67 / 92.1 -> reproduced **91.333 / 92.053** (seed 0; bars +/-5.0 / +/-2.0 pp) — **CONFIRMED**
      on both rows, all 3 seeds; the 1NN row matches the implied published correct count EXACTLY
      (139/151). Standardized drift (3-seed): **1.11 / 0.05 pp**. The audit's secondary prediction
      FAILED in its second clause: the score-5 drift (1.11 pp) sits BELOW the largest score-2 drift
      (1.96 pp) — first direct evidence against the hypothesis at the high-discretion end.

### Queue (candidate targets for future runs)

- [x] ~~Another Table 3 row from the same paper with a different discretion profile~~ — DONE
      run #2 (LogisticRegression C=1 ovr l1, see Completed audits). Still open from this bullet:
      DecisionTree entropy/depth-10 → 0.798 (adds *seed* discretion, a profile not yet tested).
- [x] ~~scikit-learn's own documented example numbers~~ — digits SVC report DONE run #3
      (see Completed audits). Still open from this bullet: LFW eigenfaces table.
- [ ] Fashion-MNIST DecisionTree entropy/depth-10 -> 0.798 — **infra-blocked in this sandbox**
      (run #3 synthetic probe: >=2 min single-process fit vs hard 45 s cap; no claim-preserving
      amendment). Needs an environment without the per-process cap.
- [x] ~~A published UCI-scale ablation row from a widely cited repo README.~~ — DONE run #4, with a
      widely cited *paper* table instead of a repo README (Breiman 2001 Table 2, ionosphere; see
      Completed audits). Still open from this bullet: a row sourced from an actual repo README;
      also LFW eigenfaces (run #3 bullet) and other Breiman Table 2 rows (sonar, glass, diabetes)
      if a cross-implementation *ladder within one paper* is wanted.

## Program 2b — pre-registered drift study (discretion predicts drift)

Registered 2026-07-05 in `audits/PREREG_DRIFT.md` (commit `ad8aa31`) BEFORE any confirmatory audit:
Spearman rho(blind discretion score, |drift| pp) > 0.5 with p < 0.01, tested ONCE at n=30 confirmatory
audits, verdict published either way in RESULTS_DRIFT.md. The 5 pre-registration audits (Program 2
runs #1–#4) are EXPLORATORY and excluded from the confirmatory set.

**Tracker: n = 7/30 confirmatory audits** (audit #4 was COULD-NOT-RUN and contributes nothing).
Points (blind score, |drift| pp): (2, 0.59), (2, 0.94) [Breiman sonar], (3, 8.95), (3, 10.35)
[Gorman-Sejnowski sonar MLP], (2, 0.00), (2, 0.00), (1, 0.00) [Hsu-Chang-Lin svmguide1],
(2, 1.96) [LeCun-1998 MNIST linear via least squares], (3, 1.08), (3, 1.34) [Breiman 2001
Table 2 "One Tree" column, ionosphere/sonar], (2, 0.02), (2, 0.04), (2, 0.59) [Aeberhard-1992
wine LOO, LDA/QDA/1NN], (5, 1.11), (2, 0.05) [Sigillito-1989 ionosphere perceptron / Aha 1NN].
Running rho (EXPLORATORY until n=30): spearmanr over the 15 points = **0.739, p = 0.0016** —
directionally consistent, no confirmatory weight. Score coverage now {1, 2, 3, 5}: run #7 landed
the first executed score-5 point and it came in LOW (1.11 pp, below the 1.96 pp score-2 ceiling;
run #7's secondary prediction failed on that clause) — the high end of the discretion scale is no
longer unexplored, but it currently leans against the hypothesis, joining the run #5 mid-range
lean. Priorities: score-0 and score-4 targets, more score-5 points (the blocked audit #4 SGD
target remains re-runnable in a cap-free environment), and new families/decades (boosting —
Freund & Schapire 1996 UCI tables — remains unclaimed).

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
- 2026-07-05 (scheduled session, Program 2 run #2) — Second replication audit landed:
  LogisticRegression row of Fashion-MNIST Table 3 (see Completed audits and
  `audits/AUDIT_fashion-mnist-logreg.md` + `audits/audit_logreg_run.py`). First use of the
  two-commit pre-registration rule — ordering provable from git history alone, no witness
  needed. Sandbox constraint discovered and documented for future runs: **hard 45 s
  per-process execution cap; background processes are SIGKILLed between shell calls**
  (signal-masking tested, does not survive), so liblinear (no warm start) ran as per-class
  ovr fits at tol=1e-2 — both reported as labelled amendments with sensitivity checks in the
  audit file. Freshness verified against the commits page per HARD GUARDRAIL 6 (HEAD
  `ff1575b` at session start). Program 1 untouched; its audit queue (B6/B11 next,
  qrc_law.png regeneration, B5 regression cells) unchanged.

- 2026-07-05 (scheduled session, Program 2 run #3) — Third replication audit landed: scikit-learn
  1.8 docs digits SVC report (`audits/AUDIT_sklearn-digits-svc.md` + `audits/audit_digits_svc_run.py`),
  verdict CONFIRMED (0.9689 vs 0.97; 33/33 printed numbers identical across the 1.8.0 -> 1.7.2
  gap; two-commit rule `b22be5d` -> `b9e481a`). Queue's first candidate (DecisionTree row)
  found infra-blocked by a synthetic timing probe BEFORE any pre-registration; the switch to the
  next queue item was pre-declared inside the audit file. Stale-CDN incident #4 (mild): post-commit
  verification via un-pinned raw URL returned the pre-results file even WITH a cache-buster —
  re-verified pinned to the HEAD SHA. Practical rule for future runs: verify pushes pinned to SHA,
  not just cache-busted. Editor typing artifacts during commit 1 were repaired before committing
  and are disclosed in the audit's honesty section (item 5). Program 1 untouched; its audit queue
  (B6/B11 next, qrc_law.png regeneration, B5 regression cells) unchanged.

- 2026-07-05 (scheduled session, Program 2 run #4) — Fourth replication audit landed: Breiman
  (2001) Table 2, ionosphere Forest-RI row (`audits/AUDIT_breiman2001-rf-ionosphere.md` +
  `audits/audit_rf_ionosphere_run.py` + `audits/rf_iono_raw.json`), verdict **CONFIRMED**
  (6.69/6.36 vs published 7.5/7.1, pre-registered bar ±1.5 pp, robust across 3 master seeds;
  two-commit rule `717ce63` -> `bdb2248`). First cross-implementation audit and first target
  older than the auditing library; drift (~0.8 pp) lands exactly where the discretion ladder
  predicted — now 5/5. Freshness verified against the commits page per HARD GUARDRAIL 6 (HEAD
  `2abb3bb` at session start); all pushes verified pinned to SHA per run #3's rule. One editor
  incident, disclosed in the audit's honesty item 8: a selectAll+paste on the lazily-rendered
  web editor replaced only rendered lines, briefly duplicating old text — caught on screen
  before committing, re-pasted whole, committed file verified byte-identical to the local copy.
  Program 1 untouched; its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression
  cells) unchanged.

- 2026-07-05 (scheduled session, Program 2b run #1) — Pre-registration + first confirmatory audit
  landed. `audits/PREREG_DRIFT.md` committed BEFORE the audit (`ad8aa31`: hypothesis, blind 0–5
  discretion rubric, 3-seed standardized drift, n=30 one-shot Spearman test). Audit #1: Breiman 2001
  Table 2 sonar (rubric 2/5 in prereg commit `babcc6a` -> results `0ad7fad`, script `46bd70c`, raw
  `ce84b48`): **CONFIRMED**, 3-seed drift 0.59/0.94 pp — see Completed audits. Incidents (cosmetic,
  disclosed in the audit's honesty section): Copilot commit-message autofill garbled the PREREG
  commit's message (file content verified byte-identical via git fetch + MD5); the session-outputs
  mount served stale copies of freshly edited files twice (worked around by writing sandbox-local);
  GitHub's web commit appended a trailing newline to rf_sonar_raw.json (20494 vs 20493 bytes,
  JSON-identical). No lazy-render paste incidents: all editor content this session was injected via
  the CodeMirror document API with length verification, and every push was verified by git fetch +
  MD5 against the local copy (stronger than SHA-pinned raw fetches). Program 1 untouched; its audit
  queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells) unchanged.
- 2026-07-05 (scheduled session, Program 2b run #2) — Second confirmatory audit landed: Gorman &
  Sejnowski (1988) sonar MLP, aspect-angle-independent 12/24-hidden rows — verdict **DISCREPANCY**
  (75.96/75.58 vs 84.7/84.5, pre-registered bar ±5.0 pp, all 3 seeds outside; 3-seed drift
  8.95/10.35 pp at blind rubric 3/5; see Completed audits). Tracker n=2/30; exploratory rho over 4
  points = 0.894 (p=0.106). Incidents, disclosed in the audit's honesty section: (a) no git push
  credentials in this sandbox, so remote publication used the GitHub web editor at session end —
  remote prereg commit precedes results, but the reproduction had already run in-session
  (local-clone ordering only). **New guardrail for Program 2b: web-commit the pre-registration to
  the remote BEFORE running any reproduction code**, as run #1 did. (b) The session-outputs mount
  again served stale/truncated copies of edited files (incident class from run #1); a truncated
  results file was briefly committed to the session-local clone, caught by byte/UTF-8 checks before
  publication, and all published files were rebuilt sandbox-locally and re-verified. (c) The first
  seed-0 process hit the 45 s cap (fetch+run combined) and was deterministically re-run; audit #1's
  sonar cache reused after md5 match. Program 1 untouched; its audit queue (B6/B11 next,
  qrc_law.png regeneration, B5 regression cells) unchanged.

## Pending push

(none)

- 2026-07-05 (late scheduled session, Program 2b run #3) — Third confirmatory audit landed:
  Hsu-Chang-Lin practical-guide Appendix A.1, svmguide1 SVC (see Completed audits and
  `audits/AUDIT_hsu2003-svmguide1-svc.md`) — **CONFIRMED with 0.000 pp drift** on all three
  pre-registered columns, exact match of the guide's printed correct-prediction counts. First
  kernel-SVM family point, first score-1 rubric point; tracker n=3/30, exploratory rho 0.827
  (p=0.022, no confirmatory weight). Session infrastructure notes: this sandbox exposes NO git
  credentials — publication ran through the GitHub web uploader via the browser; the upload
  form silently dropped the typed commit-1 summary (generic "Add files via upload"), disclosed
  in the audit's honesty section — future runs should re-check the message field before
  committing. Program 1 untouched; its audit queue (B6/B11 next, qrc_law.png regeneration,
  B5 regression cells) unchanged.

- 2026-07-06 (scheduled session, Program 2b run #4) — Two audits landed on one claim (LeCun et al.
  1998, MNIST linear classifier, Fig. 9 "Linear" 12.0%; number verified from a public mirror of the
  paper this session). Audit #4 (gradient-descent route, blind rubric 5/5, prereg `515ce8d`
  web-committed before any reproduction code ran, per the run #2 guardrail): **COULD-NOT-RUN** —
  new incident class confirmed: this sandbox kills ALL user processes at tool-call end (setsid/nohup
  sentinels dead at next call), so the pre-declared background-poll mitigation is impossible here;
  the pinned defaults fit is an atomic ≥113 s/class (tol=1e-3 never triggers on squared loss;
  probes: 1 epoch = 1.2 s, 230 epochs = 26.1 s with n_iter_=230). A sparse-CSR shortcut (10x faster)
  was tested and REJECTED: in this numerically unstable default regime dense-vs-sparse coefficients
  diverge to ~1e12 differences (48.5% prediction agreement on a subset probe) — switching
  representation post-prereg would have changed the measurand. No reproduced number was observed;
  no drift point; target remains available for a cap-free environment. Audit #5 (same claim via the
  paper's stated "directly solving linear systems" route, rubric 2/5, prereg `cb9f5b7` committed
  before the run): reproduced 13.96 vs published 12.0 — drift 1.96 pp, **CONFIRMED marginally at
  98% of the ±2.0 pp bar**, 3 bit-identical replicates; logged as the largest score-2 drift so far
  (mildly against the hypothesis at the low end). Tracker n=4/30, exploratory rho over 8 points =
  0.803 (p=0.016, no confirmatory weight). All publication via GitHub web uploader (no git
  credentials in sandbox, as in runs #2–#3); commit messages verified in the DOM before submitting
  (run #3 guardrail) and every push verified by cache-busted raw fetch + MD5. Program 1 untouched;
  its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells) unchanged.

- 2026-07-06 (scheduled session, Program 2b run #5) — Sixth confirmatory audit landed: Breiman (2001)
  Table 2 "One Tree" column, ionosphere + sonar (see Completed audits) — **CONFIRMED** (13.88/33.17 vs
  12.7/31.7, bar ±3.0 pp, all 3 seeds; 3-seed drift 1.08/1.34 pp at blind rubric 3/5). The audit's
  secondary prediction FAILED (both score-3 drifts < the 1.96 pp score-2 point) — second consecutive
  run leaning against the hypothesis in the low/mid range; tracker n=5/30, exploratory rho over 10
  points = 0.753 (p=0.012, no confirmatory weight). Score coverage still {1,2,3}: the blocked score-5
  target (audit #4) remains the top diversification priority for a cap-free environment. Publication
  via GitHub web editor/uploader (no git credentials in sandbox, as in runs #2–#4); prereg committed
  to the remote before any code ran (run #2 guardrail); commit messages DOM-verified (run #3
  guardrail); every push verified by SHA-pinned fetch with exact byte counts (prereg 6492 B, results
  10251 B, raw JSON 87442 B). The prereg commit message again acquired an autofill-appended
  description (disclosed in the audit's honesty item 5). Program 1 untouched; its audit queue (B6/B11
  next, qrc_law.png regeneration, B5 regression cells) unchanged.

- 2026-07-06 (scheduled session, Program 2b run #6) — Seventh confirmatory audit landed: Aeberhard,
  Coomans & de Vel (1992) wine LOO results, LDA/QDA/1NN rows (see Completed audits) — **CONFIRMED**
  (98.876/99.438/95.506 vs 98.9/99.4/96.1, bar ±1.5 pp; drifts 0.02/0.04/0.59 pp at blind rubric
  2/5 per row; LDA and QDA exact on the published LOO error counts). Secondary prediction HELD —
  first run since #3 to land in the hypothesis-consistent direction; tracker n=6/30, exploratory rho
  over 13 points = 0.760 (p=0.0026, no confirmatory weight). New claim class documented: dataset-
  documentation numbers (UCI wine.names quoting Tech. Rep. 92-02), provenance one step from the
  primary source — flagged in the audit's honesty item 1. Publication via GitHub web uploader (no
  git credentials in sandbox, as in runs #2–#5); prereg web-committed to the remote (`d60a39f`,
  byte-verified 7080 B) before any reproduction code ran (run #2 guardrail); commit message
  DOM-verified pre-submit (run #3 guardrail), no autofill description this time; freshness confirmed
  against the commits page (HEAD `3889133` at session start) per HARD GUARDRAIL 6. Program 1
  untouched; its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells) unchanged.
  New incident class (no files of record affected): the sandbox's outputs mount serves STALE,
  SIZE-TRUNCATED views of files edited after creation (post-edit local `wc -c`/`md5sum` reported the
  pre-edit size with new content cut mid-line), so LOCAL checksum verification is unreliable in this
  environment. The web uploader reads the true files (upload byte totals matched, and every SHA-pinned
  remote fetch verified complete content: audit 11338 B, script 4299 B, JSON 1810 B, agenda 34597 B).
  Guardrail for future runs: treat SHA-pinned remote fetch as the ONLY valid post-push verification;
  never trust mount-side sizes/checksums of files edited in-session.

- 2026-07-06 (scheduled session, Program 2b run #7) — Eighth confirmatory audit landed: Sigillito et
  al. (1989) ionosphere linear perceptron + Aha 1NN from ionosphere.names (see Completed audits) —
  **CONFIRMED** (91.333/92.053 vs 90.67/92.1, bars +/-5.0/+/-2.0 pp, all 3 seeds; 3-seed drift
  1.11/0.05 pp at blind rubric 5/5 and 2/5; 1NN exact on the implied correct count 139/151). First
  EXECUTED score-5 point — and it landed below the score-2 ceiling (secondary-prediction clause
  failed), the first direct evidence against the hypothesis at the high-discretion end; tracker
  n=7/30, exploratory rho over 15 points = 0.739 (p=0.0016, no confirmatory weight). Primary source
  strengthened over run #6's precedent: the 1989 JHU APL Technical Digest PDF was fetched and read
  directly (90.67% verified in the paper's own text), while the 1NN row remains dataset-doc class.
  Publication via GitHub web editor (no git credentials in sandbox, as in runs #2–#6); prereg
  web-committed to the remote (`e5decc2`, byte-verified 8333 B) before any reproduction code existed
  (run #2 guardrail); commit-dialog Copilot autofill (message + description) replaced/cleared and
  DOM-verified pre-submit (run #3 guardrail); freshness confirmed against the commits page (HEAD
  `2d9890d` at session start) per HARD GUARDRAIL 6; all pushes verified by SHA-pinned raw fetch with
  exact byte counts per the run #6 guardrail (local mount checksums not trusted). Program 1
  untouched; its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells) unchanged.
