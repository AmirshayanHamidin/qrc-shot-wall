# AUDIT: Freund & Schapire (1996) "Experiments with a New Boosting Algorithm" — Table 2, glass rows, C4.5 alone + boosting C4.5

Program 2b confirmatory audit #9 (VAR). Session 2026-07-06 (Program 2b run #8). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

Freund, Y. & Schapire, R. E. (1996), "Experiments with a New Boosting Algorithm", *Machine Learning: Proceedings of the Thirteenth International Conference (ICML 1996)* — **primary source fetched and read this session** (author's copy, cseweb.ucsd.edu/~yfreund/papers/boostingexperiments.pdf, 219704 B). Table 2 "Test error rates of various algorithms on benchmark problems", row `glass`, C4.5 columns (error-based only — the paper used pseudo-loss only for the simpler weak learners on multi-class problems, never with C4.5):

- **C4.5 alone ("–" column): published 31.7** (% test error).
- **boosting C4.5 ("boost" column): published 22.7** (% test error).

Verbatim setup facts from the paper: number of rounds T = 100 for all boosting/bagging runs; glass has no provided test set, so "we used 10-fold cross validation, and averaged the results over 10 runs (for a total of 100 runs of each algorithm on each dataset)"; the weak learner is "Quinlan's C4.5 decision-tree algorithm [18]. We used all the default options with pruning turned on. Since C4.5 expects an unweighted training sample, we used resampling."; boosting with C4.5 is AdaBoost.M1 (error-based; "we did not attempt to use AdaBoost.M2 since C4.5 is designed to minimize error"). Table 1 lists glass as 214 examples, no test set, 7 classes, 9 continuous attributes, no missing values.

Full printed glass row for the record: FindAttrTest 51.5/51.1/50.9, pseudo-loss 29.4/54.2; FindDecRule 49.7/48.5/47.2, pseudo-loss 25.0/52.0; C4.5 **31.7** / boost **22.7** / bag 25.7.

NOT audited, decided now before rubric scoring: the FindAttrTest/FindDecRule columns (the weak learners are the authors' own algorithms with abstain predictions and pseudo-loss variants — no scikit-learn counterpart without inventing one); the bagging column (one new-family point per audit; boosting is the paper's headline claim); other dataset rows (pima is no longer distributable by UCI; most other no-test-set rows have missing values or categorical encodings adding untestable discretion; glass is clean, small, and new to this program).

Why this target: first **boosting-family** point (explicitly unclaimed in the tracker priorities), first multi-class CV target, new dataset (glass), and — per the blind rubric below — the program's first **score-4** points, the exact coverage gap named in the run #7 tracker priorities. Feasibility: 214 instances, millisecond tree fits; the 45 s cap is handled by chunking one master seed per call.

## Data (counting-only checks done before this commit; no reproduction)

Canonical UCI `glass.data` (archive.ics.uci.edu/ml/machine-learning-databases/glass/glass.data), md5 `2732c9170bf8c483f33da3c58929c067`, 214 rows: id column + 9 float features (RI, Na, Mg, Al, Si, K, Ca, Ba, Fe) + class label. Class counts: {1: 70, 2: 76, 3: 17, 5: 13, 6: 9, 7: 29} — 214 total, 6 classes present of the 7-label space, matching Table 1. One duplicate feature-vector pair exists (identical 9 features, same class 1) — so a fully grown tree CAN reach zero training error; this matters for the pre-declared risk below.

## Blind discretion rubric (scored from the paper + scikit-learn 1.7 docs ONLY, before any code)

**C4.5-alone row — score 4/5.**

1. Tie-breaking / randomization — **1**. No seeds anywhere; the 10-run averaging implies randomized fold construction; C4.5's split tie handling and sklearn's feature-tie randomness (`random_state`) are implementation-private.
2. Regularization / smoothing defaults — **1**. The claim's learner is C4.5 "with all the default options with pruning turned on" (pessimistic pruning, confidence 0.25); scikit-learn has no pessimistic-error pruning at all — the library must default every growth/pruning control (ccp_alpha=0.0 = pruning OFF, gain-ratio inexpressible).
3. Initialization — **0**. Trees have none.
4. Stopping criteria / tolerances — **1**. Growth-termination rules for the reproducing tree (max_depth=None, min_samples_split=2, etc.) are left entirely to library defaults (same category reading as audit #6, rubric point 4).
5. Preprocessing assumptions — **1**. The 10-fold CV construction is unspecified (stratified or not, shuffling, fold-size rounding, per-run pooling vs fold-averaging) and must be fixed by the reproducer.

**boosting-C4.5 row — score 4/5.**

1. Tie-breaking / randomization — **1**. All of the above PLUS the resampling bootstrap draws ("we used resampling") and their RNG; no seeds anywhere.
2. Regularization / smoothing defaults — **1**. Same C4.5-pruning gap; the base-tree configuration inside the reproducing booster is entirely library-defaulted (sklearn's AdaBoostClassifier even defaults the base to a depth-1 stump — nothing like C4.5).
3. Initialization — **0**. D_1(i) = 1/m is specified by the paper's AdaBoost.M1 pseudocode (Figure 1).
4. Stopping criteria / tolerances — **1**. T = 100 is specified, but the pseudocode leaves epsilon_t = 0 behavior undefined and prescribes abort at epsilon_t >= 1/2, while sklearn's SAMME documentation prescribes early stop on a perfect weak fit — the effective committee size is implementation-decided.
5. Preprocessing assumptions — **1**. Same CV-construction discretion as the other row.

## Reproduction plan (pinned before running)

Per master seed m in {0, 1, 2} (seed 0 primary for the verdict; drift for the tracker = 3-seed mean |reproduced − published| per row): 10 runs; run r in {0..9} uses `StratifiedKFold(n_splits=10, shuffle=True, random_state=1000*m+r)` (stratification pinned: glass's rarest class has 9 instances, and sklearn's conventional classification CV is stratified); per-run error = pooled misclassified / 214; **row value = 100 × mean over the 10 runs** (the paper's "averaged the results over 10 runs").

- **C4.5-alone row:** `DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fold_seed)`, everything else library default. Mapping rationale (from docs only): entropy is sklearn's information-gain criterion, the closest expressible relative of C4.5's gain ratio; min_samples_leaf=2 is C4.5's documented default -m 2 (Quinlan 1993); C4.5's pessimistic pruning has no sklearn counterpart and is therefore left at the library default (no pruning, ccp_alpha=0.0) — that inexpressibility is rubric point 2, not an amendment.
- **boosting-C4.5 row:** `AdaBoostClassifier(estimator=<the same tree config>, n_estimators=100, random_state=fold_seed)` — scikit-learn 1.7.2's canonical AdaBoost (SAMME, the only remaining algorithm; reweighting-based). This is the faithful modern-default route for "AdaBoost.M1 with C4.5, T=100". Known deviations forced by the library, disclosed now: sklearn reweights while the paper resampled for C4.5; SAMME's vote weight adds log(K-1) relative to M1.
- **Pre-declared risk (before any code):** because an unpruned tree can reach zero training error on glass (duplicate check above), sklearn's documented perfect-fit early stop may collapse the boosted ensemble to a single tree, in which case the boost row would land near the tree row (~9 pp from the published 22.7). If that happens it is the RESULT of the modern-default route and will be reported as measured — the bar below is set with this risk known and accepted.
- Labelled sensitivity checks (reported, never the verdict; master seed 0 only): (a) paper-faithful AdaBoost.M1 **with resampling** (hand implementation of Figure 1: bootstrap from D_t, fit unweighted, epsilon_t on the weighted original set, beta_t = eps/(1-eps), log(1/beta) voting; stop and vote with the committee so far if epsilon_t = 0 or >= 1/2, beta floored at 1e-10); (b) pure-default base tree (gini, min_samples_leaf=1) for both rows; (c) unstratified `KFold(shuffle=True)`; (d) diagnostic: sklearn's fitted committee sizes (`len(estimators_)`) reported per fold.

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (31.7 for C4.5 alone; 22.7 for boosting C4.5). One pooled test case = 1/214 = 0.467 pp.
- **Tolerance: ±4.0 pp per row** (primary configuration, master seed 0). Rationale: continues the discretion-priced ladder (score 3 → ±3.0 in audit #6, score 5 → ±5.0 in audits #2/#8) at the rubric's 4/5; prices a 30-year C4.5→CART-family implementation gap on a 214-instance multi-class dataset plus the disclosed degeneration risk, while staying below the 9 pp published boost-vs-tree gap (the bar cannot be satisfied by the boost row merely reproducing the tree row).
- **CONFIRMED** if BOTH rows satisfy |reproduced − published| ≤ 4.0 pp at seed 0 in the primary configuration; **DISCREPANCY** if either row exceeds; **COULD-NOT-RUN** if data access or the 45 s cap blocks execution. Bars never move after data.
- Secondary pre-registered prediction (hypothesis-consistent direction): at rubric 4/5, at least one row's 3-seed drift EXCEEDS 1.96 pp (the largest score-2 drift in the confirmatory set).

## Results

Data check: `glass.data` md5 `2732c9170bf8c483f33da3c58929c067`, 214 rows, class counts {1: 70, 2: 76, 3: 17, 5: 13, 6: 9, 7: 29} — identical to the pre-commit counting check.

Primary configurations (pinned mapping, master seed 0; 10 runs × stratified 10-fold CV, pooled per-run error, mean over runs):

| Row | Published | Reproduced | Drift |
|---|---|---|---|
| C4.5 alone | 31.7 | **31.682** | −0.018 pp |
| boosting C4.5 (T=100) | 22.7 | **20.981** | −1.719 pp |

Master seeds 1 and 2: tree 31.776 / 32.290; boost 21.682 / 21.355. **Standardized drift for the tracker (3-seed mean |reproduced − published|): C4.5-alone 0.23 pp, boosting-C4.5 1.36 pp.** The paper's headline ordering reproduces: boosting improves on the single tree at every seed (published improvement 9.0 pp; reproduced 10.7 / 10.1 / 10.9 pp).

Committee diagnostic (pre-declared risk): the degeneration did NOT occur in the primary configuration — every one of the 300 AdaBoost fits (3 seeds × 100 folds) used all 100 estimators (first-round weighted error > 0 in every fold, because min_samples_leaf=2 leaves impure leaves on glass's overlapping classes).

Labelled sensitivity checks (master seed 0, never the verdict):

- (a) Paper-faithful AdaBoost.M1 **with resampling** (hand implementation of Figure 1): 20.93 — within 0.05 pp of sklearn's SAMME-with-reweighting 20.98; all 100 rounds used in every fold. The M1-vs-SAMME + resampling-vs-reweighting discretion is numerically inert here.
- (b) Pure-default base tree (gini, min_samples_leaf=1): tree row 31.45 (still within 0.3 pp of published) — but the boost row **DEGENERATES exactly as pre-declared**: the unpruned default tree reaches zero training error, sklearn's perfect-fit early stop collapses every committee to n_est = 1, and the "boosted" error is 32.01, i.e. the single-tree number, 9.31 pp from the published 22.7 and OUTSIDE the ±4.0 bar. The C4.5-default mapping (-m 2 → min_samples_leaf=2), pinned before any code ran, is load-bearing for the entire boost row.
- (c) Unstratified KFold(shuffle=True): tree 31.78, boost 22.15 — the CV-construction discretion is worth ≤ 0.6 pp.

Secondary pre-registered prediction: **FAILED.** Neither row's 3-seed drift (0.23 / 1.36 pp) exceeds 1.96 pp (the largest score-2 drift in the set). The first two score-4 points land below the score-2 ceiling — the third consecutive mid/high-score target to do so.

## Verdict

**CONFIRMED.** Both rows land within the pre-registered ±4.0 pp at master seed 0 in the primary configuration (−0.018 pp and −1.719 pp), robust across all 3 master seeds (worst case: tree +0.59, boost −1.72). A 1996 boosting table reproduces under a 2026 library: the single-tree row is within one pooled test case of the published number, and AdaBoost.M1's 9-point improvement over C4.5 reproduces as a 10–11-point improvement over the mapped CART.

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3. Reproduction script: `audits/audit_fs96_boost_glass_run.py` (chunked one master seed per invocation for the 45 s per-process cap). Raw output (per-run errors, per-fold committee sizes, all sensitivity configurations): `audits/fs96_boost_glass_raw.json` (md5 `98360db6c35c846a17db902f62b7d2e3`). Both committed in this session's batch.

## Honesty section

1. The CONFIRMED verdict is conditional on the pinned estimator mapping. Sensitivity (b) shows that the most naive library-default route (AdaBoost around sklearn's default tree) collapses to a single tree and lands 9.31 pp out — OUTSIDE the bar. The mapping that saves the row (criterion='entropy', min_samples_leaf=2 = C4.5's documented -m 2 default) was pinned in the pre-registration commit (`c364bac`) before any reproduction code existed, so this is not a post-hoc rescue — but a reproducer who chose differently would have published a DISCREPANCY. That ~9 pp mapping sensitivity IS the discretion this audit set out to measure, and it is the largest single-choice effect observed in the confirmatory set so far.
2. C4.5's gain ratio and pessimistic pruning (confidence 0.25) remain inexpressible in scikit-learn; the reproduction is unpruned information-gain CART. That this residual gap costs only ~0.2 pp (tree row) / ~1.7 pp (boost row) is the audit's finding, not an assumption.
3. The paper's boosting route for C4.5 (AdaBoost.M1 with resampling) differs from sklearn's (SAMME with reweighting); the hand-implemented paper route agrees with sklearn to 0.05 pp (sensitivity a), so this discretion is inert here despite being real.
4. The paper's own protocol has residual ambiguity (stratification, per-run pooling, fold rounding); the pinned reading was fixed before running and sensitivity (c) bounds its effect at ~0.6 pp.
5. The two (score, drift) points share one dataset and one CV harness, so they are not independent — same caveat as every prior multi-row audit.
6. Two-commit ordering: pre-registration was committed to the REMOTE (`c364bac`, verified byte-identical at 9516 B by SHA-pinned fetch) before any reproduction code existed; results were computed afterwards in this same session. The commit dialog had no Copilot autofill this session (checked in the DOM before submitting).
7. The published numbers are means over the authors' own 100 randomized runs with an unlogged 1996 RNG; our 3 × (10-run mean) band (tree 31.68–32.29, boost 20.98–21.68) is the closest achievable comparison, and the boost row's entire 3-seed band sits ~1–1.7 pp BELOW the published value (modern boosted trees slightly better than 1996 boosted C4.5 on this dataset), direction consistent with the unpruned-base difference.
8. The secondary prediction's failure is reported with the same prominence as the confirmation: at rubric 4/5 the hypothesis expects drift above the score-2 ceiling (1.96 pp) and got 0.23 / 1.36 pp. The mid/high rubric range (scores 3–5) has now produced six of seven points below that ceiling — the exploratory rho (0.625 over 17 points) is weakening as coverage improves, exactly what an honest confirmatory design is for.
