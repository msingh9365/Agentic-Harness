#!/usr/bin/env python
"""
Round 4, step 3 (ATT): what does the attention pooling look at, before and after 20 benign calls are prepended?

    python scripts/pooling_v4/attention_tokens.py --src-v4 <Kaggle output of the round-4 runs>

20 random April malware reports (numpy Generator seed 11, reports with at least one API call). Each report is also prepended with 20
random calls of the EVAL pool (the same edit as "prepend 20" of the padding test), re-tokenised, first 512 tokens. For ATT (attention
pooling) and ATT+aug, seed 0: the 10 tokens with the highest attention weight (weights of the pooling over the real tokens, summing to 1)
before and after the edit, the share of the attention that falls on the prepended tokens (their number = the growth of the token sequence,
capped at 512), the share a mean pooling would give them, and the logit before and after (flagged = above the 1% FPR threshold of that model).
The same shares for all five seeds. Edits and attention are computed in memory; only the aggregate numbers and the token lists are written.
Writes results/pooling_v4/attention_tokens.md and attention_tokens.json.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v4_common as V  # noqa: E402
from v4_common import C, _W, _init, build_variant, V2_TO_INTERNAL, pad_edit  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-v4", default="/Users/manish/Code/mtp/pooling_v4_output")
    ap.add_argument("--epochs-new", type=int, default=2)
    ap.add_argument("--n", type=int, default=20)
    a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get("NTHREADS", os.cpu_count() or 4)))
    test, y = V.april()
    ev, _ = V.pools()
    _init(V.NEBULA)
    pool = [list(_W["reps"].get(int(r)).get("apis") or []) for r in ev]
    vocab = json.load(open(os.path.join(V.NEBULA, "nebula", "objects", "bpe_50000_vocab.json")))
    inv = {i: t for t, i in vocab.items()}
    rng = np.random.default_rng(11)
    cand = [i for i in np.flatnonzero(y == 1) if _W["reps"].get(int(test.row.values[i])).get("apis")]
    pick = sorted(int(i) for i in rng.choice(cand, a.n, replace=False))
    toks, edit_toks, n_pad = [], [], []
    for i in pick:
        row = int(test.row.values[i]); rep = _W["reps"].get(row); apis = list(rep["apis"])
        t0 = _W["nb"].ids(rep)
        r2 = dict(rep); r2["apis"] = pad_edit(apis, row, 20, "prepend", pool); t1 = _W["nb"].ids(r2)
        toks.append(t0[:512]); edit_toks.append(t1[:512]); n_pad.append(min(512, len(t1) - len(t0)))
    to_x = lambda L: torch.from_numpy(np.stack([np.pad(np.asarray(t, dtype=np.int64), (0, 512 - len(t))) for t in L]))
    X0, X1 = to_x(toks), to_x(edit_toks)
    out, md = {}, ["# What the attention pooling looks at (round 4)\n",
                   "20 random April malware reports, each prepended with 20 random calls of the EVAL pool (the \"prepend 20\" edit of the padding test; in memory only). "
                   "Attention weight = weight of a token in the pooled vector (they sum to 1 over the real tokens). \"Share on the prepended tokens\": attention weight "
                   "that falls on the first n tokens after the edit, n = growth of the token sequence (at most 512); \"share with mean pooling\": n / number of real tokens.\n"]
    for disp, fam in (("ATT (attention)", "ATT"), ("ATT+aug", "ATTaug"), ("ATT+bal", "ATTbal")):
        shares, seed_rows = [], []
        for s in range(5):
            run = f"{fam}_all_s{s}"
            m = build_variant(V.NEBULA, V2_TO_INTERNAL[fam]).eval()
            m.load_state_dict(torch.load(os.path.join(a.src_v4, "ckpt", run, "final.pt"), map_location="cpu", weights_only=True))
            z0 = np.load(os.path.join(a.src_v4, "scores", f"{run}_epochs.npz"))["april"][a.epochs_new - 1]
            thr = C.thr_from(y, z0, 0.01)
            with torch.no_grad():
                w0, w1 = m.attention_weights(X0).numpy(), m.attention_weights(X1).numpy()
                l0, l1 = m(X0).squeeze(-1).numpy(), m(X1).squeeze(-1).numpy()
            real1 = (X1 != 0).sum(1).numpy()
            on_pad = np.array([w1[k, :n_pad[k]].sum() for k in range(len(pick))])
            uniform = np.array([n_pad[k] / real1[k] for k in range(len(pick))])
            seed_rows.append({"seed": s, "mean share on prepended tokens": f"{100 * on_pad.mean():.1f}%", "mean share with mean pooling": f"{100 * uniform.mean():.1f}%",
                              "flagged before": f"{int((l0 > thr).sum())}/{len(pick)}", "flagged after": f"{int((l1 > thr).sum())}/{len(pick)}",
                              "mean logit before → after": f"{l0.mean():.2f} → {l1.mean():.2f}"})
            if s == 0:
                rows = []
                for k, i in enumerate(pick):
                    top = lambda w, X: ", ".join(f"{inv[int(X[k, j])]}@{j} ({w[k, j]:.3f})" for j in np.argsort(-w[k])[:10])
                    rows.append({"report (row)": int(test.row.values[i]), "real tokens before → after": f"{int((X0[k] != 0).sum())} → {int(real1[k])}",
                                 "prepended tokens": int(n_pad[k]), "logit before → after": f"{l0[k]:.2f} → {l1[k]:.2f}",
                                 "share on prepended": f"{100 * on_pad[k]:.0f}% (mean pooling {100 * uniform[k]:.0f}%)",
                                 "top-10 tokens before: token@position (weight)": top(w0, X0), "top-10 tokens after": top(w1, X1)})
                detail = pd.DataFrame(rows)
        out[disp] = {"per_seed": seed_rows}
        md += [f"\n## {disp}: shares over the five seeds (20 reports each)\n", C.md_table(pd.DataFrame(seed_rows)),
               f"\n### {disp}, seed 0, per report\n", C.md_table(detail)]
        out[disp]["seed0"] = detail.to_dict("records")
    json.dump(out, open(f"{V.OUT}/attention_tokens.json", "w"), indent=1, default=str)
    open(f"{V.OUT}/attention_tokens.md", "w").write("\n".join(md))
    print("\n".join(md[:8]))


if __name__ == "__main__":
    main()
