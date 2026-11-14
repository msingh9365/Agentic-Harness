### 6. Do data-flow links separate the classes?

Link = REPORT.md §8 definition (merged API list, address-like return value ≥ 0x10000 reused as a later argument; producer = first call that returned it). Link features: number of links, links per call, cross-chunk links, links leaving chunk 0, maximum link distance (calls), maximum chunk distance, and counts of the 20 most common producer→user pairs (API names without DLL, lower-case) in the January training side. LightGBM as in analysis 1, seeds 0/1/2.

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

| model | AUC | TPR @1% FPR | TPR @0.1% FPR | val AUC |
|---|---|---|---|---|
| LightGBM, links only | 0.7504 [0.7446–0.7584] | 8.0% [5.7%–9.3%] (756/9,399; FP 6/12/24) | 4.8% [0.1%–9.2%] (452/9,399; FP 6/7/0) | 0.7792 [0.7678–0.7870] |
| LightGBM, length only | 0.7107 [0.6981–0.7228] | 5.0% [4.2%–5.5%] (468/9,399; FP 39/38/39) | 4.7% [3.9%–5.1%] (440/9,399; FP 1/1/1) | 0.7251 [0.7177–0.7309] |
| LightGBM, length + links | 0.8064 [0.8025–0.8084] | 10.5% [7.3%–12.8%] (986/9,399; FP 59/50/15) | 0.0% [0.0%–0.1%] (2/9,399; FP 2/0/0) | 0.8034 [0.7876–0.8220] |
| LightGBM, bag of API names | 0.9486 [0.9445–0.9519] | 49.5% [44.3%–57.1%] (4,650/9,399; FP 80/76/80) | 31.1% [28.0%–34.6%] (2,919/9,399; FP 8/8/5) | 0.9758 [0.9689–0.9830] |
| LightGBM, API names + links | 0.9367 [0.9335–0.9415] | 46.9% [46.5%–47.3%] (4,408/9,399; FP 80/70/60) | 33.9% [33.0%–35.2%] (3,183/9,399; FP 8/8/8) | 0.9616 [0.9581–0.9636] |
| LightGBM, API names + bigrams | 0.9504 [0.9490–0.9515] | 59.9% [58.3%–62.8%] (5,632/9,399; FP 80/80/80) | 30.2% [29.3%–31.5%] (2,839/9,399; FP 3/4/4) | 0.9808 [0.9788–0.9820] |
| LightGBM, API names + bigrams + links | 0.9398 [0.9347–0.9438] | 47.0% [45.4%–49.5%] (4,421/9,399; FP 64/67/75) | 35.7% [34.6%–36.5%] (3,359/9,399; FP 8/8/7) | 0.9632 [0.9604–0.9668] |

#### 6d. Paired bootstrap of the difference (mean score over the 3 seeds, 1,000 resamples)

| comparison | metric | difference | 95% interval |
|---|---|---|---|
| length + links − length only | AUC | +0.1069 | [+0.0994, +0.1140] |
| length + links − length only | TPR @1% FPR | +4.4 pp | [+3.7 pp, +5.2 pp] |
| length + links − length only | TPR @0.1% FPR | -1.1 pp | [-5.3 pp, +5.2 pp] |
| API names + links − bag of API names | AUC | -0.0129 | [-0.0141, -0.0117] |
| API names + links − bag of API names | TPR @1% FPR | -10.4 pp | [-18.6 pp, +3.6 pp] |
| API names + links − bag of API names | TPR @0.1% FPR | -1.1 pp | [-1.7 pp, +6.6 pp] |
| API names + bigrams + links − API names + bigrams | AUC | -0.0097 | [-0.0110, -0.0084] |
| API names + bigrams + links − API names + bigrams | TPR @1% FPR | -12.3 pp | [-17.0 pp, -8.6 pp] |
| API names + bigrams + links − API names + bigrams | TPR @0.1% FPR | +7.8 pp | [-0.6 pp, +8.3 pp] |

#### 6e. TPR at 1% FPR per family

| model | backdoor (n=1,940) | coinminer (n=1,684) | dropper (n=252) | keylogger (n=1,041) | ransomware (n=2,139) | rat (n=1,258) | trojan (n=1,085) |
|---|---|---|---|---|---|---|---|
| LightGBM, links only | 13.1% [13.0%–13.1%] | 6.6% [5.5%–7.8%] | 11.9% [4.0%–24.6%] | 0.4% [0.1%–0.8%] | 0.0% [0.0%–0.1%] | 13.2% [0.8%–19.7%] | 17.5% [14.4%–22.9%] |
| LightGBM, length only | 22.7% [19.1%–24.6%] | 0.1% [0.0%–0.1%] | 0.4% [0.4%–0.4%] | 0.7% [0.3%–1.4%] | 0.5% [0.5%–0.5%] | 0.2% [0.1%–0.3%] | 0.5% [0.5%–0.5%] |
| LightGBM, length + links | 28.9% [16.8%–41.8%] | 6.6% [5.5%–7.9%] | 8.3% [0.0%–21.0%] | 0.7% [0.1%–1.3%] | 0.4% [0.0%–0.6%] | 13.5% [1.0%–20.3%] | 9.8% [0.8%–23.8%] |
| LightGBM, bag of API names | 79.6% [75.7%–81.8%] | 30.8% [16.7%–58.1%] | 49.2% [48.0%–50.8%] | 13.2% [10.3%–16.9%] | 47.3% [33.9%–55.0%] | 47.8% [31.2%–78.9%] | 65.6% [60.9%–72.9%] |
| LightGBM, API names + links | 83.3% [83.0%–83.7%] | 17.5% [17.2%–18.1%] | 48.1% [47.6%–48.4%] | 10.6% [10.0%–11.7%] | 54.9% [54.7%–55.1%] | 32.8% [31.9%–33.4%] | 62.5% [61.2%–63.2%] |
| LightGBM, API names + bigrams | 78.0% [75.3%–83.2%] | 58.7% [58.1%–59.7%] | 56.1% [50.8%–66.3%] | 17.4% [17.3%–17.5%] | 46.9% [44.1%–52.5%] | 79.2% [79.1%–79.3%] | 74.5% [72.7%–77.7%] |
| LightGBM, API names + bigrams + links | 74.6% [74.2%–74.9%] | 20.8% [20.4%–21.3%] | 48.1% [47.6%–49.2%] | 12.3% [11.8%–12.9%] | 57.6% [53.6%–63.9%] | 33.7% [32.2%–34.6%] | 66.0% [63.1%–71.6%] |
