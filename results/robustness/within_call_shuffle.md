# Item 4: does C use the order of tokens inside a call?

April reports, regime S, 10 seeds, checkpoint chosen on validation AUC. Share of reports whose first 512 tokens change: whole calls shuffled 98.6%, tokens shuffled inside each call 100.0%, all tokens shuffled 100.0%. Reports left unchanged in the within-call edit because the per-call tokenisation did not reproduce the full one: 0.0%; reports without calls: 0.0%. TPR with the threshold recomputed on each score vector.

| model | input | AUC | AUC sd | TPR@1% (a) | AUC change [95% over seeds] | TPR change, points [95%] |
|---|---|---|---|---|---|---|
| A | original | 0.9325 | 0.0121 | 66.4% | – | – |
| A | whole calls | 0.6930 | 0.0305 | 7.0% | -0.2395 [-0.2540, -0.2230] | -59.4 [-62.8, -55.3] |
| A | within calls | 0.9329 | 0.0120 | 64.8% | +0.0004 [-0.0016, +0.0025] | -1.6 [-2.4, -0.7] |
| A | bag of tokens | 0.6800 | 0.0355 | 7.3% | -0.2525 [-0.2685, -0.2305] | -59.1 [-62.8, -55.1] |
| B | original | 0.9287 | 0.0104 | 56.0% | – | – |
| B | whole calls | 0.9298 | 0.0122 | 52.0% | +0.0011 [-0.0064, +0.0082] | -3.9 [-5.8, -1.9] |
| B | within calls | 0.9287 | 0.0105 | 55.8% | -0.0000 [-0.0008, +0.0007] | -0.1 [-0.9, +0.7] |
| B | bag of tokens | 0.9395 | 0.0094 | 60.4% | +0.0109 [+0.0063, +0.0149] | +4.5 [+2.8, +5.9] |
| C | original | 0.9416 | 0.0089 | 67.0% | – | – |
| C | whole calls | 0.9412 | 0.0077 | 58.6% | -0.0003 [-0.0048, +0.0042] | -8.5 [-10.5, -6.5] |
| C | within calls | 0.9439 | 0.0065 | 65.7% | +0.0024 [+0.0003, +0.0045] | -1.3 [-2.7, +0.0] |
| C | bag of tokens | 0.9475 | 0.0059 | 68.6% | +0.0060 [+0.0016, +0.0102] | +1.5 [-0.2, +3.2] |


## C versus B: difference in the change caused by the edit

| edit | metric | C's change − B's change [95% over seeds] |
|---|---|---|
| whole calls | AUC | -0.0014 [-0.0079, +0.0054] |
| whole calls | TPR@1% (a), points | -4.5 [-8.2, -0.9] |
| within calls | AUC | +0.0024 [+0.0001, +0.0047] |
| within calls | TPR@1% (a), points | -1.2 [-2.8, +0.5] |
| bag of tokens | AUC | -0.0049 [-0.0090, +0.0004] |
| bag of tokens | TPR@1% (a), points | -2.9 [-5.4, -0.4] |
