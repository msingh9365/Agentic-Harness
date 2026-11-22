### Attacks on the four final models (fixed tokenizer) (April, all reports edited; seeds present: m1: 10, m2: 10, m3: 10, m4: 10)

**Detection of malware after the edit, threshold at 1% FPR of the clean April benign scores (%)**

| edit set | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 77.2 ± 4.9 | 79.0 ± 1.9 | 77.9 ± 1.7 |
| random_20_prepend | 25.4 ± 7.8 | 54.2 ± 8.0 | 76.2 ± 2.3 | 74.4 ± 3.0 |
| random_50_prepend | 7.4 ± 4.0 | 28.5 ± 12.0 | 65.1 ± 5.8 | 67.2 ± 4.9 |
| random_60_prepend | 5.8 ± 3.5 | 22.8 ± 14.8 | 51.9 ± 9.4 | 60.8 ± 6.2 |
| random_75_prepend | 5.4 ± 4.0 | 20.7 ± 17.0 | 21.5 ± 8.3 | 41.0 ± 11.4 |
| random_100_prepend | 5.7 ± 5.1 | 17.1 ± 13.6 | 6.5 ± 1.3 | 25.9 ± 15.4 |
| random_20_insert | 55.2 ± 6.6 | 55.0 ± 6.4 | 74.5 ± 2.1 | 72.5 ± 2.7 |
| random_50_insert | 42.1 ± 6.9 | 43.2 ± 7.3 | 68.5 ± 2.8 | 65.0 ± 4.1 |
| random_60_insert | 38.9 ± 7.0 | 39.8 ± 7.3 | 66.2 ± 3.1 | 62.7 ± 4.9 |
| random_75_insert | 35.4 ± 6.7 | 34.9 ± 7.1 | 61.9 ± 3.4 | 56.6 ± 6.7 |
| random_100_insert | 30.3 ± 6.3 | 29.5 ± 6.6 | 55.3 ± 3.6 | 52.4 ± 6.0 |

**Padded-benign FPR after the same edit, threshold at 1% FPR (%) (clean benign: 1% by construction)**

| edit set | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.01 |
| random_20_prepend | 1.29 ± 1.38 | 0.22 ± 0.15 | 1.12 ± 0.22 | 0.94 ± 0.25 |
| random_50_prepend | 1.07 ± 1.96 | 0.05 ± 0.08 | 0.84 ± 0.52 | 0.49 ± 0.14 |
| random_60_prepend | 1.16 ± 2.46 | 0.04 ± 0.08 | 0.59 ± 0.49 | 0.34 ± 0.16 |
| random_75_prepend | 1.61 ± 3.69 | 0.06 ± 0.10 | 0.40 ± 0.43 | 0.13 ± 0.11 |
| random_100_prepend | 1.39 ± 3.34 | 0.03 ± 0.05 | 0.30 ± 0.37 | 0.04 ± 0.05 |
| random_20_insert | 0.69 ± 0.29 | 0.21 ± 0.11 | 0.95 ± 0.25 | 0.73 ± 0.26 |
| random_50_insert | 0.55 ± 0.59 | 0.07 ± 0.06 | 0.68 ± 0.35 | 0.45 ± 0.18 |
| random_60_insert | 0.61 ± 0.81 | 0.05 ± 0.04 | 0.57 ± 0.29 | 0.38 ± 0.16 |
| random_75_insert | 0.69 ± 1.25 | 0.06 ± 0.07 | 0.46 ± 0.30 | 0.20 ± 0.12 |
| random_100_insert | 0.71 ± 1.45 | 0.02 ± 0.02 | 0.50 ± 0.31 | 0.09 ± 0.05 |

**Detection of malware after the edit, threshold at 0.1% FPR of the clean April benign scores (%)**

| edit set | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 53.6 ± 6.0 | 38.1 ± 16.5 | 56.7 ± 4.7 | 45.3 ± 14.9 |
| random_20_prepend | 7.2 ± 4.6 | 17.4 ± 10.5 | 50.5 ± 7.3 | 44.2 ± 13.9 |
| random_50_prepend | 1.3 ± 1.7 | 1.1 ± 1.8 | 28.1 ± 8.8 | 38.1 ± 13.0 |
| random_60_prepend | 1.0 ± 1.6 | 0.2 ± 0.6 | 12.6 ± 6.4 | 28.6 ± 12.0 |
| random_75_prepend | 1.0 ± 1.7 | 0.2 ± 0.5 | 2.3 ± 1.2 | 12.3 ± 6.3 |
| random_100_prepend | 1.0 ± 1.8 | 0.1 ± 0.4 | 1.9 ± 0.9 | 5.2 ± 3.4 |
| random_20_insert | 26.8 ± 7.9 | 19.9 ± 9.5 | 43.8 ± 4.4 | 40.4 ± 11.9 |
| random_50_insert | 16.2 ± 5.7 | 10.4 ± 5.8 | 36.1 ± 4.5 | 34.8 ± 11.8 |
| random_60_insert | 14.1 ± 5.0 | 8.2 ± 4.9 | 34.4 ± 4.5 | 32.3 ± 11.8 |
| random_75_insert | 12.0 ± 4.4 | 6.0 ± 4.2 | 32.1 ± 4.0 | 27.0 ± 10.8 |
| random_100_insert | 9.4 ± 3.8 | 3.3 ± 2.7 | 29.4 ± 3.1 | 21.5 ± 10.5 |

**Padded-benign FPR after the same edit, threshold at 0.1% FPR (%) (clean benign: 0.1% by construction)**

| edit set | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 |
| random_20_prepend | 0.02 ± 0.02 | 0.00 ± 0.01 | 0.04 ± 0.02 | 0.07 ± 0.04 |
| random_50_prepend | 0.02 ± 0.04 | 0.00 ± 0.00 | 0.00 ± 0.01 | 0.03 ± 0.01 |
| random_60_prepend | 0.01 ± 0.03 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.01 ± 0.01 |
| random_75_prepend | 0.03 ± 0.09 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.01 |
| random_100_prepend | 0.02 ± 0.07 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| random_20_insert | 0.02 ± 0.02 | 0.00 ± 0.01 | 0.03 ± 0.01 | 0.05 ± 0.03 |
| random_50_insert | 0.01 ± 0.02 | 0.00 ± 0.00 | 0.01 ± 0.01 | 0.02 ± 0.01 |
| random_60_insert | 0.01 ± 0.01 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.02 ± 0.01 |
| random_75_insert | 0.00 ± 0.01 | 0.00 ± 0.00 | 0.01 ± 0.01 | 0.00 ± 0.01 |
| random_100_insert | 0.00 ± 0.01 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.01 ± 0.01 |

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
| M1 v2-PE (fixed tokenizer) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 v2-PE (fixed tokenizer) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M2 two-level, no padding (fixed tokenizer) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M2 two-level, no padding (fixed tokenizer) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal (fixed tokenizer) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal (fixed tokenizer) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M4 ATT+bal-2L (fixed tokenizer) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M4 ATT+bal-2L (fixed tokenizer) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

