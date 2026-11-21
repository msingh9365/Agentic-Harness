"""
Job (CPU kernel): tokenizer and tokens for the group split (NOTES 21).   (OURS; the authors' functions do the filtering, the BPE training and the encoding)

    python -m baseline.gs_tokens --out /kaggle/working/out [--limit N]

1. the authors' filtering of all 92,700 reports (as baseline/preprocess.py; same order: January rows = x_train rows, then April),
2. checks that the rows are the rows we know: ym_train equals the published labels, and the number of calls of every report equals that of the old call-token store (`n_calls_old.npy`),
3. BPE-50k fit on the TRAINING part of the group split only (`split.npz`, hash asserted; no validation, no April), exactly the settings of preprocess variant `bpe50k` (variant `bpe50k_gs`),
4. re-tokenisation of all reports (x_train, x_test, 512 tokens) and the call-token store with the new tokenizer (`all_gs.npz`, original reports only),
5. check: the first 512 tokens of every report in the store = the row of x_train / x_test; the concatenation of the pieces = the full tokenisation of the report.
Nothing edited is built or saved.
"""
import argparse
import json
import os
import pickle
import time

import numpy as np

from baseline import common as C
from baseline import callstore as CS
from baseline import preprocess as P


class ListReps:
    def __init__(self, events):
        self.events = events

    def get(self, i):
        return self.events[i]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--split-dir", default=None, help="folder with split.npz, split_hash.json, labels.npz (old), n_calls_old.npy")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int, default=None, help="files per folder (smoke test only)")
    ap.add_argument("--work", default="/tmp/nebula_events")
    a = ap.parse_args()
    t0 = time.time()
    info = C.setup_nebula(None, require_patched=False)
    sd = a.split_dir or C.find_dir_with("split_hash.json")
    data = C.find_data_root()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    from baseline import groupsplit as G
    trn, val = G.val_slice(os.path.join(sd, "split.npz"), os.path.join(sd, "split_hash.json"))
    print(f"split hash asserted: {len(trn)} train, {len(val)} validation", flush=True)
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
    (ev_tr, ym_tr, names_tr), (ev_te, ym_te, names_te) = ev["train"], ev["test"]
    chk = {}
    if a.limit is None:
        old = np.load(os.path.join(sd, "labels.npz"))
        assert np.array_equal(old["ym_train"], ym_tr) and np.array_equal(old["ym_test"], ym_te), "labels differ from the published ones"
        n_old = np.load(os.path.join(sd, "n_calls_old.npy"))
        n_new = np.array([len(e.get("apis") or []) for e in ev_tr + ev_te])
        assert np.array_equal(n_old, n_new), f"number of calls differs from the old store in {(n_old != n_new).sum()} reports"
        chk["labels_equal_old"], chk["n_calls_equal_old_store_rows"] = True, int(len(n_new))
        print("rows are the old rows: labels and numbers of calls identical", flush=True)
        assert len(trn) + len(val) == len(ev_tr)
    np.savez_compressed(os.path.join(a.out, "labels.npz"), ym_train=ym_tr, ym_test=ym_te)
    fit_idx = trn if a.limit is None else None
    P.run_variant("bpe50k_gs", ev_tr, ev_te, a.out, info["nebula_root"], tok_fit_idx=fit_idx)
    vdir = os.path.join(a.out, "variants", "bpe50k_gs")
    inf = json.load(open(os.path.join(vdir, "info.json")))
    if a.limit is None:
        assert inf["tokenizer_fit_reports"] == len(trn), inf
    # call-token store with the NEW tokenizer: January rows then April rows
    spec = P.VARIANTS["bpe50k_gs"]
    tok = P.build_tokenizer(spec, info["nebula_root"], model_path=os.path.join(vdir, "tokenizer.model"), vocab_file=os.path.join(vdir, "vocab.json"))
    events = ev_tr + ev_te
    CS._G["tok"], CS._G["reps"] = tok, ListReps(events)
    t = time.time()
    store = CS.build_store(np.arange(len(events)), workers=a.workers)
    store.save(os.path.join(a.out, "all_gs.npz"))
    print(f"store: {len(store):,} reports, {len(store.seg_tok):,} tokens, {len(store.names):,} API names, {(time.time() - t) / 60:.1f} min", flush=True)
    # check 5
    xtr, xte = np.load(os.path.join(vdir, "x_train.npy")), np.load(os.path.join(vdir, "x_test.npy"))
    X = np.concatenate([xtr, xte])
    bad = 0
    for r in range(len(store)):
        tk = store.report_tokens(r)[:512]
        row = X[r]
        if not np.array_equal(row[:len(tk)].astype(np.int64), tk.astype(np.int64)) or (len(tk) < 512 and row[len(tk):].any()):
            bad += 1
    chk["first512_store_vs_x_rows_differing"] = int(bad)
    print("first 512 tokens of the store vs the rows of x_train/x_test: differing reports =", bad, flush=True)
    rng = np.random.default_rng(0)
    pick = rng.choice(len(store), size=min(3000, len(store)), replace=False)
    enc = tok.encode([events[int(r)] for r in pick], pad=False)
    full_bad = sum(int(not np.array_equal(np.asarray(e, dtype=np.int64), store.report_tokens(int(r)).astype(np.int64))) for e, r in zip(enc, pick))
    chk["full_tokenisation_vs_pieces_differing_of_3000"] = int(full_bad)
    print("full re-tokenisation vs concatenation of the pieces, 3000 reports: differing =", full_bad, flush=True)
    chk.update({"minutes_total": round((time.time() - t0) / 60, 1), "tokenizer_info": inf})
    json.dump(chk, open(os.path.join(a.out, "checks_gs_tokens.json"), "w"), indent=1)
    assert bad == 0 and full_bad == 0
    print(f"all done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
