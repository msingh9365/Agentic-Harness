### Item 3 under attack: effects of head and padding and their interaction (points x100; mean of the 10-seed means; cluster 95% bootstrap interval; thresholds at 1% FPR on each model's own clean April scores)

**detection**

| effect | unedited | random_20_prepend | random_50_prepend | lgbm_50_prepend |
|---|---|---|---|---|
| head, no padding (attention - flatten) | **-4.7 [-8.3, -1.1]** | **+29.5 [+18.5, +39.6]** | -2.6 [-8.0, +2.5] | **-5.5 [-10.0, -2.2]** |
| head, balanced padding (attention - flatten) | +0.6 [-1.4, +2.4] | **+5.3 [+1.7, +9.7]** | **+14.9 [+9.7, +18.7]** | **+41.6 [+28.2, +53.3]** |
| padding, flatten head (balanced - none) | -2.2 [-5.8, +1.5] | **+52.2 [+40.8, +62.3]** | **+35.6 [+25.0, +45.7]** | -3.2 [-6.9, +0.0] |
| padding, attention head (balanced - none) | +3.2 [-0.9, +7.2] | **+28.0 [+19.4, +39.4]** | **+53.1 [+42.0, +61.2]** | **+43.9 [+30.2, +56.0]** |
| interaction (ab - an) - (fb - fn) | **+5.3 [+1.7, +8.7]** | **-24.3 [-36.9, -10.3]** | **+17.5 [+10.1, +23.7]** | **+47.1 [+32.9, +58.6]** |

**padded-benign FPR**

| effect | unedited | random_20_prepend | random_50_prepend | lgbm_50_prepend |
|---|---|---|---|---|
| head, no padding (attention - flatten) | -0.0 [-0.1, +0.0] | **-3.6 [-6.4, -1.7]** | **-5.4 [-8.4, -3.2]** | -0.0 [-0.0, +0.0] |
| head, balanced padding (attention - flatten) | -0.0 [-0.0, +0.0] | -0.3 [-0.8, +0.0] | **-0.6 [-1.3, -0.3]** | **+0.1 [+0.1, +0.2]** |
| padding, flatten head (balanced - none) | +0.0 [-0.0, +0.0] | **-2.5 [-5.0, -0.8]** | **-4.1 [-6.5, -2.2]** | -0.0 [-0.0, +0.0] |
| padding, attention head (balanced - none) | -0.0 [-0.0, +0.1] | **+0.8 [+0.6, +1.0]** | **+0.7 [+0.5, +1.1]** | **+0.1 [+0.1, +0.2]** |
| interaction (ab - an) - (fb - fn) | -0.0 [-0.0, +0.1] | **+3.3 [+1.6, +5.8]** | **+4.8 [+2.7, +7.5]** | **+0.1 [+0.1, +0.2]** |

Bold = the cluster interval excludes 0.
