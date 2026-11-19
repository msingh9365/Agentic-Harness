# Results for review: ATT+bal, clean copies, malware-only padding, and attacks it was not trained on

Clean data, robustness and shortcut experiments for ATT+bal (data: the published April 2022 set, 9,399 malware and 8,003 benign reports; models trained on the 90% January slice; logit-ranked; 10 seeds unless stated).

**Status: the attack scoring of the review experiments (§5.11) and the whole tuning section (§5.12) are preliminary and are to be re-run on the author's own Kaggle account.**

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

Training of the keep models uses ALL clean reports of the 90% slice plus a padded copy of each report with probability 0.5 (new random edits per seed and epoch, random stream 7100), so an epoch holds about 101,500 reports (1.50x the 67,768 of the other runs) and takes about 1.5x as long. ATT+aug / PE+aug are the §5.10 procedure (padded reports replace the originals) applied to malware training reports only.

**Claim rule against v2-PE** (primary metric pAUC@1e-2; CI of the per-seed means excludes 0 and the same sign in ≥ 7 of 10 seeds; points × 100; ensembles: CI only):

| difference | per-seed means, pAUC@1e-2 | seeds > 0 | claim rule | 10-seed ensembles, pAUC@1e-2 |
|---|---|---|---|---|
| attbal − v2_pe | +0.23 [-1.70, +2.09] | 4/10 | not resolved | -3.42 [-5.37, -1.55] (CI excludes 0; descriptive) |
| pebal − v2_pe | -0.64 [-2.14, +0.76] | 3/10 | not resolved | -3.34 [-4.72, -2.02] (CI excludes 0; descriptive) |
| attkeep − v2_pe | -1.17 [-3.17, +0.96] | 3/10 | not resolved | -4.70 [-6.80, -2.60] (CI excludes 0; descriptive) |
| pekeep − v2_pe | -0.87 [-2.47, +0.69] | 4/10 | not resolved | -2.88 [-4.19, -1.46] (CI excludes 0; descriptive) |
| attaug − v2_pe | -0.45 [-2.34, +1.50] | 5/10 | not resolved | -2.30 [-4.19, -0.38] (CI excludes 0; descriptive) |
| peaug − v2_pe | +2.01 [+0.46, +3.49] | 6/10 | not resolved | +1.00 [-0.65, +2.55] (CI contains 0; descriptive) |
| attbal − pebal | +0.87 [-0.55, +2.33] | 6/10 | not resolved | -0.08 [-1.67, +1.54] (CI contains 0; descriptive) |
| attkeep − pekeep | -0.31 [-1.79, +1.16] | 6/10 | not resolved | -1.82 [-3.20, -0.28] (CI excludes 0; descriptive) |
| attaug − peaug | -2.46 [-4.05, -0.94] | 4/10 | not resolved | -3.29 [-5.15, -1.61] (CI excludes 0; descriptive) |
| attkeep − attbal | -1.40 [-2.44, -0.27] | 4/10 | not resolved | -1.28 [-2.31, -0.24] (CI excludes 0; descriptive) |
| pekeep − pebal | -0.22 [-1.09, +0.66] | 4/10 | not resolved | +0.46 [-0.41, +1.49] (CI contains 0; descriptive) |
| attaug − attbal | -0.68 [-1.97, +0.67] | 7/10 | not resolved | +1.13 [-0.28, +2.71] (CI contains 0; descriptive) |
| peaug − pebal | +2.65 [+1.19, +4.08] | 8/10 | RESOLVED better | +4.34 [+2.94, +5.76] (CI excludes 0; descriptive) |

**Other metrics, per-seed means, differences against v2-PE (points × 100, 95% CI):**

| model − v2-PE | metric | difference | CI |
|---|---|---|---|
| attbal | TPR@1e-2 | -1.65 [-2.95, -0.67] | CI excludes 0 (descriptive) |
| attbal | TPR@1e-3 | +2.91 [-2.20, +7.16] | CI contains 0 (descriptive) |
| attbal | AUC | +0.68 [+0.57, +0.79] | CI excludes 0 (descriptive) |
| pebal | TPR@1e-2 | -2.45 [-3.47, -1.59] | CI excludes 0 (descriptive) |
| pebal | TPR@1e-3 | +0.86 [-4.32, +4.11] | CI contains 0 (descriptive) |
| pebal | AUC | -0.91 [-1.03, -0.80] | CI excludes 0 (descriptive) |
| attkeep | TPR@1e-2 | -1.92 [-3.38, -0.72] | CI excludes 0 (descriptive) |
| attkeep | TPR@1e-3 | -0.63 [-6.95, +3.53] | CI contains 0 (descriptive) |
| attkeep | AUC | +0.45 [+0.32, +0.57] | CI excludes 0 (descriptive) |
| pekeep | TPR@1e-2 | -1.83 [-2.94, -1.13] | CI excludes 0 (descriptive) |
| pekeep | TPR@1e-3 | -2.98 [-7.93, +1.82] | CI contains 0 (descriptive) |
| pekeep | AUC | -0.88 [-1.02, -0.75] | CI excludes 0 (descriptive) |
| attaug | TPR@1e-2 | -2.17 [-3.36, -1.09] | CI excludes 0 (descriptive) |
| attaug | TPR@1e-3 | +2.18 [-3.16, +5.98] | CI contains 0 (descriptive) |
| attaug | AUC | +0.17 [+0.05, +0.28] | CI excludes 0 (descriptive) |
| peaug | TPR@1e-2 | +0.14 [-0.88, +1.22] | CI contains 0 (descriptive) |
| peaug | TPR@1e-3 | +4.42 [+0.57, +7.41] | CI excludes 0 (descriptive) |
| peaug | AUC | +0.46 [+0.38, +0.54] | CI excludes 0 (descriptive) |

Cluster-bootstrap sensitivity (duplicates resampled together), same comparisons:

**Cluster-bootstrap sensitivity (Table 1 primary metric pAUC@1e-2, per-seed means; duplicate groups resampled together, 1,000 resamples; points × 100).**

| difference | point | 95% CI | seeds > 0 | claim rule |
|---|---|---|---|---|
| attbal − v2_pe | +0.23 | [-4.78, +4.29] | 4/10 | not resolved |
| pebal − v2_pe | -0.64 | [-4.25, +2.45] | 3/10 | not resolved |
| attbal − pebal | +0.87 | [-1.54, +3.44] | 6/10 | not resolved |
| peaug − v2_pe | +2.01 | [-1.31, +5.63] | 6/10 | not resolved |
| peaug − pebal | +2.65 | [-0.70, +6.13] | 8/10 | not resolved |
| attaug − attbal | -0.68 | [-3.16, +1.68] | 7/10 | not resolved |
| attkeep − pekeep | -0.31 | [-3.33, +2.39] | 6/10 | not resolved |
| attkeep − attbal | -1.40 | [-3.41, +0.45] | 4/10 | not resolved |

**Duplicate-aware (cluster bootstrap) additions to Table 1.**

**Table 1, duplicate-aware (cluster bootstrap over hash_apis groups; 1,000 resamples). Difference of the per-seed means in points; the released checkpoint is one model. The claim rule applies to the primary metric only; the other rows are descriptive.**

| difference | metric | mean difference | 95% CI (cluster) | seeds > 0 | outcome |
|---|---|---|---|---|---|
| v2-PE − released checkpoint | pAUC@1e-2 (primary) | +4.59 | [-2.48, +13.20] | 9/10 | not resolved |
| v2-PE − released checkpoint | TPR@1e-2 | +6.13 | [+0.02, +12.81] | 10/10 | CI excludes 0 (descriptive) |
| v2-PE − released checkpoint | TPR@1e-3 | +2.44 | [-10.32, +19.68] | 7/10 | CI contains 0 (descriptive) |
| v2-PE − released checkpoint | AUC | +0.58 | [-0.14, +1.44] | 7/10 | CI contains 0 (descriptive) |
| ATT+bal − released checkpoint | pAUC@1e-2 (primary) | +4.82 | [-4.64, +15.28] | 10/10 | not resolved |
| ATT+bal − released checkpoint | TPR@1e-2 | +4.48 | [-2.88, +12.77] | 9/10 | CI contains 0 (descriptive) |
| ATT+bal − released checkpoint | TPR@1e-3 | +5.35 | [-11.75, +23.70] | 8/10 | CI contains 0 (descriptive) |
| ATT+bal − released checkpoint | AUC | +1.26 | [+0.19, +3.07] | 9/10 | CI excludes 0 (descriptive) |
| ATT+bal − v2-PE | pAUC@1e-2 (primary) | +0.23 | [-4.78, +4.29] | 4/10 | not resolved |
| ATT+bal − v2-PE | TPR@1e-2 | -1.65 | [-7.21, +3.23] | 3/10 | CI contains 0 (descriptive) |
| ATT+bal − v2-PE | TPR@1e-3 | +2.91 | [-5.47, +9.49] | 6/10 | CI contains 0 (descriptive) |
| ATT+bal − v2-PE | AUC | +0.68 | [-0.15, +2.13] | 7/10 | CI contains 0 (descriptive) |

## Table 2. Robustness to padding

Thresholds are fixed per model and seed at 1% and 0.1% FPR of its scores of the unedited April benign reports. Random padding = the procedure of REPORT 5.10 (calls drawn from the EVAL pool) applied to all April reports; surrogate padding = the calls of rank 1..k of a ranking made with a LightGBM bag-of-API-names model (fitted on the 90% slice) or with v2-PE seed 0; white-box = greedy choice among 200 random EVAL-pool calls per step against the model's own score.

**Table 2 (1% FPR threshold). Malware flagged / padded benign flagged, in % (mean over the 10 seeds; the released checkpoint is one model). Calls prepended or inserted into every April report (9,399 malware, 8,003 benign).**

| model | random 20 prepend | random 50 prepend | random 50 insert | LightGBM 20 prepend | LightGBM 50 prepend | LightGBM 50 insert | v2-PE 20 prepend | v2-PE 50 prepend | v2-PE 50 insert |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint | 12.0 / 12.5 | 16.3 / 13.3 | 35.6 / 4.0 | 2.8 / 0.5 | 3.2 / 0.1 | 28.8 / 2.0 | 28.6 / 66.1 | 100.0 / 100.0 | 65.6 / 59.3 |
| v2-PE | 22.5 / 1.2 | 8.3 / 1.1 | 41.4 / 0.7 | 10.2 / 0.1 | 3.3 / 0.0 | 21.7 / 0.1 | 2.7 / 0.0 | 3.1 / 0.0 | 7.7 / 0.0 |
| PE+bal | 75.7 / 2.4 | 64.3 / 2.4 | 71.4 / 1.5 | 71.1 / 0.8 | 10.0 / 0.0 | 58.8 / 0.5 | 6.0 / 0.0 | 2.3 / 0.0 | 26.8 / 0.2 |
| ATT+bal | 76.9 / 1.3 | 67.6 / 1.5 | 71.9 / 1.0 | 72.3 / 0.8 | 36.5 / 0.1 | 59.0 / 0.3 | 23.8 / 0.0 | 4.2 / 0.0 | 33.9 / 0.1 |
| ATT+bal-keep | 76.7 / 1.3 | 66.6 / 1.5 | 71.7 / 1.0 | 71.2 / 2.1 | 27.1 / 0.1 | 57.0 / 0.2 | 15.9 / 0.0 | 3.3 / 0.0 | 28.2 / 0.1 |
| PE+bal-keep | 76.3 / 2.5 | 65.1 / 2.9 | 71.8 / 1.7 | 70.7 / 1.0 | 6.6 / 0.0 | 56.6 / 0.4 | 4.2 / 0.0 | 2.3 / 0.0 | 24.1 / 0.1 |

**Table 2 (0.1% FPR threshold). Malware flagged / padded benign flagged, in % (mean over the 10 seeds; the released checkpoint is one model). Calls prepended or inserted into every April report (9,399 malware, 8,003 benign).**

| model | random 20 prepend | random 50 prepend | random 50 insert | LightGBM 20 prepend | LightGBM 50 prepend | LightGBM 50 insert | v2-PE 20 prepend | v2-PE 50 prepend | v2-PE 50 insert |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint | 2.1 / 1.1 | 4.1 / 0.8 | 14.7 / 0.1 | 1.2 / 0.0 | 2.0 / 0.0 | 12.8 / 0.0 | 7.8 / 0.0 | 15.0 / 1.9 | 7.0 / 0.3 |
| v2-PE | 5.5 / 0.0 | 1.5 / 0.0 | 13.6 / 0.0 | 1.6 / 0.0 | 0.4 / 0.0 | 6.2 / 0.0 | 0.3 / 0.0 | 0.4 / 0.0 | 1.8 / 0.0 |
| PE+bal | 47.8 / 0.1 | 21.1 / 0.1 | 42.6 / 0.1 | 37.2 / 0.1 | 0.5 / 0.0 | 30.6 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 6.2 / 0.0 |
| ATT+bal | 51.8 / 0.1 | 32.2 / 0.0 | 39.7 / 0.0 | 46.8 / 0.1 | 5.2 / 0.0 | 29.9 / 0.0 | 1.2 / 0.0 | 1.1 / 0.0 | 12.5 / 0.0 |
| ATT+bal-keep | 44.6 / 0.1 | 26.1 / 0.0 | 33.6 / 0.0 | 37.6 / 0.1 | 2.3 / 0.0 | 25.0 / 0.0 | 0.9 / 0.0 | 0.8 / 0.0 | 8.1 / 0.0 |
| PE+bal-keep | 44.2 / 0.1 | 19.1 / 0.0 | 37.6 / 0.0 | 28.9 / 0.1 | 0.1 / 0.0 | 24.7 / 0.0 | 0.1 / 0.0 | 0.1 / 0.0 | 4.1 / 0.0 |

**Table 2 (white-box greedy attack, 500 April malware, seeds 0-2). Share still flagged at the 1% / 0.1% FPR thresholds after k prepended calls, in %.**

| model | seeds | k = 0 | k = 5 | k = 10 | k = 20 |
|---|---|---|---|---|---|
| released checkpoint | 1 | 70.4 / 49.0 | 3.2 / 0.0 | 1.4 / 0.0 | 1.2 / 0.0 |
| v2-PE | 3 | 75.6 / 47.5 | 9.0 / 0.7 | 5.1 / 0.6 | 2.2 / 0.2 |
| PE+bal | 3 | 76.9 / 51.5 | 62.8 / 26.9 | 57.8 / 18.8 | 39.6 / 3.5 |
| ATT+bal | 3 | 77.7 / 58.3 | 65.5 / 34.5 | 62.5 / 31.7 | 53.3 / 14.6 |
| ATT+bal-keep | 3 | 74.8 / 50.8 | 63.8 / 27.3 | 61.6 / 24.5 | 44.7 / 7.5 |
| PE+bal-keep | 3 | 76.1 / 41.8 | 62.8 / 17.1 | 56.1 / 11.0 | 41.1 / 2.5 |

White-box, ATT − PE, seed-paired:

**White-box comparisons (points; seeds 0-2 paired; CI = bootstrap over the 500 reports).**

| comparison | threshold | k | mean difference | 95% CI | seeds > 0 |
|---|---|---|---|---|---|
| ATT+bal − PE+bal | 1% FPR | 5 | +2.7 | [+1.1, +4.4] | 2/3 |
| ATT+bal − PE+bal | 1% FPR | 10 | +4.7 | [+3.3, +6.2] | 2/3 |
| ATT+bal − PE+bal | 1% FPR | 20 | +13.7 | [+11.5, +16.1] | 3/3 |
| ATT+bal − PE+bal | 0.1% FPR | 5 | +7.5 | [+5.5, +9.7] | 3/3 |
| ATT+bal − PE+bal | 0.1% FPR | 10 | +12.9 | [+10.7, +15.4] | 3/3 |
| ATT+bal − PE+bal | 0.1% FPR | 20 | +11.1 | [+8.9, +13.3] | 3/3 |
| ATT+bal-keep − PE+bal-keep | 1% FPR | 5 | +1.0 | [-0.4, +2.3] | 1/3 |
| ATT+bal-keep − PE+bal-keep | 1% FPR | 10 | +5.5 | [+3.9, +7.0] | 3/3 |
| ATT+bal-keep − PE+bal-keep | 1% FPR | 20 | +3.6 | [+1.5, +5.7] | 2/3 |
| ATT+bal-keep − PE+bal-keep | 0.1% FPR | 5 | +10.1 | [+7.9, +12.4] | 3/3 |
| ATT+bal-keep − PE+bal-keep | 0.1% FPR | 10 | +13.5 | [+11.0, +15.8] | 3/3 |
| ATT+bal-keep − PE+bal-keep | 0.1% FPR | 20 | +5.0 | [+3.5, +6.7] | 3/3 |

ATT+bal against PE+bal, counts of tests in which the CI excludes 0 with at least 7 of 10 seeds on the same side (descriptive):

**Count of tests (random padding; edit sets × the two thresholds) in which the first model is higher / lower than the second by the descriptive rule (CI excludes 0 and ≥ 7 of 10 seeds with the same sign). In brackets: the same under the cluster bootstrap over duplicate groups. For the padded-benign FPR a higher value is worse.**

| comparison | rate | tests | first higher (cluster) | first lower (cluster) | neither |
|---|---|---|---|---|---|
| ATT+bal − PE+bal | malware TPR | 12 | 6 (4) | 0 (0) | 6 |
| ATT+bal − PE+bal | malware TPR, fit subset | 12 | 2 (1) | 1 (1) | 9 |
| ATT+bal − PE+bal | padded-benign FPR | 12 | 0 (0) | 7 (7) | 5 |
| ATT+bal-keep − PE+bal-keep | malware TPR | 12 | 1 (1) | 1 (0) | 10 |
| ATT+bal-keep − PE+bal-keep | malware TPR, fit subset | 12 | 8 (6) | 0 (0) | 4 |
| ATT+bal-keep − PE+bal-keep | padded-benign FPR | 12 | 0 (0) | 2 (2) | 10 |

**Count of tests (surrogate padding; edit sets × the two thresholds) in which the first model is higher / lower than the second by the descriptive rule (CI excludes 0 and ≥ 7 of 10 seeds with the same sign). In brackets: the same under the cluster bootstrap over duplicate groups. For the padded-benign FPR a higher value is worse.**

| comparison | rate | tests | first higher (cluster) | first lower (cluster) | neither |
|---|---|---|---|---|---|
| ATT+bal − PE+bal | malware TPR | 24 | 18 (14) | 0 (0) | 6 |
| ATT+bal − PE+bal | malware TPR, fit subset | 20 | 2 (1) | 7 (2) | 11 |
| ATT+bal − PE+bal | padded-benign FPR | 24 | 3 (2) | 1 (0) | 20 |
| ATT+bal-keep − PE+bal-keep | malware TPR | 24 | 10 (9) | 1 (0) | 13 |
| ATT+bal-keep − PE+bal-keep | malware TPR, fit subset | 20 | 5 (2) | 1 (0) | 14 |
| ATT+bal-keep − PE+bal-keep | padded-benign FPR | 24 | 0 (0) | 2 (1) | 22 |

**Duplicate-aware additions to Table 2.**

**Duplicate-aware counts for Table 2: tests (edit sets × two thresholds) in which the first model is higher / lower by the descriptive rule (CI excludes 0 and ≥ 7 of 10 seeds on the same side), stratified bootstrap and, in brackets, the cluster bootstrap over hash_apis groups. For the padded-benign FPR higher is worse. All rows: `results/review/audit_cluster.md`.**

| padding | comparison | rate | tests | first higher (cluster) | first lower (cluster) | neither |
|---|---|---|---|---|---|---|
| random padding | v2-PE − released checkpoint | malware TPR | 12 | 6 (4) | 2 (2) | 4 |
| random padding | v2-PE − released checkpoint | padded-benign FPR | 12 | 0 (0) | 8 (8) | 4 |
| random padding | ATT+bal − released checkpoint | malware TPR | 12 | 12 (12) | 0 (0) | 0 |
| random padding | ATT+bal − released checkpoint | padded-benign FPR | 12 | 0 (0) | 8 (8) | 4 |
| random padding | ATT+bal − v2-PE | malware TPR | 12 | 12 (12) | 0 (0) | 0 |
| random padding | ATT+bal − v2-PE | padded-benign FPR | 12 | 10 (8) | 0 (0) | 2 |
| surrogate padding | v2-PE − released checkpoint | malware TPR | 24 | 3 (2) | 16 (13) | 5 |
| surrogate padding | v2-PE − released checkpoint | padded-benign FPR | 24 | 0 (0) | 14 (12) | 10 |
| surrogate padding | ATT+bal − released checkpoint | malware TPR | 24 | 19 (16) | 5 (4) | 0 |
| surrogate padding | ATT+bal − released checkpoint | padded-benign FPR | 24 | 6 (5) | 11 (11) | 7 |
| surrogate padding | ATT+bal − v2-PE | malware TPR | 24 | 23 (23) | 0 (0) | 1 |
| surrogate padding | ATT+bal − v2-PE | padded-benign FPR | 24 | 16 (16) | 0 (0) | 8 |

**White-box greedy, 500 reports, seeds 0-2 (the released checkpoint: its one run against every seed); share still flagged after k prepended calls; cluster bootstrap over the hash_apis groups of the 500 reports. Descriptive.**

| difference | threshold | k | mean difference (points) | 95% CI (cluster) | seeds > 0 |
|---|---|---|---|---|---|
| v2-PE − released checkpoint | 1% FPR | 5 | +5.8 | [+1.8, +10.3] | 3/3 |
| v2-PE − released checkpoint | 1% FPR | 10 | +3.7 | [+1.4, +6.5] | 3/3 |
| v2-PE − released checkpoint | 1% FPR | 20 | +1.0 | [-0.4, +2.6] | 2/3 |
| v2-PE − released checkpoint | 0.1% FPR | 5 | +0.7 | [+0.1, +1.6] | 3/3 |
| v2-PE − released checkpoint | 0.1% FPR | 10 | +0.6 | [+0.1, +1.3] | 3/3 |
| v2-PE − released checkpoint | 0.1% FPR | 20 | +0.2 | [+0.0, +0.6] | 2/3 |
| ATT+bal − released checkpoint | 1% FPR | 5 | +62.3 | [+47.4, +72.9] | 3/3 |
| ATT+bal − released checkpoint | 1% FPR | 10 | +61.1 | [+45.8, +71.7] | 3/3 |
| ATT+bal − released checkpoint | 1% FPR | 20 | +52.1 | [+37.0, +63.6] | 3/3 |
| ATT+bal − released checkpoint | 0.1% FPR | 5 | +34.5 | [+22.1, +47.4] | 3/3 |
| ATT+bal − released checkpoint | 0.1% FPR | 10 | +31.7 | [+19.8, +45.0] | 3/3 |
| ATT+bal − released checkpoint | 0.1% FPR | 20 | +14.6 | [+8.2, +22.1] | 3/3 |
| ATT+bal − v2-PE | 1% FPR | 5 | +56.5 | [+43.8, +67.6] | 3/3 |
| ATT+bal − v2-PE | 1% FPR | 10 | +57.3 | [+43.7, +69.1] | 3/3 |
| ATT+bal − v2-PE | 1% FPR | 20 | +51.1 | [+36.8, +62.8] | 3/3 |
| ATT+bal − v2-PE | 0.1% FPR | 5 | +33.7 | [+21.6, +46.1] | 3/3 |
| ATT+bal − v2-PE | 0.1% FPR | 10 | +31.1 | [+19.4, +43.2] | 3/3 |
| ATT+bal − v2-PE | 0.1% FPR | 20 | +14.4 | [+8.2, +21.4] | 3/3 |

Full tables (every model, every edit set, the malware TPR on the subset whose whole edited report fits in 512 tokens, the ATT − PE differences with the per-seed spread, seeds above/below 0 and both bootstrap intervals): `results/review/attack_tables.md`; the numbers: `results/review/attack_aggregates.json`.

![Detection against the number of calls prepended](results/review/fig_detection_vs_k.png)

## Table 3. The label shortcut

**Table 3. The label shortcut: padding applied to malware training reports only (aug) against padding of all reports (bal). Clean TPR@1% FPR, then padded malware / padded benign flagged at the 1% threshold (random calls, prepend), and the probe AUC for "padding present" (pooled vector, 64-d hidden vector).**

| model | clean TPR@1% (April) | k=20 prepend: malware / benign flagged | k=50 prepend: malware / benign flagged | probe AUC, pooled | probe AUC, hidden |
|---|---|---|---|---|---|
| v2-PE | 81.1 | 22.5 / 1.2 | 8.3 / 1.1 | 0.969 | 0.756 |
| PE+bal | 78.7 | 75.7 / 2.4 | 64.3 / 2.4 | 0.971 | 0.750 |
| PE+aug | 81.2 | 99.3 / 94.0 | 99.9 / 99.7 | 0.975 | 0.826 |
| ATT+bal | 79.5 | 76.9 / 1.3 | 67.6 / 1.5 | 0.706 | 0.657 |
| ATT+aug | 78.9 | 94.4 / 62.1 | 98.5 / 95.3 | 0.813 | 0.769 |

**Table 3b. Shortcut probe: AUC of a logistic regression predicting "padding present" on April reports (padded with probability 0.5), mean ± std over the seeds.**

| model | n seeds | AUC, pooled vector | AUC, 64-d hidden vector | shuffled-label control |
|---|---|---|---|---|
| v2-PE | 10 | 0.9693 ± 0.0011 | 0.7565 ± 0.0251 | 0.498 |
| PE+bal | 10 | 0.9707 ± 0.0020 | 0.7505 ± 0.0194 | 0.496 |
| ATT+bal | 10 | 0.7063 ± 0.0251 | 0.6574 ± 0.0219 | 0.500 |
| PE+aug | 10 | 0.9753 ± 0.0021 | 0.8262 ± 0.0185 | 0.496 |
| ATT+aug | 10 | 0.8130 ± 0.0285 | 0.7694 ± 0.0340 | 0.504 |

## Nebula paper vs ours

**Nebula paper vs ours. Different data (the paper's test set is not the published one; §6.1 of the report); for reference only.**

| model | TPR@1e-3 | AUC | F1 (threshold 0.5) |
|---|---|---|---|
| Nebula paper (Table 7, BPE, 2,116 batches, their test set) | 0.5213 | 0.9657 | 0.9136 |
| ours: released checkpoint (published April set) | 0.518 | 0.9586 | 0.8854 |
| ours: v2-PE (published April set) | 0.543 | 0.9644 | 0.9146 |
| ours: ATT+bal (published April set) | 0.572 | 0.9713 | 0.9134 |
| ours: PE+bal (published April set) | 0.551 | 0.9553 | 0.8984 |
| ours: PE+aug (published April set) | 0.587 | 0.9690 | 0.9114 |

## ATT+bal tuned under EVAL_PROTOCOL §4 (REPORT 5.12)

**Status: preliminary. The training and the scoring of this section are to be re-run on the author's own Kaggle account.**

Grid (written before training, NOTES 16): lr {1e-3, 2e-3} x padding probability {0.25, 0.5} x epochs 1-4, 10 seeds each; chosen on validation numbers only: **lr 1e-3, p 0.25, epoch 2** (mean validation pAUC@1e-2 0.9596 against 0.9553 for the existing ATT+bal). Evaluated once on April:

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

**Plainly.**
1. **The gap to v2-PE at 1% FPR did not close.** The chosen candidate (lr 1e-3, padding probability 0.25, epoch 2) has April TPR@1e-2 0.795 ± 0.011 against 0.811 ± 0.023 for v2-PE: -1.64 points, CI [-2.91, -0.60] (descriptive: the CI excludes 0 and the tuned model is above v2-PE in only 3 of 10 seeds). The existing ATT+bal had -1.65. Tuning changed nothing there (tuned − existing: +0.01 points, not resolved). No candidate of the grid reaches v2-PE's TPR@1e-2: the highest mean in the appendix is 0.799 (not used for selection).
2. **On the primary metric nothing is resolved either.** Tuned − v2-PE in pAUC@1e-2: +0.84 points per-seed means (CI [-0.78, +2.39], above in 7 of 10 seeds: rule not met; cluster bootstrap CI [-4.00, +4.54]); as 10-seed ensembles -3.02 (the CI excludes 0; descriptive). Tuned − existing ATT+bal: +0.61 (CI [-0.52, +1.74], 7 of 10 seeds, claim rule not met). The validation gain that led to the choice (+0.43 points) is of the size of its own standard error (0.15 to 0.23 points); AUC is 0.24 points lower than the existing model (descriptive: the CI excludes 0).
3. **What it cost in robustness: a little everywhere, clearly under the strongest attacks.** Against the existing ATT+bal the tuned model is lower after 20 white-box calls (46.5 against 53.3% flagged at 1% FPR: -6.9 points, 0 of 3 seeds above; 11.6 against 14.6% at 0.1% FPR), under LightGBM-chosen k = 50 prepend (31.5 against 36.5%) and under v2-PE-chosen k = 20 prepend (21.4 against 23.8%); under random padding the two are within about 2 points (66.0 against 67.6% at k = 50 prepend). It stays far above PE+bal (white-box after 20 calls 39.6%) and v2-PE (2.2%). Validation had already pointed this way (R 0.949 against 0.959).
4. **Reading.** Training with fewer padded reports (p = 0.25) and the lower learning rate buys back nothing at 1% FPR and gives up some robustness: the 1-point gap to v2-PE at 1% FPR is not a matter of these two settings in this grid. Not tested: other recipe changes (a padding schedule, k distribution, other pooling).

**Table 2 (1% FPR threshold). Malware flagged / padded benign flagged, in % (mean over the 10 seeds). Every April report is edited.**

| model | random 20 prepend | random 50 prepend | random 50 insert | LightGBM 20 prepend | LightGBM 50 prepend | LightGBM 50 insert | v2-PE 20 prepend | v2-PE 50 prepend | v2-PE 50 insert |
|---|---|---|---|---|---|---|---|---|---|
| v2-PE | 22.5 / 1.2 | 8.3 / 1.1 | 41.4 / 0.7 | 10.2 / 0.1 | 3.3 / 0.0 | 21.7 / 0.1 | 2.7 / 0.0 | 3.1 / 0.0 | 7.7 / 0.0 |
| PE+bal | 75.7 / 2.4 | 64.3 / 2.4 | 71.4 / 1.5 | 71.1 / 0.8 | 10.0 / 0.0 | 58.8 / 0.5 | 6.0 / 0.0 | 2.3 / 0.0 | 26.8 / 0.2 |
| ATT+bal (existing) | 76.9 / 1.3 | 67.6 / 1.5 | 71.9 / 1.0 | 72.3 / 0.8 | 36.5 / 0.1 | 59.0 / 0.3 | 23.8 / 0.0 | 4.2 / 0.0 | 33.9 / 0.1 |
| ATT+bal-tuned | 76.8 / 1.8 | 66.0 / 2.1 | 71.3 / 1.2 | 68.9 / 0.9 | 31.5 / 0.1 | 57.8 / 0.3 | 21.4 / 0.0 | 4.5 / 0.0 | 33.3 / 0.1 |

**Table 2 (white-box greedy attack, 500 April malware, seeds 0-2). Share still flagged at the 1% / 0.1% FPR thresholds after k prepended calls, in %.**

| model | seeds | k = 0 | k = 5 | k = 10 | k = 20 |
|---|---|---|---|---|---|
| v2-PE | 3 | 75.6 / 47.5 | 9.0 / 0.7 | 5.1 / 0.6 | 2.2 / 0.2 |
| PE+bal | 3 | 76.9 / 51.5 | 62.8 / 26.9 | 57.8 / 18.8 | 39.6 / 3.5 |
| ATT+bal (existing) | 3 | 77.7 / 58.3 | 65.5 / 34.5 | 62.5 / 31.7 | 53.3 / 14.6 |
| ATT+bal-tuned | 3 | 77.1 / 54.1 | 63.8 / 31.8 | 60.3 / 25.9 | 46.5 / 11.6 |

![Detection against the number of calls prepended, with the tuned candidate](results/tune/fig_detection_vs_k.png)

The validation table of all 16 candidates, the April numbers of every candidate (appendix, not used for selection), the 0.1% FPR table, the white-box comparison and the counts are in REPORT 5.12 and `results/tune/`.



## Audit additions (statistics and CPU checks; no training)

**Validation overlap.** Validation slice: 7,530 reports; **94.2% share their API sequence (hash_apis) with the 90% training slice** (7,097 seen, 433 unseen: 99 malware, 334 benign). April: 36.4%. Validation tables recomputed on the unseen part only are in REPRODUCTION_REPORT.md §5.13: the models rank differently there (v2-PE pAUC@1e-2 0.962 on the whole slice, 0.975 on the seen part, 0.673 on the 433 unseen reports), and the rule of §5.12 applied to the unseen part would pick (lr 1e-3, p 0.5, epoch 3) instead of (lr 1e-3, p 0.25, epoch 2). Plan for the redo on a group-split slice: NOTES.md section 17 (not run).

**Tokenizer.** Unknown pieces (mostly the letter "j") get id 0, which is also the padding id: 0.17% of the tokens of April, 21.7% of April reports have at least one (REPORT 5.9a).

**Further robustness tests (CPU).** Rare-API-name, block and copied-call padding, rotation of the call list, argument injection and the deduplication defence on v2-PE (definitions and checks in REPORT 5.13 c):

**Table X (1% FPR threshold). Further edits: malware flagged / padded benign flagged, in % (mean over the seeds scored; every April report is edited). Unedited malware flagged / benign flagged: released checkpoint: 75.0 / 1.00; v2-PE: 81.1 / 0.99; PE+bal: 78.7 / 1.00; ATT+bal: 79.5 / 0.99; v2-PE + test-time deduplication: 81.1 / 0.99.**

| model | seeds | rare 20 prepend | rare 50 insert | block 50 prepend | block 50 insert | copy 50 prepend | copy 50 insert | rot 50 | inj 50 |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint | 1 | 17.6 / 19.4 | 28.9 / 9.8 | 23.9 / 19.8 | 61.9 / 3.8 | 37.4 / 19.3 | 49.0 / 2.7 | 39.5 / 32.5 | 34.4 / 3.2 |
| v2-PE | 10 | 11.5 / 1.5 | 25.0 / 0.9 | 21.3 / 4.4 | 65.4 / 1.1 | 57.2 / 4.2 | 67.7 / 1.8 | 54.3 / 5.2 | 46.9 / 0.8 |
| PE+bal | 10 | 70.0 / 3.8 | 55.1 / 1.7 | 68.2 / 4.1 | 72.0 / 2.0 | 80.5 / 4.5 | 79.7 / 2.6 | 62.7 / 14.6 | 75.0 / 1.4 |
| ATT+bal | 10 | 70.7 / 1.4 | 52.7 / 1.1 | 72.7 / 3.1 | 72.8 / 2.6 | 79.0 / 3.2 | 80.0 / 1.8 | 62.0 / 10.0 | 76.0 / 1.0 |
| v2-PE + test-time deduplication | 10 | 11.3 / 1.4 | 24.6 / 0.8 | 21.2 / 4.2 | 65.2 / 1.0 | 57.2 / 4.0 | 67.5 / 1.7 | 53.8 / 5.0 | 46.4 / 0.8 |

**Table X (0.1% FPR threshold). Further edits: malware flagged / padded benign flagged, in % (mean over the seeds scored; every April report is edited). Unedited malware flagged / benign flagged: released checkpoint: 51.8 / 0.10; v2-PE: 54.3 / 0.10; PE+bal: 55.1 / 0.10; ATT+bal: 57.2 / 0.10; v2-PE + test-time deduplication: 54.4 / 0.10.**

| model | seeds | rare 20 prepend | rare 50 insert | block 50 prepend | block 50 insert | copy 50 prepend | copy 50 insert | rot 50 | inj 50 |
|---|---|---|---|---|---|---|---|---|---|
| released checkpoint | 1 | 3.5 / 1.1 | 9.5 / 0.2 | 5.4 / 2.9 | 37.3 / 0.3 | 13.1 / 2.0 | 22.9 / 0.1 | 13.4 / 3.6 | 15.4 / 0.0 |
| v2-PE | 10 | 1.8 / 0.0 | 6.6 / 0.0 | 5.2 / 0.1 | 36.6 / 0.0 | 27.6 / 0.4 | 36.7 / 0.2 | 18.8 / 0.3 | 13.4 / 0.0 |
| PE+bal | 10 | 30.6 / 0.2 | 24.0 / 0.0 | 32.8 / 0.1 | 44.7 / 0.1 | 65.0 / 1.1 | 61.0 / 0.5 | 32.6 / 0.3 | 46.3 / 0.1 |
| ATT+bal | 10 | 40.3 / 0.1 | 25.4 / 0.0 | 41.1 / 0.1 | 42.8 / 0.1 | 61.2 / 0.2 | 55.7 / 0.2 | 36.1 / 0.2 | 48.3 / 0.1 |
| v2-PE + test-time deduplication | 10 | 1.9 / 0.0 | 6.6 / 0.0 | 5.3 / 0.1 | 36.7 / 0.0 | 28.2 / 0.3 | 37.0 / 0.2 | 19.0 / 0.3 | 13.5 / 0.0 |

**Further edits: counts of tests (23 edit sets × two thresholds) in which the first model is higher / lower by the descriptive rule (CI excludes 0 and ≥ 7 of 10 paired seeds on the same side; in brackets the same under the cluster bootstrap). For the padded-benign FPR higher is worse.**

| comparison | rate | tests | first higher (cluster) | first lower (cluster) | neither |
|---|---|---|---|---|---|
| ATT+bal − PE+bal | malware TPR | 46 | 19 (10) | 4 (2) | 23 |
| ATT+bal − PE+bal | padded-benign FPR | 46 | 0 (0) | 21 (20) | 25 |
| ATT+bal − v2-PE | malware TPR | 46 | 45 (41) | 0 (0) | 1 |
| ATT+bal − v2-PE | padded-benign FPR | 46 | 14 (7) | 5 (4) | 27 |
| PE+bal − v2-PE | malware TPR | 46 | 45 (42) | 0 (0) | 1 |
| PE+bal − v2-PE | padded-benign FPR | 46 | 32 (29) | 1 (0) | 13 |
| v2-PE + test-time deduplication − v2-PE | malware TPR | 46 | 9 (6) | 6 (5) | 31 |
| v2-PE + test-time deduplication − v2-PE | padded-benign FPR | 46 | 0 (0) | 8 (8) | 38 |

**Reading of Table X (descriptive; none of these comparisons is a pre-registered claim; 10 seeds for v2-PE, PE+bal, ATT+bal and the deduplication family, one model for the released checkpoint).**
1. **Models trained with balanced padding hold up against every added-call edit; v2-PE and the released checkpoint do not.** At k = 50 and the 1% FPR threshold PE+bal and ATT+bal flag 53 to 80% of the malware, v2-PE 11 to 25% for rare-name prepend, rare-name insert and block prepend and 57 to 68% for copied calls and block insert; the released checkpoint 18 to 29% (rare, block prepend), 37 to 62% otherwise. ATT+bal is higher than PE+bal in the malware TPR in 19 of 46 tests (10 also under the cluster bootstrap) and lower in 4 (2), mostly rare-name and block prepend (rare-name prepend k = 20 at 0.1% FPR: 40.3 against 30.6%), and ATT+bal flags fewer padded benign reports in 21 tests (20 under the cluster bootstrap).
2. **Rotation of the call list is the hardest edit for every model.** With the second half of the report first (rot 50) the malware flagged at 1% FPR falls from 81.1 to 54.3% (v2-PE), from 78.7 and 79.5 to 62.7 and 62.0% (PE+bal, ATT+bal; unedited 1% TPRs 0.787 and 0.795), and the share of benign reports flagged rises from 1% to 5.2% (v2-PE), 14.6% (PE+bal) and 10.0% (ATT+bal): the training with balanced padding does not cover this edit and costs false alarms on it.
3. **Argument injection into the first 50 calls** (arguments of a random EVAL-pool call appended): v2-PE 46.9% (from 81.1), released checkpoint 34.4%, PE+bal 75.0%, ATT+bal 76.0%, padded-benign flagged 0.8 to 1.4%.
4. **The test-time deduplication defence on v2-PE changes almost nothing**: malware TPR differs by at most about 1 point in 31 of 46 tests (higher in 9, lower in 6 by the descriptive rule), the padded-benign FPR is slightly lower in 8 tests; the padding of these edits rarely produces consecutive identical calls, and the dedup of the unedited reports does not change the clean scores much. It is not a defence against the edits tested.
5. **The balanced-padding models flag more padded benign reports than v2-PE** (higher in 32 of 46 tests for PE+bal, in 14 of 46 for ATT+bal; in absolute terms 1 to 5% at the 1% threshold for most edits, 10 to 15% for rotation): the robustness is bought with a higher false-alarm rate on edited benign reports.
**Definitions and limits.** The edits are mine (EVAL-pool calls; rare-name pool = 372 calls of 228 names with training frequency at most 2; block = consecutive calls of one pool report; rotation of the call list as a stand-in for "rotation of the 512 window"; injection = appended arguments of a random pool call). The builders were checked against full re-tokenisation. Thresholds are fixed on the unedited April benign scores of each model (the deduplicated unedited reports for the deduplication family). The non-injection sets were scored on GPU from the call store and the injection sets on CPU; both paths gave identical scores in a test (max difference 0.0). Preliminary: to be re-run on the author's own Kaggle account.

**How often April was used.** April 2022 (17,402 reports, 2,509 distinct API sequences) is the only test set and every experiment of this report scored it: A, B, B2, B3, C, D, E, F (its recipe grid stored the April numbers of every recipe and epoch but was selected on validation numbers), the pAUC re-scoring (§5.8), v2-PE (§5.9), ATT and ATT+bal (§5.10), §5.11 and §5.12: 13 scoring rounds on the same reports. Within an experiment April was used once per model family (EVAL_PROTOCOL.md §4), and to my knowledge no hyper-parameter was selected on April numbers; from F on, settings were chosen on the validation slice. But the sequence of questions was shaped by April results of the previous round (v2-PE after the gap analysis, ATT+bal after v2-PE, keep/aug and the attacks after ATT+bal, the tuning after the attacks), so April is not an untouched holdout for the thesis claims, and the confidence intervals do not account for the repeated use. In §5.12 the April logits of all 16 candidates were stored and opened only after the choice was written down.

## What is shown and what is not

1. **Shown: balanced padding buys robustness, not clean accuracy.** ATT+bal, PE+bal and both keep models still flag 64 to 77% of the malware when 20 to 50 random benign calls are prepended or inserted, where v2-PE falls to 8 to 22% (prepend) and the released checkpoint to 12 to 16%. On clean April data no model beats v2-PE on pAUC@1e-2 under the claim rule (ATT+bal +0.23 points, CI [-1.70, +2.09], positive in 4 of 10 seeds); as 10-seed ensembles ATT+bal is 3.4 points lower (the CI excludes 0; descriptive).
2. **Shown: attention pooling adds robustness against large amounts of prepended padding, not elsewhere.** ATT+bal beats PE+bal where the padding is chosen against the model or is long (LightGBM-chosen k = 50 prepend: 36.5 against 10.0% flagged at 1% FPR; white-box after 20 calls: 53.3 against 39.6% at 1% FPR and 14.6 against 3.5% at 0.1%); in 18 of 24 surrogate tests the CI excludes 0 with at least 7 of 10 seeds in its favour (14 also under a bootstrap that resamples duplicate reports together; descriptive) and in none against it. For random and LightGBM-chosen inserted calls the two are equal (differences within 0.5 points); against calls chosen with v2-PE, ATT+bal is higher by 1.5 to 7 points. On the 0 to 30% of malware reports whose whole edited text still fits into 512 tokens the picture is mixed (2 tests for ATT+bal, 7 against). The advantage is therefore about what is pushed out of the 512-token window, and it is smaller for the keep models.
3. **Shown: keeping the clean copies did not help.** The keep models are not better on clean data (pAUC@1e-2 -1.17 and -0.87 points against v2-PE; ATT+bal-keep -1.40 against ATT+bal: the per-seed rule is not met, the 10-seed ensembles differ by -1.28 points, the CI excludes 0; descriptive) and are less robust than the replace versions under the strongest attacks (LightGBM-chosen k = 50 prepend 27.1 against 36.5%; white-box after 20 calls at 0.1% FPR: 7.5 against 14.6%).
4. **Shown: padding malware only teaches the shortcut "padding means malware", and the clean metrics do not show it.** PE+aug has the highest pAUC@1e-2 and TPR@1e-3 of all models (+2.0 points against v2-PE, rule not met) yet flags 99.9% of the malware and 99.7% of the benign reports at k = 50 (ATT+aug 98.5 and 95.3%). A linear probe reads "padding present" from the pooled vector of every flatten model at AUC 0.97 (also from v2-PE, which never saw padding), so the probe shows what can be read, not what the model uses; the attention-pooled vector of ATT+bal is much harder to read (0.71).
5. **Not shown: that ATT+bal is better than v2-PE on clean data; any robustness against an attacker who knows the defence, who edits something other than adding benign API calls, or who is limited to a different budget; any result on another month.** The white-box attack has 3 seeds and 500 reports. The intervals cover test-set sampling only and the seed-to-seed spread is large (std of pAUC@1e-2 between seeds 1.7 to 6.4 points). April holds 2,509 distinct API sequences in 17,402 reports; with whole duplicate groups resampled together no per-seed-mean comparison between the trained models of Table 1 meets the claim rule, including PE+aug against PE+bal.

## Limits and how this was done

- **Statistics.** The stratified bootstrap of EVAL_PROTOCOL.md (reports independent, 1,000 resamples, numpy seed 0) covers test-set sampling only; the claim rule adds the 7-of-10 seed count. The cluster-bootstrap columns resample the 2,509 duplicate groups (hash of the API sequence) and are wider; a result that survives both is the safe one.
- **The random-padding test is in distribution for the models trained with balanced padding** (same procedure, different pool: the training pool and the EVAL pool are disjoint). The surrogate-chosen padding and the white-box greedy attack are the attacks they were not trained on; they use the same kind of edit (benign API calls added or prepended).
- **The 512-token window.** Only 36.6% of April reports (30.4% of the malware, 43.9% of the benign reports) fit into 512 tokens unedited (mean length 1,056 tokens); prepending or inserting calls pushes original content out of the window, so much of what the attacks measure is what happens when the window fills with padding. The "fits in 512" columns restrict to reports whose whole edited text fits; at v2-PE-surrogate k = 50 no report fits (n/a). The attention-pooled models read the same 512 tokens.
- **Released checkpoint.** It has its own tokenizer; its attacks use a second call store made with it (checked the same way). At v2-PE-surrogate k = 50 it flags every report (malware 100%, benign 100%), which is not detection.
- **The probe measures readability, not use** (see line 4); features are z-scored, the same logistic regression for every model; a shuffled-label control gives AUC 0.50 for all.
- **Training.** Keep runs train on 1.50x as many reports per epoch (101,484 against 67,768; 1,058 against 706 batches), so they take 1.5x the steps in the same 2 epochs. The tokenizer was fitted on all of January, including the validation slice (as in the earlier sections). Nothing was tuned or selected on April; all settings were fixed in NOTES.md section 15 before any attack score was computed. Two choices were made while building and before any attack score existed (NOTES 15.7): the white-box attacker keeps the best edit so far and stops when a report is below the 1% threshold; the "fits in 512 tokens" subset.
- **Preliminary GPU results.** The attack scoring of §5.11 (surrogate-chosen padding, white-box attack, random-padding test, probe) and the training and scoring of §5.12 are preliminary and are to be re-run on the author's own Kaggle account. The scoring pipeline reproduces the stored April logits of the unedited reports (largest difference 3e-5) and the random-padding edits equal the arrays of REPORT 5.10 token for token (checked on 600 reports x 6 edits).
- **Edited reports exist in memory only.** The edits of the training runs and of every attack are built from the call-token store of the ORIGINAL reports (verified against full re-tokenisation: 0 of 1,500 edits and 0 of 3,000 unedited reports differ; the §5.10 arrays are reproduced exactly) and only scores, logits and AUCs are saved. Artefacts that predate this rule and contain edited tokens: `results/att_bal/pad/april_pad.npz` (tracked in git; pushed in commit 6f22129), the private Kaggle datasets `nebula-v2pe-padtest` and `nebula-v2pe-augb`, and local copies in `results/_pad_train` and `results/_pad_bundle`; they are not used by anything in this section and I have not deleted them (a history purge would need a force-push).

Code: `baseline/callstore.py`, `inmem_pad.py`, `v2pe.py` (training), `attack_rank.py`, `attack_run.py`, `probe.py`, `review_gpu.py` (scoring), `attack_stats.py`, `review_tables.py`, `review_attacks.py`, `review_cluster.py`, `review_write.py`, `review_compose.py`. Plan and decisions: `NOTES.md` section 15.
