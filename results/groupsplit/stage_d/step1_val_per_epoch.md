### Step 1: validation metrics per epoch (group-split slice, 8,718 reports: 3,161 benign, 5,557 malware; 10 seeds; mean ± SD)

**v2-PE (lr 2e-3)** (epochs 1-4; the Stage C choice was epoch 1; recomputed loss and pAUC agree with the logged values to 8.9e-16)

| epoch | val pAUC@1e-2 | val TPR@1e-2 | val AUC | val loss | mean abs logit |
|---|---|---|---|---|---|
| 1 (Stage C choice) (peak) | 0.4843 ± 0.0261 | 0.5284 ± 0.0335 | 0.9334 ± 0.0164 | 0.983 ± 0.472 | 15.1 |
| 2 | 0.4603 ± 0.0491 | 0.5050 ± 0.0714 | 0.9383 ± 0.0074 | 1.559 ± 0.461 | 21.4 |
| 3 | 0.4551 ± 0.0598 | 0.4898 ± 0.0724 | 0.9257 ± 0.0165 | 2.317 ± 0.836 | 31.9 |
| 4 | 0.4597 ± 0.1022 | 0.5147 ± 0.1222 | 0.9251 ± 0.0176 | 3.840 ± 1.467 | 47.2 |

Peak of the mean validation pAUC@1e-2: epoch 1. Best epoch per seed (seeds 0-9): [1, 1, 3, 1, 4, 1, 3, 4, 2, 3] (counts: epoch 1: 4, epoch 2: 1, epoch 3: 3, epoch 4: 2).
From epoch 1 to epoch 4: mean validation pAUC 0.4843 -> 0.4597 (per-seed change -0.0245 ± 0.0964; 6/10 seeds lower); mean validation loss 0.983 -> 3.840; mean AUC 0.9334 -> 0.9251; mean |logit| 15.1 -> 47.2.
Spearman correlation of validation pAUC with validation loss: over the 4 epoch means -0.80; over all 40 seed-epoch points -0.04; within a seed (mean of 10) -0.28. (Negative = pAUC falls as loss rises.)

**ATT+bal (lr 1e-3, p 0.5)** (epochs 1-6; the Stage C choice was epoch 3; recomputed loss and pAUC agree with the logged values to 4.4e-16)

| epoch | val pAUC@1e-2 | val TPR@1e-2 | val AUC | val loss | mean abs logit |
|---|---|---|---|---|---|
| 1 | 0.4670 ± 0.0173 | 0.5037 ± 0.0234 | 0.9197 ± 0.0174 | 0.859 ± 0.338 | 8.6 |
| 2 | 0.4656 ± 0.0176 | 0.5111 ± 0.0248 | 0.9162 ± 0.0199 | 0.956 ± 0.277 | 9.1 |
| 3 (Stage C choice) (peak) | 0.4704 ± 0.0190 | 0.5083 ± 0.0216 | 0.9133 ± 0.0140 | 1.098 ± 0.141 | 11.1 |
| 4 | 0.4674 ± 0.0144 | 0.5090 ± 0.0160 | 0.9024 ± 0.0171 | 1.518 ± 0.565 | 13.1 |
| 5 | 0.4626 ± 0.0155 | 0.4993 ± 0.0170 | 0.8892 ± 0.0221 | 1.671 ± 0.471 | 13.7 |
| 6 | 0.4602 ± 0.0177 | 0.5015 ± 0.0224 | 0.8895 ± 0.0160 | 1.689 ± 0.245 | 13.9 |

Peak of the mean validation pAUC@1e-2: epoch 3. Best epoch per seed (seeds 0-9): [5, 2, 2, 3, 4, 5, 1, 2, 1, 3] (counts: epoch 1: 2, epoch 2: 3, epoch 3: 2, epoch 4: 1, epoch 5: 2, epoch 6: 0).
From epoch 1 to epoch 6: mean validation pAUC 0.4670 -> 0.4602 (per-seed change -0.0068 ± 0.0134; 6/10 seeds lower); mean validation loss 0.859 -> 1.689; mean AUC 0.9197 -> 0.8895; mean |logit| 8.6 -> 13.9.
Spearman correlation of validation pAUC with validation loss: over the 6 epoch means -0.54; over all 60 seed-epoch points -0.14; within a seed (mean of 10) -0.13. (Negative = pAUC falls as loss rises.)

