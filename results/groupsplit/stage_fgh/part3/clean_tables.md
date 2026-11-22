### Part 3: clean April results of the test-time variants next to the final M1 and M3 (corrected tokenizer, 10 seeds; descriptive; F1 = fixed threshold 0 on the logit)

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| M1 Nebula (final) | 10 | 0.536 ± 0.060 | 0.791 ± 0.020 | 0.9639 ± 0.0111 | 0.891 ± 0.027 | 0.686 ± 0.026 | 0.398 ± 0.095 |
| M1 Nebula + dedupe (exact repeats) | 10 | 0.532 ± 0.060 | 0.791 ± 0.019 | 0.9637 ± 0.0111 | 0.892 ± 0.027 | 0.684 ± 0.028 | 0.391 ± 0.102 |
| M1 Nebula + dedupe (same API name) | 10 | 0.335 ± 0.041 | 0.577 ± 0.047 | 0.9318 ± 0.0165 | 0.785 ± 0.043 | 0.457 ± 0.046 | 0.232 ± 0.063 |
| M1 Nebula + multi-window max | 10 | 0.257 ± 0.091 | 0.610 ± 0.108 | 0.9379 ± 0.0147 | 0.866 ± 0.022 | 0.476 ± 0.088 | 0.164 ± 0.089 |
| M3 ATT+bal (final) | 10 | 0.567 ± 0.047 | 0.790 ± 0.019 | 0.9693 ± 0.0065 | 0.913 ± 0.011 | 0.705 ± 0.025 | 0.443 ± 0.089 |
| M3 ATT+bal + dedupe (exact repeats) | 10 | 0.568 ± 0.048 | 0.791 ± 0.018 | 0.9693 ± 0.0067 | 0.913 ± 0.011 | 0.705 ± 0.026 | 0.442 ± 0.089 |
| M3 ATT+bal + dedupe (same API name) | 10 | 0.440 ± 0.041 | 0.646 ± 0.033 | 0.9119 ± 0.0090 | 0.848 ± 0.014 | 0.554 ± 0.022 | 0.343 ± 0.071 |
| M3 ATT+bal + multi-window max | 10 | 0.441 ± 0.084 | 0.718 ± 0.033 | 0.9230 ± 0.0070 | 0.793 ± 0.007 | 0.594 ± 0.038 | 0.310 ± 0.084 |


10-seed ensembles:

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 (threshold 0) | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| M1 Nebula (final) | 0.663 | 0.837 | 0.9705 | 0.913 | **0.756** | 0.552 |
| M1 Nebula + dedupe (exact repeats) | 0.663 | 0.839 | 0.9703 | 0.914 | **0.755** | 0.551 |
| M1 Nebula + dedupe (same API name) | 0.405 | 0.627 | 0.9571 | 0.780 | **0.524** | 0.283 |
| M1 Nebula + multi-window max | 0.565 | 0.718 | 0.9541 | 0.874 | **0.632** | 0.239 |
| M3 ATT+bal (final) | 0.597 | 0.800 | 0.9752 | 0.919 | **0.730** | 0.532 |
| M3 ATT+bal + dedupe (exact repeats) | 0.597 | 0.801 | 0.9751 | 0.919 | **0.730** | 0.531 |
| M3 ATT+bal + dedupe (same API name) | 0.470 | 0.697 | 0.9193 | 0.865 | **0.581** | 0.405 |
| M3 ATT+bal + multi-window max | 0.494 | 0.740 | 0.9322 | 0.795 | **0.650** | 0.417 |


### Paired differences variant - final model (points ×100; stratified and cluster 95% CI; seeds paired by index)

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome (pAUC only) |
|---|---|---|---|---|---|---|
| M1 Nebula + dedupe (exact repeats) − M1 Nebula (final) | **pAUC@1e-2** | -0.23 | [-0.45, -0.04] | [-0.56, +0.02] | 1 up / 9 down | not resolved |
| M1 Nebula + dedupe (exact repeats) − M1 Nebula (final) | TPR@1e-3 | -0.48 | [-2.11, +0.80] | [-2.56, +1.09] | 4 up / 6 down |  |
| M1 Nebula + dedupe (exact repeats) − M1 Nebula (final) | TPR@1e-2 | -0.04 | [-0.43, +0.13] | [-0.82, +0.17] | 4 up / 5 down |  |
| M1 Nebula + dedupe (exact repeats) − M1 Nebula (final) | AUC | -0.02 | [-0.03, -0.01] | [-0.04, +0.00] | 2 up / 8 down |  |
| M1 Nebula + dedupe (same API name) − M1 Nebula (final) | **pAUC@1e-2** | -22.90 | [-24.52, -21.11] | [-35.13, -12.85] | 0 up / 10 down | **resolved** |
| M1 Nebula + dedupe (same API name) − M1 Nebula (final) | TPR@1e-3 | -20.13 | [-26.07, -15.43] | [-32.24, -7.33] | 0 up / 10 down |  |
| M1 Nebula + dedupe (same API name) − M1 Nebula (final) | TPR@1e-2 | -21.49 | [-23.46, -20.39] | [-36.43, -10.92] | 0 up / 10 down |  |
| M1 Nebula + dedupe (same API name) − M1 Nebula (final) | AUC | -3.21 | [-3.38, -3.04] | [-5.82, -1.56] | 0 up / 10 down |  |
| M1 Nebula + multi-window max − M1 Nebula (final) | **pAUC@1e-2** | -21.05 | [-24.63, -17.74] | [-27.89, -14.68] | 0 up / 10 down | **resolved** |
| M1 Nebula + multi-window max − M1 Nebula (final) | TPR@1e-3 | -27.91 | [-38.56, -17.55] | [-43.13, -14.59] | 0 up / 10 down |  |
| M1 Nebula + multi-window max − M1 Nebula (final) | TPR@1e-2 | -18.11 | [-19.71, -16.60] | [-23.63, -12.52] | 0 up / 10 down |  |
| M1 Nebula + multi-window max − M1 Nebula (final) | AUC | -2.59 | [-2.84, -2.37] | [-4.54, -1.08] | 1 up / 9 down |  |
| M3 ATT+bal + dedupe (exact repeats) − M3 ATT+bal (final) | **pAUC@1e-2** | +0.06 | [-0.02, +0.15] | [-0.06, +0.22] | 7 up / 3 down | not resolved |
| M3 ATT+bal + dedupe (exact repeats) − M3 ATT+bal (final) | TPR@1e-3 | +0.17 | [-0.20, +0.68] | [-0.20, +0.87] | 4 up / 6 down |  |
| M3 ATT+bal + dedupe (exact repeats) − M3 ATT+bal (final) | TPR@1e-2 | +0.03 | [-0.07, +0.22] | [-0.10, +0.33] | 6 up / 4 down |  |
| M3 ATT+bal + dedupe (exact repeats) − M3 ATT+bal (final) | AUC | -0.00 | [-0.01, +0.00] | [-0.02, +0.01] | 4 up / 6 down |  |
| M3 ATT+bal + dedupe (same API name) − M3 ATT+bal (final) | **pAUC@1e-2** | -15.10 | [-16.33, -13.87] | [-27.07, -4.31] | 0 up / 10 down | **resolved** |
| M3 ATT+bal + dedupe (same API name) − M3 ATT+bal (final) | TPR@1e-3 | -12.68 | [-16.21, -9.55] | [-21.34, -5.41] | 0 up / 10 down |  |
| M3 ATT+bal + dedupe (same API name) − M3 ATT+bal (final) | TPR@1e-2 | -14.45 | [-15.73, -13.37] | [-26.94, -2.68] | 0 up / 10 down |  |
| M3 ATT+bal + dedupe (same API name) − M3 ATT+bal (final) | AUC | -5.74 | [-6.02, -5.46] | [-9.77, -3.04] | 0 up / 10 down |  |
| M3 ATT+bal + multi-window max − M3 ATT+bal (final) | **pAUC@1e-2** | -11.03 | [-13.68, -8.69] | [-17.59, -5.62] | 0 up / 10 down | **resolved** |
| M3 ATT+bal + multi-window max − M3 ATT+bal (final) | TPR@1e-3 | -12.53 | [-17.88, -7.50] | [-20.88, -4.96] | 0 up / 10 down |  |
| M3 ATT+bal + multi-window max − M3 ATT+bal (final) | TPR@1e-2 | -7.25 | [-9.21, -6.03] | [-12.55, -3.85] | 0 up / 10 down |  |
| M3 ATT+bal + multi-window max − M3 ATT+bal (final) | AUC | -4.63 | [-4.93, -4.35] | [-8.26, -2.12] | 0 up / 10 down |  |


### Calls removed (dedupe) or windows (multi-window), April reports, median [mean] per report; first-512 total / token count of the edited report

| variant | edit set | malware: removed calls / windows | malware: total tokens / note | benign: removed calls / windows | benign: total tokens / note |
|---|---|---|---|---|---|
| M1 Nebula + dedupe (exact repeats) | unedited | 0 [6.1] | 994 | 0 [1.5] | 1008 |
| M1 Nebula + dedupe (exact repeats) | random_20_prepend | 0 [6.2] | 1122 | 0 [1.5] | 1135 |
| M1 Nebula + dedupe (exact repeats) | random_50_prepend | 1 [6.2] | 1312 | 0 [1.6] | 1314 |
| M1 Nebula + dedupe (exact repeats) | random_100_prepend | 1 [6.3] | 1624 | 0 [1.7] | 1615 |
| M1 Nebula + dedupe (exact repeats) | lgbm_50_prepend | 0 [6.1] | 1396 | 0 [1.5] | 1410 |
| M1 Nebula + dedupe (same API name) | unedited | 53 [71.2] | 576 | 59 [63.1] | 507 |
| M1 Nebula + dedupe (same API name) | random_20_prepend | 54 [71.9] | 700 | 60 [63.8] | 625 |
| M1 Nebula + dedupe (same API name) | random_50_prepend | 56 [73.0] | 881 | 61 [64.9] | 803 |
| M1 Nebula + dedupe (same API name) | random_100_prepend | 58 [74.8] | 1173 | 64 [66.7] | 1097 |
| M1 Nebula + dedupe (same API name) | lgbm_50_prepend | 53 [71.3] | 978 | 59 [63.2] | 909 |
| M1 Nebula + multi-window max | unedited | 2 [2.82] | 0.00% > 64 windows; arg-max window 0 in 83.2% | 2 [2.48] | 0.00% > 64 windows; arg-max window 0 in 44.9% |
| M1 Nebula + multi-window max | random_20_prepend | 3 [2.94] | 0.00% > 64 windows; arg-max window 0 in 53.0% | 3 [2.62] | 0.00% > 64 windows; arg-max window 0 in 43.3% |
| M1 Nebula + multi-window max | random_50_prepend | 3 [3.29] | 0.00% > 64 windows; arg-max window 0 in 28.5% | 3 [2.87] | 0.00% > 64 windows; arg-max window 0 in 44.3% |
| M1 Nebula + multi-window max | random_100_prepend | 4 [3.92] | 0.00% > 64 windows; arg-max window 0 in 15.4% | 4 [3.61] | 0.00% > 64 windows; arg-max window 0 in 37.0% |
| M1 Nebula + multi-window max | lgbm_50_prepend | 3 [3.51] | 0.00% > 64 windows; arg-max window 0 in 15.2% | 3 [3.14] | 0.00% > 64 windows; arg-max window 0 in 25.9% |
| M3 ATT+bal + dedupe (exact repeats) | unedited | 0 [6.1] | 994 | 0 [1.5] | 1008 |
| M3 ATT+bal + dedupe (exact repeats) | random_20_prepend | 0 [6.2] | 1122 | 0 [1.5] | 1135 |
| M3 ATT+bal + dedupe (exact repeats) | random_50_prepend | 1 [6.2] | 1312 | 0 [1.6] | 1314 |
| M3 ATT+bal + dedupe (exact repeats) | random_100_prepend | 1 [6.3] | 1624 | 0 [1.7] | 1615 |
| M3 ATT+bal + dedupe (exact repeats) | lgbm_50_prepend | 0 [6.1] | 1396 | 0 [1.5] | 1410 |
| M3 ATT+bal + dedupe (same API name) | unedited | 53 [71.2] | 576 | 59 [63.1] | 507 |
| M3 ATT+bal + dedupe (same API name) | random_20_prepend | 54 [71.9] | 700 | 60 [63.8] | 625 |
| M3 ATT+bal + dedupe (same API name) | random_50_prepend | 56 [73.0] | 881 | 61 [64.9] | 803 |
| M3 ATT+bal + dedupe (same API name) | random_100_prepend | 58 [74.8] | 1173 | 64 [66.7] | 1097 |
| M3 ATT+bal + dedupe (same API name) | lgbm_50_prepend | 53 [71.3] | 978 | 59 [63.2] | 909 |
| M3 ATT+bal + multi-window max | unedited | 2 [2.82] | 0.00% > 64 windows; arg-max window 0 in 74.1% | 2 [2.48] | 0.00% > 64 windows; arg-max window 0 in 44.5% |
| M3 ATT+bal + multi-window max | random_20_prepend | 3 [2.94] | 0.00% > 64 windows; arg-max window 0 in 66.2% | 3 [2.62] | 0.00% > 64 windows; arg-max window 0 in 41.1% |
| M3 ATT+bal + multi-window max | random_50_prepend | 3 [3.29] | 0.00% > 64 windows; arg-max window 0 in 32.5% | 3 [2.87] | 0.00% > 64 windows; arg-max window 0 in 33.3% |
| M3 ATT+bal + multi-window max | random_100_prepend | 4 [3.92] | 0.00% > 64 windows; arg-max window 0 in 0.4% | 4 [3.61] | 0.00% > 64 windows; arg-max window 0 in 8.7% |
| M3 ATT+bal + multi-window max | lgbm_50_prepend | 3 [3.51] | 0.00% > 64 windows; arg-max window 0 in 15.5% | 3 [3.14] | 0.00% > 64 windows; arg-max window 0 in 26.5% |


