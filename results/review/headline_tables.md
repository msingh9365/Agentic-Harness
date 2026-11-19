**Table 2 (1% FPR threshold). Malware flagged / padded benign flagged, in % (mean over the 10 seeds; the released checkpoint is one model). Calls prepended or inserted into every April report (9,399 malware, 8,003 benign).**

| model | random 20 prepend | random 50 prepend | random 50 insert | LightGBM 20 prepend | LightGBM 50 prepend | LightGBM 50 insert | v2-PE 20 prepend | v2-PE 50 prepend | v2-PE 50 insert |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint | 12.0 / 12.5 | 16.3 / 13.3 | 35.6 / 4.0 | 2.8 / 0.5 | 3.2 / 0.1 | 28.8 / 2.0 | 28.6 / 66.1 | 100.0 / 100.0 | 65.6 / 59.3 |
| v2-PE | 22.5 / 1.2 | 8.3 / 1.1 | 41.4 / 0.7 | 10.2 / 0.1 | 3.3 / 0.0 | 21.7 / 0.1 | 2.7 / 0.0 | 3.1 / 0.0 | 7.7 / 0.0 |
| PE+bal | 75.7 / 2.4 | 64.3 / 2.4 | 71.4 / 1.5 | 71.1 / 0.8 | 10.0 / 0.0 | 58.8 / 0.5 | 6.0 / 0.0 | 2.3 / 0.0 | 26.8 / 0.2 |
| ATT+bal | 76.9 / 1.3 | 67.6 / 1.5 | 71.9 / 1.0 | 72.3 / 0.8 | 36.5 / 0.1 | 59.0 / 0.3 | 23.8 / 0.0 | 4.2 / 0.0 | 33.9 / 0.1 |
| ATT+bal-keep | 76.7 / 1.3 | 66.6 / 1.5 | 71.7 / 1.0 | 71.2 / 2.1 | 27.1 / 0.1 | 57.0 / 0.2 | 15.9 / 0.0 | 3.3 / 0.0 | 28.2 / 0.1 |
| PE+bal-keep | 76.3 / 2.5 | 65.1 / 2.9 | 71.8 / 1.7 | 70.7 / 1.0 | 6.6 / 0.0 | 56.6 / 0.4 | 4.2 / 0.0 | 2.3 / 0.0 | 24.1 / 0.1 |

**Table 2 (0.1% FPR threshold). Malware flagged / padded benign flagged, in % (mean over the 10 seeds; the released checkpoint is one model). Calls prepended or inserted into every April report (9,399 malware, 8,003 benign).**

| model | random 20 prepend | random 50 prepend | random 50 insert | LightGBM 20 prepend | LightGBM 50 prepend | LightGBM 50 insert | v2-PE 20 prepend | v2-PE 50 prepend | v2-PE 50 insert |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint | 2.1 / 1.1 | 4.1 / 0.8 | 14.7 / 0.1 | 1.2 / 0.0 | 2.0 / 0.0 | 12.8 / 0.0 | 7.8 / 0.0 | 15.0 / 1.9 | 7.0 / 0.3 |
| v2-PE | 5.5 / 0.0 | 1.5 / 0.0 | 13.6 / 0.0 | 1.6 / 0.0 | 0.4 / 0.0 | 6.2 / 0.0 | 0.3 / 0.0 | 0.4 / 0.0 | 1.8 / 0.0 |
| PE+bal | 47.8 / 0.1 | 21.1 / 0.1 | 42.6 / 0.1 | 37.2 / 0.1 | 0.5 / 0.0 | 30.6 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 6.2 / 0.0 |
| ATT+bal | 51.8 / 0.1 | 32.2 / 0.0 | 39.7 / 0.0 | 46.8 / 0.1 | 5.2 / 0.0 | 29.9 / 0.0 | 1.2 / 0.0 | 1.1 / 0.0 | 12.5 / 0.0 |
| ATT+bal-keep | 44.6 / 0.1 | 26.1 / 0.0 | 33.6 / 0.0 | 37.6 / 0.1 | 2.3 / 0.0 | 25.0 / 0.0 | 0.9 / 0.0 | 0.8 / 0.0 | 8.1 / 0.0 |
| PE+bal-keep | 44.2 / 0.1 | 19.1 / 0.0 | 37.6 / 0.0 | 28.9 / 0.1 | 0.1 / 0.0 | 24.7 / 0.0 | 0.1 / 0.0 | 0.1 / 0.0 | 4.1 / 0.0 |

**Table 2 (white-box greedy attack, 500 April malware, seeds 0-2). Share still flagged at the 1% / 0.1% FPR thresholds after k prepended calls, in %.**

| model | seeds | k = 0 | k = 5 | k = 10 | k = 20 |
|---|---|---|---|---|---|
| released checkpoint | 1 | 70.4 / 49.0 | 3.2 / 0.0 | 1.4 / 0.0 | 1.2 / 0.0 |
| v2-PE | 3 | 75.6 / 47.5 | 9.0 / 0.7 | 5.1 / 0.6 | 2.2 / 0.2 |
| PE+bal | 3 | 76.9 / 51.5 | 62.8 / 26.9 | 57.8 / 18.8 | 39.6 / 3.5 |
| ATT+bal | 3 | 77.7 / 58.3 | 65.5 / 34.5 | 62.5 / 31.7 | 53.3 / 14.6 |
| ATT+bal-keep | 3 | 74.8 / 50.8 | 63.8 / 27.3 | 61.6 / 24.5 | 44.7 / 7.5 |
| PE+bal-keep | 3 | 76.1 / 41.8 | 62.8 / 17.1 | 56.1 / 11.0 | 41.1 / 2.5 |

**Count of tests (random padding; edit sets × the two thresholds) in which the first model is resolved higher / lower than the second (claim rule: CI excludes 0 and ≥ 7 of 10 seeds with the same sign). In brackets: also resolved under the cluster bootstrap over duplicate groups. For the padded-benign FPR a higher value is worse.**

| comparison | rate | tests | first higher (cluster) | first lower (cluster) | not resolved |
|---|---|---|---|---|---|
| ATT+bal − PE+bal | malware TPR | 12 | 6 (4) | 0 (0) | 6 |
| ATT+bal − PE+bal | malware TPR, fit subset | 12 | 2 (1) | 1 (1) | 9 |
| ATT+bal − PE+bal | padded-benign FPR | 12 | 0 (0) | 7 (7) | 5 |
| ATT+bal-keep − PE+bal-keep | malware TPR | 12 | 1 (1) | 1 (0) | 10 |
| ATT+bal-keep − PE+bal-keep | malware TPR, fit subset | 12 | 8 (6) | 0 (0) | 4 |
| ATT+bal-keep − PE+bal-keep | padded-benign FPR | 12 | 0 (0) | 2 (2) | 10 |

**Count of tests (surrogate padding; edit sets × the two thresholds) in which the first model is resolved higher / lower than the second (claim rule: CI excludes 0 and ≥ 7 of 10 seeds with the same sign). In brackets: also resolved under the cluster bootstrap over duplicate groups. For the padded-benign FPR a higher value is worse.**

| comparison | rate | tests | first higher (cluster) | first lower (cluster) | not resolved |
|---|---|---|---|---|---|
| ATT+bal − PE+bal | malware TPR | 24 | 18 (14) | 0 (0) | 6 |
| ATT+bal − PE+bal | malware TPR, fit subset | 20 | 2 (1) | 7 (2) | 11 |
| ATT+bal − PE+bal | padded-benign FPR | 24 | 3 (2) | 1 (0) | 20 |
| ATT+bal-keep − PE+bal-keep | malware TPR | 24 | 10 (9) | 1 (0) | 13 |
| ATT+bal-keep − PE+bal-keep | malware TPR, fit subset | 20 | 5 (2) | 1 (0) | 14 |
| ATT+bal-keep − PE+bal-keep | padded-benign FPR | 24 | 0 (0) | 2 (1) | 22 |

**Table 3. The label shortcut: padding applied to malware training reports only (aug) against padding of all reports (bal). Clean TPR@1% FPR, then padded malware / padded benign flagged at the 1% threshold (random calls, prepend), and the probe AUC for "padding present" (pooled vector, 64-d hidden vector).**

| model | clean TPR@1% (April) | k=20 prepend: malware / benign flagged | k=50 prepend: malware / benign flagged | probe AUC, pooled | probe AUC, hidden |
|---|---|---|---|---|---|
| v2-PE | 81.1 | 22.5 / 1.2 | 8.3 / 1.1 | 0.969 | 0.756 |
| PE+bal | 78.7 | 75.7 / 2.4 | 64.3 / 2.4 | 0.971 | 0.750 |
| PE+aug | 81.2 | 99.3 / 94.0 | 99.9 / 99.7 | 0.975 | 0.826 |
| ATT+bal | 79.5 | 76.9 / 1.3 | 67.6 / 1.5 | 0.706 | 0.657 |
| ATT+aug | 78.9 | 94.4 / 62.1 | 98.5 / 95.3 | 0.813 | 0.769 |

**Nebula paper vs ours. Different data (the paper's test set is not the published one; §6.1 of the report); for reference only.**

| model | TPR@1e-3 | AUC | F1 (threshold 0.5) |
|---|---|---|---|
| Nebula paper (Table 7, BPE, 2,116 batches, their test set) | 0.5213 | 0.9657 | 0.9136 |
| ours: released checkpoint (published April set) | 0.518 | 0.9586 | 0.8854 |
| ours: v2-PE (published April set) | 0.543 | 0.9644 | 0.9146 |
| ours: ATT+bal (published April set) | 0.572 | 0.9713 | 0.9134 |
| ours: PE+bal (published April set) | 0.551 | 0.9553 | 0.8984 |
| ours: PE+aug (published April set) | 0.587 | 0.9690 | 0.9114 |

