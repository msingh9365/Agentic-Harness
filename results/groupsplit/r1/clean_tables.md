### Clean April test, 10 seeds each, one evaluation per model (the windowed M3 next to M1, M3, M4 and the test-time multi-window baseline): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| M1 Nebula (final) | 10 | 0.536 ± 0.060 | 0.791 ± 0.020 | 0.9639 ± 0.0111 | 0.891 ± 0.027 | 0.686 ± 0.026 | 0.398 ± 0.095 |
| M3 ATT+bal (final) | 10 | 0.567 ± 0.047 | 0.790 ± 0.019 | 0.9693 ± 0.0065 | 0.913 ± 0.011 | 0.705 ± 0.025 | 0.443 ± 0.089 |
| M4 ATT+bal-2L (final) | 10 | 0.453 ± 0.149 | 0.779 ± 0.017 | 0.9677 ± 0.0052 | 0.911 ± 0.013 | 0.661 ± 0.035 | 0.319 ± 0.106 |
| M3 + test-time multi-window max | 10 | 0.441 ± 0.084 | 0.718 ± 0.033 | 0.9230 ± 0.0070 | 0.793 ± 0.007 | 0.594 ± 0.038 | 0.310 ± 0.084 |
| **R1 windowed M3** | 10 | 0.545 ± 0.042 | 0.736 ± 0.015 | 0.9290 ± 0.0090 | 0.870 ± 0.010 | 0.660 ± 0.016 | 0.404 ± 0.059 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| M1 Nebula (final) | 0.663 | 0.837 | 0.9705 | 0.913 | **0.756** | 0.552 |
| M3 ATT+bal (final) | 0.597 | 0.800 | 0.9752 | 0.919 | **0.730** | 0.532 |
| M4 ATT+bal-2L (final) | 0.629 | 0.803 | 0.9777 | 0.917 | **0.719** | 0.445 |
| M3 + test-time multi-window max | 0.494 | 0.740 | 0.9322 | 0.795 | **0.650** | 0.417 |
| **R1 windowed M3** | 0.610 | 0.737 | 0.9394 | 0.886 | **0.677** | 0.487 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| r1 − f3 | **pAUC@1e-2** | -4.53 | [-6.92, -2.33] | [-16.58, +5.36] | 0 up / 10 down | not resolved |
| r1 − f3 | TPR@1e-3 | -2.21 | [-11.93, +3.18] | [-20.16, +10.61] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| r1 − f3 | TPR@1e-2 | -5.43 | [-6.49, -4.43] | [-17.00, +5.00] | 0 up / 10 down | cluster CI contains 0 (descriptive) |
| r1 − f3 | AUC | -4.03 | [-4.33, -3.75] | [-8.02, -0.76] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| r1 − f4 | **pAUC@1e-2** | -0.14 | [-2.42, +2.49] | [-12.07, +8.60] | 5 up / 5 down | not resolved |
| r1 − f4 | TPR@1e-3 | +9.14 | [+0.55, +12.45] | [-8.00, +20.96] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| r1 − f4 | TPR@1e-2 | -4.31 | [-5.50, -3.39] | [-14.51, +2.57] | 0 up / 10 down | cluster CI contains 0 (descriptive) |
| r1 − f4 | AUC | -3.87 | [-4.12, -3.63] | [-7.70, -1.06] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| r1 − mw | **pAUC@1e-2** | +6.51 | [+3.67, +9.35] | [-6.59, +17.91] | 10 up / 0 down | not resolved |
| r1 − mw | TPR@1e-3 | +10.32 | [+0.21, +15.79] | [-8.95, +25.02] | 8 up / 2 down | cluster CI contains 0 (descriptive) |
| r1 − mw | TPR@1e-2 | +1.82 | [+0.47, +3.76] | [-9.42, +12.85] | 8 up / 2 down | cluster CI contains 0 (descriptive) |
| r1 − mw | AUC | +0.60 | [+0.20, +0.97] | [-3.85, +4.67] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| r1 − f1 | **pAUC@1e-2** | -2.68 | [-5.27, -0.08] | [-13.87, +5.94] | 1 up / 9 down | not resolved |
| r1 − f1 | TPR@1e-3 | +0.81 | [-10.14, +8.04] | [-15.71, +13.38] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| r1 − f1 | TPR@1e-2 | -5.54 | [-6.69, -4.39] | [-14.77, +2.55] | 0 up / 10 down | cluster CI contains 0 (descriptive) |
| r1 − f1 | AUC | -3.49 | [-3.80, -3.19] | [-7.49, +0.01] | 0 up / 10 down | cluster CI contains 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| r1 − f3 | -5.25 | [-7.56, -3.01] |
| r1 − f4 | -4.22 | [-5.96, -1.96] |
| r1 − mw | +2.66 | [-0.10, +5.96] |
| r1 − f1 | -7.88 | [-10.42, -5.22] |


### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | M1 Nebula (final) | M3 ATT+bal (final) | M4 ATT+bal-2L (final) | M3 + test-time multi-window max | **R1 windowed M3** |
|---|---|---|---|---|---|---|
| backdoor | 1940 | 82.7 ± 1.6 | 81.0 ± 0.9 | 81.0 ± 1.2 | 80.2 ± 4.1 | 81.1 ± 1.6 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 80.2 ± 7.5 | 71.9 ± 6.7 | 84.1 ± 6.6 | 67.8 ± 6.4 | 91.2 ± 1.1 |
| dropper | 252 | 75.0 ± 4.6 | 83.5 ± 1.0 | 80.3 ± 2.0 | 73.2 ± 2.4 | 75.9 ± 2.2 |
| keylogger | 1041 | 86.3 ± 5.1 | 88.7 ± 2.0 | 86.2 ± 4.3 | 76.8 ± 3.0 | 45.6 ± 14.6 |
| ransomware | 2139 | 67.0 ± 5.2 | 72.2 ± 3.1 | 62.3 ± 3.6 | 59.2 ± 4.1 | 57.8 ± 3.0 |
| rat | 1258 | 88.2 ± 2.0 | 86.8 ± 0.9 | 82.5 ± 8.3 | 77.2 ± 8.8 | 85.8 ± 0.8 |
| trojan | 1085 | 78.6 ± 3.9 | 80.8 ± 1.3 | 79.7 ± 2.7 | 76.3 ± 1.3 | 76.3 ± 1.2 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.5 ± 0.8 | 0.0 ± 0.0 | 0.2 ± 0.5 | 0.0 ± 0.0 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens of the OLD tokenizer, the same set of reports for all models; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold (threshold on the April benign scores). Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| M1 Nebula (final) | 8/10 | +1.6 (IQR +0.6 to +2.9) | 80.2 ± 3.4 | 80.2 ± 7.5 |
| M3 ATT+bal (final) | 1/10 | -3.9 (IQR -5.0 to -2.4) | 83.4 ± 2.4 | 71.9 ± 6.7 |
| M4 ATT+bal-2L (final) | 9/10 | +1.5 (IQR +0.9 to +1.8) | 83.0 ± 3.8 | 84.1 ± 6.6 |
| M3 + test-time multi-window max | 1/10 | -3.8 (IQR -5.2 to -1.9) | 78.6 ± 4.0 | 67.8 ± 6.4 |
| **R1 windowed M3** | 10/10 | +4.5 (IQR +3.7 to +5.1) | 89.5 ± 1.3 | 91.2 ± 1.1 |

