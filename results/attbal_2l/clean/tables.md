### Clean April test: per-seed mean ± std (10 seeds, logit-ranked)

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| **ATT+bal-2L (A)** | 10 | 0.506 ± 0.077 | 0.804 ± 0.019 | 0.9614 ± 0.0074 | 0.912 ± 0.015 | 0.687 ± 0.017 | 0.343 ± 0.066 |
| B: 2L without padding | 10 | 0.409 ± 0.116 | 0.748 ± 0.046 | 0.9684 ± 0.0058 | 0.897 ± 0.010 | 0.616 ± 0.062 | 0.284 ± 0.117 |
| ATT+bal | 10 | 0.572 ± 0.061 | 0.795 ± 0.020 | 0.9713 ± 0.0066 | 0.913 ± 0.017 | 0.707 ± 0.017 | 0.457 ± 0.041 |
| v2-PE | 10 | 0.543 ± 0.063 | 0.811 ± 0.023 | 0.9644 ± 0.0093 | 0.915 ± 0.012 | 0.705 ± 0.031 | 0.444 ± 0.076 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| **ATT+bal-2L (A)** | 0.618 | 0.847 | 0.9711 | 0.922 | **0.736** | 0.485 |
| B: 2L without padding | 0.511 | 0.795 | 0.9741 | 0.902 | **0.689** | 0.399 |
| ATT+bal | 0.583 | 0.814 | 0.9780 | 0.926 | **0.734** | 0.503 |
| v2-PE | 0.606 | 0.851 | 0.9705 | 0.927 | **0.768** | 0.546 |


Validation slice (7,530 reports, clean; no validation logits are kept for ATT+bal): per-seed mean ± std

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| **ATT+bal-2L (A)** | 10 | 0.866 ± 0.078 | 0.981 ± 0.002 | 0.9975 ± 0.0009 | 0.990 ± 0.001 | 0.944 ± 0.016 | 0.793 ± 0.120 |
| B: 2L without padding | 10 | 0.919 ± 0.035 | 0.986 ± 0.002 | 0.9985 ± 0.0002 | 0.990 ± 0.001 | 0.958 ± 0.010 | 0.832 ± 0.088 |
| v2-PE | 10 | 0.916 ± 0.060 | 0.984 ± 0.004 | 0.9985 ± 0.0002 | 0.990 ± 0.002 | 0.962 ± 0.013 | 0.858 ± 0.098 |


### Differences, stratified bootstrap (1000 resamples, numpy seed 0; points ×100; same resamples for all models)

| difference | statistic | metric | difference in points, 95% CI |
|---|---|---|---|
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
| a2l − v2_pe | per-seed means | **pAUC@1e-2** | -1.77 [-4.37, +0.77] CI contains 0 |
| a2l − v2_pe | per-seed means | TPR@1e-3 | -3.71 [-11.97, +2.12] CI contains 0 |
| a2l − v2_pe | per-seed means | TPR@1e-2 | -0.69 [-2.17, +0.51] CI contains 0 |
| a2l − v2_pe | per-seed means | AUC | -0.31 [-0.44, -0.18] **CI excludes 0** |
| a2l − v2_pe | per-seed means | pAUC@1e-3 | -10.06 [-17.12, -0.83] **CI excludes 0** |
| a2l − v2_pe | 10-seed ensembles | **pAUC@1e-2** | -3.29 [-5.80, -0.71] **CI excludes 0** |
| a2l − v2_pe | 10-seed ensembles | TPR@1e-3 | +1.28 [-7.60, +7.30] CI contains 0 |
| a2l − v2_pe | 10-seed ensembles | TPR@1e-2 | -0.44 [-1.34, +1.07] CI contains 0 |
| a2l − v2_pe | 10-seed ensembles | AUC | +0.06 [-0.05, +0.17] CI contains 0 |
| a2l − v2_pe | 10-seed ensembles | pAUC@1e-3 | -6.17 [-19.42, +4.66] CI contains 0 |
| a2l − b2l | per-seed means | **pAUC@1e-2** | +7.08 [+4.07, +10.23] **CI excludes 0** |
| a2l − b2l | per-seed means | TPR@1e-3 | +9.66 [+0.60, +18.39] **CI excludes 0** |
| a2l − b2l | per-seed means | TPR@1e-2 | +5.66 [+3.43, +7.58] **CI excludes 0** |
| a2l − b2l | per-seed means | AUC | -0.70 [-0.83, -0.56] **CI excludes 0** |
| a2l − b2l | per-seed means | pAUC@1e-3 | +5.89 [-3.67, +16.64] CI contains 0 |
| a2l − b2l | 10-seed ensembles | **pAUC@1e-2** | +4.64 [+1.48, +8.02] **CI excludes 0** |
| a2l − b2l | 10-seed ensembles | TPR@1e-3 | +10.71 [+4.91, +16.25] **CI excludes 0** |
| a2l − b2l | 10-seed ensembles | TPR@1e-2 | +5.17 [+3.90, +6.40] **CI excludes 0** |
| a2l − b2l | 10-seed ensembles | AUC | -0.30 [-0.42, -0.17] **CI excludes 0** |
| a2l − b2l | 10-seed ensembles | pAUC@1e-3 | +8.59 [-6.09, +24.61] CI contains 0 |
| b2l − v2_pe | per-seed means | **pAUC@1e-2** | -8.85 [-11.12, -6.48] **CI excludes 0** |
| b2l − v2_pe | per-seed means | TPR@1e-3 | -13.37 [-21.50, -7.86] **CI excludes 0** |
| b2l − v2_pe | per-seed means | TPR@1e-2 | -6.35 [-8.11, -4.40] **CI excludes 0** |
| b2l − v2_pe | per-seed means | AUC | +0.39 [+0.27, +0.51] **CI excludes 0** |
| b2l − v2_pe | per-seed means | pAUC@1e-3 | -15.95 [-23.25, -9.58] **CI excludes 0** |
| b2l − v2_pe | 10-seed ensembles | **pAUC@1e-2** | -7.93 [-10.62, -5.58] **CI excludes 0** |
| b2l − v2_pe | 10-seed ensembles | TPR@1e-3 | -9.44 [-18.92, -3.42] **CI excludes 0** |
| b2l − v2_pe | 10-seed ensembles | TPR@1e-2 | -5.61 [-6.60, -4.00] **CI excludes 0** |
| b2l − v2_pe | 10-seed ensembles | AUC | +0.36 [+0.23, +0.49] **CI excludes 0** |
| b2l − v2_pe | 10-seed ensembles | pAUC@1e-3 | -14.76 [-27.73, -5.09] **CI excludes 0** |
| b2l − attbal | per-seed means | **pAUC@1e-2** | -9.08 [-11.92, -6.36] **CI excludes 0** |
| b2l − attbal | per-seed means | TPR@1e-3 | -16.28 [-25.07, -9.69] **CI excludes 0** |
| b2l − attbal | per-seed means | TPR@1e-2 | -4.70 [-6.69, -2.43] **CI excludes 0** |
| b2l − attbal | per-seed means | AUC | -0.29 [-0.39, -0.18] **CI excludes 0** |
| b2l − attbal | per-seed means | pAUC@1e-3 | -17.27 [-26.97, -7.73] **CI excludes 0** |
| b2l − attbal | 10-seed ensembles | **pAUC@1e-2** | -4.51 [-7.60, -1.67] **CI excludes 0** |
| b2l − attbal | 10-seed ensembles | TPR@1e-3 | -7.15 [-17.66, -4.00] **CI excludes 0** |
| b2l − attbal | 10-seed ensembles | TPR@1e-2 | -1.86 [-2.96, -0.46] **CI excludes 0** |
| b2l − attbal | 10-seed ensembles | AUC | -0.39 [-0.50, -0.28] **CI excludes 0** |
| b2l − attbal | 10-seed ensembles | pAUC@1e-3 | -10.41 [-24.49, +1.34] CI contains 0 |


### Per-seed paired differences of the primary metric (same seed index; points ×100)

| pair | s0 | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9 | mean ± std | seeds > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a2l − attbal | -5.2 | -6.6 | -5.0 | +1.5 | -1.5 | +1.5 | -2.1 | -0.1 | -1.7 | -0.6 | -1.99 ± 2.80 | 2/10 |
| a2l − v2_pe | -2.5 | -1.8 | +2.7 | -0.1 | -2.6 | -4.2 | +0.3 | -3.9 | -4.0 | -1.5 | -1.77 ± 2.22 | 2/10 |
| a2l − b2l | +0.9 | +15.1 | +3.5 | +9.7 | +7.9 | +16.6 | +0.1 | +4.0 | +0.6 | +12.4 | +7.08 ± 6.16 | 10/10 |
| b2l − v2_pe | -3.5 | -16.9 | -0.8 | -9.8 | -10.5 | -20.8 | +0.2 | -8.0 | -4.6 | -13.9 | -8.85 ± 6.93 | 1/10 |
| b2l − attbal | -6.1 | -21.8 | -8.5 | -8.2 | -9.4 | -15.1 | -2.2 | -4.2 | -2.3 | -13.1 | -9.08 ± 6.15 | 0/10 |


**Claim rule (EVAL_PROTOCOL.md 5) on pAUC@1e-2, stratified bootstrap of the per-seed means:**

- a2l vs attbal: **RESOLVED, a2l worse** (CI excludes 0; negative in 8/10 seeds)
- a2l vs v2_pe: not resolved (CI contains 0; positive in 2/10, negative in 8/10 seeds)
- a2l vs b2l: **RESOLVED, a2l better** (CI excludes 0; positive in 10/10 seeds)
- b2l vs v2_pe: **RESOLVED, b2l worse** (CI excludes 0; negative in 9/10 seeds)
- b2l vs attbal: **RESOLVED, b2l worse** (CI excludes 0; negative in 10/10 seeds)

### Cluster bootstrap over hash_apis groups (2,509 groups; cells (group, class) resampled; points ×100)

| difference | metric | mean difference | 95% CI (cluster) | seeds > 0 | outcome |
|---|---|---|---|---|---|
| a2l − attbal | pAUC@1e-2 (primary) | -1.99 | [-4.86, +0.52] | 2/10 | not resolved |
| a2l − attbal | TPR@1e-2 | +0.96 | [-0.84, +3.73] | 7/10 | CI contains 0 (descriptive) |
| a2l − attbal | TPR@1e-3 | -6.62 | [-17.62, +0.70] | 3/10 | CI contains 0 (descriptive) |
| a2l − attbal | AUC | -0.99 | [-1.65, -0.50] | 1/10 | CI excludes 0 (descriptive) |
| a2l − v2_pe | pAUC@1e-2 (primary) | -1.77 | [-7.86, +3.01] | 2/10 | not resolved |
| a2l − v2_pe | TPR@1e-2 | -0.69 | [-5.23, +3.11] | 5/10 | CI contains 0 (descriptive) |
| a2l − v2_pe | TPR@1e-3 | -3.71 | [-18.22, +6.05] | 4/10 | CI contains 0 (descriptive) |
| a2l − v2_pe | AUC | -0.31 | [-1.26, +0.77] | 3/10 | CI contains 0 (descriptive) |
| a2l − b2l | pAUC@1e-2 (primary) | +7.08 | [-1.48, +15.78] | 10/10 | not resolved |
| a2l − b2l | TPR@1e-2 | +5.66 | [-1.73, +13.05] | 8/10 | CI contains 0 (descriptive) |
| a2l − b2l | TPR@1e-3 | +9.66 | [-6.10, +22.91] | 7/10 | CI contains 0 (descriptive) |
| a2l − b2l | AUC | -0.70 | [-1.56, +0.01] | 1/10 | CI contains 0 (descriptive) |
| b2l − v2_pe | pAUC@1e-2 (primary) | -8.85 | [-14.99, -3.18] | 1/10 | **meets the rule** |
| b2l − v2_pe | TPR@1e-2 | -6.35 | [-11.75, -1.20] | 1/10 | CI excludes 0 (descriptive) |
| b2l − v2_pe | TPR@1e-3 | -13.37 | [-23.97, -4.77] | 3/10 | CI excludes 0 (descriptive) |
| b2l − v2_pe | AUC | +0.39 | [-0.57, +1.74] | 8/10 | CI contains 0 (descriptive) |
| b2l − attbal | pAUC@1e-2 (primary) | -9.08 | [-17.13, +0.03] | 0/10 | not resolved |
| b2l − attbal | TPR@1e-2 | -4.70 | [-12.68, +4.67] | 2/10 | CI contains 0 (descriptive) |
| b2l − attbal | TPR@1e-3 | -16.28 | [-29.28, -4.62] | 0/10 | CI excludes 0 (descriptive) |
| b2l − attbal | AUC | -0.29 | [-0.95, +0.35] | 3/10 | CI contains 0 (descriptive) |


### Detection rate per family at the 1% FPR threshold of each model and seed (April; mean ± std over 10 seeds, %). `clean` and `windows_syswow64` rows are false-positive rates.

| family | n | **ATT+bal-2L (A)** | B: 2L without padding | ATT+bal | v2-PE |
|---|---|---|---|---|---|
| backdoor | 1940 | 81.8 ± 1.6 | 78.7 ± 5.2 | 82.1 ± 1.9 | 83.7 ± 2.4 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 79.5 ± 8.6 | 79.4 ± 6.8 | 72.8 ± 6.1 | 81.7 ± 6.8 |
| dropper | 252 | 83.2 ± 1.9 | 80.0 ± 3.4 | 81.9 ± 5.7 | 80.1 ± 2.4 |
| keylogger | 1041 | 86.8 ± 2.4 | 81.2 ± 3.4 | 87.0 ± 2.5 | 87.1 ± 6.1 |
| ransomware | 2139 | 72.2 ± 3.9 | 60.3 ± 2.9 | 72.9 ± 2.2 | 70.8 ± 4.9 |
| rat | 1258 | 86.6 ± 1.2 | 74.6 ± 15.5 | 87.8 ± 2.8 | 89.2 ± 2.0 |
| trojan | 1085 | 81.7 ± 1.1 | 81.8 ± 3.1 | 80.4 ± 2.5 | 80.9 ± 1.2 |
| windows_syswow64 | 59 | 0.2 ± 0.5 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold. Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| **ATT+bal-2L (A)** | 4/10 | -0.4 (IQR -1.1 to +0.3) | 86.8 ± 2.1 | 79.5 ± 8.6 |
| B: 2L without padding | 10/10 | +2.8 (IQR +1.7 to +3.3) | 75.5 ± 8.1 | 79.4 ± 6.8 |
| ATT+bal | 1/10 | -3.2 (IQR -4.6 to -1.6) | 84.6 ± 3.0 | 72.8 ± 6.1 |
| v2-PE | 8/10 | +7.7 (IQR +1.2 to +19.7) | 82.1 ± 2.4 | 81.7 ± 6.8 |

