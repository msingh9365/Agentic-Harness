# R1 - a windowed M3 (NOTES 30.3, 30.12, 30.13)

**In plain words.** M3 only sees the first 512 tokens of a report. An attacker can push the real behaviour out of that window by putting harmless calls at the start (about 100 calls are enough to blind M3). R1 is the same model, but trained on every 512-token window of the report; a report's score is the highest window score. On clean data R1 is a little worse than M3 (about 4.5 points of pAUC@1e-2; the difference is not resolved). Under padding it is far steadier: where M3 drops to 6.5% detection after 100 random calls are prepended, R1 stays at 69%.

Files: `choice.json`, `selection_tables.md` (January fold 9 only; variant b, 2 epochs chosen before any April logit), `clean_tables.md` / `results.json` / `bootstrap_stratified.json` / `logits_r1.npz` (April opening 32, once), `seen_unseen/`, `attack_A/` (M1, M3, M4, R1: Stage J rows + white-box), `attack_A_sets/` (all 12 sets, no white-box), `attack_B/` (M3, M3 + test-time multi-window max, R1, 13 sets incl. the adaptive one), `ci_A`, `ci_B` (cluster 95% intervals of every cell), `contrast_A`, `contrast_B` (pairwise differences with cluster intervals).

## Clean April (10 seeds, pAUC@1e-2 normalised, logits)
M1 68.6, M3 70.5, M4 66.1, M3 + test-time multi-window max 59.4, **R1 66.0** (AUC 0.929, TPR@1e-2 0.736). Differences (cluster 95% CI, seeds each way): R1 - M3 -4.53 [-16.58, +5.36] (0 up / 10 down), R1 - M4 -0.14 [-12.07, +8.60] (5 / 5), R1 - M1 -2.68 [-13.87, +5.94] (1 / 9), R1 - multi-window baseline +6.51 [-6.59, +17.91] (10 / 0). **None resolved** by the pre-registered rule (cluster interval of pAUC@1e-2 excludes 0).

## Seen / unseen (own training set)
Seen sequences: R1 0.859 vs M3 0.824 (R1 - M3 +3.54, cluster [+0.10, +9.65], 9 up / 1 down, resolved better). Unseen sequences: R1 0.565 (pAUC@1e-2); R1 - M3 -8.43 [-25.04, +6.25], not resolved (0 up / 10 down). See `seen_unseen/seen_unseen.md`.

## Attacks (detection at the 1% threshold, %, 10 seeds)
| set | M1 | M3 | M4 | M3 multi-window | R1 |
|---|---|---|---|---|---|
| unedited | 79.1 | 79.0 | 77.9 | 71.8 | 73.6 |
| random 50 prepend | 7.4 | 65.1 | 67.2 | 58.1 | 69.9 |
| random 100 prepend | 5.7 | 6.5 | 25.9 | 68.3 | 69.3 |
| random 200 prepend | - | 6.4 | - | 65.4 | 69.9 |
| random 200 insert | 18.9 | 44.3 | 37.5 | 38.4 | 50.5 |
| LightGBM 50 prepend | 1.9 | 35.1 | 48.5 | 58.0 | 65.4 |
| adaptive 50 random calls at the start of EVERY window | - | 65.1 | - | 53.8 | 64.0 |

Cluster-bootstrap contrasts (points, 95% cluster CI): R1 - M3 under random 100 prepend +62.9 [+48.8, +74.1], random 75 prepend +46.5 [+34.9, +57.3], LightGBM 50 prepend +30.3 [+13.5, +43.7] (all resolved); R1 - M3 under 20/50 prepend and inserts not resolved. R1 - multi-window baseline: only random 200 insert resolved (+12.1 [+1.4, +23.2]); on every other set the interval contains 0. Padded-benign FPR of R1 stays at about 1% (0.4 to 1.4% in every set; R1 - M3 at most +0.9 points, resolved up under long prepends, i.e. the extra detection is not paid for with false alarms beyond about one point).
**The adaptive set** (50 random calls at the start of every window, i.e. the attack that targets the windowing itself): R1 64.0 ± 6.0, M3 65.1 ± 5.7 (for M3 only the first window counts), multi-window baseline 53.8 ± 9.9; R1 - multi-window +10.2 [-4.0, +23.2], R1 - M3 -1.1 [-15.1, +9.5]: not resolved. R1 keeps 64% where the attacker does the most obvious thing against it; this is one attack with random calls, not a worst case.
**White-box greedy attack** (500 malware reports, 20 prepended calls per step up to 50, seeds 0-2 only for R1, pre-registered in 30.3): share still flagged after 50 steps at 1% FPR: R1 49.5 ± 2.9 (3 seeds), M3 2.5, M4 10.6, M1 0.6 (10 seeds each); padded-benign FPR after 50 steps 0.87%.

## Checks
Unedited scores equal the stored April logits for every seed (max difference 7.6e-6, `checks_*.json`); the re-scored plain M3 and its multi-window scores equal the stored Stage J and part-3 scores (max 7.6e-6 and 1.2e-5, `/tmp/r1_comb/assemble_checks.json`); no seed with April AUC < 0.6.

## Limits
Clean cost about 4.5 points of pAUC@1e-2 against M3 (not resolved; seeds 0 up / 10 down so I would not call it zero); one tokenizer; one adaptive attack; the white-box result is on 3 seeds; one April; windows of stride 512 and at most 64 windows, so reports longer than 32,768 tokens are cut. White-box for R1 uses the same 500 reports and greedy search as M1, M3, M4, but 3 seeds only (cost), so its cluster interval is for those 3 seeds.
