# PRE-REGISTRATION: B2 provenance restoration — sim-trained denoiser rows + redundancy probe

Registered 2026-08-02 (scheduled session, third), BEFORE any reproduction code ran. Two-commit
rule (Program 2 method rules, RESEARCH_AGENDA.md): this file is committed with an EMPTY results
section first; results land in a separate later commit. Bars are never moved after data.

## Scope and provenance finding

The 2026-07-11 B2 re-audit (AUDITS.md) found that four published numbers in
`results/RESULTS_GAP.md` have **no committed generator**: the two 40k strategy-table rows
"Sim-trained linear denoiser" (NMSE **0.1519**) and "Sim-trained MLP denoiser (256×128)"
(NMSE **0.1533**), and the secondary-findings non-redundancy probe (rel. err **0.90** linear /
**0.89** MLP "trained on 2,300 simulated timesteps"). They were produced in-session and only
the printed numbers survive (same class of gap that produced the B5 discrepancy; flagged, not
challenged — both rows are interior points of the fully-reproduced plateau). The 2026-07-27
doc-fix batch annotated the rows; the annotation is not a generator. This registration commits
a **pinned-convention reconstruction generator** and pre-declares how its output will be
compared to the printed numbers. Because the original in-session code is lost, this is a
reconstruction under declared conventions — the B5-restoration class — not a bit-reproduction
claim and not a drift audit (Program 2b is closed; no tracker point is generated).

## Pinned protocol (committed conventions wherever one exists)

Benchmark run — identical to the committed `qrc_gap_eval.run()` defaults, unmodified:
NARMA5 `narma(5, T=1200, seed=5)`; reservoir `random_reservoir_unitary(6, seed=7)`; V=4
virtual nodes; budget 40 000 → 10 000 shots/node; benchmark noise seed **1**;
`Xin = window_features(u, 10)`; splits, alpha grid and test NMSE via the committed
`eval_strategy`; downstream readout for denoised features = `hstack([lag(X_denoised), Xin])`
(the committed lag+input pipeline used by every other mitigation row).

Denoiser training data ("sim-trained"): a SECOND simulated sequence, same reservoir and V,
`narma(5, T=2400, seed=105)`, training noise seed **2**, rows after the committed washout
(100) → **2 300 training rows** (matching the printed "2,300 simulated timesteps").
Regressor input per row: [84 noisy features ‖ 10-col input window]; target: 84 exact features.

- **Linear denoiser:** multi-output ridge; alpha ∈ {1e-6, 1e-4, 1e-2, 1, 100} selected by
  feature-reconstruction MSE on the last 30% of the 2 300 rows (fit on first 70%), refit on
  all 2 300 at the selected alpha. Deterministic.
- **MLP denoiser:** sklearn `MLPRegressor(hidden_layer_sizes=(256,128), random_state=0,
  max_iter=300)`, other params default, fit on all 2 300 rows. Deterministic given
  random_state.
- Each fitted denoiser maps the benchmark sequence's noisy features → denoised features;
  NMSE from the committed `eval_strategy` on `hstack([lag(X_denoised), Xin])`.

Redundancy probe: same two regressor recipes, input per row = the 10-col input window ONLY
(committed input-history representation), target = 84 exact features; trained on the same
2 300 training rows, evaluated on the benchmark sequence rows after washout (1 100 rows).
**rel. err = ‖pred − true‖_F / ‖true − colmean(true)‖_F** (column means from the evaluation
rows; = pooled √(1−R²)). The uncentered ratio ‖pred − true‖_F/‖true‖_F is also reported as a
labeled sensitivity, no bar.

Free choices NOT recoverable from the write-up, pinned above and disclosed: training-sequence
input seed (105), training noise seed (2), denoiser alpha-selection split (70/30), MLP
max_iter (300), probe input width (the committed w=10 window), the centered rel-err
definition, and lag+input as the denoisers' downstream pipeline. If the original differed,
Bar A below fails and that is the published result.

Sensitivity (labeled, no bar): the two denoiser NMSEs re-run at benchmark noise seeds 2 and 3
(the committed plateau-check seeds).

Generator committed as `src/qrc_gap_denoiser.py` (imports the committed `qrc_gap_eval` /
`qrc_benchmark` functions; no reimplementation). Raw output published as
`results/gap_denoiser.json` (full precision).

## Pre-registered falsifiable bars (numeric; failures published as failures)

**Bar A — strict landing (did the pinned reconstruction land on the printed numbers?):**
- A1: |NMSE_linear − 0.1519| ≤ 0.010
- A2: |NMSE_MLP − 0.1533| ≤ 0.010
- A3: |relerr_linear − 0.90| ≤ 0.05
- A4: |relerr_MLP − 0.89| ≤ 0.05

(Tolerance rationale, fixed before data: the published plateau's own noise-seed spread is
±0.005 NMSE (0.142/0.152/0.150); a reconstruction with unrecoverable free choices is allowed
2× that. The rel-err tolerance is 0.05 absolute against 2-dp printed values.)

**Bar B — claim survival (do the published CLAIMS hold under the pinned reconstruction?):**
- B1: both denoiser NMSEs land inside the published 40k mitigation bracket
  **[0.1417, 0.1759]** (denoisers sit on the plateau; they do not rescue the gap).
- B2: both probe rel. errs are **≥ 0.80** (exact features not readily learnable from the
  input window — the reservoir is not linearly/simply redundant).

Bar A failures with Bar B passes mean: the printed numbers' exact provenance stays lost, but
the claims they support are restored on committed code. Bar B failures would CHALLENGE the
published claims and be escalated in AUDITS.md as a discrepancy either way.

## Environment

Linux sandbox, CPU only; Python 3; numpy 2.2.6, scikit-learn 1.7.2, qiskit 2.5.1. No
credentials, no network beyond the repo. 45 s bash chunks.

## Results

(Run 2026-08-02, same session, after registration commit `217a342` was raw-verified
byte-identical on the remote. Generator: `src/qrc_gap_denoiser.py`; raw output:
`results/gap_denoiser.json`. This section is commit 2 of 2.)

| Quantity | published | reconstructed | bar | verdict |
|---|---|---|---|---|
| Sim-trained linear denoiser NMSE | 0.1519 | **0.150739** | A1: ±0.010 | **PASSED** (Δ 0.0012) |
| Sim-trained MLP denoiser NMSE | 0.1533 | **0.148522** | A2: ±0.010 | **PASSED** (Δ 0.0048) |
| Linear probe rel. err (pinned pooled metric) | 0.90 | **0.1299** | A3: ±0.05 | **FAILED** (Δ 0.77) |
| MLP probe rel. err (pinned pooled metric) | 0.89 | **0.6012** | A4: ±0.05 | **FAILED** (Δ 0.29) |
| Both denoiser NMSEs in [0.1417, 0.1759] | — | 0.1507 / 0.1485 | B1 | **PASSED** |
| Both probe rel. errs ≥ 0.80 | — | 0.13 / 0.60 | B2 | **FAILED** |

Pre-declared sensitivities: denoiser NMSEs at benchmark noise seeds 2/3 — linear
0.150367/0.150492, MLP 0.145982/0.141607 (plateau-stable); uncentered probe ratios 0.0222
(linear) / 0.1028 (MLP). Selected alphas: denoiser 1e-2, probe 1e-6; the MLP stopped at
n_iter = 14 (adam default tolerance). Determinism: the linear and MLP stages re-ran
bit-identically in-session (byte-identical JSON via cmp).

### Post-hoc diagnosis (EXPLORATORY, labeled — computed AFTER the A3/A4/B2 failures)

1. Variance-equalized (per-feature standardized) rel err does NOT reconcile the printed
   values: linear 0.291, MLP 1.011.
2. Excluding the current input u_t from the predictor window DOES land in the printed
   number's immediate neighborhood: pooled rel err **0.861** (linear). The freshly injected
   input dominates raw feature variance (uncentered linear ratio 0.022), so with u_t included
   the exact features are ~98% linearly predictable, while the reservoir's MEMORY content
   (past-input dependence) is not. The original probe most plausibly measured the latter.

## Reading the failures (honesty section)

1. **The denoiser rows are restored at claims level.** Under entirely pinned, disclosed
   conventions the reconstruction lands within 2-seed tolerance of both printed values and
   inside the plateau bracket, at every checked noise seed. The wall claim never depended on
   the exact digits; now the rows regenerate from committed code.
2. **The redundancy probe sentence was wrong as literally written — and is corrected, not
   defended.** "A linear map from input history cannot reproduce the exact features" is
   falsified under the committed input representation (which includes u_t): pooled rel err
   0.13. The defensible claim — supported by the post-hoc 0.861 and by the committed
   downstream numbers (inputs-only NMSE 0.1483 vs exact floor 0.0030, both bit-reproduced
   2026-07-11) — is that the reservoir's memory content is not linearly recoverable from past
   inputs, which is where the task-relevant signal lives. RESULTS_GAP.md and the README are
   corrected in this batch; the printed 0.90/0.89 remain provenance-lost as exact numbers.
   Verdicts are numbers, not accusations: the likeliest history is an unstated predictor
   convention (past inputs only), not a fabricated result.
3. **The MLP probe (0.601) underperforms the linear probe (0.130) at the pinned settings** —
   MLPRegressor underfits at n_iter = 14 with default tolerances on unscaled 84-dim targets.
   Reported as-is; no post-data tuning. This also means A4 fails in a different direction
   than A3, and the printed near-equality (0.90 ≈ 0.89) is another hint the original pair was
   computed under the no-current-input convention, where linear (0.861) and a mildly better
   MLP would sit close together.
4. Scratch cache (`dn_cache.npz`, per-stage `dn_*.json`) is intermediate and not committed;
   all published quantities are in `results/gap_denoiser.json`, full precision.
