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

(EMPTY at registration — filled by commit 2 only.)
