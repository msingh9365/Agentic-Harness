"""Shared wording of the audit (status label, compute note, April-use note). Used by review_compose.py, tune_compose.py and audit_compose.py."""
STATUS_511 = "**Status: preliminary. The GPU scoring of the attacks in this section (surrogate-chosen padding, white-box attack, random-padding test, probe) is to be re-run on the author's own Kaggle account.**"
STATUS_512 = "**Status: preliminary. The training and the scoring of this section are to be re-run on the author's own Kaggle account.**"
STATUS_RESULTS = "**Status: the attack scoring of the review experiments (§5.11) and the whole tuning section (§5.12) are preliminary and are to be re-run on the author's own Kaggle account.**"
LIMITS_COMPUTE = ("- **Preliminary GPU results.** The attack scoring of §5.11 (surrogate-chosen padding, white-box attack, random-padding test, probe) and the training and scoring of §5.12 are preliminary and are to be re-run on "
                  "the author's own Kaggle account. The scoring pipeline reproduces the stored April logits of the unedited reports (largest difference 3e-5) and the random-padding edits equal the arrays of REPORT 5.10 token for token "
                  "(checked on 600 reports x 6 edits).")
APRIL_NOTE = ("**How often April was used.** April 2022 (17,402 reports, 2,509 distinct API sequences) is the only test set and every experiment of this report scored it: A, B, B2, B3, C, D, E, F (its recipe grid stored the April numbers of "
              "every recipe and epoch but was selected on validation numbers), the pAUC re-scoring (§5.8), v2-PE (§5.9), ATT and ATT+bal (§5.10), §5.11 and §5.12: 13 scoring rounds on the same reports. "
              "Within an experiment April was used once per model family (EVAL_PROTOCOL.md §4), and to my knowledge no hyper-parameter was selected on April numbers; from F on, settings were chosen on the validation slice. "
              "But the sequence of questions was shaped by April results of the previous round (v2-PE after the gap analysis, ATT+bal after v2-PE, keep/aug and the attacks after ATT+bal, the tuning after the attacks), "
              "so April is not an untouched holdout for the thesis claims, and the confidence intervals do not account for the repeated use. In §5.12 the April logits of all 16 candidates were stored and opened only after the choice was written down.")
