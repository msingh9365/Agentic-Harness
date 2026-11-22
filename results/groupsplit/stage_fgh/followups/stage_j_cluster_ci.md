### Cluster-bootstrap 95% intervals of the stage_j cells (value = mean over 10 seeds [2.5%, 97.5% interval of the seed mean]; cells = (hash_apis group, class), 1000 resamples, seed 0; thresholds recomputed on every resample)

**The cells of the Stage J report table (detection of April malware at the 1% clean-FPR threshold, %; last row padded-benign FPR %)**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 77.2 [66.3, 84.1] | 79.0 [68.6, 86.3] | 77.9 [68.0, 85.2] |
| random 20 prepend | 25.4 [16.9, 35.2] | 54.2 [39.5, 66.0] | 76.2 [65.4, 84.1] | 74.4 [62.9, 82.7] |
| random 50 prepend | 7.4 [4.3, 11.6] | 28.5 [14.3, 46.2] | 65.1 [52.3, 74.9] | 67.2 [55.1, 76.4] |
| random 100 prepend | 5.7 [3.0, 9.3] | 17.1 [6.3, 34.3] | 6.5 [3.4, 11.2] | 25.9 [15.4, 37.9] |
| random 200 insert | 18.9 [11.5, 28.0] | 12.4 [5.1, 22.3] | 44.3 [31.3, 56.1] | 37.5 [25.4, 49.7] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 17.2 [5.7, 35.7] | 35.1 [22.9, 48.2] | 48.5 [34.5, 60.9] |
| white-box 20 steps | 1.6 [0.7, 23.5] | 19.6 [10.9, 58.2] | 48.7 [34.8, 69.4] | 50.2 [35.0, 70.6] |
| white-box 50 steps | 0.6 [0.2, 23.1] | 13.8 [7.2, 57.5] | 2.5 [1.2, 37.9] | 10.6 [6.0, 47.9] |
| padded-benign FPR (%), random 50 prepend | 1.07 [0.23, 2.18] | 0.05 [0.01, 0.13] | 0.84 [0.50, 1.39] | 0.49 [0.38, 0.63] |

**Detection of April malware after the edit, 1% threshold (%)**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 77.2 [66.3, 84.1] | 79.0 [68.6, 86.3] | 77.9 [68.0, 85.2] |
| random 5 prepend | 54.8 [42.0, 64.9] | 64.0 [51.0, 73.9] | 79.0 [68.7, 85.7] | 77.6 [67.1, 85.0] |
| random 20 prepend | 25.4 [16.9, 35.2] | 54.2 [39.5, 66.0] | 76.2 [65.4, 84.1] | 74.4 [62.9, 82.7] |
| random 50 prepend | 7.4 [4.3, 11.6] | 28.5 [14.3, 46.2] | 65.1 [52.3, 74.9] | 67.2 [55.1, 76.4] |
| random 100 prepend | 5.7 [3.0, 9.3] | 17.1 [6.3, 34.3] | 6.5 [3.4, 11.2] | 25.9 [15.4, 37.9] |
| random 200 prepend | 5.7 [3.0, 9.2] | 7.8 [2.9, 20.8] | 6.4 [3.3, 11.0] | 8.2 [3.9, 14.8] |
| random 5 insert | 71.4 [60.3, 78.7] | 66.4 [53.9, 75.4] | 77.5 [67.2, 85.0] | 76.8 [66.1, 84.2] |
| random 20 insert | 55.2 [43.1, 65.5] | 55.0 [40.9, 66.6] | 74.5 [63.4, 82.5] | 72.5 [60.6, 81.1] |
| random 50 insert | 42.1 [30.5, 53.0] | 43.2 [28.5, 55.4] | 68.5 [56.0, 78.2] | 65.0 [52.2, 75.2] |
| random 100 insert | 30.3 [20.0, 40.6] | 29.5 [15.8, 42.0] | 55.3 [40.9, 68.3] | 52.4 [39.0, 65.1] |
| random 200 insert | 18.9 [11.5, 28.0] | 12.4 [5.1, 22.3] | 44.3 [31.3, 56.1] | 37.5 [25.4, 49.7] |
| lgbm 20 prepend | 8.8 [4.6, 14.0] | 46.6 [30.2, 60.3] | 73.2 [61.0, 81.8] | 73.4 [61.5, 81.8] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 17.2 [5.7, 35.7] | 35.1 [22.9, 48.2] | 48.5 [34.5, 60.9] |
| lgbm 100 prepend | 2.0 [0.9, 3.4] | 14.2 [4.4, 30.6] | 5.8 [2.8, 10.1] | 20.0 [11.8, 28.2] |
| lgbm 20 insert | 43.8 [31.9, 54.8] | 41.3 [27.5, 53.8] | 70.6 [58.5, 80.0] | 62.5 [49.4, 73.7] |
| lgbm 50 insert | 25.4 [15.6, 35.9] | 25.3 [12.5, 38.2] | 54.7 [39.4, 67.3] | 47.5 [34.6, 59.6] |
| lgbm 100 insert | 13.9 [7.7, 22.4] | 13.4 [5.2, 24.2] | 36.8 [23.1, 49.6] | 36.6 [23.4, 49.9] |

**Padded-benign FPR after the same edit, 1% threshold (%)**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] |
| random 5 prepend | 0.91 [0.53, 1.50] | 0.49 [0.27, 0.73] | 1.03 [0.90, 1.25] | 1.03 [0.83, 1.29] |
| random 20 prepend | 1.29 [0.50, 2.15] | 0.22 [0.09, 0.41] | 1.12 [0.93, 1.42] | 0.94 [0.73, 1.16] |
| random 50 prepend | 1.07 [0.23, 2.18] | 0.05 [0.01, 0.13] | 0.84 [0.50, 1.39] | 0.49 [0.38, 0.63] |
| random 100 prepend | 1.39 [0.26, 2.78] | 0.03 [0.00, 0.09] | 0.30 [0.11, 0.62] | 0.04 [0.01, 0.07] |
| random 200 prepend | 1.43 [0.27, 2.86] | 0.01 [0.00, 0.03] | 0.29 [0.12, 0.58] | 0.00 [0.00, 0.01] |
| random 5 insert | 0.87 [0.54, 1.22] | 0.46 [0.27, 0.67] | 1.08 [0.89, 1.33] | 0.87 [0.74, 1.08] |
| random 20 insert | 0.69 [0.30, 1.14] | 0.21 [0.08, 0.37] | 0.95 [0.71, 1.29] | 0.73 [0.57, 0.94] |
| random 50 insert | 0.55 [0.18, 1.05] | 0.07 [0.02, 0.17] | 0.68 [0.45, 0.99] | 0.45 [0.31, 0.64] |
| random 100 insert | 0.71 [0.17, 1.40] | 0.02 [0.00, 0.08] | 0.50 [0.31, 0.80] | 0.09 [0.04, 0.15] |
| random 200 insert | 0.84 [0.18, 1.65] | 0.00 [0.00, 0.02] | 0.44 [0.26, 0.73] | 0.02 [0.00, 0.06] |
| lgbm 20 prepend | 0.00 [0.00, 0.01] | 0.08 [0.03, 0.36] | 0.67 [0.55, 0.99] | 0.51 [0.42, 0.65] |
| lgbm 50 prepend | 0.00 [0.00, 0.01] | 0.04 [0.01, 0.10] | 0.06 [0.02, 0.10] | 0.06 [0.03, 0.11] |
| lgbm 100 prepend | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.05] | 0.00 [0.00, 0.00] | 0.02 [0.00, 0.04] |
| lgbm 20 insert | 0.15 [0.07, 0.26] | 0.04 [0.01, 0.18] | 0.39 [0.27, 0.51] | 0.23 [0.15, 0.32] |
| lgbm 50 insert | 0.07 [0.03, 0.16] | 0.01 [0.00, 0.04] | 0.16 [0.09, 0.25] | 0.04 [0.01, 0.08] |
| lgbm 100 insert | 0.02 [0.00, 0.09] | 0.02 [0.00, 0.08] | 0.08 [0.04, 0.13] | 0.03 [0.00, 0.08] |

**Detection of April malware after the edit, 0.1% threshold (%)**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 53.6 [39.6, 66.3] | 38.1 [26.2, 51.3] | 56.7 [41.7, 68.5] | 45.3 [28.5, 58.3] |
| random 5 prepend | 24.7 [16.1, 36.8] | 26.5 [16.1, 39.6] | 50.8 [35.1, 64.2] | 46.3 [28.0, 58.8] |
| random 20 prepend | 7.2 [3.9, 12.7] | 17.4 [9.4, 28.4] | 50.5 [33.7, 63.3] | 44.2 [26.3, 57.2] |
| random 50 prepend | 1.3 [0.7, 2.7] | 1.1 [0.5, 3.0] | 28.1 [15.9, 41.0] | 38.1 [22.5, 50.1] |
| random 100 prepend | 1.0 [0.5, 2.0] | 0.1 [0.0, 1.0] | 1.9 [0.7, 3.9] | 5.2 [2.8, 8.6] |
| random 200 prepend | 1.0 [0.5, 2.0] | 0.0 [0.0, 0.0] | 1.9 [0.7, 3.9] | 0.3 [0.1, 0.9] |
| random 5 insert | 41.6 [29.5, 54.7] | 27.6 [17.1, 40.2] | 51.5 [35.9, 63.8] | 44.4 [26.7, 56.6] |
| random 20 insert | 26.8 [17.4, 38.9] | 19.9 [11.0, 31.1] | 43.8 [28.0, 57.7] | 40.4 [22.6, 53.4] |
| random 50 insert | 16.2 [9.7, 25.9] | 10.4 [5.4, 17.7] | 36.1 [21.0, 50.4] | 34.8 [18.5, 47.5] |
| random 100 insert | 9.4 [5.4, 16.1] | 3.3 [1.4, 7.6] | 29.4 [15.7, 42.7] | 21.5 [11.1, 31.6] |
| random 200 insert | 4.5 [2.3, 8.6] | 0.4 [0.1, 1.5] | 21.6 [10.3, 34.1] | 10.6 [4.2, 16.6] |
| lgbm 20 prepend | 1.2 [0.5, 2.7] | 8.0 [3.1, 14.9] | 44.9 [28.3, 60.0] | 45.7 [27.7, 57.1] |
| lgbm 50 prepend | 0.3 [0.1, 0.9] | 0.1 [0.0, 0.4] | 3.7 [1.2, 9.0] | 21.6 [10.2, 34.0] |
| lgbm 100 prepend | 0.2 [0.1, 0.7] | 0.0 [0.0, 0.7] | 1.2 [0.4, 3.0] | 3.9 [1.5, 7.5] |
| lgbm 20 insert | 16.3 [9.5, 26.5] | 10.2 [5.2, 18.1] | 38.4 [23.0, 53.2] | 33.3 [18.0, 45.1] |
| lgbm 50 insert | 7.7 [3.9, 14.0] | 2.9 [0.9, 7.0] | 26.5 [13.9, 40.4] | 21.5 [9.8, 32.6] |
| lgbm 100 insert | 3.6 [1.6, 7.2] | 0.5 [0.1, 1.7] | 18.2 [8.2, 29.3] | 10.6 [3.6, 17.6] |

**Padded-benign FPR after the same edit, 0.1% threshold (%)**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 0.10 [0.07, 0.10] | 0.10 [0.07, 0.10] | 0.10 [0.08, 0.10] | 0.10 [0.07, 0.10] |
| random 5 prepend | 0.03 [0.02, 0.07] | 0.01 [0.00, 0.02] | 0.07 [0.04, 0.10] | 0.08 [0.04, 0.11] |
| random 20 prepend | 0.02 [0.00, 0.09] | 0.00 [0.00, 0.01] | 0.04 [0.01, 0.09] | 0.07 [0.03, 0.12] |
| random 50 prepend | 0.02 [0.00, 0.09] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.02] | 0.03 [0.01, 0.06] |
| random 100 prepend | 0.02 [0.00, 0.10] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| random 200 prepend | 0.02 [0.01, 0.10] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| random 5 insert | 0.03 [0.01, 0.07] | 0.01 [0.00, 0.03] | 0.06 [0.03, 0.10] | 0.07 [0.04, 0.10] |
| random 20 insert | 0.02 [0.01, 0.05] | 0.00 [0.00, 0.01] | 0.03 [0.01, 0.05] | 0.05 [0.02, 0.10] |
| random 50 insert | 0.01 [0.00, 0.03] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.02 [0.00, 0.07] |
| random 100 insert | 0.00 [0.00, 0.03] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] | 0.01 [0.00, 0.02] |
| random 200 insert | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.01] |
| lgbm 20 prepend | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] | 0.02 [0.00, 0.06] | 0.06 [0.02, 0.12] |
| lgbm 50 prepend | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| lgbm 100 prepend | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| lgbm 20 insert | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.02 [0.00, 0.06] |
| lgbm 50 insert | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.01] |
| lgbm 100 insert | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] |

**White-box greedy attack (1% threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| white-box 0 steps: still flagged (1%) | 75.2 [62.6, 83.6] | 74.4 [61.2, 82.8] | 75.6 [63.0, 84.8] | 74.6 [62.8, 84.0] |
| white-box 5 steps: still flagged (1%) | 12.5 [7.8, 31.4] | 44.1 [30.7, 64.4] | 66.2 [52.3, 79.2] | 61.3 [46.7, 76.8] |
| white-box 10 steps: still flagged (1%) | 5.9 [3.4, 26.1] | 35.9 [23.2, 62.1] | 63.1 [49.0, 77.7] | 58.3 [43.4, 75.6] |
| white-box 20 steps: still flagged (1%) | 1.6 [0.7, 23.5] | 19.6 [10.9, 58.2] | 48.7 [34.8, 69.4] | 50.2 [35.0, 70.6] |
| white-box 50 steps: still flagged (1%) | 0.6 [0.2, 23.1] | 13.8 [7.2, 57.5] | 2.5 [1.2, 37.9] | 10.6 [6.0, 47.9] |
| white-box 5 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.92 [0.52, 1.32] | 0.52 [0.16, 0.96] | 0.74 [0.28, 1.22] |
| white-box 10 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 1.56 [0.94, 2.31] | 0.48 [0.12, 0.93] | 1.00 [0.53, 1.51] |
| white-box 20 steps: padded-benign FPR (1%) | 0.30 [0.10, 0.46] | 2.18 [1.45, 3.14] | 0.42 [0.12, 0.78] | 0.94 [0.54, 1.36] |
| white-box 50 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 3.16 [1.62, 5.56] | 0.28 [0.05, 0.60] | 0.42 [0.16, 0.66] |

**White-box, the attack's own fixed threshold (1%): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| white-box 0 steps: still flagged (1%, fixed threshold) | 75.2 [64.4, 82.7] | 74.4 [64.2, 81.9] | 75.6 [64.3, 84.2] | 74.6 [63.0, 82.8] |
| white-box 5 steps: still flagged (1%, fixed threshold) | 12.5 [7.7, 18.2] | 44.1 [32.2, 55.0] | 66.2 [53.5, 76.3] | 61.3 [46.4, 73.1] |
| white-box 10 steps: still flagged (1%, fixed threshold) | 5.9 [3.2, 9.7] | 35.9 [24.6, 47.3] | 63.1 [50.2, 73.6] | 58.3 [42.8, 71.2] |
| white-box 20 steps: still flagged (1%, fixed threshold) | 1.6 [0.6, 3.2] | 19.6 [12.0, 28.0] | 48.7 [34.3, 60.7] | 50.2 [35.2, 62.5] |
| white-box 50 steps: still flagged (1%, fixed threshold) | 0.6 [0.2, 1.1] | 13.8 [7.9, 20.4] | 2.5 [1.1, 4.6] | 10.6 [6.4, 15.8] |
| white-box 5 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 0.92 [0.44, 1.59] | 0.52 [0.14, 1.08] | 0.74 [0.28, 1.31] |
| white-box 10 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 1.56 [0.92, 2.43] | 0.48 [0.11, 1.04] | 1.00 [0.52, 1.67] |
| white-box 20 steps: padded-benign FPR (1%, fixed threshold) | 0.30 [0.09, 0.63] | 2.18 [1.36, 3.20] | 0.42 [0.12, 0.86] | 0.94 [0.57, 1.44] |
| white-box 50 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 3.16 [2.35, 4.12] | 0.28 [0.06, 0.65] | 0.42 [0.19, 0.73] |

**White-box greedy attack (0.1% threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| white-box 0 steps: still flagged (0.1%) | 48.0 [34.3, 61.8] | 35.5 [22.6, 48.2] | 52.7 [37.6, 65.2] | 41.8 [24.7, 55.6] |
| white-box 5 steps: still flagged (0.1%) | 1.8 [0.6, 4.2] | 11.7 [5.0, 21.2] | 34.7 [20.3, 48.8] | 30.8 [14.8, 42.2] |
| white-box 10 steps: still flagged (0.1%) | 0.5 [0.1, 1.3] | 6.3 [2.2, 13.2] | 31.3 [17.3, 45.1] | 27.0 [11.8, 38.1] |
| white-box 20 steps: still flagged (0.1%) | 0.1 [0.0, 0.4] | 1.7 [0.5, 4.6] | 17.0 [7.8, 27.1] | 17.4 [6.6, 27.7] |
| white-box 50 steps: still flagged (0.1%) | 0.1 [0.0, 0.2] | 0.2 [0.0, 2.5] | 0.4 [0.1, 1.0] | 1.5 [0.4, 3.0] |
| white-box 5 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.08 [0.00, 0.24] | 0.14 [0.00, 0.41] | 0.12 [0.00, 0.27] |
| white-box 10 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.14 [0.06, 0.42] | 0.04 [0.00, 0.10] | 0.08 [0.00, 0.18] |
| white-box 20 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.36 [0.12, 0.93] | 0.00 [0.00, 0.00] | 0.14 [0.02, 0.27] |
| white-box 50 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.42 [0.19, 0.76] | 0.00 [0.00, 0.00] | 0.02 [0.00, 0.07] |

**White-box, the attack's own fixed threshold (0.1%): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**

| row | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| white-box 0 steps: still flagged (0.1%, fixed threshold) | 48.0 [37.8, 57.0] | 35.5 [25.6, 44.8] | 52.7 [39.5, 64.3] | 41.8 [31.8, 51.0] |
| white-box 5 steps: still flagged (0.1%, fixed threshold) | 1.8 [0.9, 3.2] | 11.7 [5.8, 18.5] | 34.7 [21.9, 48.5] | 30.8 [19.8, 41.1] |
| white-box 10 steps: still flagged (0.1%, fixed threshold) | 0.5 [0.2, 1.0] | 6.3 [3.0, 10.4] | 31.3 [19.3, 44.5] | 27.0 [16.7, 36.6] |
| white-box 20 steps: still flagged (0.1%, fixed threshold) | 0.1 [0.0, 0.2] | 1.7 [0.7, 2.9] | 17.0 [9.9, 25.2] | 17.4 [9.4, 25.3] |
| white-box 50 steps: still flagged (0.1%, fixed threshold) | 0.1 [0.0, 0.2] | 0.2 [0.0, 0.5] | 0.4 [0.1, 1.0] | 1.5 [0.6, 2.5] |
| white-box 5 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.08 [0.00, 0.21] | 0.14 [0.00, 0.46] | 0.12 [0.02, 0.27] |
| white-box 10 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.14 [0.05, 0.26] | 0.04 [0.00, 0.13] | 0.08 [0.00, 0.19] |
| white-box 20 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.36 [0.14, 0.65] | 0.00 [0.00, 0.00] | 0.14 [0.04, 0.27] |
| white-box 50 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.42 [0.19, 0.70] | 0.00 [0.00, 0.00] | 0.02 [0.00, 0.07] |

