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
