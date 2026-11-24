# STATE of the RoPE test (NOTES_ROPE.md). Owner account of every kernel is recorded here; times in UTC.

- 2026-11-24 11:27 UTC: NOTES_ROPE.md committed and pushed first (before any code ran). Unit tests (a)-(e) passed (`tests_result.json`); local CPU smoke runs of the guard and final paths with the variants worked (limit 400 reports, 1 epoch).
- Before launch: all 15 most recent kernels of the account `manishsinghxdev` COMPLETE (no running or queued session). This session only has the token of `manishsinghxdev`; the queue rule's second account is not reachable from here.
- 2026-11-24 11:27 UTC: guard kernel `manishsinghxdev/rope-guard` pushed (GPU T4; datasets es-folds, gs-fix-inputs; command `rope_test.run_jobs --mode guard --variants rope_blocks rope_full sin_full --seeds 0 1 2`, fold 9, 3 epochs, no April file).
