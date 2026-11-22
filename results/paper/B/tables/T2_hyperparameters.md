**Training settings of the four final models (all trained on the 75,298 January reports; settings chosen on a held-out validation slice, never on April).**

| setting | M1 v2-PE | M2 two-level | M3 ATT+bal | M4 ATT+bal-2L |
|---|---|---|---|---|
| tokenizer | corrected BPE-50k (bpe50k_fix) | corrected BPE-50k (bpe50k_fix) | corrected BPE-50k (bpe50k_fix) | corrected BPE-50k (bpe50k_fix) |
| input window | first 512 tokens | first 4,096 tokens (up to 8 chunks of 512) | first 512 tokens | first 4,096 tokens (up to 8 chunks of 512) |
| encoder (level 1) | 2 layers, 8 heads, d 64, hidden 256, chunks of 64 tokens | same (from scratch) | same | same (from scratch) |
| level 2 | - | 2 layers, 4 heads, hidden 128, dropout 0.1, chunk-position embedding | - | same as M2 |
| pooling | flatten | attention pooling per chunk, level 2 over chunks | attention pooling | attention pooling per chunk, level 2 over chunks |
| positional encoding | sinusoidal (paper Eq. 1-2) | sinusoidal | sinusoidal | sinusoidal |
| optimiser | AdamW, weight decay 1e-2 | same | same | same |
| learning rate | 2e-3 | 1e-3 | 1e-3 | 1e-3 |
| batch size, gradient clip, dropout | 96, 0.5, 0.3 | 96, 0.5, 0.3 | 96, 0.5, 0.3 | 96, 0.5, 0.3 |
| epochs | 1 | 1 | 3 | 1 |
| padding augmentation | none | none | balanced, p = 0.5 (malware and benign) | balanced, p = 0.5, before chunking |
| training reports | 75,298 (all of January) | 75,298 | 75,298 | 75,298 |
| seeds | 10 (0-9) | 10 | 10 | 10 |
| selection of the settings | validation slice (group split), NOTES 21.10 | validation slice, NOTES 23.1 | validation slice, NOTES 21.10 | validation slice, NOTES 23.1 |
