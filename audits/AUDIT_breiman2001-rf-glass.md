# AUDIT: Breiman (2001) "Random Forests" — Table 2, glass row (Forest-RI)

Program 2b confirmatory audit #18 (VAR). Session 2026-07-09 (Program 2b run #16, scheduled). Two-commit rule: this file is committed to the remote with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail: web-commit the pre-registration first). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

Breiman, L. (2001), "Random Forests", Machine Learning 45(1), 5–32. Table 2 "Test Set Errors (%)", row `glass`:

- Forest-RI, **Single Input (F=1)**: published **21.2%** test error
- Forest-RI, **Selection**: published **20.6%** test error

Full printed row for the record: glass — Adaboost 22.0 | Selection 20.6 | Single Input 21.2 | One Tree 36.9. Source: the author's copy at https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf, fetched and transcribed this session (same table, same transcription convention as audits #1, #4 and #6, which audited the ionosphere and sonar rows). Table 1: glass = 214 cases, 9 inputs, 6 classes.

Why this target: the named candidate from run #15's priorities — it extends the within-paper, cross-dataset ladder (Table 2 Forest-RI now: ionosphere #4, sonar #1, glass here) at the same discretion profile, adding the paper's only small multi-class row. First Forest-RI point on a >2-class problem (plurality voting across 6 classes exercises tie-breaking paths the binary rows never touch).

## Published procedure (paper Section 3.1, same wording basis as audits #1/#4)

Random division into 90% training / 10% test, repeated 100 times, errors averaged. Forest-RI with two feature-subset sizes: F=1 ("single input") and F=int(log2 M + 1) ("selection" tries both and uses OOB estimates to select); glass M=9 → F=int(log2 9 + 1) = **4**. 100 trees per forest, grown to full size, no pruning, plurality vote.

## Blind discretion rubric (scored BEFORE running any code, from paper + scikit-learn docs only)

Score: **2/5** (both columns; identical discretion profile — same harness as audits #1/#4, whose 2/5 carries over dataset-independently).

1. **Tie-breaking / randomization — 1.** No seed, RNG, bootstrap or split tie-break details published; Fortran CART vs sklearn RNG entirely different. Multi-class plurality voting adds vote-tie resolution (sklearn: lowest class index) that the paper never specifies.
2. **Regularization / smoothing defaults — 0.** RF trees conventionally unpruned and fully grown; sklearn defaults (min_samples_split=2, min_samples_leaf=1, ccp_alpha=0) match the stated convention.
3. **Initialization — 0.** Not applicable to trees.
4. **Stopping criteria / tolerances — 0.** "Grown to full size" pins growth termination; library defaults implement exactly that.
5. **Preprocessing / split construction — 1.** The "random 10%" holdout construction is the reproducer's: unstratified vs stratified, rounding (22 test / 192 train under sklearn's ceil convention), and the OOB-based Selection convention (which forest, how ties break) are all pinned here, not by the paper.

## Data

UCI `glass.data` (archive.ics.uci.edu), expected md5 `2732c9170bf8c483f33da3c58929c067`, 214 rows = id + 9 float features + integer class (6 classes present: 1,2,3,5,6,7) — same file, same md5 as audits #9/#11/#14, re-verified at download. Fallback if UCI is unreachable: OpenML data_id=41 with shape assertion (214, 9) and class-count check; the source actually used will be logged in Results.

## Reproduction plan (pinned before running)

Per master seed m ∈ {0 (primary), 1, 2}: 100 iterations. Iteration i: unstratified `train_test_split(test_size=0.10, random_state=split_seed)` with **split_seed = m*100003 + i** (chunkable under the 45-s cap; chunking cannot change the numbers). Fit two `RandomForestClassifier(n_estimators=100, criterion="gini", bootstrap=True, oob_score=True)` — `max_features=1` with `random_state=(2*split_seed+1) % 2**31` and `max_features=4` with `random_state=(2*split_seed+2) % 2**31`. Single Input column = mean over iterations of the F=1 forest's test error. Selection column = mean over iterations of the test error of the forest (F=1 vs F=4) with the lower forest-level OOB error, tie → F=1 (audit #1/#4 convention). Values ×100. Primary numbers: master seed 0; Program 2b standardized drift = mean |reproduced − published| over the 3 master seeds, per column.

## Pre-registered tolerance and verdict rule

- Expected value: the published 21.2 / 20.6 (same-harness ladder points, audits #1/#4/#6, drifted 0.2–1.3 pp; no directional prediction).
- **CONFIRMED** if BOTH columns satisfy |reproduced − published| ≤ **2.5 pp** (seed-0 primary); **DISCREPANCY** if either exceeds; **COULD-NOT-RUN** if data access or the 45-s per-process cap blocks a faithful execution. The bar is 0.5 pp wider than sonar's (±2.0): n_test=22 is as small as sonar's 21 but spread over 6 classes with a ~21% base error rate (per-iteration sd ≈ 8.7 pp; 100-iteration mean sd ≈ 0.9 pp) and Breiman (1996) reports SE ≈ 1.1 on this same 90/10 glass harness. Bars will not be moved after data.

Secondary (non-verdict) prediction, logged for the discretion-drift hypothesis: both score-2 drifts land ≤ the running score-2 ceiling (1.96 pp, audit #5).

## Results

Environment: sandboxed Ubuntu 22.04, CPU only, Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6. Data: UCI `glass.data` downloaded from archive.ics.uci.edu this session, md5 **verified** `2732c9170bf8c483f33da3c58929c067` (= audits #9/#11/#14; the OpenML fallback was not needed). Runner: `audits/audit_rf_glass_run.py` (chunked 2 x 50 iterations per master seed under the 45-s cap; per-iteration seeding makes chunking irrelevant to the numbers). Raw per-iteration cells (err_f1, err_f4, oob_f1, oob_f4, err_sel, picked): `audits/rf_glass_raw.json`.

| Column | Published | Reproduced (master seed 0, primary) | Drift |
|---|---|---|---|
| Single Input (F=1) | 21.2 | **22.591** | +1.39 pp |
| Selection | 20.6 | **22.500** | +1.90 pp |

Sensitivity seeds — Single Input: 21.500 (seed 1), 22.000 (seed 2); Selection: 22.000 (seed 1), 22.727 (seed 2).

**Verdict: CONFIRMED** — both columns inside the pre-registered +/-2.5 pp bar at seed 0. The bar was not moved.

**Program 2b standardized drift (3-seed mean |reproduced - published|): Single Input 0.83 pp, Selection 1.81 pp.** With the blind rubric score of 2/5 recorded in the pre-registration commit `80faaa4`, this audit contributes the points **(2, 0.83)** and **(2, 1.81)** to the confirmatory set (n=17/30).

Secondary prediction **HELD**: both 3-seed drifts land at or below the running score-2 ceiling (1.96 pp, audit #5) — though Selection uses 92% of it and becomes the second-largest score-2 drift in the set.

## Honesty section

1. **The published within-row ordering does not reproduce.** Breiman reports Selection *better* than Single Input (20.6 < 21.2); in this reproduction Selection is *worse* at 2 of 3 seeds and on the 3-seed means (22.41 vs 22.03). The OOB choice picked F=1 in only 54-61% of iterations, and on 192 training cases the forest-level OOB estimate is noisy enough that selection adds variance rather than value. Most of the Selection column's drift (1.81 vs the F=1 forest's 0.83) is this selection-rule noise, not forest quality.
2. **Drift direction is unfavorable (reproduced error higher than published) on both columns at all 3 seeds.** Same direction as audit #1's sonar seed 0, opposite to the ionosphere audit's uniformly favorable drift — across the three audited rows of Table 2 there is still no consistent direction, supporting the replication-noise reading. Candidate mechanisms for the glass-specific upward shift, stated without accusation: (a) the unstratified 22-case holdout frequently draws few or no cases of the rare classes (classes 3/5/6 have 17/13/9 cases), inflating error variance and possibly the mean vs whatever split construction the paper used; (b) 6-class plurality voting on 100 trees has more tie exposure than the binary rows.
3. Individual-seed Selection drifts span 1.40-2.13 pp; seed 2 alone (2.13) sits within the bar but above the score-2 ceiling. Per PREREG_DRIFT.md the tracker quantity is the 3-seed mean (1.81); stated so the single-seed spread is on the record.
4. The same-engine caveat of audit #3 does NOT apply: Fortran CART (2001) vs scikit-learn 1.7.2 are genuinely independent implementations.
5. Label correction, typo-class: the pre-registration header says "Program 2b run #16"; per the agenda log this scheduled session is run #17 (2026-07-07 was run #16). The registered file is not edited; flagged here instead.
6. Guardrail compliance note (run #16 addendum rule): the same-day-duplicate check was effectively performed by the prereg new-file web-commit itself, which would have collided ("file already exists") had another instance registered this target today; it did not. The commits page was checked after the prereg landed (`80faaa4` at HEAD) rather than before rubric scoring — order noted for the record.
