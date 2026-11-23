### Attacks on the four final models (April, all reports edited; seeds present: m3: 10, m3mw: 10, r1: 10)

**Detection of malware after the edit, threshold at 1% FPR of the clean April benign scores (%)**

| edit set | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 79.0 ± 1.9 | 71.8 ± 3.3 | 73.6 ± 1.5 |
| random_20_prepend | 76.2 ± 2.3 | 69.4 ± 2.8 | 70.8 ± 1.3 |
| random_50_prepend | 65.1 ± 5.8 | 58.1 ± 6.3 | 69.9 ± 2.8 |
| random_60_prepend | 51.9 ± 9.4 | 56.7 ± 5.6 | 68.0 ± 3.0 |
| random_75_prepend | 21.5 ± 8.3 | 64.5 ± 2.8 | 68.1 ± 1.8 |
| random_100_prepend | 6.5 ± 1.3 | 68.3 ± 2.7 | 69.3 ± 1.7 |
| random_200_prepend | 6.4 ± 1.2 | 65.4 ± 3.9 | 69.9 ± 2.8 |
| random_20_insert | 74.5 ± 2.1 | 61.5 ± 3.4 | 68.7 ± 1.5 |
| random_50_insert | 68.5 ± 2.8 | 55.4 ± 3.4 | 65.7 ± 2.6 |
| random_200_insert | 44.3 ± 4.0 | 38.4 ± 4.5 | 50.5 ± 6.2 |
| lgbm_50_prepend | 35.1 ± 13.3 | 58.0 ± 4.0 | 65.4 ± 3.7 |
| lgbm_50_insert | 54.7 ± 2.9 | 44.3 ± 4.0 | 55.8 ± 3.1 |
| adaptive_50_every_window | 65.1 ± 5.7 | 53.8 ± 9.9 | 64.0 ± 6.0 |

**Padded-benign FPR after the same edit, threshold at 1% FPR (%) (clean benign: 1% by construction)**

| edit set | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.98 ± 0.03 |
| random_20_prepend | 1.12 ± 0.22 | 1.23 ± 0.28 | 1.35 ± 0.50 |
| random_50_prepend | 0.84 ± 0.52 | 1.33 ± 0.95 | 1.09 ± 0.40 |
| random_60_prepend | 0.59 ± 0.49 | 1.13 ± 0.37 | 0.96 ± 0.26 |
| random_75_prepend | 0.40 ± 0.43 | 1.23 ± 0.37 | 0.98 ± 0.27 |
| random_100_prepend | 0.30 ± 0.37 | 1.11 ± 0.21 | 0.98 ± 0.29 |
| random_200_prepend | 0.29 ± 0.35 | 1.36 ± 0.36 | 1.15 ± 0.31 |
| random_20_insert | 0.95 ± 0.25 | 1.11 ± 0.25 | 1.04 ± 0.41 |
| random_50_insert | 0.68 ± 0.35 | 0.96 ± 0.27 | 0.84 ± 0.27 |
| random_200_insert | 0.44 ± 0.37 | 0.62 ± 0.27 | 0.69 ± 0.36 |
| lgbm_50_prepend | 0.06 ± 0.06 | 0.92 ± 0.18 | 0.89 ± 0.43 |
| lgbm_50_insert | 0.16 ± 0.06 | 0.46 ± 0.14 | 0.39 ± 0.14 |
| adaptive_50_every_window | 0.94 ± 0.61 | 0.42 ± 0.24 | 0.55 ± 0.35 |

**Detection of malware after the edit, threshold at 0.1% FPR of the clean April benign scores (%)**

| edit set | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 56.7 ± 4.7 | 44.1 ± 8.4 | 54.5 ± 4.2 |
| random_20_prepend | 50.5 ± 7.3 | 36.8 ± 7.0 | 49.2 ± 7.7 |
| random_50_prepend | 28.1 ± 8.8 | 26.3 ± 8.1 | 43.8 ± 6.6 |
| random_60_prepend | 12.6 ± 6.4 | 25.4 ± 7.2 | 41.5 ± 7.2 |
| random_75_prepend | 2.3 ± 1.2 | 33.6 ± 8.8 | 45.2 ± 6.5 |
| random_100_prepend | 1.9 ± 0.9 | 35.0 ± 7.8 | 46.8 ± 7.2 |
| random_200_prepend | 1.9 ± 0.9 | 31.4 ± 7.9 | 46.0 ± 6.2 |
| random_20_insert | 43.8 ± 4.4 | 32.9 ± 6.7 | 43.5 ± 7.2 |
| random_50_insert | 36.1 ± 4.5 | 27.4 ± 6.6 | 36.8 ± 7.0 |
| random_200_insert | 21.6 ± 2.8 | 15.0 ± 4.5 | 21.9 ± 7.5 |
| lgbm_50_prepend | 3.7 ± 2.9 | 24.6 ± 6.2 | 40.4 ± 7.9 |
| lgbm_50_insert | 26.5 ± 3.4 | 20.6 ± 4.6 | 29.0 ± 6.0 |
| adaptive_50_every_window | 28.0 ± 8.8 | 18.0 ± 11.0 | 33.2 ± 10.8 |

**Padded-benign FPR after the same edit, threshold at 0.1% FPR (%) (clean benign: 0.1% by construction)**

| edit set | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 |
| random_20_prepend | 0.04 ± 0.02 | 0.18 ± 0.06 | 0.14 ± 0.05 |
| random_50_prepend | 0.00 ± 0.01 | 0.21 ± 0.09 | 0.08 ± 0.03 |
| random_60_prepend | 0.00 ± 0.00 | 0.15 ± 0.04 | 0.08 ± 0.02 |
| random_75_prepend | 0.00 ± 0.00 | 0.21 ± 0.07 | 0.11 ± 0.04 |
| random_100_prepend | 0.00 ± 0.00 | 0.16 ± 0.03 | 0.11 ± 0.03 |
| random_200_prepend | 0.00 ± 0.00 | 0.24 ± 0.05 | 0.09 ± 0.03 |
| random_20_insert | 0.03 ± 0.01 | 0.16 ± 0.05 | 0.10 ± 0.04 |
| random_50_insert | 0.01 ± 0.01 | 0.18 ± 0.09 | 0.08 ± 0.02 |
| random_200_insert | 0.00 ± 0.00 | 0.10 ± 0.05 | 0.04 ± 0.02 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.15 ± 0.06 | 0.07 ± 0.02 |
| lgbm_50_insert | 0.01 ± 0.01 | 0.08 ± 0.07 | 0.04 ± 0.02 |
| adaptive_50_every_window | 0.01 ± 0.01 | 0.03 ± 0.04 | 0.03 ± 0.02 |

**Detection per family under random padding k = 50 prepended (1% threshold; in brackets the unedited detection) (%)**

| family | n | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|---|
| backdoor | 1940 | 68.2 ± 2.9 (clean 81.0 ± 0.9) | 73.3 ± 3.3 (clean 80.2 ± 4.1) | 78.3 ± 0.8 (clean 81.1 ± 1.6) |
| coinminer | 1684 | 65.6 ± 6.7 (clean 71.9 ± 6.7) | 56.5 ± 8.9 (clean 67.8 ± 6.4) | 90.1 ± 1.1 (clean 91.2 ± 1.1) |
| dropper | 252 | 63.7 ± 9.6 (clean 83.5 ± 1.0) | 58.0 ± 9.7 (clean 73.2 ± 2.4) | 72.8 ± 3.1 (clean 75.9 ± 2.2) |
| keylogger | 1041 | 74.0 ± 7.8 (clean 88.7 ± 2.0) | 67.8 ± 3.9 (clean 76.8 ± 3.0) | 39.9 ± 15.4 (clean 45.6 ± 14.6) |
| ransomware | 2139 | 50.2 ± 7.0 (clean 72.2 ± 3.1) | 36.9 ± 7.8 (clean 59.2 ± 4.1) | 52.3 ± 6.4 (clean 57.8 ± 3.0) |
| rat | 1258 | 74.7 ± 6.5 (clean 86.8 ± 0.9) | 56.4 ± 14.1 (clean 77.2 ± 8.8) | 81.8 ± 3.3 (clean 85.8 ± 0.8) |
| trojan | 1085 | 68.5 ± 5.5 (clean 80.8 ± 1.3) | 67.6 ± 3.2 (clean 76.3 ± 1.3) | 72.6 ± 1.8 (clean 76.3 ± 1.2) |

**White-box greedy attack (500 April malware, 200 candidates per step, prepend, up to 50 steps): share still flagged after k steps (%) and padded-benign FPR after k steps (%)**

| model | threshold | seeds | k = 0 | k = 5 | k = 10 | k = 20 | k = 50 | FPR k = 5 | FPR k = 10 | FPR k = 20 | FPR k = 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M3 ATT+bal | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 + test-time multi-window max | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 + test-time multi-window max | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| R1 windowed M3 | 1% | 3 | 71.5 ± 1.2 | 59.3 ± 3.6 | 58.5 ± 3.0 | 53.0 ± 1.9 | 49.5 ± 2.9 | 0.87 ± 0.31 | 1.13 ± 0.23 | 0.80 ± 0.20 | 0.87 ± 0.31 |
| R1 windowed M3 | 0.1% | 3 | 47.3 ± 1.6 | 26.7 ± 0.8 | 25.6 ± 0.6 | 23.9 ± 1.3 | 20.9 ± 1.3 | 0.20 ± 0.00 | 0.13 ± 0.12 | 0.00 ± 0.00 | 0.07 ± 0.12 |

