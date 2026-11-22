### Attacks on the four final models (fixed tokenizer) (April, all reports edited; seeds present: m1: 10, m2: 10, m3: 10, m4: 10)

**Detection of malware after the edit, threshold at 1% FPR of the clean April benign scores (%)**

| edit set | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 77.2 ± 4.9 | 79.0 ± 1.9 | 77.9 ± 1.7 |
| random_5_prepend | 54.8 ± 7.5 | 64.0 ± 5.9 | 79.0 ± 2.0 | 77.6 ± 1.6 |
| random_20_prepend | 25.4 ± 7.8 | 54.2 ± 8.0 | 76.2 ± 2.3 | 74.4 ± 3.0 |
| random_50_prepend | 7.4 ± 4.0 | 28.5 ± 12.0 | 65.1 ± 5.8 | 67.2 ± 4.9 |
| random_100_prepend | 5.7 ± 5.1 | 17.1 ± 13.6 | 6.5 ± 1.3 | 25.9 ± 15.4 |
| random_200_prepend | 5.7 ± 5.1 | 7.8 ± 10.9 | 6.4 ± 1.2 | 8.2 ± 8.7 |
| random_5_insert | 71.4 ± 3.5 | 66.4 ± 5.2 | 77.5 ± 2.1 | 76.8 ± 1.8 |
| random_20_insert | 55.2 ± 6.6 | 55.0 ± 6.4 | 74.5 ± 2.1 | 72.5 ± 2.7 |
| random_50_insert | 42.1 ± 6.9 | 43.2 ± 7.3 | 68.5 ± 2.8 | 65.0 ± 4.1 |
| random_100_insert | 30.3 ± 6.3 | 29.5 ± 6.6 | 55.3 ± 3.6 | 52.4 ± 6.0 |
| random_200_insert | 18.9 ± 5.9 | 12.4 ± 4.7 | 44.3 ± 4.0 | 37.5 ± 7.8 |
| lgbm_20_prepend | 8.8 ± 3.7 | 46.6 ± 10.6 | 73.2 ± 2.5 | 73.4 ± 3.8 |
| lgbm_50_prepend | 1.9 ± 2.6 | 17.2 ± 15.2 | 35.1 ± 13.3 | 48.5 ± 7.7 |
| lgbm_100_prepend | 2.0 ± 2.8 | 14.2 ± 12.5 | 5.8 ± 1.7 | 20.0 ± 16.6 |
| lgbm_20_insert | 43.8 ± 7.4 | 41.3 ± 8.7 | 70.6 ± 1.7 | 62.5 ± 2.4 |
| lgbm_50_insert | 25.4 ± 6.8 | 25.3 ± 6.8 | 54.7 ± 2.9 | 47.5 ± 5.8 |
| lgbm_100_insert | 13.9 ± 4.9 | 13.4 ± 4.7 | 36.8 ± 3.4 | 36.6 ± 6.5 |

**Padded-benign FPR after the same edit, threshold at 1% FPR (%) (clean benign: 1% by construction)**

| edit set | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.01 |
| random_5_prepend | 0.91 ± 0.40 | 0.49 ± 0.12 | 1.03 ± 0.10 | 1.03 ± 0.31 |
| random_20_prepend | 1.29 ± 1.38 | 0.22 ± 0.15 | 1.12 ± 0.22 | 0.94 ± 0.25 |
| random_50_prepend | 1.07 ± 1.96 | 0.05 ± 0.08 | 0.84 ± 0.52 | 0.49 ± 0.14 |
| random_100_prepend | 1.39 ± 3.34 | 0.03 ± 0.05 | 0.30 ± 0.37 | 0.04 ± 0.05 |
| random_200_prepend | 1.43 ± 3.27 | 0.01 ± 0.02 | 0.29 ± 0.35 | 0.00 ± 0.01 |
| random_5_insert | 0.87 ± 0.19 | 0.46 ± 0.06 | 1.08 ± 0.09 | 0.87 ± 0.15 |
| random_20_insert | 0.69 ± 0.29 | 0.21 ± 0.11 | 0.95 ± 0.25 | 0.73 ± 0.26 |
| random_50_insert | 0.55 ± 0.59 | 0.07 ± 0.06 | 0.68 ± 0.35 | 0.45 ± 0.18 |
| random_100_insert | 0.71 ± 1.45 | 0.02 ± 0.02 | 0.50 ± 0.31 | 0.09 ± 0.05 |
| random_200_insert | 0.84 ± 1.81 | 0.00 ± 0.01 | 0.44 ± 0.37 | 0.02 ± 0.02 |
| lgbm_20_prepend | 0.00 ± 0.00 | 0.08 ± 0.08 | 0.67 ± 0.21 | 0.51 ± 0.16 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.04 ± 0.08 | 0.06 ± 0.06 | 0.06 ± 0.05 |
| lgbm_100_prepend | 0.00 ± 0.00 | 0.01 ± 0.02 | 0.00 ± 0.00 | 0.02 ± 0.03 |
| lgbm_20_insert | 0.15 ± 0.11 | 0.04 ± 0.04 | 0.39 ± 0.11 | 0.23 ± 0.07 |
| lgbm_50_insert | 0.07 ± 0.09 | 0.01 ± 0.01 | 0.16 ± 0.06 | 0.04 ± 0.02 |
| lgbm_100_insert | 0.02 ± 0.04 | 0.02 ± 0.03 | 0.08 ± 0.04 | 0.03 ± 0.01 |

**Detection of malware after the edit, threshold at 0.1% FPR of the clean April benign scores (%)**

| edit set | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 53.6 ± 6.0 | 38.1 ± 16.5 | 56.7 ± 4.7 | 45.3 ± 14.9 |
| random_5_prepend | 24.7 ± 8.7 | 26.5 ± 10.7 | 50.8 ± 5.2 | 46.3 ± 13.2 |
| random_20_prepend | 7.2 ± 4.6 | 17.4 ± 10.5 | 50.5 ± 7.3 | 44.2 ± 13.9 |
| random_50_prepend | 1.3 ± 1.7 | 1.1 ± 1.8 | 28.1 ± 8.8 | 38.1 ± 13.0 |
| random_100_prepend | 1.0 ± 1.8 | 0.1 ± 0.4 | 1.9 ± 0.9 | 5.2 ± 3.4 |
| random_200_prepend | 1.0 ± 1.7 | 0.0 ± 0.0 | 1.9 ± 0.9 | 0.3 ± 0.7 |
| random_5_insert | 41.6 ± 7.2 | 27.6 ± 12.4 | 51.5 ± 4.9 | 44.4 ± 13.1 |
| random_20_insert | 26.8 ± 7.9 | 19.9 ± 9.5 | 43.8 ± 4.4 | 40.4 ± 11.9 |
| random_50_insert | 16.2 ± 5.7 | 10.4 ± 5.8 | 36.1 ± 4.5 | 34.8 ± 11.8 |
| random_100_insert | 9.4 ± 3.8 | 3.3 ± 2.7 | 29.4 ± 3.1 | 21.5 ± 10.5 |
| random_200_insert | 4.5 ± 2.6 | 0.4 ± 0.5 | 21.6 ± 2.8 | 10.6 ± 8.2 |
| lgbm_20_prepend | 1.2 ± 1.7 | 8.0 ± 8.3 | 44.9 ± 7.0 | 45.7 ± 13.9 |
| lgbm_50_prepend | 0.3 ± 1.0 | 0.1 ± 0.3 | 3.7 ± 2.9 | 21.6 ± 10.5 |
| lgbm_100_prepend | 0.2 ± 0.7 | 0.0 ± 0.0 | 1.2 ± 0.9 | 3.9 ± 3.2 |
| lgbm_20_insert | 16.3 ± 7.1 | 10.2 ± 5.1 | 38.4 ± 4.1 | 33.3 ± 11.1 |
| lgbm_50_insert | 7.7 ± 4.0 | 2.9 ± 2.2 | 26.5 ± 3.4 | 21.5 ± 9.3 |
| lgbm_100_insert | 3.6 ± 2.6 | 0.5 ± 0.9 | 18.2 ± 2.1 | 10.6 ± 7.8 |

**Padded-benign FPR after the same edit, threshold at 0.1% FPR (%) (clean benign: 0.1% by construction)**

| edit set | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 |
| random_5_prepend | 0.03 ± 0.02 | 0.01 ± 0.02 | 0.07 ± 0.02 | 0.08 ± 0.02 |
| random_20_prepend | 0.02 ± 0.02 | 0.00 ± 0.01 | 0.04 ± 0.02 | 0.07 ± 0.04 |
| random_50_prepend | 0.02 ± 0.04 | 0.00 ± 0.00 | 0.00 ± 0.01 | 0.03 ± 0.01 |
| random_100_prepend | 0.02 ± 0.07 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| random_200_prepend | 0.02 ± 0.05 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| random_5_insert | 0.03 ± 0.02 | 0.01 ± 0.02 | 0.06 ± 0.02 | 0.07 ± 0.02 |
| random_20_insert | 0.02 ± 0.02 | 0.00 ± 0.01 | 0.03 ± 0.01 | 0.05 ± 0.03 |
| random_50_insert | 0.01 ± 0.02 | 0.00 ± 0.00 | 0.01 ± 0.01 | 0.02 ± 0.01 |
| random_100_insert | 0.00 ± 0.01 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.01 ± 0.01 |
| random_200_insert | 0.01 ± 0.03 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.01 |
| lgbm_20_prepend | 0.00 ± 0.00 | 0.00 ± 0.01 | 0.02 ± 0.02 | 0.06 ± 0.02 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| lgbm_100_prepend | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| lgbm_20_insert | 0.00 ± 0.01 | 0.00 ± 0.00 | 0.01 ± 0.01 | 0.02 ± 0.02 |
| lgbm_50_insert | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.01 ± 0.01 | 0.00 ± 0.01 |
| lgbm_100_insert | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.01 ± 0.01 |

**Detection per family under random padding k = 50 prepended (1% threshold; in brackets the unedited detection) (%)**

| family | n | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|---|
| backdoor | 1940 | 25.3 ± 9.2 (clean 82.7 ± 1.6) | 51.1 ± 20.1 (clean 80.1 ± 3.7) | 68.2 ± 2.9 (clean 81.0 ± 0.9) | 75.0 ± 3.2 (clean 81.0 ± 1.2) |
| coinminer | 1684 | 2.4 ± 3.1 (clean 80.2 ± 7.5) | 29.6 ± 18.9 (clean 81.7 ± 8.3) | 65.6 ± 6.7 (clean 71.9 ± 6.7) | 73.3 ± 7.6 (clean 84.1 ± 6.6) |
| dropper | 252 | 3.7 ± 4.0 (clean 75.0 ± 4.6) | 11.0 ± 6.2 (clean 77.5 ± 2.8) | 63.7 ± 9.6 (clean 83.5 ± 1.0) | 57.7 ± 7.8 (clean 80.3 ± 2.0) |
| keylogger | 1041 | 1.2 ± 1.1 (clean 86.3 ± 5.1) | 5.5 ± 6.2 (clean 83.2 ± 5.1) | 74.0 ± 7.8 (clean 88.7 ± 2.0) | 73.8 ± 2.4 (clean 86.2 ± 4.3) |
| ransomware | 2139 | 3.6 ± 4.1 (clean 67.0 ± 5.2) | 20.9 ± 6.4 (clean 62.5 ± 2.5) | 50.2 ± 7.0 (clean 72.2 ± 3.1) | 47.8 ± 8.3 (clean 62.3 ± 3.6) |
| rat | 1258 | 1.2 ± 1.4 (clean 88.2 ± 2.0) | 20.7 ± 14.0 (clean 82.8 ± 14.8) | 74.7 ± 6.5 (clean 86.8 ± 0.9) | 75.3 ± 5.2 (clean 82.5 ± 8.3) |
| trojan | 1085 | 4.8 ± 6.4 (clean 78.6 ± 3.9) | 36.3 ± 12.4 (clean 81.5 ± 3.1) | 68.5 ± 5.5 (clean 80.8 ± 1.3) | 68.3 ± 3.0 (clean 79.7 ± 2.7) |

**White-box greedy attack (500 April malware, 200 candidates per step, prepend, up to 50 steps): share still flagged after k steps (%) and padded-benign FPR after k steps (%)**

| model | threshold | seeds | k = 0 | k = 5 | k = 10 | k = 20 | k = 50 | FPR k = 5 | FPR k = 10 | FPR k = 20 | FPR k = 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 v2-PE (fixed tokenizer) | 1% | 10 | 75.2 ± 2.6 | 12.5 ± 7.0 | 5.9 ± 3.6 | 1.6 ± 1.6 | 0.6 ± 1.2 | 0.28 ± 0.17 | 0.28 ± 0.17 | 0.30 ± 0.19 | 0.28 ± 0.17 |
| M1 v2-PE (fixed tokenizer) | 0.1% | 10 | 48.0 ± 6.1 | 1.8 ± 2.0 | 0.5 ± 0.6 | 0.1 ± 0.3 | 0.1 ± 0.3 | 0.02 ± 0.06 | 0.02 ± 0.06 | 0.02 ± 0.06 | 0.02 ± 0.06 |
| M2 two-level, no padding (fixed tokenizer) | 1% | 10 | 74.4 ± 5.3 | 44.1 ± 8.8 | 35.9 ± 10.2 | 19.6 ± 13.3 | 13.8 ± 13.6 | 0.92 ± 1.04 | 1.56 ± 2.04 | 2.18 ± 3.35 | 3.16 ± 4.18 |
| M2 two-level, no padding (fixed tokenizer) | 0.1% | 10 | 35.5 ± 15.0 | 11.7 ± 9.3 | 6.3 ± 6.3 | 1.7 ± 4.5 | 0.2 ± 0.7 | 0.08 ± 0.17 | 0.14 ± 0.38 | 0.36 ± 0.61 | 0.42 ± 0.71 |
| M3 ATT+bal (fixed tokenizer) | 1% | 10 | 75.6 ± 2.1 | 66.2 ± 2.6 | 63.1 ± 3.1 | 48.7 ± 6.3 | 2.5 ± 1.3 | 0.52 ± 0.17 | 0.48 ± 0.14 | 0.42 ± 0.24 | 0.28 ± 0.21 |
| M3 ATT+bal (fixed tokenizer) | 0.1% | 10 | 52.7 ± 4.4 | 34.7 ± 3.2 | 31.3 ± 4.1 | 17.0 ± 7.7 | 0.4 ± 0.6 | 0.14 ± 0.10 | 0.04 ± 0.08 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| M4 ATT+bal-2L (fixed tokenizer) | 1% | 10 | 74.6 ± 2.4 | 61.3 ± 3.6 | 58.3 ± 3.9 | 50.2 ± 5.4 | 10.6 ± 8.5 | 0.74 ± 0.33 | 1.00 ± 0.66 | 0.94 ± 0.75 | 0.42 ± 0.50 |
| M4 ATT+bal-2L (fixed tokenizer) | 0.1% | 10 | 41.8 ± 13.2 | 30.8 ± 12.6 | 27.0 ± 11.3 | 17.4 ± 9.0 | 1.5 ± 1.4 | 0.12 ± 0.19 | 0.08 ± 0.14 | 0.14 ± 0.21 | 0.02 ± 0.06 |

