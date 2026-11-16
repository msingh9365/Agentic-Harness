# Reproducing Nebula (Trizna et al., arXiv 2310.10664v2) with the authors' code: baseline report

**Status: DRAFT. The fixed parts (setup, what is ours and what is theirs, patches, method) are written. The result sections are
filled in from `results/baseline/tables.md` when the Kaggle runs finish.**

The goal is a trusted baseline: trained models and numbers that can be compared with the paper, using the authors' own code,
including self-supervised pre-training, on Kaggle GPUs. Faithfulness to the paper matters more than clean code. Within ±2–3
percentage points counts as a match.

## 1. What was run

| item | value |
|---|---|
| Authors' code | <https://github.com/dtrizna/nebula>, commit **`1343ae170ef32b01a75d2dd5fb906b5541f073df`** (git submodule `third_party/nebula`) |
| Patches to their code | 4 one-line library-compatibility fixes in `nebula/lit_utils.py` (`patches/0001..0004`, §3). No logic changed |
| Data | Kaggle `dmitrijstrizna/quo-vadis-malware-emulation` (id 3231810): train = January 2022 (75,298 reports), test = April 2022 (17,402 reports). **Not** the 98,966 / 27,500 of the paper's Table 3 (§6) |
| Preprocessed data | private Kaggle dataset `msingh9365/nebula-baseline-tokens` |
| Trained models | private Kaggle dataset `msingh9365/nebula-baseline-models`; small files in `baseline_models/` |
| GPU | Kaggle NVIDIA T4 (x2 per session); the paper used a Quadro T2000 |
| Seeds | detection and classification: one 3-fold CV (`KFold(3, shuffle=True, random_state=1763)`, training seed 0 + fold); self-supervised: seeds 0, 1, 2 |
| Environment | Python 3.13 (Kaggle), package versions are logged in every `results/baseline/*/metrics.json` (`env`) |

## 2. What is theirs and what is ours

| step | theirs (called, not rewritten) | ours (new code in `baseline/`) |
|---|---|---|
| Report reading and labels | `read_and_filter_json_folders` | driver that runs it once per folder in parallel (`preprocess.py`) |
| Field filter, normalization | `PEDynamicFeatureExtractor.filter_and_normalize_report` | none |
| Tokenizers | `JSONTokenizerBPE`, `JSONTokenizerNaive` (train and encode) | none; fit on the training split only |
| Model | `TransformerEncoderChunks`, `TransformerEncoderModel` (incl. `causal_attention`, `pretrain_layers`) | `CausalLastTokenClassifier` (reads the last non-pad token) |
| Supervised training | `ModelTrainer` (AdamW, BCE / cross-entropy, time budget, clipping) | the 3-fold loop with test evaluation and the exact-N-batches stop (`cv.py`) |
| Metrics | `get_tpr_at_fpr` | F1/accuracy at 0.5, per-class F1, ROC on a log grid, aggregation (`common.py`) |
| MLM pre-training | `MaskedLanguageModelTrainer`, `LitTrainerWrapper`, `PyTorchLightningModelLM` | validation-loss callback; per-position BERT MLM as a second variant |
| AR pre-training | `AutoRegressiveModelTrainer` (unfinished in their repo), causal `TransformerEncoderModel` | full-512-token, padding-ignoring subclass |
| Fine-tuning | `LitTrainerWrapper` | weight transfer + checksum proof; the 80/20 stratified split |
| Reports, plots, loader | none | `report.py`, `package_models.py`, `baseline_models/load_baseline.py` |

Unit tests (`baseline/tests/`, all pass): masking is 15% with an 80/10/10 split for their MLM trainer and ours; the causal model cannot
see later tokens (with a control that shows the test can fail); the LM loss at the start is about ln V = 9.0; fine-tuning really
starts from the pre-trained weights (encoder checksum equal, distance to the pre-trained weights 0); the CV loop stops after exactly N
batches and the time budget stops training; the preprocessing driver gives **bit-identical token arrays and labels** to their wrapper
`preprocess_nebula_speakeasy` (BPE and Whitespace).

## 3. Patches to their code

See `NOTES.md` §5 for the full list with the errors they fix. All four are in `nebula/lit_utils.py` and are needed for Lightning ≥ 2.1:
`lightning.lite` → `lightning.fabric` import; `accumulate_grad_batches=None` → `1`; `optimizer_zero_grad(..., optimizer_idx)` made
optional; the masked-LM multi-hot target is no longer cast to int64. Found but not patched: the older `SelfSupervisedPretraining`
pipeline passes `forward_pass=` to `ModelTrainer` (it expects `modelForwardPass`), and their example `train_example_lit_mlm_eval.py`
uses `pooling=None`, which cannot run.

## 4. Method notes

(Filled in with the final numbers; the settings are in `NOTES.md` §4 and §7.)

## 5. Results

(Generated from `results/baseline/tables.md`.)

## 6. Differences from the paper, and their likely causes

(To be written from the measured differences.)
