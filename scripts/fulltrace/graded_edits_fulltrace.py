#!/usr/bin/env python
"""
Item 5 (graded edits): the edits of results/robustness/graded_edits.md on model F (C over the whole report, up to 4,096 tokens),
next to A (J) and C (J) on 512 tokens and the released Nebula (512 tokens), seeds 0-4 of every model (F's five seeds).

    python scripts/fulltrace/graded_edits_fulltrace.py --src-f <fulltrace output> --work <cache folder> --full-data <fulltrace_stage>

Same edits as scripts/pooling_v2/graded_edits.py (same random seeds): insert k / prepend k (k = 1, 5, 20, 50) API calls, each a
copy of a call of the SAME report; here the edited report is tokenised up to 4,096 tokens instead of 512. Threshold: fixed at 1%
FPR on the unedited April scores of each model and seed. "Fits (4096)": the whole edited sequence is at most 4,096 tokens, so no
original call leaves F's window; "fits (512)": at most 512 tokens (the reports of results/robustness item 1, where F and C see
the same tokens). Group bootstrap (April hash_apis, 1,000 resamples, paired across models) of the change in malware TPR.
Reads the 512-token scores of A (J), C (J) and the released model from the cache of scripts/robustness/graded_edits_released.py.
Writes results/fulltrace/graded_edits.md and graded_edits.json.
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
from perturb_check import insert_calls, _init, _W  # noqa: E402
from graded_edits import prepend_calls  # noqa: E402

KS = [1, 5, 20, 50]
EDITS = [f"insert {k}" for k in KS] + [f"prepend {k}" for k in KS]
OUT = "results/fulltrace"


def _tok(row):
    nb, rep = _W["nb"], _W["reps"].get(int(row))
    apis = list(rep.get("apis") or [])
    out, lens = [], []
    for k in KS:
        r = dict(rep); r["apis"] = insert_calls(apis, row, k); t = nb.ids(r)
        out.append(np.asarray(t[:4096], dtype=np.uint16)); lens.append(len(t))
    for k in KS:
        r = dict(rep); r["apis"] = prepend_calls(apis, row, k); t = nb.ids(r)
        out.append(np.asarray(t[:4096], dtype=np.uint16)); lens.append(len(t))
    return int(row), out, lens


@torch.no_grad()
def score(model, toks, bs=64):
    """logits of a list of token arrays, sorted by length, padded per batch to a multiple of 64."""
    order = np.argsort([-len(t) for t in toks], kind="stable")
    out = np.zeros(len(toks))
    for i in range(0, len(toks), bs):
        sel = order[i:i + bs]
        L = max(64, int(-(-max(len(toks[j]) for j in sel) // 64) * 64))
        x = np.zeros((len(sel), L), dtype=np.int64)
        for r, j in enumerate(sel):
            x[r, :len(toks[j])] = toks[j]
        out[sel] = model(torch.from_numpy(x)).squeeze(-1).double().numpy()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-f", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--full-data", required=True)
    ap.add_argument("--nebula", default="../nebula")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--epochs-f", type=int, default=10)
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 4)
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    y = test.label.values
    N = len(test)
    t0 = time.time()
    cache = os.path.join(a.work, "fulltrace_edit_tokens.npz")
    if os.path.exists(cache):
        d = np.load(cache, allow_pickle=True); E, L = list(d["E"]), d["L"]
        flat = [np.split(d[f"t{j}"], d[f"o{j}"]) for j in range(8)]
    else:
        with Pool(a.workers, initializer=_init, initargs=(a.nebula,)) as pool:
            res = list(pool.imap(_tok, test.row.values, chunksize=32))
        assert [r[0] for r in res] == list(test.row.values)
        L = np.array([r[2] for r in res]).T
        flat = [[r[1][j] for r in res] for j in range(8)]
        arrs = {}
        for j in range(8):
            lens = np.array([len(t) for t in flat[j]])
            arrs[f"t{j}"] = np.concatenate(flat[j]); arrs[f"o{j}"] = np.cumsum(lens)[:-1]
        np.savez(cache, E=np.array(EDITS), L=L, **arrs)
    print(f"edited reports tokenised (4096 tokens) in {time.time() - t0:.0f}s", flush=True)
    # unedited full-length tokens of the April reports
    tf, of = np.load(os.path.join(a.full_data, "tokens_full.npy")), np.load(os.path.join(a.full_data, "offsets_full.npy"))
    plain = [tf[of[r]:of[r + 1]] for r in test.row.values]

    Z = {}                                                                # F: [9, N] per seed
    for s in range(5):
        run = f"F_all_s{s}"
        m = build_variant(a.nebula, V2_TO_INTERNAL["F"], maxlen=4096).eval()
        m.load_state_dict(torch.load(os.path.join(a.src_f, "ckpt", run, "final.pt"), map_location="cpu", weights_only=True))
        z0 = np.load(os.path.join(a.src_f, "scores", f"{run}_epochs.npz"))["april"][a.epochs_f - 1]
        if s == 0:
            chk = score(m, plain[:600])
            print("check: max |CPU logit - Kaggle logit| on 600 reports =", float(np.abs(chk - z0[:600]).max()), flush=True)
            assert np.abs(chk - z0[:600]).max() < 0.05
        Z[f"F_s{s}"] = np.stack([z0] + [score(m, flat[j]) for j in range(8)])
        print(run, f"{time.time() - t0:.0f}s", flush=True)
    z512 = np.load(os.path.join(a.work, "robustness_item1_logits.npz"))
    Z.update({k: z512[k] for k in z512.files if k == "released" or k.split("_s")[0] in ("A", "C") and int(k.split("_s")[1]) < 5})
    names = ["F (full trace)", "C (512 tokens)", "A (512 tokens)", "released Nebula"]
    keys = {"F (full trace)": [f"F_s{s}" for s in range(5)], "C (512 tokens)": [f"C_s{s}" for s in range(5)],
            "A (512 tokens)": [f"A_s{s}" for s in range(5)], "released Nebula": ["released"]}
    mal, ben = y == 1, y == 0
    per = {n: np.stack([Z[k] for k in keys[n]]) for n in names}           # [seeds, 9, N]
    flags = {}
    for n in names:
        thr = np.array([C.thr_from(y, per[n][i, 0], 0.01) for i in range(len(keys[n]))])
        flags[n] = (per[n] > thr[:, None, None]).mean(0)                  # [9, N]
    from sklearn.metrics import roc_auc_score
    auc = {n: np.array([[roc_auc_score(y, per[n][i, e]) for e in range(9)] for i in range(len(keys[n]))]).mean(0) for n in names}
    labels = ["original"] + EDITS
    fit4k, fit512 = L <= 4096, L <= 512
    rows_all = []
    for e, lab in enumerate(labels):
        r = {"edit": lab}
        for n in names: r[f"{n} AUC"] = f"{auc[n][e]:.4f}"
        for n in names: r[f"{n} TPR fixed (a)"] = f"{100 * flags[n][e][mal].mean():.1f}%"
        for n in names: r[f"{n} FPR fixed (a)"] = f"{100 * flags[n][e][ben].mean():.2f}%"
        rows_all.append(r)
    W = np.stack(list(C.group_weights_boot(test.hash_apis.values, 1000, 0)))
    wtpr = lambda fl, mask: (W @ (fl * (mask & mal))) / (W @ (mask & mal).astype(float))
    ci = lambda v: f"[{100 * np.percentile(v, 2.5):+.1f}, {100 * np.percentile(v, 97.5):+.1f}]"
    tabs = {}
    for tag, fits in (("all reports", None), ("fits in 4096 tokens", fit4k), ("fits in 512 tokens", fit512)):
        rows = []
        for e in range(1, 9):
            mask = np.ones(N, bool) if fits is None else fits[e - 1]
            r = {"edit": labels[e], "malware reports in the set": f"{int((mask & mal).sum()):,}"}
            ch = {}
            for n in names:
                ch[n] = wtpr(flags[n][e], mask) - wtpr(flags[n][0], mask)
                pt = flags[n][e][mask & mal].mean() - flags[n][0][mask & mal].mean()
                r[f"{n}: TPR change, points [group 95%]"] = f"{100 * pt:+.1f} {ci(ch[n])}"
            for x, z in (("F (full trace)", "C (512 tokens)"), ("F (full trace)", "A (512 tokens)"), ("F (full trace)", "released Nebula")):
                pt = (flags[x][e][mask & mal].mean() - flags[x][0][mask & mal].mean()) - (flags[z][e][mask & mal].mean() - flags[z][0][mask & mal].mean())
                r[f"{x.split(' ')[0]} − {z.split(' ')[0]}"] = f"{100 * pt:+.1f} {ci(ch[x] - ch[z])}"
            rows.append(r)
        tabs[tag] = pd.DataFrame(rows)
    json.dump({"labels": labels, "tpr": {n: [float(flags[n][e][mal].mean()) for e in range(9)] for n in names},
               "fpr": {n: [float(flags[n][e][ben].mean()) for e in range(9)] for n in names}, "auc": {n: auc[n].tolist() for n in names},
               "share_fit_4096": fit4k.mean(1).tolist(), "share_fit_512": fit512.mean(1).tolist()}, open(f"{OUT}/graded_edits.json", "w"), indent=1)
    md = ["# Graded edits on the full-trace model F\n",
          "Edits as in `results/robustness/graded_edits.md` (insert k / prepend k calls copied from the same report), but F reads up to 4,096 tokens of the edited "
          "report; the others read the first 512. Threshold fixed at 1% FPR on the unedited April scores of each model and seed. Mean over seeds 0-4 of every model "
          "(the released model has one score vector). Group-bootstrap intervals (April hash_apis).\n",
          "## Malware TPR and benign FPR at the fixed threshold, all April reports\n", C.md_table(pd.DataFrame(rows_all))]
    for tag, df in tabs.items():
        md += [f"\n## Change in malware TPR, {tag}\n", C.md_table(df)]
    open(f"{OUT}/graded_edits.md", "w").write("\n".join(md))
    print(C.md_table(pd.DataFrame(rows_all)))
    print(C.md_table(tabs["fits in 4096 tokens"]))


if __name__ == "__main__":
    main()
