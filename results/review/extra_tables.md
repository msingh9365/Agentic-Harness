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


**All further-edit rows (seeds as listed).** Seeds scored per model: released checkpoint 1, v2-PE 10, PE+bal 10, ATT+bal 10, v2-PE + test-time deduplication 10

| model | seeds | edit | malware TPR @1% | padded-benign FPR @1% | malware TPR @0.1% | padded-benign FPR @0.1% | malware that fit in 512 |
|---|---|---|---|---|---|---|---|
| released checkpoint | 1 | rare 5 insert | 56.9 | 1.6 | 31.1 | 0.0 | 29.7% |
| released checkpoint | 1 | rare 5 prepend | 23.5 | 3.2 | 5.5 | 0.0 | 29.7% |
| released checkpoint | 1 | rare 20 insert | 38.4 | 3.9 | 16.3 | 0.1 | 17.6% |
| released checkpoint | 1 | rare 20 prepend | 17.6 | 19.4 | 3.5 | 1.1 | 17.7% |
| released checkpoint | 1 | rare 50 insert | 28.9 | 9.8 | 9.5 | 0.2 | 0.0% |
| released checkpoint | 1 | rare 50 prepend | 23.7 | 16.6 | 3.7 | 0.5 | 0.0% |
| released checkpoint | 1 | block 5 insert | 67.7 | 1.3 | 43.7 | 0.1 | 30.1% |
| released checkpoint | 1 | block 5 prepend | 46.0 | 2.5 | 21.4 | 0.1 | 30.1% |
| released checkpoint | 1 | block 20 insert | 60.5 | 3.3 | 36.7 | 0.3 | 26.9% |
| released checkpoint | 1 | block 20 prepend | 23.6 | 19.1 | 5.7 | 4.1 | 26.9% |
| released checkpoint | 1 | block 50 insert | 61.9 | 3.8 | 37.3 | 0.3 | 20.4% |
| released checkpoint | 1 | block 50 prepend | 23.9 | 19.8 | 5.4 | 2.9 | 20.2% |
| released checkpoint | 1 | copy 5 insert | 69.5 | 1.0 | 41.7 | 0.1 | 29.9% |
| released checkpoint | 1 | copy 5 prepend | 53.7 | 2.0 | 27.8 | 0.2 | 29.8% |
| released checkpoint | 1 | copy 20 insert | 57.5 | 1.7 | 32.3 | 0.1 | 20.9% |
| released checkpoint | 1 | copy 20 prepend | 34.9 | 20.8 | 13.3 | 3.0 | 21.0% |
| released checkpoint | 1 | copy 50 insert | 49.0 | 2.7 | 22.9 | 0.1 | 16.3% |
| released checkpoint | 1 | copy 50 prepend | 37.4 | 19.3 | 13.1 | 2.0 | 16.3% |
| released checkpoint | 1 | rot 25 | 42.3 | 18.7 | 13.0 | 1.6 | 30.4% |
| released checkpoint | 1 | rot 50 | 39.5 | 32.5 | 13.4 | 3.6 | 30.4% |
| released checkpoint | 1 | inj 5 | 64.8 | 1.3 | 32.4 | 0.1 | n/a |
| released checkpoint | 1 | inj 20 | 42.1 | 2.7 | 20.6 | 0.1 | n/a |
| released checkpoint | 1 | inj 50 | 34.4 | 3.2 | 15.4 | 0.0 | n/a |
| v2-PE | 10 | rare 5 insert | 65.0 ± 4.2 | 0.8 ± 0.3 | 31.8 ± 4.6 | 0.0 ± 0.0 | 29.8% |
| v2-PE | 10 | rare 5 prepend | 42.1 ± 13.3 | 1.9 ± 1.5 | 10.8 ± 5.6 | 0.0 ± 0.0 | 29.9% |
| v2-PE | 10 | rare 20 insert | 42.3 ± 5.0 | 0.7 ± 0.7 | 14.5 ± 3.9 | 0.0 ± 0.0 | 17.7% |
| v2-PE | 10 | rare 20 prepend | 11.5 ± 5.0 | 1.5 ± 1.8 | 1.8 ± 1.8 | 0.0 ± 0.0 | 17.8% |
| v2-PE | 10 | rare 50 insert | 25.0 ± 5.2 | 0.9 ± 1.4 | 6.6 ± 3.0 | 0.0 ± 0.0 | 0.0% |
| v2-PE | 10 | rare 50 prepend | 6.3 ± 5.0 | 1.7 ± 3.1 | 1.1 ± 1.6 | 0.0 ± 0.0 | 0.0% |
| v2-PE | 10 | block 5 insert | 75.0 ± 2.6 | 1.0 ± 0.2 | 44.8 ± 4.7 | 0.1 ± 0.0 | 30.2% |
| v2-PE | 10 | block 5 prepend | 57.4 ± 7.1 | 1.2 ± 0.4 | 22.5 ± 6.1 | 0.0 ± 0.0 | 30.2% |
| v2-PE | 10 | block 20 insert | 68.5 ± 2.7 | 1.1 ± 0.6 | 38.7 ± 4.4 | 0.1 ± 0.0 | 27.4% |
| v2-PE | 10 | block 20 prepend | 34.1 ± 7.4 | 4.2 ± 4.8 | 9.2 ± 3.2 | 0.1 ± 0.2 | 27.7% |
| v2-PE | 10 | block 50 insert | 65.4 ± 2.9 | 1.1 ± 0.6 | 36.6 ± 4.2 | 0.0 ± 0.0 | 20.6% |
| v2-PE | 10 | block 50 prepend | 21.3 ± 3.5 | 4.4 ± 4.1 | 5.2 ± 1.9 | 0.1 ± 0.1 | 20.5% |
| v2-PE | 10 | copy 5 insert | 78.4 ± 2.6 | 1.1 ± 0.1 | 46.2 ± 4.7 | 0.1 ± 0.0 | 30.0% |
| v2-PE | 10 | copy 5 prepend | 68.3 ± 6.7 | 1.6 ± 0.4 | 34.2 ± 6.9 | 0.1 ± 0.1 | 30.0% |
| v2-PE | 10 | copy 20 insert | 72.0 ± 5.0 | 1.5 ± 0.3 | 40.0 ± 7.2 | 0.1 ± 0.1 | 22.1% |
| v2-PE | 10 | copy 20 prepend | 59.8 ± 10.6 | 3.8 ± 2.2 | 29.3 ± 8.9 | 0.2 ± 0.1 | 22.4% |
| v2-PE | 10 | copy 50 insert | 67.7 ± 7.9 | 1.8 ± 0.3 | 36.7 ± 7.5 | 0.2 ± 0.1 | 16.6% |
| v2-PE | 10 | copy 50 prepend | 57.2 ± 9.8 | 4.2 ± 2.5 | 27.6 ± 8.4 | 0.4 ± 0.2 | 16.5% |
| v2-PE | 10 | rot 25 | 52.8 ± 8.2 | 3.8 ± 2.1 | 19.7 ± 6.5 | 0.2 ± 0.1 | 30.4% |
| v2-PE | 10 | rot 50 | 54.3 ± 9.6 | 5.2 ± 2.1 | 18.8 ± 4.7 | 0.3 ± 0.1 | 30.4% |
| v2-PE | 10 | inj 5 | 72.5 ± 3.8 | 0.9 ± 0.1 | 34.4 ± 6.8 | 0.0 ± 0.0 | n/a |
| v2-PE | 10 | inj 20 | 58.1 ± 7.4 | 0.9 ± 0.3 | 21.9 ± 6.7 | 0.0 ± 0.0 | n/a |
| v2-PE | 10 | inj 50 | 46.9 ± 3.8 | 0.8 ± 0.4 | 13.4 ± 5.7 | 0.0 ± 0.0 | n/a |
| PE+bal | 10 | rare 5 insert | 76.1 ± 1.8 | 1.6 ± 0.3 | 48.3 ± 6.5 | 0.1 ± 0.0 | 29.8% |
| PE+bal | 10 | rare 5 prepend | 76.8 ± 1.6 | 2.5 ± 1.9 | 46.2 ± 6.8 | 0.1 ± 0.1 | 29.9% |
| PE+bal | 10 | rare 20 insert | 69.6 ± 2.2 | 2.4 ± 0.9 | 37.3 ± 7.4 | 0.1 ± 0.1 | 17.7% |
| PE+bal | 10 | rare 20 prepend | 70.0 ± 2.7 | 3.8 ± 2.0 | 30.6 ± 6.1 | 0.2 ± 0.4 | 17.8% |
| PE+bal | 10 | rare 50 insert | 55.1 ± 4.2 | 1.7 ± 1.1 | 24.0 ± 5.9 | 0.0 ± 0.1 | 0.0% |
| PE+bal | 10 | rare 50 prepend | 8.6 ± 3.8 | 3.3 ± 3.0 | 1.4 ± 0.8 | 0.1 ± 0.1 | 0.0% |
| PE+bal | 10 | block 5 insert | 77.3 ± 1.8 | 1.1 ± 0.1 | 52.4 ± 5.8 | 0.1 ± 0.0 | 30.2% |
| PE+bal | 10 | block 5 prepend | 78.2 ± 1.9 | 1.7 ± 1.2 | 51.2 ± 6.9 | 0.1 ± 0.0 | 30.2% |
| PE+bal | 10 | block 20 insert | 75.4 ± 1.5 | 1.3 ± 0.2 | 49.8 ± 5.1 | 0.1 ± 0.0 | 27.4% |
| PE+bal | 10 | block 20 prepend | 75.4 ± 2.0 | 2.4 ± 1.6 | 46.6 ± 4.9 | 0.2 ± 0.1 | 27.7% |
| PE+bal | 10 | block 50 insert | 72.0 ± 2.0 | 2.0 ± 0.6 | 44.7 ± 4.9 | 0.1 ± 0.0 | 20.6% |
| PE+bal | 10 | block 50 prepend | 68.2 ± 4.4 | 4.1 ± 1.2 | 32.8 ± 4.0 | 0.1 ± 0.1 | 20.5% |
| PE+bal | 10 | copy 5 insert | 79.3 ± 2.0 | 1.2 ± 0.3 | 55.5 ± 6.6 | 0.1 ± 0.0 | 30.0% |
| PE+bal | 10 | copy 5 prepend | 80.1 ± 2.1 | 1.9 ± 1.7 | 56.8 ± 6.1 | 0.2 ± 0.0 | 30.0% |
| PE+bal | 10 | copy 20 insert | 79.2 ± 1.7 | 1.8 ± 1.1 | 57.2 ± 6.4 | 0.2 ± 0.0 | 22.1% |
| PE+bal | 10 | copy 20 prepend | 79.8 ± 2.1 | 2.9 ± 3.3 | 64.5 ± 4.2 | 0.7 ± 1.0 | 22.4% |
| PE+bal | 10 | copy 50 insert | 79.7 ± 1.5 | 2.6 ± 1.8 | 61.0 ± 5.4 | 0.5 ± 0.2 | 16.6% |
| PE+bal | 10 | copy 50 prepend | 80.5 ± 1.9 | 4.5 ± 3.0 | 65.0 ± 4.0 | 1.1 ± 1.5 | 16.5% |
| PE+bal | 10 | rot 25 | 64.2 ± 7.6 | 12.0 ± 8.5 | 33.8 ± 5.5 | 0.1 ± 0.1 | 30.4% |
| PE+bal | 10 | rot 50 | 62.7 ± 4.7 | 14.6 ± 6.5 | 32.6 ± 4.4 | 0.3 ± 0.1 | 30.4% |
| PE+bal | 10 | inj 5 | 79.1 ± 2.0 | 1.6 ± 1.1 | 52.1 ± 7.1 | 0.1 ± 0.0 | n/a |
| PE+bal | 10 | inj 20 | 77.3 ± 2.1 | 1.4 ± 0.7 | 49.7 ± 5.4 | 0.1 ± 0.0 | n/a |
| PE+bal | 10 | inj 50 | 75.0 ± 2.2 | 1.4 ± 0.6 | 46.3 ± 5.5 | 0.1 ± 0.0 | n/a |
| ATT+bal | 10 | rare 5 insert | 75.6 ± 4.8 | 1.1 ± 0.3 | 46.6 ± 4.7 | 0.1 ± 0.0 | 29.8% |
| ATT+bal | 10 | rare 5 prepend | 76.8 ± 4.6 | 1.2 ± 0.3 | 49.8 ± 6.4 | 0.1 ± 0.0 | 29.9% |
| ATT+bal | 10 | rare 20 insert | 67.9 ± 6.6 | 1.2 ± 0.8 | 34.0 ± 4.0 | 0.0 ± 0.0 | 17.7% |
| ATT+bal | 10 | rare 20 prepend | 70.7 ± 5.1 | 1.4 ± 0.7 | 40.3 ± 6.0 | 0.1 ± 0.0 | 17.8% |
| ATT+bal | 10 | rare 50 insert | 52.7 ± 5.7 | 1.1 ± 0.8 | 25.4 ± 2.6 | 0.0 ± 0.0 | 0.0% |
| ATT+bal | 10 | rare 50 prepend | 6.7 ± 2.0 | 0.9 ± 1.1 | 1.6 ± 0.8 | 0.0 | 0.0% |
| ATT+bal | 10 | block 5 insert | 78.3 ± 2.9 | 1.1 ± 0.1 | 53.2 ± 5.5 | 0.1 ± 0.0 | 30.2% |
| ATT+bal | 10 | block 5 prepend | 79.2 ± 3.1 | 1.2 ± 0.2 | 52.7 ± 5.6 | 0.1 ± 0.0 | 30.2% |
| ATT+bal | 10 | block 20 insert | 76.4 ± 3.5 | 1.4 ± 0.4 | 49.3 ± 4.9 | 0.1 ± 0.0 | 27.4% |
| ATT+bal | 10 | block 20 prepend | 77.5 ± 3.5 | 1.8 ± 0.5 | 52.1 ± 6.4 | 0.1 ± 0.0 | 27.7% |
| ATT+bal | 10 | block 50 insert | 72.8 ± 4.1 | 2.6 ± 1.2 | 42.8 ± 4.4 | 0.1 ± 0.0 | 20.6% |
| ATT+bal | 10 | block 50 prepend | 72.7 ± 4.2 | 3.1 ± 1.4 | 41.1 ± 5.6 | 0.1 ± 0.0 | 20.5% |
| ATT+bal | 10 | copy 5 insert | 80.0 ± 2.2 | 1.1 ± 0.1 | 55.7 ± 6.1 | 0.1 ± 0.0 | 30.0% |
| ATT+bal | 10 | copy 5 prepend | 80.7 ± 2.7 | 1.2 ± 0.1 | 54.9 ± 5.5 | 0.1 ± 0.0 | 30.0% |
| ATT+bal | 10 | copy 20 insert | 79.5 ± 3.1 | 1.4 ± 0.1 | 54.1 ± 3.5 | 0.1 ± 0.0 | 22.1% |
| ATT+bal | 10 | copy 20 prepend | 80.0 ± 2.5 | 2.0 ± 1.1 | 60.2 ± 5.4 | 0.2 ± 0.0 | 22.4% |
| ATT+bal | 10 | copy 50 insert | 80.0 ± 2.6 | 1.8 ± 0.3 | 55.7 ± 4.7 | 0.2 ± 0.1 | 16.6% |
| ATT+bal | 10 | copy 50 prepend | 79.0 ± 2.3 | 3.2 ± 2.3 | 61.2 ± 3.5 | 0.2 ± 0.1 | 16.5% |
| ATT+bal | 10 | rot 25 | 63.7 ± 5.5 | 11.2 ± 6.2 | 36.0 ± 5.4 | 0.1 ± 0.0 | 30.4% |
| ATT+bal | 10 | rot 50 | 62.0 ± 5.9 | 10.0 ± 5.5 | 36.1 ± 5.4 | 0.2 ± 0.1 | 30.4% |
| ATT+bal | 10 | inj 5 | 79.8 ± 2.2 | 1.1 ± 0.1 | 55.1 ± 7.1 | 0.1 ± 0.0 | n/a |
| ATT+bal | 10 | inj 20 | 78.0 ± 3.8 | 1.1 ± 0.2 | 50.6 ± 5.0 | 0.1 ± 0.0 | n/a |
| ATT+bal | 10 | inj 50 | 76.0 ± 3.2 | 1.0 ± 0.3 | 48.3 ± 5.8 | 0.1 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | rare 5 insert | 64.7 ± 4.2 | 0.7 ± 0.2 | 32.0 ± 4.7 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | rare 5 prepend | 41.7 ± 13.6 | 1.8 ± 1.3 | 10.9 ± 5.6 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | rare 20 insert | 41.9 ± 5.0 | 0.7 ± 0.6 | 14.6 ± 4.0 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | rare 20 prepend | 11.3 ± 4.7 | 1.4 ± 1.6 | 1.9 ± 1.8 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | rare 50 insert | 24.6 ± 4.9 | 0.8 ± 1.2 | 6.6 ± 3.0 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | rare 50 prepend | 6.1 ± 4.8 | 1.6 ± 2.7 | 1.1 ± 1.6 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | block 5 insert | 74.9 ± 2.6 | 1.0 ± 0.1 | 45.0 ± 5.1 | 0.1 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | block 5 prepend | 57.2 ± 7.2 | 1.1 ± 0.3 | 22.8 ± 6.2 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | block 20 insert | 68.3 ± 2.7 | 1.1 ± 0.5 | 38.8 ± 4.7 | 0.1 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | block 20 prepend | 33.8 ± 7.7 | 3.9 ± 4.4 | 9.3 ± 3.2 | 0.1 ± 0.2 | n/a |
| v2-PE + test-time deduplication | 10 | block 50 insert | 65.2 ± 2.8 | 1.0 ± 0.5 | 36.7 ± 4.5 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | block 50 prepend | 21.2 ± 3.3 | 4.2 ± 3.6 | 5.3 ± 1.9 | 0.1 ± 0.1 | n/a |
| v2-PE + test-time deduplication | 10 | copy 5 insert | 78.6 ± 2.7 | 1.1 ± 0.1 | 46.3 ± 5.3 | 0.1 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | copy 5 prepend | 68.2 ± 6.6 | 1.6 ± 0.4 | 33.9 ± 7.4 | 0.1 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | copy 20 insert | 71.9 ± 5.0 | 1.4 ± 0.3 | 40.5 ± 6.6 | 0.1 ± 0.1 | n/a |
| v2-PE + test-time deduplication | 10 | copy 20 prepend | 59.3 ± 10.9 | 3.5 ± 2.1 | 29.2 ± 8.6 | 0.2 ± 0.1 | n/a |
| v2-PE + test-time deduplication | 10 | copy 50 insert | 67.5 ± 7.9 | 1.7 ± 0.3 | 37.0 ± 7.5 | 0.2 ± 0.1 | n/a |
| v2-PE + test-time deduplication | 10 | copy 50 prepend | 57.2 ± 9.5 | 4.0 ± 2.3 | 28.2 ± 8.3 | 0.3 ± 0.2 | n/a |
| v2-PE + test-time deduplication | 10 | rot 25 | 52.5 ± 8.3 | 3.6 ± 1.8 | 19.9 ± 6.6 | 0.2 ± 0.1 | n/a |
| v2-PE + test-time deduplication | 10 | rot 50 | 53.8 ± 9.8 | 5.0 ± 1.8 | 19.0 ± 4.9 | 0.3 ± 0.1 | n/a |
| v2-PE + test-time deduplication | 10 | inj 5 | 72.4 ± 4.0 | 0.9 ± 0.1 | 34.7 ± 6.9 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | inj 20 | 57.7 ± 7.6 | 0.9 ± 0.3 | 22.0 ± 6.7 | 0.0 ± 0.0 | n/a |
| v2-PE + test-time deduplication | 10 | inj 50 | 46.4 ± 3.8 | 0.8 ± 0.3 | 13.5 ± 5.7 | 0.0 ± 0.0 | n/a |

**Further edits, ATT+bal − PE+bal (10 paired seeds): A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; meets rule = CI excludes 0 and ≥ 7 of 10 seeds with the same sign (descriptive: none of these robustness comparisons is a pre-registered claim).**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | meets rule (descriptive) | CI (cluster bootstrap) | meets rule, cluster (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal − PE+bal | rare 5 insert | 1% FPR | malware TPR | -0.48 | 5.90 | [-0.68, -0.27] | 7/3 | **yes** | [-1.65, +0.67] | no |
| ATT+bal − PE+bal | rare 5 insert | 1% FPR | padded-benign FPR | -0.52 | 0.37 | [-0.66, -0.38] | 0/10 | **yes** | [-0.77, -0.30] | yes |
| ATT+bal − PE+bal | rare 5 insert | 1% FPR | malware TPR, fit subset | -2.76 | 9.11 | [-3.23, -2.31] | 5/5 | no | [-5.64, +0.08] | no |
| ATT+bal − PE+bal | rare 5 insert | 0.1% FPR | malware TPR | -1.61 | 8.69 | [-1.99, -1.25] | 6/4 | no | [-4.42, +0.89] | no |
| ATT+bal − PE+bal | rare 5 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.03 | [-0.03, +0.03] | 5/4 | no | [-0.03, +0.02] | no |
| ATT+bal − PE+bal | rare 5 insert | 0.1% FPR | malware TPR, fit subset | -1.93 | 9.36 | [-2.62, -1.18] | 5/5 | no | [-4.87, +0.87] | no |
| ATT+bal − PE+bal | rare 5 prepend | 1% FPR | malware TPR | -0.04 | 5.66 | [-0.24, +0.17] | 8/2 | no | [-1.18, +1.08] | no |
| ATT+bal − PE+bal | rare 5 prepend | 1% FPR | padded-benign FPR | -1.37 | 1.97 | [-1.52, -1.22] | 2/8 | **yes** | [-2.22, -0.76] | yes |
| ATT+bal − PE+bal | rare 5 prepend | 1% FPR | malware TPR, fit subset | -1.05 | 6.45 | [-1.50, -0.58] | 6/4 | no | [-2.80, +0.69] | no |
| ATT+bal − PE+bal | rare 5 prepend | 0.1% FPR | malware TPR | +3.62 | 8.12 | [+3.20, +4.05] | 7/3 | **yes** | [+0.10, +8.10] | yes |
| ATT+bal − PE+bal | rare 5 prepend | 0.1% FPR | padded-benign FPR | -0.03 | 0.13 | [-0.06, -0.00] | 5/4 | no | [-0.07, +0.01] | no |
| ATT+bal − PE+bal | rare 5 prepend | 0.1% FPR | malware TPR, fit subset | +11.98 | 11.06 | [+11.00, +12.86] | 9/1 | **yes** | [+4.28, +21.54] | yes |
| ATT+bal − PE+bal | rare 20 insert | 1% FPR | malware TPR | -1.76 | 7.97 | [-2.04, -1.48] | 6/4 | no | [-3.55, +0.02] | no |
| ATT+bal − PE+bal | rare 20 insert | 1% FPR | padded-benign FPR | -1.16 | 1.14 | [-1.34, -1.00] | 1/9 | **yes** | [-1.57, -0.79] | yes |
| ATT+bal − PE+bal | rare 20 insert | 1% FPR | malware TPR, fit subset | -9.76 | 13.05 | [-10.63, -8.88] | 2/8 | **yes** | [-12.54, -5.86] | yes |
| ATT+bal − PE+bal | rare 20 insert | 0.1% FPR | malware TPR | -3.31 | 8.17 | [-3.71, -2.94] | 6/4 | no | [-6.93, +1.09] | no |
| ATT+bal − PE+bal | rare 20 insert | 0.1% FPR | padded-benign FPR | -0.06 | 0.10 | [-0.09, -0.04] | 0/7 | **yes** | [-0.10, -0.03] | yes |
| ATT+bal − PE+bal | rare 20 insert | 0.1% FPR | malware TPR, fit subset | -8.31 | 6.82 | [-9.16, -7.52] | 0/10 | **yes** | [-11.71, -3.57] | yes |
| ATT+bal − PE+bal | rare 20 prepend | 1% FPR | malware TPR | +0.63 | 7.00 | [+0.31, +0.93] | 7/3 | **yes** | [-0.78, +2.03] | no |
| ATT+bal − PE+bal | rare 20 prepend | 1% FPR | padded-benign FPR | -2.39 | 2.00 | [-2.59, -2.19] | 0/10 | **yes** | [-3.00, -1.75] | yes |
| ATT+bal − PE+bal | rare 20 prepend | 1% FPR | malware TPR, fit subset | -4.11 | 15.08 | [-5.03, -3.15] | 5/5 | no | [-7.63, -1.92] | no |
| ATT+bal − PE+bal | rare 20 prepend | 0.1% FPR | malware TPR | +9.71 | 10.51 | [+9.27, +10.21] | 8/2 | **yes** | [+4.82, +13.97] | yes |
| ATT+bal − PE+bal | rare 20 prepend | 0.1% FPR | padded-benign FPR | -0.19 | 0.36 | [-0.24, -0.15] | 0/10 | **yes** | [-0.27, -0.12] | yes |
| ATT+bal − PE+bal | rare 20 prepend | 0.1% FPR | malware TPR, fit subset | -1.04 | 6.21 | [-1.99, -0.22] | 4/6 | no | [-4.49, +4.64] | no |
| ATT+bal − PE+bal | rare 50 insert | 1% FPR | malware TPR | -2.45 | 8.49 | [-2.78, -2.13] | 5/5 | no | [-4.41, -0.64] | no |
| ATT+bal − PE+bal | rare 50 insert | 1% FPR | padded-benign FPR | -0.68 | 1.19 | [-0.83, -0.55] | 4/6 | no | [-0.96, -0.42] | no |
| ATT+bal − PE+bal | rare 50 insert | 0.1% FPR | malware TPR | +1.33 | 6.54 | [+0.94, +1.70] | 8/2 | **yes** | [-2.41, +6.09] | no |
| ATT+bal − PE+bal | rare 50 insert | 0.1% FPR | padded-benign FPR | -0.03 | 0.07 | [-0.05, -0.01] | 2/7 | **yes** | [-0.06, -0.01] | yes |
| ATT+bal − PE+bal | rare 50 prepend | 1% FPR | malware TPR | -1.84 | 4.56 | [-2.08, -1.61] | 5/5 | no | [-2.43, -0.80] | no |
| ATT+bal − PE+bal | rare 50 prepend | 1% FPR | padded-benign FPR | -2.38 | 3.16 | [-2.58, -2.17] | 2/8 | **yes** | [-2.59, -2.20] | yes |
| ATT+bal − PE+bal | rare 50 prepend | 0.1% FPR | malware TPR | +0.20 | 1.33 | [+0.09, +0.31] | 5/5 | no | [-0.21, +0.72] | no |
| ATT+bal − PE+bal | rare 50 prepend | 0.1% FPR | padded-benign FPR | -0.10 | 0.14 | [-0.14, -0.07] | 0/7 | **yes** | [-0.14, -0.07] | yes |
| ATT+bal − PE+bal | block 5 insert | 1% FPR | malware TPR | +0.99 | 3.48 | [+0.79, +1.19] | 8/2 | **yes** | [+0.26, +1.89] | yes |
| ATT+bal − PE+bal | block 5 insert | 1% FPR | padded-benign FPR | +0.02 | 0.14 | [-0.09, +0.13] | 5/5 | no | [-0.10, +0.18] | no |
| ATT+bal − PE+bal | block 5 insert | 1% FPR | malware TPR, fit subset | +1.01 | 4.43 | [+0.56, +1.43] | 7/3 | **yes** | [-0.45, +2.43] | no |
| ATT+bal − PE+bal | block 5 insert | 0.1% FPR | malware TPR | +0.85 | 8.71 | [+0.45, +1.23] | 6/4 | no | [-1.96, +2.81] | no |
| ATT+bal − PE+bal | block 5 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.04 | [-0.07, +0.04] | 3/7 | no | [-0.08, +0.05] | no |
| ATT+bal − PE+bal | block 5 insert | 0.1% FPR | malware TPR, fit subset | +3.97 | 10.47 | [+3.08, +4.86] | 6/4 | no | [+1.86, +6.18] | no |
| ATT+bal − PE+bal | block 5 prepend | 1% FPR | malware TPR | +0.92 | 3.98 | [+0.71, +1.11] | 8/2 | **yes** | [+0.30, +1.70] | yes |
| ATT+bal − PE+bal | block 5 prepend | 1% FPR | padded-benign FPR | -0.49 | 1.20 | [-0.60, -0.38] | 3/7 | **yes** | [-1.07, -0.06] | yes |
| ATT+bal − PE+bal | block 5 prepend | 1% FPR | malware TPR, fit subset | +1.06 | 5.58 | [+0.64, +1.52] | 6/3 | no | [-0.32, +2.58] | no |
| ATT+bal − PE+bal | block 5 prepend | 0.1% FPR | malware TPR | +1.53 | 9.15 | [+1.15, +1.93] | 7/3 | **yes** | [-1.59, +4.04] | no |
| ATT+bal − PE+bal | block 5 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.05 | [-0.04, +0.03] | 5/4 | no | [-0.05, +0.04] | no |
| ATT+bal − PE+bal | block 5 prepend | 0.1% FPR | malware TPR, fit subset | +5.92 | 11.30 | [+5.03, +6.82] | 6/4 | no | [+2.92, +8.40] | no |
| ATT+bal − PE+bal | block 20 insert | 1% FPR | malware TPR | +1.06 | 4.21 | [+0.83, +1.30] | 9/1 | **yes** | [+0.27, +2.06] | yes |
| ATT+bal − PE+bal | block 20 insert | 1% FPR | padded-benign FPR | +0.13 | 0.52 | [+0.02, +0.24] | 5/5 | no | [-0.02, +0.30] | no |
| ATT+bal − PE+bal | block 20 insert | 1% FPR | malware TPR, fit subset | +0.63 | 6.05 | [+0.13, +1.19] | 7/3 | **yes** | [-0.85, +2.09] | no |
| ATT+bal − PE+bal | block 20 insert | 0.1% FPR | malware TPR | -0.45 | 7.55 | [-0.86, -0.07] | 6/4 | no | [-3.00, +1.41] | no |
| ATT+bal − PE+bal | block 20 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.03 | [-0.03, +0.03] | 4/5 | no | [-0.04, +0.03] | no |
| ATT+bal − PE+bal | block 20 insert | 0.1% FPR | malware TPR, fit subset | -0.34 | 7.79 | [-1.13, +0.54] | 6/4 | no | [-1.79, +1.71] | no |
| ATT+bal − PE+bal | block 20 prepend | 1% FPR | malware TPR | +2.12 | 4.80 | [+1.89, +2.38] | 9/1 | **yes** | [+1.25, +3.20] | yes |
| ATT+bal − PE+bal | block 20 prepend | 1% FPR | padded-benign FPR | -0.60 | 1.73 | [-0.73, -0.47] | 4/6 | no | [-1.35, -0.09] | no |
| ATT+bal − PE+bal | block 20 prepend | 1% FPR | malware TPR, fit subset | +2.71 | 6.03 | [+2.20, +3.23] | 9/1 | **yes** | [+1.53, +3.99] | yes |
| ATT+bal − PE+bal | block 20 prepend | 0.1% FPR | malware TPR | +5.44 | 8.30 | [+5.01, +5.85] | 8/2 | **yes** | [+2.76, +7.88] | yes |
| ATT+bal − PE+bal | block 20 prepend | 0.1% FPR | padded-benign FPR | -0.04 | 0.13 | [-0.09, +0.01] | 4/6 | no | [-0.10, +0.02] | no |
| ATT+bal − PE+bal | block 20 prepend | 0.1% FPR | malware TPR, fit subset | +9.61 | 8.50 | [+8.70, +10.52] | 9/1 | **yes** | [+4.90, +13.08] | yes |
| ATT+bal − PE+bal | block 50 insert | 1% FPR | malware TPR | +0.82 | 5.06 | [+0.54, +1.10] | 9/1 | **yes** | [-0.30, +1.99] | no |
| ATT+bal − PE+bal | block 50 insert | 1% FPR | padded-benign FPR | +0.61 | 1.50 | [+0.46, +0.77] | 6/4 | no | [+0.39, +0.89] | no |
| ATT+bal − PE+bal | block 50 insert | 1% FPR | malware TPR, fit subset | -1.32 | 8.71 | [-2.19, -0.48] | 4/5 | no | [-3.11, +1.12] | no |
| ATT+bal − PE+bal | block 50 insert | 0.1% FPR | malware TPR | -1.87 | 7.07 | [-2.31, -1.45] | 5/5 | no | [-5.19, +1.00] | no |
| ATT+bal − PE+bal | block 50 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.04 | [-0.06, +0.02] | 4/6 | no | [-0.06, +0.02] | no |
| ATT+bal − PE+bal | block 50 insert | 0.1% FPR | malware TPR, fit subset | -6.69 | 8.26 | [-7.91, -5.53] | 3/7 | **yes** | [-12.09, -0.35] | yes |
| ATT+bal − PE+bal | block 50 prepend | 1% FPR | malware TPR | +4.47 | 7.28 | [+4.13, +4.81] | 9/1 | **yes** | [+3.29, +5.55] | yes |
| ATT+bal − PE+bal | block 50 prepend | 1% FPR | padded-benign FPR | -1.02 | 2.22 | [-1.22, -0.83] | 2/8 | **yes** | [-1.52, -0.58] | yes |
| ATT+bal − PE+bal | block 50 prepend | 1% FPR | malware TPR, fit subset | +3.21 | 9.93 | [+2.48, +3.99] | 9/1 | **yes** | [+1.84, +4.32] | yes |
| ATT+bal − PE+bal | block 50 prepend | 0.1% FPR | malware TPR | +8.26 | 9.22 | [+7.81, +8.77] | 8/2 | **yes** | [+4.61, +11.63] | yes |
| ATT+bal − PE+bal | block 50 prepend | 0.1% FPR | padded-benign FPR | -0.05 | 0.15 | [-0.08, -0.02] | 3/7 | **yes** | [-0.11, -0.01] | yes |
| ATT+bal − PE+bal | block 50 prepend | 0.1% FPR | malware TPR, fit subset | +3.01 | 10.06 | [+2.03, +4.06] | 5/5 | no | [+0.70, +5.61] | no |
| ATT+bal − PE+bal | copy 5 insert | 1% FPR | malware TPR | +0.64 | 3.13 | [+0.44, +0.84] | 7/3 | **yes** | [-0.73, +1.89] | no |
| ATT+bal − PE+bal | copy 5 insert | 1% FPR | padded-benign FPR | -0.07 | 0.31 | [-0.17, +0.04] | 6/4 | no | [-0.26, +0.13] | no |
| ATT+bal − PE+bal | copy 5 insert | 1% FPR | malware TPR, fit subset | +1.36 | 4.44 | [+0.98, +1.75] | 7/3 | **yes** | [+0.06, +2.83] | yes |
| ATT+bal − PE+bal | copy 5 insert | 0.1% FPR | malware TPR | +0.15 | 8.95 | [-0.22, +0.52] | 6/4 | no | [-3.11, +2.61] | no |
| ATT+bal − PE+bal | copy 5 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.05, +0.04] | 3/5 | no | [-0.05, +0.05] | no |
| ATT+bal − PE+bal | copy 5 insert | 0.1% FPR | malware TPR, fit subset | +4.05 | 8.86 | [+3.30, +4.76] | 6/4 | no | [+0.93, +7.21] | no |
| ATT+bal − PE+bal | copy 5 prepend | 1% FPR | malware TPR | +0.69 | 3.60 | [+0.51, +0.86] | 7/3 | **yes** | [+0.10, +1.39] | yes |
| ATT+bal − PE+bal | copy 5 prepend | 1% FPR | padded-benign FPR | -0.62 | 1.66 | [-0.75, -0.50] | 4/6 | no | [-1.36, -0.09] | no |
| ATT+bal − PE+bal | copy 5 prepend | 1% FPR | malware TPR, fit subset | +1.39 | 4.54 | [+1.00, +1.79] | 7/3 | **yes** | [+0.25, +2.66] | yes |
| ATT+bal − PE+bal | copy 5 prepend | 0.1% FPR | malware TPR | -1.93 | 8.21 | [-2.30, -1.57] | 5/5 | no | [-5.23, +0.49] | no |
| ATT+bal − PE+bal | copy 5 prepend | 0.1% FPR | padded-benign FPR | -0.02 | 0.05 | [-0.06, +0.01] | 4/5 | no | [-0.07, +0.01] | no |
| ATT+bal − PE+bal | copy 5 prepend | 0.1% FPR | malware TPR, fit subset | +1.31 | 7.74 | [+0.58, +2.01] | 6/4 | no | [-0.59, +3.26] | no |
| ATT+bal − PE+bal | copy 20 insert | 1% FPR | malware TPR | +0.24 | 4.06 | [+0.04, +0.44] | 7/3 | **yes** | [-0.57, +1.11] | no |
| ATT+bal − PE+bal | copy 20 insert | 1% FPR | padded-benign FPR | -0.43 | 1.08 | [-0.55, -0.30] | 5/5 | no | [-0.87, -0.07] | no |
| ATT+bal − PE+bal | copy 20 insert | 1% FPR | malware TPR, fit subset | -0.21 | 4.10 | [-0.66, +0.28] | 5/5 | no | [-2.36, +1.71] | no |
| ATT+bal − PE+bal | copy 20 insert | 0.1% FPR | malware TPR | -3.15 | 7.14 | [-3.50, -2.82] | 4/6 | no | [-6.94, +0.36] | no |
| ATT+bal − PE+bal | copy 20 insert | 0.1% FPR | padded-benign FPR | -0.08 | 0.06 | [-0.12, -0.04] | 2/8 | **yes** | [-0.14, -0.04] | yes |
| ATT+bal − PE+bal | copy 20 insert | 0.1% FPR | malware TPR, fit subset | -2.73 | 3.59 | [-3.25, -2.18] | 3/7 | **yes** | [-4.97, -1.39] | yes |
| ATT+bal − PE+bal | copy 20 prepend | 1% FPR | malware TPR | +0.14 | 3.72 | [-0.06, +0.34] | 6/4 | no | [-0.69, +1.14] | no |
| ATT+bal − PE+bal | copy 20 prepend | 1% FPR | padded-benign FPR | -0.98 | 3.56 | [-1.10, -0.85] | 2/8 | **yes** | [-1.97, -0.37] | yes |
| ATT+bal − PE+bal | copy 20 prepend | 1% FPR | malware TPR, fit subset | -0.20 | 4.60 | [-0.62, +0.22] | 5/5 | no | [-1.79, +1.23] | no |
| ATT+bal − PE+bal | copy 20 prepend | 0.1% FPR | malware TPR | -4.34 | 7.30 | [-4.66, -4.04] | 4/6 | no | [-7.34, -1.63] | no |
| ATT+bal − PE+bal | copy 20 prepend | 0.1% FPR | padded-benign FPR | -0.47 | 0.99 | [-0.54, -0.41] | 0/9 | **yes** | [-0.88, -0.21] | yes |
| ATT+bal − PE+bal | copy 20 prepend | 0.1% FPR | malware TPR, fit subset | -3.23 | 3.40 | [-3.82, -2.65] | 3/7 | **yes** | [-5.98, -1.55] | yes |
| ATT+bal − PE+bal | copy 50 insert | 1% FPR | malware TPR | +0.33 | 3.39 | [+0.11, +0.53] | 6/4 | no | [-0.66, +1.39] | no |
| ATT+bal − PE+bal | copy 50 insert | 1% FPR | padded-benign FPR | -0.75 | 1.79 | [-0.88, -0.62] | 3/6 | no | [-1.31, -0.31] | no |
| ATT+bal − PE+bal | copy 50 insert | 1% FPR | malware TPR, fit subset | -2.08 | 4.90 | [-2.75, -1.41] | 3/7 | **yes** | [-7.11, +1.13] | no |
| ATT+bal − PE+bal | copy 50 insert | 0.1% FPR | malware TPR | -5.28 | 7.14 | [-5.65, -4.91] | 3/7 | **yes** | [-9.11, -1.79] | yes |
| ATT+bal − PE+bal | copy 50 insert | 0.1% FPR | padded-benign FPR | -0.28 | 0.17 | [-0.37, -0.20] | 0/10 | **yes** | [-0.47, -0.15] | yes |
| ATT+bal − PE+bal | copy 50 insert | 0.1% FPR | malware TPR, fit subset | -6.21 | 3.59 | [-6.95, -5.53] | 1/9 | **yes** | [-12.78, -2.51] | yes |
| ATT+bal − PE+bal | copy 50 prepend | 1% FPR | malware TPR | -1.49 | 3.42 | [-1.72, -1.27] | 4/6 | no | [-3.01, -0.36] | no |
| ATT+bal − PE+bal | copy 50 prepend | 1% FPR | padded-benign FPR | -1.32 | 4.02 | [-1.46, -1.17] | 4/6 | no | [-2.00, -0.73] | no |
| ATT+bal − PE+bal | copy 50 prepend | 1% FPR | malware TPR, fit subset | -2.10 | 4.89 | [-2.78, -1.43] | 3/7 | **yes** | [-7.19, +1.04] | no |
| ATT+bal − PE+bal | copy 50 prepend | 0.1% FPR | malware TPR | -3.82 | 5.64 | [-4.12, -3.54] | 3/7 | **yes** | [-5.91, -2.21] | yes |
| ATT+bal − PE+bal | copy 50 prepend | 0.1% FPR | padded-benign FPR | -0.90 | 1.48 | [-0.99, -0.81] | 0/10 | **yes** | [-1.48, -0.44] | yes |
| ATT+bal − PE+bal | copy 50 prepend | 0.1% FPR | malware TPR, fit subset | -6.57 | 3.78 | [-7.26, -5.80] | 1/9 | **yes** | [-13.32, -2.69] | yes |
| ATT+bal − PE+bal | rot 25 | 1% FPR | malware TPR | -0.48 | 8.95 | [-0.76, -0.17] | 7/3 | **yes** | [-4.29, +2.78] | no |
| ATT+bal − PE+bal | rot 25 | 1% FPR | padded-benign FPR | -0.71 | 9.94 | [-0.99, -0.42] | 4/6 | no | [-4.61, +4.74] | no |
| ATT+bal − PE+bal | rot 25 | 1% FPR | malware TPR, fit subset | +1.18 | 5.44 | [+0.76, +1.58] | 6/4 | no | [-0.54, +2.66] | no |
| ATT+bal − PE+bal | rot 25 | 0.1% FPR | malware TPR | +2.23 | 8.37 | [+1.88, +2.57] | 4/6 | no | [-1.03, +5.41] | no |
| ATT+bal − PE+bal | rot 25 | 0.1% FPR | padded-benign FPR | -0.05 | 0.09 | [-0.09, -0.02] | 4/6 | no | [-0.11, -0.01] | no |
| ATT+bal − PE+bal | rot 25 | 0.1% FPR | malware TPR, fit subset | +9.05 | 15.05 | [+8.37, +9.81] | 8/2 | **yes** | [+4.55, +15.05] | yes |
| ATT+bal − PE+bal | rot 50 | 1% FPR | malware TPR | -0.67 | 7.28 | [-0.97, -0.37] | 5/5 | no | [-4.22, +2.70] | no |
| ATT+bal − PE+bal | rot 50 | 1% FPR | padded-benign FPR | -4.63 | 10.73 | [-5.01, -4.25] | 3/7 | **yes** | [-12.51, +2.61] | no |
| ATT+bal − PE+bal | rot 50 | 1% FPR | malware TPR, fit subset | +1.54 | 6.32 | [+1.14, +1.91] | 5/5 | no | [-0.69, +3.46] | no |
| ATT+bal − PE+bal | rot 50 | 0.1% FPR | malware TPR | +3.52 | 8.41 | [+3.16, +3.90] | 6/4 | no | [-0.15, +8.12] | no |
| ATT+bal − PE+bal | rot 50 | 0.1% FPR | padded-benign FPR | -0.12 | 0.17 | [-0.18, -0.07] | 4/6 | no | [-0.21, -0.05] | no |
| ATT+bal − PE+bal | rot 50 | 0.1% FPR | malware TPR, fit subset | +8.49 | 14.29 | [+7.80, +9.21] | 8/2 | **yes** | [-0.07, +17.27] | no |
| ATT+bal − PE+bal | inj 5 | 1% FPR | malware TPR | +0.72 | 2.93 | [+0.51, +0.92] | 7/3 | **yes** | [-0.66, +1.96] | no |
| ATT+bal − PE+bal | inj 5 | 1% FPR | padded-benign FPR | -0.46 | 1.12 | [-0.57, -0.33] | 2/8 | **yes** | [-0.93, -0.09] | yes |
| ATT+bal − PE+bal | inj 5 | 0.1% FPR | malware TPR | +2.99 | 10.73 | [+2.59, +3.36] | 6/4 | no | [-1.67, +7.04] | no |
| ATT+bal − PE+bal | inj 5 | 0.1% FPR | padded-benign FPR | +0.02 | 0.03 | [-0.02, +0.07] | 8/2 | no | [-0.03, +0.07] | no |
| ATT+bal − PE+bal | inj 20 | 1% FPR | malware TPR | +0.76 | 4.87 | [+0.55, +0.96] | 8/2 | **yes** | [-0.43, +2.08] | no |
| ATT+bal − PE+bal | inj 20 | 1% FPR | padded-benign FPR | -0.35 | 0.73 | [-0.46, -0.25] | 2/7 | **yes** | [-0.76, -0.01] | yes |
| ATT+bal − PE+bal | inj 20 | 0.1% FPR | malware TPR | +0.89 | 7.04 | [+0.51, +1.27] | 6/4 | no | [-3.07, +5.31] | no |
| ATT+bal − PE+bal | inj 20 | 0.1% FPR | padded-benign FPR | +0.02 | 0.05 | [-0.02, +0.06] | 6/3 | no | [-0.02, +0.07] | no |
| ATT+bal − PE+bal | inj 50 | 1% FPR | malware TPR | +0.95 | 4.45 | [+0.73, +1.16] | 8/2 | **yes** | [-0.04, +2.25] | no |
| ATT+bal − PE+bal | inj 50 | 1% FPR | padded-benign FPR | -0.38 | 0.58 | [-0.48, -0.27] | 3/7 | **yes** | [-0.71, -0.09] | yes |
| ATT+bal − PE+bal | inj 50 | 0.1% FPR | malware TPR | +1.98 | 9.66 | [+1.54, +2.43] | 6/4 | no | [-3.10, +7.12] | no |
| ATT+bal − PE+bal | inj 50 | 0.1% FPR | padded-benign FPR | -0.01 | 0.04 | [-0.05, +0.03] | 4/5 | no | [-0.05, +0.03] | no |

**Further edits, ATT+bal − v2-PE (10 paired seeds): A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; meets rule = CI excludes 0 and ≥ 7 of 10 seeds with the same sign (descriptive: none of these robustness comparisons is a pre-registered claim).**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | meets rule (descriptive) | CI (cluster bootstrap) | meets rule, cluster (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal − v2-PE | rare 5 insert | 1% FPR | malware TPR | +10.65 | 5.94 | [+10.10, +11.18] | 10/0 | **yes** | [+4.72, +16.32] | yes |
| ATT+bal − v2-PE | rare 5 insert | 1% FPR | padded-benign FPR | +0.26 | 0.42 | [+0.12, +0.40] | 8/2 | **yes** | [+0.11, +0.45] | yes |
| ATT+bal − v2-PE | rare 5 insert | 1% FPR | malware TPR, fit subset | +19.64 | 8.16 | [+18.55, +20.75] | 10/0 | **yes** | [+10.06, +27.86] | yes |
| ATT+bal − v2-PE | rare 5 insert | 0.1% FPR | malware TPR | +14.83 | 5.83 | [+14.20, +15.49] | 10/0 | **yes** | [+6.14, +21.31] | yes |
| ATT+bal − v2-PE | rare 5 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.03 | [-0.01, +0.05] | 7/1 | no | [-0.01, +0.05] | no |
| ATT+bal − v2-PE | rare 5 insert | 0.1% FPR | malware TPR, fit subset | +23.00 | 8.20 | [+21.87, +24.10] | 10/0 | **yes** | [+8.09, +35.17] | yes |
| ATT+bal − v2-PE | rare 5 prepend | 1% FPR | malware TPR | +34.69 | 11.47 | [+34.00, +35.40] | 10/0 | **yes** | [+26.24, +42.70] | yes |
| ATT+bal − v2-PE | rare 5 prepend | 1% FPR | padded-benign FPR | -0.72 | 1.68 | [-0.90, -0.54] | 4/6 | no | [-1.16, -0.22] | no |
| ATT+bal − v2-PE | rare 5 prepend | 1% FPR | malware TPR, fit subset | +42.88 | 10.64 | [+41.56, +44.13] | 10/0 | **yes** | [+23.57, +56.44] | yes |
| ATT+bal − v2-PE | rare 5 prepend | 0.1% FPR | malware TPR | +39.08 | 7.40 | [+38.38, +39.91] | 10/0 | **yes** | [+28.85, +47.40] | yes |
| ATT+bal − v2-PE | rare 5 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.05 | [+0.04, +0.14] | 10/0 | **yes** | [+0.03, +0.16] | yes |
| ATT+bal − v2-PE | rare 5 prepend | 0.1% FPR | malware TPR, fit subset | +42.92 | 9.45 | [+41.55, +44.31] | 10/0 | **yes** | [+21.07, +56.80] | yes |
| ATT+bal − v2-PE | rare 20 insert | 1% FPR | malware TPR | +25.60 | 7.83 | [+24.93, +26.35] | 10/0 | **yes** | [+16.46, +33.50] | yes |
| ATT+bal − v2-PE | rare 20 insert | 1% FPR | padded-benign FPR | +0.47 | 1.16 | [+0.34, +0.62] | 6/4 | no | [+0.30, +0.67] | no |
| ATT+bal − v2-PE | rare 20 insert | 1% FPR | malware TPR, fit subset | +32.94 | 11.89 | [+31.35, +34.57] | 10/0 | **yes** | [+14.42, +45.99] | yes |
| ATT+bal − v2-PE | rare 20 insert | 0.1% FPR | malware TPR | +19.42 | 6.05 | [+18.72, +20.16] | 10/0 | **yes** | [+10.51, +28.35] | yes |
| ATT+bal − v2-PE | rare 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.00, +0.02] | 5/3 | no | [-0.00, +0.03] | no |
| ATT+bal − v2-PE | rare 20 insert | 0.1% FPR | malware TPR, fit subset | +4.65 | 2.75 | [+3.88, +5.41] | 9/0 | **yes** | [+1.04, +12.87] | yes |
| ATT+bal − v2-PE | rare 20 prepend | 1% FPR | malware TPR | +59.14 | 7.52 | [+58.27, +59.99] | 10/0 | **yes** | [+45.90, +68.65] | yes |
| ATT+bal − v2-PE | rare 20 prepend | 1% FPR | padded-benign FPR | -0.09 | 2.23 | [-0.26, +0.11] | 6/4 | no | [-0.37, +0.25] | no |
| ATT+bal − v2-PE | rare 20 prepend | 1% FPR | malware TPR, fit subset | +48.47 | 12.83 | [+46.58, +50.35] | 10/0 | **yes** | [+26.77, +63.35] | yes |
| ATT+bal − v2-PE | rare 20 prepend | 0.1% FPR | malware TPR | +38.45 | 7.03 | [+37.62, +39.30] | 10/0 | **yes** | [+26.89, +49.01] | yes |
| ATT+bal − v2-PE | rare 20 prepend | 0.1% FPR | padded-benign FPR | +0.03 | 0.05 | [-0.01, +0.08] | 8/2 | no | [-0.01, +0.09] | no |
| ATT+bal − v2-PE | rare 20 prepend | 0.1% FPR | malware TPR, fit subset | +11.80 | 4.69 | [+10.53, +13.10] | 10/0 | **yes** | [+4.29, +28.43] | yes |
| ATT+bal − v2-PE | rare 50 insert | 1% FPR | malware TPR | +27.69 | 8.77 | [+26.89, +28.47] | 10/0 | **yes** | [+16.59, +38.67] | yes |
| ATT+bal − v2-PE | rare 50 insert | 1% FPR | padded-benign FPR | +0.20 | 1.61 | [+0.05, +0.35] | 7/3 | **yes** | [-0.01, +0.43] | no |
| ATT+bal − v2-PE | rare 50 insert | 0.1% FPR | malware TPR | +18.80 | 4.47 | [+18.12, +19.47] | 10/0 | **yes** | [+8.90, +29.93] | yes |
| ATT+bal − v2-PE | rare 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.01, +0.03] | 6/1 | no | [-0.01, +0.03] | no |
| ATT+bal − v2-PE | rare 50 prepend | 1% FPR | malware TPR | +0.44 | 6.24 | [+0.24, +0.64] | 5/5 | no | [-0.54, +2.15] | no |
| ATT+bal − v2-PE | rare 50 prepend | 1% FPR | padded-benign FPR | -0.83 | 3.39 | [-0.95, -0.68] | 4/5 | no | [-0.96, -0.68] | no |
| ATT+bal − v2-PE | rare 50 prepend | 0.1% FPR | malware TPR | +0.51 | 2.26 | [+0.37, +0.65] | 7/3 | **yes** | [-0.21, +1.43] | no |
| ATT+bal − v2-PE | rare 50 prepend | 0.1% FPR | padded-benign FPR | -0.02 | 0.04 | [-0.03, -0.01] | 0/4 | no | [-0.03, -0.01] | no |
| ATT+bal − v2-PE | block 5 insert | 1% FPR | malware TPR | +3.24 | 4.27 | [+2.79, +3.67] | 8/2 | **yes** | [-0.92, +6.47] | no |
| ATT+bal − v2-PE | block 5 insert | 1% FPR | padded-benign FPR | +0.11 | 0.22 | [-0.03, +0.25] | 7/3 | no | [-0.06, +0.32] | no |
| ATT+bal − v2-PE | block 5 insert | 1% FPR | malware TPR, fit subset | +6.62 | 4.57 | [+5.83, +7.42] | 9/1 | **yes** | [+3.02, +9.21] | yes |
| ATT+bal − v2-PE | block 5 insert | 0.1% FPR | malware TPR | +8.45 | 6.90 | [+7.88, +9.08] | 9/1 | **yes** | [+0.87, +13.53] | yes |
| ATT+bal − v2-PE | block 5 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.02 | [-0.02, +0.07] | 8/0 | no | [-0.02, +0.09] | no |
| ATT+bal − v2-PE | block 5 insert | 0.1% FPR | malware TPR, fit subset | +17.16 | 9.85 | [+16.21, +18.13] | 10/0 | **yes** | [+6.65, +23.63] | yes |
| ATT+bal − v2-PE | block 5 prepend | 1% FPR | malware TPR | +21.77 | 6.46 | [+21.12, +22.36] | 10/0 | **yes** | [+13.72, +30.25] | yes |
| ATT+bal − v2-PE | block 5 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.47 | [-0.17, +0.17] | 7/3 | no | [-0.28, +0.34] | no |
| ATT+bal − v2-PE | block 5 prepend | 1% FPR | malware TPR, fit subset | +24.46 | 6.01 | [+23.23, +25.69] | 10/0 | **yes** | [+10.97, +38.71] | yes |
| ATT+bal − v2-PE | block 5 prepend | 0.1% FPR | malware TPR | +30.25 | 6.25 | [+29.50, +30.99] | 10/0 | **yes** | [+19.26, +38.53] | yes |
| ATT+bal − v2-PE | block 5 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.04 | [+0.03, +0.13] | 9/0 | **yes** | [+0.03, +0.15] | yes |
| ATT+bal − v2-PE | block 5 prepend | 0.1% FPR | malware TPR, fit subset | +33.69 | 8.00 | [+32.35, +35.03] | 10/0 | **yes** | [+14.24, +49.98] | yes |
| ATT+bal − v2-PE | block 20 insert | 1% FPR | malware TPR | +7.95 | 4.67 | [+7.37, +8.51] | 9/1 | **yes** | [+2.95, +12.83] | yes |
| ATT+bal − v2-PE | block 20 insert | 1% FPR | padded-benign FPR | +0.34 | 0.89 | [+0.18, +0.50] | 8/2 | **yes** | [+0.17, +0.56] | yes |
| ATT+bal − v2-PE | block 20 insert | 1% FPR | malware TPR, fit subset | +19.09 | 5.65 | [+17.80, +20.46] | 10/0 | **yes** | [+10.17, +26.77] | yes |
| ATT+bal − v2-PE | block 20 insert | 0.1% FPR | malware TPR | +10.61 | 6.94 | [+9.94, +11.27] | 9/1 | **yes** | [+3.03, +16.25] | yes |
| ATT+bal − v2-PE | block 20 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.03 | [-0.01, +0.08] | 8/2 | no | [-0.01, +0.08] | no |
| ATT+bal − v2-PE | block 20 insert | 0.1% FPR | malware TPR, fit subset | +20.18 | 8.60 | [+18.97, +21.43] | 10/0 | **yes** | [+7.59, +28.91] | yes |
| ATT+bal − v2-PE | block 20 prepend | 1% FPR | malware TPR | +43.39 | 7.55 | [+42.63, +44.19] | 10/0 | **yes** | [+33.20, +52.62] | yes |
| ATT+bal − v2-PE | block 20 prepend | 1% FPR | padded-benign FPR | -2.37 | 5.09 | [-2.62, -2.13] | 4/6 | no | [-2.81, -1.90] | no |
| ATT+bal − v2-PE | block 20 prepend | 1% FPR | malware TPR, fit subset | +50.55 | 6.60 | [+49.09, +52.10] | 10/0 | **yes** | [+29.33, +63.66] | yes |
| ATT+bal − v2-PE | block 20 prepend | 0.1% FPR | malware TPR | +42.89 | 6.89 | [+42.11, +43.76] | 10/0 | **yes** | [+31.87, +51.63] | yes |
| ATT+bal − v2-PE | block 20 prepend | 0.1% FPR | padded-benign FPR | -0.02 | 0.22 | [-0.08, +0.05] | 5/5 | no | [-0.09, +0.06] | no |
| ATT+bal − v2-PE | block 20 prepend | 0.1% FPR | malware TPR, fit subset | +40.26 | 8.52 | [+38.86, +41.77] | 10/0 | **yes** | [+19.61, +55.62] | yes |
| ATT+bal − v2-PE | block 50 insert | 1% FPR | malware TPR | +7.43 | 5.79 | [+6.80, +8.01] | 9/1 | **yes** | [+2.38, +12.03] | yes |
| ATT+bal − v2-PE | block 50 insert | 1% FPR | padded-benign FPR | +1.52 | 1.48 | [+1.29, +1.74] | 8/2 | **yes** | [+1.13, +2.01] | yes |
| ATT+bal − v2-PE | block 50 insert | 1% FPR | malware TPR, fit subset | +20.63 | 7.26 | [+19.06, +22.35] | 10/0 | **yes** | [+10.55, +29.17] | yes |
| ATT+bal − v2-PE | block 50 insert | 0.1% FPR | malware TPR | +6.24 | 6.89 | [+5.56, +6.88] | 9/1 | **yes** | [+0.01, +10.85] | yes |
| ATT+bal − v2-PE | block 50 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.04 | [-0.01, +0.06] | 7/1 | no | [-0.00, +0.06] | no |
| ATT+bal − v2-PE | block 50 insert | 0.1% FPR | malware TPR, fit subset | +8.82 | 7.05 | [+7.47, +10.08] | 9/1 | **yes** | [+2.63, +16.82] | yes |
| ATT+bal − v2-PE | block 50 prepend | 1% FPR | malware TPR | +51.32 | 4.98 | [+50.49, +52.14] | 10/0 | **yes** | [+39.87, +59.56] | yes |
| ATT+bal − v2-PE | block 50 prepend | 1% FPR | padded-benign FPR | -1.33 | 4.76 | [-1.63, -1.03] | 5/5 | no | [-1.89, -0.69] | no |
| ATT+bal − v2-PE | block 50 prepend | 1% FPR | malware TPR, fit subset | +48.68 | 6.94 | [+46.94, +50.49] | 10/0 | **yes** | [+31.64, +60.17] | yes |
| ATT+bal − v2-PE | block 50 prepend | 0.1% FPR | malware TPR | +35.90 | 6.28 | [+35.11, +36.72] | 10/0 | **yes** | [+25.75, +45.16] | yes |
| ATT+bal − v2-PE | block 50 prepend | 0.1% FPR | padded-benign FPR | -0.06 | 0.12 | [-0.11, -0.00] | 4/5 | no | [-0.12, +0.00] | no |
| ATT+bal − v2-PE | block 50 prepend | 0.1% FPR | malware TPR, fit subset | +24.02 | 7.88 | [+22.63, +25.63] | 10/0 | **yes** | [+12.22, +36.86] | yes |
| ATT+bal − v2-PE | copy 5 insert | 1% FPR | malware TPR | +1.53 | 3.71 | [+1.11, +1.92] | 8/2 | **yes** | [-3.21, +4.95] | no |
| ATT+bal − v2-PE | copy 5 insert | 1% FPR | padded-benign FPR | +0.06 | 0.14 | [-0.07, +0.19] | 6/3 | no | [-0.11, +0.24] | no |
| ATT+bal − v2-PE | copy 5 insert | 1% FPR | malware TPR, fit subset | +2.15 | 4.21 | [+1.48, +2.85] | 7/3 | **yes** | [-2.09, +5.90] | no |
| ATT+bal − v2-PE | copy 5 insert | 0.1% FPR | malware TPR | +9.54 | 7.15 | [+8.94, +10.15] | 10/0 | **yes** | [+1.29, +15.39] | yes |
| ATT+bal − v2-PE | copy 5 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.04 | [-0.02, +0.06] | 7/2 | no | [-0.02, +0.07] | no |
| ATT+bal − v2-PE | copy 5 insert | 0.1% FPR | malware TPR, fit subset | +12.92 | 11.39 | [+12.03, +13.86] | 9/1 | **yes** | [+4.34, +21.45] | yes |
| ATT+bal − v2-PE | copy 5 prepend | 1% FPR | malware TPR | +12.46 | 5.44 | [+11.97, +12.97] | 10/0 | **yes** | [+5.17, +19.83] | yes |
| ATT+bal − v2-PE | copy 5 prepend | 1% FPR | padded-benign FPR | -0.34 | 0.31 | [-0.49, -0.20] | 1/9 | **yes** | [-0.71, -0.02] | yes |
| ATT+bal − v2-PE | copy 5 prepend | 1% FPR | malware TPR, fit subset | +9.77 | 4.43 | [+8.74, +10.80] | 10/0 | **yes** | [-1.50, +21.65] | no |
| ATT+bal − v2-PE | copy 5 prepend | 0.1% FPR | malware TPR | +20.65 | 6.61 | [+19.97, +21.39] | 10/0 | **yes** | [+9.09, +29.59] | yes |
| ATT+bal − v2-PE | copy 5 prepend | 0.1% FPR | padded-benign FPR | +0.04 | 0.06 | [-0.01, +0.10] | 7/2 | no | [-0.01, +0.10] | no |
| ATT+bal − v2-PE | copy 5 prepend | 0.1% FPR | malware TPR, fit subset | +19.49 | 9.43 | [+18.31, +20.65] | 10/0 | **yes** | [+4.45, +37.51] | yes |
| ATT+bal − v2-PE | copy 20 insert | 1% FPR | malware TPR | +7.48 | 5.09 | [+6.99, +7.97] | 9/1 | **yes** | [+1.35, +13.61] | yes |
| ATT+bal − v2-PE | copy 20 insert | 1% FPR | padded-benign FPR | -0.11 | 0.24 | [-0.25, +0.04] | 4/6 | no | [-0.40, +0.15] | no |
| ATT+bal − v2-PE | copy 20 insert | 1% FPR | malware TPR, fit subset | +1.42 | 3.19 | [+0.46, +2.41] | 6/4 | no | [-2.33, +6.70] | no |
| ATT+bal − v2-PE | copy 20 insert | 0.1% FPR | malware TPR | +14.07 | 6.99 | [+13.41, +14.76] | 10/0 | **yes** | [+5.01, +21.03] | yes |
| ATT+bal − v2-PE | copy 20 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.05 | [-0.02, +0.06] | 6/3 | no | [-0.02, +0.07] | no |
| ATT+bal − v2-PE | copy 20 insert | 0.1% FPR | malware TPR, fit subset | +9.57 | 11.40 | [+8.55, +10.63] | 10/0 | **yes** | [+3.30, +16.03] | yes |
| ATT+bal − v2-PE | copy 20 prepend | 1% FPR | malware TPR | +20.14 | 9.84 | [+19.56, +20.71] | 10/0 | **yes** | [+11.61, +28.65] | yes |
| ATT+bal − v2-PE | copy 20 prepend | 1% FPR | padded-benign FPR | -1.81 | 1.76 | [-2.03, -1.62] | 1/9 | **yes** | [-2.26, -1.35] | yes |
| ATT+bal − v2-PE | copy 20 prepend | 1% FPR | malware TPR, fit subset | +3.53 | 3.68 | [+2.63, +4.49] | 9/1 | **yes** | [-1.87, +10.67] | no |
| ATT+bal − v2-PE | copy 20 prepend | 0.1% FPR | malware TPR | +30.90 | 9.25 | [+30.20, +31.71] | 10/0 | **yes** | [+18.74, +41.10] | yes |
| ATT+bal − v2-PE | copy 20 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.10 | [-0.07, +0.08] | 5/5 | no | [-0.10, +0.10] | no |
| ATT+bal − v2-PE | copy 20 prepend | 0.1% FPR | malware TPR, fit subset | +11.43 | 11.21 | [+10.37, +12.57] | 10/0 | **yes** | [+2.83, +21.95] | yes |
| ATT+bal − v2-PE | copy 50 insert | 1% FPR | malware TPR | +12.32 | 7.27 | [+11.80, +12.80] | 9/1 | **yes** | [+5.89, +18.65] | yes |
| ATT+bal − v2-PE | copy 50 insert | 1% FPR | padded-benign FPR | +0.03 | 0.47 | [-0.13, +0.21] | 5/5 | no | [-0.29, +0.32] | no |
| ATT+bal − v2-PE | copy 50 insert | 1% FPR | malware TPR, fit subset | -1.83 | 3.36 | [-2.62, -1.08] | 4/6 | no | [-6.02, +0.81] | no |
| ATT+bal − v2-PE | copy 50 insert | 0.1% FPR | malware TPR | +18.96 | 7.42 | [+18.25, +19.68] | 10/0 | **yes** | [+8.08, +27.19] | yes |
| ATT+bal − v2-PE | copy 50 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.14 | [-0.09, +0.05] | 3/7 | no | [-0.13, +0.08] | no |
| ATT+bal − v2-PE | copy 50 insert | 0.1% FPR | malware TPR, fit subset | +0.01 | 7.91 | [-0.83, +0.93] | 4/6 | no | [-5.15, +3.08] | no |
| ATT+bal − v2-PE | copy 50 prepend | 1% FPR | malware TPR | +21.78 | 9.23 | [+21.09, +22.47] | 10/0 | **yes** | [+11.78, +32.16] | yes |
| ATT+bal − v2-PE | copy 50 prepend | 1% FPR | padded-benign FPR | -1.03 | 2.22 | [-1.26, -0.80] | 3/7 | **yes** | [-1.96, +0.04] | no |
| ATT+bal − v2-PE | copy 50 prepend | 1% FPR | malware TPR, fit subset | -1.56 | 3.59 | [-2.34, -0.77] | 4/6 | no | [-5.25, +1.07] | no |
| ATT+bal − v2-PE | copy 50 prepend | 0.1% FPR | malware TPR | +33.61 | 8.11 | [+32.75, +34.42] | 10/0 | **yes** | [+19.72, +45.14] | yes |
| ATT+bal − v2-PE | copy 50 prepend | 0.1% FPR | padded-benign FPR | -0.12 | 0.13 | [-0.19, -0.04] | 2/8 | **yes** | [-0.24, -0.01] | yes |
| ATT+bal − v2-PE | copy 50 prepend | 0.1% FPR | malware TPR, fit subset | -0.12 | 7.26 | [-0.95, +0.73] | 4/6 | no | [-4.79, +3.36] | no |
| ATT+bal − v2-PE | rot 25 | 1% FPR | malware TPR | +10.84 | 6.88 | [+10.27, +11.47] | 10/0 | **yes** | [+0.15, +21.42] | yes |
| ATT+bal − v2-PE | rot 25 | 1% FPR | padded-benign FPR | +7.47 | 7.41 | [+7.01, +7.96] | 8/2 | **yes** | [-0.36, +17.78] | no |
| ATT+bal − v2-PE | rot 25 | 1% FPR | malware TPR, fit subset | +16.11 | 11.10 | [+14.85, +17.42] | 10/0 | **yes** | [-2.64, +35.12] | no |
| ATT+bal − v2-PE | rot 25 | 0.1% FPR | malware TPR | +16.37 | 7.95 | [+15.72, +16.99] | 10/0 | **yes** | [+6.41, +28.00] | yes |
| ATT+bal − v2-PE | rot 25 | 0.1% FPR | padded-benign FPR | -0.08 | 0.11 | [-0.13, -0.02] | 3/7 | **yes** | [-0.15, -0.02] | yes |
| ATT+bal − v2-PE | rot 25 | 0.1% FPR | malware TPR, fit subset | +30.61 | 14.91 | [+29.23, +31.93] | 10/0 | **yes** | [+10.86, +51.04] | yes |
| ATT+bal − v2-PE | rot 50 | 1% FPR | malware TPR | +7.77 | 10.47 | [+7.15, +8.42] | 9/1 | **yes** | [-4.48, +18.09] | no |
| ATT+bal − v2-PE | rot 50 | 1% FPR | padded-benign FPR | +4.75 | 6.09 | [+4.34, +5.17] | 9/1 | **yes** | [-1.30, +10.72] | no |
| ATT+bal − v2-PE | rot 50 | 1% FPR | malware TPR, fit subset | +10.15 | 8.70 | [+9.10, +11.32] | 10/0 | **yes** | [-3.75, +24.25] | no |
| ATT+bal − v2-PE | rot 50 | 0.1% FPR | malware TPR | +17.33 | 5.88 | [+16.71, +17.97] | 10/0 | **yes** | [+8.57, +27.54] | yes |
| ATT+bal − v2-PE | rot 50 | 0.1% FPR | padded-benign FPR | -0.08 | 0.17 | [-0.15, -0.01] | 3/6 | no | [-0.18, +0.00] | no |
| ATT+bal − v2-PE | rot 50 | 0.1% FPR | malware TPR, fit subset | +21.66 | 13.10 | [+20.50, +22.88] | 9/1 | **yes** | [+5.63, +40.43] | yes |
| ATT+bal − v2-PE | inj 5 | 1% FPR | malware TPR | +7.27 | 4.32 | [+6.81, +7.73] | 10/0 | **yes** | [+2.63, +11.36] | yes |
| ATT+bal − v2-PE | inj 5 | 1% FPR | padded-benign FPR | +0.18 | 0.15 | [+0.02, +0.32] | 9/1 | **yes** | [-0.07, +0.43] | no |
| ATT+bal − v2-PE | inj 5 | 0.1% FPR | malware TPR | +20.66 | 6.93 | [+19.99, +21.35] | 10/0 | **yes** | [+10.11, +28.50] | yes |
| ATT+bal − v2-PE | inj 5 | 0.1% FPR | padded-benign FPR | +0.07 | 0.02 | [+0.02, +0.12] | 10/0 | **yes** | [+0.02, +0.13] | yes |
| ATT+bal − v2-PE | inj 20 | 1% FPR | malware TPR | +19.96 | 6.59 | [+19.38, +20.55] | 10/0 | **yes** | [+12.31, +27.32] | yes |
| ATT+bal − v2-PE | inj 20 | 1% FPR | padded-benign FPR | +0.17 | 0.38 | [+0.03, +0.31] | 8/2 | **yes** | [-0.10, +0.46] | no |
| ATT+bal − v2-PE | inj 20 | 0.1% FPR | malware TPR | +28.68 | 7.09 | [+27.94, +29.45] | 10/0 | **yes** | [+18.66, +37.93] | yes |
| ATT+bal − v2-PE | inj 20 | 0.1% FPR | padded-benign FPR | +0.07 | 0.04 | [+0.02, +0.13] | 10/0 | **yes** | [+0.02, +0.14] | yes |
| ATT+bal − v2-PE | inj 50 | 1% FPR | malware TPR | +29.09 | 4.97 | [+28.39, +29.77] | 10/0 | **yes** | [+18.15, +40.07] | yes |
| ATT+bal − v2-PE | inj 50 | 1% FPR | padded-benign FPR | +0.21 | 0.57 | [+0.07, +0.35] | 8/2 | **yes** | [-0.04, +0.46] | no |
| ATT+bal − v2-PE | inj 50 | 0.1% FPR | malware TPR | +34.95 | 6.51 | [+34.17, +35.73] | 10/0 | **yes** | [+24.09, +45.28] | yes |
| ATT+bal − v2-PE | inj 50 | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.01, +0.09] | 8/0 | **yes** | [-0.00, +0.09] | no |

**Further edits, PE+bal − v2-PE (10 paired seeds): A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; meets rule = CI excludes 0 and ≥ 7 of 10 seeds with the same sign (descriptive: none of these robustness comparisons is a pre-registered claim).**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | meets rule (descriptive) | CI (cluster bootstrap) | meets rule, cluster (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| PE+bal − v2-PE | rare 5 insert | 1% FPR | malware TPR | +11.13 | 5.56 | [+10.57, +11.64] | 10/0 | **yes** | [+4.93, +17.46] | yes |
| PE+bal − v2-PE | rare 5 insert | 1% FPR | padded-benign FPR | +0.78 | 0.39 | [+0.62, +0.94] | 10/0 | **yes** | [+0.52, +1.09] | yes |
| PE+bal − v2-PE | rare 5 insert | 1% FPR | malware TPR, fit subset | +22.40 | 8.22 | [+21.31, +23.49] | 10/0 | **yes** | [+11.97, +33.43] | yes |
| PE+bal − v2-PE | rare 5 insert | 0.1% FPR | malware TPR | +16.44 | 9.50 | [+15.90, +16.99] | 10/0 | **yes** | [+8.86, +21.78] | yes |
| PE+bal − v2-PE | rare 5 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.05] | 8/1 | **yes** | [+0.00, +0.05] | no |
| PE+bal − v2-PE | rare 5 insert | 0.1% FPR | malware TPR, fit subset | +24.93 | 12.77 | [+23.81, +25.99] | 10/0 | **yes** | [+8.67, +36.10] | yes |
| PE+bal − v2-PE | rare 5 prepend | 1% FPR | malware TPR | +34.72 | 14.31 | [+34.07, +35.42] | 10/0 | **yes** | [+25.78, +43.01] | yes |
| PE+bal − v2-PE | rare 5 prepend | 1% FPR | padded-benign FPR | +0.65 | 1.48 | [+0.45, +0.85] | 7/3 | **yes** | [-0.12, +1.54] | no |
| PE+bal − v2-PE | rare 5 prepend | 1% FPR | malware TPR, fit subset | +43.93 | 13.23 | [+42.61, +45.25] | 10/0 | **yes** | [+25.10, +56.10] | yes |
| PE+bal − v2-PE | rare 5 prepend | 0.1% FPR | malware TPR | +35.45 | 10.00 | [+34.77, +36.14] | 10/0 | **yes** | [+26.14, +43.94] | yes |
| PE+bal − v2-PE | rare 5 prepend | 0.1% FPR | padded-benign FPR | +0.11 | 0.12 | [+0.07, +0.17] | 10/0 | **yes** | [+0.06, +0.19] | yes |
| PE+bal − v2-PE | rare 5 prepend | 0.1% FPR | malware TPR, fit subset | +30.94 | 7.56 | [+29.64, +32.34] | 10/0 | **yes** | [+12.48, +48.91] | yes |
| PE+bal − v2-PE | rare 20 insert | 1% FPR | malware TPR | +27.36 | 6.36 | [+26.69, +28.06] | 10/0 | **yes** | [+17.39, +36.16] | yes |
| PE+bal − v2-PE | rare 20 insert | 1% FPR | padded-benign FPR | +1.63 | 0.83 | [+1.44, +1.83] | 10/0 | **yes** | [+1.23, +2.08] | yes |
| PE+bal − v2-PE | rare 20 insert | 1% FPR | malware TPR, fit subset | +42.70 | 7.96 | [+40.91, +44.47] | 10/0 | **yes** | [+22.16, +58.61] | yes |
| PE+bal − v2-PE | rare 20 insert | 0.1% FPR | malware TPR | +22.73 | 8.11 | [+22.10, +23.34] | 10/0 | **yes** | [+15.36, +29.44] | yes |
| PE+bal − v2-PE | rare 20 insert | 0.1% FPR | padded-benign FPR | +0.07 | 0.10 | [+0.04, +0.10] | 9/0 | **yes** | [+0.04, +0.11] | yes |
| PE+bal − v2-PE | rare 20 insert | 0.1% FPR | malware TPR, fit subset | +12.96 | 7.75 | [+11.86, +14.03] | 10/0 | **yes** | [+6.01, +18.92] | yes |
| PE+bal − v2-PE | rare 20 prepend | 1% FPR | malware TPR | +58.51 | 6.16 | [+57.68, +59.35] | 10/0 | **yes** | [+46.06, +67.38] | yes |
| PE+bal − v2-PE | rare 20 prepend | 1% FPR | padded-benign FPR | +2.30 | 1.80 | [+2.06, +2.56] | 9/1 | **yes** | [+1.54, +3.01] | yes |
| PE+bal − v2-PE | rare 20 prepend | 1% FPR | malware TPR, fit subset | +52.58 | 8.14 | [+50.70, +54.45] | 10/0 | **yes** | [+33.01, +66.55] | yes |
| PE+bal − v2-PE | rare 20 prepend | 0.1% FPR | malware TPR | +28.74 | 5.34 | [+28.03, +29.46] | 10/0 | **yes** | [+21.14, +36.21] | yes |
| PE+bal − v2-PE | rare 20 prepend | 0.1% FPR | padded-benign FPR | +0.22 | 0.38 | [+0.17, +0.28] | 8/1 | **yes** | [+0.14, +0.31] | yes |
| PE+bal − v2-PE | rare 20 prepend | 0.1% FPR | malware TPR, fit subset | +12.84 | 3.71 | [+11.66, +14.03] | 10/0 | **yes** | [+5.90, +23.77] | yes |
| PE+bal − v2-PE | rare 50 insert | 1% FPR | malware TPR | +30.15 | 5.51 | [+29.46, +30.91] | 10/0 | **yes** | [+19.46, +40.42] | yes |
| PE+bal − v2-PE | rare 50 insert | 1% FPR | padded-benign FPR | +0.88 | 1.36 | [+0.72, +1.05] | 7/2 | **yes** | [+0.47, +1.28] | yes |
| PE+bal − v2-PE | rare 50 insert | 0.1% FPR | malware TPR | +17.47 | 4.91 | [+16.89, +18.02] | 10/0 | **yes** | [+9.61, +25.39] | yes |
| PE+bal − v2-PE | rare 50 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.07 | [+0.02, +0.06] | 7/1 | **yes** | [+0.01, +0.07] | yes |
| PE+bal − v2-PE | rare 50 prepend | 1% FPR | malware TPR | +2.29 | 5.04 | [+2.03, +2.52] | 7/3 | **yes** | [+1.80, +3.05] | yes |
| PE+bal − v2-PE | rare 50 prepend | 1% FPR | padded-benign FPR | +1.55 | 4.01 | [+1.34, +1.77] | 8/2 | **yes** | [+1.35, +1.77] | yes |
| PE+bal − v2-PE | rare 50 prepend | 0.1% FPR | malware TPR | +0.31 | 1.52 | [+0.20, +0.43] | 8/2 | **yes** | [-0.05, +0.77] | no |
| PE+bal − v2-PE | rare 50 prepend | 0.1% FPR | padded-benign FPR | +0.09 | 0.15 | [+0.05, +0.12] | 6/2 | no | [+0.05, +0.13] | no |
| PE+bal − v2-PE | block 5 insert | 1% FPR | malware TPR | +2.25 | 3.83 | [+1.82, +2.66] | 8/2 | **yes** | [-1.82, +5.32] | no |
| PE+bal − v2-PE | block 5 insert | 1% FPR | padded-benign FPR | +0.09 | 0.24 | [-0.03, +0.21] | 6/4 | no | [-0.06, +0.24] | no |
| PE+bal − v2-PE | block 5 insert | 1% FPR | malware TPR, fit subset | +5.61 | 4.63 | [+4.83, +6.42] | 9/1 | **yes** | [+2.11, +8.42] | yes |
| PE+bal − v2-PE | block 5 insert | 0.1% FPR | malware TPR | +7.60 | 9.07 | [+7.15, +8.07] | 8/2 | **yes** | [+2.06, +11.70] | yes |
| PE+bal − v2-PE | block 5 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.04 | [+0.01, +0.08] | 8/1 | **yes** | [+0.01, +0.08] | yes |
| PE+bal − v2-PE | block 5 insert | 0.1% FPR | malware TPR, fit subset | +13.18 | 13.60 | [+12.24, +14.13] | 9/1 | **yes** | [+3.24, +19.57] | yes |
| PE+bal − v2-PE | block 5 prepend | 1% FPR | malware TPR | +20.85 | 8.16 | [+20.19, +21.44] | 10/0 | **yes** | [+12.80, +29.32] | yes |
| PE+bal − v2-PE | block 5 prepend | 1% FPR | padded-benign FPR | +0.49 | 0.92 | [+0.35, +0.64] | 7/2 | **yes** | [+0.11, +0.93] | yes |
| PE+bal − v2-PE | block 5 prepend | 1% FPR | malware TPR, fit subset | +23.41 | 6.59 | [+22.18, +24.55] | 10/0 | **yes** | [+9.82, +36.65] | yes |
| PE+bal − v2-PE | block 5 prepend | 0.1% FPR | malware TPR | +28.72 | 11.06 | [+28.10, +29.35] | 10/0 | **yes** | [+19.50, +35.77] | yes |
| PE+bal − v2-PE | block 5 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.05 | [+0.04, +0.13] | 10/0 | **yes** | [+0.03, +0.15] | yes |
| PE+bal − v2-PE | block 5 prepend | 0.1% FPR | malware TPR, fit subset | +27.77 | 9.73 | [+26.53, +29.03] | 10/0 | **yes** | [+9.16, +42.57] | yes |
| PE+bal − v2-PE | block 20 insert | 1% FPR | malware TPR | +6.88 | 3.65 | [+6.37, +7.40] | 10/0 | **yes** | [+1.93, +11.77] | yes |
| PE+bal − v2-PE | block 20 insert | 1% FPR | padded-benign FPR | +0.21 | 0.66 | [+0.07, +0.35] | 8/2 | **yes** | [+0.07, +0.36] | yes |
| PE+bal − v2-PE | block 20 insert | 1% FPR | malware TPR, fit subset | +18.47 | 6.70 | [+17.20, +19.64] | 10/0 | **yes** | [+9.68, +26.96] | yes |
| PE+bal − v2-PE | block 20 insert | 0.1% FPR | malware TPR | +11.07 | 8.31 | [+10.52, +11.66] | 9/1 | **yes** | [+4.83, +16.41] | yes |
| PE+bal − v2-PE | block 20 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.03 | [-0.00, +0.07] | 7/2 | no | [-0.00, +0.08] | no |
| PE+bal − v2-PE | block 20 insert | 0.1% FPR | malware TPR, fit subset | +20.52 | 10.76 | [+19.36, +21.66] | 10/0 | **yes** | [+7.50, +29.16] | yes |
| PE+bal − v2-PE | block 20 prepend | 1% FPR | malware TPR | +41.27 | 8.36 | [+40.56, +42.04] | 10/0 | **yes** | [+30.66, +50.60] | yes |
| PE+bal − v2-PE | block 20 prepend | 1% FPR | padded-benign FPR | -1.77 | 3.68 | [-1.99, -1.55] | 4/6 | no | [-2.24, -1.27] | no |
| PE+bal − v2-PE | block 20 prepend | 1% FPR | malware TPR, fit subset | +47.84 | 7.98 | [+46.23, +49.37] | 10/0 | **yes** | [+26.59, +60.51] | yes |
| PE+bal − v2-PE | block 20 prepend | 0.1% FPR | malware TPR | +37.45 | 7.17 | [+36.73, +38.19] | 10/0 | **yes** | [+27.22, +45.99] | yes |
| PE+bal − v2-PE | block 20 prepend | 0.1% FPR | padded-benign FPR | +0.02 | 0.21 | [-0.03, +0.08] | 7/2 | no | [-0.03, +0.10] | no |
| PE+bal − v2-PE | block 20 prepend | 0.1% FPR | malware TPR, fit subset | +30.65 | 6.10 | [+29.28, +32.09] | 10/0 | **yes** | [+13.02, +46.13] | yes |
| PE+bal − v2-PE | block 50 insert | 1% FPR | malware TPR | +6.61 | 4.30 | [+6.07, +7.12] | 9/1 | **yes** | [+1.76, +11.63] | yes |
| PE+bal − v2-PE | block 50 insert | 1% FPR | padded-benign FPR | +0.91 | 0.93 | [+0.74, +1.08] | 9/1 | **yes** | [+0.65, +1.23] | yes |
| PE+bal − v2-PE | block 50 insert | 1% FPR | malware TPR, fit subset | +21.95 | 8.18 | [+20.50, +23.51] | 10/0 | **yes** | [+10.58, +31.82] | yes |
| PE+bal − v2-PE | block 50 insert | 0.1% FPR | malware TPR | +8.10 | 7.39 | [+7.59, +8.62] | 8/2 | **yes** | [+2.90, +12.72] | yes |
| PE+bal − v2-PE | block 50 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.01, +0.08] | 8/0 | **yes** | [+0.01, +0.09] | yes |
| PE+bal − v2-PE | block 50 insert | 0.1% FPR | malware TPR, fit subset | +15.52 | 6.56 | [+14.38, +16.85] | 10/0 | **yes** | [+6.66, +21.17] | yes |
| PE+bal − v2-PE | block 50 prepend | 1% FPR | malware TPR | +46.85 | 6.90 | [+46.05, +47.65] | 10/0 | **yes** | [+35.98, +54.63] | yes |
| PE+bal − v2-PE | block 50 prepend | 1% FPR | padded-benign FPR | -0.31 | 3.86 | [-0.62, +0.01] | 5/5 | no | [-1.09, +0.46] | no |
| PE+bal − v2-PE | block 50 prepend | 1% FPR | malware TPR, fit subset | +45.47 | 8.83 | [+43.72, +47.10] | 10/0 | **yes** | [+29.35, +56.51] | yes |
| PE+bal − v2-PE | block 50 prepend | 0.1% FPR | malware TPR | +27.64 | 3.71 | [+27.00, +28.32] | 10/0 | **yes** | [+20.46, +34.04] | yes |
| PE+bal − v2-PE | block 50 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.18 | [-0.06, +0.05] | 5/5 | no | [-0.07, +0.05] | no |
| PE+bal − v2-PE | block 50 prepend | 0.1% FPR | malware TPR, fit subset | +21.00 | 4.27 | [+19.58, +22.49] | 10/0 | **yes** | [+11.23, +31.64] | yes |
| PE+bal − v2-PE | copy 5 insert | 1% FPR | malware TPR | +0.88 | 3.86 | [+0.54, +1.22] | 6/4 | no | [-2.66, +3.56] | no |
| PE+bal − v2-PE | copy 5 insert | 1% FPR | padded-benign FPR | +0.12 | 0.34 | [+0.01, +0.24] | 6/4 | no | [-0.04, +0.29] | no |
| PE+bal − v2-PE | copy 5 insert | 1% FPR | malware TPR, fit subset | +0.79 | 3.78 | [+0.14, +1.46] | 6/4 | no | [-3.51, +4.60] | no |
| PE+bal − v2-PE | copy 5 insert | 0.1% FPR | malware TPR | +9.38 | 9.51 | [+8.94, +9.86] | 8/2 | **yes** | [+3.32, +14.44] | yes |
| PE+bal − v2-PE | copy 5 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.05 | [+0.00, +0.06] | 7/2 | **yes** | [-0.00, +0.07] | no |
| PE+bal − v2-PE | copy 5 insert | 0.1% FPR | malware TPR, fit subset | +8.87 | 13.28 | [+8.09, +9.76] | 7/3 | **yes** | [+0.05, +19.19] | yes |
| PE+bal − v2-PE | copy 5 prepend | 1% FPR | malware TPR | +11.77 | 7.64 | [+11.25, +12.27] | 10/0 | **yes** | [+4.61, +19.19] | yes |
| PE+bal − v2-PE | copy 5 prepend | 1% FPR | padded-benign FPR | +0.28 | 1.64 | [+0.14, +0.41] | 5/5 | no | [-0.21, +0.94] | no |
| PE+bal − v2-PE | copy 5 prepend | 1% FPR | malware TPR, fit subset | +8.38 | 5.21 | [+7.37, +9.44] | 10/0 | **yes** | [-2.84, +19.67] | no |
| PE+bal − v2-PE | copy 5 prepend | 0.1% FPR | malware TPR | +22.58 | 10.80 | [+22.01, +23.16] | 10/0 | **yes** | [+12.98, +30.38] | yes |
| PE+bal − v2-PE | copy 5 prepend | 0.1% FPR | padded-benign FPR | +0.07 | 0.08 | [+0.03, +0.11] | 8/2 | **yes** | [+0.02, +0.13] | yes |
| PE+bal − v2-PE | copy 5 prepend | 0.1% FPR | malware TPR, fit subset | +18.18 | 8.62 | [+17.07, +19.41] | 10/0 | **yes** | [+3.07, +35.69] | yes |
| PE+bal − v2-PE | copy 20 insert | 1% FPR | malware TPR | +7.24 | 5.82 | [+6.77, +7.71] | 9/1 | **yes** | [+0.99, +13.70] | yes |
| PE+bal − v2-PE | copy 20 insert | 1% FPR | padded-benign FPR | +0.32 | 1.11 | [+0.18, +0.45] | 5/5 | no | [+0.03, +0.65] | no |
| PE+bal − v2-PE | copy 20 insert | 1% FPR | malware TPR, fit subset | +1.62 | 3.81 | [+0.74, +2.57] | 6/4 | no | [-2.18, +6.81] | no |
| PE+bal − v2-PE | copy 20 insert | 0.1% FPR | malware TPR | +17.22 | 12.55 | [+16.64, +17.79] | 10/0 | **yes** | [+9.41, +23.67] | yes |
| PE+bal − v2-PE | copy 20 insert | 0.1% FPR | padded-benign FPR | +0.10 | 0.08 | [+0.06, +0.15] | 9/1 | **yes** | [+0.05, +0.18] | yes |
| PE+bal − v2-PE | copy 20 insert | 0.1% FPR | malware TPR, fit subset | +12.30 | 12.96 | [+11.31, +13.35] | 9/1 | **yes** | [+6.33, +19.35] | yes |
| PE+bal − v2-PE | copy 20 prepend | 1% FPR | malware TPR | +20.00 | 11.38 | [+19.45, +20.58] | 10/0 | **yes** | [+11.70, +28.71] | yes |
| PE+bal − v2-PE | copy 20 prepend | 1% FPR | padded-benign FPR | -0.83 | 2.78 | [-1.03, -0.65] | 2/8 | **yes** | [-1.62, +0.16] | no |
| PE+bal − v2-PE | copy 20 prepend | 1% FPR | malware TPR, fit subset | +3.73 | 4.26 | [+2.80, +4.76] | 9/1 | **yes** | [-1.57, +10.35] | no |
| PE+bal − v2-PE | copy 20 prepend | 0.1% FPR | malware TPR | +35.24 | 11.65 | [+34.57, +35.97] | 10/0 | **yes** | [+22.95, +46.74] | yes |
| PE+bal − v2-PE | copy 20 prepend | 0.1% FPR | padded-benign FPR | +0.47 | 1.05 | [+0.39, +0.56] | 9/1 | **yes** | [+0.19, +0.87] | yes |
| PE+bal − v2-PE | copy 20 prepend | 0.1% FPR | malware TPR, fit subset | +14.66 | 12.79 | [+13.54, +15.93] | 10/0 | **yes** | [+6.79, +25.35] | yes |
| PE+bal − v2-PE | copy 50 insert | 1% FPR | malware TPR | +11.99 | 8.72 | [+11.51, +12.46] | 10/0 | **yes** | [+5.31, +18.73] | yes |
| PE+bal − v2-PE | copy 50 insert | 1% FPR | padded-benign FPR | +0.78 | 1.73 | [+0.61, +0.94] | 7/3 | **yes** | [+0.30, +1.39] | yes |
| PE+bal − v2-PE | copy 50 insert | 1% FPR | malware TPR, fit subset | +0.26 | 3.56 | [-0.64, +1.10] | 4/6 | no | [-3.40, +4.23] | no |
| PE+bal − v2-PE | copy 50 insert | 0.1% FPR | malware TPR | +24.24 | 11.62 | [+23.58, +24.89] | 10/0 | **yes** | [+14.36, +32.80] | yes |
| PE+bal − v2-PE | copy 50 insert | 0.1% FPR | padded-benign FPR | +0.27 | 0.28 | [+0.20, +0.34] | 9/1 | **yes** | [+0.16, +0.40] | yes |
| PE+bal − v2-PE | copy 50 insert | 0.1% FPR | malware TPR, fit subset | +6.22 | 8.99 | [+5.37, +7.14] | 8/2 | **yes** | [+2.96, +11.16] | yes |
| PE+bal − v2-PE | copy 50 prepend | 1% FPR | malware TPR | +23.27 | 10.84 | [+22.63, +23.91] | 10/0 | **yes** | [+13.92, +33.35] | yes |
| PE+bal − v2-PE | copy 50 prepend | 1% FPR | padded-benign FPR | +0.29 | 2.34 | [+0.05, +0.52] | 5/5 | no | [-1.00, +2.02] | no |
| PE+bal − v2-PE | copy 50 prepend | 1% FPR | malware TPR, fit subset | +0.54 | 3.72 | [-0.31, +1.35] | 4/5 | no | [-3.21, +4.72] | no |
| PE+bal − v2-PE | copy 50 prepend | 0.1% FPR | malware TPR | +37.43 | 9.73 | [+36.64, +38.24] | 10/0 | **yes** | [+24.51, +48.22] | yes |
| PE+bal − v2-PE | copy 50 prepend | 0.1% FPR | padded-benign FPR | +0.78 | 1.57 | [+0.69, +0.89] | 8/2 | **yes** | [+0.33, +1.37] | yes |
| PE+bal − v2-PE | copy 50 prepend | 0.1% FPR | malware TPR, fit subset | +6.45 | 8.40 | [+5.49, +7.31] | 8/2 | **yes** | [+2.84, +11.87] | yes |
| PE+bal − v2-PE | rot 25 | 1% FPR | malware TPR | +11.32 | 11.19 | [+10.76, +11.83] | 9/1 | **yes** | [+3.12, +19.89] | yes |
| PE+bal − v2-PE | rot 25 | 1% FPR | padded-benign FPR | +8.18 | 9.48 | [+7.82, +8.58] | 8/2 | **yes** | [+2.78, +13.78] | yes |
| PE+bal − v2-PE | rot 25 | 1% FPR | malware TPR, fit subset | +14.93 | 11.60 | [+13.68, +16.25] | 9/1 | **yes** | [-3.58, +33.51] | no |
| PE+bal − v2-PE | rot 25 | 0.1% FPR | malware TPR | +14.14 | 9.94 | [+13.52, +14.76] | 9/1 | **yes** | [+4.96, +24.39] | yes |
| PE+bal − v2-PE | rot 25 | 0.1% FPR | padded-benign FPR | -0.02 | 0.14 | [-0.07, +0.02] | 5/5 | no | [-0.09, +0.03] | no |
| PE+bal − v2-PE | rot 25 | 0.1% FPR | malware TPR, fit subset | +21.56 | 17.40 | [+20.33, +22.82] | 9/1 | **yes** | [+2.75, +40.02] | yes |
| PE+bal − v2-PE | rot 50 | 1% FPR | malware TPR | +8.44 | 12.24 | [+7.86, +9.00] | 8/2 | **yes** | [-2.23, +16.67] | no |
| PE+bal − v2-PE | rot 50 | 1% FPR | padded-benign FPR | +9.38 | 6.99 | [+8.91, +9.89] | 9/1 | **yes** | [+1.61, +18.51] | yes |
| PE+bal − v2-PE | rot 50 | 1% FPR | malware TPR, fit subset | +8.62 | 9.43 | [+7.64, +9.74] | 8/2 | **yes** | [-4.25, +21.70] | no |
| PE+bal − v2-PE | rot 50 | 0.1% FPR | malware TPR | +13.81 | 8.09 | [+13.27, +14.40] | 10/0 | **yes** | [+6.49, +21.37] | yes |
| PE+bal − v2-PE | rot 50 | 0.1% FPR | padded-benign FPR | +0.04 | 0.15 | [-0.02, +0.11] | 6/3 | no | [-0.05, +0.12] | no |
| PE+bal − v2-PE | rot 50 | 0.1% FPR | malware TPR, fit subset | +13.17 | 10.56 | [+12.27, +14.09] | 10/0 | **yes** | [+1.10, +24.18] | yes |
| PE+bal − v2-PE | inj 5 | 1% FPR | malware TPR | +6.55 | 5.08 | [+6.14, +6.97] | 10/0 | **yes** | [+2.60, +10.21] | yes |
| PE+bal − v2-PE | inj 5 | 1% FPR | padded-benign FPR | +0.63 | 1.08 | [+0.50, +0.76] | 9/1 | **yes** | [+0.29, +1.07] | yes |
| PE+bal − v2-PE | inj 5 | 0.1% FPR | malware TPR | +17.67 | 11.91 | [+17.15, +18.18] | 10/0 | **yes** | [+10.26, +23.92] | yes |
| PE+bal − v2-PE | inj 5 | 0.1% FPR | padded-benign FPR | +0.05 | 0.04 | [+0.01, +0.09] | 9/1 | **yes** | [+0.01, +0.10] | yes |
| PE+bal − v2-PE | inj 20 | 1% FPR | malware TPR | +19.20 | 8.25 | [+18.61, +19.80] | 10/0 | **yes** | [+10.92, +27.43] | yes |
| PE+bal − v2-PE | inj 20 | 1% FPR | padded-benign FPR | +0.53 | 0.71 | [+0.40, +0.66] | 8/2 | **yes** | [+0.20, +0.91] | yes |
| PE+bal − v2-PE | inj 20 | 0.1% FPR | malware TPR | +27.79 | 10.08 | [+27.09, +28.46] | 10/0 | **yes** | [+19.25, +35.88] | yes |
| PE+bal − v2-PE | inj 20 | 0.1% FPR | padded-benign FPR | +0.05 | 0.05 | [+0.02, +0.10] | 8/1 | **yes** | [+0.01, +0.11] | yes |
| PE+bal − v2-PE | inj 50 | 1% FPR | malware TPR | +28.15 | 5.09 | [+27.43, +28.81] | 10/0 | **yes** | [+16.98, +39.57] | yes |
| PE+bal − v2-PE | inj 50 | 1% FPR | padded-benign FPR | +0.59 | 0.56 | [+0.46, +0.73] | 9/1 | **yes** | [+0.25, +0.97] | yes |
| PE+bal − v2-PE | inj 50 | 0.1% FPR | malware TPR | +32.97 | 7.92 | [+32.25, +33.66] | 10/0 | **yes** | [+22.60, +41.82] | yes |
| PE+bal − v2-PE | inj 50 | 0.1% FPR | padded-benign FPR | +0.05 | 0.04 | [+0.02, +0.09] | 9/0 | **yes** | [+0.01, +0.10] | yes |

**Further edits, v2-PE + test-time deduplication − v2-PE (10 paired seeds): A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; meets rule = CI excludes 0 and ≥ 7 of 10 seeds with the same sign (descriptive: none of these robustness comparisons is a pre-registered claim).**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | meets rule (descriptive) | CI (cluster bootstrap) | meets rule, cluster (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| v2-PE + test-time deduplication − v2-PE | rare 5 insert | 1% FPR | malware TPR | -0.24 | 0.57 | [-0.31, -0.18] | 5/5 | no | [-0.36, -0.09] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 insert | 1% FPR | padded-benign FPR | -0.04 | 0.06 | [-0.06, -0.02] | 1/8 | **yes** | [-0.07, -0.02] | yes |
| v2-PE + test-time deduplication − v2-PE | rare 5 insert | 1% FPR | malware TPR, fit subset | -0.51 | 0.87 | [-0.62, -0.41] | 4/6 | no | [-0.64, -0.35] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 insert | 0.1% FPR | malware TPR | +0.18 | 0.54 | [+0.11, +0.24] | 6/4 | no | [+0.05, +0.31] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.00 | [-0.00, +0.00] | 0/1 | no | [-0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 insert | 0.1% FPR | malware TPR, fit subset | +0.14 | 0.44 | [+0.07, +0.21] | 5/2 | no | [+0.03, +0.25] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 prepend | 1% FPR | malware TPR | -0.38 | 0.95 | [-0.46, -0.30] | 5/5 | no | [-0.48, -0.24] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 prepend | 1% FPR | padded-benign FPR | -0.12 | 0.31 | [-0.15, -0.09] | 4/6 | no | [-0.15, -0.08] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 prepend | 1% FPR | malware TPR, fit subset | -0.44 | 0.98 | [-0.58, -0.30] | 5/4 | no | [-0.62, -0.28] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 prepend | 0.1% FPR | malware TPR | +0.10 | 0.22 | [+0.05, +0.16] | 9/1 | **yes** | [-0.06, +0.26] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | rare 5 prepend | 0.1% FPR | malware TPR, fit subset | +0.04 | 0.06 | [-0.01, +0.10] | 7/2 | no | [-0.03, +0.12] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 insert | 1% FPR | malware TPR | -0.37 | 0.74 | [-0.44, -0.31] | 5/5 | no | [-0.47, -0.27] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 insert | 1% FPR | padded-benign FPR | -0.07 | 0.16 | [-0.09, -0.05] | 1/7 | **yes** | [-0.09, -0.05] | yes |
| v2-PE + test-time deduplication − v2-PE | rare 20 insert | 1% FPR | malware TPR, fit subset | -0.35 | 0.54 | [-0.46, -0.25] | 1/8 | **yes** | [-0.54, -0.22] | yes |
| v2-PE + test-time deduplication − v2-PE | rare 20 insert | 0.1% FPR | malware TPR | +0.11 | 0.34 | [+0.05, +0.16] | 5/4 | no | [+0.04, +0.19] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 insert | 0.1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [-0.03, +0.04] | 1/0 | no | [-0.03, +0.05] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 prepend | 1% FPR | malware TPR | -0.25 | 0.65 | [-0.30, -0.20] | 5/5 | no | [-0.37, -0.14] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 prepend | 1% FPR | padded-benign FPR | -0.09 | 0.27 | [-0.12, -0.07] | 1/5 | no | [-0.13, -0.07] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 prepend | 1% FPR | malware TPR, fit subset | -0.25 | 0.75 | [-0.37, -0.12] | 3/4 | no | [-0.45, -0.13] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 prepend | 0.1% FPR | malware TPR | +0.03 | 0.08 | [+0.02, +0.05] | 5/4 | no | [+0.01, +0.06] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.00 | [-0.00, +0.00] | 0/1 | no | [-0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | rare 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | rare 50 insert | 1% FPR | malware TPR | -0.41 | 0.81 | [-0.47, -0.35] | 3/7 | **yes** | [-0.51, -0.29] | yes |
| v2-PE + test-time deduplication − v2-PE | rare 50 insert | 1% FPR | padded-benign FPR | -0.08 | 0.23 | [-0.11, -0.06] | 2/4 | no | [-0.11, -0.06] | no |
| v2-PE + test-time deduplication − v2-PE | rare 50 insert | 0.1% FPR | malware TPR | +0.08 | 0.25 | [+0.05, +0.12] | 6/3 | no | [+0.04, +0.15] | no |
| v2-PE + test-time deduplication − v2-PE | rare 50 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | rare 50 prepend | 1% FPR | malware TPR | -0.15 | 0.40 | [-0.19, -0.12] | 3/7 | **yes** | [-0.19, -0.11] | yes |
| v2-PE + test-time deduplication − v2-PE | rare 50 prepend | 1% FPR | padded-benign FPR | -0.18 | 0.52 | [-0.21, -0.14] | 2/4 | no | [-0.21, -0.15] | no |
| v2-PE + test-time deduplication − v2-PE | rare 50 prepend | 0.1% FPR | malware TPR | +0.01 | 0.02 | [-0.01, +0.02] | 3/2 | no | [-0.00, +0.02] | no |
| v2-PE + test-time deduplication − v2-PE | rare 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [-0.00, +0.00] | 0/0 | no | [-0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 insert | 1% FPR | malware TPR | -0.14 | 0.44 | [-0.20, -0.07] | 5/5 | no | [-0.23, -0.02] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 insert | 1% FPR | padded-benign FPR | -0.02 | 0.07 | [-0.04, +0.01] | 3/4 | no | [-0.04, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 insert | 1% FPR | malware TPR, fit subset | -0.25 | 0.51 | [-0.35, -0.15] | 4/5 | no | [-0.46, -0.13] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 insert | 0.1% FPR | malware TPR | +0.16 | 0.79 | [+0.09, +0.23] | 5/4 | no | [-0.15, +0.45] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.01 | [-0.00, +0.00] | 1/1 | no | [-0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 insert | 0.1% FPR | malware TPR, fit subset | +0.33 | 0.57 | [+0.20, +0.46] | 10/0 | **yes** | [+0.16, +0.54] | yes |
| v2-PE + test-time deduplication − v2-PE | block 5 prepend | 1% FPR | malware TPR | -0.18 | 0.65 | [-0.27, -0.08] | 4/6 | no | [-0.37, +0.06] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 prepend | 1% FPR | padded-benign FPR | -0.05 | 0.09 | [-0.08, -0.03] | 2/8 | **yes** | [-0.09, -0.03] | yes |
| v2-PE + test-time deduplication − v2-PE | block 5 prepend | 1% FPR | malware TPR, fit subset | -0.37 | 0.75 | [-0.52, -0.21] | 4/5 | no | [-0.61, -0.15] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 prepend | 0.1% FPR | malware TPR | +0.28 | 0.48 | [+0.21, +0.36] | 9/1 | **yes** | [+0.14, +0.43] | yes |
| v2-PE + test-time deduplication − v2-PE | block 5 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [-0.00, +0.00] | 1/0 | no | [-0.00, +0.01] | no |
| v2-PE + test-time deduplication − v2-PE | block 5 prepend | 0.1% FPR | malware TPR, fit subset | +0.27 | 0.39 | [+0.15, +0.40] | 9/0 | **yes** | [+0.05, +0.45] | yes |
| v2-PE + test-time deduplication − v2-PE | block 20 insert | 1% FPR | malware TPR | -0.23 | 0.48 | [-0.30, -0.16] | 5/5 | no | [-0.34, -0.12] | no |
| v2-PE + test-time deduplication − v2-PE | block 20 insert | 1% FPR | padded-benign FPR | -0.03 | 0.10 | [-0.05, -0.00] | 4/5 | no | [-0.05, -0.01] | no |
| v2-PE + test-time deduplication − v2-PE | block 20 insert | 1% FPR | malware TPR, fit subset | -0.43 | 0.73 | [-0.59, -0.30] | 3/7 | **yes** | [-0.69, -0.22] | yes |
| v2-PE + test-time deduplication − v2-PE | block 20 insert | 0.1% FPR | malware TPR | +0.11 | 0.74 | [+0.05, +0.18] | 4/6 | no | [-0.19, +0.39] | no |
| v2-PE + test-time deduplication − v2-PE | block 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | block 20 insert | 0.1% FPR | malware TPR, fit subset | +0.22 | 0.64 | [+0.12, +0.32] | 6/4 | no | [+0.05, +0.38] | no |
| v2-PE + test-time deduplication − v2-PE | block 20 prepend | 1% FPR | malware TPR | -0.34 | 0.82 | [-0.42, -0.26] | 5/5 | no | [-0.51, -0.18] | no |
| v2-PE + test-time deduplication − v2-PE | block 20 prepend | 1% FPR | padded-benign FPR | -0.23 | 0.58 | [-0.26, -0.19] | 2/7 | **yes** | [-0.27, -0.19] | yes |
| v2-PE + test-time deduplication − v2-PE | block 20 prepend | 1% FPR | malware TPR, fit subset | -0.28 | 0.79 | [-0.43, -0.13] | 4/6 | no | [-0.47, -0.08] | no |
| v2-PE + test-time deduplication − v2-PE | block 20 prepend | 0.1% FPR | malware TPR | +0.11 | 0.23 | [+0.06, +0.17] | 7/2 | **yes** | [+0.04, +0.21] | yes |
| v2-PE + test-time deduplication − v2-PE | block 20 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.02 | [-0.01, +0.00] | 2/2 | no | [-0.01, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | block 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.03 | 0.13 | [-0.05, +0.11] | 4/5 | no | [-0.04, +0.13] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 insert | 1% FPR | malware TPR | -0.21 | 0.40 | [-0.26, -0.15] | 2/7 | **yes** | [-0.29, -0.13] | yes |
| v2-PE + test-time deduplication − v2-PE | block 50 insert | 1% FPR | padded-benign FPR | -0.04 | 0.09 | [-0.07, -0.02] | 3/6 | no | [-0.07, -0.02] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 insert | 1% FPR | malware TPR, fit subset | -0.39 | 0.66 | [-0.54, -0.24] | 2/7 | **yes** | [-0.58, -0.23] | yes |
| v2-PE + test-time deduplication − v2-PE | block 50 insert | 0.1% FPR | malware TPR | +0.14 | 0.86 | [+0.07, +0.21] | 3/7 | **yes** | [-0.21, +0.43] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.00 | [-0.00, +0.00] | 0/1 | no | [-0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 insert | 0.1% FPR | malware TPR, fit subset | +0.15 | 0.42 | [+0.01, +0.28] | 6/2 | no | [-0.05, +0.27] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 prepend | 1% FPR | malware TPR | -0.14 | 0.65 | [-0.21, -0.06] | 5/5 | no | [-0.23, -0.06] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 prepend | 1% FPR | padded-benign FPR | -0.21 | 0.54 | [-0.26, -0.17] | 4/5 | no | [-0.26, -0.17] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 prepend | 1% FPR | malware TPR, fit subset | -0.31 | 0.77 | [-0.47, -0.15] | 4/6 | no | [-0.49, -0.11] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 prepend | 0.1% FPR | malware TPR | +0.11 | 0.16 | [+0.06, +0.14] | 8/2 | **yes** | [+0.07, +0.15] | yes |
| v2-PE + test-time deduplication − v2-PE | block 50 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.04 | [+0.00, +0.02] | 3/2 | no | [+0.00, +0.02] | no |
| v2-PE + test-time deduplication − v2-PE | block 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.06 | 0.16 | [+0.01, +0.13] | 5/5 | no | [-0.01, +0.15] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 insert | 1% FPR | malware TPR | +0.12 | 0.39 | [+0.04, +0.22] | 6/4 | no | [-0.09, +0.45] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 insert | 1% FPR | padded-benign FPR | +0.03 | 0.06 | [-0.00, +0.07] | 7/3 | no | [-0.01, +0.07] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 insert | 1% FPR | malware TPR, fit subset | +0.23 | 0.76 | [+0.01, +0.46] | 7/3 | **yes** | [-0.29, +1.11] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 insert | 0.1% FPR | malware TPR | +0.13 | 0.99 | [-0.04, +0.27] | 6/3 | no | [-0.87, +0.94] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [-0.02, +0.02] | 4/0 | no | [-0.02, +0.03] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 insert | 0.1% FPR | malware TPR, fit subset | -1.21 | 2.43 | [-1.66, -0.81] | 3/7 | **yes** | [-3.47, +0.88] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 prepend | 1% FPR | malware TPR | -0.05 | 1.02 | [-0.16, +0.06] | 5/5 | no | [-0.41, +0.35] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 prepend | 1% FPR | padded-benign FPR | -0.04 | 0.10 | [-0.08, -0.00] | 4/6 | no | [-0.10, +0.01] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 prepend | 1% FPR | malware TPR, fit subset | +0.31 | 0.92 | [+0.06, +0.56] | 3/7 | **yes** | [-0.32, +1.06] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 prepend | 0.1% FPR | malware TPR | -0.34 | 0.96 | [-0.49, -0.20] | 3/7 | **yes** | [-1.22, +0.33] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.03, +0.01] | 2/6 | no | [-0.03, +0.02] | no |
| v2-PE + test-time deduplication − v2-PE | copy 5 prepend | 0.1% FPR | malware TPR, fit subset | -1.31 | 1.94 | [-1.72, -0.93] | 2/7 | **yes** | [-3.57, +0.72] | no |
| v2-PE + test-time deduplication − v2-PE | copy 20 insert | 1% FPR | malware TPR | -0.14 | 0.71 | [-0.25, -0.03] | 4/6 | no | [-0.43, +0.15] | no |
| v2-PE + test-time deduplication − v2-PE | copy 20 insert | 1% FPR | padded-benign FPR | -0.07 | 0.11 | [-0.12, -0.02] | 3/7 | **yes** | [-0.15, -0.01] | yes |
| v2-PE + test-time deduplication − v2-PE | copy 20 insert | 1% FPR | malware TPR, fit subset | -0.40 | 1.48 | [-0.67, -0.11] | 3/7 | **yes** | [-0.92, -0.02] | yes |
| v2-PE + test-time deduplication − v2-PE | copy 20 insert | 0.1% FPR | malware TPR | +0.51 | 1.11 | [+0.37, +0.64] | 5/5 | no | [+0.10, +0.96] | no |
| v2-PE + test-time deduplication − v2-PE | copy 20 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.03 | [-0.02, +0.01] | 3/4 | no | [-0.02, +0.01] | no |
| v2-PE + test-time deduplication − v2-PE | copy 20 insert | 0.1% FPR | malware TPR, fit subset | +0.59 | 3.90 | [+0.22, +0.93] | 4/6 | no | [-1.03, +1.86] | no |
| v2-PE + test-time deduplication − v2-PE | copy 20 prepend | 1% FPR | malware TPR | -0.51 | 0.75 | [-0.64, -0.38] | 3/7 | **yes** | [-0.95, -0.12] | yes |
| v2-PE + test-time deduplication − v2-PE | copy 20 prepend | 1% FPR | padded-benign FPR | -0.24 | 0.38 | [-0.31, -0.18] | 1/9 | **yes** | [-0.35, -0.16] | yes |
| v2-PE + test-time deduplication − v2-PE | copy 20 prepend | 1% FPR | malware TPR, fit subset | -0.11 | 1.30 | [-0.39, +0.20] | 3/6 | no | [-0.60, +0.31] | no |
| v2-PE + test-time deduplication − v2-PE | copy 20 prepend | 0.1% FPR | malware TPR | -0.06 | 1.41 | [-0.21, +0.08] | 4/6 | no | [-0.73, +0.49] | no |
| v2-PE + test-time deduplication − v2-PE | copy 20 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.05 | [-0.02, +0.01] | 4/5 | no | [-0.03, +0.02] | no |
| v2-PE + test-time deduplication − v2-PE | copy 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.49 | 2.21 | [+0.11, +0.88] | 4/6 | no | [-0.68, +1.56] | no |
| v2-PE + test-time deduplication − v2-PE | copy 50 insert | 1% FPR | malware TPR | -0.12 | 0.80 | [-0.24, -0.01] | 4/6 | no | [-0.29, +0.07] | no |
| v2-PE + test-time deduplication − v2-PE | copy 50 insert | 1% FPR | padded-benign FPR | -0.08 | 0.18 | [-0.13, -0.04] | 3/7 | **yes** | [-0.14, -0.04] | yes |
| v2-PE + test-time deduplication − v2-PE | copy 50 insert | 1% FPR | malware TPR, fit subset | +0.21 | 1.74 | [-0.10, +0.51] | 5/5 | no | [-0.32, +0.99] | no |
| v2-PE + test-time deduplication − v2-PE | copy 50 insert | 0.1% FPR | malware TPR | +0.32 | 0.64 | [+0.21, +0.46] | 8/2 | **yes** | [+0.10, +0.55] | yes |
| v2-PE + test-time deduplication − v2-PE | copy 50 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.04 | [-0.03, +0.01] | 5/4 | no | [-0.03, +0.01] | no |
| v2-PE + test-time deduplication − v2-PE | copy 50 insert | 0.1% FPR | malware TPR, fit subset | +0.42 | 1.53 | [+0.06, +0.84] | 5/5 | no | [-0.45, +0.99] | no |
| v2-PE + test-time deduplication − v2-PE | copy 50 prepend | 1% FPR | malware TPR | +0.01 | 1.07 | [-0.15, +0.16] | 5/5 | no | [-0.33, +0.45] | no |
| v2-PE + test-time deduplication − v2-PE | copy 50 prepend | 1% FPR | padded-benign FPR | -0.24 | 0.37 | [-0.31, -0.17] | 0/9 | **yes** | [-0.35, -0.15] | yes |
| v2-PE + test-time deduplication − v2-PE | copy 50 prepend | 1% FPR | malware TPR, fit subset | +0.17 | 1.66 | [-0.15, +0.52] | 4/4 | no | [-0.51, +1.13] | no |
| v2-PE + test-time deduplication − v2-PE | copy 50 prepend | 0.1% FPR | malware TPR | +0.62 | 0.85 | [+0.49, +0.77] | 7/3 | **yes** | [+0.23, +1.18] | yes |
| v2-PE + test-time deduplication − v2-PE | copy 50 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.05 | [-0.04, +0.02] | 3/5 | no | [-0.05, +0.02] | no |
| v2-PE + test-time deduplication − v2-PE | copy 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.39 | 1.15 | [-0.01, +0.80] | 6/4 | no | [-0.28, +0.88] | no |
| v2-PE + test-time deduplication − v2-PE | rot 25 | 1% FPR | malware TPR | -0.31 | 0.72 | [-0.38, -0.23] | 4/6 | no | [-0.61, -0.00] | no |
| v2-PE + test-time deduplication − v2-PE | rot 25 | 1% FPR | padded-benign FPR | -0.19 | 0.47 | [-0.24, -0.15] | 4/5 | no | [-0.28, -0.13] | no |
| v2-PE + test-time deduplication − v2-PE | rot 25 | 1% FPR | malware TPR, fit subset | -0.07 | 0.32 | [-0.16, +0.01] | 5/5 | no | [-0.28, +0.08] | no |
| v2-PE + test-time deduplication − v2-PE | rot 25 | 0.1% FPR | malware TPR | +0.21 | 0.73 | [+0.14, +0.28] | 7/3 | **yes** | [-0.23, +0.67] | no |
| v2-PE + test-time deduplication − v2-PE | rot 25 | 0.1% FPR | padded-benign FPR | -0.00 | 0.01 | [-0.00, +0.00] | 1/1 | no | [-0.00, +0.00] | no |
| v2-PE + test-time deduplication − v2-PE | rot 25 | 0.1% FPR | malware TPR, fit subset | +0.14 | 0.28 | [+0.06, +0.22] | 7/3 | **yes** | [-0.04, +0.42] | no |
| v2-PE + test-time deduplication − v2-PE | rot 50 | 1% FPR | malware TPR | -0.45 | 3.02 | [-0.51, -0.39] | 4/6 | no | [-0.80, -0.14] | no |
| v2-PE + test-time deduplication − v2-PE | rot 50 | 1% FPR | padded-benign FPR | -0.21 | 0.48 | [-0.25, -0.17] | 3/6 | no | [-0.30, -0.13] | no |
| v2-PE + test-time deduplication − v2-PE | rot 50 | 1% FPR | malware TPR, fit subset | -0.18 | 0.42 | [-0.27, -0.09] | 3/6 | no | [-0.41, +0.05] | no |
| v2-PE + test-time deduplication − v2-PE | rot 50 | 0.1% FPR | malware TPR | +0.20 | 0.81 | [+0.14, +0.26] | 5/5 | no | [-0.23, +0.63] | no |
| v2-PE + test-time deduplication − v2-PE | rot 50 | 0.1% FPR | padded-benign FPR | +0.00 | 0.02 | [-0.01, +0.01] | 5/3 | no | [-0.01, +0.01] | no |
| v2-PE + test-time deduplication − v2-PE | rot 50 | 0.1% FPR | malware TPR, fit subset | +0.22 | 0.35 | [+0.12, +0.32] | 7/3 | **yes** | [-0.01, +0.78] | no |
| v2-PE + test-time deduplication − v2-PE | inj 5 | 1% FPR | malware TPR | -0.16 | 0.60 | [-0.22, -0.09] | 6/4 | no | [-0.33, +0.03] | no |
| v2-PE + test-time deduplication − v2-PE | inj 5 | 1% FPR | padded-benign FPR | -0.03 | 0.06 | [-0.04, -0.01] | 4/5 | no | [-0.04, -0.01] | no |
| v2-PE + test-time deduplication − v2-PE | inj 5 | 0.1% FPR | malware TPR | +0.24 | 0.75 | [+0.17, +0.31] | 6/4 | no | [+0.04, +0.43] | no |
| v2-PE + test-time deduplication − v2-PE | inj 5 | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |
| v2-PE + test-time deduplication − v2-PE | inj 20 | 1% FPR | malware TPR | -0.37 | 0.62 | [-0.43, -0.31] | 3/6 | no | [-0.53, -0.23] | no |
| v2-PE + test-time deduplication − v2-PE | inj 20 | 1% FPR | padded-benign FPR | -0.04 | 0.07 | [-0.06, -0.02] | 2/5 | no | [-0.06, -0.02] | no |
| v2-PE + test-time deduplication − v2-PE | inj 20 | 0.1% FPR | malware TPR | +0.11 | 0.56 | [+0.06, +0.17] | 6/4 | no | [-0.12, +0.29] | no |
| v2-PE + test-time deduplication − v2-PE | inj 20 | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 2/0 | no | [+0.00, +0.01] | no |
| v2-PE + test-time deduplication − v2-PE | inj 50 | 1% FPR | malware TPR | -0.51 | 0.95 | [-0.56, -0.45] | 2/8 | **yes** | [-0.71, -0.35] | yes |
| v2-PE + test-time deduplication − v2-PE | inj 50 | 1% FPR | padded-benign FPR | -0.04 | 0.09 | [-0.05, -0.02] | 2/5 | no | [-0.06, -0.02] | no |
| v2-PE + test-time deduplication − v2-PE | inj 50 | 0.1% FPR | malware TPR | +0.17 | 0.46 | [+0.14, +0.20] | 7/2 | **yes** | [+0.08, +0.26] | yes |
| v2-PE + test-time deduplication − v2-PE | inj 50 | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 2/0 | no | [+0.00, +0.01] | no |
