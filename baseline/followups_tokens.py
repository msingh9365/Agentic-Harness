"""
NOTES 26 item 1b (CPU, stored data only): how many BPE tokens a padding call costs, how many random padding calls push the original report out of a model's window, and how many April benign reports sit above the 1e-3 threshold.   (OURS)

    python -m baseline.followups_tokens --store <all.npz of the corrected tokenizer> --labels <labels.npz> --logits results/groupsplit/stage_fgh/stage_i/logits_fixed_models.npz --out results/groupsplit/stage_fgh/followups

 1. Tokens per padding call in the EVAL pool (the 3,161 benign reports of the group-split validation slice with >= 1 call): over all calls of the pool (reference) and under the sampler of the random-padding attacks (a uniform pool report, then a uniform
    call in it = weight 1 / (n_pool_reports x n_calls of its report) per call; exact weighted quantiles). Median, quartiles, mean.
 2. Per model the number of random padding calls that must be PREPENDED so that the first token of the original report (the first token after the report head, i.e. the first malicious token) lies at position >= the model's window: 512 for the one-chunk models
    (M1, M3), 4,096 for the two-level models (M2, M4); over the 9,399 April malware reports with >= 1 call; calls drawn with the same sampler (vectorised, own stream numpy seed 0, up to 4,000 calls; reports that never reach the window are counted as censored).
 3. The April benign reports above the 1e-3 (and 1e-2) threshold of every model and seed: n_benign, the rank floor(fpr n), the number strictly above the threshold (min / median / max over the 10 seeds).
"""
import argparse
import json
import os

import numpy as np

from baseline import callstore as CS, groupsplit as G

NTR = 75298
WINDOW = {"M1": 512, "M2": 4096, "M3": 512, "M4": 4096}
NAME = {"M1": "M1 Nebula", "M2": "M2 two-level", "M3": "M3 ATT+bal", "M4": "M4 ATT+bal-2L"}


def wquantile(x, w, qs):
    o = np.argsort(x)
    x, w = x[o], w[o]
    c = np.cumsum(w) / w.sum()
    return [float(x[min(np.searchsorted(c, q), len(x) - 1)]) for q in qs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--logits", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--kmax", type=int, default=4000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    store = CS.CallStore.load(a.store)
    lab = np.load(a.labels)
    y_all, y_test = lab["y_train"].astype(int), lab["y_test"].astype(int)
    trn, val = G.val_slice()
    pool = np.array([int(r) for r in val if y_all[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
    assert len(pool) == 3161, len(pool)
    off, seg = store.seg_off, store.rep_seg
    lens, rep_of, n_pool = [], [], np.array([store.n_calls(int(r)) for r in pool], dtype=np.int64)
    pool_off = np.concatenate([[0], np.cumsum(n_pool)])
    for i, r in enumerate(pool):
        s0, n = int(seg[r]), int(n_pool[i])
        lens.append(off[s0 + 2:s0 + n + 2] - off[s0 + 1:s0 + n + 1])              # token counts of the n call pieces of report r
        rep_of.append(np.full(n, i))
    lens, rep_of = np.concatenate(lens).astype(np.int64), np.concatenate(rep_of)
    qs = (0.25, 0.5, 0.75)
    flat = {"calls": int(len(lens)), "q25_median_q75": [float(v) for v in np.percentile(lens, [25, 50, 75])], "mean": float(lens.mean()), "min": int(lens.min()), "max": int(lens.max())}
    w = 1.0 / (len(pool) * n_pool[rep_of])
    samp = {"q25_median_q75": wquantile(lens, w, qs), "mean": float((lens * w).sum() / w.sum())}
    # 2. calls needed to push the first token of the original report out of the window
    mal = np.array([t for t in range(len(y_test)) if y_test[t] == 1 and store.n_calls(NTR + t) > 0], dtype=np.int64)
    head = np.array([int(off[int(seg[NTR + t]) + 1] - off[int(seg[NTR + t])]) for t in mal], dtype=np.int64)
    rng = np.random.default_rng(0)
    need = {512: [], 4096: []}
    for c0 in range(0, len(mal), 400):
        hh = head[c0:c0 + 400]
        pr = rng.integers(len(pool), size=(len(hh), a.kmax))
        cc = (rng.random((len(hh), a.kmax)) * n_pool[pr]).astype(np.int64)
        tok = lens[pool_off[pr] + cc]
        cum = np.cumsum(tok, 1) + hh[:, None]
        for W in need:
            reached = cum >= W
            k = np.where(reached.any(1), reached.argmax(1) + 1, a.kmax + 1)
            k = np.where(hh >= W, 0, k)
            need[W].append(k)
    need = {W: np.concatenate(v) for W, v in need.items()}
    win = {}
    for W, k in need.items():
        ok = k <= a.kmax
        win[str(W)] = {"reports": int(len(k)), "censored_above_kmax": int((~ok).sum()), "q25_median_q75": [float(v) for v in np.percentile(k[ok], [25, 50, 75])], "mean": float(k[ok].mean()), "share_head_alone_beyond_window": float((head >= W).mean())}
    head_stats = {"head_tokens_q25_median_q75": [float(v) for v in np.percentile(head, [25, 50, 75])], "malware_reports": int(len(mal))}
    # 3. April benign above the thresholds
    z = np.load(a.logits)
    ben = y_test == 0
    nb = int(ben.sum())
    counts = {}
    for i, m in enumerate(("M1", "M2", "M3", "M4"), 1):
        Z = z[f"f{i}_test"].astype(np.float64)
        counts[m] = {}
        for f in (0.001, 0.01):
            k = int(np.floor(f * nb))
            c = []
            for s in range(Z.shape[0]):
                zb = np.sort(Z[s][ben])[::-1]
                c.append(int((zb > zb[k]).sum()))
            counts[m][str(f)] = {"n_benign": nb, "rank_k": k, "benign_strictly_above": [int(min(c)), float(np.median(c)), int(max(c))]}
    out = {"tokenizer": "bpe50k_fix (store given by --store)", "eval_pool_reports": int(len(pool)), "tokens_per_call_all_pool_calls": flat, "tokens_per_call_attack_sampler": samp, "report_head_tokens": head_stats, "calls_to_push_original_out_of_window": win, "april_benign_above_threshold": counts}
    json.dump(out, open(os.path.join(a.out, "tokens_per_call.json"), "w"), indent=1)
    f2 = lambda v: f"{v[1]:g} (IQR {v[0]:g} to {v[2]:g})"
    L = ["### Item 1b: tokens per padding call, calls needed to leave the window, April benign reports above the 1e-3 threshold (corrected tokenizer `bpe50k_fix`)", "",
         f"**BPE tokens per padding call (EVAL pool = {len(pool)} benign group-split validation reports, {flat['calls']:,} calls).** Under the attack sampler (uniform pool report, then uniform call): median {f2(samp['q25_median_q75'])}, mean {samp['mean']:.1f}. Over all pool calls (reference): median {f2(flat['q25_median_q75'])}, mean {flat['mean']:.1f}, min {flat['min']}, max {flat['max']}.", "",
         f"**Report head** (tokens before the first call; the first token of the original report comes right after it): median {f2(head_stats['head_tokens_q25_median_q75'])} over {len(mal):,} April malware reports with a call.", "",
         "**Random padding calls to prepend so that the first token of the original report lies at position >= the window (median and IQR over the April malware reports; the draws are those of the attack sampler)**", "",
         "| model | window (tokens) | calls to push the original report out (median, IQR) | mean | censored (> 4,000 calls) |", "|---|---|---|---|---|"]
    for m in ("M1", "M2", "M3", "M4"):
        r = win[str(WINDOW[m])]
        L.append(f"| {NAME[m]} | {WINDOW[m]:,} | {f2(r['q25_median_q75'])} | {r['mean']:.1f} | {r['censored_above_kmax']} |")
    L += ["", f"**April benign reports above the threshold** (n_benign = {nb:,}; the threshold is the benign logit at rank floor(fpr x n), a report is flagged if strictly above it; min / median / max over the 10 seeds)", "", "| model | fpr 1e-3: rank | benign flagged | fpr 1e-2: rank | benign flagged |", "|---|---|---|---|---|"]
    for m in ("M1", "M2", "M3", "M4"):
        c3, c2 = counts[m]["0.001"], counts[m]["0.01"]
        L.append(f"| {NAME[m]} | {c3['rank_k']} | {c3['benign_strictly_above'][1]:g} ({c3['benign_strictly_above'][0]} to {c3['benign_strictly_above'][2]}) | {c2['rank_k']} | {c2['benign_strictly_above'][1]:g} ({c2['benign_strictly_above'][0]} to {c2['benign_strictly_above'][2]}) |")
    open(os.path.join(a.out, "tokens_per_call.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
