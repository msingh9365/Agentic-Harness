### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M3 ATT+bal | M3 + test-time multi-window max | R1 windowed M3 |
|---|---|---|---|
| unedited | 79.0 ± 1.9 | 71.8 ± 3.3 | 73.6 ± 1.5 |
| random 20 prepend | 76.2 ± 2.3 | 69.4 ± 2.8 | 70.8 ± 1.3 |
| random 50 prepend | 65.1 ± 5.8 | 58.1 ± 6.3 | 69.9 ± 2.8 |
| random 60 prepend | 51.9 ± 9.4 | 56.7 ± 5.6 | 68.0 ± 3.0 |
| random 75 prepend | 21.5 ± 8.3 | 64.5 ± 2.8 | 68.1 ± 1.8 |
| random 100 prepend | 6.5 ± 1.3 | 68.3 ± 2.7 | 69.3 ± 1.7 |
| random 200 prepend | 6.4 ± 1.2 | 65.4 ± 3.9 | 69.9 ± 2.8 |
| random 20 insert | 74.5 ± 2.1 | 61.5 ± 3.4 | 68.7 ± 1.5 |
| random 50 insert | 68.5 ± 2.8 | 55.4 ± 3.4 | 65.7 ± 2.6 |
| random 200 insert | 44.3 ± 4.0 | 38.4 ± 4.5 | 50.5 ± 6.2 |
| lgbm 50 prepend | 35.1 ± 13.3 | 58.0 ± 4.0 | 65.4 ± 3.7 |
| lgbm 50 insert | 54.7 ± 2.9 | 44.3 ± 4.0 | 55.8 ± 3.1 |
| adaptive 50 every window | 65.1 ± 5.7 | 53.8 ± 9.9 | 64.0 ± 6.0 |
| padded-benign FPR (%), random 20 prepend | 1.12 ± 0.22 | 1.23 ± 0.28 | 1.35 ± 0.50 |
| padded-benign FPR (%), random 50 prepend | 0.84 ± 0.52 | 1.33 ± 0.95 | 1.09 ± 0.40 |
| padded-benign FPR (%), random 60 prepend | 0.59 ± 0.49 | 1.13 ± 0.37 | 0.96 ± 0.26 |
| padded-benign FPR (%), random 75 prepend | 0.40 ± 0.43 | 1.23 ± 0.37 | 0.98 ± 0.27 |
| padded-benign FPR (%), random 100 prepend | 0.30 ± 0.37 | 1.11 ± 0.21 | 0.98 ± 0.29 |
| padded-benign FPR (%), random 200 prepend | 0.29 ± 0.35 | 1.36 ± 0.36 | 1.15 ± 0.31 |
| padded-benign FPR (%), random 20 insert | 0.95 ± 0.25 | 1.11 ± 0.25 | 1.04 ± 0.41 |
| padded-benign FPR (%), random 50 insert | 0.68 ± 0.35 | 0.96 ± 0.27 | 0.84 ± 0.27 |
| padded-benign FPR (%), random 200 insert | 0.44 ± 0.37 | 0.62 ± 0.27 | 0.69 ± 0.36 |
| padded-benign FPR (%), lgbm 50 prepend | 0.06 ± 0.06 | 0.92 ± 0.18 | 0.89 ± 0.43 |
| padded-benign FPR (%), lgbm 50 insert | 0.16 ± 0.06 | 0.46 ± 0.14 | 0.39 ± 0.14 |
| padded-benign FPR (%), adaptive 50 every window | 0.94 ± 0.61 | 0.42 ± 0.24 | 0.55 ± 0.35 |
