# ATT+bal-2L: does reading 8 chunks of 512 tokens help? (plain-English summary)

**Short answer.** On the April test data, the two-level model (ATT+bal as level 1, a small transformer over the chunk vectors as level 2) is **about as good as ATT+bal and v2-PE on clean reports and not more robust against padding attacks**. We tried to make it better in a second round (a better training recipe); that changed little. What does help is **balanced padding during training**, with or without the two levels.

## What was built
* **Level 1** = the ATT+bal encoder (same size and settings), run on each chunk of 512 tokens (up to 8 chunks, 4,096 tokens, weights shared).
* **Level 2** = a small transformer over the chunk vectors (+ a [CLS] vector and a chunk-position vector), then one number per report (the score).
* **A** = trained with balanced padding (calls from benign training reports are added to half of the reports, 1 to 50 calls, at the front or inside). **B** = the same model without padding (the control).
* 10 seeds for every model. Choices were made on the validation slice only, never on April.

## Results (April; pAUC@1e-2 = how much malware is found at very low false-alarm rates, higher is better; mean of 10 seeds)
| model | clean pAUC@1e-2 |
|---|---|
| v2-PE | 0.705 |
| ATT+bal | 0.707 |
| A (round 1) | 0.687 |
| **A2 (round 2, better recipe)** | **0.699** |
| B (no padding, round 1) | 0.616 |
| B2 (no padding, round 2) | 0.627 |

* **Clean data:** A and A2 are not clearly different from each other (+1.2 points, not resolved). A2 is 0.8 points below ATT+bal (the stratified test says "resolved", the cluster test says "not resolved"); A2 versus v2-PE is not resolved. The padded model is clearly better than the unpadded one (A2 − B2 = +7.2 points, all 10 seeds, both tests).
* **Round 2 (`round2/`):** learning-rate decay, averaging of weights, lower rates for level 1, and a frozen level 1 were tried (6 settings × 10 seeds × 3 epochs). The setting picked on validation (level 1 frozen for the first epoch, checkpoint after epoch 1) is in effect "ATT+bal's encoder, unchanged, plus a trained level 2". None of the 36 candidates reached ATT+bal on April (0.627 to 0.701). The appendix `round2/appendix_april.md` lists all of them (it was not used for any choice).
* **Attacks (`attacks/`):** adding random calls, calls chosen by a surrogate model, and a white-box attack that picks calls to hide malware.
  * Padding in training is what protects: without it, the models collapse for 50 or more added calls; with it, 50 to 200 inserted calls still leave about 51 to 74% of malware flagged (1% false-alarm threshold).
  * A, A2 and ATT+bal are within a few points of each other. A was a few points better than ATT+bal for 50 to 200 calls; A2 is about the same as ATT+bal.
  * **All models fail when 100 or more calls are put at the front** (7 to 15% flagged): the training only showed up to 50 added calls.
  * The white-box attack gets every model, A and A2 included, down to a few percent after 50 steps. Padding only makes it need more steps (about 20 to 30 instead of 5).

## How to read the numbers
* Differences of one or two points are inside the spread between seeds (about 2 points) and should not be read as real unless the table says the rule is met (confidence interval excludes 0 **and** at least 7 of 10 seeds agree).
* The validation slice did not separate the models (all about 0.94 to 0.96) while April does (0.6 to 0.7), so the validation choice is weak evidence.
* Edited reports are built in memory only; only scores are saved.

## Where things are
* `clean/` and `clean_round2/` — clean April tables (per seed, ensembles, both bootstraps, per family, the coinminer cluster).
* `attacks/` — attack tables (`attack_tables.md`), figure `fig_detection_vs_k.png`, aggregates; scores are in `attack_scores/`.
* `loss_curves/` — training and validation loss of A, B, A2, B2 (`fig_loss_curves.png`, `curves.md`).
* `stage2/`, `selection.json`, `validation_table.md` — round 1 selection; `round2/` — round 2 selection (`selection.json`, `validation_table.md`, `runs/` seed files, `appendix_april.md`).
* Details and reasons for every step: `NOTES.md` sections 19 and 20; the summary section is `REPRODUCTION_REPORT.md` 5.14.
* Code: `baseline/twolevel.py` (training), `twolevel_select.py`, `twolevel_select2.py`, `twolevel_eval.py`, `twolevel_attack.py`, `twolevel_attack_report.py`, `twolevel_appendix.py`, `twolevel_curves.py`.
