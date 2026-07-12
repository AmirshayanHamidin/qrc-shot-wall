# Audit log

Verification-only entries: independent re-runs of published benchmarks against their written claims. Format per entry: what was re-run, how independently, verdict (CONFIRMED / DISCREPANCY), numbers side by side.

## 2026-07-11 (third late session) — B2 (RESULTS_GAP.md): full budget-grid re-run from committed code — **CONFIRMED**

**What was re-run.** The entire B2 pipeline from the repo's own committed code, unmodified: `src/qrc_gap_eval.py` at all four published budgets (4k/40k/400k/4M; 12 strategy cells each incl. the exact floor), the 40k plateau at noise seeds 2–3 via a thin driver calling the committed `run()` verbatim, and both cited reference baselines from their committed generators (`src/qrc_benchmark.py` linear-on-inputs, `src/qrc_full_eval.py` tuned ESN). Everything ran in a scratch directory; the files of record were never written. Driver + comparison summary: `audits/audit_b2_rerun.py` + `audits/b2_rerun_check.json`. Mechanical execution was double-generated this session (a first pass by a delegated executor, then the published check regenerated in a fresh scratch by the committed runner) — identical numbers both times. Environment: numpy 2.2.6, sklearn 1.7.2, qiskit 2.5.0, scipy 1.15.3 (same as all prior audits), CPU.

**Result: bit-identical everywhere full precision is stored.** `results/gap_final.json`'s raw budget sweep reproduces to the last digit (4/4; e.g. 0.5814928957420354 @40k), all three `plateau_seeds_40k` values are bit-identical, and the mitigated sweep matches at its stored 4-dp precision (0.1507/0.1417/0.1282/0.0784). All seven code-backed rows of the 40k strategy table land on the printed 4 dp exactly (raw V=4 0.5815, EMA 0.1568, PCA 0.1521, PCA+EMA 0.1515, EIV 0.1759, V=1 reallocation 0.1417, exact floor 0.0030). Both references reproduce from committed code — linear-on-inputs 0.14825 → 0.1483, tuned ESN 0.01378 → 0.0138 — and as a bonus, the two B1 files of record they live in (`results/qrc_results.json`, `results/qrc_full_results.json`) regenerate **bit-identically** wholesale. Secondary claims verified: diversity-loses-to-SNR (0.1417 vs 0.1568–0.1674 for V=4–8 @40k; the published "0.157–0.167" span is exactly the V=4/V=8 pair); the plateau ≈ inputs-only floor across noise seeds (0.142/0.152/0.150); mitigated first clearly beats the no-quantum baseline near B ≈ 4×10⁵ (0.1282 < 0.1483 at 400k; 0.1417 at 40k is marginally under, as written).

**Two provenance flags (doc-level; no headline depends on them), queued for the doc-fix batch:**

1. **Two of the nine 40k-table rows have no committed generator**: the sim-trained linear denoiser (0.1519) and MLP denoiser (0.1533), along with the non-redundancy probe cited in the secondary findings (rel. err 0.90 linear / 0.89 MLP on 2,300 simulated timesteps). `grep` over `src/` finds no denoiser/MLP code (the only hit is the PCA docstring word "denoising"). Same class of gap that produced the B5 discrepancy — though lower stakes here: both rows are interior points of the fully-reproduced plateau (between 0.1417 and 0.1759) and the wall claim stands without them. Queue: commit a generator or annotate the rows' provenance in RESULTS_GAP.md.
2. `gap_final.json` stores `mitigated` at 4 dp while `raw` is full precision — a harmless but unstated convention (cosmetic).

**Verdict: CONFIRMED.** Every number in RESULTS_GAP.md that has a committed generator reproduces exactly, the raw file of record is untouched, and the plateau/wall claims all check out; the two denoiser rows are flagged as provenance-incomplete rather than challenged. B10 and B12 remain unaudited; queue after this: B10, then B12, plus the doc-fix batch (now including flag #1 above).

---

## 2026-07-11 (second late session) — B11 (RESULTS_TASKFAM.md): full 140-cell re-run from committed code — **CONFIRMED**

**What was re-run.** The entire B11 grid — 4 architectures × (3 classification + 1 regression tasks) × 5 shot budgets × 3 sample seeds = 60 clf + 20 reg cells — from the repo's own committed `src/qrc_taskfam.py` (`run 0/1/2/4` + `agg`), unmodified, followed by the committed `src/qrc_taskfam_fig.py`, unmodified, which regenerates the 60-cell fixed-vs-retrained `retrain_check` addendum and `figures/qrc_taskfam.png`. Everything ran in a scratch directory; the files of record were never written. Driver + comparison summary: `audits/audit_b11_rerun.py` + `audits/b11_rerun_check.json`. Environment: numpy 2.2.6, sklearn 1.7.2, qiskit 2.5.0, scipy 1.15.3 (same as all prior audits), CPU.

**Result: bit-identical.** All 80 grid cells reproduce `results/taskfam_law.json` exactly on every stored field — max |Δ| = 0 for floor, exact, noisy, law_pred, retained and resid — and all 60 retrain-check cells match exactly (max |Δfixed| = |Δretrained| = 0). The aggregate summary is float-identical to the last digit (R² = 0.7929148469844362, MAE = 2.2397152186809275 pp, H2_pass false, H3_pass true, the four per-arch regression retentions at 250 shots). The figure regenerates **byte-identically** (md5 `a2342baee16bdf44735e1f0364c288c6` both sides). Like B6, the pipeline is fully deterministic (fixed Mackey-Glass input seed, sampling seeds `default_rng(1000·ss + S)`, lbfgs logistic readout), which is why bit-identity is achievable across sessions.

**Claim checks — every headline number in the write-up and the README B11 paragraph verified.** Fixed-readout mean 0.490 @250 / 0.558 @64k vs classical-floor mean 0.621 (“0.49 / 0.56 / 0.62”, and “below the inputs-only floor” holds); H2 MAE 2.24 pp, bias +0.59 pp, pooled R² 0.793 (the pre-registered bar fails exactly as published — reported, not moved); observed range 0.434–0.770, std 0.063 (parity ratio 0.198/0.063 ≈ 3.1× ✓); per-task R² = 0.87 / 0.14 / 0.89 and MAE 1.93 / 2.82 / 1.97 pp (updown / accel / prodmed), accel observed range 0.434–0.583 ✓; the arch-4 recovery is predicted as published (obs 0.748 vs law 0.711 on updown @64k; prodmed 0.770 vs 0.763); regression retention −1.06 / −0.02 / 0.57 / 0.78 / 0.86 ✓ (negative at 250 shots ✓); retrain check fixed 0.558 → retrained 0.856 @64k ✓. The “~30–40 pp” fixed-vs-retrained gap is a fair gloss: mean 29.8 pp @64k, per-cell span 7.8–46.3 pp.

**Three doc-level wording flags (no number of record affected), queued for the doc-fix batch rather than silently edited:**

1. “exact accuracy 0.94–0.98” (H1 section) is the span of **per-task mean** exact accuracies (0.944 / 0.952 / 0.983); the per-cell span is 0.874–0.990. The convention should be stated — as written it understates the best cells and hides the weakest (arch-2 accel, 0.874).
2. “341 distinct input levels” reproduces only as a 4-decimal-rounding count; the raw count is 394. Harmless, but the convention is unstated.
3. The illustrative pair “arch 0 `updown`: fixed 0.52 → retrained 0.88” should read **0.53 → 0.90** (0.534 / 0.900 @64k; no budget of that cell yields 0.52 / 0.88).

**Verdict: CONFIRMED.** Every number in RESULTS_TASKFAM.md and the README B11 paragraph reproduces exactly from committed code, including the honest H2 bar failure; the raw file of record is untouched. B11 no longer carries the “not yet re-audited post-B5” caveat; B10 remains unaudited. Queue after this: B2, B10, B12, plus the doc-fix batch (B6 readout sentence + the three items above).

---

## 2026-07-11 — B6 (RESULTS_GATENOISE.md): full 420-cell re-run from committed code — **CONFIRMED**

**What was re-run.** The entire B6 grid (2 architectures × 5 tasks × 6 γ × 7 shot budgets = 420 cells), from the repo's own committed `src/qrc_gatenoise.py`, unmodified — executed in 12 (arch, γ) slices to fit the 45 s sandbox cap via a thin driver (`audits/audit_b6_rerun.py`) that calls the committed module's functions verbatim and recomputes the deterministic γ=0 reference identically per slice. Environment: numpy 2.2.6, sklearn 1.7.2 (same as all prior audits), qiskit 2.5.0, CPU. Comparison summary: `audits/b6_rerun_check.json`.

**Result: bit-identical.** All 420 cells reproduce `results/gate_noise_law.json` exactly — max |Δacc| = 0, max |Δc| = 0, max |Δexact_sep| = 0 — so every aggregate follows: collapse **R² = 0.927091 / MAE 2.893 pp** and naive baseline **R² = 0.851222 / MAE 4.165 pp**, exactly as published. Independently of the re-run, the stored per-cell `pred_collapse` values were recomputed from the raw γ=0 cells (committed interpolation logic re-derived): max abs diff 1.1e-16; the per-γ table (mean c 0.923/0.819/0.677/0.566/0.481; law MAE 1.8→4.6 pp; naive MAE 2.1→7.2 pp) matches every printed digit, and the "advantage widens monotonically with γ" claim holds (0.24 → 2.61 pp). Unlike B5, B6's generator is committed, complete, and regenerates its published raw file exactly; the pipeline is fully deterministic (fixed input seed, sampling seeds 1–3, lbfgs logistic readout), which is why bit-identity is achievable across library versions.

**One write-up mischaracterization, flagged (doc-level, not numeric).** `RESULTS_GATENOISE.md`'s honest-residual section attributes part of the residual to "hold[ing] the linear readout fixed at its noiseless solution rather than retraining under each γ". The committed code does the opposite: `achievable_acc` **retrains** `LogisticRegression(C=1)` on the noisy features of every cell, and the module docstring says so explicitly ("RETRAINED on the noisy features at each budget"). The published numbers are therefore retrained-readout numbers (self-consistent: the γ=0 reference curve is retrained too, so the collapse maps retrained-to-retrained — consistent with B10's later finding that retraining is load-bearing). The stated residual mechanism should be corrected; the residual magnitude (~2.9 pp) and both R² values are unaffected.

**Verdict: CONFIRMED.** Every number in RESULTS_GATENOISE.md and the README B6 paragraph reproduces exactly from committed code; the raw file of record is untouched. One honesty-section sentence mischaracterizes the readout protocol and is flagged for correction (queued, not silently edited here). B6 no longer carries the "not yet re-audited post-B5" caveat; B10/B11 remain unaudited.

---

## 2026-07-04 (later session) — B5 RESTORATION — closes the 2026-07-04 discrepancy

**What was done (consolidation, not a new benchmark).** The three audit findings below are now remediated in the repo:

1. **Missing generator (finding #3) → committed.** `src/qrc_law_predict.py` is now the canonical prediction generator. Its readout convention is pinned in the docstring: raw-feature logistic regression, C = 10⁴, 70% chronological train split — the convention the audit's reconstruction found to match the published `pred` column (MAE 1.2–1.4 pp). From that file onward the law's prediction is defined by committed code, not by a lost script.
2. **Under-seeded observations (finding #2) → 8 documented seeds.** `src/qrc_law_rerun.py` re-ran all 150 classification cells with sampling seeds 1–8 (observation convention unchanged: `law_eval_arch.py`-style retrained readout). Per-seed accuracies are stored in `results/law_rerun.json`, so the noise floor is recomputable by anyone: 8-seed expected MAE floor = **0.91 pp**.
3. **Irreproducible headline (finding #1) → retired and replaced.** `results/RESULTS_LAW.md` now leads with the restored numbers and a provenance note; README and PREPRINT were updated in the same push. `law_theory.json` remains untouched as the historical file of record.

**Restored headline vs audit estimate vs original claim:**

| | R² | noise-corr. R² | MAE | bias |
|---|---|---|---|---|
| Original claim (retired) | 0.991 | — | 1.33 pp | — |
| Audit estimate (2-seed obs) | 0.922 | ≈0.944 | 3.64 pp | — |
| **Restored (8-seed obs, committed code)** | **0.939** | **0.944** | **3.33 pp** | **−0.98 pp** |

Per-budget R²: 0.855 / 0.897 / 0.946 / 0.950 / 0.962 at S = 250 / 1k / 4k / 16k / 64k. Bias runs −2.7 pp (law pessimistic; retraining recovers margin the fixed-readout probit doesn't see, cf. B10) at 250 shots to +0.85 pp at 64k. The audit's noise-corrected estimate (≈0.944) and the independent 8-seed re-run (0.944) agree to three decimals — the audit's characterization of the law is confirmed end-to-end.

**Still open:** the 30 regression cells were not re-run; B6/B10/B11 quote their own statistics and remain unaudited (B6 and B11 are the suggested next audits); `figures/qrc_law.png` still shows the original run and should be regenerated from `law_rerun.json`.

## 2026-07-04 — B5 (RESULTS_LAW.md): full 150-cell re-run from committed code — **DISCREPANCY FOUND**

**What was re-run.** The entire B5 grid, from the repo's own committed code: `src/qrc_law.py build` for all 6 architectures, then `src/law_eval_arch.py` (retrained readout, documented sampling seeds (1,2)) for all 150 classification cells. Environment: numpy + sklearn 1.7.2, fresh workspace. Raw side-by-side cells and aggregates: `results/audit_b5_repro.json`; audit predictor reconstruction: `src/audit_law_theory.py`.

**Three findings, in decreasing order of severity:**

**1. The committed code does not regenerate the published observations.** Reproduced noisy accuracies differ from `law_theory.json`'s `obs` by MAE 3.92 pp, max **17.6 pp**; 12 of 150 cells deviate by >10 pp. Same-pipeline run-to-run noise (independent seed pairs, measured on arch 0) is MAE 3.3 pp / max 9.7 pp — elevated but comparable in aggregate, so the aggregate alone is not damning. The cell-level evidence is: **arch0/parity4/S=1000 published obs = 0.5955, while eight independent sampling seeds of the committed pipeline span 0.728–0.825** — the published value lies far outside the entire seed distribution and cannot be produced by this code at any seed count. Several neighbouring low-S cells show the same pattern. Four alternative protocol conventions were tested (fixed exact-trained readout: chance level, ruled out; weak-regularization retrained readout: MAE 4.1 pp; budget split across virtual nodes: MAE 8.8 pp; alternative C-grids: contradictory by direction) — none regenerates the published obs.

**2. The published pred–obs agreement is tighter than its own protocol's noise floor.** With 2-seed observations, even a *perfect* law would show |pred−obs| MAE ≈ 0.8 × the 2-seed sampling std. Estimated floors vs published MAE, per budget: S=250: ≥3.8 pp floor vs 1.95 pp published; S=1000: ≥2.2 vs 1.86; S=4000: ≥1.8 vs 1.52; S=16000: ≥1.3 vs 0.79; S=64000: ≥0.6 vs 0.53. Published agreement beats the floor at **every** budget, which is statistically implausible for obs generated by the documented 2-seed protocol. (Floor estimated from arch-0 seed pairs, n=5 cells/budget — rough, but the direction is uniform.)

**3. The prediction-generator script is not in the repo.** `RESULTS_LAW.md` cites `src/qrc_law.py` + `src/law_eval_arch.py`, but neither computes the probit prediction; no committed script produces `law_theory.json`'s `pred` column. A reconstruction from the documented formula (σ² = Σ_nodes [Σ p_j q_j² − (p·q)²]/S, pred = mean Φ(signed margin/σ)) with a raw-feature logistic readout (C=10⁴) matches published pred to MAE 1.2–1.4 pp — close, so the formula is real, but the exact convention (readout regularization, margin set) is unrecoverable. The readout convention matters enormously: the *documented* best-C scaled-pipeline readout gives predictions ≈ 0.50 everywhere.

**What survives.** The claim's arithmetic is internally consistent (recomputing from `law_theory.json`: R² = 0.9909, MAE = 1.332 pp — matches the stated 0.991/1.3). And the law itself survives the re-run *qualitatively*: published predictions vs independently reproduced observations give **R² = 0.922, MAE = 3.64 pp** (2-seed obs; correcting for obs sampling noise, R² ≈ 0.944), improving from R² 0.82 at 250 shots to 0.96 at 64k. A zero-parameter prediction at ~3.6 pp MAE across 150 cells is still a strong, useful law.

**Verdict: DISCREPANCY.** The qualitative B5 claim (parameter-free probit law predicts shot-limited accuracy) is **confirmed** at R² ≈ 0.92–0.94. The headline precision **R² = 0.991 / MAE 1.3 pp is not reproducible** from the committed code, the published observations' provenance is unclear for at least a subset of cells, and the prediction generator is missing from `src/`. Until the original generator scripts are restored and the grid re-run with ≥8 documented seeds, README/PREPRINT should quote the reproduced numbers (R² ≈ 0.92, MAE ≈ 3.6 pp, noise-corrected R² ≈ 0.94) or explicitly flag the headline as unaudited. Downstream note: B6/B10/B11 quote or build on the 0.991 figure; their own numbers were not re-checked today. *(Update, later session same day: restoration completed — see entry above.)*

*Caveats: audit ran sklearn 1.7.2 / current numpy — environment differences could shift marginal cells a few pp, but cannot explain 13–18 pp deviations on cells where eight seeds bracket a disjoint range. The published `law_theory.json` remains untouched as file of record.*

## 2026-07-03 — B13 (RESULTS_SMALLMARGIN.md): independent re-implementation — **CONFIRMED**

**Circumstance.** This scheduled session began with a stale CDN copy of the README (pre-B13) and, before discovering the published B13, independently re-implemented the small-margin sweep from the B11/B12 specifications alone — without ever seeing `src/qrc_smallmargin.py` or its write-up. That accident is a stronger audit than a code re-run: same design, independently written code (different sampling-seed convention: `default_rng(1000*seed + S)` vs the published run's; independently re-transcribed pipeline), so agreement tests the *result*, not the file.

**Side-by-side (120 cells each, retrained readout, 250 shots unless noted):**

| Claim in RESULTS_SMALLMARGIN.md | Published | Independent re-run | Verdict |
|---|---|---|---|
| H1 pooled ρ(IPS†, acc@250) fails the +0.5 bar | +0.069 (p=0.75) | +0.109 (p=0.61) | confirmed (fails clearly in both) |
| Within-task ρ @250: updown | +0.88 | +0.90 | confirmed |
| Within-task ρ @250: prodmed | +0.77 | +0.72 | confirmed |
| Within-task ρ @250: accel | +0.60 (p=0.12) | +0.79 (p=0.02) | confirmed direction; magnitude differs (accel is the low-dynamic-range task both write-ups flag) |
| Within-task effect decays with budget | +0.8 → +0.02 @64k | +0.80 → +0.03 @64k | confirmed |
| Star topology-mean acc @250 | 0.784 | 0.789 | confirmed (±sampling seeds) |
| Star vs all-to-all | +4.9 pp, p=0.002 | +5.0 pp, 6/6 config-level wins, p=0.03‡ | confirmed |
| Star vs chain / ring not significant | +1.9 pp, p=0.11–0.22 | +1.6 / +2.4 pp, p=0.44 / 0.56 | confirmed |
| Exact accuracy span 0.961–1.000 | yes | 0.961–1.000 | confirmed exactly |
| Depth-2 collapses IPS | 3–29× | ~6× mean (e.g. all2all updown 0.51→0.02, 25×) | confirmed |
| Fixed readout below classical floor at 250 shots | (B11-consistent) | 0.614 vs floor 0.625; retraining +15.2 pp | confirmed |

† published test uses log IPS, re-run uses raw IPS — rank correlation is nearly invariant to the monotone transform; both reported.
‡ re-run paired at config level (n=6) vs published seed level (n=18), hence the weaker p at the same effect size.

**Verdict: CONFIRMED.** Every qualitative claim and every headline number in RESULTS_SMALLMARGIN.md reproduces under an independent implementation with different sampling seeds; residual differences (≤1.6 pp in accuracies, ≤0.19 in within-task ρ on the weakest task) are consistent with 3-seed sampling variance and protocol microdifferences. No discrepancies found. The re-run's raw cells are preserved in this session's local copy but are deliberately **not** pushed over the published `smallmargin_law.json` — the published file remains the file of record.

*Audit code: independent `qrc_smallmargin.py` variant (this session); pre-registration of its own H1–H3 was written before any run, and its pooled H1/H3 also failed — consistent with the published honest negative.*

*Addendum (2026-07-04): a second scheduled session, also starting from a stale CDN README, independently re-implemented B13 a third time before discovering the published version, again reproducing the headline numbers (pooled ρ = +0.069/p = 0.75, star 0.784, star−chain +1.9 pp in 3/3 seeds, exact span 0.961–1.000, within-task ρ = +0.88/+0.77/+0.60). Recorded for completeness; adds a same-convention replication on top of the different-convention one above.*

*Second addendum (2026-07-04, evening scheduled session) — stale-cache incident #3, plus a repair log. This session too started from a pre-B13 CDN copy of the README/agenda (fetched without a cache-buster; the rule added to the agenda after incident #2 was itself invisible for the same reason), concluded the small-margin sweep was still queued, pre-registered its own H1–H3, and re-implemented B13 from the B11/B12 specs. Its independently written pipeline converged on the same seed convention as the 2026-07-03 audit implementation (`default_rng(1000*seed + S)`) and matched that audit's numbers to reported precision — pooled ρ(log IPS, acc@250) = +0.109 (p = 0.61), within-task ρ = +0.90 / +0.79 / +0.72 (updown/accel/prodmed), stratified rank-within-task ρ = +0.80 (p < 10⁻⁵) decaying to +0.04 @64k, star mean 0.789, exact span 0.961–1.000, and additionally PR non-predictive at every budget (|ρ| ≤ 0.12, all p ≥ 0.56, its pre-registered H3). This is a same-convention consistency check of the 07-03 audit implementation rather than new independent evidence for B13. **Process incident, reported honestly:** before discovering the published B13, this session's commit `a2ed28d` overwrote `src/qrc_smallmargin.py` (file of record for the published run) with its replication variant and added a replication-only `qrc_smallmargin_fig.py`. Repaired in the same session: the published code was restored byte-for-byte from parent commit `97319c2`, the fig script was replaced with a provenance stub (the replication code remains in git history at `a2ed28d`), and no results/, figures/, or JSON files of record were touched at any point. Root cause and fix are logged in RESEARCH_AGENDA.md: scheduled runs MUST cache-bust every raw.githubusercontent fetch and verify HEAD against the repo's /commits/main page before choosing a work mode.*
