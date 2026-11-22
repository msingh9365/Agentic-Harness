# MTP follow-ups: results at the report cut-off (2026-11-22, about 23:40 IST; later results, if any, come as separate commits; every number is from stored scores or logits, corrected tokenizer, 10 seeds)

| item | status | where |
|---|---|---|
| 0 F1 threshold, how seeds and the bootstrap combine | **done** | STATUS.md (first MTP section) |
| 1a cluster-bootstrap intervals for every Stage J cell | **done** | `stage_j_cluster_ci.md` (in this folder) |
| 1b tokens per padding call, window analysis, April benign above 1e-3 | **done** | `tokens_per_call.md` |
| 2 random padding k = 20, 50, 60, 75, 100 (held-out pool) | **running**: kernel `msingh9365/nebula-fup-k` queued | `stage_k/` when done |
| 3 the 2 x 2 (head x padding), matched budget | **running**: budget grid on `manishsinghxdev/nebula-fup-grid`; then the final training (about 1.4 h), then attack scores | `item3/` when done |
| 4 malware-only padding, clean April comparison | **done** | `item4/clean_tables.md` |
| 4 malware-only padding, padded-benign false alarms | **running**: attack scoring `msingh9365/nebula-fup-atk4` queued | `item4/` when done |
| 5 M1 white-box, final Stage J | **done** (NOTES 25.2) | `stage_j/` |

## What is final now
- **Item 0.** The F1 in the clean tables is the F1 at the fixed decision threshold 0.5 (logit 0), not at the 1% FPR threshold. One bootstrap resample per draw is applied to all models and all 10 seeds; a difference of two models is the mean over seeds of the per-seed differences (seeds paired by index); the intervals describe the sampling of April reports (or hash groups) with the trained models fixed.
- **Item 1a.** Cluster-bootstrap 95% intervals (groups = hash_apis, the method of the clean tables; thresholds recomputed on each resample; interval of the 10-seed mean). Detection at the 1% clean-FPR threshold, % (M1 / M2 / M3 / M4): unedited 79.1 [68.6, 85.8] / 77.2 [66.3, 84.1] / 79.0 [68.6, 86.3] / 77.9 [68.0, 85.2]; random 50 prepend 7.4 [4.3, 11.6] / 28.5 [14.3, 46.2] / 65.1 [52.3, 74.9] / 67.2 [55.1, 76.4]; padded-benign FPR (%), random 50 prepend 1.07 [0.23, 2.18] / 0.05 [0.01, 0.13] / 0.84 [0.50, 1.39] / 0.49 [0.38, 0.63]. White-box rows: with the attack's own fixed threshold, after 20 steps M1 1.6 [0.6, 3.2], M2 19.6 [12.0, 28.0], M3 48.7 [34.3, 60.7], M4 50.2 [35.2, 62.5]; after 50 steps 0.6 [0.2, 1.1], 13.8 [7.9, 20.4], 2.5 [1.1, 4.6], 10.6 [6.4, 15.8]. (The recomputed-threshold intervals of the white-box rows are lopsided; see the file.)
- **Item 1b.** A padding call costs a median of 5 BPE tokens (IQR 4 to 7). About 82 random prepended calls (IQR 78 to 86) push the first token of the original report out of the 512-token window of M1 and M3, about 663 (IQR 652 to 674) out of the 4,096-token window of M2 and M4: the scale of the collapse of M3 and M1 between 50 and 100 prepended calls. 8 April benign reports are above the 1e-3 threshold (n_benign = 8,003, rank 8), 80 above the 1e-2 threshold.
- **Item 4, clean.** Malware-only padding with the final M1 and M3 settings gives the same clean April performance as the final M1 and M3: pAUC@1e-2 0.702 ± 0.038 against 0.686 ± 0.026 (+1.55 points, cluster interval [-1.72, +5.08], not resolved) and 0.703 ± 0.028 against 0.705 ± 0.025 (-0.19, [-2.48, +2.06], not resolved).
- **Item 5.** The M1 white-box attack is in the final Stage J report (NOTES 25.2): detection at the 1% threshold after 20 / 50 steps, M1 1.6 / 0.6, M2 19.6 / 13.8, M3 48.7 / 2.5, M4 50.2 / 10.6; M2 to M4 identical to the partial report.

## Not finished (do not cite as results)
Items 2, 3 and the padded-benign false alarms of item 4 are waiting for Kaggle GPU kernels (queue times of hours on this account pair). Their pre-registered design is NOTES 26; if they do not finish, the report should say they were designed and pre-registered but not run.

## Report cut-off (owner's deadline 11:50 pm IST)
At the cut-off the following were **not run to completion** and must not be cited as results: item 2 (random padding at k = 20, 50, 60, 75, 100 from the held-out pool; kernel `msingh9365/nebula-fup-k` still in the Kaggle queue), the padded-benign false alarms of item 4 (kernel `msingh9365/nebula-fup-atk4` queued; the training and the clean comparison are done), and item 3 (the 2 x 2 at a matched budget; the budget grid on `manishsinghxdev/nebula-fup-grid` was still running; the final training and the attack scores had not started). Their designs, the budget-selection rule and the checks are pre-registered in NOTES 26 (commit `0e630f4`, before any of these runs). Suggested wording for the report: "designed and pre-registered; the GPU jobs were still queued or running at the deadline".

## Update at 23:49 IST: item 3, stage 1 (budget selection) is done
The budget grid finished and the pre-registered rule chose **lr 1e-3, 1 epoch** for all four cells (all six candidates were tied within one SE; fewer epochs, then the lower lr). Validation pAUC@1e-2 per cell at that budget (descriptive): flatten/none 0.561, attention/balanced 0.478, attention/none 0.610, flatten/balanced 0.388. The final training and the April evaluation of the 2 x 2 were NOT run at the cut-off. Files: `item3/selection.json`, `item3/validation_tables.md`, NOTES 26.3.
