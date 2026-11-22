**Detection (%) of April malware after each edit at the 0.1% false-positive-rate threshold of the unedited April benign scores, mean ± std over 10 seeds (white-box: 500 malware reports; pending = not computed yet).**

| edit | M1 v2-PE | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 53.6 ± 6.0 | 38.1 ± 16.5 | 56.7 ± 4.7 | 45.3 ± 14.9 |
| random 5 prepend | 24.7 ± 8.7 | 26.5 ± 10.7 | 50.8 ± 5.2 | 46.3 ± 13.2 |
| random 20 prepend | 7.2 ± 4.6 | 17.4 ± 10.5 | 50.5 ± 7.3 | 44.2 ± 13.9 |
| random 50 prepend | 1.3 ± 1.7 | 1.1 ± 1.8 | 28.1 ± 8.8 | 38.1 ± 13.0 |
| random 100 prepend | 1.0 ± 1.8 | 0.1 ± 0.4 | 1.9 ± 0.9 | 5.2 ± 3.4 |
| random 200 prepend | 1.0 ± 1.7 | 0.0 ± 0.0 | 1.9 ± 0.9 | 0.3 ± 0.7 |
| random 5 insert | 41.6 ± 7.2 | 27.6 ± 12.4 | 51.5 ± 4.9 | 44.4 ± 13.1 |
| random 20 insert | 26.8 ± 7.9 | 19.9 ± 9.5 | 43.8 ± 4.4 | 40.4 ± 11.9 |
| random 50 insert | 16.2 ± 5.7 | 10.4 ± 5.8 | 36.1 ± 4.5 | 34.8 ± 11.8 |
| random 100 insert | 9.4 ± 3.8 | 3.3 ± 2.7 | 29.4 ± 3.1 | 21.5 ± 10.5 |
| random 200 insert | 4.5 ± 2.6 | 0.4 ± 0.5 | 21.6 ± 2.8 | 10.6 ± 8.2 |
| lgbm 20 prepend | 1.2 ± 1.7 | 8.0 ± 8.3 | 44.9 ± 7.0 | 45.7 ± 13.9 |
| lgbm 50 prepend | 0.3 ± 1.0 | 0.1 ± 0.3 | 3.7 ± 2.9 | 21.6 ± 10.5 |
| lgbm 100 prepend | 0.2 ± 0.7 | 0.0 ± 0.0 | 1.2 ± 0.9 | 3.9 ± 3.2 |
| lgbm 20 insert | 16.3 ± 7.1 | 10.2 ± 5.1 | 38.4 ± 4.1 | 33.3 ± 11.1 |
| lgbm 50 insert | 7.7 ± 4.0 | 2.9 ± 2.2 | 26.5 ± 3.4 | 21.5 ± 9.3 |
| lgbm 100 insert | 3.6 ± 2.6 | 0.5 ± 0.9 | 18.2 ± 2.1 | 10.6 ± 7.8 |
| white-box 5 steps | pending | 11.7 ± 9.3 | 34.7 ± 3.2 | 30.8 ± 12.6 |
| white-box 10 steps | pending | 6.3 ± 6.3 | 31.3 ± 4.1 | 27.0 ± 11.3 |
| white-box 20 steps | pending | 1.7 ± 4.5 | 17.0 ± 7.7 | 17.4 ± 9.0 |
| white-box 50 steps | pending | 0.2 ± 0.7 | 0.4 ± 0.6 | 1.5 ± 1.4 |
