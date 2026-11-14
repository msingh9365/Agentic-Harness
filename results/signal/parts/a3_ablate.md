### 3. Ablations of released Nebula (inference only)

Each change is applied to Nebula's filtered report, which is then tokenized and cut to 512 tokens as usual. Thresholds come from the benign scores of the changed reports; `crossed` uses the unmodified model's 1% FPR threshold and counts reports on the other side after the change (either direction). Metrics rank reports by Nebula's logit: the changed reports push hundreds of benign scores to exactly 1.0 in float32 (last column), and with the probability the 1% threshold would sit on that tie. Scores files hold logits; `mean |Δscore|` is on the probability scale. sigmoid(logit) of the unmodified reports reproduces `nebula_score_chunk0.npy` (max |diff| in the log). Removing arguments or return values deletes the key from every call (the key names are stopwords, so they produce no tokens either way).

#### 3a. Placeholder for hex values (chosen on January validation)

Candidates must be one known token (not `<unk>`, id 1) and not a hex value. Among them, the one that changes January-validation scores least under the address replacement is used: **`heap`**.

| candidate | pieces | ids | single known token | mean |Δscore| on Jan val (addr_ph) | Jan val AUC |
|---|---|---|---|---|---|
| addr | ▁addr | [38884] | True | 0.2930 | 0.7786 |
| value | ▁value | [29992] | True | 0.4212 | 0.7756 |
| mem | ▁mem | [543] | True | 0.3867 | 0.7899 |
| heap | ▁heap | [110] | True | 0.1755 | 0.8192 |
| ptr | ▁p tr | [357, 64] | False | — | — |
| handle | ▁ handle | [49966, 212] | False | — | — |
| buf | ▁ buf | [49966, 7721] | False | — | — |
| data | ▁data | [28198] | True | 0.3573 | 0.7457 |
| hex | ▁he x | [3383, 49967] | False | — | — |
| unk | ▁un k | [1760, 49981] | False | — | — |

#### 3b. Results

| set | change | AUC | TPR @1% FPR | TPR @0.1% FPR | ΔAUC | ΔTPR @1% | ΔTPR @0.1% | crossed the 1% threshold | mean \|Δscore\| | benign at p = 1.0 (float32) |
|---|---|---|---|---|---|---|---|---|---|---|
| April test | none (unmodified) | 0.9586 | 75.0% (7,047/9,399) | 51.8% (4,873) |  |  |  |  |  | 5 |
| April test | shuffle API call order (3 seeds) | 0.7139 [0.7109–0.7158] | 12.1% [11.8%–12.3%] (1,136) | 7.0% [6.6%–7.4%] (661) | -0.2448 [-0.2477–-0.2429] | -62.9 pp [-63.2 pp–-62.7 pp] | -44.8 pp [-45.2 pp–-44.5 pp] | 31.8% [31.6%–32.1%] (3,763 malware lost, 1,216 benign gained) | 0.334 [0.331–0.337] | 41 [31–53] |
| April test | remove all arguments | 0.7537 | 9.9% (933) | 8.1% (762) | -0.2049 | -65.0 pp | -43.7 pp | 28.8% (4,439 malware lost, 279 benign gained) | 0.281 | 5 |
| April test | remove return values | 0.9070 | 43.6% (4,095) | 24.6% (2,316) | -0.0517 | -31.4 pp | -27.2 pp | 15.7% (1,695 malware lost, 167 benign gained) | 0.185 | 7 |
| April test | address-like hex (≥ 0x10000) → placeholder | 0.6236 | 15.7% (1,472) | 6.3% (594) | -0.3351 | -59.3 pp | -45.5 pp | 33.4% (923 malware lost, 4,069 benign gained) | 0.370 | 25 |
| April test | all hex values → placeholder | 0.7672 | 2.4% (230) | 0.1% (10) | -0.1914 | -72.5 pp | -51.7 pp | 24.9% (2,169 malware lost, 1,398 benign gained) | 0.266 | 365 |
| April test | remove file, registry, network fields | 0.9543 | 73.0% (6,859) | 46.5% (4,374) | -0.0044 | -2.0 pp | -5.3 pp | 3.4% (354 malware lost, 9 benign gained) | 0.030 | 5 |
| April test | API names only | 0.6226 | 2.2% (204) | 2.1% (198) | -0.3361 | -72.8 pp | -49.7 pp | 35.1% (5,055 malware lost, 599 benign gained) | 0.358 | 198 |
| January validation | none (unmodified) | 0.9984 | 98.9% (7,437/7,516) | 78.9% (5,933) |  |  |  |  |  | 1 |
| January validation | shuffle API call order (3 seeds) | 0.8120 [0.8092–0.8148] | 33.1% [32.1%–33.9%] (2,488) | 24.1% [22.5%–26.5%] (1,813) | -0.1865 [-0.1892–-0.1836] | -65.9 pp [-66.9 pp–-65.1 pp] | -54.8 pp [-56.4 pp–-52.5 pp] | 32.5% [32.3%–32.7%] (2,739 malware lost, 367 benign gained) | 0.291 [0.288–0.294] | 4 [3–5] |
| January validation | remove all arguments | 0.8839 | 29.8% (2,238) | 19.5% (1,466) | -0.1145 | -69.2 pp | -59.4 pp | 29.4% (2,546 malware lost, 242 benign gained) | 0.223 | 4 |
| January validation | remove return values | 0.9446 | 61.2% (4,603) | 41.2% (3,096) | -0.0538 | -37.7 pp | -37.7 pp | 24.8% (2,325 malware lost, 38 benign gained) | 0.190 | 1 |
| January validation | address-like hex (≥ 0x10000) → placeholder | 0.8192 | 37.8% (2,841) | 26.5% (1,995) | -0.1792 | -61.1 pp | -52.4 pp | 19.0% (1,118 malware lost, 677 benign gained) | 0.175 | 9 |
| January validation | all hex values → placeholder | 0.7552 | 23.4% (1,756) | 5.9% (445) | -0.2433 | -75.6 pp | -73.0 pp | 34.0% (2,948 malware lost, 304 benign gained) | 0.350 | 29 |
| January validation | remove file, registry, network fields | 0.9845 | 92.3% (6,935) | 65.9% (4,952) | -0.0139 | -6.7 pp | -13.1 pp | 5.4% (508 malware lost, 4 benign gained) | 0.053 | 0 |
| January validation | API names only | 0.5561 | 18.0% (1,355) | 7.6% (568) | -0.4424 | -80.9 pp | -71.4 pp | 60.0% (5,311 malware lost, 432 benign gained) | 0.599 | 19 |

#### 3c. TPR at 1% FPR per family (April)

| model | backdoor (n=1,940) | coinminer (n=1,684) | dropper (n=252) | keylogger (n=1,041) | ransomware (n=2,139) | rat (n=1,258) | trojan (n=1,085) |
|---|---|---|---|---|---|---|---|
| none (unmodified) | 82.9% | 81.9% | 73.4% | 52.2% | 66.8% | 85.5% | 76.2% |
| shuffle API call order | 8.5% [7.4%–9.6%] | 3.5% [2.8%–4.1%] | 33.7% [32.9%–34.9%] | 2.4% [2.3%–2.7%] | 29.7% [29.2%–30.2%] | 2.0% [1.7%–2.1%] | 13.0% [12.4%–13.9%] |
| remove all arguments | 9.7% | 1.5% | 29.0% | 1.2% | 20.7% | 0.4% | 17.1% |
| remove return values | 60.4% | 30.6% | 56.7% | 29.3% | 52.1% | 26.9% | 46.9% |
| address-like hex (≥ 0x10000) → placeholder | 15.0% | 4.5% | 53.6% | 1.4% | 29.3% | 0.3% | 29.9% |
| all hex values → placeholder | 0.4% | 1.9% | 7.5% | 0.7% | 1.0% | 0.4% | 12.7% |
| remove file, registry, network fields | 70.9% | 81.9% | 73.4% | 54.9% | 67.8% | 86.0% | 75.2% |
| API names only | 0.4% | 1.5% | 24.6% | 1.3% | 1.1% | 0.2% | 6.4% |
