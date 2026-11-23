### Cluster-bootstrap 95% intervals of the m3e2 cells (value = mean over 10 seeds [2.5%, 97.5% interval of the seed mean]; cells = (hash_apis group, class), 1000 resamples, seed 0; thresholds recomputed on every resample)

**The cells of the Stage J report table (detection of April malware at the 1% clean-FPR threshold, %; last row padded-benign FPR %)**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.0 [68.6, 86.3] | 78.9 [68.6, 86.3] |
| random 20 prepend | 25.4 [16.9, 35.2] | 76.2 [65.4, 84.1] | 75.9 [64.8, 84.0] |
| random 50 prepend | 7.4 [4.3, 11.6] | 65.1 [52.3, 74.9] | 64.2 [51.7, 74.2] |
| random 60 prepend | 5.8 [3.1, 9.5] | 51.9 [38.8, 63.2] | 51.7 [38.5, 62.7] |
| random 75 prepend | 5.4 [2.9, 9.0] | 21.5 [13.6, 29.6] | 21.9 [13.9, 30.2] |
| random 100 prepend | 5.7 [3.0, 9.3] | 6.5 [3.4, 11.2] | 6.1 [3.3, 10.4] |
| random 20 insert | 55.2 [43.1, 65.5] | 74.5 [63.4, 82.5] | 74.3 [62.7, 82.5] |
| random 50 insert | 42.1 [30.5, 53.0] | 68.5 [56.0, 78.2] | 68.4 [55.8, 78.1] |
| random 200 insert | 18.9 [11.5, 28.0] | 44.3 [31.3, 56.1] | 46.5 [33.2, 58.1] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 35.1 [22.9, 48.2] | 38.8 [25.6, 52.4] |
| lgbm 50 insert | 25.4 [15.6, 35.9] | 54.7 [39.4, 67.3] | 55.9 [40.2, 68.8] |
| white-box 20 steps | 1.6 [0.7, 23.5] | 48.7 [34.8, 69.4] | 49.9 [34.8, 69.8] |
| white-box 50 steps | 0.6 [0.2, 23.1] | 2.5 [1.2, 37.9] | 1.9 [1.0, 35.4] |
| padded-benign FPR (%), random 50 prepend | 1.07 [0.23, 2.18] | 0.84 [0.50, 1.39] | 1.01 [0.63, 1.47] |

**Detection of April malware after the edit, 1% threshold (%)**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.0 [68.6, 86.3] | 78.9 [68.6, 86.3] |
| random 20 prepend | 25.4 [16.9, 35.2] | 76.2 [65.4, 84.1] | 75.9 [64.8, 84.0] |
| random 50 prepend | 7.4 [4.3, 11.6] | 65.1 [52.3, 74.9] | 64.2 [51.7, 74.2] |
| random 60 prepend | 5.8 [3.1, 9.5] | 51.9 [38.8, 63.2] | 51.7 [38.5, 62.7] |
| random 75 prepend | 5.4 [2.9, 9.0] | 21.5 [13.6, 29.6] | 21.9 [13.9, 30.2] |
| random 100 prepend | 5.7 [3.0, 9.3] | 6.5 [3.4, 11.2] | 6.1 [3.3, 10.4] |
| random 200 prepend | 5.7 [3.0, 9.2] | 6.4 [3.3, 11.0] | 6.1 [3.2, 10.4] |
| random 20 insert | 55.2 [43.1, 65.5] | 74.5 [63.4, 82.5] | 74.3 [62.7, 82.5] |
| random 50 insert | 42.1 [30.5, 53.0] | 68.5 [56.0, 78.2] | 68.4 [55.8, 78.1] |
| random 60 insert | 38.9 [27.3, 49.5] | 66.2 [53.0, 76.3] | 66.2 [53.1, 76.4] |
| random 75 insert | 35.4 [24.8, 46.0] | 61.9 [48.3, 72.8] | 62.3 [49.0, 73.3] |
| random 100 insert | 30.3 [20.0, 40.6] | 55.3 [40.9, 68.3] | 56.0 [41.5, 68.6] |
| random 200 insert | 18.9 [11.5, 28.0] | 44.3 [31.3, 56.1] | 46.5 [33.2, 58.1] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 35.1 [22.9, 48.2] | 38.8 [25.6, 52.4] |
| lgbm 50 insert | 25.4 [15.6, 35.9] | 54.7 [39.4, 67.3] | 55.9 [40.2, 68.8] |

**Padded-benign FPR after the same edit, 1% threshold (%)**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| unedited | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] | 1.00 [0.97, 0.99] |
| random 20 prepend | 1.29 [0.50, 2.15] | 1.12 [0.93, 1.42] | 1.15 [0.93, 1.42] |
| random 50 prepend | 1.07 [0.23, 2.18] | 0.84 [0.50, 1.39] | 1.01 [0.63, 1.47] |
| random 60 prepend | 1.16 [0.21, 2.41] | 0.59 [0.30, 1.09] | 0.76 [0.41, 1.20] |
| random 75 prepend | 1.61 [0.27, 3.25] | 0.40 [0.16, 0.74] | 0.61 [0.29, 0.99] |
| random 100 prepend | 1.39 [0.26, 2.78] | 0.30 [0.11, 0.62] | 0.54 [0.24, 0.85] |
| random 200 prepend | 1.43 [0.27, 2.86] | 0.29 [0.12, 0.58] | 0.53 [0.22, 0.87] |
| random 20 insert | 0.69 [0.30, 1.14] | 0.95 [0.71, 1.29] | 1.09 [0.83, 1.39] |
| random 50 insert | 0.55 [0.18, 1.05] | 0.68 [0.45, 0.99] | 0.81 [0.57, 1.12] |
| random 60 insert | 0.61 [0.20, 1.09] | 0.57 [0.40, 0.86] | 0.75 [0.54, 1.00] |
| random 75 insert | 0.69 [0.17, 1.26] | 0.46 [0.29, 0.67] | 0.63 [0.42, 0.86] |
| random 100 insert | 0.71 [0.17, 1.40] | 0.50 [0.31, 0.80] | 0.69 [0.44, 0.98] |
| random 200 insert | 0.84 [0.18, 1.65] | 0.44 [0.26, 0.73] | 0.63 [0.37, 0.93] |
| lgbm 50 prepend | 0.00 [0.00, 0.01] | 0.06 [0.02, 0.10] | 0.08 [0.04, 0.14] |
| lgbm 50 insert | 0.07 [0.03, 0.16] | 0.16 [0.09, 0.25] | 0.20 [0.12, 0.29] |

**Detection of April malware after the edit, 0.1% threshold (%)**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| unedited | 53.6 [39.6, 66.3] | 56.7 [41.7, 68.5] | 60.9 [45.4, 71.5] |
| random 20 prepend | 7.2 [3.9, 12.7] | 50.5 [33.7, 63.3] | 53.3 [35.5, 66.7] |
| random 50 prepend | 1.3 [0.7, 2.7] | 28.1 [15.9, 41.0] | 28.3 [14.9, 42.2] |
| random 60 prepend | 1.0 [0.5, 2.0] | 12.6 [6.1, 21.4] | 11.6 [5.3, 20.4] |
| random 75 prepend | 1.0 [0.5, 2.0] | 2.3 [0.9, 4.9] | 2.2 [0.8, 4.6] |
| random 100 prepend | 1.0 [0.5, 2.0] | 1.9 [0.7, 3.9] | 1.9 [0.7, 3.6] |
| random 200 prepend | 1.0 [0.5, 2.0] | 1.9 [0.7, 3.9] | 1.8 [0.7, 3.6] |
| random 20 insert | 26.8 [17.4, 38.9] | 43.8 [28.0, 57.7] | 45.6 [29.4, 59.5] |
| random 50 insert | 16.2 [9.7, 25.9] | 36.1 [21.0, 50.4] | 37.6 [22.2, 52.5] |
| random 60 insert | 14.1 [8.2, 23.0] | 34.4 [19.9, 48.3] | 36.1 [21.2, 50.7] |
| random 75 insert | 12.0 [6.9, 19.9] | 32.1 [18.6, 45.5] | 33.7 [19.3, 47.6] |
| random 100 insert | 9.4 [5.4, 16.1] | 29.4 [15.7, 42.7] | 30.8 [16.5, 44.0] |
| random 200 insert | 4.5 [2.3, 8.6] | 21.6 [10.3, 34.1] | 21.8 [10.4, 34.0] |
| lgbm 50 prepend | 0.3 [0.1, 0.9] | 3.7 [1.2, 9.0] | 3.3 [1.4, 8.2] |
| lgbm 50 insert | 7.7 [3.9, 14.0] | 26.5 [13.9, 40.4] | 27.6 [14.4, 41.8] |

**Padded-benign FPR after the same edit, 0.1% threshold (%)**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| unedited | 0.10 [0.07, 0.10] | 0.10 [0.08, 0.10] | 0.10 [0.08, 0.10] |
| random 20 prepend | 0.02 [0.00, 0.09] | 0.04 [0.01, 0.09] | 0.06 [0.02, 0.10] |
| random 50 prepend | 0.02 [0.00, 0.09] | 0.00 [0.00, 0.02] | 0.01 [0.00, 0.02] |
| random 60 prepend | 0.01 [0.00, 0.07] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.01] |
| random 75 prepend | 0.03 [0.00, 0.12] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] |
| random 100 prepend | 0.02 [0.00, 0.10] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| random 200 prepend | 0.02 [0.01, 0.10] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] |
| random 20 insert | 0.02 [0.01, 0.05] | 0.03 [0.01, 0.05] | 0.03 [0.01, 0.07] |
| random 50 insert | 0.01 [0.00, 0.03] | 0.01 [0.00, 0.02] | 0.01 [0.00, 0.03] |
| random 60 insert | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.02] |
| random 75 insert | 0.00 [0.00, 0.03] | 0.01 [0.00, 0.02] | 0.01 [0.00, 0.02] |
| random 100 insert | 0.00 [0.00, 0.03] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.02] |
| random 200 insert | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.01] |
| lgbm 50 prepend | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| lgbm 50 insert | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.02] |

**White-box greedy attack (1% threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| white-box 0 steps: still flagged (1%) | 75.2 [62.6, 83.6] | 75.6 [63.0, 84.8] | 75.2 [63.1, 84.6] |
| white-box 5 steps: still flagged (1%) | 12.5 [7.8, 31.4] | 66.2 [52.3, 79.2] | 65.1 [50.7, 78.7] |
| white-box 10 steps: still flagged (1%) | 5.9 [3.4, 26.1] | 63.1 [49.0, 77.7] | 62.7 [48.6, 77.6] |
| white-box 20 steps: still flagged (1%) | 1.6 [0.7, 23.5] | 48.7 [34.8, 69.4] | 49.9 [34.8, 69.8] |
| white-box 50 steps: still flagged (1%) | 0.6 [0.2, 23.1] | 2.5 [1.2, 37.9] | 1.9 [1.0, 35.4] |
| white-box 5 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.52 [0.16, 0.96] | 0.60 [0.15, 1.04] |
| white-box 10 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.48 [0.12, 0.93] | 0.54 [0.12, 0.99] |
| white-box 20 steps: padded-benign FPR (1%) | 0.30 [0.10, 0.46] | 0.42 [0.12, 0.78] | 0.30 [0.04, 0.62] |
| white-box 50 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.28 [0.05, 0.60] | 0.24 [0.02, 0.51] |

**White-box, the attack's own fixed threshold (1%): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| white-box 0 steps: still flagged (1%, fixed threshold) | 75.2 [64.4, 82.7] | 75.6 [64.3, 84.2] | 75.2 [63.5, 84.3] |
| white-box 5 steps: still flagged (1%, fixed threshold) | 12.5 [7.7, 18.2] | 66.2 [53.5, 76.3] | 65.1 [52.5, 75.5] |
| white-box 10 steps: still flagged (1%, fixed threshold) | 5.9 [3.2, 9.7] | 63.1 [50.2, 73.6] | 62.7 [49.3, 73.6] |
| white-box 20 steps: still flagged (1%, fixed threshold) | 1.6 [0.6, 3.2] | 48.7 [34.3, 60.7] | 49.9 [36.2, 61.8] |
| white-box 50 steps: still flagged (1%, fixed threshold) | 0.6 [0.2, 1.1] | 2.5 [1.1, 4.6] | 1.9 [0.8, 3.7] |
| white-box 5 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 0.52 [0.14, 1.08] | 0.60 [0.20, 1.18] |
| white-box 10 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 0.48 [0.11, 1.04] | 0.54 [0.20, 1.07] |
| white-box 20 steps: padded-benign FPR (1%, fixed threshold) | 0.30 [0.09, 0.63] | 0.42 [0.12, 0.86] | 0.30 [0.07, 0.68] |
| white-box 50 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 0.28 [0.06, 0.65] | 0.24 [0.05, 0.56] |

**White-box greedy attack (0.1% threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| white-box 0 steps: still flagged (0.1%) | 48.0 [34.3, 61.8] | 52.7 [37.6, 65.2] | 56.3 [40.3, 67.6] |
| white-box 5 steps: still flagged (0.1%) | 1.8 [0.6, 4.2] | 34.7 [20.3, 48.8] | 36.2 [21.3, 50.8] |
| white-box 10 steps: still flagged (0.1%) | 0.5 [0.1, 1.3] | 31.3 [17.3, 45.1] | 33.3 [18.2, 47.4] |
| white-box 20 steps: still flagged (0.1%) | 0.1 [0.0, 0.4] | 17.0 [7.8, 27.1] | 16.0 [7.4, 27.2] |
| white-box 50 steps: still flagged (0.1%) | 0.1 [0.0, 0.2] | 0.4 [0.1, 1.0] | 0.4 [0.1, 0.9] |
| white-box 5 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.14 [0.00, 0.41] | 0.08 [0.00, 0.23] |
| white-box 10 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.04 [0.00, 0.10] | 0.04 [0.00, 0.12] |
| white-box 20 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.04] |
| white-box 50 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

**White-box, the attack's own fixed threshold (0.1%): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**

| row | M1 Nebula | M3 (3 epochs) | M3 (2 epochs) |
|---|---|---|---|
| white-box 0 steps: still flagged (0.1%, fixed threshold) | 48.0 [37.8, 57.0] | 52.7 [39.5, 64.3] | 56.3 [42.5, 67.2] |
| white-box 5 steps: still flagged (0.1%, fixed threshold) | 1.8 [0.9, 3.2] | 34.7 [21.9, 48.5] | 36.2 [23.6, 49.2] |
| white-box 10 steps: still flagged (0.1%, fixed threshold) | 0.5 [0.2, 1.0] | 31.3 [19.3, 44.5] | 33.3 [21.0, 46.1] |
| white-box 20 steps: still flagged (0.1%, fixed threshold) | 0.1 [0.0, 0.2] | 17.0 [9.9, 25.2] | 16.0 [9.3, 24.2] |
| white-box 50 steps: still flagged (0.1%, fixed threshold) | 0.1 [0.0, 0.2] | 0.4 [0.1, 1.0] | 0.4 [0.1, 0.9] |
| white-box 5 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.14 [0.00, 0.46] | 0.08 [0.00, 0.26] |
| white-box 10 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.04 [0.00, 0.13] | 0.04 [0.00, 0.13] |
| white-box 20 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| white-box 50 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

