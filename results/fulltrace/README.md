# Model C over the whole report (round 3, GPU part)

**F** = model C (mean pooling + fixed position encoding, masked mean over the real tokens) reading the **whole report**, up to 4,096 tokens = 64 chunks of 64 (mean 1,101 tokens per report; 66% of reports are longer than 512 tokens; 0.2% are cut at 4,096). Regime J (trained on all of January, 75,298 reports), 10 epochs, seeds 0–4. References, same five seeds: **A (J)** (flatten, first 512 tokens, 1 epoch), **C 512** (the same model C, first 512 tokens, 10 epochs), the released Nebula, and LightGBM on a bag of API names. April test set: 17,402 reports, 9,399 malware. Thresholds (a): 1% / 0.1% FPR on the April benign scores (regime J has no January threshold). Intervals: group bootstrap over April `hash_apis`, 1,000 resamples, paired across models. Full tables: `tables.md` (all subsets, paired differences), `graded_edits.md`.

## Verdict

1. **Reading the whole report does not improve accuracy.** AUC F 0.9635, C 512 0.9628, A 0.9557, released 0.9586; F − A +0.0078 [−0.0033, +0.0216], F − C 512 +0.0007 [−0.0084, +0.0102], F − released +0.0049 [−0.0055, +0.0159]. TPR at 1% FPR: 74.5% against 72.3% (C 512), 72.7% (A), 75.0% (released), all within the intervals.
2. **Long reports do not benefit.** On the 4,966 reports with 4–8 chunks F has AUC 0.9381 against 0.9477 (C 512), 0.9421 (A), 0.9288 (released); F − C 512 −0.0096 [−0.0291, +0.0042]. F is best on 2–3 chunks (0.9853 against 0.9800 for C 512, 0.9772 for A), but the interval includes 0. At 0.1% FPR F is clearly worse than A (12.7% against 44.2%; F − A −31.6 [−42.8, −6.4]) and released (51.7%).
3. **Rank average with LightGBM: no gain either.** F + LightGBM 0.9765, C 512 + LightGBM 0.9793, A + LightGBM 0.9753, released + LightGBM 0.9744 (the reference 0.9745); F + LightGBM − released + LightGBM +0.0021 [−0.0040, +0.0088]. At 0.1% FPR F + LightGBM is below released + LightGBM (−11.4 [−21.5, −2.8]).
4. **F is robust to padding with copies of the report's own calls.** At the fixed 1% threshold malware TPR changes by −1.4 to +0.3 points for all eight edits (prepend 20: −1.0 [−2.5, +0.6]; A −41.5 [−52.6, −29.1], released −39.3 [−51.3, −26.1], C 512 −1.6 [−3.7, +0.3]), benign FPR stays at 0.95–1.12%. F − C 512 is positive but small (+2.5 for insert 20, +4.9 for prepend 50 are the only intervals above 0). The robustness comes from C's mean pooling, which C 512 already has; reading the full trace adds little. Calls copied from benign reports (`results/robustness`, item 2) were not tested on F.
5. **Cost and convergence.** Smoke run 0.23 h and full run 7.36 h of the weekly quota (estimate before the run 6.3 h; quota is charged about 2.9 times the wall time of 150.6 min), so about 11.5 of the 30 h remain. F reaches its final accuracy after one epoch (mean April AUC 0.9647 after epoch 1, 0.9635 from epoch 5 on), so 10 epochs were not needed; one or two epochs would cost about 1 h.

## Table 1: accuracy, all April reports (mean of 5 seeds [95% group interval])

| model | AUC | TPR@1% FPR | TPR@0.1% FPR |
|---|---|---|---|
| **F, whole report (J)** | 0.9635 [0.9405, 0.9785] | 74.5% [60.9%, 83.4%] | 12.7% [6.2%, 37.2%] |
| C 512 tokens (J) | 0.9628 [0.9395, 0.9781] | 72.3% [57.2%, 81.8%] | 18.4% [7.4%, 42.0%] |
| A (J), 512 tokens | 0.9557 [0.9267, 0.9745] | 72.7% [60.9%, 81.4%] | 44.2% [30.5%, 55.6%] |
| released Nebula | 0.9586 [0.9295, 0.9772] | 75.0% [65.3%, 82.5%] | 51.7% [0.0%, 67.0%] |
| LightGBM bag of API names | 0.9497 [0.9144, 0.9757] | 62.9% [33.5%, 74.9%] | 31.3% [18.2%, 45.4%] |
| F + LightGBM (rank average) | 0.9765 [0.9565, 0.9886] | 80.1% [68.6%, 86.9%] | 43.0% [28.8%, 59.5%] |
| C 512 + LightGBM | 0.9793 [0.9603, 0.9899] | 79.6% [68.7%, 87.7%] | 44.9% [30.0%, 61.3%] |
| A (J) + LightGBM | 0.9753 [0.9511, 0.9884] | 78.3% [68.3%, 86.1%] | 53.1% [35.6%, 66.6%] |
| released + LightGBM | 0.9744 [0.9498, 0.9884] | 79.5% [68.7%, 87.6%] | 54.4% [39.9%, 70.7%] |

Seed spread of F (AUC): 0.9626 / 0.9652 / 0.9611 / 0.9641 / 0.9644 (sd 0.0016); of C 512: sd 0.0111; of A: sd 0.0142. The five-seed mean of A (0.9557) is above its ten-seed mean in `results/pooling_v2` (0.9486): seeds 0–4 are a favourable subset for A.

## Table 2: by number of chunks (AUC; TPR@1% FPR in brackets)

| subset (malware / reports) | F | C 512 | A (J) | released | F + LightGBM | released + LightGBM |
|---|---|---|---|---|---|---|
| 1 chunk (2,855 / 6,359) | 0.9520 (73.0%) | 0.9606 (69.9%) | 0.9482 (64.4%) | 0.9556 (61.5%) | 0.9634 (68.6%) | 0.9628 (59.0%) |
| 2–3 chunks (3,676 / 6,077) | 0.9853 (71.3%) | 0.9800 (68.2%) | 0.9772 (72.4%) | 0.9833 (79.3%) | 0.9915 (85.3%) | 0.9925 (89.9%) |
| 4–8 chunks (2,868 / 4,966) | 0.9381 (80.2%) | 0.9477 (80.0%) | 0.9421 (81.4%) | 0.9288 (82.9%) | 0.9617 (85.0%) | 0.9543 (86.7%) |

Paired differences of F (AUC [95% interval]): F − A: 1 chunk +0.0038 [−0.0135, +0.0188], 2–3 chunks +0.0081 [−0.0025, +0.0327], 4–8 chunks −0.0040 [−0.0258, +0.0153]. F − released: −0.0036 [−0.0303, +0.0138], +0.0020 [−0.0037, +0.0117], +0.0093 [+0.0003, +0.0239]. No interval of F − A or F − C 512 excludes 0 for AUC.

F is not better on the 1-chunk reports either, although for them F sees exactly the same tokens as C 512; the 0.009 difference is seed noise of two independently trained models (F − C 512 −0.0086 [−0.0337, +0.0048]).

## Table 3: accuracy per training epoch of F (mean of 5 seeds, April AUC)

| epoch | 1 | 2 | 3 | 4 | 5 | 6–10 |
|---|---|---|---|---|---|---|
| AUC | 0.9647 | 0.9636 | 0.9637 | 0.9636 | 0.9636 | 0.9635 |

## Table 4: graded edits, change in malware TPR at the fixed 1% threshold (points; all reports; [group 95% interval])

Insert k / prepend k calls copied from the same report (the edits of `results/robustness`), F reading up to 4,096 tokens of the edited report, the others the first 512. Unedited TPR: F 74.5%, C 512 72.3%, A 72.7%, released 75.0%.

| edit | F | C 512 | A (J) | released | F − C 512 | F − A |
|---|---|---|---|---|---|---|
| insert 1 | −1.0 [−1.7, −0.3] | −0.9 [−1.7, −0.2] | −0.8 [−1.3, −0.2] | −1.4 [−2.8, −0.3] | −0.0 [−0.6, +0.6] | −0.2 [−1.0, +0.5] |
| insert 5 | −1.4 [−2.7, +0.0] | −2.5 [−4.7, −0.6] | −5.0 [−7.6, −2.2] | −5.7 [−10.4, −1.5] | +1.1 [−0.4, +2.6] | +3.7 [+0.8, +6.2] |
| insert 20 | −0.9 [−2.9, +1.0] | −3.3 [−6.4, −0.7] | −20.4 [−28.7, −11.1] | −17.5 [−32.0, −5.5] | +2.5 [+0.3, +4.6] | +19.5 [+10.9, +26.7] |
| insert 50 | +0.3 [−1.3, +2.2] | −1.0 [−2.8, +0.5] | −31.3 [−43.0, −19.0] | −25.7 [−40.5, −12.6] | +1.3 [−0.7, +3.6] | +31.6 [+19.8, +42.2] |
| prepend 1 | −1.1 [−2.1, −0.3] | −2.3 [−4.3, −0.6] | −3.0 [−5.1, −0.2] | −5.4 [−8.9, −1.9] | +1.1 [−0.6, +2.9] | +1.9 [−0.9, +4.0] |
| prepend 5 | −1.3 [−2.9, +0.5] | −4.4 [−10.3, −0.3] | −25.5 [−34.1, −14.5] | −21.3 [−35.8, −7.0] | +3.1 [−1.1, +8.4] | +24.2 [+14.0, +32.1] |
| prepend 20 | −1.0 [−2.5, +0.6] | −1.6 [−3.7, +0.3] | −41.5 [−52.6, −29.1] | −39.3 [−51.3, −26.1] | +0.6 [−1.6, +3.2] | +40.5 [+28.5, +51.2] |
| prepend 50 | +0.0 [−1.1, +1.5] | −4.9 [−8.4, −1.9] | −49.1 [−60.6, −33.9] | −36.9 [−47.8, −25.5] | +4.9 [+2.0, +8.1] | +49.1 [+34.4, +60.4] |

Benign FPR after the edit at that threshold: F 0.95–1.12%; C 512 up to 2.32% (prepend 5); A up to 10.3% (prepend 20/50); released up to 20.9% (prepend 20). 99.9% of the April malware reports still fit in 4,096 tokens after the edits, so for F the "fits" subset equals all reports (`graded_edits.md` also lists the 512-token subset, where F and C 512 see the same tokens: F − C 512 is within ±1.5 points for every edit).

## Table 5: cost

| run | wall time | quota charged | note |
|---|---|---|---|
| smoke (1 epoch, 1 seed, T4×2) | about 6 min | 0.23 h | timing for the estimate |
| full: F, 5 seeds, 10 epochs | 150.6 min (about 300 s per epoch) | 7.36 h | estimate before the run 6.3 h; under the 8 h limit |
| A (J) 5 seeds | reused from `results/pooling_v2` | 0 | same seeds 0–4 |
| quota state | | 10.9 h → 18.5 h used of 30 h | resets Nov 21 |

Output of the run: 574 MB (checkpoints 560 MB, per-epoch scores 14 MB) kept outside the repository (`/Users/manish/Code/mtp/fulltrace_output`).

## Caveats

- Only the regime J (all of January in training, fixed 10 epochs for F, 10 for C 512, 1 for A) and only five seeds; the intervals include sampling of April reports but not of training seeds beyond these five.
- F and C 512 are the same model class; F differs by the token budget (4,096 against 512) and by the masked mean over all real tokens, not by anything else (checked by test 8 in `hier_nebula/test_pooling.py`: on reports of at most 512 tokens F and C give the same pooled vectors).
- Training F with chunk windows beyond 512 tokens and dynamic padding is equivalent to padding to 4,096 because chunks are independent in the encoder.
- The graded edits are copies of the same report's calls. How F reacts to calls from benign reports is not measured; C 512 loses clearly there (`results/robustness`, item 2).
- Nothing here is committed.

## Files

`tables.md`, `evaluation.json` (all subsets, paired differences), `graded_edits.md`/`.json`; code in `scripts/fulltrace/` (`make_fulltrace_tokens.py`, `evaluate_fulltrace.py`, `graded_edits_fulltrace.py`) and `scripts/kaggle/train_fulltrace.py`, `kernel_ft_smoke/`, `kernel_ft_full/`.
