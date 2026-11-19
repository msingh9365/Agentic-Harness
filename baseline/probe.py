"""
Shortcut probe (NOTES 15.2): can a linear classifier read "padding present" off the pooled embedding of a model?   (OURS)

    python -m baseline.probe --plan --jobs v2_pe:v2_pe att:attbal ... --out out [--models-root ...] [--search /kaggle/input]

Data: every April report (17,402) is padded with probability 0.5 (flag = default_rng(11).random(N) < 0.5), k ~ U{1..50}, insert or prepend 50/50 (default_rng([8100, row])), the added calls drawn
uniformly (random EVAL-pool report, then random call) -- the same procedure as the balanced training padding but with the EVAL pool, in memory only, nothing written.
Features of a model (eval mode): `pooled` = the vector before the classification head (flatten models: the 32,768-d flattened vector; attention models: the 64-d pooled vector) and `hidden` =
the 64-d vector after the first head layer (same size for every model). The reports are split by row index into two halves (even / odd); a logistic regression (features z-scored with the training
half's mean and standard deviation; loss = mean cross-entropy + 1e-2 * ||w||^2 / 2; LBFGS, 100 iterations) is fitted on one half and its ROC AUC for "padded" measured on the other, in both directions;
the mean of the two AUCs is reported. Saved: probe_<family>.npz with auc_pooled / auc_hidden [n_seeds, 2] (and the chance-level check with shuffled labels). Only AUCs are saved.
"""
import argparse
import os
import subprocess
import sys
import time

import numpy as np

from baseline import callstore as CS, common as C, gap, padtest

PAD_STREAM = 8100
FLAG_SEED = 11


def padded_set(store, ntr, n_test, pool):
    """(tokens uint16 [N, 512], flags bool [N]) of April reports, padded with probability 0.5 (in memory)."""
    flags = np.random.default_rng(FLAG_SEED).random(n_test) < 0.5
    calls = [(int(r), i) for r in pool for i in range(store.n_calls(int(r)))]
    pool_n = np.array([store.n_calls(int(r)) for r in pool])
    tok = np.zeros((n_test, CS.SEQ), dtype=np.uint16)
    for t in range(n_test):
        r = ntr + t
        n = store.n_calls(r)
        if not flags[t] or n == 0:
            flags[t] = False
            tok[t] = CS.build_fast(store, r, [], None)[0]
            continue
        rng = np.random.default_rng([PAD_STREAM, int(r)])
        mode = "insert" if rng.random() < 0.5 else "prepend"
        k = int(rng.integers(1, 51))
        added = []
        for _ in range(k):
            pr = int(rng.integers(len(pool)))
            added.append(store.call(int(pool[pr]), int(rng.integers(pool_n[pr]))))
        gaps = np.sort(rng.integers(0, n + 1, k)) if mode == "insert" else None
        tok[t] = CS.build_fast(store, r, added, gaps)[0]
    return tok, flags


def features(model, tok, device, bs=256):
    import torch
    pooled, hidden = [], []
    with torch.no_grad():
        for i in range(0, len(tok), bs):
            x = torch.from_numpy(tok[i:i + bs].astype(np.int64)).to(device)
            p = model.core(x)
            pooled.append(p.float())
            hidden.append(model.classifier_head[0](p).float())
    return torch.cat(pooled), torch.cat(hidden)


def probe_auc(F, flags, device, l2=1e-2, iters=100):
    """mean over the two directions (even -> odd, odd -> even) of the AUC of a logistic regression for `flags`."""
    import torch
    from sklearn.metrics import roc_auc_score
    idx = np.arange(len(flags))
    halves = [idx[idx % 2 == 0], idx[idx % 2 == 1]]
    y = torch.as_tensor(flags.astype(np.float32), device=device)
    aucs = []
    for a, b in ((0, 1), (1, 0)):
        tr, te = torch.as_tensor(halves[a], device=device), torch.as_tensor(halves[b], device=device)
        mu, sd = F[tr].mean(0), F[tr].std(0).clamp(min=1e-6)
        Xtr, Xte = (F[tr] - mu) / sd, (F[te] - mu) / sd
        w = torch.zeros(F.shape[1], device=device, requires_grad=True)
        b0 = torch.zeros(1, device=device, requires_grad=True)
        opt = torch.optim.LBFGS([w, b0], lr=1.0, max_iter=iters, line_search_fn="strong_wolfe")

        def closure():
            opt.zero_grad()
            loss = torch.nn.functional.binary_cross_entropy_with_logits(Xtr @ w + b0, y[tr]) + l2 * (w * w).sum() / 2
            loss.backward()
            return loss
        opt.step(closure)
        with torch.no_grad():
            s = (Xte @ w + b0).cpu().numpy()
        aucs.append(float(roc_auc_score(flags[halves[b]], s)))
    return aucs


def run(a):
    store, y_test, ntr, ranking, pool = __import__("baseline.attack_run", fromlist=["inputs"]).inputs(a)
    t0 = time.time()
    tok, flags = padded_set(store, ntr, len(y_test), pool)
    print(f"[{a.family}] {len(tok):,} April reports, {int(flags.sum()):,} padded, built in memory ({time.time() - t0:.0f}s)", flush=True)
    res = {"auc_pooled": [], "auc_hidden": [], "auc_shuffled": []}
    shuf = np.random.default_rng(0).permutation(flags)
    for s in a.seeds:
        m = padtest.load_model(a.kind, padtest.find_weights(a.kind, s, a.models_root, a.search), a.device)
        P, H = features(m, tok, a.device)
        res["auc_pooled"].append(probe_auc(P, flags, a.device))
        res["auc_hidden"].append(probe_auc(H, flags, a.device))
        res["auc_shuffled"].append(probe_auc(H, shuf, a.device))
        print(f"[{a.family}] seed {s}: probe AUC pooled {np.mean(res['auc_pooled'][-1]):.4f} hidden {np.mean(res['auc_hidden'][-1]):.4f} (shuffled-label check {np.mean(res['auc_shuffled'][-1]):.3f}) ({time.time() - t0:.0f}s)", flush=True)
        del m, P, H
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(os.path.join(a.out, f"probe_{a.family}.npz"), **{k: np.array(v) for k, v in res.items()}, n_padded=int(flags.sum()), n=len(flags))


def orchestrate(a):
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    jobs, running, failed = [j.split(":") for j in a.jobs], {}, []
    while jobs or running:
        for g in range(n_gpu):
            if g not in running and jobs:
                fam, kind = jobs.pop(0)
                cmd = [sys.executable, "-m", "baseline.probe", "--family", fam, "--kind", kind, "--out", a.out, "--device", a.device, "--ranking", a.ranking, "--store", a.store, "--seeds"] + [str(x) for x in a.seeds]
                if a.models_root:
                    cmd += ["--models-root", a.models_root]
                if a.search:
                    cmd += ["--search", a.search]
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g))), fam)
                print(f"GPU {g}: started {fam}", flush=True)
        for g, (p, fam) in list(running.items()):
            if p.poll() is not None:
                print(f"GPU {g}: {fam} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(fam)
                del running[g]
        time.sleep(3)
    if failed:
        raise SystemExit(f"probe failed: {failed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--jobs", nargs="*", default=[])
    ap.add_argument("--family", default=None)
    ap.add_argument("--kind", default=None, choices=list(padtest.KINDS))
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--out", required=True)
    ap.add_argument("--store", default="all.npz")
    ap.add_argument("--store-released", default="all_released.npz")
    ap.add_argument("--ranking", default="ranking.json")
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--models-root", default=None)
    ap.add_argument("--search", default=None)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    a.released = False
    if a.plan:
        return orchestrate(a)
    C.setup_nebula(require_patched=True)
    return run(a)


if __name__ == "__main__":
    main()
