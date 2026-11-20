# Why ATT+bal misses a cluster of April coinminer reports that v2-PE catches

Analysis only: no model was trained, no report was edited or executed, no reported result changes. Code: `baseline/coinminer.py`; all numbers are in `coinminer.json`. April scores: `results/review/attack/a3pad_{v2_pe,attbal}.npz` (row 0, unedited), thresholds = 1% FPR of each model's unedited April benign scores, per seed. The cluster was defined after looking at April scores (as in the question), so this is a post-hoc description, not a test.

## Findings in plain English

1. **The "cluster" is one input.** Of the 266 reports, 265 have the same API-name sequence (`hash_apis` d91b96b4…) and **identical first 512 tokens**, so every model gives them exactly the same score within a seed. The 266th report (another hash, 2,042 tokens) starts the same way. It is one input counted 265 times, and it makes up 15.8% of the 1,684 April coinminer reports but only 2 of their 110 distinct sequences.
2. **The sequence is new.** No January training report has this hash. The closest January reports are 9 or more edits away (normalised distance 0.051) and are trojans, backdoors and benign reports; only 1 coinminer lies within distance 0.1 of it. For the coinminers that both models do detect, the median distance to the nearest January report is 0.005, and 82% have a January coinminer within 0.1.
3. **What it is.** A report of 175 calls: 163 `GetProcAddress`, 9 `LoadLibraryA` (the first call and eight between calls 120 and 151), and, at the very end (calls 172 to 174), 2 `VirtualProtect` and 1 `CreateFileA`. The first 512 tokens hold only the first 99 calls (98 of them `GetProcAddress`); **the last 76 calls, including the `VirtualProtect` and `CreateFileA` calls, are outside the window that both models read.** The call names alone do not set it apart: 29% of the detected coinminer sequences also have windows that are at least 90% `GetProcAddress`. What differs is *what is resolved*: it resolves 98 different functions (process, thread, file and system-information functions such as `OpenProcess`, `CreateProcessA`, `TerminateThread`, `GetSystemTimes`, `GetComputerNameExA`).
4. **ATT+bal's miss is a near miss, not a blind spot.** Its logit for the cluster is a median 2.8 below the threshold (IQR −4.8 to −1.4, never more than 10 below, flagged in 1 seed of 10). At the cluster's own score 3.7% of April benign reports score at least as high, so ATT+bal would catch it at about 3.7% FPR instead of 1%. v2-PE is above the threshold by a median 9.2 and flags it in 8 of 10 seeds; its two missing seeds are also just below.
5. **Attention does not ignore it.** ATT+bal's attention is almost uniform over about 435 to 493 of the 511 tokens (uniform weight 0.002; the largest weight is 0.005 to 0.007), for the cluster as for a detected coinminer (375 to 460 effective tokens). The extra weight goes to the tokens that name the resolved functions (for example `writeconsolew`, `interlockedincrement`), not to the header or to the call names.
6. **The padding link is not supported by these checks.** All call names of the window occur in the TRAIN padding pool, and `GetProcAddress` is the second most likely padding call (8.4% of padded calls), but the same holds for the detected coinminers. In January, windows that are at least 90% `GetProcAddress` are overwhelmingly malware (93.5%), so "GetProcAddress run" is not a benign signal in training. The data do not show that ATT+bal learned to ignore this variant as padding.
7. **The coinminer gap is this cluster.** Report-level coinminer TPR@1%: v2-PE 0.817, ATT+bal 0.728 (gap +8.9 points). Counting each `hash_apis` group once: 0.444 against 0.411 (gap +3.4 points, within the seed spread of 5.6). Without the cluster: 0.821 against 0.846 (gap −2.6 points, ATT+bal ahead). Both models detect only about 41 to 44% of the 110 distinct coinminer sequences at 1% FPR.

## Step 1. The cluster and its neighbours in January

| item | value |
|---|---|
| reports in the cluster (coinminer, detected by v2-PE in ≥ 8/10 seeds, by ATT+bal in ≤ 2/10) | 266 |
| hash_apis groups in it | 265 × `d91b96b4…`, 1 × `4b3ad5f6…` |
| April reports with the main hash | 265 (all coinminer) |
| January reports with the same hash | 0 |
| tokens of the full report | 939 in `meta.csv`, 935 with our BPE-50k; the other group 2,042 |
| nearest January reports (normalised edit distance on API names) | 0.051 trojan (9 edits), 0.057 backdoor, 0.063 trojan, 0.063 clean, 0.063 clean |
| January reports within distance ≤ 0.05 / 0.1 / 0.2 | 0 / 116 / 5,078 |
| the 116 within 0.1, by family | clean 45, backdoor 30, trojan 28, ransomware 8, rat 2, coinminer 1, dropper 1, keylogger 1 |
| reference: 38 other groups of coinminers detected by both models, distance to the nearest January report | median 0.005 (IQR 0.00 to 0.035); 82% have a January coinminer within 0.1 |

## Step 2. The calls in the first 512 tokens

| | cluster | coinminer groups detected by both models (38 groups, one report each) |
|---|---|---|
| calls fully inside the window (of 175 calls in the report) | 99 | median 99.5 (IQR 82 to 102) |
| distinct API names in the window | 2 | median 17 (IQR 3 to 29) |
| share of the most common name | 0.99 | median 0.36 (IQR 0.27 to 0.96) |
| longest run of the same name | 98 | median 32 (IQR 14 to 69) |
| groups with ≥ 90% of one name | — | 29% (11 of 38) |
| top names | GetProcAddress 98, LoadLibraryA 1 | GetProcAddress 1,493, InitializeCriticalSectionEx 274, InitializeCriticalSectionAndSpinCount 174, HeapAlloc 93, EnterCriticalSection 79, LeaveCriticalSection 73 (summed over the 38 windows) |

First calls of the cluster report (names only): `LoadLibraryA`, then `GetProcAddress` × 59 in the first 60 positions; the whole report is 163 `GetProcAddress`, 9 `LoadLibraryA` (positions 0 and 120 to 151), `VirtualProtect` at 172 and 173 and `CreateFileA` at 174. The detected coinminer used as the example in `coinminer.json` (median length) has the same shape (`LoadLibraryA`, then `GetProcAddress` × 101). The 98 function names that the cluster resolves begin: `SetHandleInformation, WaitForSingleObject, SetEvent, GetTickCount, GetProcessHeap, WriteFile, GetSystemTimes, GetDriveTypeA, GetProcessTimes, OpenProcess, GlobalAlloc, WideCharToMultiByte, TerminateThread, InitializeCriticalSectionAndSpinCount, Sleep, CreateEventA, LeaveCriticalSection, GetComputerNameExA, CreateProcessA, TerminateProcess, FileTimeToSystemTime, ReadFile, GetModuleFileNameW, CreateFileW, MultiByteToWideChar` (all lower case in the report). Overlap of this list with the resolved names of other `GetProcAddress`-dominated windows (Jaccard, median): January benign 0.25 (630 windows), January coinminers 0.34 (1,103), detected April coinminers 0.28 (11): the cluster resembles none of them closely, and is slightly closer to coinminers than to benign reports.

## Step 3. Scores against the threshold (all 10 seeds; the 266 reports have identical scores within a seed)

| | v2-PE | ATT+bal |
|---|---|---|
| threshold, mean (range over seeds) | 5.6 (1.1 to 15.8) | 4.3 (2.6 to 5.5) |
| cluster logit, percentiles 5 / 25 / 50 / 75 / 95 | 2.5 / 4.7 / 20.0 / 23.7 / 29.8 | −3.0 / −0.7 / 1.6 / 2.7 / 5.0 |
| margin (logit − threshold), percentiles 5 / 25 / 50 / 75 / 95 | −1.4 / 0.8 / 9.2 / 19.9 / 23.7 | −8.5 / −4.8 / −2.8 / −1.4 / +0.1 |
| share of report-seed pairs flagged | 80% | 10% |
| share within 2 below the threshold / more than 10 below | 20% / 0% | 20% / 0% |
| share of April benign reports scoring at least as high as the cluster's median report | 0.5% | 3.7% |
| April benign logit, median / 99th percentile | −16.1 / 7.9 | −9.5 / 4.4 |

`fig1_logits_vs_threshold.png`: histogram of the margin; each spike is one seed (the reports are identical).

## Step 4. Attention weights of ATT+bal (seeds 0 to 2; cluster reports 1 to 3 and one detected coinminer)

| report, seed | weight on the report header | weight on GetProcAddress calls | largest weight (uniform = 0.002) | effective tokens (1 / Σα²) | top tokens |
|---|---|---|---|---|---|
| cluster (the three reports are identical), seed 0 | 0.021 | 0.971 | 0.005 | 493 | `writeconsolew`, `interlockedincrement`, `interlockeddecrement` |
| cluster, seed 1 | 0.018 | 0.974 | 0.007 | 451 | `writeconsolew`, `createdirectorya`, `createfilew` |
| cluster, seed 2 | 0.027 | 0.965 | 0.005 | 435 | `0xfeee0021`, `drive` (header), `createdirectorya` |
| detected coinminer, seed 0 | 0.001 | 0.991 | 0.004 | 461 | `loadresource`, `getprofilestringa`, `lcmapstringa` |
| detected coinminer, seed 1 | 0.001 | 0.992 | 0.006 | 450 | `findresourcea`, `lockresource`, `createfilea` |
| detected coinminer, seed 2 | 0.001 | 0.989 | 0.007 | 375 | `flushfilebuffers`, `ects`, `filetimetolocalfiletime` |

The weights are spread over almost the whole window in all cases; the cluster puts about 2% on the header (the detected coinminer 0.1%). `fig2_attention.png`: α against token position (dotted line = uniform weight).

## Step 5. Link to the TRAIN padding pool (benign reports of the 90% slice: 22,201 reports)

| | cluster window | coinminers detected by both models (38 groups) | January windows ≥ 90% GetProcAddress |
|---|---|---|---|
| share of window call names that occur in the pool | 100% | 100% | — |
| mean log10 of the pool frequency of the window's call names | −1.03 | −1.71 (IQR −1.81 to −1.07) | — |
| mean padding-draw probability of the window's calls | 0.083 | 0.053 (IQR 0.022 to 0.083) | — |
| number of windows | 1 | 38 | 9,668 (12.8% of January): 630 benign (6.5%), 9,038 malware (ransomware 4,364, backdoor 1,854, dropper 1,369, coinminer 1,103, trojan 240, rat 77, keylogger 31) |

`GetProcAddress`: 9.8% of the pool's calls; probability that a padding call (uniform pool report, then uniform call) is `GetProcAddress` 8.4%, rank 2 of 2,401 names. `LoadLibraryA`: 0.16% and 0.43%. So the cluster is made of a very common padding call, but the detected coinminers also consist of pool names and 29% of their sequences share the structure; and in training, windows dominated by `GetProcAddress` are labelled malware 93.5% of the time.

## Step 6. Coinminer TPR@1% FPR counting each hash_apis group once

| | v2-PE | ATT+bal | gap v2-PE − ATT+bal (mean ± std over seeds, points) |
|---|---|---|---|
| per report (1,684 reports) | 0.817 ± 0.068 | 0.728 ± 0.062 | +8.9 ± 9.6 |
| one vote per hash_apis group (110 groups; vote = share of the group's reports flagged) | 0.444 ± 0.031 | 0.411 ± 0.039 | +3.4 ± 5.6 |
| per report without the 266 cluster reports (1,418 reports) | 0.821 ± 0.024 | 0.846 ± 0.030 | −2.6 ± 3.9 |

## Limits

- The cluster was selected from April scores, so the findings are descriptive; with 10 seeds the "detected in ≥ 8 / ≤ 2 seeds" split is itself noisy (v2-PE's threshold ranges from 1.1 to 15.8 over seeds).
- Attention was inspected for 3 seeds and 4 reports (the three cluster reports are identical); attention weights show where the pooled vector draws from, not why the logit is low.
- Step 5 tests the padding hypothesis at the level of call names; the resolved function names (arguments) were compared only by overlap, and no causal test (for example removing or editing calls) was run.
- Sequence distances use API names only, not arguments.
- Both models read only the first 512 tokens, so the end of the cluster report (`VirtualProtect`, `CreateFileA`) is invisible to them; no experiment here shows what v2-PE or ATT+bal would do if they saw it.
