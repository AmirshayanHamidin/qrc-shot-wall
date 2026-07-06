# PRE-REGISTRATION: Program 2b — Does implementation discretion predict reproducibility drift?

Registered 2026-07-05 (Program 2b run #1), BEFORE any confirmatory audit was selected or run. This document governs all subsequent Program 2b audits and is not edited after registration except for typo fixes flagged as such in commit messages.

## Hypothesis

Across published-ML-claim replication audits, the amount of **implementation discretion** a claim leaves to the reproducing library predicts the absolute **reproducibility drift** of the reproduced number.

**Confirmatory test (pre-registered):** at n ≥ 30 confirmatory audits, Spearman rank correlation between the blind discretion score (0–5, rubric below) and |drift| in percentage points satisfies **rho > 0.5 with p < 0.01** (exact permutation or scipy `spearmanr` two-sided p). The test is run ONCE, when n reaches 30. Verdict is published either way in `RESULTS_DRIFT.md`.

**Exploratory carve-out:** the 5 audits completed before this registration (Fashion-MNIST k-NN, Fashion-MNIST GaussianNB, Fashion-MNIST LogisticRegression, sklearn-docs digits SVC, Breiman-2001 RF ionosphere) generated this hypothesis ("discretion predicts drift", 5/5 informal ladder). They are marked **EXPLORATORY** and are **excluded** from the confirmatory set. They were not scored with the blind rubric and cannot be, since their reproduction numbers are already known. The confirmatory set starts empty at n=0.

## Blind discretion rubric (score BEFORE running any code)

Scored from the original paper plus the modern library's documentation only — never from reproduction output. One point for each of the following left unspecified by the published claim (as it would need to be fixed by the reproducing implementation):

1. **Tie-breaking / randomization** — seeds, RNG streams, bootstrap details, tie handling in ranking/splitting/voting.
2. **Regularization / smoothing defaults** — penalty strengths, variance floors, smoothing constants the library must default.
3. **Initialization** — starting weights/centroids/factor matrices where the algorithm has them.
4. **Stopping criteria / tolerances** — iteration caps, convergence tolerances, early-stopping rules.
5. **Preprocessing assumptions** — scaling, encoding, split construction (stratification, rounding), missing-value handling.

Score is an integer 0–5, with a one-line justification per point. The rubric score and its justifications MUST be committed in the audit file (pre-registration commit, empty results section) before the reproduction numbers exist, per the two-commit rule already in force (RESEARCH_AGENDA.md, Program 2 method rules).

## Standardized drift measure

**|drift| = |reproduced − published| in percentage points, on the paper's own metric**, averaged over **3 seeds** (master seeds 0, 1, 2, identical procedure). Where the paper's metric is a proportion (e.g. accuracy 0.852) it is converted to percentage points. If an audit covers multiple columns/rows, each pre-registered column contributes one (score, |drift|) point, with the rubric scored per column if the discretion profile differs.

## Per-audit order of operations (mandatory)

1. Choose target (published, small-scale, CPU-reproducible, legally public code+data).
2. Score the rubric from paper + library docs and RECORD it in the audit file.
3. Pre-register expected value and tolerance (numeric bar, never moved after data).
4. Commit the audit file with rubric + pre-registration and an EMPTY results section (commit 1).
5. Run (3 seeds), measure drift.
6. Publish results in a separate commit (commit 2) + script + raw JSON, and update the Program 2b tracker in RESEARCH_AGENDA.md, all in the same session batch.

## Target selection policy

Targets are published, small-scale, CPU-reproducible ML claims with legally public code and data (classic papers, UCI/MNIST-scale datasets, well-known repo tables), spread across algorithm families and decades. Selection happens BEFORE rubric scoring; a target is never dropped because of its reproduction result (only for pre-run infrastructure blocks, which are logged as COULD-NOT-RUN or pre-declared switches, as in Program 2 run #3).

## Analysis rules

- Running rho over the accumulating confirmatory set may be reported in RESEARCH_AGENDA.md as **EXPLORATORY** until n=30; no confirmatory language before that.
- At n ≥ 30: compute Spearman rho and p once, publish `RESULTS_DRIFT.md` with the verdict (SUPPORTED if rho > 0.5 and p < 0.01, NOT SUPPORTED otherwise), the full (score, |drift|) table, and an honesty section.
- COULD-NOT-RUN audits contribute no drift point and do not count toward n.
- All six VAR rules (PROTOCOL.md) apply to every audit.

*Program 2b of the VAR initiative — github.com/AmirshayanHamidin/qrc-shot-wall. Registered autonomously; human sign-off gate (VAR rule 6) applies before any external claim.*
