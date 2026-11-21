### Clean April test, 10 seeds each, one evaluation per model (Step 5, final protocol): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| v2-PE, old validation slice (old split, 2 epochs) | 10 | 0.543 ± 0.063 | 0.811 ± 0.023 | 0.9644 ± 0.0093 | 0.915 ± 0.012 | 0.705 ± 0.031 | 0.444 ± 0.076 |
| v2-PE, new split, NEW tokenizer (Stage C) | 10 | 0.479 ± 0.036 | 0.732 ± 0.027 | 0.9599 ± 0.0122 | 0.880 ± 0.018 | 0.634 ± 0.024 | 0.366 ± 0.066 |
| v2-PE, new split, OLD tokenizer (Step 3b) | 10 | 0.445 ± 0.095 | 0.718 ± 0.051 | 0.9486 ± 0.0111 | 0.872 ± 0.033 | 0.596 ± 0.067 | 0.328 ± 0.095 |
| **v2-PE, ALL January, old tokenizer (Step 5, final protocol)** | 10 | 0.541 ± 0.095 | 0.780 ± 0.038 | 0.9667 ± 0.0071 | 0.899 ± 0.021 | 0.674 ± 0.053 | 0.426 ± 0.086 |
| ATT+bal, old validation slice (old split, 2 epochs) | 10 | 0.572 ± 0.061 | 0.795 ± 0.020 | 0.9713 ± 0.0066 | 0.913 ± 0.017 | 0.707 ± 0.017 | 0.457 ± 0.041 |
| ATT+bal, new split, NEW tokenizer (Stage C) | 10 | 0.503 ± 0.048 | 0.665 ± 0.064 | 0.9386 ± 0.0127 | 0.860 ± 0.033 | 0.590 ± 0.052 | 0.379 ± 0.063 |
| ATT+bal, new split, OLD tokenizer (Step 3b) | 10 | 0.535 ± 0.034 | 0.711 ± 0.027 | 0.9496 ± 0.0114 | 0.881 ± 0.026 | 0.627 ± 0.025 | 0.385 ± 0.048 |
| **ATT+bal, ALL January, old tokenizer (Step 5, final protocol)** | 10 | 0.590 ± 0.029 | 0.790 ± 0.008 | 0.9694 ± 0.0044 | 0.908 ± 0.011 | 0.710 ± 0.015 | 0.477 ± 0.051 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| v2-PE, old validation slice (old split, 2 epochs) | 0.606 | 0.851 | 0.9705 | 0.927 | **0.768** | 0.546 |
| v2-PE, new split, NEW tokenizer (Stage C) | 0.603 | 0.756 | 0.9668 | 0.899 | **0.689** | 0.529 |
| v2-PE, new split, OLD tokenizer (Step 3b) | 0.574 | 0.773 | 0.9580 | 0.905 | **0.683** | 0.439 |
| **v2-PE, ALL January, old tokenizer (Step 5, final protocol)** | 0.622 | 0.843 | 0.9738 | 0.921 | **0.739** | 0.548 |
| ATT+bal, old validation slice (old split, 2 epochs) | 0.583 | 0.814 | 0.9780 | 0.926 | **0.734** | 0.503 |
| ATT+bal, new split, NEW tokenizer (Stage C) | 0.537 | 0.711 | 0.9470 | 0.857 | **0.647** | 0.442 |
| ATT+bal, new split, OLD tokenizer (Step 3b) | 0.585 | 0.723 | 0.9566 | 0.904 | **0.653** | 0.442 |
| **ATT+bal, ALL January, old tokenizer (Step 5, final protocol)** | 0.603 | 0.801 | 0.9748 | 0.921 | **0.731** | 0.536 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| full_v2pe − gs_v2pe | **pAUC@1e-2** | +3.96 | [+2.81, +5.04] | [-2.61, +12.74] | 8 up / 2 down | not resolved |
| full_v2pe − gs_v2pe | TPR@1e-3 | +6.19 | [+0.96, +8.84] | [-2.19, +13.71] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| full_v2pe − gs_v2pe | TPR@1e-2 | +4.80 | [+3.61, +5.62] | [-2.04, +12.81] | 9 up / 1 down | cluster CI contains 0 (descriptive) |
| full_v2pe − gs_v2pe | AUC | +0.68 | [+0.56, +0.81] | [-0.40, +1.98] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| full_v2pe − old_v2pe | **pAUC@1e-2** | -3.13 | [-4.33, -2.00] | [-6.01, -0.54] | 4 up / 6 down | **RESOLVED worse** |
| full_v2pe − old_v2pe | TPR@1e-3 | -0.21 | [-5.22, +2.14] | [-6.32, +2.97] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| full_v2pe − old_v2pe | TPR@1e-2 | -3.09 | [-4.18, -2.40] | [-6.47, -0.89] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| full_v2pe − old_v2pe | AUC | +0.23 | [+0.17, +0.28] | [-0.08, +0.70] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| gs_v2pe − old_v2pe | **pAUC@1e-2** | -7.09 | [-8.33, -5.78] | [-14.90, -1.45] | 0 up / 10 down | **RESOLVED worse** |
| gs_v2pe − old_v2pe | TPR@1e-3 | -6.40 | [-9.96, -3.40] | [-15.12, -0.17] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| gs_v2pe − old_v2pe | TPR@1e-2 | -7.89 | [-9.02, -6.88] | [-15.32, -1.96] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| gs_v2pe − old_v2pe | AUC | -0.45 | [-0.59, -0.32] | [-1.76, +0.84] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| full_v2pe − tk_v2pe | **pAUC@1e-2** | +7.74 | [+6.54, +8.87] | [+0.87, +16.13] | 9 up / 1 down | **RESOLVED better** |
| full_v2pe − tk_v2pe | TPR@1e-3 | +9.57 | [+5.99, +12.79] | [+1.44, +19.02] | 10 up / 0 down | cluster CI excludes 0 (descriptive) |
| full_v2pe − tk_v2pe | TPR@1e-2 | +6.22 | [+5.13, +7.09] | [-0.08, +13.49] | 9 up / 1 down | cluster CI contains 0 (descriptive) |
| full_v2pe − tk_v2pe | AUC | +1.81 | [+1.67, +1.94] | [+0.63, +3.59] | 9 up / 1 down | cluster CI excludes 0 (descriptive) |
| full_attbal − gs_attbal | **pAUC@1e-2** | +11.94 | [+10.58, +13.29] | [+5.33, +19.39] | 10 up / 0 down | **RESOLVED better** |
| full_attbal − gs_attbal | TPR@1e-3 | +8.68 | [+5.94, +12.05] | [+1.87, +17.19] | 9 up / 1 down | cluster CI excludes 0 (descriptive) |
| full_attbal − gs_attbal | TPR@1e-2 | +12.48 | [+10.91, +13.81] | [+5.42, +19.95] | 10 up / 0 down | cluster CI excludes 0 (descriptive) |
| full_attbal − gs_attbal | AUC | +3.08 | [+2.86, +3.31] | [+0.65, +6.42] | 10 up / 0 down | cluster CI excludes 0 (descriptive) |
| full_attbal − old_attbal | **pAUC@1e-2** | +0.26 | [-1.29, +2.00] | [-1.86, +2.61] | 5 up / 5 down | not resolved |
| full_attbal − old_attbal | TPR@1e-3 | +1.78 | [-3.59, +5.71] | [-6.43, +7.64] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| full_attbal − old_attbal | TPR@1e-2 | -0.45 | [-0.87, +0.33] | [-1.63, +0.67] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| full_attbal − old_attbal | AUC | -0.19 | [-0.24, -0.12] | [-0.61, +0.19] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| gs_attbal − old_attbal | **pAUC@1e-2** | -11.68 | [-13.56, -9.59] | [-19.68, -4.61] | 0 up / 10 down | **RESOLVED worse** |
| gs_attbal − old_attbal | TPR@1e-3 | -6.90 | [-13.53, -2.01] | [-17.82, +1.92] | 2 up / 8 down | cluster CI contains 0 (descriptive) |
| gs_attbal − old_attbal | TPR@1e-2 | -12.93 | [-14.17, -11.21] | [-20.10, -5.61] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − old_attbal | AUC | -3.27 | [-3.48, -3.04] | [-6.41, -0.96] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| full_attbal − tk_attbal | **pAUC@1e-2** | +8.26 | [+7.24, +9.25] | [+1.80, +16.65] | 10 up / 0 down | **RESOLVED better** |
| full_attbal − tk_attbal | TPR@1e-3 | +5.51 | [+3.45, +10.14] | [-1.95, +15.66] | 9 up / 1 down | cluster CI contains 0 (descriptive) |
| full_attbal − tk_attbal | TPR@1e-2 | +7.86 | [+7.21, +8.84] | [+1.70, +16.06] | 10 up / 0 down | cluster CI excludes 0 (descriptive) |
| full_attbal − tk_attbal | AUC | +1.98 | [+1.82, +2.14] | [+0.56, +4.16] | 10 up / 0 down | cluster CI excludes 0 (descriptive) |
| full_attbal − full_v2pe | **pAUC@1e-2** | +3.63 | [+1.47, +5.83] | [-1.58, +8.37] | 7 up / 3 down | not resolved |
| full_attbal − full_v2pe | TPR@1e-3 | +4.91 | [-0.76, +11.13] | [-4.67, +13.83] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| full_attbal − full_v2pe | TPR@1e-2 | +0.99 | [-0.09, +2.48] | [-3.99, +6.62] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| full_attbal − full_v2pe | AUC | +0.27 | [+0.15, +0.39] | [-0.64, +1.35] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| gs_attbal − gs_v2pe | **pAUC@1e-2** | -4.36 | [-6.46, -2.15] | [-9.40, +0.81] | 3 up / 7 down | not resolved |
| gs_attbal − gs_v2pe | TPR@1e-3 | +2.42 | [-6.01, +8.09] | [-8.98, +10.96] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| gs_attbal − gs_v2pe | TPR@1e-2 | -6.68 | [-8.29, -4.77] | [-12.05, -1.35] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − gs_v2pe | AUC | -2.13 | [-2.32, -1.95] | [-4.31, -0.41] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| full_v2pe − gs_v2pe | +5.01 | [+3.39, +6.53] |
| full_v2pe − old_v2pe | -2.93 | [-4.68, -1.40] |
| gs_v2pe − old_v2pe | -7.95 | [-9.25, -6.42] |
| full_v2pe − tk_v2pe | +5.60 | [+4.32, +6.90] |
| full_attbal − gs_attbal | +8.37 | [+7.11, +9.51] |
| full_attbal − old_attbal | -0.31 | [-1.78, +1.40] |
| gs_attbal − old_attbal | -8.68 | [-10.58, -6.59] |
| full_attbal − tk_attbal | +7.78 | [+6.70, +8.79] |
| full_attbal − full_v2pe | -0.80 | [-3.10, +1.90] |
| gs_attbal − gs_v2pe | -4.16 | [-6.28, -2.11] |


### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | v2-PE, old validation slice (old split, 2 epochs) | v2-PE, new split, NEW tokenizer (Stage C) | v2-PE, new split, OLD tokenizer (Step 3b) | **v2-PE, ALL January, old tokenizer (Step 5, final protocol)** | ATT+bal, old validation slice (old split, 2 epochs) | ATT+bal, new split, NEW tokenizer (Stage C) | ATT+bal, new split, OLD tokenizer (Step 3b) | **ATT+bal, ALL January, old tokenizer (Step 5, final protocol)** |
|---|---|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 83.7 ± 2.4 | 81.5 ± 2.3 | 81.0 ± 3.1 | 80.7 ± 2.7 | 82.1 ± 1.9 | 76.3 ± 7.7 | 79.0 ± 3.5 | 81.5 ± 1.2 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 81.7 ± 6.8 | 76.7 ± 7.6 | 76.5 ± 8.6 | 74.1 ± 11.6 | 72.8 ± 6.1 | 61.7 ± 6.8 | 68.2 ± 6.5 | 71.6 ± 2.1 |
| dropper | 252 | 80.1 ± 2.4 | 73.7 ± 5.4 | 70.3 ± 7.4 | 77.7 ± 3.0 | 81.9 ± 5.7 | 78.7 ± 6.3 | 82.7 ± 3.2 | 83.3 ± 0.7 |
| keylogger | 1041 | 87.1 ± 6.1 | 70.3 ± 3.0 | 68.5 ± 7.8 | 87.0 ± 2.4 | 87.0 ± 2.5 | 63.4 ± 6.6 | 68.4 ± 4.0 | 87.7 ± 2.8 |
| ransomware | 2139 | 70.8 ± 4.9 | 68.2 ± 6.8 | 64.8 ± 11.5 | 69.6 ± 5.3 | 72.9 ± 2.2 | 61.7 ± 6.8 | 67.1 ± 3.9 | 72.4 ± 3.4 |
| rat | 1258 | 89.2 ± 2.0 | 76.5 ± 1.3 | 76.3 ± 6.6 | 83.5 ± 10.0 | 87.8 ± 2.8 | 69.8 ± 11.2 | 76.5 ± 1.7 | 86.9 ± 0.6 |
| trojan | 1085 | 80.9 ± 1.2 | 61.7 ± 5.6 | 60.1 ± 5.9 | 81.1 ± 2.3 | 80.4 ± 2.5 | 62.4 ± 5.9 | 63.4 ± 1.8 | 80.6 ± 1.4 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.3 ± 0.7 | 0.5 ± 0.8 | 0.5 ± 0.8 |


### Change of the detection rate against the old-split models, per family (points; thresholds on the April benign scores)

| malware family | n | v2-PE gs − old (points) | v2-PE tk − old (points) | v2-PE full − old (points) | ATT+bal gs − old (points) | ATT+bal tk − old (points) | ATT+bal full − old (points) |
|---|---|---|---|---|---|---|---|
| backdoor | 1940 | -2.1 | -2.7 | -3.0 | -5.8 | -3.1 | -0.6 |
| coinminer | 1684 | -5.1 | -5.2 | -7.6 | -11.2 | -4.6 | -1.3 |
| dropper | 252 | -6.4 | -9.8 | -2.5 | -3.2 | +0.8 | +1.4 |
| keylogger | 1041 | -16.8 | -18.6 | -0.1 | -23.6 | -18.6 | +0.7 |
| ransomware | 2139 | -2.6 | -6.0 | -1.3 | -11.2 | -5.8 | -0.6 |
| rat | 1258 | -12.7 | -12.9 | -5.7 | -17.9 | -11.3 | -0.8 |
| trojan | 1085 | -19.3 | -20.9 | +0.2 | -17.9 | -17.0 | +0.3 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens of the OLD tokenizer; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold (threshold on the April benign scores). Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| v2-PE, old validation slice (old split, 2 epochs) | 8/10 | +7.7 (IQR +1.2 to +19.7) | 82.1 ± 2.4 | 81.7 ± 6.8 |
| v2-PE, new split, NEW tokenizer (Stage C) | 7/10 | +1.6 (IQR -1.2 to +4.7) | 77.9 ± 1.6 | 76.7 ± 7.6 |
| v2-PE, new split, OLD tokenizer (Step 3b) | 8/10 | +2.3 (IQR +0.6 to +3.0) | 75.9 ± 3.9 | 76.5 ± 8.6 |
| **v2-PE, ALL January, old tokenizer (Step 5, final protocol)** | 5/10 | +0.1 (IQR -1.2 to +4.6) | 78.6 ± 4.7 | 74.1 ± 11.6 |
| ATT+bal, old validation slice (old split, 2 epochs) | 1/10 | -3.2 (IQR -4.6 to -1.6) | 84.6 ± 3.0 | 72.8 ± 6.1 |
| ATT+bal, new split, NEW tokenizer (Stage C) | 0/10 | -6.6 (IQR -8.4 to -4.4) | 73.2 ± 8.0 | 61.7 ± 6.8 |
| ATT+bal, new split, OLD tokenizer (Step 3b) | 1/10 | -3.4 (IQR -4.1 to -2.6) | 79.1 ± 4.4 | 68.2 ± 6.5 |
| **ATT+bal, ALL January, old tokenizer (Step 5, final protocol)** | 0/10 | -4.2 (IQR -5.4 to -3.1) | 84.9 ± 2.5 | 71.6 ± 2.1 |

