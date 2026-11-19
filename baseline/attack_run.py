"""
Attacks the models were not trained on, scoring side (NOTES 15.3).   (OURS)

    python -m baseline.attack_run --mode 3a --plan --jobs v2_pe:v2_pe att:attbal ... --out out [--models-root ...] [--search /kaggle/input]
    python -m baseline.attack_run --mode 3b --plan --jobs v2_pe:v2_pe:0 ...                                              # family:kind:seed
    python -m baseline.attack_run --mode pad --plan --jobs v2_pe:v2_pe ...                                              # random padding test, all April reports, in memory

Edited reports exist in memory only: every edit is built from the call-token store of the ORIGINAL reports (baseline/callstore.py) in this process and scored at once; the saved
files hold SCORES (logits) only, never tokens or reports.

3a  surrogate-chosen padding. Edit sets (12 + the unedited one as set 0): {LightGBM surrogate, v2-PE seed-0 surrogate} x k in {5, 20, 50} x {insert, prepend}: the k API-name representative
    calls of ranks 1..k of the ranking (baseline/attack_rank.py) are added to EVERY April report (17,402); insert: k sorted random gaps (default_rng([8000, row, k, 0])), call of rank j into gap j;
    prepend: rank 1 first. Output a3_<family>.npz: seed<s> = float32 logits [13, 17,402]; a3_meta_<store>.npz: total token count of every edited report int32 [13, 17,402].
3b  white-box greedy: 500 random April malware (numpy seed 31), prepend up to 20 calls; step j: 200 random EVAL-pool calls (numpy seed 41 + j; the same for every model and report), the one that
    lowers the model's own score of the report most is prepended (in front of the calls already chosen). A report whose score is at or below the 1% threshold stops (it is evaded at both
    thresholds). Output a3b_<family>_seed<s>.npz: raw = score after every step [21, 500], best = running minimum, t1 / t01 = thresholds (1% / 0.1% FPR of the model's unedited April benign scores).
Thresholds: the benign logit at rank floor(0.01 n) and floor(0.001 n) in descending order of the model's own scores of all unedited April benign reports; flagged = score above it.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

from baseline import callstore as CS, common as C, gap, padtest

SURR = ("lgbm", "v2pe")
KS = (5, 20, 50)
MODES = ("insert", "prepend")
SETS = [(s, k, m) for s in SURR for k in KS for m in MODES]            # set index j + 1 (set 0 = unedited)
N_WB, WB_SEED, WB_STEPS, WB_CAND, WB_CAND_SEED = 500, 31, 20, 200, 41


PAD_SETS = [(k, m) for m in MODES for k in KS]                              # the random padding test (REPORT 5.10 procedure, all April reports): 6 edits + the unedited set


def set_name(j):
    return "unedited" if j == 0 else "_".join(map(str, SETS[j - 1]))


def pad_set_name(j):
    return "unedited" if j == 0 else "random_" + "_".join(map(str, PAD_SETS[j - 1]))


def inputs(a):
    """store of the models' tokenizer, April labels, ranking, EVAL pool."""
    store_path = a.store_released if a.released else a.store
    store_path = store_path if os.path.exists(store_path) else os.path.join(C.find_dir_with(os.path.basename(store_path)), os.path.basename(store_path))
    store = CS.CallStore.load(store_path)
    tokens = a.tokens or C.find_dir_with("labels.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    y_test = lab["y_test"]
    ntr = int(len(lab["y_train"]))
    assert len(store) == ntr + len(y_test), (len(store), ntr, len(y_test))
    rank_path = a.ranking if os.path.exists(a.ranking) else os.path.join(C.find_dir_with(os.path.basename(a.ranking)), os.path.basename(a.ranking))
    ranking = json.load(open(rank_path))
    trn, val = gap.val_slice(lab["ym_train"])
    pool = np.array([int(r) for r in val if lab["y_train"][r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
    assert len(pool) == ranking["eval_pool_n"], (len(pool), ranking["eval_pool_n"])
    return store, y_test, ntr, ranking, pool


def thresholds(z, y):
    return padtest.thresholds(z, y, 0.01), padtest.thresholds(z, y, 0.001)


def build_sets(store, ntr, n_test, ranking):
    """tokens uint16 [13, n_test, 512] and totals int32 [13, n_test] (in memory; nothing is written)."""
    tok = np.zeros((1 + len(SETS), n_test, CS.SEQ), dtype=np.uint16)
    tot = np.zeros((1 + len(SETS), n_test), dtype=np.int32)
    reps = {s: [ranking[f"rank_{s}"][i] for i in range(max(KS))] for s in SURR}
    rep_call = {int(k): v for k, v in ranking["rep_call"].items()}
    arrs = {s: [store.call(rep_call[int(nm)][0], rep_call[int(nm)][1]) for nm in reps[s]] for s in SURR}
    for t in range(n_test):
        r = ntr + t
        n = store.n_calls(r)
        tok[0, t], tot[0, t] = CS.build_fast(store, r, [], None)
        for j, (s, k, m) in enumerate(SETS, start=1):
            added = arrs[s][:k]
            gaps = np.sort(np.random.default_rng([8000, int(r), k, 0]).integers(0, n + 1, k)) if m == "insert" else None
            tok[j, t], tot[j, t] = CS.build_fast(store, r, added, gaps)
    return tok, tot


def build_pad_sets(store, ntr, n_test, pool):
    """tokens uint16 [7, n_test, 512] and totals [7, n_test] of the random padding test, in memory: for every April report the plan of make_pad.plan_test_row (default_rng([6000, row, k, mode]); every
    added call = a random call of a random EVAL-pool report), k in {5, 20, 50}, insert and prepend; set 0 = unedited."""
    from baseline import make_pad
    pool_n = np.array([store.n_calls(int(r)) for r in pool], dtype=np.int64)
    tok = np.zeros((1 + len(PAD_SETS), n_test, CS.SEQ), dtype=np.uint16)
    tot = np.zeros((1 + len(PAD_SETS), n_test), dtype=np.int32)
    for t in range(n_test):
        r = ntr + t
        n = store.n_calls(r)
        tok[0, t], tot[0, t] = CS.build_fast(store, r, [], None)
        for j, (k, m) in enumerate(PAD_SETS, start=1):
            if n == 0:                                             # a report without calls is left unedited (as in REPORT 5.10)
                tok[j, t], tot[j, t] = tok[0, t], tot[0, t]
                continue
            plan = make_pad.plan_test_row(t, k, m, n, pool_n)      # the plan is keyed by the April row index t, as in make_pad.make_april
            added = [store.call(int(pool[pr]), int(c)) for pr, c in plan["draws"]]
            tok[j, t], tot[j, t] = CS.build_fast(store, r, added, plan["gaps"] if m == "insert" else None)
    return tok, tot


def run_3a(a):
    store, y_test, ntr, ranking, pool = inputs(a)
    kind = a.kind
    t0 = time.time()
    pad = a.mode == "pad"
    tok, tot = build_pad_sets(store, ntr, len(y_test), pool) if pad else build_sets(store, ntr, len(y_test), ranking)
    print(f"[{a.family}] {tok.shape[0]} edit sets x {len(y_test):,} reports built in memory ({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(a.out, exist_ok=True)
    pre = "a3pad" if pad else "a3"
    meta = os.path.join(a.out, f"{pre}_meta_{'released' if a.released else 'ours'}.npz")
    if not os.path.exists(meta):
        np.savez_compressed(meta, totals=tot, set_names=np.array([(pad_set_name if pad else set_name)(j) for j in range(tok.shape[0])]))
    res = {}
    for s in a.seeds:
        m = padtest.load_model(kind, padtest.find_weights(kind, s, a.models_root, a.search), a.device)
        res[f"seed{s}"] = padtest.score(m, tok, a.device)
        z = res[f"seed{s}"]
        t1, t01 = thresholds(z[0], y_test)
        print(f"[{a.family}] seed {s} scored ({time.time() - t0:.0f}s); unedited malware TPR@1% {float((z[0][y_test == 1] > t1).mean()):.3f}", flush=True)
        del m
    np.savez_compressed(os.path.join(a.out, f"{pre}_{a.family}.npz"), **res)


def run_3b(a):
    import torch
    store, y_test, ntr, ranking, pool = inputs(a)
    m = padtest.load_model(a.kind, padtest.find_weights(a.kind, a.seed, a.models_root, a.search), a.device)
    n_test = len(y_test)
    tok0 = np.stack([CS.build_fast(store, ntr + t, [], None)[0] for t in range(n_test)])
    z0 = padtest.score(m, tok0[None], a.device)[0]
    t1, t01 = thresholds(z0, y_test)
    mal = np.where(y_test == 1)[0]
    sel = np.sort(np.random.default_rng(WB_SEED).choice(mal, N_WB, replace=False))
    flat_r = np.concatenate([np.full(store.n_calls(int(r)), int(r), dtype=np.int64) for r in pool])
    flat_i = np.concatenate([np.arange(store.n_calls(int(r)), dtype=np.int64) for r in pool])
    cur = z0[sel].astype(np.float64)
    raw, best = [cur.copy()], [cur.copy()]
    chosen = [[] for _ in sel]
    active = cur > t1
    t0 = time.time()
    for step in range(WB_STEPS):
        cand = np.random.default_rng(WB_CAND_SEED + step).choice(len(flat_r), WB_CAND, replace=False)
        idx = np.where(active)[0]
        new = cur.copy()
        if len(idx):
            toks = np.zeros((len(idx), WB_CAND, CS.SEQ), dtype=np.uint16)
            for a_, i in enumerate(idx):
                for c_, ci in enumerate(cand):
                    added = [store.call(int(flat_r[ci]), int(flat_i[ci]))] + chosen[i]
                    toks[a_, c_] = CS.build_fast(store, ntr + int(sel[i]), added, None)[0]
            z = padtest.score(m, toks.reshape(1, -1, CS.SEQ), a.device)[0].reshape(len(idx), WB_CAND)
            pick = z.argmin(1)
            for a_, i in enumerate(idx):
                ci = cand[pick[a_]]
                chosen[i] = [store.call(int(flat_r[ci]), int(flat_i[ci]))] + chosen[i]
                new[i] = z[a_, pick[a_]]
            del toks
        raw.append(new.copy())
        cur = new
        best.append(np.minimum(best[-1], cur))
        active = active & (best[-1] > t1)
        print(f"[{a.family} seed {a.seed}] step {step + 1}: active {int(active.sum())}, flagged@1% {float((best[-1] > t1).mean()):.3f}, @0.1% {float((best[-1] > t01).mean()):.3f} ({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(os.path.join(a.out, f"a3b_{a.family}_seed{a.seed}.npz"), raw=np.array(raw, dtype=np.float32), best=np.array(best, dtype=np.float32), t1=t1, t01=t01, sel=sel)


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
                j = jobs.pop(0)
                cmd = [sys.executable, "-m", "baseline.attack_run", "--mode", a.mode, "--family", j[0], "--kind", j[1], "--out", a.out, "--device", a.device, "--ranking", a.ranking, "--store", a.store,
                       "--store-released", a.store_released, "--seeds"] + [str(x) for x in a.seeds] + (["--released"] if j[1] == "released" else []) + (["--seed", j[2]] if a.mode == "3b" else []) + (["--smoke"] if a.smoke else [])
                if a.models_root:
                    cmd += ["--models-root", a.models_root]
                if a.search:
                    cmd += ["--search", a.search]
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
        raise SystemExit(f"attack scoring failed: {failed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["3a", "3b", "pad"], required=True)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--jobs", nargs="*", default=[])
    ap.add_argument("--family", default=None)
    ap.add_argument("--kind", default=None, choices=list(padtest.KINDS))
    ap.add_argument("--released", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--out", required=True)
    ap.add_argument("--store", default="all.npz")
    ap.add_argument("--store-released", default="all_released.npz")
    ap.add_argument("--ranking", default="ranking.json")
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--models-root", default=None)
    ap.add_argument("--search", default=None)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--smoke", action="store_true", help="smoke run: the white-box attack with 40 reports and 2 steps (the settings of the real run are the module constants)")
    a = ap.parse_args()
    global N_WB, WB_STEPS
    if a.smoke:
        N_WB, WB_STEPS = 40, 2
    if a.plan:
        return orchestrate(a)
    C.setup_nebula(require_patched=True)
    if a.kind == "released":
        a.released, a.seeds = True, [0]
    return run_3b(a) if a.mode == "3b" else run_3a(a)


if __name__ == "__main__":
    main()
