### Item 4: clean April results of the malware-only padding models next to the final M1 and M3 (corrected tokenizer, 10 seeds; descriptive)

| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1 | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|---|
| M1 Nebula (final, no padding) | 10 | 0.536 ± 0.060 | 0.791 ± 0.020 | 0.9639 ± 0.0111 | 0.891 ± 0.027 | 0.686 ± 0.026 | 0.398 ± 0.095 |
| M1 settings + malware-only padding | 10 | 0.565 ± 0.095 | 0.793 ± 0.031 | 0.9707 ± 0.0092 | 0.905 ± 0.016 | 0.702 ± 0.038 | 0.452 ± 0.064 |
| M3 ATT+bal (final, balanced padding) | 10 | 0.567 ± 0.047 | 0.790 ± 0.019 | 0.9693 ± 0.0065 | 0.913 ± 0.011 | 0.705 ± 0.025 | 0.443 ± 0.089 |
| M3 settings + malware-only padding | 10 | 0.553 ± 0.090 | 0.787 ± 0.018 | 0.9669 ± 0.0064 | 0.903 ± 0.011 | 0.703 ± 0.028 | 0.418 ± 0.090 |


10-seed ensembles:

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 (threshold 0.5) | **pAUC@1e-2** | pAUC@1e-3 |
|---|---|---|---|---|---|---|
| M1 Nebula (final, no padding) | 0.663 | 0.837 | 0.9705 | 0.913 | **0.756** | 0.552 |
| M1 settings + malware-only padding | 0.668 | 0.843 | 0.9812 | 0.921 | **0.777** | 0.597 |
| M3 ATT+bal (final, balanced padding) | 0.597 | 0.800 | 0.9752 | 0.919 | **0.730** | 0.532 |
| M3 settings + malware-only padding | 0.642 | 0.804 | 0.9704 | 0.916 | **0.744** | 0.518 |


### Paired differences (points ×100; stratified and cluster 95% CI; seeds paired by index only)

| difference | metric | mean difference | stratified 95% CI | cluster 95% CI | seeds | outcome (pAUC only) |
|---|---|---|---|---|---|---|
| M1 settings + malware-only padding − M1 Nebula (final, no padding) | **pAUC@1e-2** | +1.55 | [+0.04, +3.12] | [-1.72, +5.08] | 6 up / 4 down | not resolved |
| M1 settings + malware-only padding − M1 Nebula (final, no padding) | TPR@1e-3 | +2.86 | [-2.25, +7.92] | [-4.81, +9.36] | 6 up / 4 down |  |
| M1 settings + malware-only padding − M1 Nebula (final, no padding) | TPR@1e-2 | +0.16 | [-0.67, +1.11] | [-1.77, +4.33] | 5 up / 5 down |  |
| M1 settings + malware-only padding − M1 Nebula (final, no padding) | AUC | +0.69 | [+0.60, +0.77] | [+0.13, +1.51] | 9 up / 1 down |  |
| M3 settings + malware-only padding − M3 ATT+bal (final, balanced padding) | **pAUC@1e-2** | -0.19 | [-1.94, +1.54] | [-2.48, +2.06] | 3 up / 7 down | not resolved |
| M3 settings + malware-only padding − M3 ATT+bal (final, balanced padding) | TPR@1e-3 | -1.37 | [-6.28, +3.97] | [-8.67, +5.44] | 5 up / 5 down |  |
| M3 settings + malware-only padding − M3 ATT+bal (final, balanced padding) | TPR@1e-2 | -0.36 | [-0.97, +0.29] | [-1.57, +1.00] | 5 up / 5 down |  |
| M3 settings + malware-only padding − M3 ATT+bal (final, balanced padding) | AUC | -0.24 | [-0.32, -0.17] | [-0.86, +0.17] | 4 up / 6 down |  |


