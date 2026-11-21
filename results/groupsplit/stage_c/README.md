# Stage C: v2-PE and ATT+bal retrained on the group-split training part (NOTES 21.10 to 21.12)

**In plain English.** We trained both models again, 10 seeds each, on the new training part (no API sequence is shared with the validation slice) with the settings picked in Stage B on the new validation slice: v2-PE lr 2e-3, 1 epoch; ATT+bal lr 1e-3, padding probability 0.5, 3 epochs. Then we scored the April test set once per model. The settings were fixed, and pushed, before any Stage C job ran. No April number was used for any choice.

## Main result (April, pAUC@1e-2 = the main metric; mean ± std over 10 seeds; in brackets: the average of the 10 models' scores)

| model | pAUC@1e-2 | TPR@1e-2 | TPR@1e-3 | AUC |
|---|---|---|---|---|
| **v2-PE, new split** | **0.634 ± 0.024** (0.689) | 0.732 | 0.479 | 0.9599 |
| **ATT+bal, new split** | **0.590 ± 0.052** (0.647) | 0.665 | 0.503 | 0.9386 |
| v2-PE, old validation slice | 0.705 ± 0.031 (0.768) | 0.811 | 0.543 | 0.9644 |
| ATT+bal, old validation slice | 0.707 ± 0.017 (0.734) | 0.795 | 0.572 | 0.9713 |

* **New ATT+bal vs new v2-PE:** 4.4 points lower. The usual bootstrap says this is a real difference (7 of 10 seeds below); the bootstrap that resamples whole duplicate groups says it is not resolved (interval −9.4 to +0.8). Under the rule used from Stage D on (resolved only if the cluster interval excludes 0) it is NOT resolved. At the stricter 0.1% false-positive level the two are the same.
* **New vs old models:** v2-PE is 7.1 points lower and ATT+bal 11.7 points lower; every one of the 10 seeds is lower, and both bootstraps agree. The old ATT+bal and old v2-PE are still tied (+0.2, not resolved).
* **Why we cannot say what caused the drop.** The new models differ from the old ones in four ways at once: whole groups are held out of training, the tokenizer was refit on the training part only, fewer epochs, and (ATT+bal) a smaller learning rate. This experiment does not separate them. The biggest drops are in keylogger, rat and trojan, which lose whole groups to the validation slice; that is a guess we did not test.
* **Per family** (share detected at 1% false positives, new v2-PE / new ATT+bal, old v2-PE / old ATT+bal): keylogger 70 / 63 vs 87 / 87, rat 77 / 70 vs 89 / 88, trojan 62 / 62 vs 81 / 80, ransomware 68 / 62 vs 71 / 73, coinminer 77 / 62 vs 82 / 73. The 1.0% for clean reports is true by construction: the 1% threshold is set on the April benign scores themselves (Stage D, Step 4 gives the April false-positive rate with a threshold set on validation).
* **The coinminer cluster** (265 reports with the same first 512 tokens): the new v2-PE flags it in 7 of 10 seeds, the new ATT+bal in 0 of 10 (old: 8 and 1).
* **Loss curves** (`fig_loss_curves_train_vs_validation.png`): training loss goes down at every epoch, validation loss on the group-split slice goes up at every epoch, so more training only makes the models more sure and more wrong on unseen groups. The chosen epochs are the earliest ones.

Details: `tables.md` (all tables, claim rule with both bootstraps), `per_model.json`, `bootstrap.json`, `cluster.json`, `family.json`, `logits_new_models.npz` (scores), `runs/` (per-seed logs and loss curves). Code: `baseline/gs_grid.py --final`, `baseline/gs_eval.py`. No attacks were run (separate task).
