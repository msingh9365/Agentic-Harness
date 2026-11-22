"""
Stage H of NOTES 23: attacks on the four final models M1 (v2-PE), M2 (two-level, no padding), M3 (ATT+bal), M4 (ATT+bal-2L), all trained on all of January with the old tokenizer, 10 seeds.   (OURS; reuses baseline/twolevel_attack.py)

    python -m baseline.gs_attack --mode scores --plan --jobs m1 m2 m3 m4 --out out [--search /kaggle/input]
    python -m baseline.gs_attack --mode wb --plan --jobs m2:0 m2:1 ... --out out

Differences to baseline/twolevel_attack.py (everything else, the edit builder, the greedy attack, the file formats, is that module's code):
  * the EVAL pool = the benign reports of the GROUP-SPLIT validation slice with >= 1 call (3,161; never used in training: the padding pool of training is the group-split training part);
  * the surrogate ranking is `ranking_gs.json` (LightGBM fitted on the group-split training part, representative calls from the EVAL pool); only the LightGBM surrogate is used;
  * families m1..m4 with their stored final weights (`<family>/seed<k>.pt` in the weights dataset) and the stored April logits (`<family>/seed<k>_april.npy`), which the unedited scores must reproduce (STOP otherwise).
Edited reports exist in memory only; the saved files hold scores and call-list lengths only.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

from baseline import callstore as CS, common as C, groupsplit as G, padtest
from baseline import twolevel_attack as TA

FAM = {"m1": ("one", "v2_pe"), "m2": ("2l", None), "m3": ("one", "attbal"), "m4": ("2l", None)}
for _i, _x in enumerate(sys.argv):                                           # NOTES 26: further one-chunk families, --extra-families name:kind ... (kind = padtest kind: v2_pe = flatten head, attbal = attention head)
    if _x == "--extra-families":
        for _spec in sys.argv[_i + 1:]:
            if _spec.startswith("--"):
                break
            _n, _k = _spec.split(":")
            FAM[_n] = ("one", _k)
TA.SURR = ("lgbm",)                                                       # only the LightGBM surrogate (NOTES 23)
TA.FAMILIES.update({k: v[0] for k, v in FAM.items()})


def find_file(family, name, search):
    for dp, dn, fn in os.walk(search):
        if os.path.basename(dp) == family and name in fn:
            return os.path.join(dp, name)
    raise FileNotFoundError(f"{family}/{name} not found under {search}")


def inputs(a):
    """store (old tokenizer), April labels, first April row, ranking (group split), EVAL pool (group-split validation benign), pool call counts."""
    sp = a.store if os.path.exists(a.store) else os.path.join(C.find_dir_with(os.path.basename(a.store)), os.path.basename(a.store))
    store = CS.CallStore.load(sp)
    tokens = a.tokens or C.find_dir_with("all.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    y_all, y_test = lab["y_train"], lab["y_test"]
    ntr = int(len(y_all))
    assert len(store) == ntr + len(y_test)
    ranking = json.load(open(a.ranking if os.path.exists(a.ranking) else os.path.join(C.find_dir_with(os.path.basename(a.ranking)), os.path.basename(a.ranking))))
    sd = a.split_dir if os.path.exists(os.path.join(a.split_dir, "split.npz")) else C.find_dir_with("split.npz")
    trn, val = G.val_slice(os.path.join(sd, "split.npz"), os.path.join(sd, "split_hash.json"))
    assert (len(trn), len(val)) == (66580, 8718)
    pool = np.array([int(r) for r in val if y_all[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
    assert len(pool) == ranking["eval_pool_n"] == 3161, (len(pool), ranking["eval_pool_n"])
    assert not (set(pool.tolist()) & set(trn.tolist()))
    return store, y_test, ntr, ranking, pool, np.array([store.n_calls(int(r)) for r in pool], dtype=np.int64)


def load_scorer(family, seed, search, device, vocab_size=50001):
    import torch
    path = find_file(family, f"seed{seed}.pt", search)
    if FAM[family][0] == "2l":
        from baseline import twolevel as TL
        m = TL.make_model(vocab_size, seed, "scratch")
        m.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
        m = m.to(device).eval()
        return lambda tok, tot: TL.predict(m, tok, np.asarray(tot), device)
    m = padtest.load_model(FAM[family][1], path, device)
    return lambda tok, tot: padtest.score(m, np.asarray(tok)[None], device)[0]


def check_unedited(family, seed, z0, search, log=print):
    """STOP (assert) unless the unedited scores of this scoring path equal the stored April logits of the final model (tolerance 2e-3: different batch composition)."""
    ref = np.load(find_file(family, f"seed{seed}_april.npy", search)).astype(np.float64).reshape(-1)
    d = float(np.abs(ref - np.asarray(z0, dtype=np.float64)).max())
    assert d < 2e-3, f"{family} seed {seed}: unedited scores differ from the stored April logits by {d}"
    log(f"[{family} seed {seed}] unedited scores = stored April logits (max difference {d:.2e})")
    return d


def run_scores(a):
    store, y_test, ntr, ranking, pool, pool_n = inputs(a)
    cut, specs, n_test = TA.cut_of(a.family), (TA.set_list()[:a.max_sets] if a.max_sets else TA.set_list()), len(y_test)
    scorers = {s: load_scorer(a.family, s, a.search, a.device) for s in a.seeds}
    res = {f"seed{s}": np.zeros((len(specs), n_test), dtype=np.float32) for s in a.seeds}
    tots = np.zeros((len(specs), n_test), dtype=np.int32)
    chk, t0 = {}, time.time()
    for j, spec in enumerate(specs):
        tok, tot = TA.build_set(store, ntr, n_test, pool, pool_n, ranking, spec, cut)
        tots[j] = tot
        for s in a.seeds:
            res[f"seed{s}"][j] = scorers[s](tok, tot)
            if j == 0:
                chk[f"seed{s}"] = check_unedited(a.family, s, res[f"seed{s}"][0], a.search, log=lambda m: print(m, flush=True))
        print(f"[{a.family}] set {j} {spec[0]} scored for {len(a.seeds)} seeds ({time.time() - t0:.0f}s)", flush=True)
        del tok
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(os.path.join(a.out, f"scores_{a.family}.npz"), names=np.array([s[0] for s in specs]), tot=tots, **res)
    json.dump(chk, open(os.path.join(a.out, f"checks_{a.family}.json"), "w"), indent=1)


def run_wb(a):
    store, y_test, ntr, ranking, pool, pool_n = inputs(a)
    scorer = load_scorer(a.family, a.seed, a.search, a.device)
    out = TA.greedy(store, ntr, y_test, pool, scorer, TA.cut_of(a.family), n_wb=a.n_wb, steps=a.steps, label=f"{a.family} seed {a.seed}", log=lambda s: print(s, flush=True),
                    check=lambda z0: check_unedited(a.family, a.seed, z0, a.search, log=lambda m: print(m, flush=True)))
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(os.path.join(a.out, f"wb_{a.family}_seed{a.seed}.npz"), **out)


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
                done = os.path.join(a.out, f"scores_{j[0]}.npz" if a.mode == "scores" else f"wb_{j[0]}_seed{j[1]}.npz")
                if os.path.exists(done) and not a.force:
                    print(f"{':'.join(j)}: already done", flush=True)
                    continue
                cmd = [sys.executable, "-m", "baseline.gs_attack", "--mode", a.mode, "--family", j[0], "--out", a.out, "--device", a.device, "--store", a.store, "--ranking", a.ranking, "--split-dir", a.split_dir, "--search", a.search] + (["--max-sets", str(a.max_sets)] if a.max_sets else [])
                cmd += (["--ks"] + [str(x) for x in a.ks] if a.ks else []) + (["--surr-ks"] + [str(x) for x in a.surr_ks] if a.surr_ks else []) + (["--no-surrogate"] if a.no_surrogate else [])
                cmd += (["--extra-families"] + a.extra_families if a.extra_families else [])
                cmd += (["--seeds"] + [str(x) for x in a.seeds]) if a.mode == "scores" else ["--seed", j[1], "--steps", str(a.steps), "--n-wb", str(a.n_wb)]
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g))), ":".join(j))
                print(f"GPU {g}: started {':'.join(j)}", flush=True)
        for g, (p, name) in list(running.items()):
            if p.poll() is not None:
                print(f"GPU {g}: {name} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(name)
                    for q, _ in running.values():                     # fail fast (NOTES 23 automatic check (a))
                        if q.poll() is None:
                            q.terminate()
                    raise SystemExit(f"failed: {failed}")
                del running[g]
        time.sleep(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["scores", "wb"], required=True)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--jobs", nargs="*", default=[])
    ap.add_argument("--family", default=None, choices=list(FAM))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--steps", type=int, default=TA.WB_STEPS)
    ap.add_argument("--n-wb", type=int, default=TA.N_WB)
    ap.add_argument("--out", required=True)
    ap.add_argument("--store", default="all.npz")
    ap.add_argument("--ranking", default="ranking_gs.json")
    ap.add_argument("--split-dir", default="split")
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--search", default=os.environ.get("NEBULA_INPUT", "/kaggle/input"))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--max-sets", type=int, default=0, help="smoke test only: the first N edit sets")
    ap.add_argument("--ks", type=int, nargs="*", default=None, help="NOTES 26: the random-padding sizes k of the edit sets (default of twolevel_attack: 5 20 50 100 200)")
    ap.add_argument("--no-surrogate", action="store_true", help="NOTES 26: no LightGBM-ranked edit sets")
    ap.add_argument("--surr-ks", type=int, nargs="*", default=None, help="the k of the LightGBM sets (default 20 50 100)")
    ap.add_argument("--extra-families", nargs="*", default=[], help="name:kind of further one-chunk families (kind v2_pe or attbal)")
    a = ap.parse_args()
    if a.ks:
        TA.RANDOM_KS = list(a.ks)
    if a.surr_ks:
        TA.SURR_KS = list(a.surr_ks)
    if a.no_surrogate:
        TA.SURR = ()
    if a.plan:
        return orchestrate(a)
    return run_scores(a) if a.mode == "scores" else run_wb(a)


if __name__ == "__main__":
    main()
