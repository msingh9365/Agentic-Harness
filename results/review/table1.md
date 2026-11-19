**Table 1. Clean April data (9,399 malware, 8,003 benign), logit-ranked; per-seed mean ± std (n = seeds) and 10-seed ensemble.**

| model | n | pAUC@1e-2 | TPR@1e-2 | TPR@1e-3 | AUC | pAUC@1e-2 (ens.) | TPR@1e-2 (ens.) | TPR@1e-3 (ens.) | AUC (ens.) |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint (1 model) | 1 | 0.659 | 0.750 | 0.518 | 0.9586 | — | — | — | — |
| baseline v2 (released code) | 10 | 0.690 ± 0.036 | 0.788 ± 0.026 | 0.527 ± 0.082 | 0.9624 ± 0.0050 | 0.762 | 0.852 | 0.636 | 0.9722 |
| **baseline v2-PE** (the baseline) | 10 | 0.705 ± 0.031 | 0.811 ± 0.023 | 0.543 ± 0.063 | 0.9644 ± 0.0093 | 0.768 | 0.851 | 0.606 | 0.9705 |
| **ATT+bal** (attention pooling + balanced padding) | 10 | 0.707 ± 0.017 | 0.795 ± 0.020 | 0.572 ± 0.061 | 0.9713 ± 0.0066 | 0.734 | 0.814 | 0.583 | 0.9780 |
| v2-PE + balanced padding (PE+bal, flatten) | 10 | 0.699 ± 0.022 | 0.787 ± 0.016 | 0.551 ± 0.053 | 0.9553 ± 0.0110 | 0.735 | 0.805 | 0.592 | 0.9651 |
| ATT+bal-keep (attention, balanced padding, clean copies kept) | 10 | 0.693 ± 0.022 | 0.792 ± 0.014 | 0.537 ± 0.057 | 0.9689 ± 0.0042 | 0.721 | 0.809 | 0.581 | 0.9750 |
| PE+bal-keep (flatten, balanced padding, clean copies kept) | 10 | 0.696 ± 0.023 | 0.793 ± 0.020 | 0.513 ± 0.061 | 0.9556 ± 0.0091 | 0.740 | 0.809 | 0.629 | 0.9623 |
| ATT+aug (attention, padding of malware only) | 10 | 0.700 ± 0.064 | 0.789 ± 0.042 | 0.565 ± 0.081 | 0.9661 ± 0.0093 | 0.746 | 0.814 | 0.603 | 0.9713 |
| PE+aug (flatten, padding of malware only) | 10 | 0.725 ± 0.037 | 0.812 ± 0.030 | 0.587 ± 0.069 | 0.9690 ± 0.0097 | 0.778 | 0.847 | 0.682 | 0.9767 |


**Claim rule against v2-PE** (primary metric pAUC@1e-2; CI of the per-seed means excludes 0 and the same sign in ≥ 7 of 10 seeds; points × 100; ensembles: CI only):

| difference | per-seed means, pAUC@1e-2 | seeds > 0 | claim rule | 10-seed ensembles, pAUC@1e-2 |
|---|---|---|---|---|
| attbal − v2_pe | +0.23 [-1.70, +2.09] | 4/10 | not resolved | -3.42 [-5.37, -1.55] resolved |
| pebal − v2_pe | -0.64 [-2.14, +0.76] | 3/10 | not resolved | -3.34 [-4.72, -2.02] resolved |
| attkeep − v2_pe | -1.17 [-3.17, +0.96] | 3/10 | not resolved | -4.70 [-6.80, -2.60] resolved |
| pekeep − v2_pe | -0.87 [-2.47, +0.69] | 4/10 | not resolved | -2.88 [-4.19, -1.46] resolved |
| attaug − v2_pe | -0.45 [-2.34, +1.50] | 5/10 | not resolved | -2.30 [-4.19, -0.38] resolved |
| peaug − v2_pe | +2.01 [+0.46, +3.49] | 6/10 | not resolved | +1.00 [-0.65, +2.55] not resolved |
| attbal − pebal | +0.87 [-0.55, +2.33] | 6/10 | not resolved | -0.08 [-1.67, +1.54] not resolved |
| attkeep − pekeep | -0.31 [-1.79, +1.16] | 6/10 | not resolved | -1.82 [-3.20, -0.28] resolved |
| attaug − peaug | -2.46 [-4.05, -0.94] | 4/10 | not resolved | -3.29 [-5.15, -1.61] resolved |
| attkeep − attbal | -1.40 [-2.44, -0.27] | 4/10 | not resolved | -1.28 [-2.31, -0.24] resolved |
| pekeep − pebal | -0.22 [-1.09, +0.66] | 4/10 | not resolved | +0.46 [-0.41, +1.49] not resolved |
| attaug − attbal | -0.68 [-1.97, +0.67] | 7/10 | not resolved | +1.13 [-0.28, +2.71] not resolved |
| peaug − pebal | +2.65 [+1.19, +4.08] | 8/10 | RESOLVED better | +4.34 [+2.94, +5.76] resolved |


**Other metrics, per-seed means, differences against v2-PE (points × 100, 95% CI):**

| model − v2-PE | metric | difference | CI |
|---|---|---|---|
| attbal | TPR@1e-2 | -1.65 [-2.95, -0.67] | resolved |
| attbal | TPR@1e-3 | +2.91 [-2.20, +7.16] | not resolved |
| attbal | AUC | +0.68 [+0.57, +0.79] | resolved |
| pebal | TPR@1e-2 | -2.45 [-3.47, -1.59] | resolved |
| pebal | TPR@1e-3 | +0.86 [-4.32, +4.11] | not resolved |
| pebal | AUC | -0.91 [-1.03, -0.80] | resolved |
| attkeep | TPR@1e-2 | -1.92 [-3.38, -0.72] | resolved |
| attkeep | TPR@1e-3 | -0.63 [-6.95, +3.53] | not resolved |
| attkeep | AUC | +0.45 [+0.32, +0.57] | resolved |
| pekeep | TPR@1e-2 | -1.83 [-2.94, -1.13] | resolved |
| pekeep | TPR@1e-3 | -2.98 [-7.93, +1.82] | not resolved |
| pekeep | AUC | -0.88 [-1.02, -0.75] | resolved |
| attaug | TPR@1e-2 | -2.17 [-3.36, -1.09] | resolved |
| attaug | TPR@1e-3 | +2.18 [-3.16, +5.98] | not resolved |
| attaug | AUC | +0.17 [+0.05, +0.28] | resolved |
| peaug | TPR@1e-2 | +0.14 [-0.88, +1.22] | not resolved |
| peaug | TPR@1e-3 | +4.42 [+0.57, +7.41] | resolved |
| peaug | AUC | +0.46 [+0.38, +0.54] | resolved |

