**Clean April test results (17,402 reports), mean ± std over 10 seeds and 10-seed ensembles. TPR@x: true-positive rate at a threshold giving false-positive rate x on the April benign reports; the paper row gives the two numbers we take from the Nebula paper.**

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 (threshold 0.5) | pAUC@1e-2 |
|---|---|---|---|---|---|
| Nebula paper (Table 7) | 0.521 | - | - | 0.914 | - |
| M1 Nebula | 0.536 ± 0.060 | 0.791 ± 0.020 | 0.9639 ± 0.0111 | 0.891 ± 0.027 | 0.686 ± 0.026 |
| M2 two-level | 0.381 ± 0.165 | 0.772 ± 0.049 | 0.9690 ± 0.0073 | 0.898 ± 0.022 | 0.620 ± 0.080 |
| M3 ATT+bal | 0.567 ± 0.047 | 0.790 ± 0.019 | 0.9693 ± 0.0065 | 0.913 ± 0.011 | 0.705 ± 0.025 |
| M4 ATT+bal-2L | 0.453 ± 0.149 | 0.779 ± 0.017 | 0.9677 ± 0.0052 | 0.911 ± 0.013 | 0.661 ± 0.035 |
| 10-seed ensemble (mean logit) |  |  |  |  |  |
| M1 Nebula (ensemble) | 0.663 | 0.837 | 0.9705 | 0.913 | 0.756 |
| M2 two-level (ensemble) | 0.541 | 0.801 | 0.9752 | 0.910 | 0.698 |
| M3 ATT+bal (ensemble) | 0.597 | 0.800 | 0.9752 | 0.919 | 0.730 |
| M4 ATT+bal-2L (ensemble) | 0.629 | 0.803 | 0.9777 | 0.917 | 0.719 |
