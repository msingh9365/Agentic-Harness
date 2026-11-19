"""Compose REPORT section 5.12 and the new section of RESULTS_FOR_REVIEW.md from the tables of results/tune (tables are generated; the prose is written here).   (OURS)

    python -m baseline.tune_compose
"""
import json
import os
import re

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, "results", "tune")
L = {"v2_pe": "v2-PE", "pebal": "PE+bal", "attbal": "ATT+bal (existing)", "tuned": "ATT+bal-tuned"}


def md(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"] + ["| " + " | ".join(map(str, r)) + " |" for r in rows])


def tables():
    A = json.load(open(os.path.join(T, "attack_aggregates.json")))
    cols = [("random", "random_20_prepend"), ("random", "random_50_prepend"), ("random", "random_50_insert"), ("surrogate", "lgbm_20_prepend"), ("surrogate", "lgbm_50_prepend"), ("surrogate", "lgbm_50_insert"),
            ("surrogate", "v2pe_20_prepend"), ("surrogate", "v2pe_50_prepend"), ("surrogate", "v2pe_50_insert")]
    out = {}
    for t, tl in (("1e-2", "1% FPR"), ("1e-3", "0.1% FPR")):
        rows = [[L[f]] + [f"{100 * A[s][f'{f}|{n}'][t]['tpr'][0]:.1f} / {100 * A[s][f'{f}|{n}'][t]['fpr'][0]:.1f}" for s, n in cols] for f in L]
        out[t] = f"**Table 2 ({tl} threshold). Malware flagged / padded benign flagged, in % (mean over the 10 seeds). Every April report is edited.**\n\n" + md(rows, ["model"] + [("random " if s == "random" else "LightGBM " if n.startswith("lgbm") else "v2-PE ") + n.split("_", 1)[1].replace("_", " ") for s, n in cols])
    W = A["whitebox"]
    rows = []
    for f in L:
        c1, c3 = np.array(W[f]["1e-2"]), np.array(W[f]["1e-3"])
        rows.append([L[f], len(c1)] + [f"{100 * c1[:, k].mean():.1f} / {100 * c3[:, k].mean():.1f}" for k in (0, 5, 10, 20)])
    out["wb"] = "**Table 2 (white-box greedy attack, 500 April malware, seeds 0-2). Share still flagged at the 1% / 0.1% FPR thresholds after k prepended calls, in %.**\n\n" + md(rows, ["model", "seeds", "k = 0", "k = 5", "k = 10", "k = 20"])
    cnt = []
    for nm, key in (("random padding", "random_cmp"), ("surrogate padding", "surrogate_cmp")):
        for rate in ("malware TPR", "malware TPR, fit subset", "padded-benign FPR"):
            hi = lo = bh = bl = n = 0
            for k, d in A[key].items():
                p, setn, thr, r = k.split("|")
                if p != "tuned-attbal" or r != rate:
                    continue
                n += 1
                if d["resolved"]:
                    pos = d["mean"] > 0
                    hi += pos; lo += (not pos)
                    if d.get("cluster", {}).get("resolved"):
                        bh += pos; bl += (not pos)
            cnt.append([nm, rate, n, f"{hi} ({bh})", f"{lo} ({bl})", n - hi - lo])
    out["cnt"] = "**ATT+bal-tuned against the existing ATT+bal, counts of tests (edit sets × two thresholds) resolved higher / lower for the tuned model (claim rule; in brackets also resolved under the cluster bootstrap). For the padded-benign FPR higher is worse.**\n\n" + md(cnt, ["padding", "rate", "tests", "tuned higher (cluster)", "tuned lower (cluster)", "not resolved"])
    wbc = open(os.path.join(T, "attack_tables.md")).read()
    out["wbcmp"] = wbc[wbc.index("**White-box comparisons"):wbc.index("**Table 3b")].strip()
    return out


def answer():
    return """**Plainly.**
1. **The gap to v2-PE at 1% FPR did not close.** The chosen candidate (lr 1e-3, padding probability 0.25, epoch 2) has April TPR@1e-2 0.795 ± 0.011 against 0.811 ± 0.023 for v2-PE: -1.64 points, CI [-2.91, -0.60], resolved (the tuned model is above v2-PE in 3 of 10 seeds). The existing ATT+bal had -1.65. Tuning changed nothing there (tuned − existing: +0.01 points, not resolved). No candidate of the grid reaches v2-PE's TPR@1e-2: the highest mean in the appendix is 0.799 (not used for selection).
2. **On the primary metric nothing is resolved either.** Tuned − v2-PE in pAUC@1e-2: +0.84 points per-seed means (CI [-0.78, +2.39], above in 7 of 10 seeds: rule not met; cluster bootstrap CI [-4.00, +4.54]); as 10-seed ensembles -3.02 (resolved). Tuned − existing ATT+bal: +0.61 (CI [-0.52, +1.74], 7 of 10 seeds, not resolved). The validation gain that led to the choice (+0.43 points) is of the size of its own standard error (0.15 to 0.23 points); AUC is 0.24 points lower than the existing model (resolved).
3. **What it cost in robustness: a little everywhere, clearly under the strongest attacks.** Against the existing ATT+bal the tuned model is lower after 20 white-box calls (46.5 against 53.3% flagged at 1% FPR: -6.9 points, 0 of 3 seeds above; 11.6 against 14.6% at 0.1% FPR), under LightGBM-chosen k = 50 prepend (31.5 against 36.5%) and under v2-PE-chosen k = 20 prepend (21.4 against 23.8%); under random padding the two are within about 2 points (66.0 against 67.6% at k = 50 prepend). It stays far above PE+bal (white-box after 20 calls 39.6%) and v2-PE (2.2%). Validation had already pointed this way (R 0.949 against 0.959).
4. **Reading.** Training with fewer padded reports (p = 0.25) and the lower learning rate buys back nothing at 1% FPR and gives up some robustness: the 1-point gap to v2-PE at 1% FPR is not a matter of these two settings in this grid. Not tested: other recipe changes (a padding schedule, k distribution, other pooling)."""


LIMITS = """- **Selection on validation, one evaluation.** 16 candidates were compared on the validation slice (mean of 10 seeds; one-SE tie rule). The choice was written into NOTES.md (and committed) before any April logit of this section was opened; the April logits of all cells were produced by the training runs but not evaluated until then. April numbers of every candidate are in the appendix, marked not used for selection.
- **The validation robustness measure is in distribution** (calls from the TRAIN pool, prepended; validation R is 0.94 to 0.96 for every candidate), so it is a weak guard; the April attacks (EVAL-pool calls; surrogate-chosen calls; white-box) are harder and show larger differences than R does.
- **Budget asymmetry (EVAL_PROTOCOL §4.6).** ATT+bal-tuned had 16 candidates (2 tuned hyper-parameters and the epoch); v2-PE and the existing ATT+bal were not re-tuned.
- **Statistics as in §5.11:** stratified bootstrap (test-set sampling only) + the 7-of-10 seed rule, and the cluster bootstrap over the 2,509 duplicate groups as sensitivity. The white-box comparison has 3 seeds and 500 reports.
- **Reproduction.** The rerun of the cell (2e-3, 0.5) reproduced the existing ATT+bal exactly on validation (largest per-seed difference of validation pAUC@1e-2 0.0000), so the 4-epoch grid and the earlier runs are the same recipe.
- **Compute.** Training and scoring ran on the second Kaggle account (the owner's); the scoring pipeline is that of §5.11 (edits built in memory from the store of original reports; only scores saved)."""


def main():
    t = tables()
    sel = open(os.path.join(T, "validation_table.md")).read().strip()
    ap = open(os.path.join(T, "april_chosen.md")).read().strip()
    tableA = ap[:ap.index("## Appendix")].strip()
    appendix = ap[ap.index("## Appendix"):].strip().replace("## Appendix", "**Appendix", 1)
    appendix = appendix.replace(" (NOT USED FOR SELECTION; the choice was made on validation numbers)", " (NOT USED FOR SELECTION; the choice was made on validation numbers).**", 1)
    rep = f"""### 5.12 Tuning the padded-training recipe of ATT+bal under EVAL_PROTOCOL §4 (follow-up for the review)

**Question.** ATT+bal lost 1.65 points of TPR@1e-2 to v2-PE (§5.10). Is that a matter of the padded-training recipe? Grid written in `NOTES.md` section 16 before any training: learning rate in {{1e-3, 2e-3}} x padding probability in {{0.25, 0.5}}, 4 epochs, seeds 0-9 per cell, everything else as ATT+bal of §5.10; validation measures = clean pAUC@1e-2 (selection metric) and robustness R (share of validation malware still flagged at the validation 1% FPR threshold after 20 TRAIN-pool calls are prepended); rule: exclude collapsed cells (validation AUC < 0.6 in any seed), exclude mean R more than 2 points below the existing ATT+bal's (0.9586), then highest mean validation pAUC@1e-2 with ties within one SE broken by fewest epochs, then p = 0.5, then lower validation loss. April logits of all cells were stored and not opened until the choice was written down.

**Validation (the only numbers used for selection).**

{sel}

**April, chosen candidate, evaluated once.**

{tableA}

{answer()}

**Robustness of the chosen candidate** (attacks as in §5.11: random padding of REPORT 5.10 on all April reports, surrogate-chosen padding with the LightGBM and v2-PE-seed-0 rankings of §5.11, white-box greedy with seeds 0-2 and the same 500 reports).

{t['1e-2']}

{t['1e-3']}

{t['wb']}

{t['wbcmp']}

{t['cnt']}

![Detection against the number of calls prepended, with the tuned candidate](results/tune/fig_detection_vs_k.png)

{appendix}

**Limits and how this was done.**

{LIMITS}

"""
    path = os.path.join(ROOT, "REPRODUCTION_REPORT.md")
    txt = open(path).read()
    txt = re.sub(r"### 5\.12 .*?(?=\n## 6\. )", "", txt, flags=re.S) if "### 5.12 " in txt else txt
    txt = txt.replace("\n## 6. Differences from the paper", "\n" + rep + "\n## 6. Differences from the paper", 1)
    open(path, "w").write(txt)
    sec = f"""## ATT+bal tuned under EVAL_PROTOCOL §4 (REPORT 5.12)

Grid (written before training, NOTES 16): lr {{1e-3, 2e-3}} x padding probability {{0.25, 0.5}} x epochs 1-4, 10 seeds each; chosen on validation numbers only: **lr 1e-3, p 0.25, epoch 2** (mean validation pAUC@1e-2 0.9596 against 0.9553 for the existing ATT+bal). Evaluated once on April:

{tableA}

{answer()}

{t['1e-2']}

{t['wb']}

![Detection against the number of calls prepended, with the tuned candidate](results/tune/fig_detection_vs_k.png)

The validation table of all 16 candidates, the April numbers of every candidate (appendix, not used for selection), the 0.1% FPR table, the white-box comparison and the counts are in REPORT 5.12 and `results/tune/`.

"""
    rp = os.path.join(ROOT, "RESULTS_FOR_REVIEW.md")
    r = open(rp).read()
    r = re.sub(r"## ATT\+bal tuned under EVAL_PROTOCOL.*?(?=\n## What is shown)", "", r, flags=re.S) if "## ATT+bal tuned under" in r else r
    r = r.replace("\n## What is shown and what is not", "\n" + sec + "\n## What is shown and what is not", 1)
    open(rp, "w").write(r)
    print("5.12 written:", len(rep), "chars; RESULTS section:", len(sec))


if __name__ == "__main__":
    main()
