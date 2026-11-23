### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M1 Nebula | M3 ATT+bal | M4 ATT+bal-2L | R1 windowed M3 |
|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.0 ± 1.9 | 77.9 ± 1.7 | 73.6 ± 1.5 |
| random 20 prepend | 25.4 ± 7.8 | 76.2 ± 2.3 | 74.4 ± 3.0 | 70.8 ± 1.3 |
| random 50 prepend | 7.4 ± 4.0 | 65.1 ± 5.8 | 67.2 ± 4.9 | 69.9 ± 2.8 |
| random 100 prepend | 5.7 ± 5.1 | 6.5 ± 1.3 | 25.9 ± 15.4 | 69.3 ± 1.7 |
| random 200 insert | 18.9 ± 5.9 | 44.3 ± 4.0 | 37.5 ± 7.8 | 50.5 ± 6.2 |
| lgbm 50 prepend | 1.9 ± 2.6 | 35.1 ± 13.3 | 48.5 ± 7.7 | 65.4 ± 3.7 |
| white-box 20 steps | 1.6 ± 1.6 | 48.7 ± 6.3 | 50.2 ± 5.4 | 53.0 ± 1.9 |
| white-box 50 steps | 0.6 ± 1.2 | 2.5 ± 1.3 | 10.6 ± 8.5 | 49.5 ± 2.9 |
| padded-benign FPR (%), random 50 prepend | 1.07 ± 1.96 | 0.84 ± 0.52 | 0.49 ± 0.14 | 1.09 ± 0.40 |
