# Row index and released-Nebula scores

Copies of two files that `hier_nebula` writes outside the repository (in
`../hier_data/speakeasy/`), saved here so a new session does not have to
rebuild them.

| file | what it is |
|---|---|
| `meta.csv` | one row per report, 92,700 rows, in `measure_lengths.list_files()` order (the order `hier_nebula.train prepare` writes). Columns: `id` (file name without `.json`), `split`, `family`, `label` (1 = malware; `clean` and `windows_syswow64` are benign), `label_family`, `n_tokens_full`, `dataset`, `n_chunks` (512-token chunks, capped at 8). |
| `nebula_score_chunk0.npy` | float32 array of 92,700 scores, aligned with `meta.csv` row by row: the **released Nebula** model (`bpe_50000_torch.model`) on the first 512 tokens of each report, i.e. Nebula's own prediction (made by `hier_nebula.train embed`). |

How they join to the rest:

- `row` in `results/hier/<run>/test_scores.csv` is the row number (0-based) in `meta.csv`.
- `results/misses/reports.csv` has the same 92,700 rows in the same order.
- `results/samples.csv` joins on `split` + `sample_id` (= `meta.csv` `id`).

Checks done before saving: both files have 92,700 rows; the released-Nebula
scores give test AUC 0.9586 (REPORT.md §7); every `test_scores.csv` row is a
testset row of `meta.csv` with the same label.

Note: `frozen_k1` in `results/hier/` is **not** the released Nebula. It is
the frozen Nebula chunk vector plus a trained second level. The released
model's own scores are the ones in this folder.

To use them where the scripts expect them:

```bash
mkdir -p ../hier_data/speakeasy && cp results/hier/data/meta.csv results/hier/data/nebula_score_chunk0.npy ../hier_data/speakeasy/
```
