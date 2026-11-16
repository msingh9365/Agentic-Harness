# Briefing for the planning agent: state of the pooling experiments

Written 2026-11-16 by the agent that executed the runs. Self-contained: assumes no access to the execution session.
Status of every number: **final** unless marked *3 seeds*. Section 0 (added 2026-11-17) holds the latest results and supersedes the "pending" notes below.

## 0. Update 2026-11-17: the pending items are done (read this first; it supersedes section 6 and the "pending" marks)

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

## 5. What I think is established, and what is not

**Established**
1. Order of API calls carries no measurable accuracy in this setting: an order-free model (C) matches the position-dependent one (A) in AUC and TPR@1% for single models. Consistent with the bag-of-API LightGBM at 0.95.
2. The flatten model is brittle to anything that shifts token positions (shuffle destroys it; 5 inserted calls cost about 10 TPR points even when nothing leaves the window). The mean-pooled models are not.
3. Fixed positional encoding is what makes mean pooling competitive: C > B at every equal epoch count; B alone loses about 10 TPR points to A.
4. Retrained A is weaker than released Nebula as a single model by about 0.026 AUC on the train side; adding the validation reports gives about +0.02; a 10-seed ensemble of A is indistinguishable from released.

**Not established**
1. The original hypothesis (mean pooling closes the Q2-Q4 gap): no significant difference to A on Q2-Q4, and it cannot be decided with this test set (see 4b).
2. Why C beats B. C is invariant to shuffling the whole call list, so it is not using global order; within-chunk position must be acting through something else (token adjacency inside a call's fields is the obvious candidate, since shuffling whole calls keeps each call's internal token order). Untested.
3. Whether the robustness matters against a realistic attacker. The insertion test copies calls of the same report; nothing tests prepending, larger insertions, or benign-looking padding.
4. C is not uniformly as good as A: at 0.1% FPR and in ensembles A is better.

**Weaknesses of the evidence**
- April was used to judge the "reach 0.95" goal (not to pick epochs).
- Many subsets were tested; isolated significant cells (for example Q2 for C − A, AUC +0.079 [+0.005, +0.143]) may be chance.
- Under the validation-AUC rule A stops at epoch 1-2 and C at 7; the equal-epoch table (4c) is the cleaner comparison.
- B0/C0 have 3 seeds. LightGBM has 3 seeds, reused as seed mod 3 in rank averages.
- Robustness intervals are over seeds only.

## 6. Pending right now

- *Pending:* **regime J, 10 seeds** (A trained on all of January for 1 epoch, C for 10 epochs; epoch counts = highest mean validation AUC over the 10 regime-S seeds). The Kaggle run finished; output is downloading; evaluation, ensemble and robustness for it are not done. It will tell how close single-model A gets to released with all of January, and whether C − A holds there.
- *Pending (approved by the user, not started):* graded edits: insert 1 / 5 / 20 / 50 calls and prepend 1 / 5 / 20 / 50 calls, malware TPR at a fixed threshold, A vs C. CPU only, about an hour.
- README of round 2 does not yet contain 4c and 4d.

## 7. Practical constraints

- **Kaggle:** 2 × T4, two runs at a time; about 48 s per epoch per run; 36 runs × 10 epochs took 149 minutes of wall time. Weekly GPU quota 30 h, **9.7 h used**, resets 2026-11-21 (quota is charged at about 2× wall time with two GPUs). At most 2 concurrent GPU sessions. **Queue waits are unpredictable** (from seconds to several hours); a stuck kernel cannot be cancelled from the CLI, only deleted.
- **Local:** Mac CPU. Scoring 30 models on April under 2 edits took under an hour; a full evaluation with 1,000 bootstrap resamples about 20-30 minutes. Per-epoch checkpoints of all 36 regime-S runs are on disk (4.7 GB, outside the repo), so any "score existing models on edited inputs" experiment needs no GPU.
- Scores of every run after every epoch (April and validation logits) are saved, so any selection rule or ensemble can be recomputed without rerunning.

## 8. Decisions the planner should make

1. **What is the claim?** The data supports "flatten pooling adds brittleness without adding accuracy; order-free pooling with within-chunk positions keeps accuracy" far better than "mean pooling generalises to unseen sequences". Reframing changes the thesis argument.
2. **Is "A matches released" still a goal?** Options: (i) accept regime J single models (about 0.95) plus the statement that the recipe is undocumented; (ii) use the 10-seed ensemble result (indistinguishable from released); (iii) keep searching (batch 96, static LR, time budget as in the paper). I would not do (iii): the recipe study shows epochs and schedule barely matter.
3. **How to get statistical power on Q2-Q4**, if that question stays: the limit is the April set. Options: evaluate on the January validation side as a second "unseen" set (group-disjoint by construction, 9,619 reports); pool distance quartiles differently; or drop the question.
4. **Which robustness tests to add.** Cheap (no GPU): graded insertion and prepending (pending), deleting calls, duplicating calls, within-chunk versus across-chunk shuffles (would also explain C versus B), edits to malware only at a fixed threshold (evasion view).
5. **Low-FPR behaviour of C.** C loses to A at 0.1% FPR in ensembles. If the thesis cares about low FPR, this needs its own look (TPR@0.1% for the single models is in `tables.md`, for the ensembles in `followups_ensemble.md`).

## 9. Where things are

- Results: `results/pooling_v2/README.md` (verdict, tables), `tables.md`, `recipe_study.md`, `released_training.md`, `followups_same_epoch.md`, `followups_ensemble.md`, `perturb_check.json`, `evaluation.json`.
- Code: `hier_nebula/pooling_variants.py` (flags `fixed_pe`, `masked_mean`), `scripts/kaggle/train_pooling_v2.py`, `launch_pooling_v2.py`, `scripts/pooling_v2/{evaluate_v2,perturb_check,recipe_study,followups}.py`.
- Kaggle outputs (outside the repo): `../pooling_v2_full_output` (regime S, 36 runs), `../pooling_v2_recipe_merged` (recipe study), `../pooling_v2_all_output` (regime J, downloading).
- Round 1 is committed and pushed (`78bf5cf` on `nebula-length-study`); round 2 is uncommitted.
