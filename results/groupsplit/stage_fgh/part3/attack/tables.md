### Attacks on the four final models (April, all reports edited; seeds present: m1: 10, m1_dx: 10, m1_dn: 10, m1_mw: 10, m3: 10, m3_dx: 10, m3_dn: 10, m3_mw: 10)

**Detection of malware after the edit, threshold at 1% FPR of the clean April benign scores (%)**

| edit set | M1 Nebula (final) | M1 + dedupe (exact) | M1 + dedupe (name) | M1 + multi-window | M3 ATT+bal (final) | M3 + dedupe (exact) | M3 + dedupe (name) | M3 + multi-window |
|---|---|---|---|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.1 ± 1.9 | 57.7 ± 4.7 | 61.0 ± 10.8 | 79.0 ± 1.9 | 79.1 ± 1.8 | 64.6 ± 3.3 | 71.8 ± 3.3 |
| random_20_prepend | 25.4 ± 7.8 | 25.1 ± 8.0 | 22.8 ± 7.4 | 22.7 ± 8.7 | 76.2 ± 2.3 | 76.2 ± 2.2 | 61.6 ± 3.1 | 69.4 ± 2.8 |
| random_50_prepend | 7.4 ± 4.0 | 7.4 ± 4.1 | 7.1 ± 3.5 | 29.5 ± 8.6 | 65.1 ± 5.8 | 65.2 ± 5.7 | 51.1 ± 5.4 | 58.1 ± 6.3 |
| random_100_prepend | 5.7 ± 5.1 | 5.6 ± 4.9 | 5.1 ± 4.3 | 23.2 ± 9.0 | 6.5 ± 1.3 | 6.5 ± 1.3 | 5.7 ± 1.6 | 68.3 ± 2.7 |
| lgbm_50_prepend | 1.9 ± 2.6 | 1.9 ± 2.6 | 1.9 ± 2.5 | 32.2 ± 9.9 | 35.1 ± 13.3 | 35.1 ± 13.2 | 22.3 ± 10.0 | 58.0 ± 4.0 |

**Padded-benign FPR after the same edit, threshold at 1% FPR (%) (clean benign: 1% by construction)**

| edit set | M1 Nebula (final) | M1 + dedupe (exact) | M1 + dedupe (name) | M1 + multi-window | M3 ATT+bal (final) | M3 + dedupe (exact) | M3 + dedupe (name) | M3 + multi-window |
|---|---|---|---|---|---|---|---|---|
| unedited | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.99 ± 0.02 | 0.98 ± 0.05 | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 | 1.00 ± 0.00 |
| random_20_prepend | 1.29 ± 1.38 | 1.24 ± 1.30 | 1.03 ± 0.83 | 1.43 ± 0.80 | 1.12 ± 0.22 | 1.12 ± 0.21 | 0.82 ± 0.15 | 1.23 ± 0.28 |
| random_50_prepend | 1.07 ± 1.96 | 1.02 ± 1.85 | 0.78 ± 1.42 | 1.17 ± 0.56 | 0.84 ± 0.52 | 0.85 ± 0.53 | 0.36 ± 0.21 | 1.33 ± 0.95 |
| random_100_prepend | 1.39 ± 3.34 | 1.32 ± 3.16 | 0.95 ± 2.23 | 1.42 ± 0.70 | 0.30 ± 0.37 | 0.31 ± 0.39 | 0.14 ± 0.25 | 1.11 ± 0.21 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 1.52 ± 1.45 | 0.06 ± 0.06 | 0.06 ± 0.06 | 0.03 ± 0.05 | 0.92 ± 0.18 |

**Detection of malware after the edit, threshold at 0.1% FPR of the clean April benign scores (%)**

| edit set | M1 Nebula (final) | M1 + dedupe (exact) | M1 + dedupe (name) | M1 + multi-window | M3 ATT+bal (final) | M3 + dedupe (exact) | M3 + dedupe (name) | M3 + multi-window |
|---|---|---|---|---|---|---|---|---|
| unedited | 53.6 ± 6.0 | 53.2 ± 6.0 | 33.5 ± 4.1 | 25.7 ± 9.1 | 56.7 ± 4.7 | 56.8 ± 4.8 | 44.0 ± 4.1 | 44.1 ± 8.4 |
| random_20_prepend | 7.2 ± 4.6 | 7.2 ± 4.5 | 6.6 ± 3.7 | 6.8 ± 4.4 | 50.5 ± 7.3 | 50.7 ± 7.4 | 40.1 ± 4.3 | 36.8 ± 7.0 |
| random_50_prepend | 1.3 ± 1.7 | 1.3 ± 1.7 | 1.7 ± 1.6 | 8.4 ± 5.1 | 28.1 ± 8.8 | 28.5 ± 9.1 | 28.0 ± 6.8 | 26.3 ± 8.1 |
| random_100_prepend | 1.0 ± 1.8 | 1.0 ± 1.8 | 1.2 ± 1.7 | 5.8 ± 3.7 | 1.9 ± 0.9 | 1.9 ± 0.9 | 1.7 ± 0.8 | 35.0 ± 7.8 |
| lgbm_50_prepend | 0.3 ± 1.0 | 0.3 ± 1.0 | 0.3 ± 1.0 | 11.8 ± 6.6 | 3.7 ± 2.9 | 3.7 ± 2.9 | 3.0 ± 2.7 | 24.6 ± 6.2 |

**Padded-benign FPR after the same edit, threshold at 0.1% FPR (%) (clean benign: 0.1% by construction)**

| edit set | M1 Nebula (final) | M1 + dedupe (exact) | M1 + dedupe (name) | M1 + multi-window | M3 ATT+bal (final) | M3 + dedupe (exact) | M3 + dedupe (name) | M3 + multi-window |
|---|---|---|---|---|---|---|---|---|
| unedited | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.09 ± 0.02 | 0.10 ± 0.01 | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 | 0.10 ± 0.00 |
| random_20_prepend | 0.02 ± 0.02 | 0.02 ± 0.01 | 0.03 ± 0.03 | 0.09 ± 0.05 | 0.04 ± 0.02 | 0.04 ± 0.02 | 0.05 ± 0.03 | 0.18 ± 0.06 |
| random_50_prepend | 0.02 ± 0.04 | 0.02 ± 0.04 | 0.02 ± 0.05 | 0.08 ± 0.04 | 0.00 ± 0.01 | 0.00 ± 0.01 | 0.00 ± 0.00 | 0.21 ± 0.09 |
| random_100_prepend | 0.02 ± 0.07 | 0.02 ± 0.07 | 0.02 ± 0.06 | 0.10 ± 0.04 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.16 ± 0.03 |
| lgbm_50_prepend | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.08 ± 0.03 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.15 ± 0.06 |

**Detection per family under random padding k = 50 prepended (1% threshold; in brackets the unedited detection) (%)**

| family | n | M1 Nebula (final) | M1 + dedupe (exact) | M1 + dedupe (name) | M1 + multi-window | M3 ATT+bal (final) | M3 + dedupe (exact) | M3 + dedupe (name) | M3 + multi-window |
|---|---|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 25.3 ± 9.2 (clean 82.7 ± 1.6) | 25.1 ± 9.2 (clean 82.8 ± 1.6) | 24.7 ± 8.7 (clean 71.8 ± 6.2) | 53.4 ± 11.7 (clean 72.8 ± 8.1) | 68.2 ± 2.9 (clean 81.0 ± 0.9) | 68.3 ± 2.8 (clean 80.9 ± 0.9) | 63.6 ± 6.0 (clean 74.9 ± 4.0) | 73.3 ± 3.3 (clean 80.2 ± 4.1) |
| coinminer | 1684 | 2.4 ± 3.1 (clean 80.2 ± 7.5) | 2.5 ± 3.3 (clean 80.1 ± 7.5) | 3.0 ± 3.7 (clean 49.6 ± 11.1) | 32.5 ± 16.1 (clean 60.6 ± 11.0) | 65.6 ± 6.7 (clean 71.9 ± 6.7) | 65.8 ± 6.7 (clean 71.9 ± 6.7) | 44.0 ± 3.8 (clean 66.1 ± 6.3) | 56.5 ± 8.9 (clean 67.8 ± 6.4) |
| dropper | 252 | 3.7 ± 4.0 (clean 75.0 ± 4.6) | 3.8 ± 4.3 (clean 74.9 ± 4.8) | 3.7 ± 4.1 (clean 59.6 ± 8.2) | 14.6 ± 6.2 (clean 53.3 ± 16.0) | 63.7 ± 9.6 (clean 83.5 ± 1.0) | 64.1 ± 9.3 (clean 83.5 ± 1.0) | 58.5 ± 9.0 (clean 74.6 ± 1.3) | 58.0 ± 9.7 (clean 73.2 ± 2.4) |
| keylogger | 1041 | 1.2 ± 1.1 (clean 86.3 ± 5.1) | 1.2 ± 1.1 (clean 86.2 ± 4.9) | 1.0 ± 0.9 (clean 65.7 ± 11.2) | 6.1 ± 2.4 (clean 58.8 ± 18.8) | 74.0 ± 7.8 (clean 88.7 ± 2.0) | 74.3 ± 7.5 (clean 88.8 ± 2.1) | 66.6 ± 4.1 (clean 76.4 ± 2.5) | 67.8 ± 3.9 (clean 76.8 ± 3.0) |
| ransomware | 2139 | 3.6 ± 4.1 (clean 67.0 ± 5.2) | 3.6 ± 4.2 (clean 67.1 ± 5.0) | 3.2 ± 3.5 (clean 55.3 ± 4.9) | 19.4 ± 9.0 (clean 48.3 ± 11.9) | 50.2 ± 7.0 (clean 72.2 ± 3.1) | 50.2 ± 7.0 (clean 72.4 ± 3.1) | 45.4 ± 8.8 (clean 58.0 ± 4.0) | 36.9 ± 7.8 (clean 59.2 ± 4.1) |
| rat | 1258 | 1.2 ± 1.4 (clean 88.2 ± 2.0) | 1.2 ± 1.5 (clean 88.1 ± 2.0) | 0.9 ± 1.2 (clean 29.3 ± 15.9) | 27.3 ± 10.7 (clean 64.8 ± 23.5) | 74.7 ± 6.5 (clean 86.8 ± 0.9) | 74.8 ± 6.4 (clean 86.8 ± 0.9) | 23.4 ± 6.5 (clean 35.0 ± 13.0) | 56.4 ± 14.1 (clean 77.2 ± 8.8) |
| trojan | 1085 | 4.8 ± 6.4 (clean 78.6 ± 3.9) | 4.7 ± 6.4 (clean 78.4 ± 3.9) | 3.8 ± 4.3 (clean 74.2 ± 4.9) | 30.1 ± 13.5 (clean 65.2 ± 11.8) | 68.5 ± 5.5 (clean 80.8 ± 1.3) | 68.5 ± 5.5 (clean 80.7 ± 1.3) | 66.4 ± 4.1 (clean 77.2 ± 1.4) | 67.6 ± 3.2 (clean 76.3 ± 1.3) |

**White-box greedy attack (500 April malware, 200 candidates per step, prepend, up to 50 steps): share still flagged after k steps (%) and padded-benign FPR after k steps (%)**

| model | threshold | seeds | k = 0 | k = 5 | k = 10 | k = 20 | k = 50 | FPR k = 5 | FPR k = 10 | FPR k = 20 | FPR k = 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 Nebula (final) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 Nebula (final) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 + dedupe (exact) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 + dedupe (exact) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 + dedupe (name) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 + dedupe (name) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 + multi-window | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M1 + multi-window | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal (final) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 ATT+bal (final) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 + dedupe (exact) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 + dedupe (exact) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 + dedupe (name) | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 + dedupe (name) | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 + multi-window | 1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| M3 + multi-window | 0.1% | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

