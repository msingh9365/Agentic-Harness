### 2. Prefix curve: how many API calls are needed?

#### 2a. How many API calls fit in Nebula's first 512 tokens (measured on the tokenized reports)

`calls fully inside 512` counts calls whose last token is at position < 512; `calls starting inside 512` counts calls whose first token is. For reports ≤ 512 tokens every call fits.

| reports | calls fully inside 512: median [p25–p75] | calls starting inside 512: median [p25–p75] | tokens before the API list: median [p25–p75] | tokens per call (median) |
|---|---|---|---|---|
| all reports (n=92,700) | 82 [25–97] | 83 [25–98] | 1 [1–8] | 5.41 |
| reports > 512 tokens (n=61,207) | 92 [82–100] | 93 [83–101] | 1 [1–11] | 5.34 |
| reports > 512 tokens, January (n=50,164) | 92 [83–100] | 93 [83–101] | 1 [1–11] | 5.30 |
| reports > 512 tokens, April (n=11,043) | 94 [81–100] | 95 [82–101] | 1 [1–1] | 5.41 |

#### 2b. Detection against the number of API calls kept (April; 6,857 reports have > 200 calls)

Only the `apis` list is cut to its first K calls; file, registry and network fields are kept. LightGBM is trained on January prefixes of the same length and early-stopped on the group-weighted validation log-loss (seeds 0/1/2). Released Nebula is only re-scored. Thresholds: from the April benign scores of all April reports at the same K (also for the > 200-call subset). Nebula is ranked by its logit (scores files hold logits). The last column is the same LightGBM on the January validation side (all reports): there, more calls always help.

| model | subset | K (calls) | AUC | TPR @1% FPR | TPR @0.1% FPR | malware caught @1% | Jan val AUC (group-weighted) |
|---|---|---|---|---|---|---|---|
| LightGBM API names + bigrams | all April (malware n=9,399) | 10 | 0.9048 [0.8981–0.9082] | 24.9% [22.3%–27.5%] | 16.1% [13.5%–18.7%] | 2,337 | 0.9013 [0.8947–0.9139] |
| LightGBM API names + bigrams | all April (malware n=9,399) | 25 | 0.9097 [0.9086–0.9109] | 28.1% [23.9%–33.3%] | 14.7% [13.3%–16.9%] | 2,637 | 0.8972 [0.8956–0.8988] |
| LightGBM API names + bigrams | all April (malware n=9,399) | 50 | 0.8910 [0.8908–0.8913] | 28.7% [28.7%–28.8%] | 18.9% [18.8%–19.0%] | 2,700 | 0.9271 [0.9259–0.9281] |
| LightGBM API names + bigrams | all April (malware n=9,399) | 100 | 0.9056 [0.9052–0.9063] | 21.1% [21.0%–21.2%] | 21.1% [21.0%–21.2%] | 1,984 | 0.9392 [0.9384–0.9401] |
| LightGBM API names + bigrams | all April (malware n=9,399) | 200 | 0.9028 [0.9014–0.9053] | 13.1% [12.8%–13.3%] | 13.1% [12.8%–13.3%] | 1,227 | 0.9550 [0.9543–0.9556] |
| LightGBM API names + bigrams | all April (malware n=9,399) | 500 | 0.9498 [0.9485–0.9505] | 63.7% [62.7%–65.3%] | 34.9% [34.2%–35.3%] | 5,990 | 0.9686 [0.9684–0.9690] |
| LightGBM API names + bigrams | all April (malware n=9,399) | all | 0.9502 [0.9483–0.9521] | 61.9% [61.3%–62.8%] | 35.0% [32.5%–36.5%] | 5,816 | 0.9679 [0.9673–0.9690] |
| LightGBM API names + bigrams | > 200 calls (malware n=4,312) | 10 | 0.8614 [0.8477–0.8686] | 32.9% [29.5%–35.7%] | 18.2% [14.8%–21.0%] | 1,418 | — |
| LightGBM API names + bigrams | > 200 calls (malware n=4,312) | 25 | 0.8699 [0.8694–0.8706] | 34.3% [31.2%–35.9%] | 17.5% [15.0%–21.0%] | 1,480 | — |
| LightGBM API names + bigrams | > 200 calls (malware n=4,312) | 50 | 0.8037 [0.8037–0.8038] | 36.0% [36.0%–36.0%] | 21.2% [21.2%–21.2%] | 1,553 | — |
| LightGBM API names + bigrams | > 200 calls (malware n=4,312) | 100 | 0.8020 [0.8009–0.8041] | 22.6% [22.6%–22.6%] | 22.6% [22.6%–22.6%] | 976 | — |
| LightGBM API names + bigrams | > 200 calls (malware n=4,312) | 200 | 0.8543 [0.8540–0.8544] | 15.9% [15.6%–16.2%] | 15.9% [15.6%–16.2%] | 685 | — |
| LightGBM API names + bigrams | > 200 calls (malware n=4,312) | 500 | 0.9552 [0.9533–0.9575] | 76.7% [75.9%–77.3%] | 47.1% [46.9%–47.2%] | 3,306 | — |
| LightGBM API names + bigrams | > 200 calls (malware n=4,312) | all | 0.9565 [0.9556–0.9572] | 73.2% [71.8%–75.1%] | 45.1% [41.3%–47.4%] | 3,158 | — |
| released Nebula | all April (malware n=9,399) | 10 | 0.8706 | 32.9% | 17.6% | 3,092 | — |
| released Nebula | all April (malware n=9,399) | 25 | 0.9094 | 45.7% | 19.8% | 4,296 | — |
| released Nebula | all April (malware n=9,399) | 50 | 0.9464 | 61.6% | 25.2% | 5,788 | — |
| released Nebula | all April (malware n=9,399) | 100 | 0.9528 | 74.4% | 51.3% | 6,996 | — |
| released Nebula | all April (malware n=9,399) | 200 | 0.9586 | 75.0% | 51.8% | 7,047 | — |
| released Nebula | all April (malware n=9,399) | 500 | 0.9586 | 75.0% | 51.8% | 7,047 | — |
| released Nebula | all April (malware n=9,399) | all | 0.9586 | 75.0% | 51.8% | 7,047 | — |
| released Nebula | > 200 calls (malware n=4,312) | 10 | 0.8592 | 26.1% | 13.5% | 1,125 | — |
| released Nebula | > 200 calls (malware n=4,312) | 25 | 0.8948 | 33.9% | 14.3% | 1,463 | — |
| released Nebula | > 200 calls (malware n=4,312) | 50 | 0.9461 | 61.9% | 19.5% | 2,667 | — |
| released Nebula | > 200 calls (malware n=4,312) | 100 | 0.9341 | 84.6% | 57.5% | 3,650 | — |
| released Nebula | > 200 calls (malware n=4,312) | 200 | 0.9479 | 85.7% | 58.7% | 3,696 | — |
| released Nebula | > 200 calls (malware n=4,312) | 500 | 0.9479 | 85.7% | 58.7% | 3,696 | — |
| released Nebula | > 200 calls (malware n=4,312) | all | 0.9479 | 85.7% | 58.7% | 3,696 | — |

![prefix curve](plots/prefix_curve.png)
