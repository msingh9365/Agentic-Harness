### Differences under attack at the 1% threshold (points x100; difference of the 10-seed mean detection or padded-benign FPR; cluster 95% interval, 1,000 resamples; **bold** = the interval excludes 0)

**detection**

| difference | unedited | random_20_prepend | random_50_prepend | random_100_prepend | random_200_insert | lgbm_50_prepend |
|---|---|---|---|---|---|---|
| LightGBM - M1 | **-24.3 [-38.2, -9.3]** | -1.0 [-11.5, +7.0] | +2.5 [-0.6, +5.3] | **-2.6 [-5.3, -0.5]** | **-18.4 [-27.5, -11.2]** | **-1.9 [-3.4, -0.9]** |
| LightGBM - M3 | **-24.2 [-38.9, -11.0]** | **-51.8 [-62.9, -39.5]** | **-55.1 [-66.2, -41.9]** | **-3.3 [-7.3, -1.2]** | **-43.8 [-55.5, -30.8]** | **-35.1 [-48.2, -22.9]** |

**padded-benign FPR**

| difference | unedited | random_20_prepend | random_50_prepend | random_100_prepend | random_200_insert | lgbm_50_prepend |
|---|---|---|---|---|---|---|
| LightGBM - M1 | -0.0 [-0.4, +0.0] | **-1.1 [-2.0, -0.3]** | **-1.0 [-2.1, -0.2]** | **-1.4 [-2.8, -0.3]** | **-0.8 [-1.7, -0.2]** | -0.0 [-0.0, +0.0] |
| LightGBM - M3 | -0.0 [-0.4, +0.0] | **-0.9 [-1.3, -0.7]** | **-0.8 [-1.4, -0.5]** | **-0.3 [-0.6, -0.1]** | **-0.4 [-0.7, -0.3]** | **-0.1 [-0.1, -0.0]** |

