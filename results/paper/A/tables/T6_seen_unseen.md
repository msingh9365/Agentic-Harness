**April reports whose API sequence is seen / unseen in the model's own training set (seen: 6,329 reports (2,914 malware, 637 groups); unseen: 11,073 reports (6,485 malware, 1,872 groups)); metrics computed inside each subset, mean ± std over 10 seeds; CI = cluster bootstrap of the seed mean.**

| model | pAUC@1e-2 seen | cluster 95% CI | TPR@1e-2 seen | pAUC@1e-2 unseen | cluster 95% CI | TPR@1e-2 unseen |
|---|---|---|---|---|---|---|
| M1 v2-PE | 0.793 ± 0.042 | [0.685, 0.875] | 0.898 ± 0.034 | 0.617 ± 0.060 | [0.455, 0.738] | 0.711 ± 0.051 |
| M2 two-level | 0.677 ± 0.126 | [0.498, 0.818] | 0.900 ± 0.016 | 0.513 ± 0.160 | [0.379, 0.643] | 0.673 ± 0.083 |
| M3 ATT+bal | 0.834 ± 0.022 | [0.728, 0.909] | 0.912 ± 0.008 | 0.650 ± 0.017 | [0.465, 0.771] | 0.721 ± 0.016 |
| M4 ATT+bal-2L | 0.817 ± 0.026 | [0.716, 0.889] | 0.899 ± 0.010 | 0.585 ± 0.050 | [0.425, 0.703] | 0.717 ± 0.037 |
