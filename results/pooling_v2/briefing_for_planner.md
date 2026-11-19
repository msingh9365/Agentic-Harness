# Briefing for the planning agent: state of the pooling experiments

Written 2026-11-16 by the agent that executed the runs. Self-contained: assumes no access to the execution session.
Status of every number: **final** unless marked *3 seeds*. Section 0 (added 2026-11-17) holds the latest results; sections 5 to 9 were revised to match it.

## 0. Update 2026-11-17: regime J and the graded edits are done (read this first)

**Regime J, 10 seeds (all of January; A 1 epoch, C 10 epochs; no January threshold (b) because validation is in training).**

| model | AUC | TPR@1% (a) | TPR@0.1% (a) | seed range of AUC |
|---|---|---|---|---|
| A | 0.9486 [0.913, 0.971] | 71.9% | 39.6% | 0.932-0.973 |
| C | 0.9644 [0.943, 0.979] | 73.8% | 20.4% | 0.948-0.975 |
| released Nebula | 0.9586 | 75.0% | 51.7% | |

- A − released: AUC −0.010 [−0.026, +0.001], TPR@1% −3.1 points [−11.7, +2.0]. 4 of 10 seeds exceed 0.95; the mean misses the 0.95 goal narrowly.
- C − A: AUC **+0.016 [+0.004, +0.032]** (significant), TPR@1% +1.9 [−8.3, +7.9], TPR@0.1% −19.2 [−30.2, +1.6]. On Q2-Q4: AUC +0.038 [+0.011, +0.075], TPR@1% +4.1 [−7.6, +13.7].
- C − released: AUC +0.006 [−0.004, +0.018]. C after only 1 epoch on all of January already has 0.9593.
- Gap Q1 minus Q2-Q4 in TPR@1% (a): A +32.7 points, C +28.3, released +27.7. **The gap is not closed**; the small gaps seen in regime S came from low Q1 detection there.
- Ensembles (10 seeds): A (J) 0.9590 AUC / 75.5% TPR@1% / 43.3% TPR@0.1%; C (J) 0.9672 / 75.0% / 25.3%. A-ensemble (J) − released: AUC +0.0004 [−0.013, +0.011]. **A matches the released model once trained on all of January and ensembled.**
- Robustness in regime J repeats regime S: shuffle A 0.9486 → 0.703, C 0.9644 → 0.969; 5 inserted calls on reports where nothing is pushed out: A −0.028 AUC, C −0.004 (C − A +0.023 [+0.019, +0.028]).

**Graded edits (regime S, 10 seeds; added calls are copies of calls of the same report). Malware TPR at the fixed threshold that gave 1% FPR before the edit, and benign FPR at that threshold after the edit:**

| edit | A: AUC | A: TPR | A: FPR | B: AUC | B: TPR | C: AUC | C: TPR | C: FPR |
|---|---|---|---|---|---|---|---|---|
| none | 0.9325 | 66.4% | 1.00% | 0.9287 | 56.0% | 0.9416 | 67.0% | 1.00% |
| insert 5 | 0.9223 | 60.2% | 1.11% | 0.9276 | 55.0% | 0.9391 | 64.5% | 0.93% |
| insert 20 | 0.8901 | 50.0% | 1.43% | 0.9295 | 55.2% | 0.9356 | 63.9% | 1.04% |
| insert 50 | 0.8294 | 40.5% | 1.91% | 0.9357 | 57.1% | 0.9407 | 65.6% | 1.07% |
| prepend 1 | 0.9246 | 59.9% | 1.06% | 0.9286 | 54.3% | 0.9410 | 64.3% | 0.93% |
| prepend 5 | 0.8779 | 46.6% | 1.69% | 0.9262 | 54.8% | 0.9287 | 63.3% | 1.27% |
| prepend 20 | 0.6840 | 31.2% | 6.31% | 0.9357 | 55.8% | 0.9410 | 65.7% | 1.08% |
| prepend 50 | 0.5595 | 23.9% | 14.28% | 0.9328 | 53.2% | 0.9436 | 61.4% | 1.02% |

Seed-paired C − A of the TPR change: prepend 5 +16.1 points [+13.0, +18.9]; prepend 20 +33.9 [+30.6, +37.0]; insert 50 +24.5 [+21.6, +27.5]. Restricted to reports where the edit pushes nothing out of the window the effect is smaller but still clear (prepend 20: A −9.5 points, C −2.3; C − A +7.2 [+3.9, +10.5]). **One prepended call already costs A 6.5 TPR points.** Full tables: `graded_edits.md`.

**What changed in my assessment**
1. "Does A match released?" Yes, to within what April can resolve, when trained on all of January (single model −0.010 [−0.026, +0.001]; ensemble identical). The recipe stays undocumented, so it is "indistinguishable", not "reproduced". I would stop work on this question.
2. C is not merely "as good as A": with all of January it is better in AUC (+0.016, significant) and level with the released model, while keeping its robustness. Its weak point is TPR at 0.1% FPR (single models and ensembles, both regimes).
3. The robustness result is now strong and practically meaningful: a position-dependent model (A, and by construction the released Nebula, which has the same architecture) loses half its detections when 20 calls are put in front of a report and starts flagging benign reports. This was not tested on the released weights themselves; that is a cheap next check (CPU only).
4. The original hypothesis (closing the Q2-Q4 gap) is answered negatively for TPR: the gap stays about 28-33 points in regime J. C improves ranking on far sequences (AUC) only.

**Suggested next steps, cheapest first** (all CPU only, existing checkpoints): (a) run the graded edits on the **released Nebula weights**, to show the brittleness on the published model; (b) explain C's weakness at 0.1% FPR (which benign reports score highest); (c) within-chunk versus across-chunk shuffles to explain why C beats B; (d) attacker-chosen padding (benign-looking calls from other reports, malware only). Needs GPU: B in regime J (not run), more LightGBM seeds.

## 0b. Update 2026-11-17 (round 3, not committed, awaiting review): robustness checks and whole-report model

Details, tables and 5-line verdicts: `results/robustness/README.md` (items 1-4, CPU only) and `results/fulltrace/README.md` (item 5, GPU). Short version:

- **The released Nebula is as position-brittle as A.** Prepending 20 same-report calls: released -39.3 points [-51.3, -26.1], A -43.7, C (J) -2.4 (TPR at the fixed 1% threshold). Most of the released model's loss is original calls being pushed out of the 512-token window; on reports where nothing leaves the window it changes little (-6.8 [-20.2, +4.0]), A still loses 12.8.
- **C's robustness does not cover padding with benign calls.** With calls from random benign January reports, every model collapses (prepend 20: released 75.0% -> 12.1%, A 71.9% -> 19.5%, C 73.8% -> 42.6%); where no call leaves the window C is worse than A (insert 5: -14.9 points [-18.1, -11.4]). The earlier robustness result is robustness to edits that keep the report's own call mix. The padding was random, fixed k, nothing optimised or saved (a measurement only).
- **C's low-FPR weakness:** its top benign false positives are short generic start-up sequences (all 1 chunk, 11 distinct sequences among 20, 8 of 20 also occur in malware); the released model's top 20 are more varied and include long reports.
- **Token order inside a call is not what C uses:** shuffling the tokens inside each call changes A, B, C by at most 0.002 AUC; shuffling all tokens even raises B and C. Why C beats B remains unexplained.
- **Whole report (model F, 4,096 tokens, regime J, 5 seeds) does not help accuracy:** AUC 0.9635 against C 512 0.9628, A 0.9557, released 0.9586 (all differences inside the intervals); no gain on 4-8 chunk reports (0.938 against 0.948 for C 512); F is robust to same-report padding (|change| <= 1.4 points) but C 512 already is; TPR@0.1% is low (12.7%). F + LightGBM 0.9765 against released + LightGBM 0.9744 (+0.0021 [-0.004, +0.009]). F was not tested with benign-sourced padding.
- **Cost:** F used 7.36 h of GPU quota (+0.23 h smoke; estimate was 6.3 h; it reaches its final accuracy after one epoch, so 10 epochs were not needed). About 11.5 of 30 h remain (resets Nov 21).
- Consequences for sections 5 and 8: the case for C as "robust" is narrower than section 5 states (same-report edits only); the case for A or the released model at 0.1% FPR stands; reading longer traces is not supported by these data.

## 1. Setup you need to know

- **Task.** Malware detection on Speakeasy emulation reports (dataset `dtrizna/quovadis-speakeasy`, 92,700 reports). Model family: Nebula (`TransformerEncoderChunks`: 512 BPE tokens, split into eight 64-token chunks, attention inside a chunk only, then pooling and a small head). Every model here sees only the **first 512 tokens** of a report.
- **Splits.** January = training set (75,298). It is split by `hash_apis` groups (hash of the report's API-name sequence) into `train` (65,679) and `val` (9,619). April = test (17,402 reports, 9,399 malware). "Seen" April report = its `hash_apis` occurs in January (6,329 seen, 11,073 unseen).
- **Metrics.** AUC; TPR at 1% FPR with threshold **(a)** from the April benign scores, or **(b)** from the January-validation benign scores applied to April (its April FPR is reported). Intervals: bootstrap over April `hash_apis` groups, 1,000 resamples, paired across models. A model's value = mean over its seeds.
- **Distance quartiles (from "test 3").** For unseen April sequences: normalised edit distance to the nearest January sequence. Q1 ≤ 0.031, Q2 ≤ 0.083, Q3 ≤ 0.193, Q4 > 0.193. Report counts: Q1 4,017; Q2 1,896; Q3 2,757; Q4 2,403; Q2-Q4 7,056. The original motivation: released Nebula catches 87.4% of malware in Q1 but 59.7% in Q2-Q4.
- **Reference models (fixed, not retrained).** Released Nebula: April AUC **0.9586**, TPR@1% (a) 75.0%, (b) 76.6%, TPR@0.1% (a) 51.7%. Bag-of-API-names LightGBM: AUC 0.950, TPR@1% (a) 63.0%. Rank average of the two: AUC 0.9744, TPR@1% (a) 79.6%.
- **Variants.**
  - **A**: flatten pooling, positional encoding as released (retrained baseline; identical architecture to the released model, verified bit for bit).
  - **B**: mean pooling, padding tokens excluded, positional encoding as released.
  - **C**: B + fixed positional encoding (position inside the 64-token chunk).
  - **B0, C0**: B and C with the old unmasked mean over all 512 positions.
- **A code fact that matters.** The released `PositionalEncoding` adds the position-0 vector to every token (batch-first branch), so released Nebula and A/B have **no positional signal inside a chunk**. A still knows position through flatten pooling (the head sees each of the 512 slots separately). B knows no order at all. C gets within-chunk positions back.
- **Training settings (all runs).** AdamW lr 2.5e-4, weight decay 0.01, batch 64, LR ×0.5 every 1,000 steps, grad clip 0.5, dropout 0.3, BCE, fp16; 1,027 steps per epoch. Same batch order for all variants within a seed.

## 2. What is documented about the released model (step 1 of round 2)

Not documented: epochs, steps, whether it was trained on all of January, pretraining, LR schedule. Documented in the paper (arXiv 2310.10664, sec. 4.2 and 6): batch 96, AdamW 2.5e-4, weight decay 0.01, a **5-minute time budget per CV fold instead of epochs**, "released models were trained on just 70k samples". The repo's cross-validation script uses 2 epochs, batch 64, a 3000-step scheduler budget. Circumstantial: released Nebula has validation AUC 0.999 on the January `val` side, so it very likely trained on those reports. Full references: `results/pooling_v2/released_training.md`.

## 3. Round 1 (`results/pooling`, committed; 3 seeds, early stopping on validation loss)

A 0.9228, B0 0.9216, C0 0.9224 AUC; no model differed from A on Q2-Q4; all far below released. Flaw found afterwards: validation-loss early stopping picked epoch 1 in 7 of 9 runs. Round 2 replaced it.

## 4. Round 2 results (`results/pooling_v2`)

### 4a. Can A reach April AUC 0.95? (3 seeds; April was used to judge this goal)

| recipe for A | mean April AUC |
|---|---|
| train side, epoch by validation AUC | 0.9302 |
| train side, epoch by validation TPR@1% | 0.9254 |
| train side, fixed 6 epochs | 0.9238 |
| train side, 3000-step budget (proxy; real budget unknown) | 0.922-0.928 |
| **all of January**, epoch 1 / 2 / 10 | **0.9516 / 0.9499 / 0.9468** (seeds at epoch 2: 0.945, 0.945, 0.959) |

Reading: tuning epochs does nothing; the training **data** (adding the 9,619 validation reports, which are whole `hash_apis` groups) is worth about +0.02 AUC. The remaining ~0.008 to the released model is unexplained.

### 4b. A, B, C with 10 seeds, "regime S" (train side; epoch chosen per run on validation AUC)

| model | AUC | TPR@1% (a) | TPR@1% (b) | seed sd of AUC | mean chosen epoch |
|---|---|---|---|---|---|
| A | 0.9325 [0.891, 0.965] | 66.4% | 59.2% | 0.012 (range 0.912-0.951) | 1.6 |
| B | 0.9287 [0.891, 0.960] | 56.0% | 44.5% | 0.010 | 4.4 |
| C | 0.9416 [0.906, 0.969] | 67.0% | 57.4% | 0.009 | 7.3 |
| B0 (3 seeds) | 0.9166 | 53.8% | 57.2% | | |
| C0 (3 seeds) | 0.9137 | 62.1% | 55.7% | | |

Paired differences (group bootstrap):

| difference | all April: AUC | all: TPR@1% (a), points | Q2-Q4: AUC | Q2-Q4: TPR@1% (a) |
|---|---|---|---|---|
| C − A | +0.009 [−0.006, +0.027] | +0.6 [−9.1, +7.0] | +0.024 [−0.012, +0.063] | +6.3 [−7.9, +15.4] |
| B − A | −0.004 [−0.017, +0.011] | −10.4 [−28.1, −0.3] | +0.003 [−0.026, +0.027] | −7.1 [−24.9, +5.2] |
| C − B | +0.013 [+0.005, +0.023] | +11.1 [+3.8, +20.4] | +0.021 [+0.001, +0.054] | +13.4 [+2.9, +23.3] |
| A − released | −0.026 [−0.059, −0.0004] | −8.6 [−19.7, +1.1] | −0.013 [−0.059, +0.027] | −4.2 [−22.3, +6.3] |
| C − released | −0.017 [−0.049, +0.008] | −7.9 [−26.3, +4.2] | +0.011 [−0.016, +0.033] | +2.1 [−15.3, +13.2] |

Gap Q1 minus Q2-Q4 in TPR@1% (a): A +12.8 points, B +1.7, C +0.6, released Nebula +27.7, LightGBM +22.4. The gap shrinks for B and C mainly because their Q1 is lower (A 68.4%, B 50.1%, C 62.5%), not because Q2-Q4 is higher (55.5%, 48.4%, 61.8%). No interval was computed for the gap itself.

Going from 3 to 10 seeds barely narrowed the group-bootstrap intervals (C − A on Q2-Q4 TPR: [−12.6, +20.3] to [−7.9, +15.4]). **The uncertainty is dominated by the April reports (few, strongly correlated groups), not by seeds.** More seeds will not resolve Q2-Q4.

### 4c. Same number of epochs for everyone (10 seeds, no selection)

Mean April AUC after e epochs: A 0.929 (e=1), then flat at 0.924; B 0.933 (e=1), then 0.923; C 0.940 (e=1), rising to 0.941. C − A is +0.011 at 1 epoch and +0.017 at 10 epochs (seed-paired intervals exclude zero at every epoch; group-bootstrap interval at 10 epochs [−0.001, +0.042]). C − B is +0.007 at 1 epoch and +0.018 from epoch 4 on (group bootstrap at 5 and 10 epochs excludes zero). So **C's advantage over B is not an artefact of training longer**; it is there at every equal epoch count. TPR@1% (a) at 10 epochs: A 68.2%, B 59.7%, C 67.0%.

### 4d. Seed ensembles (average the 10 seeds' logits; regime S)

| model | single-seed mean AUC | ensemble AUC | ensemble TPR@1% (a) | ensemble TPR@0.1% (a) |
|---|---|---|---|---|
| A | 0.9325 | 0.9424 | 73.7% | 51.2% |
| B | 0.9287 | 0.9386 | 63.4% | 13.0% |
| C | 0.9416 | 0.9454 | 67.3% | 30.4% |
| released Nebula | | 0.9586 | 75.0% | 51.7% |

- A-ensemble − released: AUC −0.016 [−0.049, +0.011], TPR@1% −1.2 points [−11.7, +8.3], TPR@0.1% −0.5 [−19.6, +57.2]. **An ensemble of 10 retrained A models is statistically indistinguishable from the released model**, even without the validation reports.
- Ensembling helps A much more than C (A has more seed variance). In ensembles C is **worse than A at low FPR**: TPR@0.1% −20.8 points [−39.6, −1.3]; TPR@1% −6.5 [−18.0, +6.4]; AUC +0.003 [−0.013, +0.023].

### 4e. Robustness (regime S, 10 seeds, checkpoints chosen on validation AUC; edits applied to all April reports)

| edit | A: AUC before → after | C: AUC before → after | A: TPR@1% (a) | C: TPR@1% (a) |
|---|---|---|---|---|
| API call order shuffled | 0.9325 → 0.693 | 0.9416 → 0.9412 | 66.4% → 7.0% | 67.0% → 58.6% |
| 5 calls inserted (copies of calls of the same report, random places) | 0.9325 → 0.9223 | 0.9416 → 0.9391 | 66.4% → 59.3% | 67.0% → 66.0% |
| same, only the 6,278 reports where the edit pushes no call out of the 512-token window | 0.9381 → 0.9199 | 0.9408 → 0.9400 | 60.7% → 51.2% | 58.6% → 59.4% |

Seed-paired C − A of the change: shuffle AUC +0.239 [+0.222, +0.256]; insertion AUC +0.0077 [+0.0037, +0.0108]; insertion on the unaffected reports AUC +0.017 [+0.010, +0.026], TPR +10.3 points [+6.6, +13.9] (intervals over seeds only). B behaves like C here (shuffle 0.9287 → 0.9298). Share of April reports whose decision at the January 1% threshold flips after the insertion: A 6.4%, B 3.5%, C 4.0%.

## 5. What I think is established, and what is not (updated with section 0)

**Established**
1. Order of API calls carries no measurable accuracy at 1% FPR in this setting: the order-free model C matches or beats the position-dependent A in AUC (regime S +0.009 [−0.006, +0.027]; regime J +0.016 [+0.004, +0.032]) and equals it in TPR@1%. Consistent with the bag-of-API LightGBM at 0.95.
2. The flatten model is brittle to anything that shifts token positions: shuffling destroys it, one prepended call costs 6.5 TPR points, twenty cost 35 points and push its benign FPR from 1% to 6.3%. The mean-pooled models (B, C) barely move. Holds in both regimes and when no original call leaves the window.
3. The fixed positional encoding is what makes mean pooling competitive: C > B at every equal epoch count; B alone loses about 10 TPR points to A.
4. Retrained A matches the released model once trained on all of January: single model −0.010 AUC [−0.026, +0.001], 10-seed ensemble +0.0004 [−0.013, +0.011]. On the train side alone it is 0.026 lower. Epochs, step budget and selection rule do not matter; the training data does.
5. The Q1 versus Q2-Q4 gap in TPR@1% is not closed by mean pooling (regime J: A +32.7 points, C +28.3, released +27.7). C ranks far sequences better (Q2-Q4 AUC +0.038 [+0.011, +0.075]) but catches no more malware there at 1% FPR.

**Not established**
1. Why C beats B. C is invariant to shuffling the whole call list, so it does not use global order; the within-chunk positions must act through something else (token adjacency inside a call's fields is the obvious candidate, since shuffling whole calls keeps each call's internal token order). Untested.
2. Whether the brittleness holds for the **released weights themselves**. A has the same architecture, so it is very likely, but the edits were only run on retrained models.
3. Whether the robustness matters against a realistic attacker: all added calls are copies from the same report; nothing tests attacker-chosen (benign-looking) calls, deletion, or edits to malware only.
4. Why C is weaker at 0.1% FPR (regime J: −19.2 points [−30.2, +1.6]; regime-S ensembles −20.8 [−39.6, −1.3]).
5. B in regime J (not run).

**Weaknesses of the evidence**
- April was used to judge the "reach 0.95" goal and to decide to add regime J (never to pick epochs).
- Regime J compares A after 1 epoch with C after 10 (the rule's outcome); at 1 epoch each, C is still ahead (0.9593 against 0.9486).
- Many subsets were tested; isolated significant cells may be chance. Group-bootstrap intervals are wide because April has few independent groups; 10 seeds instead of 3 barely narrowed them.
- B0/C0 have 3 seeds. LightGBM has 3 seeds, reused as seed mod 3 in rank averages.
- Robustness and same-epoch intervals marked "over seeds" do not include sampling of April reports.

## 6. Pending

Nothing is running. Round 3 (section 0b) is done and written up but not committed, awaiting review. Everything planned for round 2 is done, evaluated, written up and pushed (commit `b169be3` on `nebula-length-study`, plus the commit that carries this revision of the briefing).

## 7. Practical constraints

- **Kaggle:** 2 × T4, two runs at a time; about 48 s per epoch per run; 36 runs × 10 epochs took 149 minutes of wall time. Weekly GPU quota 30 h, **10.9 h used**, resets 2026-11-21 (quota is charged at about 2× wall time with two GPUs). At most 2 concurrent GPU sessions. **Queue waits are unpredictable** (from seconds to several hours); a stuck kernel cannot be cancelled from the CLI, only deleted.
- **Local:** Mac CPU. Scoring one model on all April reports takes about 15 s; 30 models under 8 edits took about an hour; a full evaluation with 1,000 bootstrap resamples 20-30 minutes. Per-epoch checkpoints of all regime-S runs (4.7 GB) and the final weights of the regime-J runs are on disk outside the repo, so any "score existing models on edited inputs" experiment needs no GPU.
- Scores of every run after every epoch (April and validation logits) are saved, so any selection rule or ensemble can be recomputed without rerunning.

## 8. Decisions the planner should make

1. **What is the claim?** The data supports "flatten pooling adds brittleness without adding accuracy; mean pooling with within-chunk positions keeps (or slightly improves) AUC and removes the brittleness" far better than "mean pooling generalises to unseen sequences" (answered negatively for TPR). Reframing changes the thesis argument.
2. **Close the "A matches released" question?** I recommend yes: regime J single models are within noise and the ensemble is identical. Further recipe search (batch 96, static LR, time budget as in the paper) is unlikely to pay: epochs and schedule barely mattered.
3. **Which follow-ups to run** (all CPU only, existing checkpoints, cheapest first): (a) the graded edits on the released Nebula weights; (b) which benign reports limit C at 0.1% FPR; (c) within-chunk versus across-chunk shuffles, to explain C versus B; (d) attacker-chosen padding and edits to malware only. GPU needed only for B in regime J or more LightGBM seeds.
4. **Statistical power on Q2-Q4**, if that question stays open: the limit is the April set. Options: use the January validation side of regime S as a second group-disjoint "unseen" set (9,619 reports), or drop the question.
5. **Low-FPR requirement.** If the thesis needs 0.1% FPR, A (or an ensemble of A) is currently the better model and C's robustness comes at a cost there.

## 9. Where things are

- Results: `results/pooling_v2/README.md` (verdict and all sections), `tables.md` (regime S), `tables_J.md` (regime J), `recipe_study.md`, `released_training.md`, `followups_same_epoch.md`, `followups_ensemble.md`, `graded_edits.md`, and the `.json` files with the numbers.
- Code: `hier_nebula/pooling_variants.py` (flags `fixed_pe`, `masked_mean`), `scripts/kaggle/train_pooling_v2.py`, `launch_pooling_v2.py`, `scripts/pooling_v2/{evaluate_v2,perturb_check,graded_edits,recipe_study,followups}.py`.
- Kaggle outputs (outside the repo): `../pooling_v2_full_output` (regime S, 36 runs), `../pooling_v2_all_output` (regime J, 20 runs), `../pooling_v2_recipe_merged` (recipe study).
- Rounds 1 and 2 are committed and pushed on `nebula-length-study`.

## 10. Round 5: final-quality runs of ATT+bal and the examiner's tests (`results/round5`, not committed)

ATT+bal (attention pooling, fixed position encoding, 512 tokens, trained with balanced padding: benign and malware reports padded alike) with 10 seeds, 4 epochs saved (epoch 2 primary), regime S runs for a second low-FPR test set, and a whole-report version (G3). Five-line summary (numbers and intervals in `results/round5/README.md`):
1. ATT+bal beats the released Nebula on AUC (0.9752 against 0.9586, +0.0166 [+0.0043, +0.0342]) but not significantly at a fixed FPR (TPR 76.5% against 75.0% at 1%, 57.0% against 51.7% at 0.1%); it clearly beats the retrained A and C (e.g. +17.4 points at 0.1% FPR over A, seed-paired).
2. On the January validation side (regime S, 2,103 benign reports) ATT+bal reaches 46.0% [22.1, 80.0] at 0.1% FPR against 36.0% for A and 20.0% for ATT without padding: same ordering as April, intervals of 20-60 points.
3. Unseen padding (block of calls, other benign source, rare API names, surrogate-chosen calls, white-box greedy calls): costs ATT+bal 4-18 points at 20 calls, but rare names and window-filling padding at 50 calls break it (10.7% / 7.0% TPR at 1%); the released model and C fall much further, and the white-box attack leaves ATT+bal 54.0% (78.2% before), the released model 1.6%.
4. Rotating the 512 window leaves ATT+bal, C and F unchanged (|change| at most 1.2 points) while the released model and A lose 38-51 points: they use token positions, ATT+bal does not. Rotating the whole call list costs ATT+bal 7-11 points, C 18-26, F and G3 about 0-4.
5. The whole-report ATT+bal (G3, 5 seeds) is unaffected by both rotations but not more accurate (AUC 0.9578, TPR 76.1% / 55.0% at 1% / 0.1% FPR): reading more of the report does not pay. Recommendation: ATT+bal at 512 tokens. Kaggle quota used this round 2.52 h (26.84 of 30 h used, resets 2026-11-21 00:00 UTC).

