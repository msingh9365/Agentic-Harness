### Attacks on the four final models (April, all reports edited; seeds present: m1: 10, m3: 10, c1: 10)

**Detection of malware after the edit, threshold at 1% FPR of the clean April benign scores (%)**

| edit set | M1 Nebula | M3 ATT+bal | LightGBM bag of API names |
|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.0 ± 1.9 | 54.8 ± 0.0 |
| random_20_prepend | 25.4 ± 7.8 | 76.2 ± 2.3 | 24.4 ± 0.0 |
| random_50_prepend | 7.4 ± 4.0 | 65.1 ± 5.8 | 9.9 ± 0.0 |
| random_100_prepend | 5.7 ± 5.1 | 6.5 ± 1.3 | 3.1 ± 0.0 |
| random_200_insert | 18.9 ± 5.9 | 44.3 ± 4.0 | 0.5 ± 0.0 |
| lgbm_50_prepend | 1.9 ± 2.6 | 35.1 ± 13.3 | 0.0 ± 0.0 |

**Padded-benign FPR after the same edit, threshold at 1% FPR (%) (clean benign: 1% by construction)**

| edit set | M1 Nebula | M3 ATT+bal | LightGBM bag of API names |
|---|---|---|---|
| unedited | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.97 ± 0.00 |
| random_20_prepend | 1.29 ± 1.38 | 1.12 ± 0.22 | 0.19 ± 0.00 |
| random_50_prepend | 1.07 ± 1.96 | 0.84 ± 0.52 | 0.05 ± 0.00 |
| random_100_prepend | 1.39 ± 3.34 | 0.30 ± 0.37 | 0.00 ± 0.00 |
| random_200_insert | 0.84 ± 1.81 | 0.44 ± 0.37 | 0.00 ± 0.00 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.06 ± 0.06 | 0.00 ± 0.00 |

**Detection of malware after the edit, threshold at 0.1% FPR of the clean April benign scores (%)**

| edit set | M1 Nebula | M3 ATT+bal | LightGBM bag of API names |
|---|---|---|---|
| unedited | 53.6 ± 6.0 | 56.7 ± 4.7 | 26.6 ± 0.0 |
| random_20_prepend | 7.2 ± 4.6 | 50.5 ± 7.3 | 9.5 ± 0.0 |
| random_50_prepend | 1.3 ± 1.7 | 28.1 ± 8.8 | 3.1 ± 0.0 |
| random_100_prepend | 1.0 ± 1.8 | 1.9 ± 0.9 | 0.4 ± 0.0 |
| random_200_insert | 4.5 ± 2.6 | 21.6 ± 2.8 | 0.0 ± 0.0 |
| lgbm_50_prepend | 0.3 ± 1.0 | 3.7 ± 2.9 | 0.0 ± 0.0 |

**Padded-benign FPR after the same edit, threshold at 0.1% FPR (%) (clean benign: 0.1% by construction)**

| edit set | M1 Nebula | M3 ATT+bal | LightGBM bag of API names |
|---|---|---|---|
| unedited | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 |
| random_20_prepend | 0.02 ± 0.02 | 0.04 ± 0.02 | 0.02 ± 0.00 |
| random_50_prepend | 0.02 ± 0.04 | 0.00 ± 0.01 | 0.00 ± 0.00 |
| random_100_prepend | 0.02 ± 0.07 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| random_200_insert | 0.01 ± 0.03 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |

**Detection per family under random padding k = 50 prepended (1% threshold; in brackets the unedited detection) (%)**

| family | n | M1 Nebula | M3 ATT+bal | LightGBM bag of API names |
|---|---|---|---|---|
| backdoor | 1940 | 25.3 ± 9.2 (clean 82.7 ± 1.6) | 68.2 ± 2.9 (clean 81.0 ± 0.9) | 27.1 ± 0.0 (clean 74.5 ± 0.0) |
| coinminer | 1684 | 2.4 ± 3.1 (clean 80.2 ± 7.5) | 65.6 ± 6.7 (clean 71.9 ± 6.7) | 1.7 ± 0.0 (clean 33.4 ± 0.0) |
| dropper | 252 | 3.7 ± 4.0 (clean 75.0 ± 4.6) | 63.7 ± 9.6 (clean 83.5 ± 1.0) | 25.8 ± 0.0 (clean 64.3 ± 0.0) |
| keylogger | 1041 | 1.2 ± 1.1 (clean 86.3 ± 5.1) | 74.0 ± 7.8 (clean 88.7 ± 2.0) | 1.5 ± 0.0 (clean 14.2 ± 0.0) |
| ransomware | 2139 | 3.6 ± 4.1 (clean 67.0 ± 5.2) | 50.2 ± 7.0 (clean 72.2 ± 3.1) | 3.6 ± 0.0 (clean 55.3 ± 0.0) |
| rat | 1258 | 1.2 ± 1.4 (clean 88.2 ± 2.0) | 74.7 ± 6.5 (clean 86.8 ± 0.9) | 2.5 ± 0.0 (clean 75.1 ± 0.0) |
| trojan | 1085 | 4.8 ± 6.4 (clean 78.6 ± 3.9) | 68.5 ± 5.5 (clean 80.8 ± 1.3) | 17.8 ± 0.0 (clean 65.3 ± 0.0) |

**White-box greedy attack (500 April malware, 200 candidates per step, prepend, up to 50 steps): share still flagged after k steps (%) and padded-benign FPR after k steps (%)**

| model | threshold | seeds | k = 0 | k = 5 | k = 10 | k = 20 | k = 50 | FPR k = 5 | FPR k = 10 | FPR k = 20 | FPR k = 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 Nebula | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 Nebula | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| LightGBM bag of API names | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| LightGBM bag of API names | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

