# B1 - does unlabelled April text help a self-supervised detector? (NOTES 30.4, 30.4a, 30.4b, 30.14)

**In plain words.** I split April by call-sequence group into two halves, ADAPT and TEST. A detector was pre-trained to predict the next token (a) not at all, (b) on January text, (c) on January text plus the unlabelled ADAPT half; then every version was fine-tuned on the labelled January reports only and scored on the TEST half. **Result: no effect that I can resolve.** Adding the unlabelled ADAPT text changed pAUC@1e-2 by -1.1 points (cluster interval -4.6 to +2.6; 5 seeds up, 5 down). Pre-training on January itself also gave nothing resolved (+0.9, interval -5.2 to +7.1). The seed-to-seed spread (3.6 to 4.6 points) is as large as any difference.

Setting (fixed before any run, NOTES 30.4a/b): corrected 8k tokenizer (the 50k vocabulary does not fit AR pre-training on a T4), full-attention encoder with flatten head, 3 pre-training epochs (weights of the best epoch by held-out LM loss; held-out loss fell every epoch), 2 fine-tuning epochs on all 75,298 January reports, lr 1e-3, 10 seeds. Split: seed 2027, ADAPT 8,960 reports, TEST 8,442 (no group in both), TEST-unseen 5,607 reports (sequences not in January); sha256 c9808ac8... (`split.json`). ADAPT labels were never read; ADAPT scores were never computed. April opening 33: the TEST logits only, once, after all 10 seeds were in.

## Results (pAUC@1e-2 normalised, mean ± std over 10 seeds; full tables in `tables.md`)
| condition | TEST | TEST-unseen |
|---|---|---|
| (i) no pre-training | 0.601 ± 0.046 | 0.527 ± 0.061 |
| (ii) AR pre-training on January | 0.610 ± 0.036 | 0.555 ± 0.048 |
| (iii) AR pre-training on January + unlabelled ADAPT | 0.600 ± 0.036 | 0.543 ± 0.052 |

Differences (points, cluster 95% CI over hash_apis groups, seeds up / down): TEST: (iii)-(ii) -1.08 [-4.59, +2.60] 5/5; (ii)-(i) +0.90 [-5.20, +7.07] 6/4; (iii)-(i) -0.18 [-6.81, +7.38] 5/5. TEST-unseen: (iii)-(ii) -1.17 [-5.37, +4.21] 5/5; (ii)-(i) +2.83 [-6.40, +12.59] 7/3; (iii)-(i) +1.66 [-8.53, +13.98] 6/4. **None resolved.** TPR@1e-2 is 3 to 5 points lower with pre-training in both halves (stratified interval excludes 0, cluster interval does not), TPR@1e-3 higher by about 10 points with large seed spread; neither is a pre-registered primary.

## Checks and limits
No collapse (every seed and condition has TEST AUC above 0.6; no STOP.txt). Fine-tuning used only January rows (assert in `b1.py`). The unlabelled ADAPT text enters only condition (iii). Limits: 8k tokenizer, so these numbers are not comparable with M1 to M4 (the 8k models score about 0.60 on this half, the 50k models M1 to M3 about 0.69 to 0.71 on the full April set; the two sets differ, so this is only a rough comparison); a fixed short budget; one split of April; no control with extra January text (that is B2, not run); the confidence intervals are wide, so a gain of a few points cannot be excluded.
