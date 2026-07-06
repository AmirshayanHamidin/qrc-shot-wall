# AUDIT: Freund & Schapire (1996) "Experiments with a New Boosting Algorithm" — Table 2, bagging C4.5 column, glass + iris rows

Program 2b confirmatory audit #11 (VAR). Session 2026-07-06 (Program 2b run #10). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

Freund, Y. & Schapire, R. E. (1996), "Experiments with a New Boosting Algorithm", *Machine Learning: Proceedings of the Thirteenth International Conference (ICML 1996)* — **primary source re-fetched and re-read this session** (author's copy, cseweb.ucsd.edu/~yfreund/papers/boostingexperiments.pdf, 219704 B, byte-identical to the artifact audit #9 read). Table 2 "Test error rates of various algorithms on benchmark problems", column **bagging C4.5 ("bag")**, two rows:

- **glass, bagging C4.5: published 25.7** (% test error).
- **iris, bagging C4.5: published 5.0** (% test error).

Verbatim setup facts from the paper: bagging is "Breiman's [1] 'bootstrap aggregating'" — each of the multiple copies of the learner is trained "on a bootstrap sample, i.e., a sample of size N chosen uniformly at random with replacement from the original training set"; the hypotheses "are then combined using simple voting"; "bagging always uses resampling rather than reweighting" and "does not modify the distribution over examples"; "In all our experiments, we set the number of rounds of boosting or bagging to be T = 100"; the weak learner is "Quinlan's C4.5 decision-tree algorithm [18]. We used all the default options with pruning turned on."; glass and iris have no provided test set, so "we used 10-fold cross validation, and averaged the results over 10 runs (for a total of 100 runs of each algorithm on each dataset)". Table 1: glass 214 examples, no test set, 7 classes, 9 continuous attributes, no missing values; iris 150 examples, no test set, 3 classes, 4 continuous attributes, no missing values.

Full printed rows for the record: glass — FindAttrTest 51.5/51.1/50.9, pseudo-loss 29.4/54.2; FindDecRule 49.7/48.5/47.2, pseudo-loss 25.0/52.0; C4.5 31.7 / boost 22.7 / **bag 25.7**. iris — FindAttrTest 35.2/4.7/28.4, pseudo-loss 4.8/7.1; FindDecRule 38.3/4.3/18.8, pseudo-loss 4.8/5.5; C4.5 5.9 / boost 5.0 / **bag 5.0**.

NOT audited, decided now before rubric scoring: the glass C4.5-alone and boost columns (audit #9's claims — never repeated); the iris C4.5-alone and boost columns (one new-family point set per audit; the bagging column is the unclaimed family); FindAttrTest/FindDecRule columns (authors' own weak learners, no sklearn counterpart); other dataset rows (pima not distributable by UCI; most remaining no-test-set rows carry missing values or categorical encodings).

Why this target: the **bagging family** is the tracker's explicitly named unclaimed item ("bagging — same F&S/Breiman tables — remains unclaimed"), and per the blind rubric below both rows land at **score 4/5** — exactly the density priority (only three 4/5 points exist and all landed surprisingly low; these two decide whether that pattern holds). Also adds one new dataset (iris — first appearance in the program). Feasibility: 214/150 instances, millisecond tree fits, chunked one master seed per call under the 45 s cap.

## Data (counting-only checks done before this commit; no reproduction)

Canonical UCI `glass.data` (archive.ics.uci.edu/ml/machine-learning-databases/glass/glass.data), md5 `2732c9170bf8c483f33da3c58929c067` — **identical to audit #9's recorded md5** — 214 rows, class counts {1: 70, 2: 76, 3: 17, 5: 13, 6: 9, 7: 29}, matching Table 1. Canonical UCI `iris.data` (archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data), md5 `42615765a885ddf54427f12c34a0a070`, 150 rows, 50/50/50 across the three species, 4 float features, matching Table 1. Provenance note, recorded before scoring: the UCI iris file famously differs from Fisher's 1936 paper in two rows (35 and 38, per `iris.names`); the UCI file is used AS-IS because the paper's footnote 3 names the UCI repository as its source — the claim is about the UCI data.

## Blind discretion rubric (scored from the paper + scikit-learn 1.7 docs ONLY, before any code)

**bagging-C4.5, glass row — score 4/5.** **bagging-C4.5, iris row — score 4/5.** (Identical discretion profile — same column, same protocol class, both all-continuous no-missing multi-class datasets; one shared justification set.)

1. Tie-breaking / randomization — **1**. No seeds anywhere; the T=100 bootstrap draws are random by definition, the 10-run averaging implies randomized fold construction, and the reproducing tree's split tie handling (`random_state`) is implementation-private.
2. Regularization / smoothing defaults — **1**. The base learner is C4.5 "with all the default options with pruning turned on" (pessimistic pruning, confidence 0.25); scikit-learn has no pessimistic-error pruning — the library must default every growth/pruning control (ccp_alpha=0.0 = pruning OFF, gain-ratio inexpressible). Same gap as audit #9, rubric point 2.
3. Initialization — **0**. Trees have none, and bagging's per-round distribution is fully specified by the method's definition (uniform bootstrap of size N).
4. Stopping criteria / tolerances — **1**. T = 100 is specified and bagging has no early-stop discretion (unlike AdaBoost), but the base tree's growth-termination rules (max_depth=None, min_samples_split=2, etc.) are left entirely to library defaults — same category reading as audits #6 and #9, rubric point 4.
5. Preprocessing assumptions — **1**. The 10-fold CV construction is unspecified (stratified or not, shuffling, fold-size rounding, per-run pooling vs fold-averaging) and must be fixed by the reproducer.

## Reproduction plan (pinned before running)

Per master seed m in {0, 1, 2} (seed 0 primary for the verdict; drift for the tracker = 3-seed mean |reproduced − published| per row): 10 runs; run r in {0..9} uses `StratifiedKFold(n_splits=10, shuffle=True, random_state=1000*m+r)` (identical CV pinning to audit #9, for cross-audit comparability); per-run error = pooled misclassified / N; **row value = 100 × mean over the 10 runs**.

- **Base tree (both rows):** `DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fold_seed)`, everything else library default — the same C4.5 mapping pinned in audit #9's pre-registration (entropy = sklearn's information-gain criterion, closest expressible relative of gain ratio; min_samples_leaf=2 = C4.5's documented -m 2 default; C4.5's pessimistic pruning has no sklearn counterpart and stays at the library default, no pruning — that inexpressibility is rubric point 2, not an amendment).
- **Bagging:** `BaggingClassifier(estimator=<the same tree config>, n_estimators=100, random_state=fold_seed)`, everything else library default. sklearn's defaults match the paper's definition on sampling (max_samples=1.0 with replacement = bootstrap of size N) but NOT on aggregation: the paper specifies "simple voting" while sklearn's documented default aggregates by averaging predicted class probabilities (soft voting). Disclosed now; the primary route stays modern-default per program convention, and the paper-faithful vote is sensitivity (a).
- Labelled sensitivity checks (reported, never the verdict; master seed 0 only): (a) paper-faithful **hard simple voting** (majority over the 100 trees' predicted labels); (b) pure-default base tree (gini, min_samples_leaf=1) — bagging has no perfect-fit early stop, so unlike audit #9's boost row no degeneration is expected: this isolates the C4.5-mapping sensitivity in a committee that always uses all 100 trees; (c) unstratified `KFold(shuffle=True)`.
- One pooled test case = 1/214 = 0.467 pp (glass), 1/150 = 0.667 pp (iris).

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (25.7 for glass, 5.0 for iris).
- **Tolerance: ±4.0 pp per row** (primary configuration, master seed 0). Rationale: the discretion-priced ladder at rubric 4/5, identical to audit #9's score-4 bar (score 3 → ±3.0, score 4 → ±4.0, score 5 → ±5.0); prices the same 30-year C4.5→CART-family gap plus bootstrap/vote discretion. Note recorded now: for glass the published bag-vs-tree gap is 6.0 pp (25.7 vs 31.7), so the bar cannot be satisfied by the committee merely reproducing the tree row; for iris the published tree and bag rows differ by only 0.9 pp, so no such separation exists and none is claimed.
- **CONFIRMED** if BOTH rows satisfy |reproduced − published| ≤ 4.0 pp at seed 0 in the primary configuration; **DISCREPANCY** if either row exceeds; **COULD-NOT-RUN** if data access or the 45 s cap blocks execution. Bars never move after data.
- Secondary pre-registered prediction (hypothesis-consistent direction): at rubric 4/5, at least one row's 3-seed drift EXCEEDS 1.96 pp (the largest score-2 drift in the confirmatory set).

## Results

Data checks: `glass.data` md5 `2732c9170bf8c483f33da3c58929c067`, 214 rows; `iris.data` md5 `42615765a885ddf54427f12c34a0a070`, 150 rows — identical to the pre-commit counting checks (md5 re-asserted inside every runner invocation).

Primary configurations (pinned mapping, master seed 0; 10 runs × stratified 10-fold CV, pooled per-run error, mean over runs):

| Row | Published | Reproduced | Drift |
|---|---|---|---|
| glass, bagging C4.5 (T=100) | 25.7 | **23.084** | −2.616 pp |
| iris, bagging C4.5 (T=100) | 5.0 | **4.867** | −0.133 pp |

Master seeds 1 and 2: glass 23.364 / 23.364; iris 4.533 / 4.600. **Standardized drift for the tracker (3-seed mean |reproduced − published|): glass 2.43 pp, iris 0.33 pp.** The paper's bag-beats-tree ordering on glass reproduces relative to audit #9's tree row (23.08–23.36 here vs 31.68–32.29 there, an 8.3–8.6 pp improvement vs the published 6.0); on iris the published 0.9 pp tree-vs-bag gap is within noise and no ordering claim is scored.

Labelled sensitivity checks (master seed 0, never the verdict):

- (a) Paper-faithful **hard simple voting** (hand-rolled Breiman bagging, majority over 100 tree labels): glass 23.084, iris 5.200 — within 0.34 pp of sklearn's soft-vote route on both datasets. The soft-vs-hard aggregation discretion is numerically inert here. (The glass means agree to all printed digits by coincidence of averaging — the per-run values differ; see the raw JSON.)
- (b) Pure-default base tree (gini, min_samples_leaf=1): glass 23.458, iris 4.933. As pre-declared, NO degeneration occurs (bagging has no perfect-fit early stop — all 100 trees are always used), and the C4.5 mapping is worth ≤ 0.4 pp inside a bagged committee — versus 9.31 pp for the same mapping inside audit #9's AdaBoost. Bagging insulates the very discretion that broke the naive boosting route.
- (c) Unstratified `KFold(shuffle=True)`: glass 24.486, iris 4.400 — the CV-construction discretion is worth up to 1.4 pp on glass (vs ≤ 0.6 pp in audit #9), the largest single-choice effect measured in this audit.

Secondary pre-registered prediction: **HELD.** The glass row's 3-seed drift (2.43 pp) exceeds 1.96 pp (the largest score-2 drift in the confirmatory set) — the FIRST mid/high-score point to clear the score-2 ceiling after six consecutive failures of this prediction (audits #5–#10 pattern), though the iris row (0.33 pp) lands below it.

## Verdict

**CONFIRMED.** Both rows land within the pre-registered ±4.0 pp at master seed 0 in the primary configuration (−2.616 pp and −0.133 pp), robust across all 3 master seeds (worst case: glass −2.616, iris −0.467). Breiman-style bagging of a mapped C4.5 reproduces under a 2026 library: iris is within one-fifth of a pooled test case of the 1996 number, and glass lands 2.3–2.6 pp BELOW the published error (modern bagged trees slightly better than 1996 bagged C4.5 on this dataset), the same favorable direction as audit #9's boost row.

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3. Reproduction script: `audits/audit_fs96_bag_glass_iris_run.py` (chunked one master-seed × dataset per invocation for the 45 s per-process cap). Raw output (per-run errors, all sensitivity configurations): `audits/fs96_bag_glass_iris_raw.json` (md5 `2bf2379f81e98362d0b421c5704aa8bc`, 5493 B). Both committed in this session's batch.

## Honesty section

1. The reproduced glass row sits 2.3–2.6 pp below the published 25.7 at every seed — a systematic, not seed-level, gap. Default attribution: implementation differences (unpruned info-gain CART vs pruned gain-ratio C4.5 inside the committee, soft vs hard vote, 2026 numerics), not an error in the 1996 table. The published number is not challenged; its library-defaults portability costs ~2.4 pp, and that is exactly what the score-4 rubric priced.
2. What this is NOT: not an accusation, not a re-tuning exercise, and not evidence about bagging's merit — only about how far the printed numbers move when a 2026 library holds the discretion the claim left open.
3. The CONFIRMED verdict is mapping-conditional in principle, but far less than audit #9's: sensitivity (b) shows the pure-default base tree moves the rows ≤ 0.4 pp (vs 9.31 pp under boosting). A reproducer making any of the obvious choices lands inside the bar on both rows.
4. C4.5's gain ratio and pessimistic pruning remain inexpressible in scikit-learn; the residual ~2.4 pp glass gap plausibly includes exactly this (pruned committees generalize differently on glass's 6 overlapping classes), but this attribution is unverifiable here and stays a hypothesis.
5. The two (score, drift) points share the paper, the protocol, and the CV harness (though not the dataset), so they are not independent — same caveat as every prior multi-row audit; cross-audit, they also share the glass dataset and harness with audit #9's points.
6. Two-commit ordering: pre-registration was committed to the REMOTE (`b358b39`, verified byte-identical at 9218 B + md5 by SHA-pinned fetch) before any reproduction code existed; results were computed afterwards in this same session. Copilot autofill DID populate the commit-message field in the commit dialog ("Add audit for Freund & Schapire bagging C4.5 study"); it was replaced with the pre-planned message via the DOM and verified before submitting, per standing incident procedure.
7. The published numbers are means over the authors' own 100 randomized 1996 runs with an unlogged RNG; our 3 × (10-run mean) band is the closest achievable comparison. The iris row's published 5.0 is likely rounded to one decimal (± 0.05 pp), immaterial at this bar.
8. The secondary prediction's success is one point, not a trend reversal: the score-4 column now holds drifts {0.23, 1.36, 2.43, 0.33} — two of four above 1 pp, still none near the score-3 MLP points (8.95/10.35). The exploratory rho moved 0.662 → 0.629 with these two points; the n=30 test will decide.
