### Cluster-bootstrap 95% intervals of the item3 cells (value = mean over 10 seeds [2.5%, 97.5% interval of the seed mean]; cells = (hash_apis group, class), 1000 resamples, seed 0; thresholds recomputed on every resample)

**The cells of the Stage J report table (detection of April malware at the 1% clean-FPR threshold, %; last row padded-benign FPR %)**

| row | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 79.6 [69.4, 86.5] | 74.9 [64.4, 82.5] | 77.5 [67.4, 84.8] | 78.1 [67.9, 85.6] |
| random 20 prepend | 17.9 [11.5, 25.6] | 47.4 [33.1, 59.2] | 70.1 [58.6, 80.1] | 75.4 [64.7, 83.2] |
| random 50 prepend | 12.9 [8.4, 19.1] | 10.3 [5.2, 17.4] | 48.4 [37.5, 59.4] | 63.4 [51.1, 72.9] |
| lgbm 50 prepend | 6.2 [3.1, 10.7] | 0.7 [0.1, 2.1] | 3.1 [1.4, 5.4] | 44.6 [31.2, 57.4] |
| white-box 20 steps | pending | pending | pending | pending |
| white-box 50 steps | pending | pending | pending | pending |
| padded-benign FPR (%), random 50 prepend | 5.44 [3.23, 8.52] | 0.05 [0.02, 0.13] | 1.34 [0.96, 2.35] | 0.76 [0.50, 1.22] |

**Detection of April malware after the edit, 1% threshold (%)**

| row | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 79.6 [69.4, 86.5] | 74.9 [64.4, 82.5] | 77.5 [67.4, 84.8] | 78.1 [67.9, 85.6] |
| random 20 prepend | 17.9 [11.5, 25.6] | 47.4 [33.1, 59.2] | 70.1 [58.6, 80.1] | 75.4 [64.7, 83.2] |
| random 50 prepend | 12.9 [8.4, 19.1] | 10.3 [5.2, 17.4] | 48.4 [37.5, 59.4] | 63.4 [51.1, 72.9] |
| random 20 insert | 49.3 [36.9, 60.3] | 51.7 [38.5, 63.6] | 71.7 [60.7, 80.3] | 73.0 [61.8, 81.6] |
| random 50 insert | 35.2 [24.7, 46.3] | 39.8 [26.1, 52.0] | 66.5 [54.8, 76.2] | 67.0 [54.2, 77.3] |
| lgbm 50 prepend | 6.2 [3.1, 10.7] | 0.7 [0.1, 2.1] | 3.1 [1.4, 5.4] | 44.6 [31.2, 57.4] |
| lgbm 50 insert | 22.5 [14.6, 32.2] | 23.9 [12.2, 36.5] | 50.3 [36.9, 63.3] | 56.5 [41.1, 70.4] |

**Padded-benign FPR after the same edit, 1% threshold (%)**

| row | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 1.00 [0.97, 1.00] | 1.00 [0.90, 0.99] | 1.00 [0.96, 1.00] | 1.00 [0.96, 1.00] |
| random 20 prepend | 3.91 [1.99, 6.87] | 0.35 [0.21, 0.51] | 1.36 [1.09, 2.05] | 1.11 [0.94, 1.34] |
| random 50 prepend | 5.44 [3.23, 8.52] | 0.05 [0.02, 0.13] | 1.34 [0.96, 2.35] | 0.76 [0.50, 1.22] |
| random 20 insert | 1.47 [0.89, 2.41] | 0.33 [0.19, 0.81] | 1.00 [0.82, 1.47] | 0.95 [0.71, 1.29] |
| random 50 insert | 2.43 [1.37, 4.24] | 0.19 [0.08, 0.51] | 0.89 [0.71, 1.38] | 0.62 [0.42, 0.93] |
| lgbm 50 prepend | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.13 [0.07, 0.21] |
| lgbm 50 insert | 0.66 [0.17, 1.68] | 0.09 [0.03, 0.15] | 0.20 [0.13, 0.29] | 0.22 [0.15, 0.33] |

**Detection of April malware after the edit, 0.1% threshold (%)**

| row | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 50.9 [35.3, 64.5] | 49.5 [32.1, 62.7] | 57.0 [40.7, 69.3] | 57.4 [40.8, 70.7] |
| random 20 prepend | 6.3 [3.0, 10.7] | 11.6 [4.6, 21.2] | 46.9 [31.6, 60.9] | 51.8 [34.2, 65.5] |
| random 50 prepend | 4.4 [2.0, 7.8] | 0.3 [0.0, 1.3] | 15.3 [8.4, 23.4] | 26.5 [13.1, 42.2] |
| random 20 insert | 22.2 [13.7, 31.4] | 21.0 [10.2, 34.6] | 48.9 [35.0, 60.8] | 44.4 [28.4, 59.6] |
| random 50 insert | 14.1 [8.1, 21.7] | 12.3 [4.6, 22.5] | 42.0 [28.2, 53.9] | 37.0 [20.9, 51.4] |
| lgbm 50 prepend | 2.4 [0.7, 5.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.4] | 3.0 [0.9, 9.5] |
| lgbm 50 insert | 9.6 [5.1, 15.5] | 7.2 [1.8, 14.6] | 27.7 [15.5, 39.7] | 26.4 [13.1, 40.3] |

**Padded-benign FPR after the same edit, 0.1% threshold (%)**

| row | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 0.10 [0.07, 0.10] | 0.10 [0.08, 0.10] | 0.10 [0.07, 0.10] | 0.10 [0.08, 0.10] |
| random 20 prepend | 0.15 [0.04, 0.43] | 0.01 [0.00, 0.04] | 0.10 [0.06, 0.15] | 0.05 [0.02, 0.11] |
| random 50 prepend | 0.27 [0.09, 0.68] | 0.00 [0.00, 0.00] | 0.07 [0.02, 0.12] | 0.01 [0.00, 0.03] |
| random 20 insert | 0.05 [0.02, 0.12] | 0.01 [0.00, 0.04] | 0.08 [0.04, 0.12] | 0.02 [0.01, 0.06] |
| random 50 insert | 0.07 [0.02, 0.21] | 0.00 [0.00, 0.00] | 0.07 [0.04, 0.12] | 0.01 [0.00, 0.03] |
| lgbm 50 prepend | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| lgbm 50 insert | 0.00 [0.00, 0.03] | 0.00 [0.00, 0.00] | 0.03 [0.01, 0.04] | 0.01 [0.00, 0.02] |

