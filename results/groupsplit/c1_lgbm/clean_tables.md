### Clean April test, 10 seeds each, one evaluation per model (the LightGBM bag of API names next to the final M3 and the final M1): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| M1 Nebula (final) | 10 | 0.536 ± 0.060 | 0.791 ± 0.020 | 0.9639 ± 0.0111 | 0.891 ± 0.027 | 0.686 ± 0.026 | 0.398 ± 0.095 |
| M3 ATT+bal (final) | 10 | 0.567 ± 0.047 | 0.790 ± 0.019 | 0.9693 ± 0.0065 | 0.913 ± 0.011 | 0.705 ± 0.025 | 0.443 ± 0.089 |
| **LightGBM bag of API names (single model)** | 10 | 0.266 ± 0.000 | 0.548 ± 0.000 | 0.9496 ± 0.0000 | 0.852 ± 0.000 | 0.483 ± 0.000 | 0.238 ± 0.000 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| M1 Nebula (final) | 0.663 | 0.837 | 0.9705 | 0.913 | **0.756** | 0.552 |
| M3 ATT+bal (final) | 0.597 | 0.800 | 0.9752 | 0.919 | **0.730** | 0.532 |
| **LightGBM bag of API names (single model)** | 0.266 | 0.548 | 0.9496 | 0.852 | **0.483** | 0.238 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| c1 − f3 | **pAUC@1e-2** | -22.20 | [-25.56, -18.83] | [-35.54, -8.99] | 0 up / 10 down | **RESOLVED worse** |
| c1 − f3 | TPR@1e-3 | -30.07 | [-35.98, -12.17] | [-43.62, -2.52] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| c1 − f3 | TPR@1e-2 | -24.20 | [-25.92, -23.03] | [-38.86, -10.97] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| c1 − f3 | AUC | -1.97 | [-2.27, -1.69] | [-4.77, +0.29] | 0 up / 10 down | cluster CI contains 0 (descriptive) |
| c1 − f1 | **pAUC@1e-2** | -20.36 | [-23.47, -17.01] | [-34.41, -6.95] | 0 up / 10 down | **RESOLVED worse** |
| c1 − f1 | TPR@1e-3 | -27.06 | [-33.33, -9.67] | [-42.15, -1.41] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| c1 − f1 | TPR@1e-2 | -24.31 | [-26.08, -22.89] | [-38.25, -9.32] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| c1 − f1 | AUC | -1.43 | [-1.72, -1.16] | [-3.92, +0.97] | 1 up / 9 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | **pAUC@1e-2** | +1.84 | [-0.32, +4.25] | [-3.22, +6.39] | 7 up / 3 down | not resolved |
| f3 − f1 | TPR@1e-3 | +3.02 | [-3.92, +10.60] | [-8.19, +15.11] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | TPR@1e-2 | -0.11 | [-1.14, +0.95] | [-5.26, +4.62] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| f3 − f1 | AUC | +0.55 | [+0.42, +0.67] | [-0.37, +1.80] | 7 up / 3 down | cluster CI contains 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| c1 − f3 | -24.68 | [-27.92, -21.33] |
| c1 − f1 | -27.31 | [-30.34, -24.14] |
| f3 − f1 | -2.63 | [-4.74, -0.43] |


### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | M1 Nebula (final) | M3 ATT+bal (final) | **LightGBM bag of API names (single model)** |
|---|---|---|---|---|
| backdoor | 1940 | 82.7 ± 1.6 | 81.0 ± 0.9 | 74.5 ± 0.0 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 80.2 ± 7.5 | 71.9 ± 6.7 | 33.4 ± 0.0 |
| dropper | 252 | 75.0 ± 4.6 | 83.5 ± 1.0 | 64.3 ± 0.0 |
| keylogger | 1041 | 86.3 ± 5.1 | 88.7 ± 2.0 | 14.2 ± 0.0 |
| ransomware | 2139 | 67.0 ± 5.2 | 72.2 ± 3.1 | 55.3 ± 0.0 |
| rat | 1258 | 88.2 ± 2.0 | 86.8 ± 0.9 | 75.1 ± 0.0 |
| trojan | 1085 | 78.6 ± 3.9 | 80.8 ± 1.3 | 65.3 ± 0.0 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.5 ± 0.8 | 0.0 ± 0.0 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens of the OLD tokenizer, the same set of reports for all models; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold (threshold on the April benign scores). Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| M1 Nebula (final) | 8/10 | +1.6 (IQR +0.6 to +2.9) | 80.2 ± 3.4 | 80.2 ± 7.5 |
| M3 ATT+bal (final) | 1/10 | -3.9 (IQR -5.0 to -2.4) | 83.4 ± 2.4 | 71.9 ± 6.7 |
| **LightGBM bag of API names (single model)** | 0/10 | -2.1 (IQR -2.1 to -2.1) | 39.6 ± 0.0 | 33.4 ± 0.0 |

