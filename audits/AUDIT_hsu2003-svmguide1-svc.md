# AUDIT: Hsu, Chang & Lin — "A Practical Guide to Support Vector Classification", Appendix A.1 (svmguide1)

Program 2b (VAR) replication audit — **confirmatory audit #3 (n=3 toward 30)** under `audits/PREREG_DRIFT.md`. Session 2026-07-05 (late). Two-commit rule: this file is committed with rubric + pre-registration and EMPTY results sections BEFORE any experiment runs; results land in a separate later commit.

## Claim under audit

C.-W. Hsu, C.-C. Chang & C.-J. Lin, "A Practical Guide to Support Vector Classification" (first version 2003; current revision fetched this session from https://www.csie.ntu.edu.tw/~cjlin/papers/guide/guide.pdf). Appendix A.1 "Astroparticle Physics", dataset `svmguide1` (3,089 train / 4,000 test / 4 features / 2 classes, per Table 1 of the guide). Three printed accuracy numbers, each produced by an exact LIBSVM command sequence printed in the guide:

- **A — original sets, default parameters** (`svm-train svmguide1`; `svm-predict`): published **66.925%** (2677/4000)
- **B — scaled sets, default parameters** (`svm-scale -l -1 -u 1 -s range1` on train, `-r range1` on test, then train/predict): published **96.15%** (3846/4000)
- **C — scaled sets, C=2, γ=2** (`svm-train -c 2 -g 2 svmguide1.scale`; predict on scaled test): published **96.875%** (3875/4000)

This is one of the most-cited SVM how-to documents in ML; rows A/B are the canonical "scaling matters" demonstration. New algorithm family for the confirmatory set (kernel SVM) and a deliberately LOW-discretion target per the tracker's coverage note (previous confirmatory scores: {2, 3}).

## Blind discretion rubric (PREREG_DRIFT.md; scored from the guide + scikit-learn SVC docs BEFORE any code ran)

Scored per column because the discretion profile differs (C fixes the hyperparameters that A/B inherit from defaults).

| # | Item | A / B | C | Justification (one line) |
|---|---|---|---|---|
| 1 | Tie-breaking / randomization | 0 | 0 | Deterministic dual solver, fixed published train/test files; nothing random anywhere in the pipeline. |
| 2 | Regularization / smoothing defaults | **1** | 0 | A/B never print C or γ — they inherit the tool's defaults (LIBSVM: C=1, γ=1/num_features), and the modern library's default differs (sklearn `gamma='scale'` vs 1/k), so the reproducer must actively choose the mapping. C pins C=2, γ=2 in the command itself. |
| 3 | Initialization | 0 | 0 | SVM dual QP exposes no initialization choice. |
| 4 | Stopping criteria / tolerances | **1** | **1** | Solver tolerance, shrinking heuristic and cache size appear nowhere in the claim; the reproducing library must default them (sklearn: tol=1e-3, shrinking=True). |
| 5 | Preprocessing assumptions | 0 | 0 | Fully specified: A is raw; B/C scale to [−1,1] with ranges computed on train and applied to test (`-s range1` / `-r range1`), split provided as files. |

**Discretion scores: A = 2/5, B = 2/5, C = 1/5.** Recorded here before any reproduction code ran, per PREREG_DRIFT.md order of operations. C is the lowest-discretion confirmatory point so far.

## Data

`svmguide1` (train) and `svmguide1.t` (test) fetched pre-registration (cache-busted) from the LIBSVM datasets page (https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/): 3,089 / 4,000 lines — matches Table 1. MD5: train `894768696209cc3a81c2dcd5589ac67a`, test `1e1942c9361598fee3ed1d540e4f627a`. Parsed shapes and class counts will be logged in Results. No reproduction code has touched the data at pre-registration time.

## Reproduction plan (pinned before running)

scikit-learn `SVC(kernel='rbf')`, which wraps LIBSVM itself — so this audit prices *same engine, different wrapper + default-mapping* drift, exactly the low-discretion anchor the confirmatory set lacks. Declared choices resolving the rubric points: γ mapped to LIBSVM's documented default via `gamma='auto'` (= 1/num_features = 0.25), C=1.0 (A/B); `tol=1e-3`, `shrinking=True`, `cache_size=200` (sklearn defaults, matching LIBSVM's documented defaults). B/C scaling: `MinMaxScaler(feature_range=(-1, 1))` fit on train only, applied to test (mirror of `svm-scale -l -1 -u 1`). C: `C=2, gamma=2`. Data loaded with `load_svmlight_file`.

The pipeline contains no stochastic component; per PREREG_DRIFT.md the procedure is still executed identically under master seeds 0, 1, 2 (seed threaded through as `random_state` where an API accepts one — none does here), and the standardized drift is the 3-run mean |reproduced − published| in pp. Identical outputs across seeds are the expected behavior and will be reported as such, not as extra precision.

## Pre-registered expected value, tolerance and verdict rule

- **Expected value:** published values (66.925 / 96.15 / 96.875), expected drift ≈ 0–0.5 pp given the shared LIBSVM engine; the guide's LIBSVM version is old (2003–2016 era) and minor solver changes since are the plausible residual.
- **Tolerance: ±2.0 pp absolute, per column** (same bar as confirmatory audits #1–#2's CONFIRMED bar; with n_test = 4,000 the binomial SEM is ≈ 0.7 pp at p≈0.67 and ≈ 0.3 pp at p≈0.96, so the bar is generous and will not be moved).
- **CONFIRMED** if ALL THREE columns satisfy |reproduced − published| ≤ 2.0 pp (seed-0 primary); **DISCREPANCY** if any column exceeds; **COULD-NOT-RUN** if data access or the 45 s per-process cap blocks execution (fit on 3,089×4 should take well under a second; no cap risk anticipated).
- **Secondary (Program 2b, exploratory until n=30):** the hypothesis predicts LOW drift at scores 1–2 — same order as the Breiman-sonar points (0.59/0.94 pp at score 2), far below the MLP points (8.95/10.35 pp at score 3). If instead any column lands near the bar, that is evidence *against* the hypothesis at the low end and will be reported as such.

## Results

*(empty at pre-registration — filled by a later commit in this session's batch)*

## Verdict

*(empty at pre-registration)*

## Environment

*(logged with results)*
