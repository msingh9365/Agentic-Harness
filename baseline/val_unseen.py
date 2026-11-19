"""
Validation overlap audit (REPORT 5.13): 94.2% of the validation slice shares its API sequence (hash_apis) with the 90% training slice. Everything that was chosen on the validation slice is recomputed on the
validation reports whose API sequence is NOT in the training slice (433 reports: 99 malware, 334 benign), and the selection of REPORT 5.12 is redone on those numbers.   (OURS)

    python -m baseline.val_unseen --stage R          # robustness R on the unseen subset for the 16 candidates (downloads the epoch weights one batch at a time from the training kernels, scores, deletes)
    python -m baseline.val_unseen --stage report     # tables + the selection redone

Metrics of the unseen subset use ITS OWN benign reports for every threshold (1% FPR = rank floor(0.01 x 334) = 3). Only validation numbers are used; April logits are not opened.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results", "review")
TUNE = os.path.join(ROOT, "results", "tune")
KERNELS = {"tune_lr1e-3_p0.25": "nebula-tune-c1", "tune_lr1e-3_p0.5": "nebula-tune-c2", "tune_lr2e-3_p0.25": "nebula-tune-c3", "tune_lr2e-3_p0.5": "nebula-tune-c4"}


def load_val():
    from baseline import gap
    lab = np.load(os.path.join(ROOT, "results", "_tokens_raw", "out", "labels.npz"))
    trn, val = gap.val_slice(lab["ym_train"])
    seen = np.load(os.path.join(RES, "val_seen_mask.npy"))
    return lab, trn, val, lab["y_train"][val].astype(int), seen


def metrics(y, z):
    from baseline import common as C
    r = C.roc_summary(y, np.asarray(z, dtype=np.float64))
    return {"tpr@1e-3": r[0], "tpr@1e-2": r[1], "auc": r[2], "pauc@1e-2": r[3]}


def stage_R():
    import torch
    from baseline import callstore as CS, common as C, inmem_pad, padtest
    C.setup_nebula(require_patched=True)
    torch.set_num_threads(2)
    lab, trn, val, yv, seen = load_val()
    store = CS.CallStore.load(os.path.join(ROOT, "results", "callstore", "all.npz"))
    y_all = lab["y_train"]
    pool = inmem_pad.pool_rows_of(store, y_all, trn)
    rows, tok = inmem_pad.val_robust_set(store, y_all, val, pool)          # all validation malware, 20 TRAIN-pool calls prepended (the set of the tuning)
    pos_in_val = {int(r): i for i, r in enumerate(val)}
    idx = np.array([pos_in_val[int(r)] for r in rows])
    keep = ~seen[idx]
    tok_u = tok[keep]
    print(f"unseen validation malware with padding: {len(tok_u)}", flush=True)
    outp = os.path.join(RES, "val_unseen_R.json")
    res = json.load(open(outp)) if os.path.exists(outp) else {}
    ben_u = (yv == 0) & ~seen

    def R_of(model, zv):
        thr = padtest.thresholds(zv[ben_u], np.zeros(int(ben_u.sum()), dtype=int), 0.01)
        with torch.no_grad():
            z = np.concatenate([model(torch.as_tensor(tok_u[i:i + 128].astype(np.int64))).reshape(-1).numpy() for i in range(0, len(tok_u), 128)])
        return float((z > thr).mean())

    if "reference" not in res:
        r = []
        for s in range(10):
            m = padtest.load_model("attbal", os.path.join(ROOT, "results", "_attbal_raw2", "out", "attbal", f"seed{s}_epoch2_model.pt"), "cpu")
            r.append(R_of(m, np.load(os.path.join(ROOT, "results", "att_bal", "attbal", f"seed{s}_epoch2_val_logits.npy")).reshape(-1)))
        res["reference"] = r
        json.dump(res, open(outp, "w"))
        print("reference (existing ATT+bal) unseen R:", np.mean(r), flush=True)
    for tag, kernel in KERNELS.items():
        for e in (1, 2, 3, 4):
            key = f"{tag}|{e}"
            if key in res:
                continue
            tmp = os.path.join(ROOT, "results", "_tune_w", key.replace("|", "_"))
            shutil.rmtree(tmp, ignore_errors=True)
            os.makedirs(tmp)
            subprocess.run(["kaggle", "kernels", "output", f"manishsinghxdev/{kernel}", "-p", tmp, "--file-pattern", rf"seed\d_epoch{e}_model\.pt$", "-q"], check=True, capture_output=True)
            fs = sorted(glob.glob(os.path.join(tmp, "**", f"seed*_epoch{e}_model.pt"), recursive=True))
            assert len(fs) == 10, (key, len(fs))
            r = []
            for f in fs:
                s = int(os.path.basename(f).split("_")[0][4:])
                m = padtest.load_model("attbal", f, "cpu")
                r.append((s, R_of(m, np.load(os.path.join(TUNE, tag, f"seed{s}_epoch{e}_val_logits.npy")).reshape(-1))))
            res[key] = [x[1] for x in sorted(r)]
            json.dump(res, open(outp, "w"))
            shutil.rmtree(tmp, ignore_errors=True)
            print(f"{key}: unseen R mean {np.mean(res[key]):.4f}", flush=True)


def stage_report():
    from baseline import common as C, gap
    from baseline import tune_select as TS
    lab, trn, val, yv, seen = load_val()
    uns = ~seen
    res = json.load(open(os.path.join(RES, "val_unseen_R.json")))
    L = [f"Validation slice: {len(val):,} reports; **{100 * seen.mean():.1f}% share their API sequence (hash_apis) with the 90% training slice** ({int(seen.sum()):,} seen, {int(uns.sum())} unseen: {int(((yv == 1) & uns).sum())} malware, {int(((yv == 0) & uns).sum())} benign). April: 36.4%.", ""]
    # V1: the models with stored validation logits (epoch 2, flatten and attention, 10 seeds)
    fam = {"v2": ("logits", "v2"), "v2-PE": ("logits", "v2_pe")}
    for t in ("att", "attbal", "pebal", "attkeep", "pekeep", "attaug", "peaug"):
        fam[t] = ("att_bal", t)
    names = {"v2": "v2", "v2-PE": "v2-PE", "att": "ATT", "attbal": "ATT+bal", "pebal": "PE+bal", "attkeep": "ATT+bal-keep", "pekeep": "PE+bal-keep", "attaug": "ATT+aug", "peaug": "PE+aug"}
    rows = []
    for k, (kind, tag) in fam.items():
        if kind == "logits":
            d = np.load(os.path.join(ROOT, "results", "logits", f"{tag}.npz"))
            Z = np.stack([d[f"seed{s}_val"].reshape(-1) for s in range(10)])
        else:
            Z = np.stack([np.load(os.path.join(ROOT, "results", "att_bal", tag, f"seed{s}_epoch2_val_logits.npy")).reshape(-1) for s in range(10)])
        cell = []
        for sel in (np.ones(len(yv), bool), seen, uns):
            M = np.array([[metrics(yv[sel], z[sel])[m] for m in ("pauc@1e-2", "tpr@1e-2", "tpr@1e-3", "auc")] for z in Z])
            cell += [f"{M[:, 0].mean():.3f} ± {M[:, 0].std(ddof=1):.3f}", f"{M[:, 1].mean():.3f}", f"{M[:, 3].mean():.4f}"]
        rows.append([names[k]] + cell)
    L += ["**V1. Validation metrics at epoch 2 of the models of §5.7 to §5.11 (10 seeds; mean ± std), on all validation reports, on the seen part and on the unseen part.** TPR@1e-2 of the unseen part is read at 3 false alarms of 334 benign reports; pAUC on 334 benign reports is coarse.", "",
          "| model | pAUC@1e-2 all | TPR@1e-2 all | AUC all | pAUC@1e-2 seen | TPR@1e-2 seen | AUC seen | pAUC@1e-2 unseen | TPR@1e-2 unseen | AUC unseen |", "|" + "|".join("---" for _ in range(10)) + "|"]
    L += ["| " + " | ".join(r) + " |" for r in rows]
    # V2: the 16 candidates
    cands, rows2 = {}, []
    for lr, p in TS.CELLS:
        for e in TS.EPOCHS:
            tag = TS.tag_of(lr, p)
            Z = np.stack([np.load(os.path.join(TUNE, tag, f"seed{s}_epoch{e}_val_logits.npy")).reshape(-1) for s in range(10)])
            pa = np.array([metrics(yv[uns], z[uns])["pauc@1e-2"] for z in Z])
            auc = np.array([metrics(yv[uns], z[uns])["auc"] for z in Z])
            loss = np.array([gap.bce_logits(yv[uns], z[uns]) for z in Z])
            cands[(lr, p, e)] = {"pauc": pa, "auc": auc, "loss": loss, "robust": np.array(res[f"{tag}|{e}"])}
    ref = float(np.mean(res["reference"]))
    rows_sel, chosen, best = TS.select(cands, ref)
    L += ["", f"**V2. The 16 candidates of §5.12 on the unseen part only** (433 reports; unseen robustness R: the 99 unseen validation malware with 20 TRAIN-pool calls prepended, threshold = the 3rd highest of the 334 unseen benign scores; reference = the existing ATT+bal, mean R {ref:.4f}, rule 2 excludes mean R < {ref - TS.ROBUST_MARGIN:.4f}).", "",
          "| lr | p | epoch | mean pAUC@1e-2 (unseen) | SE | mean R (unseen) | mean loss (unseen) | min AUC | R excluded | note |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k in sorted(rows_sel):
        r = rows_sel[k]
        L.append(f"| {k[0]:g} | {k[1]:g} | {k[2]} | {r['mean_pauc']:.4f} | {r['se_pauc']:.4f} | {r['mean_robust']:.4f} | {r['mean_loss']:.4f} | {r['min_auc']:.4f} | {'yes' if r['robust_excluded'] else 'no'} | {'**best on unseen**' if k == best else ('tied' if r.get('tied_with_best') else '')} |")
    orig = (1e-3, 0.25, 2)
    L += ["", f"**The rule of NOTES 16.4 applied to the unseen-part numbers chooses {chosen}; on the full validation slice it chose {orig}.** " + ("The choice would not change." if chosen == orig else "The choice would change.")]
    json.dump({"chosen_unseen": list(chosen) if chosen else None, "chosen_full": list(orig), "reference_R": ref, "n_unseen": int(uns.sum())}, open(os.path.join(RES, "val_unseen.json"), "w"))
    open(os.path.join(RES, "val_unseen.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["R", "report"], required=True)
    a = ap.parse_args()
    if a.stage == "R":
        stage_R()
    else:
        stage_report()

