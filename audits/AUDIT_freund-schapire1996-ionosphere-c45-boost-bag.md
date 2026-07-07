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

Data check (re-asserted inside every runner invocation): `ionosphere.data` md5 `85649e5fb5b15fb9dab726c400be61fe`, 351 rows, {g: 225, b: 126} — identical to the pre-commit counting checks. Environment: scikit-learn 1.7.2, numpy 2.2.6, CPU only. Execution note: chunked one (column x master-seed x run-subset) per tool call under the 45 s cap; chunk log in `audits/fs96_iono_raw.json`.

Primary configurations (library defaults per the pinned plan, master seed 0):

| Row | Published | Reproduced | Drift |
|---|---|---|---|
| C4.5 alone | 8.9 | **12.251** | +3.351 pp |
| boosting C4.5 | 5.8 | **6.439** | +0.639 pp |
| bagging C4.5 | 6.2 | **7.721** | +1.521 pp |

Master seeds 1 and 2: tree 11.567 / 11.852; boost 6.838 / 6.667; bag 7.407 / 7.493. **Standardized drift for the tracker (3-seed mean |reproduced − published|): C4.5-alone 2.99 pp, boost 0.85 pp, bag 1.34 pp.**

Labelled sensitivity checks (master seed 0 only, never the verdict):

- (a) paper-faithful routes: AdaBoost.M1-with-resampling boost row **6.239** (0.20 pp closer to the published 5.8 than the library SAMME route); hard-simple-voting bag row **7.692** (−0.03 pp vs soft vote — voting discretion inert here).
- (b) pure-default base tree (gini, min_samples_leaf=1): tree row **12.308** (+0.06 — the single-tree row is mapping-insensitive); bag row **8.405** (+0.68); boost row **11.595** (+5.16 pp — the committee degenerates, same mechanism as audit #9's glass finding: unpruned perfect-fit base trees trigger sklearn's perfect-fit early stop and the boost collapses toward the single tree).
- (c) unstratified KFold(shuffle=True): tree **12.336**, boost **7.066** (+0.63), bag **7.664** (−0.06) — stratification discretion worth ≤ 0.6 pp on this 64/36 two-class data.

## Verdict

**CONFIRMED.** All three rows land within the pre-registered ±4.0 pp at master seed 0 (+3.351 / +0.639 / +1.521), robust across all 3 master seeds (worst case: tree +3.351, boost +1.038, bag +1.521). The paper's ensemble-beats-tree ordering reproduces qualitatively (12.25 → 6.44 / 7.72 vs published 8.9 → 5.8 / 6.2) and boost-beats-bag also reproduces (observation only, not scored — the bar cannot certify orderings, as recorded at pre-registration).

Secondary pre-registered prediction: **HELD.** The C4.5-alone row's 3-seed drift (2.99 pp) exceeds 1.96 pp (the largest score-2 drift in the confirmatory set) — the second score-4+ audit in a row to clear the score-2 ceiling (after audit #11's glass 2.43), though the boost (0.85) and bag (1.34) rows land below it.

## Honesty section

1. **Two-commit caveat (ordering):** this scheduled session had no push credentials, so the pre-registration commit (`d27e56a`, rubric + bars + EMPTY results) exists in the session-local clone BEFORE any reproduction code ran, but both commits land on the remote in the same session batch — the audit #2 precedent, with prereg provably first in the commit graph. The remote-first web-commit discipline of audits #8–#15 could not be followed.
2. The largest drift sits on the PLAIN C4.5 row, not the ensembles: pruned-C4.5-vs-unpruned-CART costs ~3.4 pp on ionosphere, while boosting/bagging wash most of that gap out (0.6–1.5 pp). Default attribution: implementation differences (pessimistic pruning and gain ratio inexpressible in sklearn), not an error in the 1996 table. The published numbers are not challenged; their library-defaults portability is what the drift prices.
3. The CONFIRMED verdict is mapping-conditional for the boost row: sensitivity (b) shows a pure-default base tree degenerates the boost committee (+5.16 pp, would still be inside the ±4.0 bar at 11.595 vs 5.8? — NO: |11.595 − 5.8| = 5.795 pp EXCEEDS the bar). A reproducer taking the naive AdaBoostClassifier-around-default-tree route lands OUTSIDE the bar; the pinned C4.5 mapping (entropy, min_samples_leaf=2) is load-bearing, exactly as in audit #9. The tree and bag rows are robust to the mapping (≤ 0.7 pp).
4. The three (score, drift) points share the paper, dataset, protocol, and CV harness, so they are not independent — same caveat as every prior multi-row audit; cross-audit they share the table and harness with audits #9/#11 (glass/iris) and the dataset with audits #1/#8 lineage (ionosphere).
5. The published numbers are means over the authors' own 100 randomized 1996 runs with an unlogged RNG; our 3 × (10-run mean) band is the closest achievable comparison. One pooled test case = 0.285 pp; rows are printed to one decimal (±0.05 pp rounding), immaterial at this bar.
6. The seed-0 tree row uses 84% of its bar — the verdict does not hinge on seed choice (drift shrinks at seeds 1–2), but it is the closest primary-configuration call since audit #5.
