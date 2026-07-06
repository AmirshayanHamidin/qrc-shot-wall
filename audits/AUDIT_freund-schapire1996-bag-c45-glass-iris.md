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

*(empty — to be filled in a separate commit AFTER the pre-registration commit is on the remote)*

## Verdict

*(empty)*

## Environment

*(empty)*

## Honesty section

*(empty)*
