"""
Attacks on ATT+bal-2L (A), its control B and, for the comparison on the same edits, ATT+bal and v2-PE (NOTES 19.6).   (OURS)

    python -m baseline.twolevel_attack --mode scores --plan --jobs a2l b2l attbal v2_pe --out out [--search /kaggle/input]
    python -m baseline.twolevel_attack --mode wb --plan --jobs a2l:0 a2l:1 ... --out out

Edited reports exist in memory only: every edit is built from the call-token store of the ORIGINAL reports (baseline/callstore.py) in this process and scored at once; the saved files hold SCORES
(logits) and call-list lengths only, never tokens or reports.

scores  per family, all 10 seeds, every edit set on ALL 17,402 April reports (malware and benign, so the padded-benign FPR comes with it):
        random padding with EVAL-pool calls (make_pad.plan_test_row, stream 6000: k = 5, 20, 50 are the edits of REPORT 5.10), k in {5, 20, 50, 100, 200} x {prepend, insert};
        surrogate-chosen padding (ranking.json, representative calls of ranks 1..k, as baseline/attack_run.py): {lgbm, v2pe} x k in {20, 50, 100} x {prepend, insert}.
        Output scores_<family>.npz: seed<s> = float32 [n_sets, 17,402]; names; tot = total token count of every edited report [n_sets, 17,402].
        A and B read the first 4,096 tokens (8 chunks); ATT+bal and v2-PE read the first 512.
wb      white-box greedy attack for one (family, seed): 500 random April malware (numpy seed 31), step j: 200 random EVAL-pool calls (numpy seed 41 + j, the same for every model and report), the one that
        lowers the model's own score of the report most is prepended in front of the calls already chosen, up to 50 steps; a report at or below the 1% threshold stops. Steps 1-20 are the attack of
        REPORT 5.11 (baseline/attack_run.py), step for step. Padded benign: the call list chosen for malware report i after k steps (k = 5, 10, 20, 50; the final list if it stopped earlier) is prepended to
        the benign April report ben[i] (numpy seed 32, the same for every model) and scored.
        Output wb_<family>_seed<s>.npz: raw, best = score after every step [51, 500]; t1, t01 = thresholds; sel; ben_ids; ben_k<k> = scores of the padded benign [500]; n_picked [500].
Thresholds: the benign logit at rank floor(0.01 n) and floor(0.001 n) of the model's unedited April benign scores; flagged = above.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

from baseline import callstore as CS, common as C, make_pad, padtest

FAMILIES = {"a2l": "2l", "b2l": "2l", "a2r2": "2l", "attbal": "one", "v2_pe": "one"}      # a2r2 = A2 of round 2 (NOTES 20)
CUT_2L, CUT_1 = 4096, 512
RANDOM_KS, SURR_KS, SURR, MODES = (5, 20, 50, 100, 200), (20, 50, 100), ("lgbm", "v2pe"), ("prepend", "insert")
N_WB, WB_SEED, WB_STEPS, WB_CAND, WB_CAND_SEED, WB_BEN_SEED, WB_BEN_K = 500, 31, 50, 200, 41, 32, (5, 10, 20, 50)
OLD_RANDOM = [("insert", 5), ("insert", 20), ("insert", 50), ("prepend", 5), ("prepend", 20), ("prepend", 50)]       # edit sets 1..6 of results/review/attack/a3pad_<family>.npz (REPORT 5.10)


def set_list():
    """[(name, kind, k, mode)]; set 0 = unedited."""
    out = [("unedited", "none", 0, None)]
    out += [(f"random_{k}_{m}", "random", k, m) for m in MODES for k in RANDOM_KS]
    out += [(f"{s}_{k}_{m}", s, k, m) for s in SURR for m in MODES for k in SURR_KS]
    return out


def cut_of(family):
    return CUT_2L if FAMILIES[family] == "2l" else CUT_1


# ----------------------------------------------------------------------------- inputs
def inputs(a):
    """store, April labels, first April row ntr, ranking, EVAL pool (benign reports of the validation slice with >= 1 call), pool call counts."""
    from baseline import attack_run as AR
    store, y_test, ntr, ranking, pool = AR.inputs(a)
    return store, y_test, ntr, ranking, pool, np.array([store.n_calls(int(r)) for r in pool], dtype=np.int64)


def build_set(store, ntr, n_test, pool, pool_n, ranking, spec, cut, rep_arrays=None):
    """tokens uint16 [n_test, cut] and total token counts int32 [n_test] of one edit set, in memory. spec = (name, kind, k, mode)."""
    name, kind, k, m = spec
    tok = np.zeros((n_test, cut), dtype=np.uint16)
    tot = np.zeros(n_test, dtype=np.int32)
    if kind in SURR:
        rep_call = {int(i): v for i, v in ranking["rep_call"].items()}
        arr = [store.call(rep_call[int(nm)][0], rep_call[int(nm)][1]) for nm in ranking[f"rank_{kind}"][:k]]
    for t in range(n_test):
        r = ntr + t
        n = store.n_calls(r)
        if kind == "none" or (kind == "random" and n == 0):                       # a report without calls is left unedited (as in REPORT 5.10)
            tok[t], tot[t] = CS.build_fast(store, r, [], None, cut=cut)
        elif kind == "random":
            plan = make_pad.plan_test_row(t, k, m, n, pool_n)                    # keyed by the April row index t, as in make_pad.make_april
            added = [store.call(int(pool[pr]), int(c)) for pr, c in plan["draws"]]
            tok[t], tot[t] = CS.build_fast(store, r, added, plan["gaps"] if m == "insert" else None, cut=cut)
        else:
            gaps = np.sort(np.random.default_rng([8000, int(r), k, 0]).integers(0, n + 1, k)) if m == "insert" else None
            tok[t], tot[t] = CS.build_fast(store, r, arr, gaps, cut=cut)
    return tok, tot


# ----------------------------------------------------------------------------- models
def find_weights(family, seed, search):
    if family in ("a2l", "b2l", "a2r2"):
        for dp, dn, fn in os.walk(search):
            if os.path.basename(dp) == family and f"seed{seed}.pt" in fn:
                return os.path.join(dp, f"seed{seed}.pt")
        raise FileNotFoundError(f"weights of {family} seed {seed} not found under {search}")
    return padtest.find_weights(family, seed, None, search)


def load_scorer(family, seed, search, device, vocab_size=50001):
    """score(tok uint16 [n, cut], tot int [n]) -> float32 logits [n]."""
    import torch
    path = find_weights(family, seed, search)
    if FAMILIES[family] == "2l":
        from baseline import twolevel as TL
        m = TL.make_model(vocab_size, seed, "scratch")
        m.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
        m = m.to(device).eval()
        return lambda tok, tot: TL.predict(m, tok, np.asarray(tot), device)
    m = padtest.load_model(family, path, device)
    return lambda tok, tot: padtest.score(m, np.asarray(tok)[None], device)[0]


# ----------------------------------------------------------------------------- mode scores
def run_scores(a):
    store, y_test, ntr, ranking, pool, pool_n = inputs(a)
    cut, specs, n_test = cut_of(a.family), set_list(), len(y_test)
    scorers = {s: load_scorer(a.family, s, a.search, a.device) for s in a.seeds}
    res = {f"seed{s}": np.zeros((len(specs), n_test), dtype=np.float32) for s in a.seeds}
    tots = np.zeros((len(specs), n_test), dtype=np.int32)
    t0 = time.time()
    for j, spec in enumerate(specs):
        tok, tot = build_set(store, ntr, n_test, pool, pool_n, ranking, spec, cut)
        tots[j] = tot
        for s in a.seeds:
            res[f"seed{s}"][j] = scorers[s](tok, tot)
            if j == 0:
                check_unedited(a.family, s, res[f"seed{s}"][0], log=lambda m: print(m, flush=True))
        print(f"[{a.family}] set {j} {spec[0]} scored for {len(a.seeds)} seeds ({time.time() - t0:.0f}s)", flush=True)
        del tok
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(os.path.join(a.out, f"scores_{a.family}.npz"), names=np.array([s[0] for s in specs]), tot=tots, **res)
    check_scores(a, res, specs)


def reference_unedited(family, seed):
    """April logits of the same model from the earlier run (A and B: the training run's; ATT+bal and v2-PE: row 0 of a3pad_<family>.npz), or None if the file is not there."""
    try:
        ref_dir = C.find_dir_with("ranking.json")
    except Exception:
        return None
    p = os.path.join(ref_dir, "logits", f"{family}_seed{seed}.npy") if FAMILIES[family] == "2l" else os.path.join(ref_dir, "ref", f"a3pad_{family}.npz")
    if not os.path.exists(p):
        return None
    return np.load(p).astype(np.float64) if FAMILIES[family] == "2l" else np.load(p)[f"seed{seed}"][0].astype(np.float64)


def check_unedited(family, seed, z0, log=print):
    """Fail fast: the unedited scores of this scoring path must equal the earlier run's April logits (tolerance 2e-3: different batch composition)."""
    ref = reference_unedited(family, seed)
    if ref is None:
        log(f"[{family} seed {seed}] no reference logits found: unedited check skipped")
        return None
    d = float(np.abs(ref - np.asarray(z0, dtype=np.float64)).max())
    assert d < 2e-3, f"{family} seed {seed}: unedited scores differ from the earlier run's April logits by {d}"
    log(f"[{family} seed {seed}] unedited scores = earlier April logits (max difference {d:.2e})")
    return d


def check_scores(a, res, specs):
    """ATT+bal and v2-PE on the REPORT 5.10 random edits (k = 5, 20, 50) must equal a3pad_<family>.npz (same edits, same model). Prints, writes checks_<family>.json and asserts."""
    names = [s[0] for s in specs]
    out = {}
    if FAMILIES[a.family] == "one":
        try:
            p = os.path.join(C.find_dir_with("ranking.json"), "ref", f"a3pad_{a.family}.npz")
        except Exception:
            p = ""
        if os.path.exists(p):
            for s in a.seeds:
                old = np.load(p)[f"seed{s}"]
                dm = max(float(np.abs(old[1 + i] - res[f"seed{s}"][names.index(f"random_{k}_{m}")]).max()) for i, (m, k) in enumerate(OLD_RANDOM))
                out[f"seed{s}_random_5_20_50_vs_a3pad"] = dm
                assert dm < 2e-3, f"{a.family} seed {s}: random-edit scores differ from a3pad by {dm}"
    print(f"[{a.family}] reference checks of the edits: {json.dumps(out)}", flush=True)
    json.dump(out, open(os.path.join(a.out, f"checks_{a.family}.json"), "w"), indent=1)


# ----------------------------------------------------------------------------- mode wb
def greedy(store, ntr, y_test, pool, scorer, cut, n_wb=N_WB, steps=WB_STEPS, n_cand=WB_CAND, group=40, log=print, label="", check=None):
    """The white-box greedy attack (see the module doc). `scorer(tok, tot)` -> logits. Returns the dict that is saved, and the picked call lists (as arrays) for the padded-benign scoring."""
    n_test = len(y_test)
    tok0 = np.zeros((n_test, cut), dtype=np.uint16)
    tot0 = np.zeros(n_test, dtype=np.int32)
    for t in range(n_test):
        tok0[t], tot0[t] = CS.build_fast(store, ntr + t, [], None, cut=cut)
    z0 = scorer(tok0, tot0)
    del tok0
    if check:
        check(z0)
    t1, t01 = padtest.thresholds(z0, y_test, 0.01), padtest.thresholds(z0, y_test, 0.001)
    mal = np.where(y_test == 1)[0]
    sel = np.sort(np.random.default_rng(WB_SEED).choice(mal, n_wb, replace=False))
    flat_r = np.concatenate([np.full(store.n_calls(int(r)), int(r), dtype=np.int64) for r in pool])
    flat_i = np.concatenate([np.arange(store.n_calls(int(r)), dtype=np.int64) for r in pool])
    cur = z0[sel].astype(np.float64)
    raw, best = [cur.copy()], [cur.copy()]
    picked = [[] for _ in sel]                                          # call arrays in the order of picking (the list prepended = reversed)
    n_picked = np.zeros(len(sel), dtype=np.int64)
    active = cur > t1
    t0 = time.time()
    for step in range(steps):
        cand = np.random.default_rng(WB_CAND_SEED + step).choice(len(flat_r), n_cand, replace=False)
        cand_calls = [store.call(int(flat_r[c]), int(flat_i[c])) for c in cand]
        idx = np.where(active)[0]
        new = cur.copy()
        for g0 in range(0, len(idx), group):
            gi = idx[g0:g0 + group]
            toks = np.zeros((len(gi) * n_cand, cut), dtype=np.uint16)
            tots = np.zeros(len(gi) * n_cand, dtype=np.int32)
            for a_, i in enumerate(gi):
                chosen = picked[i][::-1]                                # [c_j, ..., c_1]: the newest call is first
                for c_ in range(n_cand):
                    toks[a_ * n_cand + c_], tots[a_ * n_cand + c_] = CS.build_fast(store, ntr + int(sel[i]), [cand_calls[c_]] + chosen, None, cut=cut)
            z = scorer(toks, tots).reshape(len(gi), n_cand)
            pick = z.argmin(1)
            for a_, i in enumerate(gi):
                picked[i].append(cand_calls[pick[a_]])
                n_picked[i] += 1
                new[i] = z[a_, pick[a_]]
            del toks
        raw.append(new.copy())
        cur = new
        best.append(np.minimum(best[-1], cur))
        active = active & (best[-1] > t1)
        log(f"[{label}] step {step + 1}: active {int(active.sum())}, flagged@1% {float((best[-1] > t1).mean()):.3f}, @0.1% {float((best[-1] > t01).mean()):.3f} ({time.time() - t0:.0f}s)")
    out = {"raw": np.array(raw, dtype=np.float32), "best": np.array(best, dtype=np.float32), "t1": t1, "t01": t01, "sel": sel, "n_picked": n_picked}
    # padded benign: the list chosen for malware report i after k steps, prepended to one random April benign report
    ben = np.where(y_test == 0)[0]
    ben_ids = np.random.default_rng(WB_BEN_SEED).choice(ben, len(sel), replace=False)
    out["ben_ids"] = ben_ids
    for k in WB_BEN_K:
        if k > steps:
            continue
        toks = np.zeros((len(sel), cut), dtype=np.uint16)
        tots = np.zeros(len(sel), dtype=np.int32)
        for i in range(len(sel)):
            lst = picked[i][:k][::-1]
            toks[i], tots[i] = CS.build_fast(store, ntr + int(ben_ids[i]), lst, None, cut=cut)
        out[f"ben_k{k}"] = scorer(toks, tots).astype(np.float32)
    return out


def run_wb(a):
    store, y_test, ntr, ranking, pool, pool_n = inputs(a)
    cut = cut_of(a.family)
    scorer = load_scorer(a.family, a.seed, a.search, a.device)
    out = greedy(store, ntr, y_test, pool, scorer, cut, n_wb=a.n_wb, steps=a.steps, label=f"{a.family} seed {a.seed}", log=lambda s: print(s, flush=True),
                 check=lambda z0: check_unedited(a.family, a.seed, z0, log=lambda m: print(m, flush=True)))
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(os.path.join(a.out, f"wb_{a.family}_seed{a.seed}.npz"), **out)


# ----------------------------------------------------------------------------- orchestration
def orchestrate(a):
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    jobs, running, failed = list(a.jobs), {}, []
    while jobs or running:
        for g in range(n_gpu):
            if g not in running and jobs:
                j = jobs.pop(0).split(":")
                cmd = [sys.executable, "-m", "baseline.twolevel_attack", "--mode", a.mode, "--family", j[0], "--out", a.out, "--device", a.device, "--store", a.store, "--ranking", a.ranking]
                cmd += ["--seeds"] + [str(x) for x in a.seeds] if a.mode == "scores" else ["--seed", j[1], "--steps", str(a.steps), "--n-wb", str(a.n_wb)]
                if a.search:
                    cmd += ["--search", a.search]
                done = os.path.join(a.out, f"scores_{j[0]}.npz" if a.mode == "scores" else f"wb_{j[0]}_seed{j[1]}.npz")
                if os.path.exists(done) and not a.force:
                    print(f"{':'.join(j)}: already done", flush=True)
                    continue
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g))), ":".join(j))
                print(f"GPU {g}: started {':'.join(j)}", flush=True)
        for g, (p, name) in list(running.items()):
            if p.poll() is not None:
                print(f"GPU {g}: {name} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(name)
                del running[g]
        time.sleep(3)
    if failed:
        raise SystemExit(f"failed: {failed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["scores", "wb"], required=True)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--jobs", nargs="*", default=[])
    ap.add_argument("--family", default=None, choices=list(FAMILIES))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--steps", type=int, default=WB_STEPS)
    ap.add_argument("--n-wb", type=int, default=N_WB)
    ap.add_argument("--out", required=True)
    ap.add_argument("--store", default="all.npz")
    ap.add_argument("--ranking", default="ranking.json")
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--search", default="/kaggle/input")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--released", action="store_true")
    ap.add_argument("--store-released", default="all_released.npz")
    a = ap.parse_args()
    if a.plan:
        return orchestrate(a)
    C.setup_nebula(require_patched=True)
    return run_wb(a) if a.mode == "wb" else run_scores(a)


if __name__ == "__main__":
    main()
