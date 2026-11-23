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

