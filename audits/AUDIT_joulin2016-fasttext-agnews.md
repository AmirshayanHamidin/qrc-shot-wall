# AUDIT: Joulin, Grave, Bojanowski & Mikolov (2016) — fastText, Table 1, AG News rows

**Program 2b confirmatory audit #13.** Session: 2026-07-06 scheduled (Program 2b run #12).
Status at commit 1: **PRE-REGISTERED — results section empty** (two-commit rule; PREREG_DRIFT.md governs).

## Claim

- Paper: A. Joulin, E. Grave, P. Bojanowski, T. Mikolov, *Bag of Tricks for Efficient Text Classification*, arXiv:1607.01759 (EACL 2017). Primary source fetched and read this session (ar5iv HTML render of the arXiv paper); Table 1 numbers verified in the paper's own text.
- Table 1, AG column, test accuracy [%]:
  - **Row A: fastText, h=10 → 91.5**
  - **Row B: fastText, h=10, bigram → 92.5**
- Companion script of record: `classification-results.sh` in github.com/facebookresearch/fastText (fetched from `main` this session), whose header states "This script produces the results from Table 1". For AG News it publishes the exact bigram command — `-dim 10 -lr 0.25 -wordNgrams 2 -minCount 1 -bucket 10000000 -epoch 5 -thread 4` — and the full `normalize_text` preprocessing (lowercase; `__label__` prefix; pad `' . , ( ) ! ?` with spaces; delete `"`; drop `; :`; squeeze spaces; shuffle). The script's LR comment confirms the paper: "chosen by validation on a subset of the training set" (AG value 0.25).
- Row A (unigram) is NOT covered by the script; its lr is unpublished (paper: selected on a validation set from {0.05, 0.1, 0.25, 0.5}).
- Coverage: first 2010s-decade confirmatory target (a named tracker priority), first text-classification family points. Same-engine caveat (authors' own maintained library), analogous to audit #3's LIBSVM note.

## Data

- AG News csv of Zhang, Zhao & LeCun (2015) — the paper's stated evaluation protocol — obtained from the fast.ai S3 mirror (`s3.amazonaws.com/fast-ai-nlp/ag_news_csv.tgz`).
- Structural verification: train 120,000 rows (30,000 x 4 classes), test 7,600 rows (1,900 x 4).
- MD5: `train.csv b1a00f826fdfbd249f79597b59e1dc12`, `test.csv d52ea96a97a2d943681189a97654912d` (matches the canonical Zhang archive circulating since 2015).

## Blind discretion rubric (scored from paper + authors' script + library docs, BEFORE any reproduction run)

**Row A (h=10): 3/5**

1. Tie-breaking/randomization — **1**: no seed anywhere; the authors' own pipeline shuffles training lines with an unseeded Perl `shuffle` and trains asynchronous multithreaded SGD (`-thread 4`).
2. Regularization/smoothing — 0: plain softmax loss, no penalty terms; remaining numeric knobs (`t`, `lrUpdateRate`) are library defaults shared with the pinned row B command.
3. Initialization — **1**: unspecified in paper and script; the library's default input-matrix initialization must be accepted.
4. Stopping criteria — 0: 5 epochs fixed; linearly decaying lr stated in the paper.
5. Preprocessing — **1**: text normalization is published, but the validation split used to select this row's lr is unspecified (construction, size, seed) and the selected lr value is unpublished for this row.

**Row B (h=10, bigram): 2/5**

1. Tie-breaking/randomization — **1**: as row A (unseeded shuffle, threaded SGD, no seed).
2. Regularization/smoothing — 0: command pins lr/minCount/bucket/epoch/dim.
3. Initialization — **1**: as row A.
4. Stopping criteria — 0: pinned. 5. Preprocessing — 0: `normalize_text` + exact flags + lr all published.

## Pinned reproduction procedure

1. Python translation of `normalize_text`, exact operation order: lowercase; prefix `__label__`; `'` -> ` ' `; delete `"`; `.` -> ` . `; `<br />` -> ` `; `,` -> ` , `; `(` -> ` ( `; `)` -> ` ) `; `!` -> ` ! `; `?` -> ` ? `; `;` -> ` `; `:` -> ` `; squeeze runs of spaces. Backslashes in the csv are left untouched (the authors' script does not handle them). Labelled amendment: the unseeded `myshuf` is replaced by a seeded shuffle (`random.Random(master_seed)`) of the training lines — required for a reportable 3-seed procedure. Test file: same normalization, no shuffle.
2. **Row B** (per the published command): `fasttext.train_supervised(input, dim=10, lr=0.25, wordNgrams=2, minCount=1, bucket=10000000, epoch=5, thread=4, seed=master_seed)`.
3. **Row A**: identical except `wordNgrams=1` (library-default bucket, unused without n-grams/subwords) and lr selected as the paper describes: on the seed-0 shuffled normalized train file, first 108,000 lines train / last 12,000 lines validation; grid {0.05, 0.1, 0.25, 0.5}; highest validation P@1 wins, ties to the lower lr. Selection happens BEFORE any test-set evaluation and the chosen lr + validation table are recorded in Results. The selected lr is then used for all 3 master-seed runs on the full 120,000-line train file.
4. Master seeds 0, 1, 2 set both the train-file shuffle and fastText's `seed` argument. `thread=4` as published; residual thread-level nondeterminism is part of the claim's own recipe and is absorbed by the 3-seed average (disclosed in Honesty).
5. Metric: P@1 on the normalized 7,600-line test file, x100 (%). Standardized drift per row: mean over the 3 master seeds of |reproduced − published| pp.

## Pre-registered expectation and tolerance

- Expected: both rows within ~1 pp of published (same engine, canonical data).
- **Bar: ±2.0 pp per row, per seed. Verdict CONFIRMED for a row iff all 3 master-seed runs land within the bar; otherwise DISCREPANCY. Bars are never moved after data.**
- Secondary prediction (exploratory, hypothesis-relevant): row A's drift > row B's drift (within-paper discretion contrast, 3/5 vs 2/5), and both drifts ≤ 1.96 pp (the score-2 ceiling — engine identity dominates discretion score).

## Environment

Sandbox: Ubuntu 22, CPU only, 45 s per-process cap. Python 3.10; fasttext via PyPI `fasttext-wheel`. Exact versions recorded in the results commit.

## Results

(EMPTY at pre-registration — commit 1 of the two-commit rule. Results land in a separate, later commit.)

## Honesty section

(To be completed with results. Items known at prereg time:)

1. Same-engine caveat: the reproduction uses the authors' maintained library, so this audit prices data + preprocessing + decade drift, not cross-implementation drift.
2. Data provenance: fast.ai S3 mirror, not the original Google Drive link (which requires interactive download); MD5s recorded above match the canonical archive.
3. `myshuf` seeded-shuffle amendment (procedure step 1) — labelled, claim-preserving.
4. The paper's Table 2 reports 1 s AG train time (20 threads, 2016 hardware); the 45 s cap is not expected to bind. Any chunking will be disclosed here.
