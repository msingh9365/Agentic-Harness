# Selection from validation numbers only (NOTES 19.5)

## Model A

| cell | init | lr | epoch | mean val pAUC@1e-2 | SE | mean val loss | min val AUC | collapsed | within 1 SE of best |
|---|---|---|---|---|---|---|---|---|---|
| A_scratch_lr1e-3 | scratch | 0.001 | 1 | 0.8347 | 0.0577 | 0.0701 | 0.9921 | no |  |
| A_scratch_lr1e-3 | scratch | 0.001 | 2 | 0.8983 | 0.0182 | 0.0591 | 0.9964 | no |  |
| A_scratch_lr1e-3 | scratch | 0.001 | 3 | 0.9434 | 0.0049 | 0.0538 | 0.9974 | no | yes |
| A_scratch_lr2e-3 | scratch | 0.002 | 1 | 0.8718 | 0.0633 | 0.0591 | 0.9912 | no |  |
| A_scratch_lr2e-3 | scratch | 0.002 | 2 | 0.9023 | 0.0295 | 0.0530 | 0.9953 | no |  |
| A_scratch_lr2e-3 | scratch | 0.002 | 3 | 0.9292 | 0.0102 | 0.0511 | 0.9972 | no |  |
| A_warm_lr1e-3 | warm | 0.001 | 1 | 0.9438 | 0.0051 | 0.0568 | 0.9958 | no | **chosen** |
| A_warm_lr1e-3 | warm | 0.001 | 2 | 0.8526 | 0.0390 | 0.0628 | 0.9942 | no |  |
| A_warm_lr1e-3 | warm | 0.001 | 3 | 0.9249 | 0.0119 | 0.0567 | 0.9961 | no |  |
| A_warm_lr2e-3 | warm | 0.002 | 1 | 0.9218 | 0.0114 | 0.0563 | 0.9956 | no |  |
| A_warm_lr2e-3 | warm | 0.002 | 2 | 0.8116 | 0.0714 | 0.0618 | 0.9906 | no |  |
| A_warm_lr2e-3 | warm | 0.002 | 3 | 0.8898 | 0.0240 | 0.0609 | 0.9952 | no |  |

CHOSEN A: cell=A_warm_lr1e-3 init=warm lr=0.001 epoch=1 (mean val pAUC@1e-2 0.9438, SE 0.0051)

## Model B

| cell | init | lr | epoch | mean val pAUC@1e-2 | SE | mean val loss | min val AUC | collapsed | within 1 SE of best |
|---|---|---|---|---|---|---|---|---|---|
| B_lr1e-3 | scratch | 0.001 | 1 | 0.9188 | 0.0290 | 0.0518 | 0.9956 | no |  |
| B_lr1e-3 | scratch | 0.001 | 2 | 0.8885 | 0.0219 | 0.0481 | 0.9970 | no |  |
| B_lr1e-3 | scratch | 0.001 | 3 | 0.9631 | 0.0051 | 0.0522 | 0.9967 | no | best |
| B_lr2e-3 | scratch | 0.002 | 1 | 0.9585 | 0.0032 | 0.0448 | 0.9983 | no | **chosen** |
| B_lr2e-3 | scratch | 0.002 | 2 | 0.9418 | 0.0118 | 0.0479 | 0.9974 | no |  |
| B_lr2e-3 | scratch | 0.002 | 3 | 0.9349 | 0.0123 | 0.0514 | 0.9962 | no |  |

CHOSEN B: cell=B_lr2e-3 init=scratch lr=0.002 epoch=1 (mean val pAUC@1e-2 0.9585, SE 0.0032)
