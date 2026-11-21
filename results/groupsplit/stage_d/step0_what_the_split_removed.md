### Step 0: what the split removed (April reports: 17,402; distinct API-name sequences: April 2,489, January 6,738; exact normalised edit distance, nearest January report; descriptive)

New split: training 66,580 / validation 8,718 reports, a distinct sequence is in exactly one part. Old split: training 67,768 / validation 7,530; 1149 distinct January sequences occur in BOTH old parts. Largest validation group: group id 57, 1,056 reports (1 distinct sequences). Shares in %.

**A. Exact twins and nearest neighbours (new split)**

| family | April n | exact hash twin in January | exact twin ONLY in new validation | nearest neighbour in new validation | nearest in new training | tie | nearest within 0.05 (any January) | within 0.05 of new training | near-twin lost (within 0.05 of January, not of new training) | median nearest distance (January) | median distance to new training |
|---|---|---|---|---|---|---|---|---|---|---|---|
| backdoor | 1940 | 72.2 | 10.4 | 14.8 | 84.7 | 0.5 | 91.5 | 91.2 | 0.4 | 0.000 | 0.000 |
| clean | 7944 | 42.3 | 3.4 | 17.4 | 78.4 | 4.1 | 61.9 | 59.6 | 2.3 | 0.011 | 0.022 |
| coinminer | 1684 | 17.1 | 5.6 | 10.9 | 88.8 | 0.4 | 74.5 | 72.3 | 2.3 | 0.004 | 0.019 |
| dropper | 252 | 60.3 | 4.4 | 9.1 | 90.5 | 0.4 | 73.0 | 68.7 | 4.4 | 0.000 | 0.000 |
| keylogger **(highlight)** | 1041 | 16.6 | 0.0 | 1.7 | 97.9 | 0.4 | 25.1 | 25.1 | 0.0 | 0.176 | 0.176 |
| ransomware | 2139 | 12.0 | 2.7 | 39.7 | 55.8 | 4.5 | 44.3 | 43.7 | 0.6 | 0.099 | 0.099 |
| rat **(highlight)** | 1258 | 27.6 | 0.0 | 14.1 | 85.7 | 0.2 | 96.5 | 96.5 | 0.0 | 0.027 | 0.027 |
| trojan **(highlight)** | 1085 | 27.4 | 1.5 | 40.7 | 58.6 | 0.6 | 63.8 | 62.4 | 1.4 | 0.032 | 0.040 |
| windows_syswow64 | 59 | 89.8 | 18.6 | 20.3 | 78.0 | 1.7 | 93.2 | 74.6 | 18.6 | 0.000 | 0.000 |

**B. The same for the old split**

| family | exact twin only in old validation | only in old training | in both old parts | nearest neighbour only in old validation | nearest in both old parts (or tie) | within 0.05 of old training | near-twin lost | median distance to old training |
|---|---|---|---|---|---|---|---|---|
| backdoor | 0.0 | 5.5 | 66.8 | 0.2 | 81.6 | 91.5 | 0.0 | 0.000 |
| clean | 1.4 | 24.7 | 16.2 | 3.7 | 34.1 | 60.5 | 1.4 | 0.014 |
| coinminer | 0.0 | 2.9 | 14.2 | 2.1 | 36.0 | 74.5 | 0.0 | 0.006 |
| dropper | 0.0 | 6.7 | 53.6 | 0.0 | 67.1 | 73.0 | 0.0 | 0.000 |
| keylogger | 0.2 | 2.8 | 13.6 | 1.3 | 88.8 | 24.9 | 0.2 | 0.176 |
| ransomware | 0.0 | 1.7 | 10.2 | 8.8 | 40.4 | 44.2 | 0.1 | 0.106 |
| rat | 0.0 | 6.8 | 20.8 | 1.4 | 76.7 | 96.5 | 0.0 | 0.027 |
| trojan | 0.4 | 9.6 | 17.4 | 0.6 | 63.8 | 63.2 | 0.6 | 0.032 |
| windows_syswow64 | 0.0 | 28.8 | 61.0 | 0.0 | 66.1 | 93.2 | 0.0 | 0.000 |

**C. The largest validation group (group 57: 1,056 January reports, 1 distinct sequences)**

| family | April n | exact twin in the group (%) | nearest neighbour in the group (%) | within 0.05 of the group (%) | reports with exact twin | reports with nearest neighbour in the group |
|---|---|---|---|---|---|---|
| backdoor | 1940 | 0.0 | 0.8 | 0.8 | 0 | 16 |
| clean | 7944 | 0.0 | 0.0 | 0.0 | 0 | 3 |
| coinminer | 1684 | 0.0 | 0.1 | 0.1 | 0 | 1 |
| dropper | 252 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| keylogger | 1041 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| ransomware | 2139 | 0.0 | 0.3 | 0.3 | 0 | 6 |
| rat | 1258 | 0.0 | 10.5 | 10.4 | 0 | 132 |
| trojan | 1085 | 0.0 | 17.2 | 17.3 | 0 | 187 |
| windows_syswow64 | 59 | 0.0 | 0.0 | 0.0 | 0 | 0 |

**D. Next to the drop in detection rate at the 1% FPR threshold (new vs old models; Stage C; thresholds on April benign scores; points; descriptive only)**

| malware family | April n | nearest neighbour in new validation (%) | exact twin only in new validation (%) | near-twin lost (%) | detection drop v2-PE (points) | detection drop ATT+bal (points) |
|---|---|---|---|---|---|---|
| backdoor | 1940 | 14.8 | 10.4 | 0.4 | -2.1 | -5.8 |
| coinminer | 1684 | 10.9 | 5.6 | 2.3 | -5.1 | -11.2 |
| dropper | 252 | 9.1 | 4.4 | 4.4 | -6.4 | -3.2 |
| keylogger **(highlight)** | 1041 | 1.7 | 0.0 | 0.0 | -16.8 | -23.6 |
| ransomware | 2139 | 39.7 | 2.7 | 0.6 | -2.6 | -11.2 |
| rat **(highlight)** | 1258 | 14.1 | 0.0 | 0.0 | -12.7 | -17.9 |
| trojan **(highlight)** | 1085 | 40.7 | 1.5 | 1.4 | -19.3 | -17.9 |

Spearman rank correlation across the 7 malware families (n = 7, descriptive only, no test; negative = the larger the share, the larger the drop): nn in new validation vs v2pe: +0.11; nn in new validation vs attbal: -0.07; exact twin only in new validation vs v2pe: +0.77; exact twin only in new validation vs attbal: +0.83; lost new vs v2pe: +0.13; lost new vs attbal: +0.61.
