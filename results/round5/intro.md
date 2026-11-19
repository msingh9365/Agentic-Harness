Builds on `results/pooling_v4` (rounds 4 and 4b). Nothing in this folder is committed. Rules used throughout: thresholds fixed at 1% and 0.1% FPR on the unedited April benign scores of each model and seed;
group-bootstrap intervals over April `hash_apis` (1,000 resamples) and seed-paired intervals (95% over seeds); edited reports exist in memory only (only scores and aggregate numbers are written); only the
EVAL padding pool of `results/pooling_v4/pools.json` is used for testing (the TRAIN pool is used for training augmentation, and once, to define "rarest 20% of API names", in `prep_pools5.py`).

Models: **ATT+bal**, **MM+bal**, **C+bal** = C with attention / mean+max / mean pooling, fixed position encoding, 512 tokens, trained on all of January (regime J) with balanced padding (every training report, malware or
benign, gets 1-50 calls of the TRAIN pool inserted or prepended with probability 0.5); G1: seeds 0-9, 4 epochs, epoch 2 is primary (same data order and learning-rate schedule as a 2-epoch run; epoch 4 as a second table).
References on the same seeds: **released Nebula**, **A (J)** (flatten pooling, 1 epoch), **C (J)** (mean + fixed position encoding, 10 epochs), **C (J, 2 epochs)** (= C after its epoch 2), whole-report **F**
(`results/fulltrace`, seeds 0-4), and the bag-of-API LightGBM of `results/go_no_go` for the rank averages.
