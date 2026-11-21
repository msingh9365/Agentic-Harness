### M2: validation numbers of all candidates (5 seeds; group-split slice, 8,718 reports)

| cell | lr | init | epoch | val pAUC@1e-2 | SE | val AUC (min over seeds) | val loss | train loss | R20 (descriptive) | note |
|---|---|---|---|---|---|---|---|---|---|---|
| fm2_lr1e-3 | 0.001 | scratch | 1 | 0.5784 | 0.0243 | 0.9577 | 0.355 | 0.1143 | 0.2750 | **CHOSEN** |
| fm2_lr1e-3 | 0.001 | scratch | 2 | 0.4888 | 0.0525 | 0.9510 | 0.465 | 0.0339 | 0.2626 |  |
| fm2_lr1e-3 | 0.001 | scratch | 3 | 0.4001 | 0.1058 | 0.9272 | 0.670 | 0.0221 | 0.1927 |  |
| fm2_lr2e-3 | 0.002 | scratch | 1 | 0.5524 | 0.0738 | 0.9461 | 0.425 | 0.0969 | 0.1989 |  |
| fm2_lr2e-3 | 0.002 | scratch | 2 | 0.6035 | 0.0252 | 0.9459 | 0.483 | 0.0311 | 0.2894 | best |
| fm2_lr2e-3 | 0.002 | scratch | 3 | 0.5212 | 0.0213 | 0.9344 | 0.664 | 0.0209 | 0.2806 |  |

**Chosen for M2: fm2_lr1e-3, epoch 1** (lr 0.001, init scratch); best by mean validation pAUC@1e-2: fm2_lr2e-3 epoch 2 (0.6035, SE 0.0252); tied with best: fm2_lr1e-3/1, fm2_lr2e-3/2

### M4: validation numbers of all candidates (5 seeds; group-split slice, 8,718 reports)

| cell | lr | init | epoch | val pAUC@1e-2 | SE | val AUC (min over seeds) | val loss | train loss | R20 (descriptive) | note |
|---|---|---|---|---|---|---|---|---|---|---|
| fm4_scratch_lr1e-3 | 0.001 | scratch | 1 | 0.4537 | 0.0095 | 0.9472 | 0.276 | 0.1505 | 0.4783 | **CHOSEN** best |
| fm4_scratch_lr1e-3 | 0.001 | scratch | 2 | 0.4293 | 0.0479 | 0.9452 | 0.379 | 0.0581 | 0.5558 |  |
| fm4_scratch_lr1e-3 | 0.001 | scratch | 3 | 0.3473 | 0.0375 | 0.9241 | 0.458 | 0.0450 | 0.5337 |  |
| fm4_scratch_lr2e-3 | 0.002 | scratch | 1 | 0.4405 | 0.0352 | 0.9219 | 0.322 | 0.1304 | 0.5187 |  |
| fm4_scratch_lr2e-3 | 0.002 | scratch | 2 | 0.4034 | 0.0386 | 0.9185 | 0.447 | 0.0553 | 0.4770 |  |
| fm4_scratch_lr2e-3 | 0.002 | scratch | 3 | 0.3988 | 0.0196 | 0.8960 | 0.643 | 0.0439 | 0.4880 |  |
| fm4_warm_lr1e-3 | 0.001 | warm | 1 | 0.4163 | 0.0220 | 0.9212 | 0.793 | 0.0468 | 0.4599 |  |
| fm4_warm_lr1e-3 | 0.001 | warm | 2 | 0.3774 | 0.0460 | 0.9092 | 0.870 | 0.0337 | 0.4132 |  |
| fm4_warm_lr1e-3 | 0.001 | warm | 3 | 0.3767 | 0.0683 | 0.8994 | 0.854 | 0.0299 | 0.3925 |  |
| fm4_warm_lr2e-3 | 0.002 | warm | 1 | 0.3218 | 0.0723 | 0.9253 | 0.664 | 0.0548 | 0.3994 |  |
| fm4_warm_lr2e-3 | 0.002 | warm | 2 | 0.3985 | 0.0309 | 0.8998 | 0.638 | 0.0411 | 0.4109 |  |
| fm4_warm_lr2e-3 | 0.002 | warm | 3 | 0.3250 | 0.0366 | 0.8236 | 0.795 | 0.0358 | 0.3821 |  |

**Chosen for M4: fm4_scratch_lr1e-3, epoch 1** (lr 0.001, init scratch); best by mean validation pAUC@1e-2: fm4_scratch_lr1e-3 epoch 1 (0.4537, SE 0.0095); tied with best: fm4_scratch_lr1e-3/1

