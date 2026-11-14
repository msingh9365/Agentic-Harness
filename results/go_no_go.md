# Go / no-go: is the two-level (chunked) Nebula worth more GPU time?

Four cheap tests on the Speakeasy reports (January 2022 = train, April 2022 = test). Nothing was run or
emulated; only existing reports and scores were read and LightGBM was trained. Everything is fitted on
January only; April labels are used only to report.

## Setup

| item | value |
|---|---|
| this repository | `9fe2ec04c17636e3341a262ccd7643aee25fa516` (branch `nebula-length-study`) + uncommitted `scripts/go_no_go/` changes |
| Nebula code and released model | `1343ae170ef32b01a75d2dd5fb906b5541f073df` (`../nebula`, = upstream HEAD on 2026-11-14); `model.eval()`, batch size 256, torch 2.15.0+cpu |
| dataset | `dtrizna/quovadis-speakeasy` revision `fc2e98fac0b4d43a5557ccab70c877af6cce9f4d` (REPORT.md §1) |
| two-level model | `results/hier/finetune_k8/best.pt` (K=8, finetune, seed 0); re-scoring reproduces its `test_scores.csv` (max diff 8.3e-7) |
| January split | `results/signal/val_split.csv`: groups = SHA-1 of the API-name sequence (`hash_apis`), 10% of groups to validation, `GroupShuffleSplit` seed 0 (65,679 train / 9,619 validation reports) |
| LightGBM | `analyze_signal.fit_lgb`: lr 0.05, 63 leaves, feature/bagging fraction 0.8, early stopping (100 rounds) on group-weighted validation log-loss; seeds 0, 1, 2 |
| bootstrap | 1,000 resamples of April groups (`hash_apis`, 2,509 groups), seed 0, paired across models |
| thresholds | (a) from April benign scores; (b) from January-validation benign scores, applied to April (its April FPR is shown). Rule: flagged = score > the (⌊FPR·n⌋+1)-th highest benign score |
| subsets | seen / unseen = the report's `hash_apis` occurs / does not occur in January; chunks = 512-token chunks of Nebula's tokenized report (`meta.csv` `n_chunks`) |
| April scores | `results/go_no_go/scores/*_april.parquet` (columns `row`, `seed`, `score`; `row` = `results/hier/data/meta.csv` row), January-validation scores in `*_janval.parquet` |

Caveat for threshold (b): released Nebula and the two-level model were trained on January data, so their
January-validation scores are in-sample; only LightGBM's validation side is truly held out.

## Commands

```bash
source ../nebula-venv/bin/activate          # Python 3.11, see results/logs/signal_versions.log
python scripts/go_no_go/score_models.py      # released Nebula + two-level scores (April, January validation)
python scripts/go_no_go/test1_rank_average.py
python scripts/go_no_go/test2_ceiling.py
python scripts/go_no_go/test3_unseen_distance.py
python scripts/go_no_go/test4_long_group.py
python scripts/go_no_go/make_report.py       # this file
```
Logs: `results/go_no_go/logs/`.

## Test 1: trivial competitor (rank average of LightGBM and released Nebula)

Cell = value [95% interval, group bootstrap]. LightGBM and the rank average: mean over seeds 0/1/2 (per-seed values below). (a) = threshold from April benign scores; (b) = threshold from January validation benign scores, with the FPR it gives on April. Subsets use the overall thresholds. `rank average`: percentile ranks within each set (April ranked among April, January among January), as asked; its threshold (b) does not transfer, because the sets have different malware shares (78% vs 54%). `rank average, January reference`: each score's percentile within the January-validation scores of the same model (labels unused); this one can be deployed with a January threshold.

| subset | model | n (malware) | AUC | TPR@1% (a) | FPR (a) | TPR@1% (b) | April FPR (b) | TPR@0.1% (a) | FPR (a)  | TPR@0.1% (b) | April FPR (b)  |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | released Nebula | 17,402 (9,399) | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 1.0% [0.9%, 1.0%] | 76.6% [68.2%, 83.9%] | 1.4% [1.0%, 2.0%] | 51.7% [0.0%, 67.0%] | 0.1% [0.0%, 0.1%] | 44.0% [30.0%, 58.5%] | 0.1% [0.0%, 0.1%] |
| all | LightGBM bag of API names | 17,402 (9,399) | 0.9501 [0.9150, 0.9757] | 62.9% [33.5%, 74.9%] | 1.0% [0.9%, 1.0%] | 58.0% [44.8%, 70.8%] | 0.9% [0.6%, 1.5%] | 31.6% [18.2%, 45.4%] | 0.1% [0.0%, 0.1%] | 27.2% [16.0%, 40.8%] | 0.0% [0.0%, 0.1%] |
| all | rank average (LightGBM + Nebula) | 17,402 (9,399) | 0.9745 [0.9499, 0.9884] | 79.7% [68.9%, 87.6%] | 1.0% [1.0%, 1.0%] | 97.6% [93.4%, 99.6%] | 34.0% [23.2%, 45.8%] | 55.1% [40.4%, 70.9%] | 0.1% [0.1%, 0.1%] | 91.7% [86.5%, 95.5%] | 7.3% [5.1%, 10.8%] |
| all | rank average, January reference | 17,402 (9,399) | 0.9715 [0.9461, 0.9859] | 74.3% [55.8%, 84.4%] | 1.0% [1.0%, 1.0%] | 65.8% [54.1%, 76.3%] | 0.8% [0.4%, 1.3%] | 49.7% [32.8%, 67.5%] | 0.1% [0.1%, 0.1%] | 49.0% [35.5%, 63.7%] | 0.1% [0.0%, 0.2%] |
| all | two-level K=8 (finetune_k8) | 17,402 (9,399) | 0.9639 [0.9376, 0.9815] | 74.7% [61.5%, 83.5%] | 1.0% [1.0%, 1.0%] | 84.6% [76.5%, 90.2%] | 2.9% [2.1%, 4.0%] | 54.3% [36.4%, 66.2%] | 0.1% [0.0%, 0.1%] | 31.8% [17.6%, 44.9%] | 0.0% [0.0%, 0.1%] |
| seen | released Nebula | 6,329 (2,914) | 0.9865 [0.9709, 0.9944] | 82.1% [71.8%, 89.5%] | 0.7% [0.4%, 1.1%] | 82.8% [73.4%, 90.2%] | 1.0% [0.5%, 1.8%] | 61.3% [0.0%, 75.7%] | 0.1% [0.0%, 0.2%] | 52.8% [38.3%, 66.7%] | 0.1% [0.0%, 0.2%] |
| seen | LightGBM bag of API names | 6,329 (2,914) | 0.9749 [0.9447, 0.9904] | 79.0% [66.1%, 88.4%] | 1.1% [0.5%, 2.0%] | 78.6% [66.9%, 88.3%] | 1.1% [0.4%, 2.4%] | 62.9% [42.3%, 76.6%] | 0.0% [0.0%, 0.1%] | 50.5% [35.8%, 66.8%] | 0.0% [0.0%, 0.0%] |
| seen | rank average (LightGBM + Nebula) | 6,329 (2,914) | 0.9885 [0.9739, 0.9959] | 86.7% [77.3%, 93.7%] | 0.7% [0.3%, 1.1%] | 99.3% [98.5%, 99.8%] | 26.2% [15.1%, 42.3%] | 80.0% [68.2%, 88.6%] | 0.1% [0.0%, 0.2%] | 93.7% [87.6%, 98.0%] | 5.0% [2.5%, 9.7%] |
| seen | rank average, January reference | 6,329 (2,914) | 0.9854 [0.9664, 0.9949] | 85.4% [74.7%, 92.8%] | 1.2% [0.5%, 2.0%] | 83.4% [73.1%, 91.1%] | 1.0% [0.4%, 2.3%] | 80.3% [61.0%, 88.7%] | 0.1% [0.0%, 0.2%] | 79.0% [68.1%, 87.2%] | 0.1% [0.0%, 0.2%] |
| seen | two-level K=8 (finetune_k8) | 6,329 (2,914) | 0.9909 [0.9808, 0.9962] | 87.5% [77.1%, 93.8%] | 1.1% [0.4%, 1.8%] | 92.0% [85.4%, 96.6%] | 2.0% [1.1%, 3.5%] | 63.9% [46.3%, 76.4%] | 0.1% [0.0%, 0.2%] | 34.5% [20.8%, 47.1%] | 0.0% [0.0%, 0.0%] |
| unseen | released Nebula | 11,073 (6,485) | 0.9371 [0.8897, 0.9672] | 71.8% [56.3%, 82.1%] | 1.2% [0.9%, 1.7%] | 73.9% [59.0%, 83.8%] | 1.7% [1.1%, 2.6%] | 47.4% [0.0%, 66.1%] | 0.1% [0.0%, 0.2%] | 40.1% [20.6%, 59.1%] | 0.0% [0.0%, 0.1%] |
| unseen | LightGBM bag of API names | 11,073 (6,485) | 0.9384 [0.8917, 0.9754] | 55.7% [18.2%, 72.2%] | 0.9% [0.3%, 1.4%] | 48.7% [30.7%, 67.2%] | 0.9% [0.6%, 1.3%] | 17.5% [4.0%, 34.3%] | 0.1% [0.0%, 0.2%] | 16.7% [3.3%, 33.4%] | 0.1% [0.0%, 0.2%] |
| unseen | rank average (LightGBM + Nebula) | 11,073 (6,485) | 0.9647 [0.9237, 0.9858] | 76.5% [61.1%, 87.4%] | 1.2% [0.9%, 1.7%] | 96.8% [90.7%, 99.6%] | 39.8% [26.5%, 53.9%] | 43.9% [25.2%, 64.0%] | 0.1% [0.0%, 0.2%] | 90.9% [82.4%, 95.7%] | 9.1% [6.0%, 13.6%] |
| unseen | rank average, January reference | 11,073 (6,485) | 0.9636 [0.9234, 0.9844] | 69.4% [41.6%, 83.1%] | 0.9% [0.4%, 1.4%] | 57.9% [41.3%, 72.7%] | 0.6% [0.4%, 0.9%] | 36.0% [18.4%, 60.3%] | 0.1% [0.0%, 0.2%] | 35.5% [19.2%, 55.4%] | 0.1% [0.0%, 0.2%] |
| unseen | two-level K=8 (finetune_k8) | 11,073 (6,485) | 0.9392 [0.8847, 0.9713] | 68.9% [48.0%, 81.4%] | 0.9% [0.5%, 1.5%] | 81.2% [66.7%, 89.3%] | 3.6% [2.6%, 5.1%] | 49.9% [24.7%, 66.5%] | 0.1% [0.0%, 0.2%] | 30.6% [8.4%, 47.9%] | 0.0% [0.0%, 0.2%] |
| 1 chunk | released Nebula | 6,359 (2,855) | 0.9556 [0.9246, 0.9755] | 61.5% [43.9%, 76.5%] | 1.1% [0.7%, 1.5%] | 64.2% [47.4%, 77.6%] | 1.5% [1.0%, 2.1%] | 42.6% [0.0%, 65.1%] | 0.1% [0.0%, 0.2%] | 40.3% [18.5%, 64.3%] | 0.1% [0.0%, 0.3%] |
| 1 chunk | LightGBM bag of API names | 6,359 (2,855) | 0.9100 [0.8590, 0.9542] | 43.9% [16.0%, 67.8%] | 0.4% [0.1%, 0.7%] | 43.7% [20.1%, 69.8%] | 0.3% [0.2%, 0.6%] | 14.0% [5.6%, 30.3%] | 0.0% [0.0%, 0.1%] | 13.6% [5.2%, 30.1%] | 0.0% [0.0%, 0.1%] |
| 1 chunk | rank average (LightGBM + Nebula) | 6,359 (2,855) | 0.9630 [0.9358, 0.9801] | 59.3% [40.8%, 78.4%] | 0.8% [0.5%, 1.3%] | 98.6% [97.1%, 99.4%] | 38.8% [29.8%, 48.1%] | 43.1% [19.4%, 68.3%] | 0.1% [0.1%, 0.2%] | 87.5% [77.7%, 93.3%] | 9.1% [5.5%, 13.7%] |
| 1 chunk | rank average, January reference | 6,359 (2,855) | 0.9519 [0.9177, 0.9753] | 53.1% [31.2%, 75.9%] | 0.6% [0.3%, 0.9%] | 49.2% [27.0%, 73.4%] | 0.4% [0.2%, 0.6%] | 43.4% [18.2%, 68.4%] | 0.2% [0.1%, 0.2%] | 42.4% [19.7%, 66.8%] | 0.1% [0.0%, 0.3%] |
| 1 chunk | two-level K=8 (finetune_k8) | 6,359 (2,855) | 0.9726 [0.9480, 0.9853] | 78.6% [59.7%, 88.4%] | 1.8% [1.2%, 2.4%] | 82.9% [68.5%, 91.1%] | 3.1% [2.0%, 4.5%] | 46.4% [18.2%, 69.8%] | 0.2% [0.0%, 0.3%] | 10.5% [1.5%, 26.6%] | 0.0% [0.0%, 0.0%] |
| 2-3 chunks | released Nebula | 6,077 (3,676) | 0.9833 [0.9587, 0.9930] | 79.3% [61.6%, 89.2%] | 1.0% [0.6%, 2.0%] | 81.1% [64.8%, 90.4%] | 1.4% [0.6%, 3.1%] | 47.2% [0.0%, 70.0%] | 0.1% [0.0%, 0.2%] | 32.3% [15.0%, 55.3%] | 0.0% [0.0%, 0.0%] |
| 2-3 chunks | LightGBM bag of API names | 6,077 (3,676) | 0.9778 [0.9507, 0.9901] | 76.3% [26.3%, 88.1%] | 2.3% [1.3%, 4.3%] | 64.1% [48.0%, 77.5%] | 2.2% [0.9%, 5.0%] | 28.4% [8.1%, 54.1%] | 0.2% [0.0%, 0.3%] | 18.7% [5.3%, 43.2%] | 0.1% [0.0%, 0.2%] |
| 2-3 chunks | rank average (LightGBM + Nebula) | 6,077 (3,676) | 0.9925 [0.9813, 0.9969] | 89.9% [79.8%, 95.1%] | 1.2% [0.6%, 2.4%] | 99.5% [98.8%, 99.9%] | 17.7% [9.4%, 32.8%] | 58.9% [35.0%, 78.1%] | 0.1% [0.0%, 0.2%] | 96.7% [92.6%, 98.7%] | 7.4% [3.6%, 15.0%] |
| 2-3 chunks | rank average, January reference | 6,077 (3,676) | 0.9848 [0.9649, 0.9933] | 82.1% [46.8%, 92.4%] | 2.2% [1.3%, 4.0%] | 65.6% [52.2%, 80.9%] | 1.9% [0.7%, 4.4%] | 40.8% [19.5%, 67.6%] | 0.1% [0.0%, 0.2%] | 40.0% [20.6%, 68.8%] | 0.0% [0.0%, 0.2%] |
| 2-3 chunks | two-level K=8 (finetune_k8) | 6,077 (3,676) | 0.9817 [0.9504, 0.9925] | 67.4% [39.2%, 84.1%] | 0.2% [0.0%, 0.7%] | 84.5% [69.6%, 92.7%] | 1.7% [0.8%, 3.4%] | 48.1% [16.6%, 69.3%] | 0.1% [0.0%, 0.3%] | 31.8% [6.4%, 51.1%] | 0.1% [0.0%, 0.4%] |
| 4-8 chunks | released Nebula | 4,966 (2,868) | 0.9288 [0.8301, 0.9841] | 82.9% [64.8%, 93.1%] | 0.8% [0.3%, 1.4%] | 83.4% [65.5%, 93.6%] | 1.2% [0.6%, 2.5%] | 66.5% [0.0%, 81.6%] | 0.0% [0.0%, 0.0%] | 62.7% [36.0%, 78.3%] | 0.0% [0.0%, 0.0%] |
| 4-8 chunks | LightGBM bag of API names | 4,966 (2,868) | 0.9410 [0.8575, 0.9955] | 64.8% [35.4%, 89.8%] | 0.6% [0.0%, 1.4%] | 64.4% [35.4%, 89.1%] | 0.5% [0.2%, 1.3%] | 53.0% [26.9%, 78.1%] | 0.0% [0.0%, 0.2%] | 51.7% [25.3%, 76.6%] | 0.0% [0.0%, 0.2%] |
| 4-8 chunks | rank average (LightGBM + Nebula) | 4,966 (2,868) | 0.9544 [0.8673, 0.9965] | 86.7% [70.3%, 95.9%] | 1.0% [0.5%, 1.9%] | 94.1% [80.7%, 99.9%] | 44.6% [18.7%, 67.3%] | 62.1% [33.6%, 86.7%] | 0.0% [0.0%, 0.0%] | 89.6% [74.6%, 98.6%] | 4.4% [2.4%, 8.2%] |
| 4-8 chunks | rank average, January reference | 4,966 (2,868) | 0.9604 [0.8769, 0.9974] | 85.5% [67.5%, 94.7%] | 0.4% [0.0%, 1.1%] | 82.6% [65.6%, 92.4%] | 0.2% [0.1%, 0.5%] | 67.5% [39.8%, 88.8%] | 0.0% [0.0%, 0.2%] | 67.0% [47.4%, 85.9%] | 0.0% [0.0%, 0.2%] |
| 4-8 chunks | two-level K=8 (finetune_k8) | 4,966 (2,868) | 0.9358 [0.8459, 0.9829] | 80.2% [62.1%, 90.8%] | 0.5% [0.1%, 1.5%] | 86.2% [70.0%, 95.0%] | 4.1% [2.6%, 7.1%] | 70.1% [43.2%, 82.8%] | 0.0% [0.0%, 0.0%] | 53.0% [29.7%, 69.3%] | 0.0% [0.0%, 0.0%] |

**Per seed (all April):**

| model | AUC | TPR@1% (a) | FPR (a) | TPR@1% (b) | April FPR (b) | TPR@0.1% (a) | FPR (a)  | TPR@0.1% (b) | April FPR (b)  |
|---|---|---|---|---|---|---|---|---|---|
| LightGBM bag of API names | 0.9482 / 0.9501 / 0.9520 | 63.9% / 62.0% / 62.9% | 1.0% / 1.0% / 1.0% | 58.7% / 52.7% / 62.6% | 1.0% / 0.9% / 0.9% | 29.2% / 32.6% / 32.9% | 0.1% / 0.1% / 0.1% | 27.0% / 27.1% / 27.5% | 0.0% / 0.0% / 0.0% |
| rank average (LightGBM + Nebula) | 0.9735 / 0.9752 / 0.9747 | 79.1% / 79.6% / 80.2% | 1.0% / 1.0% / 1.0% | 97.9% / 97.4% / 97.4% | 39.9% / 30.5% / 31.6% | 54.4% / 52.2% / 58.5% | 0.1% / 0.1% / 0.1% | 91.9% / 90.8% / 92.5% | 7.4% / 6.2% / 8.4% |
| rank average, January reference | 0.9718 / 0.9718 / 0.9711 | 74.7% / 73.9% / 74.4% | 1.0% / 1.0% / 1.0% | 74.4% / 60.8% / 62.1% | 1.0% / 0.7% / 0.7% | 47.5% / 48.0% / 53.7% | 0.1% / 0.1% / 0.1% | 46.9% / 47.2% / 52.9% | 0.1% / 0.1% / 0.1% |

**Paired differences [95% interval]:**

| difference | subset | AUC | TPR@1% (a) | TPR@1% (b) | TPR@0.1% (a) | TPR@0.1% (b) |
|---|---|---|---|---|---|---|
| rank average (LightGBM + Nebula) − two-level K=8 (finetune_k8) | all | +0.0106 [-0.0056, +0.0301] | +5.0 [-6.6, +16.6] | +13.0 [+8.4, +19.4] | +0.8 [-16.9, +21.1] | +59.9 [+48.1, +72.9] |
| rank average (LightGBM + Nebula) − two-level K=8 (finetune_k8) | seen | -0.0025 [-0.0129, +0.0047] | -0.8 [-8.3, +7.5] | +7.3 [+2.9, +13.8] | +16.1 [+6.9, +29.9] | +59.2 [+46.3, +73.0] |
| rank average (LightGBM + Nebula) − two-level K=8 (finetune_k8) | unseen | +0.0255 [-0.0013, +0.0649] | +7.6 [-8.4, +26.1] | +15.6 [+9.1, +26.5] | -6.1 [-28.5, +20.5] | +60.2 [+44.1, +80.2] |
| rank average (LightGBM + Nebula) − two-level K=8 (finetune_k8) | 1 chunk | -0.0095 [-0.0259, +0.0057] | -19.2 [-37.0, -0.3] | +15.7 [+8.0, +29.7] | -3.3 [-25.1, +14.4] | +76.9 [+58.2, +87.9] |
| rank average (LightGBM + Nebula) − two-level K=8 (finetune_k8) | 2-3 chunks | +0.0108 [+0.0033, +0.0332] | +22.6 [+8.5, +47.6] | +15.0 [+7.0, +29.5] | +10.8 [-24.7, +42.9] | +64.9 [+46.6, +89.4] |
| rank average (LightGBM + Nebula) − two-level K=8 (finetune_k8) | 4-8 chunks | +0.0186 [-0.0017, +0.0514] | +6.6 [+2.4, +12.7] | +7.9 [+3.7, +16.6] | -7.9 [-41.5, +20.9] | +36.6 [+23.8, +55.0] |
| rank average, January reference − two-level K=8 (finetune_k8) | all | +0.0077 [-0.0098, +0.0280] | -0.3 [-19.7, +11.7] | -18.8 [-31.0, -7.9] | -4.5 [-21.1, +14.1] | +17.1 [-1.1, +38.6] |
| rank average, January reference − two-level K=8 (finetune_k8) | seen | -0.0055 [-0.0197, +0.0030] | -2.2 [-10.4, +5.8] | -8.6 [-16.2, -3.3] | +16.3 [+1.8, +30.2] | +44.6 [+32.3, +57.9] |
| rank average, January reference − two-level K=8 (finetune_k8) | unseen | +0.0244 [-0.0043, +0.0665] | +0.5 [-26.7, +17.8] | -23.3 [-39.8, -7.9] | -13.9 [-33.4, +10.6] | +4.8 [-17.5, +34.2] |
| rank average, January reference − two-level K=8 (finetune_k8) | 1 chunk | -0.0206 [-0.0418, -0.0005] | -25.4 [-48.3, -3.9] | -33.7 [-57.4, -10.8] | -3.0 [-25.8, +14.5] | +31.8 [+12.9, +57.3] |
| rank average, January reference − two-level K=8 (finetune_k8) | 2-3 chunks | +0.0031 [-0.0094, +0.0236] | +14.7 [-21.9, +38.1] | -19.0 [-33.8, -0.4] | -7.3 [-39.7, +27.6] | +8.2 [-23.5, +46.6] |
| rank average, January reference − two-level K=8 (finetune_k8) | 4-8 chunks | +0.0246 [+0.0044, +0.0608] | +5.3 [-0.3, +11.0] | -3.6 [-7.7, -1.1] | -2.6 [-32.6, +19.3] | +14.0 [-15.4, +39.1] |
| rank average (LightGBM + Nebula) − released Nebula | all | +0.0159 [+0.0068, +0.0284] | +4.7 [-0.3, +9.9] | +20.9 [+14.4, +28.8] | +3.4 [-11.6, +57.6] | +47.7 [+33.9, +61.2] |
| rank average (LightGBM + Nebula) − released Nebula | seen | +0.0020 [-0.0037, +0.0088] | +4.6 [+2.2, +8.6] | +16.4 [+9.1, +25.7] | +18.7 [+7.9, +82.3] | +40.8 [+28.0, +53.7] |
| rank average (LightGBM + Nebula) − released Nebula | unseen | +0.0275 [+0.0116, +0.0502] | +4.7 [-2.0, +12.5] | +23.0 [+13.9, +35.5] | -3.5 [-22.9, +44.8] | +50.8 [+31.8, +69.3] |
| rank average (LightGBM + Nebula) − released Nebula | 1 chunk | +0.0074 [-0.0016, +0.0176] | -2.1 [-10.5, +7.8] | +34.4 [+21.4, +50.5] | +0.5 [-5.4, +52.1] | +47.1 [+25.7, +68.1] |
| rank average (LightGBM + Nebula) − released Nebula | 2-3 chunks | +0.0092 [+0.0035, +0.0237] | +10.6 [+4.1, +21.6] | +18.5 [+9.2, +34.4] | +11.7 [-4.3, +62.1] | +64.4 [+40.9, +81.7] |
| rank average (LightGBM + Nebula) − released Nebula | 4-8 chunks | +0.0256 [+0.0048, +0.0613] | +3.8 [+1.2, +8.3] | +10.7 [+5.3, +22.3] | -4.4 [-39.6, +74.8] | +26.9 [+15.1, +48.1] |
| two-level K=8 (finetune_k8) − released Nebula | all | +0.0053 [-0.0072, +0.0192] | -0.3 [-10.0, +7.6] | +7.9 [+3.7, +13.5] | +2.6 [-14.4, +58.0] | -12.2 [-29.6, +3.3] |
| two-level K=8 (finetune_k8) − released Nebula | seen | +0.0044 [-0.0025, +0.0146] | +5.4 [-2.6, +13.6] | +9.2 [+4.0, +16.0] | +2.6 [-13.5, +66.0] | -18.4 [-37.9, +0.5] |
| two-level K=8 (finetune_k8) − released Nebula | unseen | +0.0020 [-0.0222, +0.0246] | -2.9 [-17.8, +8.0] | +7.4 [+2.0, +14.9] | +2.5 [-19.6, +54.4] | -9.5 [-33.1, +10.3] |
| two-level K=8 (finetune_k8) − released Nebula | 1 chunk | +0.0170 [+0.0013, +0.0352] | +17.1 [+4.3, +29.0] | +18.8 [+7.3, +29.2] | +3.8 [-9.0, +50.1] | -29.8 [-55.5, -11.4] |
| two-level K=8 (finetune_k8) − released Nebula | 2-3 chunks | -0.0016 [-0.0144, +0.0075] | -11.9 [-33.6, -0.3] | +3.5 [-0.1, +9.0] | +0.8 [-35.8, +56.0] | -0.5 [-32.5, +26.3] |
| two-level K=8 (finetune_k8) − released Nebula | 4-8 chunks | +0.0070 [-0.0126, +0.0348] | -2.7 [-7.0, +0.9] | +2.8 [+0.5, +6.8] | +3.6 [-6.8, +73.3] | -9.7 [-24.4, +6.6] |

**Decision.** By the rule set in advance, **the two-level model is dominated**: the rank average of LightGBM and released Nebula (percentile ranks within April, as specified) gets 0.9745 / 79.7% / 55.1% against 0.9639 / 74.7% / 54.3%. None of the three differences is significant (all intervals include 0), and the deployable variant (ranks against January) gets 0.9715 / 74.3% / 49.7%, which ties at 1% FPR and trails at 0.1% FPR.

## Test 2: information ceiling (first 92 calls vs full trace)

Same LightGBM as test 1 (bag of API names, early stopping on group-weighted January-validation log-loss, seeds 0/1/2: mean over seeds). Names kept if seen in ≥ 20 January-train reports, counted on the same prefix. 92 = median number of complete API calls in Nebula's 512-token window (reports > 512 tokens). 63.5% of April reports are longer than 512 tokens.

| subset | model | n (malware) | AUC | TPR@1% (a) | FPR (a) | TPR@1% (b) | April FPR (b) | TPR@0.1% (a) | FPR (a)  | TPR@0.1% (b) | April FPR (b)  |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | LightGBM, full trace | 17,402 (9,399) | 0.9501 [0.9150, 0.9757] | 62.9% [33.5%, 74.9%] | 1.0% [0.9%, 1.0%] | 58.0% [44.8%, 70.8%] | 0.9% [0.6%, 1.5%] | 31.6% [18.2%, 45.4%] | 0.1% [0.0%, 0.1%] | 27.2% [16.0%, 40.8%] | 0.0% [0.0%, 0.1%] |
| all | LightGBM, first 92 calls | 17,402 (9,399) | 0.8958 [0.8282, 0.9408] | 19.6% [10.6%, 36.0%] | 0.0% [0.0%, 1.0%] | 27.8% [15.6%, 42.3%] | 4.1% [0.7%, 11.7%] | 19.6% [10.4%, 31.5%] | 0.0% [0.0%, 0.1%] | 18.7% [9.4%, 30.1%] | 0.0% [0.0%, 0.1%] |
| seen | LightGBM, full trace | 6,329 (2,914) | 0.9749 [0.9447, 0.9904] | 79.0% [66.1%, 88.4%] | 1.1% [0.5%, 2.0%] | 78.6% [66.9%, 88.3%] | 1.1% [0.4%, 2.4%] | 62.9% [42.3%, 76.6%] | 0.0% [0.0%, 0.1%] | 50.5% [35.8%, 66.8%] | 0.0% [0.0%, 0.0%] |
| seen | LightGBM, first 92 calls | 6,329 (2,914) | 0.9360 [0.8921, 0.9671] | 29.6% [18.6%, 46.1%] | 0.0% [0.0%, 1.2%] | 34.2% [21.6%, 49.5%] | 0.9% [0.2%, 2.2%] | 29.6% [17.5%, 44.2%] | 0.0% [0.0%, 0.1%] | 28.3% [16.3%, 43.0%] | 0.0% [0.0%, 0.0%] |
| unseen | LightGBM, full trace | 11,073 (6,485) | 0.9384 [0.8917, 0.9754] | 55.7% [18.2%, 72.2%] | 0.9% [0.3%, 1.4%] | 48.7% [30.7%, 67.2%] | 0.9% [0.6%, 1.3%] | 17.5% [4.0%, 34.3%] | 0.1% [0.0%, 0.2%] | 16.7% [3.3%, 33.4%] | 0.1% [0.0%, 0.2%] |
| unseen | LightGBM, first 92 calls | 11,073 (6,485) | 0.8714 [0.7663, 0.9400] | 15.2% [4.9%, 36.4%] | 0.1% [0.0%, 1.2%] | 24.9% [9.4%, 43.9%] | 6.5% [0.8%, 18.7%] | 15.2% [4.2%, 30.6%] | 0.1% [0.0%, 0.1%] | 14.4% [3.5%, 29.6%] | 0.0% [0.0%, 0.1%] |
| 1 chunk | LightGBM, full trace | 6,359 (2,855) | 0.9100 [0.8590, 0.9542] | 43.9% [16.0%, 67.8%] | 0.4% [0.1%, 0.7%] | 43.7% [20.1%, 69.8%] | 0.3% [0.2%, 0.6%] | 14.0% [5.6%, 30.3%] | 0.0% [0.0%, 0.1%] | 13.6% [5.2%, 30.1%] | 0.0% [0.0%, 0.1%] |
| 1 chunk | LightGBM, first 92 calls | 6,359 (2,855) | 0.9194 [0.8702, 0.9565] | 16.4% [7.1%, 36.4%] | 0.1% [0.0%, 0.3%] | 20.5% [9.5%, 40.9%] | 0.2% [0.0%, 0.3%] | 16.4% [6.8%, 34.1%] | 0.1% [0.0%, 0.1%] | 14.9% [6.0%, 31.6%] | 0.0% [0.0%, 0.1%] |
| 2-3 chunks | LightGBM, full trace | 6,077 (3,676) | 0.9778 [0.9507, 0.9901] | 76.3% [26.3%, 88.1%] | 2.3% [1.3%, 4.3%] | 64.1% [48.0%, 77.5%] | 2.2% [0.9%, 5.0%] | 28.4% [8.1%, 54.1%] | 0.2% [0.0%, 0.3%] | 18.7% [5.3%, 43.2%] | 0.1% [0.0%, 0.2%] |
| 2-3 chunks | LightGBM, first 92 calls | 6,077 (3,676) | 0.9250 [0.8583, 0.9603] | 11.8% [3.7%, 47.1%] | 0.0% [0.0%, 3.0%] | 29.1% [9.8%, 55.7%] | 2.3% [1.0%, 5.3%] | 11.8% [3.4%, 26.8%] | 0.0% [0.0%, 0.2%] | 11.0% [2.7%, 25.8%] | 0.0% [0.0%, 0.2%] |
| 4-8 chunks | LightGBM, full trace | 4,966 (2,868) | 0.9410 [0.8575, 0.9955] | 64.8% [35.4%, 89.8%] | 0.6% [0.0%, 1.4%] | 64.4% [35.4%, 89.1%] | 0.5% [0.2%, 1.3%] | 53.0% [26.9%, 78.1%] | 0.0% [0.0%, 0.2%] | 51.7% [25.3%, 76.6%] | 0.0% [0.0%, 0.2%] |
| 4-8 chunks | LightGBM, first 92 calls | 4,966 (2,868) | 0.8223 [0.6410, 0.9564] | 33.0% [10.6%, 57.8%] | 0.0% [0.0%, 1.5%] | 33.4% [10.7%, 58.0%] | 12.8% [0.5%, 37.8%] | 33.0% [10.6%, 57.7%] | 0.0% [0.0%, 0.0%] | 32.3% [9.6%, 57.0%] | 0.0% [0.0%, 0.0%] |

**Per seed (all April):**

| model | AUC | TPR@1% (a) | FPR (a) | TPR@1% (b) | April FPR (b) | TPR@0.1% (a) | FPR (a)  | TPR@0.1% (b) | April FPR (b)  |
|---|---|---|---|---|---|---|---|---|---|
| LightGBM, full trace | 0.9482 / 0.9501 / 0.9520 | 63.9% / 62.0% / 62.9% | 1.0% / 1.0% / 1.0% | 58.7% / 52.7% / 62.6% | 1.0% / 0.9% / 0.9% | 29.2% / 32.6% / 32.9% | 0.1% / 0.1% / 0.1% | 27.0% / 27.1% / 27.5% | 0.0% / 0.0% / 0.0% |
| LightGBM, first 92 calls | 0.8953 / 0.8954 / 0.8967 | 18.6% / 20.3% / 20.1% | 0.0% / 0.0% / 0.0% | 27.7% / 28.0% / 27.7% | 4.1% / 4.1% / 4.1% | 18.6% / 20.3% / 20.1% | 0.0% / 0.0% / 0.0% | 18.2% / 19.6% / 18.2% | 0.0% / 0.0% / 0.0% |

**Full trace minus first 92 calls [95% interval]:**

| difference | subset | AUC | TPR@1% (a) | TPR@1% (b) | TPR@0.1% (a) | TPR@0.1% (b) |
|---|---|---|---|---|---|---|
| LightGBM, full trace − LightGBM, first 92 calls | all | +0.0543 [+0.0098, +0.1206] | +43.3 [+15.8, +56.2] | +30.2 [+15.4, +45.4] | +11.9 [+0.3, +24.2] | +8.5 [-0.9, +20.1] |
| LightGBM, full trace − LightGBM, first 92 calls | seen | +0.0389 [+0.0209, +0.0617] | +49.4 [+30.8, +62.9] | +44.4 [+27.1, +59.7] | +33.3 [+7.5, +52.2] | +22.3 [+2.9, +42.0] |
| LightGBM, full trace − LightGBM, first 92 calls | unseen | +0.0670 [-0.0025, +0.1743] | +40.6 [+3.8, +58.2] | +23.8 [+4.3, +44.5] | +2.3 [-7.5, +16.7] | +2.4 [-7.4, +15.6] |
| LightGBM, full trace − LightGBM, first 92 calls | 1 chunk | -0.0094 [-0.0288, +0.0067] | +27.6 [+4.2, +51.1] | +23.2 [+4.9, +51.0] | -2.3 [-8.3, +1.4] | -1.3 [-4.3, +0.1] |
| LightGBM, full trace − LightGBM, first 92 calls | 2-3 chunks | +0.0528 [+0.0241, +0.1015] | +64.5 [+11.5, +81.4] | +35.0 [+3.0, +58.9] | +16.7 [-5.0, +43.9] | +7.7 [-9.5, +32.2] |
| LightGBM, full trace − LightGBM, first 92 calls | 4-8 chunks | +0.1186 [+0.0252, +0.2836] | +31.8 [+14.2, +57.7] | +31.0 [+14.7, +56.3] | +20.1 [+0.3, +44.3] | +19.4 [+0.0, +43.9] |

How to read this. (1) The first-92-call model gives many reports the same score: 309 April benign reports (seed 0) sit exactly on its 1% threshold, which pushes its TPR (a) down. (2) Reports that need one chunk mostly have fewer than 92 calls, so both models see almost the same input there; yet TPR at 1% FPR differs by +27.6 points, which comes from the different model and threshold, not from more information. AUC is the cleaner measure: -0.0094 for 1-chunk reports, +0.0528 for 2-3 chunks and +0.1186 for 4-8 chunks. So later calls do carry signal for long reports, for a model that counts API names. (Released Nebula itself does not improve beyond about 100 calls: REPORT.md §10.3.)

**Decision.** The full trace adds +43.3 points of TPR at 1% FPR [+15.8, +56.2] over the first 92 calls, which is more than 1 point, so the rule does not say that long-context modelling has little to win.

## Test 3: how far is "unseen"?

1,872 unique April API-name sequences do not occur in January (11,073 reports); 6,771 unique January sequences. All of them were compared (no sampling): Jaccard shortlist of 20 on call 3-grams, then Levenshtein distance in calls / longer length (rapidfuzz). 0 unseen sequences have distance 0 (expected: an exact match would make them seen). Window share is undefined for 279 sequences shorter than 16 calls. Label rows count (sequence, label) pairs.

| measure | sequences | n | median [quartiles] |
|---|---|---|---|
| nearest January distance | all unseen sequences | 1,872 | 0.083 [0.031–0.193] |
| nearest January distance | benign | 1,507 | 0.077 [0.029–0.172] |
| nearest January distance | malware | 398 | 0.139 [0.039–0.333] |
| share of 16-call windows in January | all unseen sequences | 1,593 | 1.000 [0.933–1.000] |
| share of 16-call windows in January | benign | 1,332 | 1.000 [0.930–1.000] |
| share of 16-call windows in January | malware | 283 | 1.000 [0.959–1.000] |

**Histogram (number of (sequence, label) pairs):**

| bin | distance, benign | distance, malware | window share, benign | window share, malware |
|---|---|---|---|---|
| 0.0–0.1 | 877 | 167 | 36 | 16 |
| 0.1–0.2 | 319 | 68 | 1 | 1 |
| 0.2–0.3 | 141 | 46 | 3 | 0 |
| 0.3–0.4 | 62 | 24 | 8 | 3 |
| 0.4–0.5 | 43 | 17 | 7 | 1 |
| 0.5–0.6 | 20 | 32 | 16 | 2 |
| 0.6–0.7 | 14 | 7 | 22 | 2 |
| 0.7–0.8 | 15 | 8 | 65 | 11 |
| 0.8–0.9 | 3 | 7 | 108 | 16 |
| 0.9–1.0 | 13 | 22 | 1066 | 231 |

**Unseen April reports by number of chunks:**

| chunks | unseen April reports | nearest distance, median [quartiles] | window share, median [quartiles] |
|---|---|---|---|
| 1 | 3,629 | 0.176 [0.100–0.231] | 1.000 [0.412–1.000] |
| 2-3 | 4,207 | 0.027 [0.012–0.067] | 1.000 [1.000–1.000] |
| 4-8 | 3,237 | 0.031 [0.004–0.158] | 0.963 [0.855–1.000] |

**Detection by distance quartile and by window share** (quartiles over unique unseen sequences; the window share has its median at 100%, so it is split into 100%, the rest above its lowest quartile, the lowest quartile, and sequences too short for a window; global April thresholds (a) and January thresholds (b); 95% intervals from the group bootstrap):

| April reports | model | n (malware) | AUC | TPR@1% (a) | FPR (a) | TPR@1% (b) | April FPR (b) |
|---|---|---|---|---|---|---|---|
| seen in January | released Nebula | 6,329 (2,914) | 0.9865 [0.9709, 0.9944] | 82.1% [71.8%, 89.5%] | 0.7% [0.4%, 1.1%] | 82.8% [73.4%, 90.2%] | 1.0% [0.5%, 1.8%] |
| seen in January | two-level K=8 | 6,329 (2,914) | 0.9909 [0.9808, 0.9962] | 87.5% [77.1%, 93.8%] | 1.1% [0.4%, 1.8%] | 92.0% [85.4%, 96.6%] | 2.0% [1.1%, 3.5%] |
| seen in January | LightGBM bag of API names | 6,329 (2,914) | 0.9749 [0.9447, 0.9904] | 79.0% [66.1%, 88.4%] | 1.1% [0.5%, 2.0%] | 78.6% [66.9%, 88.3%] | 1.1% [0.4%, 2.4%] |
| unseen, all | released Nebula | 11,073 (6,485) | 0.9371 [0.8897, 0.9672] | 71.8% [56.3%, 82.1%] | 1.2% [0.9%, 1.7%] | 73.9% [59.0%, 83.8%] | 1.7% [1.1%, 2.6%] |
| unseen, all | two-level K=8 | 11,073 (6,485) | 0.9392 [0.8847, 0.9713] | 68.9% [48.0%, 81.4%] | 0.9% [0.5%, 1.5%] | 81.2% [66.7%, 89.3%] | 3.6% [2.6%, 5.1%] |
| unseen, all | LightGBM bag of API names | 11,073 (6,485) | 0.9384 [0.8917, 0.9754] | 55.7% [18.2%, 72.2%] | 0.9% [0.3%, 1.4%] | 48.7% [30.7%, 67.2%] | 0.9% [0.6%, 1.3%] |
| distance Q1 (≤ 0.031) | released Nebula | 4,017 (2,816) | 0.9775 [0.9107, 0.9959] | 87.4% [56.6%, 96.0%] | 0.9% [0.4%, 1.8%] | 88.1% [57.6%, 96.4%] | 1.2% [0.6%, 2.4%] |
| distance Q1 (≤ 0.031) | two-level K=8 | 4,017 (2,816) | 0.9828 [0.9382, 0.9945] | 85.7% [49.8%, 95.0%] | 0.2% [0.0%, 1.0%] | 88.9% [60.5%, 97.0%] | 2.7% [1.3%, 4.8%] |
| distance Q1 (≤ 0.031) | LightGBM bag of API names | 4,017 (2,816) | 0.9499 [0.8558, 0.9946] | 68.5% [14.0%, 93.9%] | 1.1% [0.2%, 2.1%] | 57.9% [23.4%, 84.0%] | 1.0% [0.4%, 2.0%] |
| distance Q2 (≤ 0.083) | released Nebula | 1,896 (1,129) | 0.9026 [0.7818, 0.9705] | 66.3% [37.0%, 86.0%] | 2.0% [0.8%, 3.3%] | 68.2% [41.0%, 86.7%] | 2.6% [1.2%, 4.4%] |
| distance Q2 (≤ 0.083) | two-level K=8 | 1,896 (1,129) | 0.9258 [0.8435, 0.9717] | 38.4% [15.2%, 68.5%] | 0.1% [0.0%, 1.3%] | 69.6% [41.1%, 88.2%] | 3.8% [2.4%, 5.7%] |
| distance Q2 (≤ 0.083) | LightGBM bag of API names | 1,896 (1,129) | 0.9495 [0.9096, 0.9715] | 64.3% [20.6%, 84.0%] | 2.2% [0.8%, 3.8%] | 56.5% [33.2%, 77.1%] | 2.1% [1.0%, 3.3%] |
| distance Q3 (≤ 0.193) | released Nebula | 2,757 (1,339) | 0.9441 [0.8487, 0.9722] | 47.6% [21.3%, 58.0%] | 0.6% [0.3%, 1.4%] | 53.3% [27.0%, 61.8%] | 1.1% [0.5%, 2.1%] |
| distance Q3 (≤ 0.193) | two-level K=8 | 2,757 (1,339) | 0.9518 [0.8321, 0.9834] | 59.5% [13.8%, 83.2%] | 1.3% [0.2%, 3.0%] | 82.2% [47.5%, 92.4%] | 3.9% [1.9%, 7.7%] |
| distance Q3 (≤ 0.193) | LightGBM bag of API names | 2,757 (1,339) | 0.9421 [0.8816, 0.9780] | 9.5% [1.6%, 29.1%] | 0.5% [0.1%, 1.2%] | 5.0% [1.7%, 21.0%] | 0.4% [0.2%, 0.9%] |
| distance Q4 (> 0.193) | released Nebula | 2,403 (1,201) | 0.8909 [0.7395, 0.9627] | 67.1% [29.6%, 85.4%] | 1.8% [0.8%, 4.5%] | 68.8% [33.6%, 87.8%] | 2.4% [1.0%, 6.4%] |
| distance Q4 (> 0.193) | two-level K=8 | 2,403 (1,201) | 0.8277 [0.6091, 0.9539] | 68.6% [33.5%, 87.2%] | 1.7% [0.7%, 4.4%] | 72.9% [41.0%, 89.6%] | 4.1% [2.6%, 8.6%] |
| distance Q4 (> 0.193) | LightGBM bag of API names | 2,403 (1,201) | 0.9586 [0.8695, 0.9836] | 69.2% [10.9%, 86.3%] | 0.4% [0.1%, 1.4%] | 68.6% [33.2%, 86.5%] | 0.4% [0.1%, 1.4%] |
| window share = 100% | released Nebula | 5,886 (3,660) | 0.9822 [0.9527, 0.9917] | 83.7% [64.9%, 91.8%] | 1.3% [0.7%, 2.0%] | 85.3% [68.2%, 92.7%] | 1.6% [0.9%, 2.5%] |
| window share = 100% | two-level K=8 | 5,886 (3,660) | 0.9818 [0.9580, 0.9903] | 71.9% [42.0%, 87.7%] | 0.3% [0.1%, 1.2%] | 88.5% [74.4%, 94.4%] | 2.9% [1.8%, 4.3%] |
| window share = 100% | LightGBM bag of API names | 5,886 (3,660) | 0.9459 [0.8801, 0.9830] | 61.9% [15.2%, 83.1%] | 1.2% [0.4%, 1.9%] | 49.7% [26.8%, 69.0%] | 1.1% [0.6%, 1.7%] |
| window share 0.933–<100% | released Nebula | 1,265 (957) | 0.7798 [0.4888, 0.9375] | 47.8% [4.5%, 82.1%] | 1.6% [0.0%, 3.6%] | 49.7% [6.1%, 83.1%] | 2.3% [0.7%, 4.7%] |
| window share 0.933–<100% | two-level K=8 | 1,265 (957) | 0.8253 [0.6053, 0.9557] | 44.2% [0.6%, 79.9%] | 0.0% [0.0%, 1.5%] | 51.3% [7.7%, 84.8%] | 4.9% [2.4%, 8.2%] |
| window share 0.933–<100% | LightGBM bag of API names | 1,265 (957) | 0.8760 [0.6353, 0.9775] | 55.8% [3.6%, 83.9%] | 2.4% [0.3%, 5.2%] | 55.7% [3.8%, 83.9%] | 2.1% [0.7%, 3.9%] |
| window share ≤ 0.933 (lowest quartile) | released Nebula | 2,256 (970) | 0.8596 [0.6133, 0.9459] | 46.8% [11.1%, 62.0%] | 0.9% [0.4%, 3.0%] | 50.9% [12.0%, 63.4%] | 1.5% [0.6%, 4.7%] |
| window share ≤ 0.933 (lowest quartile) | two-level K=8 | 2,256 (970) | 0.8487 [0.4289, 0.9619] | 70.8% [6.5%, 88.3%] | 0.5% [0.1%, 1.9%] | 76.2% [15.4%, 92.0%] | 3.3% [2.0%, 8.1%] |
| window share ≤ 0.933 (lowest quartile) | LightGBM bag of API names | 2,256 (970) | 0.9644 [0.9082, 0.9811] | 17.9% [3.9%, 72.4%] | 0.4% [0.1%, 1.6%] | 17.8% [4.5%, 70.3%] | 0.4% [0.1%, 1.5%] |
| shorter than 16 calls (no window) | released Nebula | 1,666 (898) | 0.9618 [0.8757, 0.9884] | 75.8% [30.5%, 91.6%] | 1.4% [0.6%, 3.3%] | 77.8% [39.3%, 93.4%] | 2.2% [1.0%, 4.7%] |
| shorter than 16 calls (no window) | two-level K=8 | 1,666 (898) | 0.9579 [0.8655, 0.9881] | 80.8% [43.0%, 94.8%] | 3.8% [1.3%, 7.6%] | 88.9% [64.7%, 96.7%] | 5.9% [2.7%, 12.7%] |
| shorter than 16 calls (no window) | LightGBM bag of API names | 1,666 (898) | 0.9656 [0.8804, 0.9876] | 71.0% [6.5%, 89.0%] | 0.4% [0.0%, 1.2%] | 70.6% [25.6%, 89.8%] | 0.4% [0.0%, 1.2%] |

**Decision.** "Unseen" is mostly near January: the median unseen sequence differs from its nearest January sequence in 8.3% of its calls, and the median share of its 16-call windows already seen in January is 100%; released Nebula catches 87.4% of malware in the nearest quartile but only 47.6%–67.1% in the other three (not monotone, wide intervals).

## Test 4: size of the long-report group

Share of each count that falls in each chunk group (512-token chunks of Nebula's tokenized report; 12 April reports need more than 8 chunks and are counted in 4-8). Misses = malware at or below the 1% FPR threshold: (a) from April benign scores, (b) from January validation. 95% intervals from the group bootstrap.

| population | count | n | 1 chunk | 2-3 chunks | 4-8 chunks |
|---|---|---|---|---|---|
| all April | April reports | 17,402 | 36.5% [27.8, 47.4] | 34.9% [23.6, 46.9] | 28.5% [19.3, 38.0] |
| all April | April malware | 9,399 | 30.4% [18.0, 45.4] | 39.1% [23.9, 54.7] | 30.5% [17.2, 45.2] |
| all April | released Nebula misses (a) | 2,352 | 46.8% [30.2, 63.9] | 32.4% [18.8, 46.1] | 20.9% [9.5, 34.5] |
| all April | released Nebula misses (b) | 2,195 | 46.6% [30.1, 63.5] | 31.7% [18.7, 45.5] | 21.7% [9.7, 36.1] |
| all April | two-level K=8 misses (a) | 2,381 | 25.7% [14.9, 39.2] | 50.4% [32.1, 66.5] | 23.9% [11.7, 38.7] |
| all April | two-level K=8 misses (b) | 1,451 | 33.6% [19.8, 49.4] | 39.1% [23.6, 55.4] | 27.3% [11.8, 44.7] |
| seen | April reports | 6,329 | 43.1% [30.0, 58.8] | 29.5% [12.5, 47.8] | 27.3% [17.2, 39.3] |
| seen | April malware | 2,914 | 29.0% [19.0, 43.0] | 25.8% [11.0, 40.9] | 45.2% [28.5, 61.0] |
| seen | released Nebula misses (a) | 521 | 77.7% [56.5, 89.5] | 10.4% [2.4, 26.0] | 11.9% [5.2, 24.4] |
| seen | released Nebula misses (b) | 500 | 79.2% [59.5, 90.7] | 9.0% [1.8, 23.1] | 11.8% [4.8, 24.3] |
| seen | two-level K=8 misses (a) | 363 | 64.7% [39.8, 86.5] | 11.0% [2.6, 30.7] | 24.2% [6.8, 46.1] |
| seen | two-level K=8 misses (b) | 233 | 88.4% [71.1, 95.0] | 3.9% [0.9, 10.8] | 7.7% [2.8, 20.8] |
| unseen | April reports | 11,073 | 32.8% [20.7, 46.0] | 38.0% [24.7, 52.3] | 29.2% [16.3, 42.2] |
| unseen | April malware | 6,485 | 31.0% [12.9, 53.1] | 45.1% [24.3, 66.5] | 23.9% [7.6, 43.0] |
| unseen | released Nebula misses (a) | 1,831 | 38.0% [17.8, 60.4] | 38.6% [21.6, 57.3] | 23.4% [9.4, 39.9] |
| unseen | released Nebula misses (b) | 1,695 | 37.0% [16.7, 59.4] | 38.4% [21.6, 57.5] | 24.6% [9.7, 43.0] |
| unseen | two-level K=8 misses (a) | 2,018 | 18.7% [8.8, 32.0] | 57.5% [37.5, 73.4] | 23.8% [10.3, 40.9] |
| unseen | two-level K=8 misses (b) | 1,218 | 23.1% [10.9, 38.8] | 45.9% [27.4, 64.7] | 31.0% [12.3, 51.3] |

**Decision.** Reports that need 4-8 chunks are 28.5% of April and hold 20.9% of released Nebula's misses at 1% FPR; reports beyond the first chunk (2-8 chunks) hold 53.2%, so that is the most a model that reads more chunks could fix.

## Summary

1. **Stop the two-level model in its current form:** a rank average of released Nebula and a 5-second bag-of-API LightGBM matches or beats it (0.9745 / 79.7% / 55.1% vs 0.9639 / 74.7% / 54.3%), with no training of any Transformer.
2. **Its gain does not come from the extra chunks:** it improves reports that fit in one chunk (TPR at 1% FPR 78.6% vs 61.5% for Nebula) and is worse on 2–3-chunk reports (67.4% vs 79.3%).
3. **Long reports do hold signal** (bag model AUC +0.12 on 4–8-chunk reports with the full trace, test 2) and 53% of Nebula's misses need more than one chunk, so long context is not worthless, but this model does not capture it.
4. **Most of April's loss is on "unseen" sequences that are near-copies of January** (median 8.3% of calls edited, median 100% of 16-call windows already seen), so robustness to small edits is a better target than length.
5. **The test set cannot resolve gains of this size** (group-bootstrap intervals of about ±0.02 AUC and ±10–20 TPR points), so any new GPU run should target a measured gap and be judged with group-level intervals.
