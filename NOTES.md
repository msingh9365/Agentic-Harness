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
| | | | | (filled in as jobs run) |
