# Evaluation protocol for the thesis experiments

**Date: 2026-11-18. Committed before any thesis experiment was run.** It fixes what is measured, how a model is tuned, and when a difference may be called a result.
Everything in it is about the Nebula-style detection task on the published Speakeasy data (train = January 2022, test = April 2022). The reproduction that this protocol builds on
is `REPRODUCTION_REPORT.md` (§4 metrics, §5.7 baseline v2, §5.8 partial AUC); the code is `baseline/common.py` (`pauc`, `roc_summary`), `baseline/long_stats.py` (`bootstrap`, `paired`) and `baseline/pauc_report.py`.
The protocol applies to **new** experiments. The baseline v2 recipe and the B3 settings were chosen on validation TPR@1e-3 before this protocol existed; that stays as it is and is not redone.

## 1. Data, splits, seeds

| item | fixed value |
|---|---|
| Training data | January 2022, 75,298 reports (the published `quo-vadis-malware-emulation` train folder) |
| **Validation slice** | the held-out 10% of January of follow-up F: 7,530 reports (2,467 benign, 5,063 malware), `train_test_split(test_size=0.1, stratify=family, random_state=2025)`, indices hashed in `baseline/gap_split_hash.json` (`b18269395891ee1e51d69e4a7293f0af`); the hash is asserted in every run. **Never trained on.** |
| Training set of a model | the other 90%: 67,768 reports |
| **Test set** | April 2022, 17,402 reports (8,003 benign). Used once per experiment (see §4) |
| Seeds | **0 to 9** for every model, new and baseline. A new model is trained with the same data, the same validation slice and the same 10 seeds. Seed k of a new model is compared with seed k of the baseline |
| Tokenizer | the baseline's BPE-50k (`baseline_models/tokenizers/bpe50k`, fit on all 75,298 January reports) unless the tokenizer is the object of study. **Known limitation:** it was fit on text that includes the validation slice (unsupervised, no labels; follow-up F's tokenizer test, R3, found no effect of the tokenizer). It is kept for comparability with the baseline |
| Sequence length / architecture of the baseline | 512 tokens; `TransformerEncoderChunks`, chunk size 64, 2 layers, 8 heads, dModel 64, dHidden 256, head [64], dropout 0.3, flatten pooling (5.4 M parameters) |

## 2. Metrics

All metrics are computed on **logits** (the raw model output). The probability after the sigmoid in float32 saturates to exactly 1.0 above a logit of about 17 and creates ties; the literal float32 TPR@1e-3 is therefore never used (REPORT §4).

**Primary metric: partial AUC at FPR 1e-2, normalized (pAUC@1e-2), April test set.**
`pauc(y, logits, max_fpr)` (`baseline/common.py`) = the area under the ROC curve for FPR in [0, max_fpr] (the curve interpolated linearly at exactly max_fpr) **divided by max_fpr**. It is the mean TPR over FPR in [0, max_fpr]: 1.0 for a perfect ranking, `max_fpr / 2` (0.005 at 1e-2) for a random one.
It is used because TPR@1e-3 rests on 8 allowed false alarms in the April set and is too noisy (REPORT §5.8: the per-seed std of pAUC@1e-2 is 1.5 to 4 times smaller relative to its mean than that of TPR@1e-3). sklearn's McClish-standardized value (`pauc_mcclish`) is stored next to it for papers that use that form; it is not used for decisions.

**Secondary metrics, always reported, never the basis of a claim alone:** TPR@1e-3, TPR@1e-2, AUC, F1 at logit 0 (P(malware) = 0.5), pAUC@1e-3. The metric function `common.binary_metrics` returns all of them (and `roc_summary` the five that are resampled by the bootstrap).

## 3. Baseline

**`bpe_v2`, 10 seeds** (`load_baseline("bpe_v2", seed=k)`, k = 0 to 9; recipe in `baseline_models/README.md`): AdamW, lr 2e-3, weight decay 1e-2, batch 96, dropout 0.3, gradient clipping 0.5, the authors' `ModelTrainer`, 90% of January, **2 epochs**.
Reference numbers (April test, logit-ranked, mean ± std over the 10 seeds) are in REPORT §5.8; they are not repeated here so that this file does not go stale. The released checkpoint of the authors and the previous recipe (REPORT §5.1) are context, not baselines.

## 4. Tuning of a new model (everything on the validation slice)

1. **The grid is written down before training** (in the experiment's `NOTES.md` entry): the learning rates and the epoch range (and every other hyper-parameter that is tuned), each cell run with all 10 seeds. The number of cells is fixed in advance; no cell is added after results are seen.
2. After every epoch the **validation** metrics and the validation loss are recorded. The April logits may be stored but **not printed or looked at** until the setting is chosen.
3. **Selection metric: the mean over the 10 seeds of validation pAUC@1e-2** (more stable than validation TPR@1e-3, which allows only 2 false alarms on the 2,467 validation benign reports). Let `best` be the cell (hyper-parameters, epoch) with the highest mean and SE its standard error (std over seeds / sqrt(10)).
   Every cell whose mean is within one SE of `best` is **tied** with it. Among tied cells choose the **fewest epochs**, then the **lower mean validation loss**. If the number of free hyper-parameters or the budget differs between a new model and the baseline, say so in the report.
4. **Collapse guard:** a cell in which any seed has validation AUC < 0.6 at its last epoch (a constant predictor) is excluded and reported.
5. The test set is evaluated **once, for the chosen setting**. The test numbers of every cell of the grid go into an **appendix marked "not used for selection"**.
6. The baseline is not re-tuned by this rule; the same budget of tuning for the baseline is not claimed. The comparison is "the baseline recipe against the best setting of the new method found by §4".

## 5. Reporting and the claim rule

- Per model: the per-seed values and mean ± std of the primary and the secondary metrics (single models), and the same metrics for the **10-seed ensemble** (the mean of the 10 logits per report).
- **Statistics (the method of B2, B3, F):** stratified bootstrap over the April test reports (malware and benign resampled separately, **1,000 resamples**, numpy seed 0, the same resamples for every model), applied to the per-seed mean of the metric (`ps`) and, as a robustness check, to the 10-seed ensemble (`ens`). The CI is the 95% percentile interval. It measures the noise of the finite test set; the seed-to-seed spread is reported next to it (per-seed std, number of seeds with a positive difference).
- **A difference between two models counts as a result only if both hold:**
  (a) the paired bootstrap 95% CI of the **primary metric** (per-seed means) **excludes 0**, and
  (b) the per-seed difference of the primary metric (same seed index) is **positive in at least 7 of the 10 seeds** (for a claim that the new model is better; negative in at least 7 for worse).
  Anything else is reported as **not resolved** (not as "equal").
- The ensemble statistic is reported next to the single-model one. If they disagree (for example a difference that is resolved for single models and not for ensembles), both are stated; the claim is about single models, and the ensemble result is stated as a limit of the claim.
- Claims on a secondary metric are descriptive. A difference that is resolved on a secondary metric but not on the primary one is reported as such and is not a claim.
- Results are stated at the operating point where they hold: pAUC@1e-2 (1e-2 FPR) is the point of the claim; TPR@1e-3 (8 false alarms) is reported with its noise, and a statement that rests on it alone is marked as fragile.

## 6. Optional second test bed: few labels (the B3 setup)

For methods that use unlabeled data: 20% of the labeled 90% for fine-tuning, the remaining 80% unlabeled, **BPE-8k `bpe8k_v2`** (fit on the 90% only), the splits of `baseline/b3_split_hashes.json` (asserted), the same validation slice, compared with the B3 lower bound and the B3 AR/MLM runs (REPORT §5.2c).
The same rules (§4 for tuning, §5 for claims) apply, with 10 seeds: the B3 runs exist for seeds 0 to 4; seeds 5 to 9 use the same split function (`baseline/b3.py: b3_split`, `random_state = seed`), their hashes must be written to `baseline/b3_split_hashes.json` before use, and the B3 reference runs must be re-run for seeds 5 to 9 with the B3 settings
(lr and epoch as chosen in B3, `results/B3_selfsup_v2/choice.json`) before a 10-seed comparison is made. With 5 seeds only the claim rule cannot be applied (7 of 10); results are then reported as exploratory.

## 7. What this protocol does not claim

- The baseline recipe and B3's settings were chosen on validation TPR@1e-3, not on pAUC@1e-2; they were not re-selected.
- The April test set is one fixed sample: the bootstrap covers its finite size, not a change of distribution between months, and the seeds cover training noise only.
- The published data is not the paper's data (REPORT §6.1); absolute numbers are not comparable with the paper's tables.
