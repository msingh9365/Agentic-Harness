#!/usr/bin/env python
"""
Item 4 of results/robustness: why does C beat B? Does C use the order of tokens inside a call?

    python scripts/robustness/within_call_shuffle.py --src <regime S output> --work <cache folder>

B (mean pooling, positions as released) has no position information inside a 64-token chunk; C (mean pooling, fixed position
encoding) has. Three edits of every April report, then the first 512 tokens:
  (a) whole calls shuffled   : the order of the API calls is permuted, every call keeps its own token order
                               (the same tokens as scripts/pooling_v2/perturb_check.py)
  (b) tokens shuffled inside each call, call order kept: the tokens of a call (its exact span in Nebula's token sequence,
                               from measure_links.call_positions) are permuted; the header tokens before the first call
                               and every call's position in the report are unchanged. Reports for which the per-call
                               tokenisation does not reproduce the full tokenisation are left unchanged and counted.
  (c) control: all 512 tokens of the window shuffled (a bag of tokens).
Models: regime S, 10 seeds, checkpoint chosen on validation AUC; B and C as asked, A as a reference.
Reads: the unedited scores of the Kaggle run. Reports AUC and TPR at 1% FPR (threshold recomputed on each score vector),
mean over seeds, and the seed-paired change.
Writes results/robustness/within_call_shuffle.md and .json.
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "go_no_go"))
sys.path.insert(0, os.path.join(HERE, "..", "pooling_v2"))
import common as C  # noqa: E402
from hier_nebula.pooling_variants import build_variant, V2_TO_INTERNAL  # noqa: E402
from perturb_check import _init, _W, pad, logits  # noqa: E402

OUT = "results/robustness"
_ = _init


def _tok(row):
    from measure_links import call_positions
    nb, rep = _W["nb"], _W["reps"].get(int(row))
    full = np.asarray(nb.ids(rep), dtype=np.int32)
    starts, lens, n_tok, fallback, head = call_positions(nb, rep)
    rng = np.random.default_rng(4000 + int(row))
    within = full.copy()
    if not fallback:
        for s, l in zip(starts, lens):
            if s >= 512:
                break
            if l > 1:
                within[s:s + l] = full[s:s + l][rng.permutation(l)]
    win = full[:512].copy()
    bag = win[rng.permutation(len(win))]
    return int(row), within[:512], bag, bool(fallback), int(len(starts))


def auc(y, s):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y, s))


def metrics(y, z):
    sc = C.Scorer(y, z, {0.01: np.inf, 0.001: np.inf})
    m = sc.metrics(np.ones(len(y)), [("all", np.ones(len(y), bool))])["all"]
    return float(m["auc"]), float(m["tpr1%_a"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--nebula", default="../nebula")
    ap.add_argument("--variants", default="A,B,C")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 4)
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    rows = test.row.values[:a.limit] if a.limit else test.row.values
    y = test.label.values[:len(rows)]
    N = len(rows)
    cache = os.path.join(a.work, f"within_call_tokens_{N}.npz")
    pc = np.load(os.path.join(a.work, f"perturbed_tokens_{len(test)}.npz"))
    plain, whole = pc["plain"][:N], pc["shuf"][:N]
    if os.path.exists(cache):
        d = np.load(cache); within, bag, fb, ncalls = d["within"], d["bag"], d["fb"], d["ncalls"]
    else:
        t0 = time.time()
        with Pool(a.workers, initializer=_init, initargs=(a.nebula,)) as pool:
            res = list(pool.imap(_tok, rows, chunksize=32))
        assert [r[0] for r in res] == list(rows)
        within, bag = pad([r[1] for r in res]).astype(np.int32), pad([r[2] for r in res]).astype(np.int32)
        fb, ncalls = np.array([r[3] for r in res]), np.array([r[4] for r in res])
        np.savez(cache, within=within, bag=bag, fb=fb, ncalls=ncalls)
        print(f"tokenised {N:,} reports in {time.time() - t0:.0f}s", flush=True)
    # token id 0 (<pad>) also occurs as a real token inside reports; a within-call shuffle can move one across the 512 boundary
    n_nz = (plain > 0).sum(1)
    long_ = np.load(os.path.join(a.work, f"perturbed_tokens_{len(test)}.npz"))["n_plain"][:N] >= 512
    chg = lambda x: float(np.mean((x != plain).any(1)))
    info = {"share_nonzero_count_changed_within": float((n_nz != (within > 0).sum(1)).mean()),
            "share_reports_with_real_zero_token_in_window": float((plain[long_] == 0).any(1).mean()),
            "share_changed_whole_calls": chg(whole), "share_changed_within_call": chg(within), "share_changed_bag": chg(bag),
            "share_fallback_left_unchanged": float(fb.mean()), "share_no_calls": float((ncalls == 0).mean())}
    print(info, flush=True)

    runs = {}
    for v in a.variants.split(","):
        for s in range(10):
            run = f"{v}_s{s}"
            ep = json.load(open(os.path.join(a.src, "logs", f"{run}.json")))["epoch_by_val_auc"]
            z0 = np.load(os.path.join(a.src, "scores", f"{run}_epochs.npz"))["april"][ep - 1][:N]
            m = build_variant(a.nebula, V2_TO_INTERNAL[v]).eval()
            m.load_state_dict(torch.load(os.path.join(a.src, "ckpt", run, "best_auc.pt"), map_location="cpu", weights_only=True))
            r = {"epoch": ep}
            for tag, x in (("original", None), ("whole calls", whole), ("within calls", within), ("bag of tokens", bag)):
                z = z0 if x is None else logits(m, x.astype(np.int64))
                r[tag] = metrics(y, z)
            runs[run] = r
            print(run, {k: (round(v_[0], 4), round(v_[1], 3)) for k, v_ in r.items() if k != "epoch"}, flush=True)
            json.dump({"info": info, "runs": runs}, open(f"{OUT}/within_call_shuffle.json" if not a.limit else f"{OUT}/within_call_shuffle_debug.json", "w"), indent=1)

    vs = a.variants.split(",")
    g = lambda v, tag, i: np.array([runs[f"{v}_s{s}"][tag][i] for s in range(10)])
    rng = np.random.default_rng(0)
    boot = lambda x: (x.mean(), np.percentile(rng.choice(x, (20000, len(x))).mean(1), [2.5, 97.5]))
    t1 = []
    for v in vs:
        for tag in ("original", "whole calls", "within calls", "bag of tokens"):
            au, tp = g(v, tag, 0), 100 * g(v, tag, 1)
            r = {"model": v, "input": tag, "AUC": f"{au.mean():.4f}", "AUC sd": f"{au.std(ddof=1):.4f}", "TPR@1% (a)": f"{tp.mean():.1f}%"}
            if tag != "original":
                da, dt = au - g(v, "original", 0), tp - 100 * g(v, "original", 1)
                mu, ci = boot(da); mt, ct = boot(dt)
                r["AUC change [95% over seeds]"] = f"{mu:+.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}]"
                r["TPR change, points [95%]"] = f"{mt:+.1f} [{ct[0]:+.1f}, {ct[1]:+.1f}]"
            t1.append(r)
    t2 = []
    if "B" in vs and "C" in vs:
        for tag in ("whole calls", "within calls", "bag of tokens"):
            for nm, i, sc in (("AUC", 0, 1), ("TPR@1% (a), points", 1, 100)):
                x = sc * ((g("C", tag, i) - g("C", "original", i)) - (g("B", tag, i) - g("B", "original", i)))
                mu, ci = boot(x)
                t2.append({"edit": tag, "metric": nm, "C's change − B's change [95% over seeds]": f"{mu:+.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}]" if sc == 1 else f"{mu:+.1f} [{ci[0]:+.1f}, {ci[1]:+.1f}]"})
    md = ["# Item 4: does C use the order of tokens inside a call?\n",
          f"April reports, regime S, 10 seeds, checkpoint chosen on validation AUC. Share of reports whose first 512 tokens change: whole calls "
          f"shuffled {100 * info['share_changed_whole_calls']:.1f}%, tokens shuffled inside each call {100 * info['share_changed_within_call']:.1f}%, "
          f"all tokens shuffled {100 * info['share_changed_bag']:.1f}%. Reports left unchanged in the within-call edit because the per-call tokenisation "
          f"did not reproduce the full one: {100 * info['share_fallback_left_unchanged']:.1f}%; reports without calls: {100 * info['share_no_calls']:.1f}%. "
          "TPR with the threshold recomputed on each score vector.\n", C.md_table(pd.DataFrame(t1)),
          "\n## C versus B: difference in the change caused by the edit\n", C.md_table(pd.DataFrame(t2))]
    if not a.limit:
        open(f"{OUT}/within_call_shuffle.md", "w").write("\n".join(md))
    print("\n".join(md[1:]))


if __name__ == "__main__":
    main()
