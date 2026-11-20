**Random padding with calls of the EVAL pool, all April reports** Thresholds: 1% and 0.1% FPR of each model's and seed's unedited April benign scores. Seeds 0-9, mean ± std.

| model | edit | malware TPR @1% | padded-benign FPR @1% | malware TPR @0.1% | padded-benign FPR @0.1% | malware that fit in 512 | TPR @1%, fit subset | TPR @0.1%, fit subset |
|---|---|---|---|---|---|---|---|---|
| v2-PE | random 5 prepend | 54.4 ± 7.8 | 1.0 ± 0.2 | 20.3 ± 6.2 | 0.0 ± 0.0 | 30.3% | 46.3 | 14.2 |
| v2-PE | random 20 prepend | 22.5 ± 8.2 | 1.2 ± 1.3 | 5.5 ± 2.3 | 0.0 ± 0.0 | 27.5% | 10.0 | 0.7 |
| v2-PE | random 50 prepend | 8.3 ± 3.5 | 1.1 ± 1.8 | 1.5 ± 1.8 | 0.0 ± 0.0 | 17.1% | 2.5 | 0.0 |
| v2-PE | random 100 prepend | 6.6 ± 4.5 | 1.5 ± 2.8 | 1.3 ± 1.8 | 0.0 ± 0.1 | 0.0% | n/a | n/a |
| v2-PE | random 200 prepend | 6.6 ± 4.7 | 1.4 ± 2.7 | 1.4 ± 1.9 | 0.0 ± 0.1 | 0.0% | n/a | n/a |
| v2-PE | random 5 insert | 73.8 ± 2.7 | 0.9 ± 0.2 | 40.0 ± 4.8 | 0.0 ± 0.0 | 30.3% | 65.4 | 31.5 |
| v2-PE | random 20 insert | 55.7 ± 4.5 | 0.7 ± 0.3 | 23.4 ± 4.9 | 0.0 ± 0.0 | 27.6% | 34.1 | 7.2 |
| v2-PE | random 50 insert | 41.4 ± 4.3 | 0.7 ± 0.6 | 13.6 ± 3.4 | 0.0 ± 0.0 | 17.0% | 5.3 | 0.3 |
| v2-PE | random 100 insert | 28.1 ± 3.0 | 0.8 ± 1.3 | 7.9 ± 2.6 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| v2-PE | random 200 insert | 17.1 ± 3.5 | 0.9 ± 1.5 | 4.0 ± 2.6 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal | random 5 prepend | 79.0 ± 2.9 | 1.2 ± 0.1 | 52.1 ± 5.5 | 0.1 ± 0.0 | 30.3% | 74.6 | 50.3 |
| ATT+bal | random 20 prepend | 76.9 ± 2.8 | 1.3 ± 0.3 | 51.8 ± 6.5 | 0.1 ± 0.0 | 27.5% | 73.4 | 41.9 |
| ATT+bal | random 50 prepend | 67.6 ± 5.2 | 1.5 ± 0.8 | 32.2 ± 5.4 | 0.0 ± 0.0 | 17.1% | 54.9 | 9.5 |
| ATT+bal | random 100 prepend | 7.9 ± 1.3 | 1.0 ± 0.6 | 2.2 ± 0.9 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | random 200 prepend | 8.0 ± 1.3 | 0.9 ± 0.6 | 2.2 ± 1.0 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | random 5 insert | 78.5 ± 2.5 | 1.1 ± 0.2 | 52.8 ± 6.5 | 0.1 ± 0.0 | 30.3% | 74.3 | 51.4 |
| ATT+bal | random 20 insert | 75.4 ± 4.0 | 1.1 ± 0.3 | 45.6 ± 4.0 | 0.1 ± 0.0 | 27.6% | 71.5 | 40.0 |
| ATT+bal | random 50 insert | 71.9 ± 4.3 | 1.0 ± 0.4 | 39.7 ± 4.6 | 0.0 ± 0.0 | 17.0% | 51.9 | 10.1 |
| ATT+bal | random 100 insert | 61.7 ± 4.8 | 0.8 ± 0.4 | 33.5 ± 3.6 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal | random 200 insert | 53.0 ± 5.9 | 0.9 ± 0.4 | 25.1 ± 2.2 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | random 5 prepend | 61.8 ± 6.5 | 0.5 ± 0.1 | 25.8 ± 10.9 | 0.0 ± 0.0 | 30.3% | 44.5 | 16.2 |
| B (2L, no padding) | random 20 prepend | 50.6 ± 6.8 | 0.2 ± 0.1 | 18.0 ± 9.4 | 0.0 ± 0.0 | 27.5% | 22.3 | 4.7 |
| B (2L, no padding) | random 50 prepend | 28.2 ± 8.0 | 0.0 ± 0.0 | 2.2 ± 2.5 | 0.0 ± 0.0 | 17.1% | 2.8 | 0.2 |
| B (2L, no padding) | random 100 prepend | 12.5 ± 12.6 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | random 200 prepend | 4.8 ± 7.3 | 0.0 | 0.0 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | random 5 insert | 64.3 ± 5.6 | 0.5 ± 0.2 | 26.3 ± 10.5 | 0.0 ± 0.0 | 30.3% | 50.3 | 17.5 |
| B (2L, no padding) | random 20 insert | 49.1 ± 6.0 | 0.2 ± 0.1 | 15.8 ± 7.9 | 0.0 ± 0.0 | 27.6% | 22.6 | 3.9 |
| B (2L, no padding) | random 50 insert | 33.4 ± 5.7 | 0.0 ± 0.0 | 6.4 ± 3.6 | 0.0 | 17.0% | 1.4 | 0.0 |
| B (2L, no padding) | random 100 insert | 20.0 ± 5.8 | 0.0 ± 0.0 | 2.1 ± 1.5 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | random 200 insert | 8.0 ± 3.1 | 0.0 | 0.3 ± 0.4 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | random 5 prepend | 79.8 ± 1.2 | 1.2 ± 0.1 | 45.4 ± 7.7 | 0.1 ± 0.0 | 30.3% | 76.2 | 48.7 |
| ATT+bal-2L (A) | random 20 prepend | 78.0 ± 1.5 | 1.4 ± 0.2 | 45.2 ± 8.6 | 0.1 ± 0.0 | 27.5% | 75.4 | 44.4 |
| ATT+bal-2L (A) | random 50 prepend | 71.0 ± 1.9 | 1.5 ± 0.6 | 38.8 ± 7.5 | 0.1 ± 0.0 | 17.1% | 60.9 | 22.4 |
| ATT+bal-2L (A) | random 100 prepend | 14.7 ± 10.4 | 0.5 ± 0.2 | 4.3 ± 1.7 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | random 200 prepend | 10.6 ± 2.9 | 0.4 ± 0.3 | 3.0 ± 2.3 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | random 5 insert | 79.5 ± 1.4 | 1.1 ± 0.1 | 46.5 ± 7.4 | 0.1 ± 0.0 | 30.3% | 75.4 | 47.6 |
| ATT+bal-2L (A) | random 20 insert | 77.2 ± 1.5 | 1.1 ± 0.2 | 41.0 ± 7.4 | 0.1 ± 0.0 | 27.6% | 73.5 | 39.2 |
| ATT+bal-2L (A) | random 50 insert | 73.8 ± 1.8 | 1.0 ± 0.3 | 38.0 ± 6.8 | 0.0 ± 0.0 | 17.0% | 56.4 | 15.1 |
| ATT+bal-2L (A) | random 100 insert | 65.7 ± 2.8 | 0.6 ± 0.2 | 29.5 ± 8.2 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | random 200 insert | 56.0 ± 3.3 | 0.5 ± 0.2 | 20.1 ± 7.1 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | random 5 prepend | 78.6 ± 3.4 | 1.1 ± 0.2 | 50.4 ± 7.8 | 0.1 ± 0.0 | 30.3% | 75.3 | 49.9 |
| ATT+bal-2L, round 2 (A2) | random 20 prepend | 76.7 ± 3.1 | 1.3 ± 0.3 | 49.7 ± 8.9 | 0.1 ± 0.0 | 27.5% | 74.3 | 39.9 |
| ATT+bal-2L, round 2 (A2) | random 50 prepend | 67.9 ± 4.7 | 1.1 ± 0.5 | 37.6 ± 6.1 | 0.0 ± 0.0 | 17.1% | 54.1 | 11.8 |
| ATT+bal-2L, round 2 (A2) | random 100 prepend | 9.2 ± 1.8 | 0.3 ± 0.2 | 4.0 ± 1.3 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | random 200 prepend | 7.8 ± 1.2 | 0.3 ± 0.3 | 3.6 ± 1.6 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | random 5 insert | 78.2 ± 3.1 | 1.1 ± 0.1 | 50.1 ± 7.4 | 0.1 ± 0.0 | 30.3% | 74.9 | 49.2 |
| ATT+bal-2L, round 2 (A2) | random 20 insert | 75.0 ± 4.4 | 1.0 ± 0.3 | 43.7 ± 6.7 | 0.1 ± 0.0 | 27.6% | 72.0 | 37.4 |
| ATT+bal-2L, round 2 (A2) | random 50 insert | 71.0 ± 4.6 | 0.8 ± 0.3 | 40.7 ± 6.5 | 0.0 ± 0.0 | 17.0% | 51.4 | 10.5 |
| ATT+bal-2L, round 2 (A2) | random 100 insert | 60.7 ± 4.2 | 0.5 ± 0.2 | 34.5 ± 6.5 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | random 200 insert | 51.2 ± 4.9 | 0.4 ± 0.2 | 26.3 ± 6.0 | 0.0 ± 0.0 | 0.0% | n/a | n/a |

**Random padding with calls of the EVAL pool, all April reports: A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; meets rule = CI excludes 0 and ≥ 7 of 10 seeds with the same sign (descriptive: none of these robustness comparisons is a pre-registered claim).**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | meets rule (descriptive) | CI (cluster bootstrap) | meets rule, cluster (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal-2L (A) − ATT+bal | random 5 prepend | 1% FPR | malware TPR | +0.74 | 2.39 | [+0.56, +0.92] | 5/5 | no | [-0.59, +2.22] | no |
| ATT+bal-2L (A) − ATT+bal | random 5 prepend | 1% FPR | padded-benign FPR | +0.02 | 0.14 | [-0.06, +0.09] | 5/5 | no | [-0.07, +0.10] | no |
| ATT+bal-2L (A) − ATT+bal | random 5 prepend | 1% FPR | malware TPR, fit subset | +1.55 | 3.37 | [+1.22, +1.90] | 7/3 | **yes** | [+0.16, +3.32] | yes |
| ATT+bal-2L (A) − ATT+bal | random 5 prepend | 0.1% FPR | malware TPR | -6.70 | 9.27 | [-7.10, -6.26] | 2/8 | **yes** | [-13.96, -0.89] | yes |
| ATT+bal-2L (A) − ATT+bal | random 5 prepend | 0.1% FPR | padded-benign FPR | -0.02 | 0.04 | [-0.04, +0.01] | 4/6 | no | [-0.06, +0.01] | no |
| ATT+bal-2L (A) − ATT+bal | random 5 prepend | 0.1% FPR | malware TPR, fit subset | -1.60 | 15.02 | [-2.28, -0.87] | 6/4 | no | [-6.95, +2.81] | no |
| ATT+bal-2L (A) − ATT+bal | random 20 prepend | 1% FPR | malware TPR | +1.05 | 1.86 | [+0.87, +1.21] | 6/4 | no | [-0.08, +2.56] | no |
| ATT+bal-2L (A) − ATT+bal | random 20 prepend | 1% FPR | padded-benign FPR | +0.06 | 0.32 | [-0.02, +0.14] | 5/5 | no | [-0.02, +0.16] | no |
| ATT+bal-2L (A) − ATT+bal | random 20 prepend | 1% FPR | malware TPR, fit subset | +1.97 | 3.58 | [+1.67, +2.31] | 7/3 | **yes** | [+0.80, +3.78] | yes |
| ATT+bal-2L (A) − ATT+bal | random 20 prepend | 0.1% FPR | malware TPR | -6.52 | 10.23 | [-6.95, -6.06] | 3/7 | **yes** | [-13.79, -0.20] | yes |
| ATT+bal-2L (A) − ATT+bal | random 20 prepend | 0.1% FPR | padded-benign FPR | -0.03 | 0.06 | [-0.07, +0.00] | 4/6 | no | [-0.08, +0.01] | no |
| ATT+bal-2L (A) − ATT+bal | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +2.53 | 11.92 | [+1.73, +3.36] | 5/5 | no | [-5.50, +12.28] | no |
| ATT+bal-2L (A) − ATT+bal | random 50 prepend | 1% FPR | malware TPR | +3.37 | 4.64 | [+3.16, +3.60] | 8/2 | **yes** | [+2.06, +4.70] | yes |
| ATT+bal-2L (A) − ATT+bal | random 50 prepend | 1% FPR | padded-benign FPR | -0.05 | 0.71 | [-0.14, +0.04] | 4/6 | no | [-0.32, +0.18] | no |
| ATT+bal-2L (A) − ATT+bal | random 50 prepend | 1% FPR | malware TPR, fit subset | +6.03 | 9.94 | [+5.47, +6.64] | 10/0 | **yes** | [+2.63, +8.62] | yes |
| ATT+bal-2L (A) − ATT+bal | random 50 prepend | 0.1% FPR | malware TPR | +6.64 | 9.90 | [+6.24, +7.02] | 6/4 | no | [+1.06, +12.02] | no |
| ATT+bal-2L (A) − ATT+bal | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.04 | 0.04 | [+0.02, +0.06] | 7/1 | **yes** | [+0.01, +0.07] | yes |
| ATT+bal-2L (A) − ATT+bal | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +12.93 | 8.59 | [+11.86, +13.99] | 9/1 | **yes** | [-0.44, +25.49] | no |
| ATT+bal-2L (A) − ATT+bal | random 100 prepend | 1% FPR | malware TPR | +6.82 | 10.80 | [+6.56, +7.08] | 9/1 | **yes** | [+4.14, +10.70] | yes |
| ATT+bal-2L (A) − ATT+bal | random 100 prepend | 1% FPR | padded-benign FPR | -0.44 | 0.56 | [-0.52, -0.36] | 3/7 | **yes** | [-0.52, -0.36] | yes |
| ATT+bal-2L (A) − ATT+bal | random 100 prepend | 0.1% FPR | malware TPR | +2.13 | 2.03 | [+1.91, +2.33] | 8/2 | **yes** | [+0.85, +3.87] | yes |
| ATT+bal-2L (A) − ATT+bal | random 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − ATT+bal | random 200 prepend | 1% FPR | malware TPR | +2.69 | 3.28 | [+2.52, +2.88] | 9/1 | **yes** | [+1.11, +5.37] | yes |
| ATT+bal-2L (A) − ATT+bal | random 200 prepend | 1% FPR | padded-benign FPR | -0.51 | 0.56 | [-0.58, -0.43] | 2/8 | **yes** | [-0.57, -0.44] | yes |
| ATT+bal-2L (A) − ATT+bal | random 200 prepend | 0.1% FPR | malware TPR | +0.76 | 2.19 | [+0.57, +0.94] | 5/5 | no | [-0.30, +2.19] | no |
| ATT+bal-2L (A) − ATT+bal | random 200 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − ATT+bal | random 5 insert | 1% FPR | malware TPR | +1.00 | 2.07 | [+0.81, +1.19] | 5/5 | no | [-0.91, +3.74] | no |
| ATT+bal-2L (A) − ATT+bal | random 5 insert | 1% FPR | padded-benign FPR | +0.03 | 0.16 | [-0.04, +0.09] | 5/4 | no | [-0.05, +0.12] | no |
| ATT+bal-2L (A) − ATT+bal | random 5 insert | 1% FPR | malware TPR, fit subset | +1.08 | 2.84 | [+0.78, +1.38] | 6/4 | no | [-0.13, +2.65] | no |
| ATT+bal-2L (A) − ATT+bal | random 5 insert | 0.1% FPR | malware TPR | -6.30 | 9.24 | [-6.73, -5.83] | 3/7 | **yes** | [-13.52, -0.21] | yes |
| ATT+bal-2L (A) − ATT+bal | random 5 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.03 | [-0.02, +0.02] | 5/4 | no | [-0.02, +0.03] | no |
| ATT+bal-2L (A) − ATT+bal | random 5 insert | 0.1% FPR | malware TPR, fit subset | -3.79 | 16.34 | [-4.45, -3.08] | 6/4 | no | [-8.08, -0.62] | no |
| ATT+bal-2L (A) − ATT+bal | random 20 insert | 1% FPR | malware TPR | +1.74 | 3.20 | [+1.57, +1.92] | 8/2 | **yes** | [+0.60, +3.17] | yes |
| ATT+bal-2L (A) − ATT+bal | random 20 insert | 1% FPR | padded-benign FPR | +0.01 | 0.27 | [-0.06, +0.08] | 5/5 | no | [-0.07, +0.11] | no |
| ATT+bal-2L (A) − ATT+bal | random 20 insert | 1% FPR | malware TPR, fit subset | +2.03 | 3.58 | [+1.72, +2.35] | 8/2 | **yes** | [+1.04, +3.51] | yes |
| ATT+bal-2L (A) − ATT+bal | random 20 insert | 0.1% FPR | malware TPR | -4.62 | 8.50 | [-5.07, -4.13] | 3/7 | **yes** | [-13.56, +3.51] | no |
| ATT+bal-2L (A) − ATT+bal | random 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.05 | [-0.02, +0.02] | 4/5 | no | [-0.03, +0.03] | no |
| ATT+bal-2L (A) − ATT+bal | random 20 insert | 0.1% FPR | malware TPR, fit subset | -0.84 | 15.00 | [-1.52, -0.07] | 5/5 | no | [-6.41, +2.65] | no |
| ATT+bal-2L (A) − ATT+bal | random 50 insert | 1% FPR | malware TPR | +1.87 | 3.52 | [+1.67, +2.07] | 7/3 | **yes** | [+0.64, +3.14] | yes |
| ATT+bal-2L (A) − ATT+bal | random 50 insert | 1% FPR | padded-benign FPR | +0.06 | 0.40 | [-0.02, +0.14] | 5/5 | no | [-0.04, +0.17] | no |
| ATT+bal-2L (A) − ATT+bal | random 50 insert | 1% FPR | malware TPR, fit subset | +4.52 | 6.03 | [+3.96, +5.09] | 9/1 | **yes** | [+1.44, +6.95] | yes |
| ATT+bal-2L (A) − ATT+bal | random 50 insert | 0.1% FPR | malware TPR | -1.70 | 9.11 | [-2.18, -1.22] | 5/5 | no | [-10.58, +7.07] | no |
| ATT+bal-2L (A) − ATT+bal | random 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.03 | [-0.02, +0.04] | 5/4 | no | [-0.03, +0.06] | no |
| ATT+bal-2L (A) − ATT+bal | random 50 insert | 0.1% FPR | malware TPR, fit subset | +4.97 | 9.71 | [+4.22, +5.72] | 7/3 | **yes** | [-2.70, +12.04] | no |
| ATT+bal-2L (A) − ATT+bal | random 100 insert | 1% FPR | malware TPR | +4.08 | 4.45 | [+3.85, +4.34] | 9/1 | **yes** | [+1.15, +7.51] | yes |
| ATT+bal-2L (A) − ATT+bal | random 100 insert | 1% FPR | padded-benign FPR | -0.26 | 0.39 | [-0.33, -0.19] | 3/7 | **yes** | [-0.36, -0.17] | yes |
| ATT+bal-2L (A) − ATT+bal | random 100 insert | 0.1% FPR | malware TPR | -3.97 | 10.55 | [-4.44, -3.51] | 3/7 | **yes** | [-12.72, +3.67] | no |
| ATT+bal-2L (A) − ATT+bal | random 100 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.01, +0.03] | 5/3 | no | [-0.01, +0.04] | no |
| ATT+bal-2L (A) − ATT+bal | random 200 insert | 1% FPR | malware TPR | +2.96 | 5.67 | [+2.71, +3.22] | 7/3 | **yes** | [+0.61, +5.40] | yes |
| ATT+bal-2L (A) − ATT+bal | random 200 insert | 1% FPR | padded-benign FPR | -0.41 | 0.43 | [-0.48, -0.33] | 2/8 | **yes** | [-0.54, -0.31] | yes |
| ATT+bal-2L (A) − ATT+bal | random 200 insert | 0.1% FPR | malware TPR | -5.02 | 8.34 | [-5.48, -4.53] | 2/8 | **yes** | [-12.77, +0.71] | no |
| ATT+bal-2L (A) − ATT+bal | random 200 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.01 | [-0.01, +0.00] | 1/3 | no | [-0.02, +0.01] | no |
| ATT+bal-2L (A) − v2-PE | random 5 prepend | 1% FPR | malware TPR | +25.37 | 7.25 | [+24.70, +26.01] | 10/0 | **yes** | [+15.54, +35.50] | yes |
| ATT+bal-2L (A) − v2-PE | random 5 prepend | 1% FPR | padded-benign FPR | +0.19 | 0.23 | [+0.04, +0.35] | 8/2 | **yes** | [-0.09, +0.51] | no |
| ATT+bal-2L (A) − v2-PE | random 5 prepend | 1% FPR | malware TPR, fit subset | +29.92 | 7.83 | [+28.69, +31.21] | 10/0 | **yes** | [+14.49, +46.05] | yes |
| ATT+bal-2L (A) − v2-PE | random 5 prepend | 0.1% FPR | malware TPR | +25.07 | 8.07 | [+24.30, +25.85] | 10/0 | **yes** | [+12.56, +35.22] | yes |
| ATT+bal-2L (A) − v2-PE | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.07 | 0.04 | [+0.03, +0.11] | 10/0 | **yes** | [+0.03, +0.12] | yes |
| ATT+bal-2L (A) − v2-PE | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +34.41 | 14.59 | [+32.97, +35.79] | 10/0 | **yes** | [+10.08, +50.71] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 prepend | 1% FPR | malware TPR | +55.44 | 8.55 | [+54.68, +56.22] | 10/0 | **yes** | [+44.03, +65.34] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 prepend | 1% FPR | padded-benign FPR | +0.16 | 1.47 | [-0.03, +0.36] | 8/2 | no | [-0.16, +0.53] | no |
| ATT+bal-2L (A) − v2-PE | random 20 prepend | 1% FPR | malware TPR, fit subset | +65.34 | 6.46 | [+63.79, +66.91] | 10/0 | **yes** | [+41.48, +78.18] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 prepend | 0.1% FPR | malware TPR | +39.74 | 7.57 | [+38.97, +40.58] | 10/0 | **yes** | [+26.63, +49.24] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.04 | 0.04 | [+0.01, +0.08] | 8/1 | **yes** | [+0.00, +0.09] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +43.67 | 12.34 | [+42.24, +45.08] | 10/0 | **yes** | [+17.97, +57.98] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 prepend | 1% FPR | malware TPR | +62.71 | 5.03 | [+61.81, +63.61] | 10/0 | **yes** | [+48.56, +72.74] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 prepend | 1% FPR | padded-benign FPR | +0.37 | 2.16 | [+0.17, +0.58] | 8/2 | **yes** | [+0.02, +0.83] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 prepend | 1% FPR | malware TPR, fit subset | +58.43 | 4.27 | [+56.29, +60.54] | 10/0 | **yes** | [+31.49, +77.09] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 prepend | 0.1% FPR | malware TPR | +37.29 | 7.66 | [+36.55, +38.16] | 10/0 | **yes** | [+25.00, +46.72] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.05 | 0.03 | [+0.01, +0.08] | 10/0 | **yes** | [+0.01, +0.10] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +22.35 | 10.17 | [+20.94, +23.69] | 10/0 | **yes** | [+5.55, +33.66] | yes |
| ATT+bal-2L (A) − v2-PE | random 100 prepend | 1% FPR | malware TPR | +8.10 | 11.75 | [+7.77, +8.47] | 8/2 | **yes** | [+5.27, +11.97] | yes |
| ATT+bal-2L (A) − v2-PE | random 100 prepend | 1% FPR | padded-benign FPR | -0.93 | 2.86 | [-1.06, -0.80] | 7/3 | **yes** | [-1.04, -0.81] | yes |
| ATT+bal-2L (A) − v2-PE | random 100 prepend | 0.1% FPR | malware TPR | +3.01 | 2.28 | [+2.77, +3.25] | 9/1 | **yes** | [+1.46, +5.11] | yes |
| ATT+bal-2L (A) − v2-PE | random 100 prepend | 0.1% FPR | padded-benign FPR | -0.03 | 0.07 | [-0.04, -0.02] | 0/3 | no | [-0.04, -0.02] | no |
| ATT+bal-2L (A) − v2-PE | random 200 prepend | 1% FPR | malware TPR | +4.03 | 6.22 | [+3.76, +4.34] | 8/2 | **yes** | [+1.78, +7.19] | yes |
| ATT+bal-2L (A) − v2-PE | random 200 prepend | 1% FPR | padded-benign FPR | -1.04 | 2.76 | [-1.16, -0.91] | 6/4 | no | [-1.16, -0.92] | no |
| ATT+bal-2L (A) − v2-PE | random 200 prepend | 0.1% FPR | malware TPR | +1.63 | 2.51 | [+1.47, +1.81] | 7/2 | **yes** | [+0.59, +2.99] | yes |
| ATT+bal-2L (A) − v2-PE | random 200 prepend | 0.1% FPR | padded-benign FPR | -0.03 | 0.07 | [-0.04, -0.01] | 0/2 | no | [-0.04, -0.02] | no |
| ATT+bal-2L (A) − v2-PE | random 5 insert | 1% FPR | malware TPR | +5.74 | 3.39 | [+5.33, +6.11] | 10/0 | **yes** | [+2.68, +8.48] | yes |
| ATT+bal-2L (A) − v2-PE | random 5 insert | 1% FPR | padded-benign FPR | +0.22 | 0.19 | [+0.07, +0.37] | 9/1 | **yes** | [+0.05, +0.42] | yes |
| ATT+bal-2L (A) − v2-PE | random 5 insert | 1% FPR | malware TPR, fit subset | +10.03 | 2.99 | [+9.13, +10.91] | 10/0 | **yes** | [+6.43, +14.18] | yes |
| ATT+bal-2L (A) − v2-PE | random 5 insert | 0.1% FPR | malware TPR | +6.48 | 6.94 | [+5.79, +7.21] | 8/2 | **yes** | [-4.42, +15.99] | no |
| ATT+bal-2L (A) − v2-PE | random 5 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.05 | [+0.00, +0.06] | 8/2 | **yes** | [+0.00, +0.07] | yes |
| ATT+bal-2L (A) − v2-PE | random 5 insert | 0.1% FPR | malware TPR, fit subset | +16.09 | 20.68 | [+14.97, +17.12] | 8/2 | **yes** | [+1.51, +25.46] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 insert | 1% FPR | malware TPR | +21.50 | 4.77 | [+20.85, +22.13] | 10/0 | **yes** | [+11.90, +31.78] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 insert | 1% FPR | padded-benign FPR | +0.42 | 0.46 | [+0.26, +0.58] | 8/2 | **yes** | [+0.17, +0.70] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 insert | 1% FPR | malware TPR, fit subset | +39.42 | 5.12 | [+37.86, +40.86] | 10/0 | **yes** | [+23.73, +58.97] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 insert | 0.1% FPR | malware TPR | +17.56 | 6.70 | [+16.83, +18.28] | 10/0 | **yes** | [+5.74, +26.91] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 insert | 0.1% FPR | padded-benign FPR | +0.05 | 0.03 | [+0.02, +0.09] | 9/0 | **yes** | [+0.01, +0.10] | yes |
| ATT+bal-2L (A) − v2-PE | random 20 insert | 0.1% FPR | malware TPR, fit subset | +32.02 | 15.68 | [+30.71, +33.25] | 10/0 | **yes** | [+9.32, +44.74] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 insert | 1% FPR | malware TPR | +32.35 | 4.85 | [+31.58, +33.06] | 10/0 | **yes** | [+20.92, +42.69] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 insert | 1% FPR | padded-benign FPR | +0.40 | 0.81 | [+0.24, +0.56] | 8/2 | **yes** | [+0.18, +0.66] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 insert | 1% FPR | malware TPR, fit subset | +51.05 | 4.21 | [+48.73, +53.22] | 10/0 | **yes** | [+22.56, +73.07] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 insert | 0.1% FPR | malware TPR | +24.47 | 6.54 | [+23.76, +25.24] | 10/0 | **yes** | [+11.27, +34.49] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.01, +0.07] | 9/1 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal-2L (A) − v2-PE | random 50 insert | 0.1% FPR | malware TPR, fit subset | +14.81 | 10.35 | [+13.77, +15.89] | 10/0 | **yes** | [+3.03, +22.47] | yes |
| ATT+bal-2L (A) − v2-PE | random 100 insert | 1% FPR | malware TPR | +37.68 | 5.08 | [+36.94, +38.44] | 10/0 | **yes** | [+25.91, +47.61] | yes |
| ATT+bal-2L (A) − v2-PE | random 100 insert | 1% FPR | padded-benign FPR | -0.25 | 1.38 | [-0.37, -0.14] | 7/3 | **yes** | [-0.41, -0.08] | yes |
| ATT+bal-2L (A) − v2-PE | random 100 insert | 0.1% FPR | malware TPR | +21.65 | 7.19 | [+21.00, +22.31] | 10/0 | **yes** | [+10.81, +31.05] | yes |
| ATT+bal-2L (A) − v2-PE | random 100 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.05] | 8/0 | **yes** | [-0.00, +0.07] | no |
| ATT+bal-2L (A) − v2-PE | random 200 insert | 1% FPR | malware TPR | +38.91 | 6.10 | [+38.04, +39.77] | 10/0 | **yes** | [+23.81, +51.54] | yes |
| ATT+bal-2L (A) − v2-PE | random 200 insert | 1% FPR | padded-benign FPR | -0.33 | 1.57 | [-0.45, -0.21] | 8/2 | **yes** | [-0.52, -0.14] | yes |
| ATT+bal-2L (A) − v2-PE | random 200 insert | 0.1% FPR | malware TPR | +16.06 | 6.94 | [+15.47, +16.64] | 10/0 | **yes** | [+8.27, +24.97] | yes |
| ATT+bal-2L (A) − v2-PE | random 200 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [-0.01, +0.01] | 4/2 | no | [-0.01, +0.01] | no |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 prepend | 1% FPR | malware TPR | +18.01 | 6.32 | [+17.37, +18.64] | 10/0 | **yes** | [+8.79, +27.84] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 prepend | 1% FPR | padded-benign FPR | +0.64 | 0.16 | [+0.49, +0.80] | 10/0 | **yes** | [+0.44, +0.89] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 prepend | 1% FPR | malware TPR, fit subset | +31.69 | 4.98 | [+30.27, +33.08] | 10/0 | **yes** | [+15.29, +47.17] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 prepend | 0.1% FPR | malware TPR | +19.57 | 15.60 | [+18.88, +20.25] | 9/1 | **yes** | [+6.96, +30.67] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.07 | 0.04 | [+0.03, +0.11] | 10/0 | **yes** | [+0.03, +0.13] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +32.49 | 13.53 | [+31.17, +33.87] | 10/0 | **yes** | [+6.87, +48.37] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 prepend | 1% FPR | malware TPR | +27.40 | 6.76 | [+26.65, +28.12] | 10/0 | **yes** | [+15.81, +39.73] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 prepend | 1% FPR | padded-benign FPR | +1.17 | 0.23 | [+1.01, +1.34] | 10/0 | **yes** | [+0.85, +1.56] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 prepend | 1% FPR | malware TPR, fit subset | +53.10 | 4.97 | [+51.48, +54.59] | 10/0 | **yes** | [+32.43, +69.37] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 prepend | 0.1% FPR | malware TPR | +27.26 | 15.05 | [+26.60, +27.96] | 10/0 | **yes** | [+14.59, +38.54] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.05 | 0.05 | [+0.02, +0.09] | 9/1 | **yes** | [+0.02, +0.10] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +39.74 | 13.90 | [+38.34, +41.12] | 10/0 | **yes** | [+13.61, +55.27] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 prepend | 1% FPR | malware TPR | +42.76 | 9.07 | [+41.93, +43.62] | 10/0 | **yes** | [+28.17, +56.60] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 prepend | 1% FPR | padded-benign FPR | +1.45 | 0.61 | [+1.28, +1.64] | 10/0 | **yes** | [+1.05, +1.96] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 prepend | 1% FPR | malware TPR, fit subset | +58.13 | 2.94 | [+56.03, +60.33] | 10/0 | **yes** | [+31.77, +77.89] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 prepend | 0.1% FPR | malware TPR | +36.63 | 8.65 | [+35.88, +37.47] | 10/0 | **yes** | [+24.82, +45.47] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.05 | 0.03 | [+0.02, +0.10] | 10/0 | **yes** | [+0.02, +0.11] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +22.16 | 10.57 | [+20.76, +23.49] | 10/0 | **yes** | [+5.57, +33.52] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 100 prepend | 1% FPR | malware TPR | +2.19 | 18.75 | [+1.66, +2.70] | 6/4 | no | [-3.63, +7.54] | no |
| ATT+bal-2L (A) − B (2L, no padding) | random 100 prepend | 1% FPR | padded-benign FPR | +0.52 | 0.22 | [+0.44, +0.62] | 10/0 | **yes** | [+0.43, +0.62] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 100 prepend | 0.1% FPR | malware TPR | +4.32 | 1.68 | [+4.00, +4.64] | 10/0 | **yes** | [+2.14, +7.22] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − B (2L, no padding) | random 200 prepend | 1% FPR | malware TPR | +5.84 | 8.83 | [+5.31, +6.35] | 8/2 | **yes** | [+1.76, +10.84] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 200 prepend | 1% FPR | padded-benign FPR | +0.40 | 0.27 | [+0.32, +0.47] | 10/0 | **yes** | [+0.32, +0.48] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 200 prepend | 0.1% FPR | malware TPR | +2.99 | 2.29 | [+2.74, +3.23] | 10/0 | **yes** | [+1.34, +5.19] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 200 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 insert | 1% FPR | malware TPR | +15.25 | 5.55 | [+14.70, +15.82] | 10/0 | **yes** | [+7.99, +22.87] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 insert | 1% FPR | padded-benign FPR | +0.62 | 0.15 | [+0.48, +0.77] | 10/0 | **yes** | [+0.41, +0.86] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 insert | 1% FPR | malware TPR, fit subset | +25.10 | 3.87 | [+23.81, +26.32] | 10/0 | **yes** | [+12.37, +35.97] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 insert | 0.1% FPR | malware TPR | +20.21 | 14.73 | [+19.52, +20.91] | 10/0 | **yes** | [+8.14, +31.13] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 insert | 0.1% FPR | padded-benign FPR | +0.06 | 0.03 | [+0.03, +0.09] | 10/0 | **yes** | [+0.03, +0.10] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 5 insert | 0.1% FPR | malware TPR, fit subset | +30.09 | 13.60 | [+28.78, +31.34] | 10/0 | **yes** | [+5.69, +45.52] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 insert | 1% FPR | malware TPR | +28.07 | 6.00 | [+27.36, +28.80] | 10/0 | **yes** | [+16.34, +40.11] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 insert | 1% FPR | padded-benign FPR | +0.93 | 0.17 | [+0.79, +1.09] | 10/0 | **yes** | [+0.68, +1.28] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 insert | 1% FPR | malware TPR, fit subset | +50.91 | 2.86 | [+49.38, +52.51] | 10/0 | **yes** | [+29.95, +67.73] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 insert | 0.1% FPR | malware TPR | +25.21 | 12.93 | [+24.64, +25.79] | 10/0 | **yes** | [+15.99, +33.48] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 insert | 0.1% FPR | padded-benign FPR | +0.07 | 0.03 | [+0.04, +0.11] | 10/0 | **yes** | [+0.03, +0.13] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 20 insert | 0.1% FPR | malware TPR, fit subset | +35.28 | 13.49 | [+34.00, +36.63] | 10/0 | **yes** | [+11.36, +50.78] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 insert | 1% FPR | malware TPR | +40.38 | 6.23 | [+39.54, +41.20] | 10/0 | **yes** | [+25.80, +54.18] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 insert | 1% FPR | padded-benign FPR | +1.00 | 0.30 | [+0.85, +1.17] | 10/0 | **yes** | [+0.72, +1.35] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 insert | 1% FPR | malware TPR, fit subset | +54.99 | 2.05 | [+52.64, +57.29] | 10/0 | **yes** | [+26.79, +75.48] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 insert | 0.1% FPR | malware TPR | +31.66 | 9.06 | [+31.02, +32.34] | 10/0 | **yes** | [+20.97, +40.40] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 insert | 0.1% FPR | padded-benign FPR | +0.05 | 0.03 | [+0.02, +0.08] | 10/0 | **yes** | [+0.02, +0.09] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 50 insert | 0.1% FPR | malware TPR, fit subset | +15.09 | 10.24 | [+14.03, +16.22] | 10/0 | **yes** | [+3.19, +22.80] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 100 insert | 1% FPR | malware TPR | +45.71 | 7.21 | [+44.93, +46.51] | 10/0 | **yes** | [+33.34, +57.69] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 100 insert | 1% FPR | padded-benign FPR | +0.55 | 0.18 | [+0.44, +0.66] | 10/0 | **yes** | [+0.40, +0.76] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 100 insert | 0.1% FPR | malware TPR | +27.40 | 8.73 | [+26.77, +28.08] | 10/0 | **yes** | [+17.27, +36.48] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 100 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.02 | [+0.01, +0.06] | 9/0 | **yes** | [+0.00, +0.07] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 200 insert | 1% FPR | malware TPR | +48.01 | 4.67 | [+47.19, +48.87] | 10/0 | **yes** | [+34.30, +60.03] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 200 insert | 1% FPR | padded-benign FPR | +0.53 | 0.23 | [+0.43, +0.64] | 10/0 | **yes** | [+0.40, +0.70] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 200 insert | 0.1% FPR | malware TPR | +19.81 | 7.08 | [+19.22, +20.42] | 10/0 | **yes** | [+11.77, +29.83] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | random 200 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.01] | 5/0 | no | [+0.00, +0.02] | no |
| B (2L, no padding) − ATT+bal | random 5 prepend | 1% FPR | malware TPR | -17.27 | 5.72 | [-17.91, -16.62] | 0/10 | **yes** | [-27.04, -7.57] | yes |
| B (2L, no padding) − ATT+bal | random 5 prepend | 1% FPR | padded-benign FPR | -0.62 | 0.19 | [-0.78, -0.49] | 0/10 | **yes** | [-0.87, -0.43] | yes |
| B (2L, no padding) − ATT+bal | random 5 prepend | 1% FPR | malware TPR, fit subset | -30.14 | 3.46 | [-31.46, -28.81] | 0/10 | **yes** | [-45.36, -13.49] | yes |
| B (2L, no padding) − ATT+bal | random 5 prepend | 0.1% FPR | malware TPR | -26.26 | 11.57 | [-26.93, -25.56] | 0/10 | **yes** | [-34.71, -15.79] | yes |
| B (2L, no padding) − ATT+bal | random 5 prepend | 0.1% FPR | padded-benign FPR | -0.09 | 0.03 | [-0.14, -0.04] | 0/10 | **yes** | [-0.16, -0.04] | yes |
| B (2L, no padding) − ATT+bal | random 5 prepend | 0.1% FPR | malware TPR, fit subset | -34.09 | 10.25 | [-35.30, -32.87] | 0/10 | **yes** | [-47.76, -13.32] | yes |
| B (2L, no padding) − ATT+bal | random 20 prepend | 1% FPR | malware TPR | -26.35 | 6.25 | [-27.08, -25.59] | 0/10 | **yes** | [-38.69, -14.54] | yes |
| B (2L, no padding) − ATT+bal | random 20 prepend | 1% FPR | padded-benign FPR | -1.11 | 0.26 | [-1.27, -0.96] | 0/10 | **yes** | [-1.48, -0.81] | yes |
| B (2L, no padding) − ATT+bal | random 20 prepend | 1% FPR | malware TPR, fit subset | -51.13 | 3.98 | [-52.57, -49.63] | 0/10 | **yes** | [-67.50, -30.05] | yes |
| B (2L, no padding) − ATT+bal | random 20 prepend | 0.1% FPR | malware TPR | -33.78 | 11.91 | [-34.46, -33.13] | 0/10 | **yes** | [-42.51, -23.29] | yes |
| B (2L, no padding) − ATT+bal | random 20 prepend | 0.1% FPR | padded-benign FPR | -0.08 | 0.03 | [-0.14, -0.03] | 0/10 | **yes** | [-0.16, -0.02] | yes |
| B (2L, no padding) − ATT+bal | random 20 prepend | 0.1% FPR | malware TPR, fit subset | -37.21 | 10.06 | [-38.64, -35.84] | 0/10 | **yes** | [-54.30, -16.74] | yes |
| B (2L, no padding) − ATT+bal | random 50 prepend | 1% FPR | malware TPR | -39.39 | 10.06 | [-40.17, -38.56] | 0/10 | **yes** | [-52.48, -25.61] | yes |
| B (2L, no padding) − ATT+bal | random 50 prepend | 1% FPR | padded-benign FPR | -1.50 | 0.79 | [-1.68, -1.33] | 0/10 | **yes** | [-2.02, -1.10] | yes |
| B (2L, no padding) − ATT+bal | random 50 prepend | 1% FPR | malware TPR, fit subset | -52.10 | 10.14 | [-54.05, -50.10] | 0/10 | **yes** | [-70.54, -27.99] | yes |
| B (2L, no padding) − ATT+bal | random 50 prepend | 0.1% FPR | malware TPR | -29.99 | 6.90 | [-30.80, -29.27] | 0/10 | **yes** | [-39.59, -19.76] | yes |
| B (2L, no padding) − ATT+bal | random 50 prepend | 0.1% FPR | padded-benign FPR | -0.02 | 0.02 | [-0.04, +0.00] | 0/6 | no | [-0.05, +0.00] | no |
| B (2L, no padding) − ATT+bal | random 50 prepend | 0.1% FPR | malware TPR, fit subset | -9.23 | 4.85 | [-10.33, -8.18] | 0/10 | **yes** | [-19.52, -3.32] | yes |
| B (2L, no padding) − ATT+bal | random 100 prepend | 1% FPR | malware TPR | +4.63 | 12.77 | [+4.05, +5.22] | 5/5 | no | [-2.35, +12.23] | no |
| B (2L, no padding) − ATT+bal | random 100 prepend | 1% FPR | padded-benign FPR | -0.97 | 0.62 | [-1.09, -0.85] | 0/10 | **yes** | [-1.09, -0.85] | yes |
| B (2L, no padding) − ATT+bal | random 100 prepend | 0.1% FPR | malware TPR | -2.20 | 0.94 | [-2.45, -1.95] | 0/10 | **yes** | [-4.31, -0.84] | yes |
| B (2L, no padding) − ATT+bal | random 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | random 200 prepend | 1% FPR | malware TPR | -3.15 | 7.50 | [-3.69, -2.61] | 3/7 | **yes** | [-8.95, +2.16] | no |
| B (2L, no padding) − ATT+bal | random 200 prepend | 1% FPR | padded-benign FPR | -0.90 | 0.63 | [-1.01, -0.80] | 0/10 | **yes** | [-1.00, -0.81] | yes |
| B (2L, no padding) − ATT+bal | random 200 prepend | 0.1% FPR | malware TPR | -2.22 | 1.01 | [-2.47, -1.97] | 0/10 | **yes** | [-4.36, -0.85] | yes |
| B (2L, no padding) − ATT+bal | random 200 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | random 5 insert | 1% FPR | malware TPR | -14.25 | 4.95 | [-14.85, -13.63] | 0/10 | **yes** | [-22.36, -4.99] | yes |
| B (2L, no padding) − ATT+bal | random 5 insert | 1% FPR | padded-benign FPR | -0.59 | 0.22 | [-0.73, -0.46] | 0/10 | **yes** | [-0.81, -0.42] | yes |
| B (2L, no padding) − ATT+bal | random 5 insert | 1% FPR | malware TPR, fit subset | -24.02 | 3.65 | [-25.19, -22.78] | 0/10 | **yes** | [-35.04, -11.09] | yes |
| B (2L, no padding) − ATT+bal | random 5 insert | 0.1% FPR | malware TPR | -26.51 | 11.52 | [-27.18, -25.84] | 0/10 | **yes** | [-34.76, -16.81] | yes |
| B (2L, no padding) − ATT+bal | random 5 insert | 0.1% FPR | padded-benign FPR | -0.05 | 0.03 | [-0.09, -0.02] | 0/10 | **yes** | [-0.10, -0.02] | yes |
| B (2L, no padding) − ATT+bal | random 5 insert | 0.1% FPR | malware TPR, fit subset | -33.89 | 9.61 | [-35.13, -32.59] | 0/10 | **yes** | [-47.53, -12.89] | yes |
| B (2L, no padding) − ATT+bal | random 20 insert | 1% FPR | malware TPR | -26.33 | 5.79 | [-27.07, -25.61] | 0/10 | **yes** | [-38.06, -14.90] | yes |
| B (2L, no padding) − ATT+bal | random 20 insert | 1% FPR | padded-benign FPR | -0.93 | 0.30 | [-1.07, -0.79] | 0/10 | **yes** | [-1.24, -0.67] | yes |
| B (2L, no padding) − ATT+bal | random 20 insert | 1% FPR | malware TPR, fit subset | -48.88 | 2.68 | [-50.41, -47.34] | 0/10 | **yes** | [-65.29, -27.85] | yes |
| B (2L, no padding) − ATT+bal | random 20 insert | 0.1% FPR | malware TPR | -29.84 | 8.79 | [-30.53, -29.13] | 0/10 | **yes** | [-38.70, -20.67] | yes |
| B (2L, no padding) − ATT+bal | random 20 insert | 0.1% FPR | padded-benign FPR | -0.07 | 0.03 | [-0.12, -0.03] | 0/10 | **yes** | [-0.13, -0.03] | yes |
| B (2L, no padding) − ATT+bal | random 20 insert | 0.1% FPR | malware TPR, fit subset | -36.13 | 7.56 | [-37.54, -34.67] | 0/10 | **yes** | [-51.07, -15.29] | yes |
| B (2L, no padding) − ATT+bal | random 50 insert | 1% FPR | malware TPR | -38.51 | 6.22 | [-39.34, -37.71] | 0/10 | **yes** | [-51.84, -24.50] | yes |
| B (2L, no padding) − ATT+bal | random 50 insert | 1% FPR | padded-benign FPR | -0.95 | 0.38 | [-1.09, -0.81] | 0/10 | **yes** | [-1.28, -0.70] | yes |
| B (2L, no padding) − ATT+bal | random 50 insert | 1% FPR | malware TPR, fit subset | -50.46 | 6.63 | [-52.70, -48.31] | 0/10 | **yes** | [-70.02, -24.00] | yes |
| B (2L, no padding) − ATT+bal | random 50 insert | 0.1% FPR | malware TPR | -33.36 | 5.77 | [-34.08, -32.61] | 0/10 | **yes** | [-44.25, -22.96] | yes |
| B (2L, no padding) − ATT+bal | random 50 insert | 0.1% FPR | padded-benign FPR | -0.03 | 0.01 | [-0.06, -0.01] | 0/10 | **yes** | [-0.08, -0.01] | yes |
| B (2L, no padding) − ATT+bal | random 50 insert | 0.1% FPR | malware TPR, fit subset | -10.12 | 5.36 | [-11.22, -9.06] | 0/10 | **yes** | [-18.21, -3.85] | yes |
| B (2L, no padding) − ATT+bal | random 100 insert | 1% FPR | malware TPR | -41.63 | 6.61 | [-42.40, -40.85] | 0/10 | **yes** | [-53.50, -30.56] | yes |
| B (2L, no padding) − ATT+bal | random 100 insert | 1% FPR | padded-benign FPR | -0.81 | 0.43 | [-0.93, -0.68] | 0/10 | **yes** | [-1.06, -0.62] | yes |
| B (2L, no padding) − ATT+bal | random 100 insert | 0.1% FPR | malware TPR | -31.37 | 4.09 | [-32.23, -30.55] | 0/10 | **yes** | [-43.64, -19.51] | yes |
| B (2L, no padding) − ATT+bal | random 100 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.02 | [-0.04, -0.01] | 0/8 | **yes** | [-0.04, -0.01] | yes |
| B (2L, no padding) − ATT+bal | random 200 insert | 1% FPR | malware TPR | -45.05 | 6.25 | [-45.86, -44.20] | 0/10 | **yes** | [-56.20, -32.59] | yes |
| B (2L, no padding) − ATT+bal | random 200 insert | 1% FPR | padded-benign FPR | -0.95 | 0.45 | [-1.07, -0.81] | 0/10 | **yes** | [-1.18, -0.75] | yes |
| B (2L, no padding) − ATT+bal | random 200 insert | 0.1% FPR | malware TPR | -24.82 | 2.37 | [-25.63, -24.06] | 0/10 | **yes** | [-38.35, -12.82] | yes |
| B (2L, no padding) − ATT+bal | random 200 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.01 | [-0.02, -0.00] | 0/7 | **yes** | [-0.03, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 prepend | 1% FPR | malware TPR | -0.44 | 1.06 | [-0.55, -0.33] | 4/6 | no | [-1.48, +0.51] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 prepend | 1% FPR | padded-benign FPR | -0.03 | 0.10 | [-0.07, +0.02] | 3/5 | no | [-0.09, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 prepend | 1% FPR | malware TPR, fit subset | +0.69 | 1.04 | [+0.53, +0.85] | 8/2 | **yes** | [+0.25, +1.47] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 prepend | 0.1% FPR | malware TPR | -1.69 | 4.52 | [-1.87, -1.49] | 3/7 | **yes** | [-3.48, +0.20] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.02, +0.01] | 3/4 | no | [-0.02, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 prepend | 0.1% FPR | malware TPR, fit subset | -0.40 | 4.91 | [-0.77, +0.00] | 3/7 | no | [-2.99, +2.15] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 prepend | 1% FPR | malware TPR | -0.24 | 1.01 | [-0.35, -0.14] | 4/6 | no | [-0.79, +0.27] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 prepend | 1% FPR | padded-benign FPR | -0.04 | 0.21 | [-0.09, +0.02] | 4/6 | no | [-0.13, +0.05] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 prepend | 1% FPR | malware TPR, fit subset | +0.89 | 1.07 | [+0.73, +1.07] | 7/3 | **yes** | [+0.46, +1.68] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 prepend | 0.1% FPR | malware TPR | -2.08 | 5.14 | [-2.29, -1.88] | 4/6 | no | [-3.69, -0.42] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.02 | [-0.01, +0.02] | 6/4 | no | [-0.01, +0.02] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 prepend | 0.1% FPR | malware TPR, fit subset | -2.03 | 6.19 | [-2.50, -1.55] | 4/6 | no | [-4.90, +0.46] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 prepend | 1% FPR | malware TPR | +0.25 | 1.87 | [+0.12, +0.38] | 6/4 | no | [-0.56, +1.07] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 prepend | 1% FPR | padded-benign FPR | -0.39 | 0.42 | [-0.45, -0.33] | 2/8 | **yes** | [-0.60, -0.25] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 prepend | 1% FPR | malware TPR, fit subset | -0.81 | 3.95 | [-1.15, -0.48] | 3/7 | **yes** | [-1.83, -0.14] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 prepend | 0.1% FPR | malware TPR | +5.42 | 2.83 | [+5.14, +5.70] | 10/0 | **yes** | [+2.84, +8.03] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.03] | 9/0 | **yes** | [+0.01, +0.03] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +2.38 | 4.96 | [+2.09, +2.66] | 8/2 | **yes** | [+0.95, +3.39] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 100 prepend | 1% FPR | malware TPR | +1.32 | 1.52 | [+1.22, +1.44] | 8/2 | **yes** | [+0.44, +2.90] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 100 prepend | 1% FPR | padded-benign FPR | -0.65 | 0.53 | [-0.74, -0.57] | 0/10 | **yes** | [-0.73, -0.57] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 100 prepend | 0.1% FPR | malware TPR | +1.76 | 0.92 | [+1.56, +1.94] | 10/0 | **yes** | [+0.54, +3.51] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 200 prepend | 1% FPR | malware TPR | -0.17 | 1.37 | [-0.26, -0.09] | 2/8 | **yes** | [-0.65, +0.58] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 200 prepend | 1% FPR | padded-benign FPR | -0.60 | 0.52 | [-0.67, -0.53] | 0/9 | **yes** | [-0.66, -0.53] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 200 prepend | 0.1% FPR | malware TPR | +1.38 | 1.34 | [+1.21, +1.54] | 9/1 | **yes** | [+0.29, +2.99] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 200 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 insert | 1% FPR | malware TPR | -0.28 | 1.33 | [-0.40, -0.15] | 5/5 | no | [-1.47, +1.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 insert | 1% FPR | padded-benign FPR | -0.02 | 0.10 | [-0.07, +0.01] | 4/6 | no | [-0.08, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 insert | 1% FPR | malware TPR, fit subset | +0.52 | 0.88 | [+0.38, +0.68] | 8/2 | **yes** | [+0.16, +1.22] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 insert | 0.1% FPR | malware TPR | -2.73 | 4.50 | [-2.95, -2.51] | 4/6 | no | [-5.06, -0.56] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [-0.01, +0.03] | 4/1 | no | [-0.01, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 5 insert | 0.1% FPR | malware TPR, fit subset | -2.19 | 4.96 | [-2.58, -1.79] | 4/6 | no | [-6.20, +1.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 insert | 1% FPR | malware TPR | -0.40 | 0.85 | [-0.51, -0.29] | 3/7 | **yes** | [-0.96, +0.11] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 insert | 1% FPR | padded-benign FPR | -0.08 | 0.22 | [-0.13, -0.04] | 3/7 | **yes** | [-0.14, -0.04] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 insert | 1% FPR | malware TPR, fit subset | +0.47 | 1.01 | [+0.31, +0.63] | 6/3 | no | [+0.20, +0.98] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 insert | 0.1% FPR | malware TPR | -1.86 | 4.39 | [-2.07, -1.64] | 3/7 | **yes** | [-4.36, +0.12] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.03 | [-0.01, +0.02] | 4/3 | no | [-0.01, +0.02] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 20 insert | 0.1% FPR | malware TPR, fit subset | -2.68 | 6.09 | [-3.22, -2.14] | 5/5 | no | [-9.15, +2.40] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 insert | 1% FPR | malware TPR | -0.85 | 1.26 | [-0.98, -0.73] | 2/8 | **yes** | [-1.77, -0.06] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 insert | 1% FPR | padded-benign FPR | -0.20 | 0.25 | [-0.24, -0.15] | 2/8 | **yes** | [-0.27, -0.14] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 insert | 1% FPR | malware TPR, fit subset | -0.47 | 3.09 | [-0.75, -0.21] | 3/6 | no | [-1.59, +0.23] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 insert | 0.1% FPR | malware TPR | +0.99 | 4.55 | [+0.76, +1.21] | 6/4 | no | [-1.18, +3.69] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.03 | [+0.00, +0.03] | 5/3 | no | [+0.00, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 50 insert | 0.1% FPR | malware TPR, fit subset | +0.39 | 1.56 | [+0.14, +0.64] | 6/4 | no | [+0.08, +0.86] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 100 insert | 1% FPR | malware TPR | -0.96 | 2.34 | [-1.11, -0.80] | 3/7 | **yes** | [-1.90, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 100 insert | 1% FPR | padded-benign FPR | -0.37 | 0.29 | [-0.43, -0.32] | 0/10 | **yes** | [-0.48, -0.29] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 100 insert | 0.1% FPR | malware TPR | +1.04 | 4.92 | [+0.85, +1.24] | 6/4 | no | [-0.98, +2.80] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 100 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.03 | [+0.00, +0.04] | 6/2 | no | [+0.00, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 200 insert | 1% FPR | malware TPR | -1.80 | 2.28 | [-1.95, -1.64] | 3/7 | **yes** | [-2.56, -1.03] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 200 insert | 1% FPR | padded-benign FPR | -0.50 | 0.33 | [-0.57, -0.43] | 0/10 | **yes** | [-0.60, -0.41] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 200 insert | 0.1% FPR | malware TPR | +1.17 | 5.01 | [+0.97, +1.39] | 7/3 | **yes** | [-0.74, +2.99] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | random 200 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.00, +0.02] | 4/2 | no | [+0.00, +0.02] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 prepend | 1% FPR | malware TPR | +24.19 | 6.39 | [+23.55, +24.82] | 10/0 | **yes** | [+14.24, +34.44] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 prepend | 1% FPR | padded-benign FPR | +0.15 | 0.26 | [+0.01, +0.30] | 8/2 | **yes** | [-0.16, +0.46] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 prepend | 1% FPR | malware TPR, fit subset | +29.05 | 6.47 | [+27.89, +30.29] | 10/0 | **yes** | [+13.91, +45.00] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 prepend | 0.1% FPR | malware TPR | +30.08 | 7.98 | [+29.36, +30.84] | 10/0 | **yes** | [+18.47, +38.98] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.03 | [+0.03, +0.13] | 10/0 | **yes** | [+0.03, +0.14] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +35.61 | 9.61 | [+34.20, +36.97] | 10/0 | **yes** | [+13.85, +54.57] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 prepend | 1% FPR | malware TPR | +54.15 | 8.14 | [+53.39, +54.94] | 10/0 | **yes** | [+42.26, +64.12] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 prepend | 1% FPR | padded-benign FPR | +0.06 | 1.53 | [-0.12, +0.26] | 8/2 | no | [-0.26, +0.41] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 prepend | 1% FPR | malware TPR, fit subset | +64.26 | 5.92 | [+62.79, +65.80] | 10/0 | **yes** | [+40.44, +77.09] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 prepend | 0.1% FPR | malware TPR | +44.19 | 8.55 | [+43.40, +44.97] | 10/0 | **yes** | [+31.86, +53.38] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.07 | 0.04 | [+0.02, +0.13] | 10/0 | **yes** | [+0.01, +0.15] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +39.12 | 9.32 | [+37.76, +40.60] | 10/0 | **yes** | [+18.52, +57.24] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 prepend | 1% FPR | malware TPR | +59.59 | 7.10 | [+58.68, +60.47] | 10/0 | **yes** | [+45.48, +69.78] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 prepend | 1% FPR | padded-benign FPR | +0.04 | 2.12 | [-0.13, +0.23] | 8/2 | no | [-0.25, +0.39] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 prepend | 1% FPR | malware TPR, fit subset | +51.59 | 8.90 | [+49.42, +53.63] | 10/0 | **yes** | [+26.19, +68.81] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 prepend | 0.1% FPR | malware TPR | +36.07 | 6.60 | [+35.31, +36.96] | 10/0 | **yes** | [+23.83, +47.20] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.02 | 0.04 | [+0.00, +0.05] | 8/1 | **yes** | [-0.00, +0.07] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +11.80 | 8.59 | [+10.65, +12.97] | 10/0 | **yes** | [+4.77, +21.94] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 100 prepend | 1% FPR | malware TPR | +2.60 | 5.78 | [+2.35, +2.88] | 8/2 | **yes** | [+0.85, +4.95] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 100 prepend | 1% FPR | padded-benign FPR | -1.14 | 2.91 | [-1.26, -1.03] | 6/4 | no | [-1.24, -1.03] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 100 prepend | 0.1% FPR | malware TPR | +2.64 | 2.42 | [+2.39, +2.91] | 8/2 | **yes** | [+0.98, +4.89] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 100 prepend | 0.1% FPR | padded-benign FPR | -0.02 | 0.07 | [-0.04, -0.01] | 1/3 | no | [-0.04, -0.02] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 200 prepend | 1% FPR | malware TPR | +1.16 | 5.55 | [+0.94, +1.39] | 7/3 | **yes** | [-0.18, +3.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 200 prepend | 1% FPR | padded-benign FPR | -1.13 | 2.81 | [-1.24, -1.02] | 6/4 | no | [-1.23, -1.03] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 200 prepend | 0.1% FPR | malware TPR | +2.25 | 2.54 | [+2.03, +2.47] | 8/2 | **yes** | [+0.78, +4.24] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 200 prepend | 0.1% FPR | padded-benign FPR | -0.03 | 0.07 | [-0.04, -0.01] | 0/2 | no | [-0.04, -0.02] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 insert | 1% FPR | malware TPR | +4.46 | 3.92 | [+4.06, +4.85] | 9/1 | **yes** | [+0.14, +7.70] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 insert | 1% FPR | padded-benign FPR | +0.17 | 0.24 | [+0.04, +0.31] | 8/2 | **yes** | [+0.02, +0.34] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 insert | 1% FPR | malware TPR, fit subset | +9.47 | 3.96 | [+8.66, +10.30] | 10/0 | **yes** | [+6.25, +13.15] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 insert | 0.1% FPR | malware TPR | +10.06 | 7.71 | [+9.41, +10.67] | 9/1 | **yes** | [+2.89, +15.43] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.00, +0.08] | 9/1 | **yes** | [+0.00, +0.08] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 5 insert | 0.1% FPR | malware TPR, fit subset | +17.70 | 12.17 | [+16.68, +18.61] | 9/1 | **yes** | [+6.92, +24.41] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 insert | 1% FPR | malware TPR | +19.36 | 5.19 | [+18.68, +20.00] | 10/0 | **yes** | [+9.85, +29.73] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 insert | 1% FPR | padded-benign FPR | +0.33 | 0.54 | [+0.18, +0.49] | 8/2 | **yes** | [+0.10, +0.57] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 insert | 1% FPR | malware TPR, fit subset | +37.85 | 4.97 | [+36.31, +39.25] | 10/0 | **yes** | [+22.31, +56.40] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 insert | 0.1% FPR | malware TPR | +20.32 | 7.31 | [+19.61, +21.06] | 10/0 | **yes** | [+10.63, +28.54] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 insert | 0.1% FPR | padded-benign FPR | +0.05 | 0.02 | [+0.01, +0.10] | 9/0 | **yes** | [+0.01, +0.11] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 20 insert | 0.1% FPR | malware TPR, fit subset | +30.18 | 7.90 | [+28.86, +31.55] | 10/0 | **yes** | [+11.83, +46.20] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 insert | 1% FPR | malware TPR | +29.62 | 5.37 | [+28.82, +30.32] | 10/0 | **yes** | [+18.48, +39.60] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 insert | 1% FPR | padded-benign FPR | +0.14 | 0.76 | [+0.01, +0.28] | 8/2 | **yes** | [-0.04, +0.35] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 insert | 1% FPR | malware TPR, fit subset | +46.06 | 6.45 | [+44.04, +48.14] | 10/0 | **yes** | [+19.14, +67.38] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 insert | 0.1% FPR | malware TPR | +27.16 | 7.07 | [+26.42, +27.96] | 10/0 | **yes** | [+15.92, +37.27] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.01, +0.07] | 8/0 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 50 insert | 0.1% FPR | malware TPR, fit subset | +10.23 | 5.21 | [+9.17, +11.35] | 10/0 | **yes** | [+3.89, +18.49] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 100 insert | 1% FPR | malware TPR | +32.64 | 5.51 | [+31.90, +33.34] | 10/0 | **yes** | [+21.04, +43.20] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 100 insert | 1% FPR | padded-benign FPR | -0.37 | 1.39 | [-0.48, -0.26] | 7/3 | **yes** | [-0.52, -0.21] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 100 insert | 0.1% FPR | malware TPR | +26.66 | 6.48 | [+25.91, +27.44] | 10/0 | **yes** | [+15.52, +37.33] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 100 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.04 | [+0.01, +0.07] | 8/1 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 200 insert | 1% FPR | malware TPR | +34.15 | 7.62 | [+33.29, +35.00] | 10/0 | **yes** | [+20.86, +45.41] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 200 insert | 1% FPR | padded-benign FPR | -0.41 | 1.64 | [-0.53, -0.30] | 8/2 | **yes** | [-0.59, -0.24] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 200 insert | 0.1% FPR | malware TPR | +22.25 | 5.74 | [+21.51, +22.97] | 10/0 | **yes** | [+11.87, +34.27] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | random 200 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.00, +0.03] | 6/2 | no | [-0.00, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 prepend | 1% FPR | malware TPR | -1.18 | 2.79 | [-1.34, -1.00] | 3/7 | **yes** | [-2.15, -0.43] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 prepend | 1% FPR | padded-benign FPR | -0.04 | 0.16 | [-0.11, +0.03] | 4/6 | no | [-0.14, +0.05] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 prepend | 1% FPR | malware TPR, fit subset | -0.87 | 3.51 | [-1.18, -0.53] | 5/5 | no | [-2.54, +0.57] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 prepend | 0.1% FPR | malware TPR | +5.01 | 11.19 | [+4.63, +5.40] | 7/3 | **yes** | [-0.53, +11.80] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.05 | [-0.01, +0.04] | 6/2 | no | [-0.02, +0.05] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +1.20 | 14.96 | [+0.61, +1.78] | 4/6 | no | [-4.96, +5.99] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 prepend | 1% FPR | malware TPR | -1.28 | 2.17 | [-1.45, -1.12] | 4/6 | no | [-2.77, -0.30] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 prepend | 1% FPR | padded-benign FPR | -0.10 | 0.27 | [-0.18, -0.01] | 3/7 | **yes** | [-0.25, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 prepend | 1% FPR | malware TPR, fit subset | -1.08 | 3.34 | [-1.44, -0.75] | 5/5 | no | [-2.69, +0.35] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 prepend | 0.1% FPR | malware TPR | +4.44 | 13.10 | [+4.02, +4.81] | 7/3 | **yes** | [-2.23, +11.29] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.03 | 0.06 | [+0.00, +0.07] | 6/3 | no | [-0.01, +0.09] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 prepend | 0.1% FPR | malware TPR, fit subset | -4.55 | 12.48 | [-5.31, -3.75] | 4/6 | no | [-16.81, +4.49] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 prepend | 1% FPR | malware TPR | -3.12 | 4.24 | [-3.32, -2.93] | 3/7 | **yes** | [-4.28, -2.10] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 prepend | 1% FPR | padded-benign FPR | -0.33 | 0.41 | [-0.43, -0.25] | 2/7 | **yes** | [-0.52, -0.20] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 prepend | 1% FPR | malware TPR, fit subset | -6.84 | 8.07 | [-7.53, -6.16] | 1/9 | **yes** | [-9.62, -3.49] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 prepend | 0.1% FPR | malware TPR | -1.22 | 10.92 | [-1.55, -0.90] | 7/3 | **yes** | [-6.20, +3.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 prepend | 0.1% FPR | padded-benign FPR | -0.02 | 0.04 | [-0.04, -0.00] | 4/5 | no | [-0.05, -0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 prepend | 0.1% FPR | malware TPR, fit subset | -10.55 | 9.88 | [-11.56, -9.57] | 2/8 | **yes** | [-22.27, +1.64] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 100 prepend | 1% FPR | malware TPR | -5.50 | 11.07 | [-5.69, -5.30] | 2/8 | **yes** | [-7.72, -3.63] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 100 prepend | 1% FPR | padded-benign FPR | -0.21 | 0.16 | [-0.28, -0.15] | 1/9 | **yes** | [-0.29, -0.13] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 100 prepend | 0.1% FPR | malware TPR | -0.37 | 1.89 | [-0.48, -0.24] | 4/6 | no | [-1.02, +0.28] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 200 prepend | 1% FPR | malware TPR | -2.86 | 3.42 | [-3.03, -2.71] | 2/8 | **yes** | [-4.87, -1.59] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 200 prepend | 1% FPR | padded-benign FPR | -0.09 | 0.20 | [-0.14, -0.04] | 2/8 | **yes** | [-0.14, -0.04] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 200 prepend | 0.1% FPR | malware TPR | +0.62 | 1.74 | [+0.50, +0.73] | 5/4 | no | [+0.04, +1.46] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 200 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 insert | 1% FPR | malware TPR | -1.28 | 2.47 | [-1.44, -1.12] | 2/8 | **yes** | [-2.90, -0.21] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 insert | 1% FPR | padded-benign FPR | -0.05 | 0.16 | [-0.12, +0.02] | 3/7 | no | [-0.15, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 insert | 1% FPR | malware TPR, fit subset | -0.56 | 2.94 | [-0.87, -0.25] | 4/6 | no | [-1.92, +0.87] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 insert | 0.1% FPR | malware TPR | +3.57 | 10.25 | [+3.18, +3.93] | 7/3 | **yes** | [-2.58, +9.95] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.03 | [-0.02, +0.03] | 6/3 | no | [-0.02, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 5 insert | 0.1% FPR | malware TPR, fit subset | +1.61 | 15.34 | [+1.03, +2.16] | 4/6 | no | [-4.98, +6.70] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 insert | 1% FPR | malware TPR | -2.14 | 3.58 | [-2.31, -1.98] | 1/9 | **yes** | [-3.40, -1.09] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 insert | 1% FPR | padded-benign FPR | -0.09 | 0.17 | [-0.17, -0.02] | 3/6 | no | [-0.19, -0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 insert | 1% FPR | malware TPR, fit subset | -1.57 | 3.27 | [-1.90, -1.22] | 3/7 | **yes** | [-2.95, -0.40] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 insert | 0.1% FPR | malware TPR | +2.76 | 10.45 | [+2.33, +3.18] | 6/4 | no | [-5.16, +10.84] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.04 | [-0.02, +0.03] | 6/3 | no | [-0.03, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 20 insert | 0.1% FPR | malware TPR, fit subset | -1.84 | 13.78 | [-2.48, -1.22] | 4/6 | no | [-11.18, +5.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 insert | 1% FPR | malware TPR | -2.73 | 3.88 | [-2.90, -2.55] | 2/8 | **yes** | [-3.97, -1.59] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 insert | 1% FPR | padded-benign FPR | -0.26 | 0.23 | [-0.34, -0.17] | 1/9 | **yes** | [-0.39, -0.15] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 insert | 1% FPR | malware TPR, fit subset | -4.99 | 4.15 | [-5.64, -4.35] | 0/10 | **yes** | [-7.77, -2.07] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 insert | 0.1% FPR | malware TPR | +2.69 | 10.50 | [+2.24, +3.11] | 6/4 | no | [-5.65, +10.21] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.03 | [-0.03, +0.03] | 4/3 | no | [-0.03, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 50 insert | 0.1% FPR | malware TPR, fit subset | -4.58 | 9.01 | [-5.27, -3.88] | 3/7 | **yes** | [-11.78, +3.40] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 100 insert | 1% FPR | malware TPR | -5.04 | 3.58 | [-5.29, -4.79] | 1/9 | **yes** | [-8.89, -2.04] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 100 insert | 1% FPR | padded-benign FPR | -0.12 | 0.16 | [-0.17, -0.06] | 3/7 | **yes** | [-0.19, -0.06] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 100 insert | 0.1% FPR | malware TPR | +5.01 | 12.51 | [+4.63, +5.39] | 6/4 | no | [-1.28, +12.26] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 100 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.04 | [-0.00, +0.03] | 6/3 | no | [-0.01, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 200 insert | 1% FPR | malware TPR | -4.76 | 4.50 | [-5.03, -4.51] | 2/8 | **yes** | [-7.61, -2.07] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 200 insert | 1% FPR | padded-benign FPR | -0.08 | 0.19 | [-0.14, -0.03] | 3/7 | **yes** | [-0.15, -0.02] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 200 insert | 0.1% FPR | malware TPR | +6.19 | 9.88 | [+5.81, +6.55] | 7/3 | **yes** | [+1.51, +12.23] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | random 200 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.00, +0.03] | 6/1 | no | [-0.00, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 prepend | 1% FPR | malware TPR | +16.83 | 5.54 | [+16.21, +17.47] | 10/0 | **yes** | [+7.24, +26.49] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 prepend | 1% FPR | padded-benign FPR | +0.59 | 0.24 | [+0.46, +0.74] | 10/0 | **yes** | [+0.41, +0.85] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 prepend | 1% FPR | malware TPR, fit subset | +30.82 | 3.70 | [+29.50, +32.17] | 10/0 | **yes** | [+14.35, +45.88] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 prepend | 0.1% FPR | malware TPR | +24.58 | 14.01 | [+23.92, +25.24] | 10/0 | **yes** | [+14.44, +33.31] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.03 | [+0.04, +0.13] | 10/0 | **yes** | [+0.04, +0.15] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +33.69 | 11.11 | [+32.51, +34.91] | 10/0 | **yes** | [+11.39, +48.62] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 prepend | 1% FPR | malware TPR | +26.11 | 6.25 | [+25.33, +26.83] | 10/0 | **yes** | [+14.35, +38.45] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 prepend | 1% FPR | padded-benign FPR | +1.07 | 0.26 | [+0.93, +1.24] | 10/0 | **yes** | [+0.78, +1.43] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 prepend | 1% FPR | malware TPR, fit subset | +52.02 | 4.72 | [+50.46, +53.47] | 10/0 | **yes** | [+31.29, +68.15] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 prepend | 0.1% FPR | malware TPR | +31.70 | 13.85 | [+31.06, +32.33] | 10/0 | **yes** | [+21.93, +40.40] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.03 | [+0.04, +0.15] | 10/0 | **yes** | [+0.03, +0.17] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +35.18 | 11.10 | [+33.90, +36.51] | 10/0 | **yes** | [+15.65, +53.56] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 prepend | 1% FPR | malware TPR | +39.64 | 9.57 | [+38.80, +40.44] | 10/0 | **yes** | [+25.33, +53.22] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 prepend | 1% FPR | padded-benign FPR | +1.12 | 0.49 | [+0.97, +1.27] | 10/0 | **yes** | [+0.80, +1.52] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 prepend | 1% FPR | malware TPR, fit subset | +51.29 | 7.94 | [+49.22, +53.21] | 10/0 | **yes** | [+27.05, +69.97] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 prepend | 0.1% FPR | malware TPR | +35.41 | 7.15 | [+34.64, +36.29] | 10/0 | **yes** | [+23.95, +45.72] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.03 | 0.03 | [+0.01, +0.06] | 10/0 | **yes** | [+0.01, +0.07] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +11.61 | 8.77 | [+10.49, +12.73] | 10/0 | **yes** | [+4.79, +21.24] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 100 prepend | 1% FPR | malware TPR | -3.31 | 12.05 | [-3.86, -2.72] | 5/5 | no | [-10.11, +3.13] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 100 prepend | 1% FPR | padded-benign FPR | +0.31 | 0.21 | [+0.26, +0.38] | 10/0 | **yes** | [+0.26, +0.37] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 100 prepend | 0.1% FPR | malware TPR | +3.96 | 1.28 | [+3.62, +4.29] | 10/0 | **yes** | [+1.67, +7.05] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 200 prepend | 1% FPR | malware TPR | +2.97 | 6.53 | [+2.45, +3.50] | 8/2 | **yes** | [-1.81, +8.60] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 200 prepend | 1% FPR | padded-benign FPR | +0.31 | 0.27 | [+0.25, +0.37] | 10/0 | **yes** | [+0.25, +0.38] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 200 prepend | 0.1% FPR | malware TPR | +3.61 | 1.56 | [+3.29, +3.92] | 10/0 | **yes** | [+1.49, +6.48] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 200 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 insert | 1% FPR | malware TPR | +13.97 | 4.76 | [+13.37, +14.54] | 10/0 | **yes** | [+5.77, +21.86] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 insert | 1% FPR | padded-benign FPR | +0.57 | 0.23 | [+0.44, +0.70] | 10/0 | **yes** | [+0.40, +0.78] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 insert | 1% FPR | malware TPR, fit subset | +24.54 | 3.86 | [+23.30, +25.73] | 10/0 | **yes** | [+12.10, +35.39] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 insert | 0.1% FPR | malware TPR | +23.78 | 13.22 | [+23.17, +24.40] | 10/0 | **yes** | [+14.86, +31.56] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 insert | 0.1% FPR | padded-benign FPR | +0.06 | 0.02 | [+0.03, +0.11] | 10/0 | **yes** | [+0.02, +0.12] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 5 insert | 0.1% FPR | malware TPR, fit subset | +31.70 | 10.24 | [+30.44, +32.97] | 10/0 | **yes** | [+10.62, +46.57] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 insert | 1% FPR | malware TPR | +25.93 | 6.03 | [+25.23, +26.65] | 10/0 | **yes** | [+14.56, +37.78] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 insert | 1% FPR | padded-benign FPR | +0.84 | 0.28 | [+0.71, +0.98] | 10/0 | **yes** | [+0.61, +1.13] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 insert | 1% FPR | malware TPR, fit subset | +49.35 | 2.96 | [+47.84, +50.88] | 10/0 | **yes** | [+28.53, +65.64] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 insert | 0.1% FPR | malware TPR | +27.97 | 10.56 | [+27.32, +28.59] | 10/0 | **yes** | [+19.01, +37.02] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 insert | 0.1% FPR | padded-benign FPR | +0.07 | 0.02 | [+0.03, +0.12] | 10/0 | **yes** | [+0.03, +0.14] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 20 insert | 0.1% FPR | malware TPR, fit subset | +33.45 | 7.08 | [+32.08, +34.90] | 10/0 | **yes** | [+13.54, +52.08] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 insert | 1% FPR | malware TPR | +37.66 | 6.61 | [+36.84, +38.49] | 10/0 | **yes** | [+23.30, +51.09] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 insert | 1% FPR | padded-benign FPR | +0.75 | 0.27 | [+0.61, +0.89] | 10/0 | **yes** | [+0.53, +1.04] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 insert | 1% FPR | malware TPR, fit subset | +49.99 | 4.95 | [+47.88, +52.19] | 10/0 | **yes** | [+23.09, +70.16] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 insert | 0.1% FPR | malware TPR | +34.35 | 7.77 | [+33.65, +35.09] | 10/0 | **yes** | [+23.60, +45.32] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.02, +0.08] | 9/0 | **yes** | [+0.01, +0.09] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 50 insert | 0.1% FPR | malware TPR, fit subset | +10.51 | 5.19 | [+9.43, +11.67] | 10/0 | **yes** | [+4.08, +19.00] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 100 insert | 1% FPR | malware TPR | +40.67 | 6.58 | [+39.89, +41.41] | 10/0 | **yes** | [+29.51, +52.82] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 100 insert | 1% FPR | padded-benign FPR | +0.43 | 0.18 | [+0.34, +0.54] | 10/0 | **yes** | [+0.31, +0.60] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 100 insert | 0.1% FPR | malware TPR | +32.41 | 6.98 | [+31.65, +33.22] | 10/0 | **yes** | [+21.37, +43.68] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 100 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.02, +0.07] | 8/0 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 200 insert | 1% FPR | malware TPR | +43.25 | 5.81 | [+42.45, +44.09] | 10/0 | **yes** | [+30.97, +54.27] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 200 insert | 1% FPR | padded-benign FPR | +0.45 | 0.24 | [+0.35, +0.54] | 10/0 | **yes** | [+0.33, +0.61] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 200 insert | 0.1% FPR | malware TPR | +25.99 | 6.02 | [+25.23, +26.78] | 10/0 | **yes** | [+14.86, +38.85] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | random 200 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.04] | 8/0 | **yes** | [+0.00, +0.04] | yes |

**Surrogate-chosen padding (ranks 1..k of the LightGBM or v2-PE ranking)** Thresholds: 1% and 0.1% FPR of each model's and seed's unedited April benign scores. Seeds 0-9, mean ± std.

| model | edit | malware TPR @1% | padded-benign FPR @1% | malware TPR @0.1% | padded-benign FPR @0.1% | malware that fit in 512 | TPR @1%, fit subset | TPR @0.1%, fit subset |
|---|---|---|---|---|---|---|---|---|
| v2-PE | lgbm 20 prepend | 10.2 ± 7.0 | 0.1 ± 0.4 | 1.6 ± 2.0 | 0.0 | 23.9% | 1.0 | 0.0 |
| v2-PE | lgbm 50 prepend | 3.3 ± 2.4 | 0.0 | 0.4 ± 1.1 | 0.0 | 15.4% | 0.0 | 0.0 |
| v2-PE | lgbm 100 prepend | 3.2 ± 2.4 | 0.0 | 0.7 ± 1.7 | 0.0 | 0.0% | n/a | n/a |
| v2-PE | lgbm 20 insert | 40.3 ± 6.5 | 0.2 ± 0.1 | 13.8 ± 4.7 | 0.0 ± 0.0 | 23.9% | 9.0 | 0.5 |
| v2-PE | lgbm 50 insert | 21.7 ± 4.7 | 0.1 ± 0.1 | 6.2 ± 3.9 | 0.0 | 15.4% | 0.0 | 0.0 |
| v2-PE | lgbm 100 insert | 12.4 ± 3.9 | 0.0 ± 0.1 | 3.1 ± 3.6 | 0.0 | 0.0% | n/a | n/a |
| v2-PE | v2pe 20 prepend | 2.7 ± 2.9 | 0.0 | 0.3 ± 0.7 | 0.0 | 14.9% | 0.0 | 0.0 |
| v2-PE | v2pe 50 prepend | 3.1 ± 3.3 | 0.0 | 0.4 ± 0.9 | 0.0 | 0.0% | n/a | n/a |
| v2-PE | v2pe 100 prepend | 3.1 ± 3.3 | 0.0 | 0.4 ± 0.9 | 0.0 | 0.0% | n/a | n/a |
| v2-PE | v2pe 20 insert | 17.3 ± 4.8 | 0.1 ± 0.1 | 5.3 ± 3.2 | 0.0 ± 0.0 | 14.9% | 0.0 | 0.0 |
| v2-PE | v2pe 50 insert | 7.7 ± 3.7 | 0.0 ± 0.1 | 1.8 ± 2.1 | 0.0 | 0.0% | n/a | n/a |
| v2-PE | v2pe 100 insert | 4.6 ± 3.3 | 0.0 ± 0.0 | 1.0 ± 1.5 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | lgbm 20 prepend | 72.3 ± 5.2 | 0.8 ± 0.5 | 46.8 ± 6.3 | 0.1 ± 0.0 | 23.9% | 61.6 | 26.4 |
| ATT+bal | lgbm 50 prepend | 36.5 ± 14.9 | 0.1 ± 0.1 | 5.2 ± 4.7 | 0.0 | 15.4% | 14.9 | 0.1 |
| ATT+bal | lgbm 100 prepend | 5.0 ± 1.8 | 0.0 | 1.5 ± 0.8 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | lgbm 20 insert | 69.6 ± 6.4 | 0.6 ± 0.3 | 39.0 ± 3.3 | 0.0 ± 0.0 | 23.9% | 51.6 | 16.6 |
| ATT+bal | lgbm 50 insert | 59.0 ± 5.9 | 0.3 ± 0.1 | 29.9 ± 3.2 | 0.0 ± 0.0 | 15.4% | 4.3 | 0.0 |
| ATT+bal | lgbm 100 insert | 46.4 ± 5.7 | 0.3 ± 0.4 | 22.3 ± 1.9 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal | v2pe 20 prepend | 23.8 ± 8.6 | 0.0 ± 0.0 | 1.2 ± 0.8 | 0.0 | 14.9% | 5.3 | 0.0 |
| ATT+bal | v2pe 50 prepend | 4.2 ± 1.4 | 0.0 | 1.1 ± 0.8 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | v2pe 100 prepend | 4.2 ± 1.4 | 0.0 | 1.1 ± 0.8 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | v2pe 20 insert | 51.9 ± 5.0 | 0.2 ± 0.1 | 24.0 ± 2.5 | 0.0 ± 0.0 | 14.9% | 1.5 | 0.0 |
| ATT+bal | v2pe 50 insert | 33.9 ± 5.4 | 0.1 ± 0.1 | 12.5 ± 1.6 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | v2pe 100 insert | 20.4 ± 3.6 | 0.0 ± 0.0 | 6.0 ± 1.4 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | lgbm 20 prepend | 45.1 ± 9.0 | 0.1 ± 0.1 | 12.3 ± 8.6 | 0.0 ± 0.0 | 23.9% | 10.3 | 0.3 |
| B (2L, no padding) | lgbm 50 prepend | 9.1 ± 10.9 | 0.0 ± 0.0 | 0.0 | 0.0 | 15.4% | 0.0 | 0.0 |
| B (2L, no padding) | lgbm 100 prepend | 8.0 ± 10.7 | 0.0 ± 0.0 | 0.0 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | lgbm 20 insert | 36.3 ± 4.6 | 0.1 ± 0.0 | 7.4 ± 4.6 | 0.0 | 23.9% | 4.5 | 0.1 |
| B (2L, no padding) | lgbm 50 insert | 15.5 ± 5.2 | 0.0 ± 0.0 | 1.4 ± 1.2 | 0.0 | 15.4% | 0.0 | 0.0 |
| B (2L, no padding) | lgbm 100 insert | 8.6 ± 3.4 | 0.0 | 0.3 ± 0.6 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | v2pe 20 prepend | 10.3 ± 13.0 | 0.0 ± 0.0 | 0.0 | 0.0 | 14.9% | 0.0 | 0.0 |
| B (2L, no padding) | v2pe 50 prepend | 6.8 ± 9.4 | 0.0 ± 0.0 | 0.0 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | v2pe 100 prepend | 1.8 ± 3.5 | 0.0 | 0.0 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | v2pe 20 insert | 14.4 ± 3.5 | 0.0 ± 0.0 | 1.6 ± 1.6 | 0.0 | 14.9% | 0.0 | 0.0 |
| B (2L, no padding) | v2pe 50 insert | 3.6 ± 2.0 | 0.0 | 0.1 ± 0.1 | 0.0 | 0.0% | n/a | n/a |
| B (2L, no padding) | v2pe 100 insert | 0.6 ± 0.8 | 0.0 | 0.0 ± 0.0 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | lgbm 20 prepend | 74.6 ± 2.3 | 0.8 ± 0.4 | 42.8 ± 8.6 | 0.1 ± 0.0 | 23.9% | 66.5 | 33.8 |
| ATT+bal-2L (A) | lgbm 50 prepend | 42.1 ± 7.0 | 0.1 ± 0.0 | 15.0 ± 7.1 | 0.0 | 15.4% | 25.2 | 1.1 |
| ATT+bal-2L (A) | lgbm 100 prepend | 9.2 ± 8.4 | 0.0 ± 0.0 | 3.4 ± 2.1 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | lgbm 20 insert | 73.4 ± 2.4 | 0.5 ± 0.3 | 36.2 ± 8.2 | 0.0 ± 0.0 | 23.9% | 61.3 | 22.2 |
| ATT+bal-2L (A) | lgbm 50 insert | 60.1 ± 4.3 | 0.2 ± 0.1 | 27.6 ± 9.3 | 0.0 ± 0.0 | 15.4% | 7.1 | 0.3 |
| ATT+bal-2L (A) | lgbm 100 insert | 47.2 ± 5.0 | 0.1 ± 0.1 | 17.0 ± 6.7 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | v2pe 20 prepend | 30.2 ± 6.4 | 0.0 ± 0.0 | 11.3 ± 8.6 | 0.0 ± 0.0 | 14.9% | 9.6 | 0.5 |
| ATT+bal-2L (A) | v2pe 50 prepend | 10.8 ± 14.3 | 0.0 ± 0.0 | 2.2 ± 2.4 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | v2pe 100 prepend | 9.3 ± 12.1 | 0.0 ± 0.0 | 0.7 ± 1.6 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | v2pe 20 insert | 53.7 ± 3.2 | 0.2 ± 0.0 | 23.9 ± 8.2 | 0.0 ± 0.0 | 14.9% | 2.1 | 0.0 |
| ATT+bal-2L (A) | v2pe 50 insert | 36.1 ± 4.7 | 0.1 ± 0.0 | 12.8 ± 5.1 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L (A) | v2pe 100 insert | 18.2 ± 5.3 | 0.0 ± 0.0 | 4.7 ± 3.4 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | lgbm 20 prepend | 71.6 ± 4.7 | 0.7 ± 0.5 | 48.2 ± 8.2 | 0.1 ± 0.0 | 23.9% | 60.7 | 27.9 |
| ATT+bal-2L, round 2 (A2) | lgbm 50 prepend | 37.1 ± 9.5 | 0.0 ± 0.0 | 11.3 ± 5.7 | 0.0 | 15.4% | 10.7 | 0.9 |
| ATT+bal-2L, round 2 (A2) | lgbm 100 prepend | 6.0 ± 1.5 | 0.0 ± 0.0 | 3.0 ± 1.5 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | lgbm 20 insert | 69.0 ± 6.4 | 0.5 ± 0.4 | 39.3 ± 5.9 | 0.0 ± 0.0 | 23.9% | 51.9 | 21.0 |
| ATT+bal-2L, round 2 (A2) | lgbm 50 insert | 57.9 ± 5.4 | 0.2 ± 0.1 | 33.2 ± 6.1 | 0.0 ± 0.0 | 15.4% | 3.6 | 0.0 |
| ATT+bal-2L, round 2 (A2) | lgbm 100 insert | 44.4 ± 4.4 | 0.2 ± 0.3 | 24.0 ± 4.9 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | v2pe 20 prepend | 25.0 ± 5.2 | 0.0 ± 0.0 | 6.4 ± 4.6 | 0.0 | 14.9% | 4.0 | 0.2 |
| ATT+bal-2L, round 2 (A2) | v2pe 50 prepend | 5.1 ± 0.2 | 0.0 | 2.2 ± 1.2 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | v2pe 100 prepend | 5.2 ± 1.9 | 0.0 ± 0.0 | 1.4 ± 1.4 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | v2pe 20 insert | 50.4 ± 4.3 | 0.1 ± 0.0 | 27.2 ± 5.1 | 0.0 ± 0.0 | 14.9% | 0.7 | 0.0 |
| ATT+bal-2L, round 2 (A2) | v2pe 50 insert | 31.9 ± 3.7 | 0.1 ± 0.0 | 16.1 ± 4.4 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-2L, round 2 (A2) | v2pe 100 insert | 18.5 ± 2.2 | 0.0 ± 0.0 | 8.0 ± 3.2 | 0.0 ± 0.0 | 0.0% | n/a | n/a |

**Surrogate-chosen padding (ranks 1..k of the LightGBM or v2-PE ranking): A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; meets rule = CI excludes 0 and ≥ 7 of 10 seeds with the same sign (descriptive: none of these robustness comparisons is a pre-registered claim).**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | meets rule (descriptive) | CI (cluster bootstrap) | meets rule, cluster (descriptive) |
|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal-2L (A) − ATT+bal | lgbm 20 prepend | 1% FPR | malware TPR | +2.28 | 4.34 | [+2.09, +2.48] | 6/4 | no | [+0.43, +4.84] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.05 | 0.24 | [-0.01, +0.11] | 5/5 | no | [-0.02, +0.13] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +4.84 | 9.02 | [+4.49, +5.23] | 9/1 | **yes** | [+1.96, +7.62] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 prepend | 0.1% FPR | malware TPR | -4.01 | 11.44 | [-4.40, -3.57] | 3/7 | **yes** | [-11.34, +3.50] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.05 | [-0.04, +0.01] | 4/6 | no | [-0.05, +0.01] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +7.34 | 14.78 | [+6.53, +8.18] | 7/3 | **yes** | [-3.19, +21.11] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 prepend | 1% FPR | malware TPR | +5.54 | 13.64 | [+5.21, +5.84] | 6/4 | no | [-0.16, +10.68] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 prepend | 1% FPR | padded-benign FPR | -0.02 | 0.05 | [-0.04, -0.00] | 3/7 | **yes** | [-0.05, +0.00] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +10.32 | 16.72 | [+9.57, +11.12] | 6/4 | no | [-0.65, +19.70] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 prepend | 0.1% FPR | malware TPR | +9.81 | 8.41 | [+9.45, +10.20] | 9/1 | **yes** | [+4.58, +16.85] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +1.02 | 1.31 | [+0.74, +1.32] | 6/1 | no | [+0.20, +2.90] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 100 prepend | 1% FPR | malware TPR | +4.14 | 9.70 | [+4.00, +4.29] | 8/1 | **yes** | [+2.59, +5.69] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 100 prepend | 0.1% FPR | malware TPR | +1.92 | 2.23 | [+1.72, +2.11] | 8/2 | **yes** | [+0.58, +3.93] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 insert | 1% FPR | malware TPR | +3.78 | 4.88 | [+3.56, +4.01] | 8/2 | **yes** | [+1.01, +7.95] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.03 | 0.28 | [-0.09, +0.02] | 4/6 | no | [-0.11, +0.04] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +9.75 | 9.08 | [+9.13, +10.43] | 9/1 | **yes** | [+1.96, +19.81] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 insert | 0.1% FPR | malware TPR | -2.89 | 10.10 | [-3.33, -2.40] | 3/7 | **yes** | [-12.64, +6.61] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.04 | [-0.00, +0.04] | 6/2 | no | [-0.01, +0.05] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +5.67 | 13.24 | [+5.20, +6.18] | 6/4 | no | [+1.75, +8.33] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 insert | 1% FPR | malware TPR | +1.11 | 6.33 | [+0.93, +1.29] | 7/3 | **yes** | [+0.13, +2.20] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 insert | 1% FPR | padded-benign FPR | -0.08 | 0.14 | [-0.12, -0.05] | 3/7 | **yes** | [-0.13, -0.04] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +2.75 | 2.99 | [+2.33, +3.19] | 8/2 | **yes** | [+1.26, +4.72] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 insert | 0.1% FPR | malware TPR | -2.27 | 10.74 | [-2.71, -1.79] | 4/6 | no | [-11.20, +5.06] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.03 | [-0.01, +0.02] | 4/1 | no | [-0.01, +0.03] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.28 | 0.47 | [+0.16, +0.42] | 5/0 | no | [+0.02, +1.02] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 100 insert | 1% FPR | malware TPR | +0.83 | 7.45 | [+0.63, +1.05] | 6/4 | no | [-2.73, +4.08] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 100 insert | 1% FPR | padded-benign FPR | -0.19 | 0.41 | [-0.24, -0.15] | 3/7 | **yes** | [-0.28, -0.12] | yes |
| ATT+bal-2L (A) − ATT+bal | lgbm 100 insert | 0.1% FPR | malware TPR | -5.28 | 7.86 | [-5.83, -4.67] | 2/8 | **yes** | [-15.89, +3.74] | no |
| ATT+bal-2L (A) − ATT+bal | lgbm 100 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.02] | 3/1 | no | [-0.00, +0.02] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 prepend | 1% FPR | malware TPR | +6.43 | 11.10 | [+6.21, +6.67] | 7/3 | **yes** | [+3.41, +10.36] | yes |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.04 | [+0.00, +0.03] | 6/2 | no | [+0.00, +0.04] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +4.29 | 11.58 | [+3.93, +4.65] | 7/2 | **yes** | [+0.12, +7.13] | yes |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 prepend | 0.1% FPR | malware TPR | +10.16 | 8.50 | [+9.77, +10.55] | 8/2 | **yes** | [+3.23, +17.39] | yes |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.02] | 3/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.51 | 0.82 | [+0.35, +0.68] | 6/0 | no | [+0.08, +1.60] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 50 prepend | 1% FPR | malware TPR | +6.63 | 14.62 | [+6.48, +6.76] | 6/2 | no | [+4.39, +8.75] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.05 | [+0.01, +0.02] | 1/0 | no | [+0.01, +0.03] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 50 prepend | 0.1% FPR | malware TPR | +1.08 | 2.99 | [+0.93, +1.22] | 5/5 | no | [+0.09, +2.31] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 100 prepend | 1% FPR | malware TPR | +5.06 | 12.45 | [+4.91, +5.20] | 5/2 | no | [+2.74, +7.28] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 100 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.04 | [+0.00, +0.02] | 1/0 | no | [+0.00, +0.02] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 100 prepend | 0.1% FPR | malware TPR | -0.42 | 2.11 | [-0.54, -0.30] | 3/7 | **yes** | [-1.28, +0.28] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 insert | 1% FPR | malware TPR | +1.74 | 5.14 | [+1.55, +1.92] | 6/4 | no | [+0.20, +3.31] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 insert | 1% FPR | padded-benign FPR | -0.03 | 0.07 | [-0.05, -0.00] | 4/6 | no | [-0.06, +0.00] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 insert | 1% FPR | malware TPR, fit subset | +0.67 | 1.20 | [+0.48, +0.87] | 8/2 | **yes** | [+0.20, +1.24] | yes |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 insert | 0.1% FPR | malware TPR | -0.09 | 8.45 | [-0.55, +0.41] | 5/5 | no | [-7.13, +5.66] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [+0.00, +0.02] | 5/2 | no | [-0.00, +0.02] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [+0.00, +0.03] | 1/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 50 insert | 1% FPR | malware TPR | +2.14 | 5.36 | [+1.91, +2.39] | 7/3 | **yes** | [-1.14, +5.39] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 50 insert | 1% FPR | padded-benign FPR | -0.01 | 0.05 | [-0.04, +0.01] | 2/8 | no | [-0.04, +0.00] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 50 insert | 0.1% FPR | malware TPR | +0.31 | 5.22 | [-0.16, +0.77] | 5/5 | no | [-4.85, +4.91] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.03] | 6/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 100 insert | 1% FPR | malware TPR | -2.20 | 5.03 | [-2.40, -1.98] | 2/8 | **yes** | [-5.66, +0.14] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 100 insert | 1% FPR | padded-benign FPR | -0.00 | 0.03 | [-0.03, +0.02] | 2/6 | no | [-0.03, +0.02] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 100 insert | 0.1% FPR | malware TPR | -1.25 | 3.73 | [-1.58, -0.90] | 1/9 | **yes** | [-3.92, +1.77] | no |
| ATT+bal-2L (A) − ATT+bal | v2pe 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 2/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L (A) − v2-PE | lgbm 20 prepend | 1% FPR | malware TPR | +64.39 | 8.37 | [+63.50, +65.16] | 10/0 | **yes** | [+51.65, +73.99] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.69 | 0.63 | [+0.56, +0.84] | 9/1 | **yes** | [+0.47, +0.98] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +65.53 | 3.91 | [+63.73, +67.31] | 10/0 | **yes** | [+39.09, +80.77] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 prepend | 0.1% FPR | malware TPR | +41.19 | 8.85 | [+40.47, +41.96] | 10/0 | **yes** | [+27.79, +50.69] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.06 | 0.04 | [+0.03, +0.11] | 9/0 | **yes** | [+0.02, +0.12] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +33.78 | 15.98 | [+32.48, +35.16] | 10/0 | **yes** | [+14.14, +47.96] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 prepend | 1% FPR | malware TPR | +38.77 | 9.11 | [+37.92, +39.59] | 10/0 | **yes** | [+26.05, +50.11] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.05 | 0.03 | [+0.02, +0.10] | 10/0 | **yes** | [+0.02, +0.12] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +25.24 | 19.16 | [+23.77, +26.75] | 10/0 | **yes** | [+7.04, +37.62] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 prepend | 0.1% FPR | malware TPR | +14.60 | 7.20 | [+14.07, +15.12] | 10/0 | **yes** | [+6.46, +24.42] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − v2-PE | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +1.13 | 1.28 | [+0.83, +1.45] | 8/0 | **yes** | [+0.23, +3.19] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 100 prepend | 1% FPR | malware TPR | +5.98 | 8.12 | [+5.72, +6.23] | 9/1 | **yes** | [+3.96, +8.59] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L (A) − v2-PE | lgbm 100 prepend | 0.1% FPR | malware TPR | +2.66 | 2.55 | [+2.43, +2.89] | 8/2 | **yes** | [+1.13, +4.73] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − v2-PE | lgbm 20 insert | 1% FPR | malware TPR | +33.12 | 8.36 | [+32.38, +33.89] | 10/0 | **yes** | [+20.26, +45.51] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 insert | 1% FPR | padded-benign FPR | +0.30 | 0.32 | [+0.20, +0.40] | 9/1 | **yes** | [+0.16, +0.47] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +52.29 | 8.72 | [+50.72, +54.02] | 10/0 | **yes** | [+27.96, +68.49] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 insert | 0.1% FPR | malware TPR | +22.39 | 7.62 | [+21.70, +23.08] | 10/0 | **yes** | [+11.22, +30.92] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.03 | [+0.01, +0.06] | 8/1 | **yes** | [+0.00, +0.07] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +21.78 | 11.01 | [+20.53, +23.07] | 10/0 | **yes** | [+6.44, +40.05] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 insert | 1% FPR | malware TPR | +38.46 | 7.98 | [+37.65, +39.24] | 10/0 | **yes** | [+23.64, +51.25] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 insert | 1% FPR | padded-benign FPR | +0.15 | 0.13 | [+0.08, +0.24] | 8/2 | **yes** | [+0.07, +0.27] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +7.05 | 4.09 | [+6.04, +8.05] | 10/0 | **yes** | [+3.01, +14.86] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 insert | 0.1% FPR | malware TPR | +21.37 | 8.70 | [+20.77, +21.98] | 10/0 | **yes** | [+11.23, +30.17] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.01, +0.04] | 7/0 | **yes** | [+0.01, +0.05] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.28 | 0.47 | [+0.16, +0.42] | 5/0 | no | [+0.02, +1.02] | no |
| ATT+bal-2L (A) − v2-PE | lgbm 100 insert | 1% FPR | malware TPR | +34.81 | 7.46 | [+33.94, +35.63] | 10/0 | **yes** | [+20.36, +48.86] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 100 insert | 1% FPR | padded-benign FPR | +0.11 | 0.09 | [+0.05, +0.18] | 9/1 | **yes** | [+0.04, +0.22] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 100 insert | 0.1% FPR | malware TPR | +13.91 | 5.63 | [+13.40, +14.42] | 10/0 | **yes** | [+6.10, +23.02] | yes |
| ATT+bal-2L (A) − v2-PE | lgbm 100 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.02] | 4/0 | no | [+0.00, +0.02] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 20 prepend | 1% FPR | malware TPR | +27.51 | 8.59 | [+26.76, +28.29] | 10/0 | **yes** | [+12.38, +41.89] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.05 | 0.03 | [+0.02, +0.09] | 10/0 | **yes** | [+0.01, +0.12] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +9.59 | 12.62 | [+8.59, +10.55] | 10/0 | **yes** | [+4.53, +15.72] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 20 prepend | 0.1% FPR | malware TPR | +10.99 | 8.51 | [+10.57, +11.41] | 9/0 | **yes** | [+4.03, +18.32] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.02] | 3/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.51 | 0.83 | [+0.35, +0.70] | 6/0 | no | [+0.08, +1.62] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 50 prepend | 1% FPR | malware TPR | +7.73 | 13.70 | [+7.51, +7.96] | 8/2 | **yes** | [+5.26, +10.29] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.05 | [+0.01, +0.02] | 1/0 | no | [+0.01, +0.03] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 50 prepend | 0.1% FPR | malware TPR | +1.76 | 1.75 | [+1.64, +1.88] | 7/0 | **yes** | [+0.91, +2.90] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 100 prepend | 1% FPR | malware TPR | +6.16 | 11.66 | [+5.96, +6.38] | 8/2 | **yes** | [+3.91, +8.49] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 100 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.04 | [+0.00, +0.02] | 1/0 | no | [+0.00, +0.02] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 100 prepend | 0.1% FPR | malware TPR | +0.26 | 1.11 | [+0.22, +0.30] | 2/1 | no | [+0.01, +0.63] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 20 insert | 1% FPR | malware TPR | +36.39 | 7.37 | [+35.55, +37.19] | 10/0 | **yes** | [+22.37, +48.72] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 20 insert | 1% FPR | padded-benign FPR | +0.06 | 0.10 | [+0.01, +0.13] | 6/4 | no | [+0.00, +0.15] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 20 insert | 1% FPR | malware TPR, fit subset | +2.13 | 2.10 | [+1.68, +2.57] | 9/1 | **yes** | [+0.64, +5.40] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 20 insert | 0.1% FPR | malware TPR | +18.62 | 8.54 | [+18.01, +19.23] | 10/0 | **yes** | [+9.85, +26.93] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [-0.00, +0.03] | 6/1 | no | [-0.01, +0.04] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [+0.00, +0.03] | 1/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 50 insert | 1% FPR | malware TPR | +28.43 | 7.66 | [+27.69, +29.20] | 10/0 | **yes** | [+17.76, +38.16] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 50 insert | 1% FPR | padded-benign FPR | +0.08 | 0.07 | [+0.02, +0.15] | 9/1 | **yes** | [+0.02, +0.17] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 50 insert | 0.1% FPR | malware TPR | +11.02 | 4.71 | [+10.55, +11.56] | 10/0 | **yes** | [+5.09, +20.17] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.03] | 6/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − v2-PE | v2pe 100 insert | 1% FPR | malware TPR | +13.64 | 7.08 | [+13.05, +14.20] | 9/1 | **yes** | [+6.68, +23.06] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 100 insert | 1% FPR | padded-benign FPR | +0.02 | 0.02 | [-0.00, +0.05] | 7/1 | no | [+0.00, +0.06] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 100 insert | 0.1% FPR | malware TPR | +3.72 | 2.33 | [+3.39, +4.04] | 9/1 | **yes** | [+0.21, +10.20] | yes |
| ATT+bal-2L (A) − v2-PE | v2pe 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 2/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 prepend | 1% FPR | malware TPR | +29.49 | 8.58 | [+28.72, +30.28] | 10/0 | **yes** | [+16.73, +42.77] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.71 | 0.43 | [+0.58, +0.85] | 10/0 | **yes** | [+0.46, +1.06] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +56.21 | 6.51 | [+54.52, +57.91] | 10/0 | **yes** | [+30.78, +73.72] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 prepend | 0.1% FPR | malware TPR | +30.53 | 14.20 | [+29.88, +31.17] | 10/0 | **yes** | [+18.42, +41.80] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.06 | 0.03 | [+0.03, +0.10] | 9/1 | **yes** | [+0.02, +0.11] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +33.44 | 16.25 | [+32.14, +34.81] | 10/0 | **yes** | [+13.80, +47.66] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 prepend | 1% FPR | malware TPR | +32.96 | 13.01 | [+32.15, +33.75] | 10/0 | **yes** | [+22.01, +42.97] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.05 | 0.03 | [+0.02, +0.10] | 10/0 | **yes** | [+0.01, +0.11] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +25.24 | 19.16 | [+23.77, +26.75] | 10/0 | **yes** | [+7.04, +37.62] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 prepend | 0.1% FPR | malware TPR | +15.04 | 7.09 | [+14.49, +15.57] | 10/0 | **yes** | [+6.80, +24.95] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +1.13 | 1.28 | [+0.83, +1.45] | 8/0 | **yes** | [+0.23, +3.19] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 100 prepend | 1% FPR | malware TPR | +1.19 | 14.80 | [+0.68, +1.70] | 7/3 | **yes** | [-4.98, +7.02] | no |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.01 | [-0.00, +0.01] | 1/1 | no | [-0.00, +0.01] | no |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 100 prepend | 0.1% FPR | malware TPR | +3.37 | 2.08 | [+3.09, +3.67] | 9/0 | **yes** | [+1.43, +6.05] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 insert | 1% FPR | malware TPR | +37.08 | 3.75 | [+36.23, +37.90] | 10/0 | **yes** | [+22.13, +51.76] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 insert | 1% FPR | padded-benign FPR | +0.48 | 0.25 | [+0.37, +0.58] | 10/0 | **yes** | [+0.32, +0.67] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +56.81 | 3.53 | [+55.09, +58.61] | 10/0 | **yes** | [+29.85, +73.97] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 insert | 0.1% FPR | malware TPR | +28.78 | 10.14 | [+28.19, +29.36] | 10/0 | **yes** | [+19.69, +35.81] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.01, +0.07] | 9/0 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +22.16 | 11.01 | [+20.90, +23.48] | 10/0 | **yes** | [+6.62, +40.94] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 insert | 1% FPR | malware TPR | +44.65 | 6.79 | [+43.90, +45.45] | 10/0 | **yes** | [+30.92, +57.69] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 insert | 1% FPR | padded-benign FPR | +0.22 | 0.06 | [+0.14, +0.32] | 10/0 | **yes** | [+0.12, +0.36] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +7.06 | 4.08 | [+6.05, +8.06] | 10/0 | **yes** | [+3.01, +14.89] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 insert | 0.1% FPR | malware TPR | +26.22 | 9.25 | [+25.60, +26.87] | 10/0 | **yes** | [+16.38, +35.19] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.01, +0.04] | 7/0 | **yes** | [+0.01, +0.05] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.28 | 0.47 | [+0.16, +0.42] | 5/0 | no | [+0.02, +1.02] | no |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 100 insert | 1% FPR | malware TPR | +38.59 | 5.65 | [+37.70, +39.47] | 10/0 | **yes** | [+25.04, +53.16] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 100 insert | 1% FPR | padded-benign FPR | +0.14 | 0.05 | [+0.08, +0.21] | 10/0 | **yes** | [+0.07, +0.26] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 100 insert | 0.1% FPR | malware TPR | +16.69 | 6.71 | [+16.15, +17.21] | 10/0 | **yes** | [+8.66, +26.29] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | lgbm 100 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.02] | 4/0 | no | [+0.00, +0.02] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 prepend | 1% FPR | malware TPR | +19.93 | 15.79 | [+19.12, +20.72] | 9/1 | **yes** | [+4.18, +35.60] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.04 | 0.04 | [+0.01, +0.08] | 9/0 | **yes** | [+0.01, +0.11] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +9.59 | 12.62 | [+8.59, +10.55] | 10/0 | **yes** | [+4.53, +15.72] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 prepend | 0.1% FPR | malware TPR | +11.33 | 8.57 | [+10.91, +11.77] | 9/0 | **yes** | [+4.46, +18.64] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.02] | 3/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.51 | 0.83 | [+0.35, +0.70] | 6/0 | no | [+0.08, +1.62] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 50 prepend | 1% FPR | malware TPR | +4.03 | 19.14 | [+3.60, +4.46] | 6/4 | no | [-1.53, +8.94] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.05 | [+0.01, +0.02] | 1/1 | no | [+0.01, +0.03] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 50 prepend | 0.1% FPR | malware TPR | +2.19 | 2.40 | [+2.05, +2.33] | 7/0 | **yes** | [+1.19, +3.50] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 100 prepend | 1% FPR | malware TPR | +7.44 | 13.19 | [+7.06, +7.81] | 7/2 | **yes** | [+4.18, +11.23] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 100 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.04 | [+0.00, +0.02] | 1/0 | no | [+0.00, +0.02] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 100 prepend | 0.1% FPR | malware TPR | +0.69 | 1.64 | [+0.63, +0.75] | 3/0 | no | [+0.30, +1.23] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 insert | 1% FPR | malware TPR | +39.30 | 4.38 | [+38.45, +40.08] | 10/0 | **yes** | [+25.77, +52.58] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 insert | 1% FPR | padded-benign FPR | +0.15 | 0.05 | [+0.09, +0.23] | 10/0 | **yes** | [+0.07, +0.27] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 insert | 1% FPR | malware TPR, fit subset | +2.15 | 2.09 | [+1.70, +2.58] | 9/0 | **yes** | [+0.65, +5.43] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 insert | 0.1% FPR | malware TPR | +22.26 | 8.17 | [+21.69, +22.85] | 10/0 | **yes** | [+14.23, +30.28] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.03] | 6/0 | no | [+0.00, +0.04] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [+0.00, +0.03] | 1/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 50 insert | 1% FPR | malware TPR | +32.51 | 4.56 | [+31.71, +33.35] | 10/0 | **yes** | [+22.87, +41.52] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 50 insert | 1% FPR | padded-benign FPR | +0.11 | 0.04 | [+0.05, +0.18] | 10/0 | **yes** | [+0.04, +0.20] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 50 insert | 0.1% FPR | malware TPR | +12.78 | 5.05 | [+12.29, +13.31] | 10/0 | **yes** | [+6.90, +22.20] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.03] | 6/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 100 insert | 1% FPR | malware TPR | +17.68 | 5.02 | [+17.06, +18.32] | 10/0 | **yes** | [+10.06, +27.49] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 100 insert | 1% FPR | padded-benign FPR | +0.03 | 0.02 | [+0.01, +0.06] | 8/0 | **yes** | [+0.01, +0.07] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 100 insert | 0.1% FPR | malware TPR | +4.71 | 3.36 | [+4.39, +5.03] | 10/0 | **yes** | [+1.09, +11.55] | yes |
| ATT+bal-2L (A) − B (2L, no padding) | v2pe 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 2/0 | no | [+0.00, +0.01] | no |
| B (2L, no padding) − ATT+bal | lgbm 20 prepend | 1% FPR | malware TPR | -27.20 | 10.49 | [-28.01, -26.46] | 0/10 | **yes** | [-40.16, -14.59] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 prepend | 1% FPR | padded-benign FPR | -0.66 | 0.49 | [-0.77, -0.54] | 0/10 | **yes** | [-0.99, -0.42] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | -51.36 | 10.57 | [-53.05, -49.72] | 0/10 | **yes** | [-67.98, -26.35] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 prepend | 0.1% FPR | malware TPR | -34.54 | 11.07 | [-35.20, -33.83] | 0/10 | **yes** | [-43.73, -22.69] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | -0.07 | 0.03 | [-0.13, -0.03] | 0/10 | **yes** | [-0.14, -0.02] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | -26.10 | 4.18 | [-27.64, -24.57] | 0/10 | **yes** | [-48.98, -6.76] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 prepend | 1% FPR | malware TPR | -27.42 | 23.06 | [-28.12, -26.77] | 2/8 | **yes** | [-36.67, -17.03] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 prepend | 1% FPR | padded-benign FPR | -0.07 | 0.06 | [-0.11, -0.04] | 0/9 | **yes** | [-0.13, -0.03] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | -14.92 | 16.99 | [-15.99, -13.86] | 0/10 | **yes** | [-20.60, -7.17] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 prepend | 0.1% FPR | malware TPR | -5.23 | 4.74 | [-5.52, -4.91] | 0/8 | **yes** | [-10.42, -1.69] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | -0.10 | 0.18 | [-0.22, -0.03] | 0/7 | **yes** | [-0.33, -0.01] | yes |
| B (2L, no padding) − ATT+bal | lgbm 100 prepend | 1% FPR | malware TPR | +2.96 | 10.82 | [+2.47, +3.43] | 6/4 | no | [-2.76, +9.67] | no |
| B (2L, no padding) − ATT+bal | lgbm 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | lgbm 100 prepend | 0.1% FPR | malware TPR | -1.46 | 0.79 | [-1.66, -1.26] | 0/8 | **yes** | [-3.10, -0.43] | yes |
| B (2L, no padding) − ATT+bal | lgbm 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | lgbm 20 insert | 1% FPR | malware TPR | -33.29 | 5.25 | [-34.08, -32.55] | 0/10 | **yes** | [-46.65, -19.86] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.51 | 0.25 | [-0.61, -0.40] | 0/10 | **yes** | [-0.72, -0.34] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 insert | 1% FPR | malware TPR, fit subset | -47.06 | 11.29 | [-48.66, -45.64] | 0/10 | **yes** | [-61.51, -25.47] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 insert | 0.1% FPR | malware TPR | -31.67 | 5.55 | [-32.40, -30.92] | 0/10 | **yes** | [-42.72, -21.40] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.02 | [-0.05, -0.00] | 0/9 | **yes** | [-0.05, -0.00] | yes |
| B (2L, no padding) − ATT+bal | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | -16.49 | 4.06 | [-17.67, -15.24] | 0/10 | **yes** | [-33.22, -2.14] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 insert | 1% FPR | malware TPR | -43.54 | 7.16 | [-44.31, -42.74] | 0/10 | **yes** | [-56.16, -29.76] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 insert | 1% FPR | padded-benign FPR | -0.30 | 0.15 | [-0.40, -0.22] | 0/10 | **yes** | [-0.46, -0.18] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 insert | 1% FPR | malware TPR, fit subset | -4.31 | 3.17 | [-5.07, -3.56] | 0/10 | **yes** | [-10.48, -1.34] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 insert | 0.1% FPR | malware TPR | -28.49 | 3.54 | [-29.24, -27.73] | 0/10 | **yes** | [-41.24, -16.47] | yes |
| B (2L, no padding) − ATT+bal | lgbm 50 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.03, -0.00] | 0/6 | no | [-0.03, -0.00] | no |
| B (2L, no padding) − ATT+bal | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | lgbm 100 insert | 1% FPR | malware TPR | -37.76 | 6.36 | [-38.61, -36.92] | 0/10 | **yes** | [-50.49, -24.56] | yes |
| B (2L, no padding) − ATT+bal | lgbm 100 insert | 1% FPR | padded-benign FPR | -0.34 | 0.40 | [-0.42, -0.26] | 0/10 | **yes** | [-0.48, -0.23] | yes |
| B (2L, no padding) − ATT+bal | lgbm 100 insert | 0.1% FPR | malware TPR | -21.97 | 2.13 | [-22.74, -21.22] | 0/10 | **yes** | [-35.12, -10.38] | yes |
| B (2L, no padding) − ATT+bal | lgbm 100 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.01 | [-0.01, +0.00] | 0/2 | no | [-0.01, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 20 prepend | 1% FPR | malware TPR | -13.50 | 17.29 | [-14.20, -12.77] | 3/7 | **yes** | [-26.31, -0.06] | yes |
| B (2L, no padding) − ATT+bal | v2pe 20 prepend | 1% FPR | padded-benign FPR | -0.03 | 0.03 | [-0.06, -0.00] | 1/7 | **yes** | [-0.07, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | -5.30 | 4.22 | [-6.06, -4.51] | 0/9 | **yes** | [-12.61, -1.72] | yes |
| B (2L, no padding) − ATT+bal | v2pe 20 prepend | 0.1% FPR | malware TPR | -1.17 | 0.83 | [-1.34, -1.01] | 0/8 | **yes** | [-2.55, -0.33] | yes |
| B (2L, no padding) − ATT+bal | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | -0.01 | 0.02 | [-0.02, +0.00] | 0/1 | no | [-0.03, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 50 prepend | 1% FPR | malware TPR | +2.59 | 10.17 | [+2.17, +3.03] | 5/5 | no | [-2.23, +8.39] | no |
| B (2L, no padding) − ATT+bal | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 50 prepend | 0.1% FPR | malware TPR | -1.11 | 0.83 | [-1.27, -0.95] | 0/8 | **yes** | [-2.43, -0.31] | yes |
| B (2L, no padding) − ATT+bal | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 100 prepend | 1% FPR | malware TPR | -2.38 | 3.84 | [-2.78, -2.00] | 3/7 | **yes** | [-6.58, +1.39] | no |
| B (2L, no padding) − ATT+bal | v2pe 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 100 prepend | 0.1% FPR | malware TPR | -1.11 | 0.83 | [-1.27, -0.95] | 0/8 | **yes** | [-2.43, -0.31] | yes |
| B (2L, no padding) − ATT+bal | v2pe 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 20 insert | 1% FPR | malware TPR | -37.56 | 5.54 | [-38.34, -36.75] | 0/10 | **yes** | [-49.87, -24.53] | yes |
| B (2L, no padding) − ATT+bal | v2pe 20 insert | 1% FPR | padded-benign FPR | -0.18 | 0.09 | [-0.26, -0.12] | 0/10 | **yes** | [-0.29, -0.10] | yes |
| B (2L, no padding) − ATT+bal | v2pe 20 insert | 1% FPR | malware TPR, fit subset | -1.48 | 1.40 | [-1.83, -1.11] | 0/8 | **yes** | [-4.27, -0.22] | yes |
| B (2L, no padding) − ATT+bal | v2pe 20 insert | 0.1% FPR | malware TPR | -22.34 | 2.77 | [-23.07, -21.67] | 0/10 | **yes** | [-33.17, -12.32] | yes |
| B (2L, no padding) − ATT+bal | v2pe 20 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.01 | [-0.02, +0.00] | 0/4 | no | [-0.02, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 50 insert | 1% FPR | malware TPR | -30.37 | 5.68 | [-31.22, -29.58] | 0/10 | **yes** | [-40.37, -20.19] | yes |
| B (2L, no padding) − ATT+bal | v2pe 50 insert | 1% FPR | padded-benign FPR | -0.12 | 0.06 | [-0.19, -0.07] | 0/10 | **yes** | [-0.21, -0.06] | yes |
| B (2L, no padding) − ATT+bal | v2pe 50 insert | 0.1% FPR | malware TPR | -12.47 | 1.66 | [-13.04, -11.91] | 0/10 | **yes** | [-20.78, -5.80] | yes |
| B (2L, no padding) − ATT+bal | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| B (2L, no padding) − ATT+bal | v2pe 100 insert | 1% FPR | malware TPR | -19.88 | 3.33 | [-20.62, -19.15] | 0/10 | **yes** | [-31.08, -10.45] | yes |
| B (2L, no padding) − ATT+bal | v2pe 100 insert | 1% FPR | padded-benign FPR | -0.03 | 0.02 | [-0.07, -0.01] | 0/9 | **yes** | [-0.08, -0.00] | yes |
| B (2L, no padding) − ATT+bal | v2pe 100 insert | 0.1% FPR | malware TPR | -5.96 | 1.44 | [-6.31, -5.59] | 0/10 | **yes** | [-10.90, -2.66] | yes |
| B (2L, no padding) − ATT+bal | v2pe 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 prepend | 1% FPR | malware TPR | -0.72 | 1.53 | [-0.88, -0.58] | 3/7 | **yes** | [-2.53, +0.85] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 prepend | 1% FPR | padded-benign FPR | -0.12 | 0.14 | [-0.16, -0.08] | 2/8 | **yes** | [-0.18, -0.06] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | -0.91 | 1.81 | [-1.16, -0.68] | 3/7 | **yes** | [-2.50, -0.06] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 prepend | 0.1% FPR | malware TPR | +1.34 | 5.07 | [+1.12, +1.55] | 8/2 | **yes** | [-0.79, +3.90] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.03 | [-0.00, +0.02] | 6/3 | no | [-0.01, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +1.42 | 4.68 | [+1.07, +1.80] | 7/2 | **yes** | [+0.22, +3.35] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 prepend | 1% FPR | malware TPR | +0.53 | 6.63 | [+0.39, +0.65] | 4/6 | no | [-1.40, +2.55] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 prepend | 1% FPR | padded-benign FPR | -0.03 | 0.04 | [-0.05, -0.02] | 1/5 | no | [-0.06, -0.02] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | -4.19 | 11.02 | [-4.48, -3.89] | 3/7 | **yes** | [-7.04, -0.69] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 prepend | 0.1% FPR | malware TPR | +6.05 | 2.51 | [+5.82, +6.28] | 10/0 | **yes** | [+2.92, +10.05] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.77 | 1.10 | [+0.58, +0.97] | 6/0 | no | [+0.14, +2.10] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 100 prepend | 1% FPR | malware TPR | +0.99 | 2.69 | [+0.92, +1.07] | 4/4 | no | [+0.39, +1.82] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 100 prepend | 0.1% FPR | malware TPR | +1.52 | 1.19 | [+1.37, +1.67] | 9/1 | **yes** | [+0.51, +2.98] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 insert | 1% FPR | malware TPR | -0.66 | 1.59 | [-0.78, -0.54] | 2/8 | **yes** | [-1.38, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.08 | 0.23 | [-0.12, -0.05] | 1/9 | **yes** | [-0.14, -0.04] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +0.29 | 4.43 | [+0.10, +0.49] | 3/7 | **yes** | [-0.53, +1.07] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 insert | 0.1% FPR | malware TPR | +0.22 | 5.37 | [+0.01, +0.43] | 7/3 | **yes** | [-2.57, +3.09] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.03] | 7/1 | **yes** | [+0.00, +0.03] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +4.48 | 3.00 | [+4.01, +4.96] | 10/0 | **yes** | [+0.49, +10.29] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 insert | 1% FPR | malware TPR | -1.13 | 1.47 | [-1.26, -1.01] | 2/8 | **yes** | [-1.84, -0.62] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 insert | 1% FPR | padded-benign FPR | -0.08 | 0.09 | [-0.11, -0.06] | 0/9 | **yes** | [-0.13, -0.05] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 insert | 1% FPR | malware TPR, fit subset | -0.68 | 1.13 | [-0.87, -0.49] | 2/7 | **yes** | [-1.51, -0.18] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 insert | 0.1% FPR | malware TPR | +3.34 | 6.29 | [+3.06, +3.64] | 8/2 | **yes** | [-0.87, +8.27] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.01] | 4/1 | no | [+0.00, +0.02] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 100 insert | 1% FPR | malware TPR | -1.96 | 2.56 | [-2.09, -1.82] | 3/7 | **yes** | [-2.71, -1.19] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 100 insert | 1% FPR | padded-benign FPR | -0.12 | 0.15 | [-0.15, -0.09] | 0/8 | **yes** | [-0.17, -0.08] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 100 insert | 0.1% FPR | malware TPR | +1.69 | 5.65 | [+1.45, +1.93] | 8/2 | **yes** | [-0.89, +4.35] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | lgbm 100 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [-0.00, +0.02] | 4/0 | no | [-0.00, +0.02] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 prepend | 1% FPR | malware TPR | +1.25 | 3.89 | [+1.13, +1.38] | 6/4 | no | [+0.13, +2.32] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 prepend | 1% FPR | padded-benign FPR | -0.01 | 0.01 | [-0.02, -0.00] | 0/4 | no | [-0.02, -0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | -1.26 | 2.52 | [-1.54, -1.02] | 3/7 | **yes** | [-3.11, -0.42] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 prepend | 0.1% FPR | malware TPR | +5.20 | 4.15 | [+4.95, +5.43] | 10/0 | **yes** | [+1.52, +9.69] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.16 | 0.44 | [+0.10, +0.24] | 4/0 | no | [+0.02, +0.52] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 50 prepend | 1% FPR | malware TPR | +0.88 | 1.28 | [+0.79, +0.97] | 4/3 | no | [+0.26, +1.88] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 50 prepend | 0.1% FPR | malware TPR | +1.10 | 1.08 | [+0.99, +1.22] | 9/1 | **yes** | [+0.43, +1.98] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 100 prepend | 1% FPR | malware TPR | +1.02 | 2.62 | [+0.95, +1.10] | 2/4 | no | [+0.31, +1.98] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 100 prepend | 0.1% FPR | malware TPR | +0.27 | 1.58 | [+0.21, +0.33] | 5/5 | no | [-0.05, +0.73] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 insert | 1% FPR | malware TPR | -1.58 | 1.61 | [-1.70, -1.45] | 2/8 | **yes** | [-2.16, -1.00] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 insert | 1% FPR | padded-benign FPR | -0.04 | 0.05 | [-0.07, -0.03] | 0/8 | **yes** | [-0.08, -0.02] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 insert | 1% FPR | malware TPR, fit subset | -0.79 | 1.05 | [-0.99, -0.59] | 0/7 | **yes** | [-2.17, -0.10] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 insert | 0.1% FPR | malware TPR | +3.19 | 5.68 | [+2.91, +3.45] | 7/3 | **yes** | [+1.03, +5.06] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [+0.00, +0.03] | 5/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 50 insert | 1% FPR | malware TPR | -2.04 | 2.53 | [-2.18, -1.89] | 4/6 | no | [-2.98, -1.13] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 50 insert | 1% FPR | padded-benign FPR | -0.05 | 0.03 | [-0.07, -0.03] | 0/10 | **yes** | [-0.08, -0.02] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 50 insert | 0.1% FPR | malware TPR | +3.59 | 4.64 | [+3.34, +3.85] | 9/1 | **yes** | [+1.48, +6.23] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 3/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 100 insert | 1% FPR | malware TPR | -1.92 | 2.04 | [-2.06, -1.78] | 2/8 | **yes** | [-3.40, -0.82] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 100 insert | 1% FPR | padded-benign FPR | -0.02 | 0.01 | [-0.03, -0.00] | 0/7 | **yes** | [-0.04, -0.00] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 100 insert | 0.1% FPR | malware TPR | +2.07 | 3.63 | [+1.82, +2.32] | 7/3 | **yes** | [-0.14, +5.47] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal | v2pe 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 prepend | 1% FPR | malware TPR | +61.38 | 8.43 | [+60.48, +62.17] | 10/0 | **yes** | [+47.31, +71.57] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.53 | 0.63 | [+0.41, +0.65] | 9/1 | **yes** | [+0.35, +0.76] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +59.78 | 9.11 | [+58.08, +61.54] | 10/0 | **yes** | [+32.89, +75.12] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 prepend | 0.1% FPR | malware TPR | +46.53 | 8.83 | [+45.70, +47.40] | 10/0 | **yes** | [+32.70, +57.37] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.03 | [+0.03, +0.15] | 10/0 | **yes** | [+0.03, +0.17] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +27.86 | 3.23 | [+26.31, +29.45] | 10/0 | **yes** | [+7.96, +50.72] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 prepend | 1% FPR | malware TPR | +33.76 | 10.64 | [+33.00, +34.56] | 10/0 | **yes** | [+21.10, +45.63] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.02, +0.07] | 9/0 | **yes** | [+0.01, +0.09] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +10.74 | 12.92 | [+9.72, +11.78] | 10/0 | **yes** | [+5.80, +17.13] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 prepend | 0.1% FPR | malware TPR | +10.84 | 6.44 | [+10.39, +11.29] | 9/1 | **yes** | [+4.63, +19.09] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.87 | 1.26 | [+0.64, +1.12] | 9/0 | **yes** | [+0.16, +2.42] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 100 prepend | 1% FPR | malware TPR | +2.83 | 2.63 | [+2.62, +3.04] | 8/2 | **yes** | [+1.19, +5.25] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 100 prepend | 0.1% FPR | malware TPR | +2.26 | 2.67 | [+2.04, +2.48] | 9/1 | **yes** | [+0.86, +4.34] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 insert | 1% FPR | malware TPR | +28.68 | 10.85 | [+28.02, +29.38] | 10/0 | **yes** | [+17.12, +38.84] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 insert | 1% FPR | padded-benign FPR | +0.25 | 0.41 | [+0.17, +0.34] | 9/1 | **yes** | [+0.11, +0.43] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +42.83 | 14.92 | [+41.48, +44.32] | 10/0 | **yes** | [+24.09, +53.25] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 insert | 0.1% FPR | malware TPR | +25.50 | 7.88 | [+24.76, +26.29] | 10/0 | **yes** | [+14.76, +35.93] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.02 | [+0.01, +0.06] | 10/0 | **yes** | [+0.01, +0.07] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +20.59 | 3.13 | [+19.18, +22.01] | 10/0 | **yes** | [+2.83, +42.62] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 insert | 1% FPR | malware TPR | +36.22 | 9.02 | [+35.42, +37.00] | 10/0 | **yes** | [+21.12, +49.05] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 insert | 1% FPR | padded-benign FPR | +0.15 | 0.16 | [+0.08, +0.23] | 8/2 | **yes** | [+0.07, +0.27] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +3.63 | 2.39 | [+2.94, +4.34] | 10/0 | **yes** | [+0.94, +9.38] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 insert | 0.1% FPR | malware TPR | +26.98 | 7.49 | [+26.25, +27.73] | 10/0 | **yes** | [+15.20, +38.73] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.04] | 7/0 | **yes** | [+0.00, +0.05] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 100 insert | 1% FPR | malware TPR | +32.02 | 7.54 | [+31.19, +32.83] | 10/0 | **yes** | [+17.88, +45.29] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 100 insert | 1% FPR | padded-benign FPR | +0.19 | 0.29 | [+0.13, +0.26] | 8/2 | **yes** | [+0.10, +0.29] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 100 insert | 0.1% FPR | malware TPR | +20.88 | 5.71 | [+20.21, +21.54] | 10/0 | **yes** | [+10.54, +32.63] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | lgbm 100 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.03] | 5/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 prepend | 1% FPR | malware TPR | +22.33 | 6.53 | [+21.63, +23.03] | 10/0 | **yes** | [+8.90, +34.78] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.05] | 8/0 | **yes** | [+0.00, +0.07] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +4.04 | 3.12 | [+3.32, +4.74] | 10/0 | **yes** | [+1.11, +10.37] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 prepend | 0.1% FPR | malware TPR | +6.03 | 4.81 | [+5.73, +6.32] | 10/0 | **yes** | [+2.21, +10.59] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.17 | 0.47 | [+0.10, +0.26] | 4/0 | no | [+0.02, +0.55] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 50 prepend | 1% FPR | malware TPR | +1.99 | 3.35 | [+1.75, +2.24] | 6/4 | no | [+0.31, +4.29] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 50 prepend | 0.1% FPR | malware TPR | +1.78 | 1.70 | [+1.61, +1.98] | 8/1 | **yes** | [+0.71, +3.32] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 100 prepend | 1% FPR | malware TPR | +2.13 | 3.11 | [+1.91, +2.37] | 7/3 | **yes** | [+0.44, +4.43] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 100 prepend | 0.1% FPR | malware TPR | +0.95 | 1.62 | [+0.84, +1.06] | 6/1 | no | [+0.35, +1.83] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 insert | 1% FPR | malware TPR | +33.08 | 7.16 | [+32.27, +33.89] | 10/0 | **yes** | [+19.92, +44.36] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 insert | 1% FPR | padded-benign FPR | +0.04 | 0.08 | [-0.01, +0.11] | 6/4 | no | [-0.01, +0.12] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 insert | 1% FPR | malware TPR, fit subset | +0.67 | 0.78 | [+0.44, +0.90] | 8/1 | **yes** | [+0.05, +2.15] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 insert | 0.1% FPR | malware TPR | +21.89 | 5.66 | [+21.20, +22.57] | 10/0 | **yes** | [+12.35, +31.74] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [+0.00, +0.03] | 6/1 | no | [+0.00, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 50 insert | 1% FPR | malware TPR | +24.25 | 5.38 | [+23.54, +24.99] | 10/0 | **yes** | [+14.22, +34.88] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 50 insert | 1% FPR | padded-benign FPR | +0.05 | 0.07 | [+0.00, +0.10] | 8/2 | **yes** | [-0.00, +0.11] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 50 insert | 0.1% FPR | malware TPR | +14.30 | 4.15 | [+13.72, +14.89] | 10/0 | **yes** | [+6.80, +23.98] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 3/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 100 insert | 1% FPR | malware TPR | +13.92 | 4.01 | [+13.32, +14.52] | 10/0 | **yes** | [+6.08, +24.13] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 100 insert | 1% FPR | padded-benign FPR | +0.01 | 0.03 | [-0.01, +0.03] | 6/2 | no | [-0.01, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 100 insert | 0.1% FPR | malware TPR | +7.04 | 3.03 | [+6.63, +7.42] | 10/0 | **yes** | [+2.45, +14.69] | yes |
| ATT+bal-2L, round 2 (A2) − v2-PE | v2pe 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 prepend | 1% FPR | malware TPR | -3.00 | 3.66 | [-3.18, -2.83] | 3/7 | **yes** | [-4.97, -1.56] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 prepend | 1% FPR | padded-benign FPR | -0.17 | 0.19 | [-0.23, -0.10] | 2/8 | **yes** | [-0.27, -0.09] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | -5.75 | 8.25 | [-6.22, -5.37] | 1/9 | **yes** | [-8.88, -2.46] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 prepend | 0.1% FPR | malware TPR | +5.34 | 13.49 | [+4.97, +5.72] | 7/3 | **yes** | [-1.92, +12.20] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.02 | 0.05 | [-0.00, +0.05] | 6/3 | no | [-0.01, +0.06] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | -5.92 | 15.53 | [-6.71, -5.09] | 3/7 | **yes** | [-19.92, +4.94] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 prepend | 1% FPR | malware TPR | -5.01 | 9.59 | [-5.33, -4.70] | 3/7 | **yes** | [-10.76, +0.90] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 prepend | 1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.04, +0.01] | 3/6 | no | [-0.04, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | -14.50 | 18.36 | [-15.46, -13.52] | 3/7 | **yes** | [-26.67, -0.84] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 prepend | 0.1% FPR | malware TPR | -3.76 | 9.53 | [-3.99, -3.54] | 3/7 | **yes** | [-7.84, -0.97] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | -0.26 | 1.68 | [-0.44, -0.08] | 3/5 | no | [-1.03, +0.24] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 100 prepend | 1% FPR | malware TPR | -3.15 | 8.91 | [-3.28, -3.02] | 2/7 | **yes** | [-4.57, -1.67] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 100 prepend | 1% FPR | padded-benign FPR | -0.00 | 0.01 | [-0.01, +0.00] | 1/1 | no | [-0.01, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 100 prepend | 0.1% FPR | malware TPR | -0.40 | 2.33 | [-0.48, -0.32] | 5/5 | no | [-1.18, +0.18] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 insert | 1% FPR | malware TPR | -4.44 | 4.98 | [-4.66, -4.23] | 0/10 | **yes** | [-8.23, -1.86] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.05 | 0.44 | [-0.11, +0.01] | 2/7 | no | [-0.13, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 insert | 1% FPR | malware TPR, fit subset | -9.46 | 8.81 | [-10.06, -8.84] | 0/10 | **yes** | [-18.73, -2.19] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 insert | 0.1% FPR | malware TPR | +3.11 | 11.55 | [+2.69, +3.49] | 5/5 | no | [-5.61, +10.55] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.03 | [-0.02, +0.02] | 4/5 | no | [-0.03, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | -1.19 | 11.78 | [-1.59, -0.80] | 4/6 | no | [-5.51, +3.21] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 insert | 1% FPR | malware TPR | -2.24 | 5.88 | [-2.43, -2.07] | 3/7 | **yes** | [-3.29, -1.26] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 insert | 1% FPR | padded-benign FPR | -0.00 | 0.11 | [-0.04, +0.03] | 5/5 | no | [-0.04, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 insert | 1% FPR | malware TPR, fit subset | -3.43 | 2.85 | [-3.96, -2.95] | 0/10 | **yes** | [-6.11, -1.81] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 insert | 0.1% FPR | malware TPR | +5.60 | 13.14 | [+5.26, +5.94] | 6/4 | no | [+1.50, +10.72] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.03 | [-0.02, +0.01] | 4/4 | no | [-0.02, +0.02] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | -0.28 | 0.47 | [-0.42, -0.16] | 0/5 | no | [-1.02, -0.02] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 100 insert | 1% FPR | malware TPR | -2.79 | 5.73 | [-3.04, -2.54] | 2/8 | **yes** | [-6.56, +1.12] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 100 insert | 1% FPR | padded-benign FPR | +0.08 | 0.28 | [+0.05, +0.11] | 5/4 | no | [+0.03, +0.13] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 100 insert | 0.1% FPR | malware TPR | +6.98 | 9.36 | [+6.53, +7.41] | 8/2 | **yes** | [-0.22, +15.79] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | lgbm 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.02 | [-0.01, +0.01] | 4/2 | no | [-0.01, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 prepend | 1% FPR | malware TPR | -5.18 | 8.36 | [-5.42, -4.96] | 3/7 | **yes** | [-8.94, -2.18] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 prepend | 1% FPR | padded-benign FPR | -0.03 | 0.04 | [-0.04, -0.01] | 2/7 | **yes** | [-0.05, -0.01] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | -5.56 | 12.81 | [-6.00, -5.15] | 3/7 | **yes** | [-8.28, -1.38] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 prepend | 0.1% FPR | malware TPR | -4.96 | 9.89 | [-5.19, -4.75] | 3/7 | **yes** | [-8.76, -1.07] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.01 | [-0.02, +0.00] | 0/3 | no | [-0.03, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | -0.34 | 0.80 | [-0.46, -0.23] | 2/4 | no | [-1.10, -0.06] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 50 prepend | 1% FPR | malware TPR | -5.74 | 14.35 | [-5.88, -5.60] | 3/6 | no | [-8.07, -3.29] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 50 prepend | 1% FPR | padded-benign FPR | -0.01 | 0.05 | [-0.02, -0.01] | 0/1 | no | [-0.03, -0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 50 prepend | 0.1% FPR | malware TPR | +0.02 | 3.07 | [-0.14, +0.19] | 7/3 | no | [-0.95, +1.22] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.01 | [-0.01, +0.00] | 0/1 | no | [-0.01, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 100 prepend | 1% FPR | malware TPR | -4.04 | 12.10 | [-4.19, -3.89] | 3/5 | no | [-6.49, -1.60] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 100 prepend | 1% FPR | padded-benign FPR | -0.01 | 0.04 | [-0.02, -0.00] | 1/1 | no | [-0.02, -0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 100 prepend | 0.1% FPR | malware TPR | +0.69 | 2.05 | [+0.59, +0.79] | 7/1 | **yes** | [+0.18, +1.46] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 insert | 1% FPR | malware TPR | -3.31 | 4.47 | [-3.55, -3.11] | 3/7 | **yes** | [-5.19, -1.59] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 insert | 1% FPR | padded-benign FPR | -0.02 | 0.04 | [-0.05, +0.01] | 3/6 | no | [-0.05, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 insert | 1% FPR | malware TPR, fit subset | -1.46 | 1.93 | [-1.74, -1.18] | 2/8 | **yes** | [-3.25, -0.54] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 insert | 0.1% FPR | malware TPR | +3.27 | 11.57 | [+2.92, +3.61] | 5/5 | no | [-1.30, +8.74] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.03 | [-0.01, +0.02] | 4/3 | no | [-0.01, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | -0.01 | 0.02 | [-0.03, +0.00] | 0/1 | no | [-0.03, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 50 insert | 1% FPR | malware TPR | -4.18 | 4.16 | [-4.44, -3.92] | 2/8 | **yes** | [-7.81, -0.81] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 50 insert | 1% FPR | padded-benign FPR | -0.03 | 0.05 | [-0.06, -0.01] | 1/8 | **yes** | [-0.06, -0.01] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 50 insert | 0.1% FPR | malware TPR | +3.27 | 6.46 | [+2.91, +3.63] | 7/3 | **yes** | [+0.10, +7.56] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 50 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.01 | [-0.02, +0.01] | 2/6 | no | [-0.02, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 100 insert | 1% FPR | malware TPR | +0.28 | 4.04 | [+0.05, +0.48] | 4/6 | no | [-1.38, +2.34] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 100 insert | 1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.03, +0.00] | 2/5 | no | [-0.03, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 100 insert | 0.1% FPR | malware TPR | +3.32 | 3.78 | [+3.08, +3.54] | 8/2 | **yes** | [+1.54, +5.28] | yes |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | v2pe 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [-0.00, +0.00] | 1/1 | no | [-0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 prepend | 1% FPR | malware TPR | +26.48 | 9.16 | [+25.73, +27.27] | 10/0 | **yes** | [+13.33, +39.69] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.54 | 0.46 | [+0.44, +0.64] | 10/0 | **yes** | [+0.33, +0.86] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +50.45 | 9.86 | [+48.83, +52.15] | 10/0 | **yes** | [+25.35, +67.31] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 prepend | 0.1% FPR | malware TPR | +35.87 | 12.31 | [+35.18, +36.56] | 10/0 | **yes** | [+23.74, +45.75] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.04 | [+0.03, +0.14] | 10/0 | **yes** | [+0.02, +0.16] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +27.53 | 3.73 | [+25.97, +29.12] | 10/0 | **yes** | [+7.77, +50.40] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 prepend | 1% FPR | malware TPR | +27.94 | 17.51 | [+27.24, +28.70] | 10/0 | **yes** | [+17.00, +38.01] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.01, +0.07] | 9/0 | **yes** | [+0.01, +0.09] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +10.74 | 12.92 | [+9.72, +11.78] | 10/0 | **yes** | [+5.80, +17.13] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 prepend | 0.1% FPR | malware TPR | +11.28 | 5.73 | [+10.79, +11.75] | 10/0 | **yes** | [+4.98, +19.62] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.87 | 1.26 | [+0.64, +1.12] | 9/0 | **yes** | [+0.16, +2.42] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 100 prepend | 1% FPR | malware TPR | -1.96 | 10.75 | [-2.46, -1.46] | 6/4 | no | [-8.56, +4.07] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.01 | [-0.00, +0.00] | 1/1 | no | [-0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 100 prepend | 0.1% FPR | malware TPR | +2.97 | 1.48 | [+2.69, +3.26] | 10/0 | **yes** | [+1.19, +5.58] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 insert | 1% FPR | malware TPR | +32.63 | 5.21 | [+31.92, +33.41] | 10/0 | **yes** | [+19.04, +45.98] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 insert | 1% FPR | padded-benign FPR | +0.43 | 0.36 | [+0.34, +0.52] | 10/0 | **yes** | [+0.28, +0.61] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +47.35 | 10.86 | [+45.85, +48.90] | 10/0 | **yes** | [+25.25, +61.93] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 insert | 0.1% FPR | malware TPR | +31.89 | 7.33 | [+31.19, +32.60] | 10/0 | **yes** | [+21.35, +42.81] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.02 | [+0.01, +0.07] | 10/0 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +20.97 | 2.36 | [+19.55, +22.43] | 10/0 | **yes** | [+2.96, +43.51] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 insert | 1% FPR | malware TPR | +42.41 | 6.80 | [+41.62, +43.21] | 10/0 | **yes** | [+28.71, +55.03] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 insert | 1% FPR | padded-benign FPR | +0.22 | 0.10 | [+0.14, +0.31] | 10/0 | **yes** | [+0.13, +0.36] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +3.63 | 2.38 | [+2.94, +4.35] | 10/0 | **yes** | [+0.94, +9.39] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 insert | 0.1% FPR | malware TPR | +31.83 | 6.26 | [+31.01, +32.60] | 10/0 | **yes** | [+19.91, +43.46] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.04] | 7/0 | **yes** | [+0.00, +0.05] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 100 insert | 1% FPR | malware TPR | +35.80 | 5.59 | [+34.97, +36.65] | 10/0 | **yes** | [+22.99, +48.47] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 100 insert | 1% FPR | padded-benign FPR | +0.22 | 0.27 | [+0.16, +0.29] | 10/0 | **yes** | [+0.14, +0.33] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 100 insert | 0.1% FPR | malware TPR | +23.66 | 4.89 | [+22.97, +24.41] | 10/0 | **yes** | [+12.74, +36.43] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | lgbm 100 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.03] | 5/0 | no | [+0.00, +0.03] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 prepend | 1% FPR | malware TPR | +14.75 | 15.18 | [+14.00, +15.49] | 8/2 | **yes** | [+0.84, +27.80] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.01, +0.05] | 7/1 | no | [-0.01, +0.06] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +4.04 | 3.12 | [+3.32, +4.74] | 10/0 | **yes** | [+1.11, +10.37] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 prepend | 0.1% FPR | malware TPR | +6.37 | 4.61 | [+6.04, +6.69] | 10/0 | **yes** | [+2.46, +10.98] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.17 | 0.47 | [+0.10, +0.26] | 4/0 | no | [+0.02, +0.55] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 50 prepend | 1% FPR | malware TPR | -1.71 | 9.36 | [-2.20, -1.23] | 5/5 | no | [-7.72, +3.77] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 50 prepend | 1% FPR | padded-benign FPR | -0.00 | 0.00 | [-0.00, +0.00] | 0/1 | no | [-0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 50 prepend | 0.1% FPR | malware TPR | +2.21 | 1.24 | [+1.99, +2.45] | 10/0 | **yes** | [+0.88, +4.21] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 100 prepend | 1% FPR | malware TPR | +3.40 | 3.57 | [+2.98, +3.86] | 9/1 | **yes** | [-0.75, +8.14] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 100 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 100 prepend | 0.1% FPR | malware TPR | +1.38 | 1.42 | [+1.22, +1.54] | 8/0 | **yes** | [+0.51, +2.64] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 100 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 insert | 1% FPR | malware TPR | +35.99 | 4.81 | [+35.20, +36.77] | 10/0 | **yes** | [+23.09, +47.80] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 insert | 1% FPR | padded-benign FPR | +0.13 | 0.05 | [+0.07, +0.21] | 10/0 | **yes** | [+0.07, +0.23] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 insert | 1% FPR | malware TPR, fit subset | +0.68 | 0.77 | [+0.46, +0.91] | 8/0 | **yes** | [+0.06, +2.17] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 insert | 0.1% FPR | malware TPR | +25.53 | 5.11 | [+24.83, +26.25] | 10/0 | **yes** | [+15.54, +35.57] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.04] | 6/0 | no | [+0.00, +0.05] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 50 insert | 1% FPR | malware TPR | +28.33 | 4.25 | [+27.55, +29.19] | 10/0 | **yes** | [+18.31, +37.92] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 50 insert | 1% FPR | padded-benign FPR | +0.08 | 0.04 | [+0.03, +0.13] | 9/0 | **yes** | [+0.03, +0.15] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 50 insert | 0.1% FPR | malware TPR | +16.06 | 4.43 | [+15.44, +16.71] | 10/0 | **yes** | [+8.24, +26.27] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 3/0 | no | [+0.00, +0.01] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 100 insert | 1% FPR | malware TPR | +17.97 | 2.06 | [+17.25, +18.68] | 10/0 | **yes** | [+9.44, +28.72] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 100 insert | 1% FPR | padded-benign FPR | +0.02 | 0.01 | [+0.00, +0.04] | 7/0 | **yes** | [+0.00, +0.04] | no |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 100 insert | 0.1% FPR | malware TPR | +8.03 | 3.20 | [+7.59, +8.43] | 10/0 | **yes** | [+3.14, +16.12] | yes |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | v2pe 100 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 1/0 | no | [+0.00, +0.01] | no |

**White-box greedy attack: share of the 500 malware reports still flagged after k prepended calls (mean over seeds 0-2; range in brackets).**

| model | threshold | seeds | k=0 | k=1 | k=2 | k=5 | k=10 | k=20 | k=30 | k=40 | k=50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2-PE | 1% FPR | 3 | 75.6 (74–78) | 40.1 (32–52) | 28.3 (24–33) | 9.0 (4–16) | 5.1 (2–9) | 2.2 (1–4) | 1.8 (0–4) | 1.2 (0–2) | 1.1 (0–2) |
| v2-PE | 0.1% FPR | 3 | 47.5 (44–50) | 7.7 (6–10) | 3.6 (2–6) | 0.7 (1–1) | 0.6 (0–1) | 0.2 (0–0) | 0.0 (0–0) | 0.0 (0–0) | 0.0 (0–0) |
| ATT+bal | 1% FPR | 3 | 77.7 (76–80) | 72.3 (71–74) | 69.9 (64–73) | 65.5 (61–68) | 62.5 (59–66) | 53.3 (52–56) | 11.3 (9–16) | 3.0 (3–3) | 1.8 (1–2) |
| ATT+bal | 0.1% FPR | 3 | 58.3 (56–61) | 46.4 (44–50) | 41.4 (36–47) | 34.5 (32–38) | 31.7 (28–36) | 14.6 (12–18) | 2.3 (1–3) | 0.5 (0–1) | 0.3 (0–1) |
| B (2L, no padding) | 1% FPR | 3 | 71.6 (65–76) | 51.1 (41–57) | 48.9 (38–56) | 39.9 (30–48) | 33.7 (26–44) | 16.7 (10–22) | 5.1 (1–9) | 3.3 (0–8) | 1.6 (0–4) |
| B (2L, no padding) | 0.1% FPR | 3 | 38.9 (29–44) | 19.8 (13–24) | 18.9 (11–24) | 14.7 (6–20) | 9.0 (1–13) | 2.4 (0–7) | 0.2 (0–1) | 0.0 (0–0) | 0.0 (0–0) |
| ATT+bal-2L (A) | 1% FPR | 3 | 78.7 (78–80) | 71.0 (70–72) | 70.5 (70–72) | 68.5 (67–71) | 67.6 (65–70) | 61.5 (58–63) | 39.2 (28–45) | 9.3 (5–17) | 4.4 (4–5) |
| ATT+bal-2L (A) | 0.1% FPR | 3 | 42.5 (38–49) | 32.9 (27–39) | 27.0 (23–33) | 24.1 (20–29) | 21.3 (18–25) | 11.7 (8–15) | 2.0 (1–4) | 0.8 (0–2) | 0.3 (0–1) |
| ATT+bal-2L, round 2 (A2) | 1% FPR | 3 | 77.0 (76–79) | 71.5 (70–74) | 68.9 (63–73) | 65.2 (60–68) | 63.5 (60–66) | 58.2 (52–63) | 25.3 (16–34) | 9.8 (4–16) | 6.2 (4–10) |
| ATT+bal-2L, round 2 (A2) | 0.1% FPR | 3 | 56.1 (55–57) | 44.7 (40–53) | 40.8 (36–49) | 34.7 (33–37) | 33.1 (30–36) | 25.8 (23–27) | 10.6 (7–13) | 3.9 (2–7) | 2.5 (1–5) |

**White-box: padded-benign FPR. The call list that the attack chose for malware report i after k steps (the final list if it stopped earlier) is prepended to one random benign April report (numpy seed 32, the same 500 benign reports for every model); share of those 500 flagged (mean over seeds).**

| model | threshold | k=5 | k=10 | k=20 | k=50 |
|---|---|---|---|---|---|
| v2-PE | 1% FPR | 0.1 | 0.1 | 0.1 | 0.1 |
| v2-PE | 0.1% FPR | 0.0 | 0.0 | 0.0 | 0.0 |
| ATT+bal | 1% FPR | 0.5 | 0.3 | 0.3 | 0.1 |
| ATT+bal | 0.1% FPR | 0.0 | 0.1 | 0.0 | 0.0 |
| B (2L, no padding) | 1% FPR | 0.5 | 0.3 | 0.3 | 0.3 |
| B (2L, no padding) | 0.1% FPR | 0.1 | 0.0 | 0.0 | 0.0 |
| ATT+bal-2L (A) | 1% FPR | 0.8 | 1.0 | 2.1 | 0.8 |
| ATT+bal-2L (A) | 0.1% FPR | 0.1 | 0.1 | 0.1 | 0.0 |
| ATT+bal-2L, round 2 (A2) | 1% FPR | 1.0 | 1.3 | 2.1 | 2.8 |
| ATT+bal-2L, round 2 (A2) | 0.1% FPR | 0.1 | 0.1 | 0.1 | 1.1 |

**White-box comparisons (points; share of the same 500 malware reports still flagged after k steps; seeds paired; CI = bootstrap over the 500 reports, and over their hash_apis groups).** A positive difference means that the first model is flagged MORE often (is harder to evade).

| comparison | threshold | k | mean difference | 95% CI (stratified) | 95% CI (cluster) | seeds > 0 |
|---|---|---|---|---|---|---|
| ATT+bal-2L (A) − ATT+bal | 1% FPR | 5 | +3.0 | [+1.7, +4.2] | [-0.6, +7.6] | 2/3 |
| ATT+bal-2L (A) − ATT+bal | 1% FPR | 10 | +5.1 | [+3.7, +6.5] | [+1.1, +10.1] | 3/3 |
| ATT+bal-2L (A) − ATT+bal | 1% FPR | 20 | +8.2 | [+6.4, +9.9] | [+2.3, +15.6] | 3/3 |
| ATT+bal-2L (A) − ATT+bal | 1% FPR | 50 | +2.6 | [+1.5, +3.8] | [+0.8, +5.5] | 3/3 |
| ATT+bal-2L (A) − ATT+bal | 0.1% FPR | 5 | -10.3 | [-13.5, -7.3] | [-23.1, +1.1] | 0/3 |
| ATT+bal-2L (A) − ATT+bal | 0.1% FPR | 10 | -10.5 | [-13.9, -7.5] | [-23.3, +1.1] | 0/3 |
| ATT+bal-2L (A) − ATT+bal | 0.1% FPR | 20 | -2.9 | [-5.1, -0.6] | [-9.9, +4.4] | 1/3 |
| ATT+bal-2L (A) − ATT+bal | 0.1% FPR | 50 | +0.0 | [+0.0, +0.0] | [+0.0, +0.0] | 0/3 |
| ATT+bal-2L (A) − v2-PE | 1% FPR | 5 | +59.5 | [+55.7, +63.5] | [+46.6, +70.5] | 3/3 |
| ATT+bal-2L (A) − v2-PE | 1% FPR | 10 | +62.5 | [+58.7, +66.7] | [+48.6, +73.7] | 3/3 |
| ATT+bal-2L (A) − v2-PE | 1% FPR | 20 | +59.3 | [+55.4, +63.5] | [+44.3, +71.9] | 3/3 |
| ATT+bal-2L (A) − v2-PE | 1% FPR | 50 | +3.3 | [+2.1, +4.6] | [+1.5, +6.4] | 3/3 |
| ATT+bal-2L (A) − v2-PE | 0.1% FPR | 5 | +23.4 | [+20.8, +26.1] | [+14.1, +31.5] | 3/3 |
| ATT+bal-2L (A) − v2-PE | 0.1% FPR | 10 | +20.7 | [+18.3, +23.3] | [+11.5, +28.3] | 3/3 |
| ATT+bal-2L (A) − v2-PE | 0.1% FPR | 20 | +11.5 | [+9.9, +13.4] | [+4.2, +17.8] | 3/3 |
| ATT+bal-2L (A) − v2-PE | 0.1% FPR | 50 | +0.3 | [+0.1, +0.7] | [+0.1, +0.8] | 1/3 |
| ATT+bal-2L (A) − B (2L, no padding) | 1% FPR | 5 | +28.7 | [+25.0, +32.4] | [+14.4, +41.6] | 3/3 |
| ATT+bal-2L (A) − B (2L, no padding) | 1% FPR | 10 | +33.9 | [+30.3, +37.7] | [+20.0, +47.0] | 3/3 |
| ATT+bal-2L (A) − B (2L, no padding) | 1% FPR | 20 | +44.9 | [+41.3, +48.9] | [+29.3, +59.1] | 3/3 |
| ATT+bal-2L (A) − B (2L, no padding) | 1% FPR | 50 | +2.8 | [+1.0, +4.7] | [-0.9, +7.3] | 3/3 |
| ATT+bal-2L (A) − B (2L, no padding) | 0.1% FPR | 5 | +9.4 | [+6.8, +12.3] | [-2.1, +18.5] | 3/3 |
| ATT+bal-2L (A) − B (2L, no padding) | 0.1% FPR | 10 | +12.3 | [+9.9, +14.8] | [+2.8, +19.7] | 3/3 |
| ATT+bal-2L (A) − B (2L, no padding) | 0.1% FPR | 20 | +9.3 | [+7.8, +11.0] | [+4.1, +14.8] | 3/3 |
| ATT+bal-2L (A) − B (2L, no padding) | 0.1% FPR | 50 | +0.3 | [+0.1, +0.7] | [+0.1, +0.8] | 1/3 |
| B (2L, no padding) − ATT+bal | 1% FPR | 5 | -25.7 | [-28.8, -22.5] | [-36.8, -14.0] | 0/3 |
| B (2L, no padding) − ATT+bal | 1% FPR | 10 | -28.7 | [-32.1, -25.5] | [-41.2, -16.0] | 0/3 |
| B (2L, no padding) − ATT+bal | 1% FPR | 20 | -36.7 | [-40.2, -33.3] | [-49.9, -23.8] | 0/3 |
| B (2L, no padding) − ATT+bal | 1% FPR | 50 | -0.2 | [-1.4, +0.9] | [-2.8, +2.8] | 1/3 |
| B (2L, no padding) − ATT+bal | 0.1% FPR | 5 | -19.7 | [-22.7, -17.0] | [-27.7, -12.5] | 0/3 |
| B (2L, no padding) − ATT+bal | 0.1% FPR | 10 | -22.7 | [-26.0, -19.7] | [-30.9, -14.9] | 0/3 |
| B (2L, no padding) − ATT+bal | 0.1% FPR | 20 | -12.2 | [-14.5, -9.9] | [-18.3, -7.1] | 0/3 |
| B (2L, no padding) − ATT+bal | 0.1% FPR | 50 | -0.3 | [-0.6, -0.1] | [-0.8, -0.1] | 0/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal | 1% FPR | 5 | -0.3 | [-0.9, +0.3] | [-1.2, +0.5] | 1/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal | 1% FPR | 10 | +1.1 | [+0.3, +1.9] | [-0.2, +3.0] | 2/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal | 1% FPR | 20 | +4.9 | [+3.3, +6.3] | [+1.3, +9.4] | 2/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal | 1% FPR | 50 | +4.4 | [+3.1, +5.7] | [+1.5, +8.6] | 3/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal | 0.1% FPR | 5 | +0.2 | [-1.3, +1.5] | [-4.2, +3.9] | 2/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal | 0.1% FPR | 10 | +1.3 | [-0.4, +2.9] | [-3.5, +5.5] | 2/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal | 0.1% FPR | 20 | +11.2 | [+9.1, +13.6] | [+5.2, +18.2] | 3/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal | 0.1% FPR | 50 | +2.2 | [+1.4, +3.1] | [+0.7, +4.4] | 3/3 |
| ATT+bal-2L, round 2 (A2) − v2-PE | 1% FPR | 5 | +56.2 | [+52.4, +59.9] | [+42.6, +67.4] | 3/3 |
| ATT+bal-2L, round 2 (A2) − v2-PE | 1% FPR | 10 | +58.4 | [+54.6, +62.3] | [+44.9, +69.7] | 3/3 |
| ATT+bal-2L, round 2 (A2) − v2-PE | 1% FPR | 20 | +56.0 | [+51.9, +59.9] | [+42.1, +67.5] | 3/3 |
| ATT+bal-2L, round 2 (A2) − v2-PE | 1% FPR | 50 | +5.1 | [+3.8, +6.5] | [+2.1, +9.3] | 3/3 |
| ATT+bal-2L, round 2 (A2) − v2-PE | 0.1% FPR | 5 | +33.9 | [+29.8, +37.5] | [+22.3, +46.2] | 3/3 |
| ATT+bal-2L, round 2 (A2) − v2-PE | 0.1% FPR | 10 | +32.5 | [+28.5, +35.9] | [+20.9, +44.7] | 3/3 |
| ATT+bal-2L, round 2 (A2) − v2-PE | 0.1% FPR | 20 | +25.6 | [+22.2, +28.9] | [+14.7, +37.3] | 3/3 |
| ATT+bal-2L, round 2 (A2) − v2-PE | 0.1% FPR | 50 | +2.5 | [+1.6, +3.5] | [+0.9, +4.7] | 3/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | 1% FPR | 5 | -3.3 | [-4.8, -2.0] | [-7.9, +0.4] | 0/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | 1% FPR | 10 | -4.1 | [-5.3, -2.9] | [-8.6, -0.5] | 0/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | 1% FPR | 20 | -3.3 | [-4.7, -2.0] | [-7.0, -0.1] | 0/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | 1% FPR | 50 | +1.8 | [+0.9, +2.7] | [-0.4, +5.1] | 2/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | 0.1% FPR | 5 | +10.5 | [+7.7, +13.1] | [+1.1, +20.9] | 3/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | 0.1% FPR | 10 | +11.8 | [+8.9, +14.5] | [+1.9, +22.0] | 3/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | 0.1% FPR | 20 | +14.1 | [+11.4, +16.7] | [+4.0, +23.7] | 3/3 |
| ATT+bal-2L, round 2 (A2) − ATT+bal-2L (A) | 0.1% FPR | 50 | +2.2 | [+1.4, +3.1] | [+0.7, +4.1] | 3/3 |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | 1% FPR | 5 | +25.3 | [+22.5, +28.3] | [+13.7, +36.8] | 3/3 |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | 1% FPR | 10 | +29.8 | [+26.5, +32.7] | [+18.0, +42.2] | 3/3 |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | 1% FPR | 20 | +41.5 | [+37.6, +45.0] | [+27.7, +55.2] | 3/3 |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | 1% FPR | 50 | +4.6 | [+3.1, +6.4] | [+2.0, +8.3] | 3/3 |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | 0.1% FPR | 5 | +19.9 | [+16.7, +23.0] | [+12.4, +29.1] | 3/3 |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | 0.1% FPR | 10 | +24.1 | [+21.0, +27.4] | [+16.4, +32.5] | 3/3 |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | 0.1% FPR | 20 | +23.4 | [+20.3, +26.7] | [+14.3, +33.2] | 3/3 |
| ATT+bal-2L, round 2 (A2) − B (2L, no padding) | 0.1% FPR | 50 | +2.5 | [+1.6, +3.6] | [+0.8, +4.8] | 3/3 |

