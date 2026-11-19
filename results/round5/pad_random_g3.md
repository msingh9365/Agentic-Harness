# Padding variant `random` 

Padding: random single calls of random EVAL reports (the round 4 test). k = 1, 5, 20, 50, inserted at random places or prepended. Malware: 9,399 April reports; benign: 2,000 random April reports edited the same way. Thresholds fixed at 1% and 0.1% FPR on the unedited April benign scores of each model and seed; mean over seeds (seeds per model in the json). Edited reports exist in memory only.


## Threshold of 1% FPR: malware TPR after the edit, all 9,399 malware reports

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | 76.1% | 75.3% | 74.1% | 69.9% | 64.2% | 75.8% | 75.0% | 73.9% | 71.3% |


Change in points [group 95%]

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | -0.8 [-1.5, -0.3] | -2.1 [-3.7, -0.9] | -6.2 [-11.4, -3.1] | -12.0 [-22.4, -6.0] | -0.3 [-1.0, +0.2] | -1.1 [-2.7, +0.2] | -2.3 [-3.9, -1.0] | -4.9 [-8.2, -2.7] |


## Threshold of 1% FPR: reports that fit in 512 tokens after the edit, TPR before → after

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | 68.3% → 65.9% | 68.3% → 63.5% | 68.0% → 49.8% | 65.6% → 19.1% | 68.3% → 67.3% | 68.3% → 66.3% | 68.3% → 62.3% | 65.7% → 45.4% |


Change in points [group 95%]

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | -2.3 [-5.2, -0.7] | -4.8 [-10.6, -1.1] | -18.2 [-29.5, -7.8] | -46.5 [-64.6, -23.1] | -1.0 [-3.2, +0.6] | -2.0 [-7.2, +1.2] | -6.0 [-12.2, -2.3] | -20.3 [-25.2, -14.2] |


## Threshold of 1% FPR: FPR of the 2,000 benign April reports padded the same way

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | 1.15% | 1.14% | 1.05% | 0.91% | 0.71% | 1.25% | 1.24% | 1.24% | 0.88% |


## Threshold of 0.1% FPR: malware TPR after the edit, all 9,399 malware reports

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | 55.0% | 53.0% | 49.3% | 42.9% | 35.7% | 54.1% | 51.7% | 49.0% | 44.7% |


Change in points [group 95%]

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | -2.0 [-4.9, -0.2] | -5.7 [-13.0, -1.7] | -12.1 [-21.0, -6.5] | -19.3 [-27.8, -12.9] | -0.9 [-3.0, +0.7] | -3.3 [-9.6, +0.5] | -6.0 [-12.3, -2.3] | -10.4 [-19.1, -5.4] |


## Threshold of 0.1% FPR: reports that fit in 512 tokens after the edit, TPR before → after

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | 51.3% → 46.3% | 51.4% → 36.6% | 49.7% → 22.7% | 44.6% → 2.6% | 51.3% → 48.3% | 51.4% → 40.7% | 50.1% → 35.2% | 44.5% → 10.8% |


Change in points [group 95%]

| model | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | -5.0 [-11.9, -0.5] | -14.7 [-33.0, -2.7] | -27.0 [-47.8, -9.8] | -42.0 [-59.1, -19.8] | -3.0 [-7.6, +0.5] | -10.7 [-25.8, -0.8] | -15.0 [-29.6, -4.4] | -33.7 [-53.8, -11.9] |


## Threshold of 0.1% FPR: FPR of the 2,000 benign April reports padded the same way

| model | unedited | insert 1 | insert 5 | insert 20 | insert 50 | prepend 1 | prepend 5 | prepend 20 | prepend 50 |
|---|---|---|---|---|---|---|---|---|---|
| ATT+bal whole report (G3) | 0.15% | 0.17% | 0.16% | 0.10% | 0.07% | 0.22% | 0.16% | 0.14% | 0.08% |
