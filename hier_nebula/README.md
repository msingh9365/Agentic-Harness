# Two-level Nebula (512-token chunks + a second Transformer)

Nebula reads only the first 512 tokens of a report. REPORT.md shows this cut
throws away 66.6% of all Speakeasy tokens, while 99.8% of reports fit in
8 × 512 = 4,096 tokens. This package reads **up to 8 chunks of 512 tokens**.

```
report ──Nebula preprocessing──► token ids (no truncation)
       ──cut into 512-token chunks (max 8, last one padded with 0)──►
chunk 1 ─┐
chunk 2 ─┤  level 1 = Nebula (TransformerEncoderChunks, released weights),
  ...    ├─ run on each chunk separately ─► one 64-d vector per chunk
chunk K ─┘  (the output of Nebula's first classifier layer)
                       │
[CLS] + chunk vectors + chunk-position embedding
                       │
level 2 = 2-layer Transformer (d=64, 4 heads, padding chunks masked)
                       │
LayerNorm(CLS) ─► Linear ─► malware score (or family logits)
```

Why this design:

* **Level 1 is exactly Nebula.** Its weights come from
  `nebula/objects/bpe_50000_torch.model`. With one chunk, Nebula's own head
  on the chunk vector gives Nebula's original prediction (checked in
  `tests.py`), so plain Nebula is a built-in baseline.
* **Chunks are fixed 512-token pieces, not processes.** The length study
  found 94.7% of Speakeasy samples have a single entry point, and 97% of
  threads contain one API call. So "one chunk per process" mostly wastes
  chunks.
* **Max 8 chunks.** This covers 99.8% of Speakeasy samples completely
  (REPORT.md §4).

## Files

| file | what it does |
|---|---|
| `model.py` | `HierNebula` and `build_level1()` (Nebula's model + released weights) |
| `data.py` | `prepare()`: Nebula preprocessing + tokenizer → `tokens.npy`, `offsets.npy`, `meta.csv`; `ChunkDataset` / `collate` → `[B, K, 512]` + chunk mask |
| `train.py` | `prepare`, `embed` (cache frozen level-1 vectors and Nebula's baseline score), `train --mode frozen` or `--mode finetune` |
| `tests.py` | correctness checks (see below) |

## How to run

From the repository root, with the environment from the main README plus
`torch` and `scikit-learn`:

```bash
pip install torch scikit-learn            # CPU is enough for "frozen"; use a CUDA build for "finetune"
python -m hier_nebula.tests --nebula ../nebula

# 1. tokenize all Speakeasy reports (keeps the first 8*512 tokens of each)
python -m hier_nebula.train prepare --dataset speakeasy --data-dir ../hf-git --out ../hier_data/speakeasy

# 2a. cheap: freeze Nebula, cache chunk vectors once, train only level 2
python -m hier_nebula.train embed --data ../hier_data/speakeasy
python -m hier_nebula.train train --data ../hier_data/speakeasy --mode frozen --max-chunks 8 --out results/hier/frozen_k8
python -m hier_nebula.train train --data ../hier_data/speakeasy --mode frozen --max-chunks 1 --out results/hier/frozen_k1   # ablation

# 2b. full: fine-tune both levels end to end (GPU recommended)
python -m hier_nebula.train train --data ../hier_data/speakeasy --mode finetune --max-chunks 8 --lr 3e-4 --out results/hier/finetune_k8

# multi-class (Nebula's 8 classes, syswow64 counted as clean)
python -m hier_nebula.train train --data ../hier_data/speakeasy --mode frozen --task multiclass --out results/hier/frozen_k8_mc
```

Splits: the dataset's own trainset/testset. 10% of the trainset (seed 0) is
used for validation and model selection. The testset is only used once, at
the end. Metrics: ROC AUC, TPR at FPR 0.1% / 1% / 10% (the numbers the
Nebula paper reports), and F1 and accuracy at threshold 0.5.

**Avast-CTU.** `prepare --dataset avast` uses the Avast BPE tokenizer from
the length study. No Nebula model was released for Avast, and the Speakeasy
weights belong to a different vocabulary. So Avast needs
`--scratch --mode finetune`; `embed` refuses Avast data on purpose.

## What `tests.py` checks

1. Level 1 on a chunk, followed by Nebula's head, equals the original Nebula
   output for the same 512 tokens.
2. Token chunks round-trip: same tokens, same order, padding with 0 like
   Nebula's `pad_sequence()`.
3. Masked (padding) chunks do not change the output, even if they contain
   junk tokens.
4. Gradients reach both levels, and `freeze_level1()` stops level-1
   gradients.

## Things to keep in mind

* **The released Nebula weights were trained on Speakeasy data**, presumably
  the same trainset. Validation is a slice of that trainset, so validation
  scores for frozen level-1 vectors may look optimistic. The testset
  (collected later) is the fair comparison.
* **Length shortcut.** A model that sees more chunks also sees how long a
  report is. REPORT.md §2.3 shows length alone separates some families
  (backdoor vs clean AUC 0.83). Compare against a length-only baseline, and
  report results per family.
* The `frozen` mode makes a quick experiment. The real test of the idea is
  `finetune`, where level 1 can learn to make chunk vectors that are useful
  for level 2.
