"""
P1 of NOTES 24: unknown pieces (id 0 = SentencePiece <unk> = the padding id) in the real, unpadded token sequences of the call-token store.   (OURS; CPU only, no model score)

    python -m baseline.gs_unk --store <all.npz> --labels <labels.npz> --out results/groupsplit/stage_fgh/p1

Populations: January group-split training (66,580), January group-split validation (8,718), April (17,402); all / malware / benign; the first 512 tokens and the whole report. Per cell: reports, share with at
least one unknown token, median count over all reports, median over affected reports, mean, maximum. Decision rule (NOTES 24): fix planned if for ANY population and EITHER scope the share > 1% or the median > 0.
Also checks the id: the SentencePiece unk_id and the vocabulary JSON of the old tokenizer.
"""
import argparse
import json
import os

import numpy as np

from baseline import callstore as CS, groupsplit as G

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "groupsplit", "stage_fgh", "p1"))
    ap.add_argument("--limit", type=int, default=0, help="smoke test only: reports per population")
    a = ap.parse_args()
    import sentencepiece as spm
    tokdir = os.path.join(ROOT, "baseline_models", "tokenizers", "bpe50k")
    sp = spm.SentencePieceProcessor(model_file=os.path.join(tokdir, "tokenizer.model"))
    voc = json.load(open(os.path.join(tokdir, "vocab.json")))
    idinfo = {"sentencepiece_unk_id": sp.unk_id(), "sentencepiece_unk_piece": sp.id_to_piece(sp.unk_id()), "sentencepiece_bos_id": sp.bos_id(), "sentencepiece_eos_id": sp.eos_id(), "sentencepiece_pad_id": sp.pad_id(), "pieces": sp.get_piece_size(),
              "unseen_character_encoding": sp.encode_as_ids("abc ☃ xyz"), "vocab_json_entries": len(voc), "vocab_json_pad": voc.get("<pad>"), "vocab_json_unk": voc.get("<unk>")}
    UNK = sp.unk_id()
    assert UNK == 0 and voc["<pad>"] == 0, idinfo
    store = CS.CallStore.load(a.store)
    lab = np.load(a.labels)
    y_all, y_test = lab["y_train"].astype(int), lab["y_test"].astype(int)
    trn, val = G.val_slice()
    nj = len(y_all)
    pops = {"January training (group split)": (trn, y_all[trn]), "January validation (group split)": (val, y_all[val]), "April": (np.arange(nj, nj + len(y_test)), y_test)}
    res, rows, trig = {}, [], []
    for pname, (rows_idx, y) in pops.items():
        if a.limit:
            rows_idx, y = rows_idx[:a.limit], y[:a.limit]
        c512 = np.zeros(len(rows_idx), dtype=np.int64)
        cfull = np.zeros(len(rows_idx), dtype=np.int64)
        for i, r in enumerate(rows_idx):
            t = store.report_tokens(int(r))
            c512[i] = int((t[:512] == UNK).sum())
            cfull[i] = int((t == UNK).sum())
        for cname, m in (("all", np.ones(len(y), bool)), ("malware", y == 1), ("benign", y == 0)):
            if not m.any():
                continue
            for scope, c in (("first 512 tokens", c512), ("whole report", cfull)):
                v = c[m]
                aff = v > 0
                share, med = float(aff.mean()), float(np.median(v))
                res[f"{pname}|{cname}|{scope}"] = {"reports": int(m.sum()), "share_affected": share, "median_all": med, "median_affected": float(np.median(v[aff])) if aff.any() else None, "mean": float(v.mean()), "max": int(v.max())}
                rows.append([pname, cname, scope, int(m.sum()), f"{100 * share:.3f}", f"{med:g}", (f"{np.median(v[aff]):g}" if aff.any() else "-"), f"{v.mean():.4f}", int(v.max())])
                if cname == "all" and (share > 0.01 or med > 0):
                    trig.append(f"{pname} / {scope}: share {100 * share:.3f}%, median {med:g}")
    L = ["### P1: unknown pieces (id 0) in the real token sequences (call-token store, old tokenizer)", "", "Id check: " + json.dumps(idinfo), "",
         "| population | class | scope | reports | share with >= 1 unknown (%) | median count (all) | median count (affected) | mean count | max |", "|---|---|---|---|---|---|---|---|---|"] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    fix = bool(trig)
    L += ["", f"**Decision rule (any population, either scope, class 'all': share > 1% or median > 0): {'FIX PLANNED (not run), merged into P3' if fix else 'no fix planned'}.**" + ("  Triggers: " + "; ".join(trig) if trig else "")]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "unk_counts.md"), "w").write("\n".join(L) + "\n")
    json.dump({"id_check": idinfo, "cells": res, "fix_planned": fix, "triggers": trig}, open(os.path.join(a.out, "unk_counts.json"), "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
