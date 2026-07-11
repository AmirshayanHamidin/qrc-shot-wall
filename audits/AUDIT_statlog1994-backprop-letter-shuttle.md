# AUDIT: StatLog (Michie, Spiegelhalter & Taylor 1994) Backprop rows — letters + shuttle

Program 2b confirmatory audit #30 (VAR). Session 2026-07-11 (Program 2b run #30). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs. Governed by `audits/PREREG_DRIFT.md`.

**This is the audit that takes the confirmatory set past n = 30.** The pre-registered one-shot test of `PREREG_DRIFT.md` (Spearman rho > 0.5, p < 0.01) becomes due the moment these points land. That raises the stakes on target selection, so the selection rule is stated in full below and was fixed BEFORE the rubric was scored.

## Claim under audit

D. Michie, D. J. Spiegelhalter & C. C. Taylor (eds), *Machine Learning, Neural and Statistical Classification*, Ellis Horwood, 1994 — the StatLog project book. **Primary source re-fetched and re-read this session**: `whole.pdf`, **1 787 416 B** — byte-identical in size to the artifact pinned by audits #28/#29 (the editors placed the full text online at `www1.maths.leeds.ac.uk/~charles/statlog/`; retrieved via the Internet Archive snapshot; text extracted locally with `pdftotext -layout`).

Two rows, both the **Backprop** (multilayer perceptron) **test** error rate:

- **Letters (Table 9.7, §9.3.4): published test error 0.327** (train 0.323, rank 19 of 22). Protocol stated: 26 classes, 16 attributes, **(train, test) = (15 000, 5 000)**, "one-shot train and test". 20 000 total images; 16 integer attributes scaled to 0–15.
- **Shuttle (Table 9.19, §9.5.1): published test error 0.43 %** (train 4.50 %, rank 10 of 21). Protocol stated: 7 classes, 9 attributes, **(train, test) = (43 500, 14 500)**, a fixed distributed split. (Table 9.19 is the one StatLog table already reported in percent; the metric is the same test error rate.)

What the book says about its Backprop implementation (all of it, verbatim in substance, unchanged from audits #28/#29): an external neural-network package (§11.5.1) providing "a special purpose 3-layer MLP … and general MLP with architecture specified at runtime"; and (§7.4) "cross-validation was used by Backprop in finding the optimal number of nodes in the hidden layer". For **neither** of these two rows is the hidden-node count, learning rate, momentum, weight initialisation, epoch count, stopping rule, or input scaling published anywhere in the book. (Vehicle — audit #29 — remains the only Backprop row in the book with any disclosed configuration.)

## Target selection rule (fixed BEFORE rubric scoring, stated in full)

The tracker's standing priority is score-4/5 density: before this audit, score 5 holds only 4 of 65 points. The StatLog Backprop rows are the cleanest genuinely-5/5 claim class available (a published point estimate produced by an unpublished neural-network configuration under a fully specified resampling protocol). Audits #28/#29 consumed four of them (diabetes, Australian credit, satimage, vehicle).

**Rule applied:** take *every* remaining StatLog Backprop row that (a) has legally public data, (b) reports a proportion/percentage error metric (not an average cost), and (c) has an unambiguously recoverable attribute set and split. The full remaining pool and its disposition:

| Row | Public data? | Proportion metric? | Unambiguous? | Taken |
|---|---|---|---|---|
| Letters (Table 9.7) | yes (UCI 59) | yes | yes | **YES** |
| Shuttle (Table 9.19) | yes (UCI 148) | yes | yes | **YES** |
| Image segmentation (Table 9.10) | yes | yes | **NO** — StatLog used **11 of the 19** attributes (confirmed in the book's own measures table, Table 9.30: `p = 11`) and **never says which 11** | no |
| DNA (Table 9.21) | partly | yes | **NO** — Backprop used the "one-of-four" 240-binary coding; the distributed StatLog/LIBSVM file carries the 180-binary coding | no |
| Heart (9.15), German credit (9.18), head injury (9.14) | yes | **NO** — average-cost metric, not a proportion | — | no |
| Cred.Man, Dig44, KL, Chrom, Tech, Belg I/II, Faults, Cut20/50, Tsetse | **NO** (not publicly distributed) | — | — | no |

So the rule selects letters and shuttle, and it selects *both* — not one. This matters, and it is the reason the rule is written down: **the two rows' expected drifts point in opposite directions** (see "Pre-registered expectations" below). Taking only the one I expect to drift hard would have been a hypothesis-favorable cherry-pick on the last audit before the confirmatory test fires. Taking the whole remaining feasible pool makes that impossible.

## Data checks (counting only — done BEFORE this commit, NO reproduction code run)

- **Letters:** UCI id 59, `letter-recognition.data`, md5 `6a2d740def5d13ea6096272546f6d41e`, 712 565 B. 20 000 rows × 17 columns (1 class letter + 16 integer attributes); attribute values span exactly 0–15, as the book states; 26 classes present.
- **Shuttle:** UCI id 148 (`statlog+shuttle`), `shuttle.trn` md5 `53cbd0c3ae4986fdf48b0570978b92bc` (43 500 rows) and `shuttle.tst` md5 `279c252ee3b56ae6016825afd6821ee7` (14 500 rows), each 10 columns (9 attributes + class), 7 classes, no missing values. The 43 500 / 14 500 counts match StatLog's stated split **exactly**, and the split is distributed as two files — so for shuttle there is **no split discretion at all**.
- **Pre-run arithmetic note on the letters split (flagged NOW, before any model is fitted).** StatLog's Default (majority-class) row for letters is train 0.955 / test 0.960. Taking the file-order split (first 15 000 rows train, last 5 000 test) gives Default train **0.9592** / test **0.9566** — close, but the two are *reversed* relative to the book (StatLog has train < test; the file-order split has train > test). **The published 15 000/5 000 split is therefore not the file-order split, and StatLog never states how it was drawn.** This is a genuine, unrecoverable discretion item, it is recorded here before data, and it feeds rubric point 1/5 below. The primary configuration pins the file-order split as the only deterministic reading of "(train, test) = (15 000, 5 000)"; a seeded random stratified split is run as a labelled sensitivity check.

## Blind discretion rubric (scored from the book + scikit-learn 1.7 docs ONLY, before any code)

**Letters — score 5/5.**

1. **Tie-breaking / randomization — 1.** No seed for weight initialisation or epoch shuffling, and — as the data check above proves — **the train/test split itself is unpublished and not recoverable from file order**.
2. **Regularization / smoothing — 1.** No weight decay, penalty, or early-stopping-as-regularization stated. sklearn must default (`alpha=1e-4`).
3. **Initialization — 1.** Starting weights never specified; the package's own default is not documented in the book.
4. **Stopping criteria / tolerances — 1.** No epoch count, tolerance, or learning-rate schedule. The book reports only a training *time* (277 445 s) — which is a measurement, not a specification.
5. **Preprocessing — 1.** Input scaling for Backprop is never stated. (The book's remark that "all the attributes are pre-scaled" in §9.3.4 is a comment on the *data* — integers 0–15 — offered to explain why k-NN does well; it is not a statement of what Backprop's input layer received.) Split construction also unstated, per point 1.

**Shuttle — score 5/5.**

1. **Tie-breaking / randomization — 1.** No seed for weight init or shuffling. (The split is fixed and distributed, so *that* sub-item does not fire here — but the RNG items do, and the rubric awards one point per numbered item, not per sub-item.)
2. **Regularization / smoothing — 1.** As above; nothing stated.
3. **Initialization — 1.** As above; nothing stated.
4. **Stopping criteria / tolerances — 1.** As above; only a training time (5 174 s) is reported.
5. **Preprocessing — 1.** Input scaling never stated, and on shuttle it is the single most consequential unstated choice: the 9 integer attributes have wildly different ranges, and scikit-learn's own MLP documentation warns that "Multi-layer Perceptron is sensitive to feature scaling".

Discretion axis NOT captured by the frozen 5-point rubric, recorded for honesty (identical to audits #28/#29): the **hidden-layer size** was CV-tuned by StatLog and never published, so architecture is a sixth free axis on both rows. The rubric is fixed by `PREREG_DRIFT.md` and is NOT extended post hoc; 5/5 is if anything an *under*-count on both rows.

**Both rows therefore land at 5/5 — the same score, the same algorithm, the same implementation, the same reproducer, on the same day.** That is the design; see secondary prediction B.

## Reproduction plan (pinned before running)

Per master seed m ∈ {0, 1, 2} (seed 0 primary for the verdict; tracker drift per row = 3-seed mean |reproduced − published|):

1. Load the md5-pinned files above.
2. **Primary configuration — the faithful modern default (identical to audits #28/#29, for cross-audit comparability):** `Pipeline(StandardScaler(), MLPClassifier(random_state=m))`, every other `MLPClassifier` argument at its library default (`hidden_layer_sizes=(100,)`, `activation='relu'`, `solver='adam'`, `alpha=1e-4`, `learning_rate_init=1e-3`, `max_iter=200`, `shuffle=True`, `tol=1e-4`, `n_iter_no_change=10`). The scaler is fit on the **training set only**.
3. **Splits:** letters — first 15 000 rows train, last 5 000 test (file order; see the pre-run note). Shuttle — the distributed `shuttle.trn` / `shuttle.tst`.
4. Row value = 100 × (test misclassification rate). Published comparators: **32.7** (letters) and **0.43** (shuttle), both in percentage points.
5. Convergence warnings (if `max_iter=200` is hit) are **counted and reported**, never suppressed and never fixed by raising `max_iter` — raising it would be moving a defaulted choice after seeing data.
6. Labelled sensitivity checks (reported, never the verdict): (a) **no scaler** — raw features into `MLPClassifier` defaults; (b) letters with a seeded **stratified random** 15 000/5 000 split; (c) **MinMaxScaler** instead of StandardScaler (both feature sets are bounded integers); (d) shuttle with `hidden_layer_sizes=(5,)` — the only hidden-node count the book ever discloses for *any* Backprop row (vehicle, audit #29), to probe the partial-specification trap that audit #29 identified.

## Pre-registered tolerance and verdict rule

- **Tolerance: ±5.0 pp for letters** — the score-5 bar set by precedent in audits #8/#28/#29 and not moved.
- **Tolerance: ±1.5 pp for shuttle** — deliberately tighter, and the reason is declared now, before data: the published value is **0.43 pp**. A ±5.0 pp bar on a 0.43 pp claim is unfalsifiable (it would confirm any reproduction from 0 % to 5.43 %, i.e. worse than the book's *Discrim* row). Bars in this program are priced by the blind rubric score *and* by the scale of the claim (cf. audit #10's ±0.1 pp on certified values, audit #26's ±2.0 pp on a low-error target). **The bar affects only the CONFIRMED/DISCREPANCY verdict; it has no effect whatsoever on the |drift| value that enters the drift study**, so no choice of bar can bias the pre-registered hypothesis test.
- **CONFIRMED** for a row if |reproduced − published| ≤ its bar at seed 0 in the primary configuration; **DISCREPANCY** if it exceeds; **COULD-NOT-RUN** if data access or the 45 s sandbox cap blocks execution. Each row carries its own verdict.

## Pre-registered expectations (stated openly, BEFORE running)

Pre-registration means declaring the expectation, including an uncomfortable one. Having read Table 9.7 and Table 9.19, I cannot un-form a prior, so I state it:

- **Letters: I expect a large DISCREPANCY.** A 2026 default MLP should land far below the book's 32.7 % — my prior is roughly 3–8 % test error, i.e. an expected |drift| of **~25–30 pp**, which would be by far the largest drift in the confirmatory set. StatLog's own commentary supports this reading (Backprop ranks 19th of 22 on letters, behind LVQ at 7.9 %, on a dataset where the book expects neural methods to do well).
- **Shuttle: I expect CONFIRMED with a very small drift.** Published 0.43 % sits essentially on the floor of a near-noise-free problem (the book: "arbitrarily small error rates are possible given sufficient data"). My prior is 0.1–0.5 % test error, i.e. |drift| **≲ 0.5 pp**.

**These two expectations point in opposite directions at an identical rubric score of 5/5.** That is precisely why the selection rule takes both. Whatever happens, one of these rows will cut against the program's hypothesis.

## Secondary pre-registered predictions

- **Secondary A (the standing clause, re-tested):** both rows' 3-seed |drift| is strictly greater than **1.96 pp** (the largest score-2 drift in the set). This clause failed at score 5 in audits #8 and #28 and held for the first time in audit #29. **I expect it to FAIL here, on shuttle** — and I register it anyway, because it is the standing clause and because a failure driven by a floor-bound target is exactly the diagnostic information the n=30 honesty section needs.

- **Secondary B (the decisive floor-headroom test — the real point of this audit):** **letters' 3-seed |drift| exceeds shuttle's by more than 5×.** The floor-headroom confounder (raised in audits #25/#26, contradicted by #27) says |drift| is bounded by a target's distance to the 0 % error floor, independently of discretion. Every prior test of it confounded headroom with rubric score, dataset, paper, and algorithm. **This pair does not:** same book, same algorithm, same unpublished implementation, same rubric score (5/5), same reproducer, same session — and headroom of **32.7 pp versus 0.43 pp**, a 76× ratio. If B holds, floor-headroom is established as a live confounder *at constant discretion*, which means the rubric score alone cannot explain |drift| and the n=30 rho is partly a headroom effect. **This is a hypothesis-threatening prediction, registered before data, on the last audit before the confirmatory test.**

- **Secondary C (mechanism probe, replicating audits #28/#29):** for BOTH rows, the **unscaled** sensitivity configuration's |drift| is strictly greater than the scaled primary's |drift| — i.e. rubric point 5 is a live drift driver, not an inert checkbox.

## Tracker context at registration

n = 29 confirmatory audits, 65 (score, |drift|) points, exploratory rho = **0.590**, p = 2.4e-07. Score-5 bucket: **4 points** (1.11, 1.83, 1.93, 4.18). These two rows are pre-registered to land at score 5, taking that bucket to **6 points** and the set to **n = 31, 67 points** — at which the `PREREG_DRIFT.md` one-shot confirmatory test (rho > 0.5, p < 0.01, tested once at n ≥ 30) becomes **due**.

Disclosure for the n=30 honesty section, recorded now rather than later: **5 of the 6 score-5 points will come from one book and one algorithm** (StatLog Backprop), and the 6th (audit #8, Sigillito 1989) is also a gradient-trained neural net. The high-discretion end of this study is therefore a *source-and-family-concentrated* sample. That is not a flaw that can be fixed before the test fires — high-discretion published claims with public data are genuinely scarce — but it is a limitation on the interpretation of any rho the test produces, and it must appear in `RESULTS_DRIFT.md`.

## Results

Runner: `audits/audit_statlog_backprop3_run.py`. Raw per-cell records: `audits/statlog_backprop3_raw.json`. Environment: scikit-learn 1.7.2, numpy 2.2.6, CPU only. Data md5s re-verified at run time inside the runner (asserts), matching the pre-registration exactly.

Primary configuration (StandardScaler + `MLPClassifier` defaults), master seed 0 = the verdict seed:

| Row | Published | Reproduced (seed 0) | Drift | Bar | Verdict |
|---|---|---|---|---|---|
| Backprop, letters (15 000/5 000) | 32.7 | **5.36** | **-27.34 pp** | ±5.0 | **DISCREPANCY** |
| Backprop, shuttle (43 500/14 500) | 0.43 | **0.0552** | **-0.375 pp** | ±1.5 | **CONFIRMED** |

All three master seeds, primary configuration:

| Row | seed 0 | seed 1 | seed 2 | 3-seed mean \|drift\| |
|---|---|---|---|---|
| letters | 5.36 | 5.60 | 4.54 | **27.53 pp** |
| shuttle | 0.0552 | 0.0828 | 0.0621 | **0.36 pp** |

**Standardized drift for the tracker: letters 27.53 pp, shuttle 0.36 pp — both at blind rubric 5/5.**

Verdicts hold at every seed: letters exceeds its ±5.0 pp bar by more than 5x on all three seeds; shuttle sits inside its ±1.5 pp bar by a factor of four on all three. **Letters is the largest drift in the confirmatory set** (previous maximum: 11.21 pp, audit #29's vehicle row). Shuttle is one of the program's smallest non-zero drifts.

Convergence, reported as pre-registered and NOT fixed: **letters hit `max_iter=200` without meeting `tol` at every seed** (0/3 converged) — and still beat the published number by 27 pp. Shuttle converged properly at every seed (74-86 iterations of a 200 cap). So the row that failed to converge is the one that crushed the published claim; the stopping-rule discretion is not what drives this drift.

### Secondary prediction A — **FAILED** (as pre-registered, and as expected)

Both rows' 3-seed |drift| > 1.96 pp: letters **27.53 OK**, shuttle **0.36 NO**. The clause fails on shuttle. This is the third failure of the standing clause at score 5 (audits #8, #28, and this row) against two passes (#29, and letters here) — and it is now clear *why* it keeps failing, which is the subject of prediction B.

### Secondary prediction B — **HELD, and far more sharply than registered**

Registered: letters' |drift| exceeds shuttle's by **more than 5x**. Observed: **75.8x** (27.53 vs 0.36).

The number that matters is not 75.8 but what it is 75.8 *of*:

| | published error (= headroom above the 0 % floor) | 3-seed \|drift\| | drift as % of headroom |
|---|---|---|---|
| letters | 32.7 pp | 27.53 pp | **84.2 %** |
| shuttle | 0.43 pp | 0.36 pp | **84.5 %** |
| **ratio** | **76.0x** | **75.8x** | **1.00x** |

The two rows have **the same rubric score, the same algorithm, the same unpublished 1994 implementation, the same 2026 reproducer, the same library defaults, the same session** — and their absolute drifts differ by 76x. But their *relative* drifts are identical to three significant figures: the 2026 default MLP removes **~84 %** of the published error on both. A modern MLP is, on both datasets, about six times more accurate than StatLog's Backprop; on letters that is worth 27 pp, on shuttle it is worth 0.4 pp.

**This establishes the floor-headroom confounder at constant discretion**, which no prior audit could do (audits #25/#26 raised it, #27 gave evidence against it, but all of them confounded headroom with rubric score, paper, algorithm, and dataset). The consequence for the program's own hypothesis is direct and unfavourable, and it is stated here rather than in a footnote:

> **|drift| measured in percentage points is not a scale-free measure of reproducibility.** It is approximately (relative reproduction error) x (the published value's headroom). Two claims that are *equally* reproducible in the only sense the reproducer controls — both reproduced to within 16 % of the published error — contribute 27.53 and 0.36 to the same correlation. The blind rubric scores discretion; it does not score headroom; and the pre-registered test correlates the rubric against a quantity that demonstrably depends on both.

### Secondary prediction C — **FAILED, INVERTED on both rows**

Registered: the unscaled configuration's |drift| exceeds the scaled primary's on both rows. Observed: it is **smaller** on both.

| Row | primary \|drift\| | no-scaler \|drift\| | MinMax \|drift\| |
|---|---|---|---|
| letters | 27.34 | **23.40** | **18.62** |
| shuttle | 0.375 | **0.285** | *(infra-blocked, see honesty item 2)* |

The mechanism is unambiguous once the *sign* of the drift is read. In audits #28/#29 the reproduction landed near the published value, so anything that degraded the model pushed it away and inflated |drift|. Here the reproduction lands **far better** than the published value (drift is negative on every row and every seed), so degrading the model — dropping the scaler, or squashing the features with MinMax — moves it *back toward* the 1994 number and **shrinks** |drift|. Removing the scaler recovers 4 pp of the letters gap; MinMax recovers 9 pp.

So prediction C's direction is not a property of the preprocessing discretion at all — **it is a property of the sign of the drift.** Rubric point 5 is live and large on these rows (an 8.7 pp swing across scaler choices on letters), exactly as scored; but "unstated discretion inflates |drift|" is only true when the published claim is at least as good as the modern default. When the published claim is *worse* than the modern default — which is what a 32-year-old neural net on 26-class letter recognition is — the same discretion can make the reproduction *look* more faithful. This is the **competence confounder** (audit #28) shown to have a sign, and it is a second unfavourable finding for the pp-drift measure.

### Other sensitivity checks (labelled; never the verdict)

- **Letters, seeded stratified random 15 000/5 000 split** (the split StatLog actually used is unpublished — see the pre-run data check): **4.88** vs the file-order split's 5.36 — a 0.48 pp effect. The unrecoverable split discretion is real but **small**, and it moves the drift *away* from the published value, not toward it. The DISCREPANCY is not an artifact of the split choice.
- **Shuttle, `hidden_layer_sizes=(5,)`** — the only hidden-node count the book discloses for any Backprop row (vehicle, audit #29), applied here as a partial-specification probe: **0.1103** vs the default-100 primary's 0.0552. It roughly doubles the error and still lands 0.32 pp below the published value — i.e. on shuttle the partial-specification trap that broke audit #29's vehicle row does **not** bite; the row is CONFIRMED either way (0.32 pp vs 0.37 pp drift).

## Honesty section

1. **The letters DISCREPANCY is not a challenge to the 1994 claim.** Per program policy, verdicts are numbers, never accusations, and unexplained gaps default to environment differences. StatLog's Backprop ranked 19th of 22 on letters and the book itself flags the result as disappointing for a neural method; the reproduction says only that a 2026 library-default MLP, trained in ten seconds on a laptop CPU without converging, reaches 5.4 % where the 1994 configuration reported 32.7 % after 277 445 seconds of training. What drifted is the *portability of the published number to modern defaults*, which is the only thing this program ever measures. Thirty-two years of defaults — adam, ReLU, Glorot init, 100 hidden units, standardized inputs — are doing the work.

2. **One registered sensitivity cell did not run: shuttle x MinMaxScaler.** It was attempted 11 times in fresh processes and never completed inside the sandbox's hard 45 s per-call cap (the same `.fit` under StandardScaler converges in 9 s; MinMax on shuttle's wildly-ranged integer columns evidently fails to reach `tol` and grinds against `max_iter`). No number for that cell was ever observed, the block is outcome-independent, and no configuration was altered to force it through. It is a *sensitivity* cell, not a registered primary cell: **all 6 primary cells ran, so both verdicts and both tracker points are complete.** Reported as a failure, not quietly dropped.

3. **Executor/planner split (eleventh audit under it).** The 12 cells were dispatched to a subordinate executor by exact pre-registered command; the executor was given no authority over configuration or interpretation. The auditing session then **independently re-ran both verdict cells (letters seed 0, shuttle seed 0) and reproduced them bit-identically** (5.36 / 0.0552), confirmed the runner on disk was byte-identical to the pinned script (`cmp`), and recomputed every drift, every mean, and both secondary tests from the raw JSON rather than from the executor's summary. The published 65-point rho (0.590) was reproduced from the printed list before the two new points were appended.

4. **The bar asymmetry (±5.0 letters / ±1.5 shuttle) was declared before data and did not affect the drift study.** It affects only the verdict labels. Note that letters would be a DISCREPANCY under *any* bar this program has ever used, and shuttle a CONFIRMED under any bar >= 0.4 pp — so no bar choice could have changed either verdict.

5. **Direction of drift.** Both rows drift in the *favourable* direction (the modern reproduction beats the 1994 published number) at every seed. The program has now seen favourable drift on all six StatLog Backprop rows audited (#28, #29, #30). Whatever else is true, the 1994 Backprop entries are systematically pessimistic relative to modern defaults.

6. **What this audit costs the program's hypothesis.** Prediction B was registered as hypothesis-threatening and it landed. The rubric cannot distinguish these two rows — it scores both 5/5, correctly — and yet they contribute 27.53 and 0.36 to the same Spearman correlation. The high-discretion end of the confirmatory set is now 6 points spanning 0.36 -> 27.53 pp, a 76x range, driven not by discretion (constant) but by headroom (76x). This does **not** license any adjustment to the pre-registered test: the bars are not moved, the measure is not changed, no point is dropped, and `PREREG_DRIFT.md` stands exactly as registered. It licenses one thing only — that `RESULTS_DRIFT.md` must report the confounder alongside whatever rho the one-shot test produces.
