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

Data check: `Longley.dat` md5 `2061b8f8819c5aae0f43dc87fcf658cf` (16 rows parsed), `Filip.dat` md5 `7bfcad7c8559c0baa134373f36c1cfef` (82 rows parsed) — identical to the pre-commit checks.

Primary route (`numpy.linalg.lstsq`, rcond=None, float64, raw design matrices as pinned), replicate 0; all three replicate invocations **bit-identical** on every reported number (JSON equality excluding the replicate id), so the 3-run mean |drift| equals the single-run |drift|:

| Column | Published (certified R², pp) | Reproduced (pp) | Drift | Bar |
|---|---|---|---|---|
| Longley | 99.5479004577296 | **99.54790045772953** | −7.1e-14 pp | ±0.1 pp — PASS |
| Filip | 99.6727416185620 | **99.55957626651001** | **−0.1132 pp** | ±0.1 pp — **FAIL** |

**Standardized drift for the tracker (3-run, bit-identical): Longley 0.00 pp, Filip 0.11 pp.**

Diagnostics (primary route): Longley max relative coefficient error vs certified 1.2e-11 (all 7 coefficients ~11 digits correct). Filip max relative coefficient error **1.07** — the returned coefficient vector is not the certified solution at all: `rcond=None` sets the SVD cutoff at machine-eps × max(M,N), and Filip's raw Vandermonde design (condition number ~1e15) has trailing singular values below that cutoff, so numpy silently rank-truncates and returns a minimum-norm solution of a *reduced-rank* problem. The fit loses 0.113 pp of R² — the exact NIST failure mode ("Higher difficulty" = near-degenerate design), triggered not by arithmetic but by the library's default truncation *policy*.

Labelled sensitivity checks (replicate 0, never the verdict):

- (a) `scipy.linalg.lstsq` (LAPACK gelsd): Longley identical to numpy (1.2e-11 coef err); **Filip R² 99.67099772 pp, drift −0.0176 pp — INSIDE the bar**, max coef err 8.7e-7. The two libraries' "default SVD least squares" differ only in truncation policy, and that single policy choice is worth 0.096 pp on Filip — larger than every statistical-discretion effect measured in audits #6 and #9's CV-construction checks.
- (b) Normal equations: Longley R² correct to 12 digits (coef err 4.2e-8 — modern LAPACK survives the classic Longley trap at double precision); Filip R² 99.56525 pp (coef err 1.07) — degenerate, as NIST's background page predicts.
- (c) Filip centered-predictor refit (NIST's own suggested remedy): **R² 99.67274161856202 pp — matches the certified value to 13 significant digits** (drift +2e-11 pp). The certified claim is fully recoverable in float64 once the design is centered.
- (d) Plug-in of NIST's certified coefficients into the harness: Longley 99.54790045772941 pp, Filip 99.67274161524213 pp — harness validated independently of any solver (Filip's plug-in loses ~3e-9 pp to evaluating the certified polynomial in ill-conditioned raw-power basis, itself a display of the conditioning).

Secondary pre-registered prediction: **FAILED.** Longley's drift (7e-14 pp) is below 0.01 pp as predicted, but Filip's (0.1132 pp) is not — and it ranks ABOVE three executed score-2 drifts (0.02, 0.04, 0.05 pp). Zero statistical discretion did not produce uniformly negligible drift; the drift measure's noise floor is solver-policy-dependent.

## Verdict

**DISCREPANCY.** The pre-registered rule requires BOTH columns within ±0.1 pp on the primary route; Filip lands at −0.1132 pp, 13% outside the bar (Longley passes at machine precision). Per VAR rule 1 the bar is not moved after data, and per the program's default the gap is attributed to environment/implementation, not to NIST: the certified value is demonstrably correct and float64-recoverable (sensitivities (a) and (c)); what failed is the *pinned primary route* — numpy's `rcond=None` truncation policy on a condition-1e15 design. The audit's own expectation ("< 1e-3 pp for Filip") was wrong by two orders of magnitude, and that misprediction is the finding: at rubric score 0, drift is bounded below not by zero but by the reproducing stack's numerical policy defaults.

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, numpy 2.2.6, scipy 1.15.3. Reproduction script: `audits/audit_nist_lls_run.py` (3 replicate invocations, seconds each — no 45 s chunking needed). Raw output (all 3 replicates, all sensitivity routes, data md5s): `audits/nist_lls_raw.json` (md5 `ce4b9e092020f09d15b5492471dbee83`). Both committed in this session's batch.

## Honesty section

1. This DISCREPANCY is a verdict about the pinned reproduction route, not about NIST's numbers. Sensitivity (c) reproduces the certified Filip R² to 13 digits; NIST's claim is exactly right. A reproducer choosing scipy's gelsd (or centering, as NIST's background page advises) would have published CONFIRMED. The 0.096 pp numpy-vs-scipy gap on an identical estimand is the audit's sharpest finding: **even at zero statistical discretion, library policy defaults inject measurable drift.**
2. The primary-route choice (numpy over scipy) was pinned in the prereg commit (`4ad15b8`) before any code ran; it was not selected to produce either verdict. Had scipy been pinned instead, the verdict would be CONFIRMED — the fragility of that coin-flip at a ±0.1 pp bar is itself evidence about reproduction noise floors, and both routes are published side by side above.
3. The rubric scored 0/5 by design: solver numerics fall under none of the five discretion categories (recorded at scoring time, before results). Filip's 0.11 pp point therefore enters the tracker as (0, 0.11), where it WEAKENS the hypothesis (it out-drifts three score-2 points) — reported with the same prominence as any supporting point. The Longley (0, 0.00) point anchors the low end as hoped.
4. The ±0.1 pp bar is the tightest in the program and was set knowingly (a 16-significant-digit certified target leaves no discretion to price). Under any earlier audit's bar (±0.5 pp or wider) both columns would have passed; the DISCREPANCY is meaningful only at the precision this claim class enables — which is exactly why the claim class was chosen.
5. The two (score, drift) points share a claim source (NIST StRD) and a harness but use disjoint datasets, models, and even failure modes; they are less coupled than any prior multi-row audit's points, but not fully independent.
6. Two-commit ordering: pre-registration was committed to the REMOTE (`4ad15b8`, verified byte-identical at 8388 B by SHA-pinned raw fetch) before any reproduction code existed; results were computed afterwards in this same session. Commit-form description was empty and DOM-verified before submission (no Copilot autofill this session). One mechanical incident, disclosed: the first commit-1 submission attempt did not register (submit fired before GitHub finished processing the uploaded file); the flow was redone and the second attempt landed — no repository state was affected by the failed attempt.
7. The certified values are NIST's own multi-precision computations, not an independent third party's; per the suite's documentation they are accurate to the last quoted digit. The audit treats them as the published claim, the same status given to every prior target's printed table.
8. Secondary-prediction failure is reported above with full prominence: this is the fourth consecutive audit whose hypothesis-consistent secondary clause failed, and the first where a score-0 point out-drifts score-2 points.
