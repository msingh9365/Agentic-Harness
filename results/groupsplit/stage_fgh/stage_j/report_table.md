### Detection of April malware (%) at the 1% clean-FPR threshold, mean ± std over 10 seeds; last row: padded-benign false-positive rate (%)

| row | M1 v2-PE (fixed tokenizer) | M2 two-level, no padding (fixed tokenizer) | M3 ATT+bal (fixed tokenizer) | M4 ATT+bal-2L (fixed tokenizer) |
|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 77.2 ± 4.9 | 79.0 ± 1.9 | 77.9 ± 1.7 |
| random 20 prepend | 25.4 ± 7.8 | 54.2 ± 8.0 | 76.2 ± 2.3 | 74.4 ± 3.0 |
| random 50 prepend | 7.4 ± 4.0 | 28.5 ± 12.0 | 65.1 ± 5.8 | 67.2 ± 4.9 |
| random 100 prepend | 5.7 ± 5.1 | 17.1 ± 13.6 | 6.5 ± 1.3 | 25.9 ± 15.4 |
| random 200 insert | 18.9 ± 5.9 | 12.4 ± 4.7 | 44.3 ± 4.0 | 37.5 ± 7.8 |
| lgbm 50 prepend | 1.9 ± 2.6 | 17.2 ± 15.2 | 35.1 ± 13.3 | 48.5 ± 7.7 |
| white-box 20 steps | 1.6 ± 1.6 | 19.6 ± 13.3 | 48.7 ± 6.3 | 50.2 ± 5.4 |
| white-box 50 steps | 0.6 ± 1.2 | 13.8 ± 13.6 | 2.5 ± 1.3 | 10.6 ± 8.5 |
| padded-benign FPR (%), random 50 prepend | 1.07 ± 1.96 | 0.05 ± 0.08 | 0.84 ± 0.52 | 0.49 ± 0.14 |
