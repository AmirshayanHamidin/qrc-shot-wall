# PRE-REGISTRATION: B3 provenance restoration — parity curve + reference values

Registered 2026-08-02 (scheduled session; CLOSEOUT session 1/4 of the bounded closeout),
BEFORE any reconstruction code ran. Two-commit rule (Program 2 method rules,
RESEARCH_AGENDA.md): this file is committed with an EMPTY results section first; results land
in a separate later commit. Bars are never moved after data.

## Scope and provenance finding

The 2026-08-02 fourth-session B3 audit (AUDITS.md) found that the headline raw file
`results/task_shape.json` — the 400→120k parity accuracy curve (acc_mean/acc_std over 3 noise
seeds), all four reference values (esn_tuned **0.767**, poly3_classical **1.0**, linear
**0.51**, qrc_exact **1.0**), and the retention headline "classification retains ~86% where
regression retains ~4%" — has **no committed generator**, and neither does
`figures/qrc_task_shape.png`. The write-up cites "experiment blocks reproduced below" that do
not exist in the file; `src/qrc_design.py` contains no parity task, no logistic readout and no
ESN. Same class as the B5 observations and the B2 denoiser rows before their restorations.
Because the original in-session code is lost, this is a reconstruction under declared
conventions — the B2-gen class — not a bit-reproduction claim and not a drift audit
(Program 2b is closed; no tracker point is generated).

## Pinned protocol (committed conventions wherever one exists)

Reservoir and features — the committed `src/qrc_design.py` machinery, unmodified:
`reservoir_U(depth=3, coup=1.0, seed=7)` (identical unitary to the B1/B2 baseline);
`feats(u_seq, U, gain, shots, noise_seed, exact)` — V=4 virtual nodes, 84 features
(6 ⟨Z⟩ + 15 ⟨ZZ⟩ per node), multinomial sampling at `shots = budget // 4` per node.
Sequence length T=1200 (committed `qrc_gap_eval.T`).

Task ("full-range input encoding", per the write-up): input bit stream injected directly,
`u_seq = bits` (0/1 floats) with `gain = pi/2`, so theta ∈ {0, pi/2} — bits map to |0⟩/|1⟩,
the qubit's full rotation range. Labels: temporal parity-3 per the committed `qrc_law.py`
convention: `y[t] = b[t]^b[t-1]^b[t-2]` for t ≥ 2, else 0.

Readout (write-up: "logistic regression, features standardized, regularization tuned
identically for every method") — the committed `qrc_law.perf` clf convention, with the
committed B1/B2 split constants: washout 100, 70/30 train/test on post-washout rows,
`make_pipeline(StandardScaler(), LogisticRegression(max_iter=4000, C))`, C ∈ {0.1, 1, 10,
100}, report the best held-out accuracy over the C grid. The same pipeline scores every
method (QRC noisy, QRC exact, ESN, linear, poly3).

Curve: budgets [400, 1200, 4000, 12000, 40000, 120000] (stored); noise seeds **1, 2, 3**
(the committed benchmark seed and the two committed plateau-check seeds); acc_mean/acc_std
over the 3 seeds, matching the write-up's "mean of 3 noise seeds".

References:
- `qrc_exact`: `feats(..., shots=0, exact=True)`, same readout.
- `linear`: same readout on `window_features(bits, 10)` (the committed w=10 input window).
- `poly3_classical`: same readout on `PolynomialFeatures(degree=3, include_bias=False)` of
  the same 10-col window.
- `esn_tuned`: committed `esn_features(bits, 84, seed=3)` (feature count matched to the QRC's
  84), "tuned" = best held-out accuracy over rho_sr ∈ {0.5, 0.7, 0.9, 1.1, 1.3} × leak ∈
  {0.1, 0.3, 0.5, 0.7, 1.0}, same logistic pipeline.

Free choices NOT recoverable from the write-up, pinned above and disclosed: the bit-stream
seed (**5**, the committed benchmark input-seed convention: `narma(5, T=1200, seed=5)` seeds
the B1/B2/B3-design input stream), bits = `default_rng(5).integers(0, 2, 1200)`; the washout
(100) and split (0.7) constants; the linear/poly3 input representation (w=10 window); the ESN
tuning grid and its seed (committed default 3); noise-seed triple (1, 2, 3). If the original
differed, Bar A below fails and that is the published result.

Sensitivity (labeled, no bar): acc_mean at 40k and the four reference values re-run at
bit-stream seed 6.

Figure: `figures/qrc_task_shape_recon.png`, regenerated from the reconstruction JSON by the
same generator — two panels mirroring the original: left, % of quantum benefit surviving at
40k (regression bar recomputed from the stored `results/gap_final.json` under the audited
rounded-input convention, 4.1%; classification bar from this reconstruction); right, parity
accuracy vs budget with the three reference lines.

Generator committed as `src/qrc_taskshape_gen.py` (imports the committed `qrc_design` /
`qrc_benchmark` functions; no reimplementation). Raw output published as
`results/task_shape_recon.json` (full precision). The stored `results/task_shape.json` and
`figures/qrc_task_shape.png` are files of record and are NOT overwritten.

## Pre-registered falsifiable bars (numeric; failures published as failures)

**Bar A — strict landing (did the pinned reconstruction land on the stored numbers?):**
- A1: |acc_mean_recon(b) − acc_mean_stored(b)| ≤ 0.05 at every one of the 6 budgets.
- A2: |esn_recon − 0.767| ≤ 0.05
- A3: |linear_recon − 0.51| ≤ 0.04
- A4: qrc_exact_recon ≥ 0.995 AND poly3_recon ≥ 0.995

(Tolerance rationale, fixed before data: the stored curve's own 3-seed shot-noise stds are
0.002–0.025; an unrecoverable bit-stream seed adds test-set binomial noise ~sqrt(p(1−p)/330)
≈ 0.02–0.03 on ~330 test rows. 0.05 ≈ 2× the combined spread; the A3 band is chance ± the
same binomial spread; A4 reflects that both stored values are exactly 1.0.)

**Bar B — claim survival (do the published CLAIMS hold under the pinned reconstruction?):**
- B1: retention at 40k = (acc_mean(40k) − linear_recon) / (qrc_exact_recon − linear_recon)
  ≥ **0.80** (the "~86% vs ~4%" task-shape headline survives).
- B2: acc_mean(4k) < esn_recon < acc_mean(40k) (the noisy QRC crosses the tuned classical
  ESN between 4k and 40k shots/step — "near ~12k").
- B3: acc_mean(120k) ≥ **0.97** (the curve effectively reaches its exact-readout ceiling at
  budgets routine on today's hardware).

Bar A failures with Bar B passes mean: the stored numbers' exact provenance stays lost, but
the claims they support are restored on committed code. Bar B failures would CHALLENGE the
published claims and be escalated in AUDITS.md as a discrepancy either way.

## Environment

Linux sandbox, CPU only; Python 3; numpy 2.2.6, scikit-learn 1.7.2, qiskit 2.5.1,
matplotlib 3.10.9. No credentials, no network beyond the repo. 45 s bash chunks.

## Results

(EMPTY at registration. This section is filled by a separate later commit, after the
registration commit is raw-verified byte-identical on the remote.)
