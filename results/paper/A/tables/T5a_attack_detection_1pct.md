**Detection (%) of April malware after each edit at the 1% false-positive-rate threshold of the unedited April benign scores, mean ± std over 10 seeds (white-box: 500 malware reports; pending = not computed yet).**

| edit | M1 Nebula (ours) | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 78.0 ± 3.8 | 75.1 ± 6.8 | 79.0 ± 0.8 | 77.8 ± 2.1 |
| random 5 prepend | 51.2 ± 7.9 | 63.6 ± 6.6 | 79.1 ± 1.4 | 77.0 ± 1.8 |
| random 20 prepend | 24.5 ± 11.1 | 52.7 ± 7.3 | 76.6 ± 1.4 | 73.8 ± 2.4 |
| random 50 prepend | 9.0 ± 3.0 | 24.1 ± 13.4 | 66.4 ± 3.4 | 67.5 ± 4.9 |
| random 100 prepend | 6.5 ± 3.4 | 11.9 ± 13.8 | 6.8 ± 1.0 | 26.2 ± 14.8 |
| random 200 prepend | 6.5 ± 3.4 | 7.3 ± 11.9 | 6.7 ± 1.0 | 8.0 ± 5.6 |
| random 5 insert | 70.3 ± 4.6 | 65.8 ± 6.2 | 78.0 ± 1.3 | 75.8 ± 2.3 |
| random 20 insert | 53.9 ± 5.8 | 54.4 ± 6.8 | 74.7 ± 1.0 | 71.4 ± 3.3 |
| random 50 insert | 41.3 ± 6.0 | 42.6 ± 7.9 | 69.1 ± 1.6 | 64.9 ± 4.7 |
| random 100 insert | 30.4 ± 5.3 | 28.8 ± 8.4 | 56.4 ± 3.2 | 53.1 ± 6.3 |
| random 200 insert | 19.0 ± 3.8 | 11.2 ± 5.5 | 45.4 ± 4.1 | 37.5 ± 10.1 |
| lgbm 20 prepend | 8.7 ± 3.2 | 45.0 ± 9.8 | 74.1 ± 2.4 | 73.9 ± 2.1 |
| lgbm 50 prepend | 3.8 ± 3.5 | 13.1 ± 15.5 | 36.3 ± 12.0 | 49.5 ± 10.8 |
| lgbm 100 prepend | 3.6 ± 3.5 | 9.4 ± 12.6 | 5.8 ± 1.7 | 18.5 ± 13.5 |
| lgbm 20 insert | 40.3 ± 6.3 | 41.5 ± 7.5 | 70.3 ± 2.4 | 63.2 ± 3.7 |
| lgbm 50 insert | 23.9 ± 4.9 | 24.0 ± 7.3 | 55.9 ± 2.2 | 48.8 ± 7.3 |
| lgbm 100 insert | 14.2 ± 3.7 | 11.9 ± 5.3 | 38.5 ± 4.8 | 37.0 ± 10.8 |
| white-box 5 steps | 11.1 ± 7.0 | 43.7 ± 7.8 | 66.5 ± 2.8 | 59.3 ± 3.4 |
| white-box 10 steps | 6.4 ± 5.1 | 36.6 ± 9.9 | 64.5 ± 3.2 | 56.5 ± 3.7 |
| white-box 20 steps | 2.4 ± 1.7 | 18.6 ± 15.5 | 51.5 ± 5.4 | 48.1 ± 5.6 |
| white-box 50 steps | 1.0 ± 1.5 | 13.4 ± 15.9 | 2.4 ± 1.3 | 15.1 ± 12.1 |
