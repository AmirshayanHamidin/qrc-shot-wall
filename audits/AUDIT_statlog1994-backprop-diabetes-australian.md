# AUDIT: StatLog (Michie, Spiegelhalter & Taylor 1994) Backprop rows — diabetes + Australian credit

Program 2b confirmatory audit #28 (VAR). Session 2026-07-11 (Program 2b run #28). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

D. Michie, D. J. Spiegelhalter & C. C. Taylor (eds), *Machine Learning, Neural and Statistical Classification*, Ellis Horwood, 1994 — the StatLog project book. **Primary source fetched and read this session** (the book is out of print; copyright reverted to the editors, who placed the full text online at `www1.maths.leeds.ac.uk/~charles/statlog/` — legally public, retrieved via the Internet Archive snapshot of `whole.pdf`, 1 787 416 B, and text-extracted locally).

Two rows, both the **Backprop** (multilayer perceptron) test error rate:

- **Diabetes (Table 9.20, §9.5.2): published test error 0.248** (train 0.198, rank 7 of 23). Protocol stated: *"Twelve–fold cross validation was used to estimate prediction accuracy"*; 768 observations, 8 attributes, 2 classes.
- **Australian credit (Table 9.3, §9.2.2): published test error 0.154** (train 0.087, rank 11 of 22). Protocol stated: 690 observations, 14 attributes, 2 classes, **10-fold cross-validation**; StatLog states it *"replaced the missing values by the overall medians or means (5% of the examples had some missing information)"* and distributed the imputed file.

What the book says about its Backprop implementation (all of it, verbatim in substance): it is an external neural-network software package (§11.5.1) providing "a special purpose 3-layer MLP ... and general MLP with architecture specified at runtime"; and (§7.4) *"cross-validation was used by Backprop in finding the optimal number of nodes in the hidden layer"*. The chosen hidden-node count is **never published for either row**. Learning rate, momentum, weight initialisation, epoch count, stopping rule, and input scaling are **not stated anywhere for either row**.

Why this target: **the score-5 bucket is the program's single thinnest cell — it holds exactly ONE point** (audit #8's Sigillito perceptron, 1.11 pp), and the tracker's standing priority is score-4/5 density. Backprop-in-StatLog is the cleanest genuinely-5/5 claim class available: a published point estimate produced by an unpublished neural-network configuration, on two small CPU-scale public datasets, under a fully-specified resampling protocol. Two rows from one paper give two score-5 points in one audit. New claim class (multi-lab benchmark-consortium table) and new decade anchor (1994) for the set.

NOT audited, decided now before rubric scoring: every other row of both tables (Discrim, Quadisc, Logdisc, CART, k-NN, NaiveBay, ... ) — they are lower-discretion rows and the tracker does not need more score-2/3 points; and RBF/LVQ/Kohonen/DIPOL92/ALLOC80/SMART/CASTLE/ITrule/Cal5/CN2/NewID/Baytree/IndCART/C4.5, which have no scikit-learn default estimator without inventing one (same exclusion rule as audits #7 and #8).

## Data checks (counting only — done BEFORE this commit, no reproduction code run)

- **Diabetes:** OpenML id 37 ARFF, md5 `3cbaa3e54586aa88cf6aacb4033e4470` — **byte-identical to the file audits #19/#24 already pinned** in this repo. 768 rows; 500 `tested_negative` / 268 `tested_positive` — exactly StatLog's stated "500 examples of class 1 and 268 of class 2".
- **Australian credit:** UCI `statlog/australian/australian.dat`, md5 `b6fe154b62a8eb00277acec95b608590`, 28 735 B. 690 rows × 15 columns (14 attributes + class), no missing values (consistent with StatLog's stated median/mean imputation, i.e. this IS the distributed imputed file); class distribution 383 / 307.
- Pre-run arithmetic note (flagged now, not after data): StatLog's "Default" (majority-class) rows are 0.350 for diabetes and 0.440 for Australian, while the whole-file majority-class error rates are 268/768 = **0.349** and 307/690 = **0.445**. Both differ from the published Default in the 3rd decimal, which suggests the book's Default row — like every other row — is a **mean over the CV folds**, not a whole-file figure. This is a consistency check on the datasets, and it corroborates that these are the StatLog files.

## Blind discretion rubric (scored from the book + scikit-learn 1.7 docs ONLY, before any code)

**Both rows — score 5/5.** The rows share one algorithm and one (unpublished) implementation, so the discretion profile is identical; each row still contributes its own (score, |drift|) point per `PREREG_DRIFT.md`.

1. **Tie-breaking / randomization — 1.** No seed is given for anything: not the CV fold assignment (the book states only the number of folds), not the weight-init RNG, not the presentation/shuffle order. sklearn's `MLPClassifier` shuffles each epoch under its own `random_state`, and `KFold` needs a `random_state` to partition.
2. **Regularization / smoothing defaults — 1.** No weight decay, penalty, or early-stopping-as-regularization is stated. The library must default (`alpha=1e-4`).
3. **Initialization — 1.** Starting weights never specified — no distribution, no scheme, and the package's own default is not documented in the book. sklearn defaults to Glorot-style uniform.
4. **Stopping criteria / tolerances — 1.** No epoch count, no tolerance, no learning-rate schedule for either row. The book says training time was one of Backprop's "essentially two free parameters" and was tuned — but the value is never published for these datasets. sklearn defaults (`max_iter=200`, `tol=1e-4`, `n_iter_no_change=10`, `solver='adam'`, `learning_rate_init=1e-3`) must decide.
5. **Preprocessing assumptions — 1.** Input scaling is never stated, and it is the single most consequential unstated choice for an MLP (sklearn's own docs: *"Multi-layer Perceptron is sensitive to feature scaling"*). Additionally: for Australian credit, the integer-coded categorical attributes (A1, A4, A5, A6, A8, A9, A11, A12) are distributed as integers and whether Backprop consumed them raw or one-hot-encoded is unstated; for diabetes, the handling of the biologically-impossible zeros (glucose/pressure/skinfold/insulin/BMI) is unstated.

Discretion axis NOT captured by the frozen 5-point rubric, recorded for honesty: the **hidden-layer size** was CV-tuned by StatLog but never published, so architecture is a sixth free axis here. The rubric is fixed by `PREREG_DRIFT.md` and is NOT extended post hoc; this axis is simply noted, and it means 5/5 is if anything an *under*-count of this target's discretion.

## Reproduction plan (pinned before running)

Per master seed m ∈ {0, 1, 2} (seed 0 primary for the verdict; tracker drift per row = 3-seed mean |reproduced − published|):

1. Load the md5-pinned files above. Diabetes: 8 float features, y = the two class strings. Australian: 14 features as distributed (integer-coded categoricals kept as numeric — the file StatLog itself circulated), y = last column.
2. **Primary configuration — the faithful modern default:** `Pipeline(StandardScaler(), MLPClassifier(random_state=m))`, every other `MLPClassifier` argument left at its library default (`hidden_layer_sizes=(100,)`, `activation='relu'`, `solver='adam'`, `alpha=1e-4`, `learning_rate_init=1e-3`, `max_iter=200`, `shuffle=True`, `tol=1e-4`, `n_iter_no_change=10`). The scaler is fit on the **training fold only** (no leakage). Rationale, pinned now: the rubric permits consulting the library's docs, and scikit-learn's MLP documentation explicitly prescribes standardization — so scaler+defaults, not bare defaults, is the honest "what a competent modern reproducer would run" pipeline. The bare-defaults (unscaled) variant is run as a **labelled sensitivity check**, never as the verdict.
3. **Resampling:** `KFold(n_splits=12, shuffle=True, random_state=m)` for diabetes and `KFold(n_splits=10, shuffle=True, random_state=m)` for Australian — unstratified, because the book states a fold count and nothing else. Row value = 100 × mean over folds of the fold test error rate.
4. Convergence warnings (if `max_iter=200` is hit) are **counted and reported**, not suppressed and not fixed by raising `max_iter` — raising it would be moving a defaulted choice after seeing data.
5. Labelled sensitivity checks (reported, never the verdict): (a) **no scaler** — raw features into `MLPClassifier` defaults; (b) `StratifiedKFold` instead of `KFold`; (c) Australian with the 8 categorical columns **one-hot encoded**; (d) diabetes with the impossible zeros treated as missing and median-imputed (train-fold medians).

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (24.8 pp error for diabetes; 15.4 pp for Australian).
- **Tolerance: ±5.0 pp on both rows** (primary configuration, master seed 0). This is the score-5 bar set by precedent in audit #8 (Sigillito perceptron, also 5/5): bars in this program are priced by the blind rubric score, declared before data, and never moved after.
- **CONFIRMED** if BOTH rows satisfy |reproduced − published| ≤ 5.0 pp at seed 0 in the primary configuration; **DISCREPANCY** if either row exceeds; **COULD-NOT-RUN** if data access or the 45 s sandbox cap blocks execution.
- **Secondary pre-registered prediction A (hypothesis-consistent, direct re-test of the clause that FAILED in audit #8):** both rows' 3-seed drift is **strictly greater than 1.96 pp**, the largest score-2 drift currently in the confirmatory set. Audit #8 — the only prior score-5 point — failed exactly this clause at 1.11 pp. If these two rows also land below 1.96 pp, that is a second and third independent strike against the hypothesis at the high-discretion end, and it will be reported as such.
- **Secondary pre-registered prediction B (mechanism probe):** for BOTH rows, the **unscaled** sensitivity configuration's |drift| is strictly greater than the scaled primary's |drift|. This tests whether rubric point 5 (preprocessing discretion) is a *live* drift driver on this target or an inert checkbox — the rubric counts unspecified choices, but only choices that actually move the number can produce the correlation the program is testing.

Tracker context at registration (n = 27, 61 points, exploratory rho 0.532): score 5 holds **1** point, scores 4–5 together hold 21, score 2 holds 18, score 3 holds 16. These two rows are pre-registered to land at score 5 and will take that bucket from 1 point to 3.

## Results

Data checks reproduced at run time: both md5s as pinned above; diabetes 768 × 8, Australian 690 × 14.

Primary configuration (StandardScaler + `MLPClassifier` defaults, unstratified KFold, master seed 0):

| Row | Published | Reproduced (seed 0) | Drift | Bar |
|---|---|---|---|---|
| Backprop, diabetes (12-fold CV) | 24.8 | **23.047** | **−1.753 pp** | ±5.0 |
| Backprop, Australian credit (10-fold CV) | 15.4 | **13.623** | **−1.777 pp** | ±5.0 |

All three master seeds, primary configuration:

| Row | seed 0 | seed 1 | seed 2 | 3-seed mean \|drift\| |
|---|---|---|---|---|
| diabetes | 23.047 | 22.786 | 22.786 | **1.93 pp** |
| Australian | 13.623 | 13.623 | 13.478 | **1.83 pp** |

**Standardized drift for the tracker: diabetes 1.93 pp, Australian 1.83 pp — both at blind rubric 5/5.**

Both rows drift in the same direction: the 2026 default MLP is **better** than the 1994 published Backprop by ~1.8 pp on both datasets, not worse. Between-fold spread is large relative to the drift (fold-error SD 4.1–6.2 pp on diabetes, 3.9–4.5 pp on Australian), i.e. both drifts are well inside one fold-to-fold standard deviation of the CV estimate itself.

Convergence, reported as pre-registered and NOT fixed: in the primary configuration **every fold hit `max_iter=200` without meeting `tol`** (12/12 diabetes, 10/10 Australian folds, all seeds). Raising `max_iter` would have been moving a defaulted choice after seeing data, so it was not done. The reproduction therefore reproduces the published numbers while formally *not converged* — a point in favour of the drift being insensitive to the stopping choice on these targets.

Labelled sensitivity checks (reported, never the verdict); values are 3-seed mean |drift|:

| Configuration | diabetes | Australian |
|---|---|---|
| **Primary** (scaled, KFold) | **1.93** | **1.83** |
| **Unscaled** (bare library defaults) | **4.89** | **9.72** |
| Stratified folds | 1.28 | 1.87 |
| diabetes: zeros→train-fold median | 0.93 | — |
| Australian: one-hot categoricals (14→42 cols) | — | 0.96 |

The unscaled runs are the story of this audit. Dropping the single preprocessing choice — the one the book never states — moves drift from 1.93 → **4.89 pp** (diabetes) and 1.83 → **9.72 pp** (Australian), a 2.5× and 5.3× increase, and flips the sign (the unscaled MLP is far *worse* than published, not better). Mechanism visible in the raw: unscaled, adam trips `tol` and stops early (27–150 epochs) at a poor optimum; scaled, it uses the full 200-epoch budget. Every other discretion axis tested (fold stratification, one-hot encoding, missing-value imputation) moves the number by ≤ 1 pp.

Secondary pre-registered prediction **A: FAILED on both clauses.** Neither row's 3-seed drift exceeds 1.96 pp (the largest score-2 drift in the set): diabetes **1.93**, Australian **1.83**. The diabetes row misses by 0.03 pp — a margin far smaller than the audit's own fold-to-fold noise, so the honest reading is not "score 5 drifts less than score 2" but "**score-5 drift lands in the same range as the top of the score-2 range**". This is now the second, third and fourth score-5 point (with audit #8's 1.11 pp) to land at or below the score-2 ceiling. Evidence against the hypothesis at the high-discretion end, reported with the same prominence as the confirmations.

Secondary pre-registered prediction **B: HELD on both rows, decisively.** The unscaled configuration out-drifts the scaled primary on both (4.89 > 1.93; 9.72 > 1.83). Rubric point 5 is a *live* drift driver on this target, not an inert checkbox.

A and B holding *together* is the most informative thing this audit produces, and it cuts at the program's own headline: the discretion was real and large (B), yet the measured drift was small (A). The difference is entirely **how the discretion was resolved**. The rubric counts the choices a claim leaves open; |drift| measures what happens when a *competent* reproducer closes them well. A high-discretion claim reproduced carefully drifts little; the same claim reproduced carelessly drifts 5×. See honesty item 2 — this is a confounder for the headline rho, not a footnote.

## Verdict

**CONFIRMED — both rows.** At master seed 0 in the primary configuration, diabetes lands −1.753 pp and Australian −1.777 pp against pre-registered ±5.0 pp bars, robust across all 3 master seeds (worst seed: −2.014 pp diabetes, −1.922 pp Australian). A 1994 multi-lab benchmark table's neural-network rows — produced by an unpublished MLP configuration on a since-vanished software package — reproduce to within ~1.8 pp under 2026 library defaults, with the modern default landing slightly *better* than the original on both datasets.

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3. Reproduction script: `audits/audit_statlog_backprop_run.py` (one `(dataset, config, seed)` triple per invocation; every chunk well inside the 45 s cap). Raw output (all 24 chunks = 2 datasets × 4 configurations × 3 seeds, with per-fold error rates, per-fold epoch counts and convergence counts): `audits/statlog_backprop_raw.json`. Both committed in this session's batch.

## Honesty section

1. **Estimator mapping is the load-bearing assumption.** StatLog's "Backprop" was an unnamed external package's MLP with a CV-tuned hidden-layer size that the book never publishes. `MLPClassifier` defaults (100 relu units, adam) are certainly *not* what ran in 1993 (adam did not exist). This audit therefore measures "does the published number survive a competent modern reproduction attempt", not "is this the same network". That is the honest scope of every cross-implementation audit in this program, and it is at its most stretched here.
2. **The competence confounder (new, and the most important item in this audit).** Secondary B shows one unstated choice can move drift 5×. Secondary A shows the drift we actually recorded is small. Both facts come from the same target. So |drift| as this program measures it is not a function of the claim alone — it is a function of (discretion available) × (how well the reproducer resolves it), and the reproducer here is a careful one that consults the library docs. The rubric scores only the first factor. This plausibly explains why rho keeps sagging at the high-score end (audits #8, #25, and now #28): high-discretion claims are exactly the ones where a careful reproducer's care pays off most. Flagged for the post-n=30 exploratory analysis alongside the floor-headroom confounder; it is NOT used to adjust anything now, and the rubric is NOT amended post hoc.
3. **The 1.96 pp margin.** The diabetes row failed secondary A by 0.03 pp. Had the fold-shuffle RNG landed differently it could have passed. No conclusion in this file rests on which side of 1.96 it fell — it is reported as a fail because that is what was pre-registered, and the substantive claim made is the weaker, robust one (score-5 drift is *in the range of*, not above, score-2 drift).
4. **Architecture is a sixth discretion axis the frozen rubric cannot score** (noted before running, in the rubric section). 5/5 is the ceiling, so this target's true discretion is under-counted — which makes its low drift *more* awkward for the hypothesis, not less.
5. **Non-convergence.** The verdict rests on runs where 100% of folds hit `max_iter` without meeting `tol`. This was pre-registered as report-don't-fix; it is nonetheless a real caveat on the primary configuration.
6. **The two points are not independent** in the usual sense — same algorithm, same (unpublished) implementation, same book, scored with one rubric — though unlike most prior multi-row audits they are at least on two different datasets with different fold counts. Same caveat as every multi-row audit in the set.
7. **Data provenance.** The diabetes file is byte-identical (md5) to the one audits #19/#24 already used, so the *dataset* is not a new source of drift; the Australian file is the StatLog-distributed pre-imputed version, so StatLog's own missing-value handling is inherited rather than re-derived. The book's "Default" rows (0.350 / 0.440) differ in the 3rd decimal from the whole-file majority-class rates (0.349 / 0.445) — flagged before running (data-checks section) and consistent with the book's Default being a fold-mean like every other row.
8. **Execution was delegated** to a subagent (planner/executor split): 24 chunks + one re-run check. Nothing about target choice, rubric scoring, tolerances, or interpretation was delegated. The auditor independently re-ran the two primary seed-0 chunks (reproduced bit-identically: 23.046875, 13.623188), recomputed every drift in the tables above from the raw per-fold rates rather than trusting the subagent's arithmetic, and reproduced the previously-published 61-point rho (0.532) from the printed tracker list before appending the two new points. Any error the subagent made is the auditor's once pushed.
9. **Two-commit ordering:** the pre-registration (rubric, bars, both secondary predictions, tracker context) was committed to the REMOTE at `28213ee` with EMPTY results and verified byte-identical (10 846 B, md5 `0fea4f78…`) by SHA-pinned fetch, BEFORE any reproduction code existed. Uploaded via GitHub's file-upload path rather than the web editor, deliberately: the web editor's auto-indent mangled audit #27's pre-registration and forced a byte-exact re-upload. No editor incident this session.
