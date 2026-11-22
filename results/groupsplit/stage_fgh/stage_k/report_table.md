### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 77.2 ± 4.9 | 79.0 ± 1.9 | 77.9 ± 1.7 |
| random 20 prepend | 25.4 ± 7.8 | 54.2 ± 8.0 | 76.2 ± 2.3 | 74.4 ± 3.0 |
| random 50 prepend | 7.4 ± 4.0 | 28.5 ± 12.0 | 65.1 ± 5.8 | 67.2 ± 4.9 |
| random 60 prepend | 5.8 ± 3.5 | 22.8 ± 14.8 | 51.9 ± 9.4 | 60.8 ± 6.2 |
| random 75 prepend | 5.4 ± 4.0 | 20.7 ± 17.0 | 21.5 ± 8.3 | 41.0 ± 11.4 |
| random 100 prepend | 5.7 ± 5.1 | 17.1 ± 13.6 | 6.5 ± 1.3 | 25.9 ± 15.4 |
| random 20 insert | 55.2 ± 6.6 | 55.0 ± 6.4 | 74.5 ± 2.1 | 72.5 ± 2.7 |
| random 50 insert | 42.1 ± 6.9 | 43.2 ± 7.3 | 68.5 ± 2.8 | 65.0 ± 4.1 |
| random 60 insert | 38.9 ± 7.0 | 39.8 ± 7.3 | 66.2 ± 3.1 | 62.7 ± 4.9 |
| random 75 insert | 35.4 ± 6.7 | 34.9 ± 7.1 | 61.9 ± 3.4 | 56.6 ± 6.7 |
| random 100 insert | 30.3 ± 6.3 | 29.5 ± 6.6 | 55.3 ± 3.6 | 52.4 ± 6.0 |
| padded-benign FPR (%), random 20 prepend | 1.29 ± 1.38 | 0.22 ± 0.15 | 1.12 ± 0.22 | 0.94 ± 0.25 |
| padded-benign FPR (%), random 50 prepend | 1.07 ± 1.96 | 0.05 ± 0.08 | 0.84 ± 0.52 | 0.49 ± 0.14 |
| padded-benign FPR (%), random 60 prepend | 1.16 ± 2.46 | 0.04 ± 0.08 | 0.59 ± 0.49 | 0.34 ± 0.16 |
| padded-benign FPR (%), random 75 prepend | 1.61 ± 3.69 | 0.06 ± 0.10 | 0.40 ± 0.43 | 0.13 ± 0.11 |
| padded-benign FPR (%), random 100 prepend | 1.39 ± 3.34 | 0.03 ± 0.05 | 0.30 ± 0.37 | 0.04 ± 0.05 |
| padded-benign FPR (%), random 20 insert | 0.69 ± 0.29 | 0.21 ± 0.11 | 0.95 ± 0.25 | 0.73 ± 0.26 |
| padded-benign FPR (%), random 50 insert | 0.55 ± 0.59 | 0.07 ± 0.06 | 0.68 ± 0.35 | 0.45 ± 0.18 |
| padded-benign FPR (%), random 60 insert | 0.61 ± 0.81 | 0.05 ± 0.04 | 0.57 ± 0.29 | 0.38 ± 0.16 |
| padded-benign FPR (%), random 75 insert | 0.69 ± 1.25 | 0.06 ± 0.07 | 0.46 ± 0.30 | 0.20 ± 0.12 |
| padded-benign FPR (%), random 100 insert | 0.71 ± 1.45 | 0.02 ± 0.02 | 0.50 ± 0.31 | 0.09 ± 0.05 |
