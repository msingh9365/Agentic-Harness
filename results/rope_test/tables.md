### Clean April (10 seeds; mean ± SD over seeds)

| variant | pAUC@1e-2 | TPR@1e-3 | TPR@1e-2 | AUC | F1 at logit 0 | pAUC@1e-2 seen / unseen (n) |
|---|---|---|---|---|---|---|
| M3 ATT+bal | 0.705 ± 0.025 | 0.567 | 0.790 | 0.9693 | 0.9128 | 0.824 (6329) / 0.650 (11073) |
| M3 + RoPE (blocks) | 0.691 ± 0.013 | 0.565 | 0.766 | 0.9672 | 0.9047 | 0.835 (6329) / 0.627 (11073) |
| M3 + RoPE (full) | 0.698 ± 0.014 | 0.584 | 0.766 | 0.9634 | 0.8968 | 0.837 (6329) / 0.633 (11073) |
| M3 + full attention | 0.710 ± 0.012 | 0.607 | 0.779 | 0.9656 | 0.9030 | 0.862 (6329) / 0.636 (11073) |

### Shuffle test: drop of pAUC@1e-2 (clean minus variant, points), cluster 95% interval, seeds down / up

| variant | window shuffle | local shuffle (5) | reversal | full shuffle (reference) | mean abs logit change under window shuffle, malware / benign (SD of clean logits) |
|---|---|---|---|---|---|
| M3 ATT+bal | +4.03 [+1.83, +6.67] 10/0 | +0.43 [-0.09, +0.96] 9/1 | +1.96 [-1.10, +5.57] 9/1 | +13.33 [+7.21, +19.87] 10/0 | 2.03 / 2.35 (9.5 / 6.0) |
| M3 + RoPE (blocks) | +5.42 [+2.74, +9.31] 10/0 | +0.32 [-0.37, +0.96] 5/5 | -0.54 [-2.04, +0.73] 1/9 | +13.54 [+6.80, +20.23] 10/0 | 2.47 / 1.35 (9.9 / 4.7) |
| M3 + RoPE (full) | +3.19 [+1.40, +5.31] 10/0 | +0.46 [-0.10, +0.98] 7/3 | +0.48 [-1.03, +1.86] 7/3 | +18.74 [+11.56, +25.14] 10/0 | 1.15 / 0.93 (8.6 / 4.6) |
| M3 + full attention | +1.25 [-0.85, +3.40] 10/0 | +0.30 [-0.20, +0.83] 7/3 | +1.73 [-1.86, +5.22] 9/1 | +11.87 [+6.42, +17.15] 10/0 | 1.29 / 1.90 (8.6 / 6.0) |

### Shift test: pAUC@1e-2 at the shifts (mean ± SD over seeds) and the drop against shift 0 (points; cluster 95% interval)

| variant | s 0 | s 8 | s 16 | s 24 | s 32 | s 40 | s 48 | s 56 | s 64 | largest drop (at s) |
|---|---|---|---|---|---|---|---|---|---|---|
| M3 ATT+bal | 0.705 | 0.684 | 0.686 | 0.692 | 0.685 | 0.684 | 0.695 | 0.692 | 0.698 | +2.10 [+0.33, +4.27] (s 8) |
| M3 + RoPE (blocks) | 0.691 | 0.679 | 0.676 | 0.674 | 0.663 | 0.658 | 0.674 | 0.680 | 0.693 | +3.30 [+0.60, +6.58] (s 40) |
| M3 + RoPE (full) | 0.698 | 0.690 | 0.686 | 0.684 | 0.682 | 0.676 | 0.672 | 0.669 | 0.672 | +2.80 [+0.67, +5.35] (s 56) |
| M3 + full attention | 0.710 | 0.679 | 0.682 | 0.679 | 0.675 | 0.672 | 0.667 | 0.667 | 0.658 | +5.19 [+2.93, +8.05] (s 64) |

Detection of malware at the clean 1% threshold per shift (%):

| variant | s 0 | s 8 | s 16 | s 24 | s 32 | s 40 | s 48 | s 56 | s 64 |
|---|---|---|---|---|---|---|---|---|---|
| M3 ATT+bal | 79.0 | 78.2 | 78.6 | 78.9 | 77.6 | 77.4 | 77.4 | 77.4 | 77.3 |
| M3 + RoPE (blocks) | 76.6 | 76.4 | 75.8 | 75.2 | 75.1 | 75.2 | 76.4 | 76.3 | 76.3 |
| M3 + RoPE (full) | 76.6 | 76.1 | 75.5 | 75.1 | 74.9 | 74.3 | 73.8 | 73.4 | 73.1 |
| M3 + full attention | 77.9 | 77.1 | 77.1 | 76.0 | 75.5 | 75.2 | 74.8 | 74.5 | 73.4 |

### Padding attacks: detection of April malware at the clean 1% FPR threshold (%, mean ± SD over 10 seeds); last block: padded-benign false-alarm rate (%)

| edit set | M3 ATT+bal | M3 + RoPE (blocks) | M3 + RoPE (full) | M3 + full attention |
|---|---|---|---|---|
| unedited | 79.0 ± 1.9 | 76.6 ± 1.9 | 76.6 ± 1.3 | 77.9 ± 1.2 |
| random 5 prepend | 79.0 ± 2.0 | 75.9 ± 1.6 | 75.8 ± 1.0 | 76.4 ± 1.9 |
| random 20 prepend | 76.2 ± 2.3 | 75.3 ± 2.0 | 72.5 ± 1.2 | 72.1 ± 1.4 |
| random 50 prepend | 65.1 ± 5.8 | 67.5 ± 2.9 | 52.1 ± 5.0 | 57.7 ± 3.5 |
| random 100 prepend | 6.5 ± 1.3 | 7.7 ± 1.9 | 1.6 ± 0.7 | 6.9 ± 0.2 |
| random 200 prepend | 6.4 ± 1.2 | 7.6 ± 1.9 | 1.6 ± 0.7 | 6.9 ± 0.2 |
| random 5 insert | 77.5 ± 2.1 | 75.9 ± 1.9 | 75.6 ± 1.2 | 76.0 ± 1.6 |
| random 20 insert | 74.5 ± 2.1 | 73.6 ± 2.2 | 72.2 ± 1.8 | 71.0 ± 2.6 |
| random 50 insert | 68.5 ± 2.8 | 68.1 ± 3.8 | 64.3 ± 2.6 | 64.6 ± 2.5 |
| random 100 insert | 55.3 ± 3.6 | 60.1 ± 5.3 | 50.2 ± 2.4 | 53.5 ± 2.5 |
| random 200 insert | 44.3 ± 4.0 | 50.8 ± 4.3 | 38.6 ± 2.7 | 42.5 ± 3.0 |
| lgbm 20 prepend | 73.2 ± 2.5 | 72.7 ± 2.9 | 64.5 ± 3.2 | 64.0 ± 3.3 |
| lgbm 50 prepend | 35.1 ± 13.3 | 46.0 ± 7.5 | 2.4 ± 3.0 | 10.0 ± 3.6 |
| lgbm 100 prepend | 5.8 ± 1.7 | 5.7 ± 0.6 | 0.2 ± 0.7 | 5.8 ± 1.4 |
| lgbm 20 insert | 70.6 ± 1.7 | 69.7 ± 3.0 | 64.7 ± 2.6 | 66.0 ± 3.6 |
| lgbm 50 insert | 54.7 ± 2.9 | 56.5 ± 2.6 | 43.7 ± 2.5 | 49.8 ± 3.9 |
| lgbm 100 insert | 36.8 ± 3.4 | 45.3 ± 2.6 | 30.1 ± 4.4 | 33.4 ± 5.9 |

Padded-benign FPR (%) at the same threshold:

| edit set | M3 ATT+bal | M3 + RoPE (blocks) | M3 + RoPE (full) | M3 + full attention |
|---|---|---|---|---|
| random 5 prepend | 1.03 | 1.18 | 0.98 | 1.06 |
| random 20 prepend | 1.12 | 1.19 | 0.95 | 1.08 |
| random 50 prepend | 0.84 | 0.91 | 0.36 | 0.63 |
| random 100 prepend | 0.30 | 1.11 | 0.03 | 0.10 |
| random 200 prepend | 0.29 | 1.06 | 0.02 | 0.09 |
| random 5 insert | 1.08 | 1.19 | 1.05 | 1.10 |
| random 20 insert | 0.95 | 1.19 | 0.95 | 1.00 |
| random 50 insert | 0.68 | 1.04 | 0.48 | 0.61 |
| random 100 insert | 0.50 | 1.01 | 0.28 | 0.34 |
| random 200 insert | 0.44 | 1.08 | 0.24 | 0.23 |
| lgbm 20 prepend | 0.67 | 0.53 | 0.18 | 0.18 |
| lgbm 50 prepend | 0.06 | 0.08 | 0.00 | 0.00 |
| lgbm 100 prepend | 0.00 | 0.00 | 0.00 | 0.00 |
| lgbm 20 insert | 0.39 | 0.41 | 0.29 | 0.29 |
| lgbm 50 insert | 0.16 | 0.23 | 0.10 | 0.09 |
| lgbm 100 insert | 0.08 | 0.15 | 0.03 | 0.03 |

### White-box greedy search (500 April malware, 50 steps, seeds 0 to 2): share still flagged at the clean 1% threshold (%)

| variant | seeds | step 0 | 5 | 10 | 20 | 50 |
|---|---|---|---|---|---|---|
| M3 ATT+bal | 3 | 75.2 | 64.9 | 62.4 | 43.2 | 1.3 |
| M3 + RoPE (blocks) | 3 | 73.6 | 65.4 | 62.1 | 47.3 | 1.9 |
| M3 + RoPE (full) | 3 | 71.7 | 53.1 | 32.3 | 9.7 | 0.0 |

### Contrasts (point, cluster 95% interval, seeds up / down; RESOLVED = interval excludes 0)

| contrast | clean pAUC@1e-2 | window-shuffle drop | largest shift drop (s 8 / 64 shown) | detection under LightGBM 50 prepend |
|---|---|---|---|---|
| v1-v0 | -1.35 [-4.29, +1.09] 1/9 | +1.39 [-1.51, +4.36] 8/2 | s8: -0.90 [-2.83, +0.81] 1/9; s64: -0.85 [-2.60, +0.84] 3/7 | +10.89 [+1.32, +19.31] 8/2 RESOLVED |
| v2-v0 | -0.73 [-3.67, +2.25] 4/6 | -0.85 [-3.66, +1.88] 4/6 | s8: -1.33 [-3.03, +0.19] 1/9; s64: +1.87 [-0.14, +3.94] 10/0 | -32.69 [-45.67, -21.48] 0/10 RESOLVED |
| v3-v0 | +0.54 [-1.98, +3.10] 7/3 | -2.79 [-4.65, -1.24] 0/10 RESOLVED | s8: +1.03 [-0.52, +2.80] 7/3; s64: +4.49 [+1.87, +7.63] 10/0 RESOLVED | -25.12 [-36.89, -12.89] 0/10 RESOLVED |
| v2-v3 | -1.27 [-4.56, +2.06] 3/7 | +1.94 [-0.91, +5.32] 8/2 | s8: -2.36 [-4.35, -0.98] 0/10 RESOLVED; s64: -2.62 [-5.00, -0.78] 1/9 RESOLVED | -7.57 [-14.24, -3.74] 1/9 RESOLVED |

### Decision rule (NOTES_ROPE section 5)

| variant | (i) window-shuffle drop >= 5 points and resolved | (ii) largest shift drop <= 2 points, not resolved | (iii) LightGBM-50-prepend detection not resolved worse than M3 | (iv) clean pAUC not resolved worse than M3 | order-aware and position-robust |
|---|---|---|---|---|---|
| M3 + RoPE (blocks) | met (+5.42; [+2.74, +9.31]) | NOT met (+3.30 at s 40; [+0.60, +6.58]) | met (+10.89; [+1.32, +19.31]) | met (-1.35; [-4.29, +1.09]) | **no** |
| M3 + RoPE (full) | NOT met (+3.19; [+1.40, +5.31]) | NOT met (+2.80 at s 56; [+0.67, +5.35]) | NOT met (-32.69; [-45.67, -21.48]) | met (-0.73; [-3.67, +2.25]) | **no** |
| M3 + full attention | NOT met (+1.25; [-0.85, +3.40]) | NOT met (+5.19 at s 64; [+2.93, +8.05]) | NOT met (-25.12; [-36.89, -12.89]) | met (+0.54; [-1.98, +3.10]) | **no** |

Reference M3 (V0): window-shuffle drop +4.03 points [+1.83, +6.67]; largest shift drop +2.10 points.
