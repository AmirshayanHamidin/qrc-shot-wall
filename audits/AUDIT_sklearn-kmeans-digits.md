# AUDIT — scikit-learn stable docs (1.9.0): k-means digits demo, results table (3 init rows)

**Program 2b confirmatory audit #12 · 2026-07-06 · status at this commit: PRE-REGISTERED, results EMPTY**
Two-commit rule: this file is web-committed to the remote BEFORE any reproduction code exists.

## Claim

Source: https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_digits.html
("A demo of K-Means clustering on the handwritten digits data", scikit-learn **1.9.0** documentation,
fetched and read in full this session). Claim class: library-documentation executed example — the
class of exploratory audit `AUDIT_sklearn-digits-svc.md`, appearing in the CONFIRMATORY set for the
first time. **First clustering-family target in the program.**

The example clusters the full `load_digits()` dataset (1797 samples × 64 features, 10 classes) with
a `StandardScaler → KMeans(n_clusters=10)` pipeline under three initialization strategies and prints:

```
init            time    inertia homo    compl   v-meas  ARI     AMI     silhouette
k-means++       0.029s  69545   0.598   0.645   0.621   0.469   0.617   0.171
random          0.034s  69735   0.681   0.723   0.701   0.574   0.698   0.173
PCA-based       0.012s  69513   0.600   0.647   0.622   0.468   0.618   0.162
```

Pinned by the example code itself:
- row 1: `KMeans(init="k-means++", n_clusters=10, n_init=4, random_state=0)`
- row 2: `KMeans(init="random",    n_clusters=10, n_init=4, random_state=0)`
- row 3: `KMeans(init=pca.components_, n_clusters=10, n_init=1)` with `PCA(n_components=10)` fit on
  the raw data (deterministic full SVD at this size; explicit array init makes the row seed-free)
- metrics computed against the true labels on the scaled features; silhouette on the scaled data
  with `metric="euclidean", sample_size=300` and **no random_state** (global NumPy RNG).

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the example source + sklearn API docs only. Same score applies to all three rows.

| Item | Score | Justification |
|---|---|---|
| (1) tie-breaking / randomization | 1 | KMeans RNG pinned (`random_state=0`; row 3 deterministic array init, `n_init=1`) — BUT the silhouette column subsamples 300 of 1797 points with NO seed: global-RNG, process-state dependent, unknowable from the published artifact |
| (2) regularization / smoothing defaults | 0 | none in play |
| (3) initialization | 0 | fully specified per row (initialization is the example's subject) |
| (4) stopping criteria / tolerances | 1 | `max_iter`/`tol` left at library defaults across an unclosable version gap (docs 1.9.0 vs sandbox 1.7.2; the sandbox package index caps at 1.7.2 — pre-declared, same class as exploratory audit #3's 1.8.0→1.7.2 gap) |
| (5) preprocessing | 0 | `StandardScaler` explicit in the pipeline; canonical `load_digits()` |

**Blind discretion score: 2/5, all three rows.**

## Pre-registration

- **Primary measurand (verdict-bearing): the `v-meas` column × 100, per row** —
  k-means++ **62.1 pp**, random **70.1 pp**, PCA-based **62.2 pp**.
- **Tolerance: ±2.0 pp per row** (score-2 precedent). Verdict **CONFIRMED** iff all three rows land
  inside the bar at master seed 0; **DISCREPANCY** otherwise. The bar will not move.
- **Standardized drift (Program 2b):** 3-master-seed mean |reproduced − published| pp per row →
  contributes **3 points at blind score 2**. Master seeds {0,1,2} seed only the global NumPy RNG
  before the benchmark (mimicking the claim's own unknowable process state, which feeds ONLY the
  silhouette subsample); v-meas itself is expected bit-identical across master seeds.
- **Secondary (descriptive, no verdict weight):** homo / compl / ARI / AMI × 100 vs published at the
  same ±2.0 pp, reported per row; inertia relative difference; silhouette mean ± range over master
  seeds (the published value is a single unseeded draw); `time` column excluded (pure environment).
- **Secondary prediction (hypothesis-relevant):** all three v-meas drifts ≤ 1.96 pp (the program's
  current score-2 ceiling).
- **Pre-declared risk:** with `n_init=4`, a version-gap change in the k-means++ candidate stream or
  Lloyd iteration order could select a DIFFERENT local optimum — a discrete jump plausibly worth
  >5 pp on v-meas (the published rows themselves sit 8 pp apart across optima). If it fires, that is
  a DISCREPANCY at rubric 2/5, reported as such; the mechanism hunt goes in the honesty section.
- **Environment:** CPU-only sandbox, Python 3.10.12; scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3
  (installed this session; 1.9.0 not installable).
- Reproduction script to be published as `audits/audit_kmeans_digits_run.py`, raw output as
  `audits/kmeans_digits_raw.json`, in the results commit(s), per VAR rule 3.

## Results

**Verdict: CONFIRMED** — all three rows inside the pre-registered ±2.0 pp bar at master seed 0
(and at every master seed: v-meas is bit-identical across master seeds, as pre-registered).

| init | published v-meas (pp) | reproduced (pp, all seeds) | drift (pp) |
|---|---|---|---|
| k-means++ | 62.1 | 62.056 | 0.044 |
| random | 70.1 | 70.104 | 0.004 |
| PCA-based | 62.2 | 62.224 | 0.024 |

- **Standardized drift (3-master-seed mean): 0.04 / 0.00 / 0.02 pp** → three Program 2b points
  (2, 0.04), (2, 0.00), (2, 0.02).
- **Secondary prediction HELD:** all three drifts ≤ 1.96 pp (the score-2 ceiling).
- **Secondary metrics (descriptive): 18/18 deterministic printed cells identical at published
  precision** across the 1.9.0 → 1.7.2 version gap — every homo/compl/v-meas/ARI/AMI cell
  (15) and all three inertia values (e.g. k-means++: homo 0.5981→0.598, compl 0.6448→0.645,
  ARI 0.4693→0.469, AMI 0.6166→0.617; inertia 69545.33→69545 exact at {:.0f}).
- **Silhouette (no verdict weight):** reproduced across-master-seed ranges — k-means++
  0.150–0.169, random 0.185–0.187, PCA-based 0.140–0.169 — vs published single draws
  0.171 / 0.173 / 0.162. The only column that moves is exactly the one the blind rubric
  charged with the randomization point; the deterministic 18 cells did not move at all.
- Environment: Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3, CPU-only.
- Raw per-seed rows: `audits/kmeans_digits_raw.json`; runner: `audits/audit_kmeans_digits_run.py`.

## Honesty section

1. **Prereg prose slip (disclosed, no effect on the measurand):** the prereg's claim section
   described silhouette as computed "on the scaled data". The example code actually passes the
   RAW `data` array to `silhouette_score` (the pipeline scales internally for fitting only).
   The reproduction followed the example code verbatim (raw data); silhouette carries no
   verdict weight and the code line itself was quoted correctly in the prereg.
2. **Same-engine caveat (as exploratory audit #3):** claim and reproduction both run
   scikit-learn (1.9.0 docs vs 1.7.2 sandbox). This is a version-gap point, not a
   cross-implementation one: the ~0.00–0.04 pp drift prices two minor releases of
   KMeans/metrics evolution, not an independent reimplementation.
3. **Master-seed design:** the published silhouette values come from an unknowable global-RNG
   process state, so they are compared only against the reproduced across-seed spread
   (descriptive). All verdict-bearing numbers are seed-free by construction and came out
   bit-identical across master seeds {0,1,2}.
4. The `time` column was excluded as pure environment (pre-registered).
5. **Interpretation for the drift study:** a score-2 target whose two rubric points were
   (a) an unseeded auxiliary column and (b) version-default tolerances contributed ~0 drift on
   the primary measurand — consistent with the emerging picture that at the low-discretion end
   the drift floor is set by numerical/policy details rather than the rubric's headline items
   (cf. audit #10's Filip finding).
6. Publication incidents this session: none affecting files of record (session notes in the
   RESEARCH_AGENDA.md log entry for run #11).
