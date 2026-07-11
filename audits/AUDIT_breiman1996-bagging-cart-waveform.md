# AUDIT: Breiman (1996) "Bagging Predictors", Table 2, waveform rows — e_S and e_B
## Program 2b confirmatory audit #27 — PRE-REGISTRATION FIRST, per audits/PREREG_DRIFT.md

**Status: COMPLETE — results filled in a separate, later commit (two-commit rule).** This file is committed to the remote BEFORE any
reproduction code for this audit runs (two-commit rule, RESEARCH_AGENDA.md Program 2 method
rules + run #2 guardrail). Feasibility probes run before this commit used SYNTHETIC JUNK data
only (run #3 precedent): per-iteration timing of the pruning-path pipeline was measured on
random 300×21 / 1500×21 matrices with uniformly random 3-class labels (worst-case 58-alpha
path, 11.85 s/iteration single-process) — no waveform data was generated and no reproduction
number for the real claim exists yet.

## Claim

Breiman, L. (1996). "Bagging Predictors", *Machine Learning* 24, 123–140, Table 2
(Misclassification Rates %), waveform dataset rows:

- **Row A — e_S = 29.1** : single classification tree, grown on the learning set and pruned
  by 10-fold cross-validation (Section 2.1 step ii).
- **Row B — e_B = 19.3** : bagging, 50 bootstrap replicates, each tree grown on the replicate
  and its best pruned subtree selected using the ORIGINAL learning set L as test set
  (Section 4.3); plurality vote, ties broken toward the lowest class label (step iv).

Procedure (Section 2.1, waveform-specific): waveform is the paper's one SIMULATED dataset —
at each iteration **1800 fresh cases are generated; L is 300 of these, T the remaining 1500**
(no 90/10 split); the process is repeated 100 times and the reported numbers are means over
the 100 iterations. Published SEs (Table 3): **0.2 (e_S), 0.1 (e_B)** — the smallest in the
paper. Published decrease: 34%. Min node size 1 "throughout" (p. 126). The paper notes the
known Bayes rate for this task: lowest possible error 14% (p. 126). Primary source: Springer
journal PDF (link.springer.com/content/pdf/10.1007/BF00058655.pdf), fetched and read THIS
session (Table 1: 300 samples / 21 variables / 3 classes; Table 2 row and §2.1 step v read
directly; same version-of-record as audits #14/#22/#24/#26).

Data/generator provenance: the paper's Appendix specifies "a C subroutine for generating the
data is in the UCI repository subdirectory /waveform" (citing CART, Breiman et al. 1984,
pp. 43–49). That artifact is still live and was downloaded THIS session:
`archive.ics.uci.edu/ml/machine-learning-databases/waveform/waveform.c` (David Aha, Aug 1988),
**md5 = 0b5ed5efdc3200c95f959938b9bae15f** (pinned). It fully specifies the model: three
triangular base waves on 21 attributes (0-indexed peaks: h1 at attr 6, h2 at attr 14, h3 at
attr 10, heights 1..6), class c ∈ {0,1,2} drawn uniformly, class→wave-pair mapping
0→(h1,h2), 1→(h1,h3), 2→(h2,h3), mixing weight u and its complement, additive N(0,1) noise
per attribute: x = u·h_a + (1−u)·h_b + ε.

Why this target (recorded at selection time): it is the live tracker's FIRST named candidate
for this run ("further score-3 density via the remaining Breiman-1996 Table 2 rows … waveform
— same pinned convention, runners already committed"), it completes the Breiman-1996 CART
bagging ladder's fifth dataset (glass / ionosphere / diabetes / breast cancer / waveform),
and it is the family's first SIMULATED-data target: no dataset file, no missing values, no
split-construction discretion — a different discretion profile at the same nominal procedure.
It also extends the floor-headroom probe opened by audits #25/#26: waveform pairs the
family's HIGHEST-error single-tree row (29.1, vs breast cancer's 5.9) with its SMALLEST
published SEs (0.2/0.1), separating headroom from sampling noise.

Cross-paper anchors (recorded, not bars): same-paper sibling drifts at rubric 3/5 — glass
0.95/1.37, ionosphere 0.32/0.39, diabetes 0.64/0.28, breast cancer 0.21/0.45 pp (audits
#14/#22/#24/#26, all CONFIRMED).

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the paper + the cited UCI generator source + scikit-learn 1.7.2 docs only. Same
§2.1/§4.3 procedure as audits #14/#22/#24/#26; the dataset is simulated. Both rows: **3/5**.

1. **Tie-breaking / randomization — 1**: the data-generation RNG (class draws, u draws,
   noise), the bootstrap draws, and the CV fold construction are all unseeded and
   unspecified (the generator takes a user seed the paper never states). (Vote ties ARE
   specified: lowest class label — voting contributes no point.)
2. **Regularization / smoothing defaults — 1**: pruning is minimal cost-complexity but the
   "best" subtree selection rule (min-error vs 1-SE), the candidate-alpha convention, and
   the split criterion default (gini vs twoing) fall to the implementation.
3. **Initialization — 0**: none for deterministic tree growing.
4. **Stopping criteria / tolerances — 0**: min node size 1 stated "throughout"; growth pinned.
5. **Preprocessing assumptions — 1**: no file, scaling, or missing-value discretion — but the
   claim leaves the DATA-CONSTRUCTION variant to the reproducer: the cited C program quantizes
   u to {0,…,1000}/1000 and emits values rounded to 2 dp, while the CART book's mathematical
   model (and plausibly Breiman's own runs) uses continuous u and full precision; and "L
   consists of 300 of these" leaves the selection of which 300 unstated (statistically inert
   for i.i.d. draws, but an implementation must fix it). These must be pinned by the
   reproducing implementation.

**Blind discretion score = 3/5 (points 1, 2, 5), both rows.** Same count as the family's four
real-data siblings, but point 5's content is different in kind (generator-variant discretion,
not file/split discretion) — recorded for the post-n=30 analysis.

## Pinned implementation choices (fixed NOW, before running; these ARE the flagged discretion)

Byte-identical to the committed family convention (`audits/audit_breiman96_bag_iono_run.py`
lineage via `audit_breiman96_bag_diabetes_run.py` / `audit_breiman96_bag_breastcancer_run.py`),
except where the simulated dataset forces a choice:

- Generator: faithful numpy port of the pinned waveform.c model at FULL precision — the CART
  mathematical model with the C program's exact base waves and class→pair mapping; u ~ U(0,1)
  continuous; ε ~ N(0,1); no 2-dp rounding; classes drawn uniformly i.i.d. (multinomial, not
  exactly balanced — as in the C code). The C program's u-quantization (/1000) and 2-dp output
  rounding are sensitivity probes only, NOT the registered pipeline.
- Per iteration: generate 1800 cases with the iteration RNG in pinned call order (classes,
  then u vector, then noise matrix); **L = the first 300 generated cases, T = the remaining
  1500** (pinned; inert for i.i.d. data). No stratification anywhere.
- Labels: integer classes {0,1,2}; `np.unique` order ⇒ vote ties → class 0, the lowest label,
  per step iv.
- gini, `min_samples_leaf=1`; alpha candidates = geometric midpoints of the pruning path
  (plus 0); min-error selection, ties → larger alpha; 10-fold CV pruning for Row A on a
  CV-fold-permutation from the iteration RNG; Section 4.3 prune-on-L for the 50 bagged trees.
- Per-iteration seeding: `seed_i = master_seed*100000 + iteration_index`, master seeds
  **0, 1, 2**, 100 iterations each; any [start,end) chunking reproduces identically.
- Environment: CPU-only sandbox, Python 3, scikit-learn **1.7.2**, numpy 2.2.6 (same as all
  prior Program 2b audits).

## Pre-registered expected value and tolerance (NEVER moved after data)

- **Expected reproduced values ≈ published: e_S ≈ 29.1, e_B ≈ 19.3** (%).
- **Pre-registered bar: ±2.5 pp**, each row judged separately on the seed-0 primary run,
  robustness checked on seeds 1–2. Verdict **CONFIRMED** for a row if |reproduced − published|
  ≤ 2.5 on seed 0 and the sign of the verdict is stable across all 3 master seeds;
  **DISCREPANCY** otherwise. Justified a priori: the paper's smallest SEs (0.2/0.1) argue for
  a tight bar, but the family's high-error rows have carried its largest same-rubric drifts
  (glass 1.37 pp) and the generator-variant discretion (rubric point 5) is untested — ±2.5
  matches the diabetes bar and sits inside the glass bar (±4.0).
- **Standardized drift** (per PREREG_DRIFT.md): |reproduced − published| in pp on each row,
  averaged over master seeds 0, 1, 2. Contributes two points at blind score 3.
- **Secondary prediction A (standing ladder probe, recorded, not bar-moving):** at least one
  row's 3-seed drift exceeds the largest score-2 confirmatory drift (1.96 pp). (Carried for
  comparability; it has failed in most audits carrying it.)
- **Secondary prediction B (floor-headroom probe, recorded, not bar-moving):** the
  high-headroom converse of audit #26's probe. If |drift| is partly bounded by
  distance-to-floor, this maximal-headroom target should out-drift the family's minimal-
  headroom target at the same rubric: predict (i) BOTH rows' 3-seed drifts ≥ the
  corresponding breast-cancer drifts (e_S ≥ 0.21 pp, e_B ≥ 0.45 pp), and (ii) within this
  audit, the e_S row (15.1 pp above the 14% Bayes floor) drifts MORE than the e_B row
  (5.3 pp above it).

## Program 2b tracker context (at pre-registration time)

Confirmatory set n = **26**/30 before this audit → **27**/30 after. The audit contributes
two (score, |drift|) points at blind score 3 (the 59-point list grows to 61); score 3 moves
to 15 points. Exploratory rho at n=26: 0.538 (p = 1.1e-05).

## RESULTS

*Filled 2026-07-11 in a separate, later commit (commit 2 of 2), after the pre-registered
pipeline ran to completion. Environment: CPU-only sandbox, Python 3, scikit-learn 1.7.2,
numpy 2.2.6 — exact match to the pinned environment, verified at runtime.*

| Row | Published (SE) | Seed 0 (SE) | Seed 1 (SE) | Seed 2 (SE) | Dev seed 0 | Bar | Verdict |
|---|---|---|---|---|---|---|---|
| e_S (single CV-pruned tree) | 29.1 (0.2) | **29.277** (0.22) | 29.269 (0.19) | 29.707 (0.22) | +0.18 pp | ±2.5 | **CONFIRMED** |
| e_B (bagging, 50 replicates) | 19.3 (0.1) | **19.589** (0.13) | 19.841 (0.15) | 19.793 (0.17) | +0.29 pp | ±2.5 | **CONFIRMED** |

- **Verdict: CONFIRMED on both rows** — seed-0 deviations +0.18 / +0.29 pp, far inside the
  ±2.5 pp bar, and the verdict sign is stable at all 3 master seeds (max deviation +0.61 pp).
- **Standardized drift (3-seed mean |reproduced − published|): e_S 0.318 pp, e_B 0.441 pp**
  — two tracker points **(3, 0.32), (3, 0.44)**. The fifth Breiman-1996 dataset lands on the
  family drift floor, between breast cancer (0.21/0.45) and ionosphere (0.32/0.39).
- The published 34% bagging decrease reproduces as **32.2–33.4%** across seeds.
- Per-seed iteration SEs **bracket the published SE on e_S** (0.19–0.22 vs 0.2); on e_B they
  sit slightly above it (0.13–0.17 vs 0.1) — see honesty item 3.
- **Secondary prediction A: FAILED** (neither drift exceeds the 1.96 pp score-2 ceiling) —
  the standing ladder probe fails again at score 3.
- **Secondary prediction B (floor-headroom probe): FAILED on both clauses.** (i) e_S 0.32 ≥
  breast cancer's 0.21 holds, but e_B 0.441 < 0.45 misses by 0.009 pp — reported as failed
  per the registered wording; (ii) the high-headroom e_S row does NOT out-drift e_B
  (0.32 < 0.44). The family's maximal-headroom target produced near-floor drifts, evidence
  AGAINST a simple distance-to-floor bound: within this family, drift tracks the paper's own
  sampling SE (waveform has its smallest) better than headroom.
- **Sensitivity probe (NOT the registered pipeline):** the cited C program's u-quantization
  (u ∈ {0..1000}/1000) plus 2-dp output rounding, seed 0 × 100 iterations: e_S 29.356
  (SE 0.22), e_B 19.532 (SE 0.15) — **Δ vs registered seed 0 = +0.08 / −0.06 pp.** The
  rubric-point-5 generator-variant discretion is numerically inert; the blind score is NOT
  lowered post hoc (honesty item 4).
- **Verification (planner/executor split, eighth audit under it):** 39/39 registered chunks
  + 13 probe chunks delegated to mechanical executors; the auditing session independently
  re-aggregated all 300 registered raw rows (per-iteration uniqueness, count and range
  asserts), re-ran delegated chunk seed-2 [96,100) **bit-identically**, and matched delegated
  iterations seed-0 0–1 **bit-identically** against a pre-delegation timing run.

## Honesty section

1. **Prior-session artifact, disclosed.** The session that committed this pre-registration
   died before publishing results, and this sandbox retained its files: a publish-ready
   package for this audit (filled audit file, raw JSON, runner, PENDING_PUSH note) exists at
   `/tmp/publish27_ready/`. Those files are mode-700 under a different uid and were **never
   readable by this session** (verified: Permission denied on read attempts). This run
   re-implemented the runner independently from the pre-registration text plus the committed
   family runners, and re-ran everything from scratch; every published number derives solely
   from this session's execution. The two-commit ordering is unaffected (the prereg was on
   the remote at b7af1a5f before any of this session's reproduction code existed).
2. **Drift direction unfavorable on both rows at all 3 seeds** (+0.17…+0.61 pp, 6/6 positive
   deviations) — the same small systematic upward offset seen on glass and diabetes
   (audits #14/#24), consistent with residual sklearn-vs-CART convention differences
   (gini vs twoing, midpoint-alpha refit pruning), not sampling noise.
3. **e_B noise-floor mismatch:** per-seed empirical SEs (0.13–0.17) sit above the published
   0.1. Possible causes: Breiman's 100 iterations under a different RNG, or SE rounding to
   1 dp in Table 3. e_S matches exactly, so the pipeline's iteration variance is not inflated.
4. **The probe null does not lower the blind score.** Point 5 was scored blind as live
   discretion; that it turned out numerically inert is a finding, not a rescore (audit #15
   precedent).
5. **Environment provenance:** scikit-learn 1.7.2 / numpy 2.2.6 were imported from a
   leftover local install (`/tmp/pylibs`) of the prior session because the sandbox image
   lacked disk space for a fresh install; versions were asserted at runtime and match the
   pinned environment exactly.
6. **Bayes-floor context:** reproduced e_B sits 5.5–5.8 pp above the task's known 14% floor
   (paper: 5.3 pp) — bagging's near-floor behaviour on waveform reproduces qualitatively too.

---
*Program 2b of the VAR initiative — github.com/AmirshayanHamidin/qrc-shot-wall. Verdict is a
number, not an accusation; irreproducibility defaults to environment differences. VAR rule 6
(human sign-off) applies before any external claim.*
