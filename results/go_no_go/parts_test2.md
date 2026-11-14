## Test 2: information ceiling (first 92 calls vs full trace)

Same LightGBM as test 1 (bag of API names, early stopping on group-weighted January-validation log-loss, seeds 0/1/2: mean over seeds). Names kept if seen in ≥ 20 January-train reports, counted on the same prefix. 92 = median number of complete API calls in Nebula's 512-token window (reports > 512 tokens). 63.5% of April reports are longer than 512 tokens.

| subset | model | n (malware) | AUC | TPR@1% (a) | FPR (a) | TPR@1% (b) | April FPR (b) | TPR@0.1% (a) | FPR (a)  | TPR@0.1% (b) | April FPR (b)  |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | LightGBM, full trace | 17,402 (9,399) | 0.9501 [0.9150, 0.9757] | 62.9% [33.5%, 74.9%] | 1.0% [0.9%, 1.0%] | 58.0% [44.8%, 70.8%] | 0.9% [0.6%, 1.5%] | 31.6% [18.2%, 45.4%] | 0.1% [0.0%, 0.1%] | 27.2% [16.0%, 40.8%] | 0.0% [0.0%, 0.1%] |
| all | LightGBM, first 92 calls | 17,402 (9,399) | 0.8958 [0.8282, 0.9408] | 19.6% [10.6%, 36.0%] | 0.0% [0.0%, 1.0%] | 27.8% [15.6%, 42.3%] | 4.1% [0.7%, 11.7%] | 19.6% [10.4%, 31.5%] | 0.0% [0.0%, 0.1%] | 18.7% [9.4%, 30.1%] | 0.0% [0.0%, 0.1%] |
| seen | LightGBM, full trace | 6,329 (2,914) | 0.9749 [0.9447, 0.9904] | 79.0% [66.1%, 88.4%] | 1.1% [0.5%, 2.0%] | 78.6% [66.9%, 88.3%] | 1.1% [0.4%, 2.4%] | 62.9% [42.3%, 76.6%] | 0.0% [0.0%, 0.1%] | 50.5% [35.8%, 66.8%] | 0.0% [0.0%, 0.0%] |
| seen | LightGBM, first 92 calls | 6,329 (2,914) | 0.9360 [0.8921, 0.9671] | 29.6% [18.6%, 46.1%] | 0.0% [0.0%, 1.2%] | 34.2% [21.6%, 49.5%] | 0.9% [0.2%, 2.2%] | 29.6% [17.5%, 44.2%] | 0.0% [0.0%, 0.1%] | 28.3% [16.3%, 43.0%] | 0.0% [0.0%, 0.0%] |
| unseen | LightGBM, full trace | 11,073 (6,485) | 0.9384 [0.8917, 0.9754] | 55.7% [18.2%, 72.2%] | 0.9% [0.3%, 1.4%] | 48.7% [30.7%, 67.2%] | 0.9% [0.6%, 1.3%] | 17.5% [4.0%, 34.3%] | 0.1% [0.0%, 0.2%] | 16.7% [3.3%, 33.4%] | 0.1% [0.0%, 0.2%] |
| unseen | LightGBM, first 92 calls | 11,073 (6,485) | 0.8714 [0.7663, 0.9400] | 15.2% [4.9%, 36.4%] | 0.1% [0.0%, 1.2%] | 24.9% [9.4%, 43.9%] | 6.5% [0.8%, 18.7%] | 15.2% [4.2%, 30.6%] | 0.1% [0.0%, 0.1%] | 14.4% [3.5%, 29.6%] | 0.0% [0.0%, 0.1%] |
| 1 chunk | LightGBM, full trace | 6,359 (2,855) | 0.9100 [0.8590, 0.9542] | 43.9% [16.0%, 67.8%] | 0.4% [0.1%, 0.7%] | 43.7% [20.1%, 69.8%] | 0.3% [0.2%, 0.6%] | 14.0% [5.6%, 30.3%] | 0.0% [0.0%, 0.1%] | 13.6% [5.2%, 30.1%] | 0.0% [0.0%, 0.1%] |
| 1 chunk | LightGBM, first 92 calls | 6,359 (2,855) | 0.9194 [0.8702, 0.9565] | 16.4% [7.1%, 36.4%] | 0.1% [0.0%, 0.3%] | 20.5% [9.5%, 40.9%] | 0.2% [0.0%, 0.3%] | 16.4% [6.8%, 34.1%] | 0.1% [0.0%, 0.1%] | 14.9% [6.0%, 31.6%] | 0.0% [0.0%, 0.1%] |
| 2-3 chunks | LightGBM, full trace | 6,077 (3,676) | 0.9778 [0.9507, 0.9901] | 76.3% [26.3%, 88.1%] | 2.3% [1.3%, 4.3%] | 64.1% [48.0%, 77.5%] | 2.2% [0.9%, 5.0%] | 28.4% [8.1%, 54.1%] | 0.2% [0.0%, 0.3%] | 18.7% [5.3%, 43.2%] | 0.1% [0.0%, 0.2%] |
| 2-3 chunks | LightGBM, first 92 calls | 6,077 (3,676) | 0.9250 [0.8583, 0.9603] | 11.8% [3.7%, 47.1%] | 0.0% [0.0%, 3.0%] | 29.1% [9.8%, 55.7%] | 2.3% [1.0%, 5.3%] | 11.8% [3.4%, 26.8%] | 0.0% [0.0%, 0.2%] | 11.0% [2.7%, 25.8%] | 0.0% [0.0%, 0.2%] |
| 4-8 chunks | LightGBM, full trace | 4,966 (2,868) | 0.9410 [0.8575, 0.9955] | 64.8% [35.4%, 89.8%] | 0.6% [0.0%, 1.4%] | 64.4% [35.4%, 89.1%] | 0.5% [0.2%, 1.3%] | 53.0% [26.9%, 78.1%] | 0.0% [0.0%, 0.2%] | 51.7% [25.3%, 76.6%] | 0.0% [0.0%, 0.2%] |
| 4-8 chunks | LightGBM, first 92 calls | 4,966 (2,868) | 0.8223 [0.6410, 0.9564] | 33.0% [10.6%, 57.8%] | 0.0% [0.0%, 1.5%] | 33.4% [10.7%, 58.0%] | 12.8% [0.5%, 37.8%] | 33.0% [10.6%, 57.7%] | 0.0% [0.0%, 0.0%] | 32.3% [9.6%, 57.0%] | 0.0% [0.0%, 0.0%] |

**Per seed (all April):**

| model | AUC | TPR@1% (a) | FPR (a) | TPR@1% (b) | April FPR (b) | TPR@0.1% (a) | FPR (a)  | TPR@0.1% (b) | April FPR (b)  |
|---|---|---|---|---|---|---|---|---|---|
| LightGBM, full trace | 0.9482 / 0.9501 / 0.9520 | 63.9% / 62.0% / 62.9% | 1.0% / 1.0% / 1.0% | 58.7% / 52.7% / 62.6% | 1.0% / 0.9% / 0.9% | 29.2% / 32.6% / 32.9% | 0.1% / 0.1% / 0.1% | 27.0% / 27.1% / 27.5% | 0.0% / 0.0% / 0.0% |
| LightGBM, first 92 calls | 0.8953 / 0.8954 / 0.8967 | 18.6% / 20.3% / 20.1% | 0.0% / 0.0% / 0.0% | 27.7% / 28.0% / 27.7% | 4.1% / 4.1% / 4.1% | 18.6% / 20.3% / 20.1% | 0.0% / 0.0% / 0.0% | 18.2% / 19.6% / 18.2% | 0.0% / 0.0% / 0.0% |

**Full trace minus first 92 calls [95% interval]:**

| difference | subset | AUC | TPR@1% (a) | TPR@1% (b) | TPR@0.1% (a) | TPR@0.1% (b) |
|---|---|---|---|---|---|---|
| LightGBM, full trace − LightGBM, first 92 calls | all | +0.0543 [+0.0098, +0.1206] | +43.3 [+15.8, +56.2] | +30.2 [+15.4, +45.4] | +11.9 [+0.3, +24.2] | +8.5 [-0.9, +20.1] |
| LightGBM, full trace − LightGBM, first 92 calls | seen | +0.0389 [+0.0209, +0.0617] | +49.4 [+30.8, +62.9] | +44.4 [+27.1, +59.7] | +33.3 [+7.5, +52.2] | +22.3 [+2.9, +42.0] |
| LightGBM, full trace − LightGBM, first 92 calls | unseen | +0.0670 [-0.0025, +0.1743] | +40.6 [+3.8, +58.2] | +23.8 [+4.3, +44.5] | +2.3 [-7.5, +16.7] | +2.4 [-7.4, +15.6] |
| LightGBM, full trace − LightGBM, first 92 calls | 1 chunk | -0.0094 [-0.0288, +0.0067] | +27.6 [+4.2, +51.1] | +23.2 [+4.9, +51.0] | -2.3 [-8.3, +1.4] | -1.3 [-4.3, +0.1] |
| LightGBM, full trace − LightGBM, first 92 calls | 2-3 chunks | +0.0528 [+0.0241, +0.1015] | +64.5 [+11.5, +81.4] | +35.0 [+3.0, +58.9] | +16.7 [-5.0, +43.9] | +7.7 [-9.5, +32.2] |
| LightGBM, full trace − LightGBM, first 92 calls | 4-8 chunks | +0.1186 [+0.0252, +0.2836] | +31.8 [+14.2, +57.7] | +31.0 [+14.7, +56.3] | +20.1 [+0.3, +44.3] | +19.4 [+0.0, +43.9] |

How to read this. (1) The first-92-call model gives many reports the same score: 309 April benign reports (seed 0) sit exactly on its 1% threshold, which pushes its TPR (a) down. (2) Reports that need one chunk mostly have fewer than 92 calls, so both models see almost the same input there; yet TPR at 1% FPR differs by +27.6 points, which comes from the different model and threshold, not from more information. AUC is the cleaner measure: -0.0094 for 1-chunk reports, +0.0528 for 2-3 chunks and +0.1186 for 4-8 chunks. So later calls do carry signal for long reports, for a model that counts API names. (Released Nebula itself does not improve beyond about 100 calls: REPORT.md §10.3.)

**Decision.** The full trace adds +43.3 points of TPR at 1% FPR [+15.8, +56.2] over the first 92 calls, which is more than 1 point, so the rule does not say that long-context modelling has little to win.
