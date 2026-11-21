### Clean April test, 10 seeds each, one evaluation per model: per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| **v2-PE, new split, Stage C epoch (1)** | 10 | 0.479 ± 0.036 | 0.732 ± 0.027 | 0.9599 ± 0.0122 | 0.880 ± 0.018 | 0.634 ± 0.024 | 0.366 ± 0.066 |
| **v2-PE, new split, early-stopped per seed (validation pAUC)** | 10 | 0.431 ± 0.034 | 0.726 ± 0.040 | 0.9520 ± 0.0164 | 0.865 ± 0.026 | 0.620 ± 0.026 | 0.316 ± 0.041 |
| **v2-PE, new split, 2 epochs (old epoch count)** | 10 | 0.480 ± 0.070 | 0.737 ± 0.027 | 0.9515 ± 0.0127 | 0.859 ± 0.025 | 0.634 ± 0.040 | 0.356 ± 0.067 |
| v2-PE, old validation slice (2 epochs) | 10 | 0.543 ± 0.063 | 0.811 ± 0.023 | 0.9644 ± 0.0093 | 0.915 ± 0.012 | 0.705 ± 0.031 | 0.444 ± 0.076 |
| **ATT+bal, new split, Stage C epoch (3)** | 10 | 0.503 ± 0.048 | 0.665 ± 0.064 | 0.9386 ± 0.0127 | 0.860 ± 0.033 | 0.590 ± 0.052 | 0.379 ± 0.063 |
| **ATT+bal, new split, early-stopped per seed (validation pAUC)** | 10 | 0.530 ± 0.053 | 0.701 ± 0.051 | 0.9432 ± 0.0132 | 0.878 ± 0.022 | 0.620 ± 0.047 | 0.390 ± 0.046 |
| **ATT+bal, new split, 2 epochs (old epoch count)** | 10 | 0.525 ± 0.041 | 0.727 ± 0.021 | 0.9494 ± 0.0107 | 0.874 ± 0.023 | 0.642 ± 0.013 | 0.408 ± 0.054 |
| ATT+bal, old validation slice (2 epochs) | 10 | 0.572 ± 0.061 | 0.795 ± 0.020 | 0.9713 ± 0.0066 | 0.913 ± 0.017 | 0.707 ± 0.017 | 0.457 ± 0.041 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| **v2-PE, new split, Stage C epoch (1)** | 0.603 | 0.756 | 0.9668 | 0.899 | **0.689** | 0.529 |
| **v2-PE, new split, early-stopped per seed (validation pAUC)** | 0.563 | 0.782 | 0.9573 | 0.894 | **0.695** | 0.492 |
| **v2-PE, new split, 2 epochs (old epoch count)** | 0.546 | 0.770 | 0.9600 | 0.888 | **0.696** | 0.479 |
| v2-PE, old validation slice (2 epochs) | 0.606 | 0.851 | 0.9705 | 0.927 | **0.768** | 0.546 |
| **ATT+bal, new split, Stage C epoch (3)** | 0.537 | 0.711 | 0.9470 | 0.857 | **0.647** | 0.442 |
| **ATT+bal, new split, early-stopped per seed (validation pAUC)** | 0.538 | 0.733 | 0.9500 | 0.892 | **0.663** | 0.477 |
| **ATT+bal, new split, 2 epochs (old epoch count)** | 0.582 | 0.745 | 0.9560 | 0.878 | **0.667** | 0.493 |
| ATT+bal, old validation slice (2 epochs) | 0.583 | 0.814 | 0.9780 | 0.926 | **0.734** | 0.503 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores, see Step 4.)

### Early-stopping epochs (chosen on validation logits only): v2-PE [1, 1, 3, 1, 4, 1, 3, 4, 2, 3]; ATT+bal [5, 2, 2, 3, 4, 5, 1, 2, 1, 3].
Reproduction of Stage C by the Stage D runs at the Stage C epoch (April logits): v2-PE 10/10 seeds identical (largest logit difference 0.00e+00); ATT+bal 10/10 (largest 0.00e+00).

### Gate for Step 3 (cluster CI of early-stopped minus old-split pAUC@1e-2 excludes 0 and is negative)

- v2-PE: difference -8.52 points, cluster CI [-15.88, -3.14] -> Step 3 RUN
- ATT+bal: difference -8.71 points, cluster CI [-16.55, -1.94] -> Step 3 RUN

### Differences (points ×100; mean of the 10 per-seed differences; stratified bootstrap CI, cluster bootstrap CI over 2,509 April groups; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs (new vs old, model vs model) the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| es_v2pe − gs_v2pe | **pAUC@1e-2** | -1.43 | [-2.47, -0.55] | [-3.47, +0.44] | 1 up / 5 down | not resolved |
| es_v2pe − gs_v2pe | TPR@1e-3 | -4.81 | [-7.20, -1.35] | [-9.77, +0.01] | 0 up / 6 down | cluster CI contains 0 (descriptive) |
| es_v2pe − gs_v2pe | TPR@1e-2 | -0.61 | [-1.37, +0.19] | [-2.19, +1.05] | 3 up / 3 down | cluster CI contains 0 (descriptive) |
| es_v2pe − gs_v2pe | AUC | -0.78 | [-0.86, -0.70] | [-1.66, -0.16] | 2 up / 4 down | cluster CI excludes 0 (descriptive) |
| es_v2pe − old_v2pe | **pAUC@1e-2** | -8.52 | [-9.61, -7.36] | [-15.88, -3.14] | 0 up / 10 down | **RESOLVED worse** |
| es_v2pe − old_v2pe | TPR@1e-3 | -11.21 | [-14.73, -7.39] | [-19.20, -4.49] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| es_v2pe − old_v2pe | TPR@1e-2 | -8.50 | [-9.51, -7.52] | [-15.10, -2.62] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| es_v2pe − old_v2pe | AUC | -1.24 | [-1.38, -1.11] | [-2.82, -0.02] | 3 up / 7 down | cluster CI excludes 0 (descriptive) |
| gs_v2pe − old_v2pe | **pAUC@1e-2** | -7.09 | [-8.33, -5.78] | [-14.90, -1.45] | 0 up / 10 down | **RESOLVED worse** |
| gs_v2pe − old_v2pe | TPR@1e-3 | -6.40 | [-9.96, -3.40] | [-15.12, -0.17] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| gs_v2pe − old_v2pe | TPR@1e-2 | -7.89 | [-9.02, -6.88] | [-15.32, -1.96] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| gs_v2pe − old_v2pe | AUC | -0.45 | [-0.59, -0.32] | [-1.76, +0.84] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| e2_v2pe − gs_v2pe | **pAUC@1e-2** | +0.04 | [-1.06, +1.01] | [-1.62, +1.76] | 4 up / 6 down | not resolved |
| e2_v2pe − gs_v2pe | TPR@1e-3 | +0.16 | [-4.52, +3.03] | [-4.92, +3.90] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| e2_v2pe − gs_v2pe | TPR@1e-2 | +0.47 | [-0.38, +1.19] | [-1.35, +2.19] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| e2_v2pe − gs_v2pe | AUC | -0.84 | [-0.92, -0.75] | [-1.82, -0.14] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| e2_v2pe − old_v2pe | **pAUC@1e-2** | -7.06 | [-8.12, -5.98] | [-14.78, -1.48] | 1 up / 9 down | **RESOLVED worse** |
| e2_v2pe − old_v2pe | TPR@1e-3 | -6.24 | [-10.05, -4.12] | [-15.26, -0.52] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| e2_v2pe − old_v2pe | TPR@1e-2 | -7.42 | [-8.43, -6.63] | [-14.62, -1.75] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| e2_v2pe − old_v2pe | AUC | -1.29 | [-1.43, -1.16] | [-2.92, -0.04] | 3 up / 7 down | cluster CI excludes 0 (descriptive) |
| e2_v2pe − es_v2pe | **pAUC@1e-2** | +1.46 | [+0.71, +2.26] | [-0.26, +3.46] | 5 up / 4 down | not resolved |
| e2_v2pe − es_v2pe | TPR@1e-3 | +4.97 | [+0.12, +7.59] | [-1.07, +9.70] | 7 up / 2 down | cluster CI contains 0 (descriptive) |
| e2_v2pe − es_v2pe | TPR@1e-2 | +1.08 | [+0.33, +1.53] | [-0.89, +2.83] | 5 up / 4 down | cluster CI contains 0 (descriptive) |
| e2_v2pe − es_v2pe | AUC | -0.05 | [-0.10, -0.01] | [-0.32, +0.17] | 3 up / 6 down | cluster CI contains 0 (descriptive) |
| es_attbal − gs_attbal | **pAUC@1e-2** | +2.97 | [+2.23, +3.65] | [+1.27, +4.71] | 5 up / 3 down | **RESOLVED better** |
| es_attbal − gs_attbal | TPR@1e-3 | +2.72 | [+0.29, +5.82] | [-0.80, +7.05] | 5 up / 3 down | cluster CI contains 0 (descriptive) |
| es_attbal − gs_attbal | TPR@1e-2 | +3.59 | [+2.59, +4.43] | [+1.23, +5.55] | 5 up / 3 down | cluster CI excludes 0 (descriptive) |
| es_attbal − gs_attbal | AUC | +0.47 | [+0.41, +0.52] | [-0.10, +1.40] | 6 up / 2 down | cluster CI contains 0 (descriptive) |
| es_attbal − old_attbal | **pAUC@1e-2** | -8.71 | [-10.45, -6.70] | [-16.55, -1.94] | 0 up / 10 down | **RESOLVED worse** |
| es_attbal − old_attbal | TPR@1e-3 | -4.18 | [-10.07, +0.45] | [-15.02, +4.74] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| es_attbal − old_attbal | TPR@1e-2 | -9.34 | [-10.14, -8.28] | [-16.75, -3.08] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| es_attbal − old_attbal | AUC | -2.80 | [-3.01, -2.60] | [-5.51, -0.89] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − old_attbal | **pAUC@1e-2** | -11.68 | [-13.56, -9.59] | [-19.68, -4.61] | 0 up / 10 down | **RESOLVED worse** |
| gs_attbal − old_attbal | TPR@1e-3 | -6.90 | [-13.53, -2.01] | [-17.82, +1.92] | 2 up / 8 down | cluster CI contains 0 (descriptive) |
| gs_attbal − old_attbal | TPR@1e-2 | -12.93 | [-14.17, -11.21] | [-20.10, -5.61] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − old_attbal | AUC | -3.27 | [-3.48, -3.04] | [-6.41, -0.96] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| e2_attbal − gs_attbal | **pAUC@1e-2** | +5.13 | [+4.04, +6.11] | [+2.28, +8.02] | 8 up / 2 down | **RESOLVED better** |
| e2_attbal − gs_attbal | TPR@1e-3 | +2.20 | [-1.22, +6.89] | [-2.29, +7.97] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| e2_attbal − gs_attbal | TPR@1e-2 | +6.19 | [+4.59, +7.17] | [+2.42, +8.82] | 10 up / 0 down | cluster CI excludes 0 (descriptive) |
| e2_attbal − gs_attbal | AUC | +1.08 | [+1.00, +1.16] | [+0.26, +2.33] | 8 up / 2 down | cluster CI excludes 0 (descriptive) |
| e2_attbal − old_attbal | **pAUC@1e-2** | -6.55 | [-8.37, -4.68] | [-14.68, -0.17] | 0 up / 10 down | **RESOLVED worse** |
| e2_attbal − old_attbal | TPR@1e-3 | -4.69 | [-11.15, +0.28] | [-14.93, +4.79] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| e2_attbal − old_attbal | TPR@1e-2 | -6.73 | [-7.72, -6.00] | [-13.93, -1.19] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| e2_attbal − old_attbal | AUC | -2.19 | [-2.37, -2.00] | [-4.59, -0.59] | 1 up / 9 down | cluster CI excludes 0 (descriptive) |
| e2_attbal − es_attbal | **pAUC@1e-2** | +2.16 | [+1.52, +2.78] | [+0.72, +3.78] | 5 up / 2 down | **RESOLVED better** |
| e2_attbal − es_attbal | TPR@1e-3 | -0.51 | [-2.72, +2.27] | [-3.55, +2.93] | 3 up / 4 down | cluster CI contains 0 (descriptive) |
| e2_attbal − es_attbal | TPR@1e-2 | +2.60 | [+1.72, +3.00] | [+0.99, +3.92] | 7 up / 0 down | cluster CI excludes 0 (descriptive) |
| e2_attbal − es_attbal | AUC | +0.61 | [+0.57, +0.66] | [+0.22, +1.08] | 4 up / 3 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − gs_v2pe | **pAUC@1e-2** | -4.36 | [-6.46, -2.15] | [-9.40, +0.81] | 3 up / 7 down | not resolved |
| gs_attbal − gs_v2pe | TPR@1e-3 | +2.42 | [-6.01, +8.09] | [-8.98, +10.96] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| gs_attbal − gs_v2pe | TPR@1e-2 | -6.68 | [-8.29, -4.77] | [-12.05, -1.35] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − gs_v2pe | AUC | -2.13 | [-2.32, -1.95] | [-4.31, -0.41] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| es_attbal − es_v2pe | **pAUC@1e-2** | +0.04 | [-1.83, +2.07] | [-4.34, +4.50] | 7 up / 3 down | not resolved |
| es_attbal − es_v2pe | TPR@1e-3 | +9.94 | [+2.82, +14.96] | [-0.38, +18.93] | 10 up / 0 down | cluster CI contains 0 (descriptive) |
| es_attbal − es_v2pe | TPR@1e-2 | -2.48 | [-3.68, -1.41] | [-6.65, +1.05] | 2 up / 8 down | cluster CI contains 0 (descriptive) |
| es_attbal − es_v2pe | AUC | -0.88 | [-1.01, -0.76] | [-2.11, +0.08] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| e2_attbal − e2_v2pe | **pAUC@1e-2** | +0.73 | [-1.18, +2.67] | [-4.32, +5.10] | 5 up / 5 down | not resolved |
| e2_attbal − e2_v2pe | TPR@1e-3 | +4.46 | [-0.91, +9.73] | [-3.97, +12.74] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| e2_attbal − e2_v2pe | TPR@1e-2 | -0.96 | [-2.19, -0.04] | [-6.41, +2.85] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| e2_attbal − e2_v2pe | AUC | -0.21 | [-0.33, -0.10] | [-1.18, +0.72] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| old_attbal − old_v2pe | **pAUC@1e-2** | +0.23 | [-1.70, +2.09] | [-5.31, +4.53] | 4 up / 6 down | not resolved |
| old_attbal − old_v2pe | TPR@1e-3 | +2.91 | [-2.20, +7.16] | [-6.03, +9.91] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| old_attbal − old_v2pe | TPR@1e-2 | -1.65 | [-2.95, -0.67] | [-7.30, +3.05] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| old_attbal − old_v2pe | AUC | +0.68 | [+0.57, +0.79] | [-0.17, +2.05] | 7 up / 3 down | cluster CI contains 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| es_v2pe − gs_v2pe | +0.65 | [-0.74, +1.92] |
| es_v2pe − old_v2pe | -7.30 | [-8.51, -6.10] |
| gs_v2pe − old_v2pe | -7.95 | [-9.25, -6.42] |
| e2_v2pe − gs_v2pe | +0.69 | [-0.44, +1.83] |
| e2_v2pe − old_v2pe | -7.26 | [-8.31, -6.05] |
| e2_v2pe − es_v2pe | +0.04 | [-0.85, +0.96] |
| es_attbal − gs_attbal | +1.58 | [+0.76, +2.34] |
| es_attbal − old_attbal | -7.10 | [-8.69, -5.22] |
| gs_attbal − old_attbal | -8.68 | [-10.58, -6.59] |
| e2_attbal − gs_attbal | +1.98 | [+0.99, +3.17] |
| e2_attbal − old_attbal | -6.70 | [-8.26, -4.85] |
| e2_attbal − es_attbal | +0.39 | [-0.20, +1.19] |
| gs_attbal − gs_v2pe | -4.16 | [-6.28, -2.11] |
| es_attbal − es_v2pe | -3.22 | [-5.20, -1.26] |
| e2_attbal − e2_v2pe | -2.86 | [-4.82, -0.86] |
| old_attbal − old_v2pe | -3.42 | [-5.37, -1.55] |


### Detection rate per family, thresholds set on the APRIL benign scores of each model and seed (%; the clean and windows_syswow64 rows are false-positive rates and equal the target BY CONSTRUCTION)

| family | n | **v2-PE, new split, Stage C epoch (1)** | **v2-PE, new split, early-stopped per seed (validation pAUC)** | **v2-PE, new split, 2 epochs (old epoch count)** | v2-PE, old validation slice (2 epochs) | **ATT+bal, new split, Stage C epoch (3)** | **ATT+bal, new split, early-stopped per seed (validation pAUC)** | **ATT+bal, new split, 2 epochs (old epoch count)** | ATT+bal, old validation slice (2 epochs) |
|---|---|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 81.5 ± 2.3 | 82.1 ± 4.0 | 81.8 ± 1.8 | 83.7 ± 2.4 | 76.3 ± 7.7 | 79.8 ± 4.1 | 81.3 ± 1.9 | 82.1 ± 1.9 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 76.7 ± 7.6 | 74.3 ± 9.7 | 79.8 ± 7.3 | 81.7 ± 6.8 | 61.7 ± 6.8 | 65.6 ± 7.5 | 67.3 ± 5.7 | 72.8 ± 6.1 |
| dropper | 252 | 73.7 ± 5.4 | 74.4 ± 5.7 | 76.7 ± 7.7 | 80.1 ± 2.4 | 78.7 ± 6.3 | 81.3 ± 4.5 | 82.5 ± 2.1 | 81.9 ± 5.7 |
| keylogger | 1041 | 70.3 ± 3.0 | 68.8 ± 4.9 | 70.8 ± 5.3 | 87.1 ± 6.1 | 63.4 ± 6.6 | 65.6 ± 5.1 | 69.2 ± 4.8 | 87.0 ± 2.5 |
| ransomware | 2139 | 68.2 ± 6.8 | 67.3 ± 4.7 | 65.3 ± 6.7 | 70.8 ± 4.9 | 61.7 ± 6.8 | 67.0 ± 6.5 | 69.5 ± 3.2 | 72.9 ± 2.2 |
| rat | 1258 | 76.5 ± 1.3 | 75.7 ± 8.3 | 77.9 ± 1.8 | 89.2 ± 2.0 | 69.8 ± 11.2 | 73.0 ± 8.1 | 76.5 ± 0.9 | 87.8 ± 2.8 |
| trojan | 1085 | 61.7 ± 5.6 | 63.2 ± 6.5 | 63.3 ± 7.2 | 80.9 ± 1.2 | 62.4 ± 5.9 | 64.3 ± 6.4 | 68.7 ± 8.3 | 80.4 ± 2.5 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.3 ± 0.7 | 0.2 ± 0.5 | 0.2 ± 0.5 | 0.0 ± 0.0 |


### Step 4: where the 1e-2 threshold is set. Threshold from the VALIDATION slice (benign validation logit at rank floor(0.01 x n_benign), same model and seed) applied unchanged to April, against the April-benign threshold of the other tables

| model | April FPR, validation threshold (mean ± std, range) % | April TPR, validation threshold % | April FPR, April threshold % | April TPR, April threshold % | seeds with April FPR > 1% |
|---|---|---|---|---|---|
| **v2-PE, new split, Stage C epoch (1)** | 0.74 ± 0.21 (0.44 to 0.95) | 70.4 ± 2.6 | 1.00 (by construction) | 73.2 ± 2.7 | 0/10 |
| **v2-PE, new split, early-stopped per seed (validation pAUC)** | 1.80 ± 3.62 (0.11 to 12.08) | 68.3 ± 9.0 | 1.00 (by construction) | 72.6 ± 4.0 | 1/10 |
| **v2-PE, new split, 2 epochs (old epoch count)** | 0.50 ± 0.33 (0.04 to 0.94) | 62.1 ± 14.7 | 1.00 (by construction) | 73.7 ± 2.7 | 0/10 |
| v2-PE, old validation slice (2 epochs) | 1.34 ± 0.30 (0.82 to 1.74) | 83.1 ± 2.0 | 1.00 (by construction) | 81.1 ± 2.3 | 9/10 |
| **ATT+bal, new split, Stage C epoch (3)** | 0.86 ± 0.47 (0.26 to 1.46) | 64.9 ± 4.5 | 1.00 (by construction) | 66.5 ± 6.4 | 4/10 |
| **ATT+bal, new split, early-stopped per seed (validation pAUC)** | 0.62 ± 0.44 (0.30 to 1.55) | 66.1 ± 2.9 | 1.00 (by construction) | 70.1 ± 5.1 | 2/10 |
| **ATT+bal, new split, 2 epochs (old epoch count)** | 0.45 ± 0.15 (0.26 to 0.75) | 66.3 ± 1.5 | 1.00 (by construction) | 72.7 ± 2.1 | 0/10 |
| ATT+bal, old validation slice (2 epochs) | n/a (no validation logits were kept) |  |  |  |  |


Per-family rates with the validation thresholds (mean over seeds, %; clean and windows_syswow64 = false-positive rate):

| family | n | **v2-PE, new split, Stage C epoch (1)** | **v2-PE, new split, early-stopped per seed (validation pAUC)** | **v2-PE, new split, 2 epochs (old epoch count)** | v2-PE, old validation slice (2 epochs) | **ATT+bal, new split, Stage C epoch (3)** | **ATT+bal, new split, early-stopped per seed (validation pAUC)** | **ATT+bal, new split, 2 epochs (old epoch count)** | ATT+bal, old validation slice (2 epochs) |
|---|---|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 79.8 | 78.6 | 73.9 | 84.5 | 76.3 | 78.9 | 78.3 | n/a |
| clean | 7944 | 0.7 | 1.8 | 0.5 | 1.3 | 0.9 | 0.6 | 0.5 | n/a |
| coinminer | 1684 | 74.2 | 69.6 | 64.9 | 85.7 | 59.7 | 59.9 | 59.7 | n/a |
| dropper | 252 | 69.6 | 69.2 | 65.0 | 82.3 | 76.9 | 77.0 | 76.9 | n/a |
| keylogger | 1041 | 66.5 | 64.8 | 56.1 | 89.5 | 61.3 | 60.5 | 59.7 | n/a |
| ransomware | 2139 | 64.2 | 62.7 | 54.8 | 72.9 | 59.6 | 61.6 | 61.4 | n/a |
| rat | 1258 | 75.2 | 69.1 | 63.8 | 90.2 | 67.5 | 70.5 | 73.4 | n/a |
| trojan | 1085 | 58.0 | 60.8 | 54.3 | 82.0 | 60.4 | 59.6 | 60.3 | n/a |
| windows_syswow64 | 59 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | n/a |

