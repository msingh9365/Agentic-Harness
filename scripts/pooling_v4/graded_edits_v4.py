#!/usr/bin/env python
"""
Round 4, step 3 (graded edits with copied calls): the edits of results/robustness item 1 (insert k / prepend k calls copied from the
SAME report, k = 1, 5, 20, 50; first 512 tokens) for the round-4 models, next to released, A (J), C (J) (seeds 0-4).

    python scripts/pooling_v4/graded_edits_v4.py --src-v4 <Kaggle output of the round-4 runs>

Threshold of each model and seed: 1% FPR on the unedited April benign scores (fixed). Mean over seeds 0-4. "Fits": the whole edited
token sequence is at most 512 tokens (no original call leaves the window). Group bootstrap over April hash_apis, 1,000 resamples,
paired across models. Reads the old models' edited-report logits from the cache of scripts/robustness/graded_edits_released.py.
Writes results/pooling_v4/graded_edits.md and graded_edits.json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v4_common as V  # noqa: E402
from v4_common import C, build_variant, V2_TO_INTERNAL, score512  # noqa: E402

NEW = {"M (max)": "M", "MM (mean+max)": "MM", "ATT (attention)": "ATT", "C+aug": "Caug", "ATT+aug": "ATTaug",
       "C+bal": "Cbal", "MM+bal": "MMbal", "ATT+bal": "ATTbal"}
SEEDS = list(range(5))


SKIP = [x for x in os.environ.get("GE_SKIP", "").split(",") if x]               # display names left out (e.g. a model not scored yet)
NEW = {k: v for k, v in NEW.items() if k not in SKIP}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-v4", default="/Users/manish/Code/mtp/pooling_v4_output")
    ap.add_argument("--epochs-new", type=int, default=2)
    a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get("NTHREADS", os.cpu_count() or 4)))
    test, y = V.april()
    N = len(test)
    d = np.load(os.path.join(V.WORK, f"graded_tokens_{N}.npz")); X, L = d["X"], d["L"]
    plain = np.load(os.path.join(V.WORK, f"perturbed_tokens_{N}.npz"))["plain"]
    fits = L <= 512
    z_old = np.load(os.path.join(V.WORK, "robustness_item1_logits.npz"))
    Z = {"released": z_old["released"]}
    for v in ("A", "C"):
        for s in SEEDS:
            Z[f"{v}_s{s}"] = z_old[f"{v}_s{s}"]
    t0 = time.time()
    src = dict(V.SRC); src.update({fam: (a.src_v4, fam + "_all_s{s}", a.epochs_new, 512) for fam in NEW.values()})
    for fam in [*NEW.values(), "C2"]:
        for s in SEEDS:
            run = f"{fam}_all_s{s}"
            path = os.path.join(V.WORK, f"v4_item1_logits_{run}.npz")
            if os.path.exists(path):
                Z[f"{fam}_s{s}"] = np.load(path)["z"]; continue
            m, _, kg = V.load_model(fam, s, src)
            z = np.stack([score512(m, plain.astype(np.int64))] + [score512(m, X[j].astype(np.int64)) for j in range(8)])
            assert np.abs(z[0] - kg).max() < (0.2 if fam == "C2" else 0.05), (run, np.abs(z[0] - kg).max())
            np.savez(path, z=z); Z[f"{fam}_s{s}"] = z
            print(run, f"{time.time() - t0:.0f}s", flush=True)
    names = {"released Nebula": ["released"], "A (J)": [f"A_s{s}" for s in SEEDS], "C (J)": [f"C_s{s}" for s in SEEDS]}
    names["C (J, 2 epochs)"] = [f"C2_s{s}" for s in SEEDS]
    names.update({disp: [f"{fam}_s{s}" for s in SEEDS] for disp, fam in NEW.items()})
    mal, ben = y == 1, y == 0
    flags = {}
    for n, ks in names.items():
        per = np.stack([Z[k] for k in ks])                                   # [seeds, 9, N]
        thr = np.array([C.thr_from(y, per[i, 0], 0.01) for i in range(len(ks))])
        flags[n] = (per > thr[:, None, None]).mean(0)                        # [9, N]
    labels = ["unedited"] + V.EDITS
    W = np.stack(list(C.group_weights_boot(test.hash_apis.values, 1000, 0)))
    wt = lambda fl, mask: (W @ (fl * (mask & mal))) / (W @ (mask & mal).astype(float))
    ci = lambda v: f"[{100 * np.percentile(v, 2.5):+.1f}, {100 * np.percentile(v, 97.5):+.1f}]"
    allm = np.ones(N, bool)
    tabs = {}
    t_tpr, t_fpr = [], []
    for n in names:
        t_tpr.append({"model": n, **{labels[e]: f"{100 * flags[n][e][mal].mean():.1f}%" for e in range(9)}})
        t_fpr.append({"model": n, **{labels[e]: f"{100 * flags[n][e][ben].mean():.2f}%" for e in range(9)}})
    tabs["Malware TPR at the fixed threshold, all April malware reports"] = pd.DataFrame(t_tpr)
    tabs["Benign FPR at the fixed threshold after the same edit of the benign reports (all April benign reports)"] = pd.DataFrame(t_fpr)
    for tag, fn in (("all reports", lambda e: allm), ("reports that fit in 512 tokens after the edit", lambda e: fits[e - 1])):
        rows = []
        for n in names:
            r = {"model": n}
            for e in range(1, 9):
                mk = fn(e)
                pt = flags[n][e][mal & mk].mean() - flags[n][0][mal & mk].mean()
                r[labels[e]] = f"{100 * pt:+.1f} {ci(wt(flags[n][e], mk) - wt(flags[n][0], mk))}"
            rows.append(r)
        tabs[f"Change in malware TPR, points [group 95%], {tag}"] = pd.DataFrame(rows)
        rows = []
        for n in [*NEW, "C (J, 2 epochs)", "A (J)"]:
            for ref in ("C (J, 2 epochs)", "C (J)", "released Nebula"):
                if n == ref:
                    continue
                r = {"difference": f"{n} − {ref}"}
                for e in range(1, 9):
                    mk = fn(e)
                    dd = (wt(flags[n][e], mk) - wt(flags[n][0], mk)) - (wt(flags[ref][e], mk) - wt(flags[ref][0], mk))
                    pt = (flags[n][e][mal & mk].mean() - flags[n][0][mal & mk].mean()) - (flags[ref][e][mal & mk].mean() - flags[ref][0][mal & mk].mean())
                    r[labels[e]] = f"{100 * pt:+.1f} {ci(dd)}"
                rows.append(r)
        tabs[f"Difference between models in the change of TPR, points [group 95%], {tag}"] = pd.DataFrame(rows)
    from sklearn.metrics import roc_auc_score
    auc = {n: np.array([[roc_auc_score(y, Z[k][e]) for e in range(9)] for k in ks]).mean(0) for n, ks in names.items()}
    tabs["AUC of the edited April set (threshold-free)"] = pd.DataFrame([{"model": n, **{labels[e]: f"{auc[n][e]:.4f}" for e in range(9)}} for n in names])
    md = ["# Graded edits with copied calls (round 4)\n",
          "Insert k / prepend k calls (k = 1, 5, 20, 50), each a copy of a call of the same report, first 512 tokens (the edits of `results/robustness` item 1). "
          "Threshold of each model and seed fixed at 1% FPR on the unedited April benign scores; mean over seeds 0–4 (released: one model). "
          "Group-bootstrap intervals over April `hash_apis`.\n"]
    for t, df in tabs.items():
        md += [f"\n## {t}\n", C.md_table(df)]
    open(f"{V.OUT}/graded_edits.md", "w").write("\n".join(md))
    json.dump({"labels": labels, "tpr": {n: [float(flags[n][e][mal].mean()) for e in range(9)] for n in names},
               "fpr": {n: [float(flags[n][e][ben].mean()) for e in range(9)] for n in names},
               "auc": {n: auc[n].tolist() for n in names}}, open(f"{V.OUT}/graded_edits.json", "w"), indent=1)
    print(C.md_table(tabs["Malware TPR at the fixed threshold, all April malware reports"]))


if __name__ == "__main__":
    main()
