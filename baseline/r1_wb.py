"""
ITEM R1 (NOTES 30.3), white-box greedy attack on the windowed model (one seed): the greedy attack of baseline/twolevel_attack.py (500 April malware reports = the `sel` of Stage J, 200 candidate calls per step, prepend,
50 steps; padded-benign scoring as Stage J) with the WINDOWED scorer (all windows of every candidate report, max logit; cut 32,768 tokens).   (OURS)

    python -m baseline.r1_wb --seed 0 --search <dir with r1/seed<k>.pt, r1/seed<k>_april.npy> --out out
Check: the unedited scores equal the stored April logits (tolerance 2e-3). Output wb_r1_seed<k>.npz (the format of Stage J).
"""
import argparse
import json
import os

import numpy as np

from baseline import callstore as CS, common as C, gs_attack as GA, pe
from baseline import twolevel_attack as TA
from baseline.r1 import CUT, report_max, score_windows, windows_from


def main():
    import torch
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--search", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--store", default="all.npz")
    ap.add_argument("--ranking", default="ranking_gs.json")
    ap.add_argument("--split-dir", default="split")
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--steps", type=int, default=TA.WB_STEPS)
    ap.add_argument("--n-wb", type=int, default=TA.N_WB)
    ap.add_argument("--group", type=int, default=8)
    a = ap.parse_args()
    C.setup_nebula(require_patched=True)
    store, y_test, ntr, ranking, pool, pool_n = GA.inputs(a)
    tokens = a.tokens or C.find_dir_with("all.npz")
    vocab = json.load(open(os.path.join(tokens, "variants", "bpe50k_fix", "vocab.json")))
    GA.find_file("r1", f"seed{a.seed}.pt", a.search)
    m = pe.build_chunks(len(vocab), pe_mode="paper", pool_mode="attn")
    m.load_state_dict(torch.load(GA.find_file("r1", f"seed{a.seed}.pt", a.search), map_location="cpu", weights_only=True))
    m = m.to(a.device).eval()

    def scorer(tok, tot):
        Ws, counts = [], []
        for i in range(len(tok)):
            w = windows_from(tok[i], int(tot[i]))
            Ws.append(w)
            counts.append(len(w))
        W, counts = np.concatenate(Ws), np.asarray(counts)
        return report_max(score_windows(m, W, a.device, bs=2048), counts)
    out = TA.greedy(store, ntr, y_test, pool, scorer, CUT, n_wb=a.n_wb, steps=a.steps, group=a.group, label=f"r1 seed {a.seed}", log=lambda s: print(s, flush=True),
                    check=lambda z0: GA.check_unedited("r1", a.seed, z0, a.search, log=lambda mm: print(mm, flush=True)))
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(os.path.join(a.out, f"wb_r1_seed{a.seed}.npz"), **out)


if __name__ == "__main__":
    main()
