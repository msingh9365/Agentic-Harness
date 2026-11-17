# Item 1: graded edits on the released Nebula weights, next to A and C of regime J

Edits: insert k / prepend k calls (k = 1, 5, 20, 50), each a copy of a call of the same report, first 512 tokens (the tokens of `results/pooling_v2/graded_edits.md`). TPR fixed (a): malware caught at the threshold that gave 1% FPR on the unedited April benign scores of that model, not recomputed after the edit; FPR fixed (a): benign reports flagged at that threshold after the same edit. A (J) and C (J): mean over 10 seeds. Released Nebula: the published weights.

## All April reports

| edit | released Nebula AUC | A (J) AUC | C (J) AUC | released Nebula TPR fixed (a) | A (J) TPR fixed (a) | C (J) TPR fixed (a) | released Nebula FPR fixed (a) | A (J) FPR fixed (a) | C (J) FPR fixed (a) |
|---|---|---|---|---|---|---|---|---|---|
| original | 0.9586 | 0.9486 | 0.9644 | 75.0% | 71.9% | 73.8% | 1.00% | 1.00% | 1.00% |
| insert 1 | 0.9560 | 0.9478 | 0.9629 | 73.6% | 70.6% | 72.8% | 1.09% | 1.07% | 0.98% |
| insert 5 | 0.9482 | 0.9379 | 0.9606 | 69.3% | 65.4% | 71.4% | 1.04% | 1.14% | 0.99% |
| insert 20 | 0.9177 | 0.8862 | 0.9588 | 57.5% | 49.1% | 70.5% | 1.72% | 1.57% | 1.06% |
| insert 50 | 0.8702 | 0.8089 | 0.9632 | 49.2% | 38.2% | 72.1% | 2.87% | 2.07% | 1.10% |
| prepend 1 | 0.9610 | 0.9450 | 0.9631 | 69.6% | 66.3% | 71.1% | 1.09% | 1.17% | 0.93% |
| prepend 5 | 0.9013 | 0.8775 | 0.9526 | 53.7% | 43.4% | 69.8% | 2.06% | 1.56% | 1.89% |
| prepend 20 | 0.6397 | 0.6170 | 0.9628 | 35.7% | 28.2% | 71.3% | 20.89% | 8.54% | 1.16% |
| prepend 50 | 0.6557 | 0.5666 | 0.9650 | 38.0% | 21.2% | 68.4% | 19.41% | 8.51% | 1.05% |


## Only reports whose whole edited sequence fits in 512 tokens (no original call leaves the window)

| edit | reports that fit (malware) | released Nebula TPR fixed (a) before → after | A (J) TPR fixed (a) before → after | C (J) TPR fixed (a) before → after | released Nebula AUC before → after | A (J) AUC before → after | C (J) AUC before → after |
|---|---|---|---|---|---|---|---|
| insert 1 | 6,349 (2,854) | 61.5% → 59.7% | 65.9% → 64.3% | 71.0% → 69.5% | 0.9557 → 0.9484 | 0.9496 → 0.9445 | 0.9608 → 0.9572 |
| insert 5 | 6,278 (2,813) | 61.2% → 55.8% | 65.9% → 58.5% | 71.1% → 69.5% | 0.9552 → 0.9282 | 0.9496 → 0.9221 | 0.9605 → 0.9563 |
| insert 20 | 4,975 (1,953) | 63.1% → 64.4% | 69.5% → 58.1% | 72.4% → 71.4% | 0.9584 → 0.9258 | 0.9510 → 0.8960 | 0.9569 → 0.9512 |
| insert 50 | 3,654 (1,530) | 62.5% → 66.8% | 74.2% → 61.1% | 73.4% → 73.0% | 0.9563 → 0.9365 | 0.9573 → 0.9077 | 0.9611 → 0.9564 |
| prepend 1 | 6,349 (2,851) | 61.5% → 56.5% | 65.9% → 61.2% | 71.0% → 67.9% | 0.9557 → 0.9448 | 0.9495 → 0.9386 | 0.9607 → 0.9557 |
| prepend 5 | 6,275 (2,807) | 61.1% → 52.4% | 65.8% → 51.3% | 71.0% → 68.0% | 0.9551 → 0.8967 | 0.9493 → 0.8773 | 0.9605 → 0.9519 |
| prepend 20 | 5,018 (1,980) | 63.0% → 56.3% | 69.4% → 56.6% | 72.2% → 70.4% | 0.9579 → 0.8874 | 0.9502 → 0.8572 | 0.9567 → 0.9513 |
| prepend 50 | 3,644 (1,531) | 62.8% → 65.1% | 74.1% → 57.2% | 73.5% → 73.2% | 0.9559 → 0.9326 | 0.9569 → 0.9019 | 0.9610 → 0.9555 |


## Change in malware TPR at the fixed threshold, with group-bootstrap intervals (all reports)

| edit | released Nebula: change in TPR, points [group 95%] | A (J): change in TPR, points [group 95%] | C (J): change in TPR, points [group 95%] | A (J) − released Nebula | C (J) − released Nebula | C (J) − A (J) |
|---|---|---|---|---|---|---|
| insert 1 | -1.4 [-2.8, -0.3] | -1.3 [-2.1, -0.6] | -1.0 [-1.5, -0.5] | +0.0 [-1.1, +1.3] | +0.4 [-0.6, +1.6] | +0.4 [-0.4, +1.1] |
| insert 5 | -5.7 [-10.4, -1.5] | -6.5 [-10.0, -3.0] | -2.4 [-3.7, -1.1] | -0.8 [-2.9, +1.3] | +3.3 [-0.3, +7.2] | +4.1 [+0.8, +7.2] |
| insert 20 | -17.5 [-32.0, -5.5] | -22.8 [-32.6, -12.3] | -3.3 [-5.4, -1.2] | -5.3 [-11.0, +1.4] | +14.2 [+3.6, +27.5] | +19.5 [+9.6, +28.0] |
| insert 50 | -25.7 [-40.5, -12.6] | -33.7 [-45.5, -20.5] | -1.6 [-4.0, +0.3] | -7.9 [-14.2, -1.9] | +24.1 [+11.0, +38.8] | +32.0 [+19.5, +43.4] |
| prepend 1 | -5.4 [-8.9, -1.9] | -5.6 [-9.0, -2.4] | -2.7 [-3.8, -1.5] | -0.2 [-3.0, +3.0] | +2.7 [-0.5, +5.7] | +2.9 [-0.4, +5.8] |
| prepend 5 | -21.3 [-35.8, -7.0] | -28.5 [-38.3, -16.3] | -4.0 [-7.0, -1.3] | -7.2 [-14.4, +0.5] | +17.3 [+4.8, +29.5] | +24.5 [+13.1, +33.0] |
| prepend 20 | -39.3 [-51.3, -26.1] | -43.7 [-54.8, -30.7] | -2.4 [-5.0, -0.3] | -4.4 [-10.7, +3.1] | +36.9 [+22.2, +49.3] | +41.3 [+27.8, +52.9] |
| prepend 50 | -36.9 [-47.8, -25.5] | -50.7 [-61.9, -35.8] | -5.3 [-8.5, -2.4] | -13.8 [-22.9, -2.5] | +31.6 [+20.3, +43.1] | +45.4 [+31.5, +56.2] |


## The same change on the reports that fit in 512 tokens

| edit | released Nebula: change in TPR, points [group 95%] | A (J): change in TPR, points [group 95%] | C (J): change in TPR, points [group 95%] | A (J) − released Nebula | C (J) − released Nebula | C (J) − A (J) |
|---|---|---|---|---|---|---|
| insert 1 | -1.8 [-5.0, +1.7] | -1.6 [-2.4, -0.5] | -1.5 [-2.6, -0.4] | +0.2 [-3.4, +3.4] | +0.3 [-3.2, +3.3] | +0.1 [-1.8, +1.5] |
| insert 5 | -5.4 [-15.0, +5.4] | -7.4 [-13.1, -1.7] | -1.6 [-2.8, -0.3] | -2.0 [-8.5, +2.8] | +3.8 [-6.9, +13.4] | +5.8 [-0.4, +11.5] |
| insert 20 | +1.2 [-7.3, +9.6] | -11.3 [-17.6, -3.8] | -1.0 [-3.3, +1.7] | -12.6 [-19.8, -3.0] | -2.2 [-11.0, +6.1] | +10.3 [+1.5, +17.6] |
| insert 50 | +4.2 [-2.1, +13.4] | -13.0 [-24.8, -3.4] | -0.4 [-2.0, +1.1] | -17.3 [-27.9, -9.0] | -4.6 [-13.3, +1.3] | +12.6 [+2.9, +24.5] |
| prepend 1 | -5.0 [-12.0, +2.8] | -4.7 [-6.5, -1.7] | -3.1 [-4.8, -1.1] | +0.3 [-6.6, +6.2] | +1.9 [-6.2, +8.6] | +1.6 [-1.7, +3.8] |
| prepend 5 | -8.7 [-23.8, +6.9] | -14.6 [-28.0, -2.3] | -3.1 [-4.6, -1.5] | -5.9 [-12.0, -0.1] | +5.6 [-10.8, +20.8] | +11.5 [-1.4, +24.7] |
| prepend 20 | -6.8 [-20.2, +4.0] | -12.8 [-19.5, -5.7] | -1.8 [-4.0, +0.6] | -6.0 [-13.8, +4.9] | +5.0 [-6.2, +18.5] | +11.0 [+2.5, +18.7] |
| prepend 50 | +2.4 [-4.4, +10.7] | -16.9 [-28.9, -7.1] | -0.3 [-1.9, +1.0] | -19.2 [-29.0, -11.0] | -2.7 [-11.1, +3.8] | +16.5 [+6.2, +29.0] |


## C (J) versus A (J), seed-paired

Bootstrap over the 10 seeds only.

| edit | set | A (J) change, points | C (J) change | C − A, seed-paired [95% over seeds] |
|---|---|---|---|---|
| insert 1 | all reports | -1.3 | -1.0 | +0.4 [-0.5, +1.3] |
| insert 1 | reports that fit | -1.6 | -1.5 | +0.1 [-1.4, +1.6] |
| insert 5 | all reports | -6.5 | -2.4 | +4.1 [+2.1, +6.2] |
| insert 5 | reports that fit | -7.4 | -1.6 | +5.8 [+3.6, +8.0] |
| insert 20 | all reports | -22.8 | -3.3 | +19.5 [+15.9, +22.7] |
| insert 20 | reports that fit | -11.3 | -1.0 | +10.3 [+8.0, +13.3] |
| insert 50 | all reports | -33.7 | -1.6 | +32.0 [+29.4, +34.6] |
| insert 50 | reports that fit | -13.0 | -0.4 | +12.6 [+8.5, +17.6] |
| prepend 1 | all reports | -5.6 | -2.7 | +2.9 [+0.7, +5.2] |
| prepend 1 | reports that fit | -4.7 | -3.1 | +1.6 [-1.2, +4.6] |
| prepend 5 | all reports | -28.5 | -4.0 | +24.5 [+19.5, +29.0] |
| prepend 5 | reports that fit | -14.6 | -3.1 | +11.5 [+8.1, +13.9] |
| prepend 20 | all reports | -43.7 | -2.4 | +41.3 [+39.3, +43.2] |
| prepend 20 | reports that fit | -12.8 | -1.8 | +11.0 [+7.8, +15.2] |
| prepend 50 | all reports | -50.7 | -5.3 | +45.4 [+43.4, +47.3] |
| prepend 50 | reports that fit | -16.9 | -0.3 | +16.5 [+11.8, +22.3] |
