# RoPE test: does relative position make M3 use call order? STATUS: NOT RUN (blocked at the GPU queue)

**There is no result yet.** The question of `NOTES_ROPE.md` (does replacing the absolute sinusoidal code of M3 by RoPE make the model use call order more, at what cost in shift robustness, padding robustness and clean accuracy, and what does full attention alone do?) is **unanswered**: no variant has been trained, no validation number, no April logit, no figure.

## Why
The validation-guard kernel `manishsinghxdev/rope-guard` (GPU, T4, pushed 2026-11-24 11:27 UTC) stayed QUEUED for more than 10 hours and never started. A one-line CPU probe kernel on the same account ran at once; a one-line GPU probe kernel (`rope-gpu-probe`, pushed 20:08 UTC) was also still queued 1.5 hours later. The account has no other running kernel. The queue rule's copy on the second account cannot be made (this session has no token for it). Details and times: `STATE.md`.

## What is done (all committed on branch `rope-test`)
- `NOTES_ROPE.md` (repository root): the pre-registration (design, variants, recipe, guard, checks, metrics, decision rule), committed before any code ran.
- `rope_model.py`: V1 (RoPE in 64-token blocks), V2 (RoPE, full 512 attention), V3 (sinusoidal code, full attention); `test_rope.py`: unit tests (a) to (e) all passed (`tests_result.json`: relative property max difference 3.8e-6; the new layer code with RoPE off reproduces the unmodified M3 to 7.6e-6; the parameter counts of V1 to V3 equal M3's, 3,304,321 (`param_counts.json`); same initial weights as M3 for the same seed; short CPU training falls).
- `launcher.py`, `run_jobs.py`, `build_kernel.py`: the unchanged training and attack commands run with the variant model; local CPU smoke runs of the guard path and the final path worked.
- `guard_eval.py`, `order/order_tests.py` (shuffle and shift test of `cpu-order-tests` with the variant loader), `rope_analysis.py` (clean metrics, shuffle, shift, attacks, cluster-bootstrap contrasts, decision rule, tables, figures), `v0/` (stored order-test scores of M3 from `cpu-order-tests`).

## What is left when a GPU slot is available
guard (3 variants x 3 seeds, fold 9) -> `guard_eval.py` -> final runs V1, V2, V3 (10 seeds) -> weights dataset -> attack kernel (V0 to V3 scores; white-box V1, V2) -> shuffle and shift tests on CPU -> `rope_analysis.py` -> this README.
Alternatives that would change the plan and need the owner's decision: a different GPU type, or training on CPU kernels (about 30 seed-runs of about 75 minutes on 4 cores, 40 or more CPU hours).
