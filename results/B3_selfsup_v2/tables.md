#### Settings chosen on the validation slice (rule: NOTES.md 11.4)

| run type | lr | epoch | val TPR@1e-3 | val TPR@1e-2 | val AUC | val loss | cells tied | collapsed |
|---|---|---|---|---|---|---|---|---|
| upper bound (90% labeled) | 0.002 | 3 | 0.910 ± 0.013 (SE) | 0.977 | 0.9980 | 0.093 | 2 | none |
| lower bound (20% labeled) | 0.002 | 3 | 0.693 ± 0.026 (SE) | 0.922 | 0.9942 | 0.175 | 3 | none |
| control: causal last-token, 20%, no pre-training | 0.001 | 3 | 0.747 ± 0.032 (SE) | 0.916 | 0.9950 | 0.129 | 4 | none |
| AR pre-training + last-token | 0.002 | 3 | 0.791 ± 0.028 (SE) | 0.927 | 0.9950 | 0.107 | 3 | none |
| per-position MLM pre-training | 0.002 | 6 | 0.796 ± 0.020 (SE) | 0.928 | 0.9947 | 0.259 | 1 | none |


#### April test set at the chosen settings (logit-ranked; mean ± std over 5 seeds; bootstrap 95% CI of the per-seed mean)

| run | TPR@1e-3 | 95% CI (pts) | TPR@1e-2 | 95% CI (pts) | AUC | F1 (0.5) | TPR@1e-3 literal float32 |
|---|---|---|---|---|---|---|---|
| upper bound (90% labeled) | 0.522 ± 0.092 | [46.9, 57.0] | 0.772 ± 0.024 | [75.8, 79.0] | 0.9666 ± 0.0035 | 0.907 ± 0.003 | 0.336 ± 0.315 |
| lower bound (20% labeled) | 0.368 ± 0.075 | [33.9, 41.9] | 0.666 ± 0.028 | [64.9, 68.1] | 0.9530 ± 0.0096 | 0.873 ± 0.027 | 0.213 ± 0.197 |
| control: causal last-token, 20%, no pre-training | 0.412 ± 0.055 | [34.2, 43.8] | 0.650 ± 0.012 | [63.2, 66.5] | 0.9487 ± 0.0106 | 0.862 ± 0.013 | 0.412 ± 0.055 |
| AR pre-training + last-token | 0.463 ± 0.072 | [43.4, 52.6] | 0.711 ± 0.051 | [69.4, 72.1] | 0.9617 ± 0.0038 | 0.887 ± 0.010 | 0.388 ± 0.223 |
| per-position MLM pre-training | 0.404 ± 0.037 | [37.0, 45.2] | 0.696 ± 0.040 | [68.1, 71.1] | 0.9566 ± 0.0087 | 0.882 ± 0.019 | 0.000 ± 0.000 |


#### Paired per-seed differences in points (mean ± std over 5 seeds; positive in n of 5 seeds) and bootstrap 95% CI of the difference of the seed means

| difference | metric | per-seed mean ± std | seeds > 0 | bootstrap 95% CI [pts] |
|---|---|---|---|---|
| upper − lower | TPR@1e-3 | +15.3 ± 10.3 | 4/5 | +15.3 [+10.9, +18.7] **resolved** |
| upper − lower | TPR@1e-2 | +10.7 ± 4.5 | 5/5 | +10.7 [+9.7, +12.3] **resolved** |
| upper − lower | AUC | +1.36 ± 1.01 | 5/5 | +1.4 [+1.2, +1.5] **resolved** |
| AR − lower | TPR@1e-3 | +9.5 ± 4.0 | 5/5 | +9.5 [+6.1, +14.6] **resolved** |
| AR − lower | TPR@1e-2 | +4.5 ± 5.5 | 3/5 | +4.5 [+3.0, +5.7] **resolved** |
| AR − lower | AUC | +0.87 ± 0.89 | 3/5 | +0.9 [+0.7, +1.0] **resolved** |
| MLM − lower | TPR@1e-3 | +3.6 ± 7.1 | 3/5 | +3.6 [-0.6, +7.6] not resolved |
| MLM − lower | TPR@1e-2 | +3.1 ± 4.8 | 4/5 | +3.1 [+1.9, +4.3] **resolved** |
| MLM − lower | AUC | +0.36 ± 0.97 | 3/5 | +0.4 [+0.3, +0.5] **resolved** |
| AR − its causal control | TPR@1e-3 | +5.1 ± 10.3 | 2/5 | +5.1 [+3.0, +12.3] **resolved** |
| AR − its causal control | TPR@1e-2 | +6.1 ± 5.2 | 4/5 | +6.1 [+4.6, +7.4] **resolved** |
| AR − its causal control | AUC | +1.30 ± 0.81 | 5/5 | +1.3 [+1.2, +1.4] **resolved** |
| upper − AR | TPR@1e-3 | +5.8 ± 12.6 | 3/5 | +5.8 [-0.1, +9.5] not resolved |
| upper − AR | TPR@1e-2 | +6.2 ± 5.3 | 4/5 | +6.2 [+5.1, +8.1] **resolved** |
| upper − AR | AUC | +0.49 ± 0.33 | 5/5 | +0.5 [+0.4, +0.6] **resolved** |
| upper − MLM | TPR@1e-3 | +11.8 ± 11.0 | 5/5 | +11.8 [+6.7, +16.0] **resolved** |
| upper − MLM | TPR@1e-2 | +7.6 ± 2.7 | 5/5 | +7.6 [+6.5, +9.2] **resolved** |
| upper − MLM | AUC | +1.00 ± 0.62 | 5/5 | +1.0 [+0.9, +1.1] **resolved** |


(AUC differences are in points of AUC x 100.) Seed-ensemble flavour of the CI (mean logit over the 5 seeds) is in `bootstrap.json` (`ens`).

#### Appendix: the full grid on the April test set. **NOT used for selection** (every choice was made on the validation slice)

| run | lr | epoch | TPR@1e-3 | TPR@1e-2 | AUC | F1 (0.5) |
|---|---|---|---|---|---|---|
| upper bound (90% labeled) | 0.002 | 1 | 0.458 ± 0.090 | 0.746 ± 0.021 | 0.9674 ± 0.0060 | 0.898 ± 0.014 |
| upper bound (90% labeled) | 0.002 | 2 | 0.527 ± 0.079 | 0.776 ± 0.011 | 0.9677 ± 0.0076 | 0.905 ± 0.011 |
| upper bound (90% labeled) | 0.002 | 3 | 0.522 ± 0.092 | 0.772 ± 0.024 | 0.9666 ± 0.0035 | 0.907 ± 0.003 |
| upper bound (90% labeled) | 0.002 | 4 | 0.522 ± 0.044 | 0.776 ± 0.020 | 0.9673 ± 0.0055 | 0.913 ± 0.008 |
| upper bound (90% labeled) | 0.002 | 5 | 0.520 ± 0.097 | 0.786 ± 0.029 | 0.9671 ± 0.0035 | 0.914 ± 0.009 |
| upper bound (90% labeled) | 0.002 | 6 | 0.516 ± 0.064 | 0.799 ± 0.005 | 0.9683 ± 0.0018 | 0.909 ± 0.002 |
| upper bound (90% labeled) | 0.001 | 1 | 0.474 ± 0.037 | 0.712 ± 0.037 | 0.9586 ± 0.0093 | 0.897 ± 0.014 |
| upper bound (90% labeled) | 0.001 | 2 | 0.494 ± 0.123 | 0.780 ± 0.036 | 0.9610 ± 0.0103 | 0.908 ± 0.011 |
| upper bound (90% labeled) | 0.001 | 3 | 0.511 ± 0.034 | 0.785 ± 0.016 | 0.9622 ± 0.0043 | 0.909 ± 0.004 |
| upper bound (90% labeled) | 0.001 | 4 | 0.464 ± 0.100 | 0.788 ± 0.015 | 0.9603 ± 0.0062 | 0.907 ± 0.005 |
| upper bound (90% labeled) | 0.001 | 5 | 0.515 ± 0.098 | 0.780 ± 0.021 | 0.9677 ± 0.0050 | 0.912 ± 0.005 |
| upper bound (90% labeled) | 0.001 | 6 | 0.516 ± 0.070 | 0.787 ± 0.018 | 0.9647 ± 0.0087 | 0.914 ± 0.003 |
| lower bound (20% labeled) | 0.002 | 1 | 0.321 ± 0.054 | 0.558 ± 0.075 | 0.9363 ± 0.0154 | 0.849 ± 0.034 |
| lower bound (20% labeled) | 0.002 | 2 | 0.392 ± 0.051 | 0.640 ± 0.019 | 0.9535 ± 0.0085 | 0.872 ± 0.020 |
| lower bound (20% labeled) | 0.002 | 3 | 0.368 ± 0.075 | 0.666 ± 0.028 | 0.9530 ± 0.0096 | 0.873 ± 0.027 |
| lower bound (20% labeled) | 0.002 | 4 | 0.430 ± 0.060 | 0.661 ± 0.067 | 0.9532 ± 0.0111 | 0.888 ± 0.021 |
| lower bound (20% labeled) | 0.002 | 5 | 0.376 ± 0.067 | 0.642 ± 0.062 | 0.9474 ± 0.0175 | 0.872 ± 0.043 |
| lower bound (20% labeled) | 0.002 | 6 | 0.382 ± 0.068 | 0.622 ± 0.072 | 0.9522 ± 0.0209 | 0.869 ± 0.037 |
| lower bound (20% labeled) | 0.001 | 1 | 0.290 ± 0.116 | 0.456 ± 0.117 | 0.9069 ± 0.0349 | 0.768 ± 0.108 |
| lower bound (20% labeled) | 0.001 | 2 | 0.315 ± 0.073 | 0.576 ± 0.020 | 0.9435 ± 0.0089 | 0.876 ± 0.012 |
| lower bound (20% labeled) | 0.001 | 3 | 0.333 ± 0.119 | 0.614 ± 0.116 | 0.9477 ± 0.0158 | 0.890 ± 0.018 |
| lower bound (20% labeled) | 0.001 | 4 | 0.294 ± 0.061 | 0.655 ± 0.042 | 0.9508 ± 0.0046 | 0.890 ± 0.009 |
| lower bound (20% labeled) | 0.001 | 5 | 0.384 ± 0.063 | 0.640 ± 0.076 | 0.9528 ± 0.0078 | 0.896 ± 0.009 |
| lower bound (20% labeled) | 0.001 | 6 | 0.402 ± 0.084 | 0.627 ± 0.071 | 0.9531 ± 0.0130 | 0.895 ± 0.023 |
| control: causal last-token, 20%, no pre-training | 0.002 | 1 | 0.279 ± 0.034 | 0.588 ± 0.056 | 0.9522 ± 0.0069 | 0.849 ± 0.038 |
| control: causal last-token, 20%, no pre-training | 0.002 | 2 | 0.269 ± 0.086 | 0.606 ± 0.054 | 0.9532 ± 0.0074 | 0.866 ± 0.023 |
| control: causal last-token, 20%, no pre-training | 0.002 | 3 | 0.300 ± 0.103 | 0.614 ± 0.046 | 0.9474 ± 0.0038 | 0.870 ± 0.018 |
| control: causal last-token, 20%, no pre-training | 0.002 | 4 | 0.289 ± 0.094 | 0.601 ± 0.028 | 0.9438 ± 0.0047 | 0.867 ± 0.014 |
| control: causal last-token, 20%, no pre-training | 0.002 | 5 | 0.285 ± 0.083 | 0.609 ± 0.030 | 0.9408 ± 0.0088 | 0.862 ± 0.023 |
| control: causal last-token, 20%, no pre-training | 0.002 | 6 | 0.266 ± 0.077 | 0.584 ± 0.060 | 0.9338 ± 0.0096 | 0.865 ± 0.012 |
| control: causal last-token, 20%, no pre-training | 0.001 | 1 | 0.340 ± 0.044 | 0.581 ± 0.044 | 0.9550 ± 0.0040 | 0.853 ± 0.028 |
| control: causal last-token, 20%, no pre-training | 0.001 | 2 | 0.374 ± 0.079 | 0.640 ± 0.014 | 0.9537 ± 0.0075 | 0.875 ± 0.026 |
| control: causal last-token, 20%, no pre-training | 0.001 | 3 | 0.412 ± 0.055 | 0.650 ± 0.012 | 0.9487 ± 0.0106 | 0.862 ± 0.013 |
| control: causal last-token, 20%, no pre-training | 0.001 | 4 | 0.370 ± 0.071 | 0.627 ± 0.033 | 0.9452 ± 0.0122 | 0.855 ± 0.024 |
| control: causal last-token, 20%, no pre-training | 0.001 | 5 | 0.358 ± 0.059 | 0.608 ± 0.030 | 0.9388 ± 0.0124 | 0.853 ± 0.020 |
| control: causal last-token, 20%, no pre-training | 0.001 | 6 | 0.356 ± 0.064 | 0.615 ± 0.034 | 0.9364 ± 0.0115 | 0.857 ± 0.020 |
| AR pre-training + last-token | 0.002 | 1 | 0.347 ± 0.086 | 0.565 ± 0.057 | 0.9497 ± 0.0074 | 0.834 ± 0.024 |
| AR pre-training + last-token | 0.002 | 2 | 0.409 ± 0.071 | 0.670 ± 0.045 | 0.9577 ± 0.0064 | 0.876 ± 0.015 |
| AR pre-training + last-token | 0.002 | 3 | 0.463 ± 0.072 | 0.711 ± 0.051 | 0.9617 ± 0.0038 | 0.887 ± 0.010 |
| AR pre-training + last-token | 0.002 | 4 | 0.474 ± 0.056 | 0.718 ± 0.021 | 0.9612 ± 0.0063 | 0.896 ± 0.007 |
| AR pre-training + last-token | 0.002 | 5 | 0.434 ± 0.072 | 0.700 ± 0.017 | 0.9580 ± 0.0078 | 0.893 ± 0.007 |
| AR pre-training + last-token | 0.002 | 6 | 0.465 ± 0.109 | 0.708 ± 0.025 | 0.9611 ± 0.0065 | 0.898 ± 0.009 |
| AR pre-training + last-token | 0.001 | 1 | 0.225 ± 0.148 | 0.442 ± 0.102 | 0.9244 ± 0.0119 | 0.835 ± 0.031 |
| AR pre-training + last-token | 0.001 | 2 | 0.423 ± 0.046 | 0.633 ± 0.047 | 0.9578 ± 0.0055 | 0.857 ± 0.026 |
| AR pre-training + last-token | 0.001 | 3 | 0.444 ± 0.113 | 0.697 ± 0.039 | 0.9599 ± 0.0114 | 0.879 ± 0.025 |
| AR pre-training + last-token | 0.001 | 4 | 0.450 ± 0.094 | 0.690 ± 0.024 | 0.9621 ± 0.0071 | 0.894 ± 0.012 |
| AR pre-training + last-token | 0.001 | 5 | 0.423 ± 0.065 | 0.703 ± 0.045 | 0.9607 ± 0.0073 | 0.887 ± 0.017 |
| AR pre-training + last-token | 0.001 | 6 | 0.473 ± 0.033 | 0.724 ± 0.031 | 0.9573 ± 0.0117 | 0.887 ± 0.027 |
| per-position MLM pre-training | 0.002 | 1 | 0.309 ± 0.046 | 0.488 ± 0.036 | 0.8900 ± 0.0477 | 0.769 ± 0.055 |
| per-position MLM pre-training | 0.002 | 2 | 0.342 ± 0.140 | 0.579 ± 0.059 | 0.9302 ± 0.0234 | 0.851 ± 0.035 |
| per-position MLM pre-training | 0.002 | 3 | 0.318 ± 0.104 | 0.603 ± 0.042 | 0.9428 ± 0.0097 | 0.840 ± 0.043 |
| per-position MLM pre-training | 0.002 | 4 | 0.394 ± 0.061 | 0.657 ± 0.034 | 0.9515 ± 0.0090 | 0.865 ± 0.008 |
| per-position MLM pre-training | 0.002 | 5 | 0.431 ± 0.108 | 0.672 ± 0.041 | 0.9423 ± 0.0139 | 0.860 ± 0.016 |
| per-position MLM pre-training | 0.002 | 6 | 0.404 ± 0.037 | 0.696 ± 0.040 | 0.9566 ± 0.0087 | 0.882 ± 0.019 |
| per-position MLM pre-training | 0.001 | 1 | 0.285 ± 0.075 | 0.490 ± 0.068 | 0.9313 ± 0.0114 | 0.842 ± 0.029 |
| per-position MLM pre-training | 0.001 | 2 | 0.367 ± 0.065 | 0.603 ± 0.043 | 0.9409 ± 0.0037 | 0.849 ± 0.010 |
| per-position MLM pre-training | 0.001 | 3 | 0.361 ± 0.062 | 0.630 ± 0.046 | 0.9374 ± 0.0095 | 0.834 ± 0.039 |
| per-position MLM pre-training | 0.001 | 4 | 0.393 ± 0.043 | 0.622 ± 0.029 | 0.9477 ± 0.0092 | 0.869 ± 0.016 |
| per-position MLM pre-training | 0.001 | 5 | 0.400 ± 0.088 | 0.641 ± 0.081 | 0.9484 ± 0.0099 | 0.875 ± 0.019 |
| per-position MLM pre-training | 0.001 | 6 | 0.357 ± 0.061 | 0.641 ± 0.035 | 0.9521 ± 0.0119 | 0.881 ± 0.022 |
