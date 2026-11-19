# Pooling experiment: does mean pooling help on unseen sequences?

Three Nebula models trained from scratch (same data, released BPE tokenizer, epochs, optimiser; seeds 0, 1, 2):

| | pooling | positional encoding |
|---|---|---|
| **A** | flatten | as released (retrained baseline) |
| **B** | mean | as released |
| **C** | mean | fixed: the encoding of each token's position inside its 64-token chunk |

Why C: in `nebula/models/attention.py`, `PositionalEncoding.forward()` in batch-first mode adds `self.pe[:1]`, the position-0 vector, to every token. The released model therefore has no position information inside a chunk. C adds `x + self.pe[:x.size(1), 0].unsqueeze(0)` instead, behind a `fixed_pe` flag (`hier_nebula/pooling_variants.py`; the original class is not edited; `python -m hier_nebula.test_pooling --nebula ../nebula` checks that two positions now get different vectors and that with the flag off the model equals the released one bit for bit).

## Verdict

1. **No: mean pooling (B) and fixed positions (C) do not close the gap on distance quartiles Q2-Q4.** Against the retrained baseline A, TPR at 1% FPR on Q2-Q4 changes by −10.0 points for B [−29.3, +6.8] and +2.5 for C [−12.6, +20.3] (threshold a); AUC changes by +0.035 [−0.015, +0.104] and +0.035 [−0.007, +0.090]. Every interval includes zero. Per quartile there is no consistent pattern: C gains in Q2 (+25.3 points [+3.7, +47.7]), loses AUC in Q3 (−0.041 [−0.096, −0.006]) and is flat in Q4 (+1.0 [−5.2, +5.5]).
2. **C's smaller gap is mostly C getting worse on the nearest quartile.** Gap = TPR in Q1 minus TPR in Q2-Q4 (threshold a): A 12.8 points, B 9.7, C 3.6. For C, Q1 fell from 66.6% to 59.8% while Q2-Q4 moved only from 53.7% to 56.3%; for B, Q2-Q4 is lower than A's (43.7% against 53.7%). With the January threshold (b) the gaps are A 17.4, B 6.6, C 8.2.
3. **Overall nothing beats A:** AUC B−A −0.001 [−0.026, +0.025], C−A −0.0005 [−0.023, +0.024]; TPR@1% B−A −11.6 [−25.1, −1.3], C−A −0.7 [−9.8, +7.8]; C−B +11.0 [+2.9, +22.1]. The same model varies by about 11 points of TPR from seed to seed (A 57.5-68.6%, B 49.4-60.0%, C 60.0-71.9%), so differences below roughly 15 points cannot be told from noise with three seeds.
4. **All three retrained models sit well below the released Nebula** (AUC 0.922-0.923 against 0.959; TPR@1% 53-65% against 75.0%), and their rank averages with the LightGBM (AUC 0.958-0.967) stay below released Nebula + LightGBM (0.9745). The gap that matters here is to the released, pretrained model, not between A, B and C (that it is pretraining is a guess; it was not tested).
5. **Order-shuffle check:** A collapses when the API calls are shuffled (AUC 0.923 → 0.669, TPR@1% 64.7% → 6.5%), while B and C degrade moderately (0.922 → 0.894 and 0.922 → 0.898). Mean pooling removes most of the dependence on exact token positions, but in these runs that did not turn into better detection of unseen sequences.

## What was run

- **Data.** Speakeasy reports tokenised once with the released Nebula BPE tokenizer; every model sees only the first 512 tokens of a report (`tokens_512.npy`, pad id 0), exactly Nebula's input. The released Nebula reproduces its stored scores from these arrays (max difference 5.5e-6, 5,429 reports). Train: January, grouped split, side `train` (65,679 reports). Early stopping: January validation, side `val` (9,619; disjoint `hash_apis` groups; `results/signal/val_split.csv`). Test: April (17,402 reports, 9,399 malware). The "1 / 2-3 / 4-8 chunks" subsets group April reports by their full length; the models never see more than the first chunk.
- **Training settings** (reused from Nebula's own from-scratch setup, `nebula/scripts/cross_validation/_speakeasy_model_loop.py`, Nebula commit `1343ae1`): model sizes of the released Nebula (d_model 64, 8 heads, feed-forward 256, 2 layers, chunk 64, classifier head [64], dropout 0.3, pre-norm), BCEWithLogitsLoss, AdamW lr 2.5e-4 with weight decay 0.01, batch size 64, learning rate ×0.5 every 1,000 steps (its 3,000-step budget / 3), gradient-norm clip 0.5.
- **My additions:** fp16 mixed precision; early stopping on the January validation loss (patience 2, at most 10 epochs; Nebula used a fixed 2 epochs); best-validation-loss weights are the ones scored; same batch order for A, B and C within a seed.
- **Where:** Kaggle, 2 × Tesla T4, two runs at a time (`scripts/kaggle/`), torch 2.11.0+cu130, Python 3.13; 9 runs in 13.7 minutes, about 48 s per epoch. Evaluation on the laptop (torch 2.15.0, Python 3.11).
- **Evaluation:** `scripts/pooling/evaluate_pooling.py` using `scripts/go_no_go/common.py`: AUC and TPR at 1% and 0.1% FPR with threshold (a) from the April benign scores and threshold (b) from the January-validation benign scores applied to April (its April FPR is shown); the value of a model is the mean over its three seeds; 95% intervals are a group bootstrap over `hash_apis` (1,000 resamples, seed 0), paired across models for the differences.

## Results

All April reports (mean over seeds [95% interval] in `tables.md`; point values here):

| model | AUC | TPR@1% FPR (a) | TPR@1% FPR (b) | April FPR at (b) |
|---|---|---|---|---|
| A | 0.9228 [0.8754, 0.9590] | 64.7% [53.1%, 75.1%] | 60.2% [49.3%, 70.1%] | 0.6% [0.4%, 0.8%] |
| B | 0.9216 [0.8695, 0.9628] | 53.0% [36.1%, 68.8%] | 54.8% [41.5%, 68.8%] | 1.0% [0.6%, 1.8%] |
| C | 0.9224 [0.8715, 0.9618] | 64.0% [48.1%, 76.7%] | 56.6% [43.5%, 69.2%] | 0.7% [0.4%, 1.1%] |
| released Nebula | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 76.6% [68.2%, 83.9%] | 1.4% [1.0%, 2.0%] |
| LightGBM bag of API names | 0.9501 [0.9150, 0.9757] | 62.9% [33.5%, 74.9%] | 58.0% [44.8%, 70.8%] | 0.9% [0.6%, 1.5%] |

Rank average with the bag-of-API LightGBM of the same seed (percentile ranks within each set, as test 1; "Jan ref" ranks April against the January-validation scores so a January threshold transfers; the plain variant's threshold (b) does not, hence its large April FPR):

| model | AUC | TPR@1% FPR (a) | TPR@1% FPR (b) | April FPR at (b) |
|---|---|---|---|---|
| A + LightGBM | 0.9672 [0.9369, 0.9847] | 75.9% [67.0%, 83.6%] | 94.7% [90.1%, 97.7%] | 19.2% [13.2%, 25.5%] |
| B + LightGBM | 0.9652 [0.9362, 0.9840] | 71.3% [60.6%, 81.7%] | 95.6% [91.2%, 98.3%] | 17.9% [12.8%, 25.0%] |
| C + LightGBM | 0.9630 [0.9344, 0.9825] | 74.5% [63.0%, 84.4%] | 90.8% [85.9%, 95.3%] | 13.7% [9.6%, 19.3%] |
| A + LightGBM (Jan ref) | 0.9626 [0.9305, 0.9819] | 69.7% [58.7%, 79.8%] | 63.5% [53.0%, 74.5%] | 0.6% [0.4%, 0.8%] |
| B + LightGBM (Jan ref) | 0.9618 [0.9308, 0.9813] | 68.1% [53.7%, 79.5%] | 59.8% [44.9%, 74.7%] | 0.6% [0.4%, 1.0%] |
| C + LightGBM (Jan ref) | 0.9581 [0.9274, 0.9791] | 68.8% [55.8%, 80.7%] | 56.4% [42.1%, 70.5%] | 0.3% [0.2%, 0.5%] |
| released Nebula + LightGBM | 0.9745 [0.9499, 0.9884] | 79.7% [68.9%, 87.6%] | 97.6% [93.4%, 99.6%] | 34.0% [23.2%, 45.8%] |

### Distance quartiles (unseen April reports, test 3 definitions)

Quartiles of the distance to the nearest January sequence: Q1 ≤ 0.031, Q2 ≤ 0.083, Q3 ≤ 0.193, Q4 > 0.193. TPR at 1% FPR, mean over seeds:

| model | TPR (a) Q1 | TPR (a) Q2-Q4 | gap (a), points | TPR (b) Q1 | TPR (b) Q2-Q4 | gap (b), points |
|---|---|---|---|---|---|---|
| A | 66.6% | 53.7% | +12.8 | 65.2% | 47.8% | +17.4 |
| B | 53.4% | 43.7% | +9.7 | 53.6% | 47.0% | +6.6 |
| C | 59.8% | 56.3% | +3.6 | 54.5% | 46.3% | +8.2 |
| released Nebula | 87.4% | 59.7% | +27.7 | 88.1% | 63.0% | +25.1 |
| LightGBM bag of API names | 68.5% | 45.9% | +22.6 | 57.9% | 41.7% | +16.2 |
| A + LightGBM | 78.2% | 65.9% | +12.3 | 92.3% | 95.7% | -3.4 |
| B + LightGBM | 76.0% | 57.6% | +18.4 | 92.7% | 97.5% | -4.8 |
| C + LightGBM | 74.2% | 66.2% | +8.0 | 85.5% | 92.0% | -6.6 |

Paired differences (percentage points for TPR; 95% interval):

| difference | subset | AUC | TPR@1% (a), points | TPR@1% (b), points |
|---|---|---|---|---|
| B − A | all | -0.0012 [-0.0261, +0.0250] | -11.6 [-25.1, -1.3] | -5.4 [-13.9, +3.8] |
| B − A | unseen | +0.0176 [-0.0176, +0.0630] | -11.4 [-26.4, +1.4] | -5.5 [-16.8, +7.5] |
| B − A | distance Q1 (≤ 0.031) | +0.0113 [-0.0188, +0.0733] | -13.2 [-29.5, +0.9] | -11.5 [-27.4, +2.9] |
| B − A | distance Q2 (≤ 0.083) | +0.0688 [-0.0229, +0.2060] | +13.2 [-4.3, +23.2] | +15.0 [+1.1, +25.3] |
| B − A | distance Q3 (≤ 0.193) | -0.0085 [-0.0285, +0.0277] | -26.2 [-39.8, +2.2] | -16.5 [-37.2, +19.2] |
| B − A | distance Q4 (> 0.193) | +0.0811 [-0.0407, +0.2423] | -13.8 [-45.0, +5.4] | +1.7 [-3.6, +10.0] |
| B − A | distance Q2-Q4 (farther three quartiles) | +0.0347 [-0.0146, +0.1042] | -10.0 [-29.3, +6.8] | -0.8 [-15.8, +14.0] |
| C − A | all | -0.0005 [-0.0231, +0.0239] | -0.7 [-9.8, +7.8] | -3.7 [-12.7, +6.2] |
| C − A | unseen | +0.0155 [-0.0116, +0.0515] | -1.5 [-14.8, +10.4] | -5.5 [-17.7, +9.7] |
| C − A | distance Q1 (≤ 0.031) | +0.0039 [-0.0311, +0.0408] | -6.7 [-24.5, +4.2] | -10.6 [-26.3, +5.1] |
| C − A | distance Q2 (≤ 0.083) | +0.1223 [+0.0387, +0.2133] | +25.3 [+3.7, +47.7] | +27.6 [+5.0, +46.6] |
| C − A | distance Q3 (≤ 0.193) | -0.0411 [-0.0955, -0.0059] | -15.3 [-30.8, +10.7] | -14.0 [-33.4, +18.9] |
| C − A | distance Q4 (> 0.193) | +0.0564 [+0.0020, +0.1615] | +1.0 [-5.2, +5.5] | -14.9 [-25.1, +1.0] |
| C − A | distance Q2-Q4 (farther three quartiles) | +0.0352 [-0.0067, +0.0903] | +2.5 [-12.6, +20.3] | -1.5 [-17.1, +20.2] |
| C − B | all | +0.0008 [-0.0135, +0.0207] | +11.0 [+2.9, +22.1] | +1.7 [-3.4, +6.2] |
| C − B | unseen | -0.0021 [-0.0281, +0.0271] | +9.9 [+1.7, +22.6] | +0.0 [-6.5, +5.5] |
| C − B | distance Q1 (≤ 0.031) | -0.0075 [-0.0452, +0.0083] | +6.4 [+0.2, +15.2] | +0.9 [-0.3, +4.1] |
| C − B | distance Q2 (≤ 0.083) | +0.0535 [-0.0184, +0.1344] | +12.0 [+2.0, +38.4] | +12.6 [+2.8, +22.3] |
| C − B | distance Q3 (≤ 0.193) | -0.0326 [-0.0897, -0.0104] | +10.9 [-0.0, +19.8] | +2.4 [-5.1, +4.8] |
| C − B | distance Q4 (> 0.193) | -0.0248 [-0.1078, +0.0558] | +14.8 [-4.6, +45.0] | -16.6 [-25.9, -2.2] |
| C − B | distance Q2-Q4 (farther three quartiles) | +0.0005 [-0.0415, +0.0541] | +12.5 [+1.8, +30.0] | -0.7 [-10.9, +8.3] |

All other subsets (seen, 1 / 2-3 / 4-8 chunks, window-share groups) and the rank-average differences are in `tables.md`.

### Sanity check: call order shuffled

April reports with the order of the API calls randomly permuted (each call keeps its fields), tokenised again, scored by the trained A, B and C (mean over seeds; `shuffle_check.json`). Before this, the CPU scores of the downloaded checkpoints were checked against the Kaggle run (max |difference| 1e-4 in the logit) and the unshuffled tokens against the token dataset (equal for all April reports).

| model | AUC original → shuffled | TPR@1% (a) original → shuffled | TPR@1% (b) original → shuffled | April FPR at (b) original → shuffled |
|---|---|---|---|---|
| A | 0.9228 → 0.6694 | 64.7% → 6.5% | 60.2% → 25.2% | 0.56% → 7.29% |
| B | 0.9216 → 0.8939 | 53.0% → 46.7% | 54.8% → 50.6% | 1.02% → 1.20% |
| C | 0.9224 → 0.8978 | 64.0% → 47.4% | 56.6% → 54.8% | 0.67% → 1.84% |

### Training runs

| run | epochs run | best epoch | stopped by | best val loss | val AUC by epoch | val loss by epoch | s per epoch | GPU |
|---|---|---|---|---|---|---|---|---|
| A seed 0 | 3 | 1 | early stop | 0.5655 | 0.9420 / 0.9466 / 0.9386 | 0.566 / 0.581 / 0.843 | 49 | Tesla T4 |
| A seed 1 | 4 | 2 | early stop | 0.7996 | 0.8906 / 0.9420 / 0.9422 / 0.9461 | 1.142 / 0.800 / 0.861 / 0.873 | 48 | Tesla T4 |
| A seed 2 | 3 | 1 | early stop | 0.6365 | 0.9346 / 0.9392 / 0.9308 | 0.636 / 0.902 / 1.085 | 47 | Tesla T4 |
| B seed 0 | 3 | 1 | early stop | 0.4704 | 0.9448 / 0.9297 / 0.9273 | 0.470 / 0.824 / 0.847 | 49 | Tesla T4 |
| B seed 1 | 3 | 1 | early stop | 0.7501 | 0.9167 / 0.9200 / 0.9200 | 0.750 / 0.865 / 0.931 | 48 | Tesla T4 |
| B seed 2 | 3 | 1 | early stop | 0.4830 | 0.9419 / 0.9370 / 0.9076 | 0.483 / 0.725 / 1.191 | 46 | Tesla T4 |
| C seed 0 | 3 | 1 | early stop | 0.3818 | 0.9693 / 0.9657 / 0.9639 | 0.382 / 0.561 / 0.583 | 47 | Tesla T4 |
| C seed 1 | 3 | 1 | early stop | 0.4564 | 0.9392 / 0.9574 / 0.9567 | 0.456 / 0.530 / 0.642 | 45 | Tesla T4 |
| C seed 2 | 4 | 2 | early stop | 0.8118 | 0.9521 / 0.9380 / 0.9432 / 0.9546 | 0.822 / 0.812 / 0.962 / 0.859 | 45 | Tesla T4 |

## Caveats

- **Early stopping picked epoch 1 in 7 of 9 runs** (epoch 2 in the other two). Validation loss rises after the first epoch while validation AUC is flat or still rising in several runs (for example A seed 1: 0.891, 0.942, 0.942, 0.946), so a loss-based rule favours early, possibly under-trained checkpoints. Only the best and the last checkpoint were kept, so selection by validation AUC could not be tried afterwards.
- A is a from-scratch retrain, not the released model (which is pretrained), so A is much weaker than released Nebula; conclusions about B and C are relative to A.
- The "mean" pooling of the Nebula class averages over all 512 positions, padding included (no mask), so B and C see the amount of padding as a feature.
- The quartile and window groups are small and their reports are strongly correlated, hence the wide intervals; only three seeds.
- The shuffle check also changes which calls fall into the first 512 tokens (98.6% of the token sequences changed), so a drop is not purely "order information".
- fp16 training on GPU is not bit-reproducible; a rerun gives slightly different numbers.

## Files

- `tables.md`: every table (overall, per seed, all paired differences, all subsets, training runs); `evaluation.json`: the numbers; `shuffle_check.json`; `scores/pool_{A,B,C}_{april,janval}.parquet` (row, seed, score; same layout as `results/go_no_go/scores`, ignored by git); `logs/`: training logs with epoch times, GPU name and package versions.
- Code: `hier_nebula/pooling_variants.py`, `hier_nebula/test_pooling.py`, `scripts/kaggle/` (`make_token_dataset.py`, `make_code_dataset.py`, `train_pooling.py`, `launch_pooling.py`, `kernel_smoke/`, `kernel_full/`), `scripts/pooling/` (`evaluate_pooling.py`, `shuffle_check.py`). `analyze_signal.py collect` was changed to take the report files in `meta.csv` order instead of directory-listing order (the listing order differs between machines; its self-checks all pass and `results/signal/reports.csv` is unchanged).
- Kaggle (private): datasets `nebula-speakeasy-tokens`, `nebula-thesis-code`; kernels `nebula-pooling-smoke-test`, `nebula-pooling-full-runs`. Checkpoints were downloaded to `../pooling_kernel_output/ckpt/` (outside the repository).

Reproduce:

```bash
../nebula-venv/bin/python scripts/kaggle/make_token_dataset.py --stage <empty folder>      # tokens (once)
.venv/bin/kaggle kernels push -p scripts/kaggle/kernel_full --accelerator NvidiaTeslaT4     # train
.venv/bin/kaggle kernels output msingh9365/nebula-pooling-full-runs -p ../pooling_kernel_output
../nebula-venv/bin/python scripts/pooling/evaluate_pooling.py --src ../pooling_kernel_output
../nebula-venv/bin/python scripts/pooling/shuffle_check.py --src ../pooling_kernel_output --tokens <folder with tokens_512.npy>
```
