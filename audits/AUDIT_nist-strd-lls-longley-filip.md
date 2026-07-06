# AUDIT: NIST/ITL Statistical Reference Datasets (StRD), Linear Least Squares — certified R-squared, Longley (1967) + Filip

Program 2b confirmatory audit #10 (VAR). Session 2026-07-06 (Program 2b run #9). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

NIST/ITL Statistical Reference Datasets, Linear Least Squares suite (itl.nist.gov/div898/strd/lls/) — **primary source files fetched and read this session**: `Longley.dat` (2987 B, md5 `2061b8f8819c5aae0f43dc87fcf658cf`) and `Filip.dat` (4867 B, md5 `7bfcad7c8559c0baa134373f36c1cfef`). Each file carries the data AND NIST's certified regression statistics for the stated model; per the suite's background page, certified values are quoted to 16 significant digits and accurate up to the last digit (certification methodology documented per dataset). Audited columns — the certified **R-Squared** values, the suite's only proportion-scale statistic (pp conversion sanctioned by PREREG_DRIFT.md):

- **Longley: certified R-Squared 0.995479004577296 = 99.5479004577296 pp.** Model `y = B0 + B1*x1 + ... + B6*x6 + e`, 7 parameters, 16 observations, "Higher" difficulty (multicollinear), Observed data. Original claim lineage: Longley, J. W. (1967), "An Appraisal of Least Squares Programs for the Electronic Computer from the Viewpoint of the User", *JASA* 62, 819–841 — the oldest claim year in this program.
- **Filip: certified R-Squared 0.996727416185620 = 99.6727416185620 pp.** Model `y = B0 + B1*x + B2*(x**2) + ... + B10*(x**10) + e`, 11 parameters, 82 observations, "Higher" difficulty (near-degenerate 10th-degree polynomial design; the suite's classic hard case). Source: Filippelli, A., NIST.

NOT audited, decided now before rubric scoring: the certified coefficient estimates, their standard deviations, residual standard deviations, and F statistics (not proportion-scale; the pre-registered drift measure is pp on a proportion metric); the other LLS datasets (Norris, Pontius, NoInt1/2, Wampler1–5) — Longley is chosen as the classic externally-published claim, Filip as the maximum-difficulty stress case; one audit, two pre-registered columns.

Why this target: the tracker's #1 priority after run #8 is a **true score-0 anchor** — a published claim with zero implementation discretion (the sklearn digits SVC near-zero precedent scored 1). A NIST-certified least-squares statistic is exactly that: data verbatim in the claim file, model equation written out, estimand (the exact least-squares solution) uniquely defined, no RNG, no defaults, no initialization, no stopping rules, no preprocessing. It also opens the **regression family** (unsampled), extends the claim-decade range back to 1967, and is a dataset-documentation/certified-value claim class (wine.names precedent, run #6). Feasibility: 16 and 82 observations — millisecond solves, far under the 45 s cap.

## Data (counting-only checks done before this commit; no reproduction)

`Longley.dat`: data block lines 61–76 = 16 rows (y + 6 predictors), matches the stated 16 observations; certified block lines 31–51. `Filip.dat`: data block lines 61–142 = 82 rows (y, x), matches the stated 82 observations; certified block lines 31–55. Byte counts and md5s above. Both files are US-government works, legally public.

## Blind discretion rubric (scored from the NIST claim files + suite background page + numpy/scipy docs ONLY, before any code)

**Longley column — score 0/5.** **Filip column — score 0/5.** (Identical discretion profiles; justifications apply to both.)

1. Tie-breaking / randomization — **0**. No randomness exists anywhere in the estimand: full-sample closed-form least squares; no splits, no sampling, no folds, no ties, no seeds.
2. Regularization / smoothing defaults — **0**. Plain unpenalized least squares; the certified estimand admits no penalty, shrinkage, or smoothing constant for a library to default.
3. Initialization — **0**. No starting values; the solution is the unique argmin of the residual sum of squares (full-rank design, per the certified ANOVA degrees of freedom).
4. Stopping criteria / tolerances — **0**. None; the certified values define the exact solution, not an iterative approximation with tolerances.
5. Preprocessing assumptions — **0**. The data appear verbatim in the same file as the claim; no scaling, encoding, split construction, or missing-value handling; the intercept is explicit in the stated model equation.

Honest note, recorded at scoring time: floating-point solver algebra (QR vs SVD vs normal equations, and the reproducing machine's arithmetic) remains implementation-private, but it falls under none of the five rubric categories — the rubric measures *statistical* implementation discretion. NIST built these datasets precisely to isolate *numerical* error with all statistical discretion removed, which is what makes them the clean score-0 anchor: any observed drift here is the discretion-free noise floor of the drift measure itself.

## Reproduction plan (pinned before running)

Primary route, both columns, float64 throughout: build the design matrix exactly as the stated model (column of ones + the 6 predictors as given for Longley; column of ones + x**k for k = 1..10 computed directly from the raw x for Filip — no centering, no scaling); solve with `numpy.linalg.lstsq(X, y, rcond=None)`; report R² = 1 − SS_res/SS_tot with SS_res = Σ(y − ŷ)² and SS_tot = Σ(y − ȳ)² (the certified ANOVA convention: model with intercept, total sum corrected for the mean).

Deterministic pipeline: per PREREG_DRIFT.md's 3-seed rule as applied to no-RNG pipelines (run #6 precedent), the identical computation is executed as **3 independent replicate invocations** (replicates 0, 1, 2) and bit-identity of all outputs is checked and reported; the standardized 3-run mean |drift| equals the single-replicate |drift| if bit-identical, and is reported per column in pp.

Labelled sensitivity checks (reported, never the verdict; replicate 0 only): (a) `scipy.linalg.lstsq` (LAPACK gelsd) — cross-library agreement; (b) normal-equations solve `np.linalg.solve(X.T@X, X.T@y)` — the textbook route NIST's background page warns about (condition number squared); expected to be the failure mode if one exists, especially on Filip; (c) Filip refit with centered predictor per NIST's own suggested remedy, R² recomputed on the equivalent model; (d) plug-in cross-check: R² recomputed from NIST's certified coefficients directly (validates the harness independent of any solver). Diagnostic (not a column): max relative error of reproduced coefficients vs the certified B0..Bk per column.

## Pre-registered tolerance and verdict rule

- **Expected values:** 99.5479004577296 pp (Longley), 99.6727416185620 pp (Filip). Expected drift at double precision: < 1e-6 pp for Longley; < 1e-3 pp for Filip (ill-conditioning may cost digits, but R² is insensitive to coefficient error in near-null design directions).
- **Tolerance: ±0.1 pp per column** (primary route, replicate 0). Rationale: continues the discretion-priced ladder downward (score 1 → ±0.5 pp in the digits-SVC precedent; score 2 → ±1.5/±2.0; score 3 → ±3.0; score 4 → ±4.0; score 5 → ±5.0): at score 0 the bar prices ONLY floating-point arithmetic against a 16-significant-digit certified value — no statistical discretion exists to price. This is the tightest bar in the program, set knowingly: if double-precision LAPACK cannot hit a certified regression statistic to 1 part in 1000, that is a reportable discrepancy, not tolerance-worthy drift.
- **CONFIRMED** if BOTH columns satisfy |reproduced − published| ≤ 0.1 pp at replicate 0 in the primary route; **DISCREPANCY** if either exceeds; **COULD-NOT-RUN** if execution is blocked. Bars never move after data.
- Secondary pre-registered prediction (hypothesis-consistent direction): BOTH score-0 3-run drifts land below 0.01 pp — an order of magnitude under every nonzero drift in the confirmatory set — i.e., zero discretion produces drift indistinguishable from numerical noise, anchoring the rank correlation's low end.

## Results

*(Empty at pre-registration commit. Filled by commit 2 in the same session, after the reproduction runs.)*
