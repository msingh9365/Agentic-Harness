# Briefing for the planner

State of the thesis experiments on branch `nebula-baseline` after the review experiments (REPORT 5.11), the tuning (5.12) and the audit (5.9a, 5.13). Everything described here is pushed.

## Where the thesis numbers are

- Branch `nebula-baseline`. The branch `nebula-length-study` is superseded only for its ATT+bal numbers (rounds 4b and 5: old recipe, released tokenizer); its other analyses are unaffected (`SUPERSEDED.md` there).
- Documents: `RESULTS_FOR_REVIEW.md` (summary), `REPRODUCTION_REPORT.md` sections 5.9a and 5.10 to 5.13 (details), `NOTES.md` sections 15 to 18 (pre-registrations and logs), `EVAL_PROTOCOL.md` (rules).
- `RESULTS_FOR_REVIEW.md` and sections 5.11 to 5.13 of the report are generated: `review_compose.py`, then `tune_compose.py`, then `audit_compose.py`. Do not hand-edit the generated parts.

## What the evidence supports (April, 10 seeds)

- **Clean accuracy.** Nothing beats v2-PE on pAUC@1e-2 under the claim rule. ATT+bal is +0.23 points (CI -1.70 to +2.09); its 10-seed ensemble is 3.4 points lower. The 1% FPR gap of ATT+bal (TPR@1e-2 -1.65 points) is descriptive, not a claim.
- **Released checkpoint.** "v2-PE and ATT+bal beat the released checkpoint" holds under the report-level bootstrap but not under the cluster bootstrap over the 2,509 duplicate groups (v2-PE: CI -2.48 to +13.20; ATT+bal: CI -4.64 to +15.28).
- **Robustness.** Balanced padding gives large robustness: at k = 20 to 50 PE+bal and ATT+bal still flag 64 to 77% of the malware, against 8 to 22% for v2-PE with prepended calls. Attention pooling adds robustness only against large amounts of prepended padding. Keeping the clean copies did not help. Malware-only padding creates a shortcut (PE+aug flags 99.7% of the benign reports at k = 50).
- **Tuning (5.12).** It did not close the 1% FPR gap and cost some robustness.
- **Further attacks (5.13).** Rotation of the call list is the hardest edit and raises benign false alarms to 10 to 15% for the balanced models; argument injection takes v2-PE from 81% to 47% flagged; test-time deduplication does nothing for v2-PE.

## Caveats the plan must account for

- **Validation overlap.** 94.2% of the validation slice shares its API sequence with the training slice (April: 36.4%). On the 433 unseen validation reports v2-PE drops from pAUC@1e-2 0.962 to 0.673; the 5.12 rule applied to the unseen part would choose another candidate. The v2 recipe and the B3 choices cannot be re-checked without retraining (no per-epoch validation logits). Redo plan: NOTES 17.
- **Tokenizer.** Unknown pieces (mostly the letter "j") get id 0, which is also the padding id (5.9a). Not fixed.
- **Report length.** Only 36.6% of the April reports fit into 512 tokens (30.4% of the malware).
- **April use.** April was used in 13 scoring rounds on the same reports; it is not an untouched holdout (note in both documents).
- **Wording rules for anything new.** Mark GPU results "preliminary, to be re-run on the author's own Kaggle account"; call results on secondary metrics "descriptive"; use "RESOLVED" only for pAUC@1e-2 under the claim rule (CI of the per-seed means excludes 0 and the same sign in at least 7 of 10 seeds); do not describe which Kaggle account was used.

## The paused `thesis-final` plan (nothing of it has started)

- **Stage 6 cost.** My estimate is about 6 to 8 session-hours with the attacks as specified, against the 3 h cap; it needs a scope decision before launch.
- **Benign families.** Benign reports have only two families, `clean` (32,377) and `windows_syswow64` (294); a "benign source" subset is not available in the data.
- **Group split.** January has 6,771 distinct API sequences and the largest holds 4,312 reports (5.7%); a group-split validation fold will be uneven.
- **Argument injection** needs the original call texts, so it can only be built on a machine that has the original reports (it ran on CPU here).
- **GPU cost references.** A 4-epoch tuning cell took about 0.45 session-hours; scoring one full model family from the call store about 25 minutes. The unit "GPU hour" of the cap must be defined (session hours or device hours).

## Rules that carried through

- Pre-register before training and commit it; open April once, after the choice is written; nothing is tuned on April.
- Edited reports exist in memory only; only scores are saved.
- Never print or commit tokens; keep kernels and datasets private.

## Open decisions for the author

1. Delete the old edited-token artifacts? They are `results/att_bal/pad/april_pad.npz` in git history (commit `6f22129`) and the Kaggle datasets `nebula-v2pe-padtest` and `nebula-v2pe-augb`. Removing the file from history needs a force-push.
2. Scrub the second-account mentions in the pre-registered sections 15 and 16 of `NOTES.md` (left as written)?
3. Go ahead with the `thesis-final` plan with a reduced Stage 6, or do the group-split redo (NOTES 17) first?
