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
