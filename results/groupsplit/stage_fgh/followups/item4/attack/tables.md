### Attacks on the four final models (April, all reports edited; seeds present: m1: 10, y_fm: 10, m3: 10, y_am: 10)

**Detection of malware after the edit, threshold at 1% FPR of the clean April benign scores (%)**

| edit set | M1 Nebula (no padding) | M1 settings + malware-only padding | M3 ATT+bal (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.3 ± 3.1 | 79.0 ± 1.9 | 78.7 ± 1.8 |
| random_5_prepend | 54.8 ± 7.5 | 88.8 ± 3.7 | 79.0 ± 2.0 | 85.4 ± 1.7 |
| random_20_prepend | 25.4 ± 7.8 | 97.2 ± 1.6 | 76.2 ± 2.3 | 90.6 ± 2.0 |
| random_50_prepend | 7.4 ± 4.0 | 98.6 ± 0.9 | 65.1 ± 5.8 | 94.2 ± 1.9 |
| random_5_insert | 71.4 ± 3.5 | 82.2 ± 2.9 | 77.5 ± 2.1 | 82.2 ± 1.8 |
| random_20_insert | 55.2 ± 6.6 | 86.6 ± 2.9 | 74.5 ± 2.1 | 85.6 ± 2.0 |
| random_50_insert | 42.1 ± 6.9 | 90.8 ± 2.6 | 68.5 ± 2.8 | 87.8 ± 2.3 |

**Padded-benign FPR after the same edit, threshold at 1% FPR (%) (clean benign: 1% by construction)**

| edit set | M1 Nebula (no padding) | M1 settings + malware-only padding | M3 ATT+bal (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 |
| random_5_prepend | 0.91 ± 0.40 | 30.11 ± 13.88 | 1.03 ± 0.10 | 20.41 ± 4.20 |
| random_20_prepend | 1.29 ± 1.38 | 86.27 ± 10.21 | 1.12 ± 0.22 | 46.92 ± 6.67 |
| random_50_prepend | 1.07 ± 1.96 | 97.73 ± 1.92 | 0.84 ± 0.52 | 82.42 ± 5.85 |
| random_5_insert | 0.87 ± 0.19 | 11.00 ± 3.54 | 1.08 ± 0.09 | 13.07 ± 2.30 |
| random_20_insert | 0.69 ± 0.29 | 33.40 ± 5.47 | 0.95 ± 0.25 | 29.49 ± 2.52 |
| random_50_insert | 0.55 ± 0.59 | 50.30 ± 5.88 | 0.68 ± 0.35 | 42.46 ± 3.75 |

**Detection of malware after the edit, threshold at 0.1% FPR of the clean April benign scores (%)**

| edit set | M1 Nebula (no padding) | M1 settings + malware-only padding | M3 ATT+bal (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 53.6 ± 6.0 | 56.5 ± 9.5 | 56.7 ± 4.7 | 55.3 ± 9.0 |
| random_5_prepend | 24.7 ± 8.7 | 64.3 ± 6.5 | 50.8 ± 5.2 | 63.0 ± 8.6 |
| random_20_prepend | 7.2 ± 4.6 | 80.5 ± 8.7 | 50.5 ± 7.3 | 67.2 ± 8.4 |
| random_50_prepend | 1.3 ± 1.7 | 86.8 ± 6.6 | 28.1 ± 8.8 | 57.1 ± 14.4 |
| random_5_insert | 41.6 ± 7.2 | 57.2 ± 8.5 | 51.5 ± 4.9 | 57.6 ± 10.5 |
| random_20_insert | 26.8 ± 7.9 | 64.4 ± 8.5 | 43.8 ± 4.4 | 57.5 ± 12.3 |
| random_50_insert | 16.2 ± 5.7 | 71.9 ± 7.8 | 36.1 ± 4.5 | 57.9 ± 13.0 |

**Padded-benign FPR after the same edit, threshold at 0.1% FPR (%) (clean benign: 0.1% by construction)**

| edit set | M1 Nebula (no padding) | M1 settings + malware-only padding | M3 ATT+bal (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|
| unedited | 0.10 ± 0.00 | 0.10 ± 0.01 | 0.10 ± 0.00 | 0.10 ± 0.00 |
| random_5_prepend | 0.03 ± 0.02 | 3.20 ± 3.29 | 0.07 ± 0.02 | 7.60 ± 2.38 |
| random_20_prepend | 0.02 ± 0.02 | 43.82 ± 19.87 | 0.04 ± 0.02 | 14.67 ± 4.26 |
| random_50_prepend | 0.02 ± 0.04 | 78.93 ± 14.42 | 0.00 ± 0.01 | 27.03 ± 12.36 |
| random_5_insert | 0.03 ± 0.02 | 0.87 ± 0.71 | 0.06 ± 0.02 | 5.26 ± 1.77 |
| random_20_insert | 0.02 ± 0.02 | 11.31 ± 4.93 | 0.03 ± 0.01 | 12.11 ± 3.16 |
| random_50_insert | 0.01 ± 0.02 | 29.10 ± 5.27 | 0.01 ± 0.01 | 13.28 ± 5.41 |

**Detection per family under random padding k = 50 prepended (1% threshold; in brackets the unedited detection) (%)**

| family | n | M1 Nebula (no padding) | M1 settings + malware-only padding | M3 ATT+bal (balanced padding) | M3 settings + malware-only padding |
|---|---|---|---|---|---|
| backdoor | 1940 | 25.3 ± 9.2 (clean 82.7 ± 1.6) | 99.0 ± 0.4 (clean 83.0 ± 3.1) | 68.2 ± 2.9 (clean 81.0 ± 0.9) | 95.5 ± 1.7 (clean 82.0 ± 1.1) |
| coinminer | 1684 | 2.4 ± 3.1 (clean 80.2 ± 7.5) | 98.7 ± 0.9 (clean 80.8 ± 8.1) | 65.6 ± 6.7 (clean 71.9 ± 6.7) | 95.2 ± 1.8 (clean 72.0 ± 6.0) |
| dropper | 252 | 3.7 ± 4.0 (clean 75.0 ± 4.6) | 99.0 ± 0.8 (clean 77.3 ± 2.8) | 63.7 ± 9.6 (clean 83.5 ± 1.0) | 94.8 ± 2.1 (clean 83.6 ± 2.3) |
| keylogger | 1041 | 1.2 ± 1.1 (clean 86.3 ± 5.1) | 98.0 ± 1.6 (clean 84.0 ± 7.5) | 74.0 ± 7.8 (clean 88.7 ± 2.0) | 95.9 ± 1.5 (clean 84.8 ± 4.6) |
| ransomware | 2139 | 3.6 ± 4.1 (clean 67.0 ± 5.2) | 98.7 ± 0.9 (clean 69.7 ± 5.0) | 50.2 ± 7.0 (clean 72.2 ± 3.1) | 91.2 ± 3.1 (clean 70.9 ± 3.4) |
| rat | 1258 | 1.2 ± 1.4 (clean 88.2 ± 2.0) | 98.7 ± 0.7 (clean 85.2 ± 3.2) | 74.7 ± 6.5 (clean 86.8 ± 0.9) | 95.5 ± 1.4 (clean 87.0 ± 1.1) |
| trojan | 1085 | 4.8 ± 6.4 (clean 78.6 ± 3.9) | 98.1 ± 1.7 (clean 78.5 ± 2.5) | 68.5 ± 5.5 (clean 80.8 ± 1.3) | 93.3 ± 2.4 (clean 81.7 ± 1.0) |

**White-box greedy attack (500 April malware, 200 candidates per step, prepend, up to 50 steps): share still flagged after k steps (%) and padded-benign FPR after k steps (%)**

| model | threshold | seeds | k = 0 | k = 5 | k = 10 | k = 20 | k = 50 | FPR k = 5 | FPR k = 10 | FPR k = 20 | FPR k = 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 Nebula (no padding) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 Nebula (no padding) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 settings + malware-only padding | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 settings + malware-only padding | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal (balanced padding) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal (balanced padding) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 settings + malware-only padding | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 settings + malware-only padding | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

