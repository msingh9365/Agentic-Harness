"""Check of the edit builders of baseline/extra_edits.py against the full re-tokenisation of the edited report (tokens and total length), for every edit set, and of the deduplication builder against
a dict-level deduplication.   python -m baseline.extra_check [--n 120] [--released]"""
import argparse
import os

import numpy as np

from baseline import callstore as CS, common as C, extra_edits as X, gap, inmem_pad, make_pad

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup(released=False):
    store = CS.CallStore.load(os.path.join(ROOT, "results", "callstore", "all_released.npz" if released else "all.npz"))
    tr, te = make_pad.load_row_map()
    lab = np.load(os.path.join(ROOT, "results", "_tokens_raw", "out", "labels.npz"))
    y = lab["y_train"]
    trn, val = gap.val_slice(lab["ym_train"])
    pool = np.array([int(r) for r in val if y[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
    reps = make_pad.Reps()
    jan = lambda row: reps.get(int(tr[int(row)]))
    P = X.Pools(store, pool, trn, reps=jan)
    return store, tr, te, reps, P, len(tr)


def dedup_dicts(apis):
    out, prev = [], None
    for c in apis:
        s = repr(c)
        if s == prev:
            continue
        prev = s
        out.append(c)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--released", action="store_true")
    a = ap.parse_args()
    store, tr, te, reps, P, ntr = setup(a.released)
    print(f"pools: {len(P.pool):,} EVAL-pool reports; {P.n_names:,} API names in the pool, {P.n_rare_names:,} rare (training frequency <= {P.rare_cut:g}), {len(P.rare):,} rare calls; {len(P.donors):,} argument donors", flush=True)
    tok = make_pad.make_tokenizer(released=a.released)
    rep_of = lambda row: reps.get(int(te[int(row) - ntr])) if int(row) >= ntr else reps.get(int(tr[int(row)]))
    ident = X.Ident(rep_of)
    jan = lambda row, idx: reps.get(int(tr[int(row)]))["apis"][int(idx)]
    rng = np.random.default_rng(3)
    ts = rng.choice(len(te), a.n, replace=False)
    bad = {nm: 0 for nm in X.SET_NAMES}
    bad_d = {nm: 0 for nm in X.SET_NAMES + ["unedited"]}
    nsp = {nm: 0 for nm in X.SET_NAMES}
    for t in ts:
        t = int(t); r = ntr + t
        rep = reps.get(int(te[t]))
        n = store.n_calls(r)
        specs = X.all_specs(t, n, P)
        reps_call = lambda rr, i, rep=rep: rep["apis"][i]
        for nm, sp in zip(X.SET_NAMES, specs):
            if sp is None:
                continue
            nsp[nm] += 1
            mine, total = X.spec_tokens(store, r, sp, tok, reps_call)
            full = tok.encode([X.spec_report(rep, sp, jan)], pad=False)[0]
            if not (np.array_equal(mine, make_pad.to512(full)) and total == len(full)):
                bad[nm] += 1
            d_mine = X.build_dedup(store, r, sp, ident, tok, reps_call)
            r2 = X.spec_report(rep, sp, jan)
            r2["apis"] = dedup_dicts(r2["apis"])
            d_full = make_pad.to512(tok.encode([r2], pad=False)[0])
            if not np.array_equal(d_mine, d_full):
                bad_d[nm] += 1
        d_mine = X.build_dedup(store, r, None, ident)
        r2 = dict(rep); r2["apis"] = dedup_dicts(list(rep.get("apis") or []))
        if not np.array_equal(d_mine, make_pad.to512(tok.encode([r2], pad=False)[0])):
            bad_d["unedited"] += 1
    for nm in X.SET_NAMES:
        print(f"{nm:18s} edited reports {nsp[nm]:4d}: builder != full re-tokenisation: {bad[nm]};  dedup builder != dict-level dedup: {bad_d[nm]}")
    print("unedited + dedup differs:", bad_d["unedited"])
    assert sum(bad.values()) == 0 and sum(bad_d.values()) == 0
    print("extra edit builders checked")


if __name__ == "__main__":
    main()
