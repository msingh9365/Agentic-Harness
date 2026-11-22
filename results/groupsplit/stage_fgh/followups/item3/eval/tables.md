### Clean April test, 10 seeds each, one evaluation per cell (NOTES 26 item 3, matched budget: 1 epoch(s)): per-seed mean ± std

| cell | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| M1 Nebula, Stage I (reference: lr 2e-3, 1 epoch) | 10 | 0.536 ± 0.060 | 0.791 ± 0.020 | 0.9639 ± 0.0111 | 0.891 ± 0.027 | 0.686 ± 0.026 | 0.398 ± 0.095 |
| M3 ATT+bal, Stage I (reference: lr 1e-3, 3 epochs) | 10 | 0.567 ± 0.047 | 0.790 ± 0.019 | 0.9693 ± 0.0065 | 0.913 ± 0.011 | 0.705 ± 0.025 | 0.443 ± 0.089 |
| **flatten head, no padding** | 10 | 0.509 ± 0.035 | 0.796 ± 0.030 | 0.9684 ± 0.0068 | 0.913 ± 0.008 | 0.674 ± 0.035 | 0.394 ± 0.049 |
| **attention head, no padding** | 10 | 0.495 ± 0.077 | 0.749 ± 0.096 | 0.9673 ± 0.0063 | 0.897 ± 0.030 | 0.642 ± 0.078 | 0.340 ± 0.084 |
| **flatten head, balanced padding** | 10 | 0.570 ± 0.069 | 0.775 ± 0.021 | 0.9608 ± 0.0112 | 0.897 ± 0.020 | 0.695 ± 0.023 | 0.480 ± 0.067 |
| **attention head, balanced padding** | 10 | 0.574 ± 0.072 | 0.781 ± 0.010 | 0.9726 ± 0.0039 | 0.913 ± 0.015 | 0.703 ± 0.018 | 0.457 ± 0.071 |


10-seed ensembles (mean logit):

| cell | TPR@1e-3 | TPR@1e-2 | AUC | F1 (threshold 0.5) | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| M1 Nebula, Stage I (reference: lr 2e-3, 1 epoch) | 0.663 | 0.837 | 0.9705 | 0.913 | **0.756** | 0.552 |
| M3 ATT+bal, Stage I (reference: lr 1e-3, 3 epochs) | 0.597 | 0.800 | 0.9752 | 0.919 | **0.730** | 0.532 |
| **flatten head, no padding** | 0.596 | 0.847 | 0.9765 | 0.920 | **0.738** | 0.485 |
| **attention head, no padding** | 0.539 | 0.789 | 0.9741 | 0.915 | **0.685** | 0.392 |
| **flatten head, balanced padding** | 0.675 | 0.789 | 0.9657 | 0.899 | **0.733** | 0.571 |
| **attention head, balanced padding** | 0.638 | 0.792 | 0.9783 | 0.925 | **0.727** | 0.535 |


(TPR@1e-2 and TPR@1e-3 use thresholds set on the April benign scores; the F1 column is the F1 at the fixed threshold 0.5, NOTES 26 item 0.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** Seeds are paired by index only.

| comparison | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| head effect, no padding (attention - flatten) | **pAUC@1e-2** | -3.21 | [-5.76, -0.65] | [-9.57, +2.92] | 3 up / 7 down | not resolved |
| head effect, no padding (attention - flatten) | TPR@1e-3 | -1.38 | [-9.76, +5.49] | [-19.25, +13.65] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| head effect, no padding (attention - flatten) | TPR@1e-2 | -4.71 | [-6.20, -3.49] | [-8.26, -1.12] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| head effect, no padding (attention - flatten) | AUC | -0.11 | [-0.24, +0.03] | [-1.35, +1.17] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| head effect, balanced padding (attention - flatten) | **pAUC@1e-2** | +0.80 | [-0.84, +2.28] | [-1.66, +3.57] | 7 up / 3 down | not resolved |
| head effect, balanced padding (attention - flatten) | TPR@1e-3 | +0.41 | [-5.28, +5.60] | [-7.90, +9.09] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| head effect, balanced padding (attention - flatten) | TPR@1e-2 | +0.62 | [-0.12, +1.13] | [-1.38, +2.40] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| head effect, balanced padding (attention - flatten) | AUC | +1.19 | [+1.07, +1.31] | [+0.39, +2.47] | 9 up / 1 down | cluster CI excludes 0 (descriptive) |
| padding effect, flatten head (balanced - none) | **pAUC@1e-2** | +2.10 | [+0.24, +3.94] | [-2.76, +8.05] | 8 up / 2 down | not resolved |
| padding effect, flatten head (balanced - none) | TPR@1e-3 | +6.12 | [+1.94, +9.25] | [-3.84, +18.13] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| padding effect, flatten head (balanced - none) | TPR@1e-2 | -2.17 | [-3.23, -1.00] | [-5.81, +1.54] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| padding effect, flatten head (balanced - none) | AUC | -0.76 | [-0.91, -0.63] | [-1.75, +0.04] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| padding effect, attention head (balanced - none) | **pAUC@1e-2** | +6.10 | [+3.91, +8.37] | [+0.59, +12.05] | 9 up / 1 down | **RESOLVED higher** |
| padding effect, attention head (balanced - none) | TPR@1e-3 | +7.91 | [+0.19, +16.41] | [-7.04, +24.58] | 8 up / 2 down | cluster CI contains 0 (descriptive) |
| padding effect, attention head (balanced - none) | TPR@1e-2 | +3.17 | [+2.02, +4.64] | [-0.90, +7.16] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| padding effect, attention head (balanced - none) | AUC | +0.53 | [+0.44, +0.63] | [-0.25, +1.69] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| descriptive: flatten/none at the matched budget - M1 (Stage I) | **pAUC@1e-2** | -1.26 | [-2.48, +0.09] | [-6.04, +2.63] | 4 up / 6 down | not resolved |
| descriptive: flatten/none at the matched budget - M1 (Stage I) | TPR@1e-3 | -2.72 | [-7.15, +2.53] | [-12.82, +6.87] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| descriptive: flatten/none at the matched budget - M1 (Stage I) | TPR@1e-2 | +0.51 | [-0.23, +1.45] | [-2.07, +3.35] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| descriptive: flatten/none at the matched budget - M1 (Stage I) | AUC | +0.45 | [+0.37, +0.54] | [-0.34, +1.43] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| descriptive: attention/balanced at the matched budget - M3 (Stage I) | **pAUC@1e-2** | -0.21 | [-1.80, +1.50] | [-2.84, +2.46] | 5 up / 5 down | not resolved |
| descriptive: attention/balanced at the matched budget - M3 (Stage I) | TPR@1e-3 | +0.79 | [-5.91, +6.58] | [-10.65, +12.35] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| descriptive: attention/balanced at the matched budget - M3 (Stage I) | TPR@1e-2 | -0.93 | [-1.58, -0.23] | [-2.13, +0.41] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| descriptive: attention/balanced at the matched budget - M3 (Stage I) | AUC | +0.33 | [+0.25, +0.41] | [-0.06, +0.88] | 6 up / 4 down | cluster CI contains 0 (descriptive) |


**Interaction of head and padding on pAUC@1e-2**, (attention - flatten with padding) - (attention - flatten without padding) = (ab - an) - (fb - fn): +4.00 points, cluster 95% interval [-1.89, +10.26] (contains 0).

### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | M1 Nebula, Stage I (reference: lr 2e-3, 1 epoch) | M3 ATT+bal, Stage I (reference: lr 1e-3, 3 epochs) | **flatten head, no padding** | **attention head, no padding** | **flatten head, balanced padding** | **attention head, balanced padding** |
|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 82.7 ± 1.6 | 81.0 ± 0.9 | 85.2 ± 1.8 | 79.0 ± 5.5 | 81.0 ± 2.2 | 81.1 ± 0.7 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 80.2 ± 7.5 | 71.9 ± 6.7 | 76.5 ± 9.2 | 70.1 ± 10.8 | 71.8 ± 6.7 | 69.0 ± 1.0 |
| dropper | 252 | 75.0 ± 4.6 | 83.5 ± 1.0 | 71.3 ± 8.0 | 75.3 ± 6.2 | 79.7 ± 2.5 | 82.1 ± 0.7 |
| keylogger | 1041 | 86.3 ± 5.1 | 88.7 ± 2.0 | 84.9 ± 5.1 | 76.6 ± 21.6 | 84.8 ± 6.0 | 86.6 ± 3.1 |
| ransomware | 2139 | 67.0 ± 5.2 | 72.2 ± 3.1 | 70.0 ± 4.8 | 69.0 ± 7.2 | 69.5 ± 3.7 | 71.8 ± 3.2 |
| rat | 1258 | 88.2 ± 2.0 | 86.8 ± 0.9 | 89.7 ± 2.2 | 81.4 ± 17.4 | 85.8 ± 1.4 | 86.1 ± 1.2 |
| trojan | 1085 | 78.6 ± 3.9 | 80.8 ± 1.3 | 78.6 ± 3.3 | 77.7 ± 4.8 | 78.4 ± 1.8 | 80.9 ± 1.3 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.5 ± 0.8 | 0.3 ± 0.7 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |

