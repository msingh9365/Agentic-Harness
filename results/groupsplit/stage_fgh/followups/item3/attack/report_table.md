### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | flatten, none | attention, none | flatten, balanced | attention, balanced |
|---|---|---|---|---|
| unedited | 79.6 ± 3.0 | 74.9 ± 9.6 | 77.5 ± 2.1 | 78.1 ± 1.0 |
| random 20 prepend | 17.9 ± 5.8 | 47.4 ± 17.6 | 70.1 ± 2.9 | 75.4 ± 1.6 |
| random 50 prepend | 12.9 ± 5.0 | 10.3 ± 11.6 | 48.4 ± 6.4 | 63.4 ± 3.1 |
| lgbm 50 prepend | 6.2 ± 1.6 | 0.7 ± 1.3 | 3.1 ± 3.4 | 44.6 ± 9.5 |
| padded-benign FPR (%), random 20 prepend | 3.91 ± 3.65 | 0.35 ± 0.21 | 1.36 ± 0.57 | 1.11 ± 0.18 |
| padded-benign FPR (%), random 50 prepend | 5.44 ± 4.37 | 0.05 ± 0.07 | 1.34 ± 0.68 | 0.76 ± 0.20 |
| padded-benign FPR (%), lgbm 50 prepend | 0.01 ± 0.02 | 0.00 ± 0.00 | 0.01 ± 0.02 | 0.13 ± 0.13 |
