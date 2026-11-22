### Clean April test, 10 seeds each, one evaluation per model (P3, M1 and M3 with address roles (and the control) next to the Step 5 models): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| M1 v2-PE (Step 5) | 10 | 0.541 ± 0.095 | 0.780 ± 0.038 | 0.9667 ± 0.0071 | 0.899 ± 0.021 | 0.674 ± 0.053 | 0.426 ± 0.086 |
| **M1 v2-PE + address roles** | 10 | 0.155 ± 0.077 | 0.266 ± 0.109 | 0.7748 ± 0.1020 | 0.723 ± 0.081 | 0.209 ± 0.090 | 0.099 ± 0.048 |
| M3 ATT+bal (Step 5) | 10 | 0.590 ± 0.029 | 0.790 ± 0.008 | 0.9694 ± 0.0044 | 0.908 ± 0.011 | 0.710 ± 0.015 | 0.477 ± 0.051 |
| **M3 ATT+bal + address roles** | 10 | 0.021 ± 0.030 | 0.081 ± 0.068 | 0.7376 ± 0.0214 | 0.719 ± 0.017 | 0.050 ± 0.049 | 0.014 ± 0.022 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| M1 v2-PE (Step 5) | 0.622 | 0.843 | 0.9738 | 0.921 | **0.739** | 0.548 |
| **M1 v2-PE + address roles** | 0.222 | 0.271 | 0.8091 | 0.738 | **0.236** | 0.133 |
| M3 ATT+bal (Step 5) | 0.603 | 0.801 | 0.9748 | 0.921 | **0.731** | 0.536 |
| **M3 ATT+bal + address roles** | 0.004 | 0.067 | 0.7401 | 0.719 | **0.023** | 0.004 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| r1 − c1 | **pAUC@1e-2** | -46.49 | [-49.16, -43.78] | [-57.50, -32.58] | 0 up / 10 down | **RESOLVED worse** |
| r1 − c1 | TPR@1e-3 | -38.59 | [-43.95, -32.00] | [-51.32, -23.75] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| r1 − c1 | TPR@1e-2 | -51.43 | [-53.14, -49.18] | [-62.35, -36.82] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| r1 − c1 | AUC | -19.19 | [-19.65, -18.71] | [-27.24, -12.34] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| r3 − c3 | **pAUC@1e-2** | -66.03 | [-68.62, -63.25] | [-74.76, -53.41] | 0 up / 10 down | **RESOLVED worse** |
| r3 − c3 | TPR@1e-3 | -56.88 | [-60.97, -50.99] | [-67.19, -41.92] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| r3 − c3 | TPR@1e-2 | -70.94 | [-72.63, -69.38] | [-79.33, -58.90] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| r3 − c3 | AUC | -23.18 | [-23.79, -22.48] | [-35.01, -13.49] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| r3 − r1 | **pAUC@1e-2** | -15.92 | [-17.37, -14.68] | [-23.22, -9.92] | 1 up / 9 down | **RESOLVED worse** |
| r3 − r1 | TPR@1e-3 | -13.38 | [-14.98, -9.40] | [-19.20, -6.54] | 1 up / 9 down | cluster CI excludes 0 (descriptive) |
| r3 − r1 | TPR@1e-2 | -18.52 | [-19.46, -17.44] | [-26.88, -11.16] | 1 up / 9 down | cluster CI excludes 0 (descriptive) |
| r3 − r1 | AUC | -3.72 | [-4.06, -3.36] | [-8.63, +0.31] | 2 up / 8 down | cluster CI contains 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| r1 − c1 | -50.28 | [-53.24, -46.87] |
| r3 − c3 | -70.83 | [-73.51, -67.94] |
| r3 − r1 | -21.36 | [-23.08, -19.71] |


### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | M1 v2-PE (Step 5) | **M1 v2-PE + address roles** | M3 ATT+bal (Step 5) | **M3 ATT+bal + address roles** |
|---|---|---|---|---|---|
| backdoor | 1940 | 80.7 ± 2.7 | 43.2 ± 17.9 | 81.5 ± 1.2 | 12.6 ± 9.7 |
| clean | 7944 | 1.0 ± 0.0 | 0.9 ± 0.3 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 74.1 ± 11.6 | 6.9 ± 3.4 | 71.6 ± 2.1 | 0.7 ± 1.0 |
| dropper | 252 | 77.7 ± 3.0 | 34.0 ± 13.5 | 83.3 ± 0.7 | 19.1 ± 15.2 |
| keylogger | 1041 | 87.0 ± 2.4 | 3.9 ± 2.8 | 87.7 ± 2.8 | 1.2 ± 2.5 |
| ransomware | 2139 | 69.6 ± 5.3 | 35.6 ± 18.7 | 72.4 ± 3.4 | 10.2 ± 10.3 |
| rat | 1258 | 83.5 ± 10.0 | 20.8 ± 8.6 | 86.9 ± 0.6 | 2.0 ± 6.1 |
| trojan | 1085 | 81.1 ± 2.3 | 36.4 ± 16.7 | 80.6 ± 1.4 | 18.3 ± 12.8 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.5 ± 0.8 | 0.0 ± 0.0 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens of the OLD tokenizer, the same set of reports for all models; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold (threshold on the April benign scores). Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| M1 v2-PE (Step 5) | 5/10 | +0.1 (IQR -1.2 to +4.6) | 78.6 ± 4.7 | 74.1 ± 11.6 |
| **M1 v2-PE + address roles** | 0/10 | -12.9 (IQR -15.4 to -8.4) | 8.1 ± 4.0 | 6.9 ± 3.4 |
| M3 ATT+bal (Step 5) | 0/10 | -4.2 (IQR -5.4 to -3.1) | 84.9 ± 2.5 | 71.6 ± 2.1 |
| **M3 ATT+bal + address roles** | 0/10 | -23.0 (IQR -28.9 to -18.9) | 0.8 ± 1.2 | 0.7 ± 1.0 |

