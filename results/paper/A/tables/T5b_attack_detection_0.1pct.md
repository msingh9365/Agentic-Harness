**Detection (%) of April malware after each edit at the 0.1% false-positive-rate threshold of the unedited April benign scores, mean ± std over 10 seeds (white-box: 500 malware reports).**

| edit | M1 Nebula | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 54.1 ± 9.5 | 34.4 ± 18.9 | 59.0 ± 2.9 | 46.1 ± 17.4 |
| random 5 prepend | 20.2 ± 5.5 | 22.4 ± 12.3 | 53.4 ± 3.6 | 45.0 ± 15.8 |
| random 20 prepend | 6.7 ± 3.0 | 13.6 ± 10.3 | 52.7 ± 4.3 | 42.7 ± 16.5 |
| random 50 prepend | 2.6 ± 2.0 | 0.5 ± 0.6 | 31.4 ± 7.4 | 36.6 ± 14.5 |
| random 100 prepend | 2.0 ± 2.0 | 0.1 ± 0.2 | 2.3 ± 1.2 | 4.7 ± 2.9 |
| random 200 prepend | 2.0 ± 2.0 | 0.0 ± 0.0 | 2.3 ± 1.2 | 0.8 ± 1.5 |
| random 5 insert | 41.0 ± 8.1 | 24.6 ± 13.3 | 53.8 ± 3.1 | 43.3 ± 15.3 |
| random 20 insert | 26.3 ± 6.4 | 16.0 ± 9.3 | 45.1 ± 3.4 | 38.8 ± 13.9 |
| random 50 insert | 15.9 ± 5.6 | 7.2 ± 5.3 | 38.1 ± 3.8 | 32.7 ± 12.0 |
| random 100 insert | 10.2 ± 4.4 | 1.8 ± 1.7 | 30.9 ± 2.7 | 21.2 ± 9.1 |
| random 200 insert | 6.0 ± 3.5 | 0.1 ± 0.2 | 22.8 ± 2.4 | 9.8 ± 6.6 |
| lgbm 20 prepend | 2.9 ± 2.4 | 5.5 ± 6.7 | 47.3 ± 7.5 | 42.6 ± 17.8 |
| lgbm 50 prepend | 1.2 ± 2.2 | 0.1 ± 0.4 | 4.1 ± 4.0 | 23.4 ± 13.2 |
| lgbm 100 prepend | 1.3 ± 2.5 | 0.0 ± 0.1 | 1.9 ± 1.0 | 3.5 ± 2.3 |
| lgbm 20 insert | 15.0 ± 5.7 | 7.5 ± 5.8 | 40.4 ± 3.6 | 33.6 ± 11.2 |
| lgbm 50 insert | 8.0 ± 4.2 | 1.7 ± 1.9 | 29.5 ± 3.2 | 20.5 ± 9.5 |
| lgbm 100 insert | 4.9 ± 3.6 | 0.1 ± 0.2 | 19.7 ± 2.0 | 11.7 ± 6.2 |
| white-box 5 steps | 1.6 ± 1.3 | 8.0 ± 6.8 | 35.3 ± 2.9 | 28.5 ± 15.2 |
| white-box 10 steps | 0.8 ± 1.0 | 3.1 ± 3.1 | 32.9 ± 3.3 | 25.2 ± 15.0 |
| white-box 20 steps | 0.2 ± 0.3 | 0.3 ± 0.6 | 20.9 ± 6.2 | 17.0 ± 12.2 |
| white-box 50 steps | 0.1 ± 0.3 | 0.0 ± 0.0 | 0.6 ± 0.6 | 1.1 ± 1.6 |
