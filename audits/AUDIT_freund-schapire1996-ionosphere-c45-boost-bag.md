# AUDIT: Freund & Schapire (1996) "Experiments with a New Boosting Algorithm" — Table 2, ionosphere row, C4.5 alone + boosting C4.5 + bagging C4.5

Program 2b confirmatory audit #16 (VAR). Session 2026-07-07 (Program 2b run #15, scheduled). Two-commit rule: this file is committed with an EMPTY results section BEFORE any reproduction code runs. Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

Freund, Y. & Schapire, R. E. (1996), "Experiments with a New Boosting Algorithm", *Machine Learning: Proceedings of the Thirteenth International Conference (ICML 1996)* — **primary source re-fetched and re-read this session** (author's copy, cseweb.ucsd.edu/~yfreund/papers/boostingexperiments.pdf, 219704 B, md5 `cdbaa305c6cf034dea09bb268e4a5ce2`, byte-count identical to the artifact audits #9 and #11 read). Table 2 "Test error rates of various algorithms on benchmark problems", row `ionosphere`, the three C4.5 columns (error-based only — ionosphere is two-class, and "pseudo-loss was not used on any two-class problems"):

- **C4.5 alone ("–" column): published 8.9** (% test error).
- **boosting C4.5 ("boost" column): published 5.8** (% test error).
- **bagging C4.5 ("bag" column): published 6.2** (% test error).

Full printed ionosphere row for the record: FindAttrTest 17.8 / 8.5 / 17.3; FindDecRule 10.3 / 6.6 / 9.3; C4.5 **8.9** / boost **5.8** / bag **6.2**.

Verbatim setup facts from the paper (identical protocol class to audits #9 and #11): T = 100 rounds for all boosting/bagging runs; ionosphere has no provided test set (Table 1: 351 examples, no test set, 2 classes, 34 continuous attributes, no missing values), so "we used 10-fold cross validation, and averaged the results over 10 runs (for a total of 100 runs of each algorithm on each dataset)"; the weak learner is "Quinlan's C4.5 decision-tree algorithm [18]. We used all the default options with pruning turned on. Since C4.5 expects an unweighted training sample, we used resampling."; boosting with C4.5 is AdaBoost.M1 (error-based); bagging trains each copy "on a bootstrap sample ... of size N chosen uniformly at random with replacement" combined by "simple voting", "always uses resampling".

NOT audited, decided now before rubric scoring: FindAttrTest/FindDecRule columns (authors' own weak learners, no sklearn counterpart — standing exclusion from audits #9/#11); other dataset rows (the audits #9/#11 exclusion note stands: most remaining no-test-set rows carry missing values or categorical encodings; sonar's C4.5 columns remain a clean future candidate).

Why this target: **three new score-4 points in one audit — the tracker's #1 priority is score-4/5 density** (5 points at scores 4–5 vs 18 at score 2 as of n=14). Ionosphere is clean (all-continuous, no missing), already characterized in this repo (audit #8 recorded the canonical md5), and the harness is the audits #9/#11 pinned mapping, giving a within-dataset, cross-column (plain vs boosted vs bagged) drift contrast at fixed rubric score — plus a cross-dataset contrast against the glass/iris points from the same table. Feasibility: 351 instances, millisecond tree fits, chunked one (column × master seed) per call under the 45 s cap.

## Data (counting-only checks done before this commit; no reproduction)

Canonical UCI `ionosphere.data` (archive.ics.uci.edu/ml/machine-learning-databases/ionosphere/ionosphere.data, cache-busted fetch this session), md5 `85649e5fb5b15fb9dab726c400be61fe` — **identical to audit #8's recorded md5** — 351 rows, 34 float features + class label, class counts {g: 225, b: 126}, no missing values: matches Table 1 exactly (351 examples, 2 classes, 34 continuous, no missing). Environment: python 3.x, scikit-learn 1.7.2, scipy 1.15.3 (exact versions re-asserted in the runner's JSON).

## Blind discretion rubric (scored from the paper + scikit-learn 1.7 docs ONLY, before any code)

Discretion profiles are the same as the corresponding columns in audits #9 and #11 (same paper, same protocol class, all-continuous no-missing dataset); justifications restated per column.

**C4.5-alone row — score 4/5.**

1. Tie-breaking / randomization — **1**. No seeds anywhere; the 10-run averaging implies randomized fold construction; C4.5's split tie handling and sklearn's feature-tie randomness (`random_state`) are implementation-private.
2. Regularization / smoothing defaults — **1**. C4.5 "with all the default options with pruning turned on" (pessimistic pruning, confidence 0.25); scikit-learn has no pessimistic-error pruning — the library must default every growth/pruning control (ccp_alpha=0.0 = pruning OFF, gain-ratio inexpressible).
3. Initialization — **0**. Trees have none.
4. Stopping criteria / tolerances — **1**. Growth-termination rules for the reproducing tree (max_depth=None, min_samples_split=2, etc.) are left entirely to library defaults.
5. Preprocessing assumptions — **1**. The 10-fold CV construction is unspecified (stratified or not, shuffling, fold-size rounding, per-run pooling vs fold-averaging) and must be fixed by the reproducer.

**boosting-C4.5 row — score 4/5.**

1. Tie-breaking / randomization — **1**. All of the above PLUS the resampling bootstrap draws ("we used resampling") and their RNG; no seeds anywhere.
2. Regularization / smoothing defaults — **1**. Same C4.5-pruning gap; the base-tree configuration inside the reproducing booster is entirely library-defaulted.
3. Initialization — **0**. D_1(i) = 1/m is specified by the paper's AdaBoost.M1 pseudocode (Figure 1).
4. Stopping criteria / tolerances — **1**. T = 100 is specified, but the pseudocode leaves epsilon_t = 0 behavior undefined and prescribes abort at epsilon_t >= 1/2, while sklearn's SAMME documentation prescribes early stop on a perfect weak fit — the effective committee size is implementation-decided.
5. Preprocessing assumptions — **1**. Same CV-construction discretion.

**bagging-C4.5 row — score 4/5.**

1. Tie-breaking / randomization — **1**. Bootstrap draws and their RNG, fold construction, tie handling — no seeds anywhere.
2. Regularization / smoothing defaults — **1**. Same C4.5-pruning gap inside every committee member.
3. Initialization — **0**. Trees have none.
4. Stopping criteria / tolerances — **1**. T = 100 specified and bagging has no early-stop discretion, but the base tree's growth-termination rules are library-defaulted.
5. Preprocessing assumptions — **1**. Same CV-construction discretion; soft (probability-averaging) vs the paper's "simple voting" is additionally library-decided (sklearn BaggingClassifier default: soft where available).

## Reproduction plan (pinned before running)

Per master seed m in {0, 1, 2} (seed 0 primary for the verdict; drift for the tracker = 3-seed mean |reproduced − published| per row): 10 runs; run r uses `StratifiedKFold(n_splits=10, shuffle=True, random_state=1000*m+r)` — identical CV pinning to audits #9 and #11 for cross-audit comparability; per-run error = pooled misclassified / 351; **row value = 100 × mean over the 10 runs**. Per-fold estimator seed fs = 100000*m + 100*r + k (k = fold index), identical to audits #9/#11.

- **Base tree (all rows):** `DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fs)`, everything else library default — the audits #9/#11 pinned C4.5 mapping (entropy = closest expressible relative of gain ratio; min_samples_leaf=2 = C4.5's documented -m 2 default; C4.5's pessimistic pruning has no sklearn counterpart and stays at the library default, no pruning — that inexpressibility is rubric point 2, not an amendment).
- **C4.5-alone row:** the base tree fit per fold.
- **boost row:** `AdaBoostClassifier(estimator=<base tree>, n_estimators=100, random_state=fs)`, all else library default (SAMME reweighting route) — identical to audit #9.
- **bag row:** `BaggingClassifier(estimator=<base tree>, n_estimators=100, random_state=fs)`, all else library default (bootstrap n=N, soft vote) — identical to audit #11.
- Labelled sensitivity checks (reported, never the verdict; master seed 0 only): (a) paper-faithful AdaBoost.M1 with resampling for the boost row (audit #9's sens route) and hard simple voting for the bag row (audit #11's sens route); (b) pure-default base tree (gini, min_samples_leaf=1) for all three rows; (c) unstratified `KFold(shuffle=True)` for all three rows.

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (8.9 / 5.8 / 6.2 % error).
- **Tolerance: ±4.0 pp per row** (primary configuration, master seed 0) — the discretion-priced ladder at rubric 4/5, identical to the audits #9/#11 score-4 bar. Note recorded now: the published C4.5-vs-boost gap is 3.1 pp and C4.5-vs-bag is 2.7 pp, both SMALLER than the bar, so the bar cannot certify the paper's ensemble-beats-tree ordering; the ordering is reported as an observation only, never scored.
- **CONFIRMED** if ALL THREE rows satisfy |reproduced − published| ≤ 4.0 pp at seed 0 in the primary configuration; **DISCREPANCY** if any row exceeds; **COULD-NOT-RUN** if data access or the 45 s cap blocks execution. Bars never move after data.
- Secondary pre-registered prediction (hypothesis-consistent direction): at least one of the three rows' 3-seed drifts EXCEEDS 1.96 pp (the largest score-2 drift in the confirmatory set). Recorded context: this prediction has held in only 1 of 7 prior score≥3 audits' first tests (audit #11 glass).

## Results

(EMPTY at pre-registration — filled only by the results commit.)
