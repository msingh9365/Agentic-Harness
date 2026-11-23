"""
Order tests (NOTES_ORDER.md): shuffle test (Test 1) and shift / block-boundary test (Test 2) of the final corrected-tokenizer models M1..M4.   (CPU only, no training)

    python results/order_tests/order_tests.py score --model m1 --test 1 --work <dir with in/> --out results/order_tests [--seeds 0 1 ... ] [--threads 2]
    python results/order_tests/order_tests.py score --model m1 --test 2 ...
Edited reports exist in memory only; the saved files hold logits, call counts and exact shifts, never tokens.
Run from the repository root with PYTHONPATH=<repo root> and the authors' package installed (see README.md).
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from baseline import callstore as CS, groupsplit as G  # noqa: E402

KIND = {"m1": "v2_pe", "m3": "attbal"}            # one-chunk models (padtest kinds); m2, m4 are the two-level models
FOLDER = {"m1": "m1/m1", "m2": "m2/m2", "m3": "m3/m3", "m4": "m4/m4"}
WIN = {"m1": 512, "m3": 512, "m2": 4096, "m4": 4096}
TARGETS = [0, 8, 16, 24, 32, 40, 48, 56, 64]
CTRL_T, CTRL_N = 32, 9
VAR_ID = {"a": 1, "b": 2, "d": 4}


def stop(out, msg):
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "STOP.txt"), "w") as f:
        f.write(msg + "\n")
    raise SystemExit("STOP: " + msg)


# ----------------------------------------------------------------------------- data
class Data:
    def __init__(self, work):
        self.inp = os.path.join(work, "in", "inputs")
        self.store = CS.CallStore.load(os.path.join(self.inp, "all.npz"))
        lab = np.load(os.path.join(self.inp, "labels.npz"))
        self.y_all, self.y = lab["y_train"], lab["y_test"].astype(int)
        self.ntr, self.n = len(self.y_all), len(self.y)
        assert len(self.store) == self.ntr + self.n == 92700
        sd = os.path.join(work, "in", "gs")
        trn, val = G.val_slice(os.path.join(sd, "split.npz"), os.path.join(sd, "split_hash.json"))
        assert (len(trn), len(val)) == (66580, 8718)
        self.pool = np.array([int(r) for r in val if self.y_all[r] == 0 and self.store.n_calls(int(r)) > 0], dtype=np.int64)
        assert len(self.pool) == 3161 and not (set(self.pool.tolist()) & set(trn.tolist()))
        self.pool_n = np.array([self.store.n_calls(int(r)) for r in self.pool], dtype=np.int64)
        off, rs = self.store.seg_off, self.store.rep_seg
        self.head_len = np.zeros(self.n, dtype=np.int64)
        self.lens = []                                                  # token length of every call of April report i
        for i in range(self.n):
            r = self.ntr + i
            s0, n = int(rs[r]), self.store.n_calls(r)
            self.head_len[i] = off[s0 + 1] - off[s0]
            self.lens.append(np.diff(off[s0 + 1:s0 + n + 2]).astype(np.int64))
        self.total = np.array([len(self.store.report_tokens(self.ntr + i)) for i in range(self.n)], dtype=np.int64)
        self.n_calls = np.array([len(l) for l in self.lens], dtype=np.int64)

    def window_calls(self, i, W):
        """m = number of calls that lie completely inside the first W tokens."""
        cum = self.head_len[i] + np.cumsum(self.lens[i])
        return int(np.searchsorted(cum, W, side="right"))


def assemble(D, i, order, k, cut, pad=()):
    """First `cut` tokens (uint16) and the total token count of April report i built as: head, pad calls (arrays), the original calls in `order` (a list of call indices),
    then the original calls k.. contiguous, then the tail. `order` need not cover all calls (k = len(order) when it is the prefix block)."""
    st, r = D.store, D.ntr + i
    s0, n, off = int(st.rep_seg[r]), st.n_calls(r), st.seg_off
    out = np.zeros(cut, dtype=np.uint16)
    pos = 0

    def emit(arr):
        nonlocal pos
        m = min(len(arr), cut - pos)
        if m > 0:
            out[pos:pos + m] = arr[:m]
            pos += m
    emit(st.head(r))
    for a in pad:
        if pos >= cut:
            break
        emit(a)
    full = True
    for c in order:
        if pos >= cut:
            full = False
            break
        emit(st.call(r, int(c)))
    if full and pos < cut:
        emit(st.seg_tok[int(off[s0 + 1 + k]):int(off[s0 + 1 + n])][:cut - pos])
        emit(st.tail(r))
    return out, int(D.total[i] + sum(len(a) for a in pad))


# ----------------------------------------------------------------------------- Test 1 sets
def test1_sets(D, W):
    """tok[name] uint16 [N, W], tot[name] int64 [N]; info: m (window calls), changed[name] bool. Checks C2 in the loop."""
    names = ["clean", "a", "b", "c", "d"]
    tok = {nm: np.zeros((D.n, W), dtype=np.uint16) for nm in names}
    tot = {nm: np.zeros(D.n, dtype=np.int64) for nm in names}
    m_arr = np.zeros(D.n, dtype=np.int64)
    changed = {nm: np.zeros(D.n, dtype=bool) for nm in names}
    for i in range(D.n):
        n, m = int(D.n_calls[i]), D.window_calls(i, W)
        m_arr[i] = m
        base = list(range(m))
        cl, ct = assemble(D, i, base, m, W)
        tok["clean"][i], tot["clean"][i] = cl, ct
        S = int(D.lens[i][:m].sum())
        orders = {}
        if m >= 2:
            p = np.random.default_rng([8100, i, VAR_ID["a"]]).permutation(m)
            orders["a"] = [int(x) for x in p]
            rb = np.random.default_rng([8100, i, VAR_ID["b"]])
            ob = []
            for g in range(0, m, 5):
                grp = np.arange(g, min(g + 5, m))
                ob += [int(x) for x in rb.permutation(grp)]
            orders["b"] = ob
            orders["c"] = base[::-1]
        for nm in ("a", "b", "c"):
            if nm not in orders:
                tok[nm][i], tot[nm][i] = cl, ct
                continue
            o = orders[nm]
            v, vt = assemble(D, i, o, m, W)
            # C2: same calls, same token multiset, same total, identical tokens after the block
            hl = int(D.head_len[i])
            ok = sorted(o) == base and vt == ct and np.array_equal(np.sort(v), np.sort(cl)) and np.array_equal(v[hl + S:], cl[hl + S:]) and np.array_equal(v[:hl], cl[:hl])
            if not ok:
                return None, i, nm
            tok[nm][i], tot[nm][i] = v, vt
            changed[nm][i] = o != base
        # (d) full shuffle of all calls (reference; the window content changes, only the total count is checked)
        if n >= 2:
            pd_ = np.random.default_rng([8100, i, VAR_ID["d"]]).permutation(n)
            v, vt = assemble(D, i, [int(x) for x in pd_], n, W)
            if vt != ct:
                return None, i, "d"
            tok["d"][i], tot["d"][i] = v, vt
            changed["d"][i] = bool((pd_ != np.arange(n)).any())
        else:
            tok["d"][i], tot["d"][i] = cl, ct
    return dict(tok=tok, tot=tot, m=m_arr, changed=changed), None, None


# ----------------------------------------------------------------------------- Test 2 sets
def draw_call(D, rng, rem):
    """One padding call (token array) of length <= rem by the fixed rule: 50 uniform draws (report of the pool, then call of it); a call of length exactly rem if there is one, else the first with length <= rem; None if none."""
    pi = rng.integers(0, len(D.pool), 50)
    cj = (rng.random(50) * D.pool_n[pi]).astype(np.int64)
    cands = []
    for p, c in zip(pi, cj):
        a = D.store.call(int(D.pool[p]), int(c))
        cands.append(a)
    L = np.array([len(a) for a in cands])
    hit = np.where(L == rem)[0]
    if len(hit):
        return cands[int(hit[0])]
    ok = np.where((L <= rem) & (L > 0))[0]
    return cands[int(ok[0])] if len(ok) else None


def fill(D, rng, pad, target):
    """Extend the list `pad` with calls until its token length is as close as possible to `target` without exceeding it."""
    cur = int(sum(len(a) for a in pad))
    while cur < target:
        a = draw_call(D, rng, target - cur)
        if a is None:
            break
        pad.append(a)
        cur += len(a)
    return cur


def test2_sets(D, W, control=True):
    """tok [9(+9 control), N, W], tot, s_exact [9, N] (and s_ctrl [9, N])."""
    nS = len(TARGETS)
    nset = nS + (CTRL_N if control else 0)
    tok = np.zeros((nset, D.n, W), dtype=np.uint16)
    tot = np.zeros((nset, D.n), dtype=np.int64)
    s_exact = np.zeros((nset, D.n), dtype=np.int64)
    for i in range(D.n):
        n = int(D.n_calls[i])
        rng = np.random.default_rng([8200, i])
        pad = []
        for k, t in enumerate(TARGETS):
            s = fill(D, rng, pad, t)
            v, vt = assemble(D, i, [], 0, W, pad=pad)                    # head, padding, then calls 0.. contiguous
            assert s <= t and vt == D.total[i] + s, (i, t, s)
            tok[k, i], tot[k, i], s_exact[k, i] = v, vt, s
        if control:
            for j in range(CTRL_N):
                rj = np.random.default_rng([8300, i, j])
                padj = []
                s = fill(D, rj, padj, CTRL_T)
                v, vt = assemble(D, i, [], 0, W, pad=padj)
                assert s <= CTRL_T and vt == D.total[i] + s
                tok[nS + j, i], tot[nS + j, i], s_exact[nS + j, i] = v, vt, s
    return tok, tot, s_exact


# ----------------------------------------------------------------------------- models
def load_scorer(model, seed, work, threads):
    import torch
    torch.set_num_threads(threads)
    path = os.path.join(work, "in", FOLDER[model], f"seed{seed}.pt")
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if model in ("m1", "m3"):
        from baseline import padtest
        m = padtest.load_model(KIND[model], path, "cpu")
        return (lambda tok, tot: padtest.score(m, np.asarray(tok)[None], "cpu")[0]), sha
    from baseline import twolevel as TL
    m = TL.make_model(50001, seed, "scratch")
    m.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    m.eval()
    return (lambda tok, tot: TL.predict(m, tok, np.asarray(tot), "cpu")), sha


def stored_logits(model, seed, work):
    return np.load(os.path.join(work, "in", FOLDER[model], f"seed{seed}_april.npy")).astype(np.float64).reshape(-1)


def check_c1(model, seed, z, work, out, D, tag):
    ref = stored_logits(model, seed, work)
    d = float(np.abs(ref - z.astype(np.float64)).max())
    print(f"[C1 {tag}] {model} seed {seed}: max |rebuilt - stored April logit| = {d:.2e}", flush=True)
    if not d <= 1e-4:
        stop(out, f"C1 failed: {model} seed {seed} ({tag}) differs from the stored April logits by {d:.3e} > 1e-4")
    return d


def run_score(a):
    D = Data(a.work)
    W = WIN[a.model]
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    checks = {}
    if a.model in ("m1", "m3"):                                    # C1 token-exact against the x_test rows
        xt = np.load(os.path.join(D.inp, "variants", "bpe50k_fix", "x_test.npy"), mmap_mode="r")
        assert xt.shape[0] == D.n
    if a.test == 1:
        S, bad_i, bad_v = test1_sets(D, W)
        if S is None:
            stop(a.out, f"C2 failed at April row {bad_i}, variant {bad_v}")
        if a.model in ("m1", "m3"):
            nbad = int((np.asarray(xt)[:, :W] != S["tok"]["clean"]).any(axis=1).sum())
            if nbad:
                stop(a.out, f"C1 failed: {nbad} rebuilt clean reports differ from x_test")
            checks["clean_tokens_equal_x_test_rows"] = True
        print(f"sets built ({time.time() - t0:.0f}s); share of reports with m>=2: {(S['m'] >= 2).mean():.3f}", flush=True)
        names = ["clean", "a", "b", "c", "d"]
        Z = {nm: np.zeros((len(a.seeds), D.n), dtype=np.float32) for nm in names}
        sha = {}
        for si, s in enumerate(a.seeds):
            sc, sha[f"seed{s}"] = load_scorer(a.model, s, a.work, a.threads)
            for nm in names:
                Z[nm][si] = sc(S["tok"][nm], S["tot"][nm])
                if nm == "clean":
                    checks[f"seed{s}"] = check_c1(a.model, s, Z[nm][si], a.work, a.out, D, "clean")
            print(f"[test1 {a.model}] seed {s} scored ({time.time() - t0:.0f}s)", flush=True)
        np.savez_compressed(os.path.join(a.out, f"scores_test1_{a.model}.npz"), seeds=np.array(a.seeds), y=D.y, m=S["m"], n_calls=D.n_calls, total_tokens=D.total,
                            **{f"z_{nm}": Z[nm] for nm in names}, **{f"changed_{nm}": S["changed"][nm] for nm in names if nm != "clean"})
    else:
        ctrl = a.model in ("m1", "m3")
        tok, tot, s_exact = test2_sets(D, W, control=ctrl)
        nS = len(TARGETS)
        if not (s_exact[0] == 0).all():
            stop(a.out, "C3 failed: shift 0 has padding")
        if a.model in ("m1", "m3"):
            nbad = int((np.asarray(xt)[:, :W] != tok[0]).any(axis=1).sum())
            if nbad:
                stop(a.out, f"C1 failed: {nbad} reports of shift 0 differ from x_test")
            checks["shift0_tokens_equal_x_test_rows"] = True
        print(f"shift sets built ({time.time() - t0:.0f}s); exact s: mean per target {np.round(s_exact[:nS].mean(1), 2).tolist()}", flush=True)
        Z = np.zeros((len(a.seeds), tok.shape[0], D.n), dtype=np.float32)
        sha = {}
        for si, s in enumerate(a.seeds):
            sc, sha[f"seed{s}"] = load_scorer(a.model, s, a.work, a.threads)
            for k in range(tok.shape[0]):
                Z[si, k] = sc(tok[k], tot[k])
                if k == 0:
                    checks[f"seed{s}"] = check_c1(a.model, s, Z[si, 0], a.work, a.out, D, "shift0")
            print(f"[test2 {a.model}] seed {s} scored ({time.time() - t0:.0f}s)", flush=True)
        np.savez_compressed(os.path.join(a.out, f"scores_test2_{a.model}.npz"), seeds=np.array(a.seeds), y=D.y, targets=np.array(TARGETS), s_exact=s_exact.astype(np.int16),
                            z_shift=Z[:, :nS], z_ctrl=Z[:, nS:], n_calls=D.n_calls, total_tokens=D.total)
    cf = os.path.join(a.out, f"checks_{a.model}_test{a.test}.json")
    json.dump({"c1_max_abs_diff_vs_stored_april_logits": checks, "weights_sha256": sha, "seconds": round(time.time() - t0)}, open(cf, "w"), indent=1)
    print("done", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["score"])
    ap.add_argument("--model", required=True, choices=list(WIN))
    ap.add_argument("--test", type=int, required=True, choices=[1, 2])
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "order_tests"))
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args()
    run_score(a)


if __name__ == "__main__":
    main()
