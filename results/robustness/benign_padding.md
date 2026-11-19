# Item 2: malware reports padded with calls from benign January reports (robustness measurement)

Only the 9,399 malware April reports are edited; benign April reports stay unchanged and the threshold stays fixed at 1% FPR on the unedited April scores of each model, so the benign FPR is 1% by construction. Each added call is a random call of a random benign January report (pool of 2,000), k = 1, 5, 20, 50, inserted at random places or prepended; nothing is optimised. 0.0% of the malware reports have no API call and stay unchanged. A (J), C (J): mean over 10 seeds (regime J). "Fits": the whole edited token sequence is at most 512 tokens, so no original call leaves the window.

## Malware TPR at the fixed threshold, all malware reports

| edit | released Nebula: TPR before → after | released Nebula: change, points [group 95%] | A (J): TPR before → after | A (J): change, points [group 95%] | C (J): TPR before → after | C (J): change, points [group 95%] |
|---|---|---|---|---|---|---|
| insert 1 | 75.0% → 72.8% | -2.2 [-3.3, -1.3] | 71.9% → 69.9% | -2.0 [-3.3, -0.9] | 73.8% → 70.2% | -3.6 [-6.1, -2.0] |
| insert 5 | 75.0% → 66.1% | -8.8 [-13.0, -5.0] | 71.9% → 61.4% | -10.5 [-14.2, -6.5] | 73.8% → 60.4% | -13.4 [-21.6, -7.7] |
| insert 20 | 75.0% → 46.4% | -28.6 [-43.2, -16.1] | 71.9% → 38.0% | -33.9 [-44.8, -21.2] | 73.8% → 48.6% | -25.1 [-34.5, -17.2] |
| insert 50 | 75.0% → 35.9% | -39.1 [-53.1, -26.3] | 71.9% → 29.7% | -42.2 [-52.9, -29.9] | 73.8% → 34.8% | -38.9 [-48.8, -30.2] |
| prepend 1 | 75.0% → 68.1% | -6.9 [-10.7, -3.6] | 71.9% → 64.6% | -7.3 [-11.2, -3.2] | 73.8% → 67.6% | -6.1 [-9.3, -3.7] |
| prepend 5 | 75.0% → 43.8% | -31.1 [-45.2, -16.6] | 71.9% → 35.8% | -36.1 [-45.8, -24.2] | 73.8% → 57.7% | -16.1 [-25.2, -9.1] |
| prepend 20 | 75.0% → 12.1% | -62.9 [-71.9, -52.9] | 71.9% → 19.5% | -52.4 [-64.3, -40.6] | 73.8% → 42.6% | -31.1 [-40.6, -23.7] |
| prepend 50 | 75.0% → 16.0% | -59.0 [-68.4, -48.4] | 71.9% → 16.0% | -55.9 [-66.5, -42.1] | 73.8% → 0.6% | -73.1 [-81.0, -62.5] |


## Only malware reports that fit in 512 tokens after the edit

| edit | malware reports that fit | released Nebula: TPR before → after | released Nebula: change, points [group 95%] | A (J): TPR before → after | A (J): change, points [group 95%] | C (J): TPR before → after | C (J): change, points [group 95%] |
|---|---|---|---|---|---|---|---|
| insert 1 | 2,853 | 61.5% → 57.9% | -3.6 [-6.4, -1.1] | 65.9% → 62.1% | -3.8 [-6.8, -1.4] | 70.9% → 62.3% | -8.6 [-14.2, -4.4] |
| insert 5 | 2,832 | 61.4% → 49.0% | -12.4 [-19.2, -5.7] | 66.0% → 49.5% | -16.5 [-22.7, -11.2] | 71.1% → 39.7% | -31.4 [-49.2, -18.3] |
| insert 20 | 2,451 | 61.0% → 19.7% | -41.3 [-53.2, -25.2] | 65.8% → 15.1% | -50.8 [-65.1, -31.1] | 71.1% → 16.0% | -55.1 [-72.8, -39.6] |
| insert 50 | 1,595 | 62.3% → 9.7% | -52.6 [-72.4, -25.8] | 71.0% → 12.0% | -59.0 [-75.1, -36.2] | 70.9% → 0.3% | -70.6 [-84.3, -50.8] |
| prepend 1 | 2,852 | 61.5% → 56.7% | -4.7 [-8.8, -0.2] | 65.9% → 60.0% | -5.9 [-9.2, -3.0] | 71.0% → 59.1% | -11.9 [-19.3, -6.2] |
| prepend 5 | 2,834 | 61.4% → 40.5% | -20.9 [-34.2, -8.4] | 66.0% → 34.8% | -31.2 [-40.0, -20.0] | 71.1% → 38.4% | -32.7 [-52.9, -17.8] |
| prepend 20 | 2,452 | 60.6% → 3.1% | -57.4 [-73.2, -38.5] | 65.6% → 5.7% | -59.9 [-72.4, -41.9] | 70.9% → 17.6% | -53.3 [-72.2, -37.1] |
| prepend 50 | 1,590 | 62.1% → 4.9% | -57.2 [-76.4, -30.2] | 70.9% → 7.6% | -63.4 [-78.7, -40.8] | 70.7% → 0.1% | -70.7 [-84.3, -50.9] |


## Differences between models in the change of TPR (group bootstrap), all malware

| edit | change A (J) − released Nebula, points [group 95%] | change C (J) − released Nebula, points [group 95%] | change C (J) − A (J), points [group 95%] |
|---|---|---|---|
| insert 1 | +0.1 [-1.3, +1.7] | -1.4 [-3.8, +0.3] | -1.5 [-3.2, -0.2] |
| insert 5 | -1.6 [-5.5, +2.0] | -4.5 [-14.4, +1.1] | -2.9 [-9.6, +1.7] |
| insert 20 | -5.3 [-11.0, +1.0] | +3.5 [-7.7, +14.9] | +8.7 [-1.9, +16.9] |
| insert 50 | -3.1 [-9.5, +3.4] | +0.1 [-14.5, +14.7] | +3.3 [-8.6, +14.8] |
| prepend 1 | -0.4 [-3.9, +3.2] | +0.7 [-4.0, +4.2] | +1.1 [-3.3, +4.7] |
| prepend 5 | -5.0 [-12.4, +1.4] | +15.1 [-2.7, +28.9] | +20.1 [+5.7, +30.2] |
| prepend 20 | +10.5 [+2.7, +19.1] | +31.8 [+18.8, +43.5] | +21.3 [+8.0, +33.1] |
| prepend 50 | +3.1 [-3.2, +11.6] | -14.2 [-22.5, -5.7] | -17.2 [-23.0, -12.4] |


## The same on malware that fits

| edit | change A (J) − released Nebula, points [group 95%] | change C (J) − released Nebula, points [group 95%] | change C (J) − A (J), points [group 95%] |
|---|---|---|---|
| insert 1 | -0.2 [-4.3, +3.7] | -5.0 [-11.5, +0.2] | -4.9 [-8.1, -1.7] |
| insert 5 | -4.2 [-14.9, +5.6] | -19.1 [-42.0, -1.2] | -14.9 [-28.2, -4.3] |
| insert 20 | -9.5 [-17.2, +1.0] | -13.8 [-26.7, -2.0] | -4.3 [-18.5, +5.7] |
| insert 50 | -6.4 [-19.4, +3.0] | -17.9 [-33.2, -6.7] | -11.5 [-23.8, -1.0] |
| prepend 1 | -1.2 [-7.6, +4.7] | -7.1 [-17.4, +1.4] | -6.0 [-11.0, -2.2] |
| prepend 5 | -10.4 [-18.1, -2.1] | -11.8 [-43.0, +14.6] | -1.5 [-27.6, +20.0] |
| prepend 20 | -2.5 [-12.4, +9.1] | +4.1 [-12.3, +16.7] | +6.6 [-9.4, +19.3] |
| prepend 50 | -6.2 [-19.9, +3.5] | -13.5 [-30.3, -3.0] | -7.3 [-19.6, +4.1] |


## C (J) versus A (J), seed-paired

Bootstrap over the 10 seeds only.

| edit | set | A (J) change | C (J) change | C − A, seed-paired [95% over seeds] |
|---|---|---|---|---|
| insert 1 | all malware | -2.0 | -3.6 | -1.5 [-2.3, -0.8] |
| insert 1 | malware that fits | -3.8 | -8.6 | -4.9 [-6.6, -2.9] |
| insert 5 | all malware | -10.5 | -13.4 | -2.9 [-5.1, -0.7] |
| insert 5 | malware that fits | -16.5 | -31.4 | -14.9 [-18.1, -11.4] |
| insert 20 | all malware | -33.9 | -25.1 | +8.7 [+4.7, +12.4] |
| insert 20 | malware that fits | -50.8 | -55.1 | -4.3 [-10.0, +0.4] |
| insert 50 | all malware | -42.2 | -38.9 | +3.3 [-0.5, +6.9] |
| insert 50 | malware that fits | -59.0 | -70.6 | -11.5 [-15.1, -7.7] |
| prepend 1 | all malware | -7.3 | -6.1 | +1.1 [-1.2, +3.5] |
| prepend 1 | malware that fits | -5.9 | -11.9 | -6.0 [-8.8, -2.6] |
| prepend 5 | all malware | -36.1 | -16.1 | +20.1 [+15.4, +24.5] |
| prepend 5 | malware that fits | -31.2 | -32.7 | -1.5 [-6.0, +2.5] |
| prepend 20 | all malware | -52.4 | -31.1 | +21.3 [+16.0, +25.9] |
| prepend 20 | malware that fits | -59.9 | -53.3 | +6.6 [+0.4, +11.9] |
| prepend 50 | all malware | -55.9 | -73.1 | -17.2 [-20.6, -14.2] |
| prepend 50 | malware that fits | -63.4 | -70.7 | -7.3 [-11.2, -3.6] |
