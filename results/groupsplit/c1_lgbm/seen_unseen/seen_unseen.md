### P2: April reports seen / unseen by each model's OWN training set (stored logits; pAUC@1e-2 and TPR@1e-2 computed within the subset; mean ± std over 10 seeds; 95% CI of the seed mean: stratified | cluster)

| model | training set of the model | April subset | reports / malware / benign / groups | pAUC@1e-2 | 95% CI (stratified \| cluster) | TPR@1e-2 | 95% CI (stratified \| cluster) |
|---|---|---|---|---|---|---|---|
| M1 v2-PE (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.793 ± 0.042 | [0.750, 0.838] | [0.685, 0.875] | 0.898 ± 0.034 | [0.881, 0.915] | [0.813, 0.941] |
| M3 ATT+bal (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.834 ± 0.022 | [0.790, 0.877] | [0.728, 0.909] | 0.912 ± 0.008 | [0.901, 0.926] | [0.841, 0.960] |
| M2 two-level, no padding (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.677 ± 0.126 | [0.586, 0.769] | [0.498, 0.818] | 0.900 ± 0.016 | [0.860, 0.918] | [0.731, 0.949] |
| M4 ATT+bal-2L (final) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.817 ± 0.026 | [0.774, 0.858] | [0.716, 0.889] | 0.899 ± 0.010 | [0.881, 0.916] | [0.823, 0.947] |
| M1 v2-PE (fixed tokenizer) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.800 ± 0.038 | [0.757, 0.845] | [0.687, 0.884] | 0.903 ± 0.027 | [0.886, 0.919] | [0.823, 0.942] |
| M2 two-level, no padding (fixed tokenizer) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.716 ± 0.113 | [0.647, 0.788] | [0.564, 0.835] | 0.882 ± 0.048 | [0.857, 0.909] | [0.747, 0.939] |
| M3 ATT+bal (fixed tokenizer) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.824 ± 0.040 | [0.774, 0.873] | [0.714, 0.901] | 0.916 ± 0.009 | [0.902, 0.927] | [0.840, 0.960] |
| M4 ATT+bal-2L (fixed tokenizer) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.804 ± 0.050 | [0.763, 0.848] | [0.703, 0.884] | 0.899 ± 0.011 | [0.875, 0.915] | [0.817, 0.948] |
| LightGBM bag of API names (single model) | all January (75,298) | seen | 6,329 / 2,914 / 3,415 / 637 | 0.797 ± 0.000 | [0.781, 0.814] | [0.688, 0.880] | 0.820 ± 0.000 | [0.796, 0.835] | [0.706, 0.898] |
| M1 v2-PE (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.617 ± 0.060 | [0.587, 0.649] | [0.455, 0.738] | 0.711 ± 0.051 | [0.691, 0.737] | [0.554, 0.824] |
| M3 ATT+bal (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.650 ± 0.017 | [0.622, 0.681] | [0.465, 0.771] | 0.721 ± 0.016 | [0.706, 0.740] | [0.549, 0.842] |
| M2 two-level, no padding (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.513 ± 0.160 | [0.470, 0.558] | [0.379, 0.643] | 0.673 ± 0.083 | [0.619, 0.707] | [0.499, 0.785] |
| M4 ATT+bal-2L (final) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.585 ± 0.050 | [0.533, 0.635] | [0.425, 0.703] | 0.717 ± 0.037 | [0.696, 0.733] | [0.561, 0.824] |
| M1 v2-PE (fixed tokenizer) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.633 ± 0.029 | [0.603, 0.667] | [0.472, 0.754] | 0.729 ± 0.034 | [0.705, 0.753] | [0.574, 0.837] |
| M2 two-level, no padding (fixed tokenizer) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.577 ± 0.071 | [0.534, 0.619] | [0.428, 0.698] | 0.709 ± 0.049 | [0.686, 0.734] | [0.555, 0.815] |
| M3 ATT+bal (fixed tokenizer) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.650 ± 0.019 | [0.622, 0.679] | [0.460, 0.770] | 0.721 ± 0.018 | [0.704, 0.741] | [0.547, 0.843] |
| M4 ATT+bal-2L (fixed tokenizer) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.589 ± 0.040 | [0.537, 0.636] | [0.423, 0.710] | 0.724 ± 0.031 | [0.705, 0.740] | [0.555, 0.828] |
| LightGBM bag of API names (single model) | all January (75,298) | unseen | 11,073 / 6,485 / 4,588 / 1,872 | 0.327 ± 0.000 | [0.285, 0.370] | [0.137, 0.511] | 0.426 ± 0.000 | [0.410, 0.441] | [0.195, 0.632] |

### Pairwise differences inside a training-set group (points ×100; pAUC@1e-2 outcome by the cluster interval; TPR@1e-2 descriptive)

| difference | subset | pAUC diff | stratified CI | cluster CI | seeds | outcome | TPR@1e-2 diff | TPR CI (stratified \| cluster) |
|---|---|---|---|---|---|---|---|---|
| M2 two-level, no padding (final) − M1 v2-PE (final) | seen | -11.59 | [-17.91, -5.78] | [-21.61, -4.58] | 2 up / 8 down | **RESOLVED worse** | +0.19 | [-2.86, +1.19] | [-9.31, +2.17] |
| M4 ATT+bal-2L (final) − M3 ATT+bal (final) | seen | -1.77 | [-3.96, +0.90] | [-5.32, +2.73] | 4 up / 6 down | not resolved | -1.31 | [-2.57, -0.39] | [-3.51, +0.94] |
| M4 ATT+bal-2L (final) − M2 two-level, no padding (final) | seen | +13.95 | [+7.80, +20.26] | [+5.23, +25.01] | 10 up / 0 down | **RESOLVED better** | -0.13 | [-1.10, +2.75] | [-2.33, +13.43] |
| M3 ATT+bal (final) − M1 v2-PE (final) | seen | +4.13 | [+1.02, +7.31] | [-1.66, +10.08] | 9 up / 1 down | not resolved | +1.37 | [+0.29, +2.66] | [-2.81, +7.28] |
| M1 v2-PE (fixed tokenizer) − M1 v2-PE (final) | seen | +0.73 | [-0.01, +1.42] | [-1.30, +2.46] | 4 up / 6 down | not resolved | +0.46 | [-0.20, +1.13] | [-1.50, +2.85] |
| M2 two-level, no padding (fixed tokenizer) − M2 two-level, no padding (final) | seen | +3.91 | [+0.62, +7.29] | [+0.59, +8.66] | 6 up / 4 down | **RESOLVED better** | -1.77 | [-2.30, +0.38] | [-4.02, +3.67] |
| M3 ATT+bal (fixed tokenizer) − M3 ATT+bal (final) | seen | -1.03 | [-2.12, -0.10] | [-2.74, +0.08] | 5 up / 5 down | not resolved | +0.41 | [-0.24, +0.47] | [-0.90, +0.96] |
| M4 ATT+bal-2L (fixed tokenizer) − M4 ATT+bal-2L (final) | seen | -1.26 | [-2.84, +0.28] | [-4.12, +1.07] | 5 up / 5 down | not resolved | -0.04 | [-1.12, +0.66] | [-2.97, +1.24] |
| M3 ATT+bal (fixed tokenizer) − M1 v2-PE (fixed tokenizer) | seen | +2.38 | [-0.90, +5.49] | [-4.05, +8.72] | 5 up / 5 down | not resolved | +1.32 | [-0.08, +2.37] | [-3.08, +6.29] |
| M4 ATT+bal-2L (fixed tokenizer) − M3 ATT+bal (fixed tokenizer) | seen | -2.01 | [-4.53, +0.62] | [-6.34, +3.10] | 4 up / 6 down | not resolved | -1.76 | [-3.35, -0.47] | [-5.48, +0.90] |
| M4 ATT+bal-2L (fixed tokenizer) − M2 two-level, no padding (fixed tokenizer) | seen | +8.78 | [+4.73, +13.15] | [+2.06, +17.03] | 6 up / 4 down | **RESOLVED better** | +1.61 | [-0.01, +2.78] | [-0.88, +11.50] |
| LightGBM bag of API names (single model) − M3 ATT+bal (fixed tokenizer) | seen | -2.72 | [-7.55, +2.27] | [-11.28, +8.76] | 3 up / 7 down | not resolved | -9.60 | [-11.80, -8.01] | [-17.42, -3.03] |
| LightGBM bag of API names (single model) − M1 v2-PE (fixed tokenizer) | seen | -0.34 | [-4.79, +4.02] | [-10.66, +10.71] | 5 up / 5 down | not resolved | -8.28 | [-10.67, -6.51] | [-17.72, +0.32] |
| M2 two-level, no padding (final) − M1 v2-PE (final) | unseen | -10.43 | [-13.61, -7.27] | [-16.40, -2.94] | 4 up / 6 down | **RESOLVED worse** | -3.82 | [-8.09, -1.52] | [-12.41, +1.45] |
| M4 ATT+bal-2L (final) − M3 ATT+bal (final) | unseen | -6.49 | [-10.85, -2.71] | [-13.62, +1.62] | 1 up / 9 down | not resolved | -0.42 | [-2.07, +0.56] | [-7.98, +9.40] |
| M4 ATT+bal-2L (final) − M2 two-level, no padding (final) | unseen | +7.26 | [+3.14, +11.11] | [-1.11, +13.74] | 6 up / 4 down | not resolved | +4.41 | [+1.73, +8.59] | [-1.42, +14.95] |
| M3 ATT+bal (final) − M1 v2-PE (final) | unseen | +3.31 | [+0.04, +6.12] | [-3.30, +9.39] | 6 up / 4 down | not resolved | +1.00 | [-0.87, +2.92] | [-6.32, +8.94] |
| M1 v2-PE (fixed tokenizer) − M1 v2-PE (final) | unseen | +1.62 | [+0.69, +2.54] | [-1.80, +5.46] | 6 up / 4 down | not resolved | +1.80 | [+0.55, +2.89] | [-2.00, +5.41] |
| M2 two-level, no padding (fixed tokenizer) − M2 two-level, no padding (final) | unseen | +6.44 | [+4.73, +7.90] | [+2.85, +9.68] | 6 up / 4 down | **RESOLVED better** | +3.56 | [+1.73, +7.21] | [-0.05, +10.97] |
| M3 ATT+bal (fixed tokenizer) − M3 ATT+bal (final) | unseen | -0.07 | [-0.60, +0.40] | [-1.04, +0.69] | 6 up / 4 down | not resolved | -0.08 | [-0.71, +0.55] | [-1.36, +1.03] |
| M4 ATT+bal-2L (fixed tokenizer) − M4 ATT+bal-2L (final) | unseen | +0.32 | [-1.20, +1.92] | [-2.52, +3.00] | 5 up / 5 down | not resolved | +0.63 | [+0.13, +1.39] | [-1.82, +2.29] |
| M3 ATT+bal (fixed tokenizer) − M1 v2-PE (fixed tokenizer) | unseen | +1.62 | [-1.55, +4.53] | [-5.54, +7.25] | 7 up / 3 down | not resolved | -0.87 | [-2.64, +1.35] | [-8.57, +5.78] |
| M4 ATT+bal-2L (fixed tokenizer) − M3 ATT+bal (fixed tokenizer) | unseen | -6.10 | [-10.17, -2.58] | [-13.21, +1.95] | 0 up / 10 down | not resolved | +0.29 | [-1.26, +1.56] | [-8.21, +10.37] |
| M4 ATT+bal-2L (fixed tokenizer) − M2 two-level, no padding (fixed tokenizer) | unseen | +1.14 | [-2.23, +4.32] | [-5.50, +6.81] | 5 up / 5 down | not resolved | +1.47 | [-0.16, +3.13] | [-2.83, +5.95] |
| LightGBM bag of API names (single model) − M3 ATT+bal (fixed tokenizer) | unseen | -32.29 | [-37.24, -27.65] | [-50.58, -12.38] | 0 up / 10 down | **RESOLVED worse** | -29.49 | [-31.76, -27.62] | [-50.19, -9.50] |
| LightGBM bag of API names (single model) − M1 v2-PE (fixed tokenizer) | unseen | -30.67 | [-34.99, -26.58] | [-48.57, -12.04] | 0 up / 10 down | **RESOLVED worse** | -30.36 | [-32.85, -28.00] | [-50.18, -9.37] |
