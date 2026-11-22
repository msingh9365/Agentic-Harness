### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M1 Nebula (final) | M1 + dedupe (exact) | M1 + dedupe (name) | M1 + multi-window | M3 ATT+bal (final) | M3 + dedupe (exact) | M3 + dedupe (name) | M3 + multi-window |
|---|---|---|---|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.1 ± 1.9 | 57.7 ± 4.7 | 61.0 ± 10.8 | 79.0 ± 1.9 | 79.1 ± 1.8 | 64.6 ± 3.3 | 71.8 ± 3.3 |
| random 20 prepend | 25.4 ± 7.8 | 25.1 ± 8.0 | 22.8 ± 7.4 | 22.7 ± 8.7 | 76.2 ± 2.3 | 76.2 ± 2.2 | 61.6 ± 3.1 | 69.4 ± 2.8 |
| random 50 prepend | 7.4 ± 4.0 | 7.4 ± 4.1 | 7.1 ± 3.5 | 29.5 ± 8.6 | 65.1 ± 5.8 | 65.2 ± 5.7 | 51.1 ± 5.4 | 58.1 ± 6.3 |
| random 100 prepend | 5.7 ± 5.1 | 5.6 ± 4.9 | 5.1 ± 4.3 | 23.2 ± 9.0 | 6.5 ± 1.3 | 6.5 ± 1.3 | 5.7 ± 1.6 | 68.3 ± 2.7 |
| lgbm 50 prepend | 1.9 ± 2.6 | 1.9 ± 2.6 | 1.9 ± 2.5 | 32.2 ± 9.9 | 35.1 ± 13.3 | 35.1 ± 13.2 | 22.3 ± 10.0 | 58.0 ± 4.0 |
| padded-benign FPR (%), random 20 prepend | 1.29 ± 1.38 | 1.24 ± 1.30 | 1.03 ± 0.83 | 1.43 ± 0.80 | 1.12 ± 0.22 | 1.12 ± 0.21 | 0.82 ± 0.15 | 1.23 ± 0.28 |
| padded-benign FPR (%), random 50 prepend | 1.07 ± 1.96 | 1.02 ± 1.85 | 0.78 ± 1.42 | 1.17 ± 0.56 | 0.84 ± 0.52 | 0.85 ± 0.53 | 0.36 ± 0.21 | 1.33 ± 0.95 |
| padded-benign FPR (%), random 100 prepend | 1.39 ± 3.34 | 1.32 ± 3.16 | 0.95 ± 2.23 | 1.42 ± 0.70 | 0.30 ± 0.37 | 0.31 ± 0.39 | 0.14 ± 0.25 | 1.11 ± 0.21 |
| padded-benign FPR (%), lgbm 50 prepend | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 1.52 ± 1.45 | 0.06 ± 0.06 | 0.06 ± 0.06 | 0.03 ± 0.05 | 0.92 ± 0.18 |
