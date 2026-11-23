"""
NOTES 29 (CPU, stored attack scores): pairwise differences between models in detection and in padded-benign FPR under attack, with cluster-bootstrap 95% intervals.   (OURS)

    python -m baseline.followups_contrast --scores <dir with scores_<m>.npz> --pairs g3-m3 g3-m1 m3-m1 --sets random_50_prepend lgbm_50_prepend ... --out <dir> [--boot 1000] [--labels m1=M1 ...]

Same resampling as followups_ci.py (cells = hash_apis group x class, 1,000 resamples, numpy seed 0, ONE resample for all models, thresholds at 1% FPR recomputed on every resample, mean over the 10 seeds of each model).
Difference = detection (or padded-benign FPR) of the first model minus that of the second, points x100; the models are different training runs, so the 10-seed means are compared (no seed pairing).
"""
import argparse
import json
import os

import numpy as np

from baseline import followups_ci as F
from baseline.twolevel_eval import april_meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--pairs", nargs="+", required=True, help="a-b: model a minus model b (scores_<a>.npz, scores_<b>.npz)")
    ap.add_argument("--sets", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--labels", nargs="*", default=[], help="key=label")
    a = ap.parse_args()
    lab = dict(x.split("=", 1) for x in a.labels)
    y = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "logits", "labels.npz"))["y_test"].astype(int)
    _, _, groups = april_meta()
    models = sorted({m for p in a.pairs for m in p.split("-")})
    Z = {}
    for m in models:
        d = np.load(os.path.join(a.scores, f"scores_{m}.npz"))
        names = [str(n) for n in d["names"]]
        sel = [names.index("unedited")] + [names.index(s) for s in a.sets]
        Z[m] = np.stack([d[f"seed{s}"] for s in range(10)]).astype(np.float32)[:, sel]
    n = len(y)
    members = {}
    for c in (0, 1):
        idx = np.where(y == c)[0]
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]

    def contrasts(idx, cnt):
        dr = {m: F.one_draw(Z[m], None, y, cnt, idx)[:2] for m in models}
        out = {}
        for what, ix in (("detection", 0), ("padded-benign FPR", 1)):
            for p in a.pairs:
                x, w = p.split("-")
                out[(what, p)] = dr[x][ix][1:, 0] - dr[w][ix][1:, 0]
        return out
    point = contrasts(np.arange(n), np.ones(n, dtype=np.int64))
    rng = np.random.default_rng(0)
    acc = {k: [] for k in point}
    for b in range(a.boot):
        sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        r = contrasts(sel, np.bincount(sel, minlength=n))
        for k in r:
            acc[k].append(r[k])
    L = ["### Differences under attack at the 1% threshold (points x100; difference of the 10-seed mean detection or padded-benign FPR; cluster 95% interval, 1,000 resamples; **bold** = the interval excludes 0)", ""]
    res = {}
    for what in ("detection", "padded-benign FPR"):
        L += [f"**{what}**", "", "| difference | " + " | ".join(a.sets) + " |", "|---|" + "---|" * len(a.sets)]
        for p in a.pairs:
            x, w = p.split("-")
            lo, hi = np.percentile(np.array(acc[(what, p)]), [2.5, 97.5], axis=0)
            pt = point[(what, p)]
            cells = []
            for j in range(len(a.sets)):
                mark = "**" if (lo[j] > 0 or hi[j] < 0) else ""
                cells.append(f"{mark}{100 * pt[j]:+.1f} [{100 * lo[j]:+.1f}, {100 * hi[j]:+.1f}]{mark}")
            L.append(f"| {lab.get(x, x)} - {lab.get(w, w)} | " + " | ".join(cells) + " |")
            res[f"{what}|{p}"] = {"sets": a.sets, "point": pt.tolist(), "lo": lo.tolist(), "hi": hi.tolist()}
        L.append("")
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "contrasts.md"), "w").write("\n".join(L) + "\n")
    json.dump(res, open(os.path.join(a.out, "contrasts.json"), "w"))
    print("\n".join(L))


if __name__ == "__main__":
    main()
