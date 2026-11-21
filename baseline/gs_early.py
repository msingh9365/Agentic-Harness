"""
Stage D, Step 2 of NOTES 22, part 1: the per-seed early-stopping epoch, chosen from the VALIDATION logits only.   (OURS)

    python -m baseline.gs_early --runs <Stage D outputs: gsd_v2pe/ gsd_attbal/> --out results/groupsplit/stage_d

Rule (fixed in NOTES 22 before any Stage D computation): per seed, the epoch with the highest validation pAUC@1e-2 among all epochs of that run (v2-PE 1-4, ATT+bal 1-6); ties -> the earlier epoch.
This script lists and opens only `*_val_logits.npy` files; it never opens a `*_test_logits.npy` (the April logits of every epoch are in the same folder but stay unopened until `early_stop_selection.json`
has been written and committed). It also checks that the Stage D runs reproduce Stage C on the VALIDATION logits of the chosen epoch (--stage-c).
"""
import argparse
import json
import os

import numpy as np

from baseline import common as C, groupsplit as G

SEEDS = list(range(10))
MODELS = [("v2pe", "gsd_v2pe", "gsf_v2pe", 4, 1), ("attbal", "gsd_attbal", "gsf_attbal", 6, 3)]       # name, Stage D tag, Stage C tag, epochs, Stage C chosen epoch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--stage-c", default=None, help="Stage C outputs (gsf_*), for the reproduction check on validation logits")
    ap.add_argument("--out", default="results/groupsplit/stage_d")
    a = ap.parse_args()
    _, vidx = G.val_slice()
    fam = G.january_table()["train"]["family"][vidx]
    yv = (~np.isin(fam, ["clean", "windows_syswow64"])).astype(int)
    assert int(yv.sum()) == 5557 and len(yv) == 8718
    sel, L = {}, ["### Step 2, part 1: early-stopping epoch per seed (validation pAUC@1e-2 only; ties -> earlier epoch)", ""]
    for name, tag, ctag, ne, chosen in MODELS:
        pa = np.zeros((len(SEEDS), ne))
        for s in SEEDS:
            for e in range(1, ne + 1):
                pa[s, e - 1] = C.pauc(yv, np.load(os.path.join(a.runs, tag, f"seed{s}_epoch{e}_val_logits.npy")).astype(np.float64).reshape(-1))
        best = (np.argmax(pa, axis=1) + 1).tolist()
        rep = None
        if a.stage_c:
            d = [np.abs(np.load(os.path.join(a.runs, tag, f"seed{s}_epoch{chosen}_val_logits.npy")).astype(np.float64) - np.load(os.path.join(a.stage_c, ctag, f"seed{s}_epoch{chosen}_val_logits.npy")).astype(np.float64)).max() for s in SEEDS]
            rep = {"max_abs_logit_difference_per_seed": [float(x) for x in d], "identical_seeds": int(sum(x == 0 for x in d))}
        sel[name] = {"tag": tag, "epochs": ne, "best_epoch_per_seed": best, "val_pauc_per_seed_epoch": pa.tolist(), "val_pauc_at_best_mean": float(np.mean([pa[s, best[s] - 1] for s in SEEDS])),
                     "val_pauc_at_stage_c_epoch_mean": float(pa[:, chosen - 1].mean()), "reproduction_vs_stage_c_val_logits": rep}
        L += [f"- **{name}** (epochs 1-{ne}): best epoch per seed {best}; mean validation pAUC@1e-2 at the per-seed best epoch {sel[name]['val_pauc_at_best_mean']:.4f} (selection-biased, validation only) against {sel[name]['val_pauc_at_stage_c_epoch_mean']:.4f} at the Stage C epoch {chosen}"
              + (f"; Stage C reproduction on validation logits of epoch {chosen}: {rep['identical_seeds']}/10 seeds identical, largest logit difference {max(rep['max_abs_logit_difference_per_seed']):.2e}" if rep else "")]
    os.makedirs(a.out, exist_ok=True)
    json.dump(sel, open(os.path.join(a.out, "early_stop_selection.json"), "w"), indent=1)
    open(os.path.join(a.out, "early_stop_selection.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
