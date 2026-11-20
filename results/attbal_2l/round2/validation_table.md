# Round 2: selection from validation numbers only (NOTES 20)

| cell | epoch | weights | mean val pAUC@1e-2 | SE | mean val loss | min val AUC | collapsed | within 1 SE of best |
|---|---|---|---|---|---|---|---|---|
| R1_dec_lr1e-3 | 1 | raw | 0.9404 | 0.0081 | 0.0562 | 0.9962 | no |  |
| R1_dec_lr1e-3 | 1 | ema | 0.9516 | 0.0020 | 0.0545 | 0.9978 | no | yes |
| R1_dec_lr1e-3 | 2 | raw | 0.8546 | 0.0436 | 0.0618 | 0.9942 | no |  |
| R1_dec_lr1e-3 | 2 | ema | 0.9186 | 0.0149 | 0.0598 | 0.9957 | no |  |
| R1_dec_lr1e-3 | 3 | raw | 0.9345 | 0.0044 | 0.0561 | 0.9971 | no |  |
| R1_dec_lr1e-3 | 3 | ema | 0.9364 | 0.0044 | 0.0562 | 0.9973 | no |  |
| R2_dec_lr5e-4 | 1 | raw | 0.9279 | 0.0185 | 0.0560 | 0.9949 | no |  |
| R2_dec_lr5e-4 | 1 | ema | 0.9467 | 0.0051 | 0.0539 | 0.9973 | no |  |
| R2_dec_lr5e-4 | 2 | raw | 0.9209 | 0.0087 | 0.0595 | 0.9964 | no |  |
| R2_dec_lr5e-4 | 2 | ema | 0.9358 | 0.0057 | 0.0580 | 0.9970 | no |  |
| R2_dec_lr5e-4 | 3 | raw | 0.9420 | 0.0036 | 0.0544 | 0.9972 | no |  |
| R2_dec_lr5e-4 | 3 | ema | 0.9416 | 0.0046 | 0.0543 | 0.9974 | no |  |
| R3_const_lr3e-4 | 1 | raw | 0.9299 | 0.0169 | 0.0556 | 0.9950 | no |  |
| R3_const_lr3e-4 | 1 | ema | 0.9450 | 0.0053 | 0.0537 | 0.9975 | no |  |
| R3_const_lr3e-4 | 2 | raw | 0.8914 | 0.0190 | 0.0607 | 0.9964 | no |  |
| R3_const_lr3e-4 | 2 | ema | 0.9341 | 0.0042 | 0.0581 | 0.9969 | no |  |
| R3_const_lr3e-4 | 3 | raw | 0.9442 | 0.0044 | 0.0545 | 0.9972 | no |  |
| R3_const_lr3e-4 | 3 | ema | 0.9414 | 0.0044 | 0.0549 | 0.9971 | no |  |
| R4_dec_l1x0.25 | 1 | raw | 0.9346 | 0.0184 | 0.0564 | 0.9946 | no |  |
| R4_dec_l1x0.25 | 1 | ema | 0.9502 | 0.0032 | 0.0546 | 0.9974 | no | yes |
| R4_dec_l1x0.25 | 2 | raw | 0.9254 | 0.0093 | 0.0596 | 0.9970 | no |  |
| R4_dec_l1x0.25 | 2 | ema | 0.9422 | 0.0033 | 0.0587 | 0.9970 | no |  |
| R4_dec_l1x0.25 | 3 | raw | 0.9458 | 0.0028 | 0.0545 | 0.9971 | no |  |
| R4_dec_l1x0.25 | 3 | ema | 0.9469 | 0.0028 | 0.0545 | 0.9973 | no |  |
| R5_dec_freeze1ep | 1 | raw | 0.9503 | 0.0045 | 0.0487 | 0.9978 | no | **chosen** |
| R5_dec_freeze1ep | 1 | ema | 0.9530 | 0.0028 | 0.0470 | 0.9980 | no | best |
| R5_dec_freeze1ep | 2 | raw | 0.8907 | 0.0193 | 0.0592 | 0.9958 | no |  |
| R5_dec_freeze1ep | 2 | ema | 0.9359 | 0.0032 | 0.0587 | 0.9967 | no |  |
| R5_dec_freeze1ep | 3 | raw | 0.9275 | 0.0075 | 0.0556 | 0.9968 | no |  |
| R5_dec_freeze1ep | 3 | ema | 0.9333 | 0.0054 | 0.0554 | 0.9970 | no |  |
| R6_dec_scratch | 1 | raw | 0.8778 | 0.0326 | 0.0699 | 0.9946 | no |  |
| R6_dec_scratch | 1 | ema | 0.9191 | 0.0049 | 0.0685 | 0.9970 | no |  |
| R6_dec_scratch | 2 | raw | 0.9172 | 0.0181 | 0.0605 | 0.9964 | no |  |
| R6_dec_scratch | 2 | ema | 0.9450 | 0.0045 | 0.0568 | 0.9978 | no |  |
| R6_dec_scratch | 3 | raw | 0.9459 | 0.0058 | 0.0574 | 0.9974 | no |  |
| R6_dec_scratch | 3 | ema | 0.9471 | 0.0049 | 0.0568 | 0.9976 | no |  |

CHOSEN: cell=R5_dec_freeze1ep epoch=1 weights=raw (mean val pAUC@1e-2 0.9503, SE 0.0045); best: R5_dec_freeze1ep epoch 1 ema (0.9530)
