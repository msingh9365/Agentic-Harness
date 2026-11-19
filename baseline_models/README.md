# Baseline models (Nebula reproduction)

Trained models, tokenizers and a loader for the baseline reproduction of Nebula (Trizna et al., arXiv 2310.10664v2) with the
authors' own code. The numbers and how they compare with the paper are in [`REPRODUCTION_REPORT.md`](../REPRODUCTION_REPORT.md).

## Baseline v2-PE: the thesis baseline (v2 recipe + the positional encoding of the paper)

```python
m = load_baseline("bpe_v2_pe", seed=0)   # seeds 0 to 9; manifest keys detect/bpe50k/v2_pe/seed<k>; m.score_logit(report) (rank by logit)
```

Identical to baseline v2 below (recipe, data, tokenizer, 2 epochs) except `pe_mode="paper"` (`baseline/pe.py`): the sinusoidal encoding of Eq. 1-2 of the paper is added by **global token position** 0..511 (the chunk at index c gets positions 64c..64c+63; padding tokens get their position too), instead of the released code's vector of position 0 at every token. Same seed = same initial weights and data order as v2.
April test (logit-ranked, 10 seeds): pAUC@1e-2 **0.705 ± 0.031**, TPR@1e-3 0.543 ± 0.063, TPR@1e-2 0.811 ± 0.023, AUC 0.9644 ± 0.0093, F1 0.915 ± 0.012 (v2: 0.690 / 0.527 / 0.788 / 0.9624 / 0.901). By the claim rule of `EVAL_PROTOCOL.md` v2-PE is not shown better than v2 (pAUC@1e-2 +1.45 points, positive in 6 of 10 seeds) but is better than the released checkpoint (+4.6, 9 of 10 seeds); REPORT §5.9.
**Its logits are larger than v2's** (mean |logit| 28.5 against 17.7): the float32 sigmoid saturates for most malware reports, so the literal float32 TPR@1e-3 is useless (0.06): always rank by logit. v2 is kept as the reproduction of the released code. Logits: `results/logits/v2_pe.npz`.

## Baseline v2: THE baseline from follow-up F on (reproduction of the released code)

```python
m = load_baseline("bpe_v2", seed=0)      # seeds 0 to 9; manifest keys detect/bpe50k/v2/seed<k>
m.score_logit(report)                    # rank reports by this (the logit); m.score(report) = sigmoid(logit) saturates at logit 16.6
```

Exact recipe (code: `baseline/gap.py`, recipe `R8_lr2e-3`; the authors' `ModelTrainer`, `TransformerEncoderChunks`, patched submodule at the pinned commit):

| setting | value |
|---|---|
| model | `TransformerEncoderChunks`, chunk 64, 2 layers, 8 heads, dModel 64, dHidden 256, head [64], flatten pooling, dropout 0.3, 5.397 M parameters |
| tokenizer | our BPE-50k (`tokenizers/bpe50k`), 512 tokens |
| optimizer | AdamW, **lr 2e-3**, weight decay 1e-2, constant lr, no schedule; BCE loss; gradient clipping 0.5 (their default); batch 96 |
| data | **90% of the January training reports** (67,768; family-stratified; split seed 2025, indices hashed in `baseline/gap_split_hash.json`); the other 10% (7,530) is the validation slice |
| training length | **2 epochs** (1,412 batches), chosen on the validation slice (best mean validation TPR@1e-3, agreed by early stopping on the validation loss) |
| seeds | **0 to 9** (`C.set_seed(seed)`); seeds 5 to 9 were added later with the identical recipe and the asserted split |
| selection | everything on the validation slice; the April test set was not used for any choice (`NOTES.md` §10.10, §10.11; `REPRODUCTION_REPORT.md` §5.7) |

April test numbers (logit-ranked, mean ± std over the **10 seeds**): TPR@1e-3 **0.527 ± 0.082**, TPR@1e-2 0.788 ± 0.026, AUC 0.9624 ± 0.0050, F1 (0.5) 0.901 ± 0.016, **pAUC@1e-2 (primary metric of `EVAL_PROTOCOL.md`) 0.690 ± 0.036**, pAUC@1e-3 0.381 ± 0.110; the released model: 0.518 / 0.750 / 0.9586 / 0.885 / 0.659 / 0.372. (Seeds 0 to 4 alone: 0.561 ± 0.043 at TPR@1e-3; the halves agree within seed noise, REPORT §5.8.)
Literal float32 TPR@1e-3: 0.317 ± 0.280 over the 10 seeds (several seeds saturate to 0.0): always rank by logit. Logits of every baseline model are in `results/logits/` (git), so metrics can be recomputed without the models. Each manifest entry lists its validation and test metrics.
Do **not** train much longer or with a larger lr: lr 5e-3 and 1e-2 collapse to a constant predictor, and more epochs over-train (validation TPR@1e-3 falls and the loss rises after epoch 2).

## Where the files are

| what | where | size |
|---|---|---|
| `manifest.json`, `load_baseline.py`, tokenizer files (`tokenizers/bpe50k`, `ws50k`, `bpe8k`) | this folder (git) | small |
| AR-pre-trained encoders **before fine-tuning**, 3 epochs, seeds 0 to 4 (`ssl/ar_pretrained_seed*.pt`) and the **15-epoch** ones (`ssl/ar_pretrained_long_seed*.pt`, best epoch = 15) | this folder (git) | about 5 MB each |
| Everything else: detection and classification fold models, all fine-tuned self-supervised models | private Kaggle dataset **`msingh9365/nebula-baseline-models`** (it also contains the files above, so one folder is enough) | about 1.8 GB (includes the 5 baseline-v2 models, `detection/bpe50k/v2/seed*.pt`, 22 MB each) |

Point the loader at the folder that holds `manifest.json` and the weights:

```bash
kaggle datasets download -d msingh9365/nebula-baseline-models -p baseline_models_full --unzip
export NEBULA_BASELINE_MODELS=$PWD/baseline_models_full
```

## Use

```python
from baseline_models.load_baseline import load_baseline, list_baselines

list_baselines()                                    # all keys
m = load_baseline("detect/bpe50k/time/seed0/fold0")       # detection, BPE tokenizer, time-matched training, CV fold 0
p = m.score(report)                                 # report: list of entry points or a path to the .json; returns P(malware)

c = load_baseline("classify/bpe50k/time/seed0/fold0")     # 8-class model: m.score(report) -> 8 probabilities
                                                    # order: clean, backdoor, coinminer, dropper, keylogger, ransomware, rat, trojan
ar = load_baseline("ssl/ar_pretrained/seed0")       # the AR-pre-trained encoder (3 epochs) with its LM head (no classifier)
ar15 = load_baseline("ssl/ar_pretrained_long/seed0") # the same, pre-trained 15 epochs (best validation LM loss)
ar.next_token_logits(report)                        # [512, V] next-token logits (V = 8,193, the BPE-8k vocabulary)
```

Key naming: `detect/<tokenizer>/<time|batches>/fold<k>`, `classify/...`, `ssl/<run>/seed<k>` with
`run` in `upper, lower, mlm_theirs, mlm_bert, ar_flatten, ar_lasttoken, lower_fullattn, upper_fullattn`.
Every manifest entry lists its test metrics.

## What the loader needs

It uses the authors' code for cleaning and tokenizing, so `third_party/nebula` (pinned commit, with `patches/` applied by
`bash patches/apply_patches.sh`) must be importable, plus `torch`, `sentencepiece`, `lightning` and `speakeasy-emulator`. The loader
checks itself against the authors' `Nebula` class: for the released model both give the same score on the example reports.

## Re-using the AR-pre-trained encoder

`ssl/ar_pretrained_seed*.pt` is a state dict of `TransformerEncoderModel(vocab_size=8193, maxlen=512, dModel=64, nHeads=8, dHidden=256,
nLayers=2, classifier_head=[64], norm_first=True, causal_attention=True, pretrain_layers=[])` (the authors' class; see
`baseline/lm.py: build_fullattn`). It was trained for next-token prediction on 80% of the January training reports (labels ignored,
2% of those held out for the validation loss) with the BPE-8k tokenizer of `tokenizers/bpe8k`. To fine-tune, copy the tensors whose
names start with `encoder.`, `transformer_encoder.` and `pos_encoder.` (`baseline.lm.transfer` does this) and train a new classifier
head.
