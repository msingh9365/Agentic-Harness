### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.0 ± 1.9 | 77.9 ± 1.7 | 73.6 ± 1.5 |
| random 20 prepend | 25.4 ± 7.8 | 76.2 ± 2.3 | 74.4 ± 3.0 | 70.8 ± 1.3 |
| random 50 prepend | 7.4 ± 4.0 | 65.1 ± 5.8 | 67.2 ± 4.9 | 69.9 ± 2.8 |
| random 60 prepend | 5.8 ± 3.5 | 51.9 ± 9.4 | 60.8 ± 6.2 | 68.0 ± 3.0 |
| random 75 prepend | 5.4 ± 4.0 | 21.5 ± 8.3 | 41.0 ± 11.4 | 68.1 ± 1.8 |
| random 100 prepend | 5.7 ± 5.1 | 6.5 ± 1.3 | 25.9 ± 15.4 | 69.3 ± 1.7 |
| random 200 prepend | 5.7 ± 5.1 | 6.4 ± 1.2 | 8.2 ± 8.7 | 69.9 ± 2.8 |
| random 20 insert | 55.2 ± 6.6 | 74.5 ± 2.1 | 72.5 ± 2.7 | 68.7 ± 1.5 |
| random 50 insert | 42.1 ± 6.9 | 68.5 ± 2.8 | 65.0 ± 4.1 | 65.7 ± 2.6 |
| random 200 insert | 18.9 ± 5.9 | 44.3 ± 4.0 | 37.5 ± 7.8 | 50.5 ± 6.2 |
| lgbm 50 prepend | 1.9 ± 2.6 | 35.1 ± 13.3 | 48.5 ± 7.7 | 65.4 ± 3.7 |
| lgbm 50 insert | 25.4 ± 6.8 | 54.7 ± 2.9 | 47.5 ± 5.8 | 55.8 ± 3.1 |
| padded-benign FPR (%), random 20 prepend | 1.29 ± 1.38 | 1.12 ± 0.22 | 0.94 ± 0.25 | 1.35 ± 0.50 |
| padded-benign FPR (%), random 50 prepend | 1.07 ± 1.96 | 0.84 ± 0.52 | 0.49 ± 0.14 | 1.09 ± 0.40 |
| padded-benign FPR (%), random 60 prepend | 1.16 ± 2.46 | 0.59 ± 0.49 | 0.34 ± 0.16 | 0.96 ± 0.26 |
| padded-benign FPR (%), random 75 prepend | 1.61 ± 3.69 | 0.40 ± 0.43 | 0.13 ± 0.11 | 0.98 ± 0.27 |
| padded-benign FPR (%), random 100 prepend | 1.39 ± 3.34 | 0.30 ± 0.37 | 0.04 ± 0.05 | 0.98 ± 0.29 |
| padded-benign FPR (%), random 200 prepend | 1.43 ± 3.27 | 0.29 ± 0.35 | 0.00 ± 0.01 | 1.15 ± 0.31 |
| padded-benign FPR (%), random 20 insert | 0.69 ± 0.29 | 0.95 ± 0.25 | 0.73 ± 0.26 | 1.04 ± 0.41 |
| padded-benign FPR (%), random 50 insert | 0.55 ± 0.59 | 0.68 ± 0.35 | 0.45 ± 0.18 | 0.84 ± 0.27 |
| padded-benign FPR (%), random 200 insert | 0.84 ± 1.81 | 0.44 ± 0.37 | 0.02 ± 0.02 | 0.69 ± 0.36 |
| padded-benign FPR (%), lgbm 50 prepend | 0.00 ± 0.00 | 0.06 ± 0.06 | 0.06 ± 0.05 | 0.89 ± 0.43 |
| padded-benign FPR (%), lgbm 50 insert | 0.07 ± 0.09 | 0.16 ± 0.06 | 0.04 ± 0.02 | 0.39 ± 0.14 |
