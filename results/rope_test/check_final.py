"""
Automatic checks of NOTES_ROPE.md section 6 for the final runs of one variant, from the downloaded kernel output; stages weights and stored April logits as <work>/in/rope/<v>/seed<k>.pt, seed<k>_april.npy (local, not committed).
    python results/rope_test/check_final.py --out <kernel output dir> --tag rf_rope_blocks --family v1 --work /tmp/claude-0/work --write results/rope_test/final_v1
Checks: 10 seeds, split hash asserted, tokenizer bpe50k_fix, 75,298 training reports, padding pool of 21,507 benign reports (from the log), no collapsed seed (April AUC < 0.6 from the stored logits: the ONLY April number looked at here), SHA-256 of weights and logits.
"""
import argparse
import glob
import hashlib
import json
import os
import shutil

import numpy as np


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--family", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--write", required=True)
    a = ap.parse_args()
    d = glob.glob(os.path.join(a.out, "**", a.tag), recursive=True)
    d = [x for x in d if "loss_curves" not in x][0]
    from sklearn.metrics import roc_auc_score
    y = np.load(os.path.join(a.work, "in", "inputs", "labels.npz"))["y_test"].astype(int)
    dest = os.path.join(a.work, "in", "rope", a.family)
    os.makedirs(dest, exist_ok=True)
    res = {"tag": a.tag, "seeds": [], "weights_sha256": {}, "logits_sha256": {}, "min_april_auc_for_collapse_check": 1.0}
    for s in range(10):
        j = json.load(open(os.path.join(d, f"seed{s}.json")))
        assert j["split_hash_asserted"] and j["tokenizer"] == "bpe50k_fix" and j["n_train"] == 75298 and j["epochs"] == 3, (s, j["tokenizer"], j["n_train"], j["epochs"])
        z = np.load(os.path.join(d, f"seed{s}_epoch3_test_logits.npy"))
        auc = float(roc_auc_score(y, z))
        assert auc >= 0.6, f"seed {s} collapsed (April AUC {auc:.3f})"
        res["min_april_auc_for_collapse_check"] = min(res["min_april_auc_for_collapse_check"], auc)
        wp = os.path.join(d, f"seed{s}_epoch3_model.pt")
        res["weights_sha256"][f"seed{s}"], res["logits_sha256"][f"seed{s}"] = sha(wp), sha(os.path.join(d, f"seed{s}_epoch3_test_logits.npy"))
        shutil.copy(wp, os.path.join(dest, f"seed{s}.pt"))
        np.save(os.path.join(dest, f"seed{s}_april.npy"), z.astype(np.float32))
        res["seeds"].append(s)
    res["n_train"], res["tokenizer"], res["epochs"] = 75298, "bpe50k_fix", 3
    n_pool = sum("TRAIN pool 21,507 benign" in open(p_).read() for p_ in glob.glob(os.path.join(a.out, "**", "logs", f"{a.tag}_seed*.log"), recursive=True))
    res["seeds_with_padding_pool_21507_in_log"] = n_pool
    assert n_pool == 10, f"padding pool of 21,507 found in {n_pool} of 10 seed logs"
    os.makedirs(a.write, exist_ok=True)
    json.dump(res, open(os.path.join(a.write, "checks.json"), "w"), indent=1)
    print("checks passed:", a.tag, "min April AUC", round(res["min_april_auc_for_collapse_check"], 4))


if __name__ == "__main__":
    main()
