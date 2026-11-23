### Cluster-bootstrap 95% intervals of the r1_B cells (value = mean over 10 seeds [2.5%, 97.5% interval of the seed mean]; cells = (hash_apis group, class), 1000 resamples, seed 0; thresholds recomputed on every resample)

**The cells of the Stage J report table (detection of April malware at the 1% clean-FPR threshold, %; last row padded-benign FPR %)**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 79.0 [68.6, 86.3] | 71.8 [60.8, 80.2] | 73.6 [61.1, 82.7] |
| random 20 prepend | 76.2 [65.4, 84.1] | 69.4 [57.8, 77.9] | 70.8 [56.5, 81.2] |
| random 50 prepend | 65.1 [52.3, 74.9] | 58.1 [44.9, 68.8] | 69.9 [57.7, 78.7] |
| random 60 prepend | 51.9 [38.8, 63.2] | 56.7 [42.1, 68.0] | 68.0 [55.2, 77.0] |
| random 75 prepend | 21.5 [13.6, 29.6] | 64.5 [51.2, 74.3] | 68.1 [55.4, 77.4] |
| random 100 prepend | 6.5 [3.4, 11.2] | 68.3 [57.3, 77.4] | 69.3 [55.1, 79.7] |
| random 200 prepend | 6.4 [3.3, 11.0] | 65.4 [53.3, 75.0] | 69.9 [57.2, 79.0] |
| random 20 insert | 74.5 [63.4, 82.5] | 61.5 [49.9, 71.3] | 68.7 [54.4, 79.4] |
| random 50 insert | 68.5 [56.0, 78.2] | 55.4 [42.7, 66.7] | 65.7 [52.4, 75.3] |
| random 200 insert | 44.3 [31.3, 56.1] | 38.4 [26.5, 50.7] | 50.5 [36.5, 62.5] |
| lgbm 50 prepend | 35.1 [22.9, 48.2] | 58.0 [42.5, 70.0] | 65.4 [52.8, 75.3] |
| lgbm 50 insert | 54.7 [39.4, 67.3] | 44.3 [31.4, 57.6] | 55.8 [41.1, 68.3] |
| adaptive 50 every window | 65.1 [51.8, 75.0] | 53.8 [41.3, 64.1] | 64.0 [50.0, 74.7] |
| white-box 20 steps | pending | pending | 53.0 [38.9, 70.0] |
| white-box 50 steps | pending | pending | 49.5 [35.4, 67.7] |
| padded-benign FPR (%), random 50 prepend | 0.84 [0.50, 1.39] | 1.33 [0.85, 2.30] | 1.09 [0.68, 1.82] |

**Detection of April malware after the edit, 1% threshold (%)**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 79.0 [68.6, 86.3] | 71.8 [60.8, 80.2] | 73.6 [61.1, 82.7] |
| random 20 prepend | 76.2 [65.4, 84.1] | 69.4 [57.8, 77.9] | 70.8 [56.5, 81.2] |
| random 50 prepend | 65.1 [52.3, 74.9] | 58.1 [44.9, 68.8] | 69.9 [57.7, 78.7] |
| random 60 prepend | 51.9 [38.8, 63.2] | 56.7 [42.1, 68.0] | 68.0 [55.2, 77.0] |
| random 75 prepend | 21.5 [13.6, 29.6] | 64.5 [51.2, 74.3] | 68.1 [55.4, 77.4] |
| random 100 prepend | 6.5 [3.4, 11.2] | 68.3 [57.3, 77.4] | 69.3 [55.1, 79.7] |
| random 200 prepend | 6.4 [3.3, 11.0] | 65.4 [53.3, 75.0] | 69.9 [57.2, 79.0] |
| random 20 insert | 74.5 [63.4, 82.5] | 61.5 [49.9, 71.3] | 68.7 [54.4, 79.4] |
| random 50 insert | 68.5 [56.0, 78.2] | 55.4 [42.7, 66.7] | 65.7 [52.4, 75.3] |
| random 200 insert | 44.3 [31.3, 56.1] | 38.4 [26.5, 50.7] | 50.5 [36.5, 62.5] |
| lgbm 50 prepend | 35.1 [22.9, 48.2] | 58.0 [42.5, 70.0] | 65.4 [52.8, 75.3] |
| lgbm 50 insert | 54.7 [39.4, 67.3] | 44.3 [31.4, 57.6] | 55.8 [41.1, 68.3] |
| adaptive 50 every window | 65.1 [51.8, 75.0] | 53.8 [41.3, 64.1] | 64.0 [50.0, 74.7] |

**Padded-benign FPR after the same edit, 1% threshold (%)**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] | 0.98 [0.94, 0.99] |
| random 20 prepend | 1.12 [0.93, 1.42] | 1.23 [0.94, 1.61] | 1.35 [1.07, 1.74] |
| random 50 prepend | 0.84 [0.50, 1.39] | 1.33 [0.85, 2.30] | 1.09 [0.68, 1.82] |
| random 60 prepend | 0.59 [0.30, 1.09] | 1.13 [0.84, 1.73] | 0.96 [0.61, 1.54] |
| random 75 prepend | 0.40 [0.16, 0.74] | 1.23 [0.96, 2.09] | 0.98 [0.71, 1.30] |
| random 100 prepend | 0.30 [0.11, 0.62] | 1.11 [0.92, 1.37] | 0.98 [0.80, 1.21] |
| random 200 prepend | 0.29 [0.12, 0.58] | 1.36 [1.04, 1.88] | 1.15 [0.78, 1.70] |
| random 20 insert | 0.95 [0.71, 1.29] | 1.11 [0.83, 1.48] | 1.04 [0.80, 1.39] |
| random 50 insert | 0.68 [0.45, 0.99] | 0.96 [0.70, 1.39] | 0.84 [0.55, 1.29] |
| random 200 insert | 0.44 [0.26, 0.73] | 0.62 [0.45, 0.82] | 0.69 [0.47, 0.95] |
| lgbm 50 prepend | 0.06 [0.02, 0.10] | 0.92 [0.77, 1.19] | 0.89 [0.54, 1.44] |
| lgbm 50 insert | 0.16 [0.09, 0.25] | 0.46 [0.36, 0.63] | 0.39 [0.25, 0.60] |
| adaptive 50 every window | 0.94 [0.56, 1.50] | 0.42 [0.33, 0.55] | 0.55 [0.42, 0.73] |

**Detection of April malware after the edit, 0.1% threshold (%)**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 56.7 [41.7, 68.5] | 44.1 [30.7, 56.5] | 54.5 [34.4, 67.3] |
| random 20 prepend | 50.5 [33.7, 63.3] | 36.8 [23.0, 49.7] | 49.2 [30.0, 62.7] |
| random 50 prepend | 28.1 [15.9, 41.0] | 26.3 [15.1, 38.2] | 43.8 [25.8, 57.5] |
| random 60 prepend | 12.6 [6.1, 21.4] | 25.4 [13.6, 37.0] | 41.5 [24.5, 55.2] |
| random 75 prepend | 2.3 [0.9, 4.9] | 33.6 [20.4, 44.8] | 45.2 [27.9, 58.0] |
| random 100 prepend | 1.9 [0.7, 3.9] | 35.0 [20.8, 48.2] | 46.8 [28.4, 60.1] |
| random 200 prepend | 1.9 [0.7, 3.9] | 31.4 [18.1, 44.6] | 46.0 [27.2, 59.2] |
| random 20 insert | 43.8 [28.0, 57.7] | 32.9 [19.9, 45.5] | 43.5 [25.3, 56.9] |
| random 50 insert | 36.1 [21.0, 50.4] | 27.4 [15.3, 39.6] | 36.8 [19.4, 50.5] |
| random 200 insert | 21.6 [10.3, 34.1] | 15.0 [6.6, 25.0] | 21.9 [8.2, 32.9] |
| lgbm 50 prepend | 3.7 [1.2, 9.0] | 24.6 [12.7, 36.6] | 40.4 [22.7, 54.3] |
| lgbm 50 insert | 26.5 [13.9, 40.4] | 20.6 [10.1, 32.3] | 29.0 [13.1, 41.5] |
| adaptive 50 every window | 28.0 [15.6, 40.9] | 18.0 [9.0, 27.8] | 33.2 [15.5, 45.8] |

**Padded-benign FPR after the same edit, 0.1% threshold (%)**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 0.10 [0.08, 0.10] | 0.10 [0.07, 0.10] | 0.10 [0.07, 0.10] |
| random 20 prepend | 0.04 [0.01, 0.09] | 0.18 [0.11, 0.27] | 0.14 [0.06, 0.29] |
| random 50 prepend | 0.00 [0.00, 0.02] | 0.21 [0.10, 0.33] | 0.08 [0.04, 0.10] |
| random 60 prepend | 0.00 [0.00, 0.01] | 0.15 [0.10, 0.22] | 0.08 [0.04, 0.11] |
| random 75 prepend | 0.00 [0.00, 0.00] | 0.21 [0.12, 0.33] | 0.11 [0.05, 0.16] |
| random 100 prepend | 0.00 [0.00, 0.00] | 0.16 [0.10, 0.23] | 0.11 [0.07, 0.16] |
| random 200 prepend | 0.00 [0.00, 0.00] | 0.24 [0.15, 0.36] | 0.09 [0.05, 0.13] |
| random 20 insert | 0.03 [0.01, 0.05] | 0.16 [0.10, 0.24] | 0.10 [0.06, 0.17] |
| random 50 insert | 0.01 [0.00, 0.02] | 0.18 [0.09, 0.30] | 0.08 [0.03, 0.11] |
| random 200 insert | 0.00 [0.00, 0.01] | 0.10 [0.05, 0.15] | 0.04 [0.01, 0.06] |
| lgbm 50 prepend | 0.00 [0.00, 0.00] | 0.15 [0.09, 0.23] | 0.07 [0.03, 0.09] |
| lgbm 50 insert | 0.01 [0.00, 0.02] | 0.08 [0.03, 0.14] | 0.04 [0.01, 0.06] |
| adaptive 50 every window | 0.01 [0.00, 0.03] | 0.03 [0.01, 0.05] | 0.03 [0.01, 0.05] |

**White-box greedy attack (1% threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| white-box 0 steps: still flagged (1%) | pending | pending | 71.5 [57.9, 81.5] |
| white-box 5 steps: still flagged (1%) | pending | pending | 59.3 [45.5, 74.5] |
| white-box 10 steps: still flagged (1%) | pending | pending | 58.5 [44.4, 73.9] |
| white-box 20 steps: still flagged (1%) | pending | pending | 53.0 [38.9, 70.0] |
| white-box 50 steps: still flagged (1%) | pending | pending | 49.5 [35.4, 67.7] |
| white-box 5 steps: padded-benign FPR (1%) | pending | pending | 0.87 [0.21, 1.58] |
| white-box 10 steps: padded-benign FPR (1%) | pending | pending | 1.13 [0.42, 1.84] |
| white-box 20 steps: padded-benign FPR (1%) | pending | pending | 0.80 [0.21, 1.41] |
| white-box 50 steps: padded-benign FPR (1%) | pending | pending | 0.87 [0.23, 1.48] |

**White-box, the attack's own fixed threshold (1%): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| white-box 0 steps: still flagged (1%, fixed threshold) | pending | pending | 71.5 [58.0, 81.2] |
| white-box 5 steps: still flagged (1%, fixed threshold) | pending | pending | 59.3 [44.1, 71.7] |
| white-box 10 steps: still flagged (1%, fixed threshold) | pending | pending | 58.5 [43.7, 71.1] |
| white-box 20 steps: still flagged (1%, fixed threshold) | pending | pending | 53.0 [37.8, 67.1] |
| white-box 50 steps: still flagged (1%, fixed threshold) | pending | pending | 49.5 [34.4, 63.7] |
| white-box 5 steps: padded-benign FPR (1%, fixed threshold) | pending | pending | 0.87 [0.22, 1.74] |
| white-box 10 steps: padded-benign FPR (1%, fixed threshold) | pending | pending | 1.13 [0.46, 2.07] |
| white-box 20 steps: padded-benign FPR (1%, fixed threshold) | pending | pending | 0.80 [0.24, 1.51] |
| white-box 50 steps: padded-benign FPR (1%, fixed threshold) | pending | pending | 0.87 [0.24, 1.73] |

**White-box greedy attack (0.1% threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| white-box 0 steps: still flagged (0.1%) | pending | pending | 47.3 [26.5, 61.1] |
| white-box 5 steps: still flagged (0.1%) | pending | pending | 26.7 [12.8, 41.4] |
| white-box 10 steps: still flagged (0.1%) | pending | pending | 25.6 [12.1, 40.7] |
| white-box 20 steps: still flagged (0.1%) | pending | pending | 23.9 [10.1, 38.6] |
| white-box 50 steps: still flagged (0.1%) | pending | pending | 20.9 [8.2, 35.1] |
| white-box 5 steps: padded-benign FPR (0.1%) | pending | pending | 0.20 [0.00, 0.58] |
| white-box 10 steps: padded-benign FPR (0.1%) | pending | pending | 0.13 [0.00, 0.40] |
| white-box 20 steps: padded-benign FPR (0.1%) | pending | pending | 0.00 [0.00, 0.00] |
| white-box 50 steps: padded-benign FPR (0.1%) | pending | pending | 0.07 [0.00, 0.27] |

**White-box, the attack's own fixed threshold (0.1%): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| white-box 0 steps: still flagged (0.1%, fixed threshold) | pending | pending | 47.3 [34.2, 59.7] |
| white-box 5 steps: still flagged (0.1%, fixed threshold) | pending | pending | 26.7 [14.8, 40.6] |
| white-box 10 steps: still flagged (0.1%, fixed threshold) | pending | pending | 25.6 [13.9, 39.6] |
| white-box 20 steps: still flagged (0.1%, fixed threshold) | pending | pending | 23.9 [12.6, 37.6] |
| white-box 50 steps: still flagged (0.1%, fixed threshold) | pending | pending | 20.9 [9.8, 34.4] |
| white-box 5 steps: padded-benign FPR (0.1%, fixed threshold) | pending | pending | 0.20 [0.00, 0.66] |
| white-box 10 steps: padded-benign FPR (0.1%, fixed threshold) | pending | pending | 0.13 [0.00, 0.44] |
| white-box 20 steps: padded-benign FPR (0.1%, fixed threshold) | pending | pending | 0.00 [0.00, 0.00] |
| white-box 50 steps: padded-benign FPR (0.1%, fixed threshold) | pending | pending | 0.07 [0.00, 0.22] |

