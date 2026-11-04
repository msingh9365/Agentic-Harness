#!/usr/bin/env python
"""
Turn results/samples.csv(.gz) and results/entry_points.csv(.gz) into
markdown tables (results/tables.md), a JSON of key numbers
(results/summary.json) and the plots in results/plots/.

Every number in REPORT.md is copied from results/tables.md.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIELDS = ["registry_access", "network_events.traffic", "file_access", "apis"]
THRESH = [512, 1024, 2048, 4096, 8192]
CHUNK_CAPS = [16, 32, 64]

# reference palette (light mode) from the dataviz skill
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def read(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            return pd.read_csv(p, low_memory=False)
    raise FileNotFoundError(path)


def pct(a, b):
    return 100.0 * a / b if b else float("nan")


def fmt_cnt(c, n):
    return f"{pct(c, n):.1f}% ({c:,})"


def length_row(t):
    t = np.asarray(t, dtype=float)
    n = len(t)
    row = {"n": f"{n:,}",
           "median": f"{np.median(t):,.0f}",
           "p75": f"{np.percentile(t, 75):,.0f}",
           "p90": f"{np.percentile(t, 90):,.0f}",
           "p99": f"{np.percentile(t, 99):,.0f}",
           "max": f"{t.max():,.0f}"}
    for th in THRESH:
        row[f">{th}"] = fmt_cnt(int((t > th).sum()), n)
    tot = t.sum()
    dropped = np.clip(t - 512, 0, None).sum()
    row["tokens dropped by 512 cut"] = f"{pct(dropped, tot):.1f}% ({dropped:,.0f} of {tot:,.0f})"
    return row


def md_table(rows, index_name):
    if not rows:
        return "_(empty)_\n"
    cols = list(next(iter(rows.values())).keys())
    out = "| " + index_name + " | " + " | ".join(cols) + " |\n"
    out += "|" + "---|" * (len(cols) + 1) + "\n"
    for k, r in rows.items():
        out += f"| {k} | " + " | ".join(str(r[c]) for c in cols) + " |\n"
    return out


def auc(score, y):
    """ROC AUC of a raw score (Mann-Whitney U, ties averaged)."""
    s = pd.Series(score).rank(method="average").values
    y = np.asarray(y)
    n1, n0 = (y == 1).sum(), (y == 0).sum()
    return (s[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--prefix", default="")
    args = ap.parse_args()
    R = args.results
    S = read(os.path.join(R, f"{args.prefix}samples.csv"))
    E = read(os.path.join(R, f"{args.prefix}entry_points.csv"))
    plots = os.path.join(R, "plots")
    os.makedirs(plots, exist_ok=True)
    md = []
    summ = {}

    # ---------------- status / counts
    md.append("## Sample accounting\n")
    st = S.groupby(["split", "status"]).size().unstack(fill_value=0)
    md.append(st.to_markdown() + "\n")
    shapes = S.groupby(["split", "file_shape"]).size().unstack(fill_value=0) if "file_shape" in S else None
    if shapes is not None:
        md.append("\nTop-level JSON type of each file:\n\n" + shapes.to_markdown() + "\n")
    ok = S[S.status == "ok"].copy()
    summ["n_files"] = int(len(S))
    summ["n_ok"] = int(len(ok))
    md.append(f"\nSamples measured (status ok): {len(ok):,} of {len(S):,} files.\n")
    md.append(f"\nField attribution exact (concatenated field token ids == full token ids): "
              f"{fmt_cnt(int(ok.field_attr_exact.sum()), len(ok))}\n")

    # ---------------- 7. overall
    md.append("\n## Tokens per sample (Nebula preprocessing, no truncation)\n")
    rows = {"all": length_row(ok.tokens)}
    for sp in sorted(ok.split.unique()):
        rows[sp] = length_row(ok[ok.split == sp].tokens)
    md.append(md_table(rows, "set"))
    t = ok.tokens.values
    summ["overall"] = rows["all"]
    frac_dropped = (np.clip(t - 512, 0, None) / t)
    md.append(f"\nMean per-sample fraction of tokens dropped by the 512 cut: {100*frac_dropped.mean():.1f}%; "
              f"median per-sample fraction: {100*np.median(frac_dropped):.1f}%.\n")

    # ---------------- 8. by family x split
    md.append("\n## Tokens per sample by family and split\n")
    for sp in sorted(ok.split.unique()):
        sub = ok[ok.split == sp]
        rows = {f: length_row(g.tokens) for f, g in sub.groupby("family")}
        md.append(f"\n### {sp}\n\n" + md_table(rows, "family"))

    # ---------------- 11. malware vs benign
    md.append("\n## Malware vs benign\n")
    rows = {}
    for sp in ["all"] + sorted(ok.split.unique()):
        sub = ok if sp == "all" else ok[ok.split == sp]
        for lab, name in [(1, "malware"), (0, "benign")]:
            g = sub[sub.is_malware == lab]
            rows[f"{sp} / {name}"] = {
                "n": f"{len(g):,}",
                "median tokens": f"{np.median(g.tokens):,.0f}",
                "mean tokens": f"{g.tokens.mean():,.0f}",
                ">512": fmt_cnt(int((g.tokens > 512).sum()), len(g)),
                "median entry points": f"{np.median(g.n_entry_points):,.0f}",
                "median chunks (per-EP)": f"{np.median(g.chunks_per_ep):,.0f}",
            }
    md.append(md_table(rows, "split / class"))
    md.append("\nROC AUC of a classifier that uses ONLY the length (higher = malware); 0.5 = no signal:\n\n")
    md.append("| set | AUC(tokens) | AUC(min(tokens,512)) | AUC(n_entry_points) |\n|---|---|---|---|\n")
    for sp in ["all"] + sorted(ok.split.unique()):
        sub = ok if sp == "all" else ok[ok.split == sp]
        a1 = auc(sub.tokens, sub.is_malware)
        a2 = auc(sub.tokens.clip(upper=512), sub.is_malware)
        a3 = auc(sub.n_entry_points, sub.is_malware)
        summ[f"auc_{sp}"] = [a1, a2, a3]
        md.append(f"| {sp} | {a1:.3f} | {a2:.3f} | {a3:.3f} |\n")
    md.append("\nNumber of real (non-pad) tokens Nebula sees, min(tokens, 512):\n\n")
    md.append("| set | class | median | share of samples with < 512 real tokens (i.e. padded) |\n|---|---|---|---|\n")
    for sp in ["all"] + sorted(ok.split.unique()):
        sub = ok if sp == "all" else ok[ok.split == sp]
        for lab, name in [(1, "malware"), (0, "benign")]:
            g = sub[sub.is_malware == lab]
            md.append(f"| {sp} | {name} | {np.median(g.tokens.clip(upper=512)):,.0f} | "
                      f"{fmt_cnt(int((g.tokens < 512).sum()), len(g))} |\n")

    # ---------------- 9. fields
    md.append("\n## Which fields survive the 512 cut\n")
    orders = ok.field_order.value_counts()
    md.append("\nField order actually found in the tokenized reports (all distinct orders):\n\n")
    md.append("| field order (left = first in sequence) | samples |\n|---|---|\n")
    for o, c in orders.items():
        md.append(f"| `{o}` | {c:,} |\n")
    rows = {}
    totals = ok.tokens.sum()
    for f in FIELDS:
        tc, kc = f"tok_{f}", f"kept_{f}"
        has = ok[tc].fillna(0) > 0
        tok = ok[tc].fillna(0)
        kept = ok[kc].fillna(0)
        rows[f] = {
            "samples with field": fmt_cnt(int(has.sum()), len(ok)),
            "tokens (all samples)": f"{tok.sum():,.0f}",
            "share of all tokens": f"{pct(tok.sum(), totals):.1f}%",
            "median tokens (when present)": f"{np.median(tok[has]):,.0f}" if has.any() else "-",
            "% of field tokens kept by 512 cut": f"{pct(kept.sum(), tok.sum()):.1f}% ({kept.sum():,.0f})",
            "samples where field fully kept": fmt_cnt(int(((kept == tok) & has).sum()), int(has.sum())),
            "samples where field fully cut": fmt_cnt(int(((kept == 0) & has).sum()), int(has.sum())),
        }
    md.append("\n" + md_table(rows, "field"))
    md.append("\n'samples where field fully kept / cut' are out of the samples that have the field. "
              "Field tokens include the field's own key name (e.g. `file access`).\n")
    # composition of the kept 512 tokens
    kept_tot = ok[[f"kept_{f}" for f in FIELDS]].fillna(0).sum()
    md.append("\nComposition of the tokens Nebula actually keeps (sum over samples of the first ≤512 tokens):\n\n")
    md.append("| field | kept tokens | share of kept |\n|---|---|---|\n")
    for f in FIELDS:
        md.append(f"| {f} | {kept_tot[f'kept_{f}']:,.0f} | {pct(kept_tot[f'kept_{f}'], kept_tot.sum()):.1f}% |\n")
    # same split long/short
    long = ok[ok.tokens > 512]
    md.append(f"\nFor the {len(long):,} samples longer than 512 tokens only:\n\n")
    md.append("| field | samples with field | % of field tokens kept | samples where field fully cut |\n|---|---|---|---|\n")
    kept_share = {}
    for f in FIELDS:
        tok = long[f"tok_{f}"].fillna(0); kept = long[f"kept_{f}"].fillna(0); has = tok > 0
        kept_share[f] = pct(kept.sum(), tok.sum())
        md.append(f"| {f} | {fmt_cnt(int(has.sum()), len(long))} | {kept_share[f]:.1f}% | "
                  f"{fmt_cnt(int(((kept == 0) & has).sum()), int(has.sum()))} |\n")

    # ---------------- 10. entry points
    md.append("\n## Entry points\n")
    Eok = E[E.status == "ok"]
    md.append("\nEntry-point tokenization status:\n\n" + E.status.value_counts().to_frame("entry points").to_markdown() + "\n")
    nep = ok.n_entry_points
    md.append("\n| quantity | median | p75 | p90 | p99 | max | mean |\n|---|---|---|---|---|---|---|\n")
    def q(x, name):
        x = np.asarray(x, dtype=float)
        return (f"| {name} | {np.median(x):,.0f} | {np.percentile(x,75):,.0f} | {np.percentile(x,90):,.0f} | "
                f"{np.percentile(x,99):,.0f} | {x.max():,.0f} | {x.mean():,.1f} |\n")
    md.append(q(nep, "entry points per sample"))
    md.append(q(ok.n_thread, "thread entry points per sample"))
    md.append(q(Eok.tokens, "tokens per entry point (tokenized alone)"))
    md.append(q(Eok[Eok.ep_type == "module_entry"].tokens, "tokens per module_entry"))
    md.append(q(Eok[Eok.ep_type == "thread"].tokens, "tokens per thread"))
    md.append(q(ok.ep_tokens_sum, "sum of per-EP tokens per sample"))
    md.append(q(ok.chunks_fixed, "chunks needed, (a) fixed 512"))
    md.append(q(ok.chunks_per_ep, "chunks needed, (b) per-EP, 512/overlap 64"))
    md.append(f"\nSamples with more than one entry point: {fmt_cnt(int((nep > 1).sum()), len(ok))}\n")
    md.append(f"\nEntry points longer than 512 tokens: {fmt_cnt(int((Eok.tokens > 512).sum()), len(Eok))} "
              f"(module_entry: {fmt_cnt(int(((Eok.ep_type=='module_entry') & (Eok.tokens > 512)).sum()), int((Eok.ep_type=='module_entry').sum()))}; "
              f"thread: {fmt_cnt(int(((Eok.ep_type=='thread') & (Eok.tokens > 512)).sum()), int((Eok.ep_type=='thread').sum()))})\n")
    md.append(f"\nSamples with at least one entry point longer than 512 tokens: "
              f"{fmt_cnt(int((ok.ep_tokens_max > 512).sum()), len(ok))}\n")
    md.append("\nEntry-point counts by family (all splits):\n\n| family | samples | median EPs | p90 EPs | max EPs | samples with >1 EP |\n|---|---|---|---|---|---|\n")
    for f, g in ok.groupby("family"):
        md.append(f"| {f} | {len(g):,} | {np.median(g.n_entry_points):,.0f} | {np.percentile(g.n_entry_points,90):,.0f} | "
                  f"{g.n_entry_points.max():,} | {fmt_cnt(int((g.n_entry_points>1).sum()), len(g))} |\n")
    md.append("\nShare of samples that fit within a given number of 512-token chunks:\n\n")
    md.append("| set | scheme | " + " | ".join(f"≤{c} chunks" for c in CHUNK_CAPS) + " |\n|---|---|" + "---|" * len(CHUNK_CAPS) + "\n")
    for sp in ["all"] + sorted(ok.split.unique()):
        sub = ok if sp == "all" else ok[ok.split == sp]
        for col, name in [("chunks_fixed", "(a) fixed 512"), ("chunks_per_ep", "(b) per entry point")]:
            md.append(f"| {sp} | {name} | " + " | ".join(fmt_cnt(int((sub[col] <= c).sum()), len(sub)) for c in CHUNK_CAPS) + " |\n")
    md.append("\nCoverage if the model only reads the first K chunks (share of all tokens covered):\n\n")
    md.append("| scheme | K=1 (=Nebula) | K=16 | K=32 | K=64 |\n|---|---|---|---|---|\n")
    tot = ok.tokens.sum()
    md.append("| (a) fixed 512 | " + " | ".join(f"{pct(np.minimum(ok.tokens, 512*k).sum(), tot):.1f}%" for k in [1,16,32,64]) + " |\n")
    # (b): tokens are per-EP; covering first K chunks in EP order
    Es = Eok.sort_values(["sample_id", "split", "ep_index"]).copy()
    Es["cum_chunks"] = Es.groupby(["split", "sample_id"]).chunks.cumsum()
    Es["prev_chunks"] = Es.cum_chunks - Es.chunks
    tot_ep = Es.tokens.sum()
    cov = []
    for k in [1, 16, 32, 64]:
        # entry points fully inside the budget count fully; the one straddling the
        # budget counts its first (k - prev) pieces (stride 448 after the first 512)
        room = (k - Es.prev_chunks).clip(lower=0)
        covered = np.where(room >= Es.chunks, Es.tokens,
                           np.where(room == 0, 0, np.minimum(Es.tokens, 512 + (room - 1) * 448)))
        cov.append(pct(covered.sum(), tot_ep))
    md.append("| (b) per entry point | " + " | ".join(f"{c:.1f}%" for c in cov) + " |\n")
    md.append("\n(b) coverage is measured on the sum of per-EP tokens, in entry-point order; "
              "overlap tokens are not double counted.\n")

    # ---------------- per-family chunks
    md.append("\nChunks needed by family (all splits):\n\n| family | median (a) | p90 (a) | median (b) | p90 (b) | (b) ≤32 chunks |\n|---|---|---|---|---|---|\n")
    for f, g in ok.groupby("family"):
        md.append(f"| {f} | {np.median(g.chunks_fixed):,.0f} | {np.percentile(g.chunks_fixed,90):,.0f} | "
                  f"{np.median(g.chunks_per_ep):,.0f} | {np.percentile(g.chunks_per_ep,90):,.0f} | "
                  f"{fmt_cnt(int((g.chunks_per_ep<=32).sum()), len(g))} |\n")

    # ---------------- emulation cap (Speakeasy max_api_count = 500)
    if "hit_api_cap" in ok:
        md.append("\n## Emulation cap (Speakeasy `max_api_count` = 500 in the dataset's config)\n")
        md.append("\n| set | samples that hit the API cap | median tokens (hit cap) | median tokens (no cap) | "
                  "median raw API calls |\n|---|---|---|---|---|\n")
        for name, sub in [("all", ok)] + [(f, g) for f, g in ok.groupby("family")]:
            hit = sub.hit_api_cap == 1
            md.append(f"| {name} | {fmt_cnt(int(hit.sum()), len(sub))} | "
                      f"{np.median(sub[hit].tokens) if hit.any() else float('nan'):,.0f} | "
                      f"{np.median(sub[~hit].tokens) if (~hit).any() else float('nan'):,.0f} | "
                      f"{np.median(sub.n_apis_raw):,.0f} |\n")
        long = ok.tokens > 512
        md.append(f"\nOf the samples longer than 512 tokens, {fmt_cnt(int((ok[long].hit_api_cap == 1).sum()), int(long.sum()))} "
                  f"hit the emulation cap.\n")
        if "n_apis" in Eok:
            w = Eok[Eok.n_apis > 0]
            md.append(f"\nTokens per raw API call (entry points with ≥1 API call): median "
                      f"{np.median(w.tokens / w.n_apis):.2f}, p10 {np.percentile(w.tokens / w.n_apis, 10):.2f}, "
                      f"p90 {np.percentile(w.tokens / w.n_apis, 90):.2f}. Entry points with ≥500 API calls: "
                      f"{fmt_cnt(int((Eok.n_apis >= 500).sum()), len(Eok))}.\n")

    with open(os.path.join(R, "tables.md"), "w") as fh:
        fh.write("# Generated tables (analyze.py)\n\n" + "".join(md))
    with open(os.path.join(R, "summary.json"), "w") as fh:
        json.dump(summ, fh, indent=2, default=float)

    # ================= plots
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
                         "axes.labelcolor": INK2, "text.color": INK, "figure.facecolor": SURF})
    t = ok.tokens.values

    # 1 histogram, log x
    fig, ax = plt.subplots(figsize=(8, 4.2)); style(ax)
    bins = np.logspace(0, np.log10(t.max() + 1), 80)
    ax.hist(t[ok.is_malware == 1], bins=bins, color=ORANGE, alpha=0.75, label=f"malware (n={int((ok.is_malware==1).sum()):,})")
    ax.hist(t[ok.is_malware == 0], bins=bins, color=BLUE, alpha=0.75, label=f"benign (n={int((ok.is_malware==0).sum()):,})")
    ax.axvline(512, color=INK, lw=1.5, ls="--"); ax.text(512 * 1.08, ax.get_ylim()[1] * 0.92, "512 (Nebula cut)", color=INK, fontsize=9)
    ax.set_xscale("log"); ax.set_xlabel("tokens per sample after Nebula filtering + BPE (log scale)"); ax.set_ylabel("samples")
    ax.set_title("Tokens per sample"); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(plots, "hist_tokens.png"), dpi=150); plt.close(fig)

    # 2 CDF
    fig, ax = plt.subplots(figsize=(8, 4.2)); style(ax)
    for lab, name, c in [(None, "all", INK), (1, "malware", ORANGE), (0, "benign", BLUE)]:
        x = np.sort(t if lab is None else ok[ok.is_malware == lab].tokens.values)
        ax.plot(x, np.arange(1, len(x) + 1) / len(x), color=c, lw=2, label=name)
    for th in [512, 2048, 8192]:
        ax.axvline(th, color=INK2, lw=1, ls=":")
        ax.text(th * 1.05, 0.03, str(th), color=INK2, fontsize=8)
    ax.axvline(512, color=INK, lw=1.5, ls="--")
    ax.set_xscale("log"); ax.set_ylim(0, 1); ax.set_xlabel("tokens per sample (log scale)"); ax.set_ylabel("share of samples ≤ x")
    ax.set_title("CDF of tokens per sample"); ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(plots, "cdf_tokens.png"), dpi=150); plt.close(fig)

    # 3 box per family
    fams = ok.groupby("family").tokens.median().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(9, 4.6)); style(ax)
    data = [ok[ok.family == f].tokens.clip(lower=1).values for f in fams]
    bp = ax.boxplot(data, whis=(5, 95), showfliers=False, patch_artist=True, widths=0.55,
                    medianprops=dict(color=INK, lw=1.5))
    benign = {"clean", "windows_syswow64"}
    for patch, f in zip(bp["boxes"], fams):
        patch.set_facecolor(BLUE if f in benign else ORANGE); patch.set_alpha(0.8); patch.set_edgecolor(INK2)
    ax.axhline(512, color=INK, lw=1.5, ls="--"); ax.text(0.6, 512 * 1.1, "512", fontsize=9)
    ax.set_yscale("log"); ax.set_xticks(range(1, len(fams) + 1), [f"{f}\n(n={int((ok.family==f).sum()):,})" for f in fams], fontsize=8)
    ax.set_ylabel("tokens per sample (log)"); ax.set_title("Tokens per sample by family (box = p25–p75, whiskers = p5–p95; blue = benign)")
    fig.tight_layout(); fig.savefig(os.path.join(plots, "box_family.png"), dpi=150); plt.close(fig)

    # 4 field kept
    fig, ax = plt.subplots(figsize=(8, 3.8)); style(ax)
    all_share = [pct(ok[f"kept_{f}"].fillna(0).sum(), ok[f"tok_{f}"].fillna(0).sum()) for f in FIELDS]
    long_share = [kept_share[f] for f in FIELDS]
    y = np.arange(len(FIELDS)); h = 0.38
    ax.barh(y - h / 2, all_share, h, color=BLUE, label="all samples")
    ax.barh(y + h / 2, long_share, h, color=ORANGE, label="samples > 512 tokens")
    for yi, v in zip(y - h / 2, all_share): ax.text(v + 1, yi, f"{v:.1f}%", va="center", fontsize=9, color=INK)
    for yi, v in zip(y + h / 2, long_share): ax.text(v + 1, yi, f"{v:.1f}%", va="center", fontsize=9, color=INK)
    ax.set_yticks(y, FIELDS); ax.invert_yaxis(); ax.set_xlim(0, 110); ax.set_xlabel("% of the field's tokens inside the first 512")
    ax.set_title("How much of each field survives the 512-token cut"); ax.legend(frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(plots, "field_kept.png"), dpi=150); plt.close(fig)

    # 5 chunks histogram
    fig, ax = plt.subplots(figsize=(8, 4.2)); style(ax)
    mx = int(max(ok.chunks_fixed.max(), ok.chunks_per_ep.max()))
    bins = np.unique(np.concatenate([np.arange(1, 17), np.logspace(np.log10(17), np.log10(mx + 2), 40).astype(int)]))
    ax.hist(ok.chunks_fixed, bins=bins, color=BLUE, alpha=0.75, label="(a) fixed 512-token chunks")
    ax.hist(ok.chunks_per_ep, bins=bins, color=ORANGE, alpha=0.6, label="(b) one chunk per entry point (512, overlap 64)")
    for c in CHUNK_CAPS:
        ax.axvline(c, color=INK2, lw=1, ls=":"); ax.text(c * 1.05, ax.get_ylim()[1] * 0.9, str(c), color=INK2, fontsize=8)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("chunks needed per sample (log)"); ax.set_ylabel("samples (log)")
    ax.set_title("512-token chunks needed per sample"); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(plots, "hist_chunks.png"), dpi=150); plt.close(fig)
    print("wrote", os.path.join(R, "tables.md"), "and plots in", plots)


if __name__ == "__main__":
    main()
