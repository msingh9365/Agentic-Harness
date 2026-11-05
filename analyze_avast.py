#!/usr/bin/env python
"""
Tables and plots for the Avast-CTU length study (results/avast/samples.csv),
plus a side-by-side comparison with the Speakeasy results (results/samples.csv).
Writes results/avast/tables.md, results/avast/summary.json, results/avast/plots/.
"""
import json
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyze import length_row, md_table, fmt_cnt, pct, auc, style, THRESH, BLUE, ORANGE, AQUA, INK, INK2, SURF
from measure_avast import VARIANTS

R = "results/avast"
NAMES = {"A": "A: resolved_apis + mutexes (Nebula notebook)", "B": "B: all 13 behavior.summary lists"}
CAPS = [8, 16, 32, 64]


def main():
    S = pd.read_csv(os.path.join(R, "samples.csv"), low_memory=False)
    plots = os.path.join(R, "plots")
    os.makedirs(plots, exist_ok=True)
    md, summ = [], {}

    md.append("## Avast sample accounting\n\n")
    md.append(S.groupby(["split", "status"]).size().unstack(fill_value=0).to_markdown() + "\n")
    ok = S[S.status == "ok"].copy()
    md.append(f"\nReports measured (status ok): {len(ok):,} of {len(S):,}. Split by detection date "
              f"(< 2019-08-01 = trainset), as in Nebula's Avast notebook.\n")
    for v in VARIANTS:
        md.append(f"\nVariant {v}: field attribution exact for {fmt_cnt(int(ok[f'{v}_field_attr_exact'].sum()), len(ok))}\n")

    # ---- overall
    md.append("\n## Avast tokens per sample (no truncation)\n\n")
    rows = {}
    for v in VARIANTS:
        for sp in ["all", "trainset", "testset"]:
            sub = ok if sp == "all" else ok[ok.split == sp]
            rows[f"{v} / {sp}"] = length_row(sub[f"{v}_tokens"])
        summ[v] = rows[f"{v} / all"]
    md.append(md_table(rows, "variant / set"))
    for v in VARIANTS:
        t = ok[f"{v}_tokens"].values.astype(float)
        f = np.clip(t - 512, 0, None) / t
        md.append(f"\nVariant {v}: mean per-sample fraction dropped {100*f.mean():.1f}%, median {100*np.median(f):.1f}%.\n")

    # ---- family
    md.append("\n## Avast tokens per sample by family (variant A)\n")
    for sp in ["trainset", "testset"]:
        sub = ok[ok.split == sp]
        rows = {f: length_row(g["A_tokens"]) for f, g in sub.groupby("family")}
        md.append(f"\n### Avast {sp} (variant A)\n\n" + md_table(rows, "family"))
    md.append("\n## Avast tokens per sample by family (variant B, all splits)\n\n")
    rows = {f: length_row(g["B_tokens"]) for f, g in ok.groupby("family")}
    md.append(md_table(rows, "family"))

    # ---- fields
    md.append("\n## Avast: which fields survive the 512 cut\n")
    for v, fields in VARIANTS.items():
        md.append(f"\n### Avast fields, variant {v}\n\n")
        md.append(f"Field order in the sequence: `{' → '.join(fields)}`.\n\n")
        md.append("| field | samples with field | median list length | tokens (all samples) | share of all tokens | "
                  "% of field tokens kept by 512 cut | samples where field fully cut |\n|---|---|---|---|---|---|---|\n")
        tot = ok[[f"{v}_tok_{f}" for f in fields]].sum().sum()
        for f in fields:
            n_items = ok[f"n_{f}"]
            has = n_items > 0
            tok, kept = ok[f"{v}_tok_{f}"], ok[f"{v}_kept_{f}"]
            md.append(f"| {f} | {fmt_cnt(int(has.sum()), len(ok))} | {np.median(n_items[has]) if has.any() else 0:,.0f} | "
                      f"{tok.sum():,.0f} | {pct(tok.sum(), tot):.1f}% | {pct(kept.sum(), tok.sum()):.1f}% | "
                      f"{fmt_cnt(int(((kept == 0) & has).sum()), int(has.sum()))} |\n")
        md.append("\nField tokens include the field's key name; a field with an empty list still costs its key name.\n")

    # ---- chunks
    md.append("\n## Avast: fixed 512-token chunks needed\n\n")
    md.append("| variant | median | p90 | p99 | max | " + " | ".join(f"≤{c} chunks" for c in CAPS) +
              " |\n|---|---|---|---|---|" + "---|" * len(CAPS) + "\n")
    for v in VARIANTS:
        c = ok[f"{v}_chunks_fixed"]
        md.append(f"| {v} | {np.median(c):,.0f} | {np.percentile(c,90):,.0f} | {np.percentile(c,99):,.0f} | {c.max():,} | "
                  + " | ".join(fmt_cnt(int((c <= k).sum()), len(ok)) for k in CAPS) + " |\n")
    md.append("\nShare of all tokens covered by the first K chunks:\n\n| variant | K=1 (=Nebula) | K=4 | K=8 | K=16 | K=32 |\n|---|---|---|---|---|---|\n")
    for v in VARIANTS:
        t = ok[f"{v}_tokens"]
        md.append(f"| {v} | " + " | ".join(f"{pct(np.minimum(t, 512*k).sum(), t.sum()):.1f}%" for k in [1, 4, 8, 16, 32]) + " |\n")
    md.append("\nThe reduced reports have no process tree and no per-process call sequence, so the "
              "entry-point / per-process chunking of the Speakeasy study cannot be measured on them.\n")

    # ---- length as shortcut (all samples are malware: family one-vs-rest)
    md.append("\n## Avast: length as a family shortcut\n\n"
              "There are no benign samples. ROC AUC of token count for one family vs all other families "
              "(0.5 = no signal; far from 0.5 either way = length alone separates the family).\n\n")
    md.append("| family | n | median A tokens train | median A tokens test | AUC(A tokens) train | AUC(A tokens) test | "
              "AUC(min(A,512)) test | AUC(B tokens) test |\n|---|---|---|---|---|---|---|---|\n")
    for f in sorted(ok.family.unique()):
        tr, te = ok[ok.split == "trainset"], ok[ok.split == "testset"]
        def a(df, col, cap=None):
            sc = df[col].clip(upper=cap) if cap else df[col]
            y = (df.family == f).astype(int)
            return auc(sc, y) if 0 < y.sum() < len(y) else float("nan")
        mtr = tr[tr.family == f].A_tokens; mte = te[te.family == f].A_tokens
        md.append(f"| {f} | {(ok.family == f).sum():,} | {np.median(mtr) if len(mtr) else float('nan'):,.0f} | "
                  f"{np.median(mte) if len(mte) else float('nan'):,.0f} | {a(tr,'A_tokens'):.3f} | {a(te,'A_tokens'):.3f} | "
                  f"{a(te,'A_tokens',512):.3f} | {a(te,'B_tokens'):.3f} |\n")
    md.append("\n`nan` = the family has no samples in that split.\n")

    # ---- comparison with Speakeasy
    sp_path = "results/samples.csv"
    if os.path.exists(sp_path):
        Sp = pd.read_csv(sp_path, usecols=["status", "tokens", "chunks_fixed"])
        Sp = Sp[Sp.status == "ok"]
        md.append("\n## Sandbox comparison\n\n")
        md.append("| dataset / preprocessing | samples | median tokens | p90 | p99 | >512 | tokens dropped by 512 cut | "
                  "fixed chunks p99 | ≤8 chunks |\n|---|---|---|---|---|---|---|---|---|\n")
        def line(name, t, c):
            t = np.asarray(t, float)
            md.append(f"| {name} | {len(t):,} | {np.median(t):,.0f} | {np.percentile(t,90):,.0f} | {np.percentile(t,99):,.0f} | "
                      f"{fmt_cnt(int((t > 512).sum()), len(t))} | {pct(np.clip(t-512,0,None).sum(), t.sum()):.1f}% | "
                      f"{np.percentile(c,99):,.0f} | {fmt_cnt(int((np.asarray(c) <= 8).sum()), len(t))} |\n")
        line("Speakeasy (quovadis), Nebula pipeline", Sp.tokens, Sp.chunks_fixed)
        line("Avast-CTU CAPEv2, variant A", ok.A_tokens, ok.A_chunks_fixed)
        line("Avast-CTU CAPEv2, variant B", ok.B_tokens, ok.B_chunks_fixed)

    with open(os.path.join(R, "tables.md"), "w") as fh:
        fh.write("# Generated tables for Avast-CTU (analyze_avast.py)\n\n" + "".join(md))
    with open(os.path.join(R, "summary.json"), "w") as fh:
        json.dump(summ, fh, indent=2, default=float)

    # ================= plots
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
                         "axes.labelcolor": INK2, "text.color": INK, "figure.facecolor": SURF})
    fig, ax = plt.subplots(figsize=(8, 4.2)); style(ax)
    allt = np.concatenate([ok.A_tokens.values, ok.B_tokens.values]).clip(min=1)
    bins = np.logspace(0, np.log10(allt.max() + 1), 80)
    for v, c in [("A", ORANGE), ("B", BLUE)]:
        ax.hist(ok[f"{v}_tokens"].clip(lower=1), bins=bins, histtype="step", lw=2, color=c, label=NAMES[v])
    ax.axvline(512, color=INK, lw=1.5, ls="--"); ax.text(512 * 1.08, ax.get_ylim()[1] * 0.92, "512 (Nebula cut)", fontsize=9)
    ax.set_xscale("log"); ax.set_xlabel("tokens per report (log scale)"); ax.set_ylabel("reports")
    ax.set_title(f"Avast-CTU CAPEv2: tokens per report (n={len(ok):,})"); ax.legend(frameon=False, loc="upper left", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(plots, "hist_tokens.png"), dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.2)); style(ax)
    for v, c in [("A", ORANGE), ("B", BLUE)]:
        x = np.sort(ok[f"{v}_tokens"].values)
        ax.plot(x, np.arange(1, len(x) + 1) / len(x), color=c, lw=2, label=NAMES[v])
    if os.path.exists(sp_path):
        x = np.sort(Sp.tokens.values)
        ax.plot(x, np.arange(1, len(x) + 1) / len(x), color=INK2, lw=2, ls="--", label="Speakeasy (for comparison)")
    ax.axvline(512, color=INK, lw=1.5, ls="--")
    ax.set_xscale("log"); ax.set_ylim(0, 1); ax.set_xlabel("tokens per report (log scale)"); ax.set_ylabel("share of reports ≤ x")
    ax.set_title("CDF of tokens per report: Avast vs Speakeasy"); ax.legend(frameon=False, loc="upper left", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(plots, "cdf_tokens.png"), dpi=150); plt.close(fig)

    fams = ok.groupby("family").A_tokens.median().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(9, 4.6)); style(ax)
    bp = ax.boxplot([ok[ok.family == f].A_tokens.clip(lower=1).values for f in fams], whis=(5, 95), showfliers=False,
                    patch_artist=True, widths=0.55, medianprops=dict(color=INK, lw=1.5))
    for p in bp["boxes"]:
        p.set_facecolor(ORANGE); p.set_alpha(0.8); p.set_edgecolor(INK2)
    ax.axhline(512, color=INK, lw=1.5, ls="--"); ax.text(0.6, 512 * 1.1, "512", fontsize=9)
    ax.set_yscale("log"); ax.set_xticks(range(1, len(fams) + 1), [f"{f}\n(n={int((ok.family==f).sum()):,})" for f in fams], fontsize=8)
    ax.set_ylabel("tokens per report (log)"); ax.set_title("Avast-CTU, variant A: tokens by family (box p25–p75, whiskers p5–p95)")
    fig.tight_layout(); fig.savefig(os.path.join(plots, "box_family.png"), dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw={"width_ratios": [1, 2.2]})
    for ax, v in zip(axes, ["A", "B"]):
        style(ax)
        fields = VARIANTS[v]
        vals = [pct(ok[f"{v}_kept_{f}"].sum(), ok[f"{v}_tok_{f}"].sum()) for f in fields]
        y = np.arange(len(fields))
        ax.barh(y, vals, color=AQUA if v == "A" else BLUE, height=0.6)
        for yi, val in zip(y, vals):
            ax.text(min(val, 100) + 1, yi, f"{val:.1f}%", va="center", fontsize=8)
        ax.set_yticks(y, fields, fontsize=8); ax.invert_yaxis(); ax.set_xlim(0, 115)
        ax.set_title(f"variant {v}", fontsize=10); ax.set_xlabel("% of field tokens in first 512")
    fig.suptitle("Avast-CTU: how much of each field survives the 512 cut (top = first in sequence)", fontweight="bold", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(plots, "field_kept.png"), dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.2)); style(ax)
    mx = int(max(ok.A_chunks_fixed.max(), ok.B_chunks_fixed.max()))
    bins = np.unique(np.concatenate([np.arange(1, 17), np.logspace(np.log10(17), np.log10(mx + 2), 40).astype(int)]))
    for v, c in [("A", ORANGE), ("B", BLUE)]:
        ax.hist(ok[f"{v}_chunks_fixed"], bins=bins, histtype="step", lw=2, color=c, label=NAMES[v])
    for c in CAPS:
        ax.axvline(c, color=INK2, lw=1, ls=":")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("fixed 512-token chunks needed (log)"); ax.set_ylabel("reports (log)")
    ax.set_title("Avast-CTU: 512-token chunks needed per report"); ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(plots, "hist_chunks.png"), dpi=150); plt.close(fig)
    print("wrote", os.path.join(R, "tables.md"), "and plots in", plots)


if __name__ == "__main__":
    main()
