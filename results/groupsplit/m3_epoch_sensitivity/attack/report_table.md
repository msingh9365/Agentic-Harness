### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M1 Nebula | M3 ATT+bal, 3 epochs | M3 ATT+bal, 2 epochs |
|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.0 ± 1.9 | 78.9 ± 0.7 |
| random 20 prepend | 25.4 ± 7.8 | 76.2 ± 2.3 | 75.9 ± 1.2 |
| random 50 prepend | 7.4 ± 4.0 | 65.1 ± 5.8 | 64.2 ± 4.5 |
| random 100 prepend | 5.7 ± 5.1 | 6.5 ± 1.3 | 6.1 ± 2.1 |
| random 200 insert | 18.9 ± 5.9 | 44.3 ± 4.0 | 46.5 ± 4.8 |
| lgbm 50 prepend | 1.9 ± 2.6 | 35.1 ± 13.3 | 38.8 ± 13.4 |
| white-box 20 steps | 1.6 ± 1.6 | 48.7 ± 6.3 | 49.9 ± 5.0 |
| white-box 50 steps | 0.6 ± 1.2 | 2.5 ± 1.3 | 1.9 ± 1.4 |
| padded-benign FPR (%), random 50 prepend | 1.07 ± 1.96 | 0.84 ± 0.52 | 1.01 ± 0.84 |
