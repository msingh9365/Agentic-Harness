**Table 2a. Random padding (the procedure of REPORT 5.10, calls from the EVAL pool), all April reports.** Thresholds: 1% and 0.1% FPR of each model's unedited April benign scores.

| model | edit | malware TPR @1% | padded-benign FPR @1% | malware TPR @0.1% | padded-benign FPR @0.1% | malware that fit in 512 | TPR @1%, fit subset | TPR @0.1%, fit subset |
|---|---|---|---|---|---|---|---|---|
| released checkpoint | random 5 insert | 66.5 | 1.0 | 38.8 | 0.0 | 30.1% | 49.1 | 30.1 |
| released checkpoint | random 20 insert | 46.3 | 1.8 | 23.0 | 0.0 | 26.1% | 20.3 | 5.6 |
| released checkpoint | random 50 insert | 35.6 | 4.0 | 14.7 | 0.1 | 16.9% | 9.0 | 0.9 |
| released checkpoint | random 5 prepend | 43.4 | 1.8 | 19.9 | 0.0 | 30.1% | 40.3 | 20.8 |
| released checkpoint | random 20 prepend | 12.0 | 12.5 | 2.1 | 1.1 | 25.9% | 2.4 | 0.1 |
| released checkpoint | random 50 prepend | 16.3 | 13.3 | 4.1 | 0.8 | 16.9% | 5.3 | 0.3 |
| v2-PE | random 5 insert | 73.8 ± 2.7 | 0.9 ± 0.2 | 40.0 ± 4.8 | 0.0 ± 0.0 | 30.3% | 65.4 | 31.5 |
| v2-PE | random 20 insert | 55.7 ± 4.5 | 0.7 ± 0.3 | 23.4 ± 4.9 | 0.0 ± 0.0 | 27.6% | 34.1 | 7.2 |
| v2-PE | random 50 insert | 41.4 ± 4.3 | 0.7 ± 0.6 | 13.6 ± 3.4 | 0.0 ± 0.0 | 17.0% | 5.3 | 0.3 |
| v2-PE | random 5 prepend | 54.4 ± 7.8 | 1.0 ± 0.2 | 20.3 ± 6.2 | 0.0 ± 0.0 | 30.3% | 46.3 | 14.2 |
| v2-PE | random 20 prepend | 22.5 ± 8.2 | 1.2 ± 1.3 | 5.5 ± 2.3 | 0.0 ± 0.0 | 27.5% | 10.0 | 0.7 |
| v2-PE | random 50 prepend | 8.3 ± 3.5 | 1.1 ± 1.8 | 1.5 ± 1.8 | 0.0 ± 0.0 | 17.1% | 2.5 | 0.0 |
| PE+bal | random 5 insert | 77.7 ± 1.9 | 1.1 ± 0.2 | 52.5 ± 6.7 | 0.1 ± 0.0 | 30.3% | 73.2 | 48.0 |
| PE+bal | random 20 insert | 75.2 ± 1.9 | 1.4 ± 0.3 | 47.2 ± 6.6 | 0.1 ± 0.0 | 27.6% | 71.4 | 40.0 |
| PE+bal | random 50 insert | 71.4 ± 2.0 | 1.5 ± 0.4 | 42.6 ± 6.0 | 0.1 ± 0.0 | 17.0% | 53.2 | 17.0 |
| PE+bal | random 5 prepend | 78.3 ± 2.0 | 1.6 ± 1.2 | 52.0 ± 7.0 | 0.1 ± 0.0 | 30.3% | 74.1 | 47.1 |
| PE+bal | random 20 prepend | 75.7 ± 2.3 | 2.4 ± 2.0 | 47.8 ± 4.9 | 0.1 ± 0.1 | 27.5% | 73.2 | 33.6 |
| PE+bal | random 50 prepend | 64.3 ± 8.1 | 2.4 ± 0.7 | 21.1 ± 7.2 | 0.1 ± 0.0 | 17.1% | 54.3 | 10.6 |
| ATT+bal | random 5 insert | 78.5 ± 2.5 | 1.1 ± 0.2 | 52.8 ± 6.5 | 0.1 ± 0.0 | 30.3% | 74.3 | 51.4 |
| ATT+bal | random 20 insert | 75.4 ± 4.0 | 1.1 ± 0.3 | 45.6 ± 4.0 | 0.1 ± 0.0 | 27.6% | 71.5 | 40.0 |
| ATT+bal | random 50 insert | 71.9 ± 4.3 | 1.0 ± 0.4 | 39.7 ± 4.6 | 0.0 ± 0.0 | 17.0% | 51.9 | 10.1 |
| ATT+bal | random 5 prepend | 79.0 ± 2.9 | 1.2 ± 0.1 | 52.1 ± 5.5 | 0.1 ± 0.0 | 30.3% | 74.6 | 50.3 |
| ATT+bal | random 20 prepend | 76.9 ± 2.8 | 1.3 ± 0.3 | 51.8 ± 6.5 | 0.1 ± 0.0 | 27.5% | 73.4 | 41.9 |
| ATT+bal | random 50 prepend | 67.6 ± 5.2 | 1.5 ± 0.8 | 32.2 ± 5.4 | 0.0 ± 0.0 | 17.1% | 54.9 | 9.5 |
| ATT+bal-keep | random 5 insert | 78.5 ± 1.6 | 1.0 ± 0.1 | 47.2 ± 4.9 | 0.1 ± 0.0 | 30.3% | 73.9 | 47.3 |
| ATT+bal-keep | random 20 insert | 76.0 ± 1.6 | 1.2 ± 0.3 | 40.9 ± 4.4 | 0.1 ± 0.0 | 27.6% | 71.5 | 33.9 |
| ATT+bal-keep | random 50 insert | 71.7 ± 2.2 | 1.0 ± 0.3 | 33.6 ± 4.6 | 0.0 ± 0.0 | 17.0% | 51.2 | 7.4 |
| ATT+bal-keep | random 5 prepend | 78.8 ± 1.6 | 1.1 ± 0.1 | 45.9 ± 5.6 | 0.1 ± 0.0 | 30.3% | 74.5 | 46.5 |
| ATT+bal-keep | random 20 prepend | 76.7 ± 1.5 | 1.3 ± 0.3 | 44.6 ± 5.6 | 0.1 ± 0.0 | 27.5% | 73.5 | 34.7 |
| ATT+bal-keep | random 50 prepend | 66.6 ± 3.4 | 1.5 ± 0.6 | 26.1 ± 6.5 | 0.0 ± 0.0 | 17.1% | 53.9 | 7.5 |
| PE+bal-keep | random 5 insert | 78.4 ± 1.6 | 1.1 ± 0.4 | 48.0 ± 6.0 | 0.1 ± 0.0 | 30.3% | 72.0 | 39.4 |
| PE+bal-keep | random 20 insert | 75.6 ± 2.2 | 1.5 ± 0.6 | 41.0 ± 4.8 | 0.1 ± 0.0 | 27.6% | 69.1 | 29.0 |
| PE+bal-keep | random 50 insert | 71.8 ± 3.0 | 1.7 ± 0.9 | 37.6 ± 4.2 | 0.0 ± 0.0 | 17.0% | 50.7 | 11.9 |
| PE+bal-keep | random 5 prepend | 79.0 ± 2.3 | 1.9 ± 2.2 | 45.4 ± 4.6 | 0.1 ± 0.0 | 30.3% | 72.5 | 36.3 |
| PE+bal-keep | random 20 prepend | 76.3 ± 2.3 | 2.5 ± 2.8 | 44.2 ± 4.8 | 0.1 ± 0.0 | 27.5% | 71.9 | 26.8 |
| PE+bal-keep | random 50 prepend | 65.1 ± 5.0 | 2.9 ± 1.2 | 19.1 ± 5.7 | 0.0 ± 0.0 | 17.1% | 55.1 | 9.4 |
| ATT+aug | random 5 insert | 83.4 ± 5.6 | 18.0 ± 3.9 | 60.6 ± 7.0 | 5.9 ± 1.4 | 30.3% | 88.4 | 68.8 |
| ATT+aug | random 20 insert | 88.0 ± 6.0 | 42.0 ± 7.2 | 65.1 ± 8.3 | 20.1 ± 3.3 | 27.6% | 96.7 | 80.6 |
| ATT+aug | random 50 insert | 92.1 ± 5.9 | 62.0 ± 9.8 | 72.4 ± 8.1 | 31.3 ± 6.3 | 17.0% | 98.5 | 87.4 |
| ATT+aug | random 5 prepend | 86.6 ± 6.2 | 24.2 ± 4.5 | 64.9 ± 7.4 | 8.3 ± 1.7 | 30.3% | 90.3 | 70.6 |
| ATT+aug | random 20 prepend | 94.4 ± 6.1 | 62.1 ± 13.6 | 74.7 ± 6.9 | 22.4 ± 3.7 | 27.5% | 97.1 | 82.9 |
| ATT+aug | random 50 prepend | 98.5 ± 4.0 | 95.3 ± 9.6 | 84.5 ± 9.4 | 59.0 ± 13.4 | 17.1% | 98.5 | 87.2 |
| PE+aug | random 5 insert | 86.1 ± 2.0 | 16.6 ± 4.3 | 61.4 ± 6.7 | 2.1 ± 1.8 | 30.3% | 88.4 | 54.4 |
| PE+aug | random 20 insert | 90.5 ± 1.5 | 42.3 ± 3.5 | 70.6 ± 5.3 | 19.2 ± 6.7 | 27.6% | 97.8 | 77.9 |
| PE+aug | random 50 insert | 94.2 ± 1.5 | 60.7 ± 4.5 | 80.1 ± 4.0 | 38.2 ± 3.3 | 17.0% | 99.9 | 95.6 |
| PE+aug | random 5 prepend | 92.6 ± 1.9 | 39.2 ± 11.2 | 71.1 ± 6.1 | 4.3 ± 3.4 | 30.3% | 92.2 | 57.9 |
| PE+aug | random 20 prepend | 99.3 ± 0.4 | 94.0 ± 4.7 | 89.3 ± 5.6 | 56.2 ± 20.2 | 27.5% | 99.2 | 84.3 |
| PE+aug | random 50 prepend | 99.9 ± 0.1 | 99.7 ± 0.3 | 96.3 ± 1.7 | 92.9 ± 3.9 | 17.1% | 99.9 | 96.3 |

**Table 2a comparisons: A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; resolved = CI excludes 0 and ≥ 7 of 10 seeds with the same sign.**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | resolved | CI (cluster bootstrap) | resolved (cluster) |
|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal − PE+bal | random 5 insert | 1% FPR | malware TPR | +0.81 | 3.33 | [+0.61, +1.01] | 7/3 | **yes** | [-0.27, +1.89] | no |
| ATT+bal − PE+bal | random 5 insert | 1% FPR | padded-benign FPR | -0.05 | 0.17 | [-0.15, +0.05] | 4/6 | no | [-0.19, +0.11] | no |
| ATT+bal − PE+bal | random 5 insert | 1% FPR | malware TPR, fit subset | +1.09 | 4.00 | [+0.67, +1.50] | 8/2 | **yes** | [-0.29, +2.42] | no |
| ATT+bal − PE+bal | random 5 insert | 0.1% FPR | malware TPR | +0.32 | 9.87 | [-0.09, +0.70] | 6/4 | no | [-2.67, +2.46] | no |
| ATT+bal − PE+bal | random 5 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.03 | [-0.04, +0.03] | 4/5 | no | [-0.06, +0.03] | no |
| ATT+bal − PE+bal | random 5 insert | 0.1% FPR | malware TPR, fit subset | +3.43 | 11.43 | [+2.56, +4.28] | 6/4 | no | [+1.14, +6.16] | no |
| ATT+bal − PE+bal | random 20 insert | 1% FPR | malware TPR | +0.21 | 5.21 | [-0.02, +0.43] | 8/2 | no | [-0.78, +1.32] | no |
| ATT+bal − PE+bal | random 20 insert | 1% FPR | padded-benign FPR | -0.29 | 0.30 | [-0.41, -0.18] | 1/8 | **yes** | [-0.53, -0.09] | yes |
| ATT+bal − PE+bal | random 20 insert | 1% FPR | malware TPR, fit subset | +0.15 | 5.61 | [-0.31, +0.63] | 6/4 | no | [-1.57, +1.79] | no |
| ATT+bal − PE+bal | random 20 insert | 0.1% FPR | malware TPR | -1.64 | 7.40 | [-2.02, -1.28] | 5/5 | no | [-5.52, +2.01] | no |
| ATT+bal − PE+bal | random 20 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.04 | [-0.05, +0.01] | 2/8 | no | [-0.05, +0.01] | no |
| ATT+bal − PE+bal | random 20 insert | 0.1% FPR | malware TPR, fit subset | +0.05 | 7.89 | [-0.65, +0.72] | 5/5 | no | [-1.63, +1.45] | no |
| ATT+bal − PE+bal | random 50 insert | 1% FPR | malware TPR | +0.50 | 5.66 | [+0.27, +0.72] | 7/3 | **yes** | [-0.48, +1.72] | no |
| ATT+bal − PE+bal | random 50 insert | 1% FPR | padded-benign FPR | -0.50 | 0.50 | [-0.61, -0.38] | 2/8 | **yes** | [-0.81, -0.25] | yes |
| ATT+bal − PE+bal | random 50 insert | 1% FPR | malware TPR, fit subset | -1.30 | 9.95 | [-1.95, -0.59] | 5/5 | no | [-3.36, +0.57] | no |
| ATT+bal − PE+bal | random 50 insert | 0.1% FPR | malware TPR | -2.90 | 7.17 | [-3.29, -2.53] | 4/6 | no | [-5.93, +0.37] | no |
| ATT+bal − PE+bal | random 50 insert | 0.1% FPR | padded-benign FPR | -0.03 | 0.03 | [-0.05, -0.00] | 2/8 | **yes** | [-0.06, -0.00] | yes |
| ATT+bal − PE+bal | random 50 insert | 0.1% FPR | malware TPR, fit subset | -6.86 | 5.49 | [-7.76, -6.02] | 0/9 | **yes** | [-9.95, -2.27] | yes |
| ATT+bal − PE+bal | random 5 prepend | 1% FPR | malware TPR | +0.74 | 3.80 | [+0.54, +0.94] | 8/2 | **yes** | [+0.03, +1.58] | yes |
| ATT+bal − PE+bal | random 5 prepend | 1% FPR | padded-benign FPR | -0.49 | 1.15 | [-0.60, -0.38] | 3/7 | **yes** | [-1.05, -0.06] | yes |
| ATT+bal − PE+bal | random 5 prepend | 1% FPR | malware TPR, fit subset | +0.53 | 4.68 | [+0.10, +0.96] | 5/4 | no | [-1.03, +2.00] | no |
| ATT+bal − PE+bal | random 5 prepend | 0.1% FPR | malware TPR | +0.09 | 9.15 | [-0.32, +0.50] | 7/3 | no | [-3.08, +3.01] | no |
| ATT+bal − PE+bal | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.02 | 0.04 | [-0.02, +0.05] | 6/3 | no | [-0.02, +0.05] | no |
| ATT+bal − PE+bal | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +3.11 | 12.43 | [+2.21, +3.92] | 6/4 | no | [-1.77, +8.04] | no |
| ATT+bal − PE+bal | random 20 prepend | 1% FPR | malware TPR | +1.22 | 4.27 | [+1.02, +1.44] | 8/2 | **yes** | [+0.37, +2.24] | yes |
| ATT+bal − PE+bal | random 20 prepend | 1% FPR | padded-benign FPR | -1.04 | 2.00 | [-1.17, -0.91] | 1/9 | **yes** | [-1.96, -0.45] | yes |
| ATT+bal − PE+bal | random 20 prepend | 1% FPR | malware TPR, fit subset | +0.17 | 5.39 | [-0.26, +0.63] | 5/5 | no | [-1.37, +1.61] | no |
| ATT+bal − PE+bal | random 20 prepend | 0.1% FPR | malware TPR | +3.91 | 8.51 | [+3.52, +4.31] | 7/3 | **yes** | [+1.22, +6.69] | yes |
| ATT+bal − PE+bal | random 20 prepend | 0.1% FPR | padded-benign FPR | -0.04 | 0.14 | [-0.07, -0.00] | 3/5 | no | [-0.09, +0.01] | no |
| ATT+bal − PE+bal | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +8.26 | 8.02 | [+7.41, +9.06] | 9/1 | **yes** | [+4.03, +12.28] | yes |
| ATT+bal − PE+bal | random 50 prepend | 1% FPR | malware TPR | +3.33 | 11.17 | [+2.98, +3.65] | 6/4 | no | [+1.05, +5.03] | no |
| ATT+bal − PE+bal | random 50 prepend | 1% FPR | padded-benign FPR | -0.88 | 1.15 | [-1.04, -0.72] | 2/7 | **yes** | [-1.25, -0.55] | yes |
| ATT+bal − PE+bal | random 50 prepend | 1% FPR | malware TPR, fit subset | +0.60 | 16.95 | [-0.27, +1.38] | 5/5 | no | [-2.82, +2.72] | no |
| ATT+bal − PE+bal | random 50 prepend | 0.1% FPR | malware TPR | +11.06 | 12.03 | [+10.60, +11.55] | 8/2 | **yes** | [+5.38, +17.10] | yes |
| ATT+bal − PE+bal | random 50 prepend | 0.1% FPR | padded-benign FPR | -0.04 | 0.05 | [-0.06, -0.02] | 2/8 | **yes** | [-0.06, -0.02] | yes |
| ATT+bal − PE+bal | random 50 prepend | 0.1% FPR | malware TPR, fit subset | -1.10 | 8.31 | [-1.95, -0.31] | 5/5 | no | [-3.90, +3.09] | no |
| ATT+bal-keep − PE+bal-keep | random 5 insert | 1% FPR | malware TPR | +0.05 | 1.53 | [-0.18, +0.31] | 5/5 | no | [-1.44, +1.32] | no |
| ATT+bal-keep − PE+bal-keep | random 5 insert | 1% FPR | padded-benign FPR | -0.12 | 0.44 | [-0.23, -0.01] | 4/5 | no | [-0.34, +0.08] | no |
| ATT+bal-keep − PE+bal-keep | random 5 insert | 1% FPR | malware TPR, fit subset | +1.88 | 2.18 | [+1.49, +2.32] | 8/2 | **yes** | [+0.78, +3.04] | yes |
| ATT+bal-keep − PE+bal-keep | random 5 insert | 0.1% FPR | malware TPR | -0.84 | 6.98 | [-1.34, -0.35] | 4/6 | no | [-6.15, +4.34] | no |
| ATT+bal-keep − PE+bal-keep | random 5 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.03 | [-0.04, +0.02] | 3/5 | no | [-0.05, +0.03] | no |
| ATT+bal-keep − PE+bal-keep | random 5 insert | 0.1% FPR | malware TPR, fit subset | +7.87 | 11.17 | [+7.07, +8.64] | 8/2 | **yes** | [+3.00, +13.25] | yes |
| ATT+bal-keep − PE+bal-keep | random 20 insert | 1% FPR | malware TPR | +0.44 | 2.19 | [+0.20, +0.66] | 6/4 | no | [-1.04, +1.61] | no |
| ATT+bal-keep − PE+bal-keep | random 20 insert | 1% FPR | padded-benign FPR | -0.30 | 0.84 | [-0.41, -0.18] | 6/4 | no | [-0.61, -0.02] | no |
| ATT+bal-keep − PE+bal-keep | random 20 insert | 1% FPR | malware TPR, fit subset | +2.45 | 3.39 | [+2.01, +2.94] | 8/2 | **yes** | [+0.95, +3.62] | yes |
| ATT+bal-keep − PE+bal-keep | random 20 insert | 0.1% FPR | malware TPR | -0.09 | 5.90 | [-0.53, +0.35] | 4/6 | no | [-4.80, +4.12] | no |
| ATT+bal-keep − PE+bal-keep | random 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.04 | [-0.02, +0.03] | 5/4 | no | [-0.02, +0.03] | no |
| ATT+bal-keep − PE+bal-keep | random 20 insert | 0.1% FPR | malware TPR, fit subset | +4.92 | 9.74 | [+4.08, +5.70] | 7/3 | **yes** | [-1.12, +10.24] | no |
| ATT+bal-keep − PE+bal-keep | random 50 insert | 1% FPR | malware TPR | -0.10 | 3.03 | [-0.37, +0.16] | 6/4 | no | [-1.68, +1.30] | no |
| ATT+bal-keep − PE+bal-keep | random 50 insert | 1% FPR | padded-benign FPR | -0.72 | 1.15 | [-0.83, -0.61] | 2/8 | **yes** | [-1.09, -0.44] | yes |
| ATT+bal-keep − PE+bal-keep | random 50 insert | 1% FPR | malware TPR, fit subset | +0.56 | 8.29 | [-0.19, +1.28] | 5/5 | no | [-4.38, +4.09] | no |
| ATT+bal-keep − PE+bal-keep | random 50 insert | 0.1% FPR | malware TPR | -4.00 | 5.19 | [-4.43, -3.59] | 1/9 | **yes** | [-8.48, +0.22] | no |
| ATT+bal-keep − PE+bal-keep | random 50 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.04 | [-0.04, -0.00] | 3/6 | no | [-0.04, -0.01] | no |
| ATT+bal-keep − PE+bal-keep | random 50 insert | 0.1% FPR | malware TPR, fit subset | -4.51 | 7.09 | [-5.19, -3.86] | 4/6 | no | [-7.51, -2.76] | no |
| ATT+bal-keep − PE+bal-keep | random 5 prepend | 1% FPR | malware TPR | -0.20 | 2.16 | [-0.45, +0.03] | 5/5 | no | [-1.91, +1.09] | no |
| ATT+bal-keep − PE+bal-keep | random 5 prepend | 1% FPR | padded-benign FPR | -0.80 | 2.22 | [-0.91, -0.67] | 4/5 | no | [-1.75, -0.18] | no |
| ATT+bal-keep − PE+bal-keep | random 5 prepend | 1% FPR | malware TPR, fit subset | +1.96 | 2.23 | [+1.47, +2.44] | 8/1 | **yes** | [+0.47, +3.35] | yes |
| ATT+bal-keep − PE+bal-keep | random 5 prepend | 0.1% FPR | malware TPR | +0.51 | 6.59 | [+0.04, +0.96] | 5/5 | no | [-4.04, +5.52] | no |
| ATT+bal-keep − PE+bal-keep | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.06 | [-0.02, +0.04] | 6/4 | no | [-0.02, +0.04] | no |
| ATT+bal-keep − PE+bal-keep | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +10.22 | 11.99 | [+9.39, +11.00] | 8/2 | **yes** | [+3.62, +14.97] | yes |
| ATT+bal-keep − PE+bal-keep | random 20 prepend | 1% FPR | malware TPR | +0.41 | 1.72 | [+0.17, +0.64] | 6/4 | no | [-0.71, +1.41] | no |
| ATT+bal-keep − PE+bal-keep | random 20 prepend | 1% FPR | padded-benign FPR | -1.18 | 2.92 | [-1.30, -1.04] | 4/5 | no | [-2.38, -0.40] | no |
| ATT+bal-keep − PE+bal-keep | random 20 prepend | 1% FPR | malware TPR, fit subset | +1.62 | 4.11 | [+1.12, +2.11] | 7/3 | **yes** | [-0.18, +2.80] | no |
| ATT+bal-keep − PE+bal-keep | random 20 prepend | 0.1% FPR | malware TPR | +0.40 | 5.95 | [-0.03, +0.79] | 6/4 | no | [-4.39, +4.44] | no |
| ATT+bal-keep − PE+bal-keep | random 20 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.05 | [-0.03, +0.03] | 4/5 | no | [-0.04, +0.03] | no |
| ATT+bal-keep − PE+bal-keep | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +7.82 | 7.98 | [+6.94, +8.59] | 9/1 | **yes** | [+3.14, +10.47] | yes |
| ATT+bal-keep − PE+bal-keep | random 50 prepend | 1% FPR | malware TPR | +1.42 | 4.92 | [+1.07, +1.76] | 6/4 | no | [-0.98, +3.17] | no |
| ATT+bal-keep − PE+bal-keep | random 50 prepend | 1% FPR | padded-benign FPR | -1.35 | 1.22 | [-1.51, -1.19] | 1/9 | **yes** | [-1.89, -0.87] | yes |
| ATT+bal-keep − PE+bal-keep | random 50 prepend | 1% FPR | malware TPR, fit subset | -1.25 | 9.82 | [-2.28, -0.30] | 4/6 | no | [-7.95, +3.21] | no |
| ATT+bal-keep − PE+bal-keep | random 50 prepend | 0.1% FPR | malware TPR | +7.03 | 6.30 | [+6.61, +7.44] | 8/2 | **yes** | [+2.57, +12.04] | yes |
| ATT+bal-keep − PE+bal-keep | random 50 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.01 | [-0.02, +0.00] | 1/5 | no | [-0.02, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | random 50 prepend | 0.1% FPR | malware TPR, fit subset | -1.93 | 4.76 | [-2.74, -1.19] | 5/5 | no | [-4.41, +1.48] | no |

**Table 2b. Surrogate-chosen padding: calls of rank 1..k from the LightGBM or the v2-PE surrogate (insert and prepend).** 

| model | edit | malware TPR @1% | padded-benign FPR @1% | malware TPR @0.1% | padded-benign FPR @0.1% | malware that fit in 512 | TPR @1%, fit subset | TPR @0.1%, fit subset |
|---|---|---|---|---|---|---|---|---|
| released checkpoint | lgbm 5 insert | 64.2 | 0.8 | 34.3 | 0.0 | 30.1% | 42.6 | 14.1 |
| released checkpoint | lgbm 5 prepend | 28.0 | 0.3 | 3.7 | 0.0 | 30.1% | 20.5 | 0.7 |
| released checkpoint | lgbm 20 insert | 42.1 | 1.0 | 22.8 | 0.0 | 20.3% | 3.1 | 0.3 |
| released checkpoint | lgbm 20 prepend | 2.8 | 0.5 | 1.2 | 0.0 | 20.3% | 0.1 | 0.0 |
| released checkpoint | lgbm 50 insert | 28.8 | 2.0 | 12.8 | 0.0 | 15.4% | 0.0 | 0.0 |
| released checkpoint | lgbm 50 prepend | 3.2 | 0.1 | 2.0 | 0.0 | 15.4% | 0.0 | 0.0 |
| released checkpoint | v2pe 5 insert | 41.2 | 2.3 | 21.6 | 0.0 | 18.8% | 12.6 | 1.5 |
| released checkpoint | v2pe 5 prepend | 19.2 | 14.2 | 2.4 | 0.0 | 18.8% | 44.9 | 0.1 |
| released checkpoint | v2pe 20 insert | 41.8 | 30.7 | 9.8 | 0.3 | 14.2% | 33.8 | 0.0 |
| released checkpoint | v2pe 20 prepend | 28.6 | 66.1 | 7.8 | 0.0 | 14.2% | 1.7 | 0.0 |
| released checkpoint | v2pe 50 insert | 65.6 | 59.3 | 7.0 | 0.3 | 0.0% | n/a | n/a |
| released checkpoint | v2pe 50 prepend | 100.0 | 100.0 | 15.0 | 1.9 | 0.0% | n/a | n/a |
| v2-PE | lgbm 5 insert | 63.8 ± 5.7 | 0.4 ± 0.1 | 30.7 ± 5.3 | 0.0 ± 0.0 | 30.2% | 44.0 | 14.3 |
| v2-PE | lgbm 5 prepend | 34.8 ± 10.6 | 0.3 ± 0.4 | 7.2 ± 4.1 | 0.0 ± 0.0 | 30.2% | 21.6 | 2.3 |
| v2-PE | lgbm 20 insert | 40.3 ± 6.5 | 0.2 ± 0.1 | 13.8 ± 4.7 | 0.0 ± 0.0 | 23.9% | 9.0 | 0.5 |
| v2-PE | lgbm 20 prepend | 10.2 ± 7.0 | 0.1 ± 0.4 | 1.6 ± 2.0 | 0.0 | 23.9% | 1.0 | 0.0 |
| v2-PE | lgbm 50 insert | 21.7 ± 4.7 | 0.1 ± 0.1 | 6.2 ± 3.9 | 0.0 | 15.4% | 0.0 | 0.0 |
| v2-PE | lgbm 50 prepend | 3.3 ± 2.4 | 0.0 | 0.4 ± 1.1 | 0.0 | 15.4% | 0.0 | 0.0 |
| v2-PE | v2pe 5 insert | 40.9 ± 4.2 | 0.2 ± 0.1 | 18.0 ± 4.0 | 0.0 ± 0.0 | 19.1% | 4.1 | 0.2 |
| v2-PE | v2pe 5 prepend | 9.8 ± 7.6 | 0.0 ± 0.1 | 0.7 ± 0.8 | 0.0 | 19.1% | 2.5 | 0.0 |
| v2-PE | v2pe 20 insert | 17.3 ± 4.8 | 0.1 ± 0.1 | 5.3 ± 3.2 | 0.0 ± 0.0 | 14.9% | 0.0 | 0.0 |
| v2-PE | v2pe 20 prepend | 2.7 ± 2.9 | 0.0 | 0.3 ± 0.7 | 0.0 | 14.9% | 0.0 | 0.0 |
| v2-PE | v2pe 50 insert | 7.7 ± 3.7 | 0.0 ± 0.1 | 1.8 ± 2.1 | 0.0 | 0.0% | n/a | n/a |
| v2-PE | v2pe 50 prepend | 3.1 ± 3.3 | 0.0 | 0.4 ± 0.9 | 0.0 | 0.0% | n/a | n/a |
| PE+bal | lgbm 5 insert | 77.3 ± 1.7 | 0.9 ± 0.2 | 54.2 ± 6.9 | 0.1 ± 0.0 | 30.2% | 71.8 | 51.8 |
| PE+bal | lgbm 5 prepend | 76.2 ± 2.1 | 1.1 ± 0.8 | 51.3 ± 8.1 | 0.1 ± 0.0 | 30.2% | 72.4 | 48.9 |
| PE+bal | lgbm 20 insert | 69.9 ± 2.8 | 0.7 ± 0.5 | 42.8 ± 7.1 | 0.0 ± 0.0 | 23.9% | 52.2 | 19.8 |
| PE+bal | lgbm 20 prepend | 71.1 ± 3.5 | 0.8 ± 0.6 | 37.2 ± 10.3 | 0.1 ± 0.1 | 23.9% | 66.9 | 20.9 |
| PE+bal | lgbm 50 insert | 58.8 ± 2.1 | 0.5 ± 0.5 | 30.6 ± 5.4 | 0.0 ± 0.0 | 15.4% | 6.2 | 0.3 |
| PE+bal | lgbm 50 prepend | 10.0 ± 3.6 | 0.0 ± 0.0 | 0.5 ± 0.6 | 0.0 | 15.4% | 7.5 | 0.4 |
| PE+bal | v2pe 5 insert | 66.8 ± 2.5 | 0.5 ± 0.3 | 34.0 ± 8.0 | 0.0 ± 0.0 | 19.1% | 45.5 | 8.5 |
| PE+bal | v2pe 5 prepend | 68.2 ± 3.5 | 1.7 ± 3.7 | 30.4 ± 13.5 | 0.1 ± 0.1 | 19.1% | 54.4 | 8.1 |
| PE+bal | v2pe 20 insert | 47.6 ± 4.6 | 0.3 ± 0.3 | 16.3 ± 6.0 | 0.0 ± 0.0 | 14.9% | 3.8 | 0.0 |
| PE+bal | v2pe 20 prepend | 6.0 ± 4.6 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 | 14.9% | 13.5 | 0.0 |
| PE+bal | v2pe 50 insert | 26.8 ± 5.4 | 0.2 ± 0.2 | 6.2 ± 3.6 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| PE+bal | v2pe 50 prepend | 2.3 ± 1.1 | 0.0 | 0.0 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | lgbm 5 insert | 77.3 ± 3.7 | 0.8 ± 0.2 | 51.4 ± 6.9 | 0.1 ± 0.0 | 30.2% | 71.3 | 47.6 |
| ATT+bal | lgbm 5 prepend | 77.5 ± 4.6 | 1.0 ± 0.1 | 51.8 ± 7.2 | 0.1 ± 0.0 | 30.2% | 71.0 | 48.9 |
| ATT+bal | lgbm 20 insert | 69.6 ± 6.4 | 0.6 ± 0.3 | 39.0 ± 3.3 | 0.0 ± 0.0 | 23.9% | 51.6 | 16.6 |
| ATT+bal | lgbm 20 prepend | 72.3 ± 5.2 | 0.8 ± 0.5 | 46.8 ± 6.3 | 0.1 ± 0.0 | 23.9% | 61.6 | 26.4 |
| ATT+bal | lgbm 50 insert | 59.0 ± 5.9 | 0.3 ± 0.1 | 29.9 ± 3.2 | 0.0 ± 0.0 | 15.4% | 4.3 | 0.0 |
| ATT+bal | lgbm 50 prepend | 36.5 ± 14.9 | 0.1 ± 0.1 | 5.2 ± 4.7 | 0.0 | 15.4% | 14.9 | 0.1 |
| ATT+bal | v2pe 5 insert | 68.3 ± 6.0 | 0.4 ± 0.1 | 36.1 ± 3.0 | 0.0 ± 0.0 | 19.1% | 43.6 | 6.9 |
| ATT+bal | v2pe 5 prepend | 73.2 ± 2.5 | 0.8 ± 0.6 | 46.8 ± 5.9 | 0.1 ± 0.0 | 19.1% | 60.8 | 15.4 |
| ATT+bal | v2pe 20 insert | 51.9 ± 5.0 | 0.2 ± 0.1 | 24.0 ± 2.5 | 0.0 ± 0.0 | 14.9% | 1.5 | 0.0 |
| ATT+bal | v2pe 20 prepend | 23.8 ± 8.6 | 0.0 ± 0.0 | 1.2 ± 0.8 | 0.0 | 14.9% | 5.3 | 0.0 |
| ATT+bal | v2pe 50 insert | 33.9 ± 5.4 | 0.1 ± 0.1 | 12.5 ± 1.6 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal | v2pe 50 prepend | 4.2 ± 1.4 | 0.0 | 1.1 ± 0.8 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-keep | lgbm 5 insert | 77.2 ± 1.9 | 0.7 ± 0.1 | 45.5 ± 4.3 | 0.1 ± 0.0 | 30.2% | 70.5 | 41.7 |
| ATT+bal-keep | lgbm 5 prepend | 76.7 ± 2.0 | 0.8 ± 0.2 | 43.9 ± 5.9 | 0.1 ± 0.0 | 30.2% | 71.0 | 39.3 |
| ATT+bal-keep | lgbm 20 insert | 69.5 ± 4.6 | 0.6 ± 0.7 | 33.4 ± 3.6 | 0.0 ± 0.0 | 23.9% | 49.8 | 9.4 |
| ATT+bal-keep | lgbm 20 prepend | 71.2 ± 5.8 | 2.1 ± 4.3 | 37.6 ± 6.7 | 0.1 ± 0.0 | 23.9% | 61.0 | 19.0 |
| ATT+bal-keep | lgbm 50 insert | 57.0 ± 3.7 | 0.2 ± 0.1 | 25.0 ± 3.6 | 0.0 ± 0.0 | 15.4% | 2.7 | 0.0 |
| ATT+bal-keep | lgbm 50 prepend | 27.1 ± 12.8 | 0.1 ± 0.1 | 2.3 ± 3.1 | 0.0 | 15.4% | 7.7 | 0.0 |
| ATT+bal-keep | v2pe 5 insert | 67.0 ± 3.7 | 0.4 ± 0.1 | 30.3 ± 4.1 | 0.0 ± 0.0 | 19.1% | 40.8 | 4.5 |
| ATT+bal-keep | v2pe 5 prepend | 71.3 ± 1.6 | 0.7 ± 0.2 | 39.1 ± 6.3 | 0.1 ± 0.0 | 19.1% | 57.5 | 14.2 |
| ATT+bal-keep | v2pe 20 insert | 47.9 ± 4.6 | 0.2 ± 0.1 | 18.0 ± 3.4 | 0.0 ± 0.0 | 14.9% | 0.6 | 0.0 |
| ATT+bal-keep | v2pe 20 prepend | 15.9 ± 11.5 | 0.0 ± 0.0 | 0.9 ± 0.9 | 0.0 | 14.9% | 3.5 | 0.0 |
| ATT+bal-keep | v2pe 50 insert | 28.2 ± 4.8 | 0.1 ± 0.1 | 8.1 ± 2.4 | 0.0 | 0.0% | n/a | n/a |
| ATT+bal-keep | v2pe 50 prepend | 3.3 ± 1.7 | 0.0 | 0.8 ± 0.8 | 0.0 | 0.0% | n/a | n/a |
| PE+bal-keep | lgbm 5 insert | 77.8 ± 1.9 | 0.9 ± 0.3 | 47.9 ± 6.4 | 0.1 ± 0.0 | 30.2% | 69.9 | 38.6 |
| PE+bal-keep | lgbm 5 prepend | 76.5 ± 3.5 | 0.8 ± 0.4 | 40.5 ± 7.6 | 0.1 ± 0.0 | 30.2% | 69.3 | 33.5 |
| PE+bal-keep | lgbm 20 insert | 69.0 ± 4.6 | 0.7 ± 0.6 | 35.9 ± 4.6 | 0.0 ± 0.0 | 23.9% | 46.4 | 12.5 |
| PE+bal-keep | lgbm 20 prepend | 70.7 ± 4.3 | 1.0 ± 0.8 | 28.9 ± 11.0 | 0.1 ± 0.0 | 23.9% | 62.9 | 13.0 |
| PE+bal-keep | lgbm 50 insert | 56.6 ± 5.6 | 0.4 ± 0.3 | 24.7 ± 5.0 | 0.0 ± 0.0 | 15.4% | 2.8 | 0.0 |
| PE+bal-keep | lgbm 50 prepend | 6.6 ± 4.8 | 0.0 | 0.1 ± 0.2 | 0.0 | 15.4% | 4.2 | 0.4 |
| PE+bal-keep | v2pe 5 insert | 64.1 ± 4.6 | 0.5 ± 0.3 | 26.9 ± 3.3 | 0.0 ± 0.0 | 19.1% | 34.5 | 2.1 |
| PE+bal-keep | v2pe 5 prepend | 68.5 ± 4.2 | 1.8 ± 3.5 | 25.4 ± 7.0 | 0.0 ± 0.0 | 19.1% | 55.1 | 3.4 |
| PE+bal-keep | v2pe 20 insert | 43.8 ± 4.5 | 0.2 ± 0.2 | 11.3 ± 3.1 | 0.0 ± 0.0 | 14.9% | 0.6 | 0.0 |
| PE+bal-keep | v2pe 20 prepend | 4.2 ± 4.2 | 0.0 ± 0.0 | 0.1 ± 0.5 | 0.0 | 14.9% | 5.7 | 0.0 |
| PE+bal-keep | v2pe 50 insert | 24.1 ± 4.0 | 0.1 ± 0.1 | 4.1 ± 1.9 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| PE+bal-keep | v2pe 50 prepend | 2.3 ± 1.7 | 0.0 | 0.1 ± 0.5 | 0.0 | 0.0% | n/a | n/a |

**Table 2b comparisons: A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; resolved = CI excludes 0 and ≥ 7 of 10 seeds with the same sign.**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | resolved | CI (cluster bootstrap) | resolved (cluster) |
|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal − PE+bal | lgbm 5 insert | 1% FPR | malware TPR | -0.03 | 4.53 | [-0.22, +0.17] | 7/3 | no | [-1.33, +1.18] | no |
| ATT+bal − PE+bal | lgbm 5 insert | 1% FPR | padded-benign FPR | -0.07 | 0.22 | [-0.16, +0.02] | 4/4 | no | [-0.22, +0.08] | no |
| ATT+bal − PE+bal | lgbm 5 insert | 1% FPR | malware TPR, fit subset | -0.48 | 7.43 | [-0.87, -0.11] | 7/3 | **yes** | [-2.68, +1.56] | no |
| ATT+bal − PE+bal | lgbm 5 insert | 0.1% FPR | malware TPR | -2.78 | 10.75 | [-3.16, -2.37] | 6/4 | no | [-7.31, +0.94] | no |
| ATT+bal − PE+bal | lgbm 5 insert | 0.1% FPR | padded-benign FPR | -0.03 | 0.04 | [-0.06, +0.00] | 2/7 | no | [-0.07, +0.01] | no |
| ATT+bal − PE+bal | lgbm 5 insert | 0.1% FPR | malware TPR, fit subset | -4.19 | 12.97 | [-5.04, -3.33] | 4/6 | no | [-13.92, +4.82] | no |
| ATT+bal − PE+bal | lgbm 5 prepend | 1% FPR | malware TPR | +1.23 | 5.55 | [+1.03, +1.47] | 8/2 | **yes** | [-0.44, +3.15] | no |
| ATT+bal − PE+bal | lgbm 5 prepend | 1% FPR | padded-benign FPR | -0.15 | 0.74 | [-0.25, -0.04] | 8/2 | **yes** | [-0.47, +0.15] | no |
| ATT+bal − PE+bal | lgbm 5 prepend | 1% FPR | malware TPR, fit subset | -1.33 | 9.72 | [-1.78, -0.89] | 7/3 | **yes** | [-4.70, +1.86] | no |
| ATT+bal − PE+bal | lgbm 5 prepend | 0.1% FPR | malware TPR | +0.52 | 11.57 | [+0.13, +0.91] | 7/3 | **yes** | [-4.49, +4.72] | no |
| ATT+bal − PE+bal | lgbm 5 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.06 | [-0.03, +0.03] | 4/4 | no | [-0.04, +0.04] | no |
| ATT+bal − PE+bal | lgbm 5 prepend | 0.1% FPR | malware TPR, fit subset | -0.02 | 17.87 | [-0.82, +0.81] | 6/4 | no | [-10.08, +9.11] | no |
| ATT+bal − PE+bal | lgbm 20 insert | 1% FPR | malware TPR | -0.33 | 6.65 | [-0.56, -0.10] | 5/5 | no | [-1.92, +1.20] | no |
| ATT+bal − PE+bal | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.11 | 0.43 | [-0.19, -0.03] | 5/5 | no | [-0.39, +0.11] | no |
| ATT+bal − PE+bal | lgbm 20 insert | 1% FPR | malware TPR, fit subset | -0.60 | 13.54 | [-1.28, +0.01] | 6/4 | no | [-4.87, +1.94] | no |
| ATT+bal − PE+bal | lgbm 20 insert | 0.1% FPR | malware TPR | -3.74 | 7.91 | [-4.10, -3.39] | 4/6 | no | [-8.15, +0.28] | no |
| ATT+bal − PE+bal | lgbm 20 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.03 | [-0.03, +0.00] | 3/7 | no | [-0.04, +0.00] | no |
| ATT+bal − PE+bal | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | -3.27 | 7.67 | [-3.97, -2.59] | 3/7 | **yes** | [-5.90, +0.52] | no |
| ATT+bal − PE+bal | lgbm 20 prepend | 1% FPR | malware TPR | +1.26 | 5.78 | [+0.98, +1.52] | 8/2 | **yes** | [-1.03, +3.88] | no |
| ATT+bal − PE+bal | lgbm 20 prepend | 1% FPR | padded-benign FPR | -0.03 | 0.74 | [-0.10, +0.03] | 4/6 | no | [-0.23, +0.13] | no |
| ATT+bal − PE+bal | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | -5.23 | 10.40 | [-5.94, -4.54] | 2/8 | **yes** | [-10.22, -0.25] | yes |
| ATT+bal − PE+bal | lgbm 20 prepend | 0.1% FPR | malware TPR | +9.64 | 11.11 | [+9.26, +10.05] | 8/2 | **yes** | [+4.17, +14.97] | yes |
| ATT+bal − PE+bal | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.06 | [-0.02, +0.01] | 2/6 | no | [-0.03, +0.01] | no |
| ATT+bal − PE+bal | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +5.51 | 15.32 | [+4.61, +6.52] | 7/3 | **yes** | [-6.49, +19.53] | no |
| ATT+bal − PE+bal | lgbm 50 insert | 1% FPR | malware TPR | +0.22 | 6.00 | [-0.02, +0.47] | 7/3 | no | [-1.69, +2.17] | no |
| ATT+bal − PE+bal | lgbm 50 insert | 1% FPR | padded-benign FPR | -0.16 | 0.47 | [-0.22, -0.10] | 5/5 | no | [-0.46, +0.08] | no |
| ATT+bal − PE+bal | lgbm 50 insert | 1% FPR | malware TPR, fit subset | -1.91 | 5.88 | [-2.45, -1.37] | 4/6 | no | [-4.13, +0.09] | no |
| ATT+bal − PE+bal | lgbm 50 insert | 0.1% FPR | malware TPR | -0.70 | 6.07 | [-1.06, -0.36] | 6/4 | no | [-3.89, +2.91] | no |
| ATT+bal − PE+bal | lgbm 50 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.03 | [-0.02, +0.00] | 3/6 | no | [-0.02, +0.00] | no |
| ATT+bal − PE+bal | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | -0.26 | 0.26 | [-0.42, -0.12] | 0/9 | **yes** | [-0.82, -0.03] | yes |
| ATT+bal − PE+bal | lgbm 50 prepend | 1% FPR | malware TPR | +26.55 | 14.85 | [+25.94, +27.24] | 9/1 | **yes** | [+15.90, +35.13] | yes |
| ATT+bal − PE+bal | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.07 | 0.06 | [+0.04, +0.11] | 8/0 | **yes** | [+0.03, +0.13] | yes |
| ATT+bal − PE+bal | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +7.43 | 16.78 | [+6.62, +8.21] | 6/4 | no | [-1.32, +13.22] | no |
| ATT+bal − PE+bal | lgbm 50 prepend | 0.1% FPR | malware TPR | +4.71 | 4.79 | [+4.43, +4.98] | 8/1 | **yes** | [+1.36, +9.78] | yes |
| ATT+bal − PE+bal | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − PE+bal | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | -0.25 | 0.72 | [-0.38, -0.10] | 5/3 | no | [-0.78, +0.03] | no |
| ATT+bal − PE+bal | v2pe 5 insert | 1% FPR | malware TPR | +1.45 | 5.98 | [+1.18, +1.72] | 8/2 | **yes** | [+0.07, +3.12] | yes |
| ATT+bal − PE+bal | v2pe 5 insert | 1% FPR | padded-benign FPR | -0.07 | 0.25 | [-0.13, +0.00] | 5/5 | no | [-0.21, +0.07] | no |
| ATT+bal − PE+bal | v2pe 5 insert | 1% FPR | malware TPR, fit subset | -1.90 | 10.70 | [-2.64, -1.25] | 3/7 | **yes** | [-3.80, +0.78] | no |
| ATT+bal − PE+bal | v2pe 5 insert | 0.1% FPR | malware TPR | +2.12 | 8.33 | [+1.76, +2.48] | 8/2 | **yes** | [-1.10, +5.54] | no |
| ATT+bal − PE+bal | v2pe 5 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.02 | [-0.02, +0.00] | 4/6 | no | [-0.02, +0.00] | no |
| ATT+bal − PE+bal | v2pe 5 insert | 0.1% FPR | malware TPR, fit subset | -1.59 | 11.87 | [-2.40, -0.77] | 8/2 | **yes** | [-7.31, +9.24] | no |
| ATT+bal − PE+bal | v2pe 5 prepend | 1% FPR | malware TPR | +5.05 | 4.87 | [+4.78, +5.30] | 9/1 | **yes** | [+3.08, +7.38] | yes |
| ATT+bal − PE+bal | v2pe 5 prepend | 1% FPR | padded-benign FPR | -0.93 | 3.69 | [-1.03, -0.84] | 6/4 | no | [-2.31, -0.16] | no |
| ATT+bal − PE+bal | v2pe 5 prepend | 1% FPR | malware TPR, fit subset | +6.37 | 16.73 | [+5.72, +7.07] | 6/4 | no | [+2.02, +9.48] | no |
| ATT+bal − PE+bal | v2pe 5 prepend | 0.1% FPR | malware TPR | +16.40 | 16.58 | [+15.97, +16.92] | 9/1 | **yes** | [+10.49, +22.30] | yes |
| ATT+bal − PE+bal | v2pe 5 prepend | 0.1% FPR | padded-benign FPR | +0.03 | 0.08 | [+0.00, +0.07] | 7/1 | **yes** | [-0.00, +0.08] | no |
| ATT+bal − PE+bal | v2pe 5 prepend | 0.1% FPR | malware TPR, fit subset | +7.33 | 17.95 | [+6.51, +8.25] | 9/1 | **yes** | [+2.15, +17.54] | yes |
| ATT+bal − PE+bal | v2pe 20 insert | 1% FPR | malware TPR | +4.35 | 7.94 | [+4.03, +4.67] | 7/3 | **yes** | [+1.91, +6.96] | yes |
| ATT+bal − PE+bal | v2pe 20 insert | 1% FPR | padded-benign FPR | -0.12 | 0.30 | [-0.16, -0.08] | 3/6 | no | [-0.27, -0.01] | no |
| ATT+bal − PE+bal | v2pe 20 insert | 1% FPR | malware TPR, fit subset | -2.28 | 5.59 | [-2.72, -1.87] | 4/6 | no | [-4.16, -0.98] | no |
| ATT+bal − PE+bal | v2pe 20 insert | 0.1% FPR | malware TPR | +7.71 | 6.23 | [+7.29, +8.13] | 9/1 | **yes** | [+3.47, +13.58] | yes |
| ATT+bal − PE+bal | v2pe 20 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.01 | [-0.01, +0.00] | 2/4 | no | [-0.02, +0.00] | no |
| ATT+bal − PE+bal | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | -0.04 | 0.09 | [-0.07, -0.01] | 0/2 | no | [-0.13, +0.00] | no |
| ATT+bal − PE+bal | v2pe 20 prepend | 1% FPR | malware TPR | +17.76 | 8.66 | [+17.09, +18.43] | 10/0 | **yes** | [+4.77, +29.84] | yes |
| ATT+bal − PE+bal | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.03 | 0.03 | [+0.01, +0.06] | 8/0 | **yes** | [+0.00, +0.08] | yes |
| ATT+bal − PE+bal | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | -8.20 | 19.40 | [-9.13, -7.23] | 6/3 | no | [-17.87, +5.38] | no |
| ATT+bal − PE+bal | v2pe 20 prepend | 0.1% FPR | malware TPR | +1.17 | 0.84 | [+1.01, +1.34] | 8/1 | **yes** | [+0.30, +2.44] | yes |
| ATT+bal − PE+bal | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − PE+bal | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [+0.00, +0.02] | 1/0 | no | [+0.00, +0.03] | no |
| ATT+bal − PE+bal | v2pe 50 insert | 1% FPR | malware TPR | +7.09 | 8.37 | [+6.74, +7.42] | 8/2 | **yes** | [+3.98, +10.25] | yes |
| ATT+bal − PE+bal | v2pe 50 insert | 1% FPR | padded-benign FPR | -0.03 | 0.18 | [-0.07, +0.01] | 5/5 | no | [-0.13, +0.05] | no |
| ATT+bal − PE+bal | v2pe 50 insert | 0.1% FPR | malware TPR | +6.34 | 3.48 | [+5.97, +6.71] | 10/0 | **yes** | [+2.48, +11.29] | yes |
| ATT+bal − PE+bal | v2pe 50 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.00 | [-0.00, +0.00] | 0/1 | no | [-0.00, +0.00] | no |
| ATT+bal − PE+bal | v2pe 50 prepend | 1% FPR | malware TPR | +1.97 | 1.37 | [+1.75, +2.17] | 8/0 | **yes** | [+0.48, +4.60] | yes |
| ATT+bal − PE+bal | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − PE+bal | v2pe 50 prepend | 0.1% FPR | malware TPR | +1.11 | 0.83 | [+0.95, +1.27] | 8/0 | **yes** | [+0.29, +2.35] | yes |
| ATT+bal − PE+bal | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 insert | 1% FPR | malware TPR | -0.52 | 2.32 | [-0.77, -0.30] | 4/6 | no | [-2.11, +0.80] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 insert | 1% FPR | padded-benign FPR | -0.16 | 0.40 | [-0.25, -0.07] | 4/6 | no | [-0.34, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 insert | 1% FPR | malware TPR, fit subset | +0.62 | 3.21 | [+0.19, +1.10] | 6/4 | no | [-2.01, +1.97] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 insert | 0.1% FPR | malware TPR | -2.46 | 7.71 | [-2.92, -2.02] | 4/6 | no | [-7.56, +2.33] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.04 | [-0.04, +0.02] | 4/6 | no | [-0.05, +0.02] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 insert | 0.1% FPR | malware TPR, fit subset | +3.13 | 14.34 | [+2.55, +3.71] | 7/3 | **yes** | [+0.19, +5.60] | yes |
| ATT+bal-keep − PE+bal-keep | lgbm 5 prepend | 1% FPR | malware TPR | +0.12 | 3.52 | [-0.10, +0.34] | 4/6 | no | [-1.76, +1.57] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 prepend | 1% FPR | padded-benign FPR | -0.00 | 0.53 | [-0.10, +0.09] | 6/4 | no | [-0.25, +0.20] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 prepend | 1% FPR | malware TPR, fit subset | +1.71 | 3.47 | [+1.22, +2.19] | 6/4 | no | [-1.35, +4.06] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 prepend | 0.1% FPR | malware TPR | +3.46 | 7.73 | [+3.04, +3.89] | 7/3 | **yes** | [-1.71, +8.62] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.05 | [-0.01, +0.03] | 6/4 | no | [-0.02, +0.04] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 5 prepend | 0.1% FPR | malware TPR, fit subset | +5.80 | 17.81 | [+5.03, +6.64] | 5/5 | no | [-5.49, +17.54] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 insert | 1% FPR | malware TPR | +0.57 | 5.75 | [+0.29, +0.84] | 6/4 | no | [-1.63, +2.50] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.14 | 1.07 | [-0.23, -0.06] | 3/7 | **yes** | [-0.46, +0.13] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +3.47 | 16.90 | [+2.76, +4.17] | 7/3 | **yes** | [-0.67, +6.84] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 insert | 0.1% FPR | malware TPR | -2.52 | 5.29 | [-2.93, -2.09] | 2/8 | **yes** | [-6.50, +1.32] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.04 | [-0.02, +0.02] | 6/4 | no | [-0.02, +0.02] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | -3.06 | 9.36 | [-3.71, -2.39] | 4/6 | no | [-6.99, +1.76] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 prepend | 1% FPR | malware TPR | +0.55 | 6.45 | [+0.23, +0.85] | 4/6 | no | [-1.92, +2.97] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 prepend | 1% FPR | padded-benign FPR | +1.16 | 4.51 | [+1.03, +1.28] | 6/4 | no | [+0.55, +1.89] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | -1.89 | 17.53 | [-2.74, -1.04] | 3/7 | **yes** | [-7.27, +4.59] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 prepend | 0.1% FPR | malware TPR | +8.62 | 12.35 | [+8.20, +9.06] | 6/4 | no | [+2.19, +15.22] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.02 | 0.08 | [-0.00, +0.04] | 6/4 | no | [-0.00, +0.05] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +5.95 | 10.67 | [+5.20, +6.67] | 6/4 | no | [-2.33, +16.05] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 insert | 1% FPR | malware TPR | +0.38 | 6.27 | [+0.11, +0.67] | 6/4 | no | [-2.03, +2.51] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 insert | 1% FPR | padded-benign FPR | -0.12 | 0.37 | [-0.17, -0.07] | 5/5 | no | [-0.25, -0.02] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 insert | 1% FPR | malware TPR, fit subset | -0.10 | 4.94 | [-0.40, +0.23] | 4/6 | no | [-0.74, +0.41] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 insert | 0.1% FPR | malware TPR | +0.28 | 5.64 | [-0.10, +0.62] | 5/5 | no | [-3.16, +4.23] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.03 | [-0.01, +0.00] | 4/3 | no | [-0.02, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | -0.02 | 0.05 | [-0.05, +0.00] | 0/2 | no | [-0.07, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 prepend | 1% FPR | malware TPR | +20.45 | 13.97 | [+19.89, +21.02] | 9/1 | **yes** | [+11.42, +30.54] | yes |
| ATT+bal-keep − PE+bal-keep | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.05 | 0.08 | [+0.03, +0.08] | 6/0 | no | [+0.03, +0.09] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +3.52 | 13.75 | [+3.08, +3.95] | 6/4 | no | [-1.08, +6.49] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 prepend | 0.1% FPR | malware TPR | +2.17 | 3.14 | [+2.00, +2.33] | 5/1 | no | [+0.62, +4.37] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | -0.38 | 1.33 | [-0.47, -0.28] | 1/1 | no | [-1.06, -0.03] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 5 insert | 1% FPR | malware TPR | +2.88 | 6.10 | [+2.62, +3.16] | 7/3 | **yes** | [+0.68, +5.07] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 5 insert | 1% FPR | padded-benign FPR | -0.06 | 0.41 | [-0.12, +0.00] | 7/3 | no | [-0.17, +0.06] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 5 insert | 1% FPR | malware TPR, fit subset | +6.25 | 19.21 | [+5.39, +7.06] | 7/2 | **yes** | [-0.19, +10.60] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 5 insert | 0.1% FPR | malware TPR | +3.37 | 4.60 | [+3.01, +3.73] | 9/1 | **yes** | [+0.83, +5.90] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 5 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.02, +0.01] | 4/5 | no | [-0.02, +0.01] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 5 insert | 0.1% FPR | malware TPR, fit subset | +2.48 | 2.31 | [+1.86, +3.06] | 9/1 | **yes** | [-0.44, +8.67] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 5 prepend | 1% FPR | malware TPR | +2.81 | 4.68 | [+2.56, +3.07] | 6/4 | no | [+1.23, +4.49] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 5 prepend | 1% FPR | padded-benign FPR | -1.09 | 3.66 | [-1.20, -0.98] | 7/3 | **yes** | [-2.48, -0.24] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 5 prepend | 1% FPR | malware TPR, fit subset | +2.41 | 10.86 | [+1.69, +3.15] | 5/5 | no | [-3.13, +5.82] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 5 prepend | 0.1% FPR | malware TPR | +13.66 | 9.61 | [+13.27, +14.09] | 10/0 | **yes** | [+9.65, +17.08] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 5 prepend | 0.1% FPR | padded-benign FPR | +0.03 | 0.06 | [+0.01, +0.05] | 6/2 | no | [+0.01, +0.06] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 5 prepend | 0.1% FPR | malware TPR, fit subset | +10.81 | 11.01 | [+9.96, +11.69] | 10/0 | **yes** | [+4.61, +20.10] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 20 insert | 1% FPR | malware TPR | +4.15 | 6.72 | [+3.85, +4.44] | 8/2 | **yes** | [+1.83, +6.64] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 20 insert | 1% FPR | padded-benign FPR | -0.01 | 0.19 | [-0.05, +0.03] | 6/4 | no | [-0.07, +0.05] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 20 insert | 1% FPR | malware TPR, fit subset | -0.09 | 0.48 | [-0.26, +0.07] | 4/6 | no | [-0.38, +0.27] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 20 insert | 0.1% FPR | malware TPR | +6.68 | 4.09 | [+6.28, +7.08] | 9/1 | **yes** | [+2.97, +10.95] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [-0.01, +0.01] | 4/3 | no | [-0.01, +0.01] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 20 prepend | 1% FPR | malware TPR | +11.73 | 11.45 | [+11.28, +12.17] | 8/2 | **yes** | [+3.05, +19.36] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.03 | 0.05 | [+0.01, +0.05] | 6/1 | no | [+0.01, +0.07] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | -2.21 | 9.99 | [-2.73, -1.66] | 6/4 | no | [-6.00, +3.89] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 20 prepend | 0.1% FPR | malware TPR | +0.74 | 1.18 | [+0.64, +0.85] | 5/1 | no | [+0.23, +1.49] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [+0.00, +0.02] | 1/0 | no | [+0.00, +0.03] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 50 insert | 1% FPR | malware TPR | +4.13 | 6.40 | [+3.84, +4.43] | 7/3 | **yes** | [+2.41, +6.19] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 50 insert | 1% FPR | padded-benign FPR | +0.04 | 0.10 | [+0.00, +0.07] | 6/2 | no | [+0.00, +0.08] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 50 insert | 0.1% FPR | malware TPR | +3.99 | 2.73 | [+3.67, +4.32] | 9/1 | **yes** | [+1.39, +6.91] | yes |
| ATT+bal-keep − PE+bal-keep | v2pe 50 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.00 | [-0.00, +0.00] | 0/1 | no | [-0.00, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 50 prepend | 1% FPR | malware TPR | +1.01 | 2.24 | [+0.91, +1.11] | 5/3 | no | [+0.38, +2.10] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 50 prepend | 0.1% FPR | malware TPR | +0.66 | 1.08 | [+0.56, +0.76] | 5/1 | no | [+0.16, +1.40] | no |
| ATT+bal-keep − PE+bal-keep | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |

**White-box greedy attack: share of the 500 malware reports still flagged after k prepended calls (mean over seeds; range of seeds in brackets).**

| model | threshold | seeds | k=0 | k=1 | k=2 | k=5 | k=10 | k=20 |
|---|---|---|---|---|---|---|---|---|
| released checkpoint | 1% FPR | 1 | 70.4 | 35.6 | 25.4 | 3.2 | 1.4 | 1.2 |
| released checkpoint | 0.1% FPR | 1 | 49.0 | 9.2 | 1.6 | 0.0 | 0.0 | 0.0 |
| v2-PE | 1% FPR | 3 | 75.6 (74.0–77.6) | 40.1 (31.8–52.2) | 28.3 (24.0–33.0) | 9.0 (3.8–15.8) | 5.1 (2.4–9.4) | 2.2 (1.0–3.6) |
| v2-PE | 0.1% FPR | 3 | 47.5 (44.0–50.0) | 7.7 (6.0–9.6) | 3.6 (1.6–6.4) | 0.7 (0.6–1.0) | 0.6 (0.4–1.0) | 0.2 (0.0–0.4) |
| PE+bal | 1% FPR | 3 | 76.9 (74.6–80.6) | 68.2 (66.0–72.4) | 65.4 (63.2–68.6) | 62.8 (60.0–66.2) | 57.8 (51.0–62.4) | 39.6 (35.6–42.6) |
| PE+bal | 0.1% FPR | 3 | 51.5 (49.8–54.8) | 33.3 (29.2–35.8) | 31.2 (26.6–35.0) | 26.9 (22.2–31.4) | 18.8 (14.0–23.2) | 3.5 (1.6–6.2) |
| ATT+bal | 1% FPR | 3 | 77.7 (75.6–79.6) | 72.3 (70.6–74.2) | 69.9 (64.4–73.4) | 65.5 (60.6–68.4) | 62.5 (58.6–65.8) | 53.3 (51.8–56.2) |
| ATT+bal | 0.1% FPR | 3 | 58.3 (55.6–60.8) | 46.4 (44.4–50.2) | 41.4 (35.8–46.6) | 34.5 (31.6–38.0) | 31.7 (27.6–36.0) | 14.6 (12.2–18.0) |
| ATT+bal-keep | 1% FPR | 3 | 74.8 (74.2–75.6) | 69.8 (69.0–70.4) | 67.9 (66.2–69.0) | 63.8 (60.0–66.6) | 61.6 (59.0–64.8) | 44.7 (40.0–50.0) |
| ATT+bal-keep | 0.1% FPR | 3 | 50.8 (46.8–57.4) | 32.1 (28.8–37.2) | 31.1 (27.6–35.6) | 27.3 (24.8–30.0) | 24.5 (21.2–28.4) | 7.5 (6.2–9.0) |
| PE+bal-keep | 1% FPR | 3 | 76.1 (72.6–80.6) | 70.7 (68.6–73.8) | 65.9 (62.4–68.2) | 62.8 (60.0–66.6) | 56.1 (54.0–59.2) | 41.1 (35.8–50.0) |
| PE+bal-keep | 0.1% FPR | 3 | 41.8 (38.6–44.8) | 26.6 (23.0–30.4) | 22.1 (18.2–26.2) | 17.1 (11.2–21.6) | 11.0 (4.2–16.6) | 2.5 (0.8–4.6) |

**White-box comparisons (points; seeds 0-2 paired; CI = bootstrap over the 500 reports).**

| comparison | threshold | k | mean difference | 95% CI | seeds > 0 |
|---|---|---|---|---|---|
| ATT+bal − PE+bal | 1% FPR | 5 | +2.7 | [+1.1, +4.4] | 2/3 |
| ATT+bal − PE+bal | 1% FPR | 10 | +4.7 | [+3.3, +6.2] | 2/3 |
| ATT+bal − PE+bal | 1% FPR | 20 | +13.7 | [+11.5, +16.1] | 3/3 |
| ATT+bal − PE+bal | 0.1% FPR | 5 | +7.5 | [+5.5, +9.7] | 3/3 |
| ATT+bal − PE+bal | 0.1% FPR | 10 | +12.9 | [+10.7, +15.4] | 3/3 |
| ATT+bal − PE+bal | 0.1% FPR | 20 | +11.1 | [+8.9, +13.3] | 3/3 |
| ATT+bal-keep − PE+bal-keep | 1% FPR | 5 | +1.0 | [-0.4, +2.3] | 1/3 |
| ATT+bal-keep − PE+bal-keep | 1% FPR | 10 | +5.5 | [+3.9, +7.0] | 3/3 |
| ATT+bal-keep − PE+bal-keep | 1% FPR | 20 | +3.6 | [+1.5, +5.7] | 2/3 |
| ATT+bal-keep − PE+bal-keep | 0.1% FPR | 5 | +10.1 | [+7.9, +12.4] | 3/3 |
| ATT+bal-keep − PE+bal-keep | 0.1% FPR | 10 | +13.5 | [+11.0, +15.8] | 3/3 |
| ATT+bal-keep − PE+bal-keep | 0.1% FPR | 20 | +5.0 | [+3.5, +6.7] | 3/3 |

**Table 3b. Shortcut probe: AUC of a logistic regression predicting "padding present" on April reports (padded with probability 0.5), mean ± std over the seeds.**

| model | n seeds | AUC, pooled vector | AUC, 64-d hidden vector | shuffled-label control |
|---|---|---|---|---|
| v2-PE | 10 | 0.9693 ± 0.0011 | 0.7565 ± 0.0251 | 0.498 |
| PE+bal | 10 | 0.9707 ± 0.0020 | 0.7505 ± 0.0194 | 0.496 |
| ATT+bal | 10 | 0.7063 ± 0.0251 | 0.6574 ± 0.0219 | 0.500 |
| PE+aug | 10 | 0.9753 ± 0.0021 | 0.8262 ± 0.0185 | 0.496 |
| ATT+aug | 10 | 0.8130 ± 0.0285 | 0.7694 ± 0.0340 | 0.504 |

