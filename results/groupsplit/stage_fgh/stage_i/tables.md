### Clean April test, 10 seeds each, one evaluation per model (Stage I, the four final models with the corrected tokenizer next to the current ones): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| M1 v2-PE (current tokenizer) | 10 | 0.541 ± 0.095 | 0.780 ± 0.038 | 0.9667 ± 0.0071 | 0.899 ± 0.021 | 0.674 ± 0.053 | 0.426 ± 0.086 |
| M2 two-level, no padding (current tokenizer) | 10 | 0.344 ± 0.189 | 0.751 ± 0.068 | 0.9670 ± 0.0105 | 0.888 ± 0.038 | 0.562 ± 0.146 | 0.202 ± 0.116 |
| M3 ATT+bal (current tokenizer) | 10 | 0.590 ± 0.029 | 0.790 ± 0.008 | 0.9694 ± 0.0044 | 0.908 ± 0.011 | 0.710 ± 0.015 | 0.477 ± 0.051 |
| M4 ATT+bal-2L (current tokenizer) | 10 | 0.461 ± 0.174 | 0.778 ± 0.021 | 0.9679 ± 0.0075 | 0.910 ± 0.010 | 0.663 ± 0.036 | 0.273 ± 0.124 |
| **M1 v2-PE (fixed tokenizer)** | 10 | 0.536 ± 0.060 | 0.791 ± 0.020 | 0.9639 ± 0.0111 | 0.891 ± 0.027 | 0.686 ± 0.026 | 0.398 ± 0.095 |
| **M2 two-level, no padding (fixed tokenizer)** | 10 | 0.381 ± 0.165 | 0.772 ± 0.049 | 0.9690 ± 0.0073 | 0.898 ± 0.022 | 0.620 ± 0.080 | 0.270 ± 0.153 |
| **M3 ATT+bal (fixed tokenizer)** | 10 | 0.567 ± 0.047 | 0.790 ± 0.019 | 0.9693 ± 0.0065 | 0.913 ± 0.011 | 0.705 ± 0.025 | 0.443 ± 0.089 |
| **M4 ATT+bal-2L (fixed tokenizer)** | 10 | 0.453 ± 0.149 | 0.779 ± 0.017 | 0.9677 ± 0.0052 | 0.911 ± 0.013 | 0.661 ± 0.035 | 0.319 ± 0.106 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| M1 v2-PE (current tokenizer) | 0.622 | 0.843 | 0.9738 | 0.921 | **0.739** | 0.548 |
| M2 two-level, no padding (current tokenizer) | 0.532 | 0.802 | 0.9749 | 0.914 | **0.675** | 0.317 |
| M3 ATT+bal (current tokenizer) | 0.603 | 0.801 | 0.9748 | 0.921 | **0.731** | 0.536 |
| M4 ATT+bal-2L (current tokenizer) | 0.628 | 0.812 | 0.9767 | 0.917 | **0.725** | 0.451 |
| **M1 v2-PE (fixed tokenizer)** | 0.663 | 0.837 | 0.9705 | 0.913 | **0.756** | 0.552 |
| **M2 two-level, no padding (fixed tokenizer)** | 0.541 | 0.801 | 0.9752 | 0.910 | **0.698** | 0.449 |
| **M3 ATT+bal (fixed tokenizer)** | 0.597 | 0.800 | 0.9752 | 0.919 | **0.730** | 0.532 |
| **M4 ATT+bal-2L (fixed tokenizer)** | 0.629 | 0.803 | 0.9777 | 0.917 | **0.719** | 0.445 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| f1 − c1 | **pAUC@1e-2** | +1.28 | [+0.59, +1.95] | [-0.98, +3.79] | 5 up / 5 down | not resolved |
| f1 − c1 | TPR@1e-3 | -0.43 | [-3.97, +4.35] | [-5.15, +5.35] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f1 − c1 | TPR@1e-2 | +1.12 | [+0.53, +2.07] | [-1.18, +4.26] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| f1 − c1 | AUC | -0.28 | [-0.33, -0.24] | [-0.75, +0.05] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f2 − c2 | **pAUC@1e-2** | +5.80 | [+4.40, +7.24] | [+3.12, +8.94] | 7 up / 3 down | **RESOLVED better** |
| f2 − c2 | TPR@1e-3 | +3.62 | [-0.90, +9.57] | [-3.48, +11.51] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f2 − c2 | TPR@1e-2 | +2.06 | [+1.09, +4.64] | [-0.08, +7.92] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| f2 − c2 | AUC | +0.20 | [+0.16, +0.24] | [-0.07, +0.54] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| f3 − c3 | **pAUC@1e-2** | -0.50 | [-1.01, -0.03] | [-1.18, +0.20] | 5 up / 5 down | not resolved |
| f3 − c3 | TPR@1e-3 | -2.32 | [-4.28, +1.02] | [-5.41, +1.02] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| f3 − c3 | TPR@1e-2 | +0.02 | [-0.55, +0.36] | [-0.91, +0.88] | 4 up / 5 down | cluster CI contains 0 (descriptive) |
| f3 − c3 | AUC | -0.01 | [-0.04, +0.03] | [-0.20, +0.21] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| f4 − c4 | **pAUC@1e-2** | -0.16 | [-1.43, +1.07] | [-2.13, +1.60] | 4 up / 6 down | not resolved |
| f4 − c4 | TPR@1e-3 | -0.81 | [-3.58, +8.01] | [-4.94, +8.78] | 2 up / 8 down | cluster CI contains 0 (descriptive) |
| f4 − c4 | TPR@1e-2 | +0.12 | [-0.35, +0.72] | [-1.55, +1.43] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| f4 − c4 | AUC | -0.02 | [-0.06, +0.02] | [-0.37, +0.33] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | **pAUC@1e-2** | +1.84 | [-0.32, +4.25] | [-3.22, +6.39] | 7 up / 3 down | not resolved |
| f3 − f1 | TPR@1e-3 | +3.02 | [-3.92, +10.60] | [-8.19, +15.11] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | TPR@1e-2 | -0.11 | [-1.14, +0.95] | [-5.26, +4.62] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | AUC | +0.55 | [+0.42, +0.67] | [-0.37, +1.80] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| f4 − f3 | **pAUC@1e-2** | -4.39 | [-7.07, -2.11] | [-9.43, +1.14] | 1 up / 9 down | not resolved |
| f4 − f3 | TPR@1e-3 | -11.35 | [-19.26, -3.36] | [-25.82, +0.11] | 1 up / 9 down | cluster CI contains 0 (descriptive) |
| f4 − f3 | TPR@1e-2 | -1.12 | [-2.00, -0.03] | [-6.46, +5.57] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f4 − f3 | AUC | -0.16 | [-0.30, -0.05] | [-0.97, +0.70] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f4 − f2 | **pAUC@1e-2** | +4.10 | [+1.45, +6.83] | [-0.62, +8.89] | 6 up / 4 down | not resolved |
| f4 − f2 | TPR@1e-3 | +7.25 | [-1.76, +16.70] | [-8.79, +20.31] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| f4 − f2 | TPR@1e-2 | +0.71 | [+0.05, +2.04] | [-1.54, +5.01] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f4 − f2 | AUC | -0.13 | [-0.23, -0.03] | [-0.85, +0.69] | 4 up / 6 down | cluster CI contains 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| f1 − c1 | +1.67 | [+0.50, +2.74] |
| f2 − c2 | +2.31 | [+0.82, +4.12] |
| f3 − c3 | -0.16 | [-0.56, +0.26] |
| f4 − c4 | -0.57 | [-1.40, +0.27] |
| f3 − f1 | -2.63 | [-4.74, -0.43] |
| f4 − f3 | -1.04 | [-3.62, +1.30] |
| f4 − f2 | +2.09 | [-0.27, +4.59] |


### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | M1 v2-PE (current tokenizer) | M2 two-level, no padding (current tokenizer) | M3 ATT+bal (current tokenizer) | M4 ATT+bal-2L (current tokenizer) | **M1 v2-PE (fixed tokenizer)** | **M2 two-level, no padding (fixed tokenizer)** | **M3 ATT+bal (fixed tokenizer)** | **M4 ATT+bal-2L (fixed tokenizer)** |
|---|---|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 80.7 ± 2.7 | 78.7 ± 7.0 | 81.5 ± 1.2 | 80.7 ± 1.4 | 82.7 ± 1.6 | 80.1 ± 3.7 | 81.0 ± 0.9 | 81.0 ± 1.2 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 74.1 ± 11.6 | 75.4 ± 14.9 | 71.6 ± 2.1 | 84.2 ± 6.5 | 80.2 ± 7.5 | 81.7 ± 8.3 | 71.9 ± 6.7 | 84.1 ± 6.6 |
| dropper | 252 | 77.7 ± 3.0 | 75.6 ± 5.5 | 83.3 ± 0.7 | 79.2 ± 2.3 | 75.0 ± 4.6 | 77.5 ± 2.8 | 83.5 ± 1.0 | 80.3 ± 2.0 |
| keylogger | 1041 | 87.0 ± 2.4 | 83.4 ± 3.4 | 87.7 ± 2.8 | 85.1 ± 5.7 | 86.3 ± 5.1 | 83.2 ± 5.1 | 88.7 ± 2.0 | 86.2 ± 4.3 |
| ransomware | 2139 | 69.6 ± 5.3 | 62.1 ± 2.9 | 72.4 ± 3.4 | 63.3 ± 2.4 | 67.0 ± 5.2 | 62.5 ± 2.5 | 72.2 ± 3.1 | 62.3 ± 3.6 |
| rat | 1258 | 83.5 ± 10.0 | 79.7 ± 17.2 | 86.9 ± 0.6 | 82.0 ± 9.3 | 88.2 ± 2.0 | 82.8 ± 14.8 | 86.8 ± 0.9 | 82.5 ± 8.3 |
| trojan | 1085 | 81.1 ± 2.3 | 80.8 ± 1.8 | 80.6 ± 1.4 | 78.7 ± 2.0 | 78.6 ± 3.9 | 81.5 ± 3.1 | 80.8 ± 1.3 | 79.7 ± 2.7 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.5 ± 0.8 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.5 ± 0.8 | 0.0 ± 0.0 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens of the OLD tokenizer, the same set of reports for all models; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold (threshold on the April benign scores). Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| M1 v2-PE (current tokenizer) | 5/10 | +0.1 (IQR -1.2 to +4.6) | 78.6 ± 4.7 | 74.1 ± 11.6 |
| M2 two-level, no padding (current tokenizer) | 6/10 | +1.0 (IQR -0.3 to +2.2) | 78.2 ± 10.1 | 75.4 ± 14.9 |
| M3 ATT+bal (current tokenizer) | 0/10 | -4.2 (IQR -5.4 to -3.1) | 84.9 ± 2.5 | 71.6 ± 2.1 |
| M4 ATT+bal-2L (current tokenizer) | 9/10 | +1.0 (IQR +0.2 to +2.0) | 83.2 ± 4.6 | 84.2 ± 6.5 |
| **M1 v2-PE (fixed tokenizer)** | 8/10 | +1.6 (IQR +0.6 to +2.9) | 80.2 ± 3.4 | 80.2 ± 7.5 |
| **M2 two-level, no padding (fixed tokenizer)** | 9/10 | +1.8 (IQR +0.9 to +2.1) | 80.2 ± 8.7 | 81.7 ± 8.3 |
| **M3 ATT+bal (fixed tokenizer)** | 1/10 | -3.9 (IQR -5.0 to -2.4) | 83.4 ± 2.4 | 71.9 ± 6.7 |
| **M4 ATT+bal-2L (fixed tokenizer)** | 9/10 | +1.5 (IQR +0.9 to +1.8) | 83.0 ± 3.8 | 84.1 ± 6.6 |

