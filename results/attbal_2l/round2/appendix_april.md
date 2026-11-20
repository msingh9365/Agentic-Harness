### Round 2, all 36 candidates: validation (used for the selection) and April (NOT used for any choice)

| cell | epoch | weights | mean val pAUC@1e-2 | April pAUC@1e-2 (mean ± std, 10 seeds) |  |
|---|---|---|---|---|---|
| R1_dec_lr1e-3 | 1 | raw | 0.9404 | 0.688 ± 0.023 |  |
| R1_dec_lr1e-3 | 1 | ema | 0.9516 | 0.693 ± 0.031 |  |
| R1_dec_lr1e-3 | 2 | raw | 0.8546 | 0.627 ± 0.098 |  |
| R1_dec_lr1e-3 | 2 | ema | 0.9186 | 0.652 ± 0.051 |  |
| R1_dec_lr1e-3 | 3 | raw | 0.9345 | 0.678 ± 0.038 |  |
| R1_dec_lr1e-3 | 3 | ema | 0.9364 | 0.678 ± 0.038 |  |
| R2_dec_lr5e-4 | 1 | raw | 0.9279 | 0.680 ± 0.035 |  |
| R2_dec_lr5e-4 | 1 | ema | 0.9467 | 0.687 ± 0.036 |  |
| R2_dec_lr5e-4 | 2 | raw | 0.9209 | 0.657 ± 0.044 |  |
| R2_dec_lr5e-4 | 2 | ema | 0.9358 | 0.672 ± 0.025 |  |
| R2_dec_lr5e-4 | 3 | raw | 0.9420 | 0.682 ± 0.024 |  |
| R2_dec_lr5e-4 | 3 | ema | 0.9416 | 0.682 ± 0.024 |  |
| R3_const_lr3e-4 | 1 | raw | 0.9299 | 0.681 ± 0.029 |  |
| R3_const_lr3e-4 | 1 | ema | 0.9450 | 0.685 ± 0.032 |  |
| R3_const_lr3e-4 | 2 | raw | 0.8914 | 0.641 ± 0.065 |  |
| R3_const_lr3e-4 | 2 | ema | 0.9341 | 0.669 ± 0.025 |  |
| R3_const_lr3e-4 | 3 | raw | 0.9442 | 0.686 ± 0.027 |  |
| R3_const_lr3e-4 | 3 | ema | 0.9414 | 0.685 ± 0.017 |  |
| R4_dec_l1x0.25 | 1 | raw | 0.9346 | 0.690 ± 0.033 |  |
| R4_dec_l1x0.25 | 1 | ema | 0.9502 | 0.694 ± 0.026 |  |
| R4_dec_l1x0.25 | 2 | raw | 0.9254 | 0.664 ± 0.052 |  |
| R4_dec_l1x0.25 | 2 | ema | 0.9422 | 0.685 ± 0.028 |  |
| R4_dec_l1x0.25 | 3 | raw | 0.9458 | 0.688 ± 0.029 |  |
| R4_dec_l1x0.25 | 3 | ema | 0.9469 | 0.691 ± 0.027 |  |
| R5_dec_freeze1ep | 1 | raw | 0.9503 | 0.699 ± 0.019 | **chosen** |
| R5_dec_freeze1ep | 1 | ema | 0.9530 | 0.699 ± 0.019 |  |
| R5_dec_freeze1ep | 2 | raw | 0.8907 | 0.650 ± 0.066 |  |
| R5_dec_freeze1ep | 2 | ema | 0.9359 | 0.682 ± 0.032 |  |
| R5_dec_freeze1ep | 3 | raw | 0.9275 | 0.687 ± 0.029 |  |
| R5_dec_freeze1ep | 3 | ema | 0.9333 | 0.689 ± 0.029 |  |
| R6_dec_scratch | 1 | raw | 0.8778 | 0.630 ± 0.108 |  |
| R6_dec_scratch | 1 | ema | 0.9191 | 0.680 ± 0.033 |  |
| R6_dec_scratch | 2 | raw | 0.9172 | 0.687 ± 0.034 |  |
| R6_dec_scratch | 2 | ema | 0.9450 | 0.692 ± 0.030 |  |
| R6_dec_scratch | 3 | raw | 0.9459 | 0.700 ± 0.025 |  |
| R6_dec_scratch | 3 | ema | 0.9471 | 0.701 ± 0.020 |  |

