# Baseline models (Nebula reproduction)

Trained models, tokenizers and a loader for the baseline reproduction of Nebula (Trizna et al., arXiv 2310.10664v2) with the
authors' own code. The numbers and how they compare with the paper are in [`REPRODUCTION_REPORT.md`](../REPRODUCTION_REPORT.md).

## Where the files are

| what | where | size |
|---|---|---|
| `manifest.json`, `load_baseline.py`, tokenizer files (`tokenizers/bpe50k`, `ws50k`, `bpe8k`) | this folder (git) | small |
| AR-pre-trained encoders **before fine-tuning**, seeds 0 to 4 (`ssl/ar_pretrained_seed*.pt`) | this folder (git) | about 5 MB each |
| Everything else: detection and classification fold models, all fine-tuned self-supervised models | private Kaggle dataset **`msingh9365/nebula-baseline-models`** (it also contains the files above, so one folder is enough) | about 0.8 GB |

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
ar = load_baseline("ssl/ar_pretrained/seed0")       # the AR-pre-trained encoder with its LM head (no classifier)
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
