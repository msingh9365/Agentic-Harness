**Table A. Clean April data for the chosen candidate (chosen on validation numbers only; evaluated once).** Per-seed mean ± std and 10-seed ensemble.

| model | n | pAUC@1e-2 | TPR@1e-2 | TPR@1e-3 | AUC | pAUC@1e-2 (ens.) | TPR@1e-2 (ens.) | TPR@1e-3 (ens.) | AUC (ens.) |
|---|---|---|---|---|---|---|---|---|---|
| v2-PE | 10 | 0.705 ± 0.031 | 0.811 ± 0.023 | 0.543 ± 0.063 | 0.9644 ± 0.0093 | 0.768 | 0.851 | 0.606 | 0.9705 |
| ATT+bal (existing, lr 2e-3, p 0.5, epoch 2) | 10 | 0.707 ± 0.017 | 0.795 ± 0.020 | 0.572 ± 0.061 | 0.9713 ± 0.0066 | 0.734 | 0.814 | 0.583 | 0.9780 |
| ATT+bal-tuned (lr 0.001, p 0.25, epoch 2) | 10 | 0.713 ± 0.012 | 0.795 ± 0.011 | 0.581 ± 0.045 | 0.9688 ± 0.0047 | 0.738 | 0.817 | 0.598 | 0.9738 |


**Claim rule (CI of the per-seed means excludes 0 and the same sign in ≥ 7 of 10 seeds); points × 100. Stratified bootstrap (EVAL_PROTOCOL.md) and, for pAUC@1e-2, the cluster bootstrap over duplicate groups.**

| difference | metric | per-seed means (CI) | seeds >0 / <0 | claim rule | 10-seed ensembles (CI) | cluster bootstrap CI (pAUC only) |
|---|---|---|---|---|---|---|
| tuned − v2_pe | pAUC@1e-2 | +0.84 [-0.78, +2.39] | 7/3 | not resolved | -3.02 [-4.54, -1.44] CI excludes 0 (descriptive) | [-4.00, +4.54] not resolved |
| tuned − v2_pe | TPR@1e-2 | -1.64 [-2.91, -0.60] | 3/7 | rule met, descriptive | -3.44 [-4.60, -1.98] CI excludes 0 (descriptive) | — |
| tuned − v2_pe | TPR@1e-3 | +3.84 [-2.43, +7.38] | 6/4 | rule not met, descriptive | -0.79 [-6.78, +5.30] CI contains 0 (descriptive) | — |
| tuned − v2_pe | AUC | +0.44 [+0.31, +0.55] | 7/3 | rule met, descriptive | +0.33 [+0.20, +0.45] CI excludes 0 (descriptive) | — |
| tuned − attbal | pAUC@1e-2 | +0.61 [-0.52, +1.74] | 7/3 | not resolved | +0.40 [-0.56, +1.42] CI contains 0 (descriptive) | [-1.10, +2.25] not resolved |
| tuned − attbal | TPR@1e-2 | +0.01 [-0.49, +0.62] | 3/7 | rule not met, descriptive | +0.31 [-0.47, +0.93] CI contains 0 (descriptive) | — |
| tuned − attbal | TPR@1e-3 | +0.92 [-4.83, +4.72] | 4/6 | rule not met, descriptive | +1.50 [-4.74, +5.99] CI contains 0 (descriptive) | — |
| tuned − attbal | AUC | -0.24 [-0.29, -0.20] | 3/7 | rule met, descriptive | -0.42 [-0.47, -0.37] CI excludes 0 (descriptive) | — |
| attbal − v2_pe | pAUC@1e-2 | +0.23 [-1.70, +2.09] | 4/6 | not resolved | -3.42 [-5.37, -1.55] CI excludes 0 (descriptive) | [-4.78, +4.29] not resolved |
| attbal − v2_pe | TPR@1e-2 | -1.65 [-2.95, -0.67] | 3/7 | rule met, descriptive | -3.75 [-4.73, -2.18] CI excludes 0 (descriptive) | — |
| attbal − v2_pe | TPR@1e-3 | +2.91 [-2.20, +7.16] | 6/4 | rule not met, descriptive | -2.29 [-7.12, +7.25] CI contains 0 (descriptive) | — |
| attbal − v2_pe | AUC | +0.68 [+0.57, +0.79] | 7/3 | rule met, descriptive | +0.75 [+0.62, +0.87] CI excludes 0 (descriptive) | — |


## Appendix: April clean numbers of every candidate (NOT USED FOR SELECTION; the choice was made on validation numbers)

Per-seed mean ± std over 10 seeds and the 10-seed ensemble pAUC@1e-2; the last two columns count the seeds in which the candidate is above v2-PE (same seed index).

| lr | p | epoch | pAUC@1e-2 | TPR@1e-2 | TPR@1e-3 | AUC | pAUC@1e-2 (ens.) | pAUC > v2-PE | TPR@1e-2 > v2-PE | note |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.001 | 0.25 | 1 | 0.705 ± 0.015 | 0.785 ± 0.012 | 0.585 ± 0.042 | 0.9718 ± 0.0039 | 0.733 | 4/10 | 1/10 |  |
| 0.001 | 0.25 | 2 | 0.713 ± 0.012 | 0.795 ± 0.011 | 0.581 ± 0.045 | 0.9688 ± 0.0047 | 0.738 | 7/10 | 3/10 | **chosen** |
| 0.001 | 0.25 | 3 | 0.698 ± 0.014 | 0.791 ± 0.028 | 0.550 ± 0.045 | 0.9661 ± 0.0032 | 0.730 | 4/10 | 2/10 |  |
| 0.001 | 0.25 | 4 | 0.692 ± 0.018 | 0.796 ± 0.010 | 0.543 ± 0.046 | 0.9646 ± 0.0037 | 0.725 | 2/10 | 3/10 |  |
| 0.001 | 0.5 | 1 | 0.706 ± 0.017 | 0.784 ± 0.012 | 0.594 ± 0.057 | 0.9741 ± 0.0034 | 0.724 | 2/10 | 0/10 |  |
| 0.001 | 0.5 | 2 | 0.703 ± 0.014 | 0.790 ± 0.008 | 0.557 ± 0.042 | 0.9720 ± 0.0038 | 0.729 | 4/10 | 2/10 |  |
| 0.001 | 0.5 | 3 | 0.688 ± 0.022 | 0.787 ± 0.009 | 0.540 ± 0.053 | 0.9678 ± 0.0043 | 0.720 | 4/10 | 1/10 |  |
| 0.001 | 0.5 | 4 | 0.681 ± 0.025 | 0.786 ± 0.014 | 0.546 ± 0.043 | 0.9658 ± 0.0050 | 0.712 | 2/10 | 2/10 |  |
| 0.002 | 0.25 | 1 | 0.712 ± 0.013 | 0.792 ± 0.013 | 0.606 ± 0.044 | 0.9690 ± 0.0074 | 0.741 | 6/10 | 2/10 |  |
| 0.002 | 0.25 | 2 | 0.711 ± 0.022 | 0.799 ± 0.014 | 0.557 ± 0.072 | 0.9680 ± 0.0049 | 0.741 | 5/10 | 4/10 |  |
| 0.002 | 0.25 | 3 | 0.695 ± 0.014 | 0.797 ± 0.017 | 0.529 ± 0.036 | 0.9656 ± 0.0046 | 0.732 | 4/10 | 4/10 |  |
| 0.002 | 0.25 | 4 | 0.689 ± 0.017 | 0.794 ± 0.010 | 0.519 ± 0.043 | 0.9649 ± 0.0038 | 0.732 | 3/10 | 3/10 |  |
| 0.002 | 0.5 | 1 | 0.709 ± 0.019 | 0.792 ± 0.013 | 0.590 ± 0.045 | 0.9718 ± 0.0044 | 0.739 | 6/10 | 3/10 |  |
| 0.002 | 0.5 | 2 | 0.707 ± 0.017 | 0.795 ± 0.020 | 0.572 ± 0.061 | 0.9713 ± 0.0066 | 0.734 | 4/10 | 3/10 | the existing ATT+bal |
| 0.002 | 0.5 | 3 | 0.692 ± 0.015 | 0.792 ± 0.011 | 0.520 ± 0.053 | 0.9658 ± 0.0063 | 0.720 | 3/10 | 1/10 |  |
| 0.002 | 0.5 | 4 | 0.687 ± 0.011 | 0.788 ± 0.022 | 0.508 ± 0.038 | 0.9658 ± 0.0085 | 0.722 | 2/10 | 2/10 |  |

