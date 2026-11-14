### 6. Do data-flow links separate the classes?

Link = REPORT.md §8 definition (merged API list, address-like return value ≥ 0x10000 reused as a later argument; producer = first call that returned it). Link features: number of links, links per call, cross-chunk links, links leaving chunk 0, maximum link distance (calls), maximum chunk distance, and counts of the 20 most common producer→user pairs (API names without DLL, lower-case) in the January training side. LightGBM as in analysis 1 (early stopping on group-weighted validation log-loss), seeds 0/1/2.

#### 6a. Top 20 producer→user pairs (January train side)

| pair | links |
|---|---|
| loadlibrarya>getprocaddress | 1,132,658 |
| getmodulehandlea>getprocaddress | 428,474 |
| getmodulehandlew>getprocaddress | 284,976 |
| loadlibraryexw>getprocaddress | 174,483 |
| getmodulehandlew>loadstringw | 134,890 |
| getmodulehandlea>loadstringa | 80,388 |
| charnexta>charnexta | 67,476 |
| getprocaddress>encodepointer | 40,168 |
| heapalloc>heapfree | 20,967 |
| getprocaddress>decodepointer | 19,547 |
| encodepointer>decodepointer | 18,551 |
| charnextw>charnextw | 13,239 |
| getprocaddress>tlssetvalue | 10,077 |
| getdc>getdevicecaps | 10,019 |
| heapalloc>_lread | 8,991 |
| getdc>releasedc | 7,752 |
| virtualalloc>virtualfree | 7,699 |
| getmodulehandlea>getmodulefilenamea | 5,536 |
| getdc>getsystempaletteentries | 5,222 |
| getmodulehandlea>createwindowexa | 4,941 |

#### 6b. Link features by class (January train side)

| feature | malware median [p25–p75] | benign median [p25–p75] | AUC of the feature alone (Jan train) |
|---|---|---|---|
| n_links | 23.00 [2.00–87.00] | 9.00 [1.00–21.00] | 0.6349 |
| links_per_call | 0.09 [0.02–0.46] | 0.04 [0.02–0.15] | 0.5894 |
| n_cross_chunk_links | 0.00 [0.00–12.00] | 1.00 [0.00–3.00] | 0.4755 |
| max_link_distance_calls | 33.00 [4.00–114.00] | 103.00 [1.00–168.00] | 0.4300 |

#### 6c. Models (April test set)

| model | AUC | TPR @1% FPR | TPR @0.1% FPR | val AUC (group-weighted) |
|---|---|---|---|---|
| LightGBM, links only | 0.7755 [0.7687–0.7790] | 31.1% [29.7%–32.2%] (2,923/9,399; FP 78/80/80) | 24.0% [21.7%–25.2%] (2,253/9,399; FP 6/6/7) | 0.8414 [0.8409–0.8419] |
| LightGBM, length only | 0.7574 [0.7529–0.7611] | 24.3% [24.2%–24.4%] (2,288/9,399; FP 80/80/80) | 11.5% [9.7%–14.8%] (1,083/9,399; FP 5/5/5) | 0.8245 [0.8233–0.8257] |
| LightGBM, length + links | 0.8171 [0.8084–0.8276] | 31.4% [29.0%–34.2%] (2,950/9,399; FP 80/80/66) | 19.7% [16.9%–21.7%] (1,850/9,399; FP 8/6/8) | 0.9126 [0.9108–0.9136] |
| LightGBM, bag of API names | 0.9501 [0.9482–0.9520] | 62.9% [62.0%–63.9%] (5,916/9,399; FP 80/80/80) | 31.6% [29.2%–32.9%] (2,967/9,399; FP 5/7/7) | 0.9662 [0.9658–0.9666] |
| LightGBM, API names + links | 0.9404 [0.9345–0.9457] | 59.3% [58.9%–59.6%] (5,573/9,399; FP 80/80/80) | 34.4% [34.1%–34.7%] (3,236/9,399; FP 7/7/7) | 0.9668 [0.9656–0.9677] |
| LightGBM, API names + bigrams | 0.9502 [0.9483–0.9521] | 61.9% [61.3%–62.8%] (5,816/9,399; FP 79/79/80) | 35.0% [32.5%–36.5%] (3,292/9,399; FP 4/4/4) | 0.9679 [0.9673–0.9690] |
| LightGBM, API names + bigrams + links | 0.9454 [0.9435–0.9488] | 61.2% [61.0%–61.5%] (5,751/9,399; FP 80/80/76) | 35.0% [34.7%–35.4%] (3,287/9,399; FP 4/6/4) | 0.9688 [0.9685–0.9692] |

#### 6d. Paired bootstrap of the difference (mean score over the 3 seeds, 1,000 resamples)

| comparison | metric | difference | 95% interval |
|---|---|---|---|
| length + links − length only | AUC | +0.0605 | [+0.0543, +0.0668] |
| length + links − length only | TPR @1% FPR | +7.1 pp | [+1.1 pp, +8.5 pp] |
| length + links − length only | TPR @0.1% FPR | +6.2 pp | [+2.1 pp, +7.2 pp] |
| API names + links − bag of API names | AUC | -0.0091 | [-0.0101, -0.0082] |
| API names + links − bag of API names | TPR @1% FPR | -2.8 pp | [-13.7 pp, -1.5 pp] |
| API names + links − bag of API names | TPR @0.1% FPR | +5.0 pp | [+0.7 pp, +5.5 pp] |
| API names + bigrams + links − API names + bigrams | AUC | -0.0055 | [-0.0062, -0.0049] |
| API names + bigrams + links − API names + bigrams | TPR @1% FPR | -1.8 pp | [-2.4 pp, +1.3 pp] |
| API names + bigrams + links − API names + bigrams | TPR @0.1% FPR | -0.7 pp | [-1.9 pp, +2.7 pp] |

#### 6e. TPR at 1% FPR per family

| model | backdoor (n=1,940) | coinminer (n=1,684) | dropper (n=252) | keylogger (n=1,041) | ransomware (n=2,139) | rat (n=1,258) | trojan (n=1,085) |
|---|---|---|---|---|---|---|---|
| LightGBM, links only | 72.7% [72.5%–72.9%] | 19.2% [18.2%–19.9%] | 47.0% [46.8%–47.2%] | 6.4% [6.4%–6.4%] | 19.9% [13.8%–24.0%] | 22.9% [22.8%–23.0%] | 26.6% [26.3%–27.2%] |
| LightGBM, length only | 53.6% [53.6%–53.7%] | 7.5% [7.5%–7.5%] | 4.6% [4.4%–5.2%] | 3.7% [3.0%–4.4%] | 32.7% [32.7%–32.7%] | 10.9% [10.9%–10.9%] | 21.7% [21.6%–21.9%] |
| LightGBM, length + links | 65.2% [63.4%–66.3%] | 18.4% [17.6%–19.0%] | 46.4% [45.2%–47.6%] | 5.8% [5.8%–5.9%] | 20.7% [13.8%–24.8%] | 24.5% [21.5%–30.4%] | 41.4% [32.0%–57.2%] |
| LightGBM, bag of API names | 82.7% [82.6%–82.8%] | 55.7% [54.2%–57.8%] | 51.5% [51.2%–52.0%] | 17.2% [16.9%–17.3%] | 59.9% [56.1%–65.8%] | 78.4% [78.2%–78.5%] | 73.4% [73.3%–73.6%] |
| LightGBM, API names + links | 82.1% [82.1%–82.1%] | 39.4% [38.3%–40.6%] | 52.6% [50.8%–53.6%] | 17.2% [16.8%–17.4%] | 56.9% [56.2%–58.0%] | 79.9% [79.2%–80.4%] | 72.2% [71.7%–72.9%] |
| LightGBM, API names + bigrams | 77.6% [73.6%–83.5%] | 57.1% [56.2%–59.0%] | 51.6% [51.2%–52.0%] | 17.0% [16.8%–17.3%] | 58.4% [58.3%–58.4%] | 79.0% [77.9%–80.1%] | 73.6% [73.5%–73.7%] |
| LightGBM, API names + bigrams + links | 81.1% [81.0%–81.1%] | 39.2% [38.8%–40.0%] | 51.6% [50.8%–53.2%] | 17.1% [17.0%–17.2%] | 67.0% [66.5%–67.6%] | 79.7% [79.3%–80.5%] | 71.3% [70.8%–71.9%] |
