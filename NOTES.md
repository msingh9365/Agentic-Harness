# NOTES: reproducing Nebula (Trizna et al., arXiv 2310.10664v2) with the authors' code

Working notes for the `nebula-baseline` branch. They say where things are in the authors' repository, what is
missing, what we patched, and every place where the paper, the code and the task text disagree. The numbers
and comparison with the paper go to `REPRODUCTION_REPORT.md` at the end.

## 1. Pinned code

| thing | value |
|---|---|
| Authors' repository | <https://github.com/dtrizna/nebula>, git submodule `third_party/nebula` |
| **Pinned commit** | `1343ae170ef32b01a75d2dd5fb906b5541f073df` (2026-10-08, "Merge pull request #12 ... fix/eval-mode-and-deterministic-batch-inference"); this is also upstream `main` HEAD |
| Paper | arXiv 2310.10664v2 (IEEE TIFS 2024 version has different table numbers, see §6) |
| Our changes to their code | four one-line patches in `patches/`, applied by `bash patches/apply_patches.sh` (§5). The submodule pointer stays at the pinned commit; the working tree is patched on top |
| Install | `pip install -e third_party/nebula --no-deps` (their `requirements.txt` pins `lief==0.12.3`, which is not needed for what we run; `lief` 1.0.0 imports fine) plus `lightning torchmetrics tensorboard` (not in their requirements) |

## 2. Where things are in their repository

| what | where |
|---|---|
| JSON field filter | `nebula/preprocessing/tokenization.py` `JSONFilter`; built inside `PEDynamicFeatureExtractor` (`nebula/preprocessing/pe.py`) with `SPEAKEASY_RECORD_FIELDS` (`nebula/constants.py`) |
| Normalization | `nebula/preprocessing/normalization.py` (`normalizeTablePath`, `normalizeTableIP`, `normalizeStringHash`, ...). Called from `PEDynamicFeatureExtractor.filter_and_normalize_report()` (`pe.py:106`) |
| Reading a folder of reports, labels from folder names | `nebula/preprocessing/normalization.py` `read_and_filter_json_folders()`; whole pipeline in `nebula/preprocessing/wrappers.py` `preprocess_nebula_speakeasy()` |
| Tokenizers | `nebula/preprocessing/tokenization.py`: `JSONTokenizerBPE` (SentencePiece), `JSONTokenizerNaive` (`type="whitespace"` or `"wordpunct"`) |
| Model | `nebula/models/attention.py`: `TransformerEncoderModel` (full attention, optional causal mask, optional LM head `pretrain_layers`) and `TransformerEncoderChunks` (Nebula: attention inside 64-token chunks). Other models: `nebula/models/__init__.py` (CNN, LSTM), `reformer.py`, `neurlux/`, `quovadis/`, `ember.py` |
| Training loop (plain PyTorch) | `nebula/__init__.py` `ModelTrainer` (AdamW, BCE, `time_budget`, gradient clipping 0.5, TPR/F1 at fixed FPRs) |
| Cross-validation | `nebula/evaluation/__init__.py` `CrossValidation` (3-fold `KFold(shuffle=True)`); Lightning version `nebula/evaluation/lit_cv.py` |
| Training loop (Lightning) | `nebula/lit_utils.py` `LitTrainerWrapper`, `PyTorchLightningModel`, `PyTorchLightningModelLM` |
| Pre-training | Lightning: `nebula/lit_pretraining.py` (`MaskedLanguageModelTrainer`, `AutoRegressiveModelTrainer`, `SelfSupervisedLearningEvalFramework`). Older ModelTrainer-based: `nebula/pretraining.py` + `nebula.evaluation.SelfSupervisedPretraining` |
| Scripts / configs | `scripts/cross_validation/_speakeasy_model_loop.py` (model selection CV), `scripts/preprocessing/_speakeasyPreProcessingBPE.py` (vocab-size study), `scripts/pretraining/_speakeasyMLM*.py` (older MLM runs), `scripts/pretraining/train_example_lit_mlm_eval.py`, `scripts/train_example_lit_cross_validation.py` |
| ROC plots | `nebula/evaluation/roc.py`, `nebula/misc/plots.py` |

## 3. What they ship

| file (in `nebula/objects/`) | what |
|---|---|
| `bpe_50000_sentencepiece.model`, `bpe_50000_vocab.json` | the released BPE tokenizer (50,000 pieces; the JSON has 50,001 entries because of a stray empty key from a trailing newline; `<pad>`=0, `<unk>`=1, `<mask>`=2) |
| `bpe_50000_torch.model` | released Nebula weights, BPE (5.397 M parameters, loads into the config below) |
| `whitespace_50000_vocab.json`, `whitespace_50000_torch.model` | released Whitespace tokenizer vocabulary and weights |
| `speakeasy_config.json` | emulator configuration |

Released model config (`Nebula.__init__`): `dModel 64, nHeads 8, dHidden 256, nLayers 2, chunk_size 64, classifier_head [64],
dropout 0.3, norm_first True, pooling "flatten", layerNorm False`. The paper warns that the released weights were
trained on about 70k samples (§5 Limitations), so they are a sanity check, not the target of the retraining.

No pre-trained 8,192-vocabulary models, no MLM or AR checkpoints and no classification models are shipped.

## 4. Paper settings against their code

| setting | paper | their code | note |
|---|---|---|---|
| Fields kept | API name+args+ret, file op+path, network port+server, registry op+path | `SPEAKEASY_RECORD_FIELDS`: exactly these | same |
| Hash normalization | `<sha1>/<sha256>/<md5>` | `normalizeStringHash`, applied to **file paths only** | registry paths are not normalized |
| IP normalization | loopback / private / public / IPv6 | `<lopIP>`, `<imds>`, `<prvIP>`, `<pubIP>`, `<IPv6>` on the network `server` field | same |
| **Domains** | `<domain>` | `normalizeStringDomain()` exists but is **never called** | **difference**: domains stay as they are. We follow the code |
| Path variables, `<drive>`/`<user>` | yes | `VARIABLE_MAP`, `normalizeStringPath` | same |
| Tokenizer cleanup | not stated | `JSON_CLEANUP_SYMBOLS`, stopwords `api_name, args, ret_val, event, path, ...` removed | follow code |
| BPE | SentencePiece, **byte fallback** | `--model_type=bpe --split_by_number=False --max_sentence_length=4192 --max_sentencepiece_length=64`, **no** `byte_fallback`; the released model has 0 byte pieces | **difference**. We follow the code |
| Vocabulary, length | V=50,000 + `<unk>`/`<pad>`, N=512, fitted on train only | `vocab_size=50000`, `seq_len=512`; `preprocess_nebula_speakeasy` trains the tokenizer on the train folder only | same |
| Architecture | 2 layers, 8 heads, chunks S=64 (M=8), head 64, "about 5.6M" parameters | same config, **5.397 M** parameters | small difference in the stated size |
| Optimizer | AdamW, lr 2.5e-4, betas (0.9, 0.999), eps 1e-8, wd 1e-2, static lr | `ModelTrainer` default `AdamW(lr=2.5e-4, weight_decay=1e-2)`; PyTorch defaults for betas/eps | same. `ModelTrainer` also clips gradients at norm **0.5** (not in the paper) |
| **Batch size** | b = 96 for all experiments | not in the repo: CV script uses 64, lit CV example 256, `LitTrainerWrapper` default 1024 | **gap**. We use 96 as the paper says |
| **Time budget** | 5 min per fold on a Quadro T2000 | mechanism exists (`time_budget`, `CrossValidation`), no script sets 5 min | **gap**. We use the mechanism |
| **Batches seen** | Table 7: BPE 2,116, Whitespace 2,159 | not in the repo | **gap**. Batch-matched runs stop after exactly these numbers of batches |
| CV | 3 folds on train, mean of 3 models on validation and on the test set | `CrossValidation`: `KFold(3, shuffle=True, random_state)` on validation only; no test evaluation per fold | **gap**: test evaluation per fold model is ours |
| TPR at FPR | "TPR at FPR = 1e-3" | `get_tpr_at_fpr`: TPR at the last ROC point with FPR <= target; the threshold comes from the set evaluated | same. Used for validation and test |
| F1 / accuracy | Table 7: F1 0.9136 with TPR 0.5213 | CV code computes F1 at the *FPR threshold*, which cannot give 0.91 next to TPR 0.52 | **ambiguous**. We report F1 and accuracy at threshold 0.5 (probably the paper's) and, separately, F1 at the FPR-1e-3 threshold |
| **Whitespace tokenizer** | "Whitespace" tokenizer, released weights | the released `whitespace_50000_vocab.json` has tokens `apiname`, `retval`, `kernel32getprocaddress` and keeps `args`, `event`, `path`: it was built with punctuation *deleted* and the stopwords *kept*. The pinned `JSONTokenizerNaive` turns punctuation into spaces and removes the stopwords. With the pinned tokenizer the released Whitespace model scores AUC **0.770** on a 1,259-report April sample; with the legacy cleaning (cleanup symbols to spaces, other punctuation deleted, no stopword removal) **0.943** | **difference, found while checking E**. The pinned repo cannot reproduce the released Whitespace tokenization (its `Nebula(tokenizer="whitespace")` is effectively broken). We run Whitespace both ways: `ws50k` (pinned code, the rule) and `ws50k_legacy` (ours, inferred from the vocabulary; the cleaning is in `baseline/preprocess.py`) |
| SSL vocabulary | 8,192 | example scripts use the 50k vocabulary | follow the paper (task text agrees) |
| MLM | "same pre-training parameters as BERT" | 15% masking, 80/10/10 (same as BERT). **But the target is not per-position**: the model predicts, from the pooled sequence output, a vector over the vocabulary marking *which token ids were masked* (soft-target cross-entropy) | **difference** with the task text ("loss only on the masked positions"). We run their MLM as the primary one and add a standard per-position BERT MLM (ours) as a second variant |
| AR | "global attention, Transformer tailored for these experiments" | `TransformerEncoderModel(causal_attention=True)` exists. Their `AutoRegressiveModelTrainer` is unfinished (TODO comments): random 256-token windows, loss on every position including padding | **gap**. The full-512 causal trainer with padding ignored is ours (a subclass of theirs) |
| 80/20 split | 80% unlabeled / 20% labeled | `SelfSupervisedLearningEvalFramework`: `train_test_split(train_size=0.8)`, **not stratified** | the task asks for stratified; ours is stratified |
| Model choice on test | not stated | their example passes the **test set as the validation loader** and checkpoints on `val_tpr` | we never select anything on the test set (fixed budgets, final weights) |
| LM head | not stated | `pretrain_layers=[1024]`: Linear(.,1024) + ReLU + Linear(1024, V, bias=False), not tied to the embedding | follow code for MLM. For AR we use the code's head too (tied weights are the task's default only if the code has no head) |

## 5. Patches to their code (`patches/`)

All four are in `nebula/lit_utils.py` (the Lightning wrapper), one line each, and are library-version fixes; none changes
their logic. Apply with `bash patches/apply_patches.sh` (idempotent).

| patch | why it was needed | what it does |
|---|---|---|
| `0001-lightning-fabric-seed-import.patch` | `lightning.lite` was removed (Lightning >= 2.1) | import `seed_everything` from `lightning.fabric.utilities.seed` (same function) |
| `0002-lightning-accumulate-grad-batches-none.patch` | `L.Trainer(accumulate_grad_batches=None)` raises `TypeError: unsupported operand type(s) for %` in Lightning 2.6 | pass `... or 1` (1 = no accumulation, what `None` meant) |
| `0003-lightning-optimizer-zero-grad-signature.patch` | Lightning >= 2.0 calls `optimizer_zero_grad(epoch, batch_idx, optimizer)` without `optimizer_idx` | make `optimizer_idx` optional |
| `0004-masked-lm-keep-float-target.patch` | `_shared_step` cast every 2-D-output target to int64, so the multi-hot MLM target failed with "Expected floating point type for target with class probabilities, got Long" | only cast to int64 when the target is 1-D (class indices) |

Found, **not** patched (we avoid these code paths instead):
- `nebula.evaluation.SelfSupervisedPretraining` (the older MLM pipeline used by `scripts/pretraining/_speakeasyMLM*.py`)
  passes `forward_pass=` to `ModelTrainer`, whose argument is `modelForwardPass`: `TypeError`. It looks like the pipeline that
  produced the paper's MLM numbers; we use the Lightning pipeline instead.
- `scripts/pretraining/train_example_lit_mlm_eval.py` uses `"pooling": None` with `pretrain_layers=[1024]`: output `(B, 512, V)`
  against a `(B, V)` target, which can never run (`ValueError: Expected input batch_size (16384) to match target batch_size (9600)`).
  A pooled model (`flatten` or `mean`) works.
- `nebula.pretraining.AutoRegressiveModelTrainer` (older) slices windows over the *sample* axis, so it does not work on a
  2-D token array.
- `read_and_filter_json_folders` only lists `*.json` files directly inside each `report_*` folder (`os.listdir`), so reports in
  sub-folders are silently skipped. This matters for the **Hugging Face** copy of the dataset, where the January `report_clean` and
  `report_backdoor` folders are sharded into sub-folders `0`..`f`. The **Kaggle** copy (the one used for all runs here) is flat
  (checked by the probe kernel: 75,298 train and 17,402 test files directly in the `report_*` folders), so no workaround is needed there.
  For local tests on the Hugging Face copy, `baseline/tests/make_sample.py` builds a flat sample of symlinks.

## 6. Dataset

| item | value |
|---|---|
| Kaggle dataset | **`dmitrijstrizna/quo-vadis-malware-emulation`** (dataset id 3231810 = the `/ds/3231810` link). Hugging Face mirror: `dtrizna/quovadis-speakeasy` |
| Size | 311 MB compressed on Kaggle (about 5.5 GB of JSON). **Not** the 430 GB of the task text: 329 GB + 98 GB is the raw report size in the paper's Table 3 |
| Files | `windows_emulation_trainset/report_*/<sha256>.dat.json`, `windows_emulation_testset/...`; labels from folder names; `report_clean` and `report_windows_syswow64` are benign |
| **Counts** | released data: train 75,301 files (75,298 non-empty), test 17,402 (the dataset description prose says 76,126 / 17,407). Paper Table 3: **98,966 train / 27,500 test**, with a different test mix (for example dropper 252 here against 2,500 in the paper, benign 7,944 against 10,000). The paper text itself says "approximately 93,500 samples". So the **paper's April test set is not what is published**, and exact agreement is not expected |
| Table numbers | the task's "Table 12b" is **Table 9** in arXiv v2; Whitespace F1 is 0.9068 in the paper's Table 6 and 0.9058 in its Table 7 |
| Other Kaggle datasets in the account | `msingh9365/nebula-speakeasy-tokens` (92,700 tokenized reports, from earlier thesis work) and `msingh9365/nebula-thesis-code`. They are **not touched**. The preprocessing output of this study is published as **`msingh9365/nebula-baseline-tokens`** instead of the slug in the task text, so the earlier data is not overwritten |

## 6b. Kaggle environment (measured by `baseline/kaggle/probe`)

| item | value |
|---|---|
| Python | 3.13 (Kaggle image). `speakeasy-emulator`, `lief`, `lightning`, `torchmetrics` all pip-install; `import nebula` works with the real `speakeasy` and `lief` (no stubs) |
| CPU kernel | 4 cores, 31 GB RAM, 19.5 GB free in `/kaggle/working`; about 2.5x slower per core than the local machine used for development |
| Dataset mount | `/kaggle/input/datasets/<owner>/<slug>/`; our code finds data by folder name, not by path |
| GPU | `kaggle kernels push --accelerator NvidiaTeslaT4` gives a T4 x2 session (P100 is retired). Two independent worker processes, one per GPU, use the session time twice as well |
| Quota (CLI `kaggle quota`) | on 2026-11-16: 26.62 h of 30 h GPU left, resets 2026-11-21 |
| How code reaches Kaggle | `baseline/kaggle/build_kernel.py` packs `baseline/` and `patches/` into the kernel script; the script clones the authors' repo at the pinned commit, applies the patches and runs one module. The exact code is therefore stored in each pushed kernel version |

## 7. Decisions log

- New slug `nebula-baseline-tokens` (see above), not `nebula-speakeasy-tokens`.
- Where the task text and their code differ on MLM and AR, their code is the primary run and the task's spec is run as a labelled
  second variant (cheap): see §4.
- Preprocessing calls their functions in the order of their wrapper but filters the reports once (in parallel) instead of once per
  tokenizer variant. A unit test shows the token arrays and labels are bit-identical to `preprocess_nebula_speakeasy` on a sample.
- Self-supervised runs do not use their `SelfSupervisedLearningEvalFramework`: it splits without stratification, copies weights by
  name even when shapes differ (this breaks for the AR flatten classifier) and takes the *test set* as validation loader with
  checkpoint selection on `val_tpr`. We call their trainers (`MaskedLanguageModelTrainer`, `LitTrainerWrapper`) directly, split
  stratified by family (seeds 0, 1, 2), use fixed budgets and evaluate the final weights once on the test set.
- Self-supervised budgets (the paper does not give them): pre-training 3 epochs on 98% of the unlabeled 80% (2% held out for the LM
  validation loss, early stopping with best-weights restore), dropout 0 while pre-training and 0.3 while fine-tuning (as in their
  example script), batch 96, AdamW lr 2.5e-4, gradient clipping 1.0; fine-tuning 10 epochs for every run (upper bound included).
- Detection and classification: single CV with seed 0 (the paper has one CV run); the fold split is `KFold(3, shuffle=True,
  random_state=1763)`, the state used in the authors' CV scripts.

## 8. GPU-hours log

Kaggle limits: about 12 h per session, about 30 GPU-hours per week.

| date | kernel | GPU | hours | what |
|---|---|---|---|---|
| 2026-11-16 | nebula-env-probe, nebula-preprocess-smoke, nebula-preprocess, -b, -lens | none (CPU) | 0 | tokenizer training and token arrays; CPU kernels do not use GPU quota |
| 2026-11-16 | nebula-gpu-smoke | T4 | not logged (small) | smoke test of the GPU path |
| 2026-11-16 | nebula-detect, nebula-detect-seeds | T4 x2 | see below | detection (BPE and Whitespace, time- and batch-matched, seeds 0 to 2), released checkpoints |
| 2026-11-16 | nebula-ssl, nebula-ssl-more | T4 x2 | see below | self-supervised, seeds 0 to 2 and 3 to 4 |
| 2026-11-16 | nebula-rest | T4 x2 | see below | legacy Whitespace detection, classification, ablations |
| 2026-11-17 | nebula-ssl-long-ar (v1 failed after about 3 min: packaging; v2) | T4 x2 | 4.57 (incl. the failed attempt) | B2: AR pre-training up to 15 epochs + fine-tuning from epochs 3, 6, 10, best, 5 seeds |
| 2026-11-17 | nebula-ssl-long-mlm | T4 x2 | 2.08 | B2: per-position MLM, authors' MLM, AR flatten from the best AR checkpoint, 5 seeds |
| 2026-11-17 | nebula-ssl-long-ctrl | T4 x2 | 0.21 | B2 extra control: causal last-token classifier without pre-training, 5 seeds |
| 2026-11-17 | nebula-gap-r1a | T4 x2 | 0.80 | F: R0, R1, 5 seeds, 12 epochs (47 min wall) |
| 2026-11-17 | nebula-gap-r1b | T4 x2 | 1.09 | F: R2, R3, R4, R5, 5 seeds, 8 epochs |
| 2026-11-17 | nebula-gap-r1c | T4 x2 | 0.88 | F: R6, R7, 5 seeds, 6 epochs (24 min wall) |
| 2026-11-17 | nebula-gap-r1d | T4 x2 | 0.30 | F: R8, R9, 5 seeds, 4 epochs (20 min wall) |
| 2026-11-17 | nebula-gap-final | T4 x2 | 0.11 | F: baseline v2 = R8, 5 seeds, 2 epochs, models saved |
| 2026-11-17 | nebula-b3-tokens | CPU | 0 (no GPU) | B3: BPE-8k refit on the 90% (53 min) |
| 2026-11-17 | nebula-b3-sup | T4 x2 | about 0.9 | B3: runs 1 to 3, both lrs, 5 seeds (52 min wall) |
| 2026-11-17 | nebula-b3-pre | T4 x2 | about 1.4 | B3: AR and MLM pre-training + fine-tuning, both lrs, 5 seeds (82 min wall) |
| 2026-11-17 | nebula-b3-extra | T4 x2 | 0.44 | B3 addendum: mlm_theirs (5 seeds OK); arflat failed (import path) |
| 2026-11-17 | nebula-b3-extra2 | T4 x2 | 0.33 | B3 addendum: AR flatten, 5 seeds |
| 2026-11-18 | nebula-gap-v2-s59 | T4 x2 | 0.12 | baseline v2 seeds 5-9 (R8, 2 epochs, models + logits saved), 6 min wall |
| 2026-11-19 | nebula-v2pe-smoke | T4 x2 | 0.04 | v2-PE smoke: seed 0, 1 epoch (paper) and seed 0, 2 epochs (released mode; reproduces v2 seed 0 exactly) |
| 2026-11-19 | nebula-v2pe-full | T4 x2 | 0.18 | v2-PE, seeds 0-9, 2 epochs, 10 min wall |
| | **v2-PE total** | | **0.22** | quota 26.84 h → 27.06 h (stop-and-ask threshold 1.5 h); 2.94 h left (resets 2026-11-21) |
| | **pAUC / protocol / v2 seeds 5-9 total** | | **0.12** | quota 24.20 h → 24.32 h (limit 1.5 h); the CPU re-scoring used no GPU |
| | **B3 total** | | **3.03** | quota 20.89 h → 23.92 h (estimate 4.3 h + 0.8 h addendum, limit 6 h); 6.08 h left |
| | **F total** | | **3.18** | quota 17.71 h → 20.89 h (limit 8 h, estimate 5 h); 9.11 h left, resets 2026-11-21 |

Per-kernel quota hours were not recorded. What was measured: the sum of per-model training seconds (detection 2.5 h, classification
1.1 h, ablations 2.5 h, self-supervised fine-tuning 4.1 h, pre-training 1.2 h = **11.4 h of GPU compute**; the figures come from the
`train_seconds` fields in `results/*/metrics.json`), and the account quota counter (`kaggle quota`): **10.85 h used, 19.15 h left** at
the end, 3.38 h of it used before this study, so this study used about **7.5 h** of session time (two GPUs ran in parallel, which is why this
is less than the 11.4 h of compute). The quota resets on 2026-11-21. Nothing was run near the limit.

## 9. Follow-up: longer self-supervised pre-training (experiment B2)

**Question.** In the first run pre-training lasted 3 epochs and the AR validation loss was still falling (1.95 → 1.31–1.37). Does longer
pre-training open the gap of the paper's Fig. 6 (upper − lower ≈ 15 points TPR@1e-3, AR within ≈ 3 of upper)?

**What stays the same** (checked in code, not assumed): tokens (`nebula-baseline-tokens`, BPE 8,192), seeds 0 to 4, the stratified 80/20 split of
each seed (the kernel asserts the sha256 of `unlabeled`+`labeled` against `baseline/ssl_split_hashes.json`, taken from the published
`splits.json`, sha256 `3bc9eeff…1601`, which is also the file regenerated by `make_splits`: the split is deterministic and identical to the one the first
run used), fine-tuning (10 epochs on the 20%, AdamW 2.5e-4, batch 96, gradient clipping 1.0, final weights, nothing selected on the test set),
the pre-training data split (98% / 2% held-out for the LM validation loss, same per-seed permutation), the dropout (0 while pre-training, 0.3 while fine-tuning)
and the RNG order (`set_seed`, build downstream model, pre-train). **Reused, not retrained:** upper, lower and the two full-attention controls of
`results/B_selfsup/` (same seeds, splits, fine-tuning budget). Only the pre-training length (and its early stopping) changes. New outputs:
`results/B_selfsup_long/`.

**Changes (all in `baseline/`, nothing in `third_party/nebula`).** `lm.ValLossCallback` gets `min_delta` and per-epoch checkpoints (defaults
unchanged: patience 1, min delta 1e-6); `baseline/selfsup_long.py` is the driver; `baseline/long_stats.py` the paired differences and bootstrap.
Early stopping: patience 2 epochs, min delta 0.01 on the validation LM loss (the best weights, i.e. the lowest validation loss, are restored;
"best" in all names means that epoch). Unit tests: `baseline/tests/test_long.py` (early stop, checkpoints, fine-tune-from-epoch-k checksum, split assertion).

**Plan and cost estimate** (from the first run: AR 128 s per pre-training epoch, per-position MLM 99 s, authors' MLM 55 s; fine-tuning
AR last-token 177 s, MLM about 111 s, AR flatten 256 s; T4). Worst case = no early stopping, all 15 epochs:

| step | per seed | 5 seeds |
|---|---|---|
| 1. AR pre-training, 15 epochs | 32 min | 2.67 h |
| 1. AR last-token fine-tuning from epochs 3, 6, 10 and best (4 runs) | 12 min | 0.98 h |
| 2. per-position MLM, 15 epochs + 1 fine-tune | 25 + 2 min | 2.2 h |
| 3. authors' MLM, 15 epochs + 1 fine-tune | 14 + 2 min | 1.3 h |
| 4. AR flatten fine-tune from best | 4 min | 0.36 h |
| **total compute (one GPU)** | | **≈ 7.5 h** |

Two T4s run seeds in parallel, so the quota cost is about half of it (3.8 h) plus about 10 min of set-up per kernel; the first run used
7.5 h of quota for 11.4 h of compute. Even if quota were charged per GPU the worst case (7.5 h) is half of the **hard limit of 15 GPU-hours for this follow-up**.
Quota before this follow-up: **10.85 h used, 19.15 h left** (2026-11-17). Order: kernel 1 = item 1 (AR). The epoch-3 point must reproduce
the first run within noise before anything else is launched; kernel 2 = items 2, 3, 4. Nothing is cut from the list unless the measured cost of kernel 1 changes this estimate.

**Measured, kernel 1 (AR, `nebula-ssl-long-ar`, v2; v1 failed in 1 minute on a packaging bug: the split-hash file was missing from the kernel payload and the
orchestrator hid the failure, about 0.05 h).** 5 seeds on 2 T4s, 135 min wall. The quota counter went from 10.85 h to **15.42 h (+4.57 h): Kaggle charges
both GPUs for the whole session**, so the quota cost is 2 × wall time, not the 0.5 × the estimate above assumed. Corrected estimate for kernel 2
(items 2 to 4, worst case 240 min of compute on two GPUs = 120 min wall): about **4.0 to 4.5 h** of quota, so the follow-up total stays near 9 h, under the 15 h limit.
Results: all 5 seeds ran the full 15 epochs (the validation LM loss was still falling, 0.84 to 0.92 at epoch 15; early stopping never triggered), so "best" = epoch 15.
Epoch 3 of the long run reproduces the first run: validation LM loss at epoch 3 agrees to ±0.01 for every seed, and AR last-token TPR@1e-3 is 0.412 against 0.420
(per-seed difference −0.8 ± 3.6 points), i.e. within noise.

**Measured, kernel 2 (`nebula-ssl-long-mlm`: AR flatten from the best AR checkpoint, per-position MLM, authors' MLM; 5 seeds each) and the extra control.**
Kernel 2: 102 min wall, quota 15.42 h → 17.50 h (**+2.08 h**). The per-position MLM ran all 15 epochs (25 min per seed, best epoch 15); the authors' MLM stopped early in
every seed (6 epochs run, best epoch 4, 5 min per seed). Extra control, not in the original plan (`nebula-ssl-long-ctrl`, unit `lasttoken_control`: the causal last-token classifier
fine-tuned on the labeled 20% without pre-training, the architecture-matched lower bound of the AR last-token runs): about 12 min wall, 17.50 h → 17.71 h (**+0.21 h**).
**Follow-up total: 17.71 − 10.85 = 6.86 h of quota** (limit set for this follow-up: 15 h). The estimate above (about 9 h) was an upper bound: the authors' MLM stopped early and the control was cheap.
Quota after the follow-up: **17.71 h used, 12.29 h left** (resets 2026-11-21). Results and the answer to the question: REPRODUCTION_REPORT.md §5.2b and §6.5.

## 10. Follow-up: why does the authors' released BPE model reach TPR@1e-3 ≈ 0.52 when our retrained models reach ≈ 0.41?

Step 1 (CPU only; code `baseline/gap_analysis.py`, outputs `results/F_gap/`, the extracted history in `/tmp/gap`, not kept). All facts below were read from the authors' git
history (the pinned submodule has the full history, 377 commits on all branches) or computed.

**10.1 Their history.**
- The released checkpoint file `nebula/objects/bpe_50000_torch.model` has a long history. Its weights are the **2023-06-02** file (commit `26a8986` "update bpe objects", the same day as
  `e218c48` "updated tokenizer stopwords filter" and a new sentencepiece model, which is byte-identical to the pinned `bpe_50000_sentencepiece.model`). Everything after that is a rename of keys
  (Dec 2023 "pip object config", Jan 2024 "Transformer model unification", Feb 2024 "fix of pretrained objects after model class update"): the sorted weight values hash identically in all of
  them (`cdab5bdc4c90`). The first version (2023-05-12, commit `104c3ab`) was called **`speakeasy_BPE_5ep_torch.model`** ("5ep" = 5 epochs?) and has different weights (`ac2cc3c328f7`).
  Paper v1 is Oct 2023, v2 Oct 2024: the checkpoint predates both.
- **There is no script, log or config in the repository that trains the released model** (searched `git log -S`, `git grep` on every commit for `5ep`, `torch.save`, epochs, batch size; no hit). The objects
  were produced outside the repository.
- **But the paper's own CV runs are in the `research` branch** (`evaluation/paper_ablation/out_tokenizer/`, April 2023): the logs, the per-fold metrics and the script (`run_tokenizer.py`, Jan 2024 version).
  They give the authors' training regime for the BPE CV models (the models behind Table 6/7): **batch 96, 5-minute time budget (about 5.3 epochs, 529 batches per epoch, i.e. about 2,800
  batches on a slower GPU), AdamW with lr 3e-4 (the paper text says 2.5e-4; the repo's default is 2.5e-4), gradient clipping 1.0 (the pinned `ModelTrainer` default is 0.5, which we used), dropout 0.3, no scheduler, our
  model configuration (5.3972 M parameters, identical)**. The dataset in those logs has **76,126 train reports** (50,750 + 25,376 per fold), **not** the paper's 98,966.
- The Mar 2024 byte-fallback script (`run_tokenizer.py`, last version) is a different, later recipe (Lightning, one-cycle schedule, 30 epochs, batch 512, dropout 0.5, validation on the test set): not the recipe of the released model.
- The authors' own per-fold validation metrics for BPE (`bpe_metrics_validation.json`): TPR@1e-3 = [**0.0**, 0.919, 0.846] (fold 1: the float32 tie artifact of §6.4, so **their reported CV numbers contain it too**), TPR@1e-2 = 0.961 / 0.972 / 0.966, AUC 0.9956 / 0.9976 / 0.9974.
  Ours (9 fold models, same KFold, 5 minutes on a T4): **val TPR@1e-3 0.608**, TPR@3e-3 0.839, TPR@1e-2 0.949, AUC 0.9965. **The gap is already there on in-distribution January validation data
  (0.85 to 0.92 against 0.61 at equal AUC), so it is not drift between January and April and not the test set.**
- Dataset: `emulation/kaggle_prep_speakeasy.ipynb` copies the files whose hashes are in `speakeasy_yHashes.json` of the authors' **10k-whitespace preprocessed** train/test sets: 76,126 train and 17,407 test hashes (the
  notebook's own progress bars). The published folders hold 75,301 / 17,402 files (825 and 5 hashes were not found when copying). The paper's Table 3 counts (98,966 / 27,500) are the raw emulation counts before
  the authors' own filtering; **the released model was most likely trained on this same ≈ 76k set**, so "it saw more data" is not supported (the difference to ours is 1.1%).

**10.2 The checkpoint** (`results/F_gap/state_dict_table.md`, `state_dict_tables.json`). Same architecture as ours (5,717,313 parameters in the state dict incl. the positional buffer; shapes identical: dModel 64, dHidden 256, 2 layers,
8 heads, chunk size 64, head [64] with a 32,768-input first layer, flatten pooling, no extra layers). The sinusoidal buffer is identical. **The learned weights are much larger than ours:** L2 norm of the embedding 107 (ours 41, a fresh initialization 36),
classifier first layer 87 (ours 38, init 29), attention out-projection 4.5 (ours 1.6, init 1.3), feed-forward `linear1` 9.5 (ours 3.3, init 2.6). The May-2023 `5ep` file has the same pattern (105, 85, 4.5, 9.3). Our models grow only slowly
with training (2,116 batches: embedding 39.6, head 34.4; 5,023 batches: 41.0, 38.2). The authors' training therefore **moved the weights about five times further from the initialization than ours did** (displacement 100 against 20 for the embedding).
Under Adam this means a much larger learning rate or many more updates than ours (or both).

**10.3 Output calibration** (`results/F_gap/calibration_table.md`, `calibration.json`; logits, eval mode).

| model / data | malware with float32 p = 1.0 (%) | benign with p = 1.0 (n) | benign logit p99 | p99.9 | mean of the 8 highest benign logits | malware median logit |
|---|---|---|---|---|---|---|
| released, April test | 42.3 | 5 | 2.5 | 13.5 | **19.8** | 14.3 |
| ours (9 fold models), April test, mean | 71.3 | 95.2 | 18.1 | 40.9 | **49.5** | 34.0 |
| released, January (in-sample: it was trained on it) | 72.7 | 3 | 1.1 | 7.8 | 16.3 | 25.8 |
| ours (seed-0 fold models), held-out January fold, mean | 94.6 | 88.7 | 17.6 | 42.0 | 55.6 | 49.9 |

Our models are **far more over-confident**: logits two to three times larger, 95 benign April reports at float32 1.0 (the released model: 5). This is the quantification of §6.4. Over-confidence and a poor tail (the highest-scoring benign reports score as high as malware) go
together with overtraining; our own runs agree: **models stopped after 2,116 batches (about 4 epochs) have validation TPR@1e-3 0.718 and test 0.434, models trained for the 5-minute budget (5,023 batches, 9.6 epochs) 0.608 and 0.406**, and the training loss
of the last 100 batches falls from 0.031 to 0.014.

**10.4 Tokenizer.** Both are BPE-50k models without byte pieces; 42,366 of 50,000 pieces are shared (84.7%). Token-length distributions on the same reports are almost the same (mean 382.5 against 381.6 tokens on January, 388.0 against 386.5 on April; truncated at 512: 37.8% against
37.6%, 46.3% against 46.1%; no unknown tokens). A tokenizer effect is unlikely (`tokenizer_comparison.json`).

**10.5 Our evaluation path** (`eval_path_check.json`). The released checkpoint and our fold-0 checkpoint were scored through the same function (`cv.predict_logits`: `model.eval()`, `torch.no_grad()`, int ids, 512 tokens, pad id 0 on the right, no dropout, flatten
pooling) on arrays produced by the same preprocessing code. The saved E logits are reproduced to 3.4e-5. The authors' own trainer also evaluates in `eval()` mode, in 2023 as now.

**10.6 Ranked hypotheses.**

| # | hypothesis | evidence | cheapest test |
|---|---|---|---|
| H-A | our models are over-trained (too many updates, over-confident, bad tail) | calibration (10.3); 2,116 vs 5,023 batches; the authors' runs used about 5 epochs; the "5ep" file name | per-epoch validation curves of one recipe (**H2**) |
| H-B | the learning rate / clipping differ (authors: 3e-4 and 1.0; weight norms say an even larger effective step) | 10.1, 10.2 | lr 1e-3 (**H5**) and lr 3e-4 + clip 1.0 (**H4**), one change each |
| H-C | training data size (2/3 of January against all of it) | the released model most likely saw all of January | train on 90% of January (**H1**), same recipe |
| H-D | tokenizer | 84.7% shared pieces, same length distribution: unlikely | our recipe on the released tokenizer (**H3**) |
| H-E | different data | the published set is the authors' own filtered set (76,126 against our 75,301): unlikely | none (not testable) |

**10.7 Plan and cost.** Selection only on a **held-out validation slice of January**: 10% stratified by family, `train_test_split(random_state=2025)`, hash in `baseline/gap_split_hash.json` (67,768 train / 7,530 validation reports, of which
**only 2,467 benign**). At FPR 1e-3 that slice allows 2 false alarms, so per-seed validation TPR@1e-3 is extremely noisy; selection uses the **mean over 5 seeds** of val TPR@1e-3, with TPR@3e-3 / TPR@1e-2 and AUC next to it, and ties within one standard error go to the better TPR@1e-2.
Every recipe gets 5 seeds (0 to 4); every run records validation (and, never used for selection, April test) metrics at every epoch, so the epoch count and early stopping are chosen **after** training from validation alone.
One change at a time against R0 (lr 2.5e-4, clip 0.5, dropout 0.3, batch 96, wd 1e-2, our BPE-50k, 90% of January): R0 (H1 + H2), R1 lr 1e-3 (H5), R2 lr 3e-4 + clip 1.0 (H4), R3 released tokenizer (H3); combinations only of what helps on validation.
Cost (T4: about 17 batches/s; 706 batches per epoch = 42 s, plus about 5 s of evaluation; 12 epochs = 9.4 min per run): one kernel with 2 recipes x 5 seeds = 10 runs = 5 per GPU = 47 min wall + 5 min set-up, charged for both GPUs: **about 1.7 h of quota**.
Round 1a: R0 + R1 (1.7 h); round 1b: R2 + R3, or a refinement chosen from 1a (1.7 h); final training of the chosen recipe with 5 seeds and models saved (about 0.5 h); optional re-run of the B bounds with the v2 recipe (about 1 h).
**Estimate 5 h, hard limit 8 h.** Quota before this follow-up: 17.71 h used, 12.29 h left (2026-11-17). Measured hours go in §8.

**10.8 Round 1a result (validation only; kernel `nebula-gap-r1a`, R0 and R1, 5 seeds, 12 epochs, 47 min wall, quota 17.71 h → 18.51 h = +0.80 h; the 1.7 h estimate was too high).**
R0 (our current recipe, 90% of January): validation TPR@1e-3 peaks at epochs 1 to 2 (0.75 / 0.79), then falls to about 0.6 at epochs 5 to 12; the validation loss is lowest at epoch 2 (0.099) and then rises steadily (0.30 at epoch 12): **the recipe over-trains
after 2 epochs (H-A confirmed on validation)**. R1 (lr 1e-3): better at every epoch: epoch 2 val TPR@1e-3 0.867 ± 0.115, TPR@1e-2 0.984, AUC 0.9985, loss 0.065; it also over-trains later (TPR@1e-3 0.70 at epoch 12). R0 at epoch 3 (the same 2,116 batches as our old batch-matched
2/3-data models) is 0.730 against 0.718 for those, so more data does not visibly help (H1 is tested directly by R5). The authors' own CV validation (0.85 to 0.92 at 1e-3, 0.97 at 1e-2) is matched by R1, not by R0. Validation TPR@1e-3 has a seed std of 0.04 to 0.19 (2 benign reports allowed), so
recipe choices use TPR@1e-2, AUC and the validation loss next to it.
Round 1b: R2 (lr 3e-4 + clip 1.0, the research-branch CV script), R3 (released tokenizer), R4 (lr 3e-3), R5 (R0 on a random 2/3 of January), 5 seeds, 8 epochs (everything peaks early).

**10.9 Round 1b result (validation only; kernel `nebula-gap-r1b`: R2, R3, R4, R5, 5 seeds, 8 epochs, quota 18.51 h → 19.60 h = +1.09 h; follow-up total so far 1.89 h).**
R2 (lr 3e-4 + clip 1.0, the research-branch script): **no better than R0** (best val TPR@1e-3 0.77 at epoch 3, loss minimum 0.097 at epoch 2 against 0.099): H4 is not the explanation. R3 (released tokenizer): **no effect** (0.79 at epoch 3, loss minimum 0.093): H3 rejected.
R5 (R0 on a random 2/3 of January): slightly **worse** than R0 (epoch 2: TPR@1e-3 0.73 against 0.79, TPR@1e-2 0.959 against 0.971, AUC 0.9968 against 0.9977): H1 has a small positive effect (more data helps a little; R0 already uses 90%).
R4 (lr 3e-3): **the best so far**: epoch 2 val TPR@1e-3 0.899 ± 0.038, TPR@1e-3 stays at 0.83 to 0.90 until epoch 8, TPR@1e-2 0.982, AUC 0.9984, lowest val loss of all so far at epoch 2 (0.087). Learning rate is the dominant factor:
lr 2.5e-4 → 1e-3 → 3e-3 gives epoch-2 val TPR@1e-3 0.794 → 0.867 → 0.899 and TPR@1e-2 0.971 → 0.984 → 0.982. Next (round 1c, 6 epochs, 5 seeds): R6 lr 1e-2 (where does the axis peak?) and R7 = R4 with clip 1.0.

**10.10 Round 1c result (validation only; kernel `nebula-gap-r1c`: R6, R7, 5 seeds, 6 epochs, 24 min wall, quota 19.60 h → 20.48 h = +0.88 h; follow-up total so far 2.77 h of 8 h).**
R6 (lr 1e-2): **collapsed in all 5 seeds** (AUC 0.5000, validation loss 0.6325 = the loss of a constant predictor, all scores tied from epoch 1): the lr axis has a cliff between 3e-3 and 1e-2.
R7 (lr 3e-3 + clip 1.0): the same as R4 within noise (val TPR@1e-3 0.901 at epoch 1 and 0.916 at epoch 5, 0.885 to 0.893 in between; paired difference R4@2 minus R7@1: TPR@1e-3 -0.002 ± 0.009 SE, TPR@1e-2 +0.006 ± 0.003, AUC +0.0003 ± 0.0001; its validation loss minimum is at epoch 1 and the loss then rises faster). Clipping 1.0 is not a useful change.
Validation-only effect of lr (epoch 2, mean of 5 seeds): R0 (2.5e-4) 0.794 → R1 (1e-3) 0.867 → R4 (3e-3) 0.899 for TPR@1e-3; R4 minus R0: TPR@1e-3 +0.105 ± 0.071 SE, TPR@1e-2 +0.011 ± 0.004, AUC +0.0007 ± 0.0002 (clearest on TPR@1e-2 and AUC; TPR@1e-3 on 2,467 validation benign reports is noisy).
**Rule fixed now, before any test number is looked at:** the finalist is the recipe with the highest mean validation TPR@1e-3 at its selected epoch; recipes within one standard error of each other are tied, and a tie goes to the recipe with fewer changes against R0 and then to the lower validation loss. R4 (only lr changed, the authors' clip 0.5 kept) and R7 are tied, so **R4 at epoch 2** is the current finalist (`select_epoch` and early stopping on validation loss both say epoch 2 for R4).
**Round 1d plan (margin check, because 3e-3 sits next to a collapse):** R8 lr 2e-3 and R9 lr 5e-3, 5 seeds, 4 epochs, 10 runs, about 16 min wall, estimate **0.6 h** (round 1c: 0.88 h for 6 epochs). If R9 also collapses or is unstable, R4 at 3e-3 is a brittle choice and the more stable of R4/R8 wins on validation by the rule above. After that: final retrain of the chosen recipe, 5 seeds, saved at the chosen epoch (estimate 0.4 h), then test evaluation. Projected total 3.8 h, hard limit 8 h.

**10.11 Round 1d result (validation only; kernel `nebula-gap-r1d`: R8 lr 2e-3, R9 lr 5e-3, 5 seeds, 4 epochs, 20 min wall, quota 20.48 h → 20.78 h = +0.30 h; follow-up total 3.07 h of 8 h).**
R9 (lr 5e-3): **unstable**, 3 of 5 seeds collapse to a constant predictor (AUC 0.5000; the other two reach 0.9984 and 0.9764). So lr 3e-3 (R4) has only a factor of about 1.7 of margin to a recipe that sometimes diverges.
R8 (lr 2e-3): as good as R4 on validation and safer: epoch 2 TPR@1e-3 0.898 ± 0.088 (R4: 0.899 ± 0.042), TPR@1e-2 0.985 (0.982), AUC 0.9984 (0.9984), and the **lowest validation loss of all recipes, 0.0679 (R4: 0.0872; R1 lr 1e-3: 0.0650 is similar)**. `select_epoch` gives epoch 2; early stopping on validation loss gives epochs [2, 1, 2, 2, 1].
**Decision by the rule of 10.10 (validation only):** R4 and R8 tie on TPR@1e-3; both change only the learning rate; the tie goes to the lower validation loss, and R4 sits next to a divergence cliff, so the finalist is **R8 = lr 2e-3, clip 0.5, dropout 0.3, batch 96, weight decay 1e-2, our BPE-50k, stop after epoch 2** (selected on validation, not on the test set). Next: final retrain, 5 seeds, models saved at epoch 2 (estimate 0.3 h), then the test evaluation.

**10.12 Final result (kernel `nebula-gap-final`, R8 retrained with 5 seeds, 2 epochs, models and logits saved: +0.11 h; follow-up total 3.18 h of 8 h; quota 20.89 h used, 9.11 h left).**
Validation of the retrain reproduces round 1d (mean val TPR@1e-3 0.898; seeds 0.930 / 0.941 / 0.930 / 0.741 / 0.947); its test numbers are identical to the grid's R8 (deterministic). Only now were test numbers of the final recipe looked at (`python -m baseline.gap_final`):
April test, logit-ranked, v2 / released / previous recipe: TPR@1e-3 **0.561 ± 0.043** / 0.518 / 0.406 ± 0.078; TPR@1e-2 0.793 ± 0.034 / 0.750 / 0.700 ± 0.045; AUC 0.9602 / 0.9586 / 0.9521; F1 0.893 / 0.885 / 0.897.
Bootstrap (1,000 stratified resamples, per-model means): v2 − previous: TPR@1e-3 +0.155 [+0.051, +0.221], TPR@1e-2 +0.093, AUC +0.0082, all resolved; v2 − released: +0.043 [−0.141, +0.183] (not resolved), TPR@1e-2 +0.043 [+0.027, +0.066] (resolved), AUC +0.0016 [−0.0000, +0.0033].
Literal float32 TPR@1e-3 of v2: 0.515 / 0.0 / 0.586 / 0.515 / 0.605 (seed 1 saturates). Output scale matches the released model (mean |logit| 15.4, 16.6, previous 33.7); total weight L2 420 (released 424, previous 405).
Verdict: the gap is closed on validation and on test; the explanation is learning rate (2.5e-4 too small) plus over-training. Appendix of the full grid on test (not used for selection) in `results/F_gap/final_table.md`. Baseline v2 models: Kaggle dataset `msingh9365/nebula-baseline-models` (new version), manifest keys `detect/bpe50k/v2/seed<k>`.
Not done: re-running the B2 upper/lower bounds with the v2 recipe (lowest priority; about 1 to 1.5 h of quota would have fit within the 8 h limit). A slip during the work: a stray `mv` replaced `/dev/null` in the container with a regular file; it was restored (character device 1,3) and `seed0.json` was copied back from the kernel output; nothing in the repository was affected.

## 11. Follow-up B3: the self-supervised experiment (paper Fig. 6) re-run with the baseline-v2 recipe

**Question.** With the v2 supervised recipe (lr 2e-3, up to 6 epochs, epoch chosen on validation), do the upper and lower bounds separate at FPR 1e-3, and does AR or per-position MLM pre-training close the gap (paper: upper − lower ≈ 15 points, AR within ≈ 3 of upper)?
Code: `baseline/b3.py` (driver), `baseline/b3_report.py` (selection, statistics, plots), `baseline/selfsup.py` (pre-training; new option: validation LM loss on a separate slice), `baseline/preprocess.py` (variant `bpe8k_v2`).

**11.1 Data (new, clean).**
- Validation slice: follow-up F's 10% (7,530 reports; hash in `baseline/gap_split_hash.json`, asserted in every run). Used for every choice (and for the LM validation loss of the pre-training: evaluation only); never trained on.
- Remaining 90% (67,768 reports): per seed 0 to 4 a stratified (by family) 80/20 split, `train_test_split(train_size=0.8, stratify=ym, random_state=seed)`: 54,214 unlabeled (pre-training) and 13,554 labeled (fine-tuning). Hashes of (unlabeled, labeled, validation) in `baseline/b3_split_hashes.json`, asserted in every run.
- Tokenizer: the existing `bpe8k` was **fit on all 75,298 January reports, i.e. including the validation slice** (`results/_tokens_raw/out/variants/bpe8k/info.json`: `trained_on_train`, no subset). It is therefore **refit** on the 90% only (67,768 reports): variant `bpe8k_v2`, CPU kernel `nebula-b3-tokens` (about 1 h of CPU, no GPU quota), published as the private dataset `msingh9365/nebula-b3-tokens`; every run asserts `tokenizer_fit_reports == 67768`.
  **Limitation of follow-up F that this finding exposes:** F's BPE-50k tokenizer was fit on all of January, the validation slice included (unsupervised, no labels, but the slice's text helped to build the vocabulary). F's R3 (released tokenizer, no effect) suggests the influence is negligible, but F's validation numbers are not strictly clean in this one respect. B3 does not have this problem.

**11.2 Runs (5 seeds each, same seeds and splits for all).** 1 `upper` (chunked, all 90%), 2 `lower` (chunked, 20% only), 3 `lower_lasttoken` (causal last-token classifier, 20%, no pre-training: the architecture-matched control),
4 `ar_lasttoken` (full-attention causal LM on the 80%, then the last-token classifier on the 20%), 5 `mlm_bert` (per-position BERT MLM on the 80%, then the chunked classifier on the 20%). Not run (unless quota is left at the end): the authors' multi-hot MLM, AR flatten.

**11.3 Recipe.** Pre-training (4, 5): B2's LM settings (AdamW lr 2.5e-4, batch 96, gradient clipping 1.0), **6 epochs**, early stopping on the validation-slice LM loss (patience 2, min delta 0.01), a checkpoint after every epoch; fine-tuning starts from the epoch with the lowest validation LM loss (the weights are restored by the callback).
Supervised and fine-tuning (1 to 5): the v2 recipe with the authors' `ModelTrainer`: AdamW weight decay 1e-2, batch 96, dropout 0.3, gradient clipping 0.5, **up to 6 epochs**, constant lr, validation metrics after every epoch. **Learning rate: both 2e-3 (v2) and 1e-3 (the allowed fall-back) are run for every run type** (so no run type gets more tuning than another) and chosen on validation.
After every epoch the validation and the April test **logits are stored** (test: stored, not looked at until the settings are chosen; no test number is printed in the logs). Ranking by logit; the literal float32 TPR@1e-3 is kept.

**11.4 Selection rule (written BEFORE any run; validation only, the same for every run type).**
For each run type, learning rate and epoch e = 1..6: m = mean over the 5 seeds of the validation TPR@1e-3 (logit-ranked), SE = std (ddof 1) / sqrt(5).
(a) *Collapse guard:* a (run type, lr) cell is **collapsed** if any seed has validation AUC < 0.6 at epoch 6 (constant prediction). A collapsed lr is excluded for that run type and reported; if lr 2e-3 collapses in any seed, lr 1e-3 is used for all seeds of that run type.
(b) Among the remaining (lr, epoch) cells, `best` = the highest m. Every cell with m within **one SE of the best cell's SE** is tied with it. Among tied cells choose the **fewest epochs**, then the **lower mean validation loss** (this also decides between the two lrs at the same epoch). TPR@1e-2, AUC and F1 are reported next to it, not used for selection.
(c) The chosen (lr, epoch) is the same for all 5 seeds of a run type. The pre-training epoch is the best-validation-LM-loss epoch (early stopping), fixed in advance.
The validation slice has 2,467 benign reports, so FPR 1e-3 allows 2 false alarms there: validation TPR@1e-3 is noisy (seed std 0.04 to 0.19 in F), and a rule of this kind selects some noise in every run type alike; this is stated in the report.

**11.5 Statistics (as in B2).** Mean ± std over seeds of TPR@1e-3, TPR@1e-2, AUC, F1(0.5) at the chosen settings; paired per-seed differences (upper − lower, each pre-trained run − lower, AR − its causal control, upper − each pre-trained run); stratified bootstrap of the April test reports (1,000 resamples, same resamples for all runs; per-seed-mean and seed-ensemble flavours); **resolved** = the 95% CI excludes 0.

**11.6 Cost estimate (T4 speeds of F: 17 batches/s, about 5 s to score validation + test per epoch; B2: AR about 2.3 min per epoch on 60k reports, MLM about 1.6 min per epoch).** Per seed, one T4, both lrs: `sup` unit (upper 2 × 4.7 min, lower 2 × 1.3, control 2 × 2.5) **about 17 min**; `ar` unit (pre-training 6 epochs about 14 min + 2 fine-tunings about 6 min) **about 20 min**; `mlm` unit (10 min + 4 min) **about 14 min**.
Total 5 × (17 + 20 + 14) = 255 GPU-min on two T4s = 128 min wall, charged for both GPUs: **about 4.3 h of quota** (F's estimates came out 30 to 50% too high). Kernel A (`nebula-b3-sup`, runs 1 to 3): about 1.5 h; kernel B (`nebula-b3-pre`, runs 4 and 5): about 2.9 h. **Hard limit 6 h.** Quota before: 20.89 h used, 9.11 h left (resets 2026-11-21).
Order: kernel A first (the bounds: "do they separate?"), then kernel B. If kernel B threatens the limit, the lr 1e-3 fine-tunings of the pre-trained runs are dropped first and this is reported. Measured hours go into §8.

**11.7 Launch log (2026-11-17).** `nebula-b3-tokens` (CPU, 53 min, no GPU quota): `bpe8k_v2` fit on 67,768 of 75,298 reports (validation slice left out), labels identical to the published `labels.npz`, max token id 8191, `x_train` encodes all 75,298 reports (the split indices keep their meaning).
Launched 19:25 UTC: `nebula-b3-sup` (runs 1 to 3, both lrs, 5 seeds; kernel source `nebula-b3-tokens`) and `nebula-b3-pre` (AR and MLM pre-training and fine-tuning, 5 seeds). Quota before: 20.89 h used.

**11.8 Kernel A result (`nebula-b3-sup`, runs 1 to 3, 5 seeds, both lrs, 6 epochs: 15 units all exit 0, 52 min wall, quota 20.89 h → 22.67 h = +1.78 h; the estimate was 1.5 h).**
Validation only (rule 11.4; no collapse in any cell; curves in `results/baseline/plots/b3_val_curves.png`): upper 0.91 ± 0.01 at lr 2e-3 epoch 3 to 4 (lr 1e-3: 0.86 to 0.89), lower 0.69 to 0.71 (lr 2e-3, epochs 3 to 5), control 0.75 (lr 1e-3, epochs 3 to 5).
**Chosen by the rule (final, `results/B3_selfsup_v2/choice.json` once all kernels are in): upper lr 2e-3 epoch 3; lower lr 2e-3 epoch 3; lower_lasttoken lr 1e-3 epoch 3.**
After these three were chosen, their April test numbers were read once (the choices of the pre-trained run types follow the same mechanical rule and do not depend on them): upper TPR@1e-3 0.522 ± 0.092, lower 0.368 ± 0.075, control 0.412 ± 0.055; TPR@1e-2 0.772 / 0.666 / 0.650; AUC 0.9666 / 0.9530 / 0.9487. **The bounds separate: 15.4 points at 1e-3 (the paper: about 15), 10.6 at 1e-2** (bootstrap CI with the final table).
Kernel B (`nebula-b3-pre`, AR and MLM) is still running; the projected total is 1.78 + 2.9 = 4.7 h of the 6 h limit.

**11.9 Result (kernel B `nebula-b3-pre`: 10 units all exit 0, 82 min wall; B3 total 2.26 h of 6 h; quota 23.15 h used, 6.85 h left).**
Pre-training: all 10 runs used all 6 epochs, no early stop, best epoch 6, the validation LM loss still falling (AR 2.04 → 1.12 to 1.20, MLM 4.2 → 3.3). Settings chosen by the rule 11.4 (validation only): AR lr 2e-3 epoch 3 (3 tied cells), MLM lr 2e-3 epoch 6; no collapse in any cell.
April test (logit-ranked, mean ± std over 5 seeds, chosen settings): TPR@1e-3 upper 0.522 ± 0.092, lower 0.368 ± 0.075, control 0.412 ± 0.055, AR 0.463 ± 0.072, MLM 0.404 ± 0.037; TPR@1e-2 0.772 / 0.666 / 0.650 / 0.711 / 0.696; AUC 0.9666 / 0.9530 / 0.9487 / 0.9617 / 0.9566.
Paired (per-seed mean, bootstrap CI of the difference): upper − lower +15.3 [+10.9, +18.7] at 1e-3, +10.7 at 1e-2; AR − lower +9.5 [+6.1, +14.6] (62% of the gap), MLM − lower +3.6 [−0.6, +7.6] (not resolved); AR − control +5.1 [+3.0, +12.3] (2 of 5 seeds positive); upper − AR +5.8 [−0.1, +9.5] at 1e-3 and +6.2 [+5.1, +8.1] at 1e-2.
Seed-ensemble flavour: upper − lower at 1e-3 only +1.7 [−0.4, +12.2]. Literal float32 TPR@1e-3: 0.000 for all 5 MLM seeds.
Deliverables: `results/B3_selfsup_v2/`, `results/baseline/plots/fig6_v2.png`, `b3_val_curves.png`, encoders `baseline_models/ssl/{ar,mlm}_pretrained_v2_seed*.pt` (manifest keys `ssl/ar_pretrained_v2/seed<k>`, `ssl/mlm_pretrained_v2/seed<k>`, tokenizer `bpe8k_v2`), Kaggle dataset `msingh9365/nebula-baseline-models` v4, REPORT §5.2c, §6.5, `results/baseline/tables.md` regenerated (new sections B3 and F).

**11.10 Addendum plan (written before launching; the main B3 deliverables are final and pushed).** Quota is left (6.85 h; B3 used 2.26 h of 6 h), so the two runs that the task allowed "only if quota is left at the end" are run:
`mlm_theirs` = the authors' multi-hot MLM (their `MaskedLanguageModelTrainer`, 6 epochs, early stopping on the validation-slice LM loss as before, encoder kept, then the chunked classifier fine-tuned on the 20%) and `ar_flatten` = the AR weights of the main run (imported from the output of `nebula-b3-pre`, the same files, best epoch 6) fine-tuned with the bidirectional flatten classifier on the 20%.
Same rule as 11.4 (validation only, both lrs, up to 6 epochs, collapse guard), same seeds and splits. They are reported as an addendum row in §5.2c; **the main conclusions do not depend on them and the rule and the other run types are not touched**.
Cost estimate: `mlm_theirs` about 12 min per seed (B2: 16 min for 15 epochs), `ar_flatten` about 6 min per seed (two fine-tunings of the full-attention model), 5 seeds each on two T4s: 5 × 18 = 90 GPU-min = about 45 min wall, **about 0.8 h of quota** (hard limit of the whole B3 follow-up 6 h; so far 2.26 h).

**11.11 Addendum, first kernel (`nebula-b3-extra`: mlm_theirs and arflat; quota 23.15 h → 23.59 h = +0.44 h).** `mlm_theirs` ran for all 5 seeds (exit 0, 25 min wall). `arflat` failed in all 5 seeds in 18 s: my `--import-from /kaggle/input/nebula-b3-pre` guess did not match the mount path (0 AR files imported) and the unit's assertion stopped it as intended (no run started from the wrong weights; the kernel exited with an error, not a false COMPLETE). Fix: search all of `/kaggle/input`. Relaunched as `nebula-b3-extra2` (`arflat` only, estimate 15 min wall, about 0.3 h).

**11.12 Addendum result (`nebula-b3-extra2`: AR flatten, 5 seeds, imported 10 AR files, 19 min wall, +0.33 h; B3 total 3.03 h of 6 h; quota 23.92 h, 6.08 h left).** Chosen on validation by rule 11.4: AR flatten lr 1e-3 epoch 6, the authors' MLM lr 1e-3 epoch 3; no collapse. The five main rows (and their CIs) are bit-identical after adding the two runs (same bootstrap resamples).
April test: AR flatten TPR@1e-3 0.407 ± 0.081 (+3.9 over lower, CI [+0.0, +9.8]), the authors' MLM 0.360 ± 0.127 (−0.8, [−4.8, +4.7]); TPR@1e-2 0.681 / 0.673; AUC 0.9581 / 0.9548. Literal float32 TPR@1e-3: 0.000 / 0.324. Written into REPORT §5.2c (addendum paragraph).

## 12. Follow-up: partial AUC, evaluation protocol, baseline v2 with 10 seeds (2026-11-18)

**Why.** TPR@1e-3 on the April set rests on 8 allowed false alarms (per-seed std 4 to 9 points). Add a more stable low-FPR metric (**partial AUC**), write the evaluation protocol (`EVAL_PROTOCOL.md`) before any thesis experiment, and extend baseline v2 to 10 seeds.
**Plan.**
1. `common.pauc(y, logits, max_fpr)`: area under the ROC curve from FPR 0 to `max_fpr` (linear interpolation at exactly `max_fpr`) divided by `max_fpr` (= mean TPR over FPR in [0, max_fpr]); logits only. Reported at 1e-2 (primary) and 1e-3; sklearn's McClish-standardized value stored next to it, labelled. Wired into `binary_metrics`, the bootstrap code (`long_stats`, `b3_report`, `gap_final`) and tests.
2. Re-score (no re-selection) from stored logits: baseline v2 (5 seeds), the released model, the previous recipe A (9 fold models), every B3 run at its chosen settings; paired differences with bootstrap CIs (same 1,000 resamples and seed as before, so the TPR numbers are reproduced exactly). Logits are all local (`results/F_gap`, `results/B3_selfsup_v2/raw`): no Kaggle download needed. Compressed float32 logits go to `results/logits/` (small).
3. Baseline v2 seeds 5 to 9 on Kaggle: recipe R8 (lr 2e-3, clip 0.5, dropout 0.3, batch 96, wd 1e-2, BPE-50k, the 90% January slice, 2 epochs), `gap.py` with the asserted split hash, models and logits saved. Cost estimate from the first 5 seeds (+0.11 h for the kernel): **0.15 h**; **hard limit for the whole follow-up 1.5 h**. Quota before: 24.20 h used, 5.80 h left (resets 2026-11-21). Measured hours go into §8.
4. `EVAL_PROTOCOL.md` (committed before any thesis experiment), REPORT §4, §5.8, status line, `tables.md`.
Nothing is re-selected: v2's recipe and B3's lr/epoch stay as chosen (on validation TPR@1e-3).

**12.1 Result (2026-11-18).** Implemented and tested: `common.pauc`, `pauc_mcclish`, `roc_summary`, `binary_metrics` (new keys `pauc@0.01`, `pauc@0.001`, `pauc_mcclish@...`), the bootstrap in `long_stats` (now TPR@1e-3, TPR@1e-2, AUC, pAUC@1e-2, pAUC@1e-3; the earlier TPR and AUC CIs of B3 are reproduced bit-identically), `b3_report`, `gap_final`; `baseline/tests/test_pauc.py` (7 tests; the 21 tests of long/b3/pauc pass).
Re-scoring (no re-selection; `baseline/pauc_report.py` asserts that B3's chosen lr/epoch are unchanged): `results/pauc/` and `results/logits/`. v2 seeds 5 to 9 (kernel `nebula-gap-v2-s59`, 5 units all exit 0, split hash asserted by `gap.run`, validation 0.87 to 0.94 at TPR@1e-3): +0.12 h.
v2 over 10 seeds: TPR@1e-3 0.527 ± 0.082 (first 5 seeds 0.561 ± 0.043, seeds 5 to 9 0.492 ± 0.102; Welch p 0.22), pAUC@1e-2 0.690 ± 0.036 (0.702 / 0.679, p 0.35). The std of pAUC@1e-2 relative to its mean is 1.5 to 4 times smaller than that of TPR@1e-3.
B3 under pAUC@1e-2: upper − lower +12.7 (5/5 seeds), AR − lower +6.9 (5/5), AR − control +6.3 (4/5), upper − AR +5.8 [+3.3, +8.2], MLM − lower +3.5 (3/5), authors' MLM +0.2 (n.s.); seed ensembles: AR − lower +1.6 (n.s.). `EVAL_PROTOCOL.md` written and committed before any thesis experiment. Models dataset `msingh9365/nebula-baseline-models` v5 (+ seeds 5 to 9).

## 13. New baseline: v2-PE (baseline v2 with the positional encoding that the paper describes) (2026-11-19)

**Status: working tree only. Nothing in this section is committed or pushed until it has been reviewed (instruction of 2026-11-19). No existing result, model or table is changed.**

**13.1 Why.** Paper §3.3, Eq. (1)-(2): `PE(pos, 2i) = sin(pos / 10000^(2i/d))`, `PE(pos, 2i+1) = cos(pos / 10000^(2i/d))`, "the positional encoding of the token at position pos in the sequence", added to the embedded vectors `e'_pos = e_pos + PE_pos`, for a sequence `e = [e_1, ..., e_N]` with N = 512 (spans of S = 64).
The pinned code does not do this. `nebula/models/attention.py`, `PositionalEncoding.forward` (batch-first): `x = x + self.pe[:1]`, i.e. the vector of position 0 is added to **every** token (commit `8bb17bd`, "batch-slot invariance"; before it `self.pe[:x.size(0)]` added one vector per batch slot, also not per token). `TransformerEncoderChunks.embed` additionally calls it once per 64-token chunk. So baseline v2, the released checkpoint and everything before them have **no per-token position signal** (only the chunk partition and the flatten pooling carry order). The thesis baseline should follow the paper.

**13.2 The change (own code only, `baseline/pe.py`; `third_party/nebula` and `patches/` untouched).** A subclass of `TransformerEncoderChunks` with `pe_mode`:
- `"released"`: exactly the current behaviour (calls the parent's `embed`).
- `"paper"`: `e'_t = sqrt(d) * Embedding(x_t) + PE(g_t)` followed by the same dropout, where `g_t = 64 * c + j` is the **global** position of the token at offset j of chunk c (c = 0..7, j = 0..63), so the chunk at index c gets positions 64c .. 64c+63 and not 0..63. The table is the model's own `pos_encoder.pe` buffer (sin/cos of Eq. 1-2 with d = 64), indexed by g. Padding tokens get their position too (the paper's equation is per position of the sequence, not per real token); the padding id is not masked anywhere in the released model either. Dropout, the sqrt(d) scale, the flatten pooling, the classifier head and the parameters are the same, so the **state dict has the same keys and shapes and the same initial weights for the same seed** (the PE table is a buffer, not a parameter): v2-PE seed k and v2 seed k start from identical weights.
- Positions are 0-based (token index 0..511), as in the released buffer `pe[p]` and as specified for this task; the paper's notation `e = [e_1..e_N]` can be read as 1-based. The two differ by a shift of one position in the argument of the sinusoids; `pos_offset` (default 0) makes the shift available and tested; v2-PE uses 0.

**13.3 Tests (`baseline/tests/test_pe.py`).** (a) in "paper" mode two positions inside one chunk and the same within-chunk position in two chunks get different vectors, and in "released" mode all positions get the same vector; (b) in "released" mode the logits equal those of the unmodified `TransformerEncoderChunks` **bit for bit** (`torch.equal`) on 50 real April reports (released tokenizer, the released checkpoint's weights); (c) the vector added at global position p equals Eq. 1-2 evaluated independently (numpy) for p = 0..511.

**13.4 Recipe: baseline v2, unchanged** (no tuning, nothing selected on April): AdamW lr 2e-3, weight decay 1e-2, batch 96, clip 0.5, dropout 0.3, the authors' `ModelTrainer`, BPE-50k (`baseline_models/tokenizers/bpe50k`), the 90% January slice (hash of `gap_split_hash.json` asserted), **2 epochs**, flatten pooling, **seeds 0 to 9**. Same code path as `baseline/gap.py` (`baseline/v2pe.py` reuses its helpers); same seeds give the same initial weights and data order as v2. Per-epoch validation metrics are stored; the April logits of epoch 2 are stored and **not looked at until all 10 seeds have finished**.
Order: CPU unit tests; smoke run on Kaggle (seed 0, 1 epoch in "paper" mode, plus seed 0 in "released" mode for 2 epochs to check that the subclass reproduces the existing v2 seed-0 logits); then seeds 0 to 9.

**13.5 Comparisons (EVAL_PROTOCOL.md).** v2-PE against v2 (released code, 10 seeds, same seeds) and against the released checkpoint. Primary pAUC@1e-2; secondary TPR@1e-3, TPR@1e-2, AUC, F1@0.5, pAUC@1e-3. Per-seed mean ± std; the 10-seed ensemble; stratified bootstrap (1,000 resamples, numpy seed 0, the same resamples as everywhere); per-seed differences; **claim rule (§5): the paired bootstrap 95% CI of the primary metric (per-seed means) excludes 0 AND the per-seed difference is positive in at least 7 of the 10 seeds** (negative in at least 7 for "worse"; otherwise "not resolved"); ensemble numbers next to it; validation-slice metrics next to the test metrics; output scale as in REPORT §5.7 (mean |logit|, benign logit p99, malware share above logit 16.6, total weight L2).
Because the seeds share initial weights and data order, the per-seed difference is a clean paired difference of the PE change.

**13.6 Budget.** Quota before: 26.84 h used, 3.16 h left (resets 2026-11-21). Estimate: smoke 0.1 h (two short runs), full 10 seeds about 0.25 h (v2 seeds 0-4: +0.11 h, seeds 5-9: +0.12 h) = **about 0.35 h**; the task's stop-and-ask threshold is 1.5 h.

**13.7 Result (working tree only; not committed).** Smoke: the released-mode subclass reproduces the existing v2 seed-0 logits exactly (test and validation identical): faithful and deterministic. Full run: 10 units exit 0, split hash asserted, 1,412 batches each. The April logits were first looked at after all 10 seeds had finished.
April test, logit-ranked, 10 seeds, v2-PE / v2 / released: pAUC@1e-2 **0.705 ± 0.031** / 0.690 ± 0.036 / 0.659; TPR@1e-3 0.543 ± 0.063 / 0.527 ± 0.082 / 0.518; TPR@1e-2 0.811 / 0.788 / 0.750; AUC 0.9644 / 0.9624 / 0.9586; F1 0.915 / 0.901 / 0.885.
Claim rule on pAUC@1e-2: v2-PE − v2 = +1.45 points, CI [+0.14, +2.79] but positive in only 6 of 10 seeds → **not resolved**; v2-PE − released = +4.6, CI [+0.7, +8.1], 9 of 10 seeds → **resolved**. Ensembles: v2-PE − v2 +0.7 [−0.9, +2.4] (not resolved).
Output scale: mean |logit| 28.5 (v2 17.7, released 16.6); 68% of malware above logit 16.6; literal float32 TPR@1e-3 0.060 (v2 0.317): rank by logit. Packaging: models in `results/_models_big/detection/bpe50k/v2_pe/`, manifest entries `detect/bpe50k/v2_pe/seed<k>` (the 130 existing entries unchanged), loader alias `bpe_v2_pe`, `results/logits/v2_pe.npz`, Kaggle dataset v6 (upload started). REPORT §5.9. Existing tables (`tables.md`) and sections 5.1-5.8 not changed.

## 14. ATT+bal on top of baseline v2-PE: attention pooling and balanced padding (2026-11-20)

**Status: working tree only; nothing in this section is committed or pushed until reviewed. Existing results, models and tables are not changed.**

**14.1 What is compared (all with the v2-PE base: v2 recipe unchanged, `pe_mode="paper"`, BPE-50k, the 90% January slice with the asserted hash, 2 epochs, seeds 0 to 9; nothing selected on April).**
| model | pooling | training data | note |
|---|---|---|---|
| v2-PE (baseline, exists, REPORT 5.9) | flatten | plain | the comparison base |
| **ATT** (run 1) | attention pooling | plain | |
| **ATT+bal** (run 2) | attention pooling | balanced padding | the model of interest |
| **PE+bal** (run 3, if quota allows) | flatten | balanced padding | separates the effect of the padding from the pooling |
Also compared: baseline v2 (released code) and the released checkpoint.

**14.2 Attention pooling** (ported from `hier_nebula/pooling_variants.py`, variant ATTx of nebula-length-study): one learned query q (d = 64 values, **initialised at 0**), scores `(x . q) / sqrt(d)` over the token vectors after the Transformer, softmax **over the real tokens only** (token id != 0, 0 = `<pad>`), output = the weighted sum of the token vectors, then the same head as v2 (first layer 64 -> 64 instead of 32,768 -> 64: the input size of the head follows from the pooled vector, as in the reference where `pooling="mean"` is used for the head size). A report without any real token gets weights 0. With q = 0 the weights are uniform, i.e. the **masked mean**. Implemented as a pooling option of `TransformerEncoderChunksPE` (`baseline/pe.py`, `pooling="attn"`); the attention still sees the padding positions (as in the released model); only the pooling ignores them. Unit tests: q = 0 gives the masked mean; padding gets zero weight; a no-real-token report is finite; the default `pooling="flatten"` is unchanged (bit-identical to the existing v2-PE logits on 50 April reports).

**14.3 Balanced padding** (as nebula-length-study round 4b, `scripts/pooling_v4/make_aug.py --balanced`): for every training report of the 90% slice (malware and benign alike), with probability 0.5: k ~ U{1..50} calls are added, **mode "insert" (k random gaps of the report's call list) or "prepend" (before the first call), 50/50**; each added call is a random call (uniform report of the pool, then uniform call of that report); the edited report is **re-tokenised with our BPE-50k** (`baseline_models/tokenizers/bpe50k`) and cut to the first 512 tokens. numpy `default_rng([7000, seed, epoch, row])` per report. **TRAIN pool = the benign reports of the 90% slice only** (never the validation slice, never April). One array per (seed, epoch) for seeds 0 to 9 and epochs 1, 2 (20 arrays); the epoch-e array overlays its rows over the original ones in epoch e only (the validation slice stays unedited). Reports without calls are not edited.
The "calls" and the filtered reports are those of `hier_data/signal/reps.bin` (the Nebula-filtered reports of all 92,700 Speakeasy reports, made by the same `PEDynamicFeatureExtractor.filter_and_normalize_report`; the length study's `Reps`): no raw re-filtering is needed. The mapping of our rows to `reps.bin` is by report hash and is **verified** by re-tokenising the unedited reports with BPE-50k and comparing them with the stored `x_train`/`x_test` rows (they must be identical) before anything is built. Built on this machine (CPU, 4 workers); the time is reported before upload, then uploaded as a private Kaggle dataset.

**14.4 Training change for the padded run.** The authors' `ModelTrainer.fit(x, y, epochs)` takes one array; the padded runs fit one epoch at a time on that epoch's array. Checked on CPU: fitting epoch by epoch on unchanged data reproduces the single `fit(epochs=2)` logits exactly (same data order and optimizer state), so the only difference to a plain run is the padded rows. Same recipe and seeds as v2-PE; same initial weights per seed as v2-PE except the attention head.

**14.5 Evaluation (EVAL_PROTOCOL.md) for every new model against v2-PE, v2 and the released checkpoint.** pAUC@1e-2 primary; TPR@1e-3, TPR@1e-2, AUC, F1, pAUC@1e-3 secondary; per-seed mean ± std; 10-seed ensembles; stratified bootstrap (1,000, numpy seed 0, the same resamples); per-seed differences and the 7-of-10 claim rule (CI of the primary metric excludes 0 AND the same sign in at least 7 of 10 seeds); validation-slice metrics next to the test metrics; output scale as in REPORT 5.7.
**Random benign padding test** (as `scripts/pooling_v4/padding_eval.py`, k = 5, 20, 50 and modes prepend/insert, i.e. 6 edits) on v2-PE and every new model: every April malware report (9,399) and 2,000 random benign April reports (seed 7) are padded with k random calls of the **EVAL pool = benign reports of the 10% validation slice** (disjoint from the training pool, never trained on, not April), re-tokenised with BPE-50k, cut to 512 tokens. Thresholds are **fixed at 1% FPR on the unedited April benign reports** (per model and seed: the benign logit at rank floor(0.01 n) in descending order; a report is flagged if its logit is above it). Reported: the share of padded malware still flagged (and the drop from the unedited share), and the share of padded benign flagged (padded-benign FPR). The padded arrays are made once (numpy seeds fixed per report, k and mode) and scored by every model.

**14.7 Run 1 (ATT, plain data), 2026-11-20:** kernel `nebula-att-full`, 10 seeds, all exit 0, 10 min wall, quota 27.06 h → 27.24 h (+0.18 h; estimate 0.2 h), 2.76 h left. Per-seed validation pAUC@1e-2 0.959 to 0.974 (v2-PE: mean 0.962). April logits stored; not looked at yet.

**14.6 Order, cost and stop rule.** (1) code + tests, then run 1 immediately; (2) padding arrays (time reported), then run 2; (3) run 3 if quota allows; (4) padded April arrays + scoring kernel; (5) evaluation and REPORT 5.10.
Estimates (T4, 10 seeds each 2 epochs: v2-PE took 0.18 h): run 1 about 0.2 h (the attention head is smaller than the flatten head), run 2 about 0.2 h (one array overlay per epoch), run 3 about 0.2 h, padding-test scoring about 0.15 h (4 families x 10 seeds x 11,399 x 7 sets, about 5,000 reports/s per T4), two smoke runs about 0.05 h: **total about 0.8 h** against 2.94 h left (resets 2026-11-21). If any estimate exceeds the quota left: stop and ask. Quota now: 27.06 h used.

**14.8 Padding data (built on this machine, CPU, 4 workers).** Row map verified before anything was built: our 75,298 train and 17,402 test rows map one-to-one to `reps.bin` (names, labels agree) and re-tokenising 600 sampled unedited reports (300 train, 300 test) with BPE-50k reproduces the stored `x_train`/`x_test` rows exactly (0 mismatches). Pre-pass over `reps.bin` for the number of calls per report: one sequential read (cached, `results/padding/n_apis.npy`).
**TRAIN pool: 22,201 benign reports with at least one call of the 90% slice (3,706,146 calls); the validation slice and April excluded (asserted).** The 20 arrays (seeds 0-9 x epochs 1, 2) took **20.4 minutes in total** (51 to 93 s each; plan 5 s, fetching the pool calls 4 to 6 s, tokenising 50 to 80 s), 33,701 to 34,150 reports edited per array (22,607 to 22,987 malware, 10,995 to 11,255 benign; 50% of the 67,768), mean k 25.4 to 25.8, prepend 49 to 51%; 669 MB (uint16); uploaded as the private dataset `msingh9365/nebula-v2pe-augb` (the sanity checks: every row inside the 90% slice, none in the validation slice, token ids <= 49,999).
Padded April arrays for the padding test: 11,399 reports (9,399 malware + 2,000 random benign, numpy seed 7) x 6 edits in **95 s**; EVAL pool = the 2,467 benign reports of the validation slice (406,403 calls); 15 MB, dataset `msingh9365/nebula-v2pe-padtest`.
**14.9 First launch of runs 2 and 3 failed (2026-11-20 10:08): the padding dataset is not mounted at `/kaggle/input/<slug>` (FileNotFoundError after 1.5 min, no training done; +0.07 h of quota: 27.24 h → 27.31 h).** The driver and the scoring module now search `/kaggle/input` for the files (as `find_dir_with` does for the tokens); relaunched as version 2 of both kernels.

**14.10 Results (2026-11-20; working tree only).** Runs 2 and 3 (relaunched version 2): 10 units each exit 0, padding arrays found at `/kaggle/input/datasets/msingh9365/nebula-v2pe-augb`, edited rows per epoch equal the local build (33.7k to 34.2k). Padding-test scoring (`nebula-padtest-all`, 5 families x 10 seeds x 6 edits x 11,399 reports): 2 min per family, exit 0.
Quota: ATT 0.18 h, failed first launch 0.07 h, ATT+bal + PE+bal 0.35 h, padtest 0.11 h = **0.71 h** (27.06 h → 27.77 h; 2.23 h left; no estimate exceeded the quota).
April, pAUC@1e-2 (10 seeds): v2-PE 0.705 ± 0.031, ATT 0.613 ± 0.048, ATT+bal 0.707 ± 0.017, PE+bal 0.699 ± 0.022. Claim rule: ATT worse than v2-PE (resolved, 8/10 seeds negative); ATT+bal and PE+bal not resolved against v2-PE for single models (secondary: ATT+bal TPR@1e-2 -1.7 points, 7/10 seeds negative; AUC +0.7, 7/10 positive); 10-seed ensembles: ATT+bal pAUC@1e-2 -3.4 vs v2-PE (CI [-5.4, -1.6], resolved), PE+bal -3.3 (resolved); ATT+bal better than ATT (10/10) and than the released checkpoint (10/10).
Padding test (1% FPR threshold from unedited April): malware flagged under padding, mean of 6 edits: v2-PE 42.7% (−38.4 points), ATT 35.2% (−36.0), ATT+bal 74.9% (−4.6), PE+bal 73.8% (−4.9), baseline v2 41.5% (−37.4); padded benign flagged (2,000 benign subset): 1.0%, 0.45%, 1.3%, 1.9%, 4.0%. REPORT §5.10.

## 15. Three experiments to strengthen ATT+bal: clean copies (keep), malware-only padding (aug), attacks the models were not trained on (2026-11-20)

**Status: working tree only; nothing here is committed or pushed until reviewed. Edited reports exist in memory only (see 15.6). Follow EVAL_PROTOCOL.md for every claim; nothing is tuned or selected on April; every setting below is fixed now, before any run.**

**15.1 Models and fixed training settings.** v2 recipe unchanged (lr 2e-3, wd 1e-2, batch 96, clip 0.5, dropout 0.3, authors' `ModelTrainer`, BPE-50k, the 90% January slice with the asserted hash, 2 epochs, `pe_mode="paper"`), seeds 0-9 (the same seeds as v2-PE: same initial weights except the head, same data order of the clean reports).
Padding procedure and TRAIN pool exactly as §5.10: per padded report k ~ U{1..50} calls, mode insert (k random gaps) or prepend (50/50), each call a random call of a random report of the TRAIN pool (22,201 benign reports with at least one call of the 90% slice; never the validation slice, never April), re-tokenised (BPE-50k) and cut to 512 tokens.
| model | pooling | training data per epoch |
|---|---|---|
| **ATT+bal-keep**, **PE+bal-keep** | attention / flatten | **all** clean reports of the 90% slice **plus** a padded copy of each report (malware and benign) with probability 0.5: nothing clean is replaced; the epoch has about 1.5x as many reports (about 101.7k, about 1,059 batches instead of 706), so training takes about 1.5x as long. Random stream `default_rng([7100, seed, epoch, row])` (a new stream: the copies differ from the §5.10 arrays) |
| **ATT+aug**, **PE+aug** | attention / flatten | the §5.10 procedure (the padded report **replaces** the original, probability 0.5, stream `[7000, seed, epoch, row]`) applied to **MALWARE training reports only**; benign reports are never padded. The edits of the malware reports are identical to those of the §5.10 balanced runs (the plan depends on seed, epoch and row, not on the label) |
**15.2 Experiment 2 evaluation:** clean metrics, padded-malware TPR and padded-benign FPR on **all 8,003 April benign reports** (the random-padding test of §5.10 with the EVAL pool: 6 edits, k = 5, 20, 50, prepend/insert, now with every April report), and the **shortcut probe**: logistic regression on the pooled embedding (before the head) predicting "padding present" on April reports padded or not: every April report is padded with probability 0.5 (numpy seed 11; k ~ U{1..50}, insert/prepend 50/50, EVAL pool calls, in memory), the reports are split by index into two halves (even/odd rows), the probe is trained on one half and its AUC measured on the other (and vice versa, mean); features z-scored with the training half's statistics, L2 penalty 1e-2 (LBFGS, 100 iterations), flatten models: the 32,768-d flattened vector, attention models: the 64-d pooled vector; plus for all models the 64-d hidden vector after the first head layer (same size for every model). Models: v2-PE, PE+bal, ATT+bal, PE+aug, ATT+aug; all 10 seeds.
**15.3 Experiment 3, attacks the models were not trained on** (thresholds fixed at 1% and 0.1% FPR on the unedited April benign scores of each model and seed; every April report is used: 9,399 malware, 8,003 benign; reported: malware TPR, padded-benign FPR, TPR on the subset whose whole edited report fits in 512 tokens; ATT+bal − PE+bal per test with seed-paired intervals (stratified bootstrap over the test reports, 1,000 resamples, numpy seed 0) and the 7-of-10 count).
a. **Surrogate-chosen padding.** Candidates = the EVAL pool (benign reports of the validation slice, 2,467 reports); the unit of ranking is the API name, with the most frequent call of that name in the EVAL pool as its representative call. Score drop of a name = the mean, over a fixed sample of 500 malware reports of the 90% slice (not April; numpy seed 21), of (surrogate score with the representative call prepended) − (surrogate score), for (i) a **LightGBM** bag-of-API-names model (counts of the API names, fixed hyper-parameters: 300 trees, 31 leaves, lr 0.05, fitted on the 90% slice; the drop of a name = the score change when its count is raised by 1) and (ii) **v2-PE seed 0** (the call prepended and the report re-tokenised). Rank names by the drop (most negative first). **Pad with the top-ranked calls: for k = 5, 20, 50 the k representative calls of ranks 1..k**, insert (k random gaps per report) and prepend (in rank order). All 10 seeds of every model, both surrogates.
b. **White-box greedy.** 500 random April malware reports (numpy seed 31, fixed list), prepend up to 20 calls, each step: draw 200 random calls of the EVAL pool (numpy seed 41 + step, the same candidates for every model), take the one that most lowers the model's own score of the report (the candidate prepended in front of the calls chosen so far); report the TPR curve against k = 0..20 (share of the 500 still flagged at the 1% and 0.1% thresholds). **Seeds 0-2 per model.**
**15.4 Decisions that are mine and stated here:** the "fits in 512 tokens" subset = reports whose whole edited token sequence has at most 512 tokens; thresholds use the model's own scores of all unedited April benign reports (benign logit at rank floor(0.01 n) and floor(0.001 n) in descending order; a report is flagged if its score is above the threshold); the released checkpoint has one model (no seeds).
**15.5 Estimates (T4 x 2; measured: a 10-seed 2-epoch run = 0.18 h; scoring 8.8k reports/s on both GPUs; CPU scoring 950 to 1,160 reports/s with 4 threads; per-call tokenization 11 us).**
GPU training: keep models 2 x 0.25 h, aug models 2 x 0.18 h, smoke 0.04 h = **about 0.9 h** (within 1.5 h; no stop needed for the runs of experiments 1 and 2).
Scoring that does not fit "CPU" (every number is a forward pass of a 512-token report): experiment 2's padding test on the four new families (4 x 10 models x 6 edits x 17.4k = 4.2M passes) and the probe (about 0.5M): CPU 1.3 h or GPU 0.15 h; attack 3a: models released + 3 families x 10 + 2 keep families x 10 = 51 models x 12 edit sets x 17.4k = 10.6M passes: **CPU 2.9 h**, GPU 0.33 h; attack 3b: 500 x 200 x 20 = 2M passes per model and seed, 16 model-seeds = 32M passes: **CPU 9 h**, GPU 1.0 h.
**So the full programme (training 0.9 h + GPU scoring 0.3 + 0.33 + 1.0 h) is about 2.5 h, above the 1.5 h budget and above the 2.23 h of quota left; the attacks cannot run on CPU tonight either.** I run what fits (training; CPU work while it trains: store, ranking, LightGBM, tests) and ask before the GPU scoring of 3a/3b (see the status message).
**15.6 Edited reports exist in memory only.** The in-kernel padding for the keep and aug runs and every attack edit is built from a store of the ORIGINAL reports (per-call token arrays; no edited text or tokens are ever written); only aggregate numbers are saved. Verification: the store reproduces, token for token, the tokens of the full re-tokenisation of edited reports (tested on the §5.10 arrays that already exist).
**Existing artefacts that predate this rule (to be decided by the owner):** `results/att_bal/pad/april_pad.npz` (tokens of padded April reports; **tracked and pushed in commit 6f22129**), the Kaggle datasets `nebula-v2pe-padtest` (the same file) and `nebula-v2pe-augb` (the §5.10 training arrays), and the local copies in `results/_pad_train`, `results/_pad_bundle`. I do not delete them without asking; the new runs do not use or create such files.

**15.7 Implementation log and decisions made while building (2026-11-19/20, before any attack score was seen).**
- The call-token store was checked before use: 3,000 unedited reports rebuilt from their pieces equal the stored tokens (0 differ); 1,500 edits built by concatenation equal full re-tokenisation, tokens and total length (0 differ); the in-memory edits of seed 0 epoch 1 and seed 3 epoch 2 reproduce the existing §5.10 arrays row for row and token for token (34,019 and 34,059 edited reports). The same was done for a second store made with the **tokenizer of the released checkpoint** (needed to attack the released model, whose token ids differ from ours): 0 of 3,000 unedited and 0 of 1,000 edited reports differ. Both stores hold ORIGINAL reports only (uploaded as the private dataset `nebula-callstore`).
- GPU smoke (2 seeds, 1 epoch, ATT, keep): exit 0; 101,484 reports per epoch (67,768 + 33,716 padded copies = 1.50x); TRAIN pool 22,201 reports (as in §5.10); one epoch = 111 s per seed with two seeds in parallel. Estimate for a 10-seed keep run: about 0.35 h (not 0.25 h); aug runs about 0.2 h. Total training about 1.15 h, still under the 1.5 h limit.
- The white-box attack (3b) keeps the best (lowest) score reached so far for each report ("the attacker keeps the best edit"), so the TPR curve against k never rises; a report whose score reaches the 1% threshold stops (it is evaded at both thresholds, so more calls cannot change its outcome in the curve). The greedy step itself always adds the best of the 200 candidates, even if it raises the score. Both rules were fixed before any attack score existed.
- The surrogate for ranking (ii) is v2-PE seed 0 scored on CPU: 1,031 API names with a representative call in the EVAL pool x 500 malware reports = 0.5M forward passes.
- Probe: loss = mean cross-entropy + 1e-2 * ||w||^2 / 2 (LBFGS, strong-Wolfe, 100 iterations), features z-scored with the training half's statistics; a shuffled-label control is stored next to every probe (expected AUC about 0.5).

**15.8 Results log (2026-11-19).** Training (first account): ATT+bal-keep and PE+bal-keep 10 seeds each (101,484 reports in epoch 1, 1,058 batches), ATT+aug and PE+aug 10 seeds each (22,865 and 22,814 malware reports edited in epochs 1 and 2); all with the asserted split hash. GPU scoring on a second account (the owner's, because the quota of the first did not cover it; the owner approved): smoke kernel (2 models; in-memory unedited scores = stored logits, max difference 3e-5; the random-padding edits = the arrays of §5.10 token for token on 600 reports x 6 edits), then stage 3a (51 models x 13 edit sets), 3b1 + 3b2 (white-box, 16 model-seeds), padprobe (random padding for 8 families, probe for 5). Outputs: scores only (`results/review/attack/`). Tables: `results/review/{table1,attack_tables,headline_tables,cluster_table1}.md`; REPORT 5.11 and `RESULTS_FOR_REVIEW.md` are composed from them by `baseline/review_compose.py`.
**Correction.** In the first status message I wrote that only 10.6% of April reports fit into 512 tokens (mean 1,798). That was measured on the first 500 April rows (sorted by family), not on all of April. Over all 17,402 reports: 36.6% fit unedited (malware 30.4%, benign 43.9%), mean length 1,056 tokens. The report uses the correct numbers.
**Not committed or pushed** (rule of this task). Untracked/modified: see `git status`.
