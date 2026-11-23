# Threats to validity (outline, item C2; written 2026-11-23; no compute)

An outline for the thesis chapter. Each threat has: what it is, the evidence in this repository, what is NOT known, and what the thesis should say. File and NOTES references point to the repository; items marked **verify** are statements about the data or the literature that this repository cannot confirm and that must be checked against the source before they are written as fact.

## 1. Label timing
- *Threat.* A malware label assigned long after a sample was first seen may carry information from later analysis (family names agreed over time), and benign labels may be wrong or stale. January training labels and April test labels may not have the same age or the same labelling process.
- *Evidence here.* The labels are the family labels shipped with the published Speakeasy dataset (`labels.npz`; families in `results/groupsplit/split_summary.json`). NOTES 21-22 show the model learns family-level structure (per-family detection, seen/unseen split in `results/groupsplit/stage_fgh/p2`).
- *Not known.* **Verify** in the dataset documentation when and by which process the labels were produced, and whether the April labels were produced later or differently than the January ones. No file in this repository records this.
- *Say.* Report the labels as given, state the unknown, and avoid claims about "future" malware.

## 2. Emulator realism
- *Threat.* Reports come from one emulator (Speakeasy). Real samples may detect or evade emulation, stall, or behave differently on real Windows; emulation depth, timeouts and API coverage shape what a report contains. A detector may learn emulator artefacts (for example the hash-named files and environment strings seen in the A1c pilot, `NOTES.md` 30.2a).
- *Evidence here.* P1 (`NOTES` 24.1): the unknown-token analysis shows the corpus text is dominated by few patterns; P3 (`NOTES` 27.3) shows that long hexadecimal literals carry detection signal that does not survive a coarse normalisation, i.e. low-level string content matters. The reports are capped in length (the corpus has reports with exactly 500 calls at the cap).
- *Not known.* How many samples the emulator fails on or truncates, and whether failure correlates with the label.
- *Say.* Results are about emulated behaviour; do not generalise to deployment on endpoints.

## 3. One run per sample
- *Threat.* Each sample is emulated once. Behaviour that depends on randomness, time, network or environment is observed on one path; two runs of the same sample could give different reports, so the label-report link is noisier than a per-sample claim suggests, and an attacker can change the path.
- *Evidence here.* There is no repeat run in the data. The padding attacks (`NOTES` 23, 26, 27, 29) change the report without changing the sample, which is a statement about the model's input, not about whether a real sample could produce such a report (see section 6).
- *Say.* A report is one observation of a sample; the model is evaluated on observations, not on samples.

## 4. Duplicates, near-duplicates and the cluster bootstrap
- *Threat.* Many reports share an API sequence (`hash_apis`): April has 17,402 reports in 2,509 groups, one coinminer group alone is 265 reports with the same first 512 tokens. A bootstrap over reports treats them as independent and gives intervals that are too narrow; a random validation split leaks twins between training and validation.
- *Evidence here.* The group split (NOTES 21, `results/groupsplit`), the cluster bootstrap over hash_apis (`followups_ci`, `twolevel_eval.cluster_bootstrap`), the coinminer-cluster tables (`NOTES` 22.10, 23.2, 25.1), the seen/unseen columns (P2), and the finding that on April reports unseen in January the neural models fall to about 0.65 pAUC@1e-2 and a bag-of-names model to 0.33 (`results/groupsplit/c1_lgbm`). Cluster intervals are wider than stratified ones throughout (for example the M3 - M1 difference is resolved by neither).
- *Not examined.* Near-duplicates beyond exact `hash_apis` + first-512 + call-name equality (near-duplicate shares are reported in NOTES 21.4: 56.6% of fold-9 validation reports have a training report within 5% edit distance).
- *Say.* State that the effective sample size is the number of groups, and use cluster intervals for every claim; treat the unseen-group numbers as the generalisation estimate.

## 5. April reuse
- *Threat.* One April test set has been scored many times; the sequence of questions was shaped by earlier April results, so April is not an untouched holdout and the intervals do not account for the repeated use (`RESULTS_FOR_REVIEW.md`: 13 scoring rounds up to the early baselines; the openings since are listed per section in NOTES 23-30, up to opening 32 planned for R1).
- *Evidence here.* Every item since NOTES 21 is pre-registered, selects on January validation only, and lists its April openings; the audit (`audit/README.md`) recomputes the headline numbers independently from stored files.
- *Not controlled.* Which questions were asked because of earlier April numbers (for example the window explanation after the first padding attacks, the epoch study after the M3 results).
- *Say.* Count the openings, state that choices were made on January validation, and present April numbers as descriptive of this one test month.

## 6. Report-level versus binary-level attacks
- *Threat.* All attacks here edit the REPORT (add or insert API calls, in memory) and score it. A real attacker must change the BINARY so that the emulator produces the edited report; added calls must be feasible, preserve malicious function and survive emulation (the problem-space constraints of Pierazzi et al., IEEE S&P 2020, and the report-versus-binary distinction studied by Tarallo et al., DIMVA 2024 - **verify title and the exact claims of the Tarallo reference before citing; it is named in the brief only**). Padding with benign calls is cheap at report level and may be hard, impossible or visible at binary level; the white-box greedy attack in `twolevel_attack.py` is an upper bound on feature-space attackers and not a statement about realisable binaries.
- *Evidence here.* The padding sets (random k, LightGBM-ranked, white-box, per-window adaptive set of R1) are defined in NOTES 23, 26, 29, 30.3; the padded-benign false-alarm rates (`NOTES` 26.5) show that a defender who trains on padded malware only would flag padded benign reports.
- *Not examined.* Feasibility of the added call sequences in a real binary; attacks that remove or replace original calls; attacks that exploit the 64-window cap of R1; adaptive attackers against the multi-window baseline beyond the one fixed set.
- *Say.* The attack numbers measure robustness of the model to report edits of a stated kind, not the success of an evasion against a deployed pipeline.

## 7. Narrow benign class
- *Threat.* The benign class is small and narrow (8,003 of 17,402 April reports; the validation folds have 2,200 to 3,200 benign reports); the `windows_syswow64` benign family is 59 April reports and 235 January reports; benign reports may be OS binaries run in the same emulator, not typical user software. A 1% false-positive rate on this class says little about a different benign population; the padding pool is drawn from the same benign reports.
- *Evidence here.* Family counts and benign shares per fold (`results/groupsplit/epoch_study/folds.md`, `NOTES` 21.4), per-family detection tables (`stage_i/tables.md`), the 1% / 0.1% thresholds set on April benign scores (`audit/README.md`: with float32 ties the strict count is 77-79 instead of 80 in 7 of 80 model-seeds).
- *Say.* Report false-positive rates as rates on this benign sample, never as deployment rates, and keep the benign composition visible next to every threshold-based number.

## 8. Further threats to list (shorter)
- *Tokenizer fit on all January text* (unlabelled, includes validation text; EVAL_PROTOCOL 1, `NOTES` 28.2).
- *Two study folds only* (the fold rule of NOTES 21.3 leaves folds 4 and 9; `NOTES` 28.1) and five seeds in the epoch study.
- *Selection by one validation fold* whose largest group is 12% of the slice (fold 9).
- *Metric choice.* The primary metric is normalised pAUC@1e-2, not sklearn's McClish value (`audit/README.md`); results at TPR@1e-3 rest on 8 allowed false alarms and are fragile.
- *Published data is not the paper's data* (EVAL_PROTOCOL 7), so absolute numbers are not comparable with the original paper.
- *A single deterministic LightGBM baseline* (C1') has no seed spread.
