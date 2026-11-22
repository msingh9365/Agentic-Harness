### P2: April reports seen / unseen by each model's OWN training set (stored logits; pAUC@1e-2 and TPR@1e-2 computed within the subset; mean ± std over 10 seeds; 95% CI of the seed mean: stratified | cluster)

| model | training set of the model | April subset | reports / malware / benign / groups | pAUC@1e-2 | 95% CI (stratified \| cluster) | TPR@1e-2 | 95% CI (stratified \| cluster) |
|---|---|---|---|---|---|---|---|
| M1 v2-PE (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.793 ± 0.042 | [0.750, 0.838] | [0.685, 0.875] | 0.898 ± 0.034 | [0.881, 0.915] | [0.813, 0.941] |
| M3 ATT+bal (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.834 ± 0.022 | [0.790, 0.877] | [0.728, 0.909] | 0.912 ± 0.008 | [0.901, 0.926] | [0.841, 0.960] |
| M2 two-level, no padding (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.677 ± 0.126 | [0.586, 0.769] | [0.498, 0.818] | 0.900 ± 0.016 | [0.860, 0.918] | [0.731, 0.949] |
| M4 ATT+bal-2L (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.817 ± 0.026 | [0.774, 0.858] | [0.716, 0.889] | 0.899 ± 0.010 | [0.881, 0.916] | [0.823, 0.947] |
| M1 v2-PE (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.617 ± 0.060 | [0.587, 0.649] | [0.455, 0.738] | 0.711 ± 0.051 | [0.691, 0.737] | [0.554, 0.824] |
| M3 ATT+bal (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.650 ± 0.017 | [0.622, 0.681] | [0.465, 0.771] | 0.721 ± 0.016 | [0.706, 0.740] | [0.549, 0.842] |
| M2 two-level, no padding (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.513 ± 0.160 | [0.470, 0.558] | [0.379, 0.643] | 0.673 ± 0.083 | [0.619, 0.707] | [0.499, 0.785] |
| M4 ATT+bal-2L (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.585 ± 0.050 | [0.533, 0.635] | [0.425, 0.703] | 0.717 ± 0.037 | [0.696, 0.733] | [0.561, 0.824] |
| Stage C v2-PE (group-split part) | group-split part (66,580) | seen | 5,667 / 2,535 / 3,132 / 521 | 0.787 ± 0.037 | [0.741, 0.826] | [0.665, 0.883] | 0.888 ± 0.024 | [0.866, 0.902] | [0.785, 0.942] |
| Stage C ATT+bal (group-split part) | group-split part (66,580) | seen | 5,667 / 2,535 / 3,132 / 521 | 0.757 ± 0.086 | [0.714, 0.796] | [0.629, 0.858] | 0.844 ± 0.094 | [0.814, 0.865] | [0.744, 0.925] |
| Stage C v2-PE (group-split part) | group-split part (66,580) | unseen | 11,735 / 6,864 / 4,871 / 1,988 | 0.574 ± 0.025 | [0.542, 0.603] | [0.417, 0.700] | 0.668 ± 0.032 | [0.650, 0.686] | [0.511, 0.787] |
| Stage C ATT+bal (group-split part) | group-split part (66,580) | unseen | 11,735 / 6,864 / 4,871 / 1,988 | 0.531 ± 0.039 | [0.505, 0.561] | [0.365, 0.662] | 0.610 ± 0.036 | [0.580, 0.632] | [0.433, 0.748] |
| old-split v2-PE | old training part (67,768) | seen | 6,208 / 2,908 / 3,300 / 611 | 0.825 ± 0.039 | [0.771, 0.871] | [0.698, 0.909] | 0.926 ± 0.022 | [0.912, 0.937] | [0.849, 0.961] |
| old-split ATT+bal | old training part (67,768) | seen | 6,208 / 2,908 / 3,300 / 611 | 0.832 ± 0.027 | [0.782, 0.872] | [0.712, 0.912] | 0.913 ± 0.030 | [0.901, 0.926] | [0.843, 0.958] |
| 2L A (old split) | old training part (67,768) | seen | 6,208 / 2,908 / 3,300 / 611 | 0.797 ± 0.029 | [0.727, 0.854] | [0.650, 0.893] | 0.917 ± 0.021 | [0.900, 0.928] | [0.838, 0.961] |
| 2L B, no padding (old split) | old training part (67,768) | seen | 6,208 / 2,908 / 3,300 / 611 | 0.749 ± 0.071 | [0.682, 0.811] | [0.597, 0.872] | 0.894 ± 0.038 | [0.871, 0.913] | [0.766, 0.952] |
| old-split v2-PE | old training part (67,768) | unseen | 11,194 / 6,491 / 4,703 / 1,898 | 0.650 ± 0.029 | [0.620, 0.682] | [0.489, 0.764] | 0.751 ± 0.029 | [0.724, 0.771] | [0.590, 0.847] |
| old-split ATT+bal | old training part (67,768) | unseen | 11,194 / 6,491 / 4,703 / 1,898 | 0.652 ± 0.021 | [0.616, 0.685] | [0.459, 0.776] | 0.734 ± 0.009 | [0.713, 0.751] | [0.547, 0.843] |
| 2L A (old split) | old training part (67,768) | unseen | 11,194 / 6,491 / 4,703 / 1,898 | 0.638 ± 0.024 | [0.597, 0.678] | [0.433, 0.771] | 0.747 ± 0.029 | [0.720, 0.770] | [0.569, 0.852] |
| 2L B, no padding (old split) | old training part (67,768) | unseen | 11,194 / 6,491 / 4,703 / 1,898 | 0.558 ± 0.060 | [0.516, 0.599] | [0.382, 0.694] | 0.670 ± 0.071 | [0.651, 0.698] | [0.506, 0.795] |

### Pairwise differences inside a training-set group (points ×100; pAUC@1e-2 outcome by the cluster interval; TPR@1e-2 descriptive)

| difference | subset | pAUC diff | stratified CI | cluster CI | seeds | outcome | TPR@1e-2 diff | TPR CI (stratified \| cluster) |
|---|---|---|---|---|---|---|---|---|
| M2 two-level, no padding (final) − M1 v2-PE (final) | seen | -11.59 | [-17.91, -5.78] | [-21.61, -4.58] | 2 up / 8 down | **RESOLVED worse** | +0.19 | [-2.86, +1.19] | [-9.31, +2.17] |
| M4 ATT+bal-2L (final) − M3 ATT+bal (final) | seen | -1.77 | [-3.96, +0.90] | [-5.32, +2.73] | 4 up / 6 down | not resolved | -1.31 | [-2.57, -0.39] | [-3.51, +0.94] |
| M4 ATT+bal-2L (final) − M2 two-level, no padding (final) | seen | +13.95 | [+7.80, +20.26] | [+5.23, +25.01] | 10 up / 0 down | **RESOLVED better** | -0.13 | [-1.10, +2.75] | [-2.33, +13.43] |
| M3 ATT+bal (final) − M1 v2-PE (final) | seen | +4.13 | [+1.02, +7.31] | [-1.66, +10.08] | 9 up / 1 down | not resolved | +1.37 | [+0.29, +2.66] | [-2.81, +7.28] |
| M2 two-level, no padding (final) − M1 v2-PE (final) | unseen | -10.43 | [-13.61, -7.27] | [-16.40, -2.94] | 4 up / 6 down | **RESOLVED worse** | -3.82 | [-8.09, -1.52] | [-12.41, +1.45] |
| M4 ATT+bal-2L (final) − M3 ATT+bal (final) | unseen | -6.49 | [-10.85, -2.71] | [-13.62, +1.62] | 1 up / 9 down | not resolved | -0.42 | [-2.07, +0.56] | [-7.98, +9.40] |
| M4 ATT+bal-2L (final) − M2 two-level, no padding (final) | unseen | +7.26 | [+3.14, +11.11] | [-1.11, +13.74] | 6 up / 4 down | not resolved | +4.41 | [+1.73, +8.59] | [-1.42, +14.95] |
| M3 ATT+bal (final) − M1 v2-PE (final) | unseen | +3.31 | [+0.04, +6.12] | [-3.30, +9.39] | 6 up / 4 down | not resolved | +1.00 | [-0.87, +2.92] | [-6.32, +8.94] |
| Stage C ATT+bal (group-split part) − Stage C v2-PE (group-split part) | seen | -2.97 | [-6.62, +0.91] | [-12.27, +5.36] | 5 up / 5 down | not resolved | -4.38 | [-6.94, -2.17] | [-11.42, +2.02] |
| Stage C ATT+bal (group-split part) − Stage C v2-PE (group-split part) | unseen | -4.25 | [-7.18, -1.55] | [-10.47, +1.55] | 1 up / 9 down | not resolved | -5.81 | [-8.53, -3.81] | [-14.09, -0.37] |
| old-split ATT+bal − old-split v2-PE | seen | +0.76 | [-1.54, +3.03] | [-4.44, +7.08] | 6 up / 4 down | not resolved | -1.28 | [-2.12, -0.33] | [-3.98, +2.62] |
| 2L A (old split) − old-split ATT+bal | seen | -3.57 | [-6.17, -1.43] | [-8.85, -0.23] | 2 up / 8 down | **RESOLVED worse** | +0.35 | [-0.51, +0.78] | [-1.78, +1.59] |
| 2L A (old split) − 2L B, no padding (old split) | seen | +4.73 | [+0.31, +8.81] | [-3.76, +14.14] | 6 up / 4 down | not resolved | +2.27 | [+0.75, +3.70] | [-1.32, +9.49] |
| 2L B, no padding (old split) − old-split v2-PE | seen | -7.55 | [-9.92, -5.26] | [-14.21, -2.28] | 2 up / 8 down | **RESOLVED worse** | -3.19 | [-4.81, -1.91] | [-8.97, -0.13] |
| old-split ATT+bal − old-split v2-PE | unseen | +0.23 | [-2.61, +2.68] | [-7.55, +5.42] | 5 up / 5 down | not resolved | -1.70 | [-3.50, +0.46] | [-10.76, +4.38] |
| 2L A (old split) − old-split ATT+bal | unseen | -1.40 | [-3.27, +0.27] | [-4.90, +1.56] | 3 up / 7 down | not resolved | +1.26 | [+0.01, +2.36] | [-1.36, +4.95] |
| 2L A (old split) − 2L B, no padding (old split) | unseen | +8.00 | [+4.19, +12.26] | [-4.51, +19.38] | 9 up / 1 down | not resolved | +7.71 | [+5.18, +9.52] | [-5.06, +16.63] |
| 2L B, no padding (old split) − old-split v2-PE | unseen | -9.17 | [-12.54, -6.03] | [-18.51, -1.66] | 0 up / 10 down | **RESOLVED worse** | -8.15 | [-9.70, -5.67] | [-15.69, +0.40] |
