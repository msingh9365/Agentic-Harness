### Test set: low-FPR metrics (logit-ranked; mean ± std over models)

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 | McClish pAUC@1e-2 | TPR@1e-3 literal f32 |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint (authors, 1 model) | 1 | 0.518 | 0.750 | 0.9586 | 0.885 | 0.659 | 0.372 | 0.829 | 0.517 |
| previous recipe A (9 fold models) | 9 | 0.406 ± 0.078 | 0.700 ± 0.045 | 0.9521 ± 0.0096 | 0.897 ± 0.018 | 0.577 ± 0.058 | 0.294 ± 0.099 | 0.787 ± 0.029 | 0.000 ± 0.000 |
| **baseline v2, seeds 0-4** | 5 | 0.561 ± 0.043 | 0.793 ± 0.034 | 0.9602 ± 0.0051 | 0.893 ± 0.017 | 0.702 ± 0.034 | 0.398 ± 0.092 | 0.850 ± 0.017 | 0.444 ± 0.252 |
| **baseline v2, seeds 0-9** | 10 | 0.527 ± 0.082 | 0.788 ± 0.026 | 0.9624 ± 0.0050 | 0.901 ± 0.016 | 0.690 ± 0.036 | 0.381 ± 0.110 | 0.844 ± 0.018 | 0.317 ± 0.280 |
| v2 seeds 0-4 (half 1) | 5 | 0.561 ± 0.043 | 0.793 ± 0.034 | 0.9602 ± 0.0051 | 0.893 ± 0.017 | 0.702 ± 0.034 | 0.398 ± 0.092 | 0.850 ± 0.017 | 0.444 ± 0.252 |
| v2 seeds 5-9 (half 2) | 5 | 0.492 ± 0.102 | 0.784 ± 0.019 | 0.9646 ± 0.0042 | 0.909 ± 0.011 | 0.679 ± 0.037 | 0.363 ± 0.135 | 0.839 ± 0.019 | 0.190 ± 0.269 |
| B3: upper bound (90% labeled) (lr 0.002, ep 3) | 5 | 0.522 ± 0.092 | 0.772 ± 0.024 | 0.9666 ± 0.0035 | 0.907 ± 0.003 | 0.666 ± 0.054 | 0.433 ± 0.100 | 0.832 ± 0.027 | 0.336 ± 0.315 |
| B3: lower bound (20% labeled) (lr 0.002, ep 3) | 5 | 0.368 ± 0.075 | 0.666 ± 0.028 | 0.9530 ± 0.0096 | 0.873 ± 0.027 | 0.539 ± 0.037 | 0.282 ± 0.068 | 0.768 ± 0.019 | 0.213 ± 0.197 |
| B3: control: causal last-token, 20%, no pre-training (lr 0.001, ep 3) | 5 | 0.412 ± 0.055 | 0.650 ± 0.012 | 0.9487 ± 0.0106 | 0.862 ± 0.013 | 0.545 ± 0.019 | 0.307 ± 0.027 | 0.772 ± 0.009 | 0.412 ± 0.055 |
| B3: AR pre-training + last-token (lr 0.002, ep 3) | 5 | 0.463 ± 0.072 | 0.711 ± 0.051 | 0.9617 ± 0.0038 | 0.887 ± 0.010 | 0.608 ± 0.044 | 0.369 ± 0.075 | 0.803 ± 0.022 | 0.388 ± 0.223 |
| B3: per-position MLM pre-training (lr 0.002, ep 6) | 5 | 0.404 ± 0.037 | 0.696 ± 0.040 | 0.9566 ± 0.0087 | 0.882 ± 0.019 | 0.574 ± 0.035 | 0.318 ± 0.064 | 0.786 ± 0.018 | 0.000 ± 0.000 |
| B3: AR pre-training + flatten classifier (lr 0.001, ep 6) | 5 | 0.407 ± 0.081 | 0.681 ± 0.041 | 0.9581 ± 0.0086 | 0.876 ± 0.017 | 0.578 ± 0.041 | 0.321 ± 0.056 | 0.788 ± 0.021 | 0.000 ± 0.000 |
| B3: the authors' multi-hot MLM pre-training (lr 0.001, ep 3) | 5 | 0.360 ± 0.127 | 0.673 ± 0.032 | 0.9548 ± 0.0055 | 0.890 ± 0.012 | 0.541 ± 0.047 | 0.271 ± 0.090 | 0.769 ± 0.024 | 0.324 ± 0.193 |


### Validation slice (7,530 reports, 2,467 benign): the same metrics where the slice is clean

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| **baseline v2, seeds 0-4** | 5 | 0.898 ± 0.088 | 0.985 ± 0.004 | 0.9984 ± 0.0003 | 0.990 ± 0.001 | 0.950 ± 0.019 | 0.777 ± 0.122 |
| **baseline v2, seeds 0-9** | 10 | 0.896 ± 0.061 | 0.983 ± 0.005 | 0.9984 ± 0.0003 | 0.990 ± 0.002 | 0.947 ± 0.015 | 0.773 ± 0.112 |
| B3: upper bound (90% labeled) | 5 | 0.910 ± 0.029 | 0.977 ± 0.004 | 0.9980 ± 0.0003 | 0.989 ± 0.001 | 0.951 ± 0.010 | 0.887 ± 0.032 |
| B3: lower bound (20% labeled) | 5 | 0.693 ± 0.058 | 0.922 ± 0.011 | 0.9942 ± 0.0009 | 0.973 ± 0.005 | 0.839 ± 0.024 | 0.566 ± 0.123 |
| B3: control: causal last-token, 20%, no pre-training | 5 | 0.747 ± 0.071 | 0.916 ± 0.010 | 0.9950 ± 0.0004 | 0.977 ± 0.002 | 0.843 ± 0.024 | 0.647 ± 0.103 |
| B3: AR pre-training + last-token | 5 | 0.791 ± 0.063 | 0.927 ± 0.011 | 0.9950 ± 0.0009 | 0.977 ± 0.002 | 0.867 ± 0.020 | 0.645 ± 0.075 |
| B3: per-position MLM pre-training | 5 | 0.796 ± 0.045 | 0.928 ± 0.004 | 0.9947 ± 0.0006 | 0.976 ± 0.002 | 0.866 ± 0.016 | 0.664 ± 0.057 |
| B3: AR pre-training + flatten classifier | 5 | 0.804 ± 0.039 | 0.935 ± 0.007 | 0.9951 ± 0.0009 | 0.977 ± 0.002 | 0.873 ± 0.015 | 0.685 ± 0.064 |
| B3: the authors' multi-hot MLM pre-training | 5 | 0.731 ± 0.050 | 0.926 ± 0.005 | 0.9948 ± 0.0006 | 0.977 ± 0.002 | 0.836 ± 0.032 | 0.566 ± 0.100 |


### How much more stable is pAUC@1e-2? Per-seed (per-model) std and coefficient of variation (std / mean), test set

| model | n | std TPR@1e-3 | std pAUC@1e-2 | CV TPR@1e-3 | CV pAUC@1e-2 | CV ratio |
|---|---|---|---|---|---|---|
| previous recipe A (9 fold models) | 9 | 0.078 | 0.058 | 0.19 | 0.10 | 1.9x |
| **baseline v2, seeds 0-4** | 5 | 0.043 | 0.034 | 0.08 | 0.05 | 1.6x |
| **baseline v2, seeds 0-9** | 10 | 0.082 | 0.036 | 0.16 | 0.05 | 3.0x |
| upper bound (90% labeled) | 5 | 0.092 | 0.054 | 0.18 | 0.08 | 2.2x |
| lower bound (20% labeled) | 5 | 0.075 | 0.037 | 0.20 | 0.07 | 2.9x |
| control: causal last-token, 20%, no pre-training | 5 | 0.055 | 0.019 | 0.13 | 0.03 | 3.9x |
| AR pre-training + last-token | 5 | 0.072 | 0.044 | 0.15 | 0.07 | 2.1x |
| per-position MLM pre-training | 5 | 0.037 | 0.035 | 0.09 | 0.06 | 1.5x |
| AR pre-training + flatten classifier | 5 | 0.081 | 0.041 | 0.20 | 0.07 | 2.8x |
| the authors' multi-hot MLM pre-training | 5 | 0.127 | 0.047 | 0.35 | 0.09 | 4.1x |


### Baseline v2 against the released model and the previous recipe (bootstrap 95% CI over the April test reports, 1000 stratified resamples; per-model means)

| difference | metric | difference of means, 95% CI |
|---|---|---|
| v2_5 - released | pAUC@1e-2 | +0.043 [-0.002, +0.082] not resolved |
| v2_5 - released | pAUC@1e-3 | +0.026 [-0.124, +0.197] not resolved |
| v2_5 - released | TPR@1e-3 | +0.043 [-0.141, +0.183] not resolved |
| v2_5 - released | TPR@1e-2 | +0.043 [+0.027, +0.066] **resolved** |
| v2_5 - released | AUC | +0.0016 [-0.0000, +0.0033] not resolved |
| v2_5 - prev_A | pAUC@1e-2 | +0.125 [+0.103, +0.144] **resolved** |
| v2_5 - prev_A | pAUC@1e-3 | +0.104 [+0.041, +0.182] **resolved** |
| v2_5 - prev_A | TPR@1e-3 | +0.155 [+0.051, +0.221] **resolved** |
| v2_5 - prev_A | TPR@1e-2 | +0.093 [+0.080, +0.109] **resolved** |
| v2_5 - prev_A | AUC | +0.0082 [+0.0065, +0.0097] **resolved** |
| released - prev_A | pAUC@1e-2 | +0.082 [+0.043, +0.121] **resolved** |
| released - prev_A | pAUC@1e-3 | +0.078 [-0.072, +0.207] not resolved |
| released - prev_A | TPR@1e-3 | +0.113 [-0.004, +0.236] not resolved |
| released - prev_A | TPR@1e-2 | +0.050 [+0.029, +0.068] **resolved** |
| released - prev_A | AUC | +0.0066 [+0.0043, +0.0087] **resolved** |
| v2_10 - released | pAUC@1e-2 | +0.031 [-0.011, +0.070] not resolved |
| v2_10 - released | pAUC@1e-3 | +0.008 [-0.134, +0.167] not resolved |
| v2_10 - released | TPR@1e-3 | +0.008 [-0.140, +0.143] not resolved |
| v2_10 - released | TPR@1e-2 | +0.038 [+0.025, +0.059] **resolved** |
| v2_10 - released | AUC | +0.0038 [+0.0021, +0.0054] **resolved** |
| v2_10 - prev_A | pAUC@1e-2 | +0.114 [+0.093, +0.132] **resolved** |
| v2_10 - prev_A | pAUC@1e-3 | +0.086 [+0.037, +0.143] **resolved** |
| v2_10 - prev_A | TPR@1e-3 | +0.121 [+0.052, +0.184] **resolved** |
| v2_10 - prev_A | TPR@1e-2 | +0.088 [+0.078, +0.101] **resolved** |
| v2_10 - prev_A | AUC | +0.0103 [+0.0090, +0.0116] **resolved** |
| v2_s5_9 - v2_s0_4 | pAUC@1e-2 | -0.022 [-0.035, -0.008] **resolved** |
| v2_s5_9 - v2_s0_4 | pAUC@1e-3 | -0.035 [-0.095, +0.016] not resolved |
| v2_s5_9 - v2_s0_4 | TPR@1e-3 | -0.069 [-0.112, +0.020] not resolved |
| v2_s5_9 - v2_s0_4 | TPR@1e-2 | -0.009 [-0.021, -0.001] **resolved** |
| v2_s5_9 - v2_s0_4 | AUC | +0.0043 [+0.0032, +0.0054] **resolved** |


Agreement of the two independent halves of the v2 seeds (seeds 0-4 against 5-9; Welch t-test on the per-seed values; the bootstrap row `v2_s5_9 - v2_s0_4` above is the test-set view):

| metric | seeds 0-4 | seeds 5-9 | difference | Welch p |
|---|---|---|---|---|
| pAUC@1e-2 | 0.702 | 0.679 | -0.022 | 0.35 |
| TPR@1e-3 | 0.561 | 0.492 | -0.069 | 0.22 |
| TPR@1e-2 | 0.793 | 0.784 | -0.009 | 0.61 |
| AUC | 0.960 | 0.965 | +0.004 | 0.18 |


### B3 paired differences under pAUC (per-seed mean ± std over 5 seeds; seeds > 0; bootstrap 95% CI of the difference of the seed means, [points x 100])

| difference | metric | per-seed mean ± std | seeds > 0 | bootstrap 95% CI (points) |
|---|---|---|---|---|
| upper − lower | **pAUC@1e-2** | +12.71 ± 7.10 | 5/5 | +12.71 [+10.88, +14.56] **resolved** |
| upper − lower | pAUC@1e-3 | +15.09 ± 12.17 | 5/5 | +15.09 [+10.32, +20.05] **resolved** |
| upper − lower | TPR@1e-3 | +15.32 ± 10.32 | 4/5 | +15.32 [+10.88, +18.66] **resolved** |
| upper − lower | TPR@1e-2 | +10.66 ± 4.45 | 5/5 | +10.66 [+9.66, +12.29] **resolved** |
| upper − lower | AUC | +1.36 ± 1.01 | 5/5 | +1.36 [+1.24, +1.48] **resolved** |
| AR − lower | **pAUC@1e-2** | +6.94 ± 4.19 | 5/5 | +6.94 [+4.65, +9.07] **resolved** |
| AR − lower | pAUC@1e-3 | +8.68 ± 2.43 | 5/5 | +8.68 [+3.62, +13.11] **resolved** |
| AR − lower | TPR@1e-3 | +9.47 ± 3.96 | 5/5 | +9.47 [+6.12, +14.57] **resolved** |
| AR − lower | TPR@1e-2 | +4.49 ± 5.54 | 3/5 | +4.49 [+2.96, +5.72] **resolved** |
| AR − lower | AUC | +0.87 ± 0.89 | 3/5 | +0.87 [+0.73, +1.01] **resolved** |
| AR − its causal control | **pAUC@1e-2** | +6.29 ± 5.49 | 4/5 | +6.29 [+4.30, +8.20] **resolved** |
| AR − its causal control | pAUC@1e-3 | +6.15 ± 8.76 | 4/5 | +6.15 [+0.14, +12.75] **resolved** |
| AR − its causal control | TPR@1e-3 | +5.06 ± 10.35 | 2/5 | +5.06 [+2.99, +12.33] **resolved** |
| AR − its causal control | TPR@1e-2 | +6.07 ± 5.20 | 4/5 | +6.07 [+4.57, +7.39] **resolved** |
| AR − its causal control | AUC | +1.30 ± 0.81 | 5/5 | +1.30 [+1.16, +1.44] **resolved** |
| upper − AR | **pAUC@1e-2** | +5.77 ± 6.89 | 3/5 | +5.77 [+3.28, +8.23] **resolved** |
| upper − AR | pAUC@1e-3 | +6.41 ± 13.43 | 3/5 | +6.41 [-0.08, +12.44] not resolved |
| upper − AR | TPR@1e-3 | +5.85 ± 12.58 | 3/5 | +5.85 [-0.12, +9.52] not resolved |
| upper − AR | TPR@1e-2 | +6.17 ± 5.26 | 4/5 | +6.17 [+5.09, +8.08] **resolved** |
| upper − AR | AUC | +0.49 ± 0.33 | 5/5 | +0.49 [+0.35, +0.63] **resolved** |
| MLM − lower | **pAUC@1e-2** | +3.51 ± 4.27 | 3/5 | +3.51 [+1.54, +5.48] **resolved** |
| MLM − lower | pAUC@1e-3 | +3.65 ± 3.07 | 4/5 | +3.65 [-1.09, +8.57] not resolved |
| MLM − lower | TPR@1e-3 | +3.57 ± 7.14 | 3/5 | +3.57 [-0.61, +7.64] not resolved |
| MLM − lower | TPR@1e-2 | +3.08 ± 4.75 | 4/5 | +3.08 [+1.93, +4.34] **resolved** |
| MLM − lower | AUC | +0.36 ± 0.97 | 3/5 | +0.36 [+0.26, +0.46] **resolved** |
| upper − MLM | **pAUC@1e-2** | +9.20 ± 4.69 | 5/5 | +9.20 [+7.06, +11.25] **resolved** |
| upper − MLM | pAUC@1e-3 | +11.44 ± 12.55 | 4/5 | +11.44 [+6.51, +16.86] **resolved** |
| upper − MLM | TPR@1e-3 | +11.75 ± 11.03 | 5/5 | +11.75 [+6.65, +15.98] **resolved** |
| upper − MLM | TPR@1e-2 | +7.58 ± 2.73 | 5/5 | +7.58 [+6.47, +9.20] **resolved** |
| upper − MLM | AUC | +1.00 ± 0.62 | 5/5 | +1.00 [+0.88, +1.13] **resolved** |
| AR flatten − lower | **pAUC@1e-2** | +3.95 ± 4.56 | 4/5 | +3.95 [+1.93, +5.92] **resolved** |
| AR flatten − lower | pAUC@1e-3 | +3.92 ± 7.06 | 3/5 | +3.92 [-0.41, +8.37] not resolved |
| AR flatten − lower | TPR@1e-3 | +3.89 ± 10.42 | 2/5 | +3.89 [+0.04, +9.83] **resolved** |
| AR flatten − lower | TPR@1e-2 | +1.57 ± 4.54 | 3/5 | +1.57 [+0.29, +2.95] **resolved** |
| AR flatten − lower | AUC | +0.51 ± 1.34 | 3/5 | +0.51 [+0.37, +0.65] **resolved** |
| MLM (authors') − lower | **pAUC@1e-2** | +0.19 ± 6.64 | 3/5 | +0.19 [-1.73, +2.08] not resolved |
| MLM (authors') − lower | pAUC@1e-3 | -1.11 ± 13.72 | 3/5 | -1.11 [-4.33, +3.16] not resolved |
| MLM (authors') − lower | TPR@1e-3 | -0.80 ± 17.91 | 2/5 | -0.80 [-4.82, +4.66] not resolved |
| MLM (authors') − lower | TPR@1e-2 | +0.69 ± 3.93 | 3/5 | +0.69 [-1.13, +2.42] not resolved |
| MLM (authors') − lower | AUC | +0.18 ± 0.80 | 3/5 | +0.18 [+0.06, +0.30] **resolved** |


Seed-ensemble flavour (mean logit over the 5 seeds) of the pAUC@1e-2 differences:

| difference | pAUC@1e-2 (ensemble), 95% CI (points) |
|---|---|
| upper − lower | +7.91 [+6.10, +9.63] **resolved** |
| AR − lower | +1.63 [-0.71, +4.05] not resolved |
| AR − its causal control | +5.06 [+3.01, +7.19] **resolved** |
| upper − AR | +6.28 [+3.78, +8.58] **resolved** |
| MLM − lower | +1.71 [-0.23, +3.70] not resolved |
| upper − MLM | +6.20 [+4.17, +8.40] **resolved** |
| AR flatten − lower | +1.07 [-1.03, +3.09] not resolved |
| MLM (authors') − lower | -2.43 [-4.41, -0.56] **resolved** |

