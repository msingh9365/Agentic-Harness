| model | mean spread (max-min over the 9 shifts), malware / benign | median, malware / benign | mean spread / SD of clean logits, malware / benign | control: spread over 9 equal-length paddings (s about 32), malware / benign | pAUC range over s (points) [cluster CI] | verdict |
|---|---|---|---|---|---|---|
| M1 Nebula | 20.297 [17.912, 22.322] / 11.709 [10.180, 13.552] | 19.479 / 9.927 | 1.190 / 0.980 | 12.203 / 9.498 | 35.07 [23.48, 45.81] | position-sensitive |
| M3 ATT+bal | 4.091 [3.616, 4.576] / 5.018 [4.573, 5.422] | 3.622 / 4.336 | 0.430 / 0.841 | 1.857 / 3.839 | 2.10 [1.60, 5.39] | in between |

M1 minus M3: pauc range +0.330 [+0.204, +0.425]; spread malware +16.206 [+13.886, +18.387]; spread benign +6.690 [+5.197, +8.383] (pAUC range in absolute pAUC units; spreads in logit units; cluster 95% intervals).
