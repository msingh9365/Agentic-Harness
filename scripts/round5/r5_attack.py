#!/usr/bin/env python
"""
Round 5, item 3d: white-box greedy padding ("chosen to look benign").

    python scripts/round5/r5_attack.py --models ATTbal,Cbal,released [--seed 0] [--n 500] [--steps 20] [--cands 200]

500 random April malware reports (fixed draw). For each model (one trained seed, attacked with its OWN scores) and each report, up to 20 steps; in every step
200 random candidate calls are drawn from the EVAL pool (a fixed random subset of 30,000 calls of the 361,002 calls of the 2,000 EVAL reports), each is tried
at the front of the report (prepended before the first call) and the one that lowers the model's logit most is kept. A report stops being attacked when its
logit is below the 1% FPR threshold of the model (threshold from the unedited April benign scores); it then counts as evaded for all larger k at both
thresholds (an attacker would stop there). Reports are composed from token pieces (r5_compose.py, checked against full tokenisation); edited reports exist
in memory only, aggregate numbers only are written. TPR(k) = share of the 500 reports still above the threshold after k calls.
Writes results/round5/attack_whitebox.md/json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import r5_common as R  # noqa: E402
from r5_common import C, V, _W, _init  # noqa: E402
from r5_compose import Composer  # noqa: E402

KGRID = [0, 1, 2, 3, 5, 10, 15, 20]


def to_window(arrs, win):
    x = np.zeros((len(arrs), win), dtype=np.int64)
    for i, t in enumerate(arrs):
        t = t[:win]; x[i, :len(t)] = t
    return x


def attack(key, seed, reports, comp, parts, pool_calls, a, thr1, thr01):
    import torch
    m, w, z0 = R.load_model(key, seed)
    rng = np.random.default_rng([9100, seed, 1])
    n = len(reports)
    score = lambda arrs: R.score_tokens(m, w, arrs)
    z_cur = score([comp.compose(p, []) for p in parts])
    chosen = [[] for _ in range(n)]
    length = np.array([len(comp.compose(p, [])) for p in parts])
    traj = [z_cur.copy()]
    lens = [length.copy()]
    alive = z_cur > thr1                                         # still above the 1% threshold: keep attacking
    t0 = time.time()
    for step in range(1, a.steps + 1):
        idx = np.flatnonzero(alive)
        if len(idx) == 0:
            traj.append(z_cur.copy()); lens.append(length.copy()); continue
        cand_idx = rng.integers(len(pool_calls), size=(len(idx), a.cands))
        toks, owner = [], []
        for ii, i in enumerate(idx):
            for c in cand_idx[ii]:
                toks.append(comp.compose(parts[i], [pool_calls[c]] + chosen[i])); owner.append((ii, c))
        z = score(toks).reshape(len(idx), a.cands)
        best = z.argmin(1)
        for ii, i in enumerate(idx):
            c = cand_idx[ii, best[ii]]
            if z[ii, best[ii]] < z_cur[i] or True:               # a greedy step always adds the best candidate (as a real attacker would)
                chosen[i] = [pool_calls[c]] + chosen[i]
                z_cur[i] = z[ii, best[ii]]
                length[i] = len(comp.compose(parts[i], chosen[i]))
        alive = z_cur > thr1
        traj.append(z_cur.copy()); lens.append(length.copy())
        print(f"  [{key} s{seed}] step {step}: {int(alive.sum())} of {n} still above the 1% threshold ({time.time() - t0:.0f}s)", flush=True)
    return np.array(traj), np.array(lens), z0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="ATTbal,Cbal,released")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--cands", type=int, default=200)
    ap.add_argument("--pool-size", type=int, default=30000)
    ap.add_argument("--out", default="attack_whitebox")
    a = ap.parse_args()
    R.n_threads()
    _init(R.NEBULA)
    test, y = V.april()
    rng = np.random.default_rng(11)
    pick = np.sort(rng.choice(np.flatnonzero(y == 1), a.n, replace=False))
    reports = test.row.values[pick]
    p = json.load(open("results/pooling_v4/pools.json"))
    calls = [c for r in p["eval_rows"] for c in (_W["reps"].get(int(r)).get("apis") or [])]
    pool_calls = [calls[i] for i in np.random.default_rng(12).choice(len(calls), min(a.pool_size, len(calls)), replace=False)]
    comp = Composer(_W["nb"])
    parts = [comp.parts(_W["reps"].get(int(r))) for r in reports]
    print(f"{a.n} malware reports, {sum(not q['exact'] for q in parts)} not exactly composable (tokenised in full), pool of {len(pool_calls):,} calls", flush=True)
    res = {}
    for key in a.models.split(","):
        path = os.path.join(R.WORK5, f"attack_{key}_s{a.seed}_n{a.n}.npz")
        if os.path.exists(path):
            d = np.load(path); traj, lens, z0 = d["traj"], d["lens"], d["z0"]
        else:
            thr1 = None
            m_, w_, z0 = R.load_model(key, a.seed)
            thr1, thr01 = C.thr_from(y, z0, 0.01), C.thr_from(y, z0, 0.001)
            del m_
            traj, lens, z0 = attack(key, a.seed, reports, comp, parts, pool_calls, a, thr1, thr01)
            np.savez(path, traj=traj, lens=lens, z0=z0)
        res[key] = (traj, lens, z0)
    rows = {0.01: [], 0.001: []}
    rows_fit = {0.01: [], 0.001: []}
    js = {"k": KGRID, "n": a.n, "seed": a.seed, "tpr": {}}
    for key, (traj, lens, z0) in res.items():
        for f in (0.01, 0.001):
            thr = C.thr_from(y, z0, f)
            thr1 = C.thr_from(y, z0, 0.01)
            # a report that fell below the 1% threshold stays evaded (the attack stopped there)
            ev = np.minimum.accumulate(traj, axis=0) <= thr1 if f == 0.01 else None
            above = (traj > thr)
            stopped = np.maximum.accumulate(traj <= thr1, axis=0)
            above = above & ~stopped if True else above
            r = {"model": R.DISPLAY[key] + (f" (seed {a.seed})" if key != "released" else "")}
            rf = dict(r)
            for k in KGRID:
                r[f"k={k}"] = f"{100 * above[k].mean():.1f}%"
                fit = lens[k] <= 512
                rf[f"k={k}"] = f"{100 * above[k][fit].mean():.1f}% (n={int(fit.sum())})" if fit.any() else "-"
            rows[f].append(r); rows_fit[f].append(rf)
            js["tpr"].setdefault(f"{100 * f:g}%", {})[r["model"]] = [float(above[k].mean()) for k in range(traj.shape[0])]
    md = ["# White-box greedy padding (round 5, item 3d)\n", __doc__.split("500 random")[1].split("Writes")[0].strip().join(["500 random ", "\n"]),
          f"Models: {', '.join(R.DISPLAY[k] for k in res)}; one seed ({a.seed}) each, attacked with its own scores; the 500 April malware reports are the same for all models "
          "(some are not detected at k = 0).\n"]
    for f, tag in ((0.01, "1%"), (0.001, "0.1%")):
        md += [f"\n## TPR of the 500 reports at the threshold of {tag} FPR after k prepended calls\n", C.md_table(pd.DataFrame(rows[f])),
               f"\nOnly the reports whose edited sequence fits in 512 tokens at k ({tag})\n", C.md_table(pd.DataFrame(rows_fit[f]))]
    open(f"{R.OUT}/{a.out}.md", "w").write("\n".join(md))
    json.dump(js, open(f"{R.OUT}/{a.out}.json", "w"), indent=1)
    print("\n".join(md[:14]))


if __name__ == "__main__":
    main()
