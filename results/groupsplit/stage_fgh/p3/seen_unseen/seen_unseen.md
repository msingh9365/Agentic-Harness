### P2: April reports seen / unseen by each model's OWN training set (stored logits; pAUC@1e-2 and TPR@1e-2 computed within the subset; mean ± std over 10 seeds; 95% CI of the seed mean: stratified | cluster)

| model | training set of the model | April subset | reports / malware / benign / groups | pAUC@1e-2 | 95% CI (stratified \| cluster) | TPR@1e-2 | 95% CI (stratified \| cluster) |
|---|---|---|---|---|---|---|---|
| M1 v2-PE (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.793 ± 0.042 | [0.750, 0.838] | [0.685, 0.875] | 0.898 ± 0.034 | [0.881, 0.915] | [0.813, 0.941] |
| M3 ATT+bal (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.834 ± 0.022 | [0.790, 0.877] | [0.728, 0.909] | 0.912 ± 0.008 | [0.901, 0.926] | [0.841, 0.960] |
| M2 two-level, no padding (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.677 ± 0.126 | [0.586, 0.769] | [0.498, 0.818] | 0.900 ± 0.016 | [0.860, 0.918] | [0.731, 0.949] |
| M4 ATT+bal-2L (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.817 ± 0.026 | [0.774, 0.858] | [0.716, 0.889] | 0.899 ± 0.010 | [0.881, 0.916] | [0.823, 0.947] |
| M1 v2-PE + address roles | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.352 ± 0.155 | [0.332, 0.377] | [0.246, 0.473] | 0.404 ± 0.174 | [0.381, 0.437] | [0.284, 0.537] |
| M3 ATT+bal + address roles | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.063 ± 0.080 | [0.052, 0.077] | [0.029, 0.129] | 0.097 ± 0.119 | [0.088, 0.116] | [0.044, 0.200] |
| M1 v2-PE (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.617 ± 0.060 | [0.587, 0.649] | [0.455, 0.738] | 0.711 ± 0.051 | [0.691, 0.737] | [0.554, 0.824] |
| M3 ATT+bal (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.650 ± 0.017 | [0.622, 0.681] | [0.465, 0.771] | 0.721 ± 0.016 | [0.706, 0.740] | [0.549, 0.842] |
| M2 two-level, no padding (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.513 ± 0.160 | [0.470, 0.558] | [0.379, 0.643] | 0.673 ± 0.083 | [0.619, 0.707] | [0.499, 0.785] |
| M4 ATT+bal-2L (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.585 ± 0.050 | [0.533, 0.635] | [0.425, 0.703] | 0.717 ± 0.037 | [0.696, 0.733] | [0.561, 0.824] |
| M1 v2-PE + address roles | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.145 ± 0.069 | [0.129, 0.163] | [0.070, 0.252] | 0.195 ± 0.091 | [0.185, 0.209] | [0.102, 0.328] |
| M3 ATT+bal + address roles | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.052 ± 0.039 | [0.045, 0.060] | [0.015, 0.132] | 0.074 ± 0.051 | [0.065, 0.082] | [0.022, 0.189] |

### Pairwise differences inside a training-set group (points ×100; pAUC@1e-2 outcome by the cluster interval; TPR@1e-2 descriptive)

| difference | subset | pAUC diff | stratified CI | cluster CI | seeds | outcome | TPR@1e-2 diff | TPR CI (stratified \| cluster) |
|---|---|---|---|---|---|---|---|---|
| M2 two-level, no padding (final) − M1 v2-PE (final) | seen | -11.59 | [-17.91, -5.78] | [-21.61, -4.58] | 2 up / 8 down | **RESOLVED worse** | +0.19 | [-2.86, +1.19] | [-9.31, +2.17] |
| M4 ATT+bal-2L (final) − M3 ATT+bal (final) | seen | -1.77 | [-3.96, +0.90] | [-5.32, +2.73] | 4 up / 6 down | not resolved | -1.31 | [-2.57, -0.39] | [-3.51, +0.94] |
| M4 ATT+bal-2L (final) − M2 two-level, no padding (final) | seen | +13.95 | [+7.80, +20.26] | [+5.23, +25.01] | 10 up / 0 down | **RESOLVED better** | -0.13 | [-1.10, +2.75] | [-2.33, +13.43] |
| M3 ATT+bal (final) − M1 v2-PE (final) | seen | +4.13 | [+1.02, +7.31] | [-1.66, +10.08] | 9 up / 1 down | not resolved | +1.37 | [+0.29, +2.66] | [-2.81, +7.28] |
| M1 v2-PE + address roles − M1 v2-PE (final) | seen | -44.08 | [-48.72, -39.33] | [-55.62, -31.44] | 0 up / 10 down | **RESOLVED worse** | -49.46 | [-52.13, -45.99] | [-60.98, -35.69] |
| M3 ATT+bal + address roles − M3 ATT+bal (final) | seen | -77.13 | [-81.56, -72.52] | [-85.01, -65.72] | 0 up / 10 down | **RESOLVED worse** | -81.47 | [-83.13, -79.50] | [-88.59, -69.72] |
| M2 two-level, no padding (final) − M1 v2-PE (final) | unseen | -10.43 | [-13.61, -7.27] | [-16.40, -2.94] | 4 up / 6 down | **RESOLVED worse** | -3.82 | [-8.09, -1.52] | [-12.41, +1.45] |
| M4 ATT+bal-2L (final) − M3 ATT+bal (final) | unseen | -6.49 | [-10.85, -2.71] | [-13.62, +1.62] | 1 up / 9 down | not resolved | -0.42 | [-2.07, +0.56] | [-7.98, +9.40] |
| M4 ATT+bal-2L (final) − M2 two-level, no padding (final) | unseen | +7.26 | [+3.14, +11.11] | [-1.11, +13.74] | 6 up / 4 down | not resolved | +4.41 | [+1.73, +8.59] | [-1.42, +14.95] |
| M3 ATT+bal (final) − M1 v2-PE (final) | unseen | +3.31 | [+0.04, +6.12] | [-3.30, +9.39] | 6 up / 4 down | not resolved | +1.00 | [-0.87, +2.92] | [-6.32, +8.94] |
| M1 v2-PE + address roles − M1 v2-PE (final) | unseen | -47.22 | [-50.54, -44.12] | [-60.99, -28.51] | 0 up / 10 down | **RESOLVED worse** | -51.64 | [-54.00, -49.19] | [-65.48, -31.84] |
| M3 ATT+bal + address roles − M3 ATT+bal (final) | unseen | -59.86 | [-62.84, -57.03] | [-72.20, -39.56] | 0 up / 10 down | **RESOLVED worse** | -64.78 | [-66.79, -63.03] | [-77.94, -43.55] |
