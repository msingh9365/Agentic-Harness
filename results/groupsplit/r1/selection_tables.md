### R1 selection on January fold 9 (5 seeds; validation only; no April)

| variant | epoch | val pAUC@1e-2 (mean ± SD) | val AUC (min over seeds) | val loss | train loss | R20 | R100 | status |
|---|---|---|---|---|---|---|---|---|
| a | 1 | 0.4910 ± 0.0171 | 0.9457 | 0.3702 | 0.1014 | 0.504 | 0.482 | R guard (best mean R20 0.667, R100 0.619; margin 0.02) |
| a | 2 | 0.4534 ± 0.0332 | 0.9445 | 0.4579 | 0.0491 | 0.507 | 0.476 | R guard (best mean R20 0.667, R100 0.619; margin 0.02) |
| a | 3 | 0.4403 ± 0.0355 | 0.9304 | 0.5522 | 0.0403 | 0.454 | 0.426 | R guard (best mean R20 0.667, R100 0.619; margin 0.02) |
| b | 1 | 0.5913 ± 0.0612 | 0.9235 | 0.4510 | 0.1679 | 0.602 | 0.537 | R guard (best mean R20 0.667, R100 0.619; margin 0.02) |
| b | 2 | 0.5861 ± 0.0608 | 0.9075 | 0.6670 | 0.0647 | 0.667 | 0.619 | **CHOSEN** |
| b | 3 | 0.5583 ± 0.0545 | 0.9127 | 0.7195 | 0.0499 | 0.624 | 0.583 | R guard (best mean R20 0.667, R100 0.619; margin 0.02) |

Choice: **variant (b), 2 epoch(s)**

