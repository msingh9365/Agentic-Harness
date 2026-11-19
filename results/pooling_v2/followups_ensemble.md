# Follow-up: seed ensembles

The logits of the 10 seeds of a variant are averaged and the averaged score is evaluated once. (S) = trained on the January train side, each seed at its validation-AUC epoch; (J) = trained on all of January for the fixed epoch count (A=1,C=10). Thresholds: (a) from the April benign scores. 95% group-bootstrap intervals.

## Single seeds versus the ensemble (all April reports)

| model | mean single-seed AUC | mean single-seed TPR@1% (a) | ensemble AUC | ensemble TPR@1% (a) |
|---|---|---|---|---|
| A (S) | 0.9325 | 66.4% | 0.9424 | 73.7% |
| B (S) | 0.9287 | 56.0% | 0.9386 | 63.4% |
| C (S) | 0.9416 | 67.0% | 0.9454 | 67.3% |
| A (J) | 0.9486 | 71.9% | 0.9590 | 75.5% |
| C (J) | 0.9644 | 73.8% | 0.9672 | 75.0% |


## Ensembles and the released Nebula

| subset | model | AUC | TPR@1% (a) | TPR@0.1% (a) |
|---|---|---|---|---|
| all | A ensemble (S) | 0.9424 [0.8985, 0.9741] | 73.7% [63.4%, 82.2%] | 51.2% [30.2%, 66.6%] |
| all | B ensemble (S) | 0.9386 [0.8989, 0.9679] | 63.4% [39.7%, 77.9%] | 13.0% [5.2%, 30.9%] |
| all | C ensemble (S) | 0.9454 [0.9086, 0.9723] | 67.3% [49.6%, 81.5%] | 30.4% [8.9%, 55.5%] |
| all | A ensemble (J) | 0.9590 [0.9270, 0.9795] | 75.5% [64.2%, 83.8%] | 43.3% [27.3%, 60.1%] |
| all | C ensemble (J) | 0.9672 [0.9449, 0.9815] | 75.0% [61.0%, 84.7%] | 25.3% [12.6%, 51.6%] |
| all | released Nebula | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 51.7% [0.0%, 67.0%] |
| seen | A ensemble (S) | 0.9791 [0.9497, 0.9933] | 84.5% [75.2%, 91.7%] | 63.9% [47.3%, 75.6%] |
| seen | B ensemble (S) | 0.9654 [0.9342, 0.9841] | 74.0% [55.4%, 85.1%] | 13.3% [6.8%, 26.8%] |
| seen | C ensemble (S) | 0.9724 [0.9421, 0.9889] | 80.1% [65.8%, 89.2%] | 37.6% [14.2%, 70.5%] |
| seen | A ensemble (J) | 0.9876 [0.9743, 0.9946] | 82.9% [73.4%, 91.0%] | 49.2% [33.2%, 71.7%] |
| seen | C ensemble (J) | 0.9874 [0.9764, 0.9934] | 83.6% [68.7%, 92.5%] | 38.6% [19.0%, 70.4%] |
| seen | released Nebula | 0.9865 [0.9709, 0.9944] | 82.1% [71.8%, 89.5%] | 61.3% [0.0%, 75.7%] |
| unseen | A ensemble (S) | 0.9149 [0.8512, 0.9646] | 68.9% [53.7%, 79.9%] | 45.5% [18.6%, 66.1%] |
| unseen | B ensemble (S) | 0.9115 [0.8498, 0.9608] | 58.7% [31.4%, 77.4%] | 12.9% [2.6%, 36.0%] |
| unseen | C ensemble (S) | 0.9205 [0.8641, 0.9646] | 61.5% [40.2%, 80.6%] | 27.1% [4.5%, 52.7%] |
| unseen | A ensemble (J) | 0.9335 [0.8734, 0.9704] | 72.1% [54.6%, 82.9%] | 40.6% [17.3%, 59.8%] |
| unseen | C ensemble (J) | 0.9472 [0.9023, 0.9741] | 71.2% [49.9%, 83.8%] | 19.3% [4.9%, 46.7%] |
| unseen | released Nebula | 0.9371 [0.8897, 0.9672] | 71.8% [56.3%, 82.1%] | 47.4% [0.0%, 66.1%] |
| distance Q1 (≤ 0.031) | A ensemble (S) | 0.9285 [0.8247, 0.9960] | 76.4% [53.1%, 94.1%] | 52.8% [11.1%, 88.9%] |
| distance Q1 (≤ 0.031) | B ensemble (S) | 0.9150 [0.8242, 0.9953] | 57.4% [18.3%, 92.3%] | 0.1% [0.0%, 42.9%] |
| distance Q1 (≤ 0.031) | C ensemble (S) | 0.9291 [0.8530, 0.9944] | 62.7% [22.2%, 92.1%] | 30.0% [0.1%, 77.8%] |
| distance Q1 (≤ 0.031) | A ensemble (J) | 0.9729 [0.8816, 0.9954] | 88.6% [59.6%, 97.0%] | 75.6% [36.1%, 88.7%] |
| distance Q1 (≤ 0.031) | C ensemble (J) | 0.9856 [0.9463, 0.9961] | 86.6% [55.1%, 95.9%] | 29.8% [0.1%, 72.6%] |
| distance Q1 (≤ 0.031) | released Nebula | 0.9775 [0.9107, 0.9959] | 87.4% [56.6%, 96.0%] | 61.5% [0.0%, 89.4%] |
| distance Q2-Q4 (farther three quartiles) | A ensemble (S) | 0.9239 [0.8626, 0.9617] | 63.2% [42.0%, 76.4%] | 39.9% [11.0%, 60.2%] |
| distance Q2-Q4 (farther three quartiles) | B ensemble (S) | 0.9126 [0.8461, 0.9575] | 59.7% [28.9%, 74.6%] | 22.6% [4.3%, 46.8%] |
| distance Q2-Q4 (farther three quartiles) | C ensemble (S) | 0.9232 [0.8614, 0.9630] | 60.6% [39.8%, 79.8%] | 24.9% [5.3%, 50.5%] |
| distance Q2-Q4 (farther three quartiles) | A ensemble (J) | 0.9012 [0.8222, 0.9534] | 59.4% [39.0%, 74.5%] | 13.8% [4.0%, 41.1%] |
| distance Q2-Q4 (farther three quartiles) | C ensemble (J) | 0.9196 [0.8573, 0.9618] | 59.3% [34.0%, 77.7%] | 11.2% [3.8%, 41.2%] |
| distance Q2-Q4 (farther three quartiles) | released Nebula | 0.9081 [0.8549, 0.9501] | 59.7% [44.1%, 73.2%] | 36.6% [0.0%, 58.3%] |


## Paired differences

| difference | subset | AUC | TPR@1% (a) | TPR@0.1% (a) | TPR@1% (b) |
|---|---|---|---|---|---|
| C ensemble (S) − A ensemble (S) | all | +0.0029 [-0.0126, +0.0231] | -6.5 [-18.0, +6.4] | -20.8 [-39.6, -1.3] | -6.7 [-15.5, +0.9] |
| C ensemble (S) − A ensemble (S) | seen | -0.0067 [-0.0144, -0.0009] | -4.4 [-13.8, +1.5] | -26.2 [-48.4, +3.0] | -4.0 [-9.8, +1.8] |
| C ensemble (S) − A ensemble (S) | unseen | +0.0056 [-0.0213, +0.0400] | -7.4 [-22.0, +10.9] | -18.4 [-39.1, +3.4] | -7.9 [-19.4, +2.9] |
| C ensemble (S) − A ensemble (S) | distance Q1 (≤ 0.031) | +0.0006 [-0.0501, +0.0816] | -13.7 [-38.0, +0.2] | -22.8 [-68.1, -1.4] | -16.5 [-35.4, -1.0] |
| C ensemble (S) − A ensemble (S) | distance Q2-Q4 (farther three quartiles) | -0.0008 [-0.0409, +0.0403] | -2.6 [-13.5, +19.1] | -14.9 [-30.7, +16.8] | -1.3 [-12.2, +7.7] |
| B ensemble (S) − A ensemble (S) | all | -0.0038 [-0.0186, +0.0124] | -10.3 [-27.7, -1.5] | -38.2 [-52.0, -14.2] | -20.8 [-31.2, -11.9] |
| B ensemble (S) − A ensemble (S) | seen | -0.0137 [-0.0235, -0.0055] | -10.5 [-24.6, -2.4] | -50.5 [-63.3, -28.9] | -14.5 [-22.3, -8.4] |
| B ensemble (S) − A ensemble (S) | unseen | -0.0034 [-0.0270, +0.0248] | -10.2 [-31.8, +0.2] | -32.6 [-51.1, -2.6] | -23.6 [-37.8, -10.8] |
| B ensemble (S) − A ensemble (S) | distance Q1 (≤ 0.031) | -0.0135 [-0.0669, +0.0536] | -19.0 [-43.3, +0.7] | -52.7 [-86.2, -8.4] | -20.5 [-39.8, -4.2] |
| B ensemble (S) − A ensemble (S) | distance Q2-Q4 (farther three quartiles) | -0.0113 [-0.0471, +0.0178] | -3.4 [-28.5, +1.6] | -17.2 [-28.5, +17.2] | -25.9 [-41.7, -7.1] |
| C ensemble (S) − B ensemble (S) | all | +0.0068 [+0.0009, +0.0143] | +3.8 [-0.3, +16.8] | +17.4 [-4.9, +38.2] | +14.1 [+6.9, +24.5] |
| C ensemble (S) − B ensemble (S) | seen | +0.0070 [-0.0001, +0.0159] | +6.1 [+1.2, +13.8] | +24.3 [+2.3, +57.2] | +10.5 [+5.8, +17.1] |
| C ensemble (S) − B ensemble (S) | unseen | +0.0090 [-0.0009, +0.0218] | +2.8 [-2.0, +19.2] | +14.3 [-9.8, +34.5] | +15.7 [+5.6, +30.2] |
| C ensemble (S) − B ensemble (S) | distance Q1 (≤ 0.031) | +0.0141 [-0.0032, +0.0356] | +5.4 [-5.9, +18.4] | +29.9 [+0.0, +70.7] | +4.0 [+1.6, +13.4] |
| C ensemble (S) − B ensemble (S) | distance Q2-Q4 (farther three quartiles) | +0.0105 [-0.0028, +0.0359] | +0.8 [-0.4, +25.5] | +2.3 [-19.5, +10.3] | +24.6 [+8.0, +42.9] |
| A ensemble (S) − released Nebula | all | -0.0162 [-0.0491, +0.0114] | -1.2 [-11.7, +8.3] | -0.5 [-19.6, +57.2] | -8.2 [-19.0, +1.3] |
| A ensemble (S) − released Nebula | seen | -0.0074 [-0.0330, +0.0095] | +2.4 [-7.0, +10.6] | +2.5 [-13.5, +67.4] | -3.1 [-12.1, +4.5] |
| A ensemble (S) − released Nebula | unseen | -0.0222 [-0.0747, +0.0235] | -2.9 [-17.3, +10.6] | -1.9 [-25.8, +54.0] | -10.5 [-25.4, +1.8] |
| A ensemble (S) − released Nebula | distance Q1 (≤ 0.031) | -0.0490 [-0.1119, +0.0040] | -11.0 [-27.2, +4.4] | -8.6 [-26.1, +73.9] | -16.5 [-37.2, +0.7] |
| A ensemble (S) − released Nebula | distance Q2-Q4 (farther three quartiles) | +0.0159 [-0.0246, +0.0536] | +3.4 [-19.0, +17.3] | +3.3 [-33.6, +43.8] | -5.9 [-25.6, +5.7] |
| C ensemble (S) − released Nebula | all | -0.0132 [-0.0450, +0.0116] | -7.7 [-26.0, +7.1] | -21.3 [-41.7, +36.8] | -14.9 [-33.2, -0.3] |
| C ensemble (S) − released Nebula | seen | -0.0141 [-0.0391, +0.0018] | -2.0 [-13.6, +6.2] | -23.7 [-48.5, +44.4] | -7.1 [-16.0, +0.5] |
| C ensemble (S) − released Nebula | unseen | -0.0166 [-0.0672, +0.0253] | -10.3 [-33.3, +9.9] | -20.2 [-42.9, +33.1] | -18.4 [-43.0, +2.6] |
| C ensemble (S) − released Nebula | distance Q1 (≤ 0.031) | -0.0484 [-0.1226, +0.0205] | -24.7 [-64.2, +0.5] | -31.5 [-70.1, +43.8] | -33.0 [-72.6, -2.2] |
| C ensemble (S) − released Nebula | distance Q2-Q4 (farther three quartiles) | +0.0151 [-0.0120, +0.0378] | +0.8 [-18.3, +17.3] | -11.6 [-35.3, +30.6] | -7.2 [-27.5, +9.3] |
| C ensemble (J) − A ensemble (J) | all | +0.0082 [-0.0010, +0.0217] | -0.4 [-9.4, +5.7] | -18.0 [-33.5, +9.6] | — |
| C ensemble (J) − A ensemble (J) | seen | -0.0002 [-0.0048, +0.0075] | +0.6 [-10.7, +7.7] | -10.6 [-36.9, +21.6] | — |
| C ensemble (J) − A ensemble (J) | unseen | +0.0136 [-0.0020, +0.0376] | -0.9 [-10.4, +6.6] | -21.4 [-38.0, +8.7] | — |
| C ensemble (J) − A ensemble (J) | distance Q1 (≤ 0.031) | +0.0127 [-0.0010, +0.0658] | -2.0 [-7.8, +1.2] | -45.8 [-73.6, -3.4] | — |
| C ensemble (J) − A ensemble (J) | distance Q2-Q4 (farther three quartiles) | +0.0185 [-0.0050, +0.0530] | -0.1 [-14.0, +12.2] | -2.6 [-21.2, +28.3] | — |
| A ensemble (J) − released Nebula | all | +0.0004 [-0.0126, +0.0112] | +0.5 [-7.8, +7.5] | -8.4 [-26.3, +47.2] | — |
| A ensemble (J) − released Nebula | seen | +0.0011 [-0.0066, +0.0088] | +0.8 [-7.1, +8.6] | -12.1 [-33.2, +58.1] | — |
| A ensemble (J) − released Nebula | unseen | -0.0036 [-0.0291, +0.0171] | +0.3 [-12.1, +9.2] | -6.8 [-30.9, +44.6] | — |
| A ensemble (J) − released Nebula | distance Q1 (≤ 0.031) | -0.0046 [-0.0322, +0.0054] | +1.2 [-1.6, +5.7] | +14.1 [-9.7, +78.7] | — |
| A ensemble (J) − released Nebula | distance Q2-Q4 (farther three quartiles) | -0.0069 [-0.0609, +0.0327] | -0.3 [-21.8, +13.4] | -22.8 [-47.5, +16.6] | — |
| C ensemble (J) − released Nebula | all | +0.0086 [-0.0003, +0.0210] | +0.0 [-11.6, +9.0] | -26.4 [-42.1, +31.4] | — |
| C ensemble (J) − released Nebula | seen | +0.0009 [-0.0046, +0.0091] | +1.4 [-11.9, +11.3] | -22.7 [-45.4, +45.4] | — |
| C ensemble (J) − released Nebula | unseen | +0.0100 [-0.0047, +0.0306] | -0.6 [-16.0, +10.2] | -28.1 [-46.0, +25.9] | — |
| C ensemble (J) − released Nebula | distance Q1 (≤ 0.031) | +0.0081 [-0.0031, +0.0404] | -0.8 [-5.4, +2.1] | -31.7 [-66.0, +47.2] | — |
| C ensemble (J) − released Nebula | distance Q2-Q4 (farther three quartiles) | +0.0116 [-0.0180, +0.0388] | -0.4 [-22.8, +15.9] | -25.4 [-46.6, +16.7] | — |
