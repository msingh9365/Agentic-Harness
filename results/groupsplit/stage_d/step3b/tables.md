### Clean April test, 10 seeds each, one evaluation per model (Step 3b, diagnostic): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| v2-PE, old validation slice (old split, 2 epochs) | 10 | 0.543 ± 0.063 | 0.811 ± 0.023 | 0.9644 ± 0.0093 | 0.915 ± 0.012 | 0.705 ± 0.031 | 0.444 ± 0.076 |
| v2-PE, new split, NEW tokenizer (Stage C) | 10 | 0.479 ± 0.036 | 0.732 ± 0.027 | 0.9599 ± 0.0122 | 0.880 ± 0.018 | 0.634 ± 0.024 | 0.366 ± 0.066 |
| **v2-PE, new split, OLD tokenizer (Step 3b)** | 10 | 0.445 ± 0.095 | 0.718 ± 0.051 | 0.9486 ± 0.0111 | 0.872 ± 0.033 | 0.596 ± 0.067 | 0.328 ± 0.095 |
| ATT+bal, old validation slice (old split, 2 epochs) | 10 | 0.572 ± 0.061 | 0.795 ± 0.020 | 0.9713 ± 0.0066 | 0.913 ± 0.017 | 0.707 ± 0.017 | 0.457 ± 0.041 |
| ATT+bal, new split, NEW tokenizer (Stage C) | 10 | 0.503 ± 0.048 | 0.665 ± 0.064 | 0.9386 ± 0.0127 | 0.860 ± 0.033 | 0.590 ± 0.052 | 0.379 ± 0.063 |
| **ATT+bal, new split, OLD tokenizer (Step 3b)** | 10 | 0.535 ± 0.034 | 0.711 ± 0.027 | 0.9496 ± 0.0114 | 0.881 ± 0.026 | 0.627 ± 0.025 | 0.385 ± 0.048 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| v2-PE, old validation slice (old split, 2 epochs) | 0.606 | 0.851 | 0.9705 | 0.927 | **0.768** | 0.546 |
| v2-PE, new split, NEW tokenizer (Stage C) | 0.603 | 0.756 | 0.9668 | 0.899 | **0.689** | 0.529 |
| **v2-PE, new split, OLD tokenizer (Step 3b)** | 0.574 | 0.773 | 0.9580 | 0.905 | **0.683** | 0.439 |
| ATT+bal, old validation slice (old split, 2 epochs) | 0.583 | 0.814 | 0.9780 | 0.926 | **0.734** | 0.503 |
| ATT+bal, new split, NEW tokenizer (Stage C) | 0.537 | 0.711 | 0.9470 | 0.857 | **0.647** | 0.442 |
| **ATT+bal, new split, OLD tokenizer (Step 3b)** | 0.585 | 0.723 | 0.9566 | 0.904 | **0.653** | 0.442 |


(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)

### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| tk_v2pe − gs_v2pe | **pAUC@1e-2** | -3.78 | [-4.84, -2.75] | [-6.06, -1.41] | 4 up / 6 down | **RESOLVED worse** |
| tk_v2pe − gs_v2pe | TPR@1e-3 | -3.38 | [-8.19, -0.94] | [-9.28, +1.10] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| tk_v2pe − gs_v2pe | TPR@1e-2 | -1.42 | [-2.40, -0.57] | [-4.12, +1.18] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| tk_v2pe − gs_v2pe | AUC | -1.12 | [-1.21, -1.04] | [-2.11, -0.47] | 1 up / 9 down | cluster CI excludes 0 (descriptive) |
| tk_v2pe − old_v2pe | **pAUC@1e-2** | -10.88 | [-12.13, -9.53] | [-18.48, -4.68] | 0 up / 10 down | **RESOLVED worse** |
| tk_v2pe − old_v2pe | TPR@1e-3 | -9.78 | [-14.58, -7.64] | [-19.88, -2.81] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| tk_v2pe − old_v2pe | TPR@1e-2 | -9.31 | [-10.59, -8.25] | [-15.80, -3.91] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| tk_v2pe − old_v2pe | AUC | -1.58 | [-1.72, -1.44] | [-3.33, -0.40] | 1 up / 9 down | cluster CI excludes 0 (descriptive) |
| gs_v2pe − old_v2pe | **pAUC@1e-2** | -7.09 | [-8.33, -5.78] | [-14.90, -1.45] | 0 up / 10 down | **RESOLVED worse** |
| gs_v2pe − old_v2pe | TPR@1e-3 | -6.40 | [-9.96, -3.40] | [-15.12, -0.17] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| gs_v2pe − old_v2pe | TPR@1e-2 | -7.89 | [-9.02, -6.88] | [-15.32, -1.96] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| gs_v2pe − old_v2pe | AUC | -0.45 | [-0.59, -0.32] | [-1.76, +0.84] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| tk_attbal − gs_attbal | **pAUC@1e-2** | +3.68 | [+2.65, +4.63] | [+0.87, +6.64] | 5 up / 5 down | **RESOLVED better** |
| tk_attbal − gs_attbal | TPR@1e-3 | +3.17 | [-0.82, +4.98] | [-2.24, +6.74] | 9 up / 1 down | cluster CI contains 0 (descriptive) |
| tk_attbal − gs_attbal | TPR@1e-2 | +4.61 | [+3.05, +5.63] | [+1.40, +7.15] | 8 up / 2 down | cluster CI excludes 0 (descriptive) |
| tk_attbal − gs_attbal | AUC | +1.10 | [+1.00, +1.21] | [+0.05, +2.53] | 8 up / 2 down | cluster CI excludes 0 (descriptive) |
| tk_attbal − old_attbal | **pAUC@1e-2** | -8.00 | [-9.81, -6.12] | [-16.24, -1.45] | 0 up / 10 down | **RESOLVED worse** |
| tk_attbal − old_attbal | TPR@1e-3 | -3.72 | [-11.04, +0.55] | [-15.57, +4.43] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| tk_attbal − old_attbal | TPR@1e-2 | -8.31 | [-9.17, -7.50] | [-16.36, -1.93] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| tk_attbal − old_attbal | AUC | -2.17 | [-2.33, -1.98] | [-4.32, -0.70] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − old_attbal | **pAUC@1e-2** | -11.68 | [-13.56, -9.59] | [-19.68, -4.61] | 0 up / 10 down | **RESOLVED worse** |
| gs_attbal − old_attbal | TPR@1e-3 | -6.90 | [-13.53, -2.01] | [-17.82, +1.92] | 2 up / 8 down | cluster CI contains 0 (descriptive) |
| gs_attbal − old_attbal | TPR@1e-2 | -12.93 | [-14.17, -11.21] | [-20.10, -5.61] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − old_attbal | AUC | -3.27 | [-3.48, -3.04] | [-6.41, -0.96] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |
| tk_attbal − tk_v2pe | **pAUC@1e-2** | +3.10 | [+0.36, +5.53] | [-2.83, +8.47] | 6 up / 4 down | not resolved |
| tk_attbal − tk_v2pe | TPR@1e-3 | +8.97 | [+0.13, +14.21] | [-3.97, +17.93] | 9 up / 1 down | cluster CI contains 0 (descriptive) |
| tk_attbal − tk_v2pe | TPR@1e-2 | -0.65 | [-2.19, +0.78] | [-6.82, +5.15] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| tk_attbal − tk_v2pe | AUC | +0.10 | [-0.05, +0.24] | [-0.74, +1.09] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| gs_attbal − gs_v2pe | **pAUC@1e-2** | -4.36 | [-6.46, -2.15] | [-9.40, +0.81] | 3 up / 7 down | not resolved |
| gs_attbal − gs_v2pe | TPR@1e-3 | +2.42 | [-6.01, +8.09] | [-8.98, +10.96] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| gs_attbal − gs_v2pe | TPR@1e-2 | -6.68 | [-8.29, -4.77] | [-12.05, -1.35] | 2 up / 8 down | cluster CI excludes 0 (descriptive) |
| gs_attbal − gs_v2pe | AUC | -2.13 | [-2.32, -1.95] | [-4.31, -0.41] | 0 up / 10 down | cluster CI excludes 0 (descriptive) |


Ensemble pAUC@1e-2 differences (stratified bootstrap only):

| difference | ensemble pAUC@1e-2 difference | stratified 95% CI |
|---|---|---|
| tk_v2pe − gs_v2pe | -0.59 | [-2.04, +0.57] |
| tk_v2pe − old_v2pe | -8.54 | [-10.08, -7.02] |
| gs_v2pe − old_v2pe | -7.95 | [-9.25, -6.42] |
| tk_attbal − gs_attbal | +0.58 | [-0.38, +1.55] |
| tk_attbal − old_attbal | -8.10 | [-9.80, -6.11] |
| gs_attbal − old_attbal | -8.68 | [-10.58, -6.59] |
| tk_attbal − tk_v2pe | -2.98 | [-5.76, -0.10] |
| gs_attbal − gs_v2pe | -4.16 | [-6.28, -2.11] |


### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)

| family | n | v2-PE, old validation slice (old split, 2 epochs) | v2-PE, new split, NEW tokenizer (Stage C) | **v2-PE, new split, OLD tokenizer (Step 3b)** | ATT+bal, old validation slice (old split, 2 epochs) | ATT+bal, new split, NEW tokenizer (Stage C) | **ATT+bal, new split, OLD tokenizer (Step 3b)** |
|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 83.7 ± 2.4 | 81.5 ± 2.3 | 81.0 ± 3.1 | 82.1 ± 1.9 | 76.3 ± 7.7 | 79.0 ± 3.5 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 81.7 ± 6.8 | 76.7 ± 7.6 | 76.5 ± 8.6 | 72.8 ± 6.1 | 61.7 ± 6.8 | 68.2 ± 6.5 |
| dropper | 252 | 80.1 ± 2.4 | 73.7 ± 5.4 | 70.3 ± 7.4 | 81.9 ± 5.7 | 78.7 ± 6.3 | 82.7 ± 3.2 |
| keylogger | 1041 | 87.1 ± 6.1 | 70.3 ± 3.0 | 68.5 ± 7.8 | 87.0 ± 2.5 | 63.4 ± 6.6 | 68.4 ± 4.0 |
| ransomware | 2139 | 70.8 ± 4.9 | 68.2 ± 6.8 | 64.8 ± 11.5 | 72.9 ± 2.2 | 61.7 ± 6.8 | 67.1 ± 3.9 |
| rat | 1258 | 89.2 ± 2.0 | 76.5 ± 1.3 | 76.3 ± 6.6 | 87.8 ± 2.8 | 69.8 ± 11.2 | 76.5 ± 1.7 |
| trojan | 1085 | 80.9 ± 1.2 | 61.7 ± 5.6 | 60.1 ± 5.9 | 80.4 ± 2.5 | 62.4 ± 5.9 | 63.4 ± 1.8 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.3 ± 0.7 | 0.5 ± 0.8 |


### Change of the detection rate against the old-split models, per family (points; thresholds on the April benign scores)

| malware family | n | v2-PE gs − old (points) | v2-PE tk − old (points) | ATT+bal gs − old (points) | ATT+bal tk − old (points) |
|---|---|---|---|---|---|
| backdoor | 1940 | -2.1 | -2.7 | -5.8 | -3.1 |
| coinminer | 1684 | -5.1 | -5.2 | -11.2 | -4.6 |
| dropper | 252 | -6.4 | -9.8 | -3.2 | +0.8 |
| keylogger | 1041 | -16.8 | -18.6 | -23.6 | -18.6 |
| ransomware | 2139 | -2.6 | -6.0 | -11.2 | -5.8 |
| rat | 1258 | -12.7 | -12.9 | -17.9 | -11.3 |
| trojan | 1085 | -19.3 | -20.9 | -17.9 | -17.0 |

