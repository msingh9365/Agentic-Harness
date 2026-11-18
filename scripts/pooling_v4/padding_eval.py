#!/usr/bin/env python
"""
Round 4, steps 0, 1 and 3 (padding): benign-call padding with the EVAL pool (see v4_common.py).

    python scripts/pooling_v4/padding_eval.py --set old     # released, A (J), C (J), F; seeds 0-4   -> step0_padding.md/json
    python scripts/pooling_v4/padding_eval.py --set all     # old + the round-4 models (output folder --src-v4)

Threshold of each model and seed: 1% FPR on the UNEDITED April benign scores (fixed). Malware TPR: the 9,399 April malware
reports padded; benign FPR: 2,000 random benign April reports padded the same way (the unedited benign FPR is 1% by
construction on all benign reports, on the subset it is whatever it is: both are shown). "Fits": whole edited sequence at most
512 tokens (no original call leaves a 512-token window); F also has "fits in 4096". Mean over seeds 0-4 (released: one model).
Intervals: group bootstrap over April hash_apis (1,000 resamples), paired across models; seed-paired differences: bootstrap over seeds.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v4_common as V  # noqa: E402
from v4_common import C  # noqa: E402

SEEDS = list(range(5))
V4_FAMS = ["M", "MM", "ATT", "Caug", "ATTaug", "Cbal", "MMbal", "ATTbal"]


def model_set(which, src_v4):
    m = {"released Nebula": ("released", [0], None),
         "A (J)": ("A", SEEDS, None), "C (J)": ("C", SEEDS, None), "F (whole report)": ("F", SEEDS, None)}
    if which == "all":
        src = dict(V.SRC)
        m["C (J, 2 epochs)"] = ("C2", SEEDS, None)
        for fam in V4_FAMS:
            src[fam] = (src_v4, fam + "_all_s{s}", 2, 512)
            m[{"M": "M (max)", "MM": "MM (mean+max)", "ATT": "ATT (attention)", "Caug": "C+aug", "ATTaug": "ATT+aug", "Cbal": "C+bal", "MMbal": "MM+bal", "ATTbal": "ATT+bal"}[fam]] = (fam, SEEDS, src)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["old", "all"], default="old")
    ap.add_argument("--src-v4", default="/Users/manish/Code/mtp/pooling_v4_output")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(int(os.environ.get("NTHREADS", os.cpu_count() or 4)))
    models = model_set(a.set, a.src_v4)
    test, y = V.april()
    N = len(test)
    P = V.padded_sets(workers=4, limit=a.limit)
    pos, nm = P["pos"], P["n_mal"]
    mal_pos, ben_pos = pos[:nm], pos[nm:]
    lens = P["lens"]                                              # [8, n_reports] edited token counts
    fit512 = (lens[:, :nm] <= 512)
    fit4k = (lens[:, :nm] <= 4096)
    fl_m, fl_b, seed_tpr = {}, {}, {}
    for name, (fam, seeds, src) in models.items():
        fm, fb, st = [], [], []
        for s in seeds:
            z0, ze = V.padded_logits(P, fam, s, src)
            thr = C.thr_from(y, z0, 0.01)
            f0 = (z0 > thr).astype(float)
            fm.append(np.stack([f0[mal_pos]] + [(ze[j][:nm] > thr).astype(float) for j in range(8)]))      # [9, n_mal]
            fb.append(np.stack([f0[ben_pos]] + [(ze[j][nm:] > thr).astype(float) for j in range(8)]))      # [9, n_ben]
        fl_m[name], fl_b[name] = np.mean(fm, 0), np.mean(fb, 0)
        seed_tpr[name] = fm
        print("flags", name, flush=True)
    labels = ["unedited"] + V.EDITS
    W = np.stack(list(C.group_weights_boot(test.hash_apis.values, 1000, 0)))              # [1000, N]
    full = lambda p, v: (lambda z: (z.__setitem__(p, v), z)[1])(np.zeros(N))                # place v at April positions p
    Wm, Wb = W[:, mal_pos], W[:, ben_pos]
    ci = lambda v: f"[{100 * np.percentile(v, 2.5):+.1f}, {100 * np.percentile(v, 97.5):+.1f}]"

    def wmean(Wx, fl, mask):                                                                 # weighted mean of fl over mask, per resample
        m = mask.astype(float)
        return (Wx @ (fl * m)) / (Wx @ m)

    def stat(Wx, fl, e, mask):                                                               # point change, bootstrap change
        pt = fl[e][mask].mean() - fl[0][mask].mean()
        return pt, wmean(Wx, fl[e], mask) - wmean(Wx, fl[0], mask)

    allm = np.ones(nm, bool)
    tabs = {}
    cols = lambda: ["unedited"] + V.EDITS

    def block(title, subset_fn, fl, Wx, names, mask_all, pair=False):
        """two tables: value after the edit (mean over seeds) and change vs unedited with group-bootstrap interval; rows = models."""
        t_after, t_chg = [], []
        for n in names:
            ra, rc = {"model": n}, {"model": n}
            for e in range(9):
                if pair and e == 0:
                    continue
                mk = subset_fn(e, n)
                ra[labels[e]] = (f"{100 * fl[n][0][mk].mean():.1f}% → {100 * fl[n][e][mk].mean():.1f}%" if pair else f"{100 * fl[n][e][mk].mean():.1f}%")
                if e:
                    pt, bs = stat(Wx, fl[n], e, mk)
                    rc[labels[e]] = f"{100 * pt:+.1f} {ci(bs)}"
            t_after.append(ra); t_chg.append(rc)
        tabs[f"{title}: malware TPR " + ("before → after the edit" if pair else "after the edit")] = pd.DataFrame(t_after)
        tabs[f"{title}: change, points [group 95%]"] = pd.DataFrame(t_chg)

    names_all = list(models)
    block("Malware reports padded, all 9,399", lambda e, n: allm, fl_m, Wm, names_all, True)
    # for the fits subsets the set depends on the edit (the same for every model), unedited column = the same reports before the edit
    block("Malware reports that fit in 512 tokens after the edit", lambda e, n: fit512[e - 1], fl_m, Wm, names_all, True, pair=True)
    fnames = [n for n in names_all if n.startswith("F")]
    block("Malware reports that fit in 4,096 tokens (F: no original call leaves its window)", lambda e, n: fit4k[e - 1], fl_m, Wm, fnames, True, pair=True)
    allb = np.ones(len(ben_pos), bool)
    t_f = []
    for n in names_all:
        r = {"model": n}
        for e in range(9):
            r[labels[e]] = f"{100 * fl_b[n][e].mean():.2f}%"
        t_f.append(r)
    tabs["FPR of the 2,000 benign April reports padded the same way (threshold fixed at 1% FPR on all unedited benign reports)"] = pd.DataFrame(t_f)
    # differences between models in the change of TPR
    if a.set == "old":
        pairs = [("A (J)", "released Nebula"), ("C (J)", "released Nebula"), ("C (J)", "A (J)"), ("F (whole report)", "C (J)"),
                 ("F (whole report)", "A (J)"), ("F (whole report)", "released Nebula")]
    else:
        new = [n for n in names_all if n.split(" ")[0] in ("M", "MM", "ATT", "C+aug", "ATT+aug")]
        pairs = [(n, "C (J, 2 epochs)") for n in new] + [(n, "C (J)") for n in new] + [(n, "released Nebula") for n in new] + \
                [("C (J, 2 epochs)", "C (J)"), ("C (J)", "released Nebula"), ("A (J)", "released Nebula")]
    for tag, getmask in (("all malware", lambda e: allm), ("malware that fits in 512 tokens", lambda e: fit512[e - 1])):
        rows = []
        for x, z in pairs:
            r = {"difference": f"{x} − {z}"}
            for e in range(1, 9):
                mask = getmask(e)
                px, bx = stat(Wm, fl_m[x], e, mask); pz, bz = stat(Wm, fl_m[z], e, mask)
                r[labels[e]] = f"{100 * (px - pz):+.1f} {ci(bx - bz)}"
            rows.append(r)
        tabs[f"Difference between models in the change of malware TPR, points [group 95%], {tag}"] = pd.DataFrame(rows)
    # seed-paired differences (bootstrap over seeds)
    rng = np.random.default_rng(0)
    for tag in ("all malware", "malware that fits in 512 tokens"):
        rows = []
        for x, z in pairs:
            if len(seed_tpr[x]) < 2 or len(seed_tpr[z]) < 2:
                continue
            r = {"difference": f"{x} − {z}"}
            for e in range(1, 9):
                mask = allm if tag == "all malware" else fit512[e - 1]
                dx = np.array([f[e][mask].mean() - f[0][mask].mean() for f in seed_tpr[x]])
                dz = np.array([f[e][mask].mean() - f[0][mask].mean() for f in seed_tpr[z]])
                d = 100 * (dx - dz); b = rng.choice(d, (20000, len(d))).mean(1)
                r[labels[e]] = f"{d.mean():+.1f} [{np.percentile(b, 2.5):+.1f}, {np.percentile(b, 97.5):+.1f}]"
            rows.append(r)
        tabs[f"Seed-paired difference in the change of TPR, points [95% over the 5 seeds], {tag}"] = pd.DataFrame(rows)
    out = a.out or ("step0_padding" if a.set == "old" else "step3_padding")
    js = {"labels": labels, "n_malware": nm, "n_benign_subset": int(len(ben_pos)),
          "tpr_all": {n: [float(fl_m[n][e].mean()) for e in range(9)] for n in models},
          "tpr_fit512": {n: [float(fl_m[n][e][fit512[e - 1]].mean()) if e else None for e in range(9)] for n in models},
          "fpr_benign_padded": {n: [float(fl_b[n][e].mean()) for e in range(9)] for n in models},
          "share_fit512": fit512.mean(1).tolist(), "share_fit4096": fit4k.mean(1).tolist()}
    md = [f"# Padding with benign calls from the EVAL pool ({a.set} models)\n",
          "Random calls of the 2,000 EVAL-pool reports (`pools.json`), k = 1, 5, 20, 50, inserted at random places or prepended; threshold fixed at 1% FPR on "
          "the unedited April benign scores of each model and seed; mean over seeds 0–4 (released: one model). Malware TPR on the 9,399 April malware reports; "
          "FPR on 2,000 random benign April reports padded the same way. Nothing optimised, random padding, aggregate numbers only.\n"]
    for t, df in tabs.items():
        md += [f"\n## {t}\n", C.md_table(df)]
    if not a.limit:
        json.dump(js, open(f"{V.OUT}/{out}.json", "w"), indent=1)
        open(f"{V.OUT}/{out}.md", "w").write("\n".join(md))
    print("\n".join(md[:6]))


if __name__ == "__main__":
    main()
