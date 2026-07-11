# RESULTS: Does implementation discretion predict reproducibility drift?

## Verdict: **SUPPORTED**

**Spearman rho = 0.587** (bar: > 0.5), **p = 1.7 × 10⁻⁷** two-sided (bar: < 0.01), over the closed confirmatory set of **n = 31 audits / 67 (score, |drift|) points**. Permutation cross-check: none of 10⁶ random score permutations reached |rho| ≥ 0.587 (p < 10⁻⁶, seed 0). The pre-registered hypothesis — that the amount of implementation discretion a published ML claim leaves to the reproducing library predicts the absolute reproducibility drift of the reproduced number — is supported at the registered bar.

## Provenance (what was fixed before this number existed)

- **2026-07-05 — hypothesis, bar, rubric, and stopping rule registered** (`audits/PREREG_DRIFT.md`, commit `ad8aa31`), before any confirmatory audit was selected or run. The 5 earlier exploratory audits that generated the hypothesis were excluded; the confirmatory set started at n = 0.
- **2026-07-05 → 2026-07-11 — 31 confirmatory audits** (32 attempted; audit #4 was COULD-NOT-RUN and contributes nothing), each under the two-commit rule: blind rubric score and expected-value tolerance committed with an empty results section before any reproduction code ran.
- **2026-07-11 (audit #30 batch, commit `ff7af3bd`) — set CLOSED** at 31 audits / 67 points, with a binding hand-off written *before* this test fired: the next run executes the one-shot test over exactly the 67 printed points, adds no points, re-scores nothing, and publishes this file either way. "Keep auditing until rho looks right" was thereby removed as an option.
- **2026-07-11 (this session) — test executed once.** Runner `audits/drift_confirmatory_test.py`, frozen dataset `audits/drift_confirmatory_points.json` (verified an exact machine transcription of the tracker's printed list at `ff7af3bd`), raw output `audits/drift_confirmatory_result.json`. This session added no audits and no points.

## The test

| Quantity | Value |
|---|---|
| Points (columns/rows across 31 audits) | 67 |
| Spearman rho (score vs \|drift\| pp) | **0.5875** |
| p, scipy `spearmanr` two-sided (a pre-registered option) | **1.73 × 10⁻⁷** |
| p, Monte Carlo permutation (10⁶ resamples, seed 0) | **< 10⁻⁶** |
| Pre-registered bar | rho > 0.5 AND p < 0.01 |
| **Verdict** | **SUPPORTED** |

Drift per point is the 3-seed mean |reproduced − published| in percentage points on the paper's own metric; scores are the 0–5 blind discretion rubric of `PREREG_DRIFT.md`, committed before each reproduction ran.

### Drift by rubric score

| Score | n | median \|drift\| (pp) | mean | max |
|---|---|---|---|---|
| 0 | 4 | 0.00 | 0.03 | 0.11 |
| 1 | 3 | 1.03 | 0.71 | 1.09 |
| 2 | 21 | 0.04 | 0.37 | 1.96 |
| 3 | 16 | 0.46 | 1.73 | 10.35 |
| 4 | 17 | 0.99 | 2.16 | 11.21 |
| 5 | 6 | 1.88 | 6.16 | 27.53 |

Mean and max drift rise monotonically from score 2 upward, and the three verdict-level DISCREPANCIES in the program all sit at scores 4–5 (StatLog letters −27.34 pp, StatLog vehicle +13.22 pp) or outside this set's scope (NIST Filip, a numerical-policy artifact at score 0 that contributes its honest 0.11 pp). The medians are *not* perfectly monotone: score 1 (n = 3, dominated by LFW's live unseeded randomization) sits above scores 2–4, and score 2's median is 0.04 pp because that bucket holds most of the library-demo/docs claims that reproduce exactly. See honesty items 5–6.

## Full confirmatory table

| # | Score | \|drift\| pp | Source (audit) |
|---|---|---|---|
| 1 | 2 | 0.59 | Breiman-2001 RF sonar, Single Input (#1) |
| 2 | 2 | 0.94 | Breiman-2001 RF sonar, Selection (#1) |
| 3 | 3 | 8.95 | Gorman–Sejnowski 1988 sonar MLP, 12 hidden (#2) |
| 4 | 3 | 10.35 | Gorman–Sejnowski 1988 sonar MLP, 24 hidden (#2) |
| 5 | 2 | 0.00 | Hsu–Chang–Lin svmguide1, unscaled defaults (#3) |
| 6 | 2 | 0.00 | Hsu–Chang–Lin svmguide1, scaled defaults (#3) |
| 7 | 1 | 0.00 | Hsu–Chang–Lin svmguide1, C=2 γ=2 (#3) |
| 8 | 2 | 1.96 | LeCun-1998 MNIST linear via least squares (#5) |
| 9 | 3 | 1.08 | Breiman-2001 One Tree, ionosphere (#6) |
| 10 | 3 | 1.34 | Breiman-2001 One Tree, sonar (#6) |
| 11 | 2 | 0.02 | Aeberhard-1992 wine LOO, LDA (#7) |
| 12 | 2 | 0.04 | Aeberhard-1992 wine LOO, QDA (#7) |
| 13 | 2 | 0.59 | Aeberhard-1992 wine LOO, 1NN (#7) |
| 14 | 5 | 1.11 | Sigillito-1989 ionosphere linear perceptron (#8) |
| 15 | 2 | 0.05 | Sigillito-1989 / Aha ionosphere 1NN (#8) |
| 16 | 4 | 0.23 | Freund–Schapire 1996 glass, C4.5 alone (#9) |
| 17 | 4 | 1.36 | Freund–Schapire 1996 glass, boosted C4.5 (#9) |
| 18 | 0 | 0.00 | NIST StRD LLS certified R², Longley (#10) |
| 19 | 0 | 0.11 | NIST StRD LLS certified R², Filip (#10) |
| 20 | 4 | 2.43 | Freund–Schapire 1996 bagging C4.5, glass (#11) |
| 21 | 4 | 0.33 | Freund–Schapire 1996 bagging C4.5, iris (#11) |
| 22 | 2 | 0.04 | sklearn 1.9.0 docs k-means digits, k-means++ (#12) |
| 23 | 2 | 0.00 | sklearn 1.9.0 docs k-means digits, random (#12) |
| 24 | 2 | 0.02 | sklearn 1.9.0 docs k-means digits, PCA-based (#12) |
| 25 | 3 | 0.08 | Joulin-2016 fastText AG News, h=10 (#13) |
| 26 | 2 | 0.11 | Joulin-2016 fastText AG News, h=10 bigram (#13) |
| 27 | 3 | 0.95 | Breiman-1996 Bagging glass, e_S (#14) |
| 28 | 3 | 1.37 | Breiman-1996 Bagging glass, e_B (#14) |
| 29 | 2 | 0.00 | xgboost v1.7.6 CLI mushroom demo, test r0 (#15) |
| 30 | 2 | 0.00 | xgboost v1.7.6 CLI mushroom demo, test r1 (#15) |
| 31 | 2 | 0.00 | xgboost v1.7.6 CLI mushroom demo, train r0 (#15) |
| 32 | 2 | 0.00 | xgboost v1.7.6 CLI mushroom demo, train r1 (#15) |
| 33 | 4 | 2.99 | Freund–Schapire 1996 ionosphere, C4.5 alone (#16) |
| 34 | 4 | 0.85 | Freund–Schapire 1996 ionosphere, boost (#16) |
| 35 | 4 | 1.34 | Freund–Schapire 1996 ionosphere, bag (#16) |
| 36 | 4 | 3.36 | Freund–Schapire 1996 sonar, C4.5 alone (#17) |
| 37 | 4 | 0.99 | Freund–Schapire 1996 sonar, boost (#17) |
| 38 | 4 | 6.86 | Freund–Schapire 1996 sonar, bag (#17) |
| 39 | 2 | 0.83 | Breiman-2001 glass Forest-RI, Single Input (#18) |
| 40 | 2 | 1.81 | Breiman-2001 glass Forest-RI, Selection (#18) |
| 41 | 2 | 0.46 | Breiman-2001 diabetes Forest-RI, Single Input (#19) |
| 42 | 2 | 0.33 | Breiman-2001 diabetes Forest-RI, Selection (#19) |
| 43 | 1 | 1.09 | sklearn-1.9.0 docs LFW eigenfaces, accuracy (#20) |
| 44 | 1 | 1.03 | sklearn-1.9.0 docs LFW eigenfaces, weighted-F1 (#20) |
| 45 | 0 | 0.00 | sklearn-1.7.2 seeded doctests, GBC hastie test acc (#21) |
| 46 | 0 | 0.00 | sklearn-1.7.2 seeded doctests, AdaBoost train acc (#21) |
| 47 | 3 | 0.32 | Breiman-1996 Bagging ionosphere, e_S (#22) |
| 48 | 3 | 0.39 | Breiman-1996 Bagging ionosphere, e_B (#22) |
| 49 | 4 | 2.61 | Freund–Schapire 1996 vehicle, C4.5 alone (#23) |
| 50 | 4 | 0.88 | Freund–Schapire 1996 vehicle, boost (#23) |
| 51 | 4 | 0.70 | Freund–Schapire 1996 vehicle, bag (#23) |
| 52 | 3 | 0.64 | Breiman-1996 Bagging diabetes, e_S (#24) |
| 53 | 3 | 0.28 | Breiman-1996 Bagging diabetes, e_B (#24) |
| 54 | 4 | 0.19 | Freund–Schapire 1996 segmentation, C4.5 alone (#25) |
| 55 | 4 | 0.06 | Freund–Schapire 1996 segmentation, boost (#25) |
| 56 | 4 | 0.41 | Freund–Schapire 1996 segmentation, bag (#25) |
| 57 | 3 | 0.46 | LeCun-1998 MNIST 40-PCA+quadratic (#26 tracker repair) |
| 58 | 3 | 0.21 | Breiman-1996 Bagging breast cancer, e_S (#26) |
| 59 | 3 | 0.45 | Breiman-1996 Bagging breast cancer, e_B (#26) |
| 60 | 3 | 0.32 | Breiman-1996 Bagging waveform, e_S (#27) |
| 61 | 3 | 0.44 | Breiman-1996 Bagging waveform, e_B (#27) |
| 62 | 5 | 1.93 | StatLog-1994 Backprop, diabetes Table 9.20 (#28) |
| 63 | 5 | 1.83 | StatLog-1994 Backprop, Australian credit Table 9.3 (#28) |
| 64 | 5 | 4.18 | StatLog-1994 Backprop, satimage Table 9.9 (#29) |
| 65 | 4 | 11.21 | StatLog-1994 Backprop, vehicle Table 9.6 (#29) |
| 66 | 5 | 27.53 | StatLog-1994 Backprop, letters Table 9.7 (#30) |
| 67 | 5 | 0.36 | StatLog-1994 Backprop, shuttle Table 9.19 (#30) |

## What the result means (and does not mean)

A published number's vulnerability to reproducibility drift is, to a rank-correlation of ~0.59, predictable *before running anything* from how much of its pipeline the claim leaves for the reproducing library to fill in. Zero-discretion claims (certified values, fully seeded doctests) sit on the drift floor; fully underspecified 1980s–90s neural-network claims carry the program's largest drifts and all of its executed discrepancies. The practical reading: when auditing or reusing a published ML number, the blind rubric of `PREREG_DRIFT.md` is a cheap, pre-hoc triage for how much reproduction tolerance to budget.

It does **not** mean high-scoring papers are wrong or careless: per the program's standing rule, verdicts are numbers, never accusations, and every unexplained gap defaults to environment differences. Several high-discretion claims reproduced almost exactly (StatLog shuttle, 0.36 pp at score 5); the score prices *risk*, not error.

## Honesty section

All items 1–4 were logged in the tracker BEFORE this test ran, as required by the binding hand-off; none was used to adjust the test.

1. **Floor-headroom confounder (established at constant discretion, audit #30).** |drift| in pp ≈ (relative reproduction error) × (published value's headroom above the 0% floor), and the rubric scores only the first factor. The cleanest evidence sits inside one audit: StatLog letters and shuttle share book, algorithm, reproducer, defaults, session, and blind score 5/5; the modern default removes an almost identical share of published error on both (84.2% vs 84.5%), yet their |drift|s differ 76× (27.53 vs 0.36 pp) purely because letters has 32.7 pp of headroom and shuttle 0.43 pp. Part of the score→drift correlation is therefore mediated by high-discretion claims tending to be older, harder, higher-error claims. A relative-drift re-analysis would be a *new, unregistered* estimand and is left explicitly to future exploratory work.
2. **Competence confounder, with a sign (audits #28, #30).** |drift| = discretion available × how well the reproducer resolves it; the rubric scores only availability. Audit #28's secondary B showed dropping one unstated preprocessing choice inflates drift 2.5–5.3×; audit #30's inverted secondary C showed the sign condition — unstated discretion inflates |drift| only when the published claim is at least as good as the modern default (when the modern default *beats* the published number, resolving discretion badly moves the reproduction back *toward* it).
3. **Partial-specification trap (audit #29).** The set's second-largest drift (11.21 pp) sits at score 4, not 5: honoring a *disclosed* architecture choice without its undisclosed training budget can drift more than full underspecification. The rubric counts unspecified items; it does not model interactions between specified and unspecified ones.
4. **Source concentration at the high end.** 5 of the 6 score-5 points come from one book, one algorithm, and one unpublished 1994 implementation (StatLog Backprop); the 6th (Sigillito 1989) is also a gradient-trained neural network. In this set, "maximal discretion" and "1990s neural-network claim" are empirically confounded; the high end of the correlation should be read as *that family's* drift behavior until other score-5 families exist.
5. **Points are not independent.** 67 points come from 31 audits and ~13 source papers/claim classes; multi-row audits share data, code, and reproducer decisions, and the scipy p-value assumes independent observations. Labeled EXPLORATORY aggregation checks (computed this session, after the confirmatory number): audit-level means (29 groups as printed in the tracker; the #26 repair point groups with audit #26) give rho = 0.638, p = 2.0 × 10⁻⁴; source-cluster means (13 clusters) give rho = 0.756, p = 2.8 × 10⁻³; Kendall τ on the full set = 0.458, p = 7.9 × 10⁻⁷. The registered bar (rho > 0.5, p < 0.01) survives every aggregation level, including the harshest.
6. **Non-monotone medians at the low end.** Score 1 (n = 3) has a higher median than scores 2–4, driven by LFW's live unseeded randomization — recorded at audit #20 as evidence that discretion *type* (live randomization vs pinned-but-unspecified choices) may matter as much as count. Score 2's 0.04 pp median partly reflects target composition: that bucket holds most library-docs/demo claims, which are young and same-engine. Family and claim-class are partially confounded with score throughout.
7. **Sensitivity to the extreme pair (EXPLORATORY, post-test).** Dropping letters (the largest drift): rho = 0.570, p = 6.0 × 10⁻⁷. Dropping shuttle (its hypothesis-undermining twin): rho = 0.608, p = 6.3 × 10⁻⁸. Dropping both: rho = 0.590. The verdict is insensitive to the last audit.
8. **The confirmatory number equals the last exploratory number.** The set was closed before the test, so rho = 0.587 was arithmetically determined by the closure commit; this session only executed the registered computation. The test's value is the *procedure*: bar and stopping rule fixed 2026-07-05 before any confirmatory point existed, every rubric score committed blind before its reproduction ran, and the closure written down before the trigger fired. n = 31 (not exactly 30) because the trigger was crossed during the audit-#30 batch, which included the audit-#26 tracker repair; the hand-off closed the set as-is rather than discarding a completed audit.
9. **Permutation p is Monte Carlo, not exact.** The prereg allowed "exact permutation or scipy spearmanr two-sided"; exact enumeration is infeasible at n = 67, so scipy's two-sided p is primary (a registered option) and the 10⁶-resample Monte Carlo (seed 0, 0 exceedances) is a cross-check. With zero exceedances the standard bound gives p < 10⁻⁶.
10. **Environment.** python 3.10, numpy 2.2.6, scipy 1.15.3, Linux sandbox, CPU only, fully deterministic given the frozen JSON. Runner and raw output are committed beside the dataset. File placed at `results/RESULTS_DRIFT.md` following the repo's RESULTS_* convention (the prereg named the file but not its directory; noted here as an implementation choice).

## Status of the drift study

The pre-registered question is answered and the confirmatory set is closed. Anything further on this data — relative-drift re-analysis (item 1), discretion-type subscales (item 6), cluster-level modeling (item 5), new score-5 families (item 4) — is exploratory or requires a NEW pre-registration, and per VAR rule 6, any external claim built on this result requires named human sign-off.

*Program 2b of the VAR initiative — pre-registered in `audits/PREREG_DRIFT.md` (2026-07-05), set closed at commit `ff7af3bd`, test executed 2026-07-11. Verdicts are numbers, never accusations.*
