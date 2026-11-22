**Detection (%) of April malware after each edit at the 1% false-positive-rate threshold of the unedited April benign scores, mean ± std over 10 seeds (white-box: 500 malware reports; pending = not computed yet).**

| edit | M1 Nebula (ours) | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| unedited | 79.1 ± 2.0 | 77.2 ± 4.9 | 79.0 ± 1.9 | 77.9 ± 1.7 |
| random 5 prepend | 54.8 ± 7.5 | 64.0 ± 5.9 | 79.0 ± 2.0 | 77.6 ± 1.6 |
| random 20 prepend | 25.4 ± 7.8 | 54.2 ± 8.0 | 76.2 ± 2.3 | 74.4 ± 3.0 |
| random 50 prepend | 7.4 ± 4.0 | 28.5 ± 12.0 | 65.1 ± 5.8 | 67.2 ± 4.9 |
| random 100 prepend | 5.7 ± 5.1 | 17.1 ± 13.6 | 6.5 ± 1.3 | 25.9 ± 15.4 |
| random 200 prepend | 5.7 ± 5.1 | 7.8 ± 10.9 | 6.4 ± 1.2 | 8.2 ± 8.7 |
| random 5 insert | 71.4 ± 3.5 | 66.4 ± 5.2 | 77.5 ± 2.1 | 76.8 ± 1.8 |
| random 20 insert | 55.2 ± 6.6 | 55.0 ± 6.4 | 74.5 ± 2.1 | 72.5 ± 2.7 |
| random 50 insert | 42.1 ± 6.9 | 43.2 ± 7.3 | 68.5 ± 2.8 | 65.0 ± 4.1 |
| random 100 insert | 30.3 ± 6.3 | 29.5 ± 6.6 | 55.3 ± 3.6 | 52.4 ± 6.0 |
| random 200 insert | 18.9 ± 5.9 | 12.4 ± 4.7 | 44.3 ± 4.0 | 37.5 ± 7.8 |
| lgbm 20 prepend | 8.8 ± 3.7 | 46.6 ± 10.6 | 73.2 ± 2.5 | 73.4 ± 3.8 |
| lgbm 50 prepend | 1.9 ± 2.6 | 17.2 ± 15.2 | 35.1 ± 13.3 | 48.5 ± 7.7 |
| lgbm 100 prepend | 2.0 ± 2.8 | 14.2 ± 12.5 | 5.8 ± 1.7 | 20.0 ± 16.6 |
| lgbm 20 insert | 43.8 ± 7.4 | 41.3 ± 8.7 | 70.6 ± 1.7 | 62.5 ± 2.4 |
| lgbm 50 insert | 25.4 ± 6.8 | 25.3 ± 6.8 | 54.7 ± 2.9 | 47.5 ± 5.8 |
| lgbm 100 insert | 13.9 ± 4.9 | 13.4 ± 4.7 | 36.8 ± 3.4 | 36.6 ± 6.5 |
| white-box 5 steps | pending | 44.1 ± 8.8 | 66.2 ± 2.6 | 61.3 ± 3.6 |
| white-box 10 steps | pending | 35.9 ± 10.2 | 63.1 ± 3.1 | 58.3 ± 3.9 |
| white-box 20 steps | pending | 19.6 ± 13.3 | 48.7 ± 6.3 | 50.2 ± 5.4 |
| white-box 50 steps | pending | 13.8 ± 13.6 | 2.5 ± 1.3 | 10.6 ± 8.5 |
