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

Data check: `load_svmlight_file` → train (3089, 4), test (4000, 4); train classes {1089, 2000}, test classes {2000, 2000} — matches Table 1 (3,089 / 4,000 / 4 features / 2 classes). MD5s match the pre-registered values.

| Column | Published | Reproduced (master seed 0, primary) | Drift |
|---|---|---|---|
| A — unscaled, defaults | 66.925 | **66.925** (2677/4000) | 0.000 pp |
| B — scaled, defaults | 96.15 | **96.150** (3846/4000) | 0.000 pp |
| C — scaled, C=2 γ=2 | 96.875 | **96.875** (3875/4000) | 0.000 pp |

Seed sensitivity (master seeds 1, 2): identical to the last printed digit on all three columns, as pre-registered for a pipeline with no stochastic component — the three runs are procedural replicates.

**Program 2b standardized drift (3-seed mean |reproduced − published|): A 0.000 pp, B 0.000 pp, C 0.000 pp.** With the blind rubric scores recorded in the pre-registration commit (`098cc566`), this audit contributes the points (2, 0.00), (2, 0.00) and (1, 0.00) to the confirmatory set (n=3 audits toward 30).

Not just within tolerance but *exact*: every correct-prediction count matches the guide's printed fractions (2677, 3846, 3875 of 4000). Consistent with the shared-engine expectation — sklearn's SVC wraps LIBSVM, so once the default mapping (C=1, γ=1/num_features) and the svm-scale mirror are chosen correctly, the ~two-decade-old printed numbers are bit-stable.

Secondary pre-registered prediction: **held** — low scores (1–2) produced the lowest drift yet (0.00 pp), below the Breiman-sonar score-2 points (0.59/0.94 pp) and far below the score-3 MLP points (8.95/10.35 pp).

## Verdict

**CONFIRMED.** All three columns reproduce exactly (0.000 pp drift, seed-0 primary and both sensitivity seeds) against the pre-registered ±2.0 pp bar.

## Honesty section

1. **Commit-1 message lost in the web editor**: the pre-registration commit `098cc566` carries the generic message "Add files via upload" — the typed message ("Program 2b audit #3: PRE-REGISTRATION ONLY …") did not register in the commit-summary field. The *content* of the commit is the pre-registration file, byte-identical (MD5-verified against the pinned SHA) to the local original, with empty Results/Verdict sections; ordering is provable from git history as required.
2. **Guide version ambiguity**: the guide was first issued 2003 and revised repeatedly; the audited numbers were transcribed from the current PDF fetched this session. The claim's LIBSVM version is unspecified; drift turned out to be 0.000 pp anyway, so the ambiguity is moot for this audit.
3. **Shared engine caveat for the drift study**: sklearn's SVC wraps LIBSVM itself, so these three points price *wrapper + default-mapping* discretion, not an independent re-implementation. That is exactly what the rubric scored (the two points awarded were default-mapping and tolerance discretion), but readers pooling the confirmatory set should know these are the "same engine" end of the spectrum.
4. **Zero variance across seeds**: pre-declared; the 3-seed averaging is pro forma here and adds no information.
5. **grid.py step not audited**: column C reproduces the final train/predict at C=2, γ=2; the cross-validation search that selected those values (96.8922% CV rate) was not reproduced (it is a selection procedure, not one of the three pre-registered test-set claims).

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3. Runtime ≈ 5 s for all 3 seeds (no 45 s cap risk). Reproduction script: `audits/audit_svmguide1_run.py`; raw per-seed results + data checks: `audits/svmguide1_raw.json`. Both committed in this session's batch.
