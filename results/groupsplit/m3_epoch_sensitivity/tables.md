# M3 epoch sensitivity check (NOTES 29): M1, M3 with 3 epochs (final) and M3 with 2 epochs side by side

All numbers are April (one evaluation per model; April opening 30 for M3-2ep); M1 and M3-3ep are the Stage I / Stage J models. Detection and padded-benign FPR at the 1% threshold of each model's own clean April benign scores unless stated. Cluster = hash_apis-group bootstrap (1,000 resamples, seed 0). **This is a sensitivity analysis: the final M3 stays the 3-epoch model unless the owner decides otherwise.**

## The three criteria of NOTES 29.4 (fixed before any computation)

| criterion | measured | outcome |
|---|---|---|
| (a) clean: M3-2ep minus M3-3ep in pAUC@1e-2 NOT resolved by the cluster bootstrap | +0.80 points, cluster 95% interval [-0.41, +2.36] (stratified [+0.09, +1.54]), 7 up / 3 down | **MET** |
| (b) LightGBM 50 prepend (1% threshold): M3-2ep above M1 with a cluster 95% interval of the difference that excludes 0 | +36.9 points, cluster 95% interval [+23.6, +50.4] (M3-2ep 38.8% against M1 1.9%) | **MET** |
| (c) padded-benign FPR of M3-2ep, random 50 prepend (1% threshold), 10-seed mean <= 1.5% | 1.01% ± 0.84 (cluster 95% interval of the seed mean [0.63, 1.47]) | **MET** |

## Clean April results (Stage I tables)

### Clean April test, 10 seeds each, one evaluation per model (M3 with 2 epochs next to the final M3 (3 epochs) and the final M1): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| M1 Nebula (final) | 10 | 0.536 ± 0.060 | 0.791 ± 0.020 | 0.9639 ± 0.0111 | 0.891 ± 0.027 | 0.686 ± 0.026 | 0.398 ± 0.095 |
| M3 ATT+bal, 3 epochs (final) | 10 | 0.567 ± 0.047 | 0.790 ± 0.019 | 0.9693 ± 0.0065 | 0.913 ± 0.011 | 0.705 ± 0.025 | 0.443 ± 0.089 |
| **M3 ATT+bal, 2 epochs** | 10 | 0.609 ± 0.044 | 0.789 ± 0.007 | 0.9707 ± 0.0021 | 0.906 ± 0.012 | 0.713 ± 0.013 | 0.476 ± 0.060 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| M1 Nebula (final) | 0.663 | 0.837 | 0.9705 | 0.913 | **0.756** | 0.552 |
| M3 ATT+bal, 3 epochs (final) | 0.597 | 0.800 | 0.9752 | 0.919 | **0.730** | 0.532 |
| **M3 ATT+bal, 2 epochs** | 0.632 | 0.801 | 0.9758 | 0.903 | **0.737** | 0.568 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| g3 − f3 | **pAUC@1e-2** | +0.80 | [+0.09, +1.54] | [-0.41, +2.36] | 7 up / 3 down | not resolved |
| g3 − f3 | TPR@1e-3 | +4.26 | [+0.49, +6.42] | [-1.93, +10.21] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| g3 − f3 | TPR@1e-2 | -0.13 | [-0.56, +0.25] | [-1.15, +0.76] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| g3 − f3 | AUC | +0.14 | [+0.10, +0.18] | [-0.17, +0.47] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| g3 − f1 | **pAUC@1e-2** | +2.64 | [+0.75, +4.56] | [-2.39, +6.87] | 7 up / 3 down | not resolved |
| g3 − f1 | TPR@1e-3 | +7.28 | [+0.72, +12.60] | [-3.41, +15.82] | 8 up / 2 down | cluster CI contains 0 (descriptive) |
| g3 − f1 | TPR@1e-2 | -0.24 | [-1.26, +0.78] | [-6.02, +4.60] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| g3 − f1 | AUC | +0.69 | [+0.58, +0.80] | [-0.21, +2.02] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | **pAUC@1e-2** | +1.84 | [-0.32, +4.25] | [-3.22, +6.39] | 7 up / 3 down | not resolved |
| f3 − f1 | TPR@1e-3 | +3.02 | [-3.92, +10.60] | [-8.19, +15.11] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | TPR@1e-2 | -0.11 | [-1.14, +0.95] | [-5.26, +4.62] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | AUC | +0.55 | [+0.42, +0.67] | [-0.37, +1.80] | 7 up / 3 down | cluster CI contains 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| g3 − f3 | +0.76 | [+0.09, +1.49] |
| g3 − f1 | -1.87 | [-3.88, +0.19] |
| f3 − f1 | -2.63 | [-4.74, -0.43] |


### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | M1 Nebula (final) | M3 ATT+bal, 3 epochs (final) | **M3 ATT+bal, 2 epochs** |
|---|---|---|---|---|
| backdoor | 1940 | 82.7 ± 1.6 | 81.0 ± 0.9 | 81.4 ± 1.7 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 80.2 ± 7.5 | 71.9 ± 6.7 | 70.7 ± 1.0 |
| dropper | 252 | 75.0 ± 4.6 | 83.5 ± 1.0 | 83.3 ± 0.9 |
| keylogger | 1041 | 86.3 ± 5.1 | 88.7 ± 2.0 | 87.2 ± 4.0 |
| ransomware | 2139 | 67.0 ± 5.2 | 72.2 ± 3.1 | 72.9 ± 2.9 |
| rat | 1258 | 88.2 ± 2.0 | 86.8 ± 0.9 | 87.1 ± 0.6 |
| trojan | 1085 | 78.6 ± 3.9 | 80.8 ± 1.3 | 80.6 ± 1.7 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.5 ± 0.8 | 0.2 ± 0.5 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens of the OLD tokenizer, the same set of reports for all models; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold (threshold on the April benign scores). Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| M1 Nebula (final) | 8/10 | +1.6 (IQR +0.6 to +2.9) | 80.2 ± 3.4 | 80.2 ± 7.5 |
| M3 ATT+bal, 3 epochs (final) | 1/10 | -3.9 (IQR -5.0 to -2.4) | 83.4 ± 2.4 | 71.9 ± 6.7 |
| **M3 ATT+bal, 2 epochs** | 0/10 | -4.6 (IQR -7.9 to -3.3) | 83.9 ± 1.1 | 70.7 ± 1.0 |

## Attack detection, compact (mean ± std over 10 seeds; white-box rows: share still flagged after 20 / 50 steps)

### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M1 Nebula | M3 ATT+bal, 3 epochs | M3 ATT+bal, 2 epochs |
|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.0 ± 1.9 | 78.9 ± 0.7 |
| random 20 prepend | 25.4 ± 7.8 | 76.2 ± 2.3 | 75.9 ± 1.2 |
| random 50 prepend | 7.4 ± 4.0 | 65.1 ± 5.8 | 64.2 ± 4.5 |
| random 100 prepend | 5.7 ± 5.1 | 6.5 ± 1.3 | 6.1 ± 2.1 |
| random 200 insert | 18.9 ± 5.9 | 44.3 ± 4.0 | 46.5 ± 4.8 |
| lgbm 50 prepend | 1.9 ± 2.6 | 35.1 ± 13.3 | 38.8 ± 13.4 |
| white-box 20 steps | 1.6 ± 1.6 | 48.7 ± 6.3 | 49.9 ± 5.0 |
| white-box 50 steps | 0.6 ± 1.2 | 2.5 ± 1.3 | 1.9 ± 1.4 |
| padded-benign FPR (%), random 50 prepend | 1.07 ± 1.96 | 0.84 ± 0.52 | 1.01 ± 0.84 |

## Detection after each edit with cluster 95% intervals (1% threshold, %)

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.0 [68.6, 86.3] | 78.9 [68.6, 86.3] |
| random 20 prepend | 25.4 [16.9, 35.2] | 76.2 [65.4, 84.1] | 75.9 [64.8, 84.0] |
| random 50 prepend | 7.4 [4.3, 11.6] | 65.1 [52.3, 74.9] | 64.2 [51.7, 74.2] |
| random 60 prepend | 5.8 [3.1, 9.5] | 51.9 [38.8, 63.2] | 51.7 [38.5, 62.7] |
| random 75 prepend | 5.4 [2.9, 9.0] | 21.5 [13.6, 29.6] | 21.9 [13.9, 30.2] |
| random 100 prepend | 5.7 [3.0, 9.3] | 6.5 [3.4, 11.2] | 6.1 [3.3, 10.4] |
| random 200 prepend | 5.7 [3.0, 9.2] | 6.4 [3.3, 11.0] | 6.1 [3.2, 10.4] |
| random 20 insert | 55.2 [43.1, 65.5] | 74.5 [63.4, 82.5] | 74.3 [62.7, 82.5] |
| random 50 insert | 42.1 [30.5, 53.0] | 68.5 [56.0, 78.2] | 68.4 [55.8, 78.1] |
| random 60 insert | 38.9 [27.3, 49.5] | 66.2 [53.0, 76.3] | 66.2 [53.1, 76.4] |
| random 75 insert | 35.4 [24.8, 46.0] | 61.9 [48.3, 72.8] | 62.3 [49.0, 73.3] |
| random 100 insert | 30.3 [20.0, 40.6] | 55.3 [40.9, 68.3] | 56.0 [41.5, 68.6] |
| random 200 insert | 18.9 [11.5, 28.0] | 44.3 [31.3, 56.1] | 46.5 [33.2, 58.1] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 35.1 [22.9, 48.2] | 38.8 [25.6, 52.4] |
| lgbm 50 insert | 25.4 [15.6, 35.9] | 54.7 [39.4, 67.3] | 55.9 [40.2, 68.8] |

## Padded-benign FPR after each edit with cluster 95% intervals (1% threshold, %)

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| unedited | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] | 1.00 [0.97, 0.99] |
| random 20 prepend | 1.29 [0.50, 2.15] | 1.12 [0.93, 1.42] | 1.15 [0.93, 1.42] |
| random 50 prepend | 1.07 [0.23, 2.18] | 0.84 [0.50, 1.39] | 1.01 [0.63, 1.47] |
| random 60 prepend | 1.16 [0.21, 2.41] | 0.59 [0.30, 1.09] | 0.76 [0.41, 1.20] |
| random 75 prepend | 1.61 [0.27, 3.25] | 0.40 [0.16, 0.74] | 0.61 [0.29, 0.99] |
| random 100 prepend | 1.39 [0.26, 2.78] | 0.30 [0.11, 0.62] | 0.54 [0.24, 0.85] |
| random 200 prepend | 1.43 [0.27, 2.86] | 0.29 [0.12, 0.58] | 0.53 [0.22, 0.87] |
| random 20 insert | 0.69 [0.30, 1.14] | 0.95 [0.71, 1.29] | 1.09 [0.83, 1.39] |
| random 50 insert | 0.55 [0.18, 1.05] | 0.68 [0.45, 0.99] | 0.81 [0.57, 1.12] |
| random 60 insert | 0.61 [0.20, 1.09] | 0.57 [0.40, 0.86] | 0.75 [0.54, 1.00] |
| random 75 insert | 0.69 [0.17, 1.26] | 0.46 [0.29, 0.67] | 0.63 [0.42, 0.86] |
| random 100 insert | 0.71 [0.17, 1.40] | 0.50 [0.31, 0.80] | 0.69 [0.44, 0.98] |
| random 200 insert | 0.84 [0.18, 1.65] | 0.44 [0.26, 0.73] | 0.63 [0.37, 0.93] |
| lgbm 50 prepend | 0.00 [0.00, 0.01] | 0.06 [0.02, 0.10] | 0.08 [0.04, 0.14] |
| lgbm 50 insert | 0.07 [0.03, 0.16] | 0.16 [0.09, 0.25] | 0.20 [0.12, 0.29] |

## White-box greedy attack (1% threshold)

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| white-box 0 steps: still flagged (1%) | 75.2 [62.6, 83.6] | 75.6 [63.0, 84.8] | 75.2 [63.1, 84.6] |
| white-box 5 steps: still flagged (1%) | 12.5 [7.8, 31.4] | 66.2 [52.3, 79.2] | 65.1 [50.7, 78.7] |
| white-box 10 steps: still flagged (1%) | 5.9 [3.4, 26.1] | 63.1 [49.0, 77.7] | 62.7 [48.6, 77.6] |
| white-box 20 steps: still flagged (1%) | 1.6 [0.7, 23.5] | 48.7 [34.8, 69.4] | 49.9 [34.8, 69.8] |
| white-box 50 steps: still flagged (1%) | 0.6 [0.2, 23.1] | 2.5 [1.2, 37.9] | 1.9 [1.0, 35.4] |
| white-box 5 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.52 [0.16, 0.96] | 0.60 [0.15, 1.04] |
| white-box 10 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.48 [0.12, 0.93] | 0.54 [0.12, 0.99] |
| white-box 20 steps: padded-benign FPR (1%) | 0.30 [0.10, 0.46] | 0.42 [0.12, 0.78] | 0.30 [0.04, 0.62] |
| white-box 50 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.28 [0.05, 0.60] | 0.24 [0.02, 0.51] |

## Differences under attack with cluster 95% intervals

### Differences under attack at the 1% threshold (points x100; difference of the 10-seed mean detection or padded-benign FPR; cluster 95% interval, 1,000 resamples; **bold** = the interval excludes 0)

**detection**

| difference | unedited | random_20_prepend | random_50_prepend | random_60_prepend | random_75_prepend | random_100_prepend | random_20_insert | random_50_insert | random_200_insert | lgbm_50_prepend | lgbm_50_insert |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M3-2ep - M3-3ep | -0.1 [-1.1, +0.8] | -0.3 [-1.4, +0.5] | -0.9 [-2.4, +0.8] | -0.2 [-2.7, +2.1] | +0.3 [-1.2, +1.9] | -0.3 [-1.1, +0.0] | -0.2 [-1.5, +0.9] | -0.1 [-1.4, +1.1] | **+2.2 [+0.1, +4.4]** | **+3.7 [+0.5, +6.9]** | +1.2 [-0.1, +2.4] |
| M3-2ep - M1 | -0.2 [-6.0, +4.6] | **+50.5 [+37.8, +60.9]** | **+56.7 [+43.5, +66.7]** | **+45.9 [+33.6, +56.6]** | **+16.4 [+9.2, +23.5]** | +0.4 [-1.4, +2.2] | **+19.1 [+11.1, +28.0]** | **+26.4 [+16.9, +35.2]** | **+27.6 [+16.4, +37.4]** | **+36.9 [+23.6, +50.4]** | **+30.5 [+17.0, +42.6]** |
| M3-3ep - M1 | -0.1 [-5.3, +4.6] | **+50.8 [+38.2, +61.3]** | **+57.6 [+44.2, +67.4]** | **+46.1 [+33.3, +56.9]** | **+16.1 [+9.0, +22.8]** | +0.7 [-1.3, +3.1] | **+19.3 [+11.3, +28.5]** | **+26.5 [+16.7, +35.5]** | **+25.4 [+14.5, +35.3]** | **+33.2 [+21.3, +46.5]** | **+29.4 [+16.0, +41.0]** |

**padded-benign FPR**

| difference | unedited | random_20_prepend | random_50_prepend | random_60_prepend | random_75_prepend | random_100_prepend | random_20_insert | random_50_insert | random_200_insert | lgbm_50_prepend | lgbm_50_insert |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M3-2ep - M3-3ep | +0.0 [-0.0, +0.0] | +0.0 [-0.1, +0.1] | +0.2 [-0.1, +0.3] | +0.2 [-0.0, +0.3] | **+0.2 [+0.1, +0.3]** | **+0.2 [+0.1, +0.3]** | **+0.1 [+0.0, +0.2]** | **+0.1 [+0.0, +0.2]** | **+0.2 [+0.1, +0.3]** | **+0.0 [+0.0, +0.1]** | +0.0 [+0.0, +0.1] |
| M3-2ep - M1 | +0.0 [-0.0, +0.0] | -0.1 [-0.9, +0.6] | -0.1 [-0.9, +0.6] | -0.4 [-1.4, +0.4] | -1.0 [-2.4, +0.2] | -0.9 [-2.1, +0.2] | **+0.4 [+0.1, +0.7]** | +0.3 [-0.1, +0.5] | -0.2 [-0.9, +0.4] | **+0.1 [+0.0, +0.1]** | **+0.1 [+0.0, +0.2]** |
| M3-3ep - M1 | +0.0 [-0.0, +0.0] | -0.2 [-0.9, +0.6] | -0.2 [-1.0, +0.5] | -0.6 [-1.5, +0.3] | **-1.2 [-2.6, -0.0]** | **-1.1 [-2.3, -0.0]** | +0.3 [-0.0, +0.6] | +0.1 [-0.3, +0.4] | -0.4 [-1.1, +0.2] | **+0.1 [+0.0, +0.1]** | **+0.1 [+0.0, +0.1]** |

Full tables: `attack/tables.md` (all 15 edit sets, both thresholds, per family), `attack/m3e2_cluster_ci.md`, `seen_unseen/seen_unseen.md`, `clean_tables.md`.
