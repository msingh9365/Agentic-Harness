**April pAUC@1e-2 with the current tokenizer and with the corrected tokenizer (byte fallback, full character coverage, id 0 = padding only), mean ± std over 10 seeds and the paired difference corrected − current (points x100). Bold = resolved (cluster interval excludes 0).**

| model | pAUC@1e-2 current | pAUC@1e-2 corrected | difference (points) | stratified 95% CI | cluster 95% CI | seeds | outcome |
|---|---|---|---|---|---|---|---|
| M1 v2-PE | 0.674 ± 0.053 | 0.686 ± 0.026 | +1.28 | [+0.59, +1.95] | [-0.98, +3.79] | 5 up / 5 down | not resolved |
| M2 two-level | 0.562 ± 0.146 | 0.620 ± 0.080 | **+5.80** | **[+4.40, +7.24]** | **[+3.12, +8.94]** | **7 up / 3 down** | **resolved** |
| M3 ATT+bal | 0.710 ± 0.015 | 0.705 ± 0.025 | -0.50 | [-1.01, -0.03] | [-1.18, +0.20] | 5 up / 5 down | not resolved |
| M4 ATT+bal-2L | 0.663 ± 0.036 | 0.661 ± 0.035 | -0.16 | [-1.43, +1.07] | [-2.13, +1.60] | 4 up / 6 down | not resolved |
