"""
CPU analysis for the "why is the released BPE model better than our retrained ones" follow-up (Step 1).   (OURS)

    python -m baseline.gap_analysis --tokens results/_tokens_raw/out --raw results/baseline_raw --out results/F_gap [--only state,calib,tok,eval]

state   weight tables of the released checkpoint (every historic version in the authors' git history) against 3 of our fold models
calib   logit distributions on the April test set and on January (ours: held-out fold; released: in-sample, it was trained on January)
tok     released against our BPE tokenizer: vocabulary overlap, token-length distribution, truncation
eval    the released checkpoint and one of our checkpoints through EXACTLY the same function, eval mode, same arrays
"""
import argparse
import glob
import hashlib
import json
import os

import numpy as np

from baseline import common as C, cv


def jl(p):
    return json.load(open(p))


def sd_stats(sd):
    rows, tot = [], 0.0
    for k, v in sd.items():
        v = v.detach().double()
        rows.append({"name": k, "shape": list(v.shape), "numel": int(v.numel()), "l2": float(v.norm()), "rms": float((v ** 2).mean().sqrt()),
                     "mean_abs": float(v.abs().mean())})
        tot += float((v ** 2).sum())
    return rows, tot ** 0.5


def state(a):
    import torch
    nb = C.setup_nebula(require_patched=True)
    objs = os.path.join(nb["nebula_root"], "nebula", "objects")
    out = {"released": {}, "history": {}, "ours": {}}
    rel = torch.load(os.path.join(objs, "bpe_50000_torch.model"), map_location="cpu", weights_only=True)
    rows, total = sd_stats(rel)
    out["released"] = {"rows": rows, "total_l2": total, "n_params": int(sum(r["numel"] for r in rows))}
    # every historic version of the released file (extracted from the authors' git history into --history)
    for p in sorted(glob.glob(os.path.join(a.history, "bpe_*.model"))):
        d = torch.load(p, map_location="cpu", weights_only=True)
        v = torch.cat([x.flatten().double() for x in d.values()])
        out["history"][os.path.basename(p)] = {"n_params": int(v.numel()), "abs_sum": float(v.abs().sum()),
                                               "sorted_values_sha": hashlib.sha256(np.sort(v.numpy()).tobytes()).hexdigest()[:12]}
    for i in range(3):
        d = torch.load(os.path.join(a.raw, "detect", "bpe50k_time_seed0", f"fold{i}_model.pt"), map_location="cpu", weights_only=True)
        rows, total = sd_stats(d)
        out["ours"][f"fold{i}"] = {"rows": rows, "total_l2": total, "n_params": int(sum(r["numel"] for r in rows))}
    os.makedirs(a.out, exist_ok=True)
    C.dump_json(out, os.path.join(a.out, "state_dict_tables.json"))
    # markdown table: per tensor, released vs ours (mean of the 3 folds)
    md = "| tensor | shape | released: L2 / mean abs | ours (3 folds): L2 / mean abs |\n|---|---|---|---|\n"
    for r in out["released"]["rows"]:
        o = [next(x for x in out["ours"][f]["rows"] if x["name"] == r["name"]) for f in out["ours"]]
        md += f"| `{r['name']}` | {r['shape']} | {r['l2']:.3f} / {r['mean_abs']:.4f} | " + " ; ".join(f"{x['l2']:.3f} / {x['mean_abs']:.4f}" for x in o) + " |\n"
    md += f"| **total** | {out['released']['n_params']:,} params | L2 {out['released']['total_l2']:.2f} | " + " ; ".join(f"L2 {out['ours'][f]['total_l2']:.2f}" for f in out["ours"]) + " |\n"
    open(os.path.join(a.out, "state_dict_table.md"), "w").write(md)
    print(md)
    print(json.dumps(out["history"], indent=1))


def load_model(path, V):
    import torch
    from nebula.models.attention import TransformerEncoderChunks
    m = TransformerEncoderChunks(**cv.model_config(V))
    m.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    m.eval()
    return m


def variant(tokens, name):
    d = os.path.join(tokens, "variants", name)
    return np.load(os.path.join(d, "x_train.npy"), mmap_mode="r"), np.load(os.path.join(d, "x_test.npy"), mmap_mode="r"), jl(os.path.join(d, "vocab.json"))


def released_logits(a, which):
    """Released checkpoint on its own tokenization: 'test' (April) or 'train' (January, in-sample), cached."""
    p = os.path.join(a.out, f"released_{which}_logits.npy")
    if os.path.exists(p):
        return np.load(p)
    nb = C.setup_nebula(require_patched=True)
    xt_tr, xt_te, vocab = variant(a.tokens, "released_bpe50k")
    m = load_model(os.path.join(nb["nebula_root"], "nebula", "objects", "bpe_50000_torch.model"), len(vocab))
    z = cv.predict_logits(m, xt_tr if which == "train" else xt_te, "cpu")
    np.save(p, z.astype(np.float32))
    return z


def sat(y, z):
    """float32 saturation: reports whose sigmoid in float32 is exactly 1.0."""
    p = C.sigmoid32(z)
    top = p == 1.0
    return {"malware_at_1.0_pct": float(100 * top[y == 1].mean()), "benign_at_1.0_n": int(top[y == 0].sum()), "benign_at_1.0_pct": float(100 * top[y == 0].mean()),
            "n_tied_at_top": int((z == z.max()).sum()), "benign_logit_q": {q: float(np.percentile(z[y == 0], q)) for q in (50, 90, 99, 99.9)},
            "malware_logit_q": {q: float(np.percentile(z[y == 1], q)) for q in (1, 10, 50)}, "benign_top8_mean_logit": float(np.sort(z[y == 0])[-8:].mean())}


def calib(a):
    lab = np.load(os.path.join(a.tokens, "labels.npz"))
    y_tr, y_te = lab["y_train"], lab["y_test"]
    splits = jl(os.path.join(a.tokens, "splits.json"))
    ours_test, ours_val, ours_val_y = [], [], []
    x_tr, _, vocab = variant(a.tokens, "bpe50k")
    for s in range(3):
        for i in range(3):
            d = os.path.join(a.raw, "detect", f"bpe50k_time_seed{s}")
            ours_test.append(np.load(os.path.join(d, f"fold{i}_test_logits.npy")))
    for i in range(3):                                   # held-out January fold of the seed-0 fold models: recomputed (val logits were not saved)
        va = np.asarray(splits["kfold3"][i]["val"])
        m = load_model(os.path.join(a.raw, "detect", "bpe50k_time_seed0", f"fold{i}_model.pt"), len(vocab))
        ours_val.append(cv.predict_logits(m, np.asarray(x_tr[np.sort(va)]), "cpu"))
        ours_val_y.append(y_tr[np.sort(va)])
    zr_te, zr_tr = released_logits(a, "test"), released_logits(a, "train")
    res = {"test": {"released": sat(y_te, zr_te), "ours": [sat(y_te, z) for z in ours_test]},
           "january": {"released_in_sample": sat(y_tr, zr_tr), "ours_val_fold": [sat(yv, z) for yv, z in zip(ours_val_y, ours_val)]}}
    # also: our models on the January data they were TRAINED on (train fold of fold 0, seed 0), for an in-sample comparison
    C.dump_json(res, os.path.join(a.out, "calibration.json"))
    np.savez_compressed(os.path.join(a.out, "calib_arrays.npz"), y_test=y_te, released_test=zr_te.astype(np.float32),
                        ours_test=np.stack(ours_test).astype(np.float32), y_train=y_tr, released_train=zr_tr.astype(np.float32))
    def row(n, s):
        return f"| {n} | {s['malware_at_1.0_pct']:.1f} | {s['benign_at_1.0_n']} | {s['n_tied_at_top']} | {s['benign_logit_q'][99]:.1f} | {s['benign_logit_q'][99.9]:.1f} | {s['benign_top8_mean_logit']:.1f} | {s['malware_logit_q'][50]:.1f} |"
    md = "| model / data | malware with p32 = 1.0 (%) | benign with p32 = 1.0 (n) | tied at the top (n) | benign logit p99 | p99.9 | mean of the 8 highest benign | malware median |\n|---|---|---|---|---|---|---|---|\n"
    md += row("released, April test", res["test"]["released"]) + "\n"
    ot = res["test"]["ours"]
    md += "| ours (9 fold models), April test, mean | " + " | ".join(f"{np.mean(v):.1f}" for v in zip(*[[s['malware_at_1.0_pct'], s['benign_at_1.0_n'], s['n_tied_at_top'], s['benign_logit_q'][99], s['benign_logit_q'][99.9], s['benign_top8_mean_logit'], s['malware_logit_q'][50]] for s in ot])) + " |\n"
    md += row("released, January (in-sample: trained on it)", res["january"]["released_in_sample"]) + "\n"
    ov = res["january"]["ours_val_fold"]
    md += "| ours (3 fold models of seed 0), held-out January fold, mean | " + " | ".join(f"{np.mean(v):.1f}" for v in zip(*[[s['malware_at_1.0_pct'], s['benign_at_1.0_n'], s['n_tied_at_top'], s['benign_logit_q'][99], s['benign_logit_q'][99.9], s['benign_top8_mean_logit'], s['malware_logit_q'][50]] for s in ov])) + " |\n"
    open(os.path.join(a.out, "calibration_table.md"), "w").write(md)
    print(md)


def tok(a):
    import sentencepiece as spm
    nb = C.setup_nebula(require_patched=True)
    objs = os.path.join(nb["nebula_root"], "nebula", "objects")
    rel = spm.SentencePieceProcessor(model_file=os.path.join(objs, "bpe_50000_sentencepiece.model"))
    ours = spm.SentencePieceProcessor(model_file=os.path.join(a.tokenizers, "bpe50k", "tokenizer.model"))
    pr = {rel.id_to_piece(i): i for i in range(rel.get_piece_size())}
    po = {ours.id_to_piece(i): i for i in range(ours.get_piece_size())}
    common = set(pr) & set(po)
    out = {"released_pieces": len(pr), "ours_pieces": len(po), "common_pieces": len(common), "overlap_pct_of_released": 100 * len(common) / len(pr),
           "released_byte_pieces": sum(p.startswith("<0x") for p in pr), "ours_byte_pieces": sum(p.startswith("<0x") for p in po)}
    # length distributions on the same reports, January (train) and April (test)
    for name, v in (("released", "released_bpe50k"), ("ours", "bpe50k")):
        xtr, xte, vocab = variant(a.tokens, v)
        for split, x in (("january", xtr), ("april", xte)):
            x = np.asarray(x)
            ln = (x != 0).sum(1)
            unk = ((x == 1).sum(1) / np.maximum(ln, 1))
            out[f"{name}_{split}"] = {"mean_len": float(ln.mean()), "median_len": float(np.median(ln)), "truncated_pct": float(100 * (ln >= 512).mean()),
                                      "unk_token_pct": float(100 * unk.mean()), "len_pctl": {q: float(np.percentile(ln, q)) for q in (5, 25, 50, 75, 95)}}
    C.dump_json(out, os.path.join(a.out, "tokenizer_comparison.json"))
    print(json.dumps(out, indent=1))


def evalpath(a):
    """Both checkpoints through the SAME function on the SAME kind of arrays: cv.predict_logits (model.eval(), no_grad, int64 ids, pad 0 on the right, 512)."""
    import torch
    nb = C.setup_nebula(require_patched=True)
    lab = np.load(os.path.join(a.tokens, "labels.npz"))
    y_te = lab["y_test"]
    res = {}
    for name, var, path in (("released", "released_bpe50k", os.path.join(nb["nebula_root"], "nebula", "objects", "bpe_50000_torch.model")),
                            ("ours_fold0_seed0", "bpe50k", os.path.join(a.raw, "detect", "bpe50k_time_seed0", "fold0_model.pt"))):
        _, xte, vocab = variant(a.tokens, var)
        m = load_model(path, len(vocab))
        x = np.asarray(xte)
        sub = np.random.default_rng(0).permutation(len(x))[:3000]
        z = cv.predict_logits(m, x[sub], "cpu")
        res[name] = {"training_flag_after_predict": bool(m.training), "dtype_in_file": str(x.dtype), "shape": list(x.shape), "pad_id": 0,
                     "pad_side": "right" if (x[:, 0] != 0).all() else "left?", "maxlen": int(x.shape[1]), "pooling": "flatten",
                     "dropout_modules_in_eval": all(not mm.training for mm in m.modules() if isinstance(mm, torch.nn.Dropout)),
                     "tpr@1e-3_on_3000_subset_logit": C.binary_metrics(y_te[sub], z, decision=0.0)["tpr@0.001"],
                     "auc_on_subset": C.binary_metrics(y_te[sub], z, decision=0.0)["auc"],
                     "matches_saved_logits_max_abs_diff": float(np.abs(z - (np.load(os.path.join(a.raw, "released", "released_bpe50k_test_logits.npy"))[sub] if name == "released" else
                                                                           np.load(os.path.join(a.raw, "detect", "bpe50k_time_seed0", "fold0_test_logits.npy"))[sub])).max())}
    C.dump_json(res, os.path.join(a.out, "eval_path_check.json"))
    print(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default="results/_tokens_raw/out")
    ap.add_argument("--raw", default="results/baseline_raw")
    ap.add_argument("--tokenizers", default="baseline_models/tokenizers")
    ap.add_argument("--history", default="/tmp/gap/ver", help="historic versions of bpe_50000_torch.model extracted from the authors' git history")
    ap.add_argument("--out", default="results/F_gap")
    ap.add_argument("--only", default="state,calib,tok,eval")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for step in a.only.split(","):
        print(f"\n===== {step} =====", flush=True)
        {"state": state, "calib": calib, "tok": tok, "eval": evalpath}[step](a)


if __name__ == "__main__":
    main()
