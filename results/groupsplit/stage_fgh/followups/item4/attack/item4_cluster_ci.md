### Cluster-bootstrap 95% intervals of the item4 cells (value = mean over 10 seeds [2.5%, 97.5% interval of the seed mean]; cells = (hash_apis group, class), 1000 resamples, seed 0; thresholds recomputed on every resample)

**The cells of the Stage J report table (detection of April malware at the 1% clean-FPR threshold, %; last row padded-benign FPR %)**

| row | M1 (no padding) | M1 settings + malware-only padding | M3 (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.3 [70.0, 85.9] | 79.0 [68.6, 86.3] | 78.7 [69.1, 85.9] |
| random 5 prepend | 54.8 [42.0, 64.9] | 88.8 [83.5, 92.9] | 79.0 [68.7, 85.7] | 85.4 [77.6, 90.4] |
| random 20 prepend | 25.4 [16.9, 35.2] | 97.2 [95.5, 98.4] | 76.2 [65.4, 84.1] | 90.6 [84.8, 94.2] |
| random 50 prepend | 7.4 [4.3, 11.6] | 98.6 [97.9, 99.2] | 65.1 [52.3, 74.9] | 94.2 [90.6, 96.3] |
| random 5 insert | 71.4 [60.3, 78.7] | 82.2 [73.6, 88.2] | 77.5 [67.2, 85.0] | 82.2 [73.7, 88.1] |
| random 20 insert | 55.2 [43.1, 65.5] | 86.6 [79.4, 91.5] | 74.5 [63.4, 82.5] | 85.6 [77.8, 90.8] |
| random 50 insert | 42.1 [30.5, 53.0] | 90.8 [84.8, 94.6] | 68.5 [56.0, 78.2] | 87.8 [80.6, 92.4] |
| white-box 20 steps | pending | pending | pending | pending |
| white-box 50 steps | pending | pending | pending | pending |
| padded-benign FPR (%), random 50 prepend | 1.07 [0.23, 2.18] | 97.73 [96.59, 98.48] | 0.84 [0.50, 1.39] | 82.42 [74.17, 88.39] |

**Detection of April malware after the edit, 1% threshold (%)**

| row | M1 (no padding) | M1 settings + malware-only padding | M3 (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.3 [70.0, 85.9] | 79.0 [68.6, 86.3] | 78.7 [69.1, 85.9] |
| random 5 prepend | 54.8 [42.0, 64.9] | 88.8 [83.5, 92.9] | 79.0 [68.7, 85.7] | 85.4 [77.6, 90.4] |
| random 20 prepend | 25.4 [16.9, 35.2] | 97.2 [95.5, 98.4] | 76.2 [65.4, 84.1] | 90.6 [84.8, 94.2] |
| random 50 prepend | 7.4 [4.3, 11.6] | 98.6 [97.9, 99.2] | 65.1 [52.3, 74.9] | 94.2 [90.6, 96.3] |
| random 5 insert | 71.4 [60.3, 78.7] | 82.2 [73.6, 88.2] | 77.5 [67.2, 85.0] | 82.2 [73.7, 88.1] |
| random 20 insert | 55.2 [43.1, 65.5] | 86.6 [79.4, 91.5] | 74.5 [63.4, 82.5] | 85.6 [77.8, 90.8] |
| random 50 insert | 42.1 [30.5, 53.0] | 90.8 [84.8, 94.6] | 68.5 [56.0, 78.2] | 87.8 [80.6, 92.4] |

**Padded-benign FPR after the same edit, 1% threshold (%)**

| row | M1 (no padding) | M1 settings + malware-only padding | M3 (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 1.00 [0.97, 1.00] | 1.00 [0.91, 0.99] | 1.00 [0.97, 1.00] | 1.00 [0.98, 1.00] |
| random 5 prepend | 0.91 [0.53, 1.50] | 30.11 [24.62, 37.49] | 1.03 [0.90, 1.25] | 20.41 [16.02, 25.46] |
| random 20 prepend | 1.29 [0.50, 2.15] | 86.27 [81.80, 90.38] | 1.12 [0.93, 1.42] | 46.92 [39.13, 55.13] |
| random 50 prepend | 1.07 [0.23, 2.18] | 97.73 [96.59, 98.48] | 0.84 [0.50, 1.39] | 82.42 [74.17, 88.39] |
| random 5 insert | 0.87 [0.54, 1.22] | 11.00 [8.66, 14.11] | 1.08 [0.89, 1.33] | 13.07 [10.04, 16.55] |
| random 20 insert | 0.69 [0.30, 1.14] | 33.40 [27.35, 41.14] | 0.95 [0.71, 1.29] | 29.49 [23.26, 36.59] |
| random 50 insert | 0.55 [0.18, 1.05] | 50.30 [43.27, 59.47] | 0.68 [0.45, 0.99] | 42.46 [36.33, 49.14] |

**Detection of April malware after the edit, 0.1% threshold (%)**

| row | M1 (no padding) | M1 settings + malware-only padding | M3 (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 53.6 [39.6, 66.3] | 56.5 [42.5, 67.0] | 56.7 [41.7, 68.5] | 55.3 [41.3, 66.9] |
| random 5 prepend | 24.7 [16.1, 36.8] | 64.3 [51.7, 73.8] | 50.8 [35.1, 64.2] | 63.0 [49.0, 73.0] |
| random 20 prepend | 7.2 [3.9, 12.7] | 80.5 [69.5, 87.3] | 50.5 [33.7, 63.3] | 67.2 [52.6, 76.5] |
| random 50 prepend | 1.3 [0.7, 2.7] | 86.8 [78.8, 91.4] | 28.1 [15.9, 41.0] | 57.1 [42.9, 68.9] |
| random 5 insert | 41.6 [29.5, 54.7] | 57.2 [43.4, 67.7] | 51.5 [35.9, 63.8] | 57.6 [44.5, 68.0] |
| random 20 insert | 26.8 [17.4, 38.9] | 64.4 [51.1, 73.4] | 43.8 [28.0, 57.7] | 57.5 [44.1, 68.6] |
| random 50 insert | 16.2 [9.7, 25.9] | 71.9 [59.6, 79.4] | 36.1 [21.0, 50.4] | 57.9 [43.9, 69.1] |

**Padded-benign FPR after the same edit, 0.1% threshold (%)**

| row | M1 (no padding) | M1 settings + malware-only padding | M3 (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 0.10 [0.07, 0.10] | 0.10 [0.07, 0.10] | 0.10 [0.08, 0.10] | 0.10 [0.08, 0.10] |
| random 5 prepend | 0.03 [0.02, 0.07] | 3.20 [1.62, 5.62] | 0.07 [0.04, 0.10] | 7.60 [5.27, 10.46] |
| random 20 prepend | 0.02 [0.00, 0.09] | 43.82 [29.23, 54.08] | 0.04 [0.01, 0.09] | 14.67 [10.16, 19.96] |
| random 50 prepend | 0.02 [0.00, 0.09] | 78.93 [67.83, 85.10] | 0.00 [0.00, 0.02] | 27.03 [17.11, 38.47] |
| random 5 insert | 0.03 [0.01, 0.07] | 0.87 [0.39, 1.60] | 0.06 [0.03, 0.10] | 5.26 [3.61, 7.31] |
| random 20 insert | 0.02 [0.01, 0.05] | 11.31 [7.04, 16.13] | 0.03 [0.01, 0.05] | 12.11 [8.37, 16.63] |
| random 50 insert | 0.01 [0.00, 0.03] | 29.10 [21.20, 38.10] | 0.01 [0.00, 0.02] | 13.28 [8.74, 18.51] |

