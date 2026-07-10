# AUDIT: Freund & Schapire (1996) "Experiments with a New Boosting Algorithm" — Table 2, vehicle row, C4.5 alone + boosting C4.5 + bagging C4.5

Program 2b confirmatory audit #23 (VAR). Session 2026-07-10 (Program 2b run #21, scheduled). Two-commit rule: this file is committed with an EMPTY results section BEFORE any reproduction code runs. Governed by `audits/PREREG_DRIFT.md`. This is the tracker's named candidate class from run #20 ("further score-4/5 density via the remaining FS96 Table 2 rows (vehicle / segmentation etc.)").

## Claim under audit

Freund, Y. & Schapire, R. E. (1996), "Experiments with a New Boosting Algorithm", *Machine Learning: Proceedings of the Thirteenth International Conference (ICML 1996)* — primary source re-fetched and re-read this session (author's copy, cseweb.ucsd.edu/~yfreund/papers/boostingexperiments.pdf; fetched through the session's text-extraction pipeline, so the byte-level md5 recorded by audits #9/#11/#16 (`cdbaa305c6cf034dea09bb268e4a5ce2`) could not be re-asserted this time — the Table 2 vehicle transcript below was read directly from this session's extracted text). Table 2 "Test error rates of various algorithms on benchmark problems", row `vehicle`, the three C4.5 columns:

- **C4.5 alone ("–" column): published 29.9** (% test error).
- **boosting C4.5 ("boost" column): published 22.6** (% test error).
- **bagging C4.5 ("bag" column): published 26.1** (% test error).

Full printed vehicle row for the record: FindAttrTest 64.3 / 64.4 / 57.6, pseudo-loss 26.1 / 56.1; FindDecRule 61.3 / 61.2 / 61.0, pseudo-loss 25.0 / 54.3; C4.5 **29.9** / boost **22.6** / bag **26.1**.

Verbatim setup facts from the paper (identical protocol class to audits #9, #11, #16 and #17): T = 100 rounds for all boosting/bagging runs; vehicle has no provided test set (Table 1: 846 examples, no test set, 4 classes, 18 continuous attributes, no missing values), so "we used 10-fold cross validation, and averaged the results over 10 runs (for a total of 100 runs of each algorithm on each dataset)"; the weak learner is "Quinlan's C4.5 decision-tree algorithm [18]. We used all the default options with pruning turned on. Since C4.5 expects an unweighted training sample, we used resampling."; boosting with C4.5 is error-based AdaBoost.M1 even on multiclass problems ("we did not attempt to use AdaBoost.M2 since C4.5 is designed to minimize error, not pseudo-loss"); bagging trains each copy on a bootstrap sample of size N combined by simple voting, always with resampling.

NOT audited, decided now before rubric scoring: FindAttrTest/FindDecRule columns (authors' own weak learners, no sklearn counterpart — standing exclusion from audits #9/#11/#16/#17); other dataset rows.

Why this target: **the run #20 tracker names this candidate class explicitly** — three more score-4 points at the program's #1 density priority (12 points at scores 4–5 vs 18 at score 2 as of n=21). Vehicle is the next clean no-test-set FS96 row (all-continuous, no missing values), extending the discretion-constant, same-paper contrast of audits #16 (ionosphere, CONFIRMED 3/3) and #17 (sonar, first score-4 DISCREPANCY) to a THIRD dataset — and the first mid-size 4-class dataset in the FS96 C4.5 ladder (glass, audits #9/#11, is the only other multiclass point). Cross-audit interest: audit #17's DISCREPANCY was on the bag column (candidate mechanism: bagging modern unpruned trees behaves like a proto-random-forest, far below 1996 bagged pruned C4.5); vehicle's published bag gain is small (29.9 → 26.1), so this audit tests whether that mechanism repeats where the published bagging improvement was modest and the task is multiclass.

## Data (counting-only checks done before this commit; no reproduction)

OpenML data_id=54 (Statlog vehicle silhouettes), fetched fresh this session: shape (846, 18), class counts {van: 199, saab: 217, bus: 218, opel: 212}, no missing values, X md5 `cfcd8d8b777b3dada6fcb4d2f4620951` — matches Table 1 exactly (846 examples, 4 classes, 18 continuous, no missing). Environment: python 3.x, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3 — the same triple as audits #9/#11/#16/#17 (exact versions re-asserted in the runner's JSON).

## Blind discretion rubric (scored from the paper + scikit-learn 1.7 docs ONLY, before any code)

Discretion profiles are identical to the corresponding columns of audits #9, #11, #16 and #17 (same paper, same protocol class, all-continuous no-missing dataset); justifications restated per column.

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
4. Stopping criteria / tolerances — **1**. T = 100 is specified, but the pseudocode leaves epsilon_t = 0 behavior undefined and prescribes abort at epsilon_t >= 1/2, while sklearn's SAMME documentation prescribes early stop on a perfect weak fit — the effective committee size is implementation-decided (on a 4-class problem the epsilon_t >= 1/2 abort is additionally live in the M1 pseudocode but not in sklearn's multiclass SAMME).
5. Preprocessing assumptions — **1**. Same CV-construction discretion.

**bagging-C4.5 row — score 4/5.**

1. Tie-breaking / randomization — **1**. Bootstrap draws and their RNG, fold construction, tie handling — no seeds anywhere.
2. Regularization / smoothing defaults — **1**. Same C4.5-pruning gap inside every committee member.
3. Initialization — **0**. Trees have none.
4. Stopping criteria / tolerances — **1**. T = 100 specified and bagging has no early-stop discretion, but the base tree's growth-termination rules are library-defaulted.
5. Preprocessing assumptions — **1**. Same CV-construction discretion; soft (probability-averaging) vs the paper's "simple voting" is additionally library-decided (sklearn BaggingClassifier default: soft where available).

## Reproduction plan (pinned before running)

Per master seed m in {0, 1, 2} (seed 0 primary for the verdict; drift for the tracker = 3-seed mean |reproduced − published| per row): 10 runs; run r uses `StratifiedKFold(n_splits=10, shuffle=True, random_state=1000*m+r)` — identical CV pinning to audits #9/#11/#16/#17 for cross-audit comparability; per-run error = pooled misclassified / 846; **row value = 100 × mean over the 10 runs**. Per-fold estimator seed fs = 100000*m + 100*r + k (k = fold index), identical to audits #9/#11/#16/#17.

- **Base tree (all rows):** `DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fs)`, everything else library default — the audits #9/#11/#16/#17 pinned C4.5 mapping (entropy = closest expressible relative of gain ratio; min_samples_leaf=2 = C4.5's documented -m 2 default; C4.5's pessimistic pruning has no sklearn counterpart and stays at the library default, no pruning — that inexpressibility is rubric point 2, not an amendment).
- **C4.5-alone row:** the base tree fit per fold.
- **boost row:** `AdaBoostClassifier(estimator=<base tree>, n_estimators=100, random_state=fs)`, all else library default (SAMME reweighting route) — identical to audits #9/#16/#17.
- **bag row:** `BaggingClassifier(estimator=<base tree>, n_estimators=100, random_state=fs)`, all else library default (bootstrap n=N, soft vote) — identical to audits #11/#16/#17.
- Labelled sensitivity checks (reported, never the verdict; master seed 0 only): (a) paper-faithful AdaBoost.M1 with resampling for the boost row (audit #9's sens route) and hard simple voting for the bag row (audit #11's sens route); (b) pure-default base tree (gini, min_samples_leaf=1) for all three rows; (c) unstratified `KFold(shuffle=True)` for all three rows.

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (29.9 / 22.6 / 26.1 % error).
- **Tolerance: ±4.0 pp per row** (primary configuration, master seed 0) — the discretion-priced ladder at rubric 4/5, identical to the audits #9/#11/#16/#17 score-4 bar. Note recorded now: the published C4.5-vs-boost gap here is 7.3 pp (larger than the bar), but the C4.5-vs-bag gap is 3.8 pp and the boost-vs-bag gap 3.5 pp, both SMALLER than the bar — so unlike audit #17's sonar, in-bar results here would NOT automatically preserve the paper's orderings involving bagging. Orderings are reported as observations only, never scored.
- **CONFIRMED** if ALL THREE rows satisfy |reproduced − published| <= 4.0 pp at seed 0 in the primary configuration; **DISCREPANCY** if any row exceeds; **COULD-NOT-RUN** if data access or the 45 s cap blocks execution. Bars never move after data.
- Secondary pre-registered prediction (hypothesis-consistent direction): at least one of the three rows' 3-seed drifts EXCEEDS 1.96 pp (the largest score-2 drift in the confirmatory set). Recorded context: this prediction has held in 3 of 10 prior score>=3 audits' first tests (audit #11 glass, audit #16 tree row, audit #17 tree and bag rows).

## Results

Data check (re-asserted inside every runner invocation): OpenML data_id=54, X md5 `cfcd8d8b777b3dada6fcb4d2f4620951`, 846 rows, {van: 199, saab: 217, bus: 218, opel: 212} — identical to the pre-commit counting checks. Environment: scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3, CPU only. Execution note: chunked (route × master-seed × run-subset) invocations under the 45 s cap; this session used the planner/executor split — chunk execution was delegated to a subagent running the committed script verbatim, and all 54 part files were re-aggregated, completeness-checked and duplicate-checked by the planning instance before this commit (per-run cells in `audits/fs96_vehicle_raw.json`).

Primary configurations (library defaults per the pinned plan, master seed 0):

| Row | Published | Reproduced | Drift |
|---|---|---|---|
| C4.5 alone | 29.9 | **27.258** | −2.642 pp |
| boosting C4.5 | 22.6 | **23.274** | +0.674 pp |
| bagging C4.5 | 26.1 | **25.449** | −0.651 pp |

Seeds 1 / 2 (row values): tree 27.352 / 27.258; boost 23.369 / 23.783; bag 25.095 / 25.650. **Program 2b standardized drift (3-seed mean |reproduced − published|): tree 2.61 pp, boost 0.88 pp, bag 0.70 pp.**

**VERDICT: CONFIRMED.** All three rows land inside the pre-registered ±4.0 pp bar at seed 0 (and on all three master seeds). The paper's full ordering tree > bag > boost reproduces (27.26 > 25.45 > 23.27 vs published 29.9 > 26.1 > 22.6) — reported as an observation only, per the pre-registration note that in-bar results did not guarantee it.

Secondary pre-registered prediction: **HELD** — the tree row's 3-seed drift (2.61 pp) exceeds the 1.96 pp score-2 ceiling (boost 0.88 and bag 0.70 do not).

Labelled sensitivity checks (master seed 0, 10 runs each; reported, never the verdict):

| Route | tree | boost | bag |
|---|---|---|---|
| primary (pinned mapping) | 27.258 | 23.274 | 25.449 |
| (a) paper-faithful: M1-resample boost / hard-vote bag | — | 22.116 | 25.142 |
| (b) pure-default base tree (gini, leaf=1) | 29.019 | 29.291 | 25.142 |
| (c) unstratified KFold | 27.317 | 24.054 | 24.917 |

## Honesty section

1. **The audit #17 bag mechanism did NOT repeat here.** On sonar, bagging modern unpruned trees landed 6.6 pp below the published value (the proto-random-forest reading); on vehicle the same pinned route lands 0.65 pp below published, comfortably in-bar. Consistent reading: vehicle's published bag gain was modest (29.9 → 26.1) and modern bagging delivers a similarly modest gain (27.26 → 25.45), whereas on sonar the 1996 committee under-performed what modern bagged trees achieve on that dataset. One audit cannot separate dataset-specific from protocol-specific explanations — recorded as an open contrast, not a conclusion.
2. The pure-default-base-tree boosting degeneration replicates on a FOURTH dataset (29.291, +6.69 pp vs published, where the pinned mapping gives an in-bar 23.274) — the audits #9/#16/#17 mechanism again; the naive route would flip the boost row's verdict. Bagging is again far less sensitive to the same choice (0.3 pp from the primary route) — audit #11's insulation finding, third replication.
3. The paper-faithful M1-resample boost route (22.116) lands closer to the published 22.6 than the primary sklearn SAMME route (23.274) — color for the "discretion TYPE" question raised at audit #20, but a sensitivity only, never scored. Caveat: this script's M1-resample convention (per-fold RandomState seeded fs; per-round tree seed fs*1000+t) was fixed in the pre-registered plan's spirit but implemented fresh this session; audit #9's M1 code was not re-executed, so cross-audit M1 comparability is approximate.
4. The hard-vote bag sensitivity and the default-tree bag sensitivity coincidentally aggregate to the same 2-dp value (25.142 = 2127 pooled errors each over 10 runs); their per-run error counts differ (verified in the raw JSON) — noted so the coincidence is not misread as a copy-paste error. Hard-vote ties break toward the first class in sorted order (`bus`); ties are possible with 100 voters on 4 classes but rare.
5. The tree row is in-bar on all seeds but carries the largest drift (2.61 pp) — the single-tree row is the most drift-prone C4.5 column in all three FS96 dataset audits (ionosphere 2.99, sonar 3.36, vehicle 2.61), consistent with the C4.5-pruning inexpressibility (rubric point 2) acting mainly on the unaggregated tree.
6. Primary-source caveat: the paper PDF was re-fetched this session through a text-extraction pipeline, so its byte-level md5 could not be re-asserted (audits #9/#11/#16 recorded `cdbaa305c6cf034dea09bb268e4a5ce2`); the Table 2 vehicle row was transcribed directly from this session's extracted text.
7. Two-commit rule: the pre-registration commit (`aa18d35`) was web-committed and verified byte-identical to the local file (md5 `06cf76ac2da871d449327ea93902787a`, 10354 bytes remote = local exactly, no trailing-newline delta this time) BEFORE any reproduction code existed in this session. Disclosed: GitHub's commit-message autofill prepended "Add audit for Freund & Schapire" to the intended prereg message — cosmetic only; the committed bytes are governed by the md5 verification.
8. Planner/executor split (fourth audit under the program's efficiency rule): target choice, rubric, pre-registration, aggregation, verdict and this section are the planning instance's; the subagent only executed the committed script in pinned chunks (54 part files, no errors, no retries). Their errors would be ours once pushed — hence the independent re-aggregation and the per-run duplicate check before this commit.
