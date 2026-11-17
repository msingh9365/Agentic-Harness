# Robustness checks on existing checkpoints (round 3, CPU part)

No training. Models: the **released Nebula** weights, **A (J)** (flatten pooling, 512 tokens, trained on all of January for 1 epoch) and **C (J)** (mean pooling + fixed position encoding, 512 tokens, 10 epochs), 10 seeds each (regime J of `results/pooling_v2`); item 4 uses regime S (train side only). April test set (17,402 reports, 9,399 malware), thresholds fixed at 1% FPR on the unedited April scores of each model (a), group-bootstrap intervals over April `hash_apis` (1,000 resamples).

## Verdict

1. **The released Nebula is as position-brittle as the retrained A (item 1).** Twenty calls copied from the same report and put in front of it cut malware detection at the fixed threshold from 75.0% to 35.7% (−39.3 points [−51.3, −26.1]) and raise the benign false-positive rate from 1.0% to 20.9%. A falls by 43.7 points [−54.8, −30.7] (FPR 8.5%); C (J) by 2.4 [−5.0, −0.3] (FPR 1.2%). A − released is within noise for most edits (prepend 20: −4.4 [−10.7, +3.1]).
2. **For the released model most of that loss is original calls being pushed out of the 512-token window.** On reports where no original call leaves the window its change is small (prepend 20: −6.8 [−20.2, +4.0]; insert 50: +4.2 [−2.1, +13.4]), while A still loses 12.8 points [−19.5, −5.7] (prepend 20) and 13.0 [−24.8, −3.4] (insert 50); C loses at most 3.1 points. So A depends on token positions even without truncation; the released model much less so.
3. **Padding with calls from benign reports (item 2) defeats every model, and C's advantage disappears.** Prepending 20 benign calls: released 75.0% → 12.1%, A 71.9% → 19.5%, C 73.8% → 42.6%; prepending 50: 16.0%, 16.0%, 0.6%. On malware where no original call leaves the window C is *worse* than A (insert 5: 71.1% → 39.7% against 66.0% → 49.5%; seed-paired C − A −14.9 points [−18.1, −11.4]). C's robustness in the previous round is robustness to edits that keep the report's own call mix, not to dilution with benign content.
4. **C's low-FPR weakness (item 3):** its highest-scoring benign reports are short, generic start-up sequences (all 1 chunk, median 13 calls, only 11 distinct sequences among 20; 8 of 20 sequences also occur in malware). The released model's list is more varied and includes long reports (5 of 3 chunks, up to 279 calls). Three reports are in both lists; Spearman correlation of the two benign score rankings 0.66.
5. **Why C beats B (item 4) is not token order inside calls.** Shuffling the tokens inside each call leaves A, B and C unchanged (AUC +0.000, −0.000, +0.002), and shuffling all 512 tokens even raises B (+0.011) and C (+0.006) while A collapses (−0.25). B and C act as bags of tokens; the fixed position encoding helps them by something other than order.

## Item 1: graded edits on the released weights, next to A (J) and C (J)

Insert k / prepend k (k = 1, 5, 20, 50) API calls, each a copy of a call of the same report, first 512 tokens (the tokens of `results/pooling_v2/graded_edits.md`). "TPR after": malware caught at the threshold that gave 1% FPR on the unedited April benign scores of that model; "benign FPR after": benign reports flagged at that threshold after the same edit. "Fits in 512": only reports whose whole edited sequence is at most 512 tokens (no original call leaves the window); change in TPR on those reports, in points. A (J), C (J): mean of 10 seeds.

| edit | TPR after: released | A (J) | C (J) | benign FPR after: released | A (J) | C (J) | fits in 512: change in TPR, released | A (J) | C (J) |
|---|---|---|---|---|---|---|---|---|---|
| original | 75.0% | 71.9% | 73.8% | 1.00% | 1.00% | 1.00% | — | — | — |
| insert 1 | 73.6% | 70.6% | 72.8% | 1.09% | 1.07% | 0.98% | -1.8 [-5.0, +1.7] | -1.6 [-2.4, -0.5] | -1.5 [-2.6, -0.4] |
| insert 5 | 69.3% | 65.4% | 71.4% | 1.04% | 1.14% | 0.99% | -5.4 [-15.0, +5.4] | -7.4 [-13.1, -1.7] | -1.6 [-2.8, -0.3] |
| insert 20 | 57.5% | 49.1% | 70.5% | 1.72% | 1.57% | 1.06% | +1.2 [-7.3, +9.6] | -11.3 [-17.6, -3.8] | -1.0 [-3.3, +1.7] |
| insert 50 | 49.2% | 38.2% | 72.1% | 2.87% | 2.07% | 1.10% | +4.2 [-2.1, +13.4] | -13.0 [-24.8, -3.4] | -0.4 [-2.0, +1.1] |
| prepend 1 | 69.6% | 66.3% | 71.1% | 1.09% | 1.17% | 0.93% | -5.0 [-12.0, +2.8] | -4.7 [-6.5, -1.7] | -3.1 [-4.8, -1.1] |
| prepend 5 | 53.7% | 43.4% | 69.8% | 2.06% | 1.56% | 1.89% | -8.7 [-23.8, +6.9] | -14.6 [-28.0, -2.3] | -3.1 [-4.6, -1.5] |
| prepend 20 | 35.7% | 28.2% | 71.3% | 20.89% | 8.54% | 1.16% | -6.8 [-20.2, +4.0] | -12.8 [-19.5, -5.7] | -1.8 [-4.0, +0.6] |
| prepend 50 | 38.0% | 21.2% | 68.4% | 19.41% | 8.51% | 1.05% | +2.4 [-4.4, +10.7] | -16.9 [-28.9, -7.1] | -0.3 [-1.9, +1.0] |

Change in malware TPR with group-bootstrap intervals, all reports (restricted case and AUC in `graded_edits.md`):

| edit | released: change in TPR, points [group 95%] | A (J) | C (J) | A − released | C − released | C − A |
|---|---|---|---|---|---|---|
| insert 1 | -1.4 [-2.8, -0.3] | -1.3 [-2.1, -0.6] | -1.0 [-1.5, -0.5] | +0.0 [-1.1, +1.3] | +0.4 [-0.6, +1.6] | +0.4 [-0.4, +1.1] |
| insert 5 | -5.7 [-10.4, -1.5] | -6.5 [-10.0, -3.0] | -2.4 [-3.7, -1.1] | -0.8 [-2.9, +1.3] | +3.3 [-0.3, +7.2] | +4.1 [+0.8, +7.2] |
| insert 20 | -17.5 [-32.0, -5.5] | -22.8 [-32.6, -12.3] | -3.3 [-5.4, -1.2] | -5.3 [-11.0, +1.4] | +14.2 [+3.6, +27.5] | +19.5 [+9.6, +28.0] |
| insert 50 | -25.7 [-40.5, -12.6] | -33.7 [-45.5, -20.5] | -1.6 [-4.0, +0.3] | -7.9 [-14.2, -1.9] | +24.1 [+11.0, +38.8] | +32.0 [+19.5, +43.4] |
| prepend 1 | -5.4 [-8.9, -1.9] | -5.6 [-9.0, -2.4] | -2.7 [-3.8, -1.5] | -0.2 [-3.0, +3.0] | +2.7 [-0.5, +5.7] | +2.9 [-0.4, +5.8] |
| prepend 5 | -21.3 [-35.8, -7.0] | -28.5 [-38.3, -16.3] | -4.0 [-7.0, -1.3] | -7.2 [-14.4, +0.5] | +17.3 [+4.8, +29.5] | +24.5 [+13.1, +33.0] |
| prepend 20 | -39.3 [-51.3, -26.1] | -43.7 [-54.8, -30.7] | -2.4 [-5.0, -0.3] | -4.4 [-10.7, +3.1] | +36.9 [+22.2, +49.3] | +41.3 [+27.8, +52.9] |
| prepend 50 | -36.9 [-47.8, -25.5] | -50.7 [-61.9, -35.8] | -5.3 [-8.5, -2.4] | -13.8 [-22.9, -2.5] | +31.6 [+20.3, +43.1] | +45.4 [+31.5, +56.2] |

## Item 2: malware padded with calls from benign January reports (robustness measurement)

Only the 9,399 malware April reports are edited (benign April reports unchanged, so the benign FPR is 1% by construction). Each added call is a random call of a random benign January report (pool of 2,000 reports); k = 1, 5, 20, 50; inserted at random places or prepended. Nothing is optimised: random padding, fixed k, aggregate numbers only; the edits are made in memory and not saved. "Fits": whole edited sequence at most 512 tokens (no original call leaves the window).

| edit | all malware: released TPR before → after | A (J) | C (J) | malware that fits: change, points [group 95%]: released | A (J) | C (J) | C − A on malware that fits, seed-paired |
|---|---|---|---|---|---|---|---|
| insert 1 | 75.0% → 72.8% | 71.9% → 69.9% | 73.8% → 70.2% | -3.6 [-6.4, -1.1] | -3.8 [-6.8, -1.4] | -8.6 [-14.2, -4.4] | -4.9 [-6.6, -2.9] |
| insert 5 | 75.0% → 66.1% | 71.9% → 61.4% | 73.8% → 60.4% | -12.4 [-19.2, -5.7] | -16.5 [-22.7, -11.2] | -31.4 [-49.2, -18.3] | -14.9 [-18.1, -11.4] |
| insert 20 | 75.0% → 46.4% | 71.9% → 38.0% | 73.8% → 48.6% | -41.3 [-53.2, -25.2] | -50.8 [-65.1, -31.1] | -55.1 [-72.8, -39.6] | -4.3 [-10.0, +0.4] |
| insert 50 | 75.0% → 35.9% | 71.9% → 29.7% | 73.8% → 34.8% | -52.6 [-72.4, -25.8] | -59.0 [-75.1, -36.2] | -70.6 [-84.3, -50.8] | -11.5 [-15.1, -7.7] |
| prepend 1 | 75.0% → 68.1% | 71.9% → 64.6% | 73.8% → 67.6% | -4.7 [-8.8, -0.2] | -5.9 [-9.2, -3.0] | -11.9 [-19.3, -6.2] | -6.0 [-8.8, -2.6] |
| prepend 5 | 75.0% → 43.8% | 71.9% → 35.8% | 73.8% → 57.7% | -20.9 [-34.2, -8.4] | -31.2 [-40.0, -20.0] | -32.7 [-52.9, -17.8] | -1.5 [-6.0, +2.5] |
| prepend 20 | 75.0% → 12.1% | 71.9% → 19.5% | 73.8% → 42.6% | -57.4 [-73.2, -38.5] | -59.9 [-72.4, -41.9] | -53.3 [-72.2, -37.1] | +6.6 [+0.4, +11.9] |
| prepend 50 | 75.0% → 16.0% | 71.9% → 16.0% | 73.8% → 0.6% | -57.2 [-76.4, -30.2] | -63.4 [-78.7, -40.8] | -70.7 [-84.3, -50.9] | -7.3 [-11.2, -3.6] |

## Item 3: the 20 highest-scoring benign April reports

Ranked by logit among the 8,003 benign April reports. **C (J)**: mean logit of the 10 seeds. **Released Nebula**: published weights. All 40 reports are `clean` (none from `windows_syswow64`). "Same API sequence in malware": the report's API-name sequence also occurs in a malware report of April, January, or both ("April+January"). The first 30 calls per report are in `top_benign.md`.

C (J):

| rank | report row | source | chunks | calls | seen in Jan. | same API sequence in malware | first calls of the sequence |
|---|---|---|---|---|---|---|---|
| 1 | 4073 | clean | 1 | 10 | yes | no | getsystemtimeasfiletime getcurrentprocessid getcurrentthreadid gettickcount queryperformancecounter getstartupinfoa interlockedcompareexchange _initterm_e … |
| 2 | 7932 | clean | 1 | 11 | yes | April+January | getsystemtimeasfiletime getcurrentprocessid getcurrentthreadid gettickcount queryperformancecounter getstartupinfow heapsetinformation interlockedcompareexchange … |
| 3 | 7593 | clean | 1 | 10 | yes | April+January | getsystemtimeasfiletime getcurrentprocessid getcurrentthreadid gettickcount queryperformancecounter getstartupinfoa interlockedcompareexchange _initterm_e … |
| 4 | 4350 | clean | 1 | 1 | no | no | coinitialize |
| 5 | 3741 | clean | 1 | 1 | yes | no | loadlibrarya |
| 6 | 3458 | clean | 1 | 50 | no | no | getsystemtimeasfiletime getcurrentthreadid getcurrentprocessid queryperformancecounter isprocessorfeaturepresent loadlibraryexw getlasterror loadlibraryexw … |
| 7 | 6841 | clean | 1 | 27 | no | no | seterrormode getversion getmodulehandlew getprocaddress setdefaultdlldirectories getsystemdirectoryw lstrlenw wsprintfw … |
| 8 | 4296 | clean | 1 | 27 | no | no | seterrormode getversion getmodulehandlew getprocaddress setdefaultdlldirectories getsystemdirectoryw lstrlenw wsprintfw … |
| 9 | 4583 | clean | 1 | 27 | no | no | seterrormode getversion getmodulehandlew getprocaddress setdefaultdlldirectories getsystemdirectoryw lstrlenw wsprintfw … |
| 10 | 2470 | clean | 1 | 27 | no | no | seterrormode getversion getmodulehandlew getprocaddress setdefaultdlldirectories getsystemdirectoryw lstrlenw wsprintfw … |
| 11 | 7367 | clean | 1 | 27 | no | no | seterrormode getversion getmodulehandlew getprocaddress setdefaultdlldirectories getsystemdirectoryw lstrlenw wsprintfw … |
| 12 | 4229 | clean | 1 | 18 | no | no | __set_app_type __p__fmode __p__commode _controlfp _initterm __getmainargs _initterm getstartupinfoa … |
| 13 | 2937 | clean | 1 | 10 | yes | April+January | getsystemtimeasfiletime getcurrentprocessid getcurrentthreadid gettickcount queryperformancecounter getstartupinfoa interlockedcompareexchange _initterm_e … |
| 14 | 8928 | clean | 1 | 10 | yes | April+January | getsystemtimeasfiletime getcurrentprocessid getcurrentthreadid gettickcount queryperformancecounter getstartupinfoa interlockedcompareexchange _initterm_e … |
| 15 | 3808 | clean | 1 | 6 | no | no | getprocessheap getcurrentprocess openprocesstoken gettokeninformation heapalloc gettokeninformation |
| 16 | 5105 | clean | 1 | 9 | yes | April+January | __set_app_type __p__fmode __p__commode _controlfp _initterm __getmainargs _initterm getstartupinfoa … |
| 17 | 8741 | clean | 1 | 9 | yes | April+January | __set_app_type __p__fmode __p__commode _controlfp _initterm __getmainargs _initterm getstartupinfoa … |
| 18 | 9787 | clean | 1 | 14 | no | no | __set_app_type __p__fmode __p__commode _controlfp _initterm __getmainargs _initterm getstartupinfoa … |
| 19 | 2276 | clean | 1 | 13 | no | April | getmodulehandlew getsysteminfo getkeyboardtype getcommandlinew getstartupinfoa getacp getcurrentthreadid getversion … |
| 20 | 3384 | clean | 1 | 13 | no | April | getmodulehandlew getsysteminfo getkeyboardtype getcommandlinew getstartupinfoa getacp getcurrentthreadid getversion … |

Released Nebula:

| rank | report row | source | chunks | calls | seen in Jan. | same API sequence in malware | first calls of the sequence |
|---|---|---|---|---|---|---|---|
| 1 | 3849 | clean | 1 | 47 | no | no | getcommandlinea getversionexa initializecriticalsection entercriticalsection getprocessheap getsystemtimeasfiletime getcurrentprocessid getcurrentthreadid … |
| 2 | 8175 | clean | 1 | 1 | yes | January | getcommandlinea |
| 3 | 3741 | clean | 1 | 1 | yes | no | loadlibrarya |
| 4 | 2585 | clean | 1 | 5 | no | no | getprocessheap heapalloc getsysteminfo loadlibrarya getprocaddress |
| 5 | 4364 | clean | 1 | 7 | yes | April | __set_app_type __p__fmode __p__commode _controlfp _initterm __getmainargs _initterm |
| 6 | 2343 | clean | 3 | 234 | no | no | getversionexa getmodulehandlea heapcreate getmodulehandlea getprocaddress initializecriticalsectionandspincount initializecriticalsectionandspincount initializecriticalsectionandspincount … |
| 7 | 9154 | clean | 3 | 279 | no | no | loadlibrarya getprocaddress getprocaddress getprocaddress getprocaddress getprocaddress getprocaddress getprocaddress … |
| 8 | 3951 | clean | 3 | 219 | no | April | getsystemtimeasfiletime getcurrentthreadid getcurrentprocessid queryperformancecounter getstartupinfow getprocessheap encodepointer encodepointer … |
| 9 | 6482 | clean | 1 | 4 | yes | April | __set_app_type setunhandledexceptionfilter __getmainargs __p__fmode |
| 10 | 5200 | clean | 1 | 2 | no | no | getmodulehandlea loadlibrarya |
| 11 | 5581 | clean | 1 | 2 | no | no | getmodulehandlea loadlibrarya |
| 12 | 4141 | clean | 1 | 3 | no | no | memset rtlgetversion iogetcurrentprocess |
| 13 | 5146 | clean | 2 | 142 | no | April | getsystemtimeasfiletime getcurrentprocessid getcurrentthreadid gettickcount queryperformancecounter getstartupinfoa heapcreate getmodulehandlew … |
| 14 | 4229 | clean | 1 | 18 | no | no | __set_app_type __p__fmode __p__commode _controlfp _initterm __getmainargs _initterm getstartupinfoa … |
| 15 | 6554 | clean | 1 | 8 | no | no | getmodulehandlea getcommandlinea getmodulefilenamea createfilea setfilepointer messageboxa closehandle exitprocess |
| 16 | 4350 | clean | 1 | 1 | no | no | coinitialize |
| 17 | 4608 | clean | 1 | 48 | no | no | getversion heapcreate heapalloc heapalloc virtualalloc virtualalloc getstartupinfoa getstdhandle … |
| 18 | 4725 | clean | 3 | 219 | no | April | getsystemtimeasfiletime getcurrentthreadid getcurrentprocessid queryperformancecounter getstartupinfow getprocessheap encodepointer encodepointer … |
| 19 | 5967 | clean | 1 | 1 | yes | April | virtualalloc |
| 20 | 4503 | clean | 3 | 188 | no | April | getmodulehandlea getkeyboardtype getcommandlinea getstartupinfoa getacp getcurrentthreadid getmodulefilenamea getmodulefilenamea … |

**In common.** All 40 are `clean`, mostly one chunk, and typical program start-up code (`getsystemtimeasfiletime getcurrentprocessid …`, the C-runtime start-up `__set_app_type __p__fmode …`, `loadlibrarya`, `coinitialize`) or tiny reports with 1–10 calls. 8 of 20 in each list share their API-name sequence with a malware report, so no call-based model can separate them from that malware. Three reports are in both lists (rows 3741, 4229, 4350); C's top 20 sit at ranks 3–718 of 8,003 in the released model; the released model's top 20 sit at ranks 4–3,613 in C.

**Where they differ.** C's list is narrow: 11 distinct sequences in 20 reports (one sequence five times, one four times), all one chunk, 1–50 calls (median 13), 8 seen in January. The released list is more varied: 18 distinct sequences, 1–279 calls, 6 reports with two or three chunks (188–279 calls for five of them), 5 seen in January. C's most confident mistakes are short generic reports; the released model also puts some long, unusual reports at the top, which C scores low (six of its top 20 are at rank 1,500 or lower in C).

## Item 4: does C use the order of tokens inside a call? (regime S, 10 seeds, A as reference)

Edits of the first 512 tokens of every April report: **whole calls** shuffled (call order permuted, each call keeps its tokens); **within calls**: the tokens of each call permuted (exact per-call spans), call order kept; **bag of tokens**: all 512 tokens shuffled (control). 27% of the reports longer than 512 tokens have a real token with id 0 (the pad id) in the window; a within-call shuffle moves it across the 512 boundary for 1.2% of reports. TPR with the threshold recomputed on each score vector.

| model | input | AUC | TPR@1% (a) | AUC change [95% over seeds] | TPR change, points [95%] |
|---|---|---|---|---|---|
| A | original | 0.9325 | 66.4% | – | – |
| A | whole calls | 0.6930 | 7.0% | -0.2395 [-0.2540, -0.2230] | -59.4 [-62.8, -55.3] |
| A | within calls | 0.9329 | 64.8% | +0.0004 [-0.0016, +0.0025] | -1.6 [-2.4, -0.7] |
| A | bag of tokens | 0.6800 | 7.3% | -0.2525 [-0.2685, -0.2305] | -59.1 [-62.8, -55.1] |
| B | original | 0.9287 | 56.0% | – | – |
| B | whole calls | 0.9298 | 52.0% | +0.0011 [-0.0064, +0.0082] | -3.9 [-5.8, -1.9] |
| B | within calls | 0.9287 | 55.8% | -0.0000 [-0.0008, +0.0007] | -0.1 [-0.9, +0.7] |
| B | bag of tokens | 0.9395 | 60.4% | +0.0109 [+0.0063, +0.0149] | +4.5 [+2.8, +5.9] |
| C | original | 0.9416 | 67.0% | – | – |
| C | whole calls | 0.9412 | 58.6% | -0.0003 [-0.0048, +0.0042] | -8.5 [-10.5, -6.5] |
| C | within calls | 0.9439 | 65.7% | +0.0024 [+0.0003, +0.0045] | -1.3 [-2.7, +0.0] |
| C | bag of tokens | 0.9475 | 68.6% | +0.0060 [+0.0016, +0.0102] | +1.5 [-0.2, +3.2] |

C's change minus B's change (seed-paired, 10 seeds):

| edit | metric | C's change − B's change [95% over seeds] |
|---|---|---|
| whole calls | AUC | -0.0014 [-0.0079, +0.0054] |
| whole calls | TPR@1% (a), points | -4.5 [-8.2, -0.9] |
| within calls | AUC | +0.0024 [+0.0001, +0.0047] |
| within calls | TPR@1% (a), points | -1.2 [-2.8, +0.5] |
| bag of tokens | AUC | -0.0049 [-0.0090, +0.0004] |
| bag of tokens | TPR@1% (a), points | -2.9 [-5.4, -0.4] |

Reading: if C used token order inside calls, the within-call edit would hurt C and not B; it does not hurt either (C's AUC even rises by 0.002). Whole-call shuffling costs C 8.5 TPR points and B 3.9 (C's AUC is unchanged). The fixed position encoding therefore does not make C use fine token order; why it helps B-type models (+0.013 to +0.018 AUC in the earlier round) remains unexplained.

## Caveats

- Items 1–3 use regime J (all of January in training, no January threshold); item 4 uses regime S. Thresholds are (a) throughout.
- Items 1 and 2 edit only the first 512 tokens' worth of the report as the models read it; the full-trace model is in `results/fulltrace`.
- Item 2 pads with random benign calls only. It does not search for better padding, so it measures a lower bound on how far a determined attacker could go.
- The "fits" subsets are short reports (about 36% of April), where the unedited TPR is lower (about 60–70%) than on all reports.
- Item 3 lists are for the 10-seed ensemble of C; single seeds overlap with it in 10–18 of 20 reports.
- Intervals marked "over seeds" do not include sampling of April reports.
- Nothing here is committed.

## Files

`graded_edits.md`/`.json`, `benign_padding.md`/`.json`, `top_benign.md`/`.json`, `within_call_shuffle.md`/`.json`; code in `scripts/robustness/` (`graded_edits_released.py`, `benign_padding.py`, `top_benign.py`, `within_call_shuffle.py`).
