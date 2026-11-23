"""
INDEPENDENT AUDIT of the reported numbers (CPU only; no training; no new April choices).

This file imports NOTHING from baseline/ (only numpy, scikit-learn, sentencepiece and the Python standard library) and reads only STORED files: the stored April logits and labels, the stored Stage J attack scores and
white-box files, the stored call-token store and tokenizer, and the reports (stage_i/tables.md, stage_j/report_table.md) that it checks. It re-implements every definition it needs from the written definitions of NOTES.md,
not from the code under audit.

    python baseline/audit_independent.py --repo . --stagej-scores /tmp/fix_j_all --store <all.npz> --jan-labels <labels.npz> --tokenizer-dir <variants/bpe50k_fix> --out audit [--summary audit/summary.txt]

Parts: (1) clean metrics of the final M1-M4 of both sets (current tokenizer = Step 5 / Stage G logits; fixed tokenizer = Stage I logits) against stage_i/tables.md;
(2) the 1% and 0.1% thresholds from the April benign logits by sorting (80 and 8 benign reports above them);
(3) detection at the 1% threshold of M1 and M3 under random 20 / 50 / 100 prepend, LightGBM 50 prepend and the white-box attack after 20 / 50 steps, from the stored Stage J scores, against stage_j/report_table.md;
(4) a spot check: the 'random 20 prepend' edit of three April malware reports is rebuilt from the call-token store and the stored sampler definition, decoded with the tokenizer, and checked against the stored total
    token counts of ALL 17,402 April reports. Writes audit/README.md, audit/results.json, audit/spot_check.md.
Definitions used (all stated in NOTES.md): pAUC@f = area under the ROC curve for FPR in [0, f] (linear interpolation at f) divided by f (so chance = f/2, perfect = 1); sklearn's roc_auc_score(max_fpr=f) is the
McClish-standardised form, converted back with 0.5 * (1 + (p - f^2/2) / (f - f^2/2)) = mcclish, p = pAUC * f; TPR@f = share of malware above the benign logit at rank floor(f * n_benign) in descending order (flagged =
strictly above); F1 at logit 0 = flag if logit >= 0; mean +- std over seeds with ddof 1.
"""
import argparse
import hashlib
import json
import os
import re

import numpy as np
import sentencepiece as spm
from sklearn.metrics import roc_auc_score, roc_curve

SEEDS = list(range(10))
N_JAN = 75298
FPR_SETS = [1e-2, 1e-3]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


# ----------------------------------------------------------------------------- metrics (own implementations)
def pauc_norm(y, z, f):
    """normalised partial AUC from the full ROC curve (no point dropped), linear interpolation at fpr = f, divided by f"""
    fpr, tpr, _ = roc_curve(y, z, drop_intermediate=False)
    i = int(np.searchsorted(fpr, f, side="left"))
    t_at = tpr[i] if fpr[i] == f else tpr[i - 1] + (tpr[i] - tpr[i - 1]) * (f - fpr[i - 1]) / (fpr[i] - fpr[i - 1])
    x = np.append(fpr[:i], f)
    yv = np.append(tpr[:i], t_at)
    return float(np.sum(np.diff(x) * (yv[1:] + yv[:-1]) / 2.0) / f)


def pauc_from_sklearn(y, z, f):
    """sklearn's roc_auc_score(max_fpr=f) (McClish) converted back to the normalised partial AUC"""
    mc = float(roc_auc_score(y, z, max_fpr=f))
    p = ((2 * mc - 1) * (f - f * f / 2) + f * f / 2) / f
    return mc, float(p)


def benign_threshold(z, y, f):
    neg = np.sort(z[y == 0])[::-1]
    return neg[int(np.floor(f * len(neg)))]


def tpr_at(z, y, f):
    thr = benign_threshold(z, y, f)
    return float((z[y == 1] > thr).mean())


def tpr_roc(z, y, f):
    fpr, tpr, _ = roc_curve(y, z)
    return float(tpr[fpr <= f][-1])


def f1_at_zero(z, y):
    pred = z >= 0
    tp, fp, fn = int((pred & (y == 1)).sum()), int((pred & (y == 0)).sum()), int((~pred & (y == 1)).sum())
    return 2 * tp / (2 * tp + fp + fn)


def all_metrics(z, y):
    mc2, p2s = pauc_from_sklearn(y, z, 1e-2)
    return {"TPR@1e-3": tpr_at(z, y, 1e-3), "TPR@1e-2": tpr_at(z, y, 1e-2), "AUC": float(roc_auc_score(y, z)), "F1": f1_at_zero(z, y), "pAUC@1e-2": pauc_norm(y, z, 1e-2), "pAUC@1e-3": pauc_norm(y, z, 1e-3),
            "_mcclish@1e-2": mc2, "_pauc_from_sklearn@1e-2": p2s, "_tpr_roc@1e-3": tpr_roc(z, y, 1e-3), "_tpr_roc@1e-2": tpr_roc(z, y, 1e-2)}


DEC = {"TPR@1e-3": 3, "TPR@1e-2": 3, "AUC": 4, "F1": 3, "pAUC@1e-2": 3, "pAUC@1e-3": 3}


# ----------------------------------------------------------------------------- parsing of the reports
VAL = re.compile(r"^(-?\d+\.\d+)(?: ± (\d+\.\d+))?$")


def parse_stage_i(path):
    """{(section, set, M): {column: (mean, std or None, decimals)}}, section 'seed' (per-seed mean ± std) or 'ens' (ensemble); set 'A' = current tokenizer, 'B' = fixed tokenizer"""
    out, section, cols = {}, None, None
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith("### Clean April test"):
            section = "seed"
        elif line.startswith("10-seed ensembles"):
            section = "ens"
        elif line.startswith("###") or line.startswith("(TPR@"):
            if section == "ens":
                section = None
        if section and line.startswith("|") and not line.startswith("|---"):
            cells = [c.strip().replace("**", "") for c in line.strip().strip("|").split("|")]
            if cells[0] == "model":
                cols = cells
                continue
            m = re.search(r"M(\d)", cells[0])
            which = "A" if "current tokenizer" in cells[0] else ("B" if "fixed tokenizer" in cells[0] else None)
            if not m or which is None or cols is None:
                continue
            row = {}
            for c, v in zip(cols[1:], cells[1:]):
                mv = VAL.match(v)
                if mv and c != "n":
                    row[c] = (float(mv.group(1)), float(mv.group(2)) if mv.group(2) else None, len(mv.group(1).split(".")[1]))
            out[(section, which, int(m.group(1)))] = row
    return out


def parse_stage_j(path):
    """{row label: {1: (mean, std), 2: ..., 3: ..., 4: ...}} for the rows of report_table.md (columns M1..M4)"""
    out = {}
    for line in open(path):
        if line.startswith("|") and not line.startswith("|---") and not line.startswith("| row"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            vals = {}
            for i, v in enumerate(cells[1:5], start=1):
                mv = VAL.match(v)
                if mv:
                    vals[i] = (float(mv.group(1)), float(mv.group(2)) if mv.group(2) else None)
            out[cells[0]] = vals
    return out


def fmt(v, d):
    return f"{v:.{d}f}"


def compare(rec, rep, d):
    """MATCH if the recomputed value, written with the decimals of the report, equals the reported number"""
    return "MATCH" if float(fmt(rec, d)) == float(fmt(rep, d)) else "DIFFERENT"


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--stagej-scores", required=True)
    ap.add_argument("--store", required=True)
    ap.add_argument("--jan-labels", required=True)
    ap.add_argument("--tokenizer-dir", required=True)
    ap.add_argument("--out", default="audit")
    ap.add_argument("--summary", default=None)
    a = ap.parse_args()
    R = a.repo
    os.makedirs(a.out, exist_ok=True)
    files = {
        "April labels": os.path.join(R, "results/logits/labels.npz"),
        "Stage I logits (fixed tokenizer)": os.path.join(R, "results/groupsplit/stage_fgh/stage_i/logits_fixed_models.npz"),
        "Step 5 logits (M1, M3, current tokenizer)": os.path.join(R, "results/groupsplit/stage_d/step5/logits_final_models.npz"),
        "Stage G logits (M2, M4, current tokenizer)": os.path.join(R, "results/groupsplit/stage_fgh/stage_g/logits_final_m2_m4.npz"),
        "stage_i/tables.md": os.path.join(R, "results/groupsplit/stage_fgh/stage_i/tables.md"),
        "stage_j/report_table.md": os.path.join(R, "results/groupsplit/stage_fgh/stage_j/report_table.md"),
        "group split": os.path.join(R, "results/groupsplit/split.npz"),
        "Stage J scores m1": os.path.join(a.stagej_scores, "scores_m1.npz"),
        "Stage J scores m3": os.path.join(a.stagej_scores, "scores_m3.npz"),
        "call-token store": a.store, "January labels": a.jan_labels, "tokenizer": os.path.join(a.tokenizer_dir, "tokenizer.model"), "model input rows x_test": os.path.join(a.tokenizer_dir, "x_test.npy")}
    hashes = {k: sha(v) for k, v in files.items()}
    y = np.load(files["April labels"])["y_test"].astype(int)
    n_ben, n_mal = int((y == 0).sum()), int((y == 1).sum())
    results = {"inputs_sha256_16": hashes, "n_april": int(len(y)), "n_benign": n_ben, "n_malware": n_mal}
    rows = []                                                                    # every comparison: dict(part, item, recomputed, reported, status)

    # ---- logits of the final models
    z_fix = np.load(files["Stage I logits (fixed tokenizer)"])
    z5, zg = np.load(files["Step 5 logits (M1, M3, current tokenizer)"]), np.load(files["Stage G logits (M2, M4, current tokenizer)"])
    Z = {("B", m): z_fix[f"f{m}_test"].astype(np.float64) for m in (1, 2, 3, 4)}
    Z[("A", 1)], Z[("A", 3)] = z5["v2pe_test"].astype(np.float64), z5["attbal_test"].astype(np.float64)
    Z[("A", 2)], Z[("A", 4)] = zg["m2_test"].astype(np.float64), zg["m4_test"].astype(np.float64)
    for k, z in Z.items():
        assert z.shape == (10, len(y)), (k, z.shape)

    # ---- part 1: clean metrics
    rep_i = parse_stage_i(files["stage_i/tables.md"])
    maxdiff = {}
    mcc = {"sklearn_mcclish_vs_reported_normalised_note": "roc_auc_score(max_fpr=0.01) is the McClish form (0.5 = chance); the reports use the normalised partial AUC (chance 0.005). The converted value is compared.", "max_abs_diff_converted_vs_direct": 0.0,
           "max_abs_diff_tpr_threshold_rule_vs_roc_rule": 0.0, "examples": []}
    for (which, m), z in sorted(Z.items()):
        per = [all_metrics(z[s], y) for s in SEEDS]
        ens = all_metrics(z.mean(0), y)
        for s_ in per + [ens]:
            mcc["max_abs_diff_converted_vs_direct"] = max(mcc["max_abs_diff_converted_vs_direct"], abs(s_["_pauc_from_sklearn@1e-2"] - s_["pAUC@1e-2"]))
            for f in ("1e-3", "1e-2"):
                mcc["max_abs_diff_tpr_threshold_rule_vs_roc_rule"] = max(mcc["max_abs_diff_tpr_threshold_rule_vs_roc_rule"], abs(s_[f"_tpr_roc@{f}"] - s_[f"TPR@{f}"]))
        mcc["examples"].append({"set": which, "model": m, "seed0_sklearn_mcclish_pauc@1e-2": per[0]["_mcclish@1e-2"], "seed0_converted_to_normalised": per[0]["_pauc_from_sklearn@1e-2"], "seed0_direct_normalised": per[0]["pAUC@1e-2"]})
        for col in DEC:
            vals = np.array([p[col] for p in per])
            for kind, rec, idx in (("per-seed mean", vals.mean(), 0), ("per-seed std", vals.std(ddof=1), 1), ("ensemble", ens[col], 0)):
                key = ("ens" if kind == "ensemble" else "seed", which, m)
                if key not in rep_i or col not in rep_i[key] or (kind == "per-seed std" and rep_i[key][col][1] is None):
                    continue
                rep = rep_i[key][col][idx if kind != "ensemble" else 0]
                d = rep_i[key][col][2]
                status = compare(rec, rep, d)
                md_key = f"{col} ({kind})"
                maxdiff[md_key] = max(maxdiff.get(md_key, 0.0), abs(rec - rep))
                rows.append({"part": "1 clean", "item": f"{'current' if which == 'A' else 'fixed'} tokenizer M{m} {col} {kind}", "recomputed": fmt(rec, d + 1), "reported": fmt(rep, d), "status": status})
    results["part1_max_abs_diff_per_metric"] = maxdiff
    results["part1_mcclish_note"] = mcc

    # ---- part 2: thresholds
    thr_rows, exceptions = [], []
    for (which, m), z in sorted(Z.items()):
        for s in SEEDS:
            out = {}
            for f, expect in ((1e-2, 80), (1e-3, 8)):
                thr = benign_threshold(z[s], y, f)
                above = int((z[s][y == 0] > thr).sum())
                out[f] = (float(thr), above)
                if above != expect:
                    tied_b, tied_m = int((z[s][y == 0] == thr).sum()), int((z[s][y == 1] == thr).sum())
                    exceptions.append({"set": which, "model": m, "seed": s, "fpr": f, "benign_above": above, "expected": expect, "benign_equal_to_threshold": tied_b, "malware_equal_to_threshold": tied_m,
                                       "explained_by_ties": bool(above < expect <= above + tied_b)})
            thr_rows.append((which, m, s, out))
    results["part2"] = {"n_benign": n_ben, "floor(0.01 n)": int(np.floor(0.01 * n_ben)), "floor(0.001 n)": int(np.floor(0.001 * n_ben)), "model_seeds_checked": len(thr_rows),
                        "all_exactly_80_and_8": not exceptions, "exceptions": exceptions}
    for f, expect, lab in ((1e-2, 80, "1%"), (1e-3, 8, "0.1%")):
        ex = [e for e in exceptions if e["fpr"] == f]
        rows.append({"part": "2 thresholds", "item": f"benign reports strictly above the {lab} threshold, number of the {len(thr_rows)} model-seeds with exactly {expect} (expected floor({f:g} x {n_ben}) = {expect})",
                     "recomputed": f"{len(thr_rows) - len(ex)} of {len(thr_rows)} exactly {expect}" + (f"; the other {len(ex)} have {min(e['benign_above'] for e in ex)} to {max(e['benign_above'] for e in ex)}" if ex else ""),
                     "reported": f"{expect} in every case", "status": "MATCH" if not ex else "DIFFERENT"})
    rows.append({"part": "2 thresholds", "item": "every exception explained by tied logits (benign reports with exactly the logit of the threshold: above < expected <= above + tied)", "recomputed": f"{sum(e['explained_by_ties'] for e in exceptions)} of {len(exceptions)} exceptions explained",
                 "reported": "n/a (not stated in the reports)", "status": "MATCH" if all(e["explained_by_ties"] for e in exceptions) else "DIFFERENT"})

    # ---- part 3: attacks (Stage J stored scores)
    rep_j = parse_stage_j(files["stage_j/report_table.md"])
    sc = {1: np.load(files["Stage J scores m1"]), 3: np.load(files["Stage J scores m3"])}
    link = {}
    wb_notes = {}
    labels_j = {"random 20 prepend": "random_20_prepend", "random 50 prepend": "random_50_prepend", "random 100 prepend": "random_100_prepend", "lgbm 50 prepend": "lgbm_50_prepend"}
    for m in (1, 3):
        d = sc[m]
        names = [str(x) for x in d["names"]]
        link[f"M{m}_row0_vs_stage_I_logits_max_abs_diff"] = max(float(np.abs(d[f"seed{s}"][names.index("unedited")].astype(np.float64) - Z[("B", m)][s]).max()) for s in SEEDS)
        for lab, nm in labels_j.items():
            j = names.index(nm)
            det = []
            for s in SEEDS:
                zc = d[f"seed{s}"][names.index("unedited")].astype(np.float64)
                thr = benign_threshold(zc, y, 1e-2)
                det.append(100 * float((d[f"seed{s}"][j].astype(np.float64)[y == 1] > thr).mean()))
            det = np.array(det)
            for kind, rec, idx in (("mean", det.mean(), 0), ("std", det.std(ddof=1), 1)):
                rep = rep_j[lab][m][idx]
                rows.append({"part": "3 attacks", "item": f"M{m} {lab} detection {kind} (%)", "recomputed": fmt(rec, 2), "reported": fmt(rep, 1), "status": compare(rec, rep, 1)})
        # white-box
        for steps_lab, k in (("white-box 20 steps", 20), ("white-box 50 steps", 50)):
            det, t_diff = [], []
            for s in SEEDS:
                w = np.load(os.path.join(a.stagej_scores, f"wb_m{m}_seed{s}.npz"))
                assert (y[w["sel"]] == 1).all() and len(set(w["sel"].tolist())) == 500, "white-box reports must be 500 distinct April malware reports"
                thr = benign_threshold(Z[("B", m)][s], y, 1e-2)                     # recomputed from the stored April logits, not the file's own threshold
                t_diff.append(abs(float(thr) - float(w["t1"])))
                det.append(100 * float((w["best"][k].astype(np.float64) > thr).mean()))
            det = np.array(det)
            wb_notes[f"M{m}_threshold_recomputed_vs_stored_in_wb_files_max_abs_diff"] = max(wb_notes.get(f"M{m}_threshold_recomputed_vs_stored_in_wb_files_max_abs_diff", 0.0), max(t_diff))
            for kind, rec, idx in (("mean", det.mean(), 0), ("std", det.std(ddof=1), 1)):
                rep = rep_j[steps_lab][m][idx]
                rows.append({"part": "3 attacks", "item": f"M{m} {steps_lab} detection {kind} (%)", "recomputed": fmt(rec, 2), "reported": fmt(rep, 1), "status": compare(rec, rep, 1)})
    results["part3_links"] = {**link, **wb_notes}

    # ---- part 4: spot check
    store = np.load(files["call-token store"], allow_pickle=False)
    seg_tok, seg_off, rep_seg = store["seg_tok"], store["seg_off"], store["rep_seg"]

    def seg(s):
        return seg_tok[seg_off[s]:seg_off[s + 1]]

    def n_calls(r):
        return int(rep_seg[r + 1] - rep_seg[r]) - 2

    def head(r):
        return seg(int(rep_seg[r]))

    def call(r, i):
        return seg(int(rep_seg[r]) + 1 + i)

    def report_tokens(r):
        return seg_tok[seg_off[rep_seg[r]]:seg_off[rep_seg[r + 1]]]
    y_jan = np.load(files["January labels"])["y_train"].astype(int)
    assert len(y_jan) == N_JAN and len(rep_seg) - 1 == N_JAN + len(y)
    val = np.load(files["group split"])["val"]
    pool = np.array([int(r) for r in val if y_jan[r] == 0 and n_calls(int(r)) > 0], dtype=np.int64)
    pool_n = np.array([n_calls(int(r)) for r in pool], dtype=np.int64)
    assert len(pool) == 3161, len(pool)

    def plan(t, k=20):                                                           # stored sampler definition (NOTES 23.3 / 26): per April row t, per call a uniform pool report, then a uniform call of it
        rng = np.random.default_rng([6000, int(t), int(k), 1])                    # last entry 1 = prepend (0 = insert)
        out = []
        for _ in range(k):
            pr = int(rng.integers(len(pool)))
            out.append((int(pool[pr]), int(rng.integers(pool_n[pr]))))
        return out
    tot_stored = {m: np.load(files[f"Stage J scores m{m}"])["tot"] for m in (1, 3)}
    names_j = [str(x) for x in np.load(files["Stage J scores m1"])["names"]]
    j20, j0 = names_j.index("random_20_prepend"), names_j.index("unedited")
    bad20 = bad0 = 0
    for t in range(len(y)):
        r = N_JAN + t
        base_len = len(report_tokens(r))
        if base_len != tot_stored[1][j0][t]:
            bad0 += 1
        if n_calls(r) == 0:
            tot = base_len
        else:
            tot = base_len + sum(len(call(rr, c)) for rr, c in plan(t))
        if tot != tot_stored[1][j20][t] or tot != tot_stored[3][j20][t]:
            bad20 += 1
    x_test = np.load(files["model input rows x_test"])
    bad_x = 0
    for t in range(len(y)):
        tk = report_tokens(N_JAN + t)[:512]
        row = x_test[t]
        if not (np.array_equal(row[:len(tk)], tk) and not row[len(tk):].any()):
            bad_x += 1
    results["part4_checks"] = {"april_reports": int(len(y)), "unedited_total_tokens_differing_from_stored_Stage_J": bad0, "random20prepend_total_tokens_differing_from_stored_Stage_J": bad20, "store_first512_differing_from_x_test_rows": bad_x}
    rows.append({"part": "4 rebuild", "item": "total token count of the rebuilt 'random 20 prepend' report vs the stored Stage J count, all 17,402 April reports", "recomputed": f"{len(y) - bad20} equal, {bad20} differ", "reported": "all equal", "status": "MATCH" if bad20 == 0 else "DIFFERENT"})
    rows.append({"part": "4 rebuild", "item": "total token count of the unedited report vs the stored Stage J count, all April reports", "recomputed": f"{len(y) - bad0} equal, {bad0} differ", "reported": "all equal", "status": "MATCH" if bad0 == 0 else "DIFFERENT"})
    rows.append({"part": "4 rebuild", "item": "first 512 tokens of the store vs the stored model-input rows x_test, all April reports", "recomputed": f"{len(y) - bad_x} equal, {bad_x} differ", "reported": "all equal", "status": "MATCH" if bad_x == 0 else "DIFFERENT"})
    sp = spm.SentencePieceProcessor()
    sp.Load(files["tokenizer"])
    chosen = [t for t in range(len(y)) if y[t] == 1 and n_calls(N_JAN + t) >= 20][:3]       # rule: the first three April malware reports with at least 20 calls
    md = ["# Spot check: 'random 20 prepend' on three April malware reports (decoded tokens)", "",
          "Rebuilt independently (baseline/audit_independent.py) from the call-token store with the stored sampler definition (`default_rng([6000, April row, 20, 1])`; per call a uniform report of the 3,161 held-out benign pool reports, then a uniform call of it) and decoded with the SentencePiece model of the corrected tokenizer. "
          "Order of an edited report: the report's own header tokens, then the 20 added calls, then the original calls and the tail. The model reads the first 512 tokens. Rule for the choice: the first three April malware reports (lowest April row) with at least 20 calls. No selection on any score.", ""]
    spot = []
    for t in chosen:
        r = N_JAN + t
        h = head(r)
        added = [call(rr, c) for rr, c in plan(t)]
        L = sum(len(x) for x in added)
        rest = report_tokens(r)[len(h):]
        seq = np.concatenate([h] + added + [rest])
        orig_start = len(h) + L
        assert len(seq) == len(report_tokens(r)) + L and np.array_equal(seq[:len(h)], report_tokens(r)[:len(h)]) and np.array_equal(seq[orig_start:], rest)
        un = x_test[t]
        first_diff = int(np.argmax(un[:512] != seq[:512])) if (un[:512] != seq[:512]).any() else None
        first120 = [int(v) for v in seq[:120]]
        spot.append({"april_row": t, "store_row": r, "n_calls_original": n_calls(r), "header_tokens": int(len(h)), "added_call_tokens": int(L), "original_calls_start_at_token": int(orig_start), "total_tokens_edited": int(len(seq)),
                     "total_tokens_unedited": int(len(report_tokens(r))), "first_position_where_model_input_differs_from_unedited": first_diff})
        md += [f"## April row {t} (malware; {n_calls(r)} original calls, {len(report_tokens(r))} tokens unedited, {len(seq)} tokens edited)", "",
               f"- header tokens of the original report: positions 0 to {len(h) - 1}; the 20 added calls: positions {len(h)} to {orig_start - 1} ({L} tokens); **the original report's calls start at token position {orig_start}** (0-based); the edit starts at position {len(h)}; the unedited and the edited model input first differ at position {first_diff} (earlier tokens coincide because many calls begin with the same tokens).",
               f"- the added calls come from the held-out benign pool reports: " + ", ".join(f"{rr}:{c}" for rr, c in plan(t)[:5]) + ", ... (store row : call index)", "",
               "**First 120 tokens, decoded:**", "", "```", sp.DecodeIds(first120), "```", "", "**Segments inside the first 120 tokens** (position range: decoded text):", ""]
        pos = 0
        for lab, arr in [("header of the original report", h)] + [(f"added call {i + 1}", x) for i, x in enumerate(added)]:
            if pos >= 120:
                break
            md.append(f"- {pos}-{pos + len(arr) - 1} {lab}: `{sp.DecodeIds([int(v) for v in arr])}`")
            pos += len(arr)
        if orig_start < 120:
            md.append(f"- {orig_start}-{orig_start + 24} original calls begin: `{sp.DecodeIds([int(v) for v in rest[:25]])}`")
        md += ["", f"**Boundary excerpt, tokens {max(0, orig_start - 15)} to {orig_start + 44} (the last tokens of the added calls, then the original report's calls):**", "", "```", sp.DecodeIds([int(v) for v in seq[max(0, orig_start - 15):orig_start + 45]]), "```", ""]
    open(os.path.join(a.out, "spot_check.md"), "w").write("\n".join(md) + "\n")
    results["part4_spot_check"] = spot

    # ---- outputs
    results["comparisons"] = rows
    json.dump(results, open(os.path.join(a.out, "results.json"), "w"), indent=1, default=str)
    n_match = sum(r["status"] == "MATCH" for r in rows)
    L = ["# Independent audit: recomputed numbers against the reported ones", ""]
    if a.summary and os.path.exists(a.summary):
        L += [open(a.summary).read().strip(), ""]
    L += [f"**{n_match} of {len(rows)} comparisons MATCH; {len(rows) - n_match} DIFFERENT.** Recomputed by `baseline/audit_independent.py` (imports nothing from `baseline/`; only numpy, scikit-learn, sentencepiece; CPU; stored files only). "
          "A number MATCHes if the recomputed value, written with the decimals of the report, equals the reported number. Input files (first 16 hex digits of the sha256):", ""]
    L += ["| input | sha256 (16) |", "|---|---|"] + [f"| {k} | `{v}` |" for k, v in hashes.items()] + [""]
    L += ["## 1. Clean metrics (stage_i/tables.md): maximum absolute difference per metric (recomputed, unrounded, against the reported rounded number; a match needs at most half a unit of the last printed digit)", "",
          "| metric | max abs difference | half unit of the last digit |", "|---|---|---|"]
    for k, v in sorted(maxdiff.items()):
        col = k.split(" (")[0]
        L.append(f"| {k} | {v:.2e} | {0.5 * 10 ** -DEC[col]:.1e} |")
    L += ["", f"Definition note: `roc_auc_score(max_fpr=0.01)` of scikit-learn returns the McClish-standardised partial AUC (0.5 = chance), e.g. seed 0 of the fixed-tokenizer M1: sklearn {mcc['examples'][4]['seed0_sklearn_mcclish_pauc@1e-2']:.4f}; the reports use the normalised partial AUC (area / 0.01; chance 0.005): "
          f"converted from sklearn {mcc['examples'][4]['seed0_converted_to_normalised']:.4f}, computed directly {mcc['examples'][4]['seed0_direct_normalised']:.4f}. Over all 80 model-seeds and 8 ensembles the converted-from-sklearn and the direct values differ by at most {mcc['max_abs_diff_converted_vs_direct']:.1e}; "
          f"TPR by the sorted-threshold rule and by the ROC-curve rule differ by at most {mcc['max_abs_diff_tpr_threshold_rule_vs_roc_rule']:.1e}.", "",
          "## 2. Thresholds", "", f"April: {n_mal} malware, {n_ben} benign reports; floor(0.01 x {n_ben}) = {int(np.floor(0.01 * n_ben))}, floor(0.001 x {n_ben}) = {int(np.floor(0.001 * n_ben))}. For {len(thr_rows)} model-seeds (both tokenizer sets) the threshold is the benign logit at rank floor(f x n) in the descending sort and a report is flagged if its logit is strictly above it. "
          + ("Exactly 80 and 8 benign reports lie above it in every case." if not exceptions else f"Exactly 80 / 8 benign reports lie above it except in the {len(exceptions)} cases below, where several benign reports have EXACTLY the logit of the threshold (float32 ties), so the strict count is smaller; the threshold value itself is the one defined."), "",
          *(["| set | model | seed | level | benign above (expected) | benign equal to the threshold | malware equal to the threshold | explained by ties |", "|---|---|---|---|---|---|---|---|"] + [f"| {'current' if e['set'] == 'A' else 'fixed'} tokenizer | M{e['model']} | {e['seed']} | {'1%' if e['fpr'] == 1e-2 else '0.1%'} | {e['benign_above']} ({e['expected']}) | {e['benign_equal_to_threshold']} | {e['malware_equal_to_threshold']} | {'yes' if e['explained_by_ties'] else 'NO'} |" for e in exceptions] + [""] if exceptions else []),
          "## 3. Links between stored files", "", "| check | value |", "|---|---|"] + [f"| {k} | {v:.2e} |" for k, v in {**link, **wb_notes}.items()] + ["",
          "## 4. Spot check and rebuild", "", f"`audit/spot_check.md` shows the decoded first 120 tokens of three April malware reports (rows {chosen}) with the 20 prepended calls. Summary: " + "; ".join(f"row {s['april_row']}: header {s['header_tokens']} tokens, 20 added calls {s['added_call_tokens']} tokens, original calls start at token position {s['original_calls_start_at_token']}" for s in spot) + ".", "",
          "## Every compared number", "", "| part | item | recomputed | reported | status |", "|---|---|---|---|---|"]
    L += [f"| {r['part']} | {r['item']} | {r['recomputed']} | {r['reported']} | {r['status']} |" for r in rows]
    open(os.path.join(a.out, "README.md"), "w").write("\n".join(L) + "\n")
    print(f"{n_match} of {len(rows)} comparisons MATCH; {len(rows) - n_match} DIFFERENT")
    for r in rows:
        if r["status"] != "MATCH":
            print("DIFFERENT:", r)
    print(json.dumps(results["part4_checks"]), json.dumps(results["part2"]["all_exactly_80_and_8"]))


if __name__ == "__main__":
    main()
