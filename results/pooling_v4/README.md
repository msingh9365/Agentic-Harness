# Round 4: pooling that resists dilution

Builds on `results/pooling_v2`, `results/robustness`, `results/fulltrace`. Models are C (fixed position encoding, first 512 tokens, regime J = all of January) with only the pooling changed: **M** masked max, **MM** masked mean + max concatenated, **ATT** attention pooling (one learned query, masked softmax over the real tokens), and **C+aug**, **ATT+aug** (C and ATT trained with benign-call padding of malware training reports). 5 seeds (0–4), 2 epochs. References on the same seeds: **C (J)** (10 epochs), **A (J)**, released Nebula; plus a control the plan did not list, **C (J, 2 epochs)** = the 10-epoch C runs after their epoch 2 (same data order and learning-rate schedule as a 2-epoch run), so that "2 epochs" is not confused with the pooling. April: 17,402 reports (9,399 malware); thresholds (a) from the April benign scores; group-bootstrap intervals over `hash_apis` (1,000 resamples); seed-paired intervals bootstrap over the 5 seeds. All padding numbers use the EVAL pool.

## Verdict

*(Points 1–5 are the first part of round 4. The follow-up with balanced padding, "Round 4b", follows after them and changes points 2, 3 and 5.)*

1. **Accuracy: only MM keeps (and slightly improves) C's accuracy; M and ATT lose it without augmentation.** AUC: MM 0.9695 (MM − C 2 epochs +0.0093 [+0.0027, +0.0201]), C (J, 2 epochs) 0.9602, M 0.9578, ATT 0.9532 (−0.0070 [−0.0158, −0.0015]); TPR at 1% FPR: MM 72.6%, C 72.2%, M 63.0% (−9.2 [−21.8, +1.8]), ATT 63.6% (−8.6 [−13.5, −1.9]). The augmented models have TPR 77.6% (C+aug, +5.4 [+1.1, +21.3]) and 76.2% (ATT+aug, +4.0 [−1.2, +21.3]) at unchanged AUC.
2. **No pooling resists benign padding in a useful way.** Without augmentation M, MM and ATT are diluted like C (prepend 20: 18.8%, 40.0%, 25.5% against 41.6% for C; prepend 50 fills the 512-token window for all of them: 0.8–5.9%). With augmentation the malware TPR even *rises* (prepend 20: C+aug 80.3%, ATT+aug 82.1%), but the models learned "benign-looking padding means malware": benign April reports padded the same way are flagged at 18.7% (C+aug) and 33.6% (ATT+aug) at prepend 20 and 48.6% and 66.2% at prepend 50, against 0.2% for C (copied same-report calls: 11.6% and 35.9% at prepend 20). The augmentation as specified (malware only) buys a shortcut, not resistance.
3. **At 0.1% FPR ATT+aug is best: 53.7% [34.0, 66.0]** (C 2 epochs 15.0%, A 44.2%, released 51.7%; ATT+aug − C (2 epochs) +38.7 [+15.9, +53.0]); C+aug 34.4%; M, MM, ATT 14–20%, no better than C. Given point 2 it is unclear how much of this gain is the padding shortcut rather than a better benign boundary; it was not tested separately.
4. **M and ATT do not change the low-FPR weakness.** Their highest-scoring benign reports are again short generic sequences (M: 20/20 one chunk, median 10 calls, 14/20 share their API sequence with a malware report; ATT: 16/20 one chunk, median 22 calls, 7/20 share); 10 (M) and 16 (ATT) of 20 are also in the list of C (10 epochs). The ATT pooling is almost flat: the 10 largest weights per report are at most 0.04 (uniform would be 0.002), prepended benign calls get 22–44% of the attention (mean pooling: 30%), and 1–14 of the 20 malware reports are still flagged after prepending 20 calls (11–19 before). ATT+aug puts 21–27% on the prepended tokens, less than uniform, and flags 17–18 of 20.
5. **Which one moves to the whole report?** If one has to be chosen now, MM: it is the only variant that keeps accuracy without a shortcut and keeps C's robustness to same-report copies (worst change over the eight edits −2.9 points, step 3b). But `results/fulltrace` already showed that reading the whole report does not improve accuracy, and the whole-report model F resisted padding only because long reports are not pushed out of the window (below, step 0). The augmented models should not be moved until the augmentation also pads benign reports (padding then carries no label information); that run was not made.

## Round 4b: balanced padding (benign reports padded too)

The follow-up to point 2 and 5 of the verdict above. The first augmentation padded only malware training reports, so "benign-looking padding" became a malware cue. Here **every** January training report (malware and benign alike) is edited with probability 0.5 (insert or prepend, k ~ U(1..50) random calls of TRAIN-pool benign reports, first 512 tokens), so padding carries no label (`make_aug.py --balanced`, files `augb_*`; about 37,700 of 75,298 reports per epoch, 25,300–25,500 malware and 12,350–12,400 benign). Models **C+bal**, **MM+bal**, **ATT+bal**: C, MM and ATT trained this way, regime J, seeds 0–4, 2 epochs, otherwise as in step 2 (Kaggle, 15 runs, about 20 min). Evaluation is the one of steps 3a, 3c and 3e; the tables of those steps (`accuracy.md`, `step3_padding.md`, `attention_tokens.md`, `graded_edits.md`) now include the new rows.

### Verdict of round 4b

1. **The shortcut is gone and padding no longer costs much.** Benign April reports padded like the malware ones are flagged at 0.2–1.3% (C+bal 0.86% / 0.18%, MM+bal 0.74% / 0.34%, ATT+bal 1.25% / 1.10% at prepend 20 / 50), against 18.7% / 48.6% for C+aug and 33.6% / 66.2% for ATT+aug; unedited FPR is 1% by construction.
2. **Accuracy is at least as good as before.** AUC 0.9745 (C+bal), 0.9757 (MM+bal), 0.9757 (ATT+bal) against 0.9602 for C (2 epochs) and 0.9577–0.9635 for the unbalanced augmentation; TPR at 1% FPR 76.4–77.7% against 72.2%. Seed-paired differences with C (2 epochs): AUC +0.0142 [+0.0023, +0.0320], +0.0155 [+0.0044, +0.0338], +0.0154 [+0.0044, +0.0320].
3. **ATT+bal resists benign padding best; C+bal and MM+bal only partly.** Malware TPR after prepending 20 / 50 calls: ATT+bal 72.4% / 59.5% (change −4.3 [−7.5, −2.0] / −17.2 [−23.9, −11.6]), MM+bal 66.5% / 41.9% (−9.9 / −34.5), C+bal 65.6% / 38.0% (−12.1 / −39.7), against C (2 epochs) 41.6% / 0.8%, released 10.3% / 14.0%, whole-report F 55.6% / 44.2%. On reports where no original call leaves the 512 window, prepend 20: ATT+bal 73.2% → 65.0%, C+bal 76.3% → 46.7%, C (2 epochs) 70.2% → 18.4%. ATT+bal puts only 11–12% of its attention on 20 prepended benign calls (uniform / mean pooling: 30.3%; ATT+aug 21–27%), so it has learned to look past padding.
4. **At 0.1% FPR ATT+bal reaches 53.7% [33.0, 67.3], the same as ATT+aug, so that gain was not the shortcut.** MM+bal 41.2% [22.4, 57.8], C+bal 25.4% [7.4, 50.9]; C (2 epochs) 15.0%, A 44.2%, released 51.7%. ATT+bal − C (2 epochs): +38.7 [+16.2, +53.2] at 0.1% FPR; ATT+bal is within noise of released and A (intervals of the single numbers span 20–30 points). With the LightGBM rank average: ATT+bal 57.8% [33.7, 69.7], TPR at 1% FPR 84.3%.
5. **Recommendation: ATT+bal is the pooling to move to the whole report**, with MM+bal as the cheaper alternative (same accuracy, 41% at 0.1%, more diluted by padding). Limits: only random padding with calls drawn like the training padding was tested (a padding chosen by an attacker, or from another distribution, was not); not tried on the whole report; 2 epochs, 5 seeds; the top-benign list was not run for the balanced models, and the 0.1% FPR number of ATT+bal has a wide interval.

### Tables (all from the files above)

Malware TPR after the edit (all 9,399 malware reports, threshold fixed at 1% FPR of the unedited benign April reports; mean of 5 seeds):

| model | unedited | insert 5 | insert 20 | insert 50 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|
| released Nebula | 75.0% | 66.1% | 45.9% | 35.5% | 43.4% | 10.3% | 14.0% |
| A (J) | 72.7% | 63.6% | 40.4% | 32.5% | 39.3% | 20.1% | 16.3% |
| C (J, 2 epochs) | 72.2% | 59.8% | 49.4% | 37.0% | 56.1% | 41.6% | 0.8% |
| F (whole report) | 74.5% | 62.1% | 50.7% | 36.4% | 62.1% | 55.6% | 44.2% |
| C+aug | 77.6% | 78.2% | 79.3% | 81.7% | 79.3% | 80.3% | 81.9% |
| ATT+aug | 76.2% | 77.6% | 80.7% | 84.9% | 78.9% | 82.1% | 87.3% |
| C+bal | 77.7% | 74.1% | 68.4% | 61.1% | 73.2% | 65.6% | 38.0% |
| MM+bal | 76.4% | 73.9% | 68.9% | 61.3% | 74.5% | 66.5% | 41.9% |
| ATT+bal | 76.7% | 74.5% | 70.7% | 64.1% | 75.9% | 72.4% | 59.5% |

FPR of 2,000 benign April reports padded the same way (same thresholds):

| model | insert 5 | insert 20 | insert 50 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|
| released Nebula | 0.90% | 1.85% | 3.60% | 1.55% | 10.25% | 9.55% |
| C (J, 2 epochs) | 0.65% | 0.37% | 0.25% | 1.31% | 0.21% | 0.00% |
| C+aug | 7.77% | 17.85% | 28.12% | 11.20% | 18.74% | 48.64% |
| ATT+aug | 9.33% | 25.33% | 41.30% | 11.79% | 33.60% | 66.15% |
| C+bal | 0.94% | 0.81% | 0.41% | 1.20% | 0.86% | 0.18% |
| MM+bal | 0.89% | 0.65% | 0.36% | 1.16% | 0.74% | 0.34% |
| ATT+bal | 1.00% | 0.95% | 1.16% | 1.20% | 1.25% | 1.10% |

Accuracy (April, mean of 5 seeds [group 95%]):

| model | AUC | TPR@1% FPR | TPR@0.1% FPR |
|---|---|---|---|
| C (J, 2 epochs) | 0.9602 [0.9357, 0.9767] | 72.2% [53.5%, 82.3%] | 15.0% [5.1%, 37.0%] |
| C+bal | 0.9745 [0.9576, 0.9844] | 77.7% [65.6%, 85.3%] | 25.4% [7.4%, 50.9%] |
| MM+bal | 0.9757 [0.9604, 0.9847] | 76.4% [63.5%, 85.2%] | 41.2% [22.4%, 57.8%] |
| ATT+bal | 0.9757 [0.9592, 0.9855] | 76.7% [64.7%, 84.2%] | 53.7% [33.0%, 67.3%] |

Same-report copy edits (step 3b, `graded_edits.md`): the balanced models are unaffected. Malware TPR over the eight edits: C+bal 76.2–77.7% (unedited 77.7%), MM+bal 76.4–78.2% (76.4%), ATT+bal 75.6–77.7% (76.7%); benign FPR after the same edits 0.96–1.76% (C+bal, MM+bal) and 0.95–1.29% (ATT+bal). The AUC of ATT+bal does fall with the longest edits (0.9757 unedited, 0.9627 at prepend 20, 0.9485 at prepend 50), although the TPR at the fixed threshold does not.

Attention of ATT+bal after prepending 20 benign calls to 20 malware reports (per seed): mean share on the prepended tokens 11.0–12.2% (mean pooling 30.3%); 17–19 of 20 reports flagged before and 17–18 after; mean logit about 10–13 before and 9–12 after.

## Step 0: benign padding on the whole-report model F (EVAL pool, seeds 0–4)

Same test as `results/robustness` item 2, with the EVAL pool (step 1). Threshold fixed at 1% FPR on the unedited April benign scores of each model and seed.

Malware TPR after padding (all 9,399 malware reports):

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 75.0% | 72.7% | 66.1% | 45.9% | 35.5% | 67.8% | 43.4% | 10.3% | 14.0% |
| A (J) | 72.7% | 71.3% | 63.6% | 40.4% | 32.5% | 67.7% | 39.3% | 20.1% | 16.3% |
| C (J) | 72.3% | 68.8% | 59.5% | 48.2% | 36.1% | 66.9% | 55.7% | 41.2% | 0.5% |
| F (whole report) | 74.5% | 70.4% | 62.1% | 50.7% | 36.4% | 69.5% | 62.1% | 55.6% | 44.2% |

Malware that fits in 512 tokens after the edit (before → after; the same reports for every model):

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| released Nebula | 61.5% → 57.5% | 61.4% → 49.0% | 60.6% → 18.9% | 62.7% → 8.5% | 61.5% → 56.0% | 61.4% → 39.3% | 60.2% → 1.7% | 62.3% → 3.5% |
| A (J) | 64.5% → 61.8% | 64.5% → 48.4% | 64.0% → 14.5% | 71.1% → 11.0% | 64.5% → 60.0% | 64.5% → 34.0% | 63.8% → 3.9% | 70.7% → 5.4% |
| C (J) | 69.9% → 61.5% | 70.1% → 40.0% | 69.9% → 17.4% | 70.9% → 0.6% | 69.9% → 59.3% | 70.1% → 39.3% | 69.7% → 17.8% | 70.6% → 0.1% |
| F (whole report) | 73.1% → 63.2% | 73.2% → 42.8% | 73.0% → 20.6% | 71.8% → 0.1% | 73.1% → 59.5% | 73.3% → 40.4% | 72.9% → 23.3% | 71.5% → 1.2% |

Benign FPR when 2,000 random benign April reports are padded the same way (F and C stay at or below about 1%; A and the released model rise to 7–10% at prepend 20 and 50):

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 1.15% | 1.10% | 0.90% | 1.85% | 3.60% | 1.10% | 1.55% | 10.25% | 9.55% |
| A (J) | 1.02% | 1.02% | 1.31% | 2.18% | 4.86% | 1.10% | 1.63% | 6.72% | 9.94% |
| C (J) | 0.99% | 0.75% | 0.59% | 0.30% | 0.22% | 0.96% | 1.67% | 0.17% | 0.00% |
| F (whole report) | 1.09% | 0.86% | 0.54% | 0.20% | 0.10% | 0.97% | 0.78% | 0.28% | 0.10% |

Seed-paired differences in the change of TPR, points [95% over seeds]:

| difference | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| C (J) − A (J) | -2.1 [-2.8, -1.3] | -3.7 [-5.8, -1.5] | +8.2 [+3.4, +13.8] | +4.0 [+0.7, +8.9] | -0.4 [-2.6, +1.4] | +16.9 [+12.1, +22.6] | +21.5 [+15.3, +27.6] | -15.5 [-20.9, -10.8] |
| F (whole report) − C (J) | -0.6 [-1.3, -0.1] | +0.4 [-0.4, +1.3] | +0.3 [-1.2, +1.7] | -1.9 [-2.6, -1.3] | +0.5 [-0.6, +1.3] | +4.2 [+2.4, +6.4] | +12.2 [+9.7, +14.7] | +41.5 [+39.7, +43.4] |
| F (whole report) − A (J) | -2.7 [-4.1, -1.6] | -3.3 [-5.1, -1.2] | +8.5 [+4.8, +14.0] | +2.1 [-1.4, +6.9] | +0.0 [-1.3, +1.4] | +21.1 [+17.2, +26.8] | +33.6 [+29.0, +38.3] | +26.1 [+19.0, +32.2] |

On the reports that fit in 512 tokens:

| difference | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| C (J) − A (J) | -5.7 [-8.4, -2.8] | -14.0 [-18.2, -10.0] | -3.0 [-12.9, +6.1] | -10.2 [-15.5, -4.7] | -6.1 [-9.5, -3.0] | -0.2 [-7.7, +6.1] | +7.9 [-1.6, +16.8] | -5.3 [-10.5, -0.1] |
| F (whole report) − C (J) | -1.5 [-3.4, +0.2] | -0.4 [-2.4, +1.7] | +0.1 [-3.0, +3.7] | -1.4 [-3.1, +0.6] | -3.0 [-5.8, -0.8] | -2.1 [-3.0, -1.2] | +2.3 [-0.5, +5.1] | +0.2 [-1.6, +2.0] |
| F (whole report) − A (J) | -7.1 [-8.6, -5.0] | -14.3 [-17.1, -12.0] | -2.9 [-10.6, +4.8] | -11.6 [-17.0, -6.8] | -9.1 [-11.9, -6.3] | -2.3 [-9.5, +3.5] | +10.2 [+2.2, +18.3] | -5.1 [-9.8, -0.4] |

F is much better than C on padded malware overall (prepend 20: 55.6% against 41.2%; prepend 50: 44.2% against 0.5%), but on reports whose whole padded sequence fits in 512 tokens F and C are the same (all differences within −3 to +2 points). F's gain is that long reports are not pushed out of the window; it is still diluted (malware reports that fit in 4,096 tokens lose 4 to 38 points, see `step0_padding.md`). Prepending 50 calls fills the 512-token window of every 512-token model.

## Step 1: padding pools

Benign January reports (all have at least one call) split by `hash_apis` group, numpy Generator seed 4000; a group joins EVAL only if it still fits in 2,000, so no group is cut. Row numbers in `pools.json`.

Benign January reports with at least one API call, split by `hash_apis` group (disjoint groups), numpy Generator seed 4000. Row numbers are in `pools.json`.

| pool | reports | distinct sequences (hash_apis) | median calls | mean calls | max calls | used for |
|---|---|---|---|---|---|---|
| EVAL | 2,000 | 499 | 200 | 180.5 | 539 | testing only (padding of April malware) |
| TRAIN | 22,668 | 4,075 | 179 | 165.5 | 1,002 | training augmentation only |

Benign January reports without any call (in neither pool): 0.

## Step 2: new models and training

| model | parameters | change to C | trained on |
|---|---|---|---|
| M | 3,304,257 | masked max over real tokens | January |
| MM | 3,308,353 | [masked mean, masked max] (head input 128) | January |
| ATT | 3,304,321 | learned query q (zero at the start = masked mean), weights = softmax over real tokens of x·q/√64 | January |
| C+aug | 3,304,257 | none (C) | January, malware reports padded |
| ATT+aug | 3,304,321 | as ATT | January, malware reports padded |

Augmentation: for each malware training report (50,630), in each epoch and seed, with probability 0.5 insert (random places) or prepend (50/50) k calls, k uniform 1–50 (mean 25.3), each a random call of a random TRAIN-pool report; re-tokenised, first 512 tokens; about 25,300 reports per epoch; benign reports never edited. Tokens pre-computed on the CPU (`make_aug.py`, one array per seed and epoch) and put over the original rows for that epoch only. Settings otherwise as `train_pooling_v2.py` (AdamW 2.5e-4, batch 64, LR ×0.5 every 1,000 steps, fp16), 2 epochs, 1,177 steps per epoch, no validation selection (regime J).

Cost: smoke run (ATT+aug and MM, 1 epoch, T4 ×2) 1.6 min wall, 61 s per epoch; full run (25 runs, two at a time) 27.4 min wall, about 1 min per epoch and run, peak GPU memory 0.44–0.54 GB. GPU quota was estimated before the full run at 1.5–2.5 h (about 2.9 times the wall time, as in the full-trace run), well under the 6 h limit; the charged amount is not shown by the Kaggle CLI. The kernel waited in Kaggle's queue for about an hour (no other GPU session of ours was running) and started only after it was deleted and pushed again twice, the last time under a new kernel name.

## Step 3a: accuracy on April (regime J, mean of 5 seeds [group 95%])

| subset | model | n (malware) | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|---|
| all | M (max) | 17,402 (9,399) | 0.9578 [0.9388, 0.9721] | 63.0% [36.7%, 77.3%] | 16.8% [6.7%, 29.0%] |
| all | MM (mean+max) | 17,402 (9,399) | 0.9695 [0.9525, 0.9813] | 72.6% [53.0%, 83.0%] | 14.4% [6.9%, 35.1%] |
| all | ATT (attention) | 17,402 (9,399) | 0.9532 [0.9260, 0.9723] | 63.6% [45.6%, 76.1%] | 20.1% [7.9%, 32.0%] |
| all | C+aug | 17,402 (9,399) | 0.9635 [0.9444, 0.9771] | 77.6% [66.3%, 85.3%] | 34.4% [15.3%, 59.3%] |
| all | ATT+aug | 17,402 (9,399) | 0.9577 [0.9338, 0.9742] | 76.2% [64.8%, 84.2%] | 53.7% [34.0%, 66.0%] |
| all | C (J, 2 epochs) | 17,402 (9,399) | 0.9602 [0.9357, 0.9767] | 72.2% [53.5%, 82.3%] | 15.0% [5.1%, 37.0%] |
| all | C (J) | 17,402 (9,399) | 0.9628 [0.9395, 0.9781] | 72.3% [57.2%, 81.8%] | 18.4% [7.4%, 42.0%] |
| all | A (J) | 17,402 (9,399) | 0.9557 [0.9267, 0.9745] | 72.7% [60.9%, 81.4%] | 44.2% [30.5%, 55.6%] |
| all | released Nebula | 17,402 (9,399) | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 51.7% [0.0%, 67.0%] |
| all | LightGBM bag of API names | 17,402 (9,399) | 0.9497 [0.9144, 0.9757] | 62.9% [33.5%, 74.9%] | 31.3% [18.2%, 45.4%] |
| all | M (max) + LightGBM | 17,402 (9,399) | 0.9771 [0.9609, 0.9875] | 69.5% [53.0%, 84.2%] | 44.8% [28.2%, 59.6%] |
| all | MM (mean+max) + LightGBM | 17,402 (9,399) | 0.9798 [0.9622, 0.9898] | 78.8% [62.5%, 88.2%] | 44.5% [29.7%, 60.3%] |
| all | ATT (attention) + LightGBM | 17,402 (9,399) | 0.9762 [0.9563, 0.9877] | 76.2% [59.4%, 85.0%] | 44.3% [30.1%, 59.2%] |
| all | C+aug + LightGBM | 17,402 (9,399) | 0.9770 [0.9582, 0.9880] | 78.9% [65.5%, 86.9%] | 54.1% [34.7%, 66.7%] |
| all | ATT+aug + LightGBM | 17,402 (9,399) | 0.9748 [0.9529, 0.9872] | 80.1% [65.2%, 87.0%] | 56.7% [37.1%, 68.1%] |
| all | C (J, 2 epochs) + LightGBM | 17,402 (9,399) | 0.9782 [0.9590, 0.9892] | 78.9% [63.8%, 87.5%] | 44.6% [30.0%, 60.0%] |
| all | C (J) + LightGBM | 17,402 (9,399) | 0.9793 [0.9603, 0.9899] | 79.6% [68.7%, 87.7%] | 44.9% [30.0%, 61.3%] |
| all | A (J) + LightGBM | 17,402 (9,399) | 0.9753 [0.9511, 0.9884] | 78.3% [68.3%, 86.1%] | 53.1% [35.6%, 66.6%] |
| all | released Nebula + LightGBM | 17,402 (9,399) | 0.9744 [0.9498, 0.9884] | 79.5% [68.7%, 87.6%] | 54.4% [39.9%, 70.7%] |

By number of chunks (the models without LightGBM):

| subset | model | n (malware) | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|---|
| 1 chunk | M (max) | 6,359 (2,855) | 0.9504 [0.9176, 0.9694] | 61.9% [36.5%, 81.6%] | 32.3% [12.0%, 53.4%] |
| 1 chunk | MM (mean+max) | 6,359 (2,855) | 0.9586 [0.9304, 0.9753] | 71.4% [46.9%, 83.5%] | 25.5% [12.2%, 49.9%] |
| 1 chunk | ATT (attention) | 6,359 (2,855) | 0.9495 [0.9214, 0.9684] | 60.1% [44.0%, 77.3%] | 24.3% [10.3%, 39.0%] |
| 1 chunk | C+aug | 6,359 (2,855) | 0.9519 [0.9107, 0.9743] | 75.3% [55.9%, 85.2%] | 39.0% [17.9%, 64.0%] |
| 1 chunk | ATT+aug | 6,359 (2,855) | 0.9513 [0.9093, 0.9746] | 71.9% [48.8%, 84.2%] | 46.8% [17.5%, 65.7%] |
| 1 chunk | C (J, 2 epochs) | 6,359 (2,855) | 0.9573 [0.9299, 0.9735] | 70.1% [47.7%, 82.1%] | 21.7% [9.1%, 42.0%] |
| 1 chunk | A (J) | 6,359 (2,855) | 0.9482 [0.9141, 0.9680] | 64.4% [47.2%, 77.3%] | 27.1% [14.8%, 38.7%] |
| 1 chunk | released Nebula | 6,359 (2,855) | 0.9556 [0.9246, 0.9755] | 61.5% [43.9%, 76.5%] | 42.6% [0.0%, 65.1%] |
| 2-3 chunks | M (max) | 6,077 (3,676) | 0.9748 [0.9446, 0.9884] | 53.9% [23.8%, 73.5%] | 6.4% [0.6%, 17.6%] |
| 2-3 chunks | MM (mean+max) | 6,077 (3,676) | 0.9853 [0.9644, 0.9940] | 68.5% [37.5%, 84.4%] | 5.4% [0.5%, 21.2%] |
| 2-3 chunks | ATT (attention) | 6,077 (3,676) | 0.9769 [0.9431, 0.9897] | 56.6% [32.7%, 75.5%] | 13.6% [2.2%, 29.3%] |
| 2-3 chunks | C+aug | 6,077 (3,676) | 0.9780 [0.9535, 0.9893] | 76.6% [56.0%, 88.9%] | 24.1% [3.9%, 49.4%] |
| 2-3 chunks | ATT+aug | 6,077 (3,676) | 0.9732 [0.9397, 0.9878] | 74.8% [53.7%, 88.4%] | 49.8% [22.4%, 66.9%] |
| 2-3 chunks | C (J, 2 epochs) | 6,077 (3,676) | 0.9792 [0.9497, 0.9910] | 68.0% [37.5%, 83.8%] | 7.1% [0.5%, 30.4%] |
| 2-3 chunks | A (J) | 6,077 (3,676) | 0.9772 [0.9397, 0.9904] | 72.4% [48.3%, 86.4%] | 40.6% [19.9%, 55.3%] |
| 2-3 chunks | released Nebula | 6,077 (3,676) | 0.9833 [0.9587, 0.9930] | 79.3% [61.6%, 89.2%] | 47.2% [0.0%, 70.0%] |
| 4-8 chunks | M (max) | 4,966 (2,868) | 0.9523 [0.8953, 0.9857] | 75.8% [39.0%, 88.2%] | 14.7% [2.2%, 28.8%] |
| 4-8 chunks | MM (mean+max) | 4,966 (2,868) | 0.9637 [0.9194, 0.9907] | 79.1% [58.7%, 90.4%] | 14.9% [4.2%, 47.7%] |
| 4-8 chunks | ATT (attention) | 4,966 (2,868) | 0.9387 [0.8582, 0.9839] | 76.1% [52.3%, 88.4%] | 24.2% [6.0%, 43.0%] |
| 4-8 chunks | C+aug | 4,966 (2,868) | 0.9574 [0.8939, 0.9884] | 81.2% [62.4%, 91.6%] | 43.2% [14.9%, 74.3%] |
| 4-8 chunks | ATT+aug | 4,966 (2,868) | 0.9404 [0.8606, 0.9827] | 82.2% [63.8%, 92.4%] | 65.6% [30.7%, 82.5%] |
| 4-8 chunks | C (J, 2 epochs) | 4,966 (2,868) | 0.9429 [0.8619, 0.9866] | 79.7% [59.3%, 90.8%] | 18.5% [1.2%, 51.0%] |
| 4-8 chunks | A (J) | 4,966 (2,868) | 0.9421 [0.8583, 0.9856] | 81.4% [63.1%, 91.1%] | 66.0% [42.4%, 79.8%] |
| 4-8 chunks | released Nebula | 4,966 (2,868) | 0.9288 [0.8301, 0.9841] | 82.9% [64.8%, 93.1%] | 66.5% [0.0%, 81.6%] |

Paired differences (points for TPR; all April reports):

| difference | subset | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|
| M (max) − C (J, 2 epochs) | all | -0.0025 [-0.0111, +0.0087] | -9.2 [-21.8, +1.8] | +1.8 [-16.9, +14.6] |
| MM (mean+max) − C (J, 2 epochs) | all | +0.0093 [+0.0027, +0.0201] | +0.4 [-3.4, +4.7] | -0.6 [-9.5, +11.4] |
| ATT (attention) − C (J, 2 epochs) | all | -0.0070 [-0.0158, -0.0015] | -8.6 [-13.5, -1.9] | +5.1 [-6.9, +7.8] |
| C+aug − C (J, 2 epochs) | all | +0.0032 [-0.0117, +0.0191] | +5.4 [+1.1, +21.3] | +19.4 [+1.5, +34.2] |
| ATT+aug − C (J, 2 epochs) | all | -0.0025 [-0.0177, +0.0113] | +4.0 [-1.2, +21.3] | +38.7 [+15.9, +53.0] |
| M (max) − released Nebula | all | -0.0008 [-0.0138, +0.0154] | -12.0 [-37.5, +0.8] | -34.9 [-48.9, +16.3] |
| MM (mean+max) − released Nebula | all | +0.0110 [+0.0007, +0.0264] | -2.4 [-20.9, +6.0] | -37.3 [-50.4, +16.7] |
| ATT (attention) − released Nebula | all | -0.0054 [-0.0200, +0.0091] | -11.4 [-28.5, -1.4] | -31.6 [-50.6, +21.9] |
| C+aug − released Nebula | all | +0.0049 [-0.0105, +0.0221] | +2.7 [-4.4, +9.2] | -17.3 [-39.0, +40.9] |
| ATT+aug − released Nebula | all | -0.0009 [-0.0162, +0.0136] | +1.2 [-6.9, +8.5] | +2.0 [-18.8, +57.2] |
| C (J, 2 epochs) − released Nebula | all | +0.0016 [-0.0096, +0.0136] | -2.8 [-20.0, +5.2] | -36.7 [-53.3, +18.6] |
| A (J) − released Nebula | all | -0.0029 [-0.0149, +0.0082] | -2.3 [-11.0, +3.0] | -7.5 [-23.9, +45.9] |
| C (J, 2 epochs) − C (J) | all | -0.0026 [-0.0047, -0.0009] | -0.1 [-7.2, +1.5] | -3.3 [-9.7, +2.1] |

Rank average with LightGBM, differences to released + LightGBM:

| difference | subset | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|
| M (max) + LightGBM − released Nebula + LightGBM | all | +0.0027 [-0.0035, +0.0121] | -10.0 [-22.9, +0.4] | -9.5 [-20.7, -3.3] |
| MM (mean+max) + LightGBM − released Nebula + LightGBM | all | +0.0054 [-0.0000, +0.0139] | -0.8 [-10.1, +4.8] | -9.8 [-19.5, -2.5] |
| ATT (attention) + LightGBM − released Nebula + LightGBM | all | +0.0017 [-0.0035, +0.0086] | -3.3 [-17.4, +0.5] | -10.1 [-20.4, -2.2] |
| C+aug + LightGBM − released Nebula + LightGBM | all | +0.0026 [-0.0034, +0.0101] | -0.6 [-9.9, +7.6] | -0.2 [-16.9, +6.8] |
| ATT+aug + LightGBM − released Nebula + LightGBM | all | +0.0003 [-0.0055, +0.0061] | +0.6 [-13.7, +9.0] | +2.3 [-13.4, +11.9] |
| C (J, 2 epochs) + LightGBM − released Nebula + LightGBM | all | +0.0038 [-0.0009, +0.0101] | -0.6 [-12.2, +6.4] | -9.8 [-19.9, -1.5] |
| A (J) + LightGBM − released Nebula + LightGBM | all | +0.0008 [-0.0027, +0.0045] | -1.2 [-5.8, +2.3] | -1.3 [-15.1, +6.4] |

On the 4–8 chunk reports (new − C 2 epochs) only MM has an AUC interval above 0 (+0.0208 [+0.0019, +0.0582]); the other AUC differences include 0, and ATT+aug gains +47.1 [+7.5, +70.6] points at 0.1% FPR. `accuracy.md` has every subset and difference.

| difference | subset | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|
| M (max) − C (J, 2 epochs) | 4-8 chunks | +0.0094 [-0.0059, +0.0341] | -3.9 [-29.7, +0.0] | -3.8 [-35.4, +16.4] |
| MM (mean+max) − C (J, 2 epochs) | 4-8 chunks | +0.0208 [+0.0019, +0.0582] | -0.6 [-3.3, +5.2] | -3.7 [-18.6, +17.4] |
| ATT (attention) − C (J, 2 epochs) | 4-8 chunks | -0.0042 [-0.0120, +0.0053] | -3.6 [-12.6, -0.2] | +5.7 [-11.9, +13.8] |
| C+aug − C (J, 2 epochs) | 4-8 chunks | +0.0144 [-0.0256, +0.0553] | +1.5 [-1.8, +13.2] | +24.7 [-5.2, +49.1] |
| ATT+aug − C (J, 2 epochs) | 4-8 chunks | -0.0026 [-0.0499, +0.0337] | +2.6 [-1.3, +14.8] | +47.1 [+7.5, +70.6] |

## Step 3b: graded edits with copied calls (results/robustness item 1)

Insert / prepend k = 1, 5, 20, 50 calls copied from the same report; threshold fixed at 1% FPR on the unedited April scores.

Malware TPR:

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 75.0% | 73.6% | 69.3% | 57.5% | 49.2% | 69.6% | 53.7% | 35.7% | 38.0% |
| A (J) | 72.7% | 72.0% | 67.7% | 52.3% | 41.5% | 69.7% | 47.2% | 31.2% | 23.6% |
| C (J) | 72.3% | 71.4% | 69.8% | 69.0% | 71.3% | 70.1% | 67.9% | 70.7% | 67.5% |
| C (J, 2 epochs) | 72.2% | 71.2% | 70.1% | 69.1% | 71.0% | 69.8% | 68.5% | 70.1% | 67.8% |
| M (max) | 63.0% | 62.6% | 62.2% | 60.1% | 63.2% | 62.6% | 62.0% | 61.7% | 62.2% |
| MM (mean+max) | 72.6% | 72.2% | 71.2% | 70.4% | 72.8% | 71.1% | 69.7% | 72.3% | 70.1% |
| ATT (attention) | 63.6% | 62.7% | 61.9% | 61.7% | 65.5% | 61.4% | 61.1% | 64.0% | 62.7% |
| C+aug | 77.6% | 77.5% | 78.8% | 79.9% | 81.8% | 79.1% | 81.1% | 82.0% | 86.7% |
| ATT+aug | 76.2% | 76.3% | 77.4% | 78.3% | 79.9% | 77.2% | 78.9% | 79.9% | 83.7% |

Benign FPR after the same edit of the benign reports:

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 1.00% | 1.09% | 1.04% | 1.72% | 2.87% | 1.09% | 2.06% | 20.89% | 19.41% |
| A (J) | 1.00% | 1.05% | 1.05% | 1.72% | 2.72% | 1.01% | 1.50% | 10.33% | 10.32% |
| C (J) | 1.00% | 0.95% | 1.00% | 1.06% | 1.12% | 0.95% | 2.32% | 1.20% | 1.03% |
| C (J, 2 epochs) | 1.00% | 0.94% | 1.02% | 1.03% | 1.07% | 0.98% | 1.96% | 1.16% | 1.03% |
| M (max) | 1.00% | 1.04% | 1.20% | 1.05% | 1.02% | 1.21% | 1.40% | 1.18% | 1.19% |
| MM (mean+max) | 1.00% | 0.96% | 1.00% | 1.00% | 1.07% | 0.96% | 1.13% | 1.14% | 1.21% |
| ATT (attention) | 1.00% | 0.93% | 1.03% | 0.98% | 1.02% | 1.02% | 1.30% | 1.06% | 1.05% |
| C+aug | 1.00% | 1.12% | 2.00% | 8.03% | 23.22% | 1.78% | 4.44% | 11.63% | 46.35% |
| ATT+aug | 1.00% | 1.69% | 4.63% | 16.95% | 29.45% | 2.70% | 11.66% | 35.86% | 45.69% |

Change in malware TPR [group 95%]:

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| released Nebula | -1.4 [-2.8, -0.3] | -5.7 [-10.4, -1.5] | -17.5 [-32.0, -5.5] | -25.7 [-40.5, -12.6] | -5.4 [-8.9, -1.9] | -21.3 [-35.8, -7.0] | -39.3 [-51.3, -26.1] | -36.9 [-47.8, -25.5] |
| A (J) | -0.8 [-1.3, -0.2] | -5.0 [-7.6, -2.2] | -20.4 [-28.7, -11.1] | -31.3 [-43.0, -19.0] | -3.0 [-5.1, -0.2] | -25.5 [-34.1, -14.5] | -41.5 [-52.6, -29.1] | -49.1 [-60.6, -33.9] |
| C (J) | -0.9 [-1.7, -0.2] | -2.5 [-4.7, -0.6] | -3.3 [-6.4, -0.7] | -1.0 [-2.8, +0.5] | -2.3 [-4.3, -0.6] | -4.4 [-10.3, -0.3] | -1.6 [-3.7, +0.3] | -4.9 [-8.4, -1.9] |
| C (J, 2 epochs) | -1.0 [-1.7, -0.4] | -2.1 [-3.6, -0.8] | -3.1 [-5.5, -0.9] | -1.2 [-3.0, +0.2] | -2.4 [-4.1, -0.8] | -3.7 [-8.1, -0.4] | -2.1 [-4.2, -0.4] | -4.4 [-6.9, -1.8] |
| M (max) | -0.4 [-1.1, +0.2] | -0.8 [-3.5, +1.8] | -2.9 [-6.8, +0.5] | +0.2 [-6.4, +6.0] | -0.4 [-1.8, +1.1] | -1.0 [-5.3, +3.5] | -1.3 [-7.9, +4.7] | -0.8 [-7.8, +5.3] |
| MM (mean+max) | -0.4 [-1.2, +0.4] | -1.4 [-3.1, +0.4] | -2.3 [-4.6, +0.0] | +0.2 [-2.4, +2.3] | -1.5 [-3.4, +0.1] | -2.9 [-6.6, +0.5] | -0.3 [-2.9, +1.7] | -2.5 [-5.4, +0.3] |
| ATT (attention) | -0.9 [-1.5, -0.4] | -1.7 [-3.7, +0.3] | -1.9 [-4.1, +0.9] | +1.9 [-2.8, +6.7] | -2.2 [-4.0, -0.6] | -2.5 [-6.6, +1.2] | +0.4 [-4.8, +5.5] | -1.0 [-5.6, +3.3] |
| C+aug | -0.1 [-0.7, +0.4] | +1.1 [-0.6, +3.1] | +2.3 [-0.3, +5.3] | +4.2 [+1.3, +8.1] | +1.5 [+0.5, +2.7] | +3.5 [+1.6, +6.1] | +4.3 [+1.0, +8.4] | +9.0 [+4.8, +15.0] |
| ATT+aug | +0.1 [-0.4, +0.7] | +1.2 [-0.3, +3.0] | +2.1 [-1.7, +6.6] | +3.7 [+0.5, +8.6] | +1.1 [-0.1, +2.5] | +2.7 [-0.1, +7.1] | +3.8 [-0.0, +8.5] | +7.5 [+3.1, +14.2] |

M, MM and ATT keep C's robustness to copies of the report's own calls (all within a few points of C, TPR 60–73%). The augmented models gain TPR but also false positives on edited benign reports (prepend 20: 11.6% and 35.9%; insert 50: 23.2% and 29.5%).

## Step 3c: padding with benign calls, EVAL pool (results/robustness item 2)

Malware TPR after padding (all 9,399 malware reports):

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 75.0% | 72.7% | 66.1% | 45.9% | 35.5% | 67.8% | 43.4% | 10.3% | 14.0% |
| A (J) | 72.7% | 71.3% | 63.6% | 40.4% | 32.5% | 67.7% | 39.3% | 20.1% | 16.3% |
| C (J) | 72.3% | 68.8% | 59.5% | 48.2% | 36.1% | 66.9% | 55.7% | 41.2% | 0.5% |
| F (whole report) | 74.5% | 70.4% | 62.1% | 50.7% | 36.4% | 69.5% | 62.1% | 55.6% | 44.2% |
| C (J, 2 epochs) | 72.2% | 68.6% | 59.8% | 49.4% | 37.0% | 66.4% | 56.1% | 41.6% | 0.8% |
| M (max) | 63.0% | 60.4% | 54.1% | 40.0% | 30.9% | 58.5% | 47.8% | 18.8% | 5.9% |
| MM (mean+max) | 72.6% | 69.8% | 61.4% | 50.8% | 39.5% | 67.7% | 57.4% | 40.0% | 0.8% |
| ATT (attention) | 63.6% | 60.0% | 51.3% | 40.7% | 29.9% | 57.4% | 47.4% | 25.5% | 5.6% |
| C+aug | 77.6% | 77.5% | 78.2% | 79.3% | 81.7% | 78.8% | 79.3% | 80.3% | 81.9% |
| ATT+aug | 76.2% | 76.7% | 77.6% | 80.7% | 84.9% | 77.5% | 78.9% | 82.1% | 87.3% |

Malware that fits in 512 tokens after the edit (before → after):

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| released Nebula | 61.5% → 57.5% | 61.4% → 49.0% | 60.6% → 18.9% | 62.7% → 8.5% | 61.5% → 56.0% | 61.4% → 39.3% | 60.2% → 1.7% | 62.3% → 3.5% |
| A (J) | 64.5% → 61.8% | 64.5% → 48.4% | 64.0% → 14.5% | 71.1% → 11.0% | 64.5% → 60.0% | 64.5% → 34.0% | 63.8% → 3.9% | 70.7% → 5.4% |
| C (J) | 69.9% → 61.5% | 70.1% → 40.0% | 69.9% → 17.4% | 70.9% → 0.6% | 69.9% → 59.3% | 70.1% → 39.3% | 69.7% → 17.8% | 70.6% → 0.1% |
| F (whole report) | 73.1% → 63.2% | 73.2% → 42.8% | 73.0% → 20.6% | 71.8% → 0.1% | 73.1% → 59.5% | 73.3% → 40.4% | 72.9% → 23.3% | 71.5% → 1.2% |
| C (J, 2 epochs) | 70.1% → 60.7% | 70.3% → 39.3% | 70.4% → 18.3% | 71.1% → 0.6% | 70.1% → 57.3% | 70.3% → 39.0% | 70.2% → 18.4% | 70.8% → 0.1% |
| M (max) | 61.9% → 55.5% | 61.9% → 43.6% | 62.8% → 13.1% | 71.9% → 0.8% | 61.9% → 54.0% | 61.9% → 48.2% | 62.4% → 8.8% | 71.6% → 1.8% |
| MM (mean+max) | 71.4% → 64.1% | 71.5% → 44.4% | 71.7% → 20.8% | 73.4% → 1.9% | 71.4% → 63.1% | 71.5% → 42.8% | 71.5% → 16.7% | 73.1% → 0.3% |
| ATT (attention) | 60.2% → 51.2% | 60.3% → 32.6% | 61.2% → 14.3% | 71.6% → 1.0% | 60.2% → 48.1% | 60.4% → 30.5% | 61.0% → 12.3% | 71.3% → 1.2% |
| C+aug | 75.3% → 75.1% | 75.3% → 77.3% | 74.6% → 79.0% | 69.4% → 80.1% | 75.3% → 76.2% | 75.3% → 76.7% | 74.3% → 77.7% | 69.1% → 76.8% |
| ATT+aug | 71.9% → 72.5% | 71.9% → 74.8% | 70.6% → 80.1% | 61.7% → 84.6% | 71.9% → 74.0% | 71.9% → 74.5% | 70.4% → 78.2% | 61.4% → 82.4% |

Benign FPR when 2,000 random benign April reports are padded the same way:

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| released Nebula | 1.15% | 1.10% | 0.90% | 1.85% | 3.60% | 1.10% | 1.55% | 10.25% | 9.55% |
| A (J) | 1.02% | 1.02% | 1.31% | 2.18% | 4.86% | 1.10% | 1.63% | 6.72% | 9.94% |
| C (J) | 0.99% | 0.75% | 0.59% | 0.30% | 0.22% | 0.96% | 1.67% | 0.17% | 0.00% |
| F (whole report) | 1.09% | 0.86% | 0.54% | 0.20% | 0.10% | 0.97% | 0.78% | 0.28% | 0.10% |
| C (J, 2 epochs) | 0.95% | 0.78% | 0.65% | 0.37% | 0.25% | 0.94% | 1.31% | 0.21% | 0.00% |
| M (max) | 0.99% | 1.01% | 0.76% | 0.35% | 0.23% | 1.30% | 0.71% | 0.12% | 0.06% |
| MM (mean+max) | 1.03% | 0.87% | 0.60% | 0.25% | 0.19% | 1.06% | 0.72% | 0.14% | 0.00% |
| ATT (attention) | 0.90% | 0.79% | 0.58% | 0.32% | 0.20% | 0.98% | 0.95% | 0.18% | 0.03% |
| C+aug | 1.03% | 2.63% | 7.77% | 17.85% | 28.12% | 3.92% | 11.20% | 18.74% | 48.64% |
| ATT+aug | 1.01% | 2.71% | 9.33% | 25.33% | 41.30% | 3.86% | 11.79% | 33.60% | 66.15% |

Seed-paired differences in the change of TPR, points [95% over the 5 seeds], all malware:

| difference | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| M (max) − C (J, 2 epochs) | +1.0 [+0.6, +1.2] | +3.5 [+2.8, +4.1] | -0.2 [-2.5, +2.3] | +3.1 [-0.1, +5.8] | +1.3 [-0.1, +3.6] | +0.9 [-1.5, +3.9] | -13.5 [-21.9, -3.6] | +14.3 [+9.1, +20.5] |
| MM (mean+max) − C (J, 2 epochs) | +0.8 [+0.0, +1.9] | +1.2 [-1.0, +3.1] | +1.1 [-3.5, +4.9] | +2.1 [-3.1, +7.0] | +0.9 [-1.4, +2.8] | +1.0 [-3.5, +5.4] | -1.9 [-10.2, +5.5] | -0.4 [-2.6, +2.8] |
| ATT (attention) − C (J, 2 epochs) | +0.0 [-0.3, +0.4] | +0.1 [-2.3, +2.2] | -0.1 [-3.1, +2.9] | +1.5 [-2.6, +5.6] | -0.4 [-2.4, +1.2] | -0.1 [-3.3, +2.5] | -7.5 [-15.5, +1.7] | +13.4 [+5.8, +21.0] |
| C+aug − C (J, 2 epochs) | +3.5 [+3.1, +4.1] | +12.9 [+12.4, +13.5] | +24.5 [+23.0, +26.1] | +39.3 [+37.5, +41.2] | +7.0 [+5.5, +8.3] | +17.8 [+16.6, +19.2] | +33.3 [+29.7, +36.9] | +75.7 [+73.5, +78.4] |
| ATT+aug − C (J, 2 epochs) | +4.1 [+3.4, +5.0] | +13.8 [+12.2, +15.2] | +27.4 [+24.5, +30.4] | +43.9 [+40.0, +47.8] | +7.1 [+5.8, +7.8] | +18.9 [+17.0, +20.9] | +36.5 [+31.6, +41.2] | +82.6 [+80.2, +85.0] |
| M (max) − C (J) | +0.9 [+0.4, +1.4] | +3.9 [+2.3, +5.1] | +1.1 [-1.2, +4.3] | +4.1 [+0.9, +7.8] | +1.0 [-0.9, +3.2] | +1.4 [-1.3, +4.3] | -13.0 [-22.0, -2.2] | +14.7 [+9.7, +20.5] |
| MM (mean+max) − C (J) | +0.7 [+0.2, +1.3] | +1.6 [+0.1, +3.0] | +2.4 [-1.1, +5.7] | +3.1 [-1.4, +7.6] | +0.6 [-0.2, +1.4] | +1.4 [-2.7, +5.2] | -1.4 [-8.0, +5.2] | +0.1 [-1.8, +3.1] |
| ATT (attention) − C (J) | -0.1 [-0.9, +0.7] | +0.6 [-3.0, +3.7] | +1.3 [-3.5, +5.3] | +2.5 [-2.5, +7.9] | -0.8 [-3.5, +1.4] | +0.3 [-4.4, +3.8] | -7.0 [-17.0, +3.3] | +13.8 [+6.2, +21.8] |
| C+aug − C (J) | +3.4 [+3.0, +3.7] | +13.4 [+11.7, +15.2] | +25.9 [+24.8, +27.0] | +40.3 [+39.5, +41.1] | +6.6 [+5.3, +8.0] | +18.3 [+17.1, +19.7] | +33.8 [+30.9, +36.7] | +76.1 [+74.3, +78.2] |
| ATT+aug − C (J) | +4.0 [+3.4, +4.6] | +14.2 [+12.1, +16.6] | +28.7 [+26.8, +30.5] | +45.0 [+42.5, +47.4] | +6.7 [+5.4, +8.7] | +19.4 [+17.8, +20.3] | +37.0 [+33.0, +40.8] | +83.0 [+80.3, +85.7] |
| C (J, 2 epochs) − C (J) | -0.1 [-0.7, +0.4] | +0.5 [-0.9, +2.0] | +1.3 [-0.1, +2.4] | +1.0 [-0.4, +2.4] | -0.3 [-1.5, +1.2] | +0.5 [-1.2, +1.8] | +0.5 [-1.6, +2.3] | +0.4 [-0.2, +1.1] |

Malware that fits in 512 tokens:

| difference | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| M (max) − C (J, 2 epochs) | +3.0 [+0.4, +6.7] | +12.7 [+10.7, +15.6] | +2.5 [-0.3, +5.9] | -0.7 [-3.6, +2.1] | +4.9 [+1.2, +10.6] | +17.5 [+14.4, +20.7] | -1.8 [-6.1, +2.6] | +0.9 [-2.9, +4.5] |
| MM (mean+max) − C (J, 2 epochs) | +2.2 [-0.4, +5.4] | +3.9 [-1.2, +9.0] | +1.2 [-3.4, +5.4] | -1.1 [-6.0, +3.2] | +4.6 [-0.3, +9.4] | +2.6 [-2.1, +7.2] | -2.9 [-8.1, +0.7] | -2.1 [-7.2, +2.3] |
| ATT (attention) − C (J, 2 epochs) | +0.5 [-0.3, +1.4] | +3.3 [+0.6, +6.0] | +5.2 [+1.8, +7.3] | -0.1 [-2.0, +1.6] | +0.8 [-0.7, +2.5] | +1.4 [-0.1, +3.3] | +3.1 [-0.9, +7.6] | +0.6 [-1.8, +3.4] |
| C+aug − C (J, 2 epochs) | +9.2 [+6.8, +12.2] | +33.0 [+30.5, +35.5] | +56.5 [+52.0, +61.8] | +81.2 [+75.4, +87.0] | +13.7 [+9.1, +18.3] | +32.6 [+30.7, +34.5] | +55.2 [+50.8, +60.4] | +78.4 [+72.8, +84.0] |
| ATT+aug − C (J, 2 epochs) | +10.0 [+6.8, +14.6] | +33.9 [+28.4, +39.9] | +61.6 [+53.9, +70.8] | +93.3 [+84.2, +104.2] | +15.0 [+9.6, +21.6] | +33.8 [+30.1, +39.2] | +59.6 [+52.2, +69.0] | +91.7 [+83.2, +102.4] |
| M (max) − C (J) | +1.9 [-0.3, +4.5] | +11.8 [+9.6, +14.0] | +2.9 [+0.1, +5.2] | -0.8 [-2.2, +0.5] | +2.6 [-1.0, +6.7] | +17.0 [+13.8, +20.7] | -1.6 [-5.6, +3.1] | +0.8 [-1.7, +4.5] |
| MM (mean+max) − C (J) | +1.1 [-0.3, +3.0] | +3.0 [-1.2, +7.0] | +1.7 [-2.0, +4.6] | -1.2 [-5.8, +1.8] | +2.3 [-0.7, +5.5] | +2.0 [-1.7, +5.7] | -2.8 [-7.0, +0.3] | -2.2 [-6.9, +1.3] |
| ATT (attention) − C (J) | -0.6 [-1.7, +0.6] | +2.4 [+0.5, +4.4] | +5.6 [+3.0, +8.2] | -0.3 [-3.3, +2.7] | -1.5 [-3.4, +0.2] | +0.9 [-0.9, +2.8] | +3.2 [-0.1, +8.3] | +0.4 [-3.1, +3.9] |
| C+aug − C (J) | +8.1 [+6.5, +9.7] | +32.1 [+30.3, +34.1] | +56.9 [+53.4, +60.9] | +81.0 [+77.0, +85.0] | +11.4 [+8.7, +14.3] | +32.1 [+30.9, +33.2] | +55.3 [+51.8, +59.0] | +78.2 [+74.2, +82.1] |
| ATT+aug − C (J) | +9.0 [+6.5, +12.2] | +33.0 [+28.6, +38.1] | +62.0 [+55.9, +69.9] | +93.1 [+86.0, +102.2] | +12.7 [+9.2, +16.9] | +33.3 [+30.4, +37.8] | +59.8 [+53.6, +67.7] | +91.6 [+84.8, +100.5] |
| C (J, 2 epochs) − C (J) | -1.0 [-2.5, +0.4] | -0.9 [-2.2, +0.5] | +0.4 [-1.1, +2.0] | -0.2 [-2.1, +1.8] | -2.3 [-4.4, -0.2] | -0.5 [-1.5, +0.5] | +0.1 [-1.5, +1.6] | -0.1 [-2.0, +1.8] |

## Step 3d: the 20 highest-scoring benign April reports (5-seed ensembles; C (J, 2 epochs), C (J), M, ATT, released)

| model | TPR at 0.1% FPR (of the ensemble) | median calls | max calls | distinct sequences | one chunk | share sequence with malware | source clean/syswow64 | in common with C (J, 2 epochs) | in common with C (J) | in common with M (max) | in common with ATT (attention) | in common with released Nebula |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C (J, 2 epochs) | 15.2% | 13 | 50 | 11 | 20 | 9 | 20/0 | – | 17 | 11 | 16 | 3 |
| C (J) | 12.5% | 10 | 50 | 13 | 20 | 8 | 20/0 | 17 | – | 10 | 16 | 4 |
| M (max) | 12.6% | 10 | 50 | 12 | 20 | 14 | 20/0 | 11 | 10 | – | 8 | 4 |
| ATT (attention) | 16.9% | 22 | 442 | 13 | 16 | 7 | 20/0 | 16 | 16 | 8 | – | 3 |
| released Nebula | 51.8% | 8 | 279 | 18 | 14 | 8 | 20/0 | 3 | 4 | 4 | 3 | – |


Spearman correlation of the benign scores (8,003 reports): C (J, 2 epochs) vs C (J) 0.99; C (J, 2 epochs) vs M (max) 0.90; C (J, 2 epochs) vs ATT (attention) 0.98; C (J, 2 epochs) vs released Nebula 0.65; C (J) vs M (max) 0.89; C (J) vs ATT (attention) 0.98; C (J) vs released Nebula 0.68; M (max) vs ATT (attention) 0.91; M (max) vs released Nebula 0.56; ATT (attention) vs released Nebula 0.69.

The 20 reports of every list with their first 30 API names are in `top_benign.md`.

## Step 3e: what ATT attends to when 20 benign calls are prepended

20 random April malware reports (seed 11), "prepend 20" of the padding test; shares over the five seeds (the per-report top-10 tokens of seed 0, with positions and weights, before and after, are in `attention_tokens.md`). "Share with mean pooling": the share the prepended tokens would get from a plain mean.

ATT:

| seed | mean share on prepended tokens | mean share with mean pooling | flagged before | flagged after | mean logit before → after |
|---|---|---|---|---|---|
| 0 | 38.4% | 30.3% | 16/20 | 2/20 | 6.42 → -1.39 |
| 1 | 43.6% | 30.3% | 11/20 | 1/20 | 6.51 → -1.44 |
| 2 | 30.9% | 30.3% | 17/20 | 9/20 | 8.18 → 2.44 |
| 3 | 22.4% | 30.3% | 19/20 | 14/20 | 10.16 → 5.62 |
| 4 | 38.0% | 30.3% | 14/20 | 6/20 | 6.69 → -0.26 |


### ATT (attention), seed 0, per report

| report (row) | real tokens before → after | prepended tokens | logit before → after | share on prepended | top-10 tokens before: token@position (weight) | top-10 tokens after |
|---|---|---|---|---|---|---|
| 269 | 512 → 511 | 128 | 5.39 → 0.25 | 37% (mean pooling 25%) | valueexa@472 (0.004), ▁aug@495 (0.004), ▁loadcursor@17 (0.004), ▁aug@489 (0.003), ▁aug@29 (0.003), ▁getstartupinfow@21 (0.003), ▁getsystemtimeasfiletime@2 (0.003), ▁aug@483 (0.003), ▁aug@477 (0.003), xa@464 (0.003) | ware@79 (0.003), dinstruction@11 (0.003), ▁errata@84 (0.003), ▁aaaaaaaaaaaaaaaaaa@77 (0.003), sdf@108 (0.003), enum@60 (0.003), 94e@41 (0.003), ▁loadcursor@145 (0.003), stream@80 (0.003), ▁0x121192f@59 (0.003) |
| 661 | 510 → 510 | 125 | 7.63 → -0.20 | 35% (mean pooling 25%) | ▁getmodulehandlew@296 (0.004), fc@301 (0.004), sn@302 (0.004), de9@277 (0.004), ▁0x44f8@276 (0.003), ▁kernel32@278 (0.003), 6f@272 (0.003), ▁0x77000000@315 (0.003), ▁0x77000000@270 (0.003), ▁loadlibrarya@291 (0.003) | dinstruction@16 (0.003), inac@122 (0.003), ▁0x420c50@61 (0.003), ▁0xfeee001b@85 (0.003), e2c@39 (0.003), ▁writeprivateprofile@116 (0.003), ▁0x4307e0@46 (0.003), ter@111 (0.003), a34@33 (0.003), 7f9@81 (0.003) |
| 1206 | 512 → 512 | 110 | 10.66 → 3.75 | 24% (mean pooling 21%) | 2@497 (0.004), 86@505 (0.004), an@464 (0.004), 2@504 (0.004), a9@494 (0.004), ▁aug@478 (0.004), ▁0x4610@85 (0.004), 70@79 (0.004), ▁aug@75 (0.004), keystate@496 (0.003) | b54@114 (0.003), 3d68@103 (0.003), ▁0x40c720@120 (0.003), ▁0x4093@110 (0.003), ifest@102 (0.003), 90@91 (0.003), exception@107 (0.003), ind@111 (0.003), ▁0x1211f88@85 (0.003), ▁free@81 (0.003) |
| 1219 | 512 → 510 | 146 | -4.77 → -6.18 | 33% (mean pooling 29%) | ▁loadcursor@15 (0.002), director@506 (0.002), director@482 (0.002), ▁existing@401 (0.002), an@403 (0.002), ▁loadresource@402 (0.002), tim@469 (0.002), ▁regsetvalueexw@498 (0.002), director@410 (0.002), director@47 (0.002) | ▁exe@145 (0.002), ▁instructions@143 (0.002), ▁getsystemtimeasfiletime@148 (0.002), ▁pf@142 (0.002), ▁0x7ce8@34 (0.002), ▁instruction@144 (0.002), a8c@21 (0.002), denied@48 (0.002), informationby@19 (0.002), ▁loadcursor@161 (0.002) |
| 1255 | 512 → 512 | 102 | 12.82 → 4.26 | 31% (mean pooling 20%) | ▁loadcursor@380 (0.002), ▁getsystemtimeasfiletime@370 (0.002), print@443 (0.002), ▁kernel32@297 (0.002), ▁kernel32@277 (0.002), ▁kernel32@302 (0.002), ▁0x1211528@301 (0.002), ▁kernel32@272 (0.002), ▁kernel32@405 (0.002), director@395 (0.002) | bounds@19 (0.004), ▁termin@49 (0.004), ▁0x42d8@25 (0.004), an@20 (0.004), ▁loadcursor@24 (0.004), ▁0x46a1c0@15 (0.004), ▁getmodulehandlew@35 (0.004), ▁openmutexa@41 (0.004), ind@53 (0.004), ▁0x14c@8 (0.004) |
| 1388 | 512 → 510 | 113 | 9.39 → 1.66 | 36% (mean pooling 22%) | ▁0x46f0@466 (0.003), ▁0x7690@482 (0.003), ▁0xfeee0065@462 (0.003), ▁0x77000000@470 (0.003), ▁0x120e69c@476 (0.003), ▁getprocaddress@469 (0.003), ▁0xfeee004d@467 (0.003), ▁kernel32@468 (0.003), ▁kernel32@463 (0.003), ▁0x77000000@495 (0.003) | ▁pf@15 (0.003), ▁isprocessorfeaturepresent@14 (0.003), ▁0x650064@46 (0.003), ▁createtoolhelp32snapshot@24 (0.003), xt@47 (0.003), ▁0x427000@45 (0.003), rosoft@16 (0.003), ▁isdbcsleadbyte@11 (0.003), c@35 (0.003), ▁vc@55 (0.003) |
| 11714 | 70 → 177 | 107 | 14.18 → -0.99 | 72% (mean pooling 60%) | ▁0x0@66 (0.016), ▁0x0@67 (0.016), ▁0x0@68 (0.015), ▁0x0@69 (0.015), 3934@65 (0.015), 18@47 (0.015), 18@58 (0.015), 18@43 (0.015), ▁0x400000@40 (0.015), ▁0xe01f20@20 (0.015) | ▁0x431ef0@53 (0.009), ▁7z8d01e2f892283f20974e9b5c9c74f7aca19b5410a6c1b088abe80d14@16 (0.009), ▁0x12119d0@21 (0.009), ▁7z8d01e2f892283f20974e9b5c9c74f7aca19b5410a6c1b088abe80d14@17 (0.009), 10@47 (0.009), b5e62b38bb0c8cc4c032ee@60 (0.009), ▁400000newimagebase@46 (0.009), ▁0x3e8@28 (0.009), ▁0x12119d0@23 (0.009), ▁0xfeee0059@45 (0.009) |
| 12501 | 377 → 499 | 124 | -0.91 → -2.88 | 28% (mean pooling 25%) | valueexa@156 (0.004), valueexa@295 (0.004), valueexa@191 (0.004), 2d5@297 (0.004), ▁0x7dc2@277 (0.004), ▁user@303 (0.004), ▁0x504@143 (0.004), ▁0x41dd@149 (0.004), valueexa@260 (0.004), hield@188 (0.004) | valueexa@315 (0.003), valueexa@419 (0.003), valueexa@280 (0.003), ▁0x504@406 (0.003), ▁0x7dc2@401 (0.003), 2d5@421 (0.003), ▁0x42a0a4@398 (0.003), hield@416 (0.003), ▁user@427 (0.003), ab@399 (0.003) |
| 12628 | 512 → 511 | 108 | 6.29 → 0.68 | 27% (mean pooling 21%) | 113@405 (0.004), 208@418 (0.003), an@400 (0.003), ▁aug@463 (0.003), ▁0x47ab20@424 (0.003), ▁aug@469 (0.003), ▁aug@415 (0.003), ▁0x47ab20@412 (0.003), ▁none@406 (0.003), valueexa@458 (0.003) | ▁getsystemtimeasfiletime@110 (0.003), ▁loadcursor@122 (0.003), sdf@97 (0.003), ▁0xa429@111 (0.003), ▁dis@123 (0.003), ▁0x1211e30@107 (0.003), dhandle@92 (0.003), exception@77 (0.003), ▁0x100097@78 (0.003), fc@86 (0.003) |
| 13042 | 42 → 156 | 114 | 7.11 → -7.54 | 79% (mean pooling 73%) | ▁msvcr@21 (0.039), ▁0x4600@14 (0.039), ▁codegear@31 (0.036), ▁0xfeee0059@25 (0.035), ▁b2acb2afcd@20 (0.035), ▁0x40a5a2@22 (0.029), ▁none@18 (0.027), ▁0xfeee0059@38 (0.025), ▁0x0@41 (0.023), ▁set@2 (0.023) | 0000000@79 (0.008), ▁0x1870@85 (0.008), an@80 (0.008), ▁0x120@111 (0.008), ▁set@116 (0.007), clus@117 (0.007), ▁0xfeee001b@98 (0.007), 7f9@94 (0.007), director@73 (0.007), let@84 (0.007) |
| 13088 | 512 → 512 | 122 | 9.20 → 3.25 | 27% (mean pooling 24%) | valueexa@17 (0.004), ▁comdlg32@144 (0.004), d61@170 (0.004), ▁0x4314@143 (0.004), valueexa@11 (0.004), valueexa@132 (0.004), clus@21 (0.004), ▁comdlg32@147 (0.004), ▁0x1210e@173 (0.004), ▁comdlg32@162 (0.004) | valueexa@368 (0.003), sdf@80 (0.003), valueexa@17 (0.003), valueexa@254 (0.003), ▁0x4307e0@239 (0.003), valueexa@11 (0.003), clus@21 (0.003), 30@238 (0.003), aa@85 (0.003), an@212 (0.003) |
| 13480 | 42 → 176 | 134 | 7.11 → -8.21 | 85% (mean pooling 76%) | ▁msvcr@21 (0.039), ▁0x4600@14 (0.039), ▁codegear@31 (0.036), ▁0xfeee0059@25 (0.035), ▁b2acb2afcd@20 (0.035), ▁0x40a5a2@22 (0.029), ▁none@18 (0.027), ▁0xfeee0059@38 (0.025), ▁0x0@41 (0.023), ▁set@2 (0.023) | ▁instructions@111 (0.007), ▁exe@113 (0.007), ▁instruction@112 (0.007), ▁0x4308@96 (0.007), ▁pf@110 (0.007), ▁0x12119d0@123 (0.007), ▁isprocessorfeaturepresent@109 (0.007), 98@124 (0.007), ▁0xfeee0059@122 (0.007), ▁isdbcslead@79 (0.007) |
| 13589 | 512 → 512 | 116 | 1.56 → -4.83 | 30% (mean pooling 23%) | ▁msvcrt@272 (0.003), 90@314 (0.003), 90@214 (0.003), ▁loadcursor@18 (0.003), ▁0x42f1a0@277 (0.003), an@279 (0.003), an@273 (0.003), mp@251 (0.003), an@239 (0.003), ▁0x5b45@207 (0.003) | f49c@45 (0.003), ▁0x42d8@30 (0.003), ▁3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d@22 (0.003), ▁0x4238c0@25 (0.003), clus@16 (0.003), ▁set@15 (0.003), ▁0x4114@49 (0.003), hip@34 (0.003), ▁loadcursor@29 (0.003), ▁0x4ac@82 (0.003) |
| 13789 | 512 → 512 | 103 | -0.41 → -3.81 | 27% (mean pooling 20%) | ▁0x8554@439 (0.003), ▁0x8554@446 (0.003), ▁aug@436 (0.003), ▁0x598740@444 (0.003), 113@415 (0.003), ▁widechartomultibyte@424 (0.003), ▁clo@428 (0.003), ▁widechartomultibyte@441 (0.003), ▁clo@438 (0.003), ▁clo@445 (0.003) | ▁beginpaint@85 (0.003), ▁getsystemtimeasfiletime@105 (0.003), ▁0xa429@106 (0.003), ▁dis@118 (0.003), ▁loadcursor@117 (0.003), ▁aug@126 (0.003), 0068@92 (0.003), ▁getstartupinfow@121 (0.003), ▁none@86 (0.003), next@102 (0.003) |
| 14628 | 512 → 512 | 114 | 5.59 → -1.08 | 31% (mean pooling 22%) | valueexa@126 (0.003), valueexa@243 (0.003), valueexa@17 (0.003), local@237 (0.003), ▁setst@232 (0.003), ▁0xfde9@238 (0.003), ▁0x9ad0@110 (0.003), ▁0xfff7@105 (0.003), 240d4@124 (0.003), 2a@208 (0.003) | ▁0x1211ebf@81 (0.003), exception@79 (0.003), valueexa@17 (0.003), ▁0x427000@111 (0.003), 11ff8@112 (0.003), ▁0x420c00@32 (0.003), ▁0x4018@119 (0.003), ▁0x76c8@125 (0.003), 3d68@75 (0.003), valueexa@11 (0.003) |
| 15032 | 508 → 508 | 113 | 8.41 → -3.13 | 33% (mean pooling 22%) | valueexa@348 (0.004), ▁isprocessorfeaturepresent@382 (0.004), d138@335 (0.004), ▁0x41de68@356 (0.004), ad@342 (0.004), director@376 (0.004), a8@337 (0.004), idistreamout@336 (0.004), ▁0x771@361 (0.004), window@339 (0.004) | ▁0xd4@33 (0.003), ▁0x431ef0@50 (0.003), 70@15 (0.003), ▁164635@58 (0.003), ▁getmenuitemcount@59 (0.003), dee@46 (0.003), ▁0x454840@21 (0.003), ing@22 (0.003), ies@23 (0.003), exception@10 (0.003) |
| 15422 | 512 → 512 | 102 | 4.16 → 0.78 | 27% (mean pooling 20%) | 113@405 (0.003), 208@418 (0.003), ▁aug@463 (0.003), ▁aug@469 (0.003), valueexa@458 (0.003), an@400 (0.003), ▁0x47ab20@424 (0.003), ▁aug@415 (0.003), ▁1646398@437 (0.003), ▁0x47ab20@412 (0.003) | ▁0x4238c0@54 (0.003), um@58 (0.003), ind@17 (0.003), 14@39 (0.003), ▁0x40a58@47 (0.003), eck@23 (0.003), ▁0x7de4@48 (0.003), ▁0x45f0@21 (0.003), ▁0xfeee0044@10 (0.003), ▁al@42 (0.003) |
| 16660 | 401 → 511 | 114 | 12.96 → 2.88 | 37% (mean pooling 22%) | ▁0x4610@314 (0.003), ▁kernel32@399 (0.003), ▁0x45f0@401 (0.003), ▁lstrcmp@299 (0.003), ▁0x77000000@277 (0.003), ▁0x1@398 (0.003), pri@303 (0.003), ▁getfile@304 (0.003), c000@289 (0.003), ▁0x77000000@297 (0.003) | ▁inf@41 (0.004), ▁getsystemtimeasfiletime@57 (0.003), ▁0xa429@58 (0.003), ▁0x100220@14 (0.003), ▁0x427000@28 (0.003), ▁beginpaint@62 (0.003), ▁0x9@30 (0.003), b5a5@37 (0.003), an@48 (0.003), ▁interfacenotsuped@47 (0.003) |
| 16855 | 508 → 512 | 129 | 5.92 → -3.26 | 36% (mean pooling 25%) | ▁0xfeee001b@316 (0.003), ▁0x508@304 (0.003), ▁api@314 (0.003), ▁0xfeee001b@311 (0.003), ▁0xfeee001b@308 (0.003), ▁loadlibrarya@302 (0.003), ▁loadlibraryexw@315 (0.003), ▁variantorsafearray@293 (0.003), ▁clo@366 (0.003), ▁api@306 (0.003) | ff@86 (0.003), ▁0x41@110 (0.003), ▁0x6d@111 (0.003), ▁getsystemtimeasfiletime@81 (0.003), ▁privilege@76 (0.003), db4@82 (0.003), ▁0xfeee0059@85 (0.003), ▁0x42e2f0@117 (0.003), ▁createsemaphorea@112 (0.003), ▁getusernamea@88 (0.003) |
| 17148 | 457 → 510 | 158 | 6.18 → -3.20 | 31% (mean pooling 31%) | valueexa@59 (0.004), valueexa@48 (0.004), valueexa@42 (0.004), 65@343 (0.004), valueexa@31 (0.004), ▁variantorsafearray@365 (0.004), valueexa@323 (0.004), 65@346 (0.004), ▁variantorsafearray@339 (0.004), valueexa@284 (0.004) | ken@225 (0.003), ▁exe@144 (0.003), valueexa@59 (0.003), valueexa@48 (0.003), ▁instructions@142 (0.003), ware@150 (0.003), ▁instruction@143 (0.003), ▁duplic@250 (0.003), valueexa@42 (0.003), ▁pf@141 (0.003) |

ATT+aug:

| seed | mean share on prepended tokens | mean share with mean pooling | flagged before | flagged after | mean logit before → after |
|---|---|---|---|---|---|
| 0 | 27.3% | 30.3% | 19/20 | 18/20 | 10.75 → 10.06 |
| 1 | 26.8% | 30.3% | 18/20 | 17/20 | 12.05 → 11.12 |
| 2 | 21.0% | 30.3% | 19/20 | 17/20 | 10.94 → 9.91 |
| 3 | 22.4% | 30.3% | 19/20 | 17/20 | 10.65 → 8.87 |
| 4 | 24.4% | 30.3% | 19/20 | 18/20 | 10.08 → 9.24 |


### ATT+aug, seed 0, per report

| report (row) | real tokens before → after | prepended tokens | logit before → after | share on prepended | top-10 tokens before: token@position (weight) | top-10 tokens after |
|---|---|---|---|---|---|---|
| 269 | 512 → 511 | 128 | 13.26 → 13.89 | 17% (mean pooling 25%) | ▁olerun@231 (0.004), ▁0x432c1c@351 (0.004), ▁0x44d4b8@236 (0.004), ▁0x42e713@226 (0.004), ▁olerun@359 (0.004), ▁olerun@347 (0.004), ▁0xad00@196 (0.004), ▁0x46add8@251 (0.004), ▁0x40d888@216 (0.004), ▁0x44d4b8@343 (0.004) | ▁olerun@359 (0.004), ▁0x432c1c@479 (0.004), ▁0x44d4b8@364 (0.004), ▁0x42e713@354 (0.004), ▁olerun@487 (0.004), ▁olerun@475 (0.004), ▁0xad00@324 (0.004), ▁0x46add8@379 (0.004), ▁0x40d888@344 (0.004), ▁0x44d4b8@471 (0.004) |
| 661 | 510 → 510 | 125 | 9.45 → 7.43 | 21% (mean pooling 25%) | ▁0x424530@19 (0.005), ▁0x424530@12 (0.004), ▁var@26 (0.004), ▁0x40287e@487 (0.004), virt@36 (0.004), ▁0x26@492 (0.004), c9@472 (0.004), ▁getacl@42 (0.004), lssetvalue@50 (0.004), virt@28 (0.004) | ▁0x424530@144 (0.006), ▁getacl@167 (0.006), ▁0x424530@137 (0.006), virt@166 (0.006), ▁var@151 (0.005), virt@153 (0.005), virt@178 (0.005), ▁0x120e6@133 (0.005), virt@156 (0.005), virt@183 (0.005) |
| 1206 | 512 → 512 | 110 | 14.07 → 14.04 | 26% (mean pooling 21%) | olf@31 (0.004), olf@23 (0.004), olf@7 (0.004), 95@33 (0.004), 95@25 (0.004), ▁0x4e4@24 (0.004), ▁0x4e4@32 (0.004), 95@17 (0.004), olf@15 (0.004), 95@9 (0.004) | olf@31 (0.004), 95@33 (0.004), olf@23 (0.004), 95@25 (0.004), ▁0x4e4@24 (0.004), ▁0x4e4@32 (0.004), 95@17 (0.004), olf@7 (0.004), ▁0x5266@16 (0.004), 95@9 (0.004) |
| 1219 | 512 → 510 | 146 | -6.61 → 2.98 | 50% (mean pooling 29%) | ▁tlsgetvalue@358 (0.008), ▁tlsgetvalue@382 (0.007), ▁tlsgetvalue@262 (0.007), ▁tlsgetvalue@286 (0.007), ▁tlsgetvalue@98 (0.006), ▁tlsgetvalue@310 (0.006), ▁tlsgetvalue@454 (0.006), ▁tlsgetvalue@118 (0.005), 21@69 (0.005), ▁kernel32@357 (0.005) | ▁0x90@31 (0.009), ee098@38 (0.009), disk@15 (0.009), tetow@53 (0.009), ▁heap@27 (0.008), f09fc@39 (0.008), ▁0x4160b0@24 (0.008), ▁0x1@37 (0.008), ▁0x45f0@28 (0.008), ▁0xfeee0001@5 (0.008) |
| 1255 | 512 → 512 | 102 | 14.29 → 12.18 | 8% (mean pooling 20%) | ▁0x413972@114 (0.004), drl6660drl6660drl6660drl6660drl6660drl6660drl6660drl6660@103 (0.004), ▁ntmapviewofsection@112 (0.004), ▁0x413972@106 (0.004), ▁0x413972@99 (0.004), ▁0x40f660@107 (0.004), drl6660drl6660drl6660drl6660drl6660drl6660drl6660drl6660@118 (0.004), ▁ntmapviewofsection@121 (0.004), ▁ntmapviewofsection@40 (0.004), ▁ntmapviewofsection@34 (0.004) | ▁ntmapviewofsection@229 (0.005), ▁0x413972@231 (0.005), ▁0x413972@216 (0.005), drl6660drl6660drl6660drl6660drl6660drl6660drl6660drl6660@235 (0.005), ▁ntmapviewofsection@223 (0.005), drl6660drl6660drl6660drl6660drl6660drl6660drl6660drl6660@220 (0.005), ▁ntmapviewofsection@214 (0.005), drl6660drl6660drl6660drl6660drl6660drl6660drl6660drl6660@205 (0.004), ▁0x413972@208 (0.004), ▁0x40f660@209 (0.004) |
| 1388 | 512 → 510 | 113 | 10.93 → 9.53 | 11% (mean pooling 22%) | 5b@243 (0.004), ▁0x57@88 (0.004), 180@113 (0.004), zoneinformation@203 (0.004), ▁0x75@98 (0.004), 27dc@69 (0.004), c9@361 (0.004), ▁0x26@183 (0.004), ▁0x1210e8@381 (0.004), rag@219 (0.004) | ▁ag@291 (0.005), ▁0x4238d8@504 (0.005), zoneinformation@316 (0.005), ▁0x26@296 (0.005), ed1@281 (0.005), ible@261 (0.005), ▁0xe9@286 (0.005), ▁0x40287e@489 (0.004), c9@474 (0.004), ▁0x1210e8@494 (0.004) |
| 11714 | 70 → 177 | 107 | 15.14 → 14.62 | 58% (mean pooling 60%) | een@24 (0.019), 692e6669@51 (0.019), ▁0x100300@28 (0.018), ▁0x79c0@45 (0.018), ▁ver@56 (0.018), 53@64 (0.017), ▁0x4541@37 (0.017), ▁0x71e0@19 (0.017), descrip@14 (0.017), ▁user32@50 (0.017) | c3@101 (0.008), ▁0xfeee0037@69 (0.008), 53@171 (0.008), 692e6669@158 (0.008), een@131 (0.008), descrip@121 (0.008), ▁0x79c0@152 (0.008), ▁ver@163 (0.008), ▁0x71e0@126 (0.008), ▁0x100300@135 (0.007) |
| 12501 | 377 → 499 | 124 | 11.71 → 12.97 | 32% (mean pooling 25%) | top@228 (0.007), 180@230 (0.006), top@196 (0.006), ▁0x7dc4@56 (0.006), ▁0x1075@227 (0.006), ▁0x7dc4@367 (0.006), ▁0x7dc4@363 (0.006), lu@232 (0.006), ▁0x42fbf0@359 (0.006), ▁0x77000723@249 (0.006) | ▁0x7dc4@180 (0.004), 1a0@176 (0.004), top@352 (0.004), 180@354 (0.004), ies@52 (0.004), top@320 (0.004), ▁0x7dc4@487 (0.004), ▁0x7dc4@491 (0.004), lu@356 (0.004), ▁0x42fbf0@483 (0.004) |
| 12628 | 512 → 511 | 108 | 12.90 → 13.88 | 16% (mean pooling 21%) | ▁regquery@311 (0.004), aphore@307 (0.004), aphore@303 (0.004), ▁regquery@315 (0.004), ▁0x120f7@228 (0.004), ▁regquery@252 (0.004), b18@216 (0.004), aphore@258 (0.004), lsfree@240 (0.004), db0@282 (0.004) | ▁regquery@360 (0.004), ▁regquery@419 (0.004), aphore@366 (0.004), ▁regquery@423 (0.004), ▁0x40a586@378 (0.004), b18@324 (0.004), ce8@354 (0.004), aphore@411 (0.004), lsfree@348 (0.004), aphore@415 (0.004) |
| 13042 | 42 → 156 | 114 | 9.04 → 4.67 | 67% (mean pooling 73%) | thela@39 (0.045), ffe69@27 (0.041), f7464@26 (0.041), ▁0x44d4@35 (0.039), e9297910ee4fd704f376350@40 (0.037), ▁0x7e5f@17 (0.037), 2w@33 (0.036), ▁0xfeee008c@30 (0.033), un@37 (0.032), 74c8@16 (0.031) | thela@153 (0.018), ▁0x7e5f@131 (0.016), 74c8@130 (0.016), e9297910ee4fd704f376350@154 (0.016), ▁0x7be0@45 (0.015), f7464@140 (0.015), ffe69@141 (0.015), ▁0x7ed1@16 (0.015), ▁0x120e6@61 (0.015), ▁0x4600@128 (0.014) |
| 13088 | 512 → 512 | 122 | 12.57 → 12.30 | 24% (mean pooling 24%) | ▁ifyou@70 (0.003), ▁0x4316@69 (0.003), ▁0x41cae4@78 (0.003), ▁0x4316@95 (0.003), ▁0x1211f40@86 (0.003), ▁0x4316@91 (0.003), db5@193 (0.003), ▁sleep@474 (0.003), ▁0x42e550@96 (0.003), ▁0x1211f40@82 (0.003) | ▁0x8920@33 (0.004), db5@315 (0.004), ▁bitblt@310 (0.004), ger@308 (0.003), ▁0x438c00@280 (0.003), ▁sessionmanager@2 (0.003), ad7@300 (0.003), 28000@52 (0.003), ▁ifyou@192 (0.003), ▁0x41cae4@200 (0.003) |
| 13480 | 42 → 176 | 134 | 9.04 → 7.89 | 66% (mean pooling 76%) | thela@39 (0.045), ffe69@27 (0.041), f7464@26 (0.041), ▁0x44d4@35 (0.039), e9297910ee4fd704f376350@40 (0.037), ▁0x7e5f@17 (0.037), 2w@33 (0.036), ▁0xfeee008c@30 (0.033), un@37 (0.032), 74c8@16 (0.031) | ▁0xfeee0037@33 (0.015), thela@173 (0.013), ▁heapfree@129 (0.012), ▁0x7e5f@151 (0.012), ▁kernel32@37 (0.012), ffe69@161 (0.012), 2w@167 (0.012), e9297910ee4fd704f376350@174 (0.011), f7464@160 (0.011), ▁0x1@36 (0.011) |
| 13589 | 512 → 512 | 116 | 3.39 → -0.84 | 20% (mean pooling 23%) | struction@486 (0.006), 3784@448 (0.006), yourcomputer@429 (0.006), ▁0x9c40@463 (0.006), ▁0x4611@478 (0.005), criticalsection@421 (0.005), ▁leav@407 (0.005), ▁kernel32@485 (0.005), ▁leav@432 (0.005), 96@490 (0.005) | ▁0x169b8@436 (0.007), ▁tlsgetvalue@292 (0.006), tetow@71 (0.006), ▁tlsgetvalue@444 (0.006), ▁tlsgetvalue@107 (0.006), ▁tlsgetvalue@219 (0.006), ▁tlsgetvalue@405 (0.006), ▁tlsgetvalue@256 (0.006), ▁tlsgetvalue@199 (0.005), ▁leav@439 (0.005) |
| 13789 | 512 → 512 | 103 | 9.26 → 8.03 | 16% (mean pooling 20%) | 68f@313 (0.005), ▁0x21b8@277 (0.005), 68f@317 (0.005), a891@259 (0.005), 68f@265 (0.005), ▁0x8920@419 (0.005), ▁loadstringa@297 (0.005), ▁0x2190@213 (0.005), 0064@247 (0.005), criticalsection@312 (0.005) | 68f@420 (0.006), ▁0x21b8@380 (0.005), 68f@416 (0.005), 68f@368 (0.005), 0064@350 (0.005), ▁leav@419 (0.005), a891@424 (0.005), a891@428 (0.005), a891@362 (0.005), dbc@285 (0.005) |
| 14628 | 512 → 512 | 114 | 12.60 → 11.67 | 17% (mean pooling 22%) | db5@191 (0.003), ▁bitblt@186 (0.003), 279@164 (0.003), ▁0x438c00@154 (0.003), ad7@176 (0.003), ger@184 (0.003), ▁ifyou@65 (0.003), ▁locales@357 (0.003), ▁0x44f9@185 (0.003), ▁var@156 (0.003) | db5@305 (0.004), ▁bitblt@300 (0.004), ▁sleep@449 (0.003), rwlock@450 (0.003), rwlock@484 (0.003), ▁sleep@483 (0.003), ▁0x438c00@259 (0.003), ▁0x41cae4@187 (0.003), ad7@290 (0.003), ▁ifyou@179 (0.003) |
| 15032 | 508 → 508 | 113 | 14.48 → 13.30 | 20% (mean pooling 22%) | ▁0x23@486 (0.004), ▁tolower@24 (0.004), ▁0x23@496 (0.004), 72c@171 (0.004), ▁0x42e388@28 (0.004), ▁0x23@432 (0.004), ▁0x23@504 (0.004), ▁0x23@424 (0.004), ▁0x23@478 (0.004), ▁0x23@450 (0.004) | 72c@284 (0.004), ▁0x43b3d8@262 (0.004), ▁0x43b3d8@129 (0.004), ▁0x23@133 (0.004), ies@23 (0.004), ▁tolower@137 (0.004), ▁0x42e388@141 (0.004), karton@169 (0.004), ▁0x1211f@24 (0.004), tetow@304 (0.004) |
| 15422 | 512 → 512 | 102 | 12.61 → 11.84 | 8% (mean pooling 20%) | ▁4d5a900003@303 (0.005), ▁4d5a900003@307 (0.005), ▁suspend@240 (0.005), bc5@311 (0.005), ▁0x1210e2b@216 (0.005), ▁4d5a900003@258 (0.005), 0054@228 (0.005), ▁thisprogram@222 (0.005), 7ea@246 (0.005), 005e@234 (0.005) | ▁4d5a900003@360 (0.005), ▁suspend@342 (0.005), ▁thisprogram@324 (0.005), 7ea@431 (0.005), 7ea@348 (0.005), bc5@354 (0.005), ▁0x126@372 (0.005), ▁uti@366 (0.005), ▁4d5a900003@409 (0.005), 005e@336 (0.005) |
| 16660 | 401 → 511 | 114 | 14.57 → 13.30 | 11% (mean pooling 22%) | ▁de@218 (0.004), ustbe@217 (0.004), ame@216 (0.004), ▁0x4378c8@199 (0.004), ▁fa@26 (0.004), ▁0x115@103 (0.004), lay@100 (0.004), 53@363 (0.004), bl@358 (0.004), ▁0x1211ea0@4 (0.004) | ▁0x4378c8@313 (0.004), ▁0x115@295 (0.003), f70@281 (0.003), ▁0x115@217 (0.003), ▁0x120e6@294 (0.003), ▁0x7e8d@442 (0.003), lay@224 (0.003), 148@271 (0.003), 148@447 (0.003), ▁fa@176 (0.003) |
| 16855 | 508 → 512 | 129 | 10.84 → 9.11 | 15% (mean pooling 25%) | aa8@445 (0.005), aa8@406 (0.005), ▁0x424530@19 (0.005), tetow@411 (0.004), ▁strncmp@431 (0.004), ▁sleep@52 (0.004), ▁strncmp@437 (0.004), tetow@426 (0.004), ▁initcommoncontrols@37 (0.004), ▁0x424530@12 (0.004) | ▁0x424530@148 (0.005), ▁sleep@181 (0.005), ▁initcommoncontrols@166 (0.005), ▁0x424530@141 (0.005), ingcadwork@161 (0.005), ▁heapfree@171 (0.005), lssetvalue@177 (0.005), 2w@151 (0.005), ▁0x120e6@140 (0.005), ▁0x120e6@147 (0.005) |
| 17148 | 457 → 510 | 158 | 11.44 → 8.49 | 43% (mean pooling 31%) | ▁0x4680@36 (0.004), ▁0x549@38 (0.004), fa7@434 (0.004), ▁0x4680@433 (0.004), ryptographicproviderv1@37 (0.004), ▁0x4680@441 (0.004), fa7@39 (0.004), fa7@431 (0.004), fa7@442 (0.004), ▁0x549@55 (0.004) | ▁0x4680@36 (0.005), ▁0x549@38 (0.005), ryptographicproviderv1@37 (0.005), fa7@39 (0.005), ▁0x549@55 (0.005), fa7@56 (0.005), ▁0x4680@53 (0.005), ▁documentpropertiesw@34 (0.005), ▁0x549@66 (0.004), ▁0x4680@64 (0.004) |

The top-10 tokens of ATT are mostly fragments of addresses and arguments (`0x…` pieces, `aug`, short hex tokens) spread over the window, with weights of 0.003–0.004; No token dominates (largest weight 0.039 in seed 0), so ATT behaves like a mean.

## Caveats

- Only regime J, 5 seeds, 2 epochs for the new models; the intervals include sampling of April reports but not of training seeds beyond these five (seed-paired intervals do cover seeds). M and ATT have large seed spread (TPR@1% sd 8 and 13.5 points).
- C (J, 2 epochs) uses the fp16 epoch checkpoint of the 10-epoch run for the edited-report scores (logits of the unedited April set are the Kaggle ones; they agree within 0.2).
- The padding pool EVAL is 2,000 benign January reports (499 sequences); the TRAIN pool 22,668 (4,075 sequences). The old results/robustness item 2 used a different random pool, so its numbers differ by a few points from step 0 here.
- Padded benign FPR is measured on 2,000 random benign April reports, not all 8,003. Padding is random, fixed k, nothing optimised; edits live in memory, only scores are cached. The augmentation token arrays (benign-call padding of January malware, TRAIN pool) are in `/Users/manish/Code/mtp/pooling_v4_stage/aug` and in a private Kaggle dataset; they are not in the repository.
- Round 4b: the top-benign list (step 3d) was not run for C+bal, MM+bal and ATT+bal. The graded copy edits (step 3b) cover all three (the first scoring attempt stalled on a loaded laptop and was re-run). The balanced augmentation tokens are in `/Users/manish/Code/mtp/pooling_v4_stage/augb` and the private Kaggle dataset `nebula-speakeasy-augb-v4`.
- Nothing here is committed.

## Files

`accuracy.md/json`, `step0_padding.md/json`, `step3_padding.md/json`, `graded_edits.md/json`, `top_benign.md/json`, `attention_tokens.md/json`, `pools.md`, `pools.json`; code in `scripts/pooling_v4/` (`make_pools.py`, `make_aug.py`, `padding_eval.py`, `evaluate_v4.py`, `graded_edits_v4.py`, `top_benign_v4.py`, `attention_tokens.py`, `v4_common.py`), `scripts/kaggle/train_pooling_v4.py`, `kernel_v4_smoke/`, `kernel_v4_full/`, and the pooling modes in `hier_nebula/pooling_variants.py` (tests in `hier_nebula/test_pooling.py`, test 9).
