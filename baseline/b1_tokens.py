"""
Job (CPU kernel): the corrected 8k tokenizer `bpe8k_fix` for B1 (NOTES 30.4a).   (OURS; the authors' functions do the filtering, the cleaning, the BPE training and the encoding)

    python -m baseline.b1_tokens --out /kaggle/working/out

Exactly the recipe of `baseline/gs_tokens_fix.py` (steps 1, 3, 4 and the checks of steps 2, 5 that concern the 512-token rows), with vocabulary 8,192: the authors' filtering of all 92,700 reports, SentencePiece BPE fit on ALL
75,298 January reports (no April, no ADAPT text), options of `bpe50k_fix` (`--character_coverage=1.0 --byte_fallback=true --pad_id=0 --unk_id=1 --bos_id=-1 --eos_id=-1`), encoding of January and April to 512 tokens.
Checks (assert = STOP): published labels identical; unknown tokens (id 1) = 0 in x_train and x_test; id 0 only as right padding; unk 1, pad 0. Output: labels.npz, variants/bpe8k_fix/ (x_train.npy, x_test.npy, tokenizer.model, vocab.json, info.json), checks_b1_tokens.json.
"""
import argparse
import json
import os
import pickle
import shutil
import time

import numpy as np

from baseline import common as C
from baseline import preprocess as P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int, default=None, help="files per folder (smoke test only)")
    ap.add_argument("--smoke-vocab", type=int, default=0, help="smoke test only")
    ap.add_argument("--work", default="/tmp/nebula_events")
    a = ap.parse_args()
    t0 = time.time()
    info = C.setup_nebula(None, require_patched=False)
    data = C.find_data_root()
    old_dir = C.find_dir_with("labels.npz")
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    ev = {}
    for split in ("train", "test"):
        t = time.time()
        ev[split] = P.filter_split(os.path.join(data, f"windows_emulation_{split}set"), info["nebula_root"], a.workers, a.limit)
        print(f"[{split}] {len(ev[split][0])} reports filtered in {(time.time() - t) / 60:.1f} min", flush=True)
    (ev_tr, ym_tr, _), (ev_te, ym_te, _) = ev["train"], ev["test"]
    chk = {"limit": a.limit}
    old_lab = np.load(os.path.join(old_dir, "labels.npz"))
    if a.limit is None:
        assert np.array_equal(old_lab["ym_train"], ym_tr) and np.array_equal(old_lab["ym_test"], ym_te), "labels differ from the published ones"
        assert (len(ev_tr), len(ev_te)) == (75298, 17402)
        chk["labels_equal_old"] = True
        shutil.copy(os.path.join(old_dir, "labels.npz"), os.path.join(a.out, "labels.npz"))
    else:
        np.savez_compressed(os.path.join(a.out, "labels.npz"), ym_train=ym_tr, ym_test=ym_te, y_train=(np.asarray(ym_tr) != 0).astype(int), y_test=(np.asarray(ym_te) != 0).astype(int))
    if a.smoke_vocab:
        P.VARIANTS["bpe8k_fix"]["vocab"] = a.smoke_vocab
    P.run_variant("bpe8k_fix", ev_tr, ev_te, a.out, info["nebula_root"])
    vdir = os.path.join(a.out, "variants", "bpe8k_fix")
    inf = json.load(open(os.path.join(vdir, "info.json")))
    chk["tokenizer_info"] = inf
    if a.limit is None:
        assert inf["tokenizer_fit_reports"] == 75298 and inf["vocab_entries"] == 8193, inf
    import sentencepiece as spm
    sp = spm.SentencePieceProcessor(model_file=os.path.join(vdir, "tokenizer.model"))
    assert (sp.unk_id(), sp.pad_id(), sp.bos_id(), sp.eos_id()) == (1, 0, -1, -1) and sp.id_to_piece(0) == "<pad>" and sp.id_to_piece(1) == "<unk>", "special ids"
    xtr, xte = np.load(os.path.join(vdir, "x_train.npy")), np.load(os.path.join(vdir, "x_test.npy"))
    cnt = {"x_train_unk1": int((xtr == 1).sum()), "x_test_unk1": int((xte == 1).sum()), "x_train_max_id": int(xtr.max()), "x_test_max_id": int(xte.max())}
    for nm, x in (("x_train", xtr), ("x_test", xte)):
        nz = x != 0
        last = x.shape[1] - np.argmax(nz[:, ::-1], axis=1)
        last = np.where(nz.any(1), last, 0)
        cnt[f"{nm}_id0_not_right_padding_rows"] = int((nz.sum(1) != last).sum())
    chk["unknown_and_id0"] = cnt
    print(cnt, flush=True)
    assert cnt["x_train_unk1"] == cnt["x_test_unk1"] == 0 and cnt["x_train_id0_not_right_padding_rows"] == cnt["x_test_id0_not_right_padding_rows"] == 0, "unknown tokens or a real token with id 0"
    chk["minutes_total"] = round((time.time() - t0) / 60, 1)
    json.dump(chk, open(os.path.join(a.out, "checks_b1_tokens.json"), "w"), indent=1)
    print(f"all done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
