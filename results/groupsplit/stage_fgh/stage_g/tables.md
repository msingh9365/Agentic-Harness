### Clean April test, 10 seeds each, one evaluation per model (Stage G, final models M1 to M4): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| v2-PE, old split (reference) | 10 | 0.543 ± 0.063 | 0.811 ± 0.023 | 0.9644 ± 0.0093 | 0.915 ± 0.012 | 0.705 ± 0.031 | 0.444 ± 0.076 |
| ATT+bal, old split (reference) | 10 | 0.572 ± 0.061 | 0.795 ± 0.020 | 0.9713 ± 0.0066 | 0.913 ± 0.017 | 0.707 ± 0.017 | 0.457 ± 0.041 |
| **M1 v2-PE (all January)** | 10 | 0.541 ± 0.095 | 0.780 ± 0.038 | 0.9667 ± 0.0071 | 0.899 ± 0.021 | 0.674 ± 0.053 | 0.426 ± 0.086 |
| **M2 two-level, no padding (all January)** | 10 | 0.344 ± 0.189 | 0.751 ± 0.068 | 0.9670 ± 0.0105 | 0.888 ± 0.038 | 0.562 ± 0.146 | 0.202 ± 0.116 |
| **M3 ATT+bal (all January)** | 10 | 0.590 ± 0.029 | 0.790 ± 0.008 | 0.9694 ± 0.0044 | 0.908 ± 0.011 | 0.710 ± 0.015 | 0.477 ± 0.051 |
| **M4 ATT+bal-2L (all January)** | 10 | 0.461 ± 0.174 | 0.778 ± 0.021 | 0.9679 ± 0.0075 | 0.910 ± 0.010 | 0.663 ± 0.036 | 0.273 ± 0.124 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| v2-PE, old split (reference) | 0.606 | 0.851 | 0.9705 | 0.927 | **0.768** | 0.546 |
| ATT+bal, old split (reference) | 0.583 | 0.814 | 0.9780 | 0.926 | **0.734** | 0.503 |
| **M1 v2-PE (all January)** | 0.622 | 0.843 | 0.9738 | 0.921 | **0.739** | 0.548 |
| **M2 two-level, no padding (all January)** | 0.532 | 0.802 | 0.9749 | 0.914 | **0.675** | 0.317 |
| **M3 ATT+bal (all January)** | 0.603 | 0.801 | 0.9748 | 0.921 | **0.731** | 0.536 |
| **M4 ATT+bal-2L (all January)** | 0.628 | 0.812 | 0.9767 | 0.917 | **0.725** | 0.451 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| m2 − m1 | **pAUC@1e-2** | -11.16 | [-14.19, -8.40] | [-15.79, -6.10] | 3 up / 7 down | **RESOLVED worse** |
| m2 − m1 | TPR@1e-3 | -19.63 | [-26.53, -12.92] | [-28.01, -10.89] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| m2 − m1 | TPR@1e-2 | -2.89 | [-5.90, -1.47] | [-9.59, +0.93] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| m2 − m1 | AUC | +0.03 | [-0.09, +0.14] | [-0.85, +1.13] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| m4 − m3 | **pAUC@1e-2** | -4.73 | [-7.53, -2.22] | [-9.46, +0.88] | 1 up / 9 down | not resolved |
| m4 − m3 | TPR@1e-3 | -12.86 | [-24.86, -4.73] | [-30.70, -0.77] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| m4 − m3 | TPR@1e-2 | -1.22 | [-2.32, -0.28] | [-6.64, +5.43] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| m4 − m3 | AUC | -0.15 | [-0.28, -0.04] | [-0.95, +0.64] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| m4 − m2 | **pAUC@1e-2** | +10.05 | [+6.88, +13.41] | [+4.11, +16.33] | 8 up / 2 down | **RESOLVED better** |
| m4 − m2 | TPR@1e-3 | +11.68 | [+0.41, +20.97] | [-5.81, +21.47] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| m4 − m2 | TPR@1e-2 | +2.65 | [+1.35, +5.90] | [-0.63, +11.81] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| m4 − m2 | AUC | +0.09 | [-0.01, +0.19] | [-0.69, +0.96] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| m3 − m1 | **pAUC@1e-2** | +3.63 | [+1.47, +5.83] | [-1.58, +8.37] | 7 up / 3 down | not resolved |
| m3 − m1 | TPR@1e-3 | +4.91 | [-0.76, +11.13] | [-4.67, +13.83] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| m3 − m1 | TPR@1e-2 | +0.99 | [-0.09, +2.48] | [-3.99, +6.62] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| m3 − m1 | AUC | +0.27 | [+0.15, +0.39] | [-0.64, +1.35] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| m1 − old1 | **pAUC@1e-2** | -3.13 | [-4.33, -2.00] | [-6.01, -0.54] | 4 up / 6 down | **RESOLVED worse** |
| m1 − old1 | TPR@1e-3 | -0.21 | [-5.22, +2.14] | [-6.32, +2.97] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| m1 − old1 | TPR@1e-2 | -3.09 | [-4.18, -2.40] | [-6.47, -0.89] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| m1 − old1 | AUC | +0.23 | [+0.17, +0.28] | [-0.08, +0.70] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| m3 − old3 | **pAUC@1e-2** | +0.26 | [-1.29, +2.00] | [-1.86, +2.61] | 5 up / 5 down | not resolved |
| m3 − old3 | TPR@1e-3 | +1.78 | [-3.59, +5.71] | [-6.43, +7.64] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| m3 − old3 | TPR@1e-2 | -0.45 | [-0.87, +0.33] | [-1.63, +0.67] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| m3 − old3 | AUC | -0.19 | [-0.24, -0.12] | [-0.61, +0.19] | 4 up / 6 down | cluster CI contains 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| m2 − m1 | -6.39 | [-9.80, -3.48] |
| m4 − m3 | -0.62 | [-3.39, +1.71] |
| m4 − m2 | +4.97 | [+1.86, +8.48] |
| m3 − m1 | -0.80 | [-3.10, +1.90] |
| m1 − old1 | -2.93 | [-4.68, -1.40] |
| m3 − old3 | -0.31 | [-1.78, +1.40] |


### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | v2-PE, old split (reference) | ATT+bal, old split (reference) | **M1 v2-PE (all January)** | **M2 two-level, no padding (all January)** | **M3 ATT+bal (all January)** | **M4 ATT+bal-2L (all January)** |
|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 83.7 ± 2.4 | 82.1 ± 1.9 | 80.7 ± 2.7 | 78.7 ± 7.0 | 81.5 ± 1.2 | 80.7 ± 1.4 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 81.7 ± 6.8 | 72.8 ± 6.1 | 74.1 ± 11.6 | 75.4 ± 14.9 | 71.6 ± 2.1 | 84.2 ± 6.5 |
| dropper | 252 | 80.1 ± 2.4 | 81.9 ± 5.7 | 77.7 ± 3.0 | 75.6 ± 5.5 | 83.3 ± 0.7 | 79.2 ± 2.3 |
| keylogger | 1041 | 87.1 ± 6.1 | 87.0 ± 2.5 | 87.0 ± 2.4 | 83.4 ± 3.4 | 87.7 ± 2.8 | 85.1 ± 5.7 |
| ransomware | 2139 | 70.8 ± 4.9 | 72.9 ± 2.2 | 69.6 ± 5.3 | 62.1 ± 2.9 | 72.4 ± 3.4 | 63.3 ± 2.4 |
| rat | 1258 | 89.2 ± 2.0 | 87.8 ± 2.8 | 83.5 ± 10.0 | 79.7 ± 17.2 | 86.9 ± 0.6 | 82.0 ± 9.3 |
| trojan | 1085 | 80.9 ± 1.2 | 80.4 ± 2.5 | 81.1 ± 2.3 | 80.8 ± 1.8 | 80.6 ± 1.4 | 78.7 ± 2.0 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.5 ± 0.8 | 0.0 ± 0.0 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens of the OLD tokenizer; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold (threshold on the April benign scores). Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| v2-PE, old split (reference) | 8/10 | +7.7 (IQR +1.2 to +19.7) | 82.1 ± 2.4 | 81.7 ± 6.8 |
| ATT+bal, old split (reference) | 1/10 | -3.2 (IQR -4.6 to -1.6) | 84.6 ± 3.0 | 72.8 ± 6.1 |
| **M1 v2-PE (all January)** | 5/10 | +0.1 (IQR -1.2 to +4.6) | 78.6 ± 4.7 | 74.1 ± 11.6 |
| **M2 two-level, no padding (all January)** | 6/10 | +1.0 (IQR -0.3 to +2.2) | 78.2 ± 10.1 | 75.4 ± 14.9 |
| **M3 ATT+bal (all January)** | 0/10 | -4.2 (IQR -5.4 to -3.1) | 84.9 ± 2.5 | 71.6 ± 2.1 |
| **M4 ATT+bal-2L (all January)** | 9/10 | +1.0 (IQR +0.2 to +2.0) | 83.2 ± 4.6 | 84.2 ± 6.5 |

