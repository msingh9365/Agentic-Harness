### Test set (April), logit-ranked: per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 | McClish pAUC@1e-2 | TPR@1e-3 literal f32 |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint (1 model) | 1 | 0.518 | 0.750 | 0.9586 | 0.885 | 0.659 | 0.372 | 0.829 | 0.517 |
| baseline v2 (released code), 10 seeds | 10 | 0.527 ± 0.082 | 0.788 ± 0.026 | 0.9624 ± 0.0050 | 0.901 ± 0.016 | 0.690 ± 0.036 | 0.381 ± 0.110 | 0.844 ± 0.018 | 0.317 ± 0.280 |
| **baseline v2-PE (paper positional encoding), 10 seeds** | 10 | 0.543 ± 0.063 | 0.811 ± 0.023 | 0.9644 ± 0.0093 | 0.915 ± 0.012 | 0.705 ± 0.031 | 0.444 ± 0.076 | 0.852 ± 0.016 | 0.060 ± 0.191 |


10-seed ensemble (mean logit over the seeds):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| baseline v2 (released code), 10 seeds | 0.636 | 0.852 | 0.9722 | 0.920 | **0.762** | 0.431 |
| **baseline v2-PE (paper positional encoding), 10 seeds** | 0.606 | 0.851 | 0.9705 | 0.927 | **0.768** | 0.546 |


### Validation slice (7,530 reports; clean for v2 and v2-PE, in-sample for the released checkpoint): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| baseline v2 (released code), 10 seeds | 10 | 0.896 ± 0.061 | 0.983 ± 0.005 | 0.9984 ± 0.0003 | 0.990 ± 0.002 | 0.947 ± 0.015 | 0.773 ± 0.112 |
| **baseline v2-PE (paper positional encoding), 10 seeds** | 10 | 0.916 ± 0.060 | 0.984 ± 0.004 | 0.9985 ± 0.0002 | 0.990 ± 0.002 | 0.962 ± 0.013 | 0.858 ± 0.098 |
| released checkpoint (in-sample: trained on this slice) | 1 | 0.898 | 0.962 | 0.9986 | 0.984 | 0.941 | 0.890 |


Per-epoch validation of v2-PE (stored during training):

|  | TPR@1e-3 | TPR@1e-2 | AUC | pAUC@1e-2 | val loss |
|---|---|---|---|---|---|
| v2-PE epoch 1 | 0.913 ± 0.039 | 0.980 ± 0.002 | 0.9981 ± 0.0002 | 0.945 ± 0.014 | 0.1025 ± 0.0332 |
| v2-PE epoch 2 | 0.916 ± 0.060 | 0.984 ± 0.004 | 0.9985 ± 0.0002 | 0.962 ± 0.013 | 0.1135 ± 0.0454 |


### Differences (stratified bootstrap over the April test reports, 1000 resamples, numpy seed 0; 95% CI; points = x 100)

| difference | statistic | metric | difference in points, 95% CI |
|---|---|---|---|
| v2_pe - v2 | per-seed means | **pAUC@1e-2** | +1.45 [+0.14, +2.79] **resolved** |
| v2_pe - v2 | per-seed means | TPR@1e-3 | +1.61 [-3.05, +9.33] not resolved |
| v2_pe - v2 | per-seed means | TPR@1e-2 | +2.28 [+1.29, +3.02] **resolved** |
| v2_pe - v2 | per-seed means | AUC | +0.20 [+0.14, +0.27] **resolved** |
| v2_pe - v2 | per-seed means | pAUC@1e-3 | +6.31 [-0.85, +11.90] not resolved |
| v2_pe - v2 | 10-seed ensembles | **pAUC@1e-2** | +0.67 [-0.90, +2.39] not resolved |
| v2_pe - v2 | 10-seed ensembles | TPR@1e-3 | -3.00 [-7.48, +16.52] not resolved |
| v2_pe - v2 | 10-seed ensembles | TPR@1e-2 | -0.05 [-1.40, +0.64] not resolved |
| v2_pe - v2 | 10-seed ensembles | AUC | -0.17 [-0.25, -0.09] **resolved** |
| v2_pe - v2 | 10-seed ensembles | pAUC@1e-3 | +11.55 [-1.27, +21.22] not resolved |
| v2_pe - released | per-seed means | **pAUC@1e-2** | +4.59 [+0.73, +8.12] **resolved** |
| v2_pe - released | per-seed means | TPR@1e-3 | +2.44 [-6.97, +13.49] not resolved |
| v2_pe - released | per-seed means | TPR@1e-2 | +6.13 [+4.45, +7.97] **resolved** |
| v2_pe - released | per-seed means | AUC | +0.58 [+0.41, +0.73] **resolved** |
| v2_pe - released | per-seed means | pAUC@1e-3 | +7.15 [-4.83, +21.45] not resolved |
| v2_pe - released | 10-seed ensembles | **pAUC@1e-2** | +10.95 [+7.25, +14.47] **resolved** |
| v2_pe - released | 10-seed ensembles | TPR@1e-3 | +8.72 [-2.35, +20.57] not resolved |
| v2_pe - released | 10-seed ensembles | TPR@1e-2 | +10.15 [+8.00, +11.85] **resolved** |
| v2_pe - released | 10-seed ensembles | AUC | +1.18 [+1.02, +1.34] **resolved** |
| v2_pe - released | 10-seed ensembles | pAUC@1e-3 | +17.41 [+5.38, +31.55] **resolved** |
| v2 - released | per-seed means | **pAUC@1e-2** | +3.14 [-1.15, +7.02] not resolved |
| v2 - released | per-seed means | TPR@1e-3 | +0.83 [-13.97, +14.34] not resolved |
| v2 - released | per-seed means | TPR@1e-2 | +3.85 [+2.48, +5.91] **resolved** |
| v2 - released | per-seed means | AUC | +0.38 [+0.21, +0.54] **resolved** |
| v2 - released | per-seed means | pAUC@1e-3 | +0.84 [-13.41, +16.75] not resolved |
| v2 - released | 10-seed ensembles | **pAUC@1e-2** | +10.27 [+5.43, +14.31] **resolved** |
| v2 - released | 10-seed ensembles | TPR@1e-3 | +11.72 [-15.81, +23.98] not resolved |
| v2 - released | 10-seed ensembles | TPR@1e-2 | +10.20 [+8.78, +11.92] **resolved** |
| v2 - released | 10-seed ensembles | AUC | +1.36 [+1.19, +1.52] **resolved** |
| v2 - released | 10-seed ensembles | pAUC@1e-3 | +5.86 [-11.42, +25.79] not resolved |


### Per-seed paired differences v2-PE − v2 (the same seed index: the same initial weights and data order), points x 100

| metric | s0 | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9 | mean ± std | seeds > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **pAUC@1e-2** | +4.1 | -0.7 | -8.0 | +2.1 | -3.9 | +2.4 | +5.3 | +5.3 | +7.9 | -0.1 | +1.45 ± 4.77 | 6/10 |
| TPR@1e-3 | +3.8 | -6.1 | -10.9 | +8.1 | -1.3 | +4.0 | +16.0 | +5.9 | +6.1 | -9.3 | +1.61 ± 8.44 | 6/10 |
| TPR@1e-2 | +6.8 | +1.1 | -3.1 | +2.2 | -3.9 | +3.1 | +1.8 | +5.4 | +8.6 | +0.7 | +2.28 ± 3.98 | 8/10 |
| AUC | +1.3 | -0.2 | -0.8 | -0.7 | +0.3 | +1.1 | +0.7 | +0.1 | -0.3 | +0.4 | +0.20 ± 0.71 | 6/10 |
| pAUC@1e-3 | +10.7 | +2.7 | -9.1 | +25.1 | +6.0 | -0.0 | +18.2 | +10.4 | +7.8 | -8.7 | +6.31 ± 10.80 | 7/10 |


**Claim rule (EVAL_PROTOCOL.md section 5: CI of the primary metric excludes 0 AND the same sign in at least 7 of the 10 seeds):**

- v2-PE against v2 on pAUC@1e-2: not resolved (CI excludes 0; positive in 6/10, negative in 4/10 seeds)
- v2-PE against the released checkpoint on pAUC@1e-2 (each v2-PE seed against the one released model): **RESOLVED: v2-PE better** (CI excludes 0 and positive in 9/10 seeds)
- ensembles (10-seed): v2-PE − v2 on pAUC@1e-2 = +0.67 points, CI [-0.90, +2.39]

### Output scale (as in REPORT 5.7; April test, mean over the models)

| model | mean abs(logit) | benign logit mean | benign logit p99 | malware above logit 16.6 | total weight L2 (incl. the constant PE table) |
|---|---|---|---|---|---|
| released checkpoint (1 model) | 16.6 | -16.4 | 2.5 | 42% | 424.0 |
| baseline v2 (released code), 10 seeds | 17.7 | -16.4 | 3.8 | 49% | 420.0 |
| **baseline v2-PE (paper positional encoding), 10 seeds** | 28.5 | -22.8 | 5.6 | 68% | 414.7 |

