### TEST: 8442 reports (5070 malicious, 3372 benign, 1245 hash_apis groups); 10 seeds each, per-seed mean ± std

| condition | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| (i) no pre-training | 10 | 0.345 ± 0.092 | 0.735 ± 0.029 | 0.9540 ± 0.0048 | 0.886 ± 0.022 | 0.601 ± 0.046 | 0.304 ± 0.079 |
| (ii) AR pre-training on January | 10 | 0.445 ± 0.141 | 0.695 ± 0.033 | 0.9485 ± 0.0105 | 0.876 ± 0.023 | 0.610 ± 0.036 | 0.300 ± 0.121 |
| (iii) AR pre-training on January + unlabelled ADAPT | 10 | 0.446 ± 0.113 | 0.692 ± 0.053 | 0.9520 ± 0.0128 | 0.878 ± 0.018 | 0.600 ± 0.036 | 0.353 ± 0.085 |


(TPR@1e-2 and TPR@1e-3 use thresholds set on each model's own TEST benign scores: the false-positive rate is true by construction.)

Differences on TEST (points x100; mean of the 10 per-seed differences; seeds paired by index only; **resolved = the CLUSTER interval of pAUC@1e-2 excludes 0**):

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| iii − ii | **pAUC@1e-2** | -1.08 | [-2.38, +0.28] | [-4.59, +2.60] | 5 up / 5 down | not resolved |
| iii − ii | TPR@1e-3 | +0.18 | [-5.91, +8.26] | [-7.53, +10.37] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| iii − ii | TPR@1e-2 | -0.29 | [-1.67, +0.92] | [-3.71, +2.49] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| iii − ii | AUC | +0.35 | [+0.25, +0.47] | [-0.27, +1.07] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| ii − i | **pAUC@1e-2** | +0.90 | [-2.23, +4.37] | [-5.20, +7.07] | 6 up / 4 down | not resolved |
| ii − i | TPR@1e-3 | +9.95 | [-6.16, +17.28] | [-9.32, +19.30] | 7 up / 3 down | cluster CI contains 0 (descriptive) |
| ii − i | TPR@1e-2 | -4.03 | [-5.18, -1.37] | [-8.12, +2.42] | 1 up / 9 down | cluster CI contains 0 (descriptive) |
| ii − i | AUC | -0.56 | [-0.78, -0.34] | [-2.27, +1.25] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| iii − i | **pAUC@1e-2** | -0.18 | [-3.60, +3.53] | [-6.81, +7.38] | 5 up / 5 down | not resolved |
| iii − i | TPR@1e-3 | +10.13 | [-5.79, +17.60] | [-9.05, +22.31] | 8 up / 2 down | cluster CI contains 0 (descriptive) |
| iii − i | TPR@1e-2 | -4.33 | [-5.37, -1.83] | [-7.92, +1.26] | 2 up / 8 down | cluster CI contains 0 (descriptive) |
| iii − i | AUC | -0.21 | [-0.42, +0.01] | [-1.84, +1.69] | 6 up / 4 down | cluster CI contains 0 (descriptive) |


### TEST-unseen: 5607 reports (3811 malicious, 1796 benign, 947 hash_apis groups); 10 seeds each, per-seed mean ± std

| condition | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| (i) no pre-training | 10 | 0.272 ± 0.086 | 0.693 ± 0.042 | 0.9439 ± 0.0062 | 0.879 ± 0.025 | 0.527 ± 0.061 | 0.241 ± 0.077 |
| (ii) AR pre-training on January | 10 | 0.289 ± 0.138 | 0.653 ± 0.060 | 0.9404 ± 0.0132 | 0.869 ± 0.029 | 0.555 ± 0.048 | 0.245 ± 0.124 |
| (iii) AR pre-training on January + unlabelled ADAPT | 10 | 0.298 ± 0.105 | 0.637 ± 0.068 | 0.9451 ± 0.0194 | 0.872 ± 0.023 | 0.543 ± 0.052 | 0.266 ± 0.103 |


(TPR@1e-2 and TPR@1e-3 use thresholds set on each model's own TEST benign scores: the false-positive rate is true by construction.)

Differences on TEST-unseen (points x100; mean of the 10 per-seed differences; seeds paired by index only; **resolved = the CLUSTER interval of pAUC@1e-2 excludes 0**):

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|
| iii − ii | **pAUC@1e-2** | -1.17 | [-2.91, +0.98] | [-5.37, +4.21] | 5 up / 5 down | not resolved |
| iii − ii | TPR@1e-3 | +0.91 | [-3.00, +9.51] | [-7.28, +11.85] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| iii − ii | TPR@1e-2 | -1.62 | [-3.77, +0.04] | [-6.41, +3.07] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| iii − ii | AUC | +0.47 | [+0.32, +0.63] | [-0.30, +1.64] | 5 up / 5 down | cluster CI contains 0 (descriptive) |
| ii − i | **pAUC@1e-2** | +2.83 | [-2.60, +9.08] | [-6.40, +12.59] | 7 up / 3 down | not resolved |
| ii − i | TPR@1e-3 | +1.67 | [-7.21, +18.02] | [-11.60, +23.84] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| ii − i | TPR@1e-2 | -3.93 | [-5.67, +1.37] | [-9.46, +4.48] | 4 up / 6 down | cluster CI contains 0 (descriptive) |
| ii − i | AUC | -0.35 | [-0.62, -0.05] | [-2.28, +1.57] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| iii − i | **pAUC@1e-2** | +1.66 | [-4.16, +8.13] | [-8.53, +13.98] | 6 up / 4 down | not resolved |
| iii − i | TPR@1e-3 | +2.58 | [-5.73, +21.93] | [-11.52, +27.32] | 6 up / 4 down | cluster CI contains 0 (descriptive) |
| iii − i | TPR@1e-2 | -5.54 | [-7.47, -1.25] | [-11.28, +4.23] | 3 up / 7 down | cluster CI contains 0 (descriptive) |
| iii − i | AUC | +0.12 | [-0.13, +0.42] | [-1.52, +2.41] | 7 up / 3 down | cluster CI contains 0 (descriptive) |


