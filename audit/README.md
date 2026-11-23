# Independent audit: recomputed numbers against the reported ones

**Summary in plain English.** We rebuilt the headline numbers from the stored files with a separate script that shares no code with the pipeline (it imports only numpy, scikit-learn, sentencepiece and the Python standard library), and 172 of the 174 comparisons agree with the reports. All 144 clean-metric numbers of the eight final-model sets (per-seed mean, per-seed spread and 10-seed ensemble of pAUC@1e-2, TPR@1e-3, TPR@1e-2, AUC, F1 at logit 0, and pAUC@1e-3) match stage_i/tables.md to the last printed digit, with a largest gap of 4.9e-4 (half a unit of the last digit is 5e-4). All 24 attack numbers for M1 and M3 (random 20 / 50 / 100 prepend, LightGBM 50 prepend, white-box after 20 and 50 steps, mean and spread) match stage_j/report_table.md. One definition needs a warning: scikit-learn's `roc_auc_score(max_fpr=0.01)` does not return the number in the reports; it returns the McClish-standardised form (0.5 = chance, e.g. 0.834 for the fixed-tokenizer M1 seed 0), while the reports use the normalised partial AUC (area under the ROC curve up to 1% FPR divided by 0.01, chance 0.005, 0.686 on average); converting the scikit-learn value back with the standard formula reproduces the reported definition (difference 4e-16 to the direct computation). **The two numbers that do NOT match are both the sentence "80 and 8 benign reports lie above the 1% and 0.1% thresholds":** that is exactly true for 73 of the 80 model-seeds at 1% and for 77 of 80 at 0.1%; in the other 7 and 3 cases between 2 and 6 benign reports have exactly the same float32 logit as the threshold, so the strict "above" count is 77 to 79 (and 6 to 7) instead of 80 (and 8). All ten cases are explained by those ties; the thresholds are the ones defined, every reported attack and clean number is computed with the same strict rule and matches, so no reported table changes, but the clean false-positive rate at the "1%" threshold is 0.96% to 1.00% for those seeds, not exactly 1%. The spot check shows what the 'random 20 prepend' attack does to three April malware reports: the one header token of the report (`apis`) is followed by the 20 added calls taken from benign reports (about 110 to 120 tokens, readable API calls such as `kernel32 heapalloc 0x45f0 ...`), and the original report's own calls only start at token position 120, 118 and 109, so in a 512-token window they have lost up to a quarter of their room. The rebuilt reports have exactly the stored token counts for all 17,402 April reports, and the stored first 512 tokens equal the stored model-input rows for all of them. **What this audit does not do:** it takes the stored logits, labels, scores and call-token store as given (it does not retrain or rescore a model, so it cannot detect an error inside a model run), the sampler is re-implemented from its written definition and validated through the token counts, not by feeding the rebuilt tokens to a model, and the Stage J score files are kernel outputs kept outside the git repository (their sha256 prefixes are listed above).

**172 of 174 comparisons MATCH; 2 DIFFERENT.** Recomputed by `baseline/audit_independent.py` (imports nothing from `baseline/`; only numpy, scikit-learn, sentencepiece; CPU; stored files only). A number MATCHes if the recomputed value, written with the decimals of the report, equals the reported number. Input files (first 16 hex digits of the sha256):

| input | sha256 (16) |
|---|---|
| April labels | `54308b0250636142` |
| Stage I logits (fixed tokenizer) | `6958ca2c89f4047e` |
| Step 5 logits (M1, M3, current tokenizer) | `3864e4aa379a1651` |
| Stage G logits (M2, M4, current tokenizer) | `03728738424183e5` |
| stage_i/tables.md | `70339d1f578f8f2c` |
| stage_j/report_table.md | `1e512c657e472705` |
| group split | `84020227c4dbbf16` |
| Stage J scores m1 | `998cbd4147e5403a` |
| Stage J scores m3 | `f8bddd09b0f0d232` |
| call-token store | `0a8b75e67515078e` |
| January labels | `035e3e7eb3cc5aee` |
| tokenizer | `8bcdc5f4160f3e38` |
| model input rows x_test | `2afa48f35afa4ff5` |

## 1. Clean metrics (stage_i/tables.md): maximum absolute difference per metric (recomputed, unrounded, against the reported rounded number; a match needs at most half a unit of the last printed digit)

| metric | max abs difference | half unit of the last digit |
|---|---|---|
| AUC (ensemble) | 4.52e-05 | 5.0e-05 |
| AUC (per-seed mean) | 4.43e-05 | 5.0e-05 |
| AUC (per-seed std) | 4.76e-05 | 5.0e-05 |
| F1 (ensemble) | 4.23e-04 | 5.0e-04 |
| F1 (per-seed mean) | 3.88e-04 | 5.0e-04 |
| F1 (per-seed std) | 4.17e-04 | 5.0e-04 |
| TPR@1e-2 (ensemble) | 4.94e-04 | 5.0e-04 |
| TPR@1e-2 (per-seed mean) | 3.82e-04 | 5.0e-04 |
| TPR@1e-2 (per-seed std) | 4.94e-04 | 5.0e-04 |
| TPR@1e-3 (ensemble) | 4.04e-04 | 5.0e-04 |
| TPR@1e-3 (per-seed mean) | 4.52e-04 | 5.0e-04 |
| TPR@1e-3 (per-seed std) | 4.67e-04 | 5.0e-04 |
| pAUC@1e-2 (ensemble) | 4.48e-04 | 5.0e-04 |
| pAUC@1e-2 (per-seed mean) | 4.94e-04 | 5.0e-04 |
| pAUC@1e-2 (per-seed std) | 4.94e-04 | 5.0e-04 |
| pAUC@1e-3 (ensemble) | 4.03e-04 | 5.0e-04 |
| pAUC@1e-3 (per-seed mean) | 3.80e-04 | 5.0e-04 |
| pAUC@1e-3 (per-seed std) | 4.42e-04 | 5.0e-04 |

Definition note: `roc_auc_score(max_fpr=0.01)` of scikit-learn returns the McClish-standardised partial AUC (0.5 = chance), e.g. seed 0 of the fixed-tokenizer M1: sklearn 0.8339; the reports use the normalised partial AUC (area / 0.01; chance 0.005): converted from sklearn 0.6695, computed directly 0.6695. Over all 80 model-seeds and 8 ensembles the converted-from-sklearn and the direct values differ by at most 4.4e-16; TPR by the sorted-threshold rule and by the ROC-curve rule differ by at most 0.0e+00.

## 2. Thresholds

April: 9399 malware, 8003 benign reports; floor(0.01 x 8003) = 80, floor(0.001 x 8003) = 8. For 80 model-seeds (both tokenizer sets) the threshold is the benign logit at rank floor(f x n) in the descending sort and a report is flagged if its logit is strictly above it. Exactly 80 / 8 benign reports lie above it except in the 10 cases below, where several benign reports have EXACTLY the logit of the threshold (float32 ties), so the strict count is smaller; the threshold value itself is the one defined.

| set | model | seed | level | benign above (expected) | benign equal to the threshold | malware equal to the threshold | explained by ties |
|---|---|---|---|---|---|---|---|
| current tokenizer | M1 | 0 | 1% | 79 (80) | 3 | 0 | yes |
| current tokenizer | M1 | 5 | 0.1% | 6 (8) | 3 | 0 | yes |
| current tokenizer | M1 | 7 | 0.1% | 7 (8) | 3 | 0 | yes |
| current tokenizer | M2 | 7 | 1% | 79 (80) | 2 | 0 | yes |
| current tokenizer | M3 | 6 | 1% | 79 (80) | 2 | 0 | yes |
| current tokenizer | M4 | 0 | 1% | 79 (80) | 5 | 0 | yes |
| current tokenizer | M4 | 8 | 1% | 79 (80) | 3 | 0 | yes |
| fixed tokenizer | M1 | 5 | 0.1% | 7 (8) | 3 | 0 | yes |
| fixed tokenizer | M2 | 9 | 1% | 79 (80) | 2 | 0 | yes |
| fixed tokenizer | M4 | 2 | 1% | 77 (80) | 6 | 6 | yes |

## 3. Links between stored files

| check | value |
|---|---|
| M1_row0_vs_stage_I_logits_max_abs_diff | 3.81e-05 |
| M3_row0_vs_stage_I_logits_max_abs_diff | 0.00e+00 |
| M1_threshold_recomputed_vs_stored_in_wb_files_max_abs_diff | 1.43e-06 |
| M3_threshold_recomputed_vs_stored_in_wb_files_max_abs_diff | 0.00e+00 |

## 4. Spot check and rebuild

`audit/spot_check.md` shows the decoded first 120 tokens of three April malware reports (rows [0, 1, 2]) with the 20 prepended calls. Summary: row 0: header 1 tokens, 20 added calls 119 tokens, original calls start at token position 120; row 1: header 1 tokens, 20 added calls 117 tokens, original calls start at token position 118; row 2: header 1 tokens, 20 added calls 108 tokens, original calls start at token position 109.

## Every compared number

| part | item | recomputed | reported | status |
|---|---|---|---|---|
| 1 clean | current tokenizer M1 TPR@1e-3 per-seed mean | 0.5407 | 0.541 | MATCH |
| 1 clean | current tokenizer M1 TPR@1e-3 per-seed std | 0.0945 | 0.095 | MATCH |
| 1 clean | current tokenizer M1 TPR@1e-3 ensemble | 0.6222 | 0.622 | MATCH |
| 1 clean | current tokenizer M1 TPR@1e-2 per-seed mean | 0.7802 | 0.780 | MATCH |
| 1 clean | current tokenizer M1 TPR@1e-2 per-seed std | 0.0376 | 0.038 | MATCH |
| 1 clean | current tokenizer M1 TPR@1e-2 ensemble | 0.8435 | 0.843 | MATCH |
| 1 clean | current tokenizer M1 AUC per-seed mean | 0.96671 | 0.9667 | MATCH |
| 1 clean | current tokenizer M1 AUC per-seed std | 0.00710 | 0.0071 | MATCH |
| 1 clean | current tokenizer M1 AUC ensemble | 0.97383 | 0.9738 | MATCH |
| 1 clean | current tokenizer M1 F1 per-seed mean | 0.8991 | 0.899 | MATCH |
| 1 clean | current tokenizer M1 F1 per-seed std | 0.0214 | 0.021 | MATCH |
| 1 clean | current tokenizer M1 F1 ensemble | 0.9214 | 0.921 | MATCH |
| 1 clean | current tokenizer M1 pAUC@1e-2 per-seed mean | 0.6736 | 0.674 | MATCH |
| 1 clean | current tokenizer M1 pAUC@1e-2 per-seed std | 0.0531 | 0.053 | MATCH |
| 1 clean | current tokenizer M1 pAUC@1e-2 ensemble | 0.7391 | 0.739 | MATCH |
| 1 clean | current tokenizer M1 pAUC@1e-3 per-seed mean | 0.4258 | 0.426 | MATCH |
| 1 clean | current tokenizer M1 pAUC@1e-3 per-seed std | 0.0858 | 0.086 | MATCH |
| 1 clean | current tokenizer M1 pAUC@1e-3 ensemble | 0.5476 | 0.548 | MATCH |
| 1 clean | current tokenizer M2 TPR@1e-3 per-seed mean | 0.3445 | 0.344 | MATCH |
| 1 clean | current tokenizer M2 TPR@1e-3 per-seed std | 0.1892 | 0.189 | MATCH |
| 1 clean | current tokenizer M2 TPR@1e-3 ensemble | 0.5318 | 0.532 | MATCH |
| 1 clean | current tokenizer M2 TPR@1e-2 per-seed mean | 0.7513 | 0.751 | MATCH |
| 1 clean | current tokenizer M2 TPR@1e-2 per-seed std | 0.0675 | 0.068 | MATCH |
| 1 clean | current tokenizer M2 TPR@1e-2 ensemble | 0.8021 | 0.802 | MATCH |
| 1 clean | current tokenizer M2 AUC per-seed mean | 0.96698 | 0.9670 | MATCH |
| 1 clean | current tokenizer M2 AUC per-seed std | 0.01048 | 0.0105 | MATCH |
| 1 clean | current tokenizer M2 AUC ensemble | 0.97495 | 0.9749 | MATCH |
| 1 clean | current tokenizer M2 F1 per-seed mean | 0.8879 | 0.888 | MATCH |
| 1 clean | current tokenizer M2 F1 per-seed std | 0.0382 | 0.038 | MATCH |
| 1 clean | current tokenizer M2 F1 ensemble | 0.9143 | 0.914 | MATCH |
| 1 clean | current tokenizer M2 pAUC@1e-2 per-seed mean | 0.5620 | 0.562 | MATCH |
| 1 clean | current tokenizer M2 pAUC@1e-2 per-seed std | 0.1465 | 0.146 | MATCH |
| 1 clean | current tokenizer M2 pAUC@1e-2 ensemble | 0.6752 | 0.675 | MATCH |
| 1 clean | current tokenizer M2 pAUC@1e-3 per-seed mean | 0.2020 | 0.202 | MATCH |
| 1 clean | current tokenizer M2 pAUC@1e-3 per-seed std | 0.1156 | 0.116 | MATCH |
| 1 clean | current tokenizer M2 pAUC@1e-3 ensemble | 0.3169 | 0.317 | MATCH |
| 1 clean | current tokenizer M3 TPR@1e-3 per-seed mean | 0.5898 | 0.590 | MATCH |
| 1 clean | current tokenizer M3 TPR@1e-3 per-seed std | 0.0292 | 0.029 | MATCH |
| 1 clean | current tokenizer M3 TPR@1e-3 ensemble | 0.6028 | 0.603 | MATCH |
| 1 clean | current tokenizer M3 TPR@1e-2 per-seed mean | 0.7901 | 0.790 | MATCH |
| 1 clean | current tokenizer M3 TPR@1e-2 per-seed std | 0.0082 | 0.008 | MATCH |
| 1 clean | current tokenizer M3 TPR@1e-2 ensemble | 0.8015 | 0.801 | MATCH |
| 1 clean | current tokenizer M3 AUC per-seed mean | 0.96939 | 0.9694 | MATCH |
| 1 clean | current tokenizer M3 AUC per-seed std | 0.00435 | 0.0044 | MATCH |
| 1 clean | current tokenizer M3 AUC ensemble | 0.97479 | 0.9748 | MATCH |
| 1 clean | current tokenizer M3 F1 per-seed mean | 0.9081 | 0.908 | MATCH |
| 1 clean | current tokenizer M3 F1 per-seed std | 0.0111 | 0.011 | MATCH |
| 1 clean | current tokenizer M3 F1 ensemble | 0.9210 | 0.921 | MATCH |
| 1 clean | current tokenizer M3 pAUC@1e-2 per-seed mean | 0.7098 | 0.710 | MATCH |
| 1 clean | current tokenizer M3 pAUC@1e-2 per-seed std | 0.0149 | 0.015 | MATCH |
| 1 clean | current tokenizer M3 pAUC@1e-2 ensemble | 0.7311 | 0.731 | MATCH |
| 1 clean | current tokenizer M3 pAUC@1e-3 per-seed mean | 0.4772 | 0.477 | MATCH |
| 1 clean | current tokenizer M3 pAUC@1e-3 per-seed std | 0.0510 | 0.051 | MATCH |
| 1 clean | current tokenizer M3 pAUC@1e-3 ensemble | 0.5358 | 0.536 | MATCH |
| 1 clean | current tokenizer M4 TPR@1e-3 per-seed mean | 0.4613 | 0.461 | MATCH |
| 1 clean | current tokenizer M4 TPR@1e-3 per-seed std | 0.1740 | 0.174 | MATCH |
| 1 clean | current tokenizer M4 TPR@1e-3 ensemble | 0.6283 | 0.628 | MATCH |
| 1 clean | current tokenizer M4 TPR@1e-2 per-seed mean | 0.7778 | 0.778 | MATCH |
| 1 clean | current tokenizer M4 TPR@1e-2 per-seed std | 0.0215 | 0.021 | MATCH |
| 1 clean | current tokenizer M4 TPR@1e-2 ensemble | 0.8120 | 0.812 | MATCH |
| 1 clean | current tokenizer M4 AUC per-seed mean | 0.96791 | 0.9679 | MATCH |
| 1 clean | current tokenizer M4 AUC per-seed std | 0.00747 | 0.0075 | MATCH |
| 1 clean | current tokenizer M4 AUC ensemble | 0.97668 | 0.9767 | MATCH |
| 1 clean | current tokenizer M4 F1 per-seed mean | 0.9104 | 0.910 | MATCH |
| 1 clean | current tokenizer M4 F1 per-seed std | 0.0104 | 0.010 | MATCH |
| 1 clean | current tokenizer M4 F1 ensemble | 0.9174 | 0.917 | MATCH |
| 1 clean | current tokenizer M4 pAUC@1e-2 per-seed mean | 0.6625 | 0.663 | MATCH |
| 1 clean | current tokenizer M4 pAUC@1e-2 per-seed std | 0.0362 | 0.036 | MATCH |
| 1 clean | current tokenizer M4 pAUC@1e-2 ensemble | 0.7249 | 0.725 | MATCH |
| 1 clean | current tokenizer M4 pAUC@1e-3 per-seed mean | 0.2729 | 0.273 | MATCH |
| 1 clean | current tokenizer M4 pAUC@1e-3 per-seed std | 0.1238 | 0.124 | MATCH |
| 1 clean | current tokenizer M4 pAUC@1e-3 ensemble | 0.4508 | 0.451 | MATCH |
| 1 clean | fixed tokenizer M1 TPR@1e-3 per-seed mean | 0.5364 | 0.536 | MATCH |
| 1 clean | fixed tokenizer M1 TPR@1e-3 per-seed std | 0.0600 | 0.060 | MATCH |
| 1 clean | fixed tokenizer M1 TPR@1e-3 ensemble | 0.6632 | 0.663 | MATCH |
| 1 clean | fixed tokenizer M1 TPR@1e-2 per-seed mean | 0.7914 | 0.791 | MATCH |
| 1 clean | fixed tokenizer M1 TPR@1e-2 per-seed std | 0.0196 | 0.020 | MATCH |
| 1 clean | fixed tokenizer M1 TPR@1e-2 ensemble | 0.8373 | 0.837 | MATCH |
| 1 clean | fixed tokenizer M1 AUC per-seed mean | 0.96387 | 0.9639 | MATCH |
| 1 clean | fixed tokenizer M1 AUC per-seed std | 0.01106 | 0.0111 | MATCH |
| 1 clean | fixed tokenizer M1 AUC ensemble | 0.97049 | 0.9705 | MATCH |
| 1 clean | fixed tokenizer M1 F1 per-seed mean | 0.8913 | 0.891 | MATCH |
| 1 clean | fixed tokenizer M1 F1 per-seed std | 0.0268 | 0.027 | MATCH |
| 1 clean | fixed tokenizer M1 F1 ensemble | 0.9126 | 0.913 | MATCH |
| 1 clean | fixed tokenizer M1 pAUC@1e-2 per-seed mean | 0.6864 | 0.686 | MATCH |
| 1 clean | fixed tokenizer M1 pAUC@1e-2 per-seed std | 0.0262 | 0.026 | MATCH |
| 1 clean | fixed tokenizer M1 pAUC@1e-2 ensemble | 0.7558 | 0.756 | MATCH |
| 1 clean | fixed tokenizer M1 pAUC@1e-3 per-seed mean | 0.3976 | 0.398 | MATCH |
| 1 clean | fixed tokenizer M1 pAUC@1e-3 per-seed std | 0.0950 | 0.095 | MATCH |
| 1 clean | fixed tokenizer M1 pAUC@1e-3 ensemble | 0.5521 | 0.552 | MATCH |
| 1 clean | fixed tokenizer M2 TPR@1e-3 per-seed mean | 0.3807 | 0.381 | MATCH |
| 1 clean | fixed tokenizer M2 TPR@1e-3 per-seed std | 0.1648 | 0.165 | MATCH |
| 1 clean | fixed tokenizer M2 TPR@1e-3 ensemble | 0.5410 | 0.541 | MATCH |
| 1 clean | fixed tokenizer M2 TPR@1e-2 per-seed mean | 0.7719 | 0.772 | MATCH |
| 1 clean | fixed tokenizer M2 TPR@1e-2 per-seed std | 0.0494 | 0.049 | MATCH |
| 1 clean | fixed tokenizer M2 TPR@1e-2 ensemble | 0.8013 | 0.801 | MATCH |
| 1 clean | fixed tokenizer M2 AUC per-seed mean | 0.96896 | 0.9690 | MATCH |
| 1 clean | fixed tokenizer M2 AUC per-seed std | 0.00731 | 0.0073 | MATCH |
| 1 clean | fixed tokenizer M2 AUC ensemble | 0.97522 | 0.9752 | MATCH |
| 1 clean | fixed tokenizer M2 F1 per-seed mean | 0.8979 | 0.898 | MATCH |
| 1 clean | fixed tokenizer M2 F1 per-seed std | 0.0219 | 0.022 | MATCH |
| 1 clean | fixed tokenizer M2 F1 ensemble | 0.9100 | 0.910 | MATCH |
| 1 clean | fixed tokenizer M2 pAUC@1e-2 per-seed mean | 0.6199 | 0.620 | MATCH |
| 1 clean | fixed tokenizer M2 pAUC@1e-2 per-seed std | 0.0799 | 0.080 | MATCH |
| 1 clean | fixed tokenizer M2 pAUC@1e-2 ensemble | 0.6983 | 0.698 | MATCH |
| 1 clean | fixed tokenizer M2 pAUC@1e-3 per-seed mean | 0.2701 | 0.270 | MATCH |
| 1 clean | fixed tokenizer M2 pAUC@1e-3 per-seed std | 0.1534 | 0.153 | MATCH |
| 1 clean | fixed tokenizer M2 pAUC@1e-3 ensemble | 0.4490 | 0.449 | MATCH |
| 1 clean | fixed tokenizer M3 TPR@1e-3 per-seed mean | 0.5666 | 0.567 | MATCH |
| 1 clean | fixed tokenizer M3 TPR@1e-3 per-seed std | 0.0468 | 0.047 | MATCH |
| 1 clean | fixed tokenizer M3 TPR@1e-3 ensemble | 0.5974 | 0.597 | MATCH |
| 1 clean | fixed tokenizer M3 TPR@1e-2 per-seed mean | 0.7903 | 0.790 | MATCH |
| 1 clean | fixed tokenizer M3 TPR@1e-2 per-seed std | 0.0185 | 0.019 | MATCH |
| 1 clean | fixed tokenizer M3 TPR@1e-2 ensemble | 0.7999 | 0.800 | MATCH |
| 1 clean | fixed tokenizer M3 AUC per-seed mean | 0.96932 | 0.9693 | MATCH |
| 1 clean | fixed tokenizer M3 AUC per-seed std | 0.00646 | 0.0065 | MATCH |
| 1 clean | fixed tokenizer M3 AUC ensemble | 0.97520 | 0.9752 | MATCH |
| 1 clean | fixed tokenizer M3 F1 per-seed mean | 0.9128 | 0.913 | MATCH |
| 1 clean | fixed tokenizer M3 F1 per-seed std | 0.0109 | 0.011 | MATCH |
| 1 clean | fixed tokenizer M3 F1 ensemble | 0.9191 | 0.919 | MATCH |
| 1 clean | fixed tokenizer M3 pAUC@1e-2 per-seed mean | 0.7048 | 0.705 | MATCH |
| 1 clean | fixed tokenizer M3 pAUC@1e-2 per-seed std | 0.0252 | 0.025 | MATCH |
| 1 clean | fixed tokenizer M3 pAUC@1e-2 ensemble | 0.7296 | 0.730 | MATCH |
| 1 clean | fixed tokenizer M3 pAUC@1e-3 per-seed mean | 0.4433 | 0.443 | MATCH |
| 1 clean | fixed tokenizer M3 pAUC@1e-3 per-seed std | 0.0892 | 0.089 | MATCH |
| 1 clean | fixed tokenizer M3 pAUC@1e-3 ensemble | 0.5316 | 0.532 | MATCH |
| 1 clean | fixed tokenizer M4 TPR@1e-3 per-seed mean | 0.4531 | 0.453 | MATCH |
| 1 clean | fixed tokenizer M4 TPR@1e-3 per-seed std | 0.1492 | 0.149 | MATCH |
| 1 clean | fixed tokenizer M4 TPR@1e-3 ensemble | 0.6290 | 0.629 | MATCH |
| 1 clean | fixed tokenizer M4 TPR@1e-2 per-seed mean | 0.7791 | 0.779 | MATCH |
| 1 clean | fixed tokenizer M4 TPR@1e-2 per-seed std | 0.0173 | 0.017 | MATCH |
| 1 clean | fixed tokenizer M4 TPR@1e-2 ensemble | 0.8027 | 0.803 | MATCH |
| 1 clean | fixed tokenizer M4 AUC per-seed mean | 0.96770 | 0.9677 | MATCH |
| 1 clean | fixed tokenizer M4 AUC per-seed std | 0.00524 | 0.0052 | MATCH |
| 1 clean | fixed tokenizer M4 AUC ensemble | 0.97768 | 0.9777 | MATCH |
| 1 clean | fixed tokenizer M4 F1 per-seed mean | 0.9109 | 0.911 | MATCH |
| 1 clean | fixed tokenizer M4 F1 per-seed std | 0.0133 | 0.013 | MATCH |
| 1 clean | fixed tokenizer M4 F1 ensemble | 0.9170 | 0.917 | MATCH |
| 1 clean | fixed tokenizer M4 pAUC@1e-2 per-seed mean | 0.6609 | 0.661 | MATCH |
| 1 clean | fixed tokenizer M4 pAUC@1e-2 per-seed std | 0.0354 | 0.035 | MATCH |
| 1 clean | fixed tokenizer M4 pAUC@1e-2 ensemble | 0.7192 | 0.719 | MATCH |
| 1 clean | fixed tokenizer M4 pAUC@1e-3 per-seed mean | 0.3189 | 0.319 | MATCH |
| 1 clean | fixed tokenizer M4 pAUC@1e-3 per-seed std | 0.1062 | 0.106 | MATCH |
| 1 clean | fixed tokenizer M4 pAUC@1e-3 ensemble | 0.4447 | 0.445 | MATCH |
| 2 thresholds | benign reports strictly above the 1% threshold, number of the 80 model-seeds with exactly 80 (expected floor(0.01 x 8003) = 80) | 73 of 80 exactly 80; the other 7 have 77 to 79 | 80 in every case | DIFFERENT |
| 2 thresholds | benign reports strictly above the 0.1% threshold, number of the 80 model-seeds with exactly 8 (expected floor(0.001 x 8003) = 8) | 77 of 80 exactly 8; the other 3 have 6 to 7 | 8 in every case | DIFFERENT |
| 2 thresholds | every exception explained by tied logits (benign reports with exactly the logit of the threshold: above < expected <= above + tied) | 10 of 10 exceptions explained | n/a (not stated in the reports) | MATCH |
| 3 attacks | M1 random 20 prepend detection mean (%) | 25.38 | 25.4 | MATCH |
| 3 attacks | M1 random 20 prepend detection std (%) | 7.85 | 7.8 | MATCH |
| 3 attacks | M1 random 50 prepend detection mean (%) | 7.43 | 7.4 | MATCH |
| 3 attacks | M1 random 50 prepend detection std (%) | 4.05 | 4.0 | MATCH |
| 3 attacks | M1 random 100 prepend detection mean (%) | 5.73 | 5.7 | MATCH |
| 3 attacks | M1 random 100 prepend detection std (%) | 5.13 | 5.1 | MATCH |
| 3 attacks | M1 lgbm 50 prepend detection mean (%) | 1.91 | 1.9 | MATCH |
| 3 attacks | M1 lgbm 50 prepend detection std (%) | 2.60 | 2.6 | MATCH |
| 3 attacks | M1 white-box 20 steps detection mean (%) | 1.58 | 1.6 | MATCH |
| 3 attacks | M1 white-box 20 steps detection std (%) | 1.57 | 1.6 | MATCH |
| 3 attacks | M1 white-box 50 steps detection mean (%) | 0.58 | 0.6 | MATCH |
| 3 attacks | M1 white-box 50 steps detection std (%) | 1.19 | 1.2 | MATCH |
| 3 attacks | M3 random 20 prepend detection mean (%) | 76.19 | 76.2 | MATCH |
| 3 attacks | M3 random 20 prepend detection std (%) | 2.29 | 2.3 | MATCH |
| 3 attacks | M3 random 50 prepend detection mean (%) | 65.05 | 65.1 | MATCH |
| 3 attacks | M3 random 50 prepend detection std (%) | 5.80 | 5.8 | MATCH |
| 3 attacks | M3 random 100 prepend detection mean (%) | 6.45 | 6.5 | MATCH |
| 3 attacks | M3 random 100 prepend detection std (%) | 1.32 | 1.3 | MATCH |
| 3 attacks | M3 lgbm 50 prepend detection mean (%) | 35.13 | 35.1 | MATCH |
| 3 attacks | M3 lgbm 50 prepend detection std (%) | 13.29 | 13.3 | MATCH |
| 3 attacks | M3 white-box 20 steps detection mean (%) | 48.68 | 48.7 | MATCH |
| 3 attacks | M3 white-box 20 steps detection std (%) | 6.27 | 6.3 | MATCH |
| 3 attacks | M3 white-box 50 steps detection mean (%) | 2.48 | 2.5 | MATCH |
| 3 attacks | M3 white-box 50 steps detection std (%) | 1.34 | 1.3 | MATCH |
| 4 rebuild | total token count of the rebuilt 'random 20 prepend' report vs the stored Stage J count, all 17,402 April reports | 17402 equal, 0 differ | all equal | MATCH |
| 4 rebuild | total token count of the unedited report vs the stored Stage J count, all April reports | 17402 equal, 0 differ | all equal | MATCH |
| 4 rebuild | first 512 tokens of the store vs the stored model-input rows x_test, all April reports | 17402 equal, 0 differ | all equal | MATCH |
