"""
Scoring of the further edit families of baseline/extra_edits.py (audit item 4) for released, v2-PE, PE+bal and ATT+bal, and of the test-time deduplication defence on v2-PE.   (OURS)

  GPU (Kaggle, two workers):  python -m baseline.extra_run --gpu-mode --device cuda --out out --families v2_pe pebal attbal --seeds 0 2 4 6 8 --dedup-seeds 0 2 4 6 8 [--released] --ident <extra_ident.npz>
                              builds the edit sets that need only the call-token store (rare, block, copy, rotation; NOT argument injection), no report text needed
  CPU (needs the reports):    python -m baseline.extra_run --only-inj --out results/review/extra --families v2_pe pebal attbal --seeds 0 1 ... --dedup-seeds 0 1 ... [--released]
                              builds and scores only the three argument-injection sets (they need the original call texts and the tokenizer)

Edited reports exist in memory only: the tokens of every edit set are built from the call-token store of the original reports at the start of the process and scored at once; only scores are saved:
x_<family>_seed<k>.npz / d_...  (GPU run: z [24, 17,402], row 0 = unedited, rows 1.. = extra_edits.SET_NAMES; rows not computed by this run are NaN), xi_... / di_... (the CPU injection run, same shape, other rows NaN);
d_ = deduplication applied after the edit (row 0 = the deduplicated unedited report); x_meta_<store>.npz = token totals. Resumable. baseline/extra_report.py merges the two.
"""
import argparse
import os
import time

import numpy as np

from baseline import callstore as CS, common as C, extra_edits as X, gap, make_pad, padtest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS = {"v2_pe": os.path.join(ROOT, "results", "_models_big", "detection", "bpe50k", "v2_pe", "seed{s}.pt"),
           "pebal": os.path.join(ROOT, "results", "_pebal_raw", "out", "pebal", "seed{s}_epoch2_model.pt"),
           "attbal": os.path.join(ROOT, "results", "_attbal_raw2", "out", "attbal", "seed{s}_epoch2_model.pt")}
NAMES = ["unedited"] + X.SET_NAMES
INJ = [i for i, n in enumerate(NAMES) if n.startswith("inj_")]


def setup_gpu(released, a):
    """Everything from the datasets of the kernel (no report text): store, labels, EVAL pool, pools, identities."""
    store_name = "all_released.npz" if released else "all.npz"
    store = CS.CallStore.load(os.path.join(C.find_dir_with(store_name), store_name))
    lab = np.load(os.path.join(C.find_dir_with("labels.npz"), "labels.npz"))
    y, ntr = lab["y_train"], len(lab["y_train"])
    trn, val = gap.val_slice(lab["ym_train"])
    pool = np.array([int(r) for r in val if y[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
    ident_path = a.ident if a.ident and os.path.exists(a.ident) else os.path.join(C.find_dir_with("extra_ident.npz"), "extra_ident.npz")
    return store, X.Pools(store, pool, trn, reps=None), ntr, X.Ident.from_npz(ident_path), None, None


def setup_cpu(released):
    from baseline import extra_check
    store, tr, te, reps, P, ntr = extra_check.setup(released)
    tok = make_pad.make_tokenizer(released=released)
    cache = {}

    def rep_of(row):
        row = int(row)
        if row >= ntr:
            if row not in cache:
                cache.clear() if len(cache) > 64 else None
                cache[row] = reps.get(int(te[row - ntr]))
            return cache[row]
        return reps.get(int(tr[row]))
    return store, P, ntr, X.Ident(rep_of), tok, rep_of


def build(released, with_dedup, a):
    store, P, ntr, ident, tok, rep_of = setup_gpu(released, a) if a.gpu_mode else setup_cpu(released)
    n_test = 17402 if not a.limit else a.limit
    keep = np.array([(i not in INJ) if not a.only_inj else (i in INJ) for i in range(len(NAMES))])
    keep[0] = True
    toks = np.zeros((len(NAMES), n_test, CS.SEQ), dtype=np.uint16)
    tot = np.zeros((len(NAMES), n_test), dtype=np.int32)
    dtoks = np.zeros_like(toks) if with_dedup else None
    t0 = time.time()
    rc = (lambda rr, i: rep_of(rr)["apis"][i]) if rep_of else None
    for t in range(n_test):
        r = ntr + t
        n = store.n_calls(r)
        specs = [None] + X.all_specs(t, n, P)
        for j, sp in enumerate(specs):
            if not keep[j]:
                continue
            toks[j, t], tot[j, t] = X.spec_tokens(store, r, sp, tok, rc)
            if with_dedup:
                dtoks[j, t] = X.build_dedup(store, r, sp, ident, tok, rc)
        if t % 3000 == 0:
            print(f"  built {t}/{n_test} reports ({time.time() - t0:.0f}s)", flush=True)
    return toks, tot, dtoks, keep


def score_sets(model, toks, keep, device, bs=512):
    """z [sets, N]: row 0 scored, other kept rows scored only where the tokens differ from the unedited report; rows that are not kept stay NaN."""
    import torch
    z = np.full(toks.shape[:2], np.nan, dtype=np.float32)
    same = (toks == toks[0:1]).all(2)
    with torch.no_grad():
        for j in range(toks.shape[0]):
            if not keep[j]:
                continue
            idx = np.arange(toks.shape[1]) if j == 0 else np.where(~same[j])[0]
            for i in range(0, len(idx), bs):
                b = idx[i:i + bs]
                z[j, b] = model(torch.from_numpy(toks[j, b].astype(np.int64)).to(device)).reshape(-1).float().cpu().numpy()
            if j > 0:
                z[j, same[j]] = z[0, same[j]]
    return z, int(same[keep][1:].sum()) if keep.sum() > 1 else 0


def main():
    import torch
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--families", nargs="*", default=["v2_pe", "pebal", "attbal"])
    ap.add_argument("--dedup-seeds", type=int, nargs="*", default=[])
    ap.add_argument("--released", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="smoke test: only this many April reports")
    ap.add_argument("--gpu-mode", action="store_true")
    ap.add_argument("--only-inj", action="store_true")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--ident", default=None)
    ap.add_argument("--search", default=None)
    ap.add_argument("--models-root", default=None)
    a = ap.parse_args()
    C.setup_nebula(require_patched=True)
    if a.device == "cpu":
        torch.set_num_threads(4)
    os.makedirs(a.out, exist_ok=True)
    px, pd = ("xi", "di") if a.only_inj else ("x", "d")
    work = ([("released", 0, False)] if a.released else []) + [(f, s, False) for s in a.seeds for f in a.families] + [("v2_pe", s, True) for s in a.dedup_seeds]
    work = [w for w in work if not os.path.exists(os.path.join(a.out, f"{pd if w[2] else px}_{w[0]}_seed{w[1]}.npz"))]
    if not work:
        print("nothing to do")
        return
    need_dedup = any(w[2] for w in work)
    cache = {}
    t0 = time.time()
    for fam, seed, dd in work:
        rel = fam == "released"
        if rel not in cache:
            cache.clear()
            cache[rel] = build(rel, need_dedup and not rel, a)
            toks, tot, dtoks, keep = cache[rel]
            if not a.only_inj:
                np.savez_compressed(os.path.join(a.out, f"x_meta_{'released' if rel else 'ours'}.npz"), totals=tot, set_names=np.array(NAMES))
            print(f"edit sets built ({time.time() - t0:.0f}s)", flush=True)
        toks, tot, dtoks, keep = cache[rel]
        arr = dtoks if dd else toks
        if a.gpu_mode or a.search:
            path = padtest.find_weights("released", 0) if rel else padtest.find_weights(fam, seed, a.models_root, a.search or "/kaggle/input")
        else:
            path = padtest.find_weights("released", 0) if rel else WEIGHTS[fam].format(s=seed)
        m = padtest.load_model("released" if rel else fam, path, a.device)
        z, reused = score_sets(m, arr, keep, a.device)
        np.savez_compressed(os.path.join(a.out, f"{pd if dd else px}_{fam}_seed{seed}.npz"), z=z)
        print(f"[{fam}{' + dedup' if dd else ''} seed {seed}] scored {int(keep.sum())} sets x {arr.shape[1]:,} reports, {reused:,} unchanged rows reused ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
