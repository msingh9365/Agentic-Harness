# Step 5: the final protocol (NOTES 22.2, 22.3, 22.7, 22.9, 22.10)

**Step 5 is the final protocol of the thesis. Its numbers are final for M1 and M3, regardless of the result. Any further explanation of the differences below is diagnostic only and changes nothing in these numbers.**

What was done: both models were trained on **all 75,298 January reports** with the settings chosen on the group-split validation slice (v2-PE lr 2e-3, 1 epoch; ATT+bal lr 1e-3, padding probability 0.5, 3 epochs), seeds 0 to 9, with the old BPE-50k tokenizer (checked to be a BPE-50k fitted on exactly all of January with the same settings, identical vocabulary and tokens). The ATT+bal padding calls come only from the 21,507 benign reports of the 66,580-report group-split training part (so none of the validation slice is ever used as padding). No validation-based choice was made. Each model was scored once on April. Both kernels ran on `manishsinghxdev` (the ATT+bal duplicate on `msingh9365` was never opened).

## Final numbers (April, mean ± std over 10 seeds; 10-seed ensemble in brackets)

| model | pAUC@1e-2 (main) | TPR@1e-2 | TPR@1e-3 | AUC | F1 |
|---|---|---|---|---|---|
| **ATT+bal, all January (final)** | **0.710 ± 0.015** (0.731) | 0.790 ± 0.008 | 0.590 ± 0.029 | 0.9694 | 0.908 |
| **v2-PE, all January (final)** | **0.674 ± 0.053** (0.739) | 0.780 ± 0.038 | 0.541 ± 0.095 | 0.9667 | 0.899 |
| ATT+bal, old split (REPORT 5.10) | 0.707 ± 0.017 (0.734) | 0.795 | 0.572 | 0.9713 | 0.913 |
| v2-PE, old split (REPORT 5.9) | 0.705 ± 0.031 (0.768) | 0.811 | 0.543 | 0.9644 | 0.915 |
| ATT+bal, new split, new tokenizer (Stage C) | 0.590 ± 0.052 (0.647) | 0.665 | 0.503 | 0.9386 | 0.860 |
| v2-PE, new split, new tokenizer (Stage C) | 0.634 ± 0.024 (0.689) | 0.732 | 0.479 | 0.9599 | 0.880 |
| ATT+bal, new split, old tokenizer (Step 3b) | 0.627 ± 0.025 (0.653) | 0.711 | 0.535 | 0.9496 | 0.881 |
| v2-PE, new split, old tokenizer (Step 3b) | 0.596 ± 0.067 (0.683) | 0.718 | 0.445 | 0.9486 | 0.872 |

## Differences in pAUC@1e-2 (points; cluster bootstrap decides "resolved"; seeds up / down)

| comparison | v2-PE | ATT+bal |
|---|---|---|
| final − old split | −3.1, stratified [−4.3, −2.0], cluster [−6.0, −0.5], 4 / 6: **resolved worse** | +0.3, stratified [−1.3, +2.0], cluster [−1.9, +2.6], 5 / 5: not resolved |
| final − Stage C | +4.0, cluster [−2.6, +12.7], 8 / 2: not resolved | +11.9, cluster [+5.3, +19.4], 10 / 0: **resolved better** |
| final − Step 3b | +7.7, cluster [+0.9, +16.1], 9 / 1: **resolved better** | +8.3, cluster [+1.8, +16.7], 10 / 0: **resolved better** |

ATT+bal vs v2-PE (both final): +3.6, stratified [+1.5, +5.8], cluster [−1.6, +8.4], 7 / 3: **not resolved**. All other pairs, the TPR, AUC rows and the ensembles are in `tables.md`.

## Per family and the coinminer cluster (April, thresholds on the April benign scores; full tables in `tables.md`)

* Change of the detection rate against the old-split models, final models (v2-PE / ATT+bal, points): keylogger −0.1 / +0.7, trojan +0.2 / +0.3, rat −5.7 / −0.8, coinminer −7.6 / −1.3, backdoor −3.0 / −0.6, ransomware −1.3 / −0.6, dropper −2.5 / +1.4. The large drops of keylogger, rat and trojan seen with the group-split training part (−12 to −24 points) are gone for both final models (rat of v2-PE −5.7 is the largest left).
* Coinminer cluster (265 identical April reports): flagged by 5 of 10 final v2-PE seeds (median margin +0.1) and 0 of 10 final ATT+bal seeds (−4.2); old-split models 8/10 and 1/10; Stage C 7/10 and 0/10.
* The 1.0% false-positive rate on clean reports is true by construction (the threshold is set on the April benign scores). A threshold set on validation cannot be evaluated here: the validation slice is part of the training data of these models.

## Diagnostic observation (not part of the protocol)

Step 3b and Step 5 differ in one thing only: the 8,718 reports of the group-split validation slice are added to the training data (same tokenizer, settings, seeds and padding pool). That addition raises April pAUC@1e-2 by 7.7 points (v2-PE) and 8.3 points (ATT+bal), resolved for both, and brings ATT+bal back to the old-split level. The size of the effect for keylogger, rat and trojan is surprising, because Step 0 found that almost none of their April reports had a nearest January neighbour in that slice (keylogger 1.7%). **Guess, not tested:** the held-out reports carry something the model needs that edit distance between API-name sequences does not show.

## What this does not show

* Why the held-out slice matters so much (see the guess above); no experiment varied it directly (for instance by holding out a different group fold).
* That the final models are better than the old-split models: for ATT+bal there is no resolved difference, for v2-PE the final model is resolved *worse* (−3.1) than the old-split one. Differences of 1 to 3 points are of the size of the seed spread (SD up to 0.053 for v2-PE).
* Anything about false-positive control in deployment: all thresholds here are set on April benign data or not available.
* The old-split models and the final models differ in epochs (v2-PE 2 vs 1, ATT+bal 2 vs 3), the ATT+bal learning rate (2e-3 vs 1e-3) and seeds, besides the training set.
* Attacks were not run on these models (separate task); the weights are in the kernel outputs, not in the repo.

Files: `tables.md` (all tables, both bootstraps, seeds each way, per family, coinminer cluster), `results.json`, `bootstrap_stratified.json`, `logits_final_models.npz` (April scores of the 20 final models), `runs/gsx_*/seed*.json`. Code: `baseline/gs_grid.py --full-january`, `baseline/gs_eval_gen.py --mode full`, `baseline/v2pe.py --full-january`.
