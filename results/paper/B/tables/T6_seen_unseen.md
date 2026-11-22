**April reports whose API sequence is seen / unseen in the model's own training set (seen: 6,329 reports (2,914 malware, 637 groups); unseen: 11,073 reports (6,485 malware, 1,872 groups)); metrics computed inside each subset, mean ± std over 10 seeds; CI = cluster bootstrap of the seed mean.**

| model | pAUC@1e-2 seen | cluster 95% CI | TPR@1e-2 seen | pAUC@1e-2 unseen | cluster 95% CI | TPR@1e-2 unseen |
|---|---|---|---|---|---|---|
| M1 v2-PE | 0.800 ± 0.038 | [0.687, 0.884] | 0.903 ± 0.027 | 0.633 ± 0.029 | [0.472, 0.754] | 0.729 ± 0.034 |
| M2 two-level | 0.716 ± 0.113 | [0.564, 0.835] | 0.882 ± 0.048 | 0.577 ± 0.071 | [0.428, 0.698] | 0.709 ± 0.049 |
| M3 ATT+bal | 0.824 ± 0.040 | [0.714, 0.901] | 0.916 ± 0.009 | 0.650 ± 0.019 | [0.460, 0.770] | 0.721 ± 0.018 |
| M4 ATT+bal-2L | 0.804 ± 0.050 | [0.703, 0.884] | 0.899 ± 0.011 | 0.589 ± 0.040 | [0.423, 0.710] | 0.724 ± 0.031 |
