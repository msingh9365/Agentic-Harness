# Stage D: is the drop of the new-split models caused by training too long? (NOTES 22)

Steps 1 to 4 (Step 0 and Step 5 come later). All April scores are 10 seeds each, one evaluation per model. **"Resolved" means the cluster bootstrap interval (resampling the 2,509 groups of duplicate April reports) of pAUC@1e-2 excludes zero.** That is stricter than the wording of Stage C: under it, new ATT+bal vs new v2-PE (−4.4 points) is *not* resolved.

## April pAUC@1e-2 (main metric), mean ± std over 10 seeds (10-seed ensemble in brackets)

| model | old split (2 epochs) | new split, Stage C epoch | new split, early-stopped per seed | new split, 2 epochs |
|---|---|---|---|---|
| v2-PE | 0.705 ± 0.031 (0.768) | 0.634 ± 0.024 (0.689) | 0.620 ± 0.026 (0.695) | 0.634 ± 0.040 (0.696) |
| ATT+bal | 0.707 ± 0.017 (0.734) | 0.590 ± 0.052 (0.647) | 0.620 ± 0.047 (0.663) | 0.642 ± 0.013 (0.667) |

(Stage C epoch = epoch 1 for v2-PE, epoch 3 for ATT+bal. "2 epochs" = the old epoch count, new split, new tokenizer, every other new setting; for ATT+bal that still means the new learning rate 1e-3.)

## What the steps show

* **Step 1 (validation, no training):** as the loss rises, validation pAUC barely moves; the loss rise is mostly overconfidence (the logits grow 1.6 to 3 times), not a worse ranking at the 1% false-positive point. Peak: v2-PE epoch 1, ATT+bal epoch 3, but both curves are flat within seed noise.
* **Step 2 (early stopping per seed, epoch chosen on validation only):** v2-PE −1.4 points against Stage C (not resolved); ATT+bal **+3.0 points (resolved, interval +1.3 to +4.7)**. Both are still **resolved worse than the old-split models** (−8.5 and −8.7 points; 0 of 10 seeds above).
* **Step 3 (new split with the old epoch count; run because the gate was met for both models):** v2-PE at 2 epochs is the same as at 1 epoch (+0.04, not resolved); ATT+bal at 2 epochs is **+5.1 points better than at 3 epochs (resolved, interval +2.3 to +8.0; 8 of 10 seeds up)**. Against the old-split models both remain **resolved worse**: v2-PE −7.1, ATT+bal −6.6 (interval −14.7 to −0.2, close to zero).
* **So how much is "training too long"?** For ATT+bal, going back from 3 to 2 epochs recovers about 5 of the 11.7 points lost; for v2-PE nothing (it was already at its earliest epoch). **About 7 points remain for both models** after the epoch count is matched. That remainder comes from split, tokenizer, seeds (and, for ATT+bal, the learning rate); this step does not tell which.
* **ATT+bal vs v2-PE:** in every condition (Stage C, early-stopped, 2 epochs, old) the difference is not resolved.
* **Step 4 (where the threshold is set):** the TPR@1e-2, TPR@1e-3 and per-family rates in all tables so far set the threshold on the April benign reports, so the 1.0% clean false-positive rate is **true by construction**. With the threshold set on the validation slice and applied to April, the April false-positive rate is 0.74 ± 0.21% (v2-PE) and 0.86 ± 0.47% (ATT+bal, 4 of 10 seeds above 1%); per seed it ranges from 0.04% to 12.1% (early-stopped v2-PE, one seed at 12.1%). The old v2-PE, whose validation slice was the random one, gets 1.34 ± 0.30% (9 of 10 seeds above 1%). Detection with these thresholds is 2 to 8 points lower than with the April thresholds for the new-split models (v2-PE 70.4% vs 73.2%, ATT+bal 64.9% vs 66.5%).

## What this does not show

* Which of split, tokenizer, seeds or (ATT+bal) learning rate causes the remaining ~7 points: nothing was varied alone. **Guess, not tested:** the loss of whole groups (keylogger, rat, trojan) from training; Step 0 looks at this descriptively.
* The ATT+bal "2 epochs is better than 3" result is an April observation. Validation could not have found it (validation pAUC is flat, epoch 3 is the peak by 0.004), and per-seed early stopping on validation recovered only 3.0 of the 5.1 points. It is not a validated recipe.
* The ranking of the conditions rests on 10 seeds; the cluster intervals are 2 to 3 times wider than the stratified ones, so several stratified "differences" are not resolved by the cluster rule.
* The validation-threshold false-positive rates rest on 3,161 benign validation reports (the threshold is the benign logit at rank 31), so single seeds can be far off (0.04% to 12.1%).
* New and old models are different training runs: "seeds going each way" pairs seed index i with i and means only that.

## Files

`step1_val_per_epoch.md|json`, `fig_step1_val_pauc_vs_loss.png`, `early_stop_selection.md|json`, `tables_stage_d.md` (all tables, both bootstraps, seeds, per family, Step 4), `stage_d_results.json`, `bootstrap_stratified.json`, `fig_april_pauc_by_condition.png`. Code: `baseline/gs_epochs.py`, `gs_early.py`, `gs_eval_d.py`, `gs_grid.py --stage-d`.
