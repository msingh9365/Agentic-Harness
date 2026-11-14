## Test 4: size of the long-report group

Share of each count that falls in each chunk group (512-token chunks of Nebula's tokenized report; 12 April reports need more than 8 chunks and are counted in 4-8). Misses = malware at or below the 1% FPR threshold: (a) from April benign scores, (b) from January validation. 95% intervals from the group bootstrap.

| population | count | n | 1 chunk | 2-3 chunks | 4-8 chunks |
|---|---|---|---|---|---|
| all April | April reports | 17,402 | 36.5% [27.8, 47.4] | 34.9% [23.6, 46.9] | 28.5% [19.3, 38.0] |
| all April | April malware | 9,399 | 30.4% [18.0, 45.4] | 39.1% [23.9, 54.7] | 30.5% [17.2, 45.2] |
| all April | released Nebula misses (a) | 2,352 | 46.8% [30.2, 63.9] | 32.4% [18.8, 46.1] | 20.9% [9.5, 34.5] |
| all April | released Nebula misses (b) | 2,195 | 46.6% [30.1, 63.5] | 31.7% [18.7, 45.5] | 21.7% [9.7, 36.1] |
| all April | two-level K=8 misses (a) | 2,381 | 25.7% [14.9, 39.2] | 50.4% [32.1, 66.5] | 23.9% [11.7, 38.7] |
| all April | two-level K=8 misses (b) | 1,451 | 33.6% [19.8, 49.4] | 39.1% [23.6, 55.4] | 27.3% [11.8, 44.7] |
| seen | April reports | 6,329 | 43.1% [30.0, 58.8] | 29.5% [12.5, 47.8] | 27.3% [17.2, 39.3] |
| seen | April malware | 2,914 | 29.0% [19.0, 43.0] | 25.8% [11.0, 40.9] | 45.2% [28.5, 61.0] |
| seen | released Nebula misses (a) | 521 | 77.7% [56.5, 89.5] | 10.4% [2.4, 26.0] | 11.9% [5.2, 24.4] |
| seen | released Nebula misses (b) | 500 | 79.2% [59.5, 90.7] | 9.0% [1.8, 23.1] | 11.8% [4.8, 24.3] |
| seen | two-level K=8 misses (a) | 363 | 64.7% [39.8, 86.5] | 11.0% [2.6, 30.7] | 24.2% [6.8, 46.1] |
| seen | two-level K=8 misses (b) | 233 | 88.4% [71.1, 95.0] | 3.9% [0.9, 10.8] | 7.7% [2.8, 20.8] |
| unseen | April reports | 11,073 | 32.8% [20.7, 46.0] | 38.0% [24.7, 52.3] | 29.2% [16.3, 42.2] |
| unseen | April malware | 6,485 | 31.0% [12.9, 53.1] | 45.1% [24.3, 66.5] | 23.9% [7.6, 43.0] |
| unseen | released Nebula misses (a) | 1,831 | 38.0% [17.8, 60.4] | 38.6% [21.6, 57.3] | 23.4% [9.4, 39.9] |
| unseen | released Nebula misses (b) | 1,695 | 37.0% [16.7, 59.4] | 38.4% [21.6, 57.5] | 24.6% [9.7, 43.0] |
| unseen | two-level K=8 misses (a) | 2,018 | 18.7% [8.8, 32.0] | 57.5% [37.5, 73.4] | 23.8% [10.3, 40.9] |
| unseen | two-level K=8 misses (b) | 1,218 | 23.1% [10.9, 38.8] | 45.9% [27.4, 64.7] | 31.0% [12.3, 51.3] |

**Decision.** Reports that need 4-8 chunks are 28.5% of April and hold 20.9% of released Nebula's misses at 1% FPR; reports beyond the first chunk (2-8 chunks) hold 53.2%, so that is the most a model that reads more chunks could fix.
