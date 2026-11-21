### Step 2, part 1: early-stopping epoch per seed (validation pAUC@1e-2 only; ties -> earlier epoch)

- **v2pe** (epochs 1-4): best epoch per seed [1, 1, 3, 1, 4, 1, 3, 4, 2, 3]; mean validation pAUC@1e-2 at the per-seed best epoch 0.5059 (selection-biased, validation only) against 0.4843 at the Stage C epoch 1; Stage C reproduction on validation logits of epoch 1: 10/10 seeds identical, largest logit difference 0.00e+00
- **attbal** (epochs 1-6): best epoch per seed [5, 2, 2, 3, 4, 5, 1, 2, 1, 3]; mean validation pAUC@1e-2 at the per-seed best epoch 0.4802 (selection-biased, validation only) against 0.4704 at the Stage C epoch 3; Stage C reproduction on validation logits of epoch 3: 10/10 seeds identical, largest logit difference 0.00e+00
