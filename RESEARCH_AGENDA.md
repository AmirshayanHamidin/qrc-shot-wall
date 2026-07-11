# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-11, Program 2b CONFIRMATORY TEST session — the drift study is ANSWERED)

Repo: github.com/AmirshayanHamidin/qrc-shot-wall. **The README is ground truth for what is done; where this file lags, trust the README.**

**PROGRAM 2b VERDICT (2026-07-11): SUPPORTED.** The one-shot pre-registered test of
`audits/PREREG_DRIFT.md` was executed per the audit-#30 binding hand-off, over exactly the 67
closed points and no others: **Spearman rho = 0.587 (bar > 0.5), p = 1.7e-07 two-sided (bar
< 0.01); permutation cross-check 0/10⁶ exceedances.** Full table, sensitivity checks and the four
pre-logged confounders in **`results/RESULTS_DRIFT.md`**; runner + frozen dataset + raw output in
`audits/drift_confirmatory_{test.py,points.json,result.json}`. No points were added, no rubric
re-scored, PREREG_DRIFT.md untouched. The confirmatory set is closed; further drift work is
exploratory or needs a NEW pre-registration.

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

- [x] **2026-07-06 — Freund & Schapire (1996) "Experiments with a New Boosting Algorithm", Table 2
      glass rows, C4.5 alone + boosting C4.5 (Program 2b confirmatory audit #9)**
      (`audits/AUDIT_freund-schapire1996-boost-c45-glass.md` + `audits/audit_fs96_boost_glass_run.py` +
      `audits/fs96_boost_glass_raw.json`). Two-commit rule: prereg `c364bac` web-committed to the remote
      (verified byte-identical, 9516 B) BEFORE any reproduction code existed. **First boosting-family
      points and first score-4 points** (the exact coverage gap named by run #7): blind rubric **4/5 per
      row** (primary source: the ICML-96 author PDF, fetched and read this session). Published 31.7 / 22.7
      (% test error, 10-run averaged 10-fold CV) -> reproduced **31.682 / 20.981** (seed 0; bar ±4.0 pp) —
      **CONFIRMED** on both rows, all 3 seeds; the tree row is within one pooled test case of the 1996
      number, and boosting's published 9-pp improvement reproduces as 10–11 pp. Standardized drift
      (3-seed): **0.23 / 1.36 pp**. Secondary prediction FAILED (both score-4 drifts below the 1.96 pp
      score-2 ceiling). Sharpest finding (sensitivity, honesty item 1): with sklearn's pure-default base
      tree the boosted committee degenerates to a single tree (perfect-fit early stop) and lands 9.31 pp
      OUT — the pre-pinned C4.5 -m2 mapping (entropy, min_samples_leaf=2) is load-bearing for the row;
      the paper-faithful M1-with-resampling route agrees with sklearn's SAMME to 0.05 pp.

- [x] **2026-07-06 — NIST/ITL StRD Linear Least Squares certified R-squared, Longley (1967) + Filip
      (Program 2b confirmatory audit #10)** (`audits/AUDIT_nist-strd-lls-longley-filip.md` +
      `audits/audit_nist_lls_run.py` + `audits/nist_lls_raw.json`). Two-commit rule: prereg `4ad15b8`
      web-committed to the remote (verified byte-identical, 8388 B) BEFORE any reproduction code existed.
      **First score-0 points** (the tracker's #1 coverage gap) and first regression-family target; oldest
      claim year in the program (Longley 1967 JASA). Blind rubric **0/5 both columns** — 16-digit certified
      values, data verbatim in the claim files, zero statistical discretion. Published (certified R², pp)
      99.5479004577296 / 99.6727416185620 -> reproduced **99.54790045772953 / 99.55957626651001**
      (bar ±0.1 pp, the program's tightest) — **DISCREPANCY**: Longley passes at machine precision
      (−7.1e-14 pp) but Filip lands at −0.1132 pp, 13% outside the bar. Cause isolated: numpy lstsq's
      rcond=None truncation policy rank-truncates Filip's condition-1e15 design; scipy's gelsd on the
      identical estimand drifts only −0.018 pp (in-bar) and NIST's centered-refit remedy reproduces the
      certified value to 13 digits — the certified claim itself is exactly right. Standardized drift
      (3 replicates bit-identical): **0.00 / 0.11 pp**. Secondary prediction FAILED (the Filip score-0
      point out-drifts three score-2 points). Finding: at zero statistical discretion, drift is floored
      by library numerical *policy* defaults, not by zero.

- [x] **2026-07-06 — Freund & Schapire (1996) Table 2, bagging C4.5 column, glass + iris rows
      (Program 2b confirmatory audit #11)** (`audits/AUDIT_freund-schapire1996-bag-c45-glass-iris.md` +
      `audits/audit_fs96_bag_glass_iris_run.py` + `audits/fs96_bag_glass_iris_raw.json`). Two-commit rule:
      prereg `b358b39` web-committed to the remote (verified byte-identical, 9218 B) BEFORE any reproduction
      code existed. **First bagging-family points** (the tracker's explicitly named unclaimed item) and two
      more score-4 points (the density priority); first appearance of iris. Blind rubric **4/5 both rows**
      (primary source: the ICML-96 author PDF, re-fetched and re-read this session, byte-identical to audit
      #9's artifact). Published 25.7 / 5.0 (% test error, 10-run averaged 10-fold CV, T=100) -> reproduced
      **23.084 / 4.867** (seed 0; bar ±4.0 pp) — **CONFIRMED** on both rows, all 3 seeds. Standardized drift
      (3-seed): **2.43 / 0.33 pp**. Secondary prediction **HELD** — first mid/high-score point to clear the
      1.96 pp score-2 ceiling (glass 2.43 pp), after six consecutive failures of that prediction. Sensitivity
      contrast with audit #9 (honesty item 3): the pure-default base tree moves bagged rows ≤ 0.4 pp versus
      9.31 pp under boosting — bagging insulates the exact discretion that broke the naive boosting route;
      largest single choice here is CV stratification (1.4 pp on glass).

- [x] **2026-07-06 — scikit-learn 1.9.0 docs, k-means digits demo, results table, 3 init rows
      (Program 2b confirmatory audit #12)** (`audits/AUDIT_sklearn-kmeans-digits.md` +
      `audits/audit_kmeans_digits_run.py` + `audits/kmeans_digits_raw.json`). Two-commit rule: prereg
      `988f595` web-committed to the remote (verified byte-identical) BEFORE any reproduction code
      existed. **First clustering-family target** (the tracker's named gap); the library-docs claim
      class's first confirmatory appearance. Blind rubric **2/5 all rows** (points: unseeded silhouette
      subsample; version-default tolerances across the 1.9.0→1.7.2 gap). Published v-meas 62.1 / 70.1 /
      62.2 pp (k-means++ / random / PCA-based) -> reproduced **62.056 / 70.104 / 62.224** (bar ±2.0 pp)
      — **CONFIRMED**; 18/18 deterministic printed cells (homo/compl/v-meas/ARI/AMI + inertia) identical
      at published precision across the version gap; the ONLY moving column is the unseeded silhouette
      subsample — exactly where the rubric put its randomization point. Standardized drift (3 master
      seeds, v-meas bit-identical): **0.04 / 0.00 / 0.02 pp**. Secondary prediction HELD (all ≤ 1.96 pp).

- [x] **2026-07-06 — Joulin, Grave, Bojanowski & Mikolov (2016) "Bag of Tricks", Table 1, AG News rows,
      h=10 + h=10 bigram (Program 2b confirmatory audit #13)** (`audits/AUDIT_joulin2016-fasttext-agnews.md` +
      `audits/audit_fasttext_agnews_run.py` + `audits/fasttext_agnews_raw.json`). Two-commit rule: prereg
      `f6c0417` web-committed to the remote (verified byte-identical, 6588 B) BEFORE any reproduction code
      existed. **First 2010s-decade confirmatory target and first text-classification family points**; blind
      rubric **3/5** (unigram row: lr unpublished, validation split unspecified) / **2/5** (bigram row: exact
      command published in the authors' own `classification-results.sh`, whose header states it produces
      Table 1). Published 91.5 / 92.5 (test accuracy %) -> reproduced **91.303–91.474 / 92.316–92.539**
      (bar ±2.0 pp) — **CONFIRMED** on both rows, all 3 master seeds; lr=0.1 selected on a pinned validation
      split for the unigram row (the published bigram lr 0.25 was not the unigram optimum — the selection
      procedure did real work). Standardized drift (3-seed): **0.08 / 0.11 pp**. Secondary prediction FAILED
      in its first clause (row A 0.08 < row B 0.11 against rubric ordering) — but the 0.03 pp contrast sits
      below the measured ±0.1 pp thread-noise floor (fastText's `seed` does not fully determine training at
      `thread=4`; replicates in the raw JSON), so the within-paper ordering is uninformative; second clause
      HELD. Same-engine caveat (authors' maintained library) in the audit's honesty item 1.

- [x] **2026-07-06 — Breiman (1996) "Bagging Predictors", Table 2, glass rows e_S + e_B (Program 2b
      confirmatory audit #14)** (`audits/AUDIT_breiman1996-bagging-cart-glass.md` +
      `audits/audit_breiman96_bag_glass_run.py` + `audits/breiman96_bag_glass_raw.json`). Two-commit
      rule: prereg `475742c` web-committed to the remote (verified byte-identical via git fetch + md5)
      BEFORE any reproduction code existed. Second bagging-family paper (cross-paper contrast with
      audits #9/#11: FS96's C4.5 bagging vs Breiman's own CART bagging on the SAME glass dataset);
      blind rubric **3/5 both rows**. Published 30.4 / 23.6 (% misclassification, 100× random 90/10
      splits; single CV-pruned tree / 50 bootstrap trees pruned on L per §4.3) -> reproduced
      **32.143 / 25.667** (seed 0; bar ±4.0 pp) — **CONFIRMED** on both rows, all 3 master seeds.
      Standardized drift (3-seed): **0.95 / 1.37 pp**. Per-seed iteration SEs (0.8–1.0) bracket the
      published SEs (1.1/0.9) — the reproduction's noise floor matches the paper's. The published
      6.8 pp bagging improvement reproduces as 5.8–6.5 pp. Secondary prediction FAILED (both
      standardized drifts below the 1.96 pp score-2 ceiling; fifth mid/high-score failure in seven) —
      the seed-0 e_B point alone (2.07 pp) would have cleared it, but the registered measure is the
      3-seed mean (honesty item 6: small systematic upward offset on both rows, all seeds).

- [x] **2026-07-07 — dmlc/xgboost CLI demo README (pinned v1.7.6), mushroom, printed eval log, 4
      numbers (Program 2b confirmatory audit #15)** (`audits/AUDIT_xgboost-cli-mushroom-demo.md` +
      `audits/audit_xgb_mushroom_run.py` + `audits/xgb_mushroom_raw.json`). Two-commit rule: prereg
      `f85c810` web-committed and byte-verified (git fetch + md5) BEFORE any reproduction code
      existed. **The open repo-README queue item, landed** — first confirmatory points from the
      repo-README claim class (the exploratory Fashion-MNIST class). Blind rubric **2/5, all four
      numbers**. Published test-error 1.6139/0.0000 + train-error 1.4433/0.1228 pp (README
      "Monitoring Progress" log; shipped conf + shipped LIBSVM data, md5-pinned to the tag) →
      reproduced **exactly to every printed digit** on xgboost-cpu 3.2.0 defaults (bar ±1.0 pp) —
      **CONFIRMED**, bit-identical across master seeds 0/1/2. Standardized drift (3-seed):
      **0.00 × 4**. Secondary prediction HELD. The pre-registered mechanism table
      ({tree_method} × {base_score}) came back null — neither scored discretion item fires on
      this near-separable, all-binary-feature data (honesty item 6: the null does not lower the
      blind score post hoc).

- [x] **2026-07-07 — Freund & Schapire (1996) Table 2, ionosphere row, C4.5 alone + boosting C4.5 +
      bagging C4.5 (Program 2b confirmatory audit #16)** (`audits/AUDIT_freund-schapire1996-ionosphere-c45-boost-bag.md`
      + `audits/audit_fs96_iono_run.py` + `audits/fs96_iono_raw.json`). Two-commit rule with a caveat:
      this session had no push credentials, so prereg commit `d27e56a` (blind rubric **4/4/4**, results
      EMPTY) precedes results only in the session-local commit graph; both land on the remote in one
      batch (audit #2 precedent — remote-first web-commit not available). **Three new score-4 points
      in one audit — the tracker's #1 density priority.** Published 8.9 / 5.8 / 6.2 (% test error,
      10-run averaged 10-fold CV, T=100) -> reproduced **12.251 / 6.439 / 7.721** (seed 0; bar ±4.0 pp)
      — **CONFIRMED** on all three rows, all 3 master seeds. Standardized drift (3-seed): **2.99 /
      0.85 / 1.34 pp**. Secondary prediction **HELD** (tree row 2.99 > 1.96 pp) — second consecutive
      score-4 audit to clear the score-2 ceiling. Notable: the largest drift is on the PLAIN C4.5 row
      (pruning/gain-ratio inexpressibility ~3.4 pp) and the ensembles wash it out; honesty item 3
      records that the naive default-base-tree boost route would land OUTSIDE the bar (11.595, +5.16 pp
      mapping sensitivity — audit #9's degeneration mechanism replicated on a second dataset).

- [x] **2026-07-07 — Freund & Schapire (1996) Table 2, sonar row, C4.5 alone + boosting + bagging
      (Program 2b confirmatory audit #17)** (`audits/AUDIT_freund-schapire1996-sonar-c45-boost-bag.md` +
      `audits/audit_fs96_sonar_run.py` + `audits/fs96_sonar_raw.json`). Two-commit rule: prereg web-committed
      to the remote and verified byte-identical modulo GitHub's appended trailing newline BEFORE any
      reproduction code existed (remote-first restored after run #15's ordering caveat). The run #15
      tracker's named candidate: three more score-4 points, completing the two-dataset six-column
      discretion-constant contrast with audit #16. Published 28.9 / 19.0 / 24.3 (% test error, 10-run
      averaged 10-fold CV, T=100) -> reproduced **26.731 / 17.356 / 17.740** (seed 0; bar ±4.0 pp) —
      **DISCREPANCY**: the bagging row lands −6.56 pp, outside the bar on all 3 seeds (−6.56/−7.52/−6.51);
      tree and boost rows in-bar. **The program's first DISCREPANCY at rubric 4.** Standardized drift
      (3-seed): **3.36 / 0.99 / 6.86 pp**. Secondary prediction **HELD** (tree 3.36 and bag 6.86 both
      clear the 1.96 pp score-2 ceiling). No sensitivity route reaches the bar (paper's hard voting
      16.83, pure-default base tree 19.86, unstratified 18.03): modern bagging of unpruned trees acts
      like a proto-RF (Breiman-2001 sonar Forest-RI reproduced at 18.19/17.86, audit #1), while the
      1996 value priced bagging of *pruned* C4.5 — the rubric-point-2 inexpressibility doing real work.
      Default-base-tree boost degeneration replicates on a THIRD dataset (+8.26 pp, would flip that row).

- [x] **2026-07-09 — Breiman (2001) Table 2, glass row, Forest-RI Single Input + Selection
      (Program 2b confirmatory audit #18)** (`audits/AUDIT_breiman2001-rf-glass.md` +
      `audits/audit_rf_glass_run.py` + `audits/rf_glass_raw.json`). Two-commit rule: prereg `80faaa4`
      web-committed REMOTE-FIRST and raw-verified byte-identical BEFORE any reproduction code ran;
      results `bfdab0d`, runner+raw `1f4332a`. The run #16 tracker's named candidate: extends the
      within-paper cross-dataset ladder (ionosphere / sonar / glass) at score 2/5; first Forest-RI
      point on a multi-class row. Published 21.2 / 20.6 -> reproduced **22.591 / 22.500** (seed 0;
      pre-registered bar ±2.5 pp) — **CONFIRMED** on both columns. Standardized drift (3-seed):
      **0.83 / 1.81 pp**; secondary prediction HELD (both ≤ the 1.96 pp score-2 ceiling; Selection
      uses 92% of it, now the second-largest score-2 drift). Honest notes: the published
      Selection < Single-Input ordering does NOT reproduce (OOB selection on 192 training cases adds
      variance, not value — it picked F=1 in only 54–61% of iterations); drift direction unfavorable
      at all 3 seeds on both columns.

- [x] **2026-07-10 — Breiman (2001) Table 2, diabetes row, Forest-RI Single Input + Selection
      (Program 2b confirmatory audit #19)** (`audits/AUDIT_breiman2001-rf-diabetes.md` +
      `audits/audit_rf_diabetes_run.py` + `audits/rf_diabetes_raw.json`). Two-commit rule: prereg `37200fe`
      web-committed REMOTE-FIRST and verified byte-identical (md5) BEFORE any reproduction code ran;
      results `e2e73fa`. The run #17 tracker's named candidate: completes the within-paper cross-dataset
      Forest-RI ladder (ionosphere / sonar / glass / diabetes) at score 2/5, on the ladder's largest
      holdout (77 test cases). Data provenance: original UCI Pima entry withdrawn — OpenML id 37
      (licence Public) used, md5-pinned in the prereg. Published 24.3 / 24.2 -> reproduced
      **23.701 / 23.636** (seed 0; pre-registered bar ±2.0 pp) — **CONFIRMED** on both columns, all
      3 seeds. Standardized drift (3-seed): **0.46 / 0.33 pp**; secondary prediction HELD in both
      clauses (≤ the 1.96 pp score-2 ceiling AND ≤ the glass counterparts) — drift shrank with
      test-set size exactly as the prereg's sampling-noise reasoning predicted. The published
      Selection < Single Input ordering reproduces here (unlike glass; OOB picked F=4 in 67–73% of
      iterations). First audit under the planner/executor split: chunk execution delegated to a
      subordinate executor, all 300 raw rows re-verified independently by the auditing session
      (see the audit's honesty item 3).

- [x] **2026-07-10 — scikit-learn 1.9.0 docs, LFW eigenfaces example, printed classification report,
      accuracy + weighted-F1 (Program 2b confirmatory audit #20)** (`audits/AUDIT_sklearn-lfw-eigenfaces.md` +
      `audits/audit_lfw_eigenfaces_run.py` + `audits/lfw_eigenfaces_raw.json`). Two-commit rule: prereg
      `a81500f` web-committed REMOTE-FIRST and md5-verified BEFORE any reproduction code ran; results
      `0e10d1c`. BOTH named candidates in one: the run-#3 LFW queue item AND the first score-1 point whose
      single rubric point is live (unseeded) randomization; largest dataset in the program (243 MB archive,
      sha256 == sklearn's own FUNNELED_ARCHIVE pin). Blind rubric **1/5 both columns**. Published 84 / 84
      (accuracy / weighted-F1, pp) -> reproduced **83.540 / 83.641** (seed 0; bar ±3.0 pp) — **CONFIRMED**;
      all deterministic anchors exact (1288/1850/7, 966/322, supports). Standardized drift (3-seed):
      **1.09 / 1.03 pp**. Secondary prediction HELD (both ≤ 1.96 pp) — but these are the largest score-≤1
      drifts in the set by an order of magnitude: pure randomization variance at score 1 out-drifts most
      score-2/3/4 points, moving exploratory rho 0.663 → 0.574. Sharpest finding: the printed best
      estimator (C=76823, gamma=0.0034) reproduces in NONE of the 3 seeds (best-C spread 3.5k–14.7k)
      while the report stays within 0.5–2.7 pp — the docs table is robust to the search draw; the
      best-params line is a one-off. Version gap 1.9.0→1.7.2 pre-declared (Python 3.10 pip ceiling).

### Queue (candidate targets for future runs)

- [x] ~~Another Table 3 row from the same paper with a different discretion profile~~ — DONE
      run #2 (LogisticRegression C=1 ovr l1, see Completed audits). Still open from this bullet:
      DecisionTree entropy/depth-10 → 0.798 (adds *seed* discretion, a profile not yet tested).
- [x] ~~scikit-learn's own documented example numbers~~ — digits SVC report DONE run #3
      (see Completed audits). ~~LFW eigenfaces table~~ — DONE audit #20 (see Completed audits).
- [ ] Fashion-MNIST DecisionTree entropy/depth-10 -> 0.798 — **infra-blocked in this sandbox**
      (run #3 synthetic probe: >=2 min single-process fit vs hard 45 s cap; no claim-preserving
      amendment). Needs an environment without the per-process cap.
- [x] ~~A published UCI-scale ablation row from a widely cited repo README.~~ — DONE run #4, with a
      widely cited *paper* table instead of a repo README (Breiman 2001 Table 2, ionosphere; see
      Completed audits). Repo-README row DONE run #14 (xgboost CLI mushroom demo, audit #15).
      LFW eigenfaces DONE audit #20; Breiman Table 2 rows sonar/glass/diabetes all DONE (audits #1/#18/#19)
      if a cross-implementation *ladder within one paper* is wanted.

- [x] **2026-07-10 — scikit-learn 1.7.2 docs, fully-seeded ensemble doctest rows: GradientBoostingClassifier
      (make_hastie_10_2, test acc 0.913) + AdaBoostClassifier (make_classification, train acc 0.96)
      (Program 2b confirmatory audit #21)** (`audits/AUDIT_sklearn-ensemble-doctests.md` +
      `audits/audit_ensemble_doctests_run.py` + `audits/ensemble_doctests_raw.json`). Two-commit rule:
      prereg `2cb4a52` web-committed REMOTE-FIRST and sha256-verified BEFORE any reproduction code
      existed. The run-#20 agenda's TOP priority: first score-0 anchor outside the certified-values
      class, and the program's first version-gap-free target (claim verified identical in 1.7.2 and
      stable/1.9.0 docs; executing library 1.7.2). Blind rubric **0/5 both rows**. Published 91.3 / 96.0 pp
      -> reproduced **91.30 / 96.00** — bit-exact float match on every master seed; **CONFIRMED** at the
      program's tightest bar (±0.5 pp). Standardized drift (3-seed): **0.00 / 0.00 pp**; secondary
      prediction HELD. Second audit under the planner/executor split (executor ran the pinned runner;
      planner re-ran seed 0 independently and validated the raw JSON before publishing).

- [x] **2026-07-10 — Breiman (1996) "Bagging Predictors", Table 2, ionosphere rows e_S + e_B
      (Program 2b confirmatory audit #22)** (`audits/AUDIT_breiman1996-bagging-cart-ionosphere.md` +
      `audits/audit_breiman96_bag_iono_run.py` + `audits/breiman96_bag_iono_raw.json`). Two-commit
      rule: prereg `d327f44` web-committed REMOTE-FIRST and md5-verified byte-identical BEFORE any
      reproduction code ran; results `581f6bf`. The run-#19 agenda's first named candidate (score-3
      density, the thinnest populated score): two new score-3 points via an audit-#14 dataset swap,
      completing the cross-paper bagging contrast with FS96 on ionosphere (audit #16). Blind rubric
      **3/5 both rows**. Published 11.2 / 7.9 (% misclassification, 100× random 90/10 splits) ->
      reproduced **10.914 / 8.029** (seed 0; pre-registered bar ±3.0 pp) — **CONFIRMED** on both
      rows, all 3 master seeds. Standardized drift (3-seed): **0.32 / 0.39 pp**; per-seed empirical
      SEs (0.49–0.53 / 0.39–0.47) bracket the published 0.5 / 0.4 — the reproduction's noise floor
      matches the paper's, as on glass (audit #14). Secondary prediction FAILED again at score 3
      (both ≤ 1.96 pp). Notable: the md5-pinned UCI file holds 225 g / 126 b vs the paper's stated
      226 / 125 — a one-case labeling difference caught by a pre-run assert and disclosed (honesty
      item 1); Breiman's own CART bagging is systematically more portable than FS96's C4.5 bagging
      on the same data (0.39 vs 1.34 pp here; glass 1.37 vs 2.43 pp). Third audit under the
      planner/executor split: 23/24 chunks delegated, one chunk independently re-run bit-identical,
      all 300 raw rows re-verified by the auditing session.

- [x] **2026-07-10 — Freund & Schapire (1996) Table 2, vehicle row, C4.5 alone + boosting C4.5 +
      bagging C4.5 (Program 2b confirmatory audit #23)**
      (`audits/AUDIT_freund-schapire1996-vehicle-c45-boost-bag.md` +
      `audits/audit_fs96_vehicle_run.py` + `audits/fs96_vehicle_raw.json`). Two-commit rule: prereg
      `aa18d35` web-committed and md5-verified byte-identical BEFORE any reproduction code existed;
      results in this session's batch. The run-#20 tracker's score-4/5 density priority: three more
      score-4 points, extending the FS96 C4.5 ladder to a third dataset (the first mid-size 4-class
      one). Blind rubric **4/5 all three rows**. Published 29.9 / 22.6 / 26.1 (% test error, 10-fold
      CV x 10 runs) -> reproduced **27.258 / 23.274 / 25.449** (seed 0; pre-registered bar ±4.0 pp) —
      **CONFIRMED** on all three rows, all 3 master seeds; the paper's tree > bag > boost ordering
      reproduces. Standardized drift (3-seed): **2.61 / 0.88 / 0.70 pp**; secondary prediction HELD
      via the tree row (2.61 > 1.96). Notable: audit #17's bag DISCREPANCY mechanism did NOT repeat
      (vehicle bag −0.65 pp vs sonar −6.56 pp — an open dataset-vs-protocol contrast); the
      default-base-tree boosting degeneration replicated on a fourth dataset (+6.69 pp vs published,
      would flip the boost verdict); paper-faithful M1-resample boosting lands closer to published
      (22.116) than the sklearn route. Fourth audit under the planner/executor split (54 chunks
      delegated; planner re-aggregated and duplicate-checked all parts before publishing).

- [x] **2026-07-10 — Breiman (1996) "Bagging Predictors", Table 2, diabetes rows e_S + e_B
      (Program 2b confirmatory audit #24)** (`audits/AUDIT_breiman1996-bagging-cart-diabetes.md` +
      `audits/audit_breiman96_bag_diabetes_run.py` + `audits/breiman96_bag_diabetes_raw.json`).
      Two-commit rule: prereg `564d3d2` web-committed REMOTE-FIRST and md5-verified byte-identical
      (6636 B, no trailing-newline delta) BEFORE any reproduction code ran; results `a84a656`.
      The run-#21 agenda's first named candidate: two more score-3 points via an audit-#14/#22
      dataset swap — the Breiman-1996 CART-bagging ladder's third dataset. Blind rubric **3/5 both
      rows**. Published 25.3 / 23.9 (% misclassification, 100× random 90/10 splits) -> reproduced
      **25.805 / 23.831** (seed 0; pre-registered bar ±2.5 pp, the family's tightest) — **CONFIRMED**
      on both rows, all 3 master seeds. Standardized drift (3-seed): **0.64 / 0.28 pp**; per-seed
      empirical SEs (0.46–0.54) bracket the published 0.4/0.4 from just above. The paper's smallest
      decrease (6%) reproduces as 6.1–7.6%, consistent with Breiman's near-floor conjecture.
      Secondary prediction FAILED again at score 3 (seventh failure in ten audits carrying it).
      Wrong-version trap documented: the Berkeley TR-421 PDF reports a different diabetes protocol
      (1036 duplicated cases, e_S 23.4 / e_B 18.8) — the Springer journal version was pinned in the
      prereg before scoring. Fifth audit under the planner/executor split: all 51 chunks delegated
      (zero retries); planner re-ran one chunk bit-identical and re-verified all 300 raw rows.

- [x] **2026-07-10 — Freund & Schapire (1996) Table 2, segmentation row, C4.5 alone + boosting C4.5 +
      bagging C4.5 (Program 2b confirmatory audit #25)**
      (`audits/AUDIT_freund-schapire1996-segmentation-c45-boost-bag.md` +
      `audits/audit_fs96_segmentation_run.py` + `audits/fs96_segmentation_raw.json`).
      Two-commit rule: prereg `2beb905b` web-uploaded and md5-verified byte-identical (11616 B,
      no trailing-newline delta) BEFORE any real-data reproduction code ran. The run-#22 tracker's
      named candidate: the last clean FS96 no-test-set row (segmentation, 7-class), Table 1 profile
      verified from the primary source before scoring (2310 examples, no test set, 19 continuous,
      no missing). Blind rubric **4/5 all three columns**. Published 3.6 / 1.4 / 2.7 (% test error,
      10-fold CV × 10 runs, T=100) -> reproduced **3.294 / 1.437 / 2.281** (seed 0; pre-registered
      bar ±4.0 pp) — **CONFIRMED** on all rows, all 3 master seeds; largest deviation −0.42 pp.
      Standardized drift (3-seed): **0.19 / 0.06 / 0.41 pp** — three score-4 points on the drift
      floor. Secondary prediction FAILED (eighth failure in eleven audits carrying it) — the
      program's lowest-error score-4 target produced its lowest score-4 drifts; the prereg's
      floor-headroom note flags a candidate confounder (|drift| bounded by distance to the 0 %
      floor) for post-n=30 exploratory analysis. The defaulttree boosting degeneration replicates
      on a fourth dataset (3.60 vs 1.44) but for the first time would NOT have flipped the verdict.
      Sixth audit under the planner/executor split (93/96 chunks delegated; parallel executors
      failed — the sandbox shell is single-process, re-dispatched sequentially, zero retries; two
      delegated cells re-run bit-identically; all 170 raw cells re-aggregated by the auditor).

- [x] **2026-07-10 — Breiman (1996) "Bagging Predictors", Table 2, breast cancer rows e_S + e_B
      (Program 2b confirmatory audit #26)** (`audits/AUDIT_breiman1996-bagging-cart-breastcancer.md` +
      `audits/audit_breiman96_bag_breastcancer_run.py` + `audits/breiman96_bag_breastcancer_raw.json`).
      Two-commit rule with a disclosed wrinkle: the prereg landed as TWO commits 12 s apart
      (`742b6e8a` add + revision `35045bfba7`, a prior session dying/retrying at push) — both
      precede any reproduction code; results in this session's batch. The run-#24/#25 trackers'
      named candidate: fourth dataset of the Breiman-1996 CART-bagging ladder AND the
      low-published-error probe for audit #25's floor-headroom confounder (published 5.9/3.7,
      the family's lowest errors). Blind rubric **3/5 both rows** — missing-value handling live
      for the first time in the family (16 '?' cases, kept per the paper; sklearn native-NaN
      routing pinned in the prereg). Published 5.9 / 3.7 -> reproduced **5.971 / 4.014** (seed 0;
      pre-registered bar ±2.0 pp, the family's tightest) — **CONFIRMED** on both rows, all 3
      master seeds. Standardized drift (3-seed): **0.21 / 0.45 pp**; per-seed SEs (0.26–0.30 /
      0.22–0.25) match the published 0.3/0.2; the 37% decrease reproduces as 26–33%. Secondary
      prediction A FAILED (ninth in twelve); **secondary B (floor-headroom probe) HELD** — both
      drifts ≤1.0 pp, below the same-rubric glass maxima (with the caveat that iono/diabetes sit
      in the same range; single point, not proof). Probes: column-mean imputation moves ≤0.43 pp;
      case deletion changes the estimand (−1.15 pp e_S) — keep-all-699 was the right pin.
      **Tracker repair in this batch (mandated by this audit's prereg numbering note):** the
      complete, validly two-commit-pre-registered `AUDIT_lecun1998-mnist-pca-quadratic.md`
      (2026-07-06, self-labeled "#15", drift 0.46 pp at rubric 3/5, re-verified this session from
      the file of record) was missing from the tracker — its point is added and n corrected
      24 -> 25 before this audit, **26/30 after**. Seventh audit under the planner/executor split
      (20 chunks delegated incl. 8 sensitivity-probe chunks; one probe-script pickling bug fixed
      before any probe number existed; one registered chunk re-run bit-identically; all 500 raw
      rows re-aggregated by the auditor).

- [x] **2026-07-11 — Breiman (1996) "Bagging Predictors", Table 2, waveform rows e_S + e_B
      (Program 2b confirmatory audit #27)** (`audits/AUDIT_breiman1996-bagging-cart-waveform.md` +
      `audits/audit_breiman96_bag_waveform_run.py` + `audits/breiman96_bag_waveform_raw.json`).
      Two-commit rule with a disclosed session boundary: prereg `f5d1c72` + byte-fix `b7af1a5f`
      web-committed by the PREVIOUS session (2026-07-11 10:52/10:55 UTC), which died before any
      results were published; this session found the prereg on the remote with EMPTY results and
      completed it — the dead session's leftover publish package in the sandbox was unreadable
      (mode 700, different uid) and never used (the audit's honesty item 1). Fifth dataset of the
      Breiman-1996 CART-bagging ladder and the family's first SIMULATED-data target (faithful
      full-precision port of the md5-pinned waveform.c model; 1800 fresh cases/iteration,
      L=300 / T=1500). Blind rubric **3/5 both rows**. Published 29.1 / 19.3 -> reproduced
      **29.277 / 19.589** (seed 0; pre-registered bar ±2.5 pp) — **CONFIRMED** on both rows, all
      3 master seeds. Standardized drift (3-seed): **0.32 / 0.44 pp**; e_S per-seed SEs
      (0.19–0.22) bracket the published 0.2 (the paper's smallest); the published 34% decrease
      reproduces as 32.2–33.4%. Secondary A FAILED again; **secondary B — the high-headroom
      converse of audit #26's floor-headroom probe — FAILED on both clauses**: the family's
      maximal-headroom target (15.1 pp above the Bayes floor) drifts near the family floor,
      evidence AGAINST distance-to-floor as the drift confounder and FOR the paper's own
      sampling SE as the better predictor. Sensitivity probe: the cited C code's u-quantization
      + 2-dp rounding is numerically inert (Δ ≤ 0.08 pp; blind score not lowered post hoc).
      Eighth audit under the planner/executor split: 52 chunks delegated (39 registered + 13
      probe), one delegated chunk re-run bit-identically, all 300 registered raw rows
      re-verified by the auditor.

- [x] **2026-07-11 — StatLog (Michie, Spiegelhalter & Taylor 1994) Backprop rows: diabetes
      Table 9.20 + Australian credit Table 9.3 (Program 2b confirmatory audit #28)**
      (`audits/AUDIT_statlog1994-backprop-diabetes-australian.md` +
      `audits/audit_statlog_backprop_run.py` + `audits/statlog_backprop_raw.json`).
      Two-commit rule clean in ONE session: prereg `28213ee` (rubric, bars, BOTH secondary
      predictions, EMPTY results) verified byte-identical on the remote (10 846 B) before any
      reproduction code existed; results + runner + raw in this session's batch. Published via
      GitHub's FILE-UPLOAD path rather than the web editor — deliberate, after the editor's
      auto-indent mangled audit #27's prereg; no editor incident this session. Blind rubric
      **5/5 both rows** — only the SECOND score-5 target in the program and the first since
      audit #8, taking the thinnest bucket from 1 point to 3. New claim class (1994 multi-lab
      benchmark-consortium table) and new decade anchor; the book is legally public (out of
      print, copyright reverted to the editors, full text posted by them). Published 24.8 / 15.4
      (% test error, 12-fold / 10-fold CV) -> reproduced **23.047 / 13.623** (seed 0; bar ±5.0 pp)
      — **CONFIRMED both rows**, all 3 master seeds; the 2026 default MLP lands ~1.8 pp BETTER
      than the 1994 original on both. Standardized drift (3-seed): **1.93 / 1.83 pp**.
      Secondary A **FAILED both clauses** (neither drift exceeds the 1.96 pp score-2 ceiling;
      diabetes misses by 0.03 pp) — a second/third strike against the hypothesis at the
      high-discretion end. Secondary B **HELD decisively**: the same targets reproduced WITHOUT
      the book's unstated scaling choice drift **4.89 / 9.72 pp** (2.5x / 5.3x). A and B together
      are this audit's real finding and they cut at the program's headline: the discretion is
      real and large, the measured drift is small, and the gap is how carefully the reproducer
      resolved it — the **competence confounder**, now logged for the post-n=30 analysis.
      Reported honestly and NOT fixed: 100% of folds hit `max_iter=200` without meeting `tol` in
      the primary configuration (raising it would have moved a defaulted choice after data).
      Ninth audit under the planner/executor split: 24 chunks delegated, two re-run bit-identically
      by the auditor, every drift recomputed from raw per-fold rates, and the published 61-point
      rho (0.532) reproduced from the printed list before appending.

- [x] **2026-07-11 — StatLog (Michie, Spiegelhalter & Taylor 1994) Backprop rows: satimage
      Table 9.9 + vehicle Table 9.6 (Program 2b confirmatory audit #29)**
      (`audits/AUDIT_statlog1994-backprop-satimage-vehicle.md` +
      `audits/audit_statlog_backprop2_run.py` + `audits/statlog_backprop2_raw.json`).
      Two-commit rule clean in ONE session: prereg `9139fa3` (per-column blind rubric **5/5 satimage,
      4/5 vehicle** — the program's first within-implementation 5-vs-4 contrast, vehicle being the
      book's ONLY Backprop row with a disclosed configuration: "5 hidden nodes and a training time of
      four hours"; bars ±5.0/±4.0 pp; THREE secondary predictions; EMPTY results) verified
      byte-identical on the remote (10 229 B) before any reproduction code existed; results + runner +
      raw published via the FILE-UPLOAD path in this session's batch. Published 13.9 / 20.7 (% test
      error, single 4435/2000 split / 9-fold CV) -> reproduced **9.350 / 33.924** (seed 0). Satimage
      **CONFIRMED** (-4.550 pp vs ±5.0 — in-bar by 0.45 pp, the score-5 bar doing real work for the
      first time). Vehicle **DISCREPANCY** (+13.224 pp vs ±4.0, exceeded at every seed) — the
      program's SECOND discrepancy, again at rubric 4. Standardized drift (3-seed): **4.18 / 11.21 pp**
      — 11.21 is the largest drift in the confirmatory set (previous max 10.35) and 4.18 the largest
      score-5 drift (previous ceiling 1.93). Secondary A **HELD for the first time** (both rows > 1.96
      pp, after failing in audits #8/#28); secondary B **HELD decisively** (unscaled drifts 11.68 /
      53.30 pp — scaling discretion is live, replicating #28); secondary C **FAILED INVERTED** (the
      score-4 row out-drifted the score-5 row 2.7x). Post-hoc diagnosis, labelled as such: the
      **partial-specification trap** — honoring the book's disclosed 5-hidden-node architecture
      WITHOUT its undisclosed training budget underfits badly (9/9 primary folds unconverged at
      max_iter=200, all seeds), while IGNORING the disclosure (library-default h=100 sensitivity,
      drift 3.09 pp) would have confirmed the row. A disclosed detail honored out of context drove
      more drift than full silence (satimage) — logged for the post-n=30 analysis beside the
      competence and floor-headroom confounders. Fold-assignment discretion inert (KFold sensitivity
      11.73 ≈ 11.21). Reported honestly and NOT fixed: satimage primary also hit max_iter (all
      seeds). Tenth audit under the planner/executor split: 16 chunks delegated by exact registered
      command, two re-run bit-identically by the auditor, every drift recomputed from raw JSON, and
      the published 63-point rho (0.562) reproduced from the printed list before appending.

- [x] **2026-07-11 — StatLog (Michie, Spiegelhalter & Taylor 1994) Backprop rows: letters
      Table 9.7 + shuttle Table 9.19 (Program 2b confirmatory audit #30 — THE TRIGGER AUDIT)**
      (`audits/AUDIT_statlog1994-backprop-letter-shuttle.md` + `audits/audit_statlog_backprop3_run.py`
      + `audits/statlog_backprop3_raw.json`). Two-commit rule clean in ONE session: prereg
      (blind rubric **5/5 both rows**, bars +/-5.0 / +/-1.5 pp, THREE secondary predictions, EMPTY
      results) uploaded via GitHub's FILE-UPLOAD path and verified byte-identical on the remote
      (15 523 B, md5 7e28c1fb8617aa86f452cc61604b09b1) BEFORE any reproduction code existed; results
      + runner + raw in this session's batch. Primary source re-fetched and re-verified (whole.pdf,
      1 787 416 B, size-identical to the audits #28/#29 artifact). **Target selection rule fixed
      BEFORE rubric scoring and published in the prereg:** take the ENTIRE remaining pool of StatLog
      Backprop rows with (a) public data, (b) a proportion metric, (c) a recoverable attribute set
      and split — which is exactly letters + shuttle. (Segmentation excluded: StatLog used **11 of
      the 19** attributes, confirmed in the book's own Table 9.30, and never says which 11. DNA
      excluded: Backprop used the 240-binary one-of-four coding; the distributed file carries the
      180-binary coding. Heart/German/head-injury excluded: average-cost metric, not a proportion.)
      Taking the whole pool was deliberate — the two rows' expected drifts were pre-registered as
      pointing in OPPOSITE directions, so the last audit before the n=30 trigger could not be a
      hypothesis-favorable cherry-pick. Published 32.7 / 0.43 (% test error; 15 000/5 000 one-shot
      split / distributed 43 500/14 500 split) -> reproduced **5.36 / 0.0552** (seed 0).
      Letters **DISCREPANCY** (-27.34 pp vs +/-5.0, outside at every seed) — the program's THIRD
      discrepancy and **its largest drift by 2.5x**. Shuttle **CONFIRMED** (-0.375 pp vs +/-1.5,
      inside at every seed). Standardized drift (3-seed): **27.53 / 0.36 pp** — at the SAME blind
      rubric score of 5/5. Score-5 bucket goes 4 -> 6 points and now spans 0.36-27.53 pp.
      **The finding — secondary B, registered as hypothesis-threatening, HELD at 75.8x:** the two
      rows share book, algorithm, unpublished implementation, reproducer, defaults, session and
      rubric score, and their absolute drifts differ 76x — but their RELATIVE drifts are identical
      (the 2026 default MLP removes 84.2% of the published error on letters, 84.5% on shuttle), and
      the drift ratio (75.8x) reproduces the published-headroom ratio (76.0x) to three significant
      figures. **|drift| in pp ~= (relative reproduction error) x (headroom above the 0% floor)**;
      the rubric scores only the first factor. This ESTABLISHES the floor-headroom confounder at
      constant discretion — what audits #25/#26 could only conjecture and #27 argued against, since
      every earlier test confounded headroom with score, paper, algorithm and dataset. Secondary A
      FAILED on shuttle (pre-registered as expected to fail). Secondary C FAILED **INVERTED on both
      rows**: unscaled drifts (23.40 / 0.285) are SMALLER than the scaled primaries (27.34 / 0.375)
      because both drifts are negative — degrading the model moves it back toward the 1994 number.
      Unstated discretion inflates |drift| only when the published claim is at least as good as the
      modern default: **the competence confounder has a sign.** Reported honestly and NOT fixed:
      letters hit max_iter=200 unconverged at every seed (and still beat the published number by
      27 pp); one *sensitivity* cell (shuttle x MinMaxScaler) never completed inside the 45 s cap
      after 11 attempts and is logged as a failure — all 6 registered PRIMARY cells ran, so both
      verdicts and both tracker points are complete. Eleventh audit under the planner/executor split:
      12 cells delegated by exact registered command, **both verdict cells re-run bit-identically by
      the auditor**, the runner `cmp`-verified against the pinned script, every drift recomputed from
      raw JSON, and the published 65-point rho (0.590) reproduced from the printed list before
      appending. **n = 31; the one-shot confirmatory test is now DUE and the set is CLOSED.**

## Program 2b — pre-registered drift study (discretion predicts drift)

Registered 2026-07-05 in `audits/PREREG_DRIFT.md` (commit `ad8aa31`) BEFORE any confirmatory audit:
Spearman rho(blind discretion score, |drift| pp) > 0.5 with p < 0.01, tested ONCE at n=30 confirmatory
audits, verdict published either way in RESULTS_DRIFT.md. The 5 pre-registration audits (Program 2
runs #1–#4) are EXPLORATORY and excluded from the confirmatory set.

**Tracker: n = 31 confirmatory audits — THE n>=30 TRIGGER HAS FIRED** (audit #4 was COULD-NOT-RUN and contributes nothing; includes the audit-#26 repair — the previously untracked PCA-quadratic audit — and audits #26–#30). The `PREREG_DRIFT.md` one-shot confirmatory test is now **DUE**. See the binding hand-off note below the points list.
Points (blind score, |drift| pp): (2, 0.59), (2, 0.94) [Breiman sonar], (3, 8.95), (3, 10.35)
[Gorman-Sejnowski sonar MLP], (2, 0.00), (2, 0.00), (1, 0.00) [Hsu-Chang-Lin svmguide1],
(2, 1.96) [LeCun-1998 MNIST linear via least squares], (3, 1.08), (3, 1.34) [Breiman 2001
Table 2 "One Tree" column, ionosphere/sonar], (2, 0.02), (2, 0.04), (2, 0.59) [Aeberhard-1992
wine LOO, LDA/QDA/1NN], (5, 1.11), (2, 0.05) [Sigillito-1989 ionosphere perceptron / Aha 1NN],
(4, 0.23), (4, 1.36) [Freund-Schapire 1996 glass C4.5 / boosted C4.5], (0, 0.00), (0, 0.11)
[NIST StRD LLS certified R², Longley / Filip], (4, 2.43), (4, 0.33) [Freund-Schapire 1996
bagging C4.5, glass / iris], (2, 0.04), (2, 0.00), (2, 0.02) [sklearn 1.9.0 docs k-means
digits demo, k-means++ / random / PCA-based], (3, 0.08), (2, 0.11) [Joulin-2016 fastText
AG News, h=10 / h=10 bigram], (3, 0.95), (3, 1.37) [Breiman-1996 Bagging Predictors glass,
e_S / e_B], (2, 0.00), (2, 0.00), (2, 0.00), (2, 0.00) [xgboost v1.7.6 CLI mushroom demo
README, test r0/r1 + train r0/r1], (4, 2.99), (4, 0.85), (4, 1.34) [Freund-Schapire 1996
ionosphere, C4.5 alone / boost / bag], (4, 3.36), (4, 0.99), (4, 6.86) [Freund-Schapire 1996
sonar, C4.5 alone / boost / bag], (2, 0.83), (2, 1.81) [Breiman-2001 glass Forest-RI,
Single Input / Selection], (2, 0.46), (2, 0.33) [Breiman-2001 diabetes Forest-RI, Single Input /
Selection], (1, 1.09), (1, 1.03) [sklearn-1.9.0 docs LFW eigenfaces, accuracy / weighted-F1], (0, 0.00),
(0, 0.00) [sklearn-1.7.2 docs fully-seeded ensemble doctests, GBC hastie test acc / AdaBoost
train acc], (3, 0.32), (3, 0.39) [Breiman-1996 Bagging Predictors ionosphere, e_S / e_B],
(4, 2.61), (4, 0.88), (4, 0.70) [Freund-Schapire 1996 vehicle, C4.5 alone / boost / bag],
(3, 0.64), (3, 0.28) [Breiman-1996 Bagging Predictors diabetes, e_S / e_B], (4, 0.19), (4, 0.06),
(4, 0.41) [Freund-Schapire 1996 segmentation, C4.5 alone / boost / bag], (3, 0.46)
[LeCun-1998 MNIST 40-PCA+quadratic, audit-#26 tracker repair], (3, 0.21), (3, 0.45)
[Breiman-1996 Bagging Predictors breast cancer, e_S / e_B], (3, 0.32), (3, 0.44)
[Breiman-1996 Bagging Predictors waveform, e_S / e_B], (5, 1.93), (5, 1.83)
[StatLog 1994 Backprop, diabetes Table 9.20 / Australian credit Table 9.3], (5, 4.18), (4, 11.21)
[StatLog 1994 Backprop, satimage Table 9.9 / vehicle Table 9.6], (5, 27.53), (5, 0.36)
[StatLog 1994 Backprop, letters Table 9.7 / shuttle Table 9.19].

**BINDING HAND-OFF (written 2026-07-11, audit #30, BEFORE the test is run).** The confirmatory set is
now CLOSED at n = 31 audits / 67 points. The next Program 2b run executes the one-shot pre-registered
test of `audits/PREREG_DRIFT.md` — Spearman rho(blind score, |drift| pp) > 0.5 with p < 0.01 — over
**exactly the 67 points printed above and no others**, and publishes `RESULTS_DRIFT.md` with the
verdict either way. It does NOT add points, does not re-score any rubric, does not re-run any audit,
and does not touch PREREG_DRIFT.md. This is written down now, before the test fires, so that "keep
auditing until rho looks right" is not available to any later session. The three confounders that
MUST appear in the honesty section of RESULTS_DRIFT.md, all logged before the test: **floor-headroom**
(audits #25/#26, contradicted by #27, and ESTABLISHED AT CONSTANT DISCRETION by #30 — see below),
the **competence confounder** (audit #28, shown by #30 to have a sign), and the **partial-specification
trap** (audit #29). A fourth, also pre-test: the **source concentration** of the high end — 5 of the 6
score-5 points come from one book and one algorithm (StatLog Backprop), and the 6th (Sigillito 1989)
is also a gradient-trained neural net.

**HAND-OFF DISCHARGED — TEST EXECUTED (2026-07-11, confirmatory-test session): VERDICT SUPPORTED.**
rho = 0.5875, p = 1.7e-07 two-sided scipy (a registered option), Monte Carlo permutation
cross-check 0/10⁶ exceedances (p < 1e-06, seed 0), over exactly the 67 points printed above,
transcribed to `audits/drift_confirmatory_points.json` and machine-verified identical (order and
values) to the printed list at `ff7af3bd`. Verdict published in `results/RESULTS_DRIFT.md` with
the full table, the four pre-logged confounders (floor-headroom, competence, partial-specification
trap, source concentration) plus cluster non-independence, and labeled-exploratory sensitivity
checks (audit-level rho 0.638 / p 2.0e-04; source-cluster rho 0.756 / p 2.8e-03; Kendall tau
0.458; drop-letters 0.570 / drop-shuttle 0.608 / drop-both 0.590 — the bar survives all of them).
No points added, nothing re-scored, PREREG_DRIFT.md untouched. The paragraph below is retained
as the closure record it was.
Running rho: spearmanr over the 67 points as printed above (2-dp) = **0.587, p = 1.7e-07**
(audit #30; the 65-point value 0.590/2.4e-07 was reproduced from the printed list before appending.
This is the LAST exploratory rho — the set is now closed and the next run's value is the confirmatory
one. The two new points are the program's most informative pair yet and they cut BOTH ways: letters
(5, **27.53**) is the largest drift in the entire set, at the highest rubric score, strongly
hypothesis-supporting; shuttle (5, **0.36**) is a near-floor drift at the SAME rubric score, strongly
hypothesis-undermining. They cancel almost exactly (rho moves 0.590 -> 0.587). **The finding is why
they cancel.** Same book, same algorithm, same unpublished 1994 implementation, same reproducer, same
library defaults, same session, same blind score of 5/5 — and the absolute drifts differ 76x. But the
RELATIVE drifts are identical: the 2026 default MLP removes 84.2% of the published error on letters
and 84.5% on shuttle. |drift| in pp is therefore approximately (relative reproduction error) x (the
published value's headroom above the 0% floor), and the rubric scores only the first factor. The
floor-headroom confounder is hereby ESTABLISHED AT CONSTANT DISCRETION — the one thing audits #25/#26
could not show and #27 argued against, because every earlier test of it confounded headroom with
score, paper, algorithm and dataset. Verdicts: letters DISCREPANCY (5.36 vs 32.7, -27.34 pp, outside
the +/-5.0 bar at every seed; the program's third discrepancy and its largest), shuttle CONFIRMED
(0.0552 vs 0.43, inside the +/-1.5 bar at every seed). Secondary A FAILED on shuttle as pre-registered
and as expected. Secondary B (letters |drift| > 5x shuttle's) HELD at 75.8x. Secondary C FAILED
INVERTED on BOTH rows: the unscaled configs drift LESS (23.40 / 0.285) than the scaled primaries
(27.34 / 0.375), because both drifts are NEGATIVE — the modern default beats the 1994 number, so
degrading the model moves it back TOWARD the published value. Unstated discretion inflates |drift|
only when the published claim is at least as good as the modern default; the competence confounder has
a sign. Both rows were taken by a selection rule fixed before rubric scoring — the ENTIRE remaining
pool of StatLog Backprop rows with public data, a proportion metric and a recoverable attribute
set — precisely so that the last audit before the trigger could not be a cherry-pick; their expected
drifts were pre-registered as pointing in opposite directions, and they did.) Previous note (audit #29,
superseded): rho 0.590, p = 2.4e-07 ( the 63-point value 0.562/1.7e-06 was reproduced from the printed
list before appending - both new points land far above the global median drift (0.46 pp), so rho RISES
0.028. The set's maximum drift is now at score 4 (11.21, vehicle - the program's second DISCREPANCY)
and the score-5 ceiling more than doubles (1.93 -> 4.18, satimage CONFIRMED with 0.45 pp to spare).
Secondary A (both rows > 1.96 pp) HELD for the FIRST time after failing in audits #8/#28; secondary B
(scaling) HELD decisively again (unscaled drifts 11.68/53.30 pp); secondary C (within-audit 5-vs-4
ordering) FAILED INVERTED - the score-4 row out-drifted the score-5 row 2.7x, because honoring the
book's disclosed 5-hidden-node architecture without its undisclosed 4-hour training budget underfits
(all folds unconverged), while the ignored-disclosure h100 sensitivity would have been in-bar at 3.09
pp. The PARTIAL-SPECIFICATION TRAP is logged alongside the competence and floor-headroom confounders
for the post-n=30 analysis). Previous note (audit #28, superseded): rho 0.562, p = 1.7e-06 (the 61-point value 0.532/1.0e-05 was reproduced from the
printed list before appending - the two new points are the program's FIRST score-5 additions since
audit #8, taking score 5 from 1 point to 3. rho RISES 0.030 because both land above the global median
drift, yet the score-5 bucket is now the set's most-compressed: 3 points spanning 1.11-1.93 pp, with a
CEILING (1.93) BELOW the score-3 max (10.35) and the score-4 max (6.86). The monotone rho is being
carried by the low end, not the high end. Both rows FAILED pre-registered secondary A (drift > 1.96 pp,
the largest score-2 drift) - diabetes by 0.03 pp - while secondary B HELD decisively: the same targets
reproduced WITHOUT the unstated scaling choice drift 4.89 / 9.72 pp, i.e. 2.5x / 5.3x the primary.
Discretion on this target is real and large; the recorded drift is small; the difference is entirely how
carefully the reproducer resolved it. This "competence confounder" is logged alongside floor-headroom for
the post-n=30 analysis). Previous note (audit #27, superseded): rho 0.532, p = 1.0e-05 (the 59-point
value 0.538/1.1e-05 was reproduced from the printed list before appending — two more near-floor score-3 points continue the drift-floor
squeeze at mid scores; score 3 now has 16 points. Note: the audit-#27 prereg's tracker-context
paragraph said score 3 "moves to 15" — an arithmetic slip, 14 + 2 = 16; flagged here rather
than by editing the registered file). Previous note (audit #26, superseded): rho 0.538,
p = 1.1e-05 (audit #26 + tracker repair; the 56-point value 0.547/1.3e-05 was reproduced
from the printed list before appending — three near-floor score-3 points continue the drift-floor
squeeze at mid scores; score 3 now has 14 points). Previous note (audit #25, superseded): rho 0.547,
p = 1.3e-05 (audit #25; the 53-point value 0.604/1.7e-06 was reproduced from the
printed list before appending — three score-4 points on the drift floor produce the second-largest
single-audit rho move in the program, AGAINST the hypothesis at the high-score end; candidate
floor-headroom confounder recorded in the audit's honesty section for post-n=30 exploratory
analysis). Previous note (audit #24, superseded): rho 0.604, p = 1.7e-06 (the 51-point value
0.607/2.4e-06 was reproduced from the printed list before appending — two sub-median score-3
drifts nudge rho down 0.003 while
sharpening significance). Previous note (audit #23, superseded): rho 0.607, p = 2.4e-06 ( the 48-point value 0.604/5.5e-06 was reproduced from the printed
list before appending — three new score-4 points spanning both drift regimes leave rho essentially
unchanged while sharpening significance). Previous note (audit #22, superseded): rho 0.604,
p = 5.5e-06 — the 46-point value 0.614/5.6e-06 was reproduced from the printed
list before appending — two ~0.35 pp score-3 points land below the score-3 median and nudge rho
slightly down while leaving significance unchanged). Previous note (audit #21, superseded): rho
0.614, p = 5.6e-06 — the score-0 anchor pair lands on the drift floor and pulls rho back up,
supporting the hypothesis at the low end exactly where audit #20 had cut against it. Previous note
(audit #20, superseded): rho 0.574, p = 4.7e-05 — the largest single-audit move yet (from 0.663), driven by ~1 pp of pure
randomization drift at score 1 (LFW's unseeded search out-drifts most score-2/3/4 points): evidence
against the hypothesis at the low-score end, suggesting the discretion TYPE (live randomization vs
pinned-but-unspecified choices) may matter as much as the count; no confirmatory weight. (Correction, run #11 second-instance addendum: first logged as 0.660/0.0005, computed from
the three new points' full-precision drifts; runs #1–#10's logged rho values reproduce from the
printed 2-dp list, so the printed-list convention is pinned from here on.) Family
coverage now includes clustering (a run #10 priority); the library-docs claim class enters the
confirmatory set at near-zero drift, replicating exploratory audit #3's pattern across a
2-minor-release gap. The repo-README anchor is DONE (audit #15: four points, the class's first
confirmatory entries, all at the drift floor). Priorities: a score-0/1 anchor outside the
certified-values class, further score-4/5 density (now 11 points at scores 4–5 vs 18 at score 2;
audit #17 added three and score 4 now carries the program's first high-score DISCREPANCY), and the
blocked audit #4 SGD target in a cap-free environment. The score-0 anchor outside the certified-values class is DONE (audit #21: two fully-seeded
sklearn-1.7.2 ensemble doctest rows, both 0.00 pp, the program's first version-gap-free target).
Score-3 density opened (audit #22: two Breiman-1996 ionosphere points; score 3 now at 9 points).
Score-4/5 density extended (audit #23: three FS96 vehicle points; 15 points at 4–5 vs 18 at
score 2). Score-3 density extended again (audit #24: two Breiman-1996 diabetes points at the
drift floor; score 3 now at 11 points). Score-4/5 density extended again (audit #25: three FS96
segmentation points at the drift floor; 18 points at scores 4–5 vs 18 at score 2 — parity reached;
the FS96 C4.5 no-test-set ladder is COMPLETE: glass / iris / ionosphere / sonar / vehicle /
segmentation, spanning drifts 0.06–6.86 pp at constant rubric 4). Score-5 density OPENED (audit #28: two StatLog-1994 Backprop
points; score 5 goes 1 -> 3 points, still the thinnest bucket). Named candidates for next run:
MORE score-5 targets — the one-shot n=30 test is 2 audits away and score 5 carries only 3 of the 63
points, so a third high-discretion audit would materially firm the high end before the test fires;
a low-published-error
score-2/3 target to help separate the floor-headroom confounder from the discretion score
(audit #25 honesty item 2), or the blocked audit #4 SGD target in a cap-free environment.
NOTE FOR THE n=30 ANALYSIS: two confounders are now on the record — floor-headroom (audits #25/#26,
contradicted by #27) and the COMPETENCE confounder (audit #28: secondaries A and B holding together
show that |drift| = discretion available x how well the reproducer resolves it, while the rubric
scores only the first factor). Neither may be used to adjust the pre-registered test; both belong in
the honesty section of RESULTS_DRIFT.md. LFW DONE audit #20; diabetes DONE audit #19 — the Breiman-2001 Forest-RI ladder is complete. Decade breadth 1967–2016 (audit #15
adds a 2014-era library-demo claim reproduced across a decade of releases).

## Log

- 2026-07-11 (scheduled run, Program 2b CONFIRMATORY TEST) — **The one-shot pre-registered test
  fired: VERDICT SUPPORTED (rho 0.587 > 0.5, p 1.7e-07 < 0.01).** Executed exactly per the
  audit-#30 binding hand-off: the 67 printed points were transcribed to a frozen JSON, machine-
  diffed against the tracker's printed list at `ff7af3bd` (identical, order and values), and the
  registered statistic computed once (`audits/drift_confirmatory_test.py`; scipy 1.15.3 two-sided
  primary + 10⁶-resample permutation cross-check, 0 exceedances). No audit run, no points added,
  no rubric touched. `results/RESULTS_DRIFT.md` published with the full 67-point table, the four
  pre-logged confounders, cluster non-independence (the bar survives audit-level and 13-cluster
  aggregation: rho 0.638 / 0.756, both p < 0.01), and drop-extreme sensitivities (0.570–0.608).
  Path note: prereg named the file without a directory; placed in `results/` per repo convention.
  Publish incidents: none planned via file-upload path (byte-verified below). Session choices made
  autonomously per scheduled-run rules: results path, MC permutation instead of infeasible exact
  enumeration (registered alternative scipy p is primary). OPEN FOR NEXT RUNS: Program 2b is
  complete — reverting the standing default to the main program's AUDIT MODE queue (B6/B11 next),
  unless Amirshayan registers a new drift-study extension; README does not yet mention the drift
  verdict (one-line addition, queued rather than done, to keep this increment exactly the
  hand-off's scope).

- 2026-07-11 (scheduled run, Program 2b run #28) — **Audit #28 landed clean, n=28/30.** First
  session in three to complete a full two-commit increment with no publish incident: the sandbox
  still has no git credential, so both commits went through the user's authenticated browser, but
  via GitHub's **file-upload** path instead of the web editor — byte-exact by construction, which
  retires the editor-mangling failure mode that cost audits #4/#26/#27 extra repair commits. Target:
  the StatLog book's Backprop rows (diabetes 0.248, Australian credit 0.154), chosen to attack the
  program's thinnest cell — score 5 held exactly ONE point. Both rows CONFIRMED (23.047 / 13.623 vs
  24.8 / 15.4, bar ±5.0 pp); tracker n=28/30, 63 points, exploratory rho **0.562 / p=1.7e-06**.
  The finding that matters is not the verdict but the pair of secondary predictions: A FAILED (score-5
  drift does NOT exceed the score-2 ceiling) while B HELD (dropping the one unstated preprocessing
  choice inflates drift 2.5-5.3x). Same claim, same rubric score, 5x the drift — so |drift| is a
  function of discretion AND of how well the reproducer closes it, and the rubric only scores the
  former. Logged as the **competence confounder** for the n=30 honesty section; it is NOT used to
  adjust anything, and the rubric was NOT amended post hoc. Two audits remain before the one-shot
  confirmatory test fires; the standing recommendation is that at least one of them be another
  score-5 target, since score 5 still carries only 3 of 63 points.

- 2026-07-11 (scheduled run) — **Audit #26 verified, still UNPUBLISHED (push blocker, 2nd
  session).** No new audit started: the queue's real blocker is publication, not production.
  Found the audit-#26 batch parked in the persistent sandbox by prior sessions and, rather
  than trusting it, re-verified it independently end-to-end (runner re-derived from the
  committed diabetes convention; UCI file re-downloaded and md5-rechecked; seed-0 [0,10) and
  seed-2 [50,60) chunks reproduce the parked cells BIT-IDENTICALLY; all three parked raw
  copies mutually bit-identical; every table number, SE, decrease %, probe, drift and the
  59-pt tracker rho 0.538/p=1.09e-05 recomputed from raw; prereg section diffed byte-identical
  against HEAD 35045bfba7). Verdict stands: **breast cancer e_S 5.967 / e_B 4.152 vs published
  5.9/3.7 → CONFIRMED both rows** at the ±2.0 pp bar; drifts 0.21/0.45 pp at blind rubric 3/5;
  tracker n=26/30 (incl. the PCA-quadratic repair point). Secondary prediction B (floor-headroom
  probe) HELD — the lowest-published-error target in the family under-drifted its same-rubric
  siblings, which is evidence that |drift| is partly bounded by distance-to-floor, i.e. a
  **confounder for the program's headline rho**; flagged for the post-n=30 analysis.
  **Push remains impossible from the sandbox** (no git credential; the run declined to hunt for
  one in the user's browser — correctly blocked as unauthorized credential exploration). Batch
  written to the Cowork outputs folder as `publish_audit26/` with a one-command publish script
  and md5s. **ACTION FOR AMIRSHAYAN: run that script (or paste a token) — three scheduled runs
  have now produced this same increment and none could publish it.** Until a credential path
  exists, further scheduled runs should NOT re-run audit #26; they should read this entry first.

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

- 2026-07-06 (scheduled session, Program 2b run #10) — Eleventh confirmatory audit landed: Freund &
  Schapire (1996) Table 2, bagging C4.5 column, glass + iris — verdict **CONFIRMED** (23.084/4.867 vs
  25.7/5.0, bar ±4.0 pp, all 3 seeds in; 3-seed drifts 2.43/0.33 pp at blind rubric 4/4; see Completed
  audits). First bagging-family points; secondary prediction HELD for the first time in six audits
  (glass 2.43 pp > the 1.96 pp score-2 ceiling). Tracker n=10/30; exploratory rho over 21 points =
  0.629 (p=0.0022). Sharpest finding: the pure-default base tree that broke audit #9's boost row by
  9.31 pp moves the bagged rows by ≤ 0.4 pp — ensemble type modulates how much base-learner discretion
  matters. Incidents: Copilot commit-message autofill recurred on commit 1 and was replaced+DOM-verified
  before submitting (disclosed in the audit's honesty item 6); GitHub's new-file editor now exposes the
  CodeMirror view at `.cm-content.cmTile.view` (old `.cmView` path gone) — noted for future runs;
  GitHub's web commit appended a trailing newline to fs96_bag_glass_iris_raw.json (5494 vs 5493 B,
  JSON-identical — same class as the run #1 incident). All
  pushes verified by SHA-pinned raw fetch with exact byte counts; freshness verified against the
  commits page at session start (HEAD 2eb1f5c). Program 1 untouched; its audit queue unchanged.

- 2026-07-10 (scheduled session, Program 2b run #21) — Twenty-second confirmatory audit landed:
  Freund & Schapire (1996) Table 2 vehicle row, C4.5/boost/bag (see Completed audits and
  `audits/AUDIT_freund-schapire1996-vehicle-c45-boost-bag.md`) — **CONFIRMED 3/3** at rubric
  4/4/4, drifts 2.61/0.88/0.70 pp; tracker n=22/30, exploratory rho 0.607 (p=2.4e-06). Audit #17's
  bag mechanism did NOT repeat on vehicle (−0.65 vs sonar's −6.56 pp; open contrast), while the
  default-base-tree boosting degeneration replicated on a fourth dataset. Fourth audit under the
  planner/executor split: 54 chunks delegated to a sonnet executor (no errors, no retries);
  planner re-aggregated, completeness- and duplicate-checked all parts before publishing.
  Two-commit rule kept: prereg `aa18d35` md5-verified byte-identical (10354 B, no trailing-newline
  delta) before any reproduction code; disclosed that GitHub's commit-message autofill prepended
  text to the intended prereg message (cosmetic; content governed by the md5 check). One
  sandbox incident: the session workspace disk filled mid-batch and the mounted copy of the
  results file truncated at its old byte size — caught by a byte-count check before any push;
  the push used a deterministically reconstructed copy (verified prereg bytes + results
  section), per VAR rule 5. The
  `.cm-content.cmTile.view` CodeMirror path from run #20's note still works for web edits.
  Freshness verified against the commits page at session start (HEAD e08fee3). Program 1
  untouched; its audit queue unchanged.

- 2026-07-10 (scheduled session, Program 2b run #22) — Twenty-third confirmatory audit landed:
  Breiman (1996) Table 2 diabetes rows e_S/e_B (see Completed audits and
  `audits/AUDIT_breiman1996-bagging-cart-diabetes.md`) — **CONFIRMED 2/2** at rubric 3/3, drifts
  0.64/0.28 pp; tracker n=23/30, exploratory rho 0.604 (p=1.7e-06). The Breiman-1996 CART-bagging
  ladder now spans glass / ionosphere / diabetes at drifts 0.95–1.37 / 0.32–0.39 / 0.28–0.64 pp —
  systematically more portable than FS96's C4.5 ensembles at equal-or-higher rubric scores.
  Wrong-version trap caught before registration: the Berkeley TR-421 and Springer journal PDFs
  disagree on this row's protocol AND numbers; the prereg pinned the journal version. Fifth audit
  under the planner/executor split (51/51 chunks delegated, zero retries; one chunk independently
  re-run bit-identical, all 300 raw rows re-verified). Session incidents: the home mount was 100%
  full at start (sklearn installed to a /tmp target dir, same 1.7.2/2.2.6 versions); a stale
  unreadable /tmp/diabetes.arff forced the runner's data path to /tmp/diabetes37.arff (md5 pin
  unchanged); the outputs mount served a stale copy of an edited file once (rebuilt sandbox-local,
  run-#21 incident class); GitHub's web commit appended a trailing newline to the raw JSON
  (12202 vs 12201 B, JSON-identical — run-#1/#10 incident class). Commit messages DOM-verified
  before committing (Copilot autofill active). Freshness verified against the commits API at
  session start (HEAD 797172e). Program 1 untouched; its audit queue unchanged.

- 2026-07-10 (scheduled session, Program 2b run #23) — Twenty-fourth confirmatory audit landed:
  Freund & Schapire (1996) Table 2 segmentation row, C4.5 alone / boost / bag (see Completed
  audits and `audits/AUDIT_freund-schapire1996-segmentation-c45-boost-bag.md`) — **CONFIRMED 3/3**
  at rubric 4/4/4, drifts 0.19/0.06/0.41 pp; tracker n=24/30, exploratory rho 0.547 (p=1.3e-05) —
  the second-largest single-audit rho move (0.604 → 0.547), AGAINST the hypothesis at the
  high-score end: the program's lowest-published-error score-4 target produced its lowest score-4
  drifts, and the audit's honesty section records a candidate floor-headroom confounder for
  post-n=30 exploratory analysis. Secondary prediction FAILED (eighth failure in eleven audits
  carrying it). The FS96 C4.5 no-test-set ladder is complete (six datasets, rubric-constant 4,
  drifts 0.06–6.86 pp). Sixth audit under the planner/executor split, first with the intended
  two-executor parallelism attempted: it FAILED (this sandbox's shell is single-process — the
  second executor's first instance executed nothing and was re-dispatched sequentially; new
  infrastructure rule: executors must run one at a time); 93/96 production chunks delegated, zero
  retries, two delegated cells re-run bit-identically by the auditor, all 170 raw cells
  re-aggregated from the executors' JSON logs. Session incidents, minor and disclosed: sklearn
  again absent (loaded from the surviving /tmp/pylibs target install, same 1.7.2/2.2.6/1.15.3
  triple); a stale /tmp/work dir from an earlier session was unwritable (fresh ~/w used); the
  FS96 paper PDF was read through a text-extraction pipeline so its byte md5 could not be
  re-asserted (audit honesty item 5). All pushes verified by SHA-pinned raw fetch + md5;
  freshness verified against the commits API at session start (HEAD c861da50). Program 1
  untouched; its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells)
  unchanged.

- 2026-07-10 (scheduled sessions, Program 2b runs #25 + #26; run #24 died at push after landing
  audit #26's prereg twice, 12 s apart — audit honesty item 1; run #25 executed all chunks and
  probes but died before pushing; run #26 found the completed state in the persistent sandbox,
  independently re-verified it — bit-identical chunk re-runs from a fresh md5-matched data
  download, full 500-row re-aggregation, all table numbers and both rho values recomputed,
  repair point re-checked from the file of record, runner reconstructed and proven faithful
  (audit honesty item 9) — and published the batch) — Twenty-fifth and
  twenty-sixth tracked increments landed: (a) tracker REPAIR — the untracked, complete
  PCA-quadratic audit (drift 0.46 pp, rubric 3/5) re-verified and added, n corrected 24 -> 25;
  (b) audit #26, Breiman-1996 Table 2 breast cancer e_S/e_B (see Completed audits and
  `audits/AUDIT_breiman1996-bagging-cart-breastcancer.md`) — **CONFIRMED 2/2** at rubric 3/3,
  drifts 0.21/0.45 pp at the family's tightest bar (±2.0 pp); tracker n=26/30, exploratory rho
  0.538 (p=1.1e-05). Secondary B (floor-headroom probe, the audit's purpose) HELD. Session
  incidents, minor and disclosed: /sessions disk 100% full — pip fell back and failed until
  redirected to a /tmp target install (same 1.7.2/2.2.6 stack), and one working-copy file was
  truncated mid-write (caught, refixed, all published files md5-verified); a probe-script
  multiprocessing pickling bug cost 8 executor launches (fixed before any probe number existed).
  Seventh planner/executor session: 20/20 production+probe chunks delegated sequentially (the
  run-#23 one-executor-at-a-time rule held, zero retries), one chunk re-run bit-identically,
  all 500 raw rows re-aggregated by the auditor. Freshness verified against the commits API at
  run-#26 session start (HEAD 35045bfba7). **PUSH BLOCKED in run #26 (disclosed):** the sandbox
  holds no push credential and the browser's GitHub session was signed out; per guardrail 5 the
  fully verified batch was parked, not retried endlessly — four files + md5 manifest in the
  session outputs folder (`publish/`) and the persistent sandbox (`/tmp/PENDING_PUSH_audit26.md`).
  FIRST ACTION for the next session: publish the parked batch byte-identically (md5s in the
  manifest), then update this entry's status. No number in the parked batch may be changed by
  the pushing session; re-verification recipe is in the manifest. Program 1
  untouched; its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells)
  unchanged.

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

- 2026-07-06 (scheduled session, Program 2b run #8) — Ninth confirmatory audit landed: Freund &
  Schapire (1996) ICML boosting paper, Table 2 glass rows, C4.5 alone + boosting C4.5 (see Completed
  audits) — **CONFIRMED** (31.682/20.981 vs 31.7/22.7, bar ±4.0 pp, all 3 seeds; 3-seed drifts
  0.23/1.36 pp at blind rubric 4/5 both rows). First boosting-family and first score-4 points —
  score coverage is now {1,2,3,4,5}; both landed below the 1.96 pp score-2 ceiling (secondary
  prediction FAILED), the third consecutive mid/high-score target to do so; tracker n=8/30,
  exploratory rho over 17 points = 0.625 (p=0.0073, no confirmatory weight). The audit's sharpest
  finding sits in a sensitivity check: sklearn's pure-default base tree reaches zero training error
  on glass, AdaBoost's perfect-fit early stop collapses the committee to one tree, and the boost row
  lands 9.31 pp OUT — the pre-pinned C4.5 -m2 mapping (entropy, min_samples_leaf=2) is load-bearing,
  a ~9 pp single-choice effect, the largest implementation-discretion effect measured in the
  confirmatory set so far (audit honesty item 1). The pre-declared degeneration risk (written into
  the prereg with the duplicate-pair data check) materialized exactly there and nowhere else.
  Publication via GitHub web uploader (no git credentials in sandbox, as in runs #2–#7); prereg
  web-committed to the remote (`c364bac`, byte-verified 9516 B) before any reproduction code existed
  (run #2 guardrail); commit messages DOM-verified pre-submit, no Copilot autofill this session
  (run #3 guardrail); freshness confirmed against the commits page (HEAD `da08746` at session start)
  per HARD GUARDRAIL 6; all pushes verified by SHA-pinned raw fetch with exact byte counts per the
  run #6 guardrail. Program 1 untouched; its audit queue (B6/B11 next, qrc_law.png regeneration,
  B5 regression cells) unchanged.

- 2026-07-06 (scheduled session, Program 2b run #9) — Tenth confirmatory audit landed: NIST/ITL StRD
  Linear Least Squares certified R-squared, Longley (1967) + Filip (see Completed audits) —
  **DISCREPANCY**, the program's second (after audit #2): certified 99.5479004577296 /
  99.6727416185620 pp vs reproduced 99.54790045772953 / 99.55957626651001 pp at the program's
  tightest bar (±0.1 pp); Longley exact to machine precision, Filip −0.1132 pp out via numpy
  lstsq's rcond=None rank truncation on a condition-1e15 design (scipy gelsd: −0.018 pp, in-bar;
  NIST's centered remedy: certified value to 13 digits — the claim itself is exactly right, the
  discrepancy is charged to the pinned reproduction route per protocol). First score-0 points and
  first regression-family target; score coverage now {0,1,2,3,4,5}; 3 replicate invocations
  bit-identical; standardized drifts 0.00/0.11 pp; secondary prediction FAILED (fourth consecutive
  audit — Filip's score-0 point out-drifts three score-2 points, so the drift measure's noise floor
  is solver-policy-dependent, not zero). Tracker n=9/30, exploratory rho over 19 points = 0.662
  (p=0.0020, no confirmatory weight). Publication via GitHub web uploader (no git credentials in
  sandbox, as in runs #2–#8); prereg web-committed to the remote (`4ad15b8`, byte-verified 8388 B)
  before any reproduction code existed (run #2 guardrail); commit messages DOM-verified pre-submit,
  no Copilot autofill this session (run #3 guardrail); one mechanical incident, disclosed in audit
  honesty item 6: the first commit-1 submit fired before GitHub finished processing the uploaded
  file and did not register — redone successfully, no repo state affected. Freshness confirmed
  against the commits page (HEAD `76cd9cc` at session start) per HARD GUARDRAIL 6; all pushes
  verified by SHA-pinned raw fetch with exact byte counts per the run #6 guardrail. Program 1
  untouched; its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells) unchanged.

- 2026-07-06 (scheduled session, Program 2b run #11) — Twelfth confirmatory audit landed: scikit-learn
  1.9.0 docs k-means digits demo, 3 init rows (see Completed audits) — **CONFIRMED**
  (62.056/70.104/62.224 vs 62.1/70.1/62.2, bar ±2.0 pp; 3-seed drifts 0.04/0.00/0.02 pp at blind
  rubric 2/2/2; 18/18 deterministic printed cells exact across the 1.9.0→1.7.2 gap; the only moving
  column is the unseeded silhouette subsample — precisely the rubric's randomization point). First
  clustering-family points; secondary prediction HELD. Tracker n=11/30; exploratory rho over 24
  points = 0.660 (p=0.0005, no confirmatory weight). Session notes: a stale commits-page HTML at
  session start briefly suggested run #10's agenda commit was missing; the commits API disagreed,
  was trusted, and no repair was needed or made (no files of record affected). One prereg prose slip
  disclosed in the audit's honesty item 1. Publication via GitHub web editor (no git credentials in
  sandbox, as in runs #2–#10); prereg web-committed (`988f595`) before any reproduction code existed
  (run #2 guardrail); commit messages DOM-verified pre-submit, no Copilot autofill this session
  (run #3 guardrail); freshness verified at session start (HEAD `c2b41b9`) per HARD GUARDRAIL 6; all
  pushes verified by SHA-pinned raw fetch (run #6 guardrail). Program 1 untouched; its audit queue
  (B6/B11 next, qrc_law.png regeneration, B5 regression cells) unchanged.

- 2026-07-06 (scheduled session, Program 2b run #11 — SECOND-INSTANCE ADDENDUM: duplicate-session
  incident + accidental replication) — Run #11's schedule fired TWICE: two autonomous instances
  worked the same task concurrently against one repo and one sandbox. This (second) instance
  independently selected the SAME target and measurand (sklearn 1.9.0 docs k-means digits table,
  v-meas column, ±2.0 pp at rubric 2/5) and had its own prereg drafted, then found the twin's
  `988f595` already on the commits page during the pre-commit freshness check (HARD GUARDRAIL 6)
  and STOOD DOWN — no duplicate prereg was pushed and no duplicate points entered the tracker; one
  increment, landed once, by the first instance. Working from the REMOTE prereg's pinned plan
  (started before the twin's results commit appeared), this instance's independent reproduction
  matches the published `audits/kmeans_digits_raw.json` bit-for-bit on all 54 deterministic cells
  (3 master seeds × 3 rows × 6 metrics; e.g. k-means++ v-measure 0.6205610989354435) — an
  accidental two-instance blind replication of audit #12, same class as the 2026-07-04 B13
  accidental replication. The first instance had no way to detect the second from its own session
  and is not at fault. Tracker correction folded into the tracker line above: spearmanr over the
  printed 2-dp points list gives rho 0.655 (p 0.00052), while the logged 0.660 (p 0.00045) used
  the three new points' full-precision drifts — the printed-list convention (used by runs #1–#10)
  is pinned going forward. This closes the 5-run supervised batch (runs #7–#11). **New guardrail
  for scheduled runs: re-check the live commits feed for a concurrent twin's commits BEFORE
  selecting or pushing a prereg and immediately before every push; on detection, the later
  instance stands down or adopts the earlier remote prereg — a claim is never double-registered.**

- 2026-07-06 (scheduled session, Program 2b run #12) — Thirteenth confirmatory audit landed: Joulin et
  al. (2016) fastText, Table 1, AG News h=10 + bigram rows (see Completed audits) — **CONFIRMED** on both
  rows (91.303–91.474 / 92.316–92.539 vs 91.5 / 92.5, bar ±2.0 pp, all 3 seeds; 3-seed drifts 0.08/0.11 pp
  at blind rubric 3/2). First 2010s-decade target (a run #11 priority) and first text-classification family
  points; primary source (ar5iv render of arXiv:1607.01759) and the authors' companion
  `classification-results.sh` (pins the bigram command and normalize_text preprocessing) both fetched and
  read this session; data md5-matched to the canonical Zhang AG News archive via the fast.ai S3 mirror.
  Secondary prediction FAILED in its first clause by 0.03 pp — below the measured ±0.1 pp thread-noise
  floor (fastText's `seed` does not fully determine training at `thread=4`; disclosed with replicates,
  honesty item 5) — so the within-paper ordering is uninformative. Tracker n=12/30; exploratory rho over
  26 printed 2-dp points = 0.642 (p=0.0004, no confirmatory weight). Publication via GitHub web editor (no
  git credentials in sandbox, as in runs #2–#11); prereg web-committed (`f6c0417`, byte-verified 6588 B)
  before any reproduction code existed (run #2 guardrail); live commits feed twin-checked before prereg
  selection and before pushes (run #11 guardrail) — no concurrent instance; Copilot autofill on both
  commit-dialog fields replaced/cleared and verified pre-submit (run #3 guardrail); one JS readback in the
  results-commit dialog was blocked by the browser extension (values had applied; verified visually and by
  SHA-pinned remote fetch); GitHub's web commit appended a trailing newline to fasttext_agnews_raw.json
  (2652 vs 2651 B, JSON-identical — same class as runs #1/#10). All pushes verified by SHA-pinned raw
  fetch with MD5 match per the run #6 guardrail. Program 1 untouched; its audit queue (B6/B11 next,
  qrc_law.png regeneration, B5 regression cells) unchanged.

- 2026-07-06 (scheduled session, Program 2b run #13) — Fourteenth confirmatory audit landed: Breiman
  (1996) "Bagging Predictors", Table 2, glass e_S + e_B rows (see Completed audits) — **CONFIRMED** on
  both rows (32.143 / 25.667 vs 30.4 / 23.6, bar ±4.0 pp, all 3 master seeds; 3-seed drifts 0.95 / 1.37 pp
  at blind rubric 3/5). Second bagging-family paper, giving the set's first cross-paper same-dataset
  contrast (Breiman's CART bagging vs FS96's C4.5 bagging on glass: 1.37 vs 2.43 pp at scores 3 vs 4).
  Primary source (Springer PDF of Machine Learning 24, 123–140) fetched and read this session; §4.3's
  prune-on-L rule and the tie-to-lowest-label vote implemented as stated; glass.data md5-identical to
  audits #9/#11. Secondary prediction FAILED (both standardized drifts under the 1.96 pp score-2
  ceiling). Tracker n=13/30; exploratory rho over 28 printed 2-dp points = 0.653 (p=0.0002, no
  confirmatory weight). Session mechanics: fresh git clone (not CDN) was ground truth at HEAD `9529f0d`
  (doubles as the pre-prereg twin check; post-prereg fetch showed a clean 475742c lineage, and the feed
  is re-checked before the results batch per the run #11 guardrail); no git push credentials (as runs
  #2–#12) so publication via the GitHub web editor, content injected through the CodeMirror document API
  (the new tiled editor exposes the view at `.cm-content.cmTile.view`, not `.cmView` — noted for future
  runs) with doc-vs-source equality asserted before each commit; prereg byte-verified on the remote via
  git fetch + md5 BEFORE any reproduction code ran (run #2 guardrail); Copilot autofill on both commit
  fields replaced/cleared and readback-verified (recurring class); compute chunked 12×~30 s under the
  45-s cap with per-iteration seeding (seed_i = master_seed·100000 + iteration) so chunk boundaries
  cannot affect the numbers. Priorities unchanged: score-0/1 anchors from other claim classes (repo-README
  row still open — the Zalando README table was inspected this session and its rows are third-party
  deep-learning submissions, NOT CPU-reproducible library claims; the S3 benchmark site remains the
  viable route), score-4/5 density, and the blocked audit #4 SGD target in a cap-free environment.
  Program 1 untouched; its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells)
  unchanged.

- 2026-07-07 (scheduled session, Program 2b run #14) — Fifteenth confirmatory audit landed:
  dmlc/xgboost CLI demo README (v1.7.6 tag), mushroom printed eval log, 4 numbers (see Completed
  audits) — **CONFIRMED**, exact to every printed digit at all 3 master seeds (drifts 0.00×4 at
  blind rubric 2/5; bar ±1.0 pp). The long-open repo-README anchor is DONE — the claim class
  enters the confirmatory set at the extreme low end, consistent with the shipped-artifact pattern
  (exploratory audit #3, confirmatory audit #12): when data + config ship inside the repo, a decade
  of library releases changes nothing the printed digits can see. Tracker n=14/30; exploratory rho
  over 32 printed 2-dp points = 0.667 (p=3e-05, no confirmatory weight). Session mechanics: fresh
  shallow clone as ground truth at HEAD `a6267d2`; no git push credentials (as runs #2–#13) so
  publication via the web editor's CodeMirror document API with doc-vs-source equality asserted
  before each commit (run #13 recipe worked unchanged); Copilot autofill cleared on the commit
  description and readback-verified (recurring class); the plain `xgboost` wheel blew the sandbox
  disk (bundled CUDA/NCCL) — `xgboost-cpu` used instead, noted for future runs; the whole audit fit
  in single 45-s calls (2-round GBT on 6.5k rows is trivial). Priorities now: a score-0/1 anchor
  outside the certified-values class, score-4/5 density, and the blocked audit #4 SGD target in a
  cap-free environment. Program 1 untouched; its audit queue (B6/B11 next, qrc_law.png regeneration,
  B5 regression cells) unchanged.

- 2026-07-07 (scheduled session, Program 2b run #15) — Audit #16 DONE: F&S-1996 Table 2 ionosphere
  row, all three C4.5 columns (plain / boost / bag), blind rubric 4/4/4 — three new score-4 points,
  the run #14 density priority. CONFIRMED at ±4.0 pp (12.251 / 6.439 / 7.721 vs published 8.9 /
  5.8 / 6.2); 3-seed drifts 2.99 / 0.85 / 1.34 pp; secondary prediction HELD via the tree row
  (second consecutive score-4 audit above the score-2 ceiling). Key mechanism note: audit #9's
  boost-degeneration replicated on a second dataset (default-base-tree route lands OUTSIDE the bar,
  +5.16 pp); the pinned C4.5 mapping is load-bearing for boost rows generally. Tracker n=15/30;
  exploratory rho over 35 printed 2-dp points = 0.686 (p=5.5e-06, no confirmatory weight). Session
  mechanics: fresh shallow clone at HEAD `7d31a8e`; primary-source PDF re-fetched cache-busted
  (byte-count 219704 identical to audits #9/#11); no git push credentials, publication via the web
  editor as in runs #2–#14 (prereg file web-committed before the results file, but NOTE the honesty
  caveat: reproduction ran before the prereg reached the remote this session — local prereg commit
  `d27e56a` precedes results only in the session-local graph); one file-sync truncation incident
  (runner's final print dropped by the outputs mount — silent empty-stdout failures; fixed by
  appending the tail on the Linux side and md5-checking, watch for this class); boost/bag grids
  chunked 2–4 CV runs per 45-s call. Priorities unchanged from the tracker paragraph; sonar C4.5
  columns (28.9 / 19.0 / 24.3) named as the next clean score-4 ladder rung.

- 2026-07-07 (scheduled session, Program 2b run #16) — Audit #17 DONE: F&S-1996 Table 2 sonar row,
  all three C4.5 columns, blind rubric 4/4/4 (the run #15 named candidate). **DISCREPANCY** — bagging
  row 17.740 vs published 24.3 (−6.56 pp, outside ±4.0 on all 3 seeds); tree/boost in-bar
  (26.731/17.356 vs 28.9/19.0). 3-seed drifts 3.36 / 0.99 / 6.86 pp; secondary HELD twice over.
  First high-score DISCREPANCY: at rubric 4 the drift distribution now spans 0.23–6.86 pp. Mechanism
  reading (honesty section): bagging unpruned modern trees ≈ proto-RF (16–18 % on sonar, matching
  audit #1's Breiman-2001 points), vs the paper's bagged *pruned* C4.5 at 24.3 — no sensitivity route
  (hard voting / default tree / unstratified) reaches the bar, so the discrepancy is not a pinning
  artifact. Boost-degeneration mechanism now replicated on a third dataset. Tracker n=16/30;
  exploratory rho over 38 printed 2-dp points = 0.706 (p=7.2e-07, no confirmatory weight). Session
  mechanics: fresh shallow clone at HEAD `0e2511d`, freshness confirmed against the commits page;
  primary-source PDF re-read via text extraction (byte md5 not re-assertable this session — noted in
  the audit); prereg web-committed REMOTE-FIRST and raw-verified (= local + trailing newline, the
  known web-commit behavior) before any reproduction code; boost/bag grids chunked 2–8 CV runs per
  45-s call; Copilot commit-dialog autofill replaced and readback-verified (recurring class).
  Program 1 untouched; its audit queue (B6/B11 next, qrc_law.png regeneration, B5 regression cells)
  unchanged.

- 2026-07-07 (run #16 SECOND INSTANCE, same-day addendum) — Duplicate scheduled session (second occurrence; first was run #11). This instance independently selected the same named target, scored the same blind rubric (4/4/4), and pinned a substantively identical reproduction plan; its remote-first prereg web-commit collided with `b2a5106` ("a file with the same name already exists") and it STOOD DOWN — no double-registration; audit file, raw JSON and tracker untouched by this instance. Verification banked: (a) independent rerun in a fresh sandbox (UCI raw `sonar.all-data`, md5 `77f5ca97c7b87b3edd3639a4ebc24e5c`, a different artifact than the primary's OpenML matrix; same sklearn 1.7.2/numpy 2.2.6) matches `audits/fs96_sonar_raw.json` on ALL 90 primary-configuration cells bit-identically — the audit #17 DISCREPANCY verdict (bag −6.56 pp, all 3 seeds out-of-bar) is independently reproduced end-to-end, the strongest cross-instance replication so far (run #11: 54 cells); (b) the paper artifact's byte-level md5 WAS re-asserted this session (219704 B, `cdbaa305c6cf034dea09bb268e4a5ce2`, byte-identical to audits #9/#11/#16), closing the gap noted in the primary's prereg and run #16 log entry. Convergent blind pre-registration by two instances is itself evidence the discretion rubric is mechanical. Guardrail for future scheduled runs: BEFORE scoring a rubric, check the commits page for a same-day prereg of the same target; if present, stand down to verification mode immediately (rerun the pinned plan, compare raw cells, log an addendum like this one; touch no files of record).

- 2026-07-09 (scheduled session, Program 2b run #17) — Audit #18 DONE: Breiman-2001 Table 2 glass
  row, Forest-RI Single Input + Selection, blind rubric 2/5 (the run #16 named candidate).
  **CONFIRMED** — 22.591/22.500 vs 21.2/20.6 (seed 0, bar ±2.5 pp); 3-seed drifts 0.83/1.81 pp;
  secondary HELD twice. Honest finding: the paper's Selection < Single-Input ordering does not
  reproduce — forest-level OOB selection on 192 training cases adds variance, not value. Tracker
  n=17/30; exploratory rho over 40 printed 2-dp points = 0.666 (p=2.7e-06, no confirmatory weight).
  Session mechanics: fresh shallow clone at HEAD `af410e1`, freshness confirmed against the
  commits API; paper PDF re-fetched, glass row transcribed (Adaboost 22.0 | Selection 20.6 |
  Single Input 21.2 | One Tree 36.9); prereg web-committed REMOTE-FIRST (`80faaa4`) and
  raw-verified byte-identical before any reproduction code ran; results `bfdab0d`; runner + raw
  JSON published via the repo upload page (`1f4332a`) — first use of direct multi-file upload;
  one earlier upload submit silently no-opped (redirected to the profile page, message field had
  not registered) and was caught by the commits-API SHA check and retried — verify uploads by SHA,
  not by redirect. Editor incident, same class as run #11: a first results paste APPENDED instead
  of replacing (Ctrl-A had not reached the CodeMirror editor); caught in-editor by the duplicated
  header before commit, fixed by an in-editor select-all + re-paste, and the committed file
  raw-verified. Copilot commit-dialog autofill replaced (recurring class). Note: the prereg header
  mislabels this session "run #16" — flagged in the audit's honesty section item 5; the registered
  file was not edited. Program 1 untouched; its audit queue (B6/B11 re-audit, qrc_law.png
  regeneration, B5 regression cells) unchanged.

- 2026-07-10 (scheduled session, Program 2b run #18) — Eighteenth confirmatory audit landed:
  Breiman (2001) Table 2 diabetes Forest-RI (see Completed audits) — **CONFIRMED**, 3-seed drift
  0.46/0.33 pp at blind rubric 2/5; the four-dataset within-paper ladder is complete, and drift
  shrank with holdout size exactly as the pre-registration predicted. Tracker n=18/30; exploratory
  rho over 42 points = 0.663 (p = 1.7e-06, no confirmatory weight). First run under the
  planner/executor efficiency rule: dataset download, chunk execution and the merge were delegated
  to a subordinate executor agent; judgment steps (target choice, rubric, bars, write-up,
  verification) stayed with the auditing session, which re-verified all 300 raw rows independently
  (recomputed both column means + the OOB-selection rule; 3 bit-identical spot re-runs). Incidents,
  minor and disclosed: (a) Copilot commit-message autofill recurred on web commits and was
  replaced+DOM-verified before submitting (run #10 class); (b) GitHub's web commit appended a
  trailing newline to rf_diabetes_raw.json