# How was the released Nebula Speakeasy model trained?

**Short answer: the recipe of the released file `nebula/objects/bpe_50000_torch.model` is not documented.**
The repository has no script, log or text that says which data, how many epochs or steps, which batch
size or whether it was pretrained. What exists are the paper's general setup and example scripts for
*other* runs. Paths are in the Nebula checkout `../nebula` (commit `1343ae1`).

## What the repository says about the released model

| Question | Finding | Where |
|---|---|---|
| Data | Not stated for the model file. The README only points to the Speakeasy dataset "used for experiments and pretraining". | `README.md:24` |
| Pretraining | Not stated. The README calls the files "pretrained objects" and says the model is "pre-trained only for 50k" vocabulary and 512 tokens; the SSL section only names the trainer classes (`MaskedLanguageModelTrainer`, `AutoRegressiveModelTrainer`) and says evaluation is future work. | `README.md:96`, `README.md:109-110`, `README.md:198-206` |
| Does the file contain an LM head? | No. Its 30 tensors contain no `pretrain_layers` keys (checked), so the file itself cannot show whether it was pretrained. One example script removes LM layers "if present" before loading it. | `scripts/train_example_torch.py:66` |
| Epochs, steps, batch size, LR | Not stated for the model file. | nowhere |
| How it is used | Loaded into `TransformerEncoderChunks` (d_model 64, 8 heads, feed-forward 256, 2 layers, chunk 64, head [64], dropout 0.3, pre-norm, flatten pooling). | `nebula/__init__.py:95`, `:138-160` |
| History of the file | Added 2023-12-22 ("pip object config", `da449cf`), replaced 2024-01-05 ("Transformer model unification", `9c7dbec`) and 2024-02-20 ("fix of pretrained objects after model class update", `22101ec`). The file was re-saved after class changes; no commit message records epochs, data or a recipe. | `git log -- nebula/objects/bpe_50000_torch.model` |

## Example scripts in the repository (not the released model's recipe)

| Script | Settings | Lines |
|---|---|---|
| `scripts/cross_validation/_speakeasy_model_loop.py` (from-scratch, 3-fold CV; the setup I reused in `results/pooling`) | 2 epochs, batch 64, AdamW lr 2.5e-4, "step" scheduler with an optimiser-step budget of 3000 (the scheduler multiplies the LR by 0.5 every budget/3 = 1000 steps), 3 folds. The file is set to a 1000-sample test run (`LIMIT = 1000`). | `:29-30`, `:54-61`, `:176-181`, `:191-194`; scheduler in `nebula/__init__.py:266-268` |
| `scripts/train_example_torch.py` (fine-tunes *from* the released weights) | batch 96, AdamW lr 3e-4, grad clip 1.0, 5-minute time budget, trained on the Speakeasy training set | `:79-92` |
| `scripts/nebula_pe_to_preds.py` (optional training block, off by default) | batch 96, AdamW lr 2.5e-4, weight decay 0.01, clip 1.0, 5-minute budget | `:28-55` |
| `scripts/train_example_lit.py` (Lightning) | 2 epochs, one-cycle schedule, batch 256 | `:88-92` |

## What the paper says (arXiv 2310.10664; the project contains no copy, I read the arXiv PDF)

| Item | Paper | Section |
|---|---|---|
| Speakeasy data | about 93,500 reports; training set collected January 2022, test set April 2022 | 4.1 Datasets |
| Optimiser, batch | batch size fixed at 96; AdamW, static learning rate 2.5e-4, betas 0.9/0.999, weight decay 1e-2; GPU: NVIDIA Quadro T2000 | 4.2 Experimental Setup |
| Training length | a constant **time budget instead of epochs**: 5 minutes per cross-validation fold, 15 minutes for 3 folds; a longer run (about an hour) gave similar relative outcomes. Steps reached in 5 minutes are not stated. | 4.2 |
| Validation | metrics are means over 3 cross-validation folds on the training set, plus a single test set | 4.2 |
| Self-supervised pretraining | tested separately with a vocabulary reduced to 8,192 (not the released 50k) and 80% / 20% pretrain / fine-tune splits; masked LM did worse than the supervised baseline at low FPR | 4.5 |
| Released models | "trained on just 70k samples" (the January training set has 75,298 reports in this repository); no epochs, steps or pretraining mentioned | 6 (Limitations) |

## Conclusion for the retraining

- **Documented:** architecture; AdamW at lr 2.5e-4 with weight decay 0.01 (paper and scripts); batch 96 in the paper and 64 in the cross-validation script; a time budget of 5 minutes per fold in the paper.
- **Not documented:** epochs or steps of the released model; whether it was trained on all of January or on a cross-validation fold; whether it was pretrained; learning-rate schedule (the paper says a static rate, the cross-validation script uses a step schedule); early stopping; seeds.
- **Consequence:** "the released model's step budget" cannot be taken from the repository. The only step budget written down is the 3000 optimiser steps of the cross-validation script, so that is the proxy I use (about 2.9 epochs at batch 64 on the 65,679-report January training side). It is a proxy, not a measurement of the released model.
- **Likely relevant (inference, not documented):** the REPORT.md note that released Nebula reaches validation AUC 0.999 on the January validation side suggests it saw those reports in training, so it probably used all of January (75,298 reports), not the 65,679 of my training side.
