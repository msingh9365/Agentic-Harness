| model | variant | pAUC@1e-2 | drop vs clean (points) | cluster 95% CI (points) | seeds down/up | AUC | TPR@1% (own thr) | mean abs logit change malware / benign | verdict |
|---|---|---|---|---|---|---|---|---|---|
| M1 Nebula | clean | 0.686 ± 0.026 |  |  |  | 0.9639 | 0.791 |  |  |
| M1 Nebula | (a) window shuffle | 0.417 ± 0.101 | +26.90 (RESOLVED) | [+17.74, +35.82] | 10/0 | 0.9229 | 0.516 | 10.468 / 7.190 | order-sensitive |
| M1 Nebula | (b) local shuffle (5) | 0.645 ± 0.038 | +4.15 (RESOLVED) | [+2.40, +5.90] | 10/0 | 0.9595 | 0.756 | 3.982 / 2.492 | in between / inconclusive |
| M1 Nebula | (c) reversal | 0.415 ± 0.126 | +27.10 (RESOLVED) | [+17.51, +37.84] | 10/0 | 0.8778 | 0.510 | 11.886 / 9.591 | order-sensitive |
| M1 Nebula | (d) full shuffle (reference) | 0.348 ± 0.058 | +33.83 (RESOLVED) | [+22.30, +44.37] | 10/0 | 0.9033 | 0.446 | 12.626 / 8.831 | reference |
| M2 two-level | clean | 0.677 ± 0.030 |  |  |  | 0.9706 | 0.790 |  |  |
| M2 two-level | (a) window shuffle | 0.621 ± 0.027 | +5.59 (RESOLVED) | [+1.17, +10.31] | 3/0 | 0.9675 | 0.765 | 0.854 / 0.496 | order-sensitive |
| M2 two-level | (b) local shuffle (5) | 0.661 ± 0.032 | +1.59 (not resolved) | [-0.74, +4.20] | 2/1 | 0.9698 | 0.779 | 0.390 / 0.256 | in between / inconclusive |
| M2 two-level | (c) reversal | 0.616 ± 0.042 | +6.13 (RESOLVED) | [+1.10, +11.88] | 3/0 | 0.9691 | 0.742 | 0.814 / 0.439 | order-sensitive |
| M2 two-level | (d) full shuffle (reference) | 0.629 ± 0.021 | +4.81 (RESOLVED) | [+0.45, +9.46] | 3/0 | 0.9678 | 0.765 | 0.858 / 0.487 | reference |
| M3 ATT+bal | clean | 0.705 ± 0.025 |  |  |  | 0.9693 | 0.790 |  |  |
| M3 ATT+bal | (a) window shuffle | 0.664 ± 0.027 | +4.03 (RESOLVED) | [+1.83, +6.67] | 10/0 | 0.9626 | 0.759 | 2.029 / 2.350 | in between / inconclusive |
| M3 ATT+bal | (b) local shuffle (5) | 0.701 ± 0.025 | +0.43 (not resolved) | [-0.09, +0.96] | 9/1 | 0.9680 | 0.786 | 0.884 / 1.071 | bag-of-calls-like |
| M3 ATT+bal | (c) reversal | 0.685 ± 0.015 | +1.96 (not resolved) | [-1.10, +5.57] | 9/1 | 0.9597 | 0.753 | 2.065 / 3.375 | in between / inconclusive |
| M3 ATT+bal | (d) full shuffle (reference) | 0.572 ± 0.021 | +13.33 (RESOLVED) | [+7.21, +19.87] | 10/0 | 0.9227 | 0.679 | 3.641 / 6.485 | reference |
| M4 ATT+bal-2L | clean | 0.679 ± 0.041 |  |  |  | 0.9704 | 0.771 |  |  |
| M4 ATT+bal-2L | (a) window shuffle | 0.679 ± 0.030 | +0.02 (not resolved) | [-3.36, +3.55] | 1/2 | 0.9557 | 0.781 | 0.533 / 1.026 | in between / inconclusive |
| M4 ATT+bal-2L | (b) local shuffle (5) | 0.679 ± 0.032 | +0.02 (not resolved) | [-1.26, +1.34] | 2/1 | 0.9677 | 0.777 | 0.208 / 0.390 | bag-of-calls-like |
| M4 ATT+bal-2L | (c) reversal | 0.636 ± 0.036 | +4.29 (not resolved) | [-3.39, +13.52] | 3/0 | 0.9570 | 0.733 | 0.796 / 0.935 | in between / inconclusive |
| M4 ATT+bal-2L | (d) full shuffle (reference) | 0.691 ± 0.031 | -1.18 (not resolved) | [-4.82, +2.63] | 1/2 | 0.9560 | 0.785 | 0.532 / 1.023 | reference |
