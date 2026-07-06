# AUDIT: Gorman & Sejnowski (1988) — sonar backprop network, aspect-angle-independent test accuracy

**Program 2b confirmatory audit #2** under `audits/PREREG_DRIFT.md`. Two-commit rule: this file is
committed with rubric + pre-registration and an EMPTY results section BEFORE any reproduction code runs.

## Claim

Gorman, R. P., and Sejnowski, T. J. (1988), "Analysis of Hidden Units in a Layered Network Trained to
Classify Sonar Targets", *Neural Networks* 1, pp. 75–89. Aspect-angle-**independent** series, as
republished verbatim in the dataset's canonical documentation (`sonar.names`, maintained by
S. E. Fahlman, CMU benchmark collection; UCI "Connectionist Bench (Sonar, Mines vs. Rocks)",
CC BY 4.0):

| Hidden units | Published test accuracy (%) | Published std |
|---|---|---|
| 12 | **84.7** | 5.7 |
| 24 | **84.5** | 5.7 |

Published procedure (from sonar.names): 208 cases divided **randomly** into 13 disjoint sets of 16;
13-fold rotation (train 192 / test 16); each fold run **10 times**; reported value = average over all
13 × 10 = 130 test evaluations. Standard backprop, 60 inputs, 2 outputs, single hidden layer, trained
**300 epochs**; learning rate **2.0**, momentum **0.0**; errors < 0.2 treated as zero; initial weights
uniform in **±0.3**.

- Source doc: https://archive.ics.uci.edu/dataset/151/connectionist+bench+sonar+mines+vs+rocks (sonar.names)
- Data: OpenML data_id=40 ("sonar", 208×60) — same cache as confirmatory audit #1.
- Reproducing library: scikit-learn 1.7.2 `MLPClassifier` (Python 3.10, CPU).

Selected BEFORE rubric scoring per PREREG_DRIFT target policy. Rationale for selection: extends the
confirmatory discretion range beyond score 2 (tracker request), first neural-network family point,
oldest target so far (1988, 38-year implementation gap), and same dataset as audit #1 → a
within-dataset discretion contrast.

## Blind discretion rubric (scored from paper documentation + sklearn 1.7.2 docs ONLY, before any code)

| # | Item | Point | Justification (one line) |
|---|---|---|---|
| 1 | Tie-breaking / randomization | **1** | No seed/assignment published for the random 13-way division, nor RNG streams for the 10 runs per fold. |
| 2 | Regularization / smoothing defaults | **1** | No penalty/weight-decay stated; library must default (sklearn alpha=1e-4), and the paper's "errors < 0.2 = zero" margin has no sklearn equivalent, so the default log-loss fills the gap. |
| 3 | Initialization | **0** | Specified: uniform random weights in ±0.3 (that sklearn cannot honor it is an *unhonorable specification*, logged in Honesty, not scored — rubric scores only what the claim leaves unspecified). |
| 4 | Stopping criteria / tolerances | **0** | Specified: exactly 300 epochs, no early stopping (honored via max_iter=300 with tol-stopping disabled). |
| 5 | Preprocessing assumptions | **1** | Stratification of the 13 sets unspecified ("divided randomly"; sonar.names itself notes the resulting uneven splits); features arrive pre-normalized 0–1 so no scaling discretion. |

**Blind discretion score: 3 / 5** (both rows; identical discretion profile).

## Pre-registered procedure

For master seed m ∈ {0, 1, 2}: `RandomState(m)` permutes the 208 indices into 13 unstratified folds of
16 (mirroring "divided randomly"). For each fold (test = fold, train = remaining 192) and each run
r ∈ 0..9: fit `MLPClassifier(hidden_layer_sizes=(h,), activation='logistic', solver='sgd',
learning_rate='constant', learning_rate_init=2.0, momentum=0.0, nesterovs_momentum=False,
batch_size=192, max_iter=300, n_iter_no_change=300, tol=1e-12, alpha=1e-4 (default),
random_state=derived from (m, fold, r))` and record test accuracy. Row value = 100 × mean over the
130 evaluations, for h = 12 and h = 24. Everything the paper specifies and sklearn can honor is
honored (lr 2.0, momentum 0.0, logistic units, 300 epochs, hidden width); everything else takes the
library default — that residual discretion is precisely what the drift measures. ConvergenceWarnings
are expected and correct (fixed 300-epoch budget, matching the paper).

## Pre-registered expectation and bar (never moved after data)

- **Expected value:** published value for each row (84.7 / 84.5), direction of deviation genuinely
  uncertain (unhonorable loss, init, and output coding could push either way).
- **Verdict bar:** seed 0 primary — **CONFIRMED iff |reproduced − published| ≤ 5.0 pp for BOTH rows**,
  else DISCREPANCY. Bar is wider than audits at score 2 (±1.5/±2.0 pp) by design: it scales with the
  scored discretion, consistent with the hypothesis under test.
- **Standardized drift (per PREREG_DRIFT):** 3-seed mean |reproduced − published| pp, one point per
  row → this audit contributes (3, ·) and (3, ·).

## Results

*(empty at pre-registration — filled in a separate commit)*

## Honesty section

*(empty at pre-registration)*
