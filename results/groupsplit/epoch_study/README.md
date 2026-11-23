# Epoch study (diagnostic): README

**Diagnostic only. The final models are NOT changed by this study; any change needs the owner's approval after reading the results.** Validation parts of two folds only (folds 9 and 4; only these two pass the fold rule, so the "mean over folds" rests on two folds and is weak), 5 seeds per fold, epochs 1 to 5, corrected tokenizer. No April data was used or opened. No seed collapsed (lowest validation AUC 0.873).

**Summary in plain English.** (1) *Does validation pAUC peak at the chosen epochs?* Only for M1 and M2, and only on both folds: M1 and M2 are best at epoch 1 on fold 9 and on fold 4, which is the epoch we chose. For M3 (chosen epoch 3) and M4 (chosen epoch 1) the peak is somewhere else on both folds: M3 peaks at epoch 5 on fold 9 (0.474, but only 0.008 above epoch 3, so that curve is flat) and at epoch 2 on fold 4 (0.670 against 0.618 at epoch 3, a drop of 5 points); M4 peaks at epoch 4 on fold 9 (0.467 against 0.444 at epoch 1, but its epoch-3 value is 0.245, so that curve is erratic) and at epoch 2 on fold 4 (0.666 against 0.654 at epoch 1). (2) *Does validation loss rise after epoch 1?* From epoch 3 on, yes, for every model on both folds: the loss keeps growing (M1 on fold 9: 0.67 at epoch 1, 1.56 at epoch 5) while the training loss falls to about 0.04, so the models become over-confident. At epoch 2 it is not the same on the two folds: on fold 4 the loss of M1 (0.85 to 0.76) and M3 (0.40 to 0.35) is lower at epoch 2 than at epoch 1, on fold 9 it is already higher. The ranking quality (pAUC) falls much less than the loss rises for M1 and M3 (nearly flat), but it falls clearly and becomes erratic for M2 and M4 (M2 on fold 9: 0.59 at epoch 1, 0.35 at epoch 4). (3) *Do the padded models gain robustness with more epochs, and does it cost clean pAUC?* No consistent gain. Detection after 50 LightGBM-chosen calls: M3 goes from 6.7% to 4.9% on fold 9 and from 16.5% to 5.9% on fold 4; M4 from 19.1% to 16.9% on fold 9 (dip to 11.4% at epoch 3) and from 34.3% to 47.4% on fold 4 (peak 56.0% at epoch 2); the balanced 2 x 2 cells are flat or fall (flatten + balanced 2.6% to 0.0%, attention + balanced 6.7% to 4.9%). Random 50 prepended calls give the same picture (M3 20.8% to 21.8% and 27.2% to 20.7%; M4 29.9% to 31.1% and 63.7% to 66.3%). So the only visible gain is M4 on fold 4, and it is largest at epoch 2, not at epoch 5. The clean cost is small to moderate: M3 +1.5 points (fold 9) and -4.3 points (fold 4) of pAUC from epoch 1 to 5, M4 -5.2 and -4.9 points; the padded-benign false-alarm rate (seed mean) stays below 0.8% at every epoch (the largest single seed-epoch value is 1.3%), so more epochs do not make padded benign reports look malicious. The padded models are more robust than their unpadded counterparts already at epoch 1 (for example LightGBM 50 detection M4 34.3% against M2 15.6% on fold 4). (4) *Is the chosen epoch inside the one-SE band on every fold?* For M1, M2 and M4 yes, on both folds (M1: band [1] and [1, 2, 4]; M2: [1] and [1]; M4: [1, 4] and [1, 2, 3]). For M3 no, on both folds: the band is [2, 4, 5] on fold 9 and [2] on fold 4, and epoch 3 is in neither. With the SE across the two folds every epoch is inside the band for M1, M3 and M4 (two folds give a very wide SE), so that version says nothing; only M2 (band [1]) is clearly pinned to epoch 1. **The two folds differ** in level (epoch-1 pAUC 0.44 to 0.59 on fold 9, 0.63 to 0.65 on fold 4) and in shape: on fold 4 M3 and M4 are best at epoch 2 and M1 is flat, on fold 9 M3 is flat and M4 erratic. **Limits:** two folds, five seeds (the seed spread is large, especially for M2 and M4), validation reports only (the absolute detection numbers under padding are much lower here than on April because the group-split validation is harder), one tokenizer fitted on all January text, padding at k = 50 only. This study does not choose or change any epoch.

## Contents

- `tables.md`: tables per model and fold (mean ± SD over seeds), mean over folds ± 1 SE across folds, best epochs and one-SE bands; `results.json`: the same numbers;
- `facts.md`: the numbers behind the four questions; `folds.md`: the folds (NOTES 28.1);
- `fig_epochs_M1_M4_{single,double}_column.{pdf,png}` + `fig_epochs_M1_M4_caption.txt`; `fig_epochs_2x2_fold9_{single,double}_column.{pdf,png}` + caption;
- design and rules: NOTES 28 (written before any computation). **Diagnostic only. The final models are NOT changed by this study; any change needs the owner's approval after reading the results.**

## Facts behind the four questions (computed by baseline/epoch_study_report.py)

**Q1 peak of validation pAUC at the chosen epoch**

- M1 Nebula (chosen epoch 1): fold 9: best epoch 1 (= chosen); fold 4: best epoch 1 (= chosen); mean over folds: best epoch 1
- M2 two-level (chosen epoch 1): fold 9: best epoch 1 (= chosen); fold 4: best epoch 1 (= chosen); mean over folds: best epoch 1
- M3 ATT+bal (chosen epoch 3): fold 9: best epoch 5 (NOT the chosen epoch); fold 4: best epoch 2 (NOT the chosen epoch); mean over folds: best epoch 2
- M4 ATT+bal-2L (chosen epoch 1): fold 9: best epoch 4 (NOT the chosen epoch); fold 4: best epoch 2 (NOT the chosen epoch); mean over folds: best epoch 1

**Q2 validation loss after epoch 1** (mean over seeds, per fold; rises = the loss of every later epoch is above epoch 1)

- M1 Nebula: fold 9: 0.673 / 0.916 / 1.520 / 1.724 / 1.562 -> rises after epoch 1; fold 4: 0.851 / 0.763 / 1.003 / 1.092 / 1.589 -> minimum at epoch 2
- M2 two-level: fold 9: 0.363 / 0.530 / 0.607 / 0.774 / 0.984 -> rises after epoch 1; fold 4: 0.167 / 0.279 / 0.305 / 0.476 / 0.485 -> rises after epoch 1
- M3 ATT+bal: fold 9: 0.545 / 0.557 / 0.630 / 0.914 / 1.158 -> rises after epoch 1; fold 4: 0.398 / 0.349 / 0.400 / 0.462 / 0.580 -> minimum at epoch 2
- M4 ATT+bal-2L: fold 9: 0.307 / 0.398 / 0.496 / 0.616 / 0.740 -> rises after epoch 1; fold 4: 0.197 / 0.237 / 0.266 / 0.350 / 0.342 -> rises after epoch 1
- cell flatten, no padding (fold 9): 0.602 / 0.987 / 1.050 / 1.214 / 1.529 -> rises after epoch 1
- cell attention, no padding (fold 9): 0.371 / 0.402 / 0.493 / 0.710 / 0.837 -> rises after epoch 1
- cell flatten, balanced padding (fold 9): 0.585 / 1.298 / 1.059 / 1.294 / 1.401 -> rises after epoch 1
- cell attention, balanced padding (fold 9): 0.545 / 0.557 / 0.630 / 0.914 / 1.158 -> rises after epoch 1

**Q3 robustness over epochs of the padded models** (epoch 1 -> epoch 5; detection under LightGBM 50 prepend / random 50 prepend in points, padded-benign FPR at epoch 5, validation pAUC change)

- M3 ATT+bal, fold 9: LightGBM 50: 6.7 -> 4.9 (by epoch: 6.7, 4.9, 6.5, 6.8, 4.9); random 50: 20.8 -> 21.8 (by epoch: 20.8, 18.5, 22.8, 23.9, 21.8); padded-benign FPR epoch 1 / 5: 0.16 / 0.30; val pAUC 0.459 -> 0.474 (by epoch: 0.459, 0.471, 0.466, 0.470, 0.474)
- M3 ATT+bal, fold 4: LightGBM 50: 16.5 -> 5.9 (by epoch: 16.5, 11.5, 5.7, 6.7, 5.9); random 50: 27.2 -> 20.7 (by epoch: 27.2, 30.0, 21.7, 22.4, 20.7); padded-benign FPR epoch 1 / 5: 0.18 / 0.11; val pAUC 0.651 -> 0.608 (by epoch: 0.651, 0.670, 0.618, 0.621, 0.608)
- M4 ATT+bal-2L, fold 9: LightGBM 50: 19.1 -> 16.9 (by epoch: 19.1, 18.1, 11.4, 14.7, 16.9); random 50: 29.9 -> 31.1 (by epoch: 29.9, 33.7, 20.5, 27.8, 31.1); padded-benign FPR epoch 1 / 5: 0.39 / 0.35; val pAUC 0.444 -> 0.392 (by epoch: 0.444, 0.403, 0.245, 0.467, 0.392)
- M4 ATT+bal-2L, fold 4: LightGBM 50: 34.3 -> 47.4 (by epoch: 34.3, 56.0, 53.5, 34.5, 47.4); random 50: 63.7 -> 66.3 (by epoch: 63.7, 76.3, 75.9, 56.4, 66.3); padded-benign FPR epoch 1 / 5: 0.58 / 0.69; val pAUC 0.654 -> 0.605 (by epoch: 0.654, 0.666, 0.654, 0.556, 0.605)
- cell flatten, balanced, fold 9: LightGBM 50: 2.6 -> 0.0 (by epoch: 2.6, 0.0, 0.0, 0.0, 0.0); random 50: 13.3 -> 14.0 (by epoch: 13.3, 12.3, 15.0, 18.8, 14.0); padded-benign FPR epoch 1 / 5: 0.07 / 0.08; val pAUC 0.423 -> 0.427 (by epoch: 0.423, 0.455, 0.442, 0.428, 0.427)
- cell attention, balanced, fold 9: LightGBM 50: 6.7 -> 4.9 (by epoch: 6.7, 4.9, 6.5, 6.8, 4.9); random 50: 20.8 -> 21.8 (by epoch: 20.8, 18.5, 22.8, 23.9, 21.8); padded-benign FPR epoch 1 / 5: 0.16 / 0.30; val pAUC 0.459 -> 0.474 (by epoch: 0.459, 0.471, 0.466, 0.470, 0.474)
- M1 (no padding, for reference), fold 9: LightGBM 50: 4.4 -> 2.1 (by epoch: 4.4, 1.5, 0.7, 2.5, 2.1); random 50: 11.1 -> 7.8 (by epoch: 11.1, 8.7, 8.5, 6.7, 7.8); padded-benign FPR epoch 1 / 5: 0.44 / 0.18; val pAUC 0.519 -> 0.485 (by epoch: 0.519, 0.477, 0.498, 0.493, 0.485)
- M1 (no padding, for reference), fold 4: LightGBM 50: 8.1 -> 1.2 (by epoch: 8.1, 2.5, 1.6, 0.7, 1.2); random 50: 14.9 -> 7.5 (by epoch: 14.9, 11.6, 10.3, 7.4, 7.5); padded-benign FPR epoch 1 / 5: 0.24 / 0.03; val pAUC 0.644 -> 0.588 (by epoch: 0.644, 0.627, 0.625, 0.629, 0.588)
- M2 (no padding, for reference), fold 9: LightGBM 50: 12.5 -> 11.6 (by epoch: 12.5, 15.6, 7.9, 7.1, 11.6); random 50: 11.0 -> 8.0 (by epoch: 11.0, 11.4, 8.0, 8.3, 8.0); padded-benign FPR epoch 1 / 5: 0.12 / 0.35; val pAUC 0.586 -> 0.468 (by epoch: 0.586, 0.540, 0.460, 0.348, 0.468)
- M2 (no padding, for reference), fold 4: LightGBM 50: 15.6 -> 0.0 (by epoch: 15.6, 33.6, 5.2, 1.4, 0.0); random 50: 18.3 -> 1.2 (by epoch: 18.3, 24.3, 8.0, 2.4, 1.2); padded-benign FPR epoch 1 / 5: 0.06 / 0.02; val pAUC 0.626 -> 0.422 (by epoch: 0.626, 0.591, 0.548, 0.394, 0.422)

**Q4 chosen epoch inside the one-SE band** (per fold: SE = SD over 5 seeds / sqrt(5) at the best epoch; across folds: SE of the two fold means)

- M1 Nebula (chosen 1): fold 9: band [1] -> inside; fold 4: band [1, 2, 4] -> inside; across folds: band [1, 2, 3, 4, 5] -> inside
- M2 two-level (chosen 1): fold 9: band [1] -> inside; fold 4: band [1] -> inside; across folds: band [1] -> inside
- M3 ATT+bal (chosen 3): fold 9: band [2, 4, 5] -> OUTSIDE; fold 4: band [2] -> OUTSIDE; across folds: band [1, 2, 3, 4, 5] -> inside
- M4 ATT+bal-2L (chosen 1): fold 9: band [1, 4] -> inside; fold 4: band [1, 2, 3] -> inside; across folds: band [1, 2, 3, 4, 5] -> inside
