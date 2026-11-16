# Recipe study: can the retrained flatten model A reach April AUC 0.95?

Goal: mean April AUC >= 0.95 over seeds. Released Nebula: AUC 0.9586 on the same April set. Epoch selection uses the January-validation side only; April numbers are reported, not used to pick an epoch.


## A

| seed | epochs | epoch by val AUC | April AUC | April TPR@1% (a) | epoch by val TPR@1% | April AUC | April TPR@1% (a) |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 2 | 0.9335 | 70.9% | 9 | 0.9298 | 72.0% |
| 1 | 10 | 4 | 0.9253 | 69.3% | 9 | 0.9228 | 68.7% |
| 2 | 10 | 2 | 0.9317 | 63.2% | 5 | 0.9236 | 67.9% |
| **mean** | | | **0.9302** | 67.8% | | **0.9254** | 69.5% |

Per epoch, mean over seeds (validation = January grouped validation side):

| epoch | val AUC | val TPR@1% | April AUC | April TPR@1% (a) |
|---|---|---|---|---|
| 1 | 0.9224 | 60.6% | 0.9224 | 61.2% |
| 2 | 0.9426 | 73.0% | 0.9262 | 67.6% |
| 3 | 0.9372 | 74.0% | 0.9235 | 69.0% |
| 4 | 0.9371 | 74.5% | 0.9260 | 69.9% |
| 5 | 0.9363 | 74.7% | 0.9238 | 69.5% |
| 6 | 0.9357 | 74.6% | 0.9238 | 69.2% |
| 7 | 0.9359 | 74.6% | 0.9239 | 69.3% |
| 8 | 0.9367 | 74.6% | 0.9245 | 69.1% |
| 9 | 0.9370 | 74.7% | 0.9246 | 69.2% |
| 10 | 0.9370 | 74.7% | 0.9247 | 69.2% |

## A_steps3000

| seed | epochs | epoch by val AUC | April AUC | April TPR@1% (a) | epoch by val TPR@1% | April AUC | April TPR@1% (a) |
|---|---|---|---|---|---|---|---|
| 0 | 3 | 2 | 0.9335 | 70.9% | 2 | 0.9335 | 70.9% |
| 1 | 3 | 3 | 0.9194 | 68.3% | 3 | 0.9194 | 68.3% |
| 2 | 3 | 2 | 0.9317 | 63.2% | 3 | 0.9205 | 68.0% |
| **mean** | | | **0.9282** | 67.5% | | **0.9245** | 69.1% |

Per epoch, mean over seeds (validation = January grouped validation side):

| epoch | val AUC | val TPR@1% | April AUC | April TPR@1% (a) |
|---|---|---|---|---|
| 1 | 0.9224 | 60.6% | 0.9224 | 61.2% |
| 2 | 0.9426 | 73.0% | 0.9262 | 67.6% |
| 3 | 0.9388 | 74.3% | 0.9223 | 69.1% |

## A_all

| seed | epochs | epoch by val AUC | April AUC | April TPR@1% (a) | epoch by val TPR@1% | April AUC | April TPR@1% (a) |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 9 | 0.9417 | 72.2% | 4 | 0.9434 | 73.0% |
| 1 | 10 | 9 | 0.9420 | 74.0% | 3 | 0.9419 | 74.7% |
| 2 | 10 | 10 | 0.9569 | 76.2% | 10 | 0.9569 | 76.2% |
| **mean** | | | **0.9469** | 74.2% | | **0.9474** | 74.6% |

Per epoch, mean over seeds (validation = January grouped validation side):

| epoch | val AUC | val TPR@1% | April AUC | April TPR@1% (a) |
|---|---|---|---|---|
| 1 | 0.9971 | 98.4% | 0.9516 | 71.7% |
| 2 | 0.9980 | 98.9% | 0.9499 | 74.9% |
| 3 | 0.9984 | 99.1% | 0.9477 | 75.4% |
| 4 | 0.9986 | 99.1% | 0.9467 | 74.5% |
| 5 | 0.9986 | 99.2% | 0.9455 | 73.9% |
| 6 | 0.9987 | 99.2% | 0.9469 | 74.2% |
| 7 | 0.9987 | 99.2% | 0.9467 | 74.1% |
| 8 | 0.9987 | 99.2% | 0.9469 | 74.1% |
| 9 | 0.9987 | 99.2% | 0.9469 | 74.2% |
| 10 | 0.9987 | 99.2% | 0.9468 | 74.1% |

## Summary: mean April AUC (per seed in brackets)

| option | mean April AUC | seeds | reaches 0.95 |
|---|---|---|---|
| A: selected on validation AUC | 0.9302 | 0.9335 / 0.9253 / 0.9317 | no |
| A: selected on validation TPR@1% | 0.9254 | 0.9298 / 0.9228 / 0.9236 | no |
| A: fixed 6 epochs | 0.9238 | 0.9283 / 0.9216 / 0.9214 | no |
| A: end of run (10 epochs or the step budget) | 0.9247 | 0.9299 / 0.9229 / 0.9213 | no |
| A_steps3000: selected on validation AUC | 0.9282 | 0.9335 / 0.9194 / 0.9317 | no |
| A_steps3000: selected on validation TPR@1% | 0.9245 | 0.9335 / 0.9194 / 0.9205 | no |
| A_steps3000: end of run (3 epochs or the step budget) | 0.9223 | 0.9270 / 0.9194 / 0.9205 | no |
| A_all: selected on validation AUC | 0.9469 | 0.9417 / 0.9420 / 0.9569 | no |
| A_all: selected on validation TPR@1% | 0.9474 | 0.9434 / 0.9419 / 0.9569 | no |
| A_all: fixed 6 epochs | 0.9469 | 0.9417 / 0.9416 / 0.9574 | no |
| A_all: end of run (10 epochs or the step budget) | 0.9468 | 0.9417 / 0.9419 / 0.9569 | no |
