"""
Stage D, Step 0 of NOTES 22.2: what the group split removed from training, seen from the April test set (CPU only; no model score is used to build it).   (OURS)

    python -m baseline.gs_removed --store <all.npz of the call-token store> --labels <labels.npz with ym_train> --out results/groupsplit/stage_d

For every April report: the nearest January report by normalised edit distance between API-name sequences (Levenshtein / longer length, exact, between DISTINCT sequences, mapped back to reports), and the part
it is in (new training / new validation; old training / old validation, a distinct sequence can be in both old parts); the distance to the nearest report of each part; the exact hash_apis twin and its part.
Per family: shares of April reports whose exact twin / nearest neighbour is in the new validation part (unseen by the new models), within distance 0.05, and the drop of the detection rate (Stage C family.json,
thresholds on the April benign scores) next to them. Highlights: keylogger, rat, trojan and the largest validation group (1,056 reports). Descriptive only.
"""
import argparse
import hashlib
import json
import os

import numpy as np

from baseline import callstore as CS, gap, groupsplit as G

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMS = ["backdoor", "coinminer", "dropper", "keylogger", "ransomware", "rat", "trojan"]
ALLF = ["backdoor", "clean", "coinminer", "dropper", "keylogger", "ransomware", "rat", "trojan", "windows_syswow64"]
NEAR = 0.05


def md(rows, header):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def pct(x, d=1):
    return f"{100 * x:.{d}f}"


def main():
    from rapidfuzz.distance import Levenshtein
    from rapidfuzz.process import cdist
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "groupsplit", "stage_d"))
    a = ap.parse_args()
    store = CS.CallStore.load(a.store)
    jt = G.january_table()
    nj, na = len(jt["train"]["family"]), len(jt["test"]["family"])
    assert len(store) == nj + na
    trn, val = G.val_slice()
    otrn, oval = gap.val_slice(np.load(a.labels)["ym_train"])
    grp = np.load(os.path.join(ROOT, "results", "groupsplit", "split.npz"))["group"]
    seqj, seqa = G.name_sequences(store, range(nj)), G.name_sequences(store, range(nj, nj + na))
    hs = lambda q: hashlib.sha1(np.ascontiguousarray(q).tobytes()).hexdigest()
    hj, ha = np.array([hs(q) for q in seqj]), np.array([hs(q) for q in seqa])
    uj, ij, invj = np.unique(hj, return_index=True, return_inverse=True)          # distinct January sequences
    ua, ia, inva = np.unique(ha, return_index=True, return_inverse=True)          # distinct April sequences
    cnt = lambda idx: np.bincount(invj[idx], minlength=len(uj))
    n_tr, n_va, o_tr, o_va = cnt(trn), cnt(val), cnt(otrn), cnt(oval)
    assert (np.minimum(n_tr, n_va) == 0).all(), "a distinct sequence is in both parts of the NEW split"
    in_ntr, in_nva, in_otr, in_ova = n_tr > 0, n_va > 0, o_tr > 0, o_va > 0
    print(f"{len(uj)} distinct January sequences, {len(ua)} distinct April sequences; in both OLD parts: {int((in_otr & in_ova).sum())}", flush=True)
    A = [list(seqa[i]) for i in ia]
    B = [list(seqj[i]) for i in ij]
    D = cdist(A, B, scorer=Levenshtein.normalized_distance, workers=4, dtype=np.float32)          # exact normalised distances [distinct April, distinct January]
    big = np.where(~np.isnan(D), D, 2.0)
    mn = lambda m: np.where(m.any(), np.where(m[None, :], big, 9.0).min(1), 9.0)
    d_all, d_ntr, d_nva, d_otr, d_ova = big.min(1), mn(in_ntr), mn(in_nva), mn(in_otr), mn(in_ova)
    amin = big == d_all[:, None]                                                   # all nearest January sequences (ties included)
    nn_new = np.where((amin & in_ntr[None, :]).any(1) & (amin & in_nva[None, :]).any(1), "tie", np.where((amin & in_nva[None, :]).any(1), "val", "train"))
    ot, ov = (amin & in_otr[None, :]).any(1), (amin & in_ova[None, :]).any(1)
    nn_old = np.where(ot & ov, "both", np.where(ov, "val", "train"))
    # largest validation group
    vg = np.bincount(grp[val]).argmax()
    in_big = np.zeros(len(uj), bool)
    in_big[np.unique(invj[np.where(grp == vg)[0]])] = True
    nn_big = (amin & in_big[None, :]).any(1)
    d_big = mn(in_big)
    # per April report
    fam = jt["test"]["family"]
    hap = jt["test"]["hash_apis"]
    jh = jt["train"]["hash_apis"]
    hj_new_tr, hj_new_va, hj_old_tr, hj_old_va = set(jh[trn]), set(jh[val]), set(jh[otrn]), set(jh[oval])
    twin_any = np.array([h in hj_new_tr or h in hj_new_va for h in hap])
    twin_nva = np.array([(h in hj_new_va) and (h not in hj_new_tr) for h in hap])
    twin_ova = np.array([(h in hj_old_va) and (h not in hj_old_tr) for h in hap])
    twin_otr_only = np.array([(h in hj_old_tr) and (h not in hj_old_va) for h in hap])
    twin_both_old = np.array([(h in hj_old_tr) and (h in hj_old_va) for h in hap])
    # name-sequence twin of the big group
    twin_big = np.isin(ha, uj[in_big])                                              # the report's name sequence is one of the sequences of the largest validation group
    R = lambda v: v[inva]                                                           # distinct April sequence -> report
    r = {k: R(v) for k, v in dict(d_all=d_all, d_ntr=d_ntr, d_nva=d_nva, d_otr=d_otr, d_ova=d_ova, nn_new=nn_new, nn_old=nn_old, nn_big=nn_big, d_big=d_big).items()}
    fj = json.load(open(os.path.join(ROOT, "results", "groupsplit", "stage_c", "family.json")))["family"]
    rows, res = [], {}
    for g in ALLF:
        m = fam == g
        n = int(m.sum())
        s = lambda x: float(np.mean(x[m]))
        res[g] = {"n": n, "exact_hash_twin_in_january": s(twin_any), "exact_twin_only_in_new_validation": s(twin_nva), "nn_in_new_validation": s(r["nn_new"] == "val"), "nn_in_new_train": s(r["nn_new"] == "train"), "nn_tie_between_new_parts": s(r["nn_new"] == "tie"),
                  "nn_within_0.05_any": s(r["d_all"] <= NEAR), "within_0.05_of_new_train": s(r["d_ntr"] <= NEAR), "within_0.05_of_new_val": s(r["d_nva"] <= NEAR), "within_0.05_of_old_train": s(r["d_otr"] <= NEAR),
                  "lost_new": s((r["d_all"] <= NEAR) & (r["d_ntr"] > NEAR)), "lost_old": s((r["d_all"] <= NEAR) & (r["d_otr"] > NEAR)), "exact_twin_only_in_old_validation": s(twin_ova), "exact_twin_only_in_old_train": s(twin_otr_only), "exact_twin_in_both_old_parts": s(twin_both_old),
                  "nn_old_val_only": s(r["nn_old"] == "val"), "nn_old_both": s(r["nn_old"] == "both"), "median_nn_distance_all": float(np.median(r["d_all"][m])), "median_distance_new_train": float(np.median(r["d_ntr"][m])), "median_distance_old_train": float(np.median(r["d_otr"][m])),
                  "exact_twin_in_largest_val_group": s(twin_big), "nn_in_largest_val_group": s(r["nn_big"]), "within_0.05_of_largest_val_group": s(r["d_big"] <= NEAR)}
        if g in fj:
            for mod, lab in (("v2_pe", "old_v2pe"), ("gs_v2pe", "new_v2pe"), ("attbal", "old_attbal"), ("gs_attbal", "new_attbal")):
                res[g][f"detect_{lab}"] = fj[g][mod][0]
            res[g]["drop_v2pe_points"] = 100 * (fj[g]["gs_v2pe"][0] - fj[g]["v2_pe"][0])
            res[g]["drop_attbal_points"] = 100 * (fj[g]["gs_attbal"][0] - fj[g]["attbal"][0])
    # tables
    L = [f"### Step 0: what the split removed (April reports: {na:,}; distinct API-name sequences: April {len(ua):,}, January {len(uj):,}; exact normalised edit distance, nearest January report; descriptive)", "",
         f"New split: training {len(trn):,} / validation {len(val):,} reports, a distinct sequence is in exactly one part. Old split: training {len(otrn):,} / validation {len(oval):,}; {int((in_otr & in_ova).sum())} distinct January sequences occur in BOTH old parts. "
         f"Largest validation group: group id {int(vg)}, {int((grp[val] == vg).sum()):,} reports ({int(in_big.sum())} distinct sequences). Shares in %.", "",
         "**A. Exact twins and nearest neighbours (new split)**", "",
         md([[g + (" **(highlight)**" if g in ("keylogger", "rat", "trojan") else ""), res[g]["n"], pct(res[g]["exact_hash_twin_in_january"]), pct(res[g]["exact_twin_only_in_new_validation"]), pct(res[g]["nn_in_new_validation"]), pct(res[g]["nn_in_new_train"]), pct(res[g]["nn_tie_between_new_parts"]),
              pct(res[g]["nn_within_0.05_any"]), pct(res[g]["within_0.05_of_new_train"]), pct(res[g]["lost_new"]), f"{res[g]['median_nn_distance_all']:.3f}", f"{res[g]['median_distance_new_train']:.3f}"] for g in ALLF],
            ["family", "April n", "exact hash twin in January", "exact twin ONLY in new validation", "nearest neighbour in new validation", "nearest in new training", "tie", "nearest within 0.05 (any January)", "within 0.05 of new training", "near-twin lost (within 0.05 of January, not of new training)",
             "median nearest distance (January)", "median distance to new training"]), "",
         "**B. The same for the old split**", "",
         md([[g, pct(res[g]["exact_twin_only_in_old_validation"]), pct(res[g]["exact_twin_only_in_old_train"]), pct(res[g]["exact_twin_in_both_old_parts"]), pct(res[g]["nn_old_val_only"]), pct(res[g]["nn_old_both"]), pct(res[g]["within_0.05_of_old_train"]), pct(res[g]["lost_old"]), f"{res[g]['median_distance_old_train']:.3f}"] for g in ALLF],
            ["family", "exact twin only in old validation", "only in old training", "in both old parts", "nearest neighbour only in old validation", "nearest in both old parts (or tie)", "within 0.05 of old training", "near-twin lost", "median distance to old training"]), "",
         f"**C. The largest validation group (group {int(vg)}: {int((grp[val] == vg).sum()):,} January reports, {int(in_big.sum())} distinct sequences)**", "",
         md([[g, res[g]["n"], pct(res[g]["exact_twin_in_largest_val_group"]), pct(res[g]["nn_in_largest_val_group"]), pct(res[g]["within_0.05_of_largest_val_group"]), int(round(res[g]["exact_twin_in_largest_val_group"] * res[g]["n"])), int(round(res[g]["nn_in_largest_val_group"] * res[g]["n"]))] for g in ALLF],
            ["family", "April n", "exact twin in the group (%)", "nearest neighbour in the group (%)", "within 0.05 of the group (%)", "reports with exact twin", "reports with nearest neighbour in the group"]), "",
         "**D. Next to the drop in detection rate at the 1% FPR threshold (new vs old models; Stage C; thresholds on April benign scores; points; descriptive only)**", "",
         md([[g + (" **(highlight)**" if g in ("keylogger", "rat", "trojan") else ""), res[g]["n"], pct(res[g]["nn_in_new_validation"]), pct(res[g]["exact_twin_only_in_new_validation"]), pct(res[g]["lost_new"]), f"{res[g]['drop_v2pe_points']:+.1f}", f"{res[g]['drop_attbal_points']:+.1f}"] for g in FAMS],
            ["malware family", "April n", "nearest neighbour in new validation (%)", "exact twin only in new validation (%)", "near-twin lost (%)", "detection drop v2-PE (points)", "detection drop ATT+bal (points)"])]
    from scipy.stats import spearmanr
    corr = {}
    for xk, xl in (("nn_in_new_validation", "nearest neighbour in new validation"), ("exact_twin_only_in_new_validation", "exact twin only in new validation"), ("lost_new", "near-twin lost")):
        for yk in ("drop_v2pe_points", "drop_attbal_points"):
            corr[f"{xk}|{yk}"] = float(spearmanr([res[g][xk] for g in FAMS], [res[g][yk] for g in FAMS])[0])
    L += ["", "Spearman rank correlation across the 7 malware families (n = 7, descriptive only, no test; negative = the larger the share, the larger the drop): " + "; ".join(f"{k.split('|')[0].replace('_', ' ')} vs {k.split('|')[1].replace('drop_', '').replace('_points', '')}: {v:+.2f}" for k, v in corr.items()) + "."]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "step0_what_the_split_removed.md"), "w").write("\n".join(L) + "\n")
    json.dump({"per_family": res, "spearman_n7": corr, "largest_val_group": {"id": int(vg), "reports": int((grp[val] == vg).sum()), "distinct_sequences": int(in_big.sum())}, "n_distinct_january": int(len(uj)), "n_distinct_april": int(len(ua)),
               "distinct_in_both_old_parts": int((in_otr & in_ova).sum())}, open(os.path.join(a.out, "step0_what_the_split_removed.json"), "w"), indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2), dpi=200)
    x = np.arange(len(ALLF))
    for k, (key, col, lab) in enumerate((("nn_in_new_validation", "#eb6834", "nearest neighbour in new validation"), ("exact_twin_only_in_new_validation", "#6250d6", "exact twin only in new validation"), ("lost_new", "#1baf7a", "near-twin lost (new split)"), ("lost_old", "#bbbbbb", "near-twin lost (old split)"))):
        ax[0].bar(x + (k - 1.5) * 0.2, [100 * res[g][key] for g in ALLF], 0.2, color=col, label=lab)
    ax[0].set_xticks(x)
    ax[0].set_xticklabels([g.replace("windows_", "w_") for g in ALLF], rotation=30, ha="right", fontsize=8)
    ax[0].set_ylabel("share of April reports of the family (%)")
    ax[0].legend(fontsize=7, frameon=False)
    ax[0].set_title("What the new split took away from training", fontsize=9)
    for g in FAMS:
        for key, mk, col in (("drop_v2pe_points", "o", "#6250d6"), ("drop_attbal_points", "s", "#eb6834")):
            ax[1].scatter(100 * res[g]["nn_in_new_validation"], res[g][key], marker=mk, color=col, s=28)
        ax[1].annotate(g, (100 * res[g]["nn_in_new_validation"], res[g]["drop_v2pe_points"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax[1].scatter([], [], marker="o", color="#6250d6", label="v2-PE")
    ax[1].scatter([], [], marker="s", color="#eb6834", label="ATT+bal")
    ax[1].set_xlabel("April reports whose nearest January report is in the new validation part (%)")
    ax[1].set_ylabel("detection drop, new vs old models (points)")
    ax[1].legend(fontsize=7, frameon=False)
    ax[1].set_title("Descriptive only (7 families)", fontsize=9)
    for a_ in ax:
        a_.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_step0_what_the_split_removed.png"))
    print("\n".join(L))


if __name__ == "__main__":
    main()
