# White-box greedy padding (round 5, item 3d)

500 random April malware reports (fixed draw). For each model (one trained seed, attacked with its OWN scores) and each report, up to 20 steps; in every step
200 random candidate calls are drawn from the EVAL pool (a fixed random subset of 30,000 calls of the 361,002 calls of the 2,000 EVAL reports), each is tried
at the front of the report (prepended before the first call) and the one that lowers the model's logit most is kept. A report stops being attacked when its
logit is below the 1% FPR threshold of the model (threshold from the unedited April benign scores); it then counts as evaded for all larger k at both
thresholds (an attacker would stop there). Reports are composed from token pieces (r5_compose.py, checked against full tokenisation); edited reports exist
in memory only, aggregate numbers only are written. TPR(k) = share of the 500 reports still above the threshold after k calls.

Models: ATT+bal, C+bal, released Nebula; one seed (0) each, attacked with its own scores; the 500 April malware reports are the same for all models (some are not detected at k = 0).


## TPR of the 500 reports at the threshold of 1% FPR after k prepended calls

| model | k=0 | k=1 | k=2 | k=3 | k=5 | k=10 | k=15 | k=20 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal (seed 0) | 78.2% | 65.0% | 64.4% | 64.2% | 63.2% | 61.4% | 60.2% | 54.0% |
| C+bal (seed 0) | 79.8% | 70.0% | 63.6% | 63.0% | 61.6% | 58.4% | 53.8% | 35.0% |
| released Nebula | 73.0% | 38.2% | 21.0% | 14.2% | 7.4% | 3.4% | 1.6% | 1.6% |


Only the reports whose edited sequence fits in 512 tokens at k (1%)

| model | k=0 | k=1 | k=2 | k=3 | k=5 | k=10 | k=15 | k=20 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal (seed 0) | 69.3% (n=140) | 46.4% (n=140) | 44.3% (n=140) | 43.6% (n=140) | 41.0% (n=139) | 26.1% (n=111) | 13.7% (n=95) | 9.9% (n=91) |
| C+bal (seed 0) | 75.7% (n=140) | 62.1% (n=140) | 44.3% (n=140) | 42.1% (n=140) | 40.0% (n=140) | 19.8% (n=111) | 6.2% (n=97) | 5.2% (n=96) |
| released Nebula | 53.6% (n=140) | 30.7% (n=140) | 5.0% (n=140) | 0.7% (n=140) | 0.0% (n=139) | 0.0% (n=139) | 0.0% (n=139) | 0.0% (n=139) |


## TPR of the 500 reports at the threshold of 0.1% FPR after k prepended calls

| model | k=0 | k=1 | k=2 | k=3 | k=5 | k=10 | k=15 | k=20 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal (seed 0) | 54.8% | 50.6% | 48.2% | 48.4% | 48.8% | 40.2% | 37.4% | 31.8% |
| C+bal (seed 0) | 42.0% | 14.2% | 11.0% | 12.4% | 11.4% | 8.0% | 1.2% | 0.0% |
| released Nebula | 51.2% | 8.2% | 2.4% | 1.0% | 0.8% | 0.6% | 0.6% | 0.6% |


Only the reports whose edited sequence fits in 512 tokens at k (0.1%)

| model | k=0 | k=1 | k=2 | k=3 | k=5 | k=10 | k=15 | k=20 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal (seed 0) | 40.7% (n=140) | 38.6% (n=140) | 34.3% (n=140) | 36.4% (n=140) | 37.4% (n=139) | 16.2% (n=111) | 5.3% (n=95) | 6.6% (n=91) |
| C+bal (seed 0) | 57.9% (n=140) | 12.1% (n=140) | 13.6% (n=140) | 15.7% (n=140) | 12.1% (n=140) | 5.4% (n=111) | 0.0% (n=97) | 0.0% (n=96) |
| released Nebula | 37.9% (n=140) | 2.1% (n=140) | 0.0% (n=140) | 0.0% (n=140) | 0.0% (n=139) | 0.0% (n=139) | 0.0% (n=139) | 0.0% (n=139) |
