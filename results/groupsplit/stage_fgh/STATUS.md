# STATUS of the unattended run (Stages F, G, H of NOTES 23; CPU follow-ups P1 and P2 of NOTES 24)

Written 2026-11-22. **All stages ran to the end; no automatic check fired and nothing was stopped.** Everything is committed LOCALLY on branch `nebula-baseline`; **nothing was pushed** (last pushed commit `45de642`). The stop hook asked for a push after almost every step; it was refused because of the instruction "DO NOT push".

## What ran

| part | what | kernel(s) and owner | GPU / quota used (estimate in NOTES 23) | result |
|---|---|---|---|---|
| Stage F | selection of the M2 and M4 settings on the group-split validation slice (30 runs, 5 seeds, 3 epochs, no April logit) | `nebula-fgh-f`, **manishsinghxdev** | 1.66 h quota on two T4 (estimate 1.6 h, limit 4.8 h) | NOTES 23.1, `stage_f/` |
| Stage G | M2 and M4 trained on all of January, 10 seeds, one April evaluation; loss-log reruns of M1 and M3 for the figure | `nebula-fgh-g-2l` (M2, M4: about 0.46 h), `nebula-fgh-g-attbal` (0.35 h), `nebula-fgh-g-v2pe` (about 0.1 h), **manishsinghxdev** | about 0.9 h quota (estimate about 1.4 h, limit 4.2 h) | NOTES 23.2, `stage_g/` |
| Stage H | attacks on M1 to M4 (random and LightGBM padding, white-box greedy, per family) | `nebula-fgh-h-scores` (0.60 h), `-h-wb-m2` (1.09 h), `-h-wb-m4` (1.58 h), `-h-wb-m1m3` (0.52 h), **msingh9365** | about 3.8 h quota (estimate about 11 h, limit 33 h) | NOTES 23.3, `stage_h/` |
| P1 | unknown pieces: id, counts, which strings | CPU kernels `nebula-p1-unk-smoke`, `nebula-p1-unk-strings` (28.5 min), **manishsinghxdev**, no GPU | none | NOTES 24.1, `p1/` |
| P2 | April seen / unseen columns for all models | local CPU, stored logits only | none | NOTES 24.1, `p2/` |

GPU: Kaggle T4 (two per kernel). No kernel was duplicated on two accounts. Only one account was used per stage (F, G, P1: manishsinghxdev; H: msingh9365; the token for msingh9365 is the environment's `KAGGLE_ACCESS_TOKEN`, the default `KAGGLE_API_TOKEN` is manishsinghxdev). No token was printed or committed.

## Chosen settings (Stage F, by the rule fixed in NOTES 23, validation numbers only; committed before Stage G)

- **M2** (two-level, no padding): lr 1e-3, scratch, **epoch 1** (mean validation pAUC@1e-2 0.578, SE 0.024; best candidate lr 2e-3 epoch 2 = 0.604, tied within one SE; the tie rule takes fewer epochs).
- **M4** (ATT+bal-2L, balanced padding before chunking): lr 1e-3, scratch, **epoch 1** (0.454, SE 0.010; also the best candidate). No warm-start candidate was chosen.
- Full tables: `stage_f/validation_tables.md`, `selection.json`.

## Headline: April, final models trained on all of January, 10 seeds (Stage G, NOTES 23.2)

| model | pAUC@1e-2 (per-seed mean ± std) | ensemble | TPR@1e-3 | AUC |
|---|---|---|---|---|
| M1 v2-PE | 0.674 ± 0.053 | 0.739 | 0.541 ± 0.095 | 0.9667 |
| M2 two-level, no padding | 0.562 ± 0.146 | 0.675 | 0.344 ± 0.189 | 0.9670 |
| M3 ATT+bal | 0.710 ± 0.015 | 0.731 | 0.590 ± 0.029 | 0.9694 |
| M4 ATT+bal-2L | 0.663 ± 0.036 | 0.725 | 0.461 ± 0.174 | 0.9679 |

Differences in points (resolved = the cluster interval of pAUC@1e-2 excludes 0; seeds up / down): M2 - M1 -11.16 (cluster -15.8 to -6.1; 3/7) **resolved worse**; M4 - M3 -4.73 (-9.5 to +0.9; 1/9) not resolved; M4 - M2 +10.05 (+4.1 to +16.3; 8/2) **resolved better**; M3 - M1 +3.63 (-1.6 to +8.4; 7/3) not resolved. Per family, coinminer cluster and the loss figure (`fig_loss_curves_four_final_models.png`) are in `stage_g/`. In this reproduction the two-level models do not beat the one-chunk models.

## Headline: attacks (Stage H, NOTES 23.3; detection of April malware at the 1% FPR threshold, %)

| edit | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| unedited | 78.0 | 75.1 | 79.0 | 77.8 |
| random 20 prepend | 24.5 | 52.7 | 76.6 | 73.8 |
| random 50 prepend | 9.0 | 24.1 | 66.4 | 67.5 |
| random 100 prepend | 6.5 | 11.9 | 6.8 | 26.2 |
| random 200 insert | 19.0 | 11.2 | 45.4 | 37.5 |
| LightGBM 50 prepend | 3.8 | 13.1 | 36.3 | 49.5 |
| white-box, 50 steps | 1.0 | 13.4 | 2.4 | 15.1 |

The padded-benign false-positive rate stays at or below the clean rate in nearly all cells. The padding-trained models (M3, M4) hold up against 20 to 50 random calls and fail at 100 prepended calls and against the white-box attack. The two-level models show no robustness advantage over their one-chunk counterparts. All 17 edit sets, both thresholds, per-family rows and `fig_detection_vs_k_four_models.png` are in `stage_h/`.

## Headline: P1 and P2 (NOTES 24.1)

- **P1:** unknown pieces get id 0, the padding id. 66.7% / 60.2% / 64.0% of the reports (January training / validation / April, whole report; median 4 unknown tokens) and 32.8% / 30.7% / 21.7% of them within the first 512 tokens contain at least one. **The decision rule triggered: the fix is planned and merged into P3, not run.** Nearly all unknown tokens are one letter: the character `j` (99.94% of the January unknown tokens), which the old BPE-50k has no piece for; words such as `getstockobject`, `waitforsingleobject`, `deleteobject`, `jan`, `june` become unknown at that letter. A dedicated id for unknown pieces would not restore these words; a refit that covers every character would. The choice is the owner's (NOTES 24.1).
- **P2:** every model scores much lower on April reports whose API sequence is not in its own training set (final models pAUC@1e-2 seen / unseen: M1 0.793 / 0.617, M2 0.677 / 0.513, M3 0.834 / 0.650, M4 0.817 / 0.585); the same pattern holds for the Stage C, old-split and two-level A and B models. The final-model comparisons keep the order of the overall table (M2 - M1 resolved worse on both subsets; M4 - M2 resolved better on the seen subset only). Descriptive: the two subsets also differ in families and size.
- **P3 and P4** are pre-registered in NOTES 24 and were not run (no GPU run was started). April openings still to come if both are run: 22 (P3) and 23 (P4); Stage G was opening 20 and Stage H 21.

## Anything unusual

- Stage F waited in the Kaggle queue after the launch at 20:16 UTC and ran for 1.66 h; all other kernels started within minutes.
- `baseline/gs_eval_g.py` reads the Step 5 logits of M1 and M3 from `stage_d/step5/logits_final_models.npz` (the run folders hold only the JSONs); the loss-log reruns of M1 and M3 in Stage G reproduce those logits exactly (max difference 0.0, 10 seeds each), and their weights are sha256-equal to the Step 5 weights used in Stage H.
- In Stage H every job reproduced the stored April logits from the unedited scores (M1 up to 3e-5, M2 to M4 0.0; tolerance 2e-3).
- A first P1 smoke kernel failed because the dataset of the old tokenizer has no `tokenizer.model`; the old tokenizer files were published as the small private dataset `manishsinghxdev/gs-old-tokenizer` (vocabulary asserted equal to the old one) and the job was rerun. No result was affected.
- Small slips corrected in the record: the STATE note for the Stage H launch first said 00:35 UTC (real: 00:12 UTC); the Stage H figure had a literal backslash-n in a y-label (fixed, figure regenerated from the same scores).
- Stage F outputs contain no April logit; the selection (commit `ff0fbd2`) was committed before the Stage G kernels were launched. No April number was used for any choice.
- The seed spread of M2 and M4 is large in every table (for example one M2 seed has an in-sample validation pAUC of only 0.61), so their means move with the seed set.
- The Kaggle datasets published for this run (all private): `manishsinghxdev/gs-3b-attbal-weights`, `gs-final-attbal-weights`, `gs-attack-smoke`, `gs-old-tokenizer`; `msingh9365/gs-final-models` (weights and April logits of M1 to M4, about 640 MB) and the earlier copies of `nebula-tune-inputs` and `nebula-groupsplit`.

## Where things are

`NOTES.md` sections 23 (plan, 23.1 to 23.3 results) and 24 (P1, P2 results, P3 and P4 plans); code in `baseline/` (`twolevel.py`, `gs_select_f.py`, `gs_eval_g.py`, `gs_fig_g.py`, `gs_attack.py`, `gs_attack_report.py`, `gs_unk.py`, `gs_unk_strings.py`, `gs_seen_unseen.py`); results in `results/groupsplit/stage_fgh/`; progress log `STATE.md`. Model weights and the downloaded Kaggle outputs are not in the repository (weights are in the Kaggle datasets above).
