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
| ATT+bal-tuned | random 5 insert | 78.9 ± 1.6 | 1.2 ± 0.2 | 51.2 ± 4.4 | 0.1 ± 0.0 | 30.3% | 73.9 | 48.6 |
| ATT+bal-tuned | random 20 insert | 75.9 ± 1.3 | 1.2 ± 0.2 | 44.5 ± 5.5 | 0.1 ± 0.0 | 27.6% | 71.4 | 36.0 |
| ATT+bal-tuned | random 50 insert | 71.3 ± 1.8 | 1.2 ± 0.3 | 38.6 ± 5.7 | 0.0 ± 0.0 | 17.0% | 47.4 | 7.6 |
| ATT+bal-tuned | random 5 prepend | 79.4 ± 1.4 | 1.4 ± 0.2 | 50.3 ± 5.6 | 0.1 ± 0.0 | 30.3% | 74.1 | 46.2 |
| ATT+bal-tuned | random 20 prepend | 76.8 ± 1.1 | 1.8 ± 0.4 | 50.2 ± 5.6 | 0.1 ± 0.0 | 27.5% | 73.8 | 34.4 |
| ATT+bal-tuned | random 50 prepend | 66.0 ± 2.6 | 2.1 ± 0.8 | 23.7 ± 6.5 | 0.0 ± 0.0 | 17.1% | 51.7 | 6.2 |

**Table 2a comparisons: A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; resolved = CI excludes 0 and ≥ 7 of 10 seeds with the same sign.**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | resolved | CI (cluster bootstrap) | resolved (cluster) |
|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal-tuned − ATT+bal | random 5 insert | 1% FPR | malware TPR | +0.42 | 2.60 | [+0.25, +0.60] | 3/7 | **yes** | [-0.42, +1.39] | no |
| ATT+bal-tuned − ATT+bal | random 5 insert | 1% FPR | padded-benign FPR | +0.13 | 0.24 | [+0.05, +0.21] | 7/3 | **yes** | [+0.03, +0.25] | yes |
| ATT+bal-tuned − ATT+bal | random 5 insert | 1% FPR | malware TPR, fit subset | -0.48 | 4.05 | [-0.88, -0.12] | 2/8 | **yes** | [-2.73, +0.90] | no |
| ATT+bal-tuned − ATT+bal | random 5 insert | 0.1% FPR | malware TPR | -1.66 | 5.11 | [-1.91, -1.41] | 4/6 | no | [-4.58, +1.34] | no |
| ATT+bal-tuned − ATT+bal | random 5 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.03 | [-0.02, +0.02] | 3/3 | no | [-0.02, +0.02] | no |
| ATT+bal-tuned − ATT+bal | random 5 insert | 0.1% FPR | malware TPR, fit subset | -2.76 | 9.07 | [-3.29, -2.21] | 3/7 | **yes** | [-7.01, +0.98] | no |
| ATT+bal-tuned − ATT+bal | random 20 insert | 1% FPR | malware TPR | +0.49 | 3.69 | [+0.33, +0.66] | 3/7 | **yes** | [-0.27, +1.39] | no |
| ATT+bal-tuned − ATT+bal | random 20 insert | 1% FPR | padded-benign FPR | +0.12 | 0.37 | [+0.03, +0.21] | 7/3 | **yes** | [+0.03, +0.24] | yes |
| ATT+bal-tuned − ATT+bal | random 20 insert | 1% FPR | malware TPR, fit subset | -0.14 | 4.47 | [-0.55, +0.25] | 4/6 | no | [-1.31, +1.12] | no |
| ATT+bal-tuned − ATT+bal | random 20 insert | 0.1% FPR | malware TPR | -1.10 | 4.68 | [-1.32, -0.86] | 4/6 | no | [-2.99, +0.58] | no |
| ATT+bal-tuned − ATT+bal | random 20 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.04 | [-0.04, +0.01] | 4/5 | no | [-0.04, +0.01] | no |
| ATT+bal-tuned − ATT+bal | random 20 insert | 0.1% FPR | malware TPR, fit subset | -4.00 | 6.37 | [-4.55, -3.45] | 3/7 | **yes** | [-8.81, +0.00] | no |
| ATT+bal-tuned − ATT+bal | random 50 insert | 1% FPR | malware TPR | -0.59 | 3.33 | [-0.77, -0.41] | 3/7 | **yes** | [-1.94, +0.61] | no |
| ATT+bal-tuned − ATT+bal | random 50 insert | 1% FPR | padded-benign FPR | +0.18 | 0.40 | [+0.10, +0.26] | 7/3 | **yes** | [+0.08, +0.34] | yes |
| ATT+bal-tuned − ATT+bal | random 50 insert | 1% FPR | malware TPR, fit subset | -4.43 | 4.90 | [-5.08, -3.74] | 2/8 | **yes** | [-7.39, +0.05] | no |
| ATT+bal-tuned − ATT+bal | random 50 insert | 0.1% FPR | malware TPR | -1.12 | 5.09 | [-1.34, -0.89] | 6/4 | no | [-2.50, +0.30] | no |
| ATT+bal-tuned − ATT+bal | random 50 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.03, +0.01] | 1/6 | no | [-0.04, +0.01] | no |
| ATT+bal-tuned − ATT+bal | random 50 insert | 0.1% FPR | malware TPR, fit subset | -2.49 | 2.01 | [-2.99, -1.98] | 1/9 | **yes** | [-4.82, -0.71] | yes |
| ATT+bal-tuned − ATT+bal | random 5 prepend | 1% FPR | malware TPR | +0.32 | 2.54 | [+0.15, +0.49] | 4/6 | no | [-0.50, +1.19] | no |
| ATT+bal-tuned − ATT+bal | random 5 prepend | 1% FPR | padded-benign FPR | +0.21 | 0.22 | [+0.12, +0.29] | 9/0 | **yes** | [+0.10, +0.36] | yes |
| ATT+bal-tuned − ATT+bal | random 5 prepend | 1% FPR | malware TPR, fit subset | -0.54 | 4.56 | [-0.93, -0.22] | 2/8 | **yes** | [-2.80, +0.68] | no |
| ATT+bal-tuned − ATT+bal | random 5 prepend | 0.1% FPR | malware TPR | -1.76 | 5.76 | [-2.04, -1.46] | 4/6 | no | [-4.91, +1.10] | no |
| ATT+bal-tuned − ATT+bal | random 5 prepend | 0.1% FPR | padded-benign FPR | -0.00 | 0.06 | [-0.03, +0.02] | 5/4 | no | [-0.04, +0.03] | no |
| ATT+bal-tuned − ATT+bal | random 5 prepend | 0.1% FPR | malware TPR, fit subset | -4.01 | 9.24 | [-4.68, -3.30] | 3/7 | **yes** | [-12.82, +3.50] | no |
| ATT+bal-tuned − ATT+bal | random 20 prepend | 1% FPR | malware TPR | -0.16 | 2.99 | [-0.33, +0.02] | 3/7 | no | [-0.76, +0.39] | no |
| ATT+bal-tuned − ATT+bal | random 20 prepend | 1% FPR | padded-benign FPR | +0.47 | 0.46 | [+0.37, +0.57] | 9/1 | **yes** | [+0.24, +0.83] | yes |
| ATT+bal-tuned − ATT+bal | random 20 prepend | 1% FPR | malware TPR, fit subset | +0.40 | 4.60 | [-0.00, +0.77] | 5/5 | no | [-1.14, +1.86] | no |
| ATT+bal-tuned − ATT+bal | random 20 prepend | 0.1% FPR | malware TPR | -1.54 | 5.58 | [-1.80, -1.26] | 4/6 | no | [-5.27, +1.72] | no |
| ATT+bal-tuned − ATT+bal | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.04 | [-0.01, +0.03] | 5/3 | no | [-0.02, +0.04] | no |
| ATT+bal-tuned − ATT+bal | random 20 prepend | 0.1% FPR | malware TPR, fit subset | -7.49 | 6.83 | [-8.14, -6.81] | 1/9 | **yes** | [-15.85, -0.53] | yes |
| ATT+bal-tuned − ATT+bal | random 50 prepend | 1% FPR | malware TPR | -1.61 | 5.01 | [-1.84, -1.39] | 3/7 | **yes** | [-3.06, -0.09] | yes |
| ATT+bal-tuned − ATT+bal | random 50 prepend | 1% FPR | padded-benign FPR | +0.55 | 1.04 | [+0.44, +0.66] | 7/3 | **yes** | [+0.18, +1.08] | yes |
| ATT+bal-tuned − ATT+bal | random 50 prepend | 1% FPR | malware TPR, fit subset | -3.19 | 10.20 | [-3.89, -2.45] | 1/9 | **yes** | [-5.19, +0.58] | no |
| ATT+bal-tuned − ATT+bal | random 50 prepend | 0.1% FPR | malware TPR | -8.45 | 7.05 | [-8.83, -8.05] | 1/9 | **yes** | [-13.96, -3.62] | yes |
| ATT+bal-tuned − ATT+bal | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.02 | [-0.00, +0.00] | 4/4 | no | [-0.01, +0.01] | no |
| ATT+bal-tuned − ATT+bal | random 50 prepend | 0.1% FPR | malware TPR, fit subset | -3.25 | 4.47 | [-3.71, -2.81] | 3/7 | **yes** | [-5.14, -1.47] | yes |
| ATT+bal-tuned − v2-PE | random 5 insert | 1% FPR | malware TPR | +5.16 | 3.70 | [+4.77, +5.56] | 9/1 | **yes** | [+1.36, +8.28] | yes |
| ATT+bal-tuned − v2-PE | random 5 insert | 1% FPR | padded-benign FPR | +0.32 | 0.21 | [+0.19, +0.47] | 9/1 | **yes** | [+0.16, +0.53] | yes |
| ATT+bal-tuned − v2-PE | random 5 insert | 1% FPR | malware TPR, fit subset | +8.47 | 3.63 | [+7.65, +9.30] | 10/0 | **yes** | [+5.47, +12.02] | yes |
| ATT+bal-tuned − v2-PE | random 5 insert | 0.1% FPR | malware TPR | +11.13 | 5.03 | [+10.47, +11.69] | 10/0 | **yes** | [+4.41, +15.90] | yes |
| ATT+bal-tuned − v2-PE | random 5 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.02 | [-0.00, +0.07] | 9/1 | no | [-0.00, +0.06] | no |
| ATT+bal-tuned − v2-PE | random 5 insert | 0.1% FPR | malware TPR, fit subset | +17.12 | 13.57 | [+16.13, +18.10] | 9/1 | **yes** | [+7.56, +23.96] | yes |
| ATT+bal-tuned − v2-PE | random 20 insert | 1% FPR | malware TPR | +20.25 | 5.18 | [+19.59, +20.89] | 10/0 | **yes** | [+11.52, +29.18] | yes |
| ATT+bal-tuned − v2-PE | random 20 insert | 1% FPR | padded-benign FPR | +0.54 | 0.22 | [+0.40, +0.69] | 10/0 | **yes** | [+0.34, +0.81] | yes |
| ATT+bal-tuned − v2-PE | random 20 insert | 1% FPR | malware TPR, fit subset | +37.25 | 4.79 | [+35.73, +38.71] | 10/0 | **yes** | [+22.09, +52.87] | yes |
| ATT+bal-tuned − v2-PE | random 20 insert | 0.1% FPR | malware TPR | +21.08 | 7.21 | [+20.41, +21.75] | 10/0 | **yes** | [+11.69, +29.38] | yes |
| ATT+bal-tuned − v2-PE | random 20 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.04 | [+0.01, +0.08] | 7/2 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal-tuned − v2-PE | random 20 insert | 0.1% FPR | malware TPR, fit subset | +28.86 | 8.13 | [+27.59, +30.18] | 10/0 | **yes** | [+12.20, +43.60] | yes |
| ATT+bal-tuned − v2-PE | random 50 insert | 1% FPR | malware TPR | +29.89 | 5.18 | [+29.13, +30.60] | 10/0 | **yes** | [+19.82, +38.70] | yes |
| ATT+bal-tuned − v2-PE | random 50 insert | 1% FPR | padded-benign FPR | +0.52 | 0.53 | [+0.37, +0.67] | 8/2 | **yes** | [+0.32, +0.77] | yes |
| ATT+bal-tuned − v2-PE | random 50 insert | 1% FPR | malware TPR, fit subset | +42.10 | 5.20 | [+40.05, +44.01] | 10/0 | **yes** | [+19.43, +59.49] | yes |
| ATT+bal-tuned − v2-PE | random 50 insert | 0.1% FPR | malware TPR | +25.05 | 7.36 | [+24.32, +25.80] | 10/0 | **yes** | [+15.37, +34.11] | yes |
| ATT+bal-tuned − v2-PE | random 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.00, +0.04] | 7/1 | no | [-0.00, +0.04] | no |
| ATT+bal-tuned − v2-PE | random 50 insert | 0.1% FPR | malware TPR, fit subset | +7.35 | 5.28 | [+6.54, +8.23] | 10/0 | **yes** | [+2.72, +15.33] | yes |
| ATT+bal-tuned − v2-PE | random 5 prepend | 1% FPR | malware TPR | +24.94 | 8.38 | [+24.31, +25.57] | 10/0 | **yes** | [+15.57, +34.97] | yes |
| ATT+bal-tuned − v2-PE | random 5 prepend | 1% FPR | padded-benign FPR | +0.39 | 0.32 | [+0.23, +0.55] | 9/1 | **yes** | [+0.09, +0.76] | yes |
| ATT+bal-tuned − v2-PE | random 5 prepend | 1% FPR | malware TPR, fit subset | +27.82 | 7.91 | [+26.60, +29.11] | 10/0 | **yes** | [+11.62, +45.16] | yes |
| ATT+bal-tuned − v2-PE | random 5 prepend | 0.1% FPR | malware TPR | +30.00 | 8.32 | [+29.27, +30.78] | 10/0 | **yes** | [+18.55, +39.62] | yes |
| ATT+bal-tuned − v2-PE | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.04 | [+0.04, +0.14] | 9/0 | **yes** | [+0.04, +0.15] | yes |
| ATT+bal-tuned − v2-PE | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +32.00 | 8.27 | [+30.56, +33.45] | 10/0 | **yes** | [+11.99, +54.73] | yes |
| ATT+bal-tuned − v2-PE | random 20 prepend | 1% FPR | malware TPR | +54.23 | 8.88 | [+53.46, +55.06] | 10/0 | **yes** | [+42.59, +64.06] | yes |
| ATT+bal-tuned − v2-PE | random 20 prepend | 1% FPR | padded-benign FPR | +0.57 | 1.34 | [+0.37, +0.78] | 8/2 | **yes** | [+0.15, +1.13] | yes |
| ATT+bal-tuned − v2-PE | random 20 prepend | 1% FPR | malware TPR, fit subset | +63.77 | 6.00 | [+62.28, +65.32] | 10/0 | **yes** | [+39.40, +76.81] | yes |
| ATT+bal-tuned − v2-PE | random 20 prepend | 0.1% FPR | malware TPR | +44.73 | 6.24 | [+43.88, +45.56] | 10/0 | **yes** | [+31.70, +55.65] | yes |
| ATT+bal-tuned − v2-PE | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.04 | [+0.03, +0.14] | 10/0 | **yes** | [+0.02, +0.16] | yes |
| ATT+bal-tuned − v2-PE | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +33.65 | 4.71 | [+32.13, +35.21] | 10/0 | **yes** | [+12.24, +56.53] | yes |
| ATT+bal-tuned − v2-PE | random 50 prepend | 1% FPR | malware TPR | +57.73 | 4.46 | [+56.84, +58.56] | 10/0 | **yes** | [+45.11, +66.19] | yes |
| ATT+bal-tuned − v2-PE | random 50 prepend | 1% FPR | padded-benign FPR | +0.98 | 1.69 | [+0.77, +1.21] | 8/2 | **yes** | [+0.33, +1.86] | yes |
| ATT+bal-tuned − v2-PE | random 50 prepend | 1% FPR | malware TPR, fit subset | +49.20 | 5.51 | [+47.15, +51.30] | 10/0 | **yes** | [+27.17, +63.76] | yes |
| ATT+bal-tuned − v2-PE | random 50 prepend | 0.1% FPR | malware TPR | +22.20 | 7.85 | [+21.55, +22.90] | 10/0 | **yes** | [+14.89, +29.65] | yes |
| ATT+bal-tuned − v2-PE | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.03 | [-0.01, +0.03] | 6/1 | no | [-0.01, +0.04] | no |
| ATT+bal-tuned − v2-PE | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +6.17 | 1.24 | [+5.17, +7.18] | 10/0 | **yes** | [+1.07, +19.14] | yes |

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
| ATT+bal-tuned | lgbm 5 insert | 77.8 ± 1.3 | 0.8 ± 0.1 | 49.3 ± 4.6 | 0.1 ± 0.0 | 30.2% | 71.4 | 42.3 |
| ATT+bal-tuned | lgbm 5 prepend | 77.5 ± 1.6 | 1.0 ± 0.2 | 49.3 ± 6.7 | 0.1 ± 0.0 | 30.2% | 72.4 | 39.5 |
| ATT+bal-tuned | lgbm 20 insert | 66.1 ± 1.8 | 0.5 ± 0.1 | 37.5 ± 5.3 | 0.0 ± 0.0 | 23.9% | 35.8 | 11.8 |
| ATT+bal-tuned | lgbm 20 prepend | 68.9 ± 2.8 | 0.9 ± 0.5 | 44.8 ± 7.3 | 0.1 ± 0.0 | 23.9% | 48.3 | 22.4 |
| ATT+bal-tuned | lgbm 50 insert | 57.8 ± 2.9 | 0.3 ± 0.1 | 27.4 ± 3.5 | 0.0 ± 0.0 | 15.4% | 1.7 | 0.0 |
| ATT+bal-tuned | lgbm 50 prepend | 31.5 ± 16.8 | 0.1 ± 0.1 | 2.2 ± 1.3 | 0.0 | 15.4% | 12.3 | 0.0 |
| ATT+bal-tuned | v2pe 5 insert | 66.9 ± 3.9 | 0.4 ± 0.1 | 35.4 ± 4.6 | 0.0 ± 0.0 | 19.1% | 34.7 | 4.8 |
| ATT+bal-tuned | v2pe 5 prepend | 72.5 ± 3.4 | 1.3 ± 0.7 | 45.3 ± 6.5 | 0.1 ± 0.0 | 19.1% | 56.8 | 10.2 |
| ATT+bal-tuned | v2pe 20 insert | 51.7 ± 4.5 | 0.2 ± 0.1 | 21.5 ± 5.1 | 0.0 ± 0.0 | 14.9% | 0.3 | 0.0 |
| ATT+bal-tuned | v2pe 20 prepend | 21.4 ± 14.1 | 0.0 ± 0.0 | 1.0 ± 0.8 | 0.0 | 14.9% | 7.0 | 0.0 |
| ATT+bal-tuned | v2pe 50 insert | 33.3 ± 6.1 | 0.1 ± 0.0 | 9.4 ± 3.6 | 0.0 ± 0.0 | 0.0% | n/a | n/a |
| ATT+bal-tuned | v2pe 50 prepend | 4.5 ± 2.1 | 0.0 | 0.9 ± 0.8 | 0.0 | 0.0% | n/a | n/a |

**Table 2b comparisons: A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; resolved = CI excludes 0 and ≥ 7 of 10 seeds with the same sign.**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | resolved | CI (cluster bootstrap) | resolved (cluster) |
|---|---|---|---|---|---|---|---|---|---|---|
| ATT+bal-tuned − ATT+bal | lgbm 5 insert | 1% FPR | malware TPR | +0.55 | 3.12 | [+0.39, +0.71] | 4/6 | no | [-0.25, +1.37] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 insert | 1% FPR | padded-benign FPR | +0.03 | 0.12 | [-0.03, +0.10] | 6/3 | no | [-0.05, +0.12] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 insert | 1% FPR | malware TPR, fit subset | +0.10 | 5.49 | [-0.26, +0.46] | 3/7 | no | [-2.83, +1.81] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 insert | 0.1% FPR | malware TPR | -2.09 | 4.90 | [-2.37, -1.81] | 4/6 | no | [-6.45, +2.05] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.03 | [-0.02, +0.01] | 2/5 | no | [-0.03, +0.01] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 insert | 0.1% FPR | malware TPR, fit subset | -5.31 | 8.33 | [-5.96, -4.65] | 3/7 | **yes** | [-14.73, +1.83] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 prepend | 1% FPR | malware TPR | -0.01 | 3.80 | [-0.17, +0.16] | 1/9 | no | [-1.67, +1.41] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 prepend | 1% FPR | padded-benign FPR | +0.02 | 0.20 | [-0.05, +0.09] | 5/5 | no | [-0.07, +0.14] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 prepend | 1% FPR | malware TPR, fit subset | +1.39 | 8.35 | [+1.01, +1.74] | 2/7 | **yes** | [-2.55, +4.37] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 prepend | 0.1% FPR | malware TPR | -2.56 | 8.81 | [-2.90, -2.22] | 4/6 | no | [-9.21, +2.35] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.05 | [-0.03, +0.01] | 5/5 | no | [-0.04, +0.01] | no |
| ATT+bal-tuned − ATT+bal | lgbm 5 prepend | 0.1% FPR | malware TPR, fit subset | -9.37 | 10.08 | [-10.28, -8.43] | 4/6 | no | [-25.44, +2.79] | no |
| ATT+bal-tuned − ATT+bal | lgbm 20 insert | 1% FPR | malware TPR | -3.53 | 4.95 | [-3.84, -3.22] | 1/9 | **yes** | [-9.58, +0.47] | no |
| ATT+bal-tuned − ATT+bal | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.11 | 0.21 | [-0.17, -0.05] | 3/7 | **yes** | [-0.20, -0.04] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 20 insert | 1% FPR | malware TPR, fit subset | -15.78 | 9.62 | [-16.74, -14.75] | 0/10 | **yes** | [-29.87, -3.65] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 20 insert | 0.1% FPR | malware TPR | -1.53 | 5.07 | [-1.75, -1.30] | 3/7 | **yes** | [-3.25, +0.04] | no |
| ATT+bal-tuned − ATT+bal | lgbm 20 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.04, +0.00] | 1/8 | no | [-0.04, +0.01] | no |
| ATT+bal-tuned − ATT+bal | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | -4.78 | 4.28 | [-5.31, -4.27] | 3/7 | **yes** | [-9.12, -1.56] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 20 prepend | 1% FPR | malware TPR | -3.48 | 3.15 | [-3.74, -3.19] | 1/9 | **yes** | [-8.62, -0.11] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.09 | 0.39 | [+0.02, +0.16] | 4/4 | no | [-0.09, +0.35] | no |
| ATT+bal-tuned − ATT+bal | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | -13.33 | 11.93 | [-14.27, -12.37] | 1/9 | **yes** | [-26.62, -1.77] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 20 prepend | 0.1% FPR | malware TPR | -2.01 | 5.15 | [-2.25, -1.79] | 3/7 | **yes** | [-3.79, -0.51] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.04 | [-0.02, +0.01] | 5/4 | no | [-0.03, +0.01] | no |
| ATT+bal-tuned − ATT+bal | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | -4.05 | 2.98 | [-4.60, -3.49] | 1/9 | **yes** | [-8.26, -1.78] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 50 insert | 1% FPR | malware TPR | -1.19 | 3.52 | [-1.39, -1.00] | 3/7 | **yes** | [-2.74, +0.07] | no |
| ATT+bal-tuned − ATT+bal | lgbm 50 insert | 1% FPR | padded-benign FPR | -0.03 | 0.13 | [-0.06, +0.01] | 4/6 | no | [-0.07, +0.02] | no |
| ATT+bal-tuned − ATT+bal | lgbm 50 insert | 1% FPR | malware TPR, fit subset | -2.59 | 3.27 | [-3.17, -2.04] | 2/8 | **yes** | [-7.09, -0.39] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 50 insert | 0.1% FPR | malware TPR | -2.50 | 3.23 | [-2.72, -2.29] | 2/8 | **yes** | [-4.17, -1.13] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 50 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.01 | [-0.02, +0.00] | 1/5 | no | [-0.02, +0.00] | no |
| ATT+bal-tuned − ATT+bal | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − ATT+bal | lgbm 50 prepend | 1% FPR | malware TPR | -5.05 | 16.39 | [-5.29, -4.81] | 5/5 | no | [-8.16, -1.46] | no |
| ATT+bal-tuned − ATT+bal | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.11 | [-0.02, +0.02] | 4/5 | no | [-0.04, +0.04] | no |
| ATT+bal-tuned − ATT+bal | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | -2.62 | 26.15 | [-3.07, -2.17] | 5/5 | no | [-6.20, -0.92] | no |
| ATT+bal-tuned − ATT+bal | lgbm 50 prepend | 0.1% FPR | malware TPR | -3.00 | 4.06 | [-3.20, -2.79] | 2/7 | **yes** | [-7.89, -0.24] | yes |
| ATT+bal-tuned − ATT+bal | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − ATT+bal | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | -0.06 | 0.18 | [-0.11, -0.03] | 1/3 | no | [-0.20, -0.01] | no |
| ATT+bal-tuned − ATT+bal | v2pe 5 insert | 1% FPR | malware TPR | -1.32 | 4.58 | [-1.52, -1.12] | 3/7 | **yes** | [-4.43, +0.66] | no |
| ATT+bal-tuned − ATT+bal | v2pe 5 insert | 1% FPR | padded-benign FPR | +0.05 | 0.11 | [+0.00, +0.10] | 8/2 | **yes** | [+0.01, +0.11] | yes |
| ATT+bal-tuned − ATT+bal | v2pe 5 insert | 1% FPR | malware TPR, fit subset | -8.92 | 11.22 | [-9.65, -8.17] | 2/8 | **yes** | [-16.94, -0.36] | yes |
| ATT+bal-tuned − ATT+bal | v2pe 5 insert | 0.1% FPR | malware TPR | -0.67 | 4.63 | [-0.90, -0.45] | 5/5 | no | [-2.00, +0.63] | no |
| ATT+bal-tuned − ATT+bal | v2pe 5 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.02 | [-0.01, +0.01] | 3/3 | no | [-0.01, +0.01] | no |
| ATT+bal-tuned − ATT+bal | v2pe 5 insert | 0.1% FPR | malware TPR, fit subset | -2.07 | 1.85 | [-2.43, -1.72] | 2/8 | **yes** | [-5.10, -0.52] | yes |
| ATT+bal-tuned − ATT+bal | v2pe 5 prepend | 1% FPR | malware TPR | -0.72 | 3.99 | [-0.87, -0.57] | 5/5 | no | [-1.88, +0.31] | no |
| ATT+bal-tuned − ATT+bal | v2pe 5 prepend | 1% FPR | padded-benign FPR | +0.46 | 0.68 | [+0.37, +0.56] | 8/2 | **yes** | [+0.02, +1.31] | yes |
| ATT+bal-tuned − ATT+bal | v2pe 5 prepend | 1% FPR | malware TPR, fit subset | -3.94 | 12.02 | [-4.47, -3.41] | 5/5 | no | [-6.95, +1.15] | no |
| ATT+bal-tuned − ATT+bal | v2pe 5 prepend | 0.1% FPR | malware TPR | -1.51 | 3.54 | [-1.78, -1.25] | 4/6 | no | [-3.53, +0.77] | no |
| ATT+bal-tuned − ATT+bal | v2pe 5 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.03, +0.00] | 2/6 | no | [-0.04, +0.01] | no |
| ATT+bal-tuned − ATT+bal | v2pe 5 prepend | 0.1% FPR | malware TPR, fit subset | -5.26 | 8.40 | [-5.70, -4.81] | 2/8 | **yes** | [-7.57, -2.14] | yes |
| ATT+bal-tuned − ATT+bal | v2pe 20 insert | 1% FPR | malware TPR | -0.24 | 3.89 | [-0.42, -0.05] | 5/5 | no | [-1.14, +0.54] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 insert | 1% FPR | padded-benign FPR | +0.06 | 0.07 | [+0.03, +0.09] | 8/2 | **yes** | [+0.02, +0.10] | yes |
| ATT+bal-tuned − ATT+bal | v2pe 20 insert | 1% FPR | malware TPR, fit subset | -1.18 | 1.38 | [-1.51, -0.84] | 1/8 | **yes** | [-3.65, -0.04] | yes |
| ATT+bal-tuned − ATT+bal | v2pe 20 insert | 0.1% FPR | malware TPR | -2.43 | 4.43 | [-2.65, -2.21] | 5/5 | no | [-4.59, -0.63] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [+0.00, +0.01] | 3/0 | no | [+0.00, +0.01] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 prepend | 1% FPR | malware TPR | -2.40 | 10.37 | [-2.61, -2.18] | 5/5 | no | [-6.00, +1.45] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.05 | [-0.01, +0.02] | 3/4 | no | [-0.01, +0.02] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +1.72 | 11.88 | [+1.25, +2.16] | 3/7 | **yes** | [-4.22, +5.57] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 prepend | 0.1% FPR | malware TPR | -0.22 | 0.56 | [-0.25, -0.19] | 3/4 | no | [-0.45, -0.06] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − ATT+bal | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.03 | 0.04 | [+0.00, +0.09] | 4/0 | no | [+0.00, +0.12] | no |
| ATT+bal-tuned − ATT+bal | v2pe 50 insert | 1% FPR | malware TPR | -0.62 | 5.17 | [-0.83, -0.40] | 4/6 | no | [-2.42, +1.62] | no |
| ATT+bal-tuned − ATT+bal | v2pe 50 insert | 1% FPR | padded-benign FPR | +0.00 | 0.04 | [-0.02, +0.03] | 5/5 | no | [-0.02, +0.04] | no |
| ATT+bal-tuned − ATT+bal | v2pe 50 insert | 0.1% FPR | malware TPR | -3.14 | 3.34 | [-3.35, -2.91] | 3/7 | **yes** | [-5.94, -0.83] | yes |
| ATT+bal-tuned − ATT+bal | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − ATT+bal | v2pe 50 prepend | 1% FPR | malware TPR | +0.23 | 2.22 | [+0.17, +0.29] | 5/3 | no | [-0.20, +0.70] | no |
| ATT+bal-tuned − ATT+bal | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − ATT+bal | v2pe 50 prepend | 0.1% FPR | malware TPR | -0.17 | 0.62 | [-0.20, -0.14] | 1/4 | no | [-0.36, -0.04] | no |
| ATT+bal-tuned − ATT+bal | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − v2-PE | lgbm 5 insert | 1% FPR | malware TPR | +14.04 | 6.12 | [+13.44, +14.57] | 10/0 | **yes** | [+7.34, +21.97] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 insert | 1% FPR | padded-benign FPR | +0.44 | 0.21 | [+0.31, +0.56] | 10/0 | **yes** | [+0.28, +0.65] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 insert | 1% FPR | malware TPR, fit subset | +27.38 | 9.49 | [+26.15, +28.54] | 10/0 | **yes** | [+13.92, +43.41] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 insert | 0.1% FPR | malware TPR | +18.64 | 8.21 | [+17.97, +19.33] | 10/0 | **yes** | [+10.32, +26.32] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.04 | [+0.00, +0.07] | 8/2 | **yes** | [+0.00, +0.07] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 insert | 0.1% FPR | malware TPR, fit subset | +27.92 | 11.78 | [+26.77, +29.19] | 10/0 | **yes** | [+13.52, +42.49] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 prepend | 1% FPR | malware TPR | +42.70 | 11.01 | [+41.93, +43.49] | 10/0 | **yes** | [+30.00, +54.32] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 prepend | 1% FPR | padded-benign FPR | +0.71 | 0.41 | [+0.56, +0.87] | 9/1 | **yes** | [+0.37, +1.11] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 prepend | 1% FPR | malware TPR, fit subset | +50.85 | 11.06 | [+49.41, +52.27] | 10/0 | **yes** | [+25.55, +68.97] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 prepend | 0.1% FPR | malware TPR | +42.09 | 8.35 | [+41.31, +42.91] | 10/0 | **yes** | [+29.34, +53.40] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.03 | [+0.04, +0.13] | 10/0 | **yes** | [+0.03, +0.15] | yes |
| ATT+bal-tuned − v2-PE | lgbm 5 prepend | 0.1% FPR | malware TPR, fit subset | +37.27 | 3.84 | [+35.77, +38.85] | 10/0 | **yes** | [+14.14, +60.63] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 insert | 1% FPR | malware TPR | +25.80 | 7.08 | [+25.12, +26.48] | 10/0 | **yes** | [+15.37, +36.95] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 insert | 1% FPR | padded-benign FPR | +0.22 | 0.18 | [+0.14, +0.31] | 9/1 | **yes** | [+0.11, +0.36] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +26.77 | 9.02 | [+25.42, +28.20] | 10/0 | **yes** | [+12.62, +43.66] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 insert | 0.1% FPR | malware TPR | +23.75 | 9.04 | [+23.06, +24.50] | 10/0 | **yes** | [+14.31, +33.26] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.02 | [-0.00, +0.01] | 3/2 | no | [-0.00, +0.01] | no |
| ATT+bal-tuned − v2-PE | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +11.33 | 5.97 | [+10.38, +12.34] | 9/1 | **yes** | [+0.68, +25.57] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 prepend | 1% FPR | malware TPR | +58.62 | 7.59 | [+57.78, +59.39] | 10/0 | **yes** | [+46.59, +69.01] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.73 | 0.46 | [+0.61, +0.86] | 10/0 | **yes** | [+0.47, +1.11] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +47.36 | 10.96 | [+45.71, +49.05] | 10/0 | **yes** | [+28.42, +65.77] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 prepend | 0.1% FPR | malware TPR | +43.19 | 8.78 | [+42.31, +44.05] | 10/0 | **yes** | [+29.69, +54.97] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.07 | 0.04 | [+0.03, +0.12] | 10/0 | **yes** | [+0.02, +0.13] | yes |
| ATT+bal-tuned − v2-PE | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +22.39 | 2.56 | [+20.94, +23.89] | 10/0 | **yes** | [+4.32, +46.09] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 insert | 1% FPR | malware TPR | +36.15 | 6.86 | [+35.33, +36.94] | 10/0 | **yes** | [+22.10, +49.67] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 insert | 1% FPR | padded-benign FPR | +0.21 | 0.15 | [+0.13, +0.30] | 9/1 | **yes** | [+0.10, +0.34] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +1.71 | 2.09 | [+1.38, +2.05] | 9/1 | **yes** | [+0.96, +3.24] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 insert | 0.1% FPR | malware TPR | +21.14 | 6.66 | [+20.43, +21.80] | 10/0 | **yes** | [+10.89, +33.22] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [+0.00, +0.02] | 4/0 | no | [+0.00, +0.02] | no |
| ATT+bal-tuned − v2-PE | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − v2-PE | lgbm 50 prepend | 1% FPR | malware TPR | +28.18 | 17.94 | [+27.50, +28.80] | 9/1 | **yes** | [+19.84, +36.41] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.08 | 0.12 | [+0.05, +0.11] | 8/0 | **yes** | [+0.04, +0.13] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +12.30 | 17.49 | [+11.50, +13.10] | 10/0 | **yes** | [+5.43, +16.62] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 prepend | 0.1% FPR | malware TPR | +1.80 | 2.23 | [+1.58, +2.01] | 9/1 | **yes** | [+0.51, +3.70] | yes |
| ATT+bal-tuned − v2-PE | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − v2-PE | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.04 | 0.04 | [+0.00, +0.13] | 6/0 | no | [+0.00, +0.17] | no |
| ATT+bal-tuned − v2-PE | v2pe 5 insert | 1% FPR | malware TPR | +26.07 | 6.34 | [+25.34, +26.80] | 10/0 | **yes** | [+17.38, +34.42] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 insert | 1% FPR | padded-benign FPR | +0.21 | 0.11 | [+0.13, +0.30] | 10/0 | **yes** | [+0.11, +0.34] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 insert | 1% FPR | malware TPR, fit subset | +30.53 | 12.56 | [+28.96, +32.12] | 10/0 | **yes** | [+18.33, +38.98] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 insert | 0.1% FPR | malware TPR | +17.43 | 6.91 | [+16.73, +18.13] | 10/0 | **yes** | [+10.28, +23.58] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.03 | [-0.01, +0.02] | 4/4 | no | [-0.01, +0.02] | no |
| ATT+bal-tuned − v2-PE | v2pe 5 insert | 0.1% FPR | malware TPR, fit subset | +4.59 | 2.54 | [+3.86, +5.33] | 10/0 | **yes** | [+0.65, +14.14] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 prepend | 1% FPR | malware TPR | +62.68 | 9.64 | [+61.81, +63.46] | 10/0 | **yes** | [+49.84, +72.00] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 prepend | 1% FPR | padded-benign FPR | +1.24 | 0.64 | [+1.07, +1.41] | 10/0 | **yes** | [+0.59, +2.35] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 prepend | 1% FPR | malware TPR, fit subset | +54.34 | 14.44 | [+52.47, +56.19] | 10/0 | **yes** | [+32.80, +69.71] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 prepend | 0.1% FPR | malware TPR | +44.63 | 6.97 | [+43.79, +45.52] | 10/0 | **yes** | [+32.01, +55.86] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 prepend | 0.1% FPR | padded-benign FPR | +0.07 | 0.04 | [+0.03, +0.13] | 9/0 | **yes** | [+0.03, +0.14] | yes |
| ATT+bal-tuned − v2-PE | v2pe 5 prepend | 0.1% FPR | malware TPR, fit subset | +10.16 | 2.74 | [+9.04, +11.50] | 10/0 | **yes** | [+2.84, +26.13] | yes |
| ATT+bal-tuned − v2-PE | v2pe 20 insert | 1% FPR | malware TPR | +34.41 | 7.77 | [+33.59, +35.22] | 10/0 | **yes** | [+22.51, +45.07] | yes |
| ATT+bal-tuned − v2-PE | v2pe 20 insert | 1% FPR | padded-benign FPR | +0.15 | 0.11 | [+0.08, +0.23] | 9/1 | **yes** | [+0.07, +0.25] | yes |
| ATT+bal-tuned − v2-PE | v2pe 20 insert | 1% FPR | malware TPR, fit subset | +0.29 | 0.42 | [+0.15, +0.43] | 7/1 | **yes** | [+0.12, +0.65] | yes |
| ATT+bal-tuned − v2-PE | v2pe 20 insert | 0.1% FPR | malware TPR | +16.27 | 6.99 | [+15.65, +16.89] | 10/0 | **yes** | [+9.00, +23.96] | yes |
| ATT+bal-tuned − v2-PE | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.01 | [-0.00, +0.02] | 4/1 | no | [-0.00, +0.02] | no |
| ATT+bal-tuned − v2-PE | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − v2-PE | v2pe 20 prepend | 1% FPR | malware TPR | +18.68 | 15.71 | [+18.15, +19.21] | 8/2 | **yes** | [+8.48, +27.17] | yes |
| ATT+bal-tuned − v2-PE | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.04 | 0.04 | [+0.02, +0.07] | 6/0 | no | [+0.01, +0.08] | no |
| ATT+bal-tuned − v2-PE | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +7.02 | 12.77 | [+6.40, +7.63] | 10/0 | **yes** | [+3.03, +9.90] | yes |
| ATT+bal-tuned − v2-PE | v2pe 20 prepend | 0.1% FPR | malware TPR | +0.61 | 1.40 | [+0.51, +0.70] | 6/2 | no | [+0.11, +1.34] | no |
| ATT+bal-tuned − v2-PE | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − v2-PE | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.04 | 0.04 | [+0.00, +0.11] | 5/0 | no | [+0.00, +0.15] | no |
| ATT+bal-tuned − v2-PE | v2pe 50 insert | 1% FPR | malware TPR | +25.67 | 8.07 | [+24.95, +26.40] | 10/0 | **yes** | [+16.50, +35.24] | yes |
| ATT+bal-tuned − v2-PE | v2pe 50 insert | 1% FPR | padded-benign FPR | +0.10 | 0.08 | [+0.04, +0.16] | 8/2 | **yes** | [+0.03, +0.20] | yes |
| ATT+bal-tuned − v2-PE | v2pe 50 insert | 0.1% FPR | malware TPR | +7.57 | 5.22 | [+7.16, +8.02] | 9/1 | **yes** | [+3.64, +12.14] | yes |
| ATT+bal-tuned − v2-PE | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 1/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − v2-PE | v2pe 50 prepend | 1% FPR | malware TPR | +1.34 | 4.51 | [+1.19, +1.49] | 5/5 | no | [+0.39, +2.90] | no |
| ATT+bal-tuned − v2-PE | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal-tuned − v2-PE | v2pe 50 prepend | 0.1% FPR | malware TPR | +0.51 | 1.55 | [+0.42, +0.60] | 6/2 | no | [+0.01, +1.22] | no |
| ATT+bal-tuned − v2-PE | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |

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
| ATT+bal-tuned | 1% FPR | 3 | 77.1 (76.8–77.4) | 70.7 (70.2–71.0) | 69.6 (68.6–70.2) | 63.8 (61.0–65.8) | 60.3 (57.2–64.6) | 46.5 (42.4–50.6) |
| ATT+bal-tuned | 0.1% FPR | 3 | 54.1 (50.8–56.6) | 36.8 (31.0–40.6) | 34.9 (29.8–39.2) | 31.8 (26.0–36.2) | 25.9 (19.6–29.2) | 11.6 (7.0–17.4) |

**White-box comparisons (points; seeds 0-2 paired; CI = bootstrap over the 500 reports).**

| comparison | threshold | k | mean difference | 95% CI | seeds > 0 |
|---|---|---|---|---|---|
| ATT+bal-tuned − ATT+bal | 1% FPR | 5 | -1.7 | [-2.7, -0.9] | 1/3 |
| ATT+bal-tuned − ATT+bal | 1% FPR | 10 | -2.2 | [-3.3, -1.1] | 1/3 |
| ATT+bal-tuned − ATT+bal | 1% FPR | 20 | -6.9 | [-8.7, -5.1] | 0/3 |
| ATT+bal-tuned − ATT+bal | 0.1% FPR | 5 | -2.7 | [-4.0, -1.3] | 1/3 |
| ATT+bal-tuned − ATT+bal | 0.1% FPR | 10 | -5.8 | [-7.2, -4.4] | 1/3 |
| ATT+bal-tuned − ATT+bal | 0.1% FPR | 20 | -3.0 | [-4.7, -1.3] | 1/3 |
| ATT+bal-tuned − v2-PE | 1% FPR | 5 | +54.8 | [+50.9, +58.7] | 3/3 |
| ATT+bal-tuned − v2-PE | 1% FPR | 10 | +55.1 | [+51.3, +59.3] | 3/3 |
| ATT+bal-tuned − v2-PE | 1% FPR | 20 | +44.3 | [+40.5, +48.4] | 3/3 |
| ATT+bal-tuned − v2-PE | 0.1% FPR | 5 | +31.1 | [+27.4, +34.8] | 3/3 |
| ATT+bal-tuned − v2-PE | 0.1% FPR | 10 | +25.3 | [+22.1, +28.9] | 3/3 |
| ATT+bal-tuned − v2-PE | 0.1% FPR | 20 | +11.4 | [+9.3, +13.7] | 3/3 |

**Table 3b. Shortcut probe: AUC of a logistic regression predicting "padding present" on April reports (padded with probability 0.5), mean ± std over the seeds.**

| model | n seeds | AUC, pooled vector | AUC, 64-d hidden vector | shuffled-label control |
|---|---|---|---|---|
| v2-PE | 10 | 0.9693 ± 0.0011 | 0.7565 ± 0.0251 | 0.498 |
| PE+bal | 10 | 0.9707 ± 0.0020 | 0.7505 ± 0.0194 | 0.496 |
| ATT+bal | 10 | 0.7063 ± 0.0251 | 0.6574 ± 0.0219 | 0.500 |

