### Cluster-bootstrap 95% intervals of the r1_A cells (value = mean over 10 seeds [2.5%, 97.5% interval of the seed mean]; cells = (hash_apis group, class), 1000 resamples, seed 0; thresholds recomputed on every resample)

**The cells of the Stage J report table (detection of April malware at the 1% clean-FPR threshold, %; last row padded-benign FPR %)**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.0 [68.6, 86.3] | 77.9 [68.0, 85.2] | 73.6 [61.1, 82.7] |
| random 20 prepend | 25.4 [16.9, 35.2] | 76.2 [65.4, 84.1] | 74.4 [62.9, 82.7] | 70.8 [56.5, 81.2] |
| random 50 prepend | 7.4 [4.3, 11.6] | 65.1 [52.3, 74.9] | 67.2 [55.1, 76.4] | 69.9 [57.7, 78.7] |
| random 60 prepend | 5.8 [3.1, 9.5] | 51.9 [38.8, 63.2] | 60.8 [48.6, 71.1] | 68.0 [55.2, 77.0] |
| random 75 prepend | 5.4 [2.9, 9.0] | 21.5 [13.6, 29.6] | 41.0 [30.5, 51.5] | 68.1 [55.4, 77.4] |
| random 100 prepend | 5.7 [3.0, 9.3] | 6.5 [3.4, 11.2] | 25.9 [15.4, 37.9] | 69.3 [55.1, 79.7] |
| random 200 prepend | 5.7 [3.0, 9.2] | 6.4 [3.3, 11.0] | 8.2 [3.9, 14.8] | 69.9 [57.2, 79.0] |
| random 20 insert | 55.2 [43.1, 65.5] | 74.5 [63.4, 82.5] | 72.5 [60.6, 81.1] | 68.7 [54.4, 79.4] |
| random 50 insert | 42.1 [30.5, 53.0] | 68.5 [56.0, 78.2] | 65.0 [52.2, 75.2] | 65.7 [52.4, 75.3] |
| random 200 insert | 18.9 [11.5, 28.0] | 44.3 [31.3, 56.1] | 37.5 [25.4, 49.7] | 50.5 [36.5, 62.5] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 35.1 [22.9, 48.2] | 48.5 [34.5, 60.9] | 65.4 [52.8, 75.3] |
| lgbm 50 insert | 25.4 [15.6, 35.9] | 54.7 [39.4, 67.3] | 47.5 [34.6, 59.6] | 55.8 [41.1, 68.3] |
| white-box 20 steps | 1.6 [0.7, 23.5] | 48.7 [34.8, 69.4] | 50.2 [35.0, 70.6] | 53.0 [38.9, 70.0] |
| white-box 50 steps | 0.6 [0.2, 23.1] | 2.5 [1.2, 37.9] | 10.6 [6.0, 47.9] | 49.5 [35.4, 67.7] |
| padded-benign FPR (%), random 50 prepend | 1.07 [0.23, 2.18] | 0.84 [0.50, 1.39] | 0.49 [0.38, 0.63] | 1.09 [0.68, 1.82] |

**Detection of April malware after the edit, 1% threshold (%)**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.0 [68.6, 86.3] | 77.9 [68.0, 85.2] | 73.6 [61.1, 82.7] |
| random 20 prepend | 25.4 [16.9, 35.2] | 76.2 [65.4, 84.1] | 74.4 [62.9, 82.7] | 70.8 [56.5, 81.2] |
| random 50 prepend | 7.4 [4.3, 11.6] | 65.1 [52.3, 74.9] | 67.2 [55.1, 76.4] | 69.9 [57.7, 78.7] |
| random 60 prepend | 5.8 [3.1, 9.5] | 51.9 [38.8, 63.2] | 60.8 [48.6, 71.1] | 68.0 [55.2, 77.0] |
| random 75 prepend | 5.4 [2.9, 9.0] | 21.5 [13.6, 29.6] | 41.0 [30.5, 51.5] | 68.1 [55.4, 77.4] |
| random 100 prepend | 5.7 [3.0, 9.3] | 6.5 [3.4, 11.2] | 25.9 [15.4, 37.9] | 69.3 [55.1, 79.7] |
| random 200 prepend | 5.7 [3.0, 9.2] | 6.4 [3.3, 11.0] | 8.2 [3.9, 14.8] | 69.9 [57.2, 79.0] |
| random 20 insert | 55.2 [43.1, 65.5] | 74.5 [63.4, 82.5] | 72.5 [60.6, 81.1] | 68.7 [54.4, 79.4] |
| random 50 insert | 42.1 [30.5, 53.0] | 68.5 [56.0, 78.2] | 65.0 [52.2, 75.2] | 65.7 [52.4, 75.3] |
| random 200 insert | 18.9 [11.5, 28.0] | 44.3 [31.3, 56.1] | 37.5 [25.4, 49.7] | 50.5 [36.5, 62.5] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 35.1 [22.9, 48.2] | 48.5 [34.5, 60.9] | 65.4 [52.8, 75.3] |
| lgbm 50 insert | 25.4 [15.6, 35.9] | 54.7 [39.4, 67.3] | 47.5 [34.6, 59.6] | 55.8 [41.1, 68.3] |

**Padded-benign FPR after the same edit, 1% threshold (%)**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| unedited | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] | 0.98 [0.94, 0.99] |
| random 20 prepend | 1.29 [0.50, 2.15] | 1.12 [0.93, 1.42] | 0.94 [0.73, 1.16] | 1.35 [1.07, 1.74] |
| random 50 prepend | 1.07 [0.23, 2.18] | 0.84 [0.50, 1.39] | 0.49 [0.38, 0.63] | 1.09 [0.68, 1.82] |
| random 60 prepend | 1.16 [0.21, 2.41] | 0.59 [0.30, 1.09] | 0.34 [0.24, 0.45] | 0.96 [0.61, 1.54] |
| random 75 prepend | 1.61 [0.27, 3.25] | 0.40 [0.16, 0.74] | 0.13 [0.07, 0.22] | 0.98 [0.71, 1.30] |
| random 100 prepend | 1.39 [0.26, 2.78] | 0.30 [0.11, 0.62] | 0.04 [0.01, 0.07] | 0.98 [0.80, 1.21] |
| random 200 prepend | 1.43 [0.27, 2.86] | 0.29 [0.12, 0.58] | 0.00 [0.00, 0.01] | 1.15 [0.78, 1.70] |
| random 20 insert | 0.69 [0.30, 1.14] | 0.95 [0.71, 1.29] | 0.73 [0.57, 0.94] | 1.04 [0.80, 1.39] |
| random 50 insert | 0.55 [0.18, 1.05] | 0.68 [0.45, 0.99] | 0.45 [0.31, 0.64] | 0.84 [0.55, 1.29] |
| random 200 insert | 0.84 [0.18, 1.65] | 0.44 [0.26, 0.73] | 0.02 [0.00, 0.06] | 0.69 [0.47, 0.95] |
| lgbm 50 prepend | 0.00 [0.00, 0.01] | 0.06 [0.02, 0.10] | 0.06 [0.03, 0.11] | 0.89 [0.54, 1.44] |
| lgbm 50 insert | 0.07 [0.03, 0.16] | 0.16 [0.09, 0.25] | 0.04 [0.01, 0.08] | 0.39 [0.25, 0.60] |

**Detection of April malware after the edit, 0.1% threshold (%)**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| unedited | 53.6 [39.6, 66.3] | 56.7 [41.7, 68.5] | 45.3 [28.5, 58.3] | 54.5 [34.4, 67.3] |
| random 20 prepend | 7.2 [3.9, 12.7] | 50.5 [33.7, 63.3] | 44.2 [26.3, 57.2] | 49.2 [30.0, 62.7] |
| random 50 prepend | 1.3 [0.7, 2.7] | 28.1 [15.9, 41.0] | 38.1 [22.5, 50.1] | 43.8 [25.8, 57.5] |
| random 60 prepend | 1.0 [0.5, 2.0] | 12.6 [6.1, 21.4] | 28.6 [14.8, 40.9] | 41.5 [24.5, 55.2] |
| random 75 prepend | 1.0 [0.5, 2.0] | 2.3 [0.9, 4.9] | 12.3 [5.9, 18.8] | 45.2 [27.9, 58.0] |
| random 100 prepend | 1.0 [0.5, 2.0] | 1.9 [0.7, 3.9] | 5.2 [2.8, 8.6] | 46.8 [28.4, 60.1] |
| random 200 prepend | 1.0 [0.5, 2.0] | 1.9 [0.7, 3.9] | 0.3 [0.1, 0.9] | 46.0 [27.2, 59.2] |
| random 20 insert | 26.8 [17.4, 38.9] | 43.8 [28.0, 57.7] | 40.4 [22.6, 53.4] | 43.5 [25.3, 56.9] |
| random 50 insert | 16.2 [9.7, 25.9] | 36.1 [21.0, 50.4] | 34.8 [18.5, 47.5] | 36.8 [19.4, 50.5] |
| random 200 insert | 4.5 [2.3, 8.6] | 21.6 [10.3, 34.1] | 10.6 [4.2, 16.6] | 21.9 [8.2, 32.9] |
| lgbm 50 prepend | 0.3 [0.1, 0.9] | 3.7 [1.2, 9.0] | 21.6 [10.2, 34.0] | 40.4 [22.7, 54.3] |
| lgbm 50 insert | 7.7 [3.9, 14.0] | 26.5 [13.9, 40.4] | 21.5 [9.8, 32.6] | 29.0 [13.1, 41.5] |

**Padded-benign FPR after the same edit, 0.1% threshold (%)**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| unedited | 0.10 [0.07, 0.10] | 0.10 [0.08, 0.10] | 0.10 [0.07, 0.10] | 0.10 [0.07, 0.10] |
| random 20 prepend | 0.02 [0.00, 0.09] | 0.04 [0.01, 0.09] | 0.07 [0.03, 0.12] | 0.14 [0.06, 0.29] |
| random 50 prepend | 0.02 [0.00, 0.09] | 0.00 [0.00, 0.02] | 0.03 [0.01, 0.06] | 0.08 [0.04, 0.10] |
| random 60 prepend | 0.01 [0.00, 0.07] | 0.00 [0.00, 0.01] | 0.01 [0.00, 0.02] | 0.08 [0.04, 0.11] |
| random 75 prepend | 0.03 [0.00, 0.12] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] | 0.11 [0.05, 0.16] |
| random 100 prepend | 0.02 [0.00, 0.10] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.11 [0.07, 0.16] |
| random 200 prepend | 0.02 [0.01, 0.10] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.09 [0.05, 0.13] |
| random 20 insert | 0.02 [0.01, 0.05] | 0.03 [0.01, 0.05] | 0.05 [0.02, 0.10] | 0.10 [0.06, 0.17] |
| random 50 insert | 0.01 [0.00, 0.03] | 0.01 [0.00, 0.02] | 0.02 [0.00, 0.07] | 0.08 [0.03, 0.11] |
| random 200 insert | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.01] | 0.04 [0.01, 0.06] |
| lgbm 50 prepend | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.07 [0.03, 0.09] |
| lgbm 50 insert | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.01] | 0.04 [0.01, 0.06] |

**White-box greedy attack (1% threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| white-box 0 steps: still flagged (1%) | 75.2 [62.6, 83.6] | 75.6 [63.0, 84.8] | 74.6 [62.8, 84.0] | 71.5 [57.9, 81.5] |
| white-box 5 steps: still flagged (1%) | 12.5 [7.8, 31.4] | 66.2 [52.3, 79.2] | 61.3 [46.7, 76.8] | 59.3 [45.5, 74.5] |
| white-box 10 steps: still flagged (1%) | 5.9 [3.4, 26.1] | 63.1 [49.0, 77.7] | 58.3 [43.4, 75.6] | 58.5 [44.4, 73.9] |
| white-box 20 steps: still flagged (1%) | 1.6 [0.7, 23.5] | 48.7 [34.8, 69.4] | 50.2 [35.0, 70.6] | 53.0 [38.9, 70.0] |
| white-box 50 steps: still flagged (1%) | 0.6 [0.2, 23.1] | 2.5 [1.2, 37.9] | 10.6 [6.0, 47.9] | 49.5 [35.4, 67.7] |
| white-box 5 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.52 [0.16, 0.96] | 0.74 [0.28, 1.22] | 0.87 [0.21, 1.58] |
| white-box 10 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.48 [0.12, 0.93] | 1.00 [0.53, 1.51] | 1.13 [0.42, 1.84] |
| white-box 20 steps: padded-benign FPR (1%) | 0.30 [0.10, 0.46] | 0.42 [0.12, 0.78] | 0.94 [0.54, 1.36] | 0.80 [0.21, 1.41] |
| white-box 50 steps: padded-benign FPR (1%) | 0.28 [0.09, 0.43] | 0.28 [0.05, 0.60] | 0.42 [0.16, 0.66] | 0.87 [0.23, 1.48] |

**White-box, the attack's own fixed threshold (1%): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| white-box 0 steps: still flagged (1%, fixed threshold) | 75.2 [64.4, 82.7] | 75.6 [64.3, 84.2] | 74.6 [63.0, 82.8] | 71.5 [58.0, 81.2] |
| white-box 5 steps: still flagged (1%, fixed threshold) | 12.5 [7.7, 18.2] | 66.2 [53.5, 76.3] | 61.3 [46.4, 73.1] | 59.3 [44.1, 71.7] |
| white-box 10 steps: still flagged (1%, fixed threshold) | 5.9 [3.2, 9.7] | 63.1 [50.2, 73.6] | 58.3 [42.8, 71.2] | 58.5 [43.7, 71.1] |
| white-box 20 steps: still flagged (1%, fixed threshold) | 1.6 [0.6, 3.2] | 48.7 [34.3, 60.7] | 50.2 [35.2, 62.5] | 53.0 [37.8, 67.1] |
| white-box 50 steps: still flagged (1%, fixed threshold) | 0.6 [0.2, 1.1] | 2.5 [1.1, 4.6] | 10.6 [6.4, 15.8] | 49.5 [34.4, 63.7] |
| white-box 5 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 0.52 [0.14, 1.08] | 0.74 [0.28, 1.31] | 0.87 [0.22, 1.74] |
| white-box 10 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 0.48 [0.11, 1.04] | 1.00 [0.52, 1.67] | 1.13 [0.46, 2.07] |
| white-box 20 steps: padded-benign FPR (1%, fixed threshold) | 0.30 [0.09, 0.63] | 0.42 [0.12, 0.86] | 0.94 [0.57, 1.44] | 0.80 [0.24, 1.51] |
| white-box 50 steps: padded-benign FPR (1%, fixed threshold) | 0.28 [0.07, 0.62] | 0.28 [0.06, 0.65] | 0.42 [0.19, 0.73] | 0.87 [0.24, 1.73] |

**White-box greedy attack (0.1% threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| white-box 0 steps: still flagged (0.1%) | 48.0 [34.3, 61.8] | 52.7 [37.6, 65.2] | 41.8 [24.7, 55.6] | 47.3 [26.5, 61.1] |
| white-box 5 steps: still flagged (0.1%) | 1.8 [0.6, 4.2] | 34.7 [20.3, 48.8] | 30.8 [14.8, 42.2] | 26.7 [12.8, 41.4] |
| white-box 10 steps: still flagged (0.1%) | 0.5 [0.1, 1.3] | 31.3 [17.3, 45.1] | 27.0 [11.8, 38.1] | 25.6 [12.1, 40.7] |
| white-box 20 steps: still flagged (0.1%) | 0.1 [0.0, 0.4] | 17.0 [7.8, 27.1] | 17.4 [6.6, 27.7] | 23.9 [10.1, 38.6] |
| white-box 50 steps: still flagged (0.1%) | 0.1 [0.0, 0.2] | 0.4 [0.1, 1.0] | 1.5 [0.4, 3.0] | 20.9 [8.2, 35.1] |
| white-box 5 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.14 [0.00, 0.41] | 0.12 [0.00, 0.27] | 0.20 [0.00, 0.58] |
| white-box 10 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.04 [0.00, 0.10] | 0.08 [0.00, 0.18] | 0.13 [0.00, 0.40] |
| white-box 20 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.14 [0.02, 0.27] | 0.00 [0.00, 0.00] |
| white-box 50 steps: padded-benign FPR (0.1%) | 0.02 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.02 [0.00, 0.07] | 0.07 [0.00, 0.27] |

**White-box, the attack's own fixed threshold (0.1%): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| white-box 0 steps: still flagged (0.1%, fixed threshold) | 48.0 [37.8, 57.0] | 52.7 [39.5, 64.3] | 41.8 [31.8, 51.0] | 47.3 [34.2, 59.7] |
| white-box 5 steps: still flagged (0.1%, fixed threshold) | 1.8 [0.9, 3.2] | 34.7 [21.9, 48.5] | 30.8 [19.8, 41.1] | 26.7 [14.8, 40.6] |
| white-box 10 steps: still flagged (0.1%, fixed threshold) | 0.5 [0.2, 1.0] | 31.3 [19.3, 44.5] | 27.0 [16.7, 36.6] | 25.6 [13.9, 39.6] |
| white-box 20 steps: still flagged (0.1%, fixed threshold) | 0.1 [0.0, 0.2] | 17.0 [9.9, 25.2] | 17.4 [9.4, 25.3] | 23.9 [12.6, 37.6] |
| white-box 50 steps: still flagged (0.1%, fixed threshold) | 0.1 [0.0, 0.2] | 0.4 [0.1, 1.0] | 1.5 [0.6, 2.5] | 20.9 [9.8, 34.4] |
| white-box 5 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.14 [0.00, 0.46] | 0.12 [0.02, 0.27] | 0.20 [0.00, 0.66] |
| white-box 10 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.04 [0.00, 0.13] | 0.08 [0.00, 0.19] | 0.13 [0.00, 0.44] |
| white-box 20 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.00 [0.00, 0.00] | 0.14 [0.04, 0.27] | 0.00 [0.00, 0.00] |
| white-box 50 steps: padded-benign FPR (0.1%, fixed threshold) | 0.02 [0.00, 0.07] | 0.00 [0.00, 0.00] | 0.02 [0.00, 0.07] | 0.07 [0.00, 0.22] |

