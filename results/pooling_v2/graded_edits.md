# Follow-up: graded edits (insert or prepend k API calls)

Edits of the filtered report of every April report (then Nebula's tokenizer, first 512 tokens):
  insert k  : k extra API calls at random places (k = 1, 5, 20, 50)
  prepend k : k extra API calls put before the first call (k = 1, 5, 20, 50); this shifts every later token
Every added call is a copy of a call of the SAME report (no new API names or arguments are introduced), chosen at
random (numpy Generator; seeds 2000 + row for insert, 3000 + row for prepend). Reports without API calls stay as is.

Regime S, 10 seeds, checkpoint chosen on validation AUC. "TPR fixed (a)": malware caught at the threshold that gave 1% FPR on the original April benign scores (not recomputed after the edit); "FPR fixed (a)": benign reports flagged at that threshold after the same edit; (b): the January-validation threshold. Means over seeds.

## All April reports

| edit | A AUC | B AUC | C AUC | A TPR fixed (a) | B TPR fixed (a) | C TPR fixed (a) | A FPR fixed (a) | B FPR fixed (a) | C FPR fixed (a) | A TPR fixed (b) | B TPR fixed (b) | C TPR fixed (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| original | 0.9325 | 0.9287 | 0.9416 | 66.4% | 56.0% | 67.0% | 1.00% | 1.00% | 1.00% | 59.2% | 44.5% | 57.4% |
| insert 1 | 0.9310 | 0.9286 | 0.9407 | 64.8% | 55.4% | 66.0% | 0.95% | 0.98% | 0.95% | 57.5% | 44.1% | 56.2% |
| insert 5 | 0.9223 | 0.9276 | 0.9391 | 60.2% | 55.0% | 64.5% | 1.11% | 0.92% | 0.93% | 53.2% | 43.4% | 55.2% |
| insert 20 | 0.8901 | 0.9295 | 0.9356 | 50.0% | 55.2% | 63.9% | 1.43% | 0.91% | 1.04% | 43.0% | 40.8% | 53.5% |
| insert 50 | 0.8294 | 0.9357 | 0.9407 | 40.5% | 57.1% | 65.6% | 1.91% | 0.97% | 1.07% | 34.1% | 43.2% | 55.1% |
| prepend 1 | 0.9246 | 0.9286 | 0.9410 | 59.9% | 54.3% | 64.3% | 1.06% | 0.97% | 0.93% | 52.0% | 42.0% | 54.2% |
| prepend 5 | 0.8779 | 0.9262 | 0.9287 | 46.6% | 54.8% | 63.3% | 1.69% | 0.98% | 1.27% | 39.4% | 40.9% | 54.4% |
| prepend 20 | 0.6840 | 0.9357 | 0.9410 | 31.2% | 55.8% | 65.7% | 6.31% | 0.95% | 1.08% | 25.7% | 41.7% | 54.9% |
| prepend 50 | 0.5595 | 0.9328 | 0.9436 | 23.9% | 53.2% | 61.4% | 14.28% | 0.98% | 1.02% | 19.1% | 40.7% | 52.2% |


## Only reports whose whole edited sequence fits in 512 tokens (nothing pushed out of the window)

| edit | reports that fit (malware) | A AUC before → after | B AUC before → after | C AUC before → after | A TPR fixed (a) before → after | B TPR fixed (a) before → after | C TPR fixed (a) before → after |
|---|---|---|---|---|---|---|---|
| insert 1 | 6,349 (2,854) | 0.9384 → 0.9351 | 0.9310 → 0.9305 | 0.9412 → 0.9399 | 64.2% → 62.6% | 62.4% → 61.6% | 69.3% → 67.8% |
| insert 5 | 6,278 (2,813) | 0.9381 → 0.9199 | 0.9309 → 0.9292 | 0.9408 → 0.9400 | 64.2% → 58.3% | 62.7% → 62.1% | 69.4% → 67.1% |
| insert 20 | 4,975 (1,953) | 0.9475 → 0.9125 | 0.9344 → 0.9375 | 0.9431 → 0.9423 | 69.7% → 64.4% | 69.2% → 68.9% | 71.3% → 69.5% |
| insert 50 | 3,654 (1,530) | 0.9505 → 0.9171 | 0.9422 → 0.9451 | 0.9489 → 0.9509 | 72.1% → 63.8% | 71.7% → 70.8% | 71.1% → 69.2% |
| prepend 1 | 6,349 (2,851) | 0.9383 → 0.9284 | 0.9310 → 0.9293 | 0.9412 → 0.9388 | 64.1% → 61.0% | 62.5% → 60.6% | 69.3% → 66.6% |
| prepend 5 | 6,275 (2,807) | 0.9378 → 0.8853 | 0.9308 → 0.9290 | 0.9408 → 0.9352 | 64.1% → 54.0% | 62.7% → 61.8% | 69.4% → 66.3% |
| prepend 20 | 5,018 (1,980) | 0.9467 → 0.8826 | 0.9340 → 0.9361 | 0.9430 → 0.9418 | 69.7% → 60.2% | 68.9% → 68.1% | 71.2% → 68.8% |
| prepend 50 | 3,644 (1,531) | 0.9500 → 0.9094 | 0.9418 → 0.9444 | 0.9486 → 0.9503 | 72.1% → 61.4% | 71.7% → 70.8% | 71.2% → 69.6% |


## Change in malware TPR at the fixed threshold (a): C versus A, seed-paired

Intervals from a bootstrap over the 10 seeds only.

| edit | A: change in TPR fixed (a), points | C | C − A [95% over seeds] | reports that fit: A | reports that fit: C | reports that fit: C − A |
|---|---|---|---|---|---|---|
| insert 1 | -1.6 | -1.0 | +0.6 [-0.1, +1.4] | -1.6 | -1.5 | +0.1 [-1.0, +1.1] |
| insert 5 | -6.2 | -2.5 | +3.7 [+2.2, +5.3] | -5.9 | -2.3 | +3.6 [+1.8, +5.6] |
| insert 20 | -16.4 | -3.2 | +13.2 [+11.0, +15.5] | -5.3 | -1.8 | +3.5 [+0.7, +6.3] |
| insert 50 | -25.9 | -1.4 | +24.5 [+21.6, +27.5] | -8.3 | -1.9 | +6.5 [+2.4, +10.8] |
| prepend 1 | -6.5 | -2.8 | +3.7 [+1.6, +5.8] | -3.1 | -2.7 | +0.4 [-1.3, +2.4] |
| prepend 5 | -19.8 | -3.7 | +16.1 [+13.0, +18.9] | -10.1 | -3.1 | +7.0 [+4.2, +9.9] |
| prepend 20 | -35.2 | -1.4 | +33.9 [+30.6, +37.0] | -9.5 | -2.3 | +7.2 [+3.9, +10.5] |
| prepend 50 | -42.5 | -5.7 | +36.8 [+34.1, +39.5] | -10.6 | -1.6 | +9.0 [+4.7, +13.6] |
