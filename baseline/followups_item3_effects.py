"""
NOTES 26 item 3 (CPU, stored attack scores): main effects of head and of padding, and their interaction, on detection and on the padded-benign false-positive rate under attack, with cluster-bootstrap 95% intervals.   (OURS)

    python -m baseline.followups_item3_effects --scores <dir with scores_x_fn/x_an/x_fb/x_ab.npz> --out <dir> [--boot 1000]

Same resampling as followups_ci.py (cells = hash_apis group x class, 1,000 resamples, numpy seed 0, one resample for all four models, thresholds at 1% FPR recomputed on every resample, mean over the 10 seeds).
Effects (points x100; detection at the 1% threshold or padded-benign FPR): head | none = an - fn, head | balanced = ab - fb, padding | flatten = fb - fn, padding | attention = ab - an, interaction = (ab - an) - (fb - fn).
Seeds are different training runs: the models are compared through their 10-seed means (seed pairing is not used).
"""
import argparse
import json
import os

import numpy as np

from baseline import followups_ci as F
from baseline.twolevel_eval import april_meta

SETS = ["random_20_prepend", "random_50_prepend", "lgbm_50_prepend"]
M = {"fn": "x_fn", "an": "x_an", "fb": "x_fb", "ab": "x_ab"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "logits", "labels.npz"))["y_test"].astype(int)
    _, _, groups = april_meta()
    Z, names = {}, None
    for k, f in M.items():
        d = np.load(os.path.join(a.scores, f"scores_{f}.npz"))
        names = [str(n) for n in d["names"]]
        Z[k] = np.stack([d[f"seed{s}"] for s in range(10)]).astype(np.float32)
    sel_sets = [names.index("unedited")] + [names.index(s) for s in SETS]
    Z = {k: v[:, sel_sets] for k, v in Z.items()}
    n = len(y)
    members = {}
    for c in (0, 1):
        idx = np.where(y == c)[0]
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]

    def contrasts(draw):                                           # draw[k] = (det[sets, 2], fpr[sets, 2]); use the 1% column
        out = {}
        for what, ix in (("detection", 0), ("padded-benign FPR", 1)):
            v = {k: draw[k][ix][:, 0] for k in M}
            out[what] = {"head, no padding (attention - flatten)": v["an"] - v["fn"], "head, balanced padding (attention - flatten)": v["ab"] - v["fb"],
                         "padding, flatten head (balanced - none)": v["fb"] - v["fn"], "padding, attention head (balanced - none)": v["ab"] - v["an"],
                         "interaction (ab - an) - (fb - fn)": (v["ab"] - v["an"]) - (v["fb"] - v["fn"])}
        return out

    def draw_of(idx, cnt):
        return {k: F.one_draw(Z[k], None, y, cnt, idx)[:2] for k in M}

    point = contrasts(draw_of(np.arange(n), np.ones(n, dtype=np.int64)))
    rng = np.random.default_rng(0)
    acc = {w: {c: [] for c in point[w]} for w in point}
    for b in range(a.boot):
        sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        r = contrasts(draw_of(sel, np.bincount(sel, minlength=n)))
        for w in r:
            for c in r[w]:
                acc[w][c].append(r[w][c])
    label = ["unedited"] + SETS
    L = ["### Item 3 under attack: effects of head and padding and their interaction (points x100; mean of the 10-seed means; cluster 95% bootstrap interval; thresholds at 1% FPR on each model's own clean April scores)", ""]
    res = {}
    for w in point:
        L += [f"**{w}**", "", "| effect | " + " | ".join(label) + " |", "|---|" + "---|" * len(label)]
        for c in point[w]:
            lo, hi = np.percentile(np.array(acc[w][c]), [2.5, 97.5], axis=0)
            cells = []
            for j in range(len(label)):
                mark = "**" if (lo[j] > 0 or hi[j] < 0) else ""
                cells.append(f"{mark}{100 * point[w][c][j]:+.1f} [{100 * lo[j]:+.1f}, {100 * hi[j]:+.1f}]{mark}")
            L.append(f"| {c} | " + " | ".join(cells) + " |")
            res[f"{w}|{c}"] = {"sets": label, "point": point[w][c].tolist(), "lo": lo.tolist(), "hi": hi.tolist()}
        L.append("")
    L.append("Bold = the cluster interval excludes 0.")
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "effects_under_attack.md"), "w").write("\n".join(L) + "\n")
    json.dump(res, open(os.path.join(a.out, "effects_under_attack.json"), "w"))
    print("\n".join(L))


if __name__ == "__main__":
    main()
