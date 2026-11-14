### 1. Simple baselines vs Nebula (April test set)

Features from Nebula's filtered reports. Bag of API names: 633 names, bigrams: 2,772 (both kept if seen in ≥ 20 January-train reports); field counts: 11 columns (records per field and per event type). LR: L2, `liblinear`, TF-IDF (sublinear tf) on the bag features, standardised dense features; C from {0.01, 0.1, 1, 10, 100} by group-weighted validation AUC. LightGBM: raw counts, fixed parameters, early stopping (100 rounds) on group-weighted validation log-loss, seeds 0/1/2: mean [min–max]. *Group-weighted*: each API-name sequence of the validation side counts once in total (weight 1 / group size), because one sequence covers 2,292 of the 9,619 validation reports. TPR thresholds come from the 8,003 April benign scores of each model; the 0.1% FPR threshold rests on 8 benign reports. FP = benign reports above the threshold (one number per seed). Fewer than 80 / 8 means ties at the threshold: a bag model gives every report with the same API names the same score.

Why group-weighted: with plain validation AUC, one run (API names + bigrams, seed 2) stopped after 1 tree (log `signal_baselines_auc_early_stop.log`). With plain validation log-loss, the prefix models of analysis 2 stopped after 16–48 trees: the 2,292-report group gets an uncertain score on short prefixes and its loss alone rises after ~20 trees, while the group-weighted loss keeps falling to ~500 trees (checked on January validation only; logs `signal_baselines_plain_logloss.log`, `signal_prefix_plain_logloss.log`). All LightGBM and LR choices in this study use the group-weighted validation metrics.

| model | AUC | TPR @1% FPR | TPR @0.1% FPR | seeds | val AUC (group-weighted) |
|---|---|---|---|---|---|
| released Nebula | 0.9586 | 75.0% (7,047/9,399; FP 80) | 51.7% (4,860/9,399; FP 7) | 1 (existing scores) | — |
| finetune_k8 | 0.9639 | 74.7% (7,018/9,399; FP 80) | 54.3% (5,101/9,399; FP 8) | 1 (existing scores) | — |
| frozen_k1 | 0.9590 | 75.8% (7,129/9,399; FP 80) | 47.8% (4,493/9,399; FP 8) | 1 (existing scores) | — |
| LR, length only | 0.6018 | 4.5% (424/9,399; FP 78) | 4.4% (417/9,399; FP 8) | deterministic (C=1) | 0.6793 |
| LightGBM, length only | 0.7574 [0.7529–0.7611] | 24.3% [24.2%–24.4%] (2,288/9,399; FP 80/80/80) | 11.5% [9.7%–14.8%] (1,083/9,399; FP 5/5/5) | 3 (iters 230, 169, 189) | 0.8245 [0.8233–0.8257] |
| LR, bag of API names | 0.8778 | 27.1% (2,550/9,399; FP 79) | 13.6% (1,277/9,399; FP 8) | deterministic (C=10) | 0.9259 |
| LightGBM, bag of API names | 0.9501 [0.9482–0.9520] | 62.9% [62.0%–63.9%] (5,916/9,399; FP 80/80/80) | 31.6% [29.2%–32.9%] (2,967/9,399; FP 5/7/7) | 3 (iters 604, 590, 569) | 0.9662 [0.9658–0.9666] |
| LR, API names + bigrams | 0.9252 | 39.6% (3,718/9,399; FP 80) | 29.2% (2,743/9,399; FP 8) | deterministic (C=10) | 0.9476 |
| LightGBM, API names + bigrams | 0.9502 [0.9483–0.9521] | 61.9% [61.3%–62.8%] (5,816/9,399; FP 79/79/80) | 35.0% [32.5%–36.5%] (3,292/9,399; FP 4/4/4) | 3 (iters 521, 520, 528) | 0.9679 [0.9673–0.9690] |
| LR, API names + field counts | 0.8775 | 30.7% (2,887/9,399; FP 80) | 13.0% (1,219/9,399; FP 8) | deterministic (C=10) | 0.9228 |
| LightGBM, API names + field counts | 0.9503 [0.9484–0.9512] | 58.2% [54.3%–60.4%] (5,468/9,399; FP 79/79/80) | 31.0% [29.2%–33.7%] (2,916/9,399; FP 7/7/6) | 3 (iters 509, 600, 685) | 0.9669 [0.9660–0.9676] |

Best on group-weighted January validation AUC: LR = `lr_api_bigram`, LightGBM = `lgbm_api_bigram`.

#### 1b. TPR at 1% FPR per family (April)

| model | backdoor (n=1,940) | coinminer (n=1,684) | dropper (n=252) | keylogger (n=1,041) | ransomware (n=2,139) | rat (n=1,258) | trojan (n=1,085) |
|---|---|---|---|---|---|---|---|
| released Nebula | 82.9% | 81.9% | 73.4% | 52.2% | 66.8% | 85.5% | 76.2% |
| finetune_k8 | 80.0% | 66.3% | 77.4% | 88.1% | 60.4% | 84.8% | 80.9% |
| frozen_k1 | 82.2% | 79.5% | 71.8% | 64.4% | 66.5% | 83.9% | 79.8% |
| LR, length only | 0.1% | 0.1% | 0.0% | 0.1% | 19.5% | 0.1% | 0.2% |
| LightGBM, length only | 53.6% [53.6%–53.7%] | 7.5% [7.5%–7.5%] | 4.6% [4.4%–5.2%] | 3.7% [3.0%–4.4%] | 32.7% [32.7%–32.7%] | 10.9% [10.9%–10.9%] | 21.7% [21.6%–21.9%] |
| LR, bag of API names | 51.3% | 18.4% | 57.5% | 8.2% | 23.7% | 0.6% | 46.2% |
| LightGBM, bag of API names | 82.7% [82.6%–82.8%] | 55.7% [54.2%–57.8%] | 51.5% [51.2%–52.0%] | 17.2% [16.9%–17.3%] | 59.9% [56.1%–65.8%] | 78.4% [78.2%–78.5%] | 73.4% [73.3%–73.6%] |
| LR, API names + bigrams | 77.2% | 24.8% | 62.7% | 13.3% | 29.0% | 12.5% | 67.4% |
| LightGBM, API names + bigrams | 77.6% [73.6%–83.5%] | 57.1% [56.2%–59.0%] | 51.6% [51.2%–52.0%] | 17.0% [16.8%–17.3%] | 58.4% [58.3%–58.4%] | 79.0% [77.9%–80.1%] | 73.6% [73.5%–73.7%] |
| LR, API names + field counts | 52.1% | 18.5% | 58.7% | 5.7% | 24.9% | 10.9% | 63.5% |
| LightGBM, API names + field counts | 82.6% [82.5%–82.7%] | 41.0% [39.4%–42.2%] | 51.3% [50.8%–52.4%] | 17.1% [16.8%–17.3%] | 50.5% [35.2%–58.8%] | 78.7% [78.5%–78.9%] | 73.4% [73.0%–73.6%] |

#### 1c. Released Nebula minus best LightGBM (`lgbm_api_bigram`, mean of 3 seeds), paired bootstrap

| metric | difference | 95% interval |
|---|---|---|
| AUC | +0.0082 | [+0.0054, +0.0109] |
| TPR @1% FPR | +11.7 pp | [+10.0 pp, +15.9 pp] |
| TPR @0.1% FPR | +16.4 pp | [-35.7 pp, +25.8 pp] |

#### 1d. Top 15 LightGBM features by gain (API names + bigrams, seed 0)

| feature | gain share |
|---|---|
| queryperformancecounter>isprocessorfeaturepresent | 43.4% |
| getprocaddress>getprocaddress | 12.0% |
| heapalloc>multibytetowidechar | 3.9% |
| getprocaddress | 3.9% |
| loadlibraryexw | 3.4% |
| loadlibraryexw>getprocaddress | 3.4% |
| getmodulehandlea | 1.9% |
| getsystemtimeasfiletime | 1.5% |
| initializecriticalsection | 1.4% |
| getprocaddress>getsysteminfo | 1.3% |
| sleep | 1.2% |
| getcurrentthreadid | 1.2% |
| __set_app_type>setunhandledexceptionfilter | 1.1% |
| registerclassexa | 1.1% |
| setlasterror>getlasterror | 1.1% |

(gain share is relative to the top 40 features.)
