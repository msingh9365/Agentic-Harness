### 5. Drift breakdown (April)

Thresholds: each model's global April 1% FPR threshold (LightGBM: per seed, then mean [min–max]). AUC inside a cell needs ≥ 10 reports of each class. Cells with fewer than 30 reports: `n<30`. Stop reason = `stop_category(main_error)` (REPORT.md §9.4). Seen = the report's API-name sequence (`hash_apis`) occurs in some January report (train or validation side).

#### 5a. Composition: stop reasons in January and April

| stop reason | January malware | January benign | April malware | April benign |
|---|---|---|---|---|
| no error recorded | 41.6% (21,083/50,630) | 51.4% (12,676/24,668) | 26.5% (2,491/9,399) | 32.4% (2,592/8,003) |
| max_api_count (500-call cap) | 24.8% (12,540/50,630) | 9.0% (2,209/24,668) | 15.0% (1,410/9,399) | 8.4% (670/8,003) |
| unsupported API | 0.0% (0/50,630) | 0.9% (210/24,668) | 51.5% (4,844/9,399) | 52.1% (4,172/8,003) |
| invalid memory / CPU fault | 32.8% (16,614/50,630) | 38.2% (9,432/24,668) | 6.2% (580/9,399) | 6.0% (482/8,003) |
| emulator internal error | 0.8% (393/50,630) | 0.6% (141/24,668) | 0.8% (74/9,399) | 1.1% (87/8,003) |

#### 5b. Composition: April reports whose API-name sequence occurs in January

| April | seen in January | unseen | same API-name sequence also occurs in April with the other label |
|---|---|---|---|
| malware | 31.0% (2,914/9,399) | 69.0% (6,485/9,399) | 26.9% (2,532/9,399) |
| benign | 42.7% (3,415/8,003) | 57.3% (4,588/8,003) | 15.3% (1,221/8,003) |

#### 5c. By stop reason: TPR at 1% FPR (malware in the cell)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded | 5,083 (2,491 / 2,592) | 74.0% | 70.4% | 73.0% | 51.7% | 72.6% [72.3%–73.0%] |
| max_api_count (500-call cap) | 2,080 (1,410 / 670) | 82.0% | 81.2% | 80.5% | 79.4% | 77.6% [74.0%–84.9%] |
| unsupported API | 9,016 (4,844 / 4,172) | 73.9% | 77.7% | 76.2% | 17.2% | 49.3% [49.0%–49.8%] |
| invalid memory / CPU fault | 1,062 (580 / 482) | 79.0% | 58.3% | 80.9% | 81.0% | 85.7% [85.7%–85.9%] |
| emulator internal error | 161 (74 / 87) | 9.5% | 27.0% | 21.6% | 6.8% | 37.8% [37.8%–37.8%] |

#### 5d. By stop reason: share of benign flagged (FPR)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded | 5,083 (2,491 / 2,592) | 1.3% | 0.9% | 1.1% | 2.3% | 2.1% [2.0%–2.2%] |
| max_api_count (500-call cap) | 2,080 (1,410 / 670) | 0.9% | 0.3% | 1.0% | 0.1% | 0.4% [0.3%–0.4%] |
| unsupported API | 9,016 (4,844 / 4,172) | 0.8% | 1.0% | 0.9% | 0.5% | 0.4% [0.4%–0.4%] |
| invalid memory / CPU fault | 1,062 (580 / 482) | 0.6% | 1.5% | 1.2% | 0.2% | 1.1% [0.4%–1.5%] |
| emulator internal error | 161 (74 / 87) | 3.4% | 5.7% | 1.1% | 0.0% | 1.1% [1.1%–1.1%] |

#### 5e. By stop reason: AUC inside the cell

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded | 5,083 (2,491 / 2,592) | 0.9395 | 0.9571 | 0.9313 | 0.9423 | 0.9540 [0.9534–0.9548] |
| max_api_count (500-call cap) | 2,080 (1,410 / 670) | 0.9671 | 0.9533 | 0.9673 | 0.8781 | 0.9332 [0.9326–0.9337] |
| unsupported API | 9,016 (4,844 / 4,172) | 0.9689 | 0.9675 | 0.9767 | 0.9412 | 0.9586 [0.9555–0.9625] |
| invalid memory / CPU fault | 1,062 (580 / 482) | 0.9854 | 0.9844 | 0.9806 | 0.9658 | 0.9778 [0.9774–0.9782] |
| emulator internal error | 161 (74 / 87) | 0.8978 | 0.8729 | 0.8660 | 0.9427 | 0.8806 [0.8599–0.8948] |

#### 5f. By seen / unseen: TPR at 1% FPR (malware in the cell)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| seen in January | 6,329 (2,914 / 3,415) | 82.1% | 87.5% | 83.0% | 63.2% | 76.7% [74.3%–80.5%] |
| unseen | 11,073 (6,485 / 4,588) | 71.8% | 68.9% | 72.6% | 28.9% | 55.2% [54.8%–55.9%] |

#### 5g. By seen / unseen: share of benign flagged (FPR)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| seen in January | 6,329 (2,914 / 3,415) | 0.7% | 1.1% | 0.8% | 0.9% | 1.1% [1.1%–1.1%] |
| unseen | 11,073 (6,485 / 4,588) | 1.2% | 0.9% | 1.2% | 1.1% | 0.9% [0.9%–0.9%] |

#### 5h. By seen / unseen: AUC inside the cell

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| seen in January | 6,329 (2,914 / 3,415) | 0.9865 | 0.9909 | 0.9883 | 0.9665 | 0.9737 [0.9724–0.9746] |
| unseen | 11,073 (6,485 / 4,588) | 0.9371 | 0.9392 | 0.9386 | 0.8881 | 0.9379 [0.9354–0.9395] |

#### 5i. By family: TPR at 1% FPR

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| backdoor | 1,940 (1,940 / 0) | 82.9% | 80.0% | 82.2% | 77.2% | 77.6% [73.6%–83.5%] |
| coinminer | 1,684 (1,684 / 0) | 81.9% | 66.3% | 79.5% | 24.8% | 57.1% [56.2%–59.0%] |
| dropper | 252 (252 / 0) | 73.4% | 77.4% | 71.8% | 62.7% | 51.6% [51.2%–52.0%] |
| keylogger | 1,041 (1,041 / 0) | 52.2% | 88.1% | 64.4% | 13.3% | 17.0% [16.8%–17.3%] |
| ransomware | 2,139 (2,139 / 0) | 66.8% | 60.4% | 66.5% | 29.0% | 58.4% [58.3%–58.4%] |
| rat | 1,258 (1,258 / 0) | 85.5% | 84.8% | 83.9% | 12.5% | 79.0% [77.9%–80.1%] |
| trojan | 1,085 (1,085 / 0) | 76.2% | 80.9% | 79.8% | 67.4% | 73.6% [73.5%–73.7%] |

#### 5j. By family: AUC (family vs all 8,003 April benign)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| backdoor vs all benign | 9,943 (1,940 / 8,003) | 0.9577 | 0.9678 | 0.9604 | 0.9470 | 0.9465 [0.9463–0.9466] |
| coinminer vs all benign | 9,687 (1,684 / 8,003) | 0.9726 | 0.9691 | 0.9684 | 0.9118 | 0.9393 [0.9332–0.9484] |
| dropper vs all benign | 8,255 (252 / 8,003) | 0.9458 | 0.9678 | 0.9398 | 0.9464 | 0.9503 [0.9484–0.9520] |
| keylogger vs all benign | 9,044 (1,041 / 8,003) | 0.9640 | 0.9861 | 0.9787 | 0.8963 | 0.9101 [0.9048–0.9153] |
| ransomware vs all benign | 10,142 (2,139 / 8,003) | 0.9298 | 0.9464 | 0.9195 | 0.9247 | 0.9526 [0.9510–0.9535] |
| rat vs all benign | 9,261 (1,258 / 8,003) | 0.9842 | 0.9756 | 0.9864 | 0.9076 | 0.9825 [0.9823–0.9827] |
| trojan vs all benign | 9,088 (1,085 / 8,003) | 0.9634 | 0.9473 | 0.9731 | 0.9512 | 0.9704 [0.9696–0.9708] |

#### 5k. Stop reason × seen/unseen: TPR at 1% FPR

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded / seen in January | 2,409 (1,245 / 1,164) | 87.0% | 89.3% | 86.3% | 46.5% | 77.4% [75.7%–78.6%] |
| no error recorded / unseen | 2,674 (1,246 / 1,428) | 61.1% | 51.4% | 59.7% | 56.9% | 67.8% [66.8%–69.2%] |
| max_api_count (500-call cap) / seen in January | 1,460 (1,161 / 299) | 95.4% | 94.8% | 93.8% | 92.4% | 90.0% [85.5%–98.8%] |
| max_api_count (500-call cap) / unseen | 620 (249 / 371) | 19.3% | 17.7% | 18.5% | 18.9% | 20.2% [20.1%–20.5%] |
| unsupported API / seen in January | 1,694 (216 / 1,478) | 9.7% | 38.9% | 26.4% | 0.9% | 1.9% [1.9%–1.9%] |
| unsupported API / unseen | 7,322 (4,628 / 2,694) | 76.9% | 79.5% | 78.5% | 18.0% | 51.5% [51.2%–52.0%] |
| invalid memory / CPU fault / seen in January | 709 (268 / 441) | 67.2% | 90.3% | 71.3% | 69.8% | 74.6% [74.6%–74.6%] |
| invalid memory / CPU fault / unseen | 353 (312 / 41) | 89.1% | 30.8% | 89.1% | 90.7% | 95.3% [95.2%–95.5%] |
| emulator internal error / seen in January | 57 (24 / 33) | 4.2% | 50.0% | 33.3% | 4.2% | 100.0% [100.0%–100.0%] |
| emulator internal error / unseen | 104 (50 / 54) | 12.0% | 16.0% | 16.0% | 8.0% | 8.0% [8.0%–8.0%] |

#### 5l. Stop reason × seen/unseen: share of benign flagged

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded / seen in January | 2,409 (1,245 / 1,164) | 1.1% | 1.1% | 0.9% | 2.6% | 2.7% [2.7%–2.7%] |
| no error recorded / unseen | 2,674 (1,246 / 1,428) | 1.4% | 0.8% | 1.3% | 2.0% | 1.5% [1.3%–1.8%] |
| max_api_count (500-call cap) / seen in January | 1,460 (1,161 / 299) | 0.3% | 0.0% | 1.0% | 0.0% | 0.9% [0.7%–1.0%] |
| max_api_count (500-call cap) / unseen | 620 (249 / 371) | 1.3% | 0.5% | 1.1% | 0.3% | 0.0% [0.0%–0.0%] |
| unsupported API / seen in January | 1,694 (216 / 1,478) | 0.4% | 1.0% | 0.6% | 0.0% | 0.0% [0.0%–0.0%] |
| unsupported API / unseen | 7,322 (4,628 / 2,694) | 1.1% | 1.0% | 1.1% | 0.7% | 0.6% [0.6%–0.7%] |
| invalid memory / CPU fault / seen in January | 709 (268 / 441) | 0.5% | 1.6% | 0.7% | 0.2% | 0.2% [0.2%–0.2%] |
| invalid memory / CPU fault / unseen | 353 (312 / 41) | 2.4% | 0.0% | 7.3% | 0.0% | 10.6% [2.4%–14.6%] |
| emulator internal error / seen in January | 57 (24 / 33) | 3.0% | 6.1% | 3.0% | 0.0% | 3.0% [3.0%–3.0%] |
| emulator internal error / unseen | 104 (50 / 54) | 3.7% | 5.6% | 0.0% | 0.0% | 0.0% [0.0%–0.0%] |

#### 5m. Stop reason × seen/unseen: AUC

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded / seen in January | 2,409 (1,245 / 1,164) | 0.9904 | 0.9903 | 0.9920 | 0.9503 | 0.9633 [0.9614–0.9650] |
| no error recorded / unseen | 2,674 (1,246 / 1,428) | 0.8754 | 0.9063 | 0.8605 | 0.9342 | 0.9442 [0.9418–0.9469] |
| max_api_count (500-call cap) / seen in January | 1,460 (1,161 / 299) | 0.9975 | 0.9977 | 0.9966 | 0.9986 | 0.9985 [0.9983–0.9988] |
| max_api_count (500-call cap) / unseen | 620 (249 / 371) | 0.8500 | 0.7598 | 0.8238 | 0.3131 | 0.4295 [0.4264–0.4338] |
| unsupported API / seen in January | 1,694 (216 / 1,478) | 0.9278 | 0.9743 | 0.9446 | 0.8902 | 0.8882 [0.8874–0.8892] |
| unsupported API / unseen | 7,322 (4,628 / 2,694) | 0.9674 | 0.9611 | 0.9754 | 0.9368 | 0.9594 [0.9570–0.9608] |
| invalid memory / CPU fault / seen in January | 709 (268 / 441) | 0.9887 | 0.9937 | 0.9793 | 0.9384 | 0.9682 [0.9682–0.9682] |
| invalid memory / CPU fault / unseen | 353 (312 / 41) | 0.9569 | 0.9392 | 0.9570 | 0.9840 | 0.9829 [0.9824–0.9833] |
| emulator internal error / seen in January | 57 (24 / 33) | 0.9609 | 0.9583 | 0.9545 | 0.9848 | 1.0000 [1.0000–1.0000] |
| emulator internal error / unseen | 104 (50 / 54) | 0.8444 | 0.8111 | 0.8000 | 0.9359 | 0.8223 [0.7993–0.8456] |

#### 5n. Reference: the same baselines on January validation, by stop reason

Threshold from the January-validation benign scores. Released Nebula is not shown: it was probably trained on these January reports.

| model | stop reason | reports (malware / benign) | TPR at 1% FPR | AUC |
|---|---|---|---|---|
| lr_api_bigram | no error recorded | 3,401 (2,842 / 559) | 92.7% | 0.9897 |
| lr_api_bigram | max_api_count (500-call cap) | 976 (812 / 164) | 74.3% | 0.9817 |
| lr_api_bigram | unsupported API | 28 (0 / 28) | n<30 | n<30 |
| lr_api_bigram | invalid memory / CPU fault | 5,178 (3,833 / 1,345) | 28.6% | 0.9630 |
| lr_api_bigram | emulator internal error | 36 (29 / 7) | 0.0% | — |
| lgbm_api_bigram | no error recorded | 3,401 (2,842 / 559) | 67.6% [67.6%–67.6%] | 0.9801 [0.9755–0.9830] |
| lgbm_api_bigram | max_api_count (500-call cap) | 976 (812 / 164) | 94.4% [94.1%–94.6%] | 0.9907 [0.9859–0.9931] |
| lgbm_api_bigram | unsupported API | 28 (0 / 28) | n<30 | n<30 |
| lgbm_api_bigram | invalid memory / CPU fault | 5,178 (3,833 / 1,345) | 68.0% [27.7%–88.5%] | 0.9734 [0.9728–0.9744] |
| lgbm_api_bigram | emulator internal error | 36 (29 / 7) | 31.0% [0.0%–93.1%] | — |
