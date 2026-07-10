# AUDIT: Breiman (1996) "Bagging Predictors", Table 2, breast cancer rows — e_S and e_B
## Program 2b confirmatory audit #26 — PRE-REGISTRATION FIRST, per audits/PREREG_DRIFT.md

**Status: PRE-REGISTERED, results EMPTY.** This file is committed to the remote BEFORE any
reproduction code for this audit runs (two-commit rule, RESEARCH_AGENDA.md Program 2 method
rules + run #2 guardrail). Feasibility probes run before this commit used SYNTHETIC data only
(run #3 precedent): sklearn 1.7.2 NaN-in-tree support and per-iteration timing were verified
on a fake 699×9 matrix; no reproduction number for the real claim exists yet.

**Numbering note (disclosed):** the tracker's audit labels run to #25, but the repo also holds
`AUDIT_lecun1998-mnist-pca-quadratic.md`, a complete, validly two-commit-pre-registered
confirmatory audit (commits `38c33294` → `e57272c1`, 2026-07-06) that self-labels "#15" —
colliding with the xgboost audit's label — and whose point (3, 0.46) is MISSING from the
agenda tracker and its n count. A later session evidently renumbered without seeing it
(stale-cache incident class, guardrail 6). This audit therefore takes label **#26**, and the
tracker repair (n=24 → 25 before this audit) is published in the same session batch as this
audit's results, per VAR rule 5 (incidents are logged and repaired, not papered over).

## Claim

Breiman, L. (1996). "Bagging Predictors", *Machine Learning* 24, 123–140, Table 2
(Misclassification Rates %), breast cancer dataset rows:

- **Row A — e_S = 5.9** : single classification tree, grown on the learning set and pruned
  by 10-fold cross-validation (Section 2.1 step ii).
- **Row B — e_B = 3.7** : bagging, 50 bootstrap replicates, each tree grown on the replicate
  and its best pruned subtree selected using the ORIGINAL learning set L as test set
  (Section 4.3); plurality vote, ties broken toward the lowest class label (step iv).

Procedure (Section 2.1): the 699-case data is divided at random into 10% test / 90% learning;
e_S and e_B are measured on the test set; the random division is repeated 100 times and the
reported numbers are means over the 100 iterations. Published SEs (Table 3): **0.3 (e_S),
0.2 (e_B)** — the smallest in the paper's Table 3. Published decrease: 37%. Min node size 1
"throughout" (p. 126). Primary source: Springer journal PDF
(link.springer.com/content/pdf/10.1007/BF00058655.pdf), fetched and read THIS session
(Table 1: 699 samples / 9 variables / 2 classes; Table 2 row read directly; the audit #24
wrong-version trap re-checked — the journal version is the version of record here).

Dataset: Wisconsin breast cancer (Wolberg & Mangasarian 1990), per the paper's Appendix:
699 cases, **458 benign / 241 malignant** (counts stated in the paper and asserted at load),
9 cellular-characteristic variables. Provenance: the ORIGINAL UCI entry, still live —
`archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data`,
downloaded this session, **md5 = 52b89051b9bd37a91a54e8570b963719** (pinned; 699 rows,
11 columns: id + 9 features + class {2,4}). The file contains **16 cases with a missing
value ('?')**, all in attribute 7 (bare nuclei). The paper keeps all 699 cases yet never
states how missing values were handled — see rubric point 5.

Why this target (recorded at selection time): it is BOTH named candidates of the run-#22/#24
trackers in one — (a) score-3 density via the Breiman-1996 ladder's fourth dataset (same
pinned convention, committed runners), and (b) **the low-published-error probe for the
floor-headroom confounder** flagged in audit #25's honesty section: published errors 5.9/3.7
are the family's lowest (vs glass 30.4/23.6, diabetes 25.3/23.9, iono 11.2/7.9), so if
|drift| is partly bounded by distance-to-floor, this target should under-drift its
same-rubric siblings.

Cross-paper anchors (recorded, not bars): same-paper sibling drifts — glass 0.95/1.37,
ionosphere 0.32/0.39, diabetes 0.64/0.28 pp (audits #14/#22/#24, all CONFIRMED, rubric 3/5).

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the paper + scikit-learn 1.7.2 docs only. Same §2.1/§4.3 procedure as audits
#14/#22/#24; only the dataset changes. Both rows: **3/5**.

1. **Tie-breaking / randomization — 1**: the 90/10 division, the bootstrap draws, and the
   CV fold construction are all unseeded and unspecified. (Vote ties ARE specified: lowest
   class label — voting contributes no point.)
2. **Regularization / smoothing defaults — 1**: pruning is minimal cost-complexity but the
   "best" subtree selection rule (min-error vs 1-SE), the candidate-alpha convention, and
   the split criterion default (gini vs twoing) fall to the implementation.
3. **Initialization — 0**: none for deterministic tree growing.
4. **Stopping criteria / tolerances — 0**: min node size 1 stated "throughout"; growth pinned.
5. **Preprocessing assumptions — 1**: stratification of the 90/10 split unspecified; test-set
   size rounding unspecified; and — new to this dataset — **missing-value handling is real,
   live discretion**: the paper uses all 699 cases (Table 1 + Appendix) but never says how
   the 16 missing bare-nuclei values were treated (CART's surrogate splits are implied by
   the CART machinery but unstated); the reproducing library must choose among native-NaN
   splits, imputation, or case deletion, and sklearn's NaN routing is NOT CART's surrogate
   mechanism.

**Blind discretion score = 3/5 (points 1, 2, 5), both rows.** Same count as the family, but
point 5 is denser here (missing values add a mechanism the siblings didn't have).

## Pinned implementation choices (fixed NOW, before running; these ARE the flagged discretion)

Byte-identical to the committed family convention (`audits/audit_breiman96_bag_iono_run.py`
lineage, dataset-swapped as in audits #22/#24), except where the dataset forces a choice:

- Features: columns 2–10 of the UCI file as float (id column dropped); labels column 11,
  classes {2, 4}; `np.unique` order ⇒ vote ties → class 2 (benign), the lowest label, per
  step iv.
- '?' → NaN; **all 699 cases kept** (as the paper did). Missing values handled by sklearn
  1.7.2 `DecisionTreeClassifier`'s native NaN support (per-split learned routing of missing
  samples) — the closest committed-library analogue of CART's keep-all-cases behaviour.
  Verified on synthetic data this session that the full `cost_complexity_pruning_path` +
  fit + predict pipeline accepts NaN. Imputation and deletion variants are sensitivity
  probes only, NOT the registered pipeline.
- |test| = **70** (= round(0.1 × 699)), |L| = 629, bootstrap size 629; unstratified split.
- gini, `min_samples_leaf=1`; alpha candidates = geometric midpoints of the pruning path
  (plus 0); min-error selection, ties → larger alpha; 10-fold CV pruning for Row A on
  CV-fold-permutation from the iteration RNG; Section 4.3 prune-on-L for the 50 bagged trees.
- Per-iteration seeding: `seed_i = master_seed*100000 + iteration_index`, master seeds
  **0, 1, 2**, 100 iterations each; any [start,end) chunking reproduces identically.
- Environment: CPU-only sandbox, Python 3, scikit-learn **1.7.2**, numpy 2.2.6 (same as all
  prior Program 2b audits).

## Pre-registered expected value and tolerance (NEVER moved after data)

- **Expected reproduced values ≈ published: e_S ≈ 5.9, e_B ≈ 3.7** (%).
- **Pre-registered bar: ±2.0 pp**, each row judged separately on the seed-0 primary run,
  robustness checked on seeds 1–2. Verdict **CONFIRMED** for a row if |reproduced − published|
  ≤ 2.0 on seed 0 and the sign of the verdict is stable across all 3 master seeds;
  **DISCREPANCY** otherwise. The family's tightest bar (glass ±4.0, iono ±3.0, diabetes
  ±2.5), justified a priori: the paper's smallest SEs (0.3/0.2), the family's prior drifts
  (0.28–1.37 pp), and the smallest published values (5.9/3.7 bound the downward drift).
- **Standardized drift** (per PREREG_DRIFT.md): |reproduced − published| in pp on each row,
  averaged over master seeds 0, 1, 2. Contributes two points at blind score 3.
- **Secondary prediction A (standing ladder probe, recorded, not bar-moving):** at least one
  row's 3-seed drift exceeds the largest score-2 confirmatory drift (1.96 pp). (Carried for
  comparability; it has failed in 8 of 11 audits carrying it.)
- **Secondary prediction B (floor-headroom probe — this audit's purpose, recorded, not
  bar-moving):** BOTH rows' 3-seed drifts land ≤ 1.0 pp, i.e. below the same-rubric
  high-error siblings' maxima (glass 1.37 pp), consistent with |drift| being partly
  floor-bounded rather than purely discretion-driven. If instead this low-error target
  out-drifts its siblings, that is evidence AGAINST the floor-headroom confounder and FOR
  the discretion score carrying the signal.

## Program 2b tracker context (at pre-registration time)

Confirmatory set n = **25**/30 before this audit (24 tracked + the untracked PCA-quadratic
audit found this session; repair published with this audit's results batch) → **26**/30 after.
Two score-3 points; score 3 moves to 13 points.

## RESULTS

*(EMPTY at pre-registration commit. Filled in a separate, later commit.)*

## Honesty section

*(EMPTY at pre-registration commit.)*

---
*Program 2b of the VAR initiative — github.com/AmirshayanHamidin/qrc-shot-wall. Verdict is a
number, not an accusation; irreproducibility defaults to environment differences. VAR rule 6
(human sign-off) applies before any external claim.*
