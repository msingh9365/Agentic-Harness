## GPU part (Kaggle, T4 x2)

Quota before the batch: 24.32 h of 30 h used (5.68 h remaining); weekly quota resets **2026-11-21 00:00 UTC**. A 1-epoch smoke run (4 jobs: ATT+bal J, MM+bal J, ATT+bal S, A S; 52-64 s per epoch, 2.5 min wall, 0.04 h)
gave a batch estimate of 2.3-2.6 h at the charge rate of about 1 x wall time, far below the 6 h limit, so the batch was launched without asking. (The whole-report run of `results/fulltrace` had been charged 2.9 x
its wall time; this round the charge was 1.0 x.) Quota after the round: **26.84 h used, 3.16 h remaining**, same reset.

| run | what | jobs | wall time | quota charged |
|---|---|---|---|---|
| G1 | ATT+bal, MM+bal, C+bal, regime J, balanced padding, seeds 0-9, 4 epochs, scores after every epoch (fp32 epoch checkpoints) | 30 | 64.8 min (63 s per epoch) | 1.07 h |
| G2 | regime S (January train side only; the validation side is held out): ATT+bal, MM+bal, C+bal, ATT (no padding), A, seeds 0-9, 2 epochs | 50 | 49.1 min (55 s per epoch; queued 19 min before starting) | 0.82 h |
| G3 | ATT+bal over the whole report (up to 4,096 tokens), balanced padding of the full report, regime J, seeds 0-4, 2 epochs | 5 | 34.1 min (337 s per epoch) | 0.58 h |

Checks of the G1 runs: the CPU logits of the epoch-2 checkpoints equal the Kaggle logits (maximum difference 0.0000 on 1,500 reports, 4 runs); epoch 2 of a 4-epoch run reproduces the round-4b 2-epoch run of the same
seed (April AUC 0.9787 and 0.9787, score correlation 1.0000). The augmentation tokens were precomputed on this machine (`scripts/pooling_v4/make_aug.py --balanced`, `make_aug_full.py` for G3) and uploaded as private
Kaggle datasets; the regime S runs drop the validation-side rows of those files.
