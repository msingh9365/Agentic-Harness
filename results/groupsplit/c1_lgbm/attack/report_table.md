### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M1 Nebula | M3 ATT+bal | LightGBM bag of API names |
|---|---|---|---|
| unedited | 79.1 ± 2.0 | 79.0 ± 1.9 | 54.8 ± 0.0 |
| random 20 prepend | 25.4 ± 7.8 | 76.2 ± 2.3 | 24.4 ± 0.0 |
| random 50 prepend | 7.4 ± 4.0 | 65.1 ± 5.8 | 9.9 ± 0.0 |
| random 100 prepend | 5.7 ± 5.1 | 6.5 ± 1.3 | 3.1 ± 0.0 |
| random 200 insert | 18.9 ± 5.9 | 44.3 ± 4.0 | 0.5 ± 0.0 |
| lgbm 50 prepend | 1.9 ± 2.6 | 35.1 ± 13.3 | 0.0 ± 0.0 |
| padded-benign FPR (%), random 20 prepend | 1.29 ± 1.38 | 1.12 ± 0.22 | 0.19 ± 0.00 |
| padded-benign FPR (%), random 50 prepend | 1.07 ± 1.96 | 0.84 ± 0.52 | 0.05 ± 0.00 |
| padded-benign FPR (%), random 100 prepend | 1.39 ± 3.34 | 0.30 ± 0.37 | 0.00 ± 0.00 |
| padded-benign FPR (%), random 200 insert | 0.84 ± 1.81 | 0.44 ± 0.37 | 0.00 ± 0.00 |
| padded-benign FPR (%), lgbm 50 prepend | 0.00 ± 0.00 | 0.06 ± 0.06 | 0.00 ± 0.00 |
