# AUDIT: Freund & Schapire (1996) "Experiments with a New Boosting Algorithm" — Table 2, segmentation row, C4.5 alone + boosting C4.5 + bagging C4.5

Program 2b confirmatory audit #25 (VAR). Session 2026-07-10 (Program 2b run #23, scheduled). Two-commit rule: this file is committed with an EMPTY results section BEFORE any reproduction code runs. Governed by `audits/PREREG_DRIFT.md`. This is the run #22 tracker's named candidate ("the last clean FS96 no-test-set candidate row (segmentation, 7-class — verify its Table 1 profile before scoring)"); the Table 1 profile was verified from the primary source THIS session, before rubric scoring, per that instruction.

## Claim under audit

Freund, Y. & Schapire, R. E. (1996), "Experiments with a New Boosting Algorithm", *Machine Learning: Proceedings of the Thirteenth International Conference (ICML 1996)* — primary source re-fetched and re-read this session (author's copy, cseweb.ucsd.edu/~yfreund/papers/boostingexperiments.pdf; fetched through the session's text-extraction pipeline, so the byte-level md5 could not be re-asserted this time — audits #9/#11/#16 recorded `cdbaa305c6cf034dea09bb268e4a5ce2`; the Table 1 and Table 2 segmentation transcripts below were read directly from this session's extracted text). Table 2 "Test error rates of various algorithms on benchmark problems", row `segmentation`, the three C4.5 columns (error-based; the C4.5 block of Table 2 carries only – / boost / bag columns — pseudo-loss applies to the FindAttrTest/FindDecRule weak learners, not to C4.5):

- **C4.5 alone ("–" column): published 3.6** (% test error).
- **boosting C4.5 ("boost" column): published 1.4** (% test error).
- **bagging C4.5 ("bag" column): published 2.7** (% test error).

Full printed segmentation row for the record: FindAttrTest 75.8 / 75.8 / 54.5, pseudo-loss 4.2 / 72.5; FindDecRule 73.7 / 53.3 / 54.3, pseudo-loss 2.4 / 58.0; C4.5 **3.6** / boost **1.4** / bag **2.7**.

Verbatim setup facts from the paper (identical protocol class to audits #9, #11, #16, #17 and #23): T = 100 rounds for all boosting/bagging runs; Table 1 row `segmentation 2310 - 7 - 19 -` — 2310 examples, **no provided test set**, 7 classes, 0 discrete + 19 continuous attributes, no missing values — so "we used 10-fold cross validation, and averaged the results over 10 runs (for a total of 100 runs of each algorithm on each dataset)"; the weak learner is "Quinlan's C4.5 decision-tree algorithm [18]. We used all the default options with pruning turned on. Since C4.5 expects an unweighted training sample, we used resampling."; boosting with C4.5 is AdaBoost.M1 (error-based); bagging trains each copy on a bootstrap sample of size N chosen uniformly at random with replacement, combined by "simple voting", "always uses resampling".

NOT audited, decided now before rubric scoring: FindAttrTest/FindDecRule columns (authors' own weak learners, no sklearn counterpart — standing exclusion from audits #9/#11/#16/#17/#23); other dataset rows.

Why this target: **the run #22 tracker names it explicitly** as the last clean FS96 no-test-set candidate row, and its Table 1 profile checked out clean this session (all-continuous, no missing values). Three more score-4 candidate points extend the score-4/5 density priority (15 points at scores 4–5 vs 18 at score 2 as of n=23). Completes the FS96 C4.5 no-test-set ladder at its largest dataset (2310 examples, 11× sonar) and in the program's lowest published-error regime for a score-4 target (1.4–3.6 %) — a floor-adjacent probe of the discretion–drift relation from the high-discretion side, complementing audit #21's score-0 floor anchors from the low-discretion side.

## Data (counting-only checks done before this commit; no reproduction)

OpenML data_id=36 (`segment`, the UCI Image Segmentation data in its combined 2310-example form — the form matching FS96's Table 1), fetched fresh this session: shape (2310, 19), class counts {brickface: 330, cement: 330, foliage: 330, grass: 330, path: 330, sky: 330, window: 330}, no missing values, X md5 (float64 C-order) `6bde54879753df9c397f892f6621ed6e` — matches Table 1 exactly (2310 examples, 7 classes, 19 continuous, no missing). Environment: python 3.10, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3 — the same triple as every prior Program 2b sklearn audit (re-asserted in the runner's JSON; sklearn again loaded from the /tmp target-dir install, run #20/#22 incident class).

## Blind discretion rubric (scored from the paper + scikit-learn 1.7 docs ONLY, before any code)

Discretion profiles are structurally identical to the corresponding columns of audits #9, #16, #17 and #23 (same paper, same protocol class, all-continuous no-missing no-test-set dataset); justifications restated per column with segmentation-specific notes.

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
4. Stopping criteria / tolerances — **1**. T = 100 is specified, but the pseudocode leaves epsilon_t = 0 behavior undefined and prescribes abort at epsilon_t >= 1/2, while sklearn's SAMME documentation prescribes early stop on a perfect weak fit — the effective committee size is implementation-decided. Segmentation note: on a 7-class problem sklearn's SAMME multiclass generalization stands in for the paper's error-based M1 (the audits #9/#23 multiclass route); the paper's 1/2 abort threshold vs SAMME's 1 − 1/K threshold is likewise implementation-decided.
5. Preprocessing assumptions — **1**. Same CV-construction discretion.

**bagging-C4.5 row — score 4/5.**

1. Tie-breaking / randomization — **1**. Bootstrap draws and their RNG, fold construction, tie handling (7-way vote ties possible) — no seeds anywhere.
2. Regularization / smoothing defaults — **1**. Same C4.5-pruning gap inside every committee member.
3. Initialization — **0**. Trees have none.
4. Stopping criteria / tolerances — **1**. T = 100 specified and bagging has no early-stop discretion, but the base tree's growth-termination rules are library-defaulted.
5. Preprocessing assumptions — **1**. Same CV-construction discretion; soft (probability-averaging) vs the paper's "simple voting" is additionally library-decided (sklearn BaggingClassifier default: soft where available).

## Reproduction plan (pinned before running)

Per master seed m in {0, 1, 2} (seed 0 primary for the verdict; drift for the tracker = 3-seed mean |reproduced − published| per row): 10 runs; run r uses `StratifiedKFold(n_splits=10, shuffle=True, random_state=1000*m+r)` — identical CV pinning to audits #9/#11/#16/#17/#23 for cross-audit comparability; per-run error = pooled misclassified / 2310; **row value = 100 × mean over the 10 runs**. Per-fold estimator seed fs = 100000*m + 100*r + k (k = fold index), identical to prior FS96 audits. Labels encoded to integers 0–6 in sorted class-name order (brickface … window).

- **Base tree (all rows):** `DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fs)`, everything else library default — the audits #9/#11/#16/#17/#23 pinned C4.5 mapping (entropy = closest expressible relative of gain ratio; min_samples_leaf=2 = C4.5's documented -m 2 default; C4.5's pessimistic pruning has no sklearn counterpart and stays at the library default, no pruning — that inexpressibility is rubric point 2, not an amendment).
- **C4.5-alone row:** the base tree fit per fold.
- **boost row:** `AdaBoostClassifier(estimator=<base tree>, n_estimators=100, random_state=fs)`, all else library default (SAMME reweighting route, sklearn's multiclass generalization of error-based M1) — identical to audits #9/#16/#17/#23.
- **bag row:** `BaggingClassifier(estimator=<base tree>, n_estimators=100, random_state=fs)`, all else library default (bootstrap n=N, soft vote) — identical to audits #11/#16/#17/#23.
- Labelled sensitivity checks (master seed 0 only; reported if the session budget allows, and never the verdict — this audit's compute is ~11× sonar's): (a) paper-faithful AdaBoost.M1 with resampling for the boost row (audit #9's sens route, votes generalized to 7 classes) and hard simple voting for the bag row (audit #11's sens route, 7-way majority, ties to the lowest class index); (b) pure-default base tree (gini, min_samples_leaf=1) for all three rows; (c) unstratified `KFold(shuffle=True)` for all three rows.

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (3.6 / 1.4 / 2.7 % error).
- **Tolerance: ±4.0 pp per row** (primary configuration, master seed 0) — the discretion-priced ladder at rubric 4/5, identical to the audits #9/#11/#16/#17/#23 score-4 bar. Two notes recorded now, before any data: (i) unlike sonar (audit #17), the published tree-vs-boost gap here is 2.2 pp and boost-vs-bag is 1.3 pp, both SMALLER than the bar — in-bar results need NOT preserve the paper's orderings, which are reported as observations only, never scored. (ii) Floor asymmetry: the published values sit 1.4–3.6 pp above the 0 % floor, so downward drift is bounded above by the published value itself for each row and a bar-exceeding DISCREPANCY can only occur UPWARD (reproduced worse than published by > 4.0 pp).
- **CONFIRMED** if ALL THREE rows satisfy |reproduced − published| ≤ 4.0 pp at seed 0 in the primary configuration; **DISCREPANCY** if any row exceeds; **COULD-NOT-RUN** if data access or the 45 s cap blocks execution. Bars never move after data.
- Secondary pre-registered prediction (hypothesis-consistent direction): at least one of the three rows' 3-seed drifts EXCEEDS 1.96 pp (still the largest score-2 drift in the confirmatory set at n=23). Recorded context, derived from the log: audit #17 registered this as 2-of-8 for prior score≥3 audits; since then it held in audits #17 and #23 and failed in #22 and #24 — 4 of 12 going in. Floor note (i) above cuts against it here: the tree row can at most drift 3.6 pp downward, the boost/bag rows at most 1.4/2.7 pp downward, so the prediction effectively requires either upward drift or a large tree-row drop.

## Results

*(empty at pre-registration commit — two-commit rule)*

## Honesty section

*(empty at pre-registration commit)*
