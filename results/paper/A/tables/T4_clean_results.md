**Clean April test results (17,402 reports), mean ± std over 10 seeds and 10-seed ensembles. TPR@x: true-positive rate at a threshold giving false-positive rate x on the April benign reports; the paper row gives the two numbers we take from the Nebula paper.**

| model | TPR@1e-3 | TPR@1e-2 | AUC | F1 (threshold 0.5) | pAUC@1e-2 |
|---|---|---|---|---|---|
| Nebula paper (Table 7) | 0.521 | - | - | 0.914 | - |
| M1 v2-PE | 0.541 ± 0.095 | 0.780 ± 0.038 | 0.9667 ± 0.0071 | 0.899 ± 0.021 | 0.674 ± 0.053 |
| M2 two-level | 0.344 ± 0.189 | 0.751 ± 0.068 | 0.9670 ± 0.0105 | 0.888 ± 0.038 | 0.562 ± 0.146 |
| M3 ATT+bal | 0.590 ± 0.029 | 0.790 ± 0.008 | 0.9694 ± 0.0044 | 0.908 ± 0.011 | 0.710 ± 0.015 |
| M4 ATT+bal-2L | 0.461 ± 0.174 | 0.778 ± 0.021 | 0.9679 ± 0.0075 | 0.910 ± 0.010 | 0.663 ± 0.036 |
| 10-seed ensemble (mean logit) |  |  |  |  |  |
| M1 v2-PE (ensemble) | 0.622 | 0.843 | 0.9738 | 0.921 | 0.739 |
| M2 two-level (ensemble) | 0.532 | 0.802 | 0.9749 | 0.914 | 0.675 |
| M3 ATT+bal (ensemble) | 0.603 | 0.801 | 0.9748 | 0.921 | 0.731 |
| M4 ATT+bal-2L (ensemble) | 0.628 | 0.812 | 0.9767 | 0.917 | 0.725 |
