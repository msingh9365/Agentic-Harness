# Pooling experiment, round 2 (v2)

Follow-up to `results/pooling` (which is unchanged). Two questions: **does the retrained flatten model A match the released Nebula, and at equal accuracy is C more robust than A?**

| | pooling | positional encoding |
|---|---|---|
| **A** | flatten | as released |
| **B** | mean, padding tokens excluded (`masked_mean` flag) | as released |
| **C** | mean, padding excluded | fixed: position inside the 64-token chunk (`fixed_pe` flag) |
| B0, C0 | B and C with the old unmasked mean over all 512 positions | reference |

Two training regimes: **S** = January train side, epoch chosen per run on January-validation AUC (the recipe as specified); **J** = all of January (train + validation sides), epoch count fixed in advance from regime S (A: 1 epoch, C: 10 epochs; the count with the highest mean validation AUC over the 10 seeds). 10 seeds each.

## Verdict

1. **A matches the released Nebula once it is trained on all of January; on the train side alone it does not.** Regime S: 0.9325 against 0.9586 (A − released −0.026 [−0.059, −0.0004]). Regime J: 0.9486, A − released −0.010 [−0.026, +0.001] in AUC and −3.1 points [−11.7, +2.0] in TPR at 1% FPR; 4 of 10 seeds are above 0.95, the mean is just under the 0.95 goal. A 10-seed ensemble of regime-J A is identical to the released model (AUC 0.9590 against 0.9586, +0.0004 [−0.013, +0.011]; TPR@1% 75.5% against 75.0%). How the released model was trained is not documented, so this is "indistinguishable on this test set", not "reproduced".
2. **C is at least as accurate as A, except at very low FPR.** AUC: C − A +0.009 [−0.006, +0.027] in regime S and +0.016 [+0.004, +0.032] in regime J, where C (0.9644) is also level with the released model (+0.006 [−0.004, +0.018]). TPR at 1% FPR is the same (+0.6 [−9.1, +7.0]; +1.9 [−8.3, +7.9]). At 0.1% FPR C is lower: −19.2 points [−30.2, +1.6] in regime J, and −20.8 [−39.6, −1.3] between the regime-S ensembles.
3. **C is far more robust than A to edits that move tokens.** Shuffled call order: A 0.9325 → 0.693 AUC, C 0.9416 → 0.9412. Twenty copied calls put in front of the report: A 0.9325 → 0.684 AUC and malware TPR at the fixed 1% threshold 66.4% → 31.2% while its benign FPR rises from 1.0% to 6.3%; C 0.9416 → 0.9410 and 67.0% → 65.7%. Five calls inserted where no original call leaves the window: A −0.018 AUC and −9.5 TPR points, C −0.001 and +0.8 (difference in the AUC drop +0.017 [+0.010, +0.026]). The same holds in regime J.
4. **The gain comes from mean pooling plus the fixed position encoding, not from masking or longer training.** Mean pooling alone (B) is just as robust but 10 TPR points below A (−10.4 [−28.1, −0.3]). C beats B after every equal number of epochs (+0.007 AUC at 1 epoch, +0.018 from 4 epochs on). Masking the padding adds little (C over unmasked C0: +0.022 AUC [+0.002, +0.047], 3 seeds).
5. **The distance-quartile gap is not closed.** In regime J, C ranks the far quartiles better than A (Q2-Q4 AUC +0.038 [+0.011, +0.075]) but catches no more malware at 1% FPR (+4.1 points [−7.6, +13.7]), and the gap between the nearest quartile and the rest stays (A +32.7 points, C +28.3, released +27.7). The small gaps in regime S (A +12.8, C +0.6) came from low detection in the nearest quartile, not from better detection far away.

## What was found about the released model

`released_training.md`: how the released model was trained is **not documented** in the Nebula repository (no epochs, steps, batch size or pretraining for `bpe_50000_torch.model`). The paper (arXiv 2310.10664) gives batch 96, AdamW at 2.5e-4, a 5-minute time budget per fold instead of epochs, and says the released models were trained on "just 70k samples". File and line references are in that file.

## Recipe study for A (goal: April AUC ≥ 0.95)

Seeds 0-2. Every run keeps a checkpoint and the April and validation scores after each of 10 epochs; the epoch is chosen on the January-validation side only (AUC primary, TPR@1% secondary). April numbers decide whether the goal is met, so April influenced which options were tried, not which epoch was chosen.

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

- For the `A_all` rows the January validation side is part of the training set, so "selected on validation" is not a meaningful selection there; read them as "the last epochs".
- Epoch choice, fixed 6 epochs and the 3000-step budget (the only step budget written in Nebula's scripts; the released model's own budget is not documented) all stay at 0.922-0.930.
- Training on all of January is what moves A: 0.9516 after 1 epoch, 0.9499 after 2 (3 seeds). With 10 seeds and 1 epoch: 0.9486 (next section).

## Results, regime J (all of January; A 1 epoch, C 10 epochs; 10 seeds)

The January validation side is in the training set here, so there is no January threshold (b); thresholds are (a), from the April benign scores. Mean over seeds [95% group-bootstrap interval].

| model | AUC | TPR@1% FPR (a) | TPR@0.1% FPR (a) |
|---|---|---|---|
| A | 0.9486 [0.9132, 0.9710] | 71.9% [59.9%, 80.4%] | 39.6% [26.7%, 50.8%] |
| C | 0.9644 [0.9433, 0.9785] | 73.8% [58.1%, 83.2%] | 20.4% [10.5%, 42.4%] |
| A + LightGBM | 0.9732 [0.9464, 0.9878] | 78.7% [69.6%, 86.1%] | 49.3% [34.6%, 64.1%] |
| C + LightGBM | 0.9797 [0.9616, 0.9899] | 80.9% [69.9%, 87.8%] | 45.3% [30.6%, 61.5%] |
| released Nebula | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 51.7% [0.0%, 67.0%] |
| LightGBM bag of API names | 0.9499 [0.9147, 0.9757] | 63.0% [33.5%, 74.8%] | 31.3% [18.1%, 45.4%] |
| released Nebula + LightGBM | 0.9744 [0.9498, 0.9884] | 79.6% [68.9%, 87.6%] | 55.0% [40.2%, 70.9%] |

| model | metric | seeds | mean | sd | min | max |
|---|---|---|---|---|---|---|
| A | AUC | 10 | 0.9486 | 0.0133 | 0.9319 | 0.9734 |
| A | TPR@1% (a) | 10 | 71.9% | 2.9 | 66.6% | 75.7% |
| C | AUC | 10 | 0.9644 | 0.0085 | 0.9479 | 0.9750 |
| C | TPR@1% (a) | 10 | 73.8% | 2.8 | 69.3% | 78.8% |

Paired differences (TPR in points):

| difference | subset | AUC | TPR@1% (a), points | TPR@0.1% (a), points |
|---|---|---|---|---|
| C − A | all | +0.0158 [+0.0044, +0.0318] | +1.9 [-8.3, +7.9] | -19.2 [-30.2, +1.6] |
| C − A | unseen | +0.0256 [+0.0073, +0.0520] | +2.1 [-9.7, +9.1] | -21.9 [-33.8, -1.5] |
| C − A | distance Q1 (≤ 0.031) | +0.0121 [+0.0009, +0.0555] | -0.4 [-14.9, +2.4] | -45.9 [-61.5, -12.7] |
| C − A | distance Q2 (≤ 0.083) | +0.0775 [+0.0202, +0.1327] | +6.9 [-11.7, +24.4] | -7.6 [-22.1, +1.1] |
| C − A | distance Q3 (≤ 0.193) | +0.0084 [-0.0069, +0.0259] | +5.0 [-20.8, +18.2] | -13.4 [-22.0, +0.6] |
| C − A | distance Q4 (> 0.193) | +0.0362 [-0.0137, +0.1187] | +0.3 [-5.3, +8.6] | +11.4 [-2.3, +31.6] |
| C − A | distance Q2-Q4 (farther three quartiles) | +0.0383 [+0.0111, +0.0752] | +4.1 [-7.6, +13.7] | -3.5 [-13.1, +10.6] |
| A − released Nebula | all | -0.0100 [-0.0255, +0.0010] | -3.1 [-11.7, +2.0] | -12.1 [-28.0, +41.8] |
| A − released Nebula | unseen | -0.0168 [-0.0484, +0.0029] | -3.6 [-15.8, +3.0] | -9.7 [-29.4, +41.4] |
| A − released Nebula | distance Q1 (≤ 0.031) | -0.0083 [-0.0359, -0.0011] | -0.7 [-4.9, +1.9] | -0.1 [-19.5, +66.8] |
| A − released Nebula | distance Q2 (≤ 0.083) | -0.0555 [-0.1440, +0.0633] | -29.0 [-61.1, -1.8] | -28.1 [-60.7, +27.2] |
| A − released Nebula | distance Q3 (≤ 0.193) | +0.0060 [-0.0260, +0.0438] | +10.6 [-4.1, +17.4] | +6.6 [-1.6, +21.1] |
| A − released Nebula | distance Q4 (> 0.193) | -0.0631 [-0.1846, +0.0111] | -2.2 [-11.7, +5.7] | -33.3 [-58.6, +20.8] |
| A − released Nebula | distance Q2-Q4 (farther three quartiles) | -0.0276 [-0.0895, +0.0131] | -5.8 [-26.2, +5.1] | -17.1 [-40.2, +21.3] |
| C − released Nebula | all | +0.0058 [-0.0041, +0.0177] | -1.2 [-15.0, +6.3] | -31.3 [-45.7, +23.3] |
| C − released Nebula | unseen | +0.0088 [-0.0069, +0.0279] | -1.5 [-17.9, +7.8] | -31.6 [-47.2, +18.0] |
| C − released Nebula | distance Q1 (≤ 0.031) | +0.0038 [-0.0037, +0.0248] | -1.1 [-16.5, +0.9] | -45.9 [-70.3, +21.5] |
| C − released Nebula | distance Q2 (≤ 0.083) | +0.0220 [-0.0239, +0.0934] | -22.1 [-55.0, +6.0] | -35.8 [-67.2, +20.3] |
| C − released Nebula | distance Q3 (≤ 0.193) | +0.0144 [-0.0149, +0.0590] | +15.6 [-15.0, +29.8] | -6.8 [-13.2, +4.7] |
| C − released Nebula | distance Q4 (> 0.193) | -0.0269 [-0.1021, +0.0510] | -1.8 [-8.3, +5.3] | -21.9 [-48.6, +35.2] |
| C − released Nebula | distance Q2-Q4 (farther three quartiles) | +0.0107 [-0.0181, +0.0376] | -1.7 [-21.5, +12.5] | -20.7 [-40.7, +18.3] |

Distance quartiles, TPR at 1% FPR (a):

| model | TPR (a) Q1 | TPR (a) Q2-Q4 | gap (a), points |
|---|---|---|---|
| A | 86.7% | 54.0% | +32.7 |
| C | 86.3% | 58.0% | +28.3 |
| released Nebula | 87.4% | 59.7% | +27.7 |
| LightGBM bag of API names | 68.5% | 46.1% | +22.4 |

C after 1 epoch on all of January already has 0.9593 AUC, so the difference to A is not only the longer training. Full tables: `tables_J.md`.

## Results, regime S (January train side; epoch chosen on validation AUC; 10 seeds)

Thresholds: (a) from the April benign scores; (b) from the January-validation benign scores applied to April (its April FPR shown). B0, C0: unmasked, 3 seeds. Rank-average rows: percentile rank average with the bag-of-API LightGBM (seeds 0-2 of the earlier LightGBM, reused as seed mod 3).

| model | AUC | TPR@1% FPR (a) | TPR@1% FPR (b) | April FPR at (b) |
|---|---|---|---|---|
| A | 0.9325 [0.8914, 0.9648] | 66.4% [55.7%, 77.0%] | 59.2% [48.1%, 69.8%] | 0.5% [0.4%, 0.8%] |
| B | 0.9287 [0.8911, 0.9599] | 56.0% [33.1%, 72.8%] | 44.5% [31.7%, 57.3%] | 0.7% [0.4%, 1.2%] |
| C | 0.9416 [0.9060, 0.9687] | 67.0% [49.8%, 78.8%] | 57.4% [45.6%, 69.7%] | 0.6% [0.3%, 1.0%] |
| A + LightGBM | 0.9700 [0.9422, 0.9858] | 74.9% [65.8%, 84.0%] | 94.7% [90.3%, 97.5%] | 17.3% [12.2%, 22.6%] |
| B + LightGBM | 0.9689 [0.9461, 0.9834] | 70.4% [51.0%, 82.9%] | 88.1% [82.1%, 93.0%] | 6.0% [4.5%, 8.3%] |
| C + LightGBM | 0.9736 [0.9536, 0.9859] | 77.7% [65.6%, 86.2%] | 91.8% [86.8%, 95.4%] | 11.5% [7.9%, 15.5%] |
| released Nebula | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 76.6% [68.2%, 83.9%] | 1.4% [1.0%, 2.0%] |
| LightGBM bag of API names | 0.9499 [0.9147, 0.9757] | 63.0% [33.5%, 74.8%] | 58.1% [44.6%, 71.0%] | 0.9% [0.6%, 1.5%] |
| released Nebula + LightGBM | 0.9744 [0.9498, 0.9884] | 79.6% [68.9%, 87.6%] | 97.6% [93.4%, 99.6%] | 34.6% [23.7%, 46.4%] |
| B0 | 0.9166 [0.8621, 0.9606] | 53.8% [37.3%, 69.1%] | 57.2% [43.6%, 71.4%] | 1.1% [0.7%, 1.9%] |
| C0 | 0.9137 [0.8566, 0.9580] | 62.1% [46.6%, 74.9%] | 55.7% [43.0%, 68.3%] | 0.7% [0.4%, 1.1%] |

Seed spread:

| model | metric | seeds | mean | sd | min | max |
|---|---|---|---|---|---|---|
| A | AUC | 10 | 0.9325 | 0.0121 | 0.9124 | 0.9514 |
| A | TPR@1% (a) | 10 | 66.4% | 3.4 | 59.3% | 70.9% |
| B | AUC | 10 | 0.9287 | 0.0104 | 0.9081 | 0.9421 |
| B | TPR@1% (a) | 10 | 56.0% | 7.2 | 42.2% | 63.3% |
| C | AUC | 10 | 0.9416 | 0.0089 | 0.9282 | 0.9572 |
| C | TPR@1% (a) | 10 | 67.0% | 4.4 | 59.8% | 74.4% |
| B0 | AUC | 3 | 0.9166 | 0.0097 | 0.9076 | 0.9269 |
| B0 | TPR@1% (a) | 3 | 53.8% | 7.4 | 49.4% | 62.4% |
| C0 | AUC | 3 | 0.9137 | 0.0285 | 0.8908 | 0.9457 |
| C0 | TPR@1% (a) | 3 | 62.1% | 2.5 | 60.0% | 64.9% |

Epochs chosen on validation AUC:

| model | epoch chosen by validation AUC, per seed | mean |
|---|---|---|
| A | 2 / 4 / 2 / 1 / 1 / 1 / 2 / 1 / 1 / 1 | 1.6 |
| B | 5 / 9 / 1 / 6 / 1 / 1 / 10 / 8 / 2 / 1 | 4.4 |
| C | 4 / 10 / 8 / 6 / 8 / 3 / 10 / 5 / 9 / 10 | 7.3 |
| B0 | 1 / 6 / 1 | 2.7 |
| C0 | 1 / 4 / 4 | 3.0 |

### Paired differences (group bootstrap, 1,000 resamples)

TPR in percentage points; difference of the seed means.

| difference | subset | AUC | TPR@1% (a), points | TPR@1% (b), points |
|---|---|---|---|---|
| B − A | all | -0.0038 [-0.0172, +0.0109] | -10.4 [-28.1, -0.3] | -14.6 [-19.7, -8.9] |
| B − A | unseen | +0.0043 [-0.0138, +0.0262] | -12.0 [-26.5, +1.1] | -15.0 [-21.7, -6.7] |
| B − A | distance Q1 (≤ 0.031) | -0.0086 [-0.0424, +0.0382] | -18.3 [-35.4, -1.1] | -20.1 [-27.8, -9.0] |
| B − A | distance Q2 (≤ 0.083) | +0.0442 [+0.0120, +0.0935] | -3.0 [-27.0, +10.3] | -10.8 [-23.1, -2.5] |
| B − A | distance Q3 (≤ 0.193) | -0.0053 [-0.0290, +0.0099] | -15.4 [-44.5, +11.6] | -24.9 [-50.0, +9.3] |
| B − A | distance Q4 (> 0.193) | -0.0317 [-0.1184, +0.0396] | -1.8 [-9.6, +1.3] | +4.0 [-3.6, +7.8] |
| B − A | distance Q2-Q4 (farther three quartiles) | +0.0025 [-0.0256, +0.0270] | -7.1 [-24.9, +5.2] | -11.1 [-21.4, +0.0] |
| C − A | all | +0.0091 [-0.0055, +0.0268] | +0.6 [-9.1, +7.0] | -1.8 [-6.1, +3.1] |
| C − A | unseen | +0.0190 [-0.0044, +0.0471] | +1.0 [-10.7, +9.2] | -2.1 [-8.2, +4.4] |
| C − A | distance Q1 (≤ 0.031) | +0.0010 [-0.0350, +0.0654] | -5.9 [-18.7, +1.7] | -8.8 [-14.4, -2.5] |
| C − A | distance Q2 (≤ 0.083) | +0.0785 [+0.0054, +0.1432] | +14.8 [-3.9, +30.9] | +7.7 [-3.0, +18.4] |
| C − A | distance Q3 (≤ 0.193) | -0.0017 [-0.0288, +0.0107] | +5.1 [-24.5, +19.7] | -3.4 [-31.8, +14.4] |
| C − A | distance Q4 (> 0.193) | -0.0087 [-0.0856, +0.0756] | -0.4 [-6.0, +3.5] | +5.6 [-1.4, +9.5] |
| C − A | distance Q2-Q4 (farther three quartiles) | +0.0240 [-0.0118, +0.0631] | +6.3 [-7.9, +15.4] | +3.0 [-6.6, +10.6] |
| C − B | all | +0.0129 [+0.0051, +0.0229] | +11.1 [+3.8, +20.4] | +12.9 [+9.0, +16.9] |
| C − B | unseen | +0.0147 [+0.0021, +0.0330] | +13.0 [+2.9, +20.2] | +12.9 [+7.4, +18.2] |
| C − B | distance Q1 (≤ 0.031) | +0.0096 [-0.0039, +0.0339] | +12.4 [+0.9, +20.7] | +11.3 [+5.2, +17.4] |
| C − B | distance Q2 (≤ 0.083) | +0.0343 [-0.0224, +0.0807] | +17.8 [+2.1, +31.8] | +18.4 [+7.8, +27.7] |
| C − B | distance Q3 (≤ 0.193) | +0.0036 [-0.0127, +0.0125] | +20.4 [+1.4, +33.3] | +21.5 [+0.7, +27.7] |
| C − B | distance Q4 (> 0.193) | +0.0230 [+0.0052, +0.0619] | +1.4 [+0.3, +5.6] | +1.5 [+0.5, +3.8] |
| C − B | distance Q2-Q4 (farther three quartiles) | +0.0214 [+0.0013, +0.0540] | +13.4 [+2.9, +23.3] | +14.0 [+6.0, +20.9] |
| A − released Nebula | all | -0.0261 [-0.0589, -0.0004] | -8.6 [-19.7, +1.1] | -17.5 [-29.6, -7.7] |
| A − released Nebula | unseen | -0.0375 [-0.0862, +0.0064] | -10.7 [-25.9, +2.8] | -20.3 [-36.4, -6.8] |
| A − released Nebula | distance Q1 (≤ 0.031) | -0.0508 [-0.1083, -0.0006] | -19.0 [-43.4, +0.5] | -24.9 [-53.6, -2.2] |
| A − released Nebula | distance Q2 (≤ 0.083) | -0.0547 [-0.1399, +0.0629] | -28.0 [-55.8, -2.9] | -36.5 [-65.5, -9.2] |
| A − released Nebula | distance Q3 (≤ 0.193) | +0.0143 [-0.0094, +0.0564] | +12.6 [+2.2, +23.4] | -6.0 [-11.7, +4.7] |
| A − released Nebula | distance Q4 (> 0.193) | -0.0229 [-0.0891, +0.0361] | -0.6 [-6.1, +6.9] | -10.2 [-17.1, -5.2] |
| A − released Nebula | distance Q2-Q4 (farther three quartiles) | -0.0130 [-0.0588, +0.0267] | -4.2 [-22.3, +6.3] | -16.8 [-32.7, -7.1] |
| C − released Nebula | all | -0.0170 [-0.0486, +0.0075] | -7.9 [-26.3, +4.2] | -19.2 [-33.9, -8.1] |
| C − released Nebula | unseen | -0.0186 [-0.0673, +0.0224] | -9.7 [-32.9, +6.5] | -22.4 [-41.3, -7.0] |
| C − released Nebula | distance Q1 (≤ 0.031) | -0.0498 [-0.1205, +0.0130] | -25.0 [-60.0, -0.5] | -33.7 [-68.0, -5.7] |
| C − released Nebula | distance Q2 (≤ 0.083) | +0.0238 [-0.0082, +0.0751] | -13.2 [-43.1, +9.3] | -28.8 [-48.6, -5.1] |
| C − released Nebula | distance Q3 (≤ 0.193) | +0.0125 [-0.0213, +0.0482] | +17.7 [-7.0, +30.0] | -9.4 [-29.6, +6.8] |
| C − released Nebula | distance Q4 (> 0.193) | -0.0316 [-0.1381, +0.0504] | -0.9 [-6.6, +5.9] | -4.7 [-13.4, -1.2] |
| C − released Nebula | distance Q2-Q4 (farther three quartiles) | +0.0109 [-0.0161, +0.0327] | +2.1 [-15.3, +13.2] | -13.8 [-25.7, -3.4] |

Masked versus unmasked (same seeds, 0-2):

| difference (same seeds) | subset | AUC | TPR@1% (a), points |
|---|---|---|---|
| B[seeds of B0] − B0 | all | +0.0140 [-0.0141, +0.0460] | +1.1 [-13.9, +16.4] |
| B[seeds of B0] − B0 | distance Q2-Q4 (farther three quartiles) | -0.0016 [-0.0577, +0.0501] | +4.9 [-14.7, +25.0] |
| C[seeds of C0] − C0 | all | +0.0215 [+0.0019, +0.0467] | +2.5 [-3.6, +9.0] |
| C[seeds of C0] − C0 | distance Q2-Q4 (farther three quartiles) | +0.0129 [-0.0044, +0.0318] | +6.9 [-6.9, +16.3] |

### Distance quartiles (unseen April reports, test 3 definitions)

Quartiles of the distance to the nearest January sequence: Q1 ≤ 0.031, Q2 ≤ 0.083, Q3 ≤ 0.193, Q4 > 0.193. TPR at 1% FPR, mean over seeds. Gap = Q1 minus Q2-Q4.

| model | TPR (a) Q1 | TPR (a) Q2-Q4 | gap (a), points | TPR (b) Q1 | TPR (b) Q2-Q4 | gap (b), points |
|---|---|---|---|---|---|---|
| A | 68.4% | 55.5% | +12.8 | 63.1% | 46.2% | +17.0 |
| B | 50.1% | 48.4% | +1.7 | 43.0% | 35.1% | +7.9 |
| C | 62.5% | 61.8% | +0.6 | 54.4% | 49.1% | +5.2 |
| released Nebula | 87.4% | 59.7% | +27.7 | 88.1% | 63.0% | +25.1 |
| LightGBM bag of API names | 68.5% | 46.1% | +22.4 | 58.9% | 41.1% | +17.8 |
| B0 | 53.8% | 42.5% | +11.2 | 54.3% | 48.3% | +5.9 |
| C0 | 55.6% | 56.0% | -0.4 | 54.2% | 44.7% | +9.4 |

All other subsets (seen, 1 / 2-3 / 4-8 chunks, window-share groups), the rank-average differences and the results when the epoch is chosen by validation TPR@1% instead are in `tables.md`. Choosing by TPR@1% gives A 0.9253, B 0.9236, C 0.9407 AUC, so the ordering C > A > B is the same.

## Same number of epochs for every model (regime S, no epoch selection)

Under the validation-AUC rule A stops after 1-2 epochs and C after about 7. Scoring every model after the same number of epochs removes that difference (`followups_same_epoch.md`):

| epochs | A AUC | B AUC | C AUC | A TPR@1% (a) | B TPR@1% (a) | C TPR@1% (a) |
|---|---|---|---|---|---|---|
| 1 | 0.9288 | 0.9331 | 0.9397 | 63.7% | 52.0% | 65.3% |
| 2 | 0.9243 | 0.9265 | 0.9378 | 66.5% | 58.7% | 65.9% |
| 3 | 0.9255 | 0.9245 | 0.9402 | 67.8% | 59.6% | 67.0% |
| 4 | 0.9249 | 0.9230 | 0.9404 | 67.9% | 59.7% | 66.8% |
| 5 | 0.9245 | 0.9235 | 0.9413 | 68.1% | 59.7% | 66.7% |
| 6 | 0.9235 | 0.9231 | 0.9412 | 67.9% | 59.6% | 67.0% |
| 7 | 0.9243 | 0.9230 | 0.9412 | 68.4% | 59.6% | 67.0% |
| 8 | 0.9243 | 0.9233 | 0.9411 | 67.9% | 59.7% | 67.0% |
| 9 | 0.9243 | 0.9232 | 0.9409 | 68.2% | 59.7% | 67.0% |
| 10 | 0.9243 | 0.9230 | 0.9409 | 68.2% | 59.7% | 67.0% |

Seed-paired differences in April AUC [95% interval over the 10 seeds]:

| epochs | C − B AUC | C − A AUC | B − A AUC |
|---|---|---|---|
| 1 | +0.0066 [-0.0029, +0.0161] | +0.0109 [+0.0028, +0.0195] | +0.0043 [-0.0093, +0.0167] |
| 2 | +0.0113 [+0.0019, +0.0205] | +0.0135 [+0.0035, +0.0226] | +0.0022 [-0.0051, +0.0103] |
| 5 | +0.0179 [+0.0098, +0.0260] | +0.0168 [+0.0094, +0.0247] | -0.0010 [-0.0087, +0.0071] |
| 10 | +0.0179 [+0.0097, +0.0261] | +0.0166 [+0.0085, +0.0251] | -0.0013 [-0.0089, +0.0070] |

## Seed ensembles

The logits of the 10 seeds are averaged and scored once (`followups_ensemble.md`). This removes the seed spread from the comparison with the released model.

| model | mean single-seed AUC | mean single-seed TPR@1% (a) | ensemble AUC | ensemble TPR@1% (a) |
|---|---|---|---|---|
| A (S) | 0.9325 | 66.4% | 0.9424 | 73.7% |
| B (S) | 0.9287 | 56.0% | 0.9386 | 63.4% |
| C (S) | 0.9416 | 67.0% | 0.9454 | 67.3% |
| A (J) | 0.9486 | 71.9% | 0.9590 | 75.5% |
| C (J) | 0.9644 | 73.8% | 0.9672 | 75.0% |

| model | AUC | TPR@1% FPR (a) | TPR@0.1% FPR (a) |
|---|---|---|---|
| A ensemble (S) | 0.9424 [0.8985, 0.9741] | 73.7% [63.4%, 82.2%] | 51.2% [30.2%, 66.6%] |
| B ensemble (S) | 0.9386 [0.8989, 0.9679] | 63.4% [39.7%, 77.9%] | 13.0% [5.2%, 30.9%] |
| C ensemble (S) | 0.9454 [0.9086, 0.9723] | 67.3% [49.6%, 81.5%] | 30.4% [8.9%, 55.5%] |
| A ensemble (J) | 0.9590 [0.9270, 0.9795] | 75.5% [64.2%, 83.8%] | 43.3% [27.3%, 60.1%] |
| C ensemble (J) | 0.9672 [0.9449, 0.9815] | 75.0% [61.0%, 84.7%] | 25.3% [12.6%, 51.6%] |
| released Nebula | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 51.7% [0.0%, 67.0%] |

| difference (all April reports) | AUC | TPR@1% (a), points | TPR@0.1% (a), points |
|---|---|---|---|
| C ensemble (S) − A ensemble (S) | +0.0029 [-0.0126, +0.0231] | -6.5 [-18.0, +6.4] | -20.8 [-39.6, -1.3] |
| B ensemble (S) − A ensemble (S) | -0.0038 [-0.0186, +0.0124] | -10.3 [-27.7, -1.5] | -38.2 [-52.0, -14.2] |
| C ensemble (S) − B ensemble (S) | +0.0068 [+0.0009, +0.0143] | +3.8 [-0.3, +16.8] | +17.4 [-4.9, +38.2] |
| A ensemble (S) − released Nebula | -0.0162 [-0.0491, +0.0114] | -1.2 [-11.7, +8.3] | -0.5 [-19.6, +57.2] |
| C ensemble (S) − released Nebula | -0.0132 [-0.0450, +0.0116] | -7.7 [-26.0, +7.1] | -21.3 [-41.7, +36.8] |
| C ensemble (J) − A ensemble (J) | +0.0082 [-0.0010, +0.0217] | -0.4 [-9.4, +5.7] | -18.0 [-33.5, +9.6] |
| A ensemble (J) − released Nebula | +0.0004 [-0.0126, +0.0112] | +0.5 [-7.8, +7.5] | -8.4 [-26.3, +47.2] |
| C ensemble (J) − released Nebula | +0.0086 [-0.0003, +0.0210] | +0.0 [-11.6, +9.0] | -26.4 [-42.1, +31.4] |

Ensembling helps A more than C (A varies more between seeds). The ensembles of A reach the released model; C's ensembles have the highest AUC but the lowest TPR at 0.1% FPR.

## Robustness checks (April, 10 seeds)

Edits applied to the filtered report of every April report, then Nebula's tokenizer, first 512 tokens. **Shuffled:** the order of all API calls permuted (98.6% of token sequences change). **+5 calls:** five extra calls inserted at random places, each a copy of a call of the same report taken from elsewhere (not a neighbour of the insertion point); 90.0% of token sequences change. TPR with the April threshold (a) recomputed on each score vector. The CPU scores of the unedited input reproduce the Kaggle scores (max logit difference 1e-4).

Regime S (checkpoint chosen on validation AUC):

| model | AUC original | AUC shuffled | AUC +5 calls | TPR@1% (a) original | shuffled | +5 calls |
|---|---|---|---|---|---|---|
| A | 0.9325 | 0.6930 | 0.9223 | 66.4% | 7.0% | 59.3% |
| B | 0.9287 | 0.9298 | 0.9276 | 56.0% | 52.0% | 58.1% |
| C | 0.9416 | 0.9412 | 0.9391 | 67.0% | 58.6% | 66.0% |

**Same edit, only reports where nothing is pushed out of the window.** "Without changing which calls fit": inserting calls before the 512-token cut can push original calls out of the window. This view keeps only the 6,278 April reports (2,813 malware) whose whole edited token sequence is at most 512 tokens, so every original call is still seen; before and after are on exactly these reports.

| model | AUC before | AUC after | TPR@1% (a) before | after |
|---|---|---|---|---|
| A | 0.9381 | 0.9199 | 60.7% | 51.2% |
| B | 0.9309 | 0.9292 | 44.3% | 47.8% |
| C | 0.9408 | 0.9400 | 58.6% | 59.4% |

Seed-paired differences in the change caused by the edit (bootstrap over the 10 seeds only, so sampling of April reports is not in these intervals):

| change after the edit | A | C | C − A [95% interval over seeds] |
|---|---|---|---|
| AUC, call order shuffled | -0.2395 | -0.0003 | +0.2392 [+0.2216, +0.2558] |
| TPR@1% (a), call order shuffled, points | -59.4 | -8.5 | +50.9 [+47.4, +54.3] |
| AUC, 5 calls inserted | -0.0102 | -0.0025 | +0.0077 [+0.0037, +0.0108] |
| TPR@1% (a), 5 calls inserted, points | -7.1 | -1.0 | +6.1 [+4.0, +8.1] |
| AUC, 5 calls inserted, reports where nothing is pushed out | -0.0182 | -0.0009 | +0.0174 [+0.0100, +0.0256] |
| TPR@1% (a), same reports, points | -9.5 | +0.8 | +10.3 [+6.6, +13.9] |

Regime J (weights after the fixed number of epochs):

| model | AUC original | AUC shuffled | AUC +5 calls | TPR@1% (a) original | shuffled | +5 calls |
|---|---|---|---|---|---|---|
| A | 0.9486 | 0.7028 | 0.9379 | 71.9% | 9.8% | 64.1% |
| C | 0.9644 | 0.9690 | 0.9606 | 73.8% | 65.5% | 72.2% |

| model | AUC before | AUC after | TPR@1% (a) before | after |
|---|---|---|---|---|
| A | 0.9496 | 0.9221 | 63.1% | 52.9% |
| C | 0.9605 | 0.9563 | 58.1% | 56.7% |

| change after the edit | A | C | C − A [95% interval over seeds] |
|---|---|---|---|
| AUC, call order shuffled | -0.2458 | +0.0046 | +0.2504 [+0.2284, +0.2681] |
| TPR@1% (a), call order shuffled, points | -62.1 | -8.2 | +53.9 [+48.5, +58.1] |
| AUC, 5 calls inserted | -0.0107 | -0.0037 | +0.0070 [+0.0046, +0.0096] |
| TPR@1% (a), 5 calls inserted, points | -7.8 | -1.6 | +6.3 [+3.9, +9.5] |
| AUC, 5 calls inserted, reports where nothing is pushed out | -0.0275 | -0.0043 | +0.0233 [+0.0189, +0.0276] |
| TPR@1% (a), same reports, points | -10.3 | -1.4 | +8.9 [+2.3, +14.6] |

### Graded edits: insert or prepend k calls (regime S)

`graded_edits.md`. k = 1, 5, 20, 50 calls, each a copy of a call of the same report: inserted at random places, or all put before the first call (which shifts every later token). "TPR fixed (a)": malware caught at the threshold that gave 1% FPR on the original April benign scores, not recomputed after the edit, as for a deployed model; "FPR fixed (a)": benign reports flagged at that threshold after the same edit.

| edit | A AUC | B AUC | C AUC | A TPR fixed (a) | B TPR fixed (a) | C TPR fixed (a) | A FPR fixed (a) | B FPR fixed (a) | C FPR fixed (a) | A TPR fixed (b) | B TPR fixed (b) | C TPR fixed (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| original | 0.9325 | 0.9287 | 0.9416 | 66.4% | 56.0% | 67.0% | 1.00% | 1.00% | 1.00% | 59.2% | 44.5% | 57.4% |
| insert 1 | 0.9310 | 0.9286 | 0.9407 | 64.8% | 55.4% | 66.0% | 0.95% | 0.98% | 0.95% | 57.5% | 44.1% | 56.2% |
| insert 5 | 0.9223 | 0.9276 | 0.9391 | 60.2% | 55.0% | 64.5% | 1.11% | 0.92% | 0.93% | 53.2% | 43.4% | 55.2% |
| insert 20 | 0.8901 | 0.9295 | 0.9356 | 50.0% | 55.2% | 63.9% | 1.43% | 0.91% | 1.04% | 43.0% | 40.8% | 53.5% |
| insert 50 | 0.8294 | 0.9357 | 0.9407 | 40.5% | 57.1% | 65.6% | 1.91% | 0.97% | 1.07% | 34.1% | 43.2% | 55.1% |
| prepend 1 | 0.9246 | 0.9286 | 0.9410 | 59.9% | 54.3% | 64.3% | 1.06% | 0.97% | 0.93% | 52.0% | 42.0% | 54.2% |
| prepend 5 | 0.8779 | 0.9262 | 0.9287 | 46.6% | 54.8% | 63.3% | 1.69% | 0.98% | 1.27% | 39.4% | 40.9% | 54.4% |
| prepend 20 | 0.6840 | 0.9357 | 0.9410 | 31.2% | 55.8% | 65.7% | 6.31% | 0.95% | 1.08% | 25.7% | 41.7% | 54.9% |
| prepend 50 | 0.5595 | 0.9328 | 0.9436 | 23.9% | 53.2% | 61.4% | 14.28% | 0.98% | 1.02% | 19.1% | 40.7% | 52.2% |

Only reports whose whole edited sequence fits in 512 tokens (nothing pushed out of the window):

| edit | reports that fit (malware) | A AUC before → after | B AUC before → after | C AUC before → after | A TPR fixed (a) before → after | B TPR fixed (a) before → after | C TPR fixed (a) before → after |
|---|---|---|---|---|---|---|---|
| insert 1 | 6,349 (2,854) | 0.9384 → 0.9351 | 0.9310 → 0.9305 | 0.9412 → 0.9399 | 64.2% → 62.6% | 62.4% → 61.6% | 69.3% → 67.8% |
| insert 5 | 6,278 (2,813) | 0.9381 → 0.9199 | 0.9309 → 0.9292 | 0.9408 → 0.9400 | 64.2% → 58.3% | 62.7% → 62.1% | 69.4% → 67.1% |
| insert 20 | 4,975 (1,953) | 0.9475 → 0.9125 | 0.9344 → 0.9375 | 0.9431 → 0.9423 | 69.7% → 64.4% | 69.2% → 68.9% | 71.3% → 69.5% |
| insert 50 | 3,654 (1,530) | 0.9505 → 0.9171 | 0.9422 → 0.9451 | 0.9489 → 0.9509 | 72.1% → 63.8% | 71.7% → 70.8% | 71.1% → 69.2% |
| prepend 1 | 6,349 (2,851) | 0.9383 → 0.9284 | 0.9310 → 0.9293 | 0.9412 → 0.9388 | 64.1% → 61.0% | 62.5% → 60.6% | 69.3% → 66.6% |
| prepend 5 | 6,275 (2,807) | 0.9378 → 0.8853 | 0.9308 → 0.9290 | 0.9408 → 0.9352 | 64.1% → 54.0% | 62.7% → 61.8% | 69.4% → 66.3% |
| prepend 20 | 5,018 (1,980) | 0.9467 → 0.8826 | 0.9340 → 0.9361 | 0.9430 → 0.9418 | 69.7% → 60.2% | 68.9% → 68.1% | 71.2% → 68.8% |
| prepend 50 | 3,644 (1,531) | 0.9500 → 0.9094 | 0.9418 → 0.9444 | 0.9486 → 0.9503 | 72.1% → 61.4% | 71.7% → 70.8% | 71.2% → 69.6% |

Change in malware TPR at the fixed threshold, C versus A (seed-paired):

| edit | A: change in TPR fixed (a), points | C | C − A [95% over seeds] | reports that fit: A | reports that fit: C | reports that fit: C − A |
|---|---|---|---|---|---|---|
| insert 1 | -1.6 | -1.0 | +0.6 [-0.1, +1.4] | -1.6 | -1.5 | +0.1 [-1.0, +1.1] |
| insert 5 | -6.2 | -2.5 | +3.7 [+2.2, +5.3] | -5.9 | -2.3 | +3.6 [+1.8, +5.6] |
| insert 20 | -16.4 | -3.2 | +13.2 [+11.0, +15.5] | -5.3 | -1.8 | +3.5 [+0.7, +6.3] |
| insert 50 | -25.9 | -1.4 | +24.5 [+21.6, +27.5] | -8.3 | -1.9 | +6.5 [+2.4, +10.8] |
| prepend 1 | -6.5 | -2.8 | +3.7 [+1.6, +5.8] | -3.1 | -2.7 | +0.4 [-1.3, +2.4] |
| prepend 5 | -19.8 | -3.7 | +16.1 [+13.0, +18.9] | -10.1 | -3.1 | +7.0 [+4.2, +9.9] |
| prepend 20 | -35.2 | -1.4 | +33.9 [+30.6, +37.0] | -9.5 | -2.3 | +7.2 [+3.9, +10.5] |
| prepend 50 | -42.5 | -5.7 | +36.8 [+34.1, +39.5] | -10.6 | -1.6 | +9.0 [+4.7, +13.6] |

## Caveats

- **April was used to judge whether the recipe goal was met** (which options to try and whether to add regime J), so "A reaches the released model" is not a clean held-out result. Epochs were never chosen on April.
- **Regime J compares A after 1 epoch with C after 10** (the rule's outcome). At 1 epoch each C is still ahead (0.9593 against 0.9486), and A does not improve with more epochs in the recipe study.
- **C's shuffle invariance means it uses little about call order.** It behaves close to a bag of calls with some within-chunk structure; here that costs nothing at 1% FPR but may be why it is weaker at 0.1% FPR. Why the fixed encoding helps an order-free model is not explained by these runs.
- **The added calls are copies from the same report.** No test uses calls chosen by an attacker (for example benign-looking calls from other reports), deletion, or edits to malware only.
- **Many subsets were tested**; isolated significant cells may be chance. The group-bootstrap intervals are wide because April has few independent groups; going from 3 to 10 seeds barely narrowed them.
- **B0 and C0** were rerun on 3 seeds only. The old unmasked runs of `results/pooling` appear as "(v1)" rows in `tables.md`. LightGBM has 3 seeds, reused as seed mod 3.
- Robustness intervals are over seeds only. Padding positions are still seen by the attention in B and C (only the pooling ignores them). fp16 training is not bit-reproducible.

## Files

- `briefing_for_planner.md`: self-contained summary of the state and the open decisions.
- `released_training.md`, `recipe_study.md`, `regime_J_epochs.json`, `tables.md` (regime S), `tables_J.md` (regime J), `followups_same_epoch.md`, `followups_ensemble.md`, `graded_edits.md`, and the `.json` files with the numbers (`evaluation*.json`, `perturb_check*.json`, `graded_edits.json`, ...).
- Code: `hier_nebula/pooling_variants.py` (`masked_mean`, variants `Bm`, `Cm`), `hier_nebula/test_pooling.py`, `scripts/kaggle/train_pooling_v2.py`, `launch_pooling_v2.py`, `kernel_v2_*`, `scripts/pooling_v2/` (`recipe_study.py`, `evaluate_v2.py`, `perturb_check.py`, `graded_edits.py`, `followups.py`).
- Kaggle outputs (not in the repository): `../pooling_v2_full_output` (regime S, 36 runs, 4.7 GB, a checkpoint after every epoch), `../pooling_v2_all_output` (regime J, 20 runs), `../pooling_v2_recipe_merged` (recipe study).

```bash
python scripts/pooling_v2/recipe_study.py --src ../pooling_v2_recipe_merged --runs A,A_steps3000,A_all
python scripts/pooling_v2/evaluate_v2.py --src ../pooling_v2_full_output --rule auc
python scripts/pooling_v2/evaluate_v2.py --src ../pooling_v2_all_output --tag _all --rule fixed --fixed A=1,C=10
python scripts/pooling_v2/perturb_check.py --src ../pooling_v2_full_output --work ../pooling_v2_work --tokens <folder with tokens_512.npy>
python scripts/pooling_v2/perturb_check.py --src ../pooling_v2_all_output --work ../pooling_v2_work --tag _all --select final --variants A,C
python scripts/pooling_v2/graded_edits.py --src ../pooling_v2_full_output --work ../pooling_v2_work
python scripts/pooling_v2/followups.py same_epoch --src ../pooling_v2_full_output
python scripts/pooling_v2/followups.py ensemble --src ../pooling_v2_full_output --src-j ../pooling_v2_all_output
```
