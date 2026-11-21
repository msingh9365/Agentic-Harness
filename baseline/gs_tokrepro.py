"""
Job (CPU kernel): direct check of NOTES 22.7 that the old BPE-50k = a BPE-50k fitted on ALL 75,298 January reports with the same settings.   (OURS; the authors' functions do the filtering, the fit and the encoding)

    python -m baseline.gs_tokrepro --out /kaggle/working/out

Filters all 92,700 reports (as baseline/preprocess.py), asserts that the labels are the published ones, fits a BPE-50k on ALL 75,298 January (trainset) reports ONLY (no April; variant `bpe50k_all`, the settings of `bpe50k`),
encodes January and April, and compares the new vocabulary and the token arrays x_train / x_test with the old files of the dataset of the old tokenizer (`variants/bpe50k` next to `all.npz`). Writes the new tokenizer
files, the arrays and `checks_tokrepro.json` (sha256 of tokenizer.model, vocabulary equal, arrays equal, number of reports differing). Nothing edited is built or saved.
"""
import argparse
import hashlib
import json
import os
import pickle
import time

import numpy as np

from baseline import common as C
from baseline import preprocess as P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int, default=None, help="files per folder (smoke test only)")
    ap.add_argument("--work", default="/tmp/nebula_events")
    a = ap.parse_args()
    t0 = time.time()
    info = C.setup_nebula(None, require_patched=False)
    data = C.find_data_root()
    old_dir = C.find_dir_with("all.npz")
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    ev = {}
    for split in ("train", "test"):
        cache = os.path.join(a.work, f"{split}_{a.limit}.pkl")
        if os.path.exists(cache):
            ev[split] = pickle.load(open(cache, "rb"))
            continue
        t = time.time()
        ev[split] = P.filter_split(os.path.join(data, f"windows_emulation_{split}set"), info["nebula_root"], a.workers, a.limit)
        pickle.dump(ev[split], open(cache, "wb"), protocol=4)
        print(f"[{split}] {len(ev[split][0])} reports filtered in {(time.time() - t) / 60:.1f} min", flush=True)
    (ev_tr, ym_tr, _), (ev_te, ym_te, _) = ev["train"], ev["test"]
    chk = {"fit_reports": len(ev_tr), "fit_set": "all January (windows_emulation_trainset) only; April is encoded, never fitted"}
    if a.limit is None:
        old = np.load(os.path.join(old_dir, "labels.npz"))
        assert np.array_equal(old["ym_train"], ym_tr) and np.array_equal(old["ym_test"], ym_te), "labels differ from the published ones"
        assert len(ev_tr) == 75298
    P.run_variant("bpe50k_all", ev_tr, ev_te, a.out, info["nebula_root"])
    vdir = os.path.join(a.out, "variants", "bpe50k_all")
    inf = json.load(open(os.path.join(vdir, "info.json")))
    chk["tokenizer_info"] = inf
    chk["tokenizer_model_sha256"] = hashlib.sha256(open(os.path.join(vdir, "tokenizer.model"), "rb").read()).hexdigest()
    ovoc = json.load(open(os.path.join(old_dir, "variants", "bpe50k", "vocab.json")))
    nvoc = json.load(open(os.path.join(vdir, "vocab.json")))
    chk["vocab_entries_old_new"] = [len(ovoc), len(nvoc)]
    chk["vocabulary_identical"] = bool(ovoc == nvoc)
    for nm in ("x_train", "x_test"):
        o, n = np.load(os.path.join(old_dir, "variants", "bpe50k", f"{nm}.npy")), np.load(os.path.join(vdir, f"{nm}.npy"))
        chk[f"{nm}_shape_old_new"] = [list(o.shape), list(n.shape)]
        chk[f"{nm}_identical"] = bool(o.shape == n.shape and np.array_equal(o, n))
        chk[f"{nm}_reports_differing"] = int((o != n).any(1).sum()) if o.shape == n.shape else None
    chk["minutes_total"] = round((time.time() - t0) / 60, 1)
    json.dump(chk, open(os.path.join(a.out, "checks_tokrepro.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in chk.items() if k != "tokenizer_info"}, indent=1), flush=True)


if __name__ == "__main__":
    main()
