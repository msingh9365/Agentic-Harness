# Step 3b: is it the tokenizer? (diagnostic, NOTES 22.7 and 22.8)

Stage C exactly (group-split training part, same settings, seeds 0 to 9), with ONE change: the old tokenizer (fitted on all of January) instead of the one refit on the training part. April pAUC@1e-2, mean ± std over 10 seeds (10-seed ensemble). "Resolved" means the cluster-bootstrap interval excludes zero.

| model | old split (2 epochs) | new split, new tokenizer (Stage C) | new split, OLD tokenizer (3b) |
|---|---|---|---|
| v2-PE | 0.705 ± 0.031 (0.768) | 0.634 ± 0.024 (0.689) | 0.596 ± 0.067 (0.683) |
| ATT+bal | 0.707 ± 0.017 (0.734) | 0.590 ± 0.052 (0.647) | 0.627 ± 0.025 (0.653) |

* **The tokenizer swap goes in opposite directions for the two models.** v2-PE gets 3.8 points *worse* with the old tokenizer (resolved, interval −6.1 to −1.4; 4 seeds up / 6 down); ATT+bal gets 3.7 points *better* (resolved, interval +0.9 to +6.6; 5 up / 5 down). The 10-seed ensembles hardly move (−0.6 and +0.6).
* **Against the old-split models both stay clearly worse:** v2-PE −10.9 points, ATT+bal −8.0 points (resolved, 0 of 10 seeds above).
* **So the tokenizer explains none of the drop for v2-PE and about 3.7 of the 11.7 points for ATT+bal.** The ~7 points that remained after matching the epoch count (Step 3) are therefore not mainly a tokenizer effect.
* **Per family** the big drops stay with the old tokenizer: keylogger −18.6 (v2-PE) and −18.6 (ATT+bal), rat −12.9 and −11.3, trojan −20.9 and −17.0 points against the old-split models.
* ATT+bal vs v2-PE with the old tokenizer: +3.1 points, not resolved.

## What this does not show

* What causes the rest: the group split itself (a different training set, not just a different validation set), the seeds, the epoch count of the old models (2, against 1 and 3 here) or the ATT+bal learning rate (1e-3 here, 2e-3 in the old model) were not varied alone. Nothing here tests the group split directly.
* The two tokenizer effects were measured on different seeds-by-model pairs with a large seed spread (SD up to 0.067); the sign flip between the models is a fact of these runs, not an explanation.
* The old tokenizer was fitted on all of January, so it saw the text of the validation slice (no labels); the new one did not. This is the one factor changed, not a statement about leakage into April (April is in neither fit).
* Thresholds of TPR@1e-2 and the per-family rates are set on the April benign scores (clean false-positive rate 1% by construction).

Files: `tables.md` (all tables, both bootstraps, seeds each way, per family), `results.json`, `bootstrap_stratified.json`. Code: `baseline/gs_eval_gen.py --mode tk`, `baseline/gs_grid.py --tok-old`.
