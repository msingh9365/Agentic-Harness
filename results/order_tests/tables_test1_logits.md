| model | variant | share of reports whose order changed | mean abs logit change / SD of clean logits (malware / benign) | mean abs change by stratum of m (malware / benign): m<2 | 2<=m<10 | m>=10 |
|---|---|---|---|---|---|---|
| M1 Nebula | (a) window shuffle | 98.7% | 0.622 / 0.624 | 0.000 / 0.000 (n=170) | 2.687 / 1.653 (n=2098) | 11.452 / 8.223 (n=15134) |
| M1 Nebula | (b) local shuffle (5) | 98.7% | 0.239 / 0.210 | 0.000 / 0.000 (n=170) | 2.000 / 1.415 (n=2098) | 4.242 / 2.710 (n=15134) |
| M1 Nebula | (c) reversal | 99.0% | 0.691 / 0.817 | 0.000 / 0.000 (n=170) | 2.813 / 1.869 (n=2098) | 13.032 / 11.025 (n=15134) |
| M1 Nebula | (d) full shuffle (reference) | 98.7% | 0.748 / 0.760 | 0.000 / 0.000 (n=170) | 2.742 / 1.668 (n=2098) | 13.872 / 10.160 (n=15134) |
| M3 ATT+bal | (a) window shuffle | 98.7% | 0.213 / 0.393 | 0.000 / 0.000 (n=170) | 1.113 / 1.553 (n=2098) | 2.151 / 2.519 (n=15134) |
| M3 ATT+bal | (b) local shuffle (5) | 98.7% | 0.093 / 0.180 | 0.000 / 0.000 (n=170) | 0.820 / 1.327 (n=2098) | 0.898 / 1.045 (n=15134) |
| M3 ATT+bal | (c) reversal | 99.0% | 0.216 / 0.568 | 0.000 / 0.000 (n=170) | 1.418 / 1.900 (n=2098) | 2.155 / 3.673 (n=15134) |
| M3 ATT+bal | (d) full shuffle (reference) | 98.7% | 0.381 / 1.090 | 0.000 / 0.000 (n=170) | 1.149 / 1.565 (n=2098) | 3.958 / 7.405 (n=15134) |
