# QUEUED TASK (verbatim from the owner; NOT started): paper figures and tables
Do NOT interrupt the running corrected-tokenizer job (NOTES 25). Start this task only after that job finishes or stops with a STATUS.md. Run it UNATTENDED; the owner is not supervising.

Task: generate all paper figures and tables, CPU only, from stored logits, scores and results. No new April evaluation, no training, no model choice.

Model sets (generate everything for each set that exists):
- SET A "reproduction (paper's tokenizer)": final M1, M3 (Step 5) and M2, M4 (Stage G); attacks from Stage H.
- SET B "corrected tokenizer": the four NOTES 25 models and their attacks, ONLY if that run completed; otherwise skip SET B and say so in the README.
- Plus one comparison table/figure A vs B per model if SET B exists.

Write ONE script, baseline/paper_figs.py, with a --models argument (model set + paths), so every figure can be regenerated later by changing only the input. Outputs under results/paper/<set>/figs/ and results/paper/<set>/tables/.

Style: matplotlib; vector PDF + PNG at 300 dpi; single-column width 3.5 in, double-column 7.16 in; serif font 8-9 pt (IEEE); colour-blind-safe palette with ONE fixed colour per model (M1, M2, M3, M4) in every figure; log-scale FPR axes; error bars/bands = std over 10 seeds unless stated; a caption draft (.txt) next to each figure.

Figures:
F2 samples per family, January vs April (grouped bars).
F3 report length in tokens (CDF), lines at 512 and 4,096, malware vs benign.
F4 training vs validation loss of M1-M4 (2x2 panels, same y-axis).
F5 ROC on log-FPR axis (1e-4 to 1), mean over seeds with band; marker for the Nebula paper's TPR@1e-3 (0.5213).
F6 heatmap: per-family detection at 1% FPR, rows = models, cols = families, values in cells.
F7 heatmap: robustness, rows = models, cols = attacks (unedited; random 20/50/100 prepend; random 200 insert; LightGBM 50 prepend; white-box 20 and 50 steps), values in cells.
F8 detection vs number of added calls (random prepend, random insert, LightGBM, white-box).
F9 seen vs unseen pAUC@1e-2 per model, bars with cluster-bootstrap 95% CI.
F10 logit distributions benign vs malware for M1 and M3, threshold lines.
F11 pAUC@1e-2 per seed per model (box + strip plot).
F12 attention-pooling weights of M3 (seed 0) over the 512 tokens of 2 April malware reports (one detected, one missed), top tokens labelled; CPU forward pass with the stored weights.
F13 padded-benign false alarms, malware-only vs balanced padding (existing review results; label them as the earlier models; SET A only).

Tables (Markdown and LaTeX booktabs):
T1 dataset per family and split; T2 hyper-parameters per model; T3 parameter counts from the weights (sum(p.numel()), level 1 / level 2 / total); T4 clean results with the Nebula paper row; T5 attack results; T6 seen/unseen; T7 pairwise differences (M3-M1, M4-M3, M4-M2, M2-M1) with stratified and cluster 95% CIs and seeds each way, bold = resolved (cluster CI excludes 0); T8 (if SET B) current vs corrected tokenizer per model.

Write results/paper/README.md: every figure/table, its source files, and which set it belongs to. If something cannot be made, skip it, note why in the README, and continue. Commit locally; do not push. Update STATUS.md at the end.
