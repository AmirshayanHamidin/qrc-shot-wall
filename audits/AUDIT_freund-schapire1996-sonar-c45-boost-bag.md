# AUDIT: Freund & Schapire (1996) "Experiments with a New Boosting Algorithm" — Table 2, sonar row, C4.5 alone + boosting C4.5 + bagging C4.5

Program 2b confirmatory audit #17 (VAR). Session 2026-07-07 (Program 2b run #16, scheduled). Two-commit rule: this file is committed with an EMPTY results section BEFORE any reproduction code runs. Governed by `audits/PREREG_DRIFT.md`. This is the tracker's named candidate from run #15 ("F&S-1996 sonar row, C4.5 columns").

## Claim under audit

Freund, Y. & Schapire, R. E. (1996), "Experiments with a New Boosting Algorithm", *Machine Learning: Proceedings of the Thirteenth International Conference (ICML 1996)* — primary source re-fetched and re-read this session (author's copy, cseweb.ucsd.edu/~yfreund/papers/boostingexperiments.pdf; fetched through the session's text-extraction pipeline, so the byte-level md5 could not be re-asserted this time — the Table 2 sonar transcript below was read directly from this session's extracted text and is identical to the transcript recorded in audit #16's session). Table 2 "Test error rates of various algorithms on benchmark problems", row `sonar`, the three C4.5 columns (error-based only — sonar is two-class, and "pseudo-loss was not used on any two-class problems"):

- **C4.5 alone ("–" column): published 28.9** (% test error).
- **boosting C4.5 ("boost" column): published 19.0** (% test error).
- **bagging C4.5 ("bag" column): published 24.3** (% test error).

Full printed sonar row for the record: FindAttrTest 25.9 / 16.5 / 25.9; FindDecRule 31.4 / 16.2 / 26.1; C4.5 **28.9** / boost **19.0** / bag **24.3**.

Verbatim setup facts from the paper (identical protocol class to audits #9, #11 and #16): T = 100 rounds for all boosting/bagging runs; sonar has no provided test set (Table 1: 208 examples, no test set, 2 classes, 60 continuous attributes, no missing values), so "we used 10-fold cross validation, and averaged the results over 10 runs (for a total of 100 runs of each algorithm on each dataset)"; the weak learner is "Quinlan's C4.5 decision-tree algorithm [18]. We used all the default options with pruning turned on. Since C4.5 expects an unweighted training sample, we used resampling."; boosting with C4.5 is AdaBoost.M1 (error-based); bagging trains each copy "on a bootstrap sample ... of size N chosen uniformly at random with replacement" combined by "simple voting", "always uses resampling".

NOT audited, decided now before rubric scoring: FindAttrTest/FindDecRule columns (authors' own weak learners, no sklearn counterpart — standing exclusion from audits #9/#11/#16); other dataset rows (the standing exclusion note applies: most remaining no-test-set rows carry missing values or categorical encodings).

Why this target: **the run #15 tracker names it explicitly** — three more score-4 points (the #1 density priority: 8 points at scores 4–5 vs 18 at score 2 as of n=15), completing a two-dataset, six-column discretion-constant contrast with audit #16 (same paper, same columns, same rubric profile, different dataset), plus a third F&S dataset family point after glass and iris. Sonar is clean (all-continuous, no missing), already characterized in this repo (audits #1 and #2 used it; audit #1 recorded the canonical OpenML md5), and the harness is the audits #9/#11/#16 pinned mapping. Cross-audit interest: sonar is the same dataset on which the program measured its largest drifts so far (Gorman-Sejnowski MLP, 8.95/10.35 pp) and near-floor drifts (Breiman RF, 0.59/0.94 pp) — this audit adds the tree-ensemble family on that same dataset at rubric 4.

## Data (counting-only checks done before this commit; no reproduction)

OpenML data_id=40 (Aha's canonical `sonar.all-data`), fetched fresh this session: shape (208, 60), class counts {Mine: 111, Rock: 97}, no missing values, X md5 `e5f03fedbe063c500c22a7be8c4fe878` — **identical to audit #1's recorded md5** — matches Table 1 exactly (208 examples, 2 classes, 60 continuous, no missing). Environment: python 3.x, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3 — the same triple as audits #9/#11/#16 (exact versions re-asserted in the runner's JSON).

## Blind discretion rubric (scored from the paper + scikit-learn 1.7 docs ONLY, before any code)

Discretion profiles are identical to the corresponding columns of audits #9, #11 and #16 (same paper, same protocol class, all-continuous no-missing dataset); justifications restated per column.

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

Per master seed m in {0, 1, 2} (seed 0 primary for the verdict; drift for the tracker = 3-seed mean |reproduced − published| per row): 10 runs; run r uses `StratifiedKFold(n_splits=10, shuffle=True, random_state=1000*m+r)` — identical CV pinning to audits #9/#11/#16 for cross-audit comparability; per-run error = pooled misclassified / 208; **row value = 100 × mean over the 10 runs**. Per-fold estimator seed fs = 100000*m + 100*r + k (k = fold index), identical to audits #9/#11/#16.

- **Base tree (all rows):** `DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fs)`, everything else library default — the audits #9/#11/#16 pinned C4.5 mapping (entropy = closest expressible relative of gain ratio; min_samples_leaf=2 = C4.5's documented -m 2 default; C4.5's pessimistic pruning has no sklearn counterpart and stays at the library default, no pruning — that inexpressibility is rubric point 2, not an amendment).
- **C4.5-alone row:** the base tree fit per fold.
- **boost row:** `AdaBoostClassifier(estimator=<base tree>, n_estimators=100, random_state=fs)`, all else library default (SAMME reweighting route) — identical to audits #9/#16.
- **bag row:** `BaggingClassifier(estimator=<base tree>, n_estimators=100, random_state=fs)`, all else library default (bootstrap n=N, soft vote) — identical to audits #11/#16.
- Labelled sensitivity checks (reported, never the verdict; master seed 0 only): (a) paper-faithful AdaBoost.M1 with resampling for the boost row (audit #9's sens route) and hard simple voting for the bag row (audit #11's sens route); (b) pure-default base tree (gini, min_samples_leaf=1) for all three rows; (c) unstratified `KFold(shuffle=True)` for all three rows.

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (28.9 / 19.0 / 24.3 % error).
- **Tolerance: ±4.0 pp per row** (primary configuration, master seed 0) — the discretion-priced ladder at rubric 4/5, identical to the audits #9/#11/#16 score-4 bar. Note recorded now: unlike ionosphere (audit #16), the published C4.5-vs-boost gap here is 9.9 pp and C4.5-vs-bag is 4.6 pp, both LARGER than the bar — so if all three rows land in-bar, the reproduction necessarily preserves the paper's boost-beats-tree ordering (bag-vs-boost gap 5.3 pp likewise). The ordering is still reported as an observation only, never scored.
- **CONFIRMED** if ALL THREE rows satisfy |reproduced − published| ≤ 4.0 pp at seed 0 in the primary configuration; **DISCREPANCY** if any row exceeds; **COULD-NOT-RUN** if data access or the 45 s cap blocks execution. Bars never move after data.
- Secondary pre-registered prediction (hypothesis-consistent direction): at least one of the three rows' 3-seed drifts EXCEEDS 1.96 pp (the largest score-2 drift in the confirmatory set). Recorded context: this prediction has held in 2 of 8 prior score≥3 audits' first tests (audit #11 glass, audit #16 tree row).

## Results

*(empty at pre-registration — to be filled only after the runs complete)*

