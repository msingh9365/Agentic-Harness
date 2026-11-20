### Clean April test: per-seed mean ± std (10 seeds, logit-ranked)

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| **A2: ATT+bal-2L, round 2** | 10 | 0.554 ± 0.070 | 0.791 ± 0.025 | 0.9694 ± 0.0071 | 0.912 ± 0.023 | 0.699 ± 0.019 | 0.390 ± 0.074 |
| B2: 2L without padding, round 2 | 10 | 0.374 ± 0.109 | 0.774 ± 0.014 | 0.9692 ± 0.0067 | 0.908 ± 0.010 | 0.627 ± 0.046 | 0.266 ± 0.080 |
| A: ATT+bal-2L (19.12) | 10 | 0.506 ± 0.077 | 0.804 ± 0.019 | 0.9614 ± 0.0074 | 0.912 ± 0.015 | 0.687 ± 0.017 | 0.343 ± 0.066 |
| B: 2L without padding (19.12) | 10 | 0.409 ± 0.116 | 0.748 ± 0.046 | 0.9684 ± 0.0058 | 0.897 ± 0.010 | 0.616 ± 0.062 | 0.284 ± 0.117 |
| ATT+bal | 10 | 0.572 ± 0.061 | 0.795 ± 0.020 | 0.9713 ± 0.0066 | 0.913 ± 0.017 | 0.707 ± 0.017 | 0.457 ± 0.041 |
| v2-PE | 10 | 0.543 ± 0.063 | 0.811 ± 0.023 | 0.9644 ± 0.0093 | 0.915 ± 0.012 | 0.705 ± 0.031 | 0.444 ± 0.076 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| **A2: ATT+bal-2L, round 2** | 0.572 | 0.817 | 0.9765 | 0.919 | **0.732** | 0.477 |
| B2: 2L without padding, round 2 | 0.581 | 0.793 | 0.9745 | 0.917 | **0.694** | 0.382 |
| A: ATT+bal-2L (19.12) | 0.618 | 0.847 | 0.9711 | 0.922 | **0.736** | 0.485 |
| B: 2L without padding (19.12) | 0.511 | 0.795 | 0.9741 | 0.902 | **0.689** | 0.399 |
| ATT+bal | 0.583 | 0.814 | 0.9780 | 0.926 | **0.734** | 0.503 |
| v2-PE | 0.606 | 0.851 | 0.9705 | 0.927 | **0.768** | 0.546 |


Validation slice (7,530 reports, clean; no validation logits are kept for ATT+bal): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| **A2: ATT+bal-2L, round 2** | 10 | 0.896 ± 0.058 | 0.982 ± 0.003 | 0.9982 ± 0.0002 | 0.990 ± 0.001 | 0.950 ± 0.014 | 0.828 ± 0.108 |
| B2: 2L without padding, round 2 | 10 | 0.898 ± 0.028 | 0.983 ± 0.002 | 0.9983 ± 0.0002 | 0.989 ± 0.001 | 0.953 ± 0.008 | 0.857 ± 0.045 |
| A: ATT+bal-2L (19.12) | 10 | 0.866 ± 0.078 | 0.981 ± 0.002 | 0.9975 ± 0.0009 | 0.990 ± 0.001 | 0.944 ± 0.016 | 0.793 ± 0.120 |
| B: 2L without padding (19.12) | 10 | 0.919 ± 0.035 | 0.986 ± 0.002 | 0.9985 ± 0.0002 | 0.990 ± 0.001 | 0.958 ± 0.010 | 0.832 ± 0.088 |
| v2-PE | 10 | 0.916 ± 0.060 | 0.984 ± 0.004 | 0.9985 ± 0.0002 | 0.990 ± 0.002 | 0.962 ± 0.013 | 0.858 ± 0.098 |


### Differences, stratified bootstrap (1000 resamples, numpy seed 0; points ×100; same resamples for all models)

| difference | statistic | metric | difference in points, 95% CI |
|---|---|---|---|
| a2r2 − attbal | per-seed means | **pAUC@1e-2** | -0.83 [-1.65, -0.23] **CI excludes 0** |
| a2r2 − attbal | per-seed means | TPR@1e-3 | -1.76 [-5.97, +0.64] CI contains 0 |
| a2r2 − attbal | per-seed means | TPR@1e-2 | -0.32 [-0.60, +0.16] CI contains 0 |
| a2r2 − attbal | per-seed means | AUC | -0.18 [-0.22, -0.15] **CI excludes 0** |
| a2r2 − attbal | per-seed means | pAUC@1e-3 | -6.66 [-12.08, -2.10] **CI excludes 0** |
| a2r2 − attbal | 10-seed ensembles | **pAUC@1e-2** | -0.20 [-1.10, +0.44] CI contains 0 |
| a2r2 − attbal | 10-seed ensembles | TPR@1e-3 | -1.09 [-6.97, +4.24] CI contains 0 |
| a2r2 − attbal | 10-seed ensembles | TPR@1e-2 | +0.31 [-0.28, +0.84] CI contains 0 |
| a2r2 − attbal | 10-seed ensembles | AUC | -0.15 [-0.18, -0.12] **CI excludes 0** |
| a2r2 − attbal | 10-seed ensembles | pAUC@1e-3 | -2.60 [-9.82, +2.86] CI contains 0 |
| a2r2 − v2_pe | per-seed means | **pAUC@1e-2** | -0.60 [-2.98, +1.50] CI contains 0 |
| a2r2 − v2_pe | per-seed means | TPR@1e-3 | +1.16 [-6.62, +6.12] CI contains 0 |
| a2r2 − v2_pe | per-seed means | TPR@1e-2 | -1.97 [-3.14, -0.94] **CI excludes 0** |
| a2r2 − v2_pe | per-seed means | AUC | +0.50 [+0.39, +0.61] **CI excludes 0** |
| a2r2 − v2_pe | per-seed means | pAUC@1e-3 | -5.34 [-15.68, +4.69] CI contains 0 |
| a2r2 − v2_pe | 10-seed ensembles | **pAUC@1e-2** | -3.62 [-6.03, -1.48] **CI excludes 0** |
| a2r2 − v2_pe | 10-seed ensembles | TPR@1e-3 | -3.37 [-8.33, +7.78] CI contains 0 |
| a2r2 − v2_pe | 10-seed ensembles | TPR@1e-2 | -3.44 [-4.39, -2.03] **CI excludes 0** |
| a2r2 − v2_pe | 10-seed ensembles | AUC | +0.60 [+0.48, +0.72] **CI excludes 0** |
| a2r2 − v2_pe | 10-seed ensembles | pAUC@1e-3 | -6.95 [-20.53, +3.50] CI contains 0 |
| a2r2 − b2r2 | per-seed means | **pAUC@1e-2** | +7.17 [+3.91, +10.64] **CI excludes 0** |
| a2r2 − b2r2 | per-seed means | TPR@1e-3 | +18.02 [+7.83, +26.72] **CI excludes 0** |
| a2r2 − b2r2 | per-seed means | TPR@1e-2 | +1.70 [+0.59, +3.80] **CI excludes 0** |
| a2r2 − b2r2 | per-seed means | AUC | +0.02 [-0.10, +0.14] CI contains 0 |
| a2r2 − b2r2 | per-seed means | pAUC@1e-3 | +12.48 [+0.15, +24.43] **CI excludes 0** |
| a2r2 − b2r2 | 10-seed ensembles | **pAUC@1e-2** | +3.81 [+0.36, +7.60] **CI excludes 0** |
| a2r2 − b2r2 | 10-seed ensembles | TPR@1e-3 | -0.86 [-4.33, +22.43] CI contains 0 |
| a2r2 − b2r2 | 10-seed ensembles | TPR@1e-2 | +2.40 [+1.24, +3.77] **CI excludes 0** |
| a2r2 − b2r2 | 10-seed ensembles | AUC | +0.20 [+0.08, +0.33] **CI excludes 0** |
| a2r2 − b2r2 | 10-seed ensembles | pAUC@1e-3 | +9.43 [-10.33, +30.29] CI contains 0 |
| a2r2 − a2l | per-seed means | **pAUC@1e-2** | +1.16 [-0.05, +2.42] CI contains 0 |
| a2r2 − a2l | per-seed means | TPR@1e-3 | +4.87 [+0.45, +10.15] **CI excludes 0** |
| a2r2 − a2l | per-seed means | TPR@1e-2 | -1.28 [-1.98, -0.54] **CI excludes 0** |
| a2r2 − a2l | per-seed means | AUC | +0.81 [+0.73, +0.88] **CI excludes 0** |
| a2r2 − a2l | per-seed means | pAUC@1e-3 | +4.71 [-1.61, +10.61] CI contains 0 |
| a2r2 − a2l | 10-seed ensembles | **pAUC@1e-2** | -0.33 [-1.53, +0.90] CI contains 0 |
| a2r2 − a2l | 10-seed ensembles | TPR@1e-3 | -4.65 [-6.64, +4.63] CI contains 0 |
| a2r2 − a2l | 10-seed ensembles | TPR@1e-2 | -3.00 [-4.07, -2.37] **CI excludes 0** |
| a2r2 − a2l | 10-seed ensembles | AUC | +0.54 [+0.48, +0.61] **CI excludes 0** |
| a2r2 − a2l | 10-seed ensembles | pAUC@1e-3 | -0.78 [-6.88, +6.24] CI contains 0 |
| b2r2 − v2_pe | per-seed means | **pAUC@1e-2** | -7.78 [-10.47, -5.28] **CI excludes 0** |
| b2r2 − v2_pe | per-seed means | TPR@1e-3 | -16.86 [-24.17, -8.40] **CI excludes 0** |
| b2r2 − v2_pe | per-seed means | TPR@1e-2 | -3.67 [-5.57, -2.64] **CI excludes 0** |
| b2r2 − v2_pe | per-seed means | AUC | +0.48 [+0.35, +0.61] **CI excludes 0** |
| b2r2 − v2_pe | per-seed means | pAUC@1e-3 | -17.82 [-24.63, -11.11] **CI excludes 0** |
| b2r2 − v2_pe | 10-seed ensembles | **pAUC@1e-2** | -7.43 [-10.48, -4.84] **CI excludes 0** |
| b2r2 − v2_pe | 10-seed ensembles | TPR@1e-3 | -2.51 [-19.87, +3.64] CI contains 0 |
| b2r2 − v2_pe | 10-seed ensembles | TPR@1e-2 | -5.84 [-7.30, -4.42] **CI excludes 0** |
| b2r2 − v2_pe | 10-seed ensembles | AUC | +0.40 [+0.25, +0.54] **CI excludes 0** |
| b2r2 − v2_pe | 10-seed ensembles | pAUC@1e-3 | -16.38 [-34.03, -1.04] **CI excludes 0** |
| b2r2 − attbal | per-seed means | **pAUC@1e-2** | -8.00 [-11.37, -4.99] **CI excludes 0** |
| b2r2 − attbal | per-seed means | TPR@1e-3 | -19.77 [-27.86, -10.08] **CI excludes 0** |
| b2r2 − attbal | per-seed means | TPR@1e-2 | -2.02 [-4.03, -0.73] **CI excludes 0** |
| b2r2 − attbal | per-seed means | AUC | -0.20 [-0.32, -0.09] **CI excludes 0** |
| b2r2 − attbal | per-seed means | pAUC@1e-3 | -19.14 [-28.97, -9.15] **CI excludes 0** |
| b2r2 − attbal | 10-seed ensembles | **pAUC@1e-2** | -4.01 [-7.55, -0.86] **CI excludes 0** |
| b2r2 − attbal | 10-seed ensembles | TPR@1e-3 | -0.22 [-20.16, +3.09] CI contains 0 |
| b2r2 − attbal | 10-seed ensembles | TPR@1e-2 | -2.10 [-3.67, -0.98] **CI excludes 0** |
| b2r2 − attbal | 10-seed ensembles | AUC | -0.36 [-0.48, -0.23] **CI excludes 0** |
| b2r2 − attbal | 10-seed ensembles | pAUC@1e-3 | -12.03 [-30.50, +4.12] CI contains 0 |
| b2r2 − b2l | per-seed means | **pAUC@1e-2** | +1.07 [-0.22, +2.27] CI contains 0 |
| b2r2 − b2l | per-seed means | TPR@1e-3 | -3.49 [-7.13, +1.93] CI contains 0 |
| b2r2 − b2l | per-seed means | TPR@1e-2 | +2.68 [+0.99, +3.58] **CI excludes 0** |
| b2r2 − b2l | per-seed means | AUC | +0.09 [+0.03, +0.13] **CI excludes 0** |
| b2r2 − b2l | per-seed means | pAUC@1e-3 | -1.87 [-5.00, +1.16] CI contains 0 |
| b2r2 − b2l | 10-seed ensembles | **pAUC@1e-2** | +0.50 [-1.05, +2.03] CI contains 0 |
| b2r2 − b2l | 10-seed ensembles | TPR@1e-3 | +6.93 [-7.24, +9.98] CI contains 0 |
| b2r2 − b2l | 10-seed ensembles | TPR@1e-2 | -0.23 [-1.39, +0.39] CI contains 0 |
| b2r2 − b2l | 10-seed ensembles | AUC | +0.04 [-0.03, +0.09] CI contains 0 |
| b2r2 − b2l | 10-seed ensembles | pAUC@1e-3 | -1.62 [-10.95, +6.50] CI contains 0 |
| a2l − attbal | per-seed means | **pAUC@1e-2** | -1.99 [-3.47, -0.68] **CI excludes 0** |
| a2l − attbal | per-seed means | TPR@1e-3 | -6.62 [-13.02, -2.48] **CI excludes 0** |
| a2l − attbal | per-seed means | TPR@1e-2 | +0.96 [+0.38, +1.75] **CI excludes 0** |
| a2l − attbal | per-seed means | AUC | -0.99 [-1.08, -0.90] **CI excludes 0** |
| a2l − attbal | per-seed means | pAUC@1e-3 | -11.37 [-16.63, -5.31] **CI excludes 0** |
| a2l − attbal | 10-seed ensembles | **pAUC@1e-2** | +0.13 [-1.12, +1.27] CI contains 0 |
| a2l − attbal | 10-seed ensembles | TPR@1e-3 | +3.56 [-4.75, +5.43] CI contains 0 |
| a2l − attbal | 10-seed ensembles | TPR@1e-2 | +3.31 [+2.68, +4.21] **CI excludes 0** |
| a2l − attbal | 10-seed ensembles | AUC | -0.69 [-0.77, -0.62] **CI excludes 0** |
| a2l − attbal | 10-seed ensembles | pAUC@1e-3 | -1.82 [-7.25, +3.36] CI contains 0 |


### Per-seed paired differences of the primary metric (same seed index; points ×100)

| pair | s0 | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9 | mean ± std | seeds > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a2r2 − attbal | -1.1 | -1.1 | -2.0 | +1.1 | +0.4 | -2.2 | -0.5 | -0.6 | -0.5 | -1.8 | -0.83 ± 1.05 | 2/10 |
| a2r2 − v2_pe | +1.6 | +3.7 | +5.7 | -0.6 | -0.7 | -7.9 | +2.0 | -4.4 | -2.8 | -2.7 | -0.60 ± 4.04 | 4/10 |
| a2r2 − b2r2 | +7.0 | +7.3 | +8.9 | +1.8 | +3.4 | +8.4 | +5.8 | +9.8 | +15.8 | +3.5 | +7.17 ± 4.01 | 10/10 |
| a2r2 − a2l | +4.1 | +5.5 | +3.0 | -0.4 | +1.9 | -3.7 | +1.6 | -0.5 | +1.2 | -1.2 | +1.16 ± 2.71 | 6/10 |
| b2r2 − v2_pe | -5.4 | -3.6 | -3.2 | -2.4 | -4.0 | -16.3 | -3.8 | -14.3 | -18.7 | -6.2 | -7.78 ± 6.13 | 0/10 |
| b2r2 − attbal | -8.1 | -8.4 | -10.9 | -0.8 | -2.9 | -10.6 | -6.2 | -10.5 | -16.3 | -5.4 | -8.00 ± 4.45 | 0/10 |
| b2r2 − b2l | -1.9 | +13.4 | -2.4 | +7.4 | +6.4 | +4.5 | -4.0 | -6.3 | -14.1 | +7.7 | +1.07 ± 8.21 | 5/10 |
| a2l − attbal | -5.2 | -6.6 | -5.0 | +1.5 | -1.5 | +1.5 | -2.1 | -0.1 | -1.7 | -0.6 | -1.99 ± 2.80 | 2/10 |


**Claim rule (EVAL_PROTOCOL.md 5) on pAUC@1e-2, stratified bootstrap of the per-seed means:**

- a2r2 vs attbal: **RESOLVED, a2r2 worse** (CI excludes 0; negative in 8/10 seeds)
- a2r2 vs v2_pe: not resolved (CI contains 0; positive in 4/10, negative in 6/10 seeds)
- a2r2 vs b2r2: **RESOLVED, a2r2 better** (CI excludes 0; positive in 10/10 seeds)
- a2r2 vs a2l: not resolved (CI contains 0; positive in 6/10, negative in 4/10 seeds)
- b2r2 vs v2_pe: **RESOLVED, b2r2 worse** (CI excludes 0; negative in 10/10 seeds)
- b2r2 vs attbal: **RESOLVED, b2r2 worse** (CI excludes 0; negative in 10/10 seeds)
- b2r2 vs b2l: not resolved (CI contains 0; positive in 5/10, negative in 5/10 seeds)
- a2l vs attbal: **RESOLVED, a2l worse** (CI excludes 0; negative in 8/10 seeds)

### Cluster bootstrap over hash_apis groups (2,509 groups; cells (group, class) resampled; points ×100)

| difference | metric | mean difference | 95% CI (cluster) | seeds > 0 | outcome |
|---|---|---|---|---|---|
| a2r2 − attbal | pAUC@1e-2 (primary) | -0.83 | [-1.85, +0.07] | 2/10 | not resolved |
| a2r2 − attbal | TPR@1e-2 | -0.32 | [-1.32, +0.80] | 4/10 | CI contains 0 (descriptive) |
| a2r2 − attbal | TPR@1e-3 | -1.76 | [-7.62, +1.52] | 4/10 | CI contains 0 (descriptive) |
| a2r2 − attbal | AUC | -0.18 | [-0.41, -0.01] | 1/10 | CI excludes 0 (descriptive) |
| a2r2 − v2_pe | pAUC@1e-2 (primary) | -0.60 | [-6.50, +3.70] | 4/10 | not resolved |
| a2r2 − v2_pe | TPR@1e-2 | -1.97 | [-7.33, +2.62] | 4/10 | CI contains 0 (descriptive) |
| a2r2 − v2_pe | TPR@1e-3 | +1.16 | [-11.37, +8.35] | 5/10 | CI contains 0 (descriptive) |
| a2r2 − v2_pe | AUC | +0.50 | [-0.34, +1.90] | 7/10 | CI contains 0 (descriptive) |
| a2r2 − b2r2 | pAUC@1e-2 (primary) | +7.17 | [+0.06, +13.45] | 10/10 | **meets the rule** |
| a2r2 − b2r2 | TPR@1e-2 | +1.70 | [-3.92, +8.65] | 7/10 | CI contains 0 (descriptive) |
| a2r2 − b2r2 | TPR@1e-3 | +18.02 | [+1.80, +29.16] | 8/10 | CI excludes 0 (descriptive) |
| a2r2 − b2r2 | AUC | +0.02 | [-0.67, +0.80] | 4/10 | CI contains 0 (descriptive) |
| a2r2 − a2l | pAUC@1e-2 (primary) | +1.16 | [-0.86, +3.54] | 6/10 | not resolved |
| a2r2 − a2l | TPR@1e-2 | -1.28 | [-3.86, +0.56] | 1/10 | CI contains 0 (descriptive) |
| a2r2 − a2l | TPR@1e-3 | +4.87 | [-2.39, +13.87] | 7/10 | CI contains 0 (descriptive) |
| a2r2 − a2l | AUC | +0.81 | [+0.40, +1.39] | 8/10 | CI excludes 0 (descriptive) |
| b2r2 − v2_pe | pAUC@1e-2 (primary) | -7.78 | [-12.49, -3.39] | 0/10 | **meets the rule** |
| b2r2 − v2_pe | TPR@1e-2 | -3.67 | [-8.14, -0.72] | 0/10 | CI excludes 0 (descriptive) |
| b2r2 − v2_pe | TPR@1e-3 | -16.86 | [-27.88, -5.66] | 0/10 | CI excludes 0 (descriptive) |
| b2r2 − v2_pe | AUC | +0.48 | [-0.57, +1.85] | 7/10 | CI contains 0 (descriptive) |
| b2r2 − attbal | pAUC@1e-2 (primary) | -8.00 | [-14.37, -0.75] | 0/10 | **meets the rule** |
| b2r2 − attbal | TPR@1e-2 | -2.02 | [-9.43, +4.27] | 2/10 | CI contains 0 (descriptive) |
| b2r2 − attbal | TPR@1e-3 | -19.77 | [-31.64, -5.56] | 1/10 | CI excludes 0 (descriptive) |
| b2r2 − attbal | AUC | -0.20 | [-1.01, +0.54] | 4/10 | CI contains 0 (descriptive) |
| b2r2 − b2l | pAUC@1e-2 (primary) | +1.07 | [-3.01, +5.79] | 5/10 | not resolved |
| b2r2 − b2l | TPR@1e-2 | +2.68 | [-1.92, +6.91] | 5/10 | CI contains 0 (descriptive) |
| b2r2 − b2l | TPR@1e-3 | -3.49 | [-11.77, +5.27] | 4/10 | CI contains 0 (descriptive) |
| b2r2 − b2l | AUC | +0.09 | [-0.21, +0.35] | 5/10 | CI contains 0 (descriptive) |
| a2l − attbal | pAUC@1e-2 (primary) | -1.99 | [-4.86, +0.52] | 2/10 | not resolved |
| a2l − attbal | TPR@1e-2 | +0.96 | [-0.84, +3.73] | 7/10 | CI contains 0 (descriptive) |
| a2l − attbal | TPR@1e-3 | -6.62 | [-17.62, +0.70] | 3/10 | CI contains 0 (descriptive) |
| a2l − attbal | AUC | -0.99 | [-1.65, -0.50] | 1/10 | CI excludes 0 (descriptive) |


### Detection rate per family at the 1% FPR threshold of each model and seed (April; mean ± std over 10 seeds, %). `clean` and `windows_syswow64` rows are false-positive rates.

| family | n | **A2: ATT+bal-2L, round 2** | B2: 2L without padding, round 2 | A: ATT+bal-2L (19.12) | B: 2L without padding (19.12) | ATT+bal | v2-PE |
|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 82.2 ± 1.9 | 82.3 ± 1.3 | 81.8 ± 1.6 | 78.7 ± 5.2 | 82.1 ± 1.9 | 83.7 ± 2.4 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 72.5 ± 6.4 | 81.5 ± 6.7 | 79.5 ± 8.6 | 79.4 ± 6.8 | 72.8 ± 6.1 | 81.7 ± 6.8 |
| dropper | 252 | 82.0 ± 5.1 | 76.6 ± 2.2 | 83.2 ± 1.9 | 80.0 ± 3.4 | 81.9 ± 5.7 | 80.1 ± 2.4 |
| keylogger | 1041 | 88.1 ± 3.1 | 82.5 ± 3.4 | 86.8 ± 2.4 | 81.2 ± 3.4 | 87.0 ± 2.5 | 87.1 ± 6.1 |
| ransomware | 2139 | 71.1 ± 2.9 | 61.2 ± 1.8 | 72.2 ± 3.9 | 60.3 ± 2.9 | 72.9 ± 2.2 | 70.8 ± 4.9 |
| rat | 1258 | 87.6 ± 3.4 | 85.7 ± 5.2 | 86.6 ± 1.2 | 74.6 ± 15.5 | 87.8 ± 2.8 | 89.2 ± 2.0 |
| trojan | 1085 | 80.6 ± 2.5 | 80.1 ± 0.9 | 81.7 ± 1.1 | 81.8 ± 3.1 | 80.4 ± 2.5 | 80.9 ± 1.2 |
| windows_syswow64 | 59 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.2 ± 0.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold. Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| **A2: ATT+bal-2L, round 2** | 1/10 | -1.4 (IQR -3.0 to -0.8) | 84.1 ± 4.7 | 72.5 ± 6.4 |
| B2: 2L without padding, round 2 | 8/10 | +1.7 (IQR +0.5 to +2.3) | 81.8 ± 1.3 | 81.5 ± 6.7 |
| A: ATT+bal-2L (19.12) | 4/10 | -0.4 (IQR -1.1 to +0.3) | 86.8 ± 2.1 | 79.5 ± 8.6 |
| B: 2L without padding (19.12) | 10/10 | +2.8 (IQR +1.7 to +3.3) | 75.5 ± 8.1 | 79.4 ± 6.8 |
| ATT+bal | 1/10 | -3.2 (IQR -4.6 to -1.6) | 84.6 ± 3.0 | 72.8 ± 6.1 |
| v2-PE | 8/10 | +7.7 (IQR +1.2 to +19.7) | 82.1 ± 2.4 | 81.7 ± 6.8 |

