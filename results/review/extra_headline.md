**Table X (1% FPR threshold). Further edits: malware flagged / padded benign flagged, in % (mean over the seeds scored; every April report is edited). Unedited malware flagged / benign flagged: released checkpoint: 75.0 / 1.00; v2-PE: 81.1 / 0.99; PE+bal: 78.7 / 1.00; ATT+bal: 79.5 / 0.99; v2-PE + test-time deduplication: 81.1 / 0.99.**

| model | seeds | rare 20 prepend | rare 50 insert | block 50 prepend | block 50 insert | copy 50 prepend | copy 50 insert | rot 50 | inj 50 |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint | 1 | 17.6 / 19.4 | 28.9 / 9.8 | 23.9 / 19.8 | 61.9 / 3.8 | 37.4 / 19.3 | 49.0 / 2.7 | 39.5 / 32.5 | 34.4 / 3.2 |
| v2-PE | 10 | 11.5 / 1.5 | 25.0 / 0.9 | 21.3 / 4.4 | 65.4 / 1.1 | 57.2 / 4.2 | 67.7 / 1.8 | 54.3 / 5.2 | 46.9 / 0.8 |
| PE+bal | 10 | 70.0 / 3.8 | 55.1 / 1.7 | 68.2 / 4.1 | 72.0 / 2.0 | 80.5 / 4.5 | 79.7 / 2.6 | 62.7 / 14.6 | 75.0 / 1.4 |
| ATT+bal | 10 | 70.7 / 1.4 | 52.7 / 1.1 | 72.7 / 3.1 | 72.8 / 2.6 | 79.0 / 3.2 | 80.0 / 1.8 | 62.0 / 10.0 | 76.0 / 1.0 |
| v2-PE + test-time deduplication | 10 | 11.3 / 1.4 | 24.6 / 0.8 | 21.2 / 4.2 | 65.2 / 1.0 | 57.2 / 4.0 | 67.5 / 1.7 | 53.8 / 5.0 | 46.4 / 0.8 |

**Table X (0.1% FPR threshold). Further edits: malware flagged / padded benign flagged, in % (mean over the seeds scored; every April report is edited). Unedited malware flagged / benign flagged: released checkpoint: 51.8 / 0.10; v2-PE: 54.3 / 0.10; PE+bal: 55.1 / 0.10; ATT+bal: 57.2 / 0.10; v2-PE + test-time deduplication: 54.4 / 0.10.**

| model | seeds | rare 20 prepend | rare 50 insert | block 50 prepend | block 50 insert | copy 50 prepend | copy 50 insert | rot 50 | inj 50 |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint | 1 | 3.5 / 1.1 | 9.5 / 0.2 | 5.4 / 2.9 | 37.3 / 0.3 | 13.1 / 2.0 | 22.9 / 0.1 | 13.4 / 3.6 | 15.4 / 0.0 |
| v2-PE | 10 | 1.8 / 0.0 | 6.6 / 0.0 | 5.2 / 0.1 | 36.6 / 0.0 | 27.6 / 0.4 | 36.7 / 0.2 | 18.8 / 0.3 | 13.4 / 0.0 |
| PE+bal | 10 | 30.6 / 0.2 | 24.0 / 0.0 | 32.8 / 0.1 | 44.7 / 0.1 | 65.0 / 1.1 | 61.0 / 0.5 | 32.6 / 0.3 | 46.3 / 0.1 |
| ATT+bal | 10 | 40.3 / 0.1 | 25.4 / 0.0 | 41.1 / 0.1 | 42.8 / 0.1 | 61.2 / 0.2 | 55.7 / 0.2 | 36.1 / 0.2 | 48.3 / 0.1 |
| v2-PE + test-time deduplication | 10 | 1.9 / 0.0 | 6.6 / 0.0 | 5.3 / 0.1 | 36.7 / 0.0 | 28.2 / 0.3 | 37.0 / 0.2 | 19.0 / 0.3 | 13.5 / 0.0 |

**Further edits: counts of tests (23 edit sets × two thresholds) in which the first model is higher / lower by the descriptive rule (CI excludes 0 and ≥ 7 of 10 paired seeds on the same side; in brackets the same under the cluster bootstrap). For the padded-benign FPR higher is worse.**

| comparison | rate | tests | first higher (cluster) | first lower (cluster) | neither |
|---|---|---|---|---|---|
| ATT+bal − PE+bal | malware TPR | 46 | 19 (10) | 4 (2) | 23 |
| ATT+bal − PE+bal | padded-benign FPR | 46 | 0 (0) | 21 (20) | 25 |
| ATT+bal − v2-PE | malware TPR | 46 | 45 (41) | 0 (0) | 1 |
| ATT+bal − v2-PE | padded-benign FPR | 46 | 14 (7) | 5 (4) | 27 |
| PE+bal − v2-PE | malware TPR | 46 | 45 (42) | 0 (0) | 1 |
| PE+bal − v2-PE | padded-benign FPR | 46 | 32 (29) | 1 (0) | 13 |
| v2-PE + test-time deduplication − v2-PE | malware TPR | 46 | 9 (6) | 6 (5) | 31 |
| v2-PE + test-time deduplication − v2-PE | padded-benign FPR | 46 | 0 (0) | 8 (8) | 38 |

