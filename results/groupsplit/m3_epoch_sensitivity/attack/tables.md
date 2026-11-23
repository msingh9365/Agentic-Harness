### Attacks on the four final models (April, all reports edited; seeds present: m1: 10, m3: 10, g3: 10)

**Detection of malware after the edit, threshold at 1% FPR of the clean April benign scores (%)**

| edit set | M1 Nebula | M3 ATT+bal, 3 epochs | M3 ATT+bal, 2 epochs |
|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.0 ± 1.9 | 78.9 ± 0.7 |
| random_20_prepend | 25.4 ± 7.8 | 76.2 ± 2.3 | 75.9 ± 1.2 |
| random_50_prepend | 7.4 ± 4.0 | 65.1 ± 5.8 | 64.2 ± 4.5 |
| random_60_prepend | 5.8 ± 3.5 | 51.9 ± 9.4 | 51.7 ± 8.7 |
| random_75_prepend | 5.4 ± 4.0 | 21.5 ± 8.3 | 21.9 ± 8.5 |
| random_100_prepend | 5.7 ± 5.1 | 6.5 ± 1.3 | 6.1 ± 2.1 |
| random_200_prepend | 5.7 ± 5.1 | 6.4 ± 1.2 | 6.1 ± 2.1 |
| random_20_insert | 55.2 ± 6.6 | 74.5 ± 2.1 | 74.3 ± 1.4 |
| random_50_insert | 42.1 ± 6.9 | 68.5 ± 2.8 | 68.4 ± 2.6 |
| random_60_insert | 38.9 ± 7.0 | 66.2 ± 3.1 | 66.2 ± 3.1 |
| random_75_insert | 35.4 ± 6.7 | 61.9 ± 3.4 | 62.3 ± 3.4 |
| random_100_insert | 30.3 ± 6.3 | 55.3 ± 3.6 | 56.0 ± 3.9 |
| random_200_insert | 18.9 ± 5.9 | 44.3 ± 4.0 | 46.5 ± 4.8 |
| lgbm_50_prepend | 1.9 ± 2.6 | 35.1 ± 13.3 | 38.8 ± 13.4 |
| lgbm_50_insert | 25.4 ± 6.8 | 54.7 ± 2.9 | 55.9 ± 2.2 |

**Padded-benign FPR after the same edit, threshold at 1% FPR (%) (clean benign: 1% by construction)**

| edit set | M1 Nebula | M3 ATT+bal, 3 epochs | M3 ATT+bal, 2 epochs |
|---|---|---|---|
| unedited | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 |
| random_20_prepend | 1.29 ± 1.38 | 1.12 ± 0.22 | 1.15 ± 0.25 |
| random_50_prepend | 1.07 ± 1.96 | 0.84 ± 0.52 | 1.01 ± 0.84 |
| random_60_prepend | 1.16 ± 2.46 | 0.59 ± 0.49 | 0.76 ± 0.89 |
| random_75_prepend | 1.61 ± 3.69 | 0.40 ± 0.43 | 0.61 ± 0.88 |
| random_100_prepend | 1.39 ± 3.34 | 0.30 ± 0.37 | 0.54 ± 0.91 |
| random_200_prepend | 1.43 ± 3.27 | 0.29 ± 0.35 | 0.53 ± 0.93 |
| random_20_insert | 0.69 ± 0.29 | 0.95 ± 0.25 | 1.09 ± 0.44 |
| random_50_insert | 0.55 ± 0.59 | 0.68 ± 0.35 | 0.81 ± 0.60 |
| random_60_insert | 0.61 ± 0.81 | 0.57 ± 0.29 | 0.75 ± 0.66 |
| random_75_insert | 0.69 ± 1.25 | 0.46 ± 0.30 | 0.63 ± 0.65 |
| random_100_insert | 0.71 ± 1.45 | 0.50 ± 0.31 | 0.69 ± 0.73 |
| random_200_insert | 0.84 ± 1.81 | 0.44 ± 0.37 | 0.63 ± 0.76 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.06 ± 0.06 | 0.08 ± 0.09 |
| lgbm_50_insert | 0.07 ± 0.09 | 0.16 ± 0.06 | 0.20 ± 0.09 |

**Detection of malware after the edit, threshold at 0.1% FPR of the clean April benign scores (%)**

| edit set | M1 Nebula | M3 ATT+bal, 3 epochs | M3 ATT+bal, 2 epochs |
|---|---|---|---|
| unedited | 53.6 ± 6.0 | 56.7 ± 4.7 | 60.9 ± 4.4 |
| random_20_prepend | 7.2 ± 4.6 | 50.5 ± 7.3 | 53.3 ± 6.3 |
| random_50_prepend | 1.3 ± 1.7 | 28.1 ± 8.8 | 28.3 ± 7.2 |
| random_60_prepend | 1.0 ± 1.6 | 12.6 ± 6.4 | 11.6 ± 4.5 |
| random_75_prepend | 1.0 ± 1.7 | 2.3 ± 1.2 | 2.2 ± 1.6 |
| random_100_prepend | 1.0 ± 1.8 | 1.9 ± 0.9 | 1.9 ± 1.4 |
| random_200_prepend | 1.0 ± 1.7 | 1.9 ± 0.9 | 1.8 ± 1.4 |
| random_20_insert | 26.8 ± 7.9 | 43.8 ± 4.4 | 45.6 ± 5.3 |
| random_50_insert | 16.2 ± 5.7 | 36.1 ± 4.5 | 37.6 ± 5.4 |
| random_60_insert | 14.1 ± 5.0 | 34.4 ± 4.5 | 36.1 ± 5.1 |
| random_75_insert | 12.0 ± 4.4 | 32.1 ± 4.0 | 33.7 ± 4.9 |
| random_100_insert | 9.4 ± 3.8 | 29.4 ± 3.1 | 30.8 ± 4.5 |
| random_200_insert | 4.5 ± 2.6 | 21.6 ± 2.8 | 21.8 ± 4.8 |
| lgbm_50_prepend | 0.3 ± 1.0 | 3.7 ± 2.9 | 3.3 ± 3.6 |
| lgbm_50_insert | 7.7 ± 4.0 | 26.5 ± 3.4 | 27.6 ± 3.9 |

**Padded-benign FPR after the same edit, threshold at 0.1% FPR (%) (clean benign: 0.1% by construction)**

| edit set | M1 Nebula | M3 ATT+bal, 3 epochs | M3 ATT+bal, 2 epochs |
|---|---|---|---|
| unedited | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 |
| random_20_prepend | 0.02 ± 0.02 | 0.04 ± 0.02 | 0.06 ± 0.03 |
| random_50_prepend | 0.02 ± 0.04 | 0.00 ± 0.01 | 0.01 ± 0.01 |
| random_60_prepend | 0.01 ± 0.03 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| random_75_prepend | 0.03 ± 0.09 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| random_100_prepend | 0.02 ± 0.07 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| random_200_prepend | 0.02 ± 0.05 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| random_20_insert | 0.02 ± 0.02 | 0.03 ± 0.01 | 0.03 ± 0.02 |
| random_50_insert | 0.01 ± 0.02 | 0.01 ± 0.01 | 0.01 ± 0.01 |
| random_60_insert | 0.01 ± 0.01 | 0.00 ± 0.00 | 0.00 ± 0.01 |
| random_75_insert | 0.00 ± 0.01 | 0.01 ± 0.01 | 0.01 ± 0.01 |
| random_100_insert | 0.00 ± 0.01 | 0.00 ± 0.00 | 0.00 ± 0.01 |
| random_200_insert | 0.01 ± 0.03 | 0.00 ± 0.00 | 0.00 ± 0.01 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| lgbm_50_insert | 0.00 ± 0.00 | 0.01 ± 0.01 | 0.00 ± 0.01 |

**Detection per family under random padding k = 50 prepended (1% threshold; in brackets the unedited detection) (%)**

| family | n | M1 Nebula | M3 ATT+bal, 3 epochs | M3 ATT+bal, 2 epochs |
|---|---|---|---|---|
| backdoor | 1940 | 25.3 ± 9.2 (clean 82.7 ± 1.6) | 68.2 ± 2.9 (clean 81.0 ± 0.9) | 68.6 ± 1.8 (clean 81.4 ± 1.7) |
| coinminer | 1684 | 2.4 ± 3.1 (clean 80.2 ± 7.5) | 65.6 ± 6.7 (clean 71.9 ± 6.7) | 64.0 ± 4.5 (clean 70.7 ± 1.0) |
| dropper | 252 | 3.7 ± 4.0 (clean 75.0 ± 4.6) | 63.7 ± 9.6 (clean 83.5 ± 1.0) | 62.2 ± 8.3 (clean 83.3 ± 0.9) |
| keylogger | 1041 | 1.2 ± 1.1 (clean 86.3 ± 5.1) | 74.0 ± 7.8 (clean 88.7 ± 2.0) | 73.6 ± 5.6 (clean 87.2 ± 4.0) |
| ransomware | 2139 | 3.6 ± 4.1 (clean 67.0 ± 5.2) | 50.2 ± 7.0 (clean 72.2 ± 3.1) | 48.6 ± 6.9 (clean 72.9 ± 2.9) |
| rat | 1258 | 1.2 ± 1.4 (clean 88.2 ± 2.0) | 74.7 ± 6.5 (clean 86.8 ± 0.9) | 73.8 ± 5.2 (clean 87.1 ± 0.6) |
| trojan | 1085 | 4.8 ± 6.4 (clean 78.6 ± 3.9) | 68.5 ± 5.5 (clean 80.8 ± 1.3) | 67.5 ± 4.9 (clean 80.6 ± 1.7) |

**White-box greedy attack (500 April malware, 200 candidates per step, prepend, up to 50 steps): share still flagged after k steps (%) and padded-benign FPR after k steps (%)**

| model | threshold | seeds | k = 0 | k = 5 | k = 10 | k = 20 | k = 50 | FPR k = 5 | FPR k = 10 | FPR k = 20 | FPR k = 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 Nebula | 1% | 10 | 75.2 ± 2.6 | 12.5 ± 7.0 | 5.9 ± 3.6 | 1.6 ± 1.6 | 0.6 ± 1.2 | 0.28 ± 0.17 | 0.28 ± 0.17 | 0.30 ± 0.19 | 0.28 ± 0.17 |
| M1 Nebula | 0.1% | 10 | 48.0 ± 6.1 | 1.8 ± 2.0 | 0.5 ± 0.6 | 0.1 ± 0.3 | 0.1 ± 0.3 | 0.02 ± 0.06 | 0.02 ± 0.06 | 0.02 ± 0.06 | 0.02 ± 0.06 |
| M3 ATT+bal, 3 epochs | 1% | 10 | 75.6 ± 2.1 | 66.2 ± 2.6 | 63.1 ± 3.1 | 48.7 ± 6.3 | 2.5 ± 1.3 | 0.52 ± 0.17 | 0.48 ± 0.14 | 0.42 ± 0.24 | 0.28 ± 0.21 |
| M3 ATT+bal, 3 epochs | 0.1% | 10 | 52.7 ± 4.4 | 34.7 ± 3.2 | 31.3 ± 4.1 | 17.0 ± 7.7 | 0.4 ± 0.6 | 0.14 ± 0.10 | 0.04 ± 0.08 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| M3 ATT+bal, 2 epochs | 1% | 10 | 75.2 ± 0.7 | 65.1 ± 2.5 | 62.7 ± 2.6 | 49.9 ± 5.0 | 1.9 ± 1.4 | 0.60 ± 0.16 | 0.54 ± 0.38 | 0.30 ± 0.29 | 0.24 ± 0.23 |
| M3 ATT+bal, 2 epochs | 0.1% | 10 | 56.3 ± 4.2 | 36.2 ± 4.7 | 33.3 ± 4.9 | 16.0 ± 5.0 | 0.4 ± 0.5 | 0.08 ± 0.10 | 0.04 ± 0.08 | 0.00 ± 0.00 | 0.00 ± 0.00 |

