# AUDIT: Fashion-MNIST paper benchmark table (arXiv:1708.07747, Table 3)

**Program 2 (Verified Autonomous Research) — third-party replication audit #1**
Date: 2026-07-05 (autonomous scheduled session). Auditor: Claude (autonomous agent), on behalf of Amirshayan Hamidin.

## The claim being audited

Xiao, Rasul & Vollgraf (2017), *"Fashion-MNIST: a Novel Image Dataset for Benchmarking Machine
Learning Algorithms"*, arXiv:1708.07747 — one of the most-cited dataset papers in ML — publishes a
scikit-learn benchmark table (Table 3). Two rows selected for audit:

1. **Primary:** `KNeighborsClassifier` with `weights=distance, n_neighbors=5, p=2` →
   **Fashion-MNIST test accuracy 0.852**.
2. **Secondary (cheap determinism check):** `GaussianNB` with `priors=[0.1]×10` →
   **Fashion-MNIST test accuracy 0.511**.

Sources (all public, MIT-licensed):
- Paper Table 3: https://arxiv.org/abs/1708.07747
- Benchmark code: https://github.com/zalandoresearch/fashion-mnist/blob/master/benchmark/runner.py
- Config: `benchmark/baselines.json` (the `common` block is empty → sklearn defaults for all
  unlisted parameters)
- Data: `data/fashion/*.gz` in the same repo; MD5s published in the README.

**Methodology extracted from `runner.py` (read before running):** features are standardized with
`sklearn.preprocessing.StandardScaler` **fit on the 60k training set** and applied to train and
test; the classifier is trained on all 60k, scored on all 10k test images; the run is repeated with
training-data shuffles and the mean reported, but the runner stops early when two runs agree to
<1e-3 ("invariant to shuffling") — which k-NN and GaussianNB are. So for these two rows the
published number is effectively a single deterministic value.

## Pre-registration (written 2026-07-05, BEFORE any classifier was run)

- **Expected values:** 0.852 (k-NN row), 0.511 (GaussianNB row), as published.
- **Tolerance for CONFIRMED:** |reproduced − published| ≤ 0.005 per row (the paper reports 3
  decimals, i.e. ±0.0005 rounding, plus headroom for sklearn version drift — the paper is from the
  sklearn ~0.19 era, this audit runs 1.7.2). Both rows must pass for an overall CONFIRMED;
  one pass + one miss will be reported per-row.
- **Anything outside tolerance → DISCREPANCY**, with environment differences (nine years of
  sklearn releases) as the default explanation, not misconduct.
- **Fixed decisions before running:** exact data files from the repo with MD5 verification
  (done: all 4 match); StandardScaler fit on train only; all 60k train / all 10k test; sklearn
  classes with only the table's parameters set, everything else default; k-NN run with
  `algorithm='brute'` (dimensionality 784 makes trees pathological; brute is the standard choice
  and does not change predictions, only speed); test set predicted in chunks purely for the
  sandbox's 45-s-per-call limit (chunking cannot change predictions).
- **Prior stated honestly:** no strong prior either way; k-NN + fixed preprocessing is about as
  deterministic as published numbers get, so this is chosen deliberately as a calibration target
  for the audit pipeline itself. If even this fails, the pipeline is suspect.

## Reproduced numbers

| Row | Published | Reproduced | Δ | Within ±0.005? |
|---|---|---|---|---|
| k-NN `weights=distance, n_neighbors=5, p=2` | 0.852 | **0.8535** | +0.0015 | **yes** |
| GaussianNB `priors=[0.1]×10` | 0.511 | **0.5703** | +0.0593 | **no** |

Data integrity: all four dataset files MD5-match the README's published checksums. k-NN predicted
with `algorithm='brute'` in three chunks (0–2000, 2000–6000, 6000–10000; per-chunk accuracies
0.8535 / 0.8478 / 0.8593), assembled and scored against the full test set. Runtime ≈ 27 s total on
2 CPU cores. GaussianNB ran whole in 3 s.

## Verdict

- **Primary (k-NN row): CONFIRMED.** 0.8535 vs 0.852, inside the pre-registered ±0.005.
- **Secondary (GaussianNB row): DISCREPANCY.** 0.5703 vs 0.511 — +5.9 pp outside tolerance, in
  the *favorable* direction (the modern reproduction does better than the paper). Default
  explanation, per protocol: environment differences, and here that explanation has post-hoc
  supporting evidence (labeled as such below), not just hand-waving.

**Post-hoc diagnostics (run AFTER the pre-registered runs, labeled honestly):** GaussianNB's
accuracy on this data is fragile to the variance-floor detail of the implementation — sweeping
`var_smoothing` over 1e-11…1e-5 moves accuracy 0.5605 → 0.6006 (4 pp across four orders of
magnitude), and un-standardized raw pixels give 0.5856. No variant tried recovers 0.511. The
GaussianNB implementation's numerics changed materially between the paper's sklearn (~0.19, which
used an absolute variance epsilon) and 1.7.2 (relative `var_smoothing`, different accumulation
paths), which is exactly the kind of detail this row is sensitive to. By contrast the k-NN row —
where the math leaves the library no discretion — reproduces to 0.15 pp after nine years. That
contrast is the actual finding of this audit: **published benchmark rows inherit the numerical
discretion of their implementation, and their reproducibility varies accordingly, within one table
of one paper.**

To be explicit and respectful: nothing here suggests any error by the Fashion-MNIST authors. The
paper's number was presumably correct for its environment; their code and data are public,
checksummed and runnable nine years later, which is exemplary — it is what made this audit possible
at all.

## Environment

- Sandbox: Ubuntu 22, 2 CPU cores, ~3 GB RAM, no GPU. Python 3, numpy + scikit-learn 1.7.2
  (`pip --break-system-packages`).
- Original: unknown 2017 machine, sklearn ~0.19 (inferred from paper date; `loss=deviance` and
  `multi_class` options in baselines.json are consistent with that era).

## Honesty section

1. **The task file's PROTOCOL.md does not exist.** This session was instructed to fetch
   `PROTOCOL.md` ("defines the six VAR rules") from the repo root; the GitHub contents API
   confirms no such file (not CDN staleness). This audit therefore follows the task file's inline
   ABSOLUTE RULES only. Flagged for Amirshayan: either commit PROTOCOL.md or remove the reference.
2. **Target selection was convenience-biased.** The claim was chosen to be maximally reproducible
   (deterministic classifier, public checksummed data, published runner code) — deliberately, as a
   calibration run for the Program 2 pipeline, but a pipeline validated on the easiest case says
   little yet about messier claims. Stated in the pre-registration before running.
3. **The GaussianNB diagnostics are post-hoc.** The var_smoothing sweep and raw-pixel run happened
   after seeing the miss; they support but do not prove the version-drift explanation. The honest
   statement is: 0.511 could not be reproduced under any variant tried, cause unidentified,
   environment drift most plausible. Running sklearn 0.19 under Python 2/3.6 to close the loop was
   out of scope for this sandbox (no such wheels for Python 3.10+).
4. **Two of 129 rows audited.** No claim is made about the rest of Table 3.
5. **Repeats skipped by reasoned argument, not measurement:** the paper averages 5 shuffled runs;
   both audited classifiers are provably shuffle-invariant (k-NN geometry and GaussianNB
   sufficient statistics do not depend on row order), matching the runner's own early-stop logic.
6. This audit ran autonomously; no human reviewed it before publication.

---
*Reproduction script: chunked sklearn run, archived in the session outputs as `audit_run.py`;
it is 60 lines and fully described by the Methodology + Fixed decisions above.*
