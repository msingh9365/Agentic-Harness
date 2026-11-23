### Cluster-bootstrap 95% intervals of the c1 cells (value = mean over 10 seeds [2.5%, 97.5% interval of the seed mean]; cells = (hash_apis group, class), 1000 resamples, seed 0; thresholds recomputed on every resample)

**The cells of the Stage J report table (detection of April malware at the 1% clean-FPR threshold, %; last row padded-benign FPR %)**

| row | M1 Nebula | M3 ATT+bal | LightGBM bag of names |
|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.0 [68.6, 86.3] | 54.8 [39.1, 70.1] |
| random 20 prepend | 25.4 [16.9, 35.2] | 76.2 [65.4, 84.1] | 24.4 [16.3, 31.9] |
| random 50 prepend | 7.4 [4.3, 11.6] | 65.1 [52.3, 74.9] | 9.9 [6.0, 14.4] |
| random 100 prepend | 5.7 [3.0, 9.3] | 6.5 [3.4, 11.2] | 3.1 [1.7, 4.7] |
| random 200 insert | 18.9 [11.5, 28.0] | 44.3 [31.3, 56.1] | 0.5 [0.2, 0.9] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 35.1 [22.9, 48.2] | 0.0 [0.0, 0.0] |
| white-box 20 steps | pending | pending | pending |
| white-box 50 steps | pending | pending | pending |
| padded-benign FPR (%), random 50 prepend | 1.07 [0.23, 2.18] | 0.84 [0.50, 1.39] | 0.05 [0.00, 0.09] |

**Detection of April malware after the edit, 1% threshold (%)**

| row | M1 Nebula | M3 ATT+bal | LightGBM bag of names |
|---|---|---|---|
| unedited | 79.1 [68.6, 85.8] | 79.0 [68.6, 86.3] | 54.8 [39.1, 70.1] |
| random 20 prepend | 25.4 [16.9, 35.2] | 76.2 [65.4, 84.1] | 24.4 [16.3, 31.9] |
| random 50 prepend | 7.4 [4.3, 11.6] | 65.1 [52.3, 74.9] | 9.9 [6.0, 14.4] |
| random 100 prepend | 5.7 [3.0, 9.3] | 6.5 [3.4, 11.2] | 3.1 [1.7, 4.7] |
| random 200 insert | 18.9 [11.5, 28.0] | 44.3 [31.3, 56.1] | 0.5 [0.2, 0.9] |
| lgbm 50 prepend | 1.9 [0.9, 3.4] | 35.1 [22.9, 48.2] | 0.0 [0.0, 0.0] |

**Padded-benign FPR after the same edit, 1% threshold (%)**

| row | M1 Nebula | M3 ATT+bal | LightGBM bag of names |
|---|---|---|---|
| unedited | 1.00 [0.97, 1.00] | 1.00 [0.97, 1.00] | 0.97 [0.61, 1.00] |
| random 20 prepend | 1.29 [0.50, 2.15] | 1.12 [0.93, 1.42] | 0.19 [0.06, 0.27] |
| random 50 prepend | 1.07 [0.23, 2.18] | 0.84 [0.50, 1.39] | 0.05 [0.00, 0.09] |
| random 100 prepend | 1.39 [0.26, 2.78] | 0.30 [0.11, 0.62] | 0.00 [0.00, 0.00] |
| random 200 insert | 0.84 [0.18, 1.65] | 0.44 [0.26, 0.73] | 0.00 [0.00, 0.00] |
| lgbm 50 prepend | 0.00 [0.00, 0.01] | 0.06 [0.02, 0.10] | 0.00 [0.00, 0.00] |

**Detection of April malware after the edit, 0.1% threshold (%)**

| row | M1 Nebula | M3 ATT+bal | LightGBM bag of names |
|---|---|---|---|
| unedited | 53.6 [39.6, 66.3] | 56.7 [41.7, 68.5] | 26.6 [15.6, 51.7] |
| random 20 prepend | 7.2 [3.9, 12.7] | 50.5 [33.7, 63.3] | 9.5 [6.0, 18.9] |
| random 50 prepend | 1.3 [0.7, 2.7] | 28.1 [15.9, 41.0] | 3.1 [1.7, 7.2] |
| random 100 prepend | 1.0 [0.5, 2.0] | 1.9 [0.7, 3.9] | 0.4 [0.2, 1.8] |
| random 200 insert | 4.5 [2.3, 8.6] | 21.6 [10.3, 34.1] | 0.0 [0.0, 0.1] |
| lgbm 50 prepend | 0.3 [0.1, 0.9] | 3.7 [1.2, 9.0] | 0.0 [0.0, 0.0] |

**Padded-benign FPR after the same edit, 0.1% threshold (%)**

| row | M1 Nebula | M3 ATT+bal | LightGBM bag of names |
|---|---|---|---|
| unedited | 0.10 [0.07, 0.10] | 0.10 [0.08, 0.10] | 0.10 [0.06, 0.10] |
| random 20 prepend | 0.02 [0.00, 0.09] | 0.04 [0.01, 0.09] | 0.02 [0.00, 0.07] |
| random 50 prepend | 0.02 [0.00, 0.09] | 0.00 [0.00, 0.02] | 0.00 [0.00, 0.00] |
| random 100 prepend | 0.02 [0.00, 0.10] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| random 200 insert | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] |
| lgbm 50 prepend | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

