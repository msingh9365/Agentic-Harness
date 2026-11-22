### Item 1b: tokens per padding call, calls needed to leave the window, April benign reports above the 1e-3 threshold (corrected tokenizer `bpe50k_fix`)

**BPE tokens per padding call (EVAL pool = 3161 benign group-split validation reports, 579,163 calls).** Under the attack sampler (uniform pool report, then uniform call): median 5 (IQR 4 to 7), mean 6.2. Over all pool calls (reference): median 5 (IQR 4 to 6), mean 5.5, min 3, max 121.

**Report head** (tokens before the first call; the first token of the original report comes right after it): median 1 (IQR 1 to 15) over 9,399 April malware reports with a call.

**Random padding calls to prepend so that the first token of the original report lies at position >= the window (median and IQR over the April malware reports; the draws are those of the attack sampler)**

| model | window (tokens) | calls to push the original report out (median, IQR) | mean | censored (> 4,000 calls) |
|---|---|---|---|---|
| M1 Nebula | 512 | 82 (IQR 78 to 86) | 82.0 | 0 |
| M2 two-level | 4,096 | 663 (IQR 652 to 674) | 662.6 | 0 |
| M3 ATT+bal | 512 | 82 (IQR 78 to 86) | 82.0 | 0 |
| M4 ATT+bal-2L | 4,096 | 663 (IQR 652 to 674) | 662.6 | 0 |

**April benign reports above the threshold** (n_benign = 8,003; the threshold is the benign logit at rank floor(fpr x n), a report is flagged if strictly above it; min / median / max over the 10 seeds)

| model | fpr 1e-3: rank | benign flagged | fpr 1e-2: rank | benign flagged |
|---|---|---|---|---|
| M1 Nebula | 8 | 8 (7 to 8) | 80 | 80 (80 to 80) |
| M2 two-level | 8 | 8 (8 to 8) | 80 | 80 (79 to 80) |
| M3 ATT+bal | 8 | 8 (8 to 8) | 80 | 80 (80 to 80) |
| M4 ATT+bal-2L | 8 | 8 (8 to 8) | 80 | 80 (77 to 80) |
