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
| no error recorded | 5,083 (2,491 / 2,592) | 74.0% | 70.4% | 73.0% | 50.2% | 72.7% [71.2%–74.6%] |
| max_api_count (500-call cap) | 2,080 (1,410 / 670) | 82.0% | 81.2% | 80.5% | 80.0% | 77.7% [74.0%–85.0%] |
| unsupported API | 9,016 (4,844 / 4,172) | 73.9% | 77.7% | 76.2% | 21.2% | 45.2% [43.9%–47.7%] |
| invalid memory / CPU fault | 1,062 (580 / 482) | 79.0% | 58.3% | 80.9% | 51.4% | 87.6% [87.6%–87.6%] |
| emulator internal error | 161 (74 / 87) | 9.5% | 27.0% | 21.6% | 31.1% | 37.8% [37.8%–37.8%] |

#### 5d. By stop reason: share of benign flagged (FPR)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded | 5,083 (2,491 / 2,592) | 1.3% | 0.9% | 1.1% | 1.9% | 2.2% [2.2%–2.2%] |
| max_api_count (500-call cap) | 2,080 (1,410 / 670) | 0.9% | 0.3% | 1.0% | 0.1% | 0.4% [0.4%–0.4%] |
| unsupported API | 9,016 (4,844 / 4,172) | 0.8% | 1.0% | 0.9% | 0.7% | 0.4% [0.4%–0.5%] |
| invalid memory / CPU fault | 1,062 (580 / 482) | 0.6% | 1.5% | 1.2% | 0.2% | 0.4% [0.4%–0.4%] |
| emulator internal error | 161 (74 / 87) | 3.4% | 5.7% | 1.1% | 1.1% | 0.0% [0.0%–0.0%] |

#### 5e. By stop reason: AUC inside the cell

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded | 5,083 (2,491 / 2,592) | 0.9395 | 0.9571 | 0.9313 | 0.9291 | 0.9563 [0.9560–0.9567] |
| max_api_count (500-call cap) | 2,080 (1,410 / 670) | 0.9671 | 0.9533 | 0.9673 | 0.9025 | 0.9327 [0.9317–0.9335] |
| unsupported API | 9,016 (4,844 / 4,172) | 0.9689 | 0.9675 | 0.9767 | 0.9292 | 0.9585 [0.9563–0.9603] |
| invalid memory / CPU fault | 1,062 (580 / 482) | 0.9854 | 0.9844 | 0.9806 | 0.9678 | 0.9782 [0.9776–0.9786] |
| emulator internal error | 161 (74 / 87) | 0.8978 | 0.8729 | 0.8660 | 0.9390 | 0.8974 [0.8955–0.8990] |

#### 5f. By seen / unseen: TPR at 1% FPR (malware in the cell)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| seen in January | 6,329 (2,914 / 3,415) | 82.1% | 87.5% | 83.0% | 65.7% | 77.3% [74.4%–82.9%] |
| unseen | 11,073 (6,485 / 4,588) | 71.8% | 68.9% | 72.6% | 27.9% | 52.1% [51.0%–53.8%] |

#### 5g. By seen / unseen: share of benign flagged (FPR)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| seen in January | 6,329 (2,914 / 3,415) | 0.7% | 1.1% | 0.8% | 0.7% | 1.2% [1.1%–1.2%] |
| unseen | 11,073 (6,485 / 4,588) | 1.2% | 0.9% | 1.2% | 1.2% | 0.9% [0.9%–0.9%] |

#### 5h. By seen / unseen: AUC inside the cell

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| seen in January | 6,329 (2,914 / 3,415) | 0.9865 | 0.9909 | 0.9883 | 0.9645 | 0.9756 [0.9748–0.9763] |
| unseen | 11,073 (6,485 / 4,588) | 0.9371 | 0.9392 | 0.9386 | 0.8784 | 0.9379 [0.9357–0.9402] |

#### 5i. By family: TPR at 1% FPR

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| backdoor | 1,940 (1,940 / 0) | 82.9% | 80.0% | 82.2% | 76.2% | 78.0% [75.3%–83.2%] |
| coinminer | 1,684 (1,684 / 0) | 81.9% | 66.3% | 79.5% | 9.3% | 58.7% [58.1%–59.7%] |
| dropper | 252 (252 / 0) | 73.4% | 77.4% | 71.8% | 68.7% | 56.1% [50.8%–66.3%] |
| keylogger | 1,041 (1,041 / 0) | 52.2% | 88.1% | 64.4% | 13.5% | 17.4% [17.3%–17.5%] |
| ransomware | 2,139 (2,139 / 0) | 66.8% | 60.4% | 66.5% | 40.7% | 46.9% [44.1%–52.5%] |
| rat | 1,258 (1,258 / 0) | 85.5% | 84.8% | 83.9% | 14.3% | 79.2% [79.1%–79.3%] |
| trojan | 1,085 (1,085 / 0) | 76.2% | 80.9% | 79.8% | 66.9% | 74.5% [72.7%–77.7%] |

#### 5j. By family: AUC (family vs all 8,003 April benign)

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| backdoor vs all benign | 9,943 (1,940 / 8,003) | 0.9577 | 0.9678 | 0.9604 | 0.9378 | 0.9461 [0.9452–0.9468] |
| coinminer vs all benign | 9,687 (1,684 / 8,003) | 0.9726 | 0.9691 | 0.9684 | 0.9155 | 0.9415 [0.9360–0.9446] |
| dropper vs all benign | 8,255 (252 / 8,003) | 0.9458 | 0.9678 | 0.9398 | 0.9418 | 0.9586 [0.9559–0.9610] |
| keylogger vs all benign | 9,044 (1,041 / 8,003) | 0.9640 | 0.9861 | 0.9787 | 0.8209 | 0.9201 [0.9191–0.9211] |
| ransomware vs all benign | 10,142 (2,139 / 8,003) | 0.9298 | 0.9464 | 0.9195 | 0.8983 | 0.9442 [0.9419–0.9465] |
| rat vs all benign | 9,261 (1,258 / 8,003) | 0.9842 | 0.9756 | 0.9864 | 0.9408 | 0.9843 [0.9843–0.9843] |
| trojan vs all benign | 9,088 (1,085 / 8,003) | 0.9634 | 0.9473 | 0.9731 | 0.9546 | 0.9719 [0.9718–0.9720] |

#### 5k. Stop reason × seen/unseen: TPR at 1% FPR

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded / seen in January | 2,409 (1,245 / 1,164) | 87.0% | 89.3% | 86.3% | 50.4% | 78.0% [75.3%–82.9%] |
| no error recorded / unseen | 2,674 (1,246 / 1,428) | 61.1% | 51.4% | 59.7% | 50.1% | 67.4% [66.4%–69.3%] |
| max_api_count (500-call cap) / seen in January | 1,460 (1,161 / 299) | 95.4% | 94.8% | 93.8% | 93.1% | 90.0% [85.5%–98.8%] |
| max_api_count (500-call cap) / unseen | 620 (249 / 371) | 19.3% | 17.7% | 18.5% | 18.9% | 20.5% [20.5%–20.5%] |
| unsupported API / seen in January | 1,694 (216 / 1,478) | 9.7% | 38.9% | 26.4% | 0.9% | 0.9% [0.9%–0.9%] |
| unsupported API / unseen | 7,322 (4,628 / 2,694) | 76.9% | 79.5% | 78.5% | 22.1% | 47.3% [45.9%–49.8%] |
| invalid memory / CPU fault / seen in January | 709 (268 / 441) | 67.2% | 90.3% | 71.3% | 72.0% | 78.7% [78.7%–78.7%] |
| invalid memory / CPU fault / unseen | 353 (312 / 41) | 89.1% | 30.8% | 89.1% | 33.7% | 95.2% [95.2%–95.2%] |
| emulator internal error / seen in January | 57 (24 / 33) | 4.2% | 50.0% | 33.3% | 50.0% | 100.0% [100.0%–100.0%] |
| emulator internal error / unseen | 104 (50 / 54) | 12.0% | 16.0% | 16.0% | 22.0% | 8.0% [8.0%–8.0%] |

#### 5l. Stop reason × seen/unseen: share of benign flagged

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded / seen in January | 2,409 (1,245 / 1,164) | 1.1% | 1.1% | 0.9% | 1.9% | 3.0% [3.0%–3.1%] |
| no error recorded / unseen | 2,674 (1,246 / 1,428) | 1.4% | 0.8% | 1.3% | 1.8% | 1.5% [1.5%–1.5%] |
| max_api_count (500-call cap) / seen in January | 1,460 (1,161 / 299) | 0.3% | 0.0% | 1.0% | 0.0% | 1.0% [1.0%–1.0%] |
| max_api_count (500-call cap) / unseen | 620 (249 / 371) | 1.3% | 0.5% | 1.1% | 0.3% | 0.0% [0.0%–0.0%] |
| unsupported API / seen in January | 1,694 (216 / 1,478) | 0.4% | 1.0% | 0.6% | 0.0% | 0.0% [0.0%–0.0%] |
| unsupported API / unseen | 7,322 (4,628 / 2,694) | 1.1% | 1.0% | 1.1% | 1.1% | 0.7% [0.6%–0.7%] |
| invalid memory / CPU fault / seen in January | 709 (268 / 441) | 0.5% | 1.6% | 0.7% | 0.2% | 0.2% [0.2%–0.2%] |
| invalid memory / CPU fault / unseen | 353 (312 / 41) | 2.4% | 0.0% | 7.3% | 0.0% | 2.4% [2.4%–2.4%] |
| emulator internal error / seen in January | 57 (24 / 33) | 3.0% | 6.1% | 3.0% | 0.0% | 0.0% [0.0%–0.0%] |
| emulator internal error / unseen | 104 (50 / 54) | 3.7% | 5.6% | 0.0% | 1.9% | 0.0% [0.0%–0.0%] |

#### 5m. Stop reason × seen/unseen: AUC

| cell | reports (malware / benign) | released Nebula | finetune_k8 | frozen_k1 | LR `lr_api_bigram` | LightGBM `lgbm_api_bigram` |
|---|---|---|---|---|---|---|
| no error recorded / seen in January | 2,409 (1,245 / 1,164) | 0.9904 | 0.9903 | 0.9920 | 0.9477 | 0.9665 [0.9646–0.9702] |
| no error recorded / unseen | 2,674 (1,246 / 1,428) | 0.8754 | 0.9063 | 0.8605 | 0.9111 | 0.9452 [0.9411–0.9494] |
| max_api_count (500-call cap) / seen in January | 1,460 (1,161 / 299) | 0.9975 | 0.9977 | 0.9966 | 0.9993 | 0.9983 [0.9983–0.9983] |
| max_api_count (500-call cap) / unseen | 620 (249 / 371) | 0.8500 | 0.7598 | 0.8238 | 0.3657 | 0.4241 [0.4203–0.4281] |
| unsupported API / seen in January | 1,694 (216 / 1,478) | 0.9278 | 0.9743 | 0.9446 | 0.8595 | 0.8934 [0.8924–0.8948] |
| unsupported API / unseen | 7,322 (4,628 / 2,694) | 0.9674 | 0.9611 | 0.9754 | 0.9240 | 0.9593 [0.9588–0.9597] |
| invalid memory / CPU fault / seen in January | 709 (268 / 441) | 0.9887 | 0.9937 | 0.9793 | 0.9574 | 0.9698 [0.9691–0.9712] |
| invalid memory / CPU fault / unseen | 353 (312 / 41) | 0.9569 | 0.9392 | 0.9570 | 0.8702 | 0.9834 [0.9827–0.9838] |
| emulator internal error / seen in January | 57 (24 / 33) | 0.9609 | 0.9583 | 0.9545 | 0.9848 | 1.0000 [1.0000–1.0000] |
| emulator internal error / unseen | 104 (50 / 54) | 0.8444 | 0.8111 | 0.8000 | 0.9019 | 0.8386 [0.8374–0.8404] |

#### 5n. Reference: the same baselines on January validation, by stop reason

Threshold from the January-validation benign scores. Released Nebula is not shown: it was probably trained on these January reports.

| model | stop reason | reports (malware / benign) | TPR at 1% FPR | AUC |
|---|---|---|---|---|
| lr_api_bigram | no error recorded | 3,401 (2,842 / 559) | 84.5% | 0.9817 |
| lr_api_bigram | max_api_count (500-call cap) | 976 (812 / 164) | 74.1% | 0.9868 |
| lr_api_bigram | unsupported API | 28 (0 / 28) | n<30 | n<30 |
| lr_api_bigram | invalid memory / CPU fault | 5,178 (3,833 / 1,345) | 27.2% | 0.9634 |
| lr_api_bigram | emulator internal error | 36 (29 / 7) | 0.0% | — |
| lgbm_api_bigram | no error recorded | 3,401 (2,842 / 559) | 66.8% [66.8%–66.9%] | 0.9803 [0.9778–0.9818] |
| lgbm_api_bigram | max_api_count (500-call cap) | 976 (812 / 164) | 93.7% [93.5%–93.8%] | 0.9944 [0.9932–0.9955] |
| lgbm_api_bigram | unsupported API | 28 (0 / 28) | n<30 | n<30 |
| lgbm_api_bigram | invalid memory / CPU fault | 5,178 (3,833 / 1,345) | 87.5% [87.5%–87.6%] | 0.9757 [0.9753–0.9762] |
| lgbm_api_bigram | emulator internal error | 36 (29 / 7) | 0.0% [0.0%–0.0%] | — |
