#!/usr/bin/env python
"""
Round 5, G3: ATT+bal over the whole report (up to 4,096 tokens, balanced padding of the full report), regime J, seeds 0-4, 2 epochs. April accuracy next to ATT+bal
(512 tokens, same 5 seeds and all 10), F (C over the whole report, results/fulltrace, seeds 0-4), C (J), and the released Nebula; thresholds (a) at 1% and 0.1% FPR; group
bootstrap over April hash_apis; seed-paired differences; subsets all, 1 / 2-3 / 4-8 chunks, seen / unseen.
Writes results/round5/g3_accuracy.md/json.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import r5_common as R  # noqa: E402
from r5_common import C  # noqa: E402
from r5_accuracy import load_logit, sigmoid  # noqa: E402


def main():
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    never = {f: np.inf for f, _ in C.FPRS}
    neb = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    S5 = list(range(5))
    avail = lambda k, ss: [s for s in ss if R.available(k, s)]
    models = {}
    models["ATT+bal whole report (G3)"] = {s: sigmoid(load_logit("ATTbalW", s)) for s in avail("ATTbalW", S5)}
    models["ATT+bal 512 tokens (seeds 0-4)"] = {s: sigmoid(load_logit("ATTbal", s)) for s in avail("ATTbal", S5)}
    models["ATT+bal 512 tokens (seeds 0-9)"] = {s: sigmoid(load_logit("ATTbal", s)) for s in avail("ATTbal", list(range(10)))}
    models["F (C whole report)"] = {s: sigmoid(load_logit("F", s)) for s in avail("F", S5)}
    models["C 512 tokens (J)"] = {s: sigmoid(load_logit("C", s)) for s in avail("C", S5)}
    models["released Nebula"] = {0: neb}
    zg = np.mean([load_logit("ATTbalW", s) for s in avail("ATTbalW", S5)], 0)
    z5 = np.mean([load_logit("ATTbal", s) for s in avail("ATTbal", S5)], 0)
    models["ATT+bal whole report (G3), ensemble of 5"] = {0: sigmoid(zg)}
    models["ATT+bal 512 tokens, ensemble of 5"] = {0: sigmoid(z5)}
    thr_b = {m: {s: never for s in d} for m, d in models.items()}
    chunks = [("1 chunk", (test.chunks == "1").values), ("2-3 chunks", (test.chunks == "2-3").values), ("4-8 chunks", (test.chunks == "4-8").values),
              ("seen", test.seen.values), ("unseen", (~test.seen.values)), ("all", np.ones(len(test), bool))]
    masks = [chunks[-1]] + chunks[:-1]
    G, A5, F, Cc = "ATT+bal whole report (G3)", "ATT+bal 512 tokens (seeds 0-4)", "F (C whole report)", "C 512 tokens (J)"
    diffs = [(G, A5), (G, F), (G, Cc), (G, "released Nebula"), (A5, F), (A5, "released Nebula")]
    point, cis, dci, masks = C.evaluate_models(test, models, thr_b, n_boot=1000, diffs=diffs, masks=masks)
    cols = ["auc", "tpr1%_a", "tpr0.1%_a"]
    rows = []
    for sub, _ in masks:
        for m in models:
            r = {"subset": sub, "model": m, "seeds": len(point[m]["_seeds"]), "n (malware)": f"{point[m][sub]['n']:,.0f} ({point[m][sub]['n_mal']:,.0f})"}
            for k in cols:
                lo, hi = cis[(m, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt(k, point[m][sub][k])} [{C.fmt(k, lo)}, {C.fmt(k, hi)}]"
            rows.append(r)
    drows = []
    for x, z in diffs:
        for sub, _ in masks:
            r = {"difference": f"{x} − {z}", "subset": sub}
            for k in cols:
                lo, hi = dci[(x, z, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt_d(k, point[x][sub][k] - point[z][sub][k])} [{C.fmt_d(k, lo)}, {C.fmt_d(k, hi)}]"
            drows.append(r)
    rng = np.random.default_rng(0)
    sp = []
    for x, z in ((G, A5), (G, F), (G, Cc), (A5, F)):
        n = min(len(point[x]["_seeds"]), len(point[z]["_seeds"]))
        r = {"difference": f"{x} − {z}", "seeds": n}
        for k, tag in (("auc", "AUC"), ("tpr1%_a", "TPR@1%"), ("tpr0.1%_a", "TPR@0.1%")):
            d = np.array([point[x]["_seeds"][i]["all"][k] - point[z]["_seeds"][i]["all"][k] for i in range(n)])
            b = rng.choice(d, (20000, n)).mean(1)
            f = (lambda v: f"{v:+.4f}") if k == "auc" else (lambda v: f"{100 * v:+.1f}")
            r[tag] = f"{f(d.mean())} [{f(np.percentile(b, 2.5))}, {f(np.percentile(b, 97.5))}]"
        sp.append(r)
    md = ["# G3: ATT+bal over the whole report (round 5)\n",
          "ATT pooling over up to 4,096 tokens, trained with balanced padding of the full report (benign and malware training reports padded with TRAIN-pool calls with probability 0.5, "
          "re-tokenised up to 4,096 tokens), regime J, seeds 0-4, 2 epochs. April, thresholds (a) at 1% and 0.1% FPR of each model and seed, mean over seeds [95% group-bootstrap interval].\n",
          C.md_table(pd.DataFrame(rows)), "\n## Paired differences (group bootstrap; TPR in points)\n", C.md_table(pd.DataFrame(drows)),
          "\n## Seed-paired differences, all April reports [95% over the seeds]\n", C.md_table(pd.DataFrame(sp))]
    open(f"{R.OUT}/g3_accuracy.md", "w").write("\n".join(md))
    json.dump({"point": {m: {s: {k: float(v) for k, v in d.items()} for s, d in point[m].items() if s != "_seeds"} for m in point}}, open(f"{R.OUT}/g3_accuracy.json", "w"), indent=1)
    print(C.md_table(pd.DataFrame([r for r in rows if r["subset"] == "all"])))


if __name__ == "__main__":
    main()
