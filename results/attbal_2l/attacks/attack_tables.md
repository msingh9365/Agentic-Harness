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

**White-box greedy attack: share of the 500 malware reports still flagged after k prepended calls (mean over seeds 0-2; range in brackets).**

| model | threshold | seeds | k=0 | k=1 | k=2 | k=5 | k=10 | k=20 | k=30 | k=40 | k=50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal | 1% FPR | 3 | 77.7 (76–80) | 72.3 (71–74) | 69.9 (64–73) | 65.5 (61–68) | 62.5 (59–66) | 53.3 (52–56) | 11.3 (9–16) | 3.0 (3–3) | 1.8 (1–2) |
| ATT+bal | 0.1% FPR | 3 | 58.3 (56–61) | 46.4 (44–50) | 41.4 (36–47) | 34.5 (32–38) | 31.7 (28–36) | 14.6 (12–18) | 2.3 (1–3) | 0.5 (0–1) | 0.3 (0–1) |
| ATT+bal-2L (A) | 1% FPR | 3 | 78.7 (78–80) | 71.0 (70–72) | 70.5 (70–72) | 68.5 (67–71) | 67.6 (65–70) | 61.5 (58–63) | 39.2 (28–45) | 9.3 (5–17) | 4.4 (4–5) |
| ATT+bal-2L (A) | 0.1% FPR | 3 | 42.5 (38–49) | 32.9 (27–39) | 27.0 (23–33) | 24.1 (20–29) | 21.3 (18–25) | 11.7 (8–15) | 2.0 (1–4) | 0.8 (0–2) | 0.3 (0–1) |

**White-box: padded-benign FPR. The call list that the attack chose for malware report i after k steps (the final list if it stopped earlier) is prepended to one random benign April report (numpy seed 32, the same 500 benign reports for every model); share of those 500 flagged (mean over seeds).**

| model | threshold | k=5 | k=10 | k=20 | k=50 |
|---|---|---|---|---|---|
| ATT+bal | 1% FPR | 0.5 | 0.3 | 0.3 | 0.1 |
| ATT+bal | 0.1% FPR | 0.0 | 0.1 | 0.0 | 0.0 |
| ATT+bal-2L (A) | 1% FPR | 0.8 | 1.0 | 2.1 | 0.8 |
| ATT+bal-2L (A) | 0.1% FPR | 0.1 | 0.1 | 0.1 | 0.0 |

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

