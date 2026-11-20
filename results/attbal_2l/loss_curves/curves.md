| model | val loss epoch 1 | epoch 2 | epoch 3 | last training loss |
|---|---|---|---|---|
| A (stage 2: warm, lr 1e-3, constant) | 0.0568 ± 0.0061 | 0.0628 ± 0.0058 | 0.0567 ± 0.0046 | 0.0359 |
| B (stage 2: no padding, lr 2e-3, constant) | 0.0448 ± 0.0038 | 0.0479 ± 0.0074 | 0.0514 ± 0.0047 | 0.0208 |
| A2 (round 2: level 1 frozen in epoch 1, lr decay) | 0.0487 ± 0.0046 | 0.0592 ± 0.0036 | 0.0556 ± 0.0033 | 0.0360 |
| B2 (round 2: no padding, lr decay) | 0.0541 ± 0.0062 | 0.0491 ± 0.0043 | 0.0505 ± 0.0011 | 0.0211 |
