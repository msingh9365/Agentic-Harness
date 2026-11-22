### Attacks on the four final models (April, all reports edited; seeds present: x_fn: 10, x_an: 10, x_fb: 10, x_ab: 10)

**Detection of malware after the edit, threshold at 1% FPR of the clean April benign scores (%)**

| edit set | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 79.6 ± 3.0 | 74.9 ± 9.6 | 77.5 ± 2.1 | 78.1 ± 1.0 |
| random_20_prepend | 17.9 ± 5.8 | 47.4 ± 17.6 | 70.1 ± 2.9 | 75.4 ± 1.6 |
| random_50_prepend | 12.9 ± 5.0 | 10.3 ± 11.6 | 48.4 ± 6.4 | 63.4 ± 3.1 |
| random_20_insert | 49.3 ± 5.2 | 51.7 ± 12.0 | 71.7 ± 3.7 | 73.0 ± 1.3 |
| random_50_insert | 35.2 ± 5.4 | 39.8 ± 11.1 | 66.5 ± 3.6 | 67.0 ± 1.8 |
| lgbm_50_prepend | 6.2 ± 1.6 | 0.7 ± 1.3 | 3.1 ± 3.4 | 44.6 ± 9.5 |
| lgbm_50_insert | 22.5 ± 5.1 | 23.9 ± 7.5 | 50.3 ± 5.2 | 56.5 ± 1.7 |

**Padded-benign FPR after the same edit, threshold at 1% FPR (%) (clean benign: 1% by construction)**

| edit set | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.01 |
| random_20_prepend | 3.91 ± 3.65 | 0.35 ± 0.21 | 1.36 ± 0.57 | 1.11 ± 0.18 |
| random_50_prepend | 5.44 ± 4.37 | 0.05 ± 0.07 | 1.34 ± 0.68 | 0.76 ± 0.20 |
| random_20_insert | 1.47 ± 0.98 | 0.33 ± 0.19 | 1.00 ± 0.29 | 0.95 ± 0.27 |
| random_50_insert | 2.43 ± 1.90 | 0.19 ± 0.14 | 0.89 ± 0.32 | 0.62 ± 0.19 |
| lgbm_50_prepend | 0.01 ± 0.02 | 0.00 ± 0.00 | 0.01 ± 0.02 | 0.13 ± 0.13 |
| lgbm_50_insert | 0.66 ± 0.86 | 0.09 ± 0.05 | 0.20 ± 0.07 | 0.22 ± 0.08 |

**Detection of malware after the edit, threshold at 0.1% FPR of the clean April benign scores (%)**

| edit set | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 50.9 ± 3.5 | 49.5 ± 7.7 | 57.0 ± 6.9 | 57.4 ± 7.2 |
| random_20_prepend | 6.3 ± 1.5 | 11.6 ± 10.4 | 46.9 ± 10.8 | 51.8 ± 6.6 |
| random_50_prepend | 4.4 ± 1.7 | 0.3 ± 0.7 | 15.3 ± 8.5 | 26.5 ± 8.3 |
| random_20_insert | 22.2 ± 4.5 | 21.0 ± 8.0 | 48.9 ± 7.2 | 44.4 ± 7.4 |
| random_50_insert | 14.1 ± 2.7 | 12.3 ± 6.6 | 42.0 ± 6.8 | 37.0 ± 6.6 |
| lgbm_50_prepend | 2.4 ± 2.4 | 0.0 ± 0.0 | 0.0 ± 0.0 | 3.0 ± 2.2 |
| lgbm_50_insert | 9.6 ± 2.8 | 7.2 ± 5.5 | 27.7 ± 7.5 | 26.4 ± 5.2 |

**Padded-benign FPR after the same edit, threshold at 0.1% FPR (%) (clean benign: 0.1% by construction)**

| edit set | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 0.10 ± 0.01 | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 |
| random_20_prepend | 0.15 ± 0.19 | 0.01 ± 0.02 | 0.10 ± 0.06 | 0.05 ± 0.03 |
| random_50_prepend | 0.27 ± 0.25 | 0.00 ± 0.00 | 0.07 ± 0.09 | 0.01 ± 0.01 |
| random_20_insert | 0.05 ± 0.05 | 0.01 ± 0.02 | 0.08 ± 0.03 | 0.02 ± 0.02 |
| random_50_insert | 0.07 ± 0.05 | 0.00 ± 0.00 | 0.07 ± 0.03 | 0.01 ± 0.01 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| lgbm_50_insert | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.03 ± 0.01 | 0.01 ± 0.01 |

**Detection per family under random padding k = 50 prepended (1% threshold; in brackets the unedited detection) (%)**

| family | n | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|---|
| backdoor | 1940 | 36.1 ± 4.7 (clean 85.2 ± 1.8) | 19.7 ± 22.2 (clean 79.0 ± 5.5) | 56.5 ± 5.9 (clean 81.0 ± 2.2) | 69.1 ± 1.9 (clean 81.1 ± 0.7) |
| coinminer | 1684 | 7.2 ± 7.3 (clean 76.5 ± 9.2) | 10.4 ± 13.8 (clean 70.1 ± 10.8) | 50.4 ± 9.7 (clean 71.8 ± 6.7) | 66.1 ± 3.8 (clean 69.0 ± 1.0) |
| dropper | 252 | 6.9 ± 4.9 (clean 71.3 ± 8.0) | 5.2 ± 6.0 (clean 75.3 ± 6.2) | 46.5 ± 5.8 (clean 79.7 ± 2.5) | 61.2 ± 6.4 (clean 82.1 ± 0.7) |
| keylogger | 1041 | 3.8 ± 3.0 (clean 84.9 ± 5.1) | 4.8 ± 6.6 (clean 76.6 ± 21.6) | 54.9 ± 7.9 (clean 84.8 ± 6.0) | 71.6 ± 4.0 (clean 86.6 ± 3.1) |
| ransomware | 2139 | 7.6 ± 5.5 (clean 70.0 ± 4.8) | 3.6 ± 5.0 (clean 69.0 ± 7.2) | 31.5 ± 6.8 (clean 69.5 ± 3.7) | 43.7 ± 6.2 (clean 71.8 ± 3.2) |
| rat | 1258 | 5.0 ± 4.7 (clean 89.7 ± 2.2) | 5.9 ± 7.4 (clean 81.4 ± 17.4) | 51.7 ± 10.3 (clean 85.8 ± 1.4) | 74.8 ± 2.8 (clean 86.1 ± 1.2) |
| trojan | 1085 | 9.7 ± 7.8 (clean 78.6 ± 3.3) | 17.9 ± 16.2 (clean 77.7 ± 4.8) | 54.9 ± 5.4 (clean 78.4 ± 1.8) | 66.9 ± 3.6 (clean 80.9 ± 1.3) |

**White-box greedy attack (500 April malware, 200 candidates per step, prepend, up to 50 steps): share still flagged after k steps (%) and padded-benign FPR after k steps (%)**

| model | threshold | seeds | k = 0 | k = 5 | k = 10 | k = 20 | k = 50 | FPR k = 5 | FPR k = 10 | FPR k = 20 | FPR k = 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| flatten, none | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| flatten, none | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| attention, none | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| attention, none | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| flatten, balanced | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| flatten, balanced | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| attention, balanced | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| attention, balanced | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

