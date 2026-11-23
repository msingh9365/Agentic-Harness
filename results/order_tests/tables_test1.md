| model | variant | pAUC@1e-2 | drop vs clean (points) | cluster 95% CI (points) | seeds down/up | AUC | TPR@1% (own thr) | mean abs logit change malware / benign | verdict |
|---|---|---|---|---|---|---|---|---|---|
| M1 Nebula | clean | 0.686 ± 0.026 |  |  |  | 0.9639 | 0.791 |  |  |
| M1 Nebula | (a) window shuffle | 0.417 ± 0.101 | +26.90 (RESOLVED) | [+17.74, +35.82] | 10/0 | 0.9229 | 0.516 | 10.468 / 7.190 | order-sensitive |
| M1 Nebula | (b) local shuffle (5) | 0.645 ± 0.038 | +4.15 (RESOLVED) | [+2.40, +5.90] | 10/0 | 0.9595 | 0.756 | 3.982 / 2.492 | in between / inconclusive |
| M1 Nebula | (c) reversal | 0.415 ± 0.126 | +27.10 (RESOLVED) | [+17.51, +37.84] | 10/0 | 0.8778 | 0.510 | 11.886 / 9.591 | order-sensitive |
| M1 Nebula | (d) full shuffle (reference) | 0.348 ± 0.058 | +33.83 (RESOLVED) | [+22.30, +44.37] | 10/0 | 0.9033 | 0.446 | 12.626 / 8.831 | reference |
| M3 ATT+bal | clean | 0.705 ± 0.025 |  |  |  | 0.9693 | 0.790 |  |  |
| M3 ATT+bal | (a) window shuffle | 0.664 ± 0.027 | +4.03 (RESOLVED) | [+1.83, +6.67] | 10/0 | 0.9626 | 0.759 | 2.029 / 2.350 | in between / inconclusive |
| M3 ATT+bal | (b) local shuffle (5) | 0.701 ± 0.025 | +0.43 (not resolved) | [-0.09, +0.96] | 9/1 | 0.9680 | 0.786 | 0.884 / 1.071 | bag-of-calls-like |
| M3 ATT+bal | (c) reversal | 0.685 ± 0.015 | +1.96 (not resolved) | [-1.10, +5.57] | 9/1 | 0.9597 | 0.753 | 2.065 / 3.375 | in between / inconclusive |
| M3 ATT+bal | (d) full shuffle (reference) | 0.572 ± 0.021 | +13.33 (RESOLVED) | [+7.21, +19.87] | 10/0 | 0.9227 | 0.679 | 3.641 / 6.485 | reference |
