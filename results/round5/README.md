# Round 5: final-quality runs of ATT+bal and the tests an examiner will ask for

Builds on `results/pooling_v4` (rounds 4 and 4b). Nothing in this folder is committed. Rules used throughout: thresholds fixed at 1% and 0.1% FPR on the unedited April benign scores of each model and seed;
group-bootstrap intervals over April `hash_apis` (1,000 resamples) and seed-paired intervals (95% over seeds); edited reports exist in memory only (only scores and aggregate numbers are written); only the
EVAL padding pool of `results/pooling_v4/pools.json` is used for testing (the TRAIN pool is used for training augmentation, and once, to define "rarest 20% of API names", in `prep_pools5.py`).

Models: **ATT+bal**, **MM+bal**, **C+bal** = C with attention / mean+max / mean pooling, fixed position encoding, 512 tokens, trained on all of January (regime J) with balanced padding (every training report, malware or
benign, gets 1-50 calls of the TRAIN pool inserted or prepended with probability 0.5); G1: seeds 0-9, 4 epochs, epoch 2 is primary (same data order and learning-rate schedule as a 2-epoch run; epoch 4 as a second table).
References on the same seeds: **released Nebula**, **A (J)** (flatten pooling, 1 epoch), **C (J)** (mean + fixed position encoding, 10 epochs), **C (J, 2 epochs)** (= C after its epoch 2), whole-report **F**
(`results/fulltrace`, seeds 0-4), and the bag-of-API LightGBM of `results/go_no_go` for the rank averages.

## Verdict

1. **ATT+bal beats the released Nebula on ranking quality, not clearly at a fixed false-positive rate.** 10 seeds, April: AUC 0.9752 against 0.9586 (+0.0166 [+0.0043, +0.0342]; unseen sequences +0.0262 [+0.0052, +0.0558], seen +0.0027 [−0.0038, +0.0122]); TPR at 1% FPR 76.5% against 75.0% (+1.5 [−6.4, +8.7]); at 0.1% FPR 57.0% against 51.7% (+5.3 [−16.7, +59.0]; the 0.1% threshold is set by 8 benign reports, the released model's own interval is 0-67%). With the LightGBM rank average the gap is +0.0070 AUC [+0.0015, +0.0153] and +4.3 [−1.0, +12.8] TPR at 1%. Against the retrained baselines the gain is clear (seed-paired, 10 seeds): ATT+bal − A (J) +0.0266 AUC [+0.0183, +0.0339], +17.4 [+9.1, +26.5] points at 0.1% FPR; − C (J, 2 epochs) +0.0136 [+0.0078, +0.0198], +41.8 [+37.5, +46.1]. The ensemble of the 10 seeds gives 0.9782 / 75.8% / 60.1%. Where ATT+bal clearly beats the released model is under edits (points 3 and 4 and items 3 and 5).
2. **The 0.1% FPR result keeps its ordering on the second test set, but the evidence is weak.** January validation side (regime S, 10 seeds; 9,619 reports, 2,103 benign from 678 distinct API sequences, so the 0.1% threshold lets only 2 benign reports lie above it): ATT+bal 46.0% [22.1, 80.0] against MM+bal 31.9%, C+bal 27.2%, ATT without padding 20.0% (ATT+bal − ATT +26.0 [+5.8, +48.3]) and A 36.0% (ATT+bal − A +10.1 [−1.5, +20.4]); at 1% FPR ATT+bal and A are tied at 71.4%. On April the standardised partial AUC to 1% FPR is 0.8384 [0.7745, 0.8865] for ATT+bal against 0.8286 for the released model and 0.7942 for A; with 4 / 8 / 12 benign reports allowed above the threshold ATT+bal has 43.8% / 57.0% / 63.5% against 41.5% / 51.8% / 55.8% for the released model. Same direction on both sets, intervals of 20-60 points, no significant gain over A or the released model.
3. **Unseen padding: block, other-source and clean padding cost 4-10 points at 20 calls; rare API names and padding that fills the window break it.** TPR at 1% FPR after prepending 20 / 50 calls (unedited 76.7%): block of consecutive calls 72.6% / 62.9%, other benign source (windows_syswow64) 72.7% / 60.0%, clean only 72.4% / 59.8%; ATT+bal's padded benign reports stay at 0.4-2.3% FPR (C+bal and MM+bal up to 3.5% with block padding). **Rare API names (rarest 20% of the TRAIN pool): 69.5% at 20 but 10.7% at 50 calls (5.9% at 0.1% FPR); calls ranked by the C (J) surrogate: 72.0% / 7.0%; by the LightGBM surrogate: 70.7% / 30.1%** (long calls fill the 512-token window; for the released model and A the same padding raises their scores, so padded benign reports are flagged at up to 99%). White-box greedy padding of 500 malware reports (200 candidates per step, 20 steps): ATT+bal falls from 78.2% to 54.0% (0.1% FPR: 54.8% to 31.8%), C+bal to 35.0% (0.0%), the released Nebula to 1.6% (0.6%). ATT+bal is far more robust than the released model and C, but not immune: an adversary that fills the window can still hide the malware.
4. **Rotation: ATT+bal does not use token position, only content.** Rotating the 512 window at a call boundary changes TPR at 1% FPR by −0.1 / −0.3 / +0.3 points (25 / 50 / 75%), like C (J) (+1.2 / +0.6 / 0.0) and F, while the released Nebula and A (J) lose 38-51 points (AUC 0.43-0.59). Rotating the whole call list before taking the first 512 tokens costs ATT+bal 7.3 [−13.5, −2.7] / 11.3 [−24.1, −0.7] / 0.0 points (C (J) 18-26 points, F 0.5-3.6): the signal is spread over the report, with more in the first calls than in the last ones; on reports that fit in 512 tokens nothing changes (74.0% to 74.0-74.5%). The whole-report ATT+bal (G3) is unaffected by both rotations (≤ 0.5 points) but does not gain accuracy (AUC 0.9578, TPR 76.1% at 1%, 55.0% at 0.1% FPR; ATT+bal on 512 tokens 0.9757 / 76.7% / 53.7%).
5. **Recommendation:** use ATT+bal at 512 tokens (balanced padding is what makes pooling robust; the attention pooling keeps the 0.1% FPR result and the padding resistance that mean pooling loses). Not shown: robustness to padding chosen with white-box access that fills the window, or to API names never seen in training, and a significant fixed-FPR gain over the released Nebula on clean data.


## GPU part (Kaggle, T4 x2)

Quota before the batch: 24.32 h of 30 h used (5.68 h remaining); weekly quota resets **2026-11-21 00:00 UTC**. A 1-epoch smoke run (4 jobs: ATT+bal J, MM+bal J, ATT+bal S, A S; 52-64 s per epoch, 2.5 min wall, 0.04 h)
gave a batch estimate of 2.3-2.6 h at the charge rate of about 1 x wall time, far below the 6 h limit, so the batch was launched without asking. (The whole-report run of `results/fulltrace` had been charged 2.9 x
its wall time; this round the charge was 1.0 x.) Quota after the round: **26.84 h used, 3.16 h remaining**, same reset.

| run | what | jobs | wall time | quota charged |
|---|---|---|---|---|
| G1 | ATT+bal, MM+bal, C+bal, regime J, balanced padding, seeds 0-9, 4 epochs, scores after every epoch (fp32 epoch checkpoints) | 30 | 64.8 min (63 s per epoch) | 1.07 h |
| G2 | regime S (January train side only; the validation side is held out): ATT+bal, MM+bal, C+bal, ATT (no padding), A, seeds 0-9, 2 epochs | 50 | 49.1 min (55 s per epoch; queued 19 min before starting) | 0.82 h |
| G3 | ATT+bal over the whole report (up to 4,096 tokens), balanced padding of the full report, regime J, seeds 0-4, 2 epochs | 5 | 34.1 min (337 s per epoch) | 0.58 h |

Checks of the G1 runs: the CPU logits of the epoch-2 checkpoints equal the Kaggle logits (maximum difference 0.0000 on 1,500 reports, 4 runs); epoch 2 of a 4-epoch run reproduces the round-4b 2-epoch run of the same
seed (April AUC 0.9787 and 0.9787, score correlation 1.0000). The augmentation tokens were precomputed on this machine (`scripts/pooling_v4/make_aug.py --balanced`, `make_aug_full.py` for G3) and uploaded as private
Kaggle datasets; the regime S runs drop the validation-side rows of those files.


## Item 1: final accuracy, 10 seeds (epoch 2 of the G1 runs)

Single models: mean over 10 seeds (released: one model); `+ LightGBM`: percentile rank average with the bag-of-API LightGBM (seeds 0-2 as seed mod 3); `(ensemble)`: mean logit of the 10 seeds. Thresholds (a) at 1% / 0.1% FPR of the April benign scores of each model and seed; intervals: group bootstrap over April hash_apis (1,000 resamples). All subsets (seen, unseen, distance quartiles, 1 / 2-3 / 4-8 chunks), seed spread and all paired differences are in `accuracy.md`.

| subset | model | n (malware) | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|---|
| all | ATT+bal | 17,402 (9,399) | 0.9752 [0.9589, 0.9847] | 76.5% [64.9%, 84.2%] | 57.0% [36.8%, 68.3%] |
| all | ATT+bal + LightGBM | 17,402 (9,399) | 0.9813 [0.9636, 0.9912] | 83.8% [76.1%, 89.5%] | 57.6% [35.2%, 70.0%] |
| all | ATT+bal (ensemble) | 17,402 (9,399) | 0.9782 [0.9628, 0.9871] | 75.8% [63.9%, 85.5%] | 60.1% [38.7%, 72.5%] |
| all | MM+bal | 17,402 (9,399) | 0.9760 [0.9615, 0.9848] | 76.3% [63.1%, 85.0%] | 38.0% [19.8%, 57.2%] |
| all | MM+bal + LightGBM | 17,402 (9,399) | 0.9823 [0.9660, 0.9912] | 83.5% [74.3%, 89.3%] | 49.5% [33.8%, 63.7%] |
| all | MM+bal (ensemble) | 17,402 (9,399) | 0.9791 [0.9657, 0.9872] | 77.8% [63.9%, 86.2%] | 37.9% [22.7%, 60.9%] |
| all | C+bal | 17,402 (9,399) | 0.9737 [0.9573, 0.9836] | 77.5% [65.9%, 85.0%] | 27.3% [8.0%, 51.4%] |
| all | C+bal + LightGBM | 17,402 (9,399) | 0.9810 [0.9627, 0.9909] | 83.7% [75.6%, 89.5%] | 45.2% [29.0%, 61.3%] |
| all | C+bal (ensemble) | 17,402 (9,399) | 0.9792 [0.9658, 0.9874] | 77.0% [63.6%, 87.8%] | 26.0% [7.1%, 57.4%] |
| all | C (J, 2 epochs) | 17,402 (9,399) | 0.9616 [0.9394, 0.9766] | 73.6% [51.9%, 83.7%] | 15.2% [7.2%, 36.6%] |
| all | C (J, 2 epochs) + LightGBM | 17,402 (9,399) | 0.9785 [0.9600, 0.9892] | 80.1% [65.4%, 87.6%] | 43.2% [29.5%, 59.3%] |
| all | C (J, 2 epochs) (ensemble) | 17,402 (9,399) | 0.9659 [0.9432, 0.9804] | 74.1% [53.2%, 85.8%] | 15.6% [7.6%, 47.8%] |
| all | C (J) | 17,402 (9,399) | 0.9644 [0.9433, 0.9785] | 73.8% [58.1%, 83.2%] | 20.4% [10.5%, 42.4%] |
| all | C (J) + LightGBM | 17,402 (9,399) | 0.9797 [0.9616, 0.9899] | 80.9% [69.9%, 87.8%] | 45.3% [30.6%, 61.5%] |
| all | C (J) (ensemble) | 17,402 (9,399) | 0.9672 [0.9449, 0.9815] | 75.0% [61.0%, 84.7%] | 25.3% [12.6%, 51.6%] |
| all | A (J) | 17,402 (9,399) | 0.9486 [0.9132, 0.9710] | 71.9% [59.9%, 80.4%] | 39.6% [26.7%, 50.8%] |
| all | A (J) + LightGBM | 17,402 (9,399) | 0.9732 [0.9464, 0.9878] | 78.7% [69.6%, 86.1%] | 49.3% [34.6%, 64.1%] |
| all | A (J) (ensemble) | 17,402 (9,399) | 0.9590 [0.9270, 0.9795] | 75.5% [64.2%, 83.8%] | 43.3% [27.3%, 60.1%] |
| all | released Nebula | 17,402 (9,399) | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 51.7% [0.0%, 67.0%] |
| all | LightGBM bag of API names | 17,402 (9,399) | 0.9499 [0.9147, 0.9757] | 63.0% [33.5%, 74.8%] | 31.3% [18.1%, 45.4%] |
| all | released Nebula + LightGBM | 17,402 (9,399) | 0.9744 [0.9498, 0.9884] | 79.6% [68.9%, 87.6%] | 55.0% [40.2%, 70.9%] |

Seed-paired differences (mean over the 10 seeds [95% over seeds]; TPR in points):

| difference | seeds | AUC | TPR@1% | TPR@0.1% |
|---|---|---|---|---|
| ATT+bal − A (J) | 10 | +0.0266 [+0.0183, +0.0339] | +4.6 [+2.6, +6.6] | +17.4 [+9.1, +26.5] |
| ATT+bal − C (J) | 10 | +0.0108 [+0.0051, +0.0170] | +2.8 [+1.3, +4.2] | +36.6 [+32.4, +40.7] |
| ATT+bal − C (J, 2 epochs) | 10 | +0.0136 [+0.0078, +0.0198] | +3.0 [+1.3, +4.6] | +41.8 [+37.5, +46.1] |
| MM+bal − A (J) | 10 | +0.0273 [+0.0188, +0.0351] | +4.4 [+2.0, +6.5] | -1.6 [-12.2, +7.9] |
| MM+bal − C (J) | 10 | +0.0116 [+0.0067, +0.0168] | +2.5 [+0.5, +4.5] | +17.6 [+9.3, +25.7] |
| MM+bal − C (J, 2 epochs) | 10 | +0.0144 [+0.0090, +0.0198] | +2.7 [+0.7, +4.8] | +22.9 [+15.6, +30.4] |
| C+bal − A (J) | 10 | +0.0250 [+0.0167, +0.0325] | +5.6 [+3.5, +7.9] | -12.3 [-23.2, -1.2] |
| C+bal − C (J) | 10 | +0.0093 [+0.0024, +0.0158] | +3.8 [+1.7, +5.7] | +6.9 [-0.7, +14.8] |
| C+bal − C (J, 2 epochs) | 10 | +0.0121 [+0.0050, +0.0187] | +4.0 [+1.9, +5.9] | +12.1 [+4.3, +20.1] |

ATT+bal against the released Nebula and the other models, group-bootstrap intervals (all April reports, and the subsets that matter):

| difference | subset | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|
| ATT+bal − released Nebula | all | +0.0166 [+0.0043, +0.0342] | +1.5 [-6.4, +8.7] | +5.3 [-16.7, +59.0] |
| ATT+bal − released Nebula | seen | +0.0027 [-0.0038, +0.0122] | +6.3 [+1.2, +12.8] | +0.4 [-28.7, +66.0] |
| ATT+bal − released Nebula | unseen | +0.0262 [+0.0052, +0.0558] | -0.6 [-12.2, +9.6] | +7.5 [-17.8, +56.1] |
| ATT+bal − released Nebula | 1 chunk | +0.0071 [-0.0120, +0.0236] | +12.6 [-0.8, +24.7] | +12.0 [-22.9, +58.4] |
| ATT+bal − released Nebula | 2-3 chunks | +0.0016 [-0.0047, +0.0113] | -5.5 [-20.7, +4.4] | +5.4 [-30.9, +56.2] |
| ATT+bal − released Nebula | 4-8 chunks | +0.0495 [+0.0077, +0.1262] | -0.4 [-3.1, +2.0] | -1.5 [-32.1, +68.2] |
| ATT+bal + LightGBM − released Nebula + LightGBM | all | +0.0070 [+0.0015, +0.0153] | +4.3 [-1.0, +12.8] | +2.6 [-13.5, +13.1] |
| ATT+bal + LightGBM − released Nebula + LightGBM | seen | +0.0025 [-0.0012, +0.0095] | +2.0 [-1.1, +6.4] | -1.8 [-25.8, +3.2] |
| ATT+bal + LightGBM − released Nebula + LightGBM | unseen | +0.0098 [+0.0016, +0.0225] | +5.3 [-2.2, +17.0] | +4.6 [-14.7, +19.2] |
| ATT+bal + LightGBM − released Nebula + LightGBM | 1 chunk | +0.0062 [-0.0047, +0.0162] | +14.7 [-1.7, +33.2] | +3.2 [-30.4, +16.1] |
| ATT+bal + LightGBM − released Nebula + LightGBM | 2-3 chunks | +0.0001 [-0.0022, +0.0026] | -0.1 [-3.1, +3.6] | +2.9 [-24.6, +25.6] |
| ATT+bal + LightGBM − released Nebula + LightGBM | 4-8 chunks | +0.0188 [+0.0001, +0.0567] | -0.5 [-1.8, +1.2] | +1.7 [-17.1, +18.8] |
| ATT+bal (ensemble) − released Nebula | all | +0.0196 [+0.0068, +0.0380] | +0.9 [-8.1, +9.4] | +8.4 [-14.5, +65.3] |
| ATT+bal (ensemble) − released Nebula | seen | +0.0048 [-0.0025, +0.0168] | +6.2 [+0.8, +13.8] | +1.7 [-25.1, +71.1] |
| ATT+bal (ensemble) − released Nebula | unseen | +0.0288 [+0.0077, +0.0597] | -1.6 [-14.2, +10.2] | +11.4 [-15.8, +64.4] |
| ATT+bal (ensemble) − released Nebula | 1 chunk | +0.0129 [-0.0055, +0.0308] | +12.6 [-0.6, +25.4] | +16.2 [-23.4, +66.5] |
| ATT+bal (ensemble) − released Nebula | 2-3 chunks | +0.0036 [-0.0017, +0.0140] | -6.9 [-24.8, +8.5] | +7.1 [-29.5, +61.7] |
| ATT+bal (ensemble) − released Nebula | 4-8 chunks | +0.0514 [+0.0086, +0.1328] | -0.9 [-3.6, +2.5] | +2.3 [-26.4, +75.2] |
| ATT+bal − A (J) | all | +0.0266 [+0.0105, +0.0515] | +4.6 [+0.3, +10.3] | +17.4 [+2.1, +27.9] |
| ATT+bal − A (J) | seen | +0.0069 [+0.0004, +0.0182] | +8.3 [+2.4, +16.1] | +17.8 [-5.8, +34.3] |
| ATT+bal − A (J) | unseen | +0.0430 [+0.0131, +0.0895] | +3.0 [-2.7, +10.0] | +17.2 [+1.0, +29.1] |
| ATT+bal − A (J) | 1 chunk | +0.0131 [-0.0055, +0.0311] | +8.1 [-3.3, +19.1] | +29.4 [+6.1, +44.2] |
| ATT+bal − A (J) | 2-3 chunks | +0.0120 [+0.0030, +0.0370] | +3.3 [-2.8, +11.3] | +18.5 [+0.4, +29.1] |
| ATT+bal − A (J) | 4-8 chunks | +0.0508 [+0.0077, +0.1264] | +2.9 [+0.7, +6.2] | +4.0 [-19.1, +18.3] |
| ATT+bal − C (J) | all | +0.0108 [+0.0013, +0.0243] | +2.8 [-1.4, +13.5] | +36.6 [+15.4, +46.8] |
| ATT+bal − C (J) | seen | +0.0050 [+0.0011, +0.0111] | +7.0 [+1.2, +16.8] | +31.0 [-1.2, +45.2] |
| ATT+bal − C (J) | unseen | +0.0173 [-0.0023, +0.0458] | +0.8 [-4.0, +13.5] | +39.1 [+13.9, +50.5] |
| ATT+bal − C (J) | 1 chunk | +0.0020 [-0.0121, +0.0111] | +3.1 [-4.4, +13.4] | +27.7 [-4.2, +48.5] |
| ATT+bal − C (J) | 2-3 chunks | +0.0036 [-0.0002, +0.0123] | +3.0 [-3.3, +21.6] | +42.8 [+12.8, +55.2] |
| ATT+bal − C (J) | 4-8 chunks | +0.0299 [+0.0020, +0.0812] | +2.2 [-0.7, +7.5] | +37.4 [+5.2, +54.0] |
| ATT+bal − MM+bal | all | -0.0008 [-0.0034, +0.0011] | +0.3 [-2.6, +4.5] | +19.0 [+5.1, +29.9] |
| ATT+bal − MM+bal | seen | +0.0012 [-0.0014, +0.0029] | -1.1 [-3.4, +6.4] | +26.9 [+7.5, +38.3] |
| ATT+bal − MM+bal | unseen | -0.0029 [-0.0076, -0.0001] | +0.8 [-3.0, +4.9] | +15.4 [+0.8, +29.5] |
| ATT+bal − MM+bal | 1 chunk | -0.0028 [-0.0081, +0.0002] | -3.0 [-7.7, -0.2] | +10.0 [-18.4, +30.5] |
| ATT+bal − MM+bal | 2-3 chunks | -0.0015 [-0.0047, -0.0001] | +1.9 [-3.0, +11.0] | +25.9 [+9.8, +39.0] |
| ATT+bal − MM+bal | 4-8 chunks | -0.0044 [-0.0131, -0.0004] | +1.4 [+0.2, +5.5] | +19.0 [-0.1, +36.3] |
| ATT+bal − C+bal | all | +0.0015 [-0.0001, +0.0035] | -1.0 [-3.7, +1.9] | +29.7 [+11.0, +42.9] |
| ATT+bal − C+bal | seen | +0.0020 [+0.0004, +0.0041] | +0.3 [-2.2, +4.8] | +33.8 [+8.0, +51.5] |
| ATT+bal − C+bal | unseen | -0.0008 [-0.0038, +0.0017] | -1.6 [-5.0, +1.1] | +27.8 [+6.0, +43.6] |
| ATT+bal − C+bal | 1 chunk | -0.0000 [-0.0043, +0.0029] | -2.0 [-6.0, +0.7] | +11.5 [-22.5, +34.5] |
| ATT+bal − C+bal | 2-3 chunks | -0.0017 [-0.0053, -0.0001] | -2.2 [-7.3, +3.1] | +43.2 [+15.4, +55.7] |
| ATT+bal − C+bal | 4-8 chunks | -0.0019 [-0.0084, +0.0020] | +1.5 [+0.1, +4.6] | +30.5 [+7.8, +57.0] |

At 4 epochs (second table, `accuracy_epoch4.md`; the 2-epoch results above are primary):

| subset | model | n (malware) | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|---|
| all | ATT+bal | 17,402 (9,399) | 0.9740 [0.9570, 0.9841] | 75.5% [64.1%, 84.0%] | 59.4% [38.5%, 70.0%] |
| all | ATT+bal + LightGBM | 17,402 (9,399) | 0.9811 [0.9628, 0.9912] | 84.1% [76.1%, 89.6%] | 58.1% [36.6%, 70.5%] |
| all | ATT+bal (ensemble) | 17,402 (9,399) | 0.9771 [0.9616, 0.9863] | 76.7% [64.1%, 84.6%] | 61.4% [42.1%, 73.5%] |
| all | MM+bal | 17,402 (9,399) | 0.9757 [0.9610, 0.9847] | 76.2% [63.4%, 85.1%] | 36.3% [21.6%, 57.8%] |
| all | C+bal | 17,402 (9,399) | 0.9736 [0.9570, 0.9837] | 77.7% [65.2%, 84.9%] | 29.5% [8.0%, 55.2%] |

## Item 2: low-FPR, measured more stably

### Benign reports above the thresholds (April)

The 0.1% threshold of April is the (floor(0.001 x 8,003) + 1) = 9th highest benign score: only 8 benign reports may lie above it, which is why TPR at 0.1% FPR is unstable (ties can add reports above the threshold).

| model | benign reports in April | allowed above 0.1% threshold (floor) | benign above the 0.1% threshold (mean over seeds) | allowed above 1% threshold | benign above the 1% threshold |
|---|---|---|---|---|---|
| ATT+bal | 8003 | 8 | 8.0 | 80 | 79.4 |
| MM+bal | 8003 | 8 | 8.0 | 80 | 80.0 |
| C+bal | 8003 | 8 | 8.0 | 80 | 78.4 |
| C (J, 2 epochs) | 8003 | 8 | 6.7 | 80 | 79.9 |
| C (J) | 8003 | 8 | 6.8 | 80 | 79.9 |
| A (J) | 8003 | 8 | 8.0 | 80 | 80.0 |
| released Nebula | 8003 | 8 | 8.0 | 80 | 80.0 |

### TPR when 4 / 8 / 12 benign reports may lie above the threshold (April)

| model | TPR with 4 benign above the threshold (0.050% FPR) | TPR with 8 benign above the threshold (0.100% FPR) | TPR with 12 benign above the threshold (0.150% FPR) |
|---|---|---|---|
| ATT+bal | 43.8% | 57.0% | 63.5% |
| MM+bal | 23.9% | 38.0% | 46.0% |
| C+bal | 10.2% | 27.3% | 39.5% |
| C (J, 2 epochs) | 9.1% | 15.2% | 20.2% |
| C (J) | 12.4% | 20.4% | 27.1% |
| A (J) | 33.3% | 39.6% | 44.2% |
| released Nebula | 41.5% | 51.8% | 55.8% |

### Standardised partial AUC up to 1% FPR (McClish), April

Mean over seeds [95% group-bootstrap interval, 300 resamples].

| model | standardised partial AUC to 1% FPR |
|---|---|
| ATT+bal | 0.8384 [0.7745, 0.8865] |
| MM+bal | 0.8092 [0.7373, 0.8709] |
| C+bal | 0.8026 [0.7392, 0.8590] |
| C (J, 2 epochs) | 0.7371 [0.6492, 0.8244] |
| C (J) | 0.7607 [0.6820, 0.8342] |
| A (J) | 0.7942 [0.7369, 0.8488] |
| released Nebula | 0.8286 [0.7732, 0.8794] |

### Second test set: the January validation side (regime S models, G2)

Validation side: 9,619 reports (7,516 malware, 2,103 benign; 678 distinct API sequences = groups). The 0.1% FPR threshold lets floor(0.001 x 2,103) = 2 benign reports lie above it, the 1% threshold 21. Models trained on the train side of January only, 2 epochs, seeds listed in the table; thresholds from the benign scores of the same set. Group-bootstrap 95% intervals (1,000 resamples over API-sequence groups); the ensemble is the mean logit of the seeds.

| model | seeds | AUC | TPR@1% (a) | TPR@0.1% (a) | standardised pAUC to 1% FPR |
|---|---|---|---|---|---|
| ATT+bal (S) | 10 | 0.9490 [0.9107, 0.9801] | 71.4% [46.7%, 86.8%] | 46.0% [22.1%, 80.0%] | 0.8060 [0.7020, 0.9167] |
| ATT+bal (S) (ensemble) | 1 | 0.9533 [0.9205, 0.9823] | 70.9% [47.3%, 86.5%] | 53.9% [21.1%, 81.4%] | 0.8278 [0.7308, 0.9205] |
| MM+bal (S) | 10 | 0.9510 [0.9165, 0.9795] | 68.5% [41.2%, 87.3%] | 31.9% [10.9%, 61.0%] | 0.7392 [0.6299, 0.8813] |
| MM+bal (S) (ensemble) | 1 | 0.9554 [0.9262, 0.9820] | 74.2% [37.8%, 89.5%] | 34.7% [10.1%, 67.4%] | 0.7621 [0.6323, 0.8972] |
| C+bal (S) | 10 | 0.9397 [0.9016, 0.9743] | 50.5% [28.3%, 80.1%] | 27.2% [10.4%, 55.2%] | 0.6854 [0.5973, 0.8295] |
| C+bal (S) (ensemble) | 1 | 0.9448 [0.9079, 0.9785] | 44.9% [22.0%, 85.6%] | 33.9% [8.5%, 63.2%] | 0.6826 [0.5868, 0.8476] |
| ATT (S, no padding) | 10 | 0.9594 [0.9345, 0.9784] | 54.6% [32.5%, 79.5%] | 20.0% [8.2%, 49.6%] | 0.6923 [0.5973, 0.8288] |
| ATT (S, no padding) (ensemble) | 1 | 0.9662 [0.9441, 0.9822] | 66.8% [43.5%, 84.9%] | 18.7% [8.4%, 69.0%] | 0.7618 [0.6549, 0.8675] |
| A (S) | 10 | 0.9448 [0.9157, 0.9798] | 71.4% [50.3%, 87.8%] | 36.0% [18.7%, 66.5%] | 0.7853 [0.6876, 0.9040] |
| A (S) (ensemble) | 1 | 0.9489 [0.9184, 0.9841] | 74.4% [51.8%, 90.6%] | 52.5% [24.6%, 84.3%] | 0.8400 [0.7332, 0.9421] |

Paired differences on the validation side:

| difference | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|
| ATT+bal (S) − A (S) | +0.0042 [-0.0225, +0.0242] | -0.0 [-8.5, +10.4] | +10.1 [-1.5, +20.4] |
| ATT+bal (S) − ATT (S, no padding) | -0.0104 [-0.0331, +0.0120] | +16.7 [-9.4, +37.9] | +26.0 [+5.8, +48.3] |
| ATT+bal (S) − C+bal (S) | +0.0093 [-0.0005, +0.0178] | +20.8 [-1.1, +38.1] | +18.8 [+4.6, +44.2] |
| MM+bal (S) − A (S) | +0.0062 [-0.0165, +0.0260] | -2.9 [-23.6, +6.2] | -4.1 [-30.2, +9.5] |
| MM+bal (S) − ATT (S, no padding) | -0.0083 [-0.0278, +0.0114] | +13.8 [-9.3, +26.7] | +11.9 [-1.5, +25.1] |
| MM+bal (S) − C+bal (S) | +0.0113 [+0.0023, +0.0189] | +17.9 [-1.8, +29.8] | +4.7 [-1.5, +13.2] |
| MM+bal (S) − ATT+bal (S) | +0.0020 [-0.0052, +0.0103] | -2.9 [-24.3, +5.8] | -14.1 [-40.9, -2.3] |
| C+bal (S) − A (S) | -0.0051 [-0.0288, +0.0111] | -20.8 [-39.5, +1.8] | -8.7 [-33.2, +4.4] |
| C+bal (S) − ATT (S, no padding) | -0.0197 [-0.0426, +0.0049] | -4.1 [-23.1, +16.1] | +7.3 [-3.6, +15.3] |
| C+bal (S) − ATT+bal (S) | -0.0093 [-0.0178, +0.0005] | -20.8 [-38.1, +1.1] | -18.8 [-44.2, -4.6] |
| ATT+bal (S) (ensemble) − A (S) (ensemble) | +0.0044 [-0.0230, +0.0246] | -3.5 [-9.4, +1.0] | +1.4 [-10.5, +13.1] |
| ATT+bal (S) (ensemble) − ATT (S, no padding) (ensemble) | -0.0129 [-0.0344, +0.0088] | +4.1 [-10.8, +24.7] | +35.2 [-4.8, +52.7] |
| ATT+bal (S) (ensemble) − C+bal (S) (ensemble) | +0.0085 [-0.0016, +0.0193] | +26.1 [-4.2, +52.2] | +20.0 [-0.4, +51.2] |
| MM+bal (S) (ensemble) − A (S) (ensemble) | +0.0065 [-0.0178, +0.0279] | -0.1 [-38.9, +3.4] | -17.8 [-45.2, +0.8] |
| MM+bal (S) (ensemble) − ATT (S, no padding) (ensemble) | -0.0108 [-0.0288, +0.0083] | +7.4 [-29.3, +24.8] | +16.1 [-12.3, +30.9] |
| MM+bal (S) (ensemble) − C+bal (S) (ensemble) | +0.0106 [+0.0005, +0.0212] | +29.4 [-0.9, +48.7] | +0.8 [-4.1, +19.7] |
| MM+bal (S) (ensemble) − ATT+bal (S) (ensemble) | +0.0021 [-0.0048, +0.0101] | +3.3 [-36.9, +8.3] | -19.2 [-43.5, +2.7] |
| C+bal (S) (ensemble) − A (S) (ensemble) | -0.0041 [-0.0301, +0.0155] | -29.5 [-54.5, +2.2] | -18.6 [-52.9, -0.8] |
| C+bal (S) (ensemble) − ATT (S, no padding) (ensemble) | -0.0214 [-0.0480, +0.0038] | -22.0 [-44.6, +15.7] | +15.2 [-14.7, +29.0] |
| C+bal (S) (ensemble) − ATT+bal (S) (ensemble) | -0.0085 [-0.0193, +0.0016] | -26.1 [-52.2, +4.2] | -20.0 [-51.2, +0.4] |

### The 20 highest-scoring April benign reports

Full lists (first 30 calls of every report) in `top_benign.md`. Comparison:

- ATT+bal and C (J): 11 reports in both top-20 lists (9 shared sequences); Spearman correlation over the 8,003 benign April reports 0.63; the top 20 of ATT+bal sit at ranks 1–209 in C (J) (median 17); the top 20 of C (J) sit at ranks 3–242 in ATT+bal (median 18).
- ATT+bal and released Nebula: 5 reports in both top-20 lists (4 shared sequences); Spearman correlation over the 8,003 benign April reports 0.64; the top 20 of ATT+bal sit at ranks 5–3315 in released Nebula (median 302); the top 20 of released Nebula sit at ranks 1–4458 in ATT+bal (median 231).
- C (J) and released Nebula: 3 reports in both top-20 lists (3 shared sequences); Spearman correlation over the 8,003 benign April reports 0.66; the top 20 of C (J) sit at ranks 3–718 in released Nebula (median 389); the top 20 of released Nebula sit at ranks 4–3613 in C (J) (median 162).
- ATT+bal: 9/20 share their sequence with a malware report; median calls 10; distinct sequences 15; sources {'clean': 20}; chunks {1: 14, 2: 2, 3: 3, 4: 1}; seen in January 9/20.
- C (J): 8/20 share their sequence with a malware report; median calls 12; distinct sequences 12; sources {'clean': 20}; chunks {1: 20}; seen in January 8/20.
- released Nebula: 8/20 share their sequence with a malware report; median calls 8; distinct sequences 18; sources {'clean': 20}; chunks {1: 14, 2: 1, 3: 5}; seen in January 5/20.
- Overlap of each ATT+bal seed's own top 20 with the ensemble top 20: [15, 15, 14, 14, 14, 16, 16, 15, 17, 14].

## Item 3: padding the models have never seen

Malware April reports (9,399) are edited, and 2,000 random benign April reports are edited the same way; k = 1, 5, 20, 50; thresholds fixed at 1% and 0.1% FPR on the unedited April benign scores of each model and seed; mean over seeds (released: one model; the retrained models: seeds 0-4); edited reports exist in memory only. Cells: **insert 20 | prepend 20 | prepend 50** (unedited in the second column). Complete tables for every variant (all k, changes with group-bootstrap and seed-paired intervals, 'fits in 512 tokens') are in the `pad_*.md` files.


**Malware TPR (%) at the threshold of 1% FPR** (insert 20 | prepend 20 | prepend 50):

| padding | released Nebula | A (J) | C (J) | C+bal | MM+bal | ATT+bal |
|---|---|---|---|---|---|---|
| 3a block of 20 / 50 consecutive calls of one benign report | 39.7 \| 24.5 \| 29.7 (unedited 75.0) | 33.8 \| 32.6 \| 27.8 (unedited 72.7) | 41.4 \| 44.3 \| 7.8 (unedited 72.3) | 66.7 \| 68.3 \| 48.2 (unedited 77.7) | 66.8 \| 69.6 \| 54.1 (unedited 76.4) | 67.2 \| 72.6 \| 62.9 (unedited 76.7) |
| 3b other benign source (windows_syswow64 only) | 34.8 \| 11.1 \| 13.4 (unedited 75.0) | 31.3 \| 12.6 \| 9.5 (unedited 72.7) | 34.1 \| 38.8 \| 0.2 (unedited 72.3) | 62.4 \| 67.6 \| 40.0 (unedited 77.7) | 63.6 \| 69.0 \| 48.6 (unedited 76.4) | 64.5 \| 72.7 \| 60.0 (unedited 76.7) |
| 3b source clean only | 35.7 \| 10.2 \| 14.1 (unedited 75.0) | 33.2 \| 20.1 \| 16.1 (unedited 72.7) | 36.2 \| 41.2 \| 0.5 (unedited 72.3) | 61.1 \| 65.8 \| 38.2 (unedited 77.7) | 61.2 \| 66.7 \| 42.3 (unedited 76.4) | 64.1 \| 72.4 \| 59.8 (unedited 76.7) |
| 3b rarest 20% of API names of the TRAIN pool | 33.4 \| 18.6 \| 31.8 (unedited 75.0) | 30.6 \| 29.3 \| 24.2 (unedited 72.7) | 20.3 \| 10.6 \| 0.0 (unedited 72.3) | 52.2 \| 58.2 \| 1.6 (unedited 77.7) | 53.3 \| 59.6 \| 3.8 (unedited 76.4) | 58.8 \| 69.5 \| 10.7 (unedited 76.7) |
| 3c top-ranked calls of the LightGBM surrogate | 41.9 \| 18.6 \| 56.0 (unedited 75.0) | 43.3 \| 59.8 \| 64.8 (unedited 72.7) | 18.0 \| 16.2 \| 0.0 (unedited 72.3) | - | - | 59.9 \| 70.7 \| 30.1 (unedited 76.7) |
| 3c top-ranked calls of the C (J) surrogate | 64.8 \| 95.4 \| 99.4 (unedited 75.0) | 50.6 \| 81.0 \| 91.3 (unedited 72.7) | 2.4 \| 31.2 \| 0.0 (unedited 72.3) | - | - | 60.6 \| 72.0 \| 7.0 (unedited 76.7) |

**Malware TPR (%) at the threshold of 0.1% FPR** (insert 20 | prepend 20 | prepend 50):

| padding | released Nebula | A (J) | C (J) | C+bal | MM+bal | ATT+bal |
|---|---|---|---|---|---|---|
| 3a block of 20 / 50 consecutive calls of one benign report | 15.7 \| 5.1 \| 7.1 (unedited 51.8) | 14.7 \| 14.5 \| 10.9 (unedited 44.2) | 2.4 \| 1.0 \| 0.2 (unedited 18.4) | 9.1 \| 7.4 \| 0.4 (unedited 25.4) | 22.1 \| 18.4 \| 2.9 (unedited 41.2) | 40.5 \| 44.1 \| 28.7 (unedited 53.7) |
| 3b other benign source (windows_syswow64 only) | 13.8 \| 2.2 \| 3.2 (unedited 51.8) | 14.5 \| 5.9 \| 4.8 (unedited 44.2) | 1.1 \| 0.1 \| 0.0 (unedited 18.4) | 7.7 \| 6.0 \| 0.0 (unedited 25.4) | 20.5 \| 16.5 \| 0.4 (unedited 41.2) | 39.0 \| 43.7 \| 25.6 (unedited 53.7) |
| 3b source clean only | 14.8 \| 1.9 \| 3.9 (unedited 51.8) | 14.5 \| 8.9 \| 6.2 (unedited 44.2) | 1.2 \| 0.2 \| 0.0 (unedited 18.4) | 7.2 \| 5.9 \| 0.0 (unedited 25.4) | 19.3 \| 14.4 \| 0.1 (unedited 41.2) | 39.1 \| 43.9 \| 26.0 (unedited 53.7) |
| 3b rarest 20% of API names of the TRAIN pool | 11.4 \| 3.2 \| 6.6 (unedited 51.8) | 12.0 \| 9.5 \| 7.1 (unedited 44.2) | 0.3 \| 0.0 \| 0.0 (unedited 18.4) | 5.8 \| 0.4 \| 0.0 (unedited 25.4) | 14.9 \| 2.9 \| 0.0 (unedited 41.2) | 31.0 \| 39.7 \| 5.9 (unedited 53.7) |
| 3c top-ranked calls of the LightGBM surrogate | 10.7 \| 4.1 \| 4.1 (unedited 51.8) | 15.7 \| 19.9 \| 13.5 (unedited 44.2) | 0.1 \| 0.0 \| 0.0 (unedited 18.4) | - | - | 33.6 \| 42.3 \| 8.5 (unedited 53.7) |
| 3c top-ranked calls of the C (J) surrogate | 37.5 \| 88.2 \| 90.9 (unedited 51.8) | 24.8 \| 48.9 \| 82.9 (unedited 44.2) | 0.0 \| 0.0 \| 0.0 (unedited 18.4) | - | - | 38.0 \| 45.5 \| 5.8 (unedited 53.7) |

**FPR (%) of the padded benign reports at the 1% threshold (1% by construction without padding)** (insert 20 | prepend 20 | prepend 50):

| padding | released Nebula | A (J) | C (J) | C+bal | MM+bal | ATT+bal |
|---|---|---|---|---|---|---|
| 3a block of 20 / 50 consecutive calls of one benign report | 6.0 \| 21.9 \| 29.5 (unedited 1.1) | 7.2 \| 22.1 \| 29.5 (unedited 1.0) | 0.8 \| 0.6 \| 0.7 (unedited 1.0) | 2.5 \| 1.8 \| 3.5 (unedited 1.0) | 2.1 \| 1.6 \| 2.5 (unedited 1.0) | 1.4 \| 1.6 \| 2.3 (unedited 1.0) |
| 3b other benign source (windows_syswow64 only) | 3.5 \| 9.4 \| 8.6 (unedited 1.1) | 3.4 \| 0.6 \| 1.5 (unedited 1.0) | 0.2 \| 0.1 \| 0.0 (unedited 1.0) | 0.4 \| 0.6 \| 0.2 (unedited 1.0) | 0.3 \| 0.9 \| 0.4 (unedited 1.0) | 0.5 \| 0.7 \| 0.4 (unedited 1.0) |
| 3b source clean only | 4.9 \| 10.5 \| 9.9 (unedited 1.1) | 5.6 \| 6.9 \| 10.2 (unedited 1.0) | 0.2 \| 0.1 \| 0.0 (unedited 1.0) | 0.4 \| 0.8 \| 0.1 (unedited 1.0) | 0.3 \| 0.7 \| 0.1 (unedited 1.0) | 1.1 \| 1.3 \| 1.3 (unedited 1.0) |
| 3b rarest 20% of API names of the TRAIN pool | 15.0 \| 17.3 \| 28.0 (unedited 1.1) | 11.4 \| 11.9 \| 23.6 (unedited 1.0) | 0.1 \| 0.0 \| 0.0 (unedited 1.0) | 0.2 \| 0.4 \| 0.0 (unedited 1.0) | 0.2 \| 0.3 \| 0.0 (unedited 1.0) | 1.2 \| 1.2 \| 0.5 (unedited 1.0) |
| 3c top-ranked calls of the LightGBM surrogate | 21.1 \| 7.2 \| 94.0 (unedited 1.1) | 24.2 \| 24.6 \| 95.9 (unedited 1.0) | 0.1 \| 0.0 \| 0.0 (unedited 1.0) | - | - | 0.2 \| 0.7 \| 0.1 (unedited 1.0) |
| 3c top-ranked calls of the C (J) surrogate | 42.6 \| 99.0 \| 98.9 (unedited 1.1) | 31.1 \| 91.5 \| 98.2 (unedited 1.0) | 0.0 \| 0.1 \| 0.0 (unedited 1.0) | - | - | 0.3 \| 0.7 \| 0.0 (unedited 1.0) |

### 3d. Chosen to look benign: white-box greedy padding

500 random April malware reports; each model (one seed, attacked with its own scores) greedily prepends up to 20 EVAL-pool calls, each step the best of 200 random candidates; a report stops being attacked below the 1% threshold and then counts as evaded at both thresholds. TPR of the 500 reports after k prepended calls, threshold of 1% FPR:

| model | k=0 | k=1 | k=2 | k=3 | k=5 | k=10 | k=15 | k=20 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal (seed 0) | 78.2% | 65.0% | 64.4% | 64.2% | 63.2% | 61.4% | 60.2% | 54.0% |
| C+bal (seed 0) | 79.8% | 70.0% | 63.6% | 63.0% | 61.6% | 58.4% | 53.8% | 35.0% |
| released Nebula | 73.0% | 38.2% | 21.0% | 14.2% | 7.4% | 3.4% | 1.6% | 1.6% |


Only the reports whose edited sequence fits in 512 tokens at k (1%)

| model | k=0 | k=1 | k=2 | k=3 | k=5 | k=10 | k=15 | k=20 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal (seed 0) | 69.3% (n=140) | 46.4% (n=140) | 44.3% (n=140) | 43.6% (n=140) | 41.0% (n=139) | 26.1% (n=111) | 13.7% (n=95) | 9.9% (n=91) |
| C+bal (seed 0) | 75.7% (n=140) | 62.1% (n=140) | 44.3% (n=140) | 42.1% (n=140) | 40.0% (n=140) | 19.8% (n=111) | 6.2% (n=97) | 5.2% (n=96) |
| released Nebula | 53.6% (n=140) | 30.7% (n=140) | 5.0% (n=140) | 0.7% (n=140) | 0.0% (n=139) | 0.0% (n=139) | 0.0% (n=139) | 0.0% (n=139) |

Threshold of 0.1% FPR:

| model | k=0 | k=1 | k=2 | k=3 | k=5 | k=10 | k=15 | k=20 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal (seed 0) | 54.8% | 50.6% | 48.2% | 48.4% | 48.8% | 40.2% | 37.4% | 31.8% |
| C+bal (seed 0) | 42.0% | 14.2% | 11.0% | 12.4% | 11.4% | 8.0% | 1.2% | 0.0% |
| released Nebula | 51.2% | 8.2% | 2.4% | 1.0% | 0.8% | 0.6% | 0.6% | 0.6% |


Only the reports whose edited sequence fits in 512 tokens at k (0.1%)

| model | k=0 | k=1 | k=2 | k=3 | k=5 | k=10 | k=15 | k=20 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal (seed 0) | 40.7% (n=140) | 38.6% (n=140) | 34.3% (n=140) | 36.4% (n=140) | 37.4% (n=139) | 16.2% (n=111) | 5.3% (n=95) | 6.6% (n=91) |
| C+bal (seed 0) | 57.9% (n=140) | 12.1% (n=140) | 13.6% (n=140) | 15.7% (n=140) | 12.1% (n=140) | 5.4% (n=111) | 0.0% (n=97) | 0.0% (n=96) |
| released Nebula | 37.9% (n=140) | 2.1% (n=140) | 0.0% (n=140) | 0.0% (n=140) | 0.0% (n=139) | 0.0% (n=139) | 0.0% (n=139) | 0.0% (n=139) |

## Item 4: rotation check

Every April report (17,402) is rotated in memory. (a) *window*: the real tokens of the model's window (first 512; 4,096 for F and G3) are rotated at a call boundary by 25 / 50 / 75%, so the last calls come first (a position test: same tokens, different order). (b) *whole*: the full call list is rotated by the fraction, re-tokenised, and the first 512 (4,096) tokens taken (a 'where is the signal' test: the window sees different calls). Thresholds fixed at 1% / 0.1% FPR on the unedited April benign scores; seeds: released 1, A (J) and C (J) 5, F 3, ATT+bal 10, G3 5. Malware TPR at the threshold of 1% FPR:

| model | unedited | window 25% | window 50% | window 75% | whole 25% | whole 50% | whole 75% |
|---|---|---|---|---|---|---|---|
| released Nebula | 75.0% | 29.2% | 37.0% | 24.0% | 43.4% | 38.4% | 43.7% |
| A (J) | 72.7% | 28.9% | 23.0% | 26.5% | 37.3% | 25.8% | 29.4% |
| C (J) | 72.3% | 73.5% | 72.9% | 72.3% | 54.0% | 46.4% | 50.6% |
| F (whole report) | 74.3% | 74.9% | 72.1% | 75.9% | 70.7% | 74.8% | 72.9% |
| ATT+bal | 76.5% | 76.4% | 76.2% | 76.9% | 69.2% | 65.2% | 76.5% |
| ATT+bal whole report (G3) | 76.1% | 76.6% | 75.7% | 76.6% | 76.7% | 75.9% | 76.4% |


Change in points [group 95%], all

| model | window 25% | window 50% | window 75% | whole 25% | whole 50% | whole 75% |
|---|---|---|---|---|---|---|
| released Nebula | -45.8 [-62.0, -27.7] | -38.0 [-51.9, -22.2] | -50.9 [-63.9, -35.2] | -31.5 [-48.2, -14.5] | -36.5 [-53.9, -18.1] | -31.3 [-46.8, -17.0] |
| A (J) | -43.8 [-54.6, -30.3] | -49.7 [-63.9, -33.7] | -46.2 [-58.9, -32.7] | -35.4 [-50.1, -18.3] | -46.9 [-60.7, -28.6] | -43.3 [-57.4, -26.9] |
| C (J) | +1.2 [+0.2, +2.3] | +0.6 [-0.6, +2.0] | -0.0 [-2.6, +2.2] | -18.4 [-34.5, -6.7] | -25.9 [-37.9, -13.1] | -21.8 [-32.3, -10.8] |
| F (whole report) | +0.6 [-1.4, +3.5] | -2.2 [-6.8, +1.2] | +1.5 [-0.4, +4.4] | -3.6 [-9.4, +2.0] | +0.5 [-2.2, +3.5] | -1.4 [-4.4, +0.9] |
| ATT+bal | -0.1 [-0.6, +0.4] | -0.3 [-1.9, +0.7] | +0.3 [-0.2, +0.9] | -7.3 [-13.5, -2.7] | -11.3 [-24.1, -0.7] | -0.0 [-5.2, +5.7] |
| ATT+bal whole report (G3) | +0.5 [-1.1, +2.0] | -0.5 [-2.3, +1.1] | +0.4 [-1.5, +2.1] | +0.5 [-1.2, +2.1] | -0.2 [-2.0, +1.1] | +0.2 [-1.5, +2.0] |

Change in points [group 95%]:

| model | window 25% | window 50% | window 75% | whole 25% | whole 50% | whole 75% |
|---|---|---|---|---|---|---|
| released Nebula | -45.8 [-62.0, -27.7] | -38.0 [-51.9, -22.2] | -50.9 [-63.9, -35.2] | -31.5 [-48.2, -14.5] | -36.5 [-53.9, -18.1] | -31.3 [-46.8, -17.0] |
| A (J) | -43.8 [-54.6, -30.3] | -49.7 [-63.9, -33.7] | -46.2 [-58.9, -32.7] | -35.4 [-50.1, -18.3] | -46.9 [-60.7, -28.6] | -43.3 [-57.4, -26.9] |
| C (J) | +1.2 [+0.2, +2.3] | +0.6 [-0.6, +2.0] | -0.0 [-2.6, +2.2] | -18.4 [-34.5, -6.7] | -25.9 [-37.9, -13.1] | -21.8 [-32.3, -10.8] |
| F (whole report) | +0.6 [-1.4, +3.5] | -2.2 [-6.8, +1.2] | +1.5 [-0.4, +4.4] | -3.6 [-9.4, +2.0] | +0.5 [-2.2, +3.5] | -1.4 [-4.4, +0.9] |
| ATT+bal | -0.1 [-0.6, +0.4] | -0.3 [-1.9, +0.7] | +0.3 [-0.2, +0.9] | -7.3 [-13.5, -2.7] | -11.3 [-24.1, -0.7] | -0.0 [-5.2, +5.7] |
| ATT+bal whole report (G3) | +0.5 [-1.1, +2.0] | -0.5 [-2.3, +1.1] | +0.4 [-1.5, +2.1] | +0.5 [-1.2, +2.1] | -0.2 [-2.0, +1.1] | +0.2 [-1.5, +2.0] |

On the 6,359 reports that fit in 512 tokens (rotation only reorders; TPR at 1% FPR):

| model | unedited | window 25% | window 50% | window 75% | whole 25% | whole 50% | whole 75% |
|---|---|---|---|---|---|---|---|
| released Nebula | 61.5% | 60.2% | 45.8% | 51.3% | 59.3% | 60.9% | 53.3% |
| A (J) | 64.4% | 42.6% | 55.6% | 47.8% | 42.6% | 41.5% | 46.4% |
| C (J) | 69.9% | 72.6% | 72.1% | 70.0% | 61.1% | 62.2% | 60.0% |
| F (whole report) | 71.9% | 72.6% | 73.1% | 74.5% | 68.0% | 70.5% | 68.1% |
| ATT+bal | 74.0% | 74.2% | 74.7% | 75.2% | 74.5% | 74.0% | 74.1% |
| ATT+bal whole report (G3) | 68.2% | 71.6% | 69.5% | 71.6% | 72.1% | 70.3% | 71.3% |


Change in points [group 95%], fits in 512 tokens

| model | window 25% | window 50% | window 75% | whole 25% | whole 50% | whole 75% |
|---|---|---|---|---|---|---|
| released Nebula | -1.3 [-18.8, +10.9] | -15.7 [-32.6, +1.4] | -10.2 [-23.3, +3.2] | -2.1 [-18.3, +6.8] | -0.5 [-20.4, +14.0] | -8.2 [-21.9, +9.4] |
| A (J) | -21.8 [-39.8, -1.7] | -8.8 [-18.6, -3.0] | -16.7 [-30.2, +0.2] | -21.9 [-39.9, -1.9] | -22.9 [-40.8, -4.8] | -18.0 [-31.2, -2.9] |
| C (J) | +2.7 [-0.2, +5.4] | +2.2 [-1.6, +6.1] | +0.1 [-7.5, +7.3] | -8.8 [-15.6, +2.2] | -7.7 [-12.2, -0.1] | -9.9 [-21.3, -0.3] |
| F (whole report) | +0.7 [-2.7, +5.0] | +1.2 [-3.8, +6.2] | +2.6 [-0.9, +7.7] | -3.9 [-10.3, +4.5] | -1.4 [-6.4, +4.5] | -3.8 [-10.3, +4.4] |
| ATT+bal | +0.2 [-1.2, +1.7] | +0.6 [-0.7, +2.6] | +1.1 [-0.4, +3.4] | +0.5 [-0.7, +1.8] | +0.0 [-1.2, +1.3] | +0.1 [-1.3, +1.8] |
| ATT+bal whole report (G3) | +3.3 [+0.1, +7.6] | +1.2 [-1.9, +6.1] | +3.4 [-0.8, +7.8] | +3.9 [+0.4, +8.1] | +2.1 [-0.8, +4.5] | +3.0 [-1.2, +8.1] |

AUC (all reports; benign reports rotated too):

| model | unedited | window 25% | window 50% | window 75% | whole 25% | whole 50% | whole 75% |
|---|---|---|---|---|---|---|---|
| released Nebula | 0.9586 | 0.4731 | 0.4811 | 0.5018 | 0.6884 | 0.5842 | 0.6366 |
| A (J) | 0.9557 | 0.5422 | 0.4331 | 0.5922 | 0.6383 | 0.5029 | 0.6341 |
| C (J) | 0.9628 | 0.9603 | 0.9623 | 0.9647 | 0.9431 | 0.9492 | 0.9550 |
| F (whole report) | 0.9630 | 0.9587 | 0.9602 | 0.9630 | 0.9585 | 0.9589 | 0.9609 |
| ATT+bal | 0.9752 | 0.9733 | 0.9741 | 0.9736 | 0.8613 | 0.8663 | 0.9406 |
| ATT+bal whole report (G3) | 0.9578 | 0.9486 | 0.9520 | 0.9518 | 0.9515 | 0.9489 | 0.9498 |

Thresholds of 0.1% FPR, longer-report subset and seed-paired differences are in `rotation.md`.


## Item 5: the round-4 padding and copied-call tables for the 10-seed models

Same models and seeds as item 1 (released 1 model; A (J), C (J), C (J, 2 epochs), ATT+bal, MM+bal, C+bal 10 seeds each). Thresholds fixed at 1% (and 0.1%, in the .md files) FPR on the unedited April benign scores.

### Copied calls: insert k / prepend k calls copied from the same report (the edits of `results/robustness` item 1)

Malware TPR at the 1% threshold after the edit (all April malware):

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 75.0% | 73.6% | 69.3% | 57.5% | 49.2% | 69.6% | 53.7% | 35.7% | 38.0% |
| A (J) | 71.9% | 70.6% | 65.4% | 49.1% | 38.2% | 66.3% | 43.4% | 28.2% | 21.2% |
| C (J) | 73.8% | 72.8% | 71.4% | 70.5% | 72.1% | 71.1% | 69.8% | 71.3% | 68.4% |
| C (J, 2 epochs) | 73.6% | 72.4% | 71.2% | 70.2% | 71.5% | 70.3% | 69.8% | 70.6% | 68.4% |
| ATT+bal | 76.5% | 76.2% | 76.6% | 77.3% | 76.5% | 76.2% | 77.6% | 75.7% | 76.0% |
| MM+bal | 76.3% | 76.1% | 76.4% | 76.6% | 77.2% | 76.1% | 77.5% | 76.9% | 77.7% |
| C+bal | 77.5% | 77.2% | 77.2% | 76.7% | 77.2% | 76.8% | 76.8% | 76.7% | 76.9% |


Benign FPR after the same edit of the benign reports (all April benign)

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 1.00% | 1.09% | 1.04% | 1.72% | 2.87% | 1.09% | 2.06% | 20.89% | 19.41% |
| A (J) | 1.00% | 1.07% | 1.14% | 1.57% | 2.07% | 1.17% | 1.56% | 8.54% | 8.51% |
| C (J) | 1.00% | 0.98% | 0.99% | 1.06% | 1.10% | 0.93% | 1.89% | 1.16% | 1.05% |
| C (J, 2 epochs) | 1.00% | 0.96% | 1.01% | 1.02% | 1.04% | 0.97% | 1.56% | 1.11% | 1.07% |
| ATT+bal | 0.99% | 0.97% | 1.02% | 1.06% | 1.17% | 0.97% | 1.09% | 1.20% | 1.33% |
| MM+bal | 1.00% | 1.05% | 1.05% | 1.14% | 1.37% | 1.06% | 1.17% | 1.32% | 1.69% |
| C+bal | 0.98% | 0.97% | 1.02% | 1.08% | 1.25% | 0.99% | 1.13% | 1.29% | 1.56% |


Change in malware TPR, points [group 95%], all reports

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| released Nebula | -1.4 [-2.8, -0.3] | -5.7 [-10.4, -1.5] | -17.5 [-32.0, -5.5] | -25.7 [-40.5, -12.6] | -5.4 [-8.9, -1.9] | -21.3 [-35.8, -7.0] | -39.3 [-51.3, -26.1] | -36.9 [-47.8, -25.5] |
| A (J) | -1.3 [-2.1, -0.6] | -6.5 [-10.0, -3.0] | -22.8 [-32.6, -12.3] | -33.7 [-45.5, -20.5] | -5.6 [-9.0, -2.4] | -28.5 [-38.3, -16.3] | -43.7 [-54.8, -30.7] | -50.7 [-61.9, -35.8] |
| C (J) | -1.0 [-1.5, -0.5] | -2.4 [-3.7, -1.1] | -3.3 [-5.4, -1.2] | -1.6 [-4.0, +0.3] | -2.7 [-3.8, -1.5] | -4.0 [-7.0, -1.3] | -2.4 [-5.0, -0.3] | -5.3 [-8.5, -2.4] |
| C (J, 2 epochs) | -1.2 [-1.9, -0.6] | -2.4 [-3.8, -1.1] | -3.4 [-5.5, -1.5] | -2.1 [-4.1, -0.5] | -3.3 [-4.9, -1.7] | -3.8 [-6.3, -1.3] | -3.0 [-5.4, -1.2] | -5.2 [-7.9, -2.8] |
| ATT+bal | -0.3 [-0.8, +0.1] | +0.1 [-0.8, +1.2] | +0.8 [-1.8, +4.8] | +0.0 [-2.1, +2.5] | -0.3 [-1.0, +0.4] | +1.1 [-1.8, +6.0] | -0.8 [-3.2, +1.3] | -0.5 [-3.2, +2.9] |
| MM+bal | -0.1 [-0.9, +0.4] | +0.1 [-0.5, +0.8] | +0.4 [-1.7, +3.0] | +0.9 [-1.4, +3.8] | -0.2 [-1.6, +0.7] | +1.2 [-0.1, +3.3] | +0.6 [-1.8, +3.3] | +1.4 [-1.4, +5.8] |
| C+bal | -0.4 [-0.9, -0.0] | -0.3 [-1.8, +1.0] | -0.8 [-3.5, +1.3] | -0.4 [-3.4, +2.3] | -0.7 [-2.1, +0.1] | -0.7 [-2.1, +0.5] | -0.8 [-4.2, +2.0] | -0.6 [-4.1, +2.9] |


Reports that fit in 512 tokens after the edit: TPR before → after; change in points [group 95%]

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| released Nebula | 61.5% → 59.7%; -1.8 [-5.0, +1.7] | 61.2% → 55.8%; -5.4 [-15.0, +5.4] | 63.1% → 64.4%; +1.2 [-7.3, +9.6] | 62.5% → 66.8%; +4.2 [-2.1, +13.4] | 61.5% → 56.5%; -5.0 [-12.0, +2.8] | 61.1% → 52.4%; -8.7 [-23.8, +6.9] | 63.0% → 56.3%; -6.8 [-20.2, +4.0] | 62.8% → 65.1%; +2.4 [-4.4, +10.7] |
| A (J) | 65.9% → 64.3%; -1.6 [-2.4, -0.5] | 65.9% → 58.5%; -7.4 [-13.1, -1.7] | 69.5% → 58.1%; -11.3 [-17.6, -3.8] | 74.2% → 61.1%; -13.0 [-24.8, -3.4] | 65.9% → 61.2%; -4.7 [-6.5, -1.7] | 65.8% → 51.3%; -14.6 [-28.0, -2.3] | 69.4% → 56.6%; -12.8 [-19.5, -5.7] | 74.1% → 57.2%; -16.9 [-28.9, -7.1] |
| C (J) | 71.0% → 69.5%; -1.5 [-2.6, -0.4] | 71.1% → 69.5%; -1.6 [-2.8, -0.3] | 72.4% → 71.4%; -1.0 [-3.3, +1.7] | 73.4% → 73.0%; -0.4 [-2.0, +1.1] | 71.0% → 67.9%; -3.1 [-4.8, -1.1] | 71.0% → 68.0%; -3.1 [-4.6, -1.5] | 72.2% → 70.4%; -1.8 [-4.0, +0.6] | 73.5% → 73.2%; -0.3 [-1.9, +1.0] |
| C (J, 2 epochs) | 70.2% → 67.8%; -2.4 [-4.1, -1.1] | 70.4% → 68.4%; -2.0 [-4.3, -0.2] | 72.2% → 70.7%; -1.5 [-4.5, +1.9] | 73.5% → 72.9%; -0.6 [-1.9, +1.0] | 70.2% → 65.5%; -4.7 [-7.5, -2.0] | 70.4% → 67.0%; -3.4 [-6.1, -1.1] | 72.0% → 69.6%; -2.4 [-5.2, +0.7] | 73.6% → 73.2%; -0.4 [-2.0, +1.3] |
| ATT+bal | 74.1% → 72.9%; -1.2 [-3.1, -0.1] | 73.9% → 74.0%; +0.2 [-1.0, +1.3] | 69.3% → 71.2%; +1.9 [+0.6, +3.8] | 69.7% → 73.1%; +3.4 [+1.3, +7.3] | 74.0% → 73.5%; -0.5 [-2.1, +0.6] | 73.8% → 74.0%; +0.2 [-1.3, +1.6] | 69.5% → 71.6%; +2.0 [+0.5, +4.3] | 69.9% → 72.7%; +2.9 [+1.1, +6.0] |
| MM+bal | 77.1% → 77.6%; +0.6 [-0.1, +1.3] | 76.9% → 77.9%; +0.9 [-0.2, +2.2] | 74.2% → 76.1%; +2.0 [+0.4, +4.0] | 75.2% → 78.1%; +2.9 [+1.0, +6.1] | 77.0% → 78.0%; +1.0 [+0.2, +2.0] | 76.8% → 78.0%; +1.1 [+0.1, +2.2] | 74.3% → 76.5%; +2.2 [+0.5, +4.5] | 75.3% → 77.6%; +2.3 [+0.6, +4.9] |
| C+bal | 76.0% → 75.8%; -0.2 [-1.3, +0.4] | 75.9% → 76.1%; +0.3 [-1.0, +1.3] | 73.3% → 74.3%; +1.0 [-0.4, +2.6] | 73.9% → 76.3%; +2.4 [+1.0, +5.0] | 76.0% → 76.1%; +0.1 [-0.8, +1.1] | 75.8% → 75.8%; +0.0 [-1.3, +1.0] | 73.4% → 74.3%; +0.9 [-0.3, +2.5] | 74.0% → 75.8%; +1.7 [+0.6, +3.9] |

Benign FPR at the 1% threshold after the same edit of the benign reports:

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 1.00% | 1.09% | 1.04% | 1.72% | 2.87% | 1.09% | 2.06% | 20.89% | 19.41% |
| A (J) | 1.00% | 1.07% | 1.14% | 1.57% | 2.07% | 1.17% | 1.56% | 8.54% | 8.51% |
| C (J) | 1.00% | 0.98% | 0.99% | 1.06% | 1.10% | 0.93% | 1.89% | 1.16% | 1.05% |
| C (J, 2 epochs) | 1.00% | 0.96% | 1.01% | 1.02% | 1.04% | 0.97% | 1.56% | 1.11% | 1.07% |
| ATT+bal | 0.99% | 0.97% | 1.02% | 1.06% | 1.17% | 0.97% | 1.09% | 1.20% | 1.33% |
| MM+bal | 1.00% | 1.05% | 1.05% | 1.14% | 1.37% | 1.06% | 1.17% | 1.32% | 1.69% |
| C+bal | 0.98% | 0.97% | 1.02% | 1.08% | 1.25% | 0.99% | 1.13% | 1.29% | 1.56% |

### Random benign-call padding (the round-4 test; random single calls of the EVAL pool)

Malware TPR (%) at the thresholds of 1% / 0.1% FPR after the edit, and FPR (%) of the 2,000 padded benign reports (1% threshold); cells: insert 20 | prepend 20 | prepend 50 (unedited in brackets):

| model | TPR at 1% FPR | TPR at 0.1% FPR | padded benign FPR at 1% |
|---|---|---|---|
| released Nebula | 35.5 \| 10.3 \| 14.0 (75.0) | 14.5 \| 1.9 \| 3.8 (51.8) | 3.6 \| 10.2 \| 9.6 (1.1) |
| A (J) | 29.2 \| 17.1 \| 13.2 (71.9) | 11.8 \| 6.8 \| 5.1 (39.6) | 4.1 \| 5.4 \| 8.2 (1.1) |
| C (J) | 39.1 \| 45.1 \| 1.0 (73.8) | 1.8 \| 0.5 \| 0.0 (20.4) | 0.2 \| 0.3 \| 0.0 (1.0) |
| C (J, 2 epochs) | 39.1 \| 44.4 \| 1.1 (73.6) | 1.2 \| 0.2 \| 0.0 (15.2) | 0.2 \| 0.3 \| 0.0 (1.0) |
| ATT+bal | 63.8 \| 72.5 \| 59.2 (76.5) | 41.8 \| 47.7 \| 29.6 (57.0) | 0.7 \| 1.1 \| 1.0 (1.0) |
| MM+bal | 61.0 \| 66.0 \| 40.3 (76.3) | 18.1 \| 14.5 \| 0.7 (38.0) | 0.2 \| 0.6 \| 0.2 (1.0) |
| C+bal | 61.5 \| 66.8 \| 39.6 (77.5) | 8.9 \| 7.4 \| 0.0 (27.3) | 0.3 \| 0.9 \| 0.2 (1.0) |

All k, 'fits in 512 tokens' subsets, changes with intervals and the seed-paired differences: `pad_random.md`, `graded_edits.md`.


## G3: ATT+bal over the whole report

ATT pooling over up to 4,096 tokens (3,304,321 parameters), balanced padding of the full report (the same edits as G1, re-tokenised without the 512-token cut), regime J, seeds 0-4, 2 epochs.
April accuracy with intervals and the seed-paired differences are in `g3_accuracy.md`:

# G3: ATT+bal over the whole report (round 5)

| all | ATT+bal whole report (G3) | 5 | 17,402 (9,399) | 0.9578 [0.9350, 0.9738] | 76.1% [66.4%, 84.2%] | 55.0% [38.9%, 65.7%] |
| all | ATT+bal 512 tokens (seeds 0-4) | 5 | 17,402 (9,399) | 0.9757 [0.9592, 0.9855] | 76.7% [64.7%, 84.2%] | 53.7% [33.0%, 67.3%] |
| all | ATT+bal 512 tokens (seeds 0-9) | 10 | 17,402 (9,399) | 0.9752 [0.9589, 0.9847] | 76.5% [64.9%, 84.2%] | 57.0% [36.8%, 68.3%] |
| all | F (C whole report) | 5 | 17,402 (9,399) | 0.9635 [0.9405, 0.9785] | 74.5% [60.9%, 83.4%] | 12.7% [6.2%, 37.2%] |
| all | C 512 tokens (J) | 5 | 17,402 (9,399) | 0.9628 [0.9395, 0.9781] | 72.3% [57.2%, 81.8%] | 18.4% [7.4%, 42.0%] |
| all | released Nebula | 1 | 17,402 (9,399) | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 51.7% [0.0%, 67.0%] |
| all | ATT+bal whole report (G3), ensemble of 5 | 1 | 17,402 (9,399) | 0.9618 [0.9377, 0.9783] | 76.1% [66.9%, 84.8%] | 61.0% [40.4%, 71.1%] |
| all | ATT+bal 512 tokens, ensemble of 5 | 1 | 17,402 (9,399) | 0.9782 [0.9622, 0.9874] | 75.5% [63.5%, 84.8%] | 59.3% [33.9%, 72.1%] |

Rotation of G3 is in the table of item 4; random benign-call padding (threshold 1% FPR, cells insert 20 | prepend 20 | prepend 50; benign FPR in the second row):

| model | TPR at 1% FPR | TPR at 0.1% FPR | padded benign FPR at 1% |
|---|---|---|---|
| ATT+bal whole report (G3) | 64.2 \| 73.9 \| 71.3 (76.1) | 35.7 \| 49.0 \| 44.7 (55.0) | 0.7 \| 1.2 \| 0.9 (1.1) |

## Caveats

- Item 3 uses seeds 0-4 of every retrained model (ATT+bal, MM+bal, C+bal, A, C) and one released model; items 1, 2 and 5 use seeds 0-9 (F: seeds 0-4; rotation: ATT+bal 10 seeds, A and C 5, F 3; G3: 5 seeds). The unedited columns of the 5-seed tables therefore differ slightly from the 10-seed ones.
- The edits are random or chosen with the information described in each section; the white-box attack (3d) uses one trained seed per model, 500 reports and candidates from a fixed random subset of 30,000 of the 361,002 EVAL-pool calls; the surrogate rankings use January malware (not April).
- The EVAL pool has only 4 reports of source windows_syswow64 (370 calls); the rare-name pool has 763 calls (603 of 3,011 API names). Padding with long calls fills the 512-token window quickly (prepend 50), which for window-limited models is a separate effect from the content of the padding: see the "fits in 512 tokens" tables in the `pad_*.md` files.
- Item 2: the 0.1% FPR threshold of April is set by the 9th highest benign score (8 of 8,003 benign reports may lie above it), that of the January validation side by 2 of 2,103; the released Nebula's accuracy-table intervals at 0.1% (0.0%-67.0%) come from the stored probabilities, which saturate and tie; `lowfpr_april.md` uses its CPU logits (4 / 8 / 12 benign reports allowed above the threshold).
- The balanced padding of training uses the same kind of padding as the main test (random single calls of benign reports, pools disjoint by API-sequence group); the resistance shown for other padding (block, other source, rare names, optimised) is therefore a transfer result.
- Regime S models use 2 epochs without early stopping on the validation side (the validation side is a test set here). G2's ATT+bal, MM+bal and C+bal were trained with the augmentation files of regime J with the validation-side rows removed.
- Nothing here is committed.

## Files

`accuracy.md/json`, `accuracy_epoch4.md/json`, `lowfpr_april.md/json` (+ `_epoch4`), `janval.md/json`, `top_benign.md/json`, `pad_block.md`, `pad_syswow.md`, `pad_clean.md`, `pad_rare.md`, `pad_sur_lgb.md`, `pad_sur_c.md`, `attack_whitebox.md`, `rotation.md`, `graded_edits.md`, `pad_random.md`, `pad_random_g3.md`, `g3_accuracy.md`, `pools5.json`, `surrogate_lgb.json`, `surrogate_c.json` (+ `.json` of every table);
code in `scripts/round5/` (`r5_common.py`, `r5_accuracy.py`, `r5_janval.py`, `r5_topbenign.py`, `r5_pad.py`, `r5_attack.py`, `r5_compose.py`, `r5_rotation.py`, `r5_graded.py`, `r5_g3.py`, `prep_pools5.py`, `surrogate_rank.py`, `build_readme.py`, `run_cpu_chains.sh`), `scripts/pooling_v4/make_aug.py --balanced` and `make_aug_full.py`, `scripts/kaggle/train_pooling_v4.py`, `train_fulltrace_v5.py`, `kernel_r5_*`.

