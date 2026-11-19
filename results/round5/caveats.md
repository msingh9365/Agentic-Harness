## Caveats

- Item 3 uses seeds 0-4 of every retrained model (ATT+bal, MM+bal, C+bal, A, C) and one released model; items 1, 2 and 5 use seeds 0-9 (F: seeds 0-4; rotation: ATT+bal 10 seeds, A and C 5, F 3; G3: 5 seeds). The unedited columns of the 5-seed tables therefore differ slightly from the 10-seed ones.
- The edits are random or chosen with the information described in each section; the white-box attack (3d) uses one trained seed per model, 500 reports and candidates from a fixed random subset of 30,000 of the 361,002 EVAL-pool calls; the surrogate rankings use January malware (not April).
- The EVAL pool has only 4 reports of source windows_syswow64 (370 calls); the rare-name pool has 763 calls (603 of 3,011 API names). Padding with long calls fills the 512-token window quickly (prepend 50), which for window-limited models is a separate effect from the content of the padding: see the "fits in 512 tokens" tables in the `pad_*.md` files.
- Item 2: the 0.1% FPR threshold of April is set by the 9th highest benign score (8 of 8,003 benign reports may lie above it), that of the January validation side by 2 of 2,103; the released Nebula's accuracy-table intervals at 0.1% (0.0%-67.0%) come from the stored probabilities, which saturate and tie; `lowfpr_april.md` uses its CPU logits (4 / 8 / 12 benign reports allowed above the threshold).
- The balanced padding of training uses the same kind of padding as the main test (random single calls of benign reports, pools disjoint by API-sequence group); the resistance shown for other padding (block, other source, rare names, optimised) is therefore a transfer result.
- Regime S models use 2 epochs without early stopping on the validation side (the validation side is a test set here). G2's ATT+bal, MM+bal and C+bal were trained with the augmentation files of regime J with the validation-side rows removed.
- Nothing here is committed.

## Files

`accuracy.md/json`, `accuracy_epoch4.md/json`, `lowfpr_april.md/json` (+ `_epoch4`), `janval.md/json`, `top_benign.md/json`, `pad_block.md`, `pad_syswow.md`, `pad_clean.md`, `pad_rare.md`, `pad_sur_lgb.md`, `pad_sur_c.md`, `attack_whitebox.md`, `rotation.md`, `graded_edits.md`, `pad_random.md`, `pad_random_g3.md`, `g3_accuracy.md`, `pools5.json`, `surrogate_lgb.json`, `surrogate_c.json` (+ `.json` of every table);
code in `scripts/round5/` (`r5_common.py`, `r5_accuracy.py`, `r5_janval.py`, `r5_topbenign.py`, `r5_pad.py`, `r5_attack.py`, `r5_compose.py`, `r5_rotation.py`, `r5_graded.py`, `r5_g3.py`, `prep_pools5.py`, `surrogate_rank.py`, `build_readme.py`, `run_cpu_chains.sh`), `scripts/pooling_v4/make_aug.py --balanced` and `make_aug_full.py`, `scripts/kaggle/train_pooling_v4.py`, `train_fulltrace_v5.py`, `kernel_r5_*`.
