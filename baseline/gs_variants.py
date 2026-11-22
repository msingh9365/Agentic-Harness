"""
Part 3 of NOTES 27: two cheap TEST-TIME baselines on the final one-chunk models M1 (flatten head) and M3 (attention head, balanced padding), corrected tokenizer (Stage I weights), seeds 0-9.   (OURS; no retraining)

    python -m baseline.gs_variants --jobs m1 m3 --variants plain dedupe_exact dedupe_name multiwin --out out [--search /kaggle/input]

Edit sets (prepend only; the sampler, the EVAL pool and the ranking of Stage J): unedited, random_{20,50,100}_prepend, lgbm_50_prepend.
Variants:
  plain         the Stage J scoring path (first 512 tokens), only to reproduce the stored April logits (assert <= 2e-3) and to give the plain edited scores of the same call;
  dedupe_exact  AFTER the padding is added, every run of consecutive identical calls (identical cleaned token sequence = same API, arguments, return value) is collapsed to ONE call, then tokenised (first 512 tokens);
  dedupe_name   the same with "same call" = same API-name id (arguments ignored);
  multiwin      every window of 512 tokens of the whole edited report (stride 512; windows [0:512], [512:1024], ...; the last one zero-padded like the training padding), at most 64 windows; the report logit is the
                maximum window logit. The logit of the first window of the unedited report is checked against the stored April logit (assert <= 2e-3).
Saved: scores (float32 [n_sets, n_test] per seed), total token count after the variant, calls removed (dedupe), number of windows and the arg-max window (multiwin), first-window logit (multiwin).
Edited reports exist in memory only. No threshold, no April label is used here.
"""
import argparse
import json
import os
import time

import numpy as np

from baseline import callstore as CS, common as C, make_pad, padtest
from baseline import gs_attack as GA
from baseline import twolevel_attack as TA

SETS = [("unedited", "none", 0, None), ("random_20_prepend", "random", 20, "prepend"), ("random_50_prepend", "random", 50, "prepend"),
        ("random_100_prepend", "random", 100, "prepend"), ("lgbm_50_prepend", "lgbm", 50, "prepend")]
CUT, MAXWIN = 512, 64


def call_keys(store, rows, kind, cache):
    """per-call key array of the original report r (int64): exact = hash of the token sequence (verified below), name = API-name id"""
    out = {}
    for r in rows:
        if r in cache:
            out[r] = cache[r]
            continue
        n, s0 = store.n_calls(r), int(store.rep_seg[r])
        if kind == "name":
            k = store.seg_name[s0 + 1:s0 + 1 + n].astype(np.int64)
        else:
            k = np.array([hash(store.seg(s0 + 1 + i).tobytes()) for i in range(n)], dtype=np.int64)
            if n > 1:                                                                        # a hash collision would collapse two different calls: verify every adjacent pair with equal keys
                for i in np.where(k[1:] == k[:-1])[0]:
                    if not np.array_equal(store.seg(s0 + 1 + int(i)), store.seg(s0 + 2 + int(i))):
                        k[i + 1] ^= 0x5555
        cache[r] = out[r] = k
    return out


def added_calls(store, ntr, t, spec, pool, pool_n, ranking, ranked):
    """(token arrays, name ids) of the k calls prepended to April row t (in prepend order); [] for the unedited set and for a report without calls (left unedited, as Stage J)"""
    name, kind, k, mode = spec
    n = store.n_calls(ntr + t)
    if kind == "none" or (kind == "random" and n == 0):
        return [], []
    if kind == "random":
        plan = make_pad.plan_test_row(t, k, mode, n, pool_n)
        pairs = [(int(pool[pr]), int(c)) for pr, c in plan["draws"]]
    else:
        pairs = ranked[spec[0]]
    return [store.call(r, c) for r, c in pairs], [store.name(r, c) for r, c in pairs]


def ranked_pairs(store, ranking, spec):
    if spec[1] != "lgbm":
        return None
    rep_call = {int(i): v for i, v in ranking["rep_call"].items()}
    return [(int(rep_call[int(nm)][0]), int(rep_call[int(nm)][1])) for nm in ranking[f"rank_lgbm"][:spec[2]]]


def dedupe_row(store, r, added, added_names, kind, keys):
    """first CUT tokens and total token count of the report r (prepend `added`) after collapsing consecutive repeats; returns (tokens, total, calls removed)"""
    n, s0, off = store.n_calls(r), int(store.rep_seg[r]), store.seg_off
    if kind == "name":
        ak = np.asarray(added_names, dtype=np.int64)
    else:
        ak = np.array([hash(a.tobytes()) for a in added], dtype=np.int64)
    seq = np.concatenate([ak, keys])
    keep = np.ones(len(seq), dtype=bool)
    if len(seq) > 1:
        keep[1:] = seq[1:] != seq[:-1]
    if kind != "name" and len(added):                                                       # exact: verify equal-hash neighbours that involve an added call
        full = list(added) + [None] * n
        for i in np.where(~keep[1:len(added) + 1])[0] + 1:
            a = full[i] if i < len(added) else None
            b = full[i - 1] if i - 1 < len(added) else None
            a = store.seg(s0 + 1 + i - len(added)) if a is None else a
            b = store.seg(s0 + 1 + i - 1 - len(added)) if b is None else b
            if not np.array_equal(a, b):
                keep[i] = True
    lens = np.concatenate([[len(a) for a in added], np.diff(off[s0 + 1:s0 + n + 2])]).astype(np.int64)
    head, tail = store.head(r), store.tail(r)
    total = int(len(head) + len(tail) + lens[keep].sum())
    out = np.zeros(CUT, dtype=np.uint16)
    out[:min(CUT, len(head))] = head[:CUT]
    pos = min(CUT, len(head))
    for i in np.where(keep)[0]:
        if pos >= CUT:
            break
        seg = added[i] if i < len(added) else store.seg(s0 + 1 + i - len(added))
        m = min(len(seg), CUT - pos)
        out[pos:pos + m] = seg[:m]
        pos += m
    if pos < CUT:
        m = min(len(tail), CUT - pos)
        out[pos:pos + m] = tail[:m]
    return out, total, int((~keep).sum())


def full_tokens(store, r, added):
    head = store.head(r)
    return np.concatenate([head] + [np.asarray(a) for a in added] + [store.report_tokens(r)[len(head):]]) if len(added) else store.report_tokens(r)


def run_job(a, family):
    store, y_test, ntr, ranking, pool, pool_n = GA.inputs(a)
    n_test = len(y_test) if not a.limit_test else a.limit_test
    scorers = {s: GA.load_scorer(family, s, a.search, a.device) for s in a.seeds}
    ranked = {sp[0]: ranked_pairs(store, ranking, sp) for sp in SETS}
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    chk = {}
    for variant in a.variants:
        res = {f"seed{s}": np.zeros((len(SETS), n_test), dtype=np.float32) for s in a.seeds}
        tot = np.zeros((len(SETS), n_test), dtype=np.int64)
        removed = np.zeros((len(SETS), n_test), dtype=np.int32)
        nwin = np.zeros((len(SETS), n_test), dtype=np.int32)
        argwin = np.zeros((len(SETS), n_test), dtype=np.int32)
        first = {f"seed{s}": np.zeros((len(SETS), n_test), dtype=np.float32) for s in a.seeds}
        cache = {}
        for j, spec in enumerate(SETS):
            if variant == "plain":
                tok, tt = TA.build_set(store, ntr, len(y_test), pool, pool_n, ranking, spec, CUT)
                tok, tt = tok[:n_test], tt[:n_test]
                tot[j] = tt
                for s in a.seeds:
                    res[f"seed{s}"][j] = scorers[s](tok, tt)
            elif variant.startswith("dedupe"):
                kind = variant.split("_")[1]
                keys = call_keys(store, [ntr + t for t in range(n_test)], kind, cache)
                tok = np.zeros((n_test, CUT), dtype=np.uint16)
                for t in range(n_test):
                    add, add_nm = added_calls(store, ntr, t, spec, pool, pool_n, ranking, ranked)
                    tok[t], tot[j, t], removed[j, t] = dedupe_row(store, ntr + t, add, add_nm, kind, keys[ntr + t])
                ptok, ptot = TA.build_set(store, ntr, len(y_test), pool, pool_n, ranking, spec, CUT)                  # automatic check: a report without a collapsed call is the plain edited report
                same = removed[j] == 0
                assert np.array_equal(tok[same], ptok[:n_test][same]) and np.array_equal(tot[j][same], ptot[:n_test][same]), f"{variant} {spec[0]}: reports without a removed call differ from the plain edit"
                chk[f"{variant}_{spec[0]}_unchanged_rows"] = int(same.sum())
                for s in a.seeds:
                    res[f"seed{s}"][j] = scorers[s](tok, tot[j])
            else:                                                                           # multiwin
                for c0 in range(0, n_test, a.chunk):
                    rows = range(c0, min(c0 + a.chunk, n_test))
                    wins, owner, firstw = [], [], []
                    for t in rows:
                        add, _ = added_calls(store, ntr, t, spec, pool, pool_n, ranking, ranked)
                        ft = full_tokens(store, ntr + t, add)
                        tot[j, t] = len(ft)
                        nw = min(MAXWIN, max(1, -(-len(ft) // CUT)))
                        nwin[j, t] = nw
                        buf = np.zeros(nw * CUT, dtype=np.uint16)
                        m = min(len(ft), nw * CUT)
                        buf[:m] = ft[:m]
                        wins.append(buf.reshape(nw, CUT))
                        owner += [t - c0] * nw
                        firstw.append(len(owner) - nw)
                    W = np.concatenate(wins)
                    owner, firstw = np.asarray(owner), np.asarray(firstw)
                    if c0 == 0:                                                                      # automatic check: the first window of every edited report is the plain edited report (first 512 tokens)
                        ptok_all, _ = TA.build_set(store, ntr, len(y_test), pool, pool_n, ranking, spec, CUT)
                    assert np.array_equal(W[firstw], ptok_all[c0:c0 + len(firstw)]), f"multiwin {spec[0]}: first window differs from the plain edited report"
                    for s in a.seeds:
                        z = scorers[s](W, np.full(len(W), CUT))
                        mx = np.maximum.reduceat(z, firstw)
                        res[f"seed{s}"][j, c0:c0 + len(firstw)] = mx
                        first[f"seed{s}"][j, c0:c0 + len(firstw)] = z[firstw]
                        if s == a.seeds[0]:
                            for q in range(len(firstw)):
                                lo = firstw[q]
                                argwin[j, c0 + q] = int(np.argmax(z[lo:lo + nwin[j, c0 + q]]))
            if j == 0 and variant in ("plain", "multiwin") and not a.limit_test:
                src = res if variant == "plain" else first
                for s in a.seeds:
                    chk[f"{variant}_seed{s}"] = GA.check_unedited(family, s, src[f"seed{s}"][0], a.search, log=lambda m: print(m, flush=True))
            print(f"[{family} {variant}] set {j} {spec[0]} done for {len(a.seeds)} seeds ({time.time() - t0:.0f}s)", flush=True)
        np.savez_compressed(os.path.join(a.out, f"scores_{family}_{variant}.npz"), names=np.array([s[0] for s in SETS]), tot=tot, removed=removed, nwin=nwin, argwin=argwin,
                            **res, **{f"first_{k}": v for k, v in first.items()} if variant == "multiwin" else {})
    json.dump(chk, open(os.path.join(a.out, f"checks_{family}.json"), "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", nargs="+", default=["m1", "m3"], choices=["m1", "m3"])
    ap.add_argument("--variants", nargs="+", default=["plain", "dedupe_exact", "dedupe_name", "multiwin"])
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--out", required=True)
    ap.add_argument("--store", default="all.npz")
    ap.add_argument("--ranking", default="ranking_gs.json")
    ap.add_argument("--split-dir", default="split")
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--search", default=os.environ.get("NEBULA_INPUT", "/kaggle/input"))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--limit-test", type=int, default=0, help="smoke test only: the first N April reports")
    a = ap.parse_args()
    for f in a.jobs:
        run_job(a, f)


if __name__ == "__main__":
    main()
