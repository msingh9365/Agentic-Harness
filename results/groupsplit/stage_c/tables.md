### Clean April test: per-seed mean ± std (10 seeds, logit-ranked; one evaluation per model)

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| **ATT+bal, new split (lr 1e-3, p 0.5, epoch 3)** | 10 | 0.503 ± 0.048 | 0.665 ± 0.064 | 0.9386 ± 0.0127 | 0.860 ± 0.033 | 0.590 ± 0.052 | 0.379 ± 0.063 |
| **v2-PE, new split (lr 2e-3, epoch 1)** | 10 | 0.479 ± 0.036 | 0.732 ± 0.027 | 0.9599 ± 0.0122 | 0.880 ± 0.018 | 0.634 ± 0.024 | 0.366 ± 0.066 |
| ATT+bal, old validation slice (lr 2e-3, p 0.5, epoch 2) | 10 | 0.572 ± 0.061 | 0.795 ± 0.020 | 0.9713 ± 0.0066 | 0.913 ± 0.017 | 0.707 ± 0.017 | 0.457 ± 0.041 |
| v2-PE, old validation slice (lr 2e-3, epoch 2) | 10 | 0.543 ± 0.063 | 0.811 ± 0.023 | 0.9644 ± 0.0093 | 0.915 ± 0.012 | 0.705 ± 0.031 | 0.444 ± 0.076 |


10-seed ensembles (mean logit):

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| **ATT+bal, new split (lr 1e-3, p 0.5, epoch 3)** | 0.537 | 0.711 | 0.9470 | 0.857 | **0.647** | 0.442 |
| **v2-PE, new split (lr 2e-3, epoch 1)** | 0.603 | 0.756 | 0.9668 | 0.899 | **0.689** | 0.529 |
| ATT+bal, old validation slice (lr 2e-3, p 0.5, epoch 2) | 0.583 | 0.814 | 0.9780 | 0.926 | **0.734** | 0.503 |
| v2-PE, old validation slice (lr 2e-3, epoch 2) | 0.606 | 0.851 | 0.9705 | 0.927 | **0.768** | 0.546 |


Group-split validation slice (8,718 reports; per-seed mean ± std; the old models have no validation logits on this slice):

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| **v2-PE, new split (lr 2e-3, epoch 1)** | 10 | 0.436 ± 0.044 | 0.528 ± 0.034 | 0.9334 ± 0.0164 | 0.802 ± 0.064 | 0.484 ± 0.026 | 0.353 ± 0.126 |
| **ATT+bal, new split (lr 1e-3, p 0.5, epoch 3)** | 10 | 0.431 ± 0.029 | 0.508 ± 0.022 | 0.9133 ± 0.0140 | 0.778 ± 0.027 | 0.470 ± 0.019 | 0.374 ± 0.031 |


### Differences, stratified bootstrap (1000 resamples, numpy seed 0; points ×100). Pairs: new ATT+bal vs new v2-PE (the claim of this stage); new vs old for each model; old ATT+bal vs old v2-PE

| difference | statistic | metric | difference in points, 95% CI |
|---|---|---|---|
| gs_attbal − gs_v2pe | per-seed means | **pAUC@1e-2** | -4.36 [-6.46, -2.15] **CI excludes 0** |
| gs_attbal − gs_v2pe | per-seed means | TPR@1e-3 | +2.42 [-6.01, +8.09] CI contains 0 |
| gs_attbal − gs_v2pe | per-seed means | TPR@1e-2 | -6.68 [-8.29, -4.77] **CI excludes 0** |
| gs_attbal − gs_v2pe | per-seed means | AUC | -2.13 [-2.32, -1.95] **CI excludes 0** |
| gs_attbal − gs_v2pe | per-seed means | pAUC@1e-3 | +1.27 [-7.03, +8.99] CI contains 0 |
| gs_attbal − gs_v2pe | 10-seed ensembles | **pAUC@1e-2** | -4.16 [-6.28, -2.11] **CI excludes 0** |
| gs_attbal − gs_v2pe | 10-seed ensembles | TPR@1e-3 | -6.60 [-17.11, +1.47] CI contains 0 |
| gs_attbal − gs_v2pe | 10-seed ensembles | TPR@1e-2 | -4.44 [-7.79, -2.98] **CI excludes 0** |
| gs_attbal − gs_v2pe | 10-seed ensembles | AUC | -1.99 [-2.17, -1.79] **CI excludes 0** |
| gs_attbal − gs_v2pe | 10-seed ensembles | pAUC@1e-3 | -8.68 [-17.40, +1.28] CI contains 0 |
| gs_v2pe − v2_pe | per-seed means | **pAUC@1e-2** | -7.09 [-8.33, -5.78] **CI excludes 0** |
| gs_v2pe − v2_pe | per-seed means | TPR@1e-3 | -6.40 [-9.96, -3.40] **CI excludes 0** |
| gs_v2pe − v2_pe | per-seed means | TPR@1e-2 | -7.89 [-9.02, -6.88] **CI excludes 0** |
| gs_v2pe − v2_pe | per-seed means | AUC | -0.45 [-0.59, -0.32] **CI excludes 0** |
| gs_v2pe − v2_pe | per-seed means | pAUC@1e-3 | -7.78 [-10.70, -4.59] **CI excludes 0** |
| gs_v2pe − v2_pe | 10-seed ensembles | **pAUC@1e-2** | -7.95 [-9.25, -6.42] **CI excludes 0** |
| gs_v2pe − v2_pe | 10-seed ensembles | TPR@1e-3 | -0.31 [-9.28, +4.57] CI contains 0 |
| gs_v2pe − v2_pe | 10-seed ensembles | TPR@1e-2 | -9.54 [-10.68, -6.90] **CI excludes 0** |
| gs_v2pe − v2_pe | 10-seed ensembles | AUC | -0.37 [-0.54, -0.21] **CI excludes 0** |
| gs_v2pe − v2_pe | 10-seed ensembles | pAUC@1e-3 | -1.76 [-7.99, +2.53] CI contains 0 |
| gs_attbal − attbal | per-seed means | **pAUC@1e-2** | -11.68 [-13.56, -9.59] **CI excludes 0** |
| gs_attbal − attbal | per-seed means | TPR@1e-3 | -6.90 [-13.53, -2.01] **CI excludes 0** |
| gs_attbal − attbal | per-seed means | TPR@1e-2 | -12.93 [-14.17, -11.21] **CI excludes 0** |
| gs_attbal − attbal | per-seed means | AUC | -3.27 [-3.48, -3.04] **CI excludes 0** |
| gs_attbal − attbal | per-seed means | pAUC@1e-3 | -7.83 [-17.37, +2.29] CI contains 0 |
| gs_attbal − attbal | 10-seed ensembles | **pAUC@1e-2** | -8.68 [-10.58, -6.59] **CI excludes 0** |
| gs_attbal − attbal | 10-seed ensembles | TPR@1e-3 | -4.62 [-15.20, +0.99] CI contains 0 |
| gs_attbal − attbal | 10-seed ensembles | TPR@1e-2 | -10.24 [-11.98, -9.37] **CI excludes 0** |
| gs_attbal − attbal | 10-seed ensembles | AUC | -3.11 [-3.32, -2.87] **CI excludes 0** |
| gs_attbal − attbal | 10-seed ensembles | pAUC@1e-3 | -6.09 [-16.05, +4.72] CI contains 0 |
| attbal − v2_pe | per-seed means | **pAUC@1e-2** | +0.23 [-1.70, +2.09] CI contains 0 |
| attbal − v2_pe | per-seed means | TPR@1e-3 | +2.91 [-2.20, +7.16] CI contains 0 |
| attbal − v2_pe | per-seed means | TPR@1e-2 | -1.65 [-2.95, -0.67] **CI excludes 0** |
| attbal − v2_pe | per-seed means | AUC | +0.68 [+0.57, +0.79] **CI excludes 0** |
| attbal − v2_pe | per-seed means | pAUC@1e-3 | +1.32 [-6.47, +9.05] CI contains 0 |
| attbal − v2_pe | 10-seed ensembles | **pAUC@1e-2** | -3.42 [-5.37, -1.55] **CI excludes 0** |
| attbal − v2_pe | 10-seed ensembles | TPR@1e-3 | -2.29 [-7.12, +7.25] CI contains 0 |
| attbal − v2_pe | 10-seed ensembles | TPR@1e-2 | -3.75 [-4.73, -2.18] **CI excludes 0** |
| attbal − v2_pe | 10-seed ensembles | AUC | +0.75 [+0.62, +0.87] **CI excludes 0** |
| attbal − v2_pe | 10-seed ensembles | pAUC@1e-3 | -4.35 [-13.45, +3.91] CI contains 0 |


### Per-seed paired differences of the primary metric (same seed index; points ×100)

| pair | s0 | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9 | mean ± std | seeds > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gs_attbal − gs_v2pe | -4.8 | -7.7 | +3.2 | +5.7 | +1.2 | -3.5 | -8.3 | -16.3 | -0.5 | -12.6 | -4.36 ± 7.00 | 3/10 |
| gs_v2pe − v2_pe | -6.5 | -6.8 | -4.9 | -10.5 | -7.6 | -9.6 | -4.7 | -9.0 | -8.4 | -2.8 | -7.09 ± 2.44 | 0/10 |
| gs_attbal − attbal | -14.0 | -19.3 | -9.4 | -3.2 | -5.3 | -7.4 | -15.4 | -21.5 | -6.7 | -14.6 | -11.68 ± 6.17 | 0/10 |
| attbal − v2_pe | +2.7 | +4.8 | +7.7 | -1.6 | -1.1 | -5.7 | +2.4 | -3.8 | -2.3 | -0.8 | +0.23 ± 4.11 | 4/10 |


**Claim rule (EVAL_PROTOCOL.md 5) on pAUC@1e-2, stratified bootstrap of the per-seed means:** (the seeds of the new and the old models are different training runs: the 'same seed index' pairing is only a pairing of 10 values with 10 values)

- gs_attbal vs gs_v2pe: **RESOLVED, gs_attbal worse** (CI excludes 0; negative in 7/10 seeds)
- gs_v2pe vs v2_pe: **RESOLVED, gs_v2pe worse** (CI excludes 0; negative in 10/10 seeds)
- gs_attbal vs attbal: **RESOLVED, gs_attbal worse** (CI excludes 0; negative in 10/10 seeds)
- attbal vs v2_pe: not resolved (CI contains 0; positive in 4/10, negative in 6/10 seeds)

### Cluster bootstrap over hash_apis groups (2,509 April groups; cells (group, class) resampled; points ×100)

| difference | metric | mean difference | 95% CI (cluster) | seeds > 0 | outcome |
|---|---|---|---|---|---|
| gs_attbal − gs_v2pe | pAUC@1e-2 (primary) | -4.36 | [-9.40, +0.81] | 3/10 | not resolved |
| gs_attbal − gs_v2pe | TPR@1e-2 | -6.68 | [-12.05, -1.35] | 2/10 | CI excludes 0 (descriptive) |
| gs_attbal − gs_v2pe | TPR@1e-3 | +2.42 | [-8.98, +10.96] | 7/10 | CI contains 0 (descriptive) |
| gs_attbal − gs_v2pe | AUC | -2.13 | [-4.31, -0.41] | 0/10 | CI excludes 0 (descriptive) |
| gs_v2pe − v2_pe | pAUC@1e-2 (primary) | -7.09 | [-14.90, -1.45] | 0/10 | **meets the rule** |
| gs_v2pe − v2_pe | TPR@1e-2 | -7.89 | [-15.32, -1.96] | 0/10 | CI excludes 0 (descriptive) |
| gs_v2pe − v2_pe | TPR@1e-3 | -6.40 | [-15.12, -0.17] | 2/10 | CI excludes 0 (descriptive) |
| gs_v2pe − v2_pe | AUC | -0.45 | [-1.76, +0.84] | 5/10 | CI contains 0 (descriptive) |
| gs_attbal − attbal | pAUC@1e-2 (primary) | -11.68 | [-19.68, -4.61] | 0/10 | **meets the rule** |
| gs_attbal − attbal | TPR@1e-2 | -12.93 | [-20.10, -5.61] | 0/10 | CI excludes 0 (descriptive) |
| gs_attbal − attbal | TPR@1e-3 | -6.90 | [-17.82, +1.92] | 2/10 | CI contains 0 (descriptive) |
| gs_attbal − attbal | AUC | -3.27 | [-6.41, -0.96] | 0/10 | CI excludes 0 (descriptive) |
| attbal − v2_pe | pAUC@1e-2 (primary) | +0.23 | [-5.31, +4.53] | 4/10 | not resolved |
| attbal − v2_pe | TPR@1e-2 | -1.65 | [-7.30, +3.05] | 3/10 | CI contains 0 (descriptive) |
| attbal − v2_pe | TPR@1e-3 | +2.91 | [-6.03, +9.91] | 6/10 | CI contains 0 (descriptive) |
| attbal − v2_pe | AUC | +0.68 | [-0.17, +2.05] | 7/10 | CI contains 0 (descriptive) |


### Detection rate per family at the 1% FPR threshold of each model and seed (April; mean ± std over 10 seeds, %). `clean` and `windows_syswow64` rows are false-positive rates.

| family | n | **ATT+bal, new split (lr 1e-3, p 0.5, epoch 3)** | **v2-PE, new split (lr 2e-3, epoch 1)** | ATT+bal, old validation slice (lr 2e-3, p 0.5, epoch 2) | v2-PE, old validation slice (lr 2e-3, epoch 2) |
|---|---|---|---|---|---|
| backdoor | 1940 | 76.3 ± 7.7 | 81.5 ± 2.3 | 82.1 ± 1.9 | 83.7 ± 2.4 |
| clean | 7944 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 |
| coinminer | 1684 | 61.7 ± 6.8 | 76.7 ± 7.6 | 72.8 ± 6.1 | 81.7 ± 6.8 |
| dropper | 252 | 78.7 ± 6.3 | 73.7 ± 5.4 | 81.9 ± 5.7 | 80.1 ± 2.4 |
| keylogger | 1041 | 63.4 ± 6.6 | 70.3 ± 3.0 | 87.0 ± 2.5 | 87.1 ± 6.1 |
| ransomware | 2139 | 61.7 ± 6.8 | 68.2 ± 6.8 | 72.9 ± 2.2 | 70.8 ± 4.9 |
| rat | 1258 | 69.8 ± 11.2 | 76.5 ± 1.3 | 87.8 ± 2.8 | 89.2 ± 2.0 |
| trojan | 1085 | 62.4 ± 5.9 | 61.7 ± 5.6 | 80.4 ± 2.5 | 80.9 ± 1.2 |
| windows_syswow64 | 59 | 0.3 ± 0.7 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 |


### The coinminer cluster (hash_apis d91b96b4…, 265 April reports with the same first 512 tokens of the OLD tokenizer; one input counted 265 times)

Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold. Margin = median cluster logit minus the threshold (positive = flagged).

| model | seeds flagging the cluster | median margin (logit) | TPR of the other 1419 coinminer reports (%) | TPR of all 1684 coinminer reports (%) |
|---|---|---|---|---|
| **ATT+bal, new split (lr 1e-3, p 0.5, epoch 3)** | 0/10 | -6.6 (IQR -8.4 to -4.4) | 73.2 ± 8.0 | 61.7 ± 6.8 |
| **v2-PE, new split (lr 2e-3, epoch 1)** | 7/10 | +1.6 (IQR -1.2 to +4.7) | 77.9 ± 1.6 | 76.7 ± 7.6 |
| ATT+bal, old validation slice (lr 2e-3, p 0.5, epoch 2) | 1/10 | -3.2 (IQR -4.6 to -1.6) | 84.6 ± 3.0 | 72.8 ± 6.1 |
| v2-PE, old validation slice (lr 2e-3, epoch 2) | 8/10 | +7.7 (IQR +1.2 to +19.7) | 82.1 ± 2.4 | 81.7 ± 6.8 |

