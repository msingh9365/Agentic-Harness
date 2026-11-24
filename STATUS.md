<!-- NIGHT3-BEGIN -->
# STATUS of the night run of 2026-11-23/24 (NOTES 30: C1', A1c, R1, B1, C2)

**Summary in plain English.** Four of the five items that were allowed to run are finished and pushed; B1 also finished (it was the item most at risk of not fitting in the night). (1) **C1'**, a plain LightGBM that only counts which API names appear (it ignores order and arguments), is much worse than the neural models on the clean April data (pAUC@1e-2 0.483 against M1 0.686 and M3 0.705), and is useless on sequences it has never seen. Under padding it behaves like M1 (it collapses). It is a floor, not a competitor. (2) **A1c**, a rule that makes API paths and arguments path-invariant, was only tested on January with a bag-of-words classifier: it changes 59% of reports, but only 35 of 44,446 components end up kept, and the validation score moves by +0.45 points (confidence interval -0.87 to +2.31, so no effect). By the rule I set beforehand this means "training a Transformer with it is allowed later"; I trained nothing tonight. (3) **R1**, M3 trained on every 512-token window and scored by the highest window, removes the 100-call padding cliff: after 100 random calls are put in front, M3 detects 6.5% of malware, R1 69.3% (difference +62.9 points, interval +48.8 to +74.1). It costs about 4.5 points of clean pAUC@1e-2 against M3 (66.0 against 70.5; not resolved, but 0 of 10 seeds go the other way, so I would not call it zero). Against the test-time multi-window baseline from NOTES 27.2, R1 is about 6.5 points better on clean data and equally robust (clean not resolved). In the white-box greedy attack (3 seeds), 49.5% of malware is still flagged after 50 steps, where M3 keeps 2.5% and M4 10.6%. The one adaptive attack I tried (50 random calls at the start of EVERY window) leaves R1 at 64.0%. (4) **B1**, does unlabelled April text help a self-supervised detector: no effect that I can resolve. Pre-training on January gives +0.9 points of pAUC@1e-2 on the held-out April half (interval -5.2 to +7.1) and adding the unlabelled April text gives another -1.1 (interval -4.6 to +2.6, 5 seeds up and 5 down); the seed-to-seed spread (about 4 points) is as large as any difference. This is at 8k tokens, 3 + 2 epochs and one split, so it does not say adaptation never helps. (5) **C2**, the threats-to-validity outline, is written (`THREATS_TO_VALIDITY.md`). B2 was not run, as asked; what B2 should be is an open question in NOTES 30.5. Nothing existing was changed.

## What ran tonight

| item | what | kernel(s) and owner account | result |
|---|---|---|---|
| C1' (NOTES 30.1, 30.10) | LightGBM bag of API names, one deterministic model | local CPU | done, `results/groupsplit/c1_lgbm/` |
| A1c (30.2, 30.11) | path-invariant rule, January only, no April | `nebula-a1c`, `nebula-a1c-pilot`, `nebula-a1c-smoke` **manishsinghxdev** (CPU) | done, GO for a later GPU test |
| R1 (30.3, 30.12, 30.13) | windowed M3; selection on January fold 9; final 10 seeds; attacks | selection `nebula-r1-sel-a` **manishsinghxdev**, `nebula-r1-sel-b` **msingh9365**; final `nebula-r1-fin-a` **manishsinghxdev**, `nebula-r1-fin-b` **msingh9365**; scoring `nebula-r1-score-a` **manishsinghxdev**, `nebula-r1-score-b` **msingh9365**; comparator `nebula-r1-m3score` **msingh9365** (used; the first on manishsinghxdev never started, deleted); white-box `nebula-r1-wb` **msingh9365** (used) and **manishsinghxdev** (copy, deleted) | done, `results/groupsplit/r1/` |
| B1 (30.4, 30.4a, 30.4b) | three conditions x 10 seeds on the 8k corrected tokenizer | tokenizer `nebula-b1-tok` **msingh9365** (CPU), smoke `nebula-b1-tok-smoke` (deleted); training `nebula-b1-a` and `nebula-b1-b` **manishsinghxdev**, `nebula-b1-c` and `nebula-b1-d` **msingh9365** | done, `results/groupsplit/b1/`, no effect resolved |
| C2 (30.6) | threats to validity | none | done |

GPU time (kernel runtimes from the logs, not re-priced as quota): R1 selection about 2 x 23 min on two T4 sessions, final 17 + 19 min, scoring 12 + 13 min, comparator 22 min, white-box 55 min (the deleted duplicate another 55 min); B1 training 96 + 63.5 + 87.5 + 59.4 min = 5.1 GPU-h (estimate 7). CPU: tokenizer 65 min, A1c decision 40 min.

## Deviations (every one)

1. **B1 uses an 8k vocabulary, not the 50k tokenizer** (NOTES 30.4a, written before any B1 code ran): autoregressive pre-training predicts over the whole vocabulary at each position and needs about 10 GB per batch at 50k. The corrected 8k tokenizer was built for it. B1 numbers are therefore comparable inside B1 only, not with M1 to M4. The fixed budget (3 pre-training epochs, 2 fine-tuning epochs, lr 1e-3) replaces the B3 budget because B3's would have cost about 17 GPU-h.
2. **B1 launch bug:** the first B1 kernel (`nebula-b1-a`) stopped at start because the split file was not shipped in the kernel code; no data touched, no GPU time. Fixed in `build_kernel.py`, queued copy `nebula-b1-c` deleted and both launched again. Recorded in STATE.
3. **Queue-rule copies** (owner's rule, queued > 60 min): `nebula-r1-m3score` (the copy won, the original was deleted); `nebula-r1-wb` (both copies finished in 55 min with equal arrays, the original was kept and the copy deleted). Every pair is in `STATE.md` with times.
4. **R1 selection was split over two accounts** (variant a on manishsinghxdev, variant b on msingh9365) to avoid queueing, as announced in NOTES 30.9.
5. **R1 white-box on 3 seeds** (0 to 2), as pre-registered; `followups_ci.py` was changed to accept fewer white-box seeds than score seeds (white-box means over the seeds present).
6. **A1c exact rule was fixed after a January-only pilot** (NOTES 30.2a), committed before the decision run.
7. B1 evaluates only the TEST half of April (April opening 33); the ADAPT half is used as unlabelled token rows in condition (iii) and is never scored. The collapse check (TEST AUC < 0.6) runs at evaluation time, not inside the kernel.
8. Datasets and kernels are private; no token was printed or committed.

April openings of this phase: 31 (C1'), 32 (R1: clean logits once, then attack scores), 33 (B1, TEST half only); 34 (B2) not opened.
<!-- NIGHT3-END -->

