"""
Why does ATT+bal miss a cluster of April coinminer reports that v2-PE catches?   (OURS; analysis only, no model is trained and no reported result changes)

    python -m baseline.coinminer --out results/coinminer

Cluster = April coinminer reports detected by v2-PE in >= 8 of 10 seeds and by ATT+bal in <= 2 of 10 seeds, at the 1% FPR threshold fixed on the unedited April benign scores of each model and seed
(scores: results/review/attack/a3pad_{v2_pe,attbal}.npz, row 0 = unedited). Steps (numbers in coinminer.json, tables in tables.md, figures fig1_logits_vs_threshold, fig2_attention):
 1 the cluster by hash_apis; same sequence / close sequences (normalised Levenshtein distance on the API-name sequence) among the January training reports
 2 the calls in the first 512 tokens, against the coinminers that both models detect
 3 logits of the cluster against the thresholds
 4 attention-pooling weights of ATT+bal (seeds 0-2) on cluster reports and on a detected coinminer
 5 link to the TRAIN padding pool (benign reports of the 90% slice)
 6 coinminer TPR@1% counting every hash_apis group once
Only the original reports (call-token store), scores and the stored ATT+bal weights are used; no report is edited or executed.
"""
import argparse
import collections
import json
import os

import numpy as np
import pandas as pd

from baseline import callstore as CS, common as C, gap, inmem_pad, padtest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"


class Data:
    def __init__(self):
        meta = pd.read_csv(os.path.join(ROOT, "results", "hier", "data", "meta.csv"))
        rm = np.load(os.path.join(ROOT, "results", "padding", "row_map.npz"))
        self.tr_map, self.te_map = rm["train"], rm["test"]
        self.ntr = len(self.tr_map)
        self.A = meta.iloc[self.te_map].reset_index(drop=True)                      # April rows in our order
        self.J = meta.iloc[self.tr_map].reset_index(drop=True)                      # January rows in our order
        self.y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
        self.store = CS.CallStore.load(os.path.join(ROOT, "results", "callstore", "all.npz"))
        r = pd.read_csv(os.path.join(ROOT, "results", "misses", "reports.csv"), usecols=["split", "sample_id", "hash_apis"]).drop_duplicates("sample_id")
        self.hash_apr = r[r.split == "testset"].set_index("sample_id").loc[self.A.id.values, "hash_apis"].values
        self.hash_jan = r[r.split == "trainset"].set_index("sample_id").loc[self.J.id.values, "hash_apis"].values
        self.Z = {f: np.stack([np.load(os.path.join(ROOT, "results", "review", "attack", f"a3pad_{f}.npz"))[f"seed{s}"][0] for s in range(10)]).astype(np.float64) for f in ("v2_pe", "attbal")}
        self.thr = {f: np.array([padtest.thresholds(self.Z[f][s], self.y, 0.01) for s in range(10)]) for f in self.Z}
        self.flag = {f: self.Z[f] > self.thr[f][:, None] for f in self.Z}
        self.cnt = {f: self.flag[f].sum(0) for f in self.Z}
        self.coin = self.A.family.values == "coinminer"

    def names(self, row):
        s0, s1 = int(self.store.rep_seg[row]) + 1, int(self.store.rep_seg[row + 1]) - 1
        return self.store.seg_name[s0:s1]

    def window_calls(self, row, cut=512):
        """number of calls that lie completely inside the first `cut` tokens of the report"""
        s = self.store
        cum = np.cumsum([len(s.head(row))] + [len(s.call(row, i)) for i in range(s.n_calls(row))])
        return int((cum[1:] <= cut).sum()), cum


def pct(a, q):
    return [float(np.percentile(a, x)) for x in q]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "coinminer"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    D = Data()
    S = D.store
    out, md = {}, []
    cl = D.coin & (D.cnt["v2_pe"] >= 8) & (D.cnt["attbal"] <= 2)
    both = D.coin & (D.cnt["v2_pe"] >= 8) & (D.cnt["attbal"] >= 8)
    n_coin = int(D.coin.sum())
    out["definition"] = "April coinminer reports detected by v2-PE in >= 8/10 seeds and by ATT+bal in <= 2/10 seeds at the 1% FPR threshold of each model and seed"
    # ------------------------------------------------------------------ step 1
    groups = pd.Series(D.hash_apr[cl]).value_counts()
    big = groups.index[0]
    in_big = np.where(D.hash_apr == big)[0]
    rep = D.ntr + int(in_big[0])
    seq = D.names(rep)
    from rapidfuzz.distance import Levenshtein as L

    def neighbours(row):
        a_ = D.names(row).tolist()
        d = np.empty(D.ntr)
        for j in range(D.ntr):
            d[j] = L.normalized_distance(a_, D.names(j).tolist())
        return d
    d = neighbours(rep)
    o = np.argsort(d)[:5]
    near = {f"{th:g}": {"n": int((d <= th).sum()), "by_family_label": {f"{k[0]}|{k[1]}": int(v) for k, v in D.J[d <= th].groupby(["family", "label"]).size().items()}} for th in (0.02, 0.05, 0.1, 0.2)}
    # reference: the same distance for one report of each of 40 other hash groups of the coinminers detected by both models
    ref_groups = pd.Series(D.hash_apr[both]).value_counts()
    rng = np.random.default_rng(0)
    ref_hashes = list(rng.choice(ref_groups.index.values, size=min(40, len(ref_groups)), replace=False))
    ref_min = []
    ref_coin_within = []
    for hsh in ref_hashes:
        r_ = D.ntr + int(np.where(D.hash_apr == hsh)[0][0])
        dd = neighbours(r_)
        ref_min.append(float(dd.min()))
        ref_coin_within.append(int(((dd <= 0.1) & (D.J.family.values == "coinminer")).sum() > 0))
    out["step1"] = {"cluster_size": int(cl.sum()), "groups_in_cluster": {k: int(v) for k, v in groups.items()}, "n_tokens_full_of_cluster": {int(k): int(v) for k, v in pd.Series(D.A.n_tokens_full.values[cl]).value_counts().items()},
                    "main_group_hash": big, "april_reports_with_main_hash": int(len(in_big)), "april_families_with_main_hash": {k: int(v) for k, v in pd.Series(D.A.family.values[in_big]).value_counts().items()},
                    "january_reports_with_main_hash": int((D.hash_jan == big).sum()), "calls": int(len(seq)), "tokens_full": int(len(S.report_tokens(rep))), "distinct_names": int(len(set(seq.tolist()))),
                    "nearest_january": [{"row": int(j), "family": D.J.family[j], "label": int(D.J.label[j]), "calls": int(len(D.names(j))), "norm_distance": float(d[j]), "edits": int(round(d[j] * max(len(seq), len(D.names(j)))))} for j in o],
                    "january_within_distance": near, "april_coinminer_reports": n_coin, "april_coinminer_hash_groups": int(len(set(D.hash_apr[D.coin]))),
                    "reference_detected_groups_min_norm_distance": {"n_groups": len(ref_hashes), "median": float(np.median(ref_min)), "q25_q75": pct(ref_min, [25, 75]), "share_with_a_january_coinminer_within_0.1": float(np.mean(ref_coin_within))}}
    md.append("### Step 1. The cluster\n\n" + f"{int(cl.sum())} reports; hash_apis groups: " + ", ".join(f"`{k[:8]}…` ({v})" for k, v in groups.items()) + f". April reports with the main hash: {len(in_big)} (families: {out['step1']['april_families_with_main_hash']}). January reports with the same hash: {out['step1']['january_reports_with_main_hash']}.\n")
    # ------------------------------------------------------------------ step 2
    nwin, cum = D.window_calls(rep)
    wnames = [S.names[i] for i in seq[:nwin]]
    cluster_top = collections.Counter(wnames).most_common(8)

    def window_stats(row):
        n, _ = D.window_calls(row)
        nm = D.names(row)[:n]
        c = collections.Counter(nm.tolist())
        top = c.most_common(1)[0][1] if c else 0
        runs, best, cur = 0, 0, 0
        for i in range(len(nm)):
            cur = cur + 1 if i and nm[i] == nm[i - 1] else 1
            best = max(best, cur)
        return {"calls_in_window": int(n), "distinct_names": int(len(c)), "top_name_share": float(top / max(n, 1)), "longest_run_same_name": int(best)}
    ref_rows = {h: D.ntr + int(np.where(D.hash_apr == h)[0][0]) for h in ref_groups.index.values}
    ws_ref = [window_stats(r_) for r_ in ref_rows.values()]
    ws_cl = window_stats(rep)
    agg_ref = collections.Counter()
    for r_ in ref_rows.values():
        n, _ = D.window_calls(r_)
        agg_ref.update(S.names[i] for i in D.names(r_)[:n])
    ex_ref_h = min(ref_rows, key=lambda h: abs(len(D.names(ref_rows[h])) - np.median([len(D.names(r_)) for r_ in ref_rows.values()])))
    ex_ref = ref_rows[ex_ref_h]
    odd = [i for i in np.where(cl)[0] if D.hash_apr[i] != big]
    ex_odd = D.ntr + int(odd[0]) if odd else None
    out["step2"] = {"cluster_window": ws_cl, "cluster_top_names": cluster_top, "detected_coinminers_groups": len(ws_ref),
                    "detected_window_stats_median": {k: float(np.median([w[k] for w in ws_ref])) for k in ws_ref[0]}, "detected_window_stats_q25_q75": {k: pct([w[k] for w in ws_ref], [25, 75]) for k in ws_ref[0]},
                    "detected_share_of_groups_with_top_name_share_ge_0.9": float(np.mean([w["top_name_share"] >= 0.9 for w in ws_ref])),
                    "detected_top_names_all_windows": agg_ref.most_common(8),
                    "example_cluster_first60": [S.names[i] for i in D.names(rep)[:60]], "example_detected_first60": [S.names[i] for i in D.names(ex_ref)[:60]],
                    "example_odd_cluster_member_first60": ([S.names[i] for i in D.names(ex_odd)[:60]] if ex_odd else None),
                    "example_detected_hash": ex_ref_h, "example_detected_window": window_stats(ex_ref),
                    "cluster_full_sequence": {"calls": int(len(seq)), "counts": dict(collections.Counter(S.names[i] for i in seq)), "calls_inside_window": int(nwin), "calls_outside_window": int(len(seq) - nwin),
                                              "non_getprocaddress_positions": [[int(i), S.names[n]] for i, n in enumerate(seq) if S.names[n] != "kernel32.getprocaddress"]}}
    # ------------------------------------------------------------------ step 3
    sc = {}
    for f in D.Z:
        z = D.Z[f][:, cl]                                       # [10, n]
        margin = z - D.thr[f][:, None]
        sc[f] = {"logit_percentiles_5_25_50_75_95": pct(z, [5, 25, 50, 75, 95]), "threshold_mean": float(D.thr[f].mean()), "threshold_min_max": [float(D.thr[f].min()), float(D.thr[f].max())],
                 "margin_percentiles_5_25_50_75_95": pct(margin, [5, 25, 50, 75, 95]), "share_flagged": float((margin > 0).mean()), "share_within_2_below": float(((margin <= 0) & (margin > -2)).mean()),
                 "share_more_than_10_below": float((margin < -10).mean()), "median_margin_per_seed": [float(np.median(margin[s])) for s in range(10)],
                 "benign_logit_p50_p99_april": pct(D.Z[f][:, D.y == 0], [50, 99])}
    for f in D.Z:
        ben = D.Z[f][:, D.y == 0]
        fpr_at = [float((ben[s] >= np.median(D.Z[f][s, cl])).mean()) for s in range(10)]              # share of April benign reports scoring at least as high as the cluster's median report
        sc[f]["benign_share_at_or_above_cluster_median_per_seed"] = fpr_at
        sc[f]["benign_share_at_or_above_cluster_median_mean"] = float(np.mean(fpr_at))
    out["step3"] = sc
    # ------------------------------------------------------------------ step 4
    import torch
    from baseline import pe
    C.setup_nebula(require_patched=True)
    tokp = __import__("baseline.make_pad", fromlist=["x"]).make_tokenizer()
    cl_rows = [D.ntr + int(i) for i in in_big[:3]]
    det_pool = np.where(both & (D.cnt["attbal"] >= 9))[0]
    det_row = D.ntr + int(det_pool[len(det_pool) // 2])
    rows4 = {"cluster_1": cl_rows[0], "cluster_2": cl_rows[1], "cluster_3": cl_rows[2], "detected_coinminer": det_row}
    toks = {k: CS.build_fast(S, r, [], None)[0].astype(np.int64) for k, r in rows4.items()}
    ident = {k: bool(np.array_equal(toks[k], toks["cluster_1"])) for k in ("cluster_2", "cluster_3")}
    seg = {}
    for k, r in rows4.items():
        m = np.full(512, -2)
        m[:len(S.head(r))] = -1
        pos = len(S.head(r))
        for i in range(S.n_calls(r)):
            ln = len(S.call(r, i))
            m[pos:min(pos + ln, 512)] = i
            pos += ln
            if pos >= 512:
                break
        seg[k] = m
    att = {k: {} for k in rows4}
    for s in range(3):
        mdl = padtest.load_model("attbal", os.path.join(ROOT, "results", "_attbal_raw2", "out", "attbal", f"seed{s}_epoch2_model.pt"), "cpu")
        with torch.no_grad():
            w = mdl.attention_weights(torch.as_tensor(np.stack([toks[k] for k in rows4]))).numpy()
        for i, k in enumerate(rows4):
            att[k][s] = w[i]
    t4 = {}
    for k, r in rows4.items():
        names_k = D.names(r)
        rec = {}
        for s in range(3):
            w = att[k][s]
            head = float(w[seg[k] == -1].sum())
            by = collections.Counter()
            for p in np.nonzero(w)[0]:
                if seg[k][p] >= 0:
                    by[S.names[names_k[seg[k][p]]]] += float(w[p])
            top_pos = np.argsort(w)[::-1][:5]
            rec[f"seed{s}"] = {"weight_on_report_header": head, "weight_by_api_name": {n: float(v) for n, v in by.most_common(4)}, "max_weight": float(w.max()), "n_tokens_with_weight": int((w > 0).sum()),
                               "effective_tokens_1_over_sum_w2": float(1.0 / (w ** 2).sum()),
                               "top_tokens": [{"pos": int(p), "piece": tokp.tokenizer.id_to_piece(int(toks[k][p])), "weight": float(w[p]), "call": (S.names[names_k[seg[k][p]]] if seg[k][p] >= 0 else ("header" if seg[k][p] == -1 else "tail"))} for p in top_pos]}
        t4[k] = rec
    out["step4"] = {"rows": {k: int(r) for k, r in rows4.items()}, "cluster_reports_have_identical_tokens": ident, "attention": t4}
    # ------------------------------------------------------------------ step 5
    lab = np.load(os.path.join(ROOT, "results", "_tokens_raw", "out", "labels.npz"))
    trn, _ = gap.val_slice(lab["ym_train"])
    pool = inmem_pad.pool_rows_of(S, lab["y_train"], trn)
    cnt_pool = np.zeros(len(S.names))
    draw = np.zeros(len(S.names))                                                  # P(a padding call has this name): uniform pool report, then uniform call of it
    for r_ in pool:
        nm = D.names(int(r_))
        bc = np.bincount(nm, minlength=len(S.names))
        cnt_pool += bc
        draw += bc / len(nm)
    n_pool_calls = cnt_pool.sum()
    freq = cnt_pool / n_pool_calls
    draw /= len(pool)
    rank_draw = (-draw).argsort().argsort()

    def pool_link(row):
        n, _ = D.window_calls(row)
        nm = D.names(row)[:n]
        in_pool = cnt_pool[nm] > 0
        return {"calls": int(n), "share_names_in_pool": float(in_pool.mean()), "mean_log10_pool_freq": float(np.mean(np.log10(np.maximum(freq[nm], 1e-9)))), "mean_draw_probability": float(draw[nm].mean()),
                "median_draw_rank": float(np.median(rank_draw[nm]))}
    pl_cl = pool_link(rep)
    pl_ref = [pool_link(r_) for r_ in ref_rows.values()]
    gp = S.names.index("kernel32.getprocaddress")
    # how often do January training windows look like this one (most calls = GetProcAddress)?
    jan_share = np.zeros(D.ntr)
    for j in range(D.ntr):
        n, _ = D.window_calls(j)
        nm = D.names(j)[:n]
        jan_share[j] = float((nm[1:] == gp).mean()) if n > 2 else 0.0
    jt = D.J.assign(gp_share=jan_share)
    hi = jt[jt.gp_share >= 0.9]
    out["step5"] = {"pool_reports": int(len(pool)), "pool_calls": int(n_pool_calls), "cluster": pl_cl, "detected_coinminer_groups_mean": {k: float(np.mean([p[k] for p in pl_ref])) for k in pl_ref[0]},
                    "detected_coinminer_groups_q25_q75": {k: pct([p[k] for p in pl_ref], [25, 75]) for k in pl_ref[0]},
                    "getprocaddress": {"pool_call_share": float(freq[gp]), "padding_draw_probability": float(draw[gp]), "padding_draw_rank_of_%d_names" % int((draw > 0).sum()): int(rank_draw[gp]) + 1},
                    "loadlibrarya": {"pool_call_share": float(freq[S.names.index("kernel32.loadlibrarya")]), "padding_draw_probability": float(draw[S.names.index("kernel32.loadlibrarya")])},
                    "january_windows_with_90pct_getprocaddress": {"n": int(len(hi)), "by_label": {int(k): int(v) for k, v in hi.groupby("label").size().items()}, "by_family": {k: int(v) for k, v in hi.groupby("family").size().items()},
                                                                  "share_benign": float((hi.label == 0).mean()) if len(hi) else None}}
    from baseline import make_pad
    reps = make_pad.Reps()

    def resolved(rep_dict, n_win):
        out_ = []
        for c in (rep_dict.get("apis") or [])[:n_win]:
            if isinstance(c, dict) and str(c.get("api_name", "")).lower() == "kernel32.getprocaddress":
                ar = c.get("args") or []
                if len(ar) > 1 and isinstance(ar[1], str) and not ar[1].startswith("0x"):
                    out_.append(ar[1].lower())
        return out_
    cl_names = resolved(reps.get(int(D.te_map[rep - D.ntr])), nwin)
    cl_set = set(cl_names)

    def sim(rep_dict, n_win):
        b = set(resolved(rep_dict, n_win))
        return (len(cl_set & b) / max(len(cl_set | b), 1), len(cl_set & b) / max(len(cl_set), 1), len(b))
    ben_dom = hi[hi.label == 0].index.values
    coin_dom = hi[hi.family == "coinminer"].index.values
    sims_b = np.array([sim(reps.get(int(D.tr_map[j])), D.window_calls(int(j))[0]) for j in ben_dom])
    sims_c = np.array([sim(reps.get(int(D.tr_map[j])), D.window_calls(int(j))[0]) for j in coin_dom])
    det_dom = [h_ for h_, r_ in ref_rows.items() if window_stats(r_)["top_name_share"] >= 0.9]
    sims_d = np.array([sim(reps.get(int(D.te_map[ref_rows[h_] - D.ntr])), D.window_calls(ref_rows[h_])[0]) for h_ in det_dom]) if det_dom else np.zeros((0, 3))
    summ = lambda m: {"n_windows": int(len(m)), "jaccard_median": float(np.median(m[:, 0])) if len(m) else None, "jaccard_q25_q75": pct(m[:, 0], [25, 75]) if len(m) else None,
                      "share_of_cluster_resolved_names_found_median": float(np.median(m[:, 1])) if len(m) else None, "n_resolved_names_median": float(np.median(m[:, 2])) if len(m) else None}
    out["step5b"] = {"cluster_resolved_names_in_window": int(len(cl_names)), "cluster_distinct_resolved_names": int(len(cl_set)), "cluster_first_25_resolved_names": cl_names[:25],
                     "similarity_with_january_benign_getprocaddress_windows": summ(sims_b), "similarity_with_january_coinminer_getprocaddress_windows": summ(sims_c),
                     "similarity_with_detected_april_coinminer_getprocaddress_groups": summ(sims_d)}
    # ------------------------------------------------------------------ step 6
    coin_idx = np.where(D.coin)[0]
    gid = pd.factorize(D.hash_apr[coin_idx])[0]
    ng = gid.max() + 1
    res6 = {}
    for f in D.Z:
        fl = D.flag[f][:, coin_idx].astype(float)                                 # [10, n_coin]
        grp = np.stack([np.bincount(gid, weights=fl[s], minlength=ng) / np.bincount(gid, minlength=ng) for s in range(10)])
        res6[f] = {"report_level_tpr_per_seed": fl.mean(1).tolist(), "group_level_tpr_per_seed": grp.mean(1).tolist()}
    keep = ~np.isin(coin_idx, np.where(cl)[0])
    for f in D.Z:
        fl = D.flag[f][:, coin_idx][:, keep].astype(float)
        res6[f]["report_level_tpr_without_cluster_per_seed"] = fl.mean(1).tolist()
    s6 = {"n_reports": int(len(coin_idx)), "n_groups": int(ng), "cluster_share_of_reports": float(cl.sum() / len(coin_idx)), "models": res6}
    for k in ("report_level_tpr_per_seed", "group_level_tpr_per_seed", "report_level_tpr_without_cluster_per_seed"):
        gap_ = np.array(res6["v2_pe"][k]) - np.array(res6["attbal"][k])
        s6["gap_v2pe_minus_attbal_" + k] = {"mean": float(gap_.mean()), "std": float(gap_.std(ddof=1)), "per_seed": gap_.tolist()}
    out["step6"] = s6
    json.dump(out, open(os.path.join(a.out, "coinminer.json"), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    # ------------------------------------------------------------------ figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, mute, bg = "#0b0b0b", "#52514e", "#fcfcfb"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": mute, "axes.labelcolor": ink, "text.color": ink, "xtick.color": mute, "ytick.color": mute, "figure.facecolor": bg, "axes.facecolor": bg})
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4), sharey=False)
    for ax, (f, lbl, col) in zip(axes, (("v2_pe", "v2-PE", BLUE), ("attbal", "ATT+bal", ORANGE))):
        marg = (D.Z[f][:, cl] - D.thr[f][:, None]).ravel()
        ax.hist(marg, bins=70, color=col, alpha=0.8, label=f"cluster reports x 10 seeds ({int(cl.sum())} reports; identical within a seed)")
        x0, x1 = ax.get_xlim()
        ax.axvspan(0, max(x1, 1), color="#dcebdc", alpha=0.7, lw=0, label="detected (logit above the seed's 1% FPR threshold)")
        ax.axvline(0, color=ink, lw=1.4, ls="--", label="threshold (margin 0)")
        ax.set_xlim(x0, max(x1, 1))
        ax.set_xlabel("logit minus the 1% FPR threshold of the same model and seed")
        ax.set_ylabel("reports x seeds")
        ax.set_title(f"{lbl}: detected in {100 * float((marg > 0).mean()):.0f}% of the report-seed pairs; median margin {np.median(marg):+.1f}", loc="left", fontsize=10.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.legend(fontsize=8.3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17))
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out, f"fig1_logits_vs_threshold.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    fig, axes = plt.subplots(4, 1, figsize=(12.5, 9.2), sharex=True)
    seed_col = [BLUE, ORANGE, GREEN]
    ttl = {"cluster_1": "cluster report 1 (hash d91b96b4…)", "cluster_2": "cluster report 2 (its first 512 tokens are identical to report 1)", "cluster_3": "cluster report 3 (identical to report 1)", "detected_coinminer": "a coinminer that ATT+bal detects (in >= 9 of 10 seeds)"}
    for ax, (k, r) in zip(axes, rows4.items()):
        m = seg[k]
        head_end = int((m == -1).sum())
        ax.axvspan(0, head_end, color="#e6e5df", lw=0)
        ax.text(head_end / 2, 0.0, "header", ha="center", va="bottom", fontsize=7.5, color=mute)
        for s in range(3):
            ax.plot(np.arange(512), att[k][s], color=seed_col[s], lw=1.0, label=f"seed {s}")
        ax.axhline(1.0 / 511, color=mute, lw=0.8, ls=":", label="uniform weight 1/511")
        ax.set_ylabel("α (weight)")
        ax.set_title(ttl[k], loc="left", fontsize=9.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ymax = max(att[k][s].max() for s in range(3))
        top = int(np.argmax(att[k][0]))
        ax.annotate(f"max α = {att[k][0].max():.3f}: {S.names[D.names(r)[m[top]]] if m[top] >= 0 else 'header'}", (top, att[k][0].max()), xytext=(top + 15, ymax * 0.98), fontsize=7.8, arrowprops=dict(arrowstyle="-", color=mute, lw=0.6))
    axes[-1].set_xlabel("token position (first 512 tokens)")
    h_, l_ = axes[-1].get_legend_handles_labels()
    fig.legend(h_[:4], l_[:4], fontsize=8.5, frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out, f"fig2_attention.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({"step1": {k: out["step1"][k] for k in ("cluster_size", "groups_in_cluster", "january_reports_with_main_hash", "nearest_january")}, "step2": {k: out["step2"][k] for k in ("cluster_window", "cluster_top_names", "detected_window_stats_median", "detected_share_of_groups_with_top_name_share_ge_0.9")}}, indent=1, default=str)[:3500])


if __name__ == "__main__":
    main()
