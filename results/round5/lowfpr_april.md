# Low-FPR measurements (round 5, item 2)

## Benign reports above the thresholds (April)

The 0.1% threshold of April is the (floor(0.001 x 8,003) + 1) = 9th highest benign score: only 8 benign reports may lie above it, which is why TPR at 0.1% FPR is unstable (ties can add reports above the threshold).

| model | benign reports in April | allowed above 0.1% threshold (floor) | benign above the 0.1% threshold (mean over seeds) | allowed above 1% threshold | benign above the 1% threshold |
|---|---|---|---|---|---|
| ATT+bal | 8003 | 8 | 8.0 | 80 | 79.4 |
| MM+bal | 8003 | 8 | 8.0 | 80 | 80.0 |
| C+bal | 8003 | 8 | 8.0 | 80 | 78.4 |
| C (J, 2 epochs) | 8003 | 8 | 6.7 | 80 | 79.9 |
| C (J) | 8003 | 8 | 6.8 | 80 | 79.9 |
| A (J) | 8003 | 8 | 8.0 | 80 | 80.0 |
| released Nebula | 8003 | 8 | 8.0 | 80 | 80.0 |


## TPR when 4 / 8 / 12 benign reports may lie above the threshold (April)

| model | TPR with 4 benign above the threshold (0.050% FPR) | TPR with 8 benign above the threshold (0.100% FPR) | TPR with 12 benign above the threshold (0.150% FPR) |
|---|---|---|---|
| ATT+bal | 43.8% | 57.0% | 63.5% |
| MM+bal | 23.9% | 38.0% | 46.0% |
| C+bal | 10.2% | 27.3% | 39.5% |
| C (J, 2 epochs) | 9.1% | 15.2% | 20.2% |
| C (J) | 12.4% | 20.4% | 27.1% |
| A (J) | 33.3% | 39.6% | 44.2% |
| released Nebula | 41.5% | 51.8% | 55.8% |


## Standardised partial AUC up to 1% FPR (McClish; 0.5 = chance, 1 = perfect), April

Mean over seeds [95% group-bootstrap interval, 300 resamples].

| model | standardised partial AUC to 1% FPR |
|---|---|
| ATT+bal | 0.8384 [0.7745, 0.8865] |
| MM+bal | 0.8092 [0.7373, 0.8709] |
| C+bal | 0.8026 [0.7392, 0.8590] |
| C (J, 2 epochs) | 0.7371 [0.6492, 0.8244] |
| C (J) | 0.7607 [0.6820, 0.8342] |
| A (J) | 0.7942 [0.7369, 0.8488] |
| released Nebula | 0.8286 [0.7732, 0.8794] |
