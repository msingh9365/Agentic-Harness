**Table 1, duplicate-aware (cluster bootstrap over hash_apis groups; 1,000 resamples). Difference of the per-seed means in points; the released checkpoint is one model. The claim rule applies to the primary metric only; the other rows are descriptive.**

| difference | metric | mean difference | 95% CI (cluster) | seeds > 0 | outcome |
|---|---|---|---|---|---|
| v2-PE − released checkpoint | pAUC@1e-2 (primary) | +4.59 | [-2.48, +13.20] | 9/10 | not resolved |
| v2-PE − released checkpoint | TPR@1e-2 | +6.13 | [+0.02, +12.81] | 10/10 | CI excludes 0 (descriptive) |
| v2-PE − released checkpoint | TPR@1e-3 | +2.44 | [-10.32, +19.68] | 7/10 | CI contains 0 (descriptive) |
| v2-PE − released checkpoint | AUC | +0.58 | [-0.14, +1.44] | 7/10 | CI contains 0 (descriptive) |
| ATT+bal − released checkpoint | pAUC@1e-2 (primary) | +4.82 | [-4.64, +15.28] | 10/10 | not resolved |
| ATT+bal − released checkpoint | TPR@1e-2 | +4.48 | [-2.88, +12.77] | 9/10 | CI contains 0 (descriptive) |
| ATT+bal − released checkpoint | TPR@1e-3 | +5.35 | [-11.75, +23.70] | 8/10 | CI contains 0 (descriptive) |
| ATT+bal − released checkpoint | AUC | +1.26 | [+0.19, +3.07] | 9/10 | CI excludes 0 (descriptive) |
| ATT+bal − v2-PE | pAUC@1e-2 (primary) | +0.23 | [-4.78, +4.29] | 4/10 | not resolved |
| ATT+bal − v2-PE | TPR@1e-2 | -1.65 | [-7.21, +3.23] | 3/10 | CI contains 0 (descriptive) |
| ATT+bal − v2-PE | TPR@1e-3 | +2.91 | [-5.47, +9.49] | 6/10 | CI contains 0 (descriptive) |
| ATT+bal − v2-PE | AUC | +0.68 | [-0.15, +2.13] | 7/10 | CI contains 0 (descriptive) |

**random padding (REPORT 5.10 procedure, all April reports): A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; resolved = CI excludes 0 and ≥ 7 of 10 seeds with the same sign.**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | resolved | CI (cluster bootstrap) | resolved (cluster) |
|---|---|---|---|---|---|---|---|---|---|---|
| v2-PE − released checkpoint | random 5 insert | 1% FPR | malware TPR | +7.24 | 2.75 | [+6.55, +7.96] | 10/0 | **yes** | [+1.42, +16.06] | yes |
| v2-PE − released checkpoint | random 5 insert | 1% FPR | padded-benign FPR | -0.10 | 0.16 | [-0.35, +0.12] | 1/9 | no | [-0.40, +0.16] | no |
| v2-PE − released checkpoint | random 5 insert | 1% FPR | malware TPR, fit subset | +16.26 | 2.82 | [+14.64, +17.83] | 10/0 | **yes** | [-0.47, +35.43] | no |
| v2-PE − released checkpoint | random 5 insert | 0.1% FPR | malware TPR | +1.21 | 4.83 | [+0.38, +2.00] | 6/4 | no | [-7.87, +11.60] | no |
| v2-PE − released checkpoint | random 5 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [-0.05, +0.05] | 3/3 | no | [-0.05, +0.06] | no |
| v2-PE − released checkpoint | random 5 insert | 0.1% FPR | malware TPR, fit subset | +1.44 | 12.30 | [-0.31, +3.06] | 6/4 | no | [-21.62, +25.02] | no |
| v2-PE − released checkpoint | random 20 insert | 1% FPR | malware TPR | +9.31 | 4.53 | [+8.55, +10.15] | 10/0 | **yes** | [-0.34, +19.37] | no |
| v2-PE − released checkpoint | random 20 insert | 1% FPR | padded-benign FPR | -1.08 | 0.33 | [-1.37, -0.79] | 0/10 | **yes** | [-1.59, -0.67] | yes |
| v2-PE − released checkpoint | random 20 insert | 1% FPR | malware TPR, fit subset | +14.32 | 4.83 | [+12.49, +16.06] | 10/0 | **yes** | [-4.68, +36.65] | no |
| v2-PE − released checkpoint | random 20 insert | 0.1% FPR | malware TPR | +0.39 | 4.88 | [-0.33, +1.11] | 5/5 | no | [-6.52, +7.42] | no |
| v2-PE − released checkpoint | random 20 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.02 | [-0.05, +0.03] | 3/5 | no | [-0.05, +0.03] | no |
| v2-PE − released checkpoint | random 20 insert | 0.1% FPR | malware TPR, fit subset | +1.63 | 4.63 | [+0.73, +2.55] | 5/5 | no | [-4.89, +7.34] | no |
| v2-PE − released checkpoint | random 50 insert | 1% FPR | malware TPR | +5.85 | 4.34 | [+5.00, +6.66] | 10/0 | **yes** | [-1.62, +13.16] | no |
| v2-PE − released checkpoint | random 50 insert | 1% FPR | padded-benign FPR | -3.40 | 0.60 | [-3.83, -2.98] | 0/10 | **yes** | [-4.24, -2.66] | yes |
| v2-PE − released checkpoint | random 50 insert | 1% FPR | malware TPR, fit subset | -3.80 | 2.51 | [-5.17, -2.48] | 1/9 | **yes** | [-6.10, -2.04] | yes |
| v2-PE − released checkpoint | random 50 insert | 0.1% FPR | malware TPR | -1.16 | 3.37 | [-1.78, -0.65] | 5/5 | no | [-6.59, +4.55] | no |
| v2-PE − released checkpoint | random 50 insert | 0.1% FPR | padded-benign FPR | -0.10 | 0.01 | [-0.18, -0.03] | 0/10 | **yes** | [-0.20, -0.04] | yes |
| v2-PE − released checkpoint | random 50 insert | 0.1% FPR | malware TPR, fit subset | -0.58 | 0.23 | [-1.08, -0.18] | 0/10 | **yes** | [-2.05, +0.13] | no |
| v2-PE − released checkpoint | random 5 prepend | 1% FPR | malware TPR | +11.01 | 7.79 | [+10.24, +11.83] | 9/1 | **yes** | [+1.98, +20.61] | yes |
| v2-PE − released checkpoint | random 5 prepend | 1% FPR | padded-benign FPR | -0.80 | 0.21 | [-1.11, -0.52] | 0/10 | **yes** | [-1.22, -0.44] | yes |
| v2-PE − released checkpoint | random 5 prepend | 1% FPR | malware TPR, fit subset | +6.07 | 7.16 | [+4.77, +7.28] | 7/3 | **yes** | [-3.75, +15.59] | no |
| v2-PE − released checkpoint | random 5 prepend | 0.1% FPR | malware TPR | +0.43 | 6.22 | [-0.36, +1.21] | 5/5 | no | [-8.14, +9.83] | no |
| v2-PE − released checkpoint | random 5 prepend | 0.1% FPR | padded-benign FPR | -0.02 | 0.02 | [-0.07, +0.02] | 0/8 | no | [-0.07, +0.02] | no |
| v2-PE − released checkpoint | random 5 prepend | 0.1% FPR | malware TPR, fit subset | -6.52 | 5.82 | [-7.92, -5.18] | 1/9 | **yes** | [-20.65, +7.09] | no |
| v2-PE − released checkpoint | random 20 prepend | 1% FPR | malware TPR | +10.52 | 8.22 | [+9.84, +11.13] | 10/0 | **yes** | [+5.80, +15.76] | yes |
| v2-PE − released checkpoint | random 20 prepend | 1% FPR | padded-benign FPR | -11.27 | 1.34 | [-12.02, -10.55] | 0/10 | **yes** | [-19.16, -5.37] | yes |
| v2-PE − released checkpoint | random 20 prepend | 1% FPR | malware TPR, fit subset | +7.67 | 6.05 | [+6.84, +8.54] | 10/0 | **yes** | [+4.66, +12.63] | yes |
| v2-PE − released checkpoint | random 20 prepend | 0.1% FPR | malware TPR | +3.34 | 2.25 | [+2.98, +3.64] | 10/0 | **yes** | [+1.65, +5.65] | yes |
| v2-PE − released checkpoint | random 20 prepend | 0.1% FPR | padded-benign FPR | -1.08 | 0.03 | [-1.31, -0.86] | 0/10 | **yes** | [-2.11, -0.35] | yes |
| v2-PE − released checkpoint | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.66 | 0.81 | [+0.48, +0.86] | 9/1 | **yes** | [+0.15, +1.55] | yes |
| v2-PE − released checkpoint | random 50 prepend | 1% FPR | malware TPR | -7.97 | 3.47 | [-8.64, -7.34] | 0/10 | **yes** | [-11.02, -5.13] | yes |
| v2-PE − released checkpoint | random 50 prepend | 1% FPR | padded-benign FPR | -12.23 | 1.80 | [-12.96, -11.50] | 0/10 | **yes** | [-14.09, -10.45] | yes |
| v2-PE − released checkpoint | random 50 prepend | 1% FPR | malware TPR, fit subset | -2.82 | 2.57 | [-4.00, -1.78] | 1/9 | **yes** | [-5.78, -1.16] | yes |
| v2-PE − released checkpoint | random 50 prepend | 0.1% FPR | malware TPR | -2.59 | 1.77 | [-2.94, -2.26] | 1/9 | **yes** | [-4.25, -1.34] | yes |
| v2-PE − released checkpoint | random 50 prepend | 0.1% FPR | padded-benign FPR | -0.80 | 0.02 | [-1.01, -0.61] | 0/10 | **yes** | [-1.06, -0.57] | yes |
| v2-PE − released checkpoint | random 50 prepend | 0.1% FPR | malware TPR, fit subset | -0.26 | 0.10 | [-0.55, -0.04] | 0/9 | **yes** | [-0.66, -0.04] | yes |
| ATT+bal − released checkpoint | random 5 insert | 1% FPR | malware TPR | +11.98 | 2.50 | [+11.18, +12.80] | 10/0 | **yes** | [+3.64, +21.30] | yes |
| ATT+bal − released checkpoint | random 5 insert | 1% FPR | padded-benign FPR | +0.09 | 0.16 | [-0.19, +0.33] | 8/2 | no | [-0.22, +0.37] | no |
| ATT+bal − released checkpoint | random 5 insert | 1% FPR | malware TPR, fit subset | +25.21 | 3.52 | [+23.55, +26.83] | 10/0 | **yes** | [+8.54, +43.48] | yes |
| ATT+bal − released checkpoint | random 5 insert | 0.1% FPR | malware TPR | +13.99 | 6.47 | [+13.09, +14.88] | 10/0 | **yes** | [+2.97, +26.67] | yes |
| ATT+bal − released checkpoint | random 5 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.02 | [-0.03, +0.10] | 10/0 | no | [-0.03, +0.10] | no |
| ATT+bal − released checkpoint | random 5 insert | 0.1% FPR | malware TPR, fit subset | +21.32 | 9.04 | [+19.64, +22.88] | 10/0 | **yes** | [-0.09, +46.99] | no |
| ATT+bal − released checkpoint | random 20 insert | 1% FPR | malware TPR | +29.06 | 4.05 | [+28.08, +30.13] | 10/0 | **yes** | [+13.26, +43.36] | yes |
| ATT+bal − released checkpoint | random 20 insert | 1% FPR | padded-benign FPR | -0.66 | 0.33 | [-1.01, -0.34] | 0/10 | **yes** | [-1.13, -0.24] | yes |
| ATT+bal − released checkpoint | random 20 insert | 1% FPR | malware TPR, fit subset | +51.71 | 4.44 | [+49.85, +53.51] | 10/0 | **yes** | [+26.85, +68.13] | yes |
| ATT+bal − released checkpoint | random 20 insert | 0.1% FPR | malware TPR | +22.57 | 4.04 | [+21.57, +23.52] | 10/0 | **yes** | [+9.00, +35.80] | yes |
| ATT+bal − released checkpoint | random 20 insert | 0.1% FPR | padded-benign FPR | +0.05 | 0.03 | [-0.01, +0.10] | 10/0 | no | [-0.01, +0.11] | no |
| ATT+bal − released checkpoint | random 20 insert | 0.1% FPR | malware TPR, fit subset | +34.49 | 7.76 | [+32.89, +36.11] | 10/0 | **yes** | [+12.92, +51.31] | yes |
| ATT+bal − released checkpoint | random 50 insert | 1% FPR | malware TPR | +36.33 | 4.32 | [+35.19, +37.38] | 10/0 | **yes** | [+20.94, +49.91] | yes |
| ATT+bal − released checkpoint | random 50 insert | 1% FPR | padded-benign FPR | -3.06 | 0.39 | [-3.49, -2.59] | 0/10 | **yes** | [-3.88, -2.35] | yes |
| ATT+bal − released checkpoint | random 50 insert | 1% FPR | malware TPR, fit subset | +42.72 | 7.03 | [+40.34, +45.14] | 10/0 | **yes** | [+16.26, +63.23] | yes |
| ATT+bal − released checkpoint | random 50 insert | 0.1% FPR | malware TPR | +25.01 | 4.56 | [+24.01, +25.90] | 10/0 | **yes** | [+12.05, +38.48] | yes |
| ATT+bal − released checkpoint | random 50 insert | 0.1% FPR | padded-benign FPR | -0.08 | 0.01 | [-0.16, -0.01] | 0/10 | **yes** | [-0.19, -0.00] | yes |
| ATT+bal − released checkpoint | random 50 insert | 0.1% FPR | malware TPR, fit subset | +9.26 | 5.34 | [+8.23, +10.30] | 10/0 | **yes** | [+3.39, +17.85] | yes |
| ATT+bal − released checkpoint | random 5 prepend | 1% FPR | malware TPR | +35.64 | 2.86 | [+34.68, +36.57] | 10/0 | **yes** | [+19.40, +51.52] | yes |
| ATT+bal − released checkpoint | random 5 prepend | 1% FPR | padded-benign FPR | -0.62 | 0.12 | [-0.98, -0.30] | 0/10 | **yes** | [-1.02, -0.21] | yes |
| ATT+bal − released checkpoint | random 5 prepend | 1% FPR | malware TPR, fit subset | +34.44 | 4.04 | [+32.56, +36.12] | 10/0 | **yes** | [+12.68, +59.28] | yes |
| ATT+bal − released checkpoint | random 5 prepend | 0.1% FPR | malware TPR | +32.19 | 5.49 | [+31.17, +33.20] | 10/0 | **yes** | [+18.86, +46.17] | yes |
| ATT+bal − released checkpoint | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.06 | 0.04 | [-0.01, +0.13] | 10/0 | no | [-0.00, +0.14] | no |
| ATT+bal − released checkpoint | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +29.48 | 9.45 | [+27.67, +31.21] | 10/0 | **yes** | [+7.43, +52.53] | yes |
| ATT+bal − released checkpoint | random 20 prepend | 1% FPR | malware TPR | +64.91 | 2.83 | [+63.99, +65.84] | 10/0 | **yes** | [+53.16, +73.20] | yes |
| ATT+bal − released checkpoint | random 20 prepend | 1% FPR | padded-benign FPR | -11.18 | 0.29 | [-11.92, -10.41] | 0/10 | **yes** | [-19.02, -5.35] | yes |
| ATT+bal − released checkpoint | random 20 prepend | 1% FPR | malware TPR, fit subset | +71.05 | 4.41 | [+69.34, +72.68] | 10/0 | **yes** | [+46.31, +82.92] | yes |
| ATT+bal − released checkpoint | random 20 prepend | 0.1% FPR | malware TPR | +49.61 | 6.54 | [+48.80, +50.49] | 10/0 | **yes** | [+37.60, +60.20] | yes |
| ATT+bal − released checkpoint | random 20 prepend | 0.1% FPR | padded-benign FPR | -1.01 | 0.03 | [-1.26, -0.79] | 0/10 | **yes** | [-2.05, -0.26] | yes |
| ATT+bal − released checkpoint | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +41.80 | 8.88 | [+40.27, +43.42] | 10/0 | **yes** | [+20.56, +58.68] | yes |
| ATT+bal − released checkpoint | random 50 prepend | 1% FPR | malware TPR | +51.37 | 5.22 | [+50.31, +52.46] | 10/0 | **yes** | [+39.03, +60.33] | yes |
| ATT+bal − released checkpoint | random 50 prepend | 1% FPR | padded-benign FPR | -11.80 | 0.78 | [-12.57, -11.07] | 0/10 | **yes** | [-13.61, -10.08] | yes |
| ATT+bal − released checkpoint | random 50 prepend | 1% FPR | malware TPR, fit subset | +49.58 | 10.56 | [+47.13, +52.20] | 10/0 | **yes** | [+23.42, +66.26] | yes |
| ATT+bal − released checkpoint | random 50 prepend | 0.1% FPR | malware TPR | +28.05 | 5.44 | [+27.31, +28.89] | 10/0 | **yes** | [+18.02, +38.45] | yes |
| ATT+bal − released checkpoint | random 50 prepend | 0.1% FPR | padded-benign FPR | -0.79 | 0.02 | [-1.00, -0.60] | 0/10 | **yes** | [-1.06, -0.56] | yes |
| ATT+bal − released checkpoint | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +9.16 | 4.62 | [+8.03, +10.34] | 10/0 | **yes** | [+2.92, +22.89] | yes |
| ATT+bal − v2-PE | random 5 insert | 1% FPR | malware TPR | +4.74 | 4.12 | [+4.32, +5.14] | 8/2 | **yes** | [+0.27, +8.26] | yes |
| ATT+bal − v2-PE | random 5 insert | 1% FPR | padded-benign FPR | +0.19 | 0.26 | [+0.06, +0.32] | 8/2 | **yes** | [+0.04, +0.38] | yes |
| ATT+bal − v2-PE | random 5 insert | 1% FPR | malware TPR, fit subset | +8.95 | 4.14 | [+8.10, +9.79] | 10/0 | **yes** | [+5.61, +12.98] | yes |
| ATT+bal − v2-PE | random 5 insert | 0.1% FPR | malware TPR | +12.79 | 7.18 | [+12.12, +13.41] | 10/0 | **yes** | [+4.10, +18.31] | yes |
| ATT+bal − v2-PE | random 5 insert | 0.1% FPR | padded-benign FPR | +0.03 | 0.03 | [+0.00, +0.06] | 9/1 | **yes** | [+0.00, +0.06] | yes |
| ATT+bal − v2-PE | random 5 insert | 0.1% FPR | malware TPR, fit subset | +19.88 | 9.71 | [+18.88, +20.77] | 10/0 | **yes** | [+8.45, +26.17] | yes |
| ATT+bal − v2-PE | random 20 insert | 1% FPR | malware TPR | +19.76 | 5.44 | [+19.05, +20.40] | 10/0 | **yes** | [+11.14, +28.68] | yes |
| ATT+bal − v2-PE | random 20 insert | 1% FPR | padded-benign FPR | +0.41 | 0.52 | [+0.26, +0.57] | 9/1 | **yes** | [+0.17, +0.68] | yes |
| ATT+bal − v2-PE | random 20 insert | 1% FPR | malware TPR, fit subset | +37.38 | 5.39 | [+35.87, +38.79] | 10/0 | **yes** | [+21.96, +52.94] | yes |
| ATT+bal − v2-PE | random 20 insert | 0.1% FPR | malware TPR | +22.18 | 5.99 | [+21.43, +22.94] | 10/0 | **yes** | [+11.89, +31.06] | yes |
| ATT+bal − v2-PE | random 20 insert | 0.1% FPR | padded-benign FPR | +0.05 | 0.03 | [+0.01, +0.09] | 9/0 | **yes** | [+0.02, +0.10] | yes |
| ATT+bal − v2-PE | random 20 insert | 0.1% FPR | malware TPR, fit subset | +32.86 | 7.57 | [+31.49, +34.18] | 10/0 | **yes** | [+13.20, +45.35] | yes |
| ATT+bal − v2-PE | random 50 insert | 1% FPR | malware TPR | +30.48 | 5.85 | [+29.69, +31.20] | 10/0 | **yes** | [+20.10, +39.57] | yes |
| ATT+bal − v2-PE | random 50 insert | 1% FPR | padded-benign FPR | +0.34 | 0.74 | [+0.20, +0.48] | 8/2 | **yes** | [+0.15, +0.58] | yes |
| ATT+bal − v2-PE | random 50 insert | 1% FPR | malware TPR, fit subset | +46.53 | 8.20 | [+44.45, +48.57] | 10/0 | **yes** | [+20.97, +66.35] | yes |
| ATT+bal − v2-PE | random 50 insert | 0.1% FPR | malware TPR | +26.17 | 6.55 | [+25.44, +26.91] | 10/0 | **yes** | [+15.79, +36.35] | yes |
| ATT+bal − v2-PE | random 50 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.01 | [+0.00, +0.05] | 9/0 | **yes** | [-0.00, +0.06] | no |
| ATT+bal − v2-PE | random 50 insert | 0.1% FPR | malware TPR, fit subset | +9.84 | 5.39 | [+8.80, +10.90] | 10/0 | **yes** | [+3.51, +20.00] | yes |
| ATT+bal − v2-PE | random 5 prepend | 1% FPR | malware TPR | +24.63 | 7.16 | [+24.01, +25.26] | 10/0 | **yes** | [+15.32, +34.67] | yes |
| ATT+bal − v2-PE | random 5 prepend | 1% FPR | padded-benign FPR | +0.18 | 0.22 | [+0.03, +0.33] | 8/2 | **yes** | [-0.13, +0.52] | no |
| ATT+bal − v2-PE | random 5 prepend | 1% FPR | malware TPR, fit subset | +28.37 | 6.78 | [+27.19, +29.61] | 10/0 | **yes** | [+12.99, +45.24] | yes |
| ATT+bal − v2-PE | random 5 prepend | 0.1% FPR | malware TPR | +31.77 | 6.53 | [+31.07, +32.50] | 10/0 | **yes** | [+20.16, +40.59] | yes |
| ATT+bal − v2-PE | random 5 prepend | 0.1% FPR | padded-benign FPR | +0.09 | 0.04 | [+0.04, +0.14] | 10/0 | **yes** | [+0.04, +0.15] | yes |
| ATT+bal − v2-PE | random 5 prepend | 0.1% FPR | malware TPR, fit subset | +36.01 | 8.68 | [+34.62, +37.29] | 10/0 | **yes** | [+14.98, +53.13] | yes |
| ATT+bal − v2-PE | random 20 prepend | 1% FPR | malware TPR | +54.39 | 8.70 | [+53.64, +55.17] | 10/0 | **yes** | [+43.06, +64.19] | yes |
| ATT+bal − v2-PE | random 20 prepend | 1% FPR | padded-benign FPR | +0.09 | 1.52 | [-0.09, +0.30] | 8/2 | no | [-0.22, +0.47] | no |
| ATT+bal − v2-PE | random 20 prepend | 1% FPR | malware TPR, fit subset | +63.37 | 6.62 | [+61.90, +64.86] | 10/0 | **yes** | [+38.50, +76.35] | yes |
| ATT+bal − v2-PE | random 20 prepend | 0.1% FPR | malware TPR | +46.27 | 6.65 | [+45.48, +47.06] | 10/0 | **yes** | [+34.68, +56.20] | yes |
| ATT+bal − v2-PE | random 20 prepend | 0.1% FPR | padded-benign FPR | +0.07 | 0.04 | [+0.02, +0.13] | 9/1 | **yes** | [+0.01, +0.15] | yes |
| ATT+bal − v2-PE | random 20 prepend | 0.1% FPR | malware TPR, fit subset | +41.14 | 8.94 | [+39.65, +42.74] | 10/0 | **yes** | [+20.05, +58.23] | yes |
| ATT+bal − v2-PE | random 50 prepend | 1% FPR | malware TPR | +59.34 | 7.61 | [+58.44, +60.18] | 10/0 | **yes** | [+46.00, +68.28] | yes |
| ATT+bal − v2-PE | random 50 prepend | 1% FPR | padded-benign FPR | +0.43 | 2.23 | [+0.23, +0.63] | 8/2 | **yes** | [+0.05, +0.87] | yes |
| ATT+bal − v2-PE | random 50 prepend | 1% FPR | malware TPR, fit subset | +52.40 | 11.21 | [+50.27, +54.44] | 10/0 | **yes** | [+28.65, +68.14] | yes |
| ATT+bal − v2-PE | random 50 prepend | 0.1% FPR | malware TPR | +30.65 | 6.35 | [+29.94, +31.49] | 10/0 | **yes** | [+20.34, +41.29] | yes |
| ATT+bal − v2-PE | random 50 prepend | 0.1% FPR | padded-benign FPR | +0.01 | 0.03 | [-0.01, +0.03] | 7/2 | no | [-0.01, +0.04] | no |
| ATT+bal − v2-PE | random 50 prepend | 0.1% FPR | malware TPR, fit subset | +9.42 | 4.64 | [+8.34, +10.55] | 10/0 | **yes** | [+3.32, +23.25] | yes |

**surrogate-chosen padding (LightGBM and v2-PE-seed-0 rankings): A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports (1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; resolved = CI excludes 0 and ≥ 7 of 10 seeds with the same sign.**

| comparison | edit | threshold | rate | mean difference | std over seeds | CI (stratified bootstrap) | seeds >0 / <0 | resolved | CI (cluster bootstrap) | resolved (cluster) |
|---|---|---|---|---|---|---|---|---|---|---|
| v2-PE − released checkpoint | lgbm 5 insert | 1% FPR | malware TPR | -0.45 | 5.67 | [-1.18, +0.34] | 7/3 | no | [-9.75, +10.65] | no |
| v2-PE − released checkpoint | lgbm 5 insert | 1% FPR | padded-benign FPR | -0.44 | 0.13 | [-0.64, -0.26] | 0/10 | **yes** | [-0.75, -0.22] | yes |
| v2-PE − released checkpoint | lgbm 5 insert | 1% FPR | malware TPR, fit subset | +1.36 | 7.83 | [-0.59, +3.25] | 5/5 | no | [-26.87, +29.11] | no |
| v2-PE − released checkpoint | lgbm 5 insert | 0.1% FPR | malware TPR | -3.58 | 5.31 | [-4.30, -2.91] | 3/7 | **yes** | [-10.59, +2.92] | no |
| v2-PE − released checkpoint | lgbm 5 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.03 | [-0.02, +0.03] | 4/3 | no | [-0.02, +0.04] | no |
| v2-PE − released checkpoint | lgbm 5 insert | 0.1% FPR | malware TPR, fit subset | +0.30 | 7.49 | [-0.76, +1.36] | 4/6 | no | [-13.59, +9.79] | no |
| v2-PE − released checkpoint | lgbm 5 prepend | 1% FPR | malware TPR | +6.79 | 10.64 | [+5.88, +7.73] | 7/3 | **yes** | [-6.37, +19.91] | no |
| v2-PE − released checkpoint | lgbm 5 prepend | 1% FPR | padded-benign FPR | -0.03 | 0.40 | [-0.17, +0.11] | 1/9 | no | [-0.27, +0.26] | no |
| v2-PE − released checkpoint | lgbm 5 prepend | 1% FPR | malware TPR, fit subset | +1.09 | 10.07 | [-0.51, +2.59] | 5/5 | no | [-20.99, +26.28] | no |
| v2-PE − released checkpoint | lgbm 5 prepend | 0.1% FPR | malware TPR | +3.46 | 4.09 | [+3.02, +3.87] | 10/0 | **yes** | [+0.70, +7.26] | yes |
| v2-PE − released checkpoint | lgbm 5 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.00 | [-0.04, +0.00] | 0/9 | no | [-0.04, +0.00] | no |
| v2-PE − released checkpoint | lgbm 5 prepend | 0.1% FPR | malware TPR, fit subset | +1.59 | 2.91 | [+1.24, +1.92] | 5/5 | no | [-0.57, +5.16] | no |
| v2-PE − released checkpoint | lgbm 20 insert | 1% FPR | malware TPR | -1.82 | 6.55 | [-2.45, -1.15] | 4/6 | no | [-8.38, +4.12] | no |
| v2-PE − released checkpoint | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.73 | 0.12 | [-0.97, -0.52] | 0/10 | **yes** | [-1.07, -0.46] | yes |
| v2-PE − released checkpoint | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +6.26 | 6.69 | [+5.40, +7.11] | 8/2 | **yes** | [+0.24, +13.76] | yes |
| v2-PE − released checkpoint | lgbm 20 insert | 0.1% FPR | malware TPR | -9.04 | 4.70 | [-9.68, -8.44] | 1/9 | **yes** | [-15.95, -2.76] | yes |
| v2-PE − released checkpoint | lgbm 20 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.01 | [-0.06, +0.01] | 0/9 | no | [-0.06, +0.01] | no |
| v2-PE − released checkpoint | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +0.23 | 1.14 | [-0.00, +0.42] | 2/8 | no | [-0.43, +0.87] | no |
| v2-PE − released checkpoint | lgbm 20 prepend | 1% FPR | malware TPR | +7.42 | 7.03 | [+7.03, +7.79] | 10/0 | **yes** | [+3.31, +12.21] | yes |
| v2-PE − released checkpoint | lgbm 20 prepend | 1% FPR | padded-benign FPR | -0.33 | 0.40 | [-0.50, -0.20] | 1/9 | **yes** | [-0.73, +0.01] | no |
| v2-PE − released checkpoint | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +0.74 | 1.50 | [+0.47, +0.97] | 4/5 | no | [-0.02, +2.09] | no |
| v2-PE − released checkpoint | lgbm 20 prepend | 0.1% FPR | malware TPR | +0.45 | 2.03 | [+0.26, +0.63] | 5/5 | no | [-0.61, +1.78] | no |
| v2-PE − released checkpoint | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.00 | [-0.04, +0.00] | 0/10 | no | [-0.04, +0.00] | no |
| v2-PE − released checkpoint | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE − released checkpoint | lgbm 50 insert | 1% FPR | malware TPR | -7.13 | 4.66 | [-7.77, -6.53] | 1/9 | **yes** | [-11.77, -2.94] | yes |
| v2-PE − released checkpoint | lgbm 50 insert | 1% FPR | padded-benign FPR | -1.90 | 0.09 | [-2.21, -1.61] | 0/10 | **yes** | [-2.72, -1.33] | yes |
| v2-PE − released checkpoint | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [+0.00, +0.02] | 1/0 | no | [+0.00, +0.03] | no |
| v2-PE − released checkpoint | lgbm 50 insert | 0.1% FPR | malware TPR | -6.55 | 3.92 | [-7.08, -6.09] | 1/9 | **yes** | [-13.12, -1.99] | yes |
| v2-PE − released checkpoint | lgbm 50 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.00 | [-0.06, +0.00] | 0/10 | no | [-0.07, +0.00] | no |
| v2-PE − released checkpoint | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE − released checkpoint | lgbm 50 prepend | 1% FPR | malware TPR | +0.06 | 2.36 | [-0.13, +0.23] | 4/6 | no | [-1.19, +1.49] | no |
| v2-PE − released checkpoint | lgbm 50 prepend | 1% FPR | padded-benign FPR | -0.06 | 0.00 | [-0.12, -0.01] | 0/10 | **yes** | [-0.15, +0.00] | no |
| v2-PE − released checkpoint | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE − released checkpoint | lgbm 50 prepend | 0.1% FPR | malware TPR | -1.61 | 1.13 | [-1.86, -1.37] | 1/9 | **yes** | [-3.46, -0.42] | yes |
| v2-PE − released checkpoint | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE − released checkpoint | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE − released checkpoint | v2pe 5 insert | 1% FPR | malware TPR | -0.31 | 4.17 | [-1.01, +0.37] | 5/5 | no | [-4.77, +4.47] | no |
| v2-PE − released checkpoint | v2pe 5 insert | 1% FPR | padded-benign FPR | -2.11 | 0.07 | [-2.46, -1.80] | 0/10 | **yes** | [-2.80, -1.56] | yes |
| v2-PE − released checkpoint | v2pe 5 insert | 1% FPR | malware TPR, fit subset | -8.42 | 2.81 | [-9.86, -6.91] | 0/10 | **yes** | [-13.83, +0.17] | no |
| v2-PE − released checkpoint | v2pe 5 insert | 0.1% FPR | malware TPR | -3.55 | 3.98 | [-4.15, -2.98] | 2/8 | **yes** | [-8.32, +1.10] | no |
| v2-PE − released checkpoint | v2pe 5 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.02 | [-0.07, +0.01] | 0/8 | no | [-0.08, +0.01] | no |
| v2-PE − released checkpoint | v2pe 5 insert | 0.1% FPR | malware TPR, fit subset | -1.30 | 0.23 | [-1.82, -0.82] | 0/10 | **yes** | [-4.24, -0.00] | yes |
| v2-PE − released checkpoint | v2pe 5 prepend | 1% FPR | malware TPR | -9.38 | 7.65 | [-10.14, -8.62] | 1/9 | **yes** | [-20.85, +1.38] | no |
| v2-PE − released checkpoint | v2pe 5 prepend | 1% FPR | padded-benign FPR | -14.12 | 0.06 | [-14.88, -13.37] | 0/10 | **yes** | [-26.08, -5.89] | yes |
| v2-PE − released checkpoint | v2pe 5 prepend | 1% FPR | malware TPR, fit subset | -41.71 | 3.94 | [-44.08, -39.53] | 0/10 | **yes** | [-64.72, -13.30] | yes |
| v2-PE − released checkpoint | v2pe 5 prepend | 0.1% FPR | malware TPR | -1.74 | 0.83 | [-1.98, -1.49] | 0/10 | **yes** | [-3.30, -0.60] | yes |
| v2-PE − released checkpoint | v2pe 5 prepend | 0.1% FPR | padded-benign FPR | -0.01 | 0.00 | [-0.04, +0.00] | 0/10 | no | [-0.05, +0.00] | no |
| v2-PE − released checkpoint | v2pe 5 prepend | 0.1% FPR | malware TPR, fit subset | -0.11 | 0.00 | [-0.28, +0.00] | 0/10 | no | [-0.35, +0.00] | no |
| v2-PE − released checkpoint | v2pe 20 insert | 1% FPR | malware TPR | -24.57 | 4.80 | [-25.56, -23.60] | 0/10 | **yes** | [-33.86, -16.13] | yes |
| v2-PE − released checkpoint | v2pe 20 insert | 1% FPR | padded-benign FPR | -30.55 | 0.08 | [-31.54, -29.45] | 0/10 | **yes** | [-36.76, -24.98] | yes |
| v2-PE − released checkpoint | v2pe 20 insert | 1% FPR | malware TPR, fit subset | -34.86 | 0.03 | [-37.40, -32.38] | 0/10 | **yes** | [-45.01, -29.00] | yes |
| v2-PE − released checkpoint | v2pe 20 insert | 0.1% FPR | malware TPR | -4.52 | 3.16 | [-5.01, -4.00] | 1/9 | **yes** | [-9.31, -0.62] | yes |
| v2-PE − released checkpoint | v2pe 20 insert | 0.1% FPR | padded-benign FPR | -0.28 | 0.01 | [-0.41, -0.18] | 0/10 | **yes** | [-0.43, -0.16] | yes |
| v2-PE − released checkpoint | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE − released checkpoint | v2pe 20 prepend | 1% FPR | malware TPR | -25.87 | 2.91 | [-26.73, -24.97] | 0/10 | **yes** | [-40.57, -13.46] | yes |
| v2-PE − released checkpoint | v2pe 20 prepend | 1% FPR | padded-benign FPR | -66.05 | 0.00 | [-67.03, -65.05] | 0/10 | **yes** | [-75.35, -54.45] | yes |
| v2-PE − released checkpoint | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | -2.07 | 0.00 | [-2.88, -1.36] | 0/10 | **yes** | [-4.95, -0.88] | yes |
| v2-PE − released checkpoint | v2pe 20 prepend | 0.1% FPR | malware TPR | -7.44 | 0.74 | [-7.97, -6.95] | 0/10 | **yes** | [-13.58, -2.86] | yes |
| v2-PE − released checkpoint | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE − released checkpoint | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| v2-PE − released checkpoint | v2pe 50 insert | 1% FPR | malware TPR | -57.97 | 3.66 | [-58.95, -56.98] | 0/10 | **yes** | [-67.69, -47.82] | yes |
| v2-PE − released checkpoint | v2pe 50 insert | 1% FPR | padded-benign FPR | -59.27 | 0.06 | [-60.34, -58.12] | 0/10 | **yes** | [-67.62, -49.65] | yes |
| v2-PE − released checkpoint | v2pe 50 insert | 0.1% FPR | malware TPR | -5.23 | 2.09 | [-5.68, -4.76] | 0/10 | **yes** | [-7.87, -3.10] | yes |
| v2-PE − released checkpoint | v2pe 50 insert | 0.1% FPR | padded-benign FPR | -0.27 | 0.00 | [-0.40, -0.17] | 0/10 | **yes** | [-0.40, -0.16] | yes |
| v2-PE − released checkpoint | v2pe 50 prepend | 1% FPR | malware TPR | -96.89 | 3.26 | [-97.12, -96.65] | 0/10 | **yes** | [-98.37, -94.48] | yes |
| v2-PE − released checkpoint | v2pe 50 prepend | 1% FPR | padded-benign FPR | -100.00 | 0.00 | [-100.00, -100.00] | 0/10 | **yes** | [-100.00, -100.00] | yes |
| v2-PE − released checkpoint | v2pe 50 prepend | 0.1% FPR | malware TPR | -14.54 | 0.92 | [-15.25, -13.88] | 0/10 | **yes** | [-24.07, -7.07] | yes |
| v2-PE − released checkpoint | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | -1.89 | 0.00 | [-2.20, -1.59] | 0/10 | **yes** | [-3.63, -0.77] | yes |
| ATT+bal − released checkpoint | lgbm 5 insert | 1% FPR | malware TPR | +13.03 | 3.68 | [+12.23, +13.82] | 10/0 | **yes** | [+4.63, +22.84] | yes |
| ATT+bal − released checkpoint | lgbm 5 insert | 1% FPR | padded-benign FPR | -0.03 | 0.16 | [-0.27, +0.18] | 3/6 | no | [-0.31, +0.24] | no |
| ATT+bal − released checkpoint | lgbm 5 insert | 1% FPR | malware TPR, fit subset | +28.64 | 7.42 | [+27.06, +30.21] | 10/0 | **yes** | [+11.43, +47.59] | yes |
| ATT+bal − released checkpoint | lgbm 5 insert | 0.1% FPR | malware TPR | +17.16 | 6.88 | [+16.17, +18.04] | 10/0 | **yes** | [+5.15, +28.59] | yes |
| ATT+bal − released checkpoint | lgbm 5 insert | 0.1% FPR | padded-benign FPR | +0.05 | 0.02 | [+0.00, +0.10] | 10/0 | **yes** | [+0.00, +0.10] | yes |
| ATT+bal − released checkpoint | lgbm 5 insert | 0.1% FPR | malware TPR, fit subset | +33.54 | 10.64 | [+32.01, +35.05] | 10/0 | **yes** | [+8.57, +51.62] | yes |
| ATT+bal − released checkpoint | lgbm 5 prepend | 1% FPR | malware TPR | +49.49 | 4.63 | [+48.36, +50.49] | 10/0 | **yes** | [+33.58, +64.39] | yes |
| ATT+bal − released checkpoint | lgbm 5 prepend | 1% FPR | padded-benign FPR | +0.66 | 0.13 | [+0.46, +0.85] | 10/0 | **yes** | [+0.40, +1.00] | yes |
| ATT+bal − released checkpoint | lgbm 5 prepend | 1% FPR | malware TPR, fit subset | +50.55 | 9.67 | [+48.69, +52.42] | 10/0 | **yes** | [+22.08, +75.65] | yes |
| ATT+bal − released checkpoint | lgbm 5 prepend | 0.1% FPR | malware TPR | +48.10 | 7.22 | [+47.23, +49.02] | 10/0 | **yes** | [+35.44, +58.00] | yes |
| ATT+bal − released checkpoint | lgbm 5 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.04 | [+0.02, +0.14] | 10/0 | **yes** | [+0.02, +0.16] | yes |
| ATT+bal − released checkpoint | lgbm 5 prepend | 0.1% FPR | malware TPR, fit subset | +48.23 | 12.43 | [+46.83, +49.75] | 10/0 | **yes** | [+24.73, +61.95] | yes |
| ATT+bal − released checkpoint | lgbm 20 insert | 1% FPR | malware TPR | +27.52 | 6.36 | [+26.60, +28.51] | 10/0 | **yes** | [+12.23, +41.48] | yes |
| ATT+bal − released checkpoint | lgbm 20 insert | 1% FPR | padded-benign FPR | -0.39 | 0.27 | [-0.65, -0.15] | 0/9 | **yes** | [-0.71, -0.13] | yes |
| ATT+bal − released checkpoint | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +48.81 | 12.06 | [+47.28, +50.61] | 10/0 | **yes** | [+27.11, +64.12] | yes |
| ATT+bal − released checkpoint | lgbm 20 insert | 0.1% FPR | malware TPR | +16.24 | 3.27 | [+15.27, +17.16] | 10/0 | **yes** | [+3.16, +29.49] | yes |
| ATT+bal − released checkpoint | lgbm 20 insert | 0.1% FPR | padded-benign FPR | -0.00 | 0.02 | [-0.05, +0.03] | 2/6 | no | [-0.05, +0.04] | no |
| ATT+bal − released checkpoint | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +16.34 | 4.06 | [+15.13, +17.55] | 10/0 | **yes** | [+2.21, +34.11] | yes |
| ATT+bal − released checkpoint | lgbm 20 prepend | 1% FPR | malware TPR | +69.52 | 5.19 | [+68.70, +70.37] | 10/0 | **yes** | [+57.57, +77.53] | yes |
| ATT+bal − released checkpoint | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.31 | 0.49 | [+0.11, +0.51] | 8/2 | **yes** | [-0.08, +0.73] | no |
| ATT+bal − released checkpoint | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +61.43 | 9.79 | [+59.67, +63.22] | 10/0 | **yes** | [+35.76, +75.36] | yes |
| ATT+bal − released checkpoint | lgbm 20 prepend | 0.1% FPR | malware TPR | +45.65 | 6.31 | [+44.80, +46.53] | 10/0 | **yes** | [+32.39, +57.31] | yes |
| ATT+bal − released checkpoint | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.06 | 0.03 | [+0.01, +0.12] | 9/0 | **yes** | [+0.01, +0.14] | yes |
| ATT+bal − released checkpoint | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +26.44 | 3.86 | [+24.90, +27.98] | 10/0 | **yes** | [+7.81, +49.70] | yes |
| ATT+bal − released checkpoint | lgbm 50 insert | 1% FPR | malware TPR | +30.22 | 5.93 | [+29.25, +31.24] | 10/0 | **yes** | [+16.02, +44.11] | yes |
| ATT+bal − released checkpoint | lgbm 50 insert | 1% FPR | padded-benign FPR | -1.66 | 0.14 | [-1.99, -1.36] | 0/10 | **yes** | [-2.45, -1.14] | yes |
| ATT+bal − released checkpoint | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +4.31 | 3.17 | [+3.56, +5.07] | 10/0 | **yes** | [+1.53, +10.31] | yes |
| ATT+bal − released checkpoint | lgbm 50 insert | 0.1% FPR | malware TPR | +17.09 | 3.17 | [+16.27, +17.91] | 10/0 | **yes** | [+5.83, +30.46] | yes |
| ATT+bal − released checkpoint | lgbm 50 insert | 0.1% FPR | padded-benign FPR | -0.01 | 0.02 | [-0.05, +0.02] | 2/8 | no | [-0.06, +0.02] | no |
| ATT+bal − released checkpoint | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − released checkpoint | lgbm 50 prepend | 1% FPR | malware TPR | +33.30 | 14.92 | [+32.58, +34.05] | 10/0 | **yes** | [+22.29, +43.28] | yes |
| ATT+bal − released checkpoint | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.01 | 0.06 | [-0.06, +0.08] | 5/5 | no | [-0.09, +0.11] | no |
| ATT+bal − released checkpoint | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +14.92 | 16.99 | [+13.86, +15.99] | 10/0 | **yes** | [+7.61, +20.57] | yes |
| ATT+bal − released checkpoint | lgbm 50 prepend | 0.1% FPR | malware TPR | +3.19 | 4.74 | [+2.89, +3.45] | 7/3 | **yes** | [-0.15, +8.17] | no |
| ATT+bal − released checkpoint | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − released checkpoint | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.10 | 0.18 | [+0.03, +0.22] | 7/0 | **yes** | [+0.01, +0.33] | yes |
| ATT+bal − released checkpoint | v2pe 5 insert | 1% FPR | malware TPR | +27.09 | 5.99 | [+26.01, +28.04] | 10/0 | **yes** | [+15.93, +37.32] | yes |
| ATT+bal − released checkpoint | v2pe 5 insert | 1% FPR | padded-benign FPR | -1.95 | 0.13 | [-2.29, -1.62] | 0/10 | **yes** | [-2.62, -1.39] | yes |
| ATT+bal − released checkpoint | v2pe 5 insert | 1% FPR | malware TPR, fit subset | +31.02 | 13.23 | [+28.98, +33.24] | 10/0 | **yes** | [+16.52, +40.45] | yes |
| ATT+bal − released checkpoint | v2pe 5 insert | 0.1% FPR | malware TPR | +14.55 | 3.04 | [+13.63, +15.39] | 10/0 | **yes** | [+5.89, +22.98] | yes |
| ATT+bal − released checkpoint | v2pe 5 insert | 0.1% FPR | padded-benign FPR | -0.02 | 0.01 | [-0.07, +0.01] | 0/9 | no | [-0.08, +0.01] | no |
| ATT+bal − released checkpoint | v2pe 5 insert | 0.1% FPR | malware TPR, fit subset | +5.36 | 2.48 | [+4.46, +6.26] | 10/0 | **yes** | [+1.05, +15.02] | yes |
| ATT+bal − released checkpoint | v2pe 5 prepend | 1% FPR | malware TPR | +54.02 | 2.54 | [+52.92, +55.01] | 10/0 | **yes** | [+39.04, +66.44] | yes |
| ATT+bal − released checkpoint | v2pe 5 prepend | 1% FPR | padded-benign FPR | -13.34 | 0.64 | [-14.11, -12.59] | 0/10 | **yes** | [-25.30, -5.11] | yes |
| ATT+bal − released checkpoint | v2pe 5 prepend | 1% FPR | malware TPR, fit subset | +16.58 | 4.30 | [+14.59, +18.59] | 10/0 | **yes** | [+7.52, +32.74] | yes |
| ATT+bal − released checkpoint | v2pe 5 prepend | 0.1% FPR | malware TPR | +44.40 | 5.89 | [+43.58, +45.24] | 10/0 | **yes** | [+31.46, +55.05] | yes |
| ATT+bal − released checkpoint | v2pe 5 prepend | 0.1% FPR | padded-benign FPR | +0.07 | 0.03 | [+0.02, +0.13] | 9/0 | **yes** | [+0.01, +0.16] | yes |
| ATT+bal − released checkpoint | v2pe 5 prepend | 0.1% FPR | malware TPR, fit subset | +15.30 | 9.63 | [+14.20, +16.62] | 10/0 | **yes** | [+7.56, +29.74] | yes |
| ATT+bal − released checkpoint | v2pe 20 insert | 1% FPR | malware TPR | +10.09 | 5.03 | [+8.81, +11.36] | 9/1 | **yes** | [-6.18, +26.36] | no |
| ATT+bal − released checkpoint | v2pe 20 insert | 1% FPR | padded-benign FPR | -30.46 | 0.09 | [-31.43, -29.33] | 0/10 | **yes** | [-36.65, -24.90] | yes |
| ATT+bal − released checkpoint | v2pe 20 insert | 1% FPR | malware TPR, fit subset | -33.40 | 1.40 | [-36.02, -30.93] | 0/10 | **yes** | [-43.73, -27.32] | yes |
| ATT+bal − released checkpoint | v2pe 20 insert | 0.1% FPR | malware TPR | +14.18 | 2.46 | [+13.35, +15.00] | 10/0 | **yes** | [+5.48, +24.45] | yes |
| ATT+bal − released checkpoint | v2pe 20 insert | 0.1% FPR | padded-benign FPR | -0.28 | 0.01 | [-0.40, -0.18] | 0/10 | **yes** | [-0.43, -0.15] | yes |
| ATT+bal − released checkpoint | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − released checkpoint | v2pe 20 prepend | 1% FPR | malware TPR | -4.80 | 8.60 | [-5.62, -3.91] | 3/7 | **yes** | [-16.12, +6.31] | no |
| ATT+bal − released checkpoint | v2pe 20 prepend | 1% FPR | padded-benign FPR | -66.02 | 0.03 | [-67.00, -65.01] | 0/10 | **yes** | [-75.32, -54.43] | yes |
| ATT+bal − released checkpoint | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +3.23 | 4.22 | [+2.06, +4.32] | 6/4 | no | [-0.33, +9.98] | no |
| ATT+bal − released checkpoint | v2pe 20 prepend | 0.1% FPR | malware TPR | -6.62 | 0.83 | [-7.11, -6.16] | 0/10 | **yes** | [-12.62, -2.18] | yes |
| ATT+bal − released checkpoint | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − released checkpoint | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [+0.00, +0.02] | 1/0 | no | [+0.00, +0.03] | no |
| ATT+bal − released checkpoint | v2pe 50 insert | 1% FPR | malware TPR | -31.68 | 5.35 | [-33.12, -30.33] | 0/10 | **yes** | [-49.58, -12.87] | yes |
| ATT+bal − released checkpoint | v2pe 50 insert | 1% FPR | padded-benign FPR | -59.18 | 0.06 | [-60.25, -58.00] | 0/10 | **yes** | [-67.46, -49.52] | yes |
| ATT+bal − released checkpoint | v2pe 50 insert | 0.1% FPR | malware TPR | +5.48 | 1.64 | [+4.82, +6.23] | 10/0 | **yes** | [-0.29, +12.14] | no |
| ATT+bal − released checkpoint | v2pe 50 insert | 0.1% FPR | padded-benign FPR | -0.27 | 0.00 | [-0.40, -0.17] | 0/10 | **yes** | [-0.40, -0.16] | yes |
| ATT+bal − released checkpoint | v2pe 50 prepend | 1% FPR | malware TPR | -95.78 | 1.38 | [-96.15, -95.41] | 0/10 | **yes** | [-98.12, -91.95] | yes |
| ATT+bal − released checkpoint | v2pe 50 prepend | 1% FPR | padded-benign FPR | -100.00 | 0.00 | [-100.00, -100.00] | 0/10 | **yes** | [-100.00, -100.00] | yes |
| ATT+bal − released checkpoint | v2pe 50 prepend | 0.1% FPR | malware TPR | -13.86 | 0.83 | [-14.57, -13.19] | 0/10 | **yes** | [-23.15, -6.32] | yes |
| ATT+bal − released checkpoint | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | -1.89 | 0.00 | [-2.20, -1.59] | 0/10 | **yes** | [-3.63, -0.77] | yes |
| ATT+bal − v2-PE | lgbm 5 insert | 1% FPR | malware TPR | +13.49 | 7.96 | [+12.92, +14.04] | 9/1 | **yes** | [+6.70, +21.10] | yes |
| ATT+bal − v2-PE | lgbm 5 insert | 1% FPR | padded-benign FPR | +0.41 | 0.24 | [+0.28, +0.53] | 9/1 | **yes** | [+0.25, +0.63] | yes |
| ATT+bal − v2-PE | lgbm 5 insert | 1% FPR | malware TPR, fit subset | +27.28 | 12.15 | [+26.07, +28.42] | 10/0 | **yes** | [+14.36, +42.14] | yes |
| ATT+bal − v2-PE | lgbm 5 insert | 0.1% FPR | malware TPR | +20.74 | 10.25 | [+20.01, +21.46] | 10/0 | **yes** | [+10.81, +27.97] | yes |
| ATT+bal − v2-PE | lgbm 5 insert | 0.1% FPR | padded-benign FPR | +0.04 | 0.03 | [+0.01, +0.08] | 8/1 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal − v2-PE | lgbm 5 insert | 0.1% FPR | malware TPR, fit subset | +33.24 | 13.75 | [+32.06, +34.44] | 10/0 | **yes** | [+14.57, +43.94] | yes |
| ATT+bal − v2-PE | lgbm 5 prepend | 1% FPR | malware TPR | +42.71 | 10.01 | [+41.95, +43.44] | 10/0 | **yes** | [+29.97, +54.39] | yes |
| ATT+bal − v2-PE | lgbm 5 prepend | 1% FPR | padded-benign FPR | +0.69 | 0.39 | [+0.55, +0.83] | 9/1 | **yes** | [+0.35, +1.05] | yes |
| ATT+bal − v2-PE | lgbm 5 prepend | 1% FPR | malware TPR, fit subset | +49.46 | 10.63 | [+47.96, +50.89] | 10/0 | **yes** | [+26.02, +67.77] | yes |
| ATT+bal − v2-PE | lgbm 5 prepend | 0.1% FPR | malware TPR | +44.65 | 8.35 | [+43.90, +45.47] | 10/0 | **yes** | [+32.50, +53.76] | yes |
| ATT+bal − v2-PE | lgbm 5 prepend | 0.1% FPR | padded-benign FPR | +0.09 | 0.04 | [+0.04, +0.15] | 10/0 | **yes** | [+0.04, +0.16] | yes |
| ATT+bal − v2-PE | lgbm 5 prepend | 0.1% FPR | malware TPR, fit subset | +46.64 | 11.47 | [+45.30, +48.06] | 10/0 | **yes** | [+24.20, +60.61] | yes |
| ATT+bal − v2-PE | lgbm 20 insert | 1% FPR | malware TPR | +29.34 | 11.00 | [+28.66, +30.03] | 10/0 | **yes** | [+18.40, +38.98] | yes |
| ATT+bal − v2-PE | lgbm 20 insert | 1% FPR | padded-benign FPR | +0.34 | 0.30 | [+0.25, +0.44] | 9/1 | **yes** | [+0.19, +0.51] | yes |
| ATT+bal − v2-PE | lgbm 20 insert | 1% FPR | malware TPR, fit subset | +42.55 | 15.48 | [+41.15, +44.01] | 10/0 | **yes** | [+24.41, +52.53] | yes |
| ATT+bal − v2-PE | lgbm 20 insert | 0.1% FPR | malware TPR | +25.28 | 7.45 | [+24.55, +26.04] | 10/0 | **yes** | [+15.18, +35.82] | yes |
| ATT+bal − v2-PE | lgbm 20 insert | 0.1% FPR | padded-benign FPR | +0.02 | 0.02 | [+0.00, +0.04] | 8/0 | **yes** | [+0.00, +0.04] | yes |
| ATT+bal − v2-PE | lgbm 20 insert | 0.1% FPR | malware TPR, fit subset | +16.11 | 4.93 | [+14.88, +17.26] | 10/0 | **yes** | [+2.28, +33.72] | yes |
| ATT+bal − v2-PE | lgbm 20 prepend | 1% FPR | malware TPR | +62.10 | 8.83 | [+61.26, +62.85] | 10/0 | **yes** | [+50.10, +71.43] | yes |
| ATT+bal − v2-PE | lgbm 20 prepend | 1% FPR | padded-benign FPR | +0.64 | 0.65 | [+0.52, +0.78] | 9/1 | **yes** | [+0.45, +0.93] | yes |
| ATT+bal − v2-PE | lgbm 20 prepend | 1% FPR | malware TPR, fit subset | +60.69 | 10.34 | [+58.96, +62.44] | 10/0 | **yes** | [+34.48, +74.90] | yes |
| ATT+bal − v2-PE | lgbm 20 prepend | 0.1% FPR | malware TPR | +45.20 | 7.87 | [+44.37, +46.08] | 10/0 | **yes** | [+32.05, +56.90] | yes |
| ATT+bal − v2-PE | lgbm 20 prepend | 0.1% FPR | padded-benign FPR | +0.08 | 0.03 | [+0.03, +0.13] | 10/0 | **yes** | [+0.02, +0.15] | yes |
| ATT+bal − v2-PE | lgbm 20 prepend | 0.1% FPR | malware TPR, fit subset | +26.44 | 3.86 | [+24.90, +27.98] | 10/0 | **yes** | [+7.81, +49.70] | yes |
| ATT+bal − v2-PE | lgbm 50 insert | 1% FPR | malware TPR | +37.35 | 9.44 | [+36.55, +38.13] | 10/0 | **yes** | [+24.44, +50.17] | yes |
| ATT+bal − v2-PE | lgbm 50 insert | 1% FPR | padded-benign FPR | +0.23 | 0.19 | [+0.16, +0.32] | 9/1 | **yes** | [+0.13, +0.38] | yes |
| ATT+bal − v2-PE | lgbm 50 insert | 1% FPR | malware TPR, fit subset | +4.30 | 3.18 | [+3.56, +5.07] | 10/0 | **yes** | [+1.53, +10.28] | yes |
| ATT+bal − v2-PE | lgbm 50 insert | 0.1% FPR | malware TPR | +23.64 | 6.57 | [+22.93, +24.35] | 10/0 | **yes** | [+13.00, +35.98] | yes |
| ATT+bal − v2-PE | lgbm 50 insert | 0.1% FPR | padded-benign FPR | +0.01 | 0.02 | [+0.00, +0.03] | 6/0 | no | [+0.00, +0.03] | no |
| ATT+bal − v2-PE | lgbm 50 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − v2-PE | lgbm 50 prepend | 1% FPR | malware TPR | +33.23 | 16.04 | [+32.51, +33.95] | 9/1 | **yes** | [+22.15, +43.06] | yes |
| ATT+bal − v2-PE | lgbm 50 prepend | 1% FPR | padded-benign FPR | +0.08 | 0.06 | [+0.04, +0.11] | 9/0 | **yes** | [+0.04, +0.14] | yes |
| ATT+bal − v2-PE | lgbm 50 prepend | 1% FPR | malware TPR, fit subset | +14.92 | 16.99 | [+13.86, +15.99] | 10/0 | **yes** | [+7.61, +20.57] | yes |
| ATT+bal − v2-PE | lgbm 50 prepend | 0.1% FPR | malware TPR | +4.80 | 5.34 | [+4.50, +5.06] | 8/2 | **yes** | [+1.34, +9.85] | yes |
| ATT+bal − v2-PE | lgbm 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − v2-PE | lgbm 50 prepend | 0.1% FPR | malware TPR, fit subset | +0.10 | 0.18 | [+0.03, +0.22] | 7/0 | **yes** | [+0.01, +0.33] | yes |
| ATT+bal − v2-PE | v2pe 5 insert | 1% FPR | malware TPR | +27.40 | 7.84 | [+26.61, +28.13] | 10/0 | **yes** | [+17.60, +35.97] | yes |
| ATT+bal − v2-PE | v2pe 5 insert | 1% FPR | padded-benign FPR | +0.16 | 0.12 | [+0.08, +0.25] | 9/1 | **yes** | [+0.07, +0.28] | yes |
| ATT+bal − v2-PE | v2pe 5 insert | 1% FPR | malware TPR, fit subset | +39.44 | 12.72 | [+37.74, +41.15] | 10/0 | **yes** | [+19.47, +52.66] | yes |
| ATT+bal − v2-PE | v2pe 5 insert | 0.1% FPR | malware TPR | +18.10 | 6.30 | [+17.39, +18.86] | 10/0 | **yes** | [+10.41, +24.98] | yes |
| ATT+bal − v2-PE | v2pe 5 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.02 | [-0.01, +0.01] | 3/3 | no | [-0.01, +0.01] | no |
| ATT+bal − v2-PE | v2pe 5 insert | 0.1% FPR | malware TPR, fit subset | +6.66 | 2.51 | [+5.77, +7.61] | 10/0 | **yes** | [+1.33, +19.17] | yes |
| ATT+bal − v2-PE | v2pe 5 prepend | 1% FPR | malware TPR | +63.40 | 7.84 | [+62.55, +64.22] | 10/0 | **yes** | [+50.30, +72.82] | yes |
| ATT+bal − v2-PE | v2pe 5 prepend | 1% FPR | padded-benign FPR | +0.78 | 0.65 | [+0.64, +0.91] | 10/0 | **yes** | [+0.51, +1.13] | yes |
| ATT+bal − v2-PE | v2pe 5 prepend | 1% FPR | malware TPR, fit subset | +58.28 | 5.43 | [+56.31, +60.20] | 10/0 | **yes** | [+33.89, +75.63] | yes |
| ATT+bal − v2-PE | v2pe 5 prepend | 0.1% FPR | malware TPR | +46.14 | 6.26 | [+45.31, +46.99] | 10/0 | **yes** | [+33.62, +56.80] | yes |
| ATT+bal − v2-PE | v2pe 5 prepend | 0.1% FPR | padded-benign FPR | +0.09 | 0.03 | [+0.04, +0.15] | 10/0 | **yes** | [+0.03, +0.16] | yes |
| ATT+bal − v2-PE | v2pe 5 prepend | 0.1% FPR | malware TPR, fit subset | +15.41 | 9.63 | [+14.29, +16.70] | 10/0 | **yes** | [+7.68, +30.09] | yes |
| ATT+bal − v2-PE | v2pe 20 insert | 1% FPR | malware TPR | +34.65 | 7.90 | [+33.83, +35.45] | 10/0 | **yes** | [+22.61, +45.04] | yes |
| ATT+bal − v2-PE | v2pe 20 insert | 1% FPR | padded-benign FPR | +0.09 | 0.12 | [+0.03, +0.16] | 8/2 | **yes** | [+0.03, +0.17] | yes |
| ATT+bal − v2-PE | v2pe 20 insert | 1% FPR | malware TPR, fit subset | +1.46 | 1.41 | [+1.11, +1.82] | 8/1 | **yes** | [+0.22, +4.18] | yes |
| ATT+bal − v2-PE | v2pe 20 insert | 0.1% FPR | malware TPR | +18.70 | 4.70 | [+18.03, +19.35] | 10/0 | **yes** | [+9.93, +28.05] | yes |
| ATT+bal − v2-PE | v2pe 20 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.01 | [-0.01, +0.02] | 2/1 | no | [-0.01, +0.02] | no |
| ATT+bal − v2-PE | v2pe 20 insert | 0.1% FPR | malware TPR, fit subset | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − v2-PE | v2pe 20 prepend | 1% FPR | malware TPR | +21.08 | 9.55 | [+20.44, +21.73] | 10/0 | **yes** | [+7.84, +32.63] | yes |
| ATT+bal − v2-PE | v2pe 20 prepend | 1% FPR | padded-benign FPR | +0.03 | 0.03 | [+0.01, +0.07] | 8/0 | **yes** | [+0.01, +0.08] | yes |
| ATT+bal − v2-PE | v2pe 20 prepend | 1% FPR | malware TPR, fit subset | +5.30 | 4.22 | [+4.51, +6.06] | 9/0 | **yes** | [+2.03, +13.09] | yes |
| ATT+bal − v2-PE | v2pe 20 prepend | 0.1% FPR | malware TPR | +0.82 | 1.46 | [+0.71, +0.95] | 8/2 | **yes** | [+0.19, +1.75] | yes |
| ATT+bal − v2-PE | v2pe 20 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − v2-PE | v2pe 20 prepend | 0.1% FPR | malware TPR, fit subset | +0.01 | 0.02 | [+0.00, +0.02] | 1/0 | no | [+0.00, +0.03] | no |
| ATT+bal − v2-PE | v2pe 50 insert | 1% FPR | malware TPR | +26.29 | 6.73 | [+25.56, +27.05] | 10/0 | **yes** | [+15.93, +36.42] | yes |
| ATT+bal − v2-PE | v2pe 50 insert | 1% FPR | padded-benign FPR | +0.09 | 0.09 | [+0.04, +0.16] | 8/2 | **yes** | [+0.03, +0.19] | yes |
| ATT+bal − v2-PE | v2pe 50 insert | 0.1% FPR | malware TPR | +10.71 | 2.70 | [+10.21, +11.26] | 10/0 | **yes** | [+4.64, +17.93] | yes |
| ATT+bal − v2-PE | v2pe 50 insert | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − v2-PE | v2pe 50 prepend | 1% FPR | malware TPR | +1.11 | 3.74 | [+0.93, +1.29] | 6/4 | no | [-0.13, +2.75] | no |
| ATT+bal − v2-PE | v2pe 50 prepend | 1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |
| ATT+bal − v2-PE | v2pe 50 prepend | 0.1% FPR | malware TPR | +0.68 | 1.60 | [+0.57, +0.79] | 8/2 | **yes** | [+0.12, +1.52] | yes |
| ATT+bal − v2-PE | v2pe 50 prepend | 0.1% FPR | padded-benign FPR | +0.00 | 0.00 | [+0.00, +0.00] | 0/0 | no | [+0.00, +0.00] | no |

**White-box greedy, 500 reports, seeds 0-2 (the released checkpoint: its one run against every seed); share still flagged after k prepended calls; cluster bootstrap over the hash_apis groups of the 500 reports. Descriptive.**

| difference | threshold | k | mean difference (points) | 95% CI (cluster) | seeds > 0 |
|---|---|---|---|---|---|
| v2-PE − released checkpoint | 1% FPR | 5 | +5.8 | [+1.8, +10.3] | 3/3 |
| v2-PE − released checkpoint | 1% FPR | 10 | +3.7 | [+1.4, +6.5] | 3/3 |
| v2-PE − released checkpoint | 1% FPR | 20 | +1.0 | [-0.4, +2.6] | 2/3 |
| v2-PE − released checkpoint | 0.1% FPR | 5 | +0.7 | [+0.1, +1.6] | 3/3 |
| v2-PE − released checkpoint | 0.1% FPR | 10 | +0.6 | [+0.1, +1.3] | 3/3 |
| v2-PE − released checkpoint | 0.1% FPR | 20 | +0.2 | [+0.0, +0.6] | 2/3 |
| ATT+bal − released checkpoint | 1% FPR | 5 | +62.3 | [+47.4, +72.9] | 3/3 |
| ATT+bal − released checkpoint | 1% FPR | 10 | +61.1 | [+45.8, +71.7] | 3/3 |
| ATT+bal − released checkpoint | 1% FPR | 20 | +52.1 | [+37.0, +63.6] | 3/3 |
| ATT+bal − released checkpoint | 0.1% FPR | 5 | +34.5 | [+22.1, +47.4] | 3/3 |
| ATT+bal − released checkpoint | 0.1% FPR | 10 | +31.7 | [+19.8, +45.0] | 3/3 |
| ATT+bal − released checkpoint | 0.1% FPR | 20 | +14.6 | [+8.2, +22.1] | 3/3 |
| ATT+bal − v2-PE | 1% FPR | 5 | +56.5 | [+43.8, +67.6] | 3/3 |
| ATT+bal − v2-PE | 1% FPR | 10 | +57.3 | [+43.7, +69.1] | 3/3 |
| ATT+bal − v2-PE | 1% FPR | 20 | +51.1 | [+36.8, +62.8] | 3/3 |
| ATT+bal − v2-PE | 0.1% FPR | 5 | +33.7 | [+21.6, +46.1] | 3/3 |
| ATT+bal − v2-PE | 0.1% FPR | 10 | +31.1 | [+19.4, +43.2] | 3/3 |
| ATT+bal − v2-PE | 0.1% FPR | 20 | +14.4 | [+8.2, +21.4] | 3/3 |
