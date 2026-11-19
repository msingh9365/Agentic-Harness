#!/usr/bin/env python
"""
Builds results/round5/README.md from the result files of results/round5 (tables are cut out of the .md / .json files; the verdict is in verdict.md).

    python scripts/round5/build_readme.py
"""
import json
import os
import re
import sys


OUT = "results/round5"


def read(name):
    p = f"{OUT}/{name}"
    return open(p).read() if os.path.exists(p) else None


def js(name):
    p = f"{OUT}/{name}"
    return json.load(open(p)) if os.path.exists(p) else None


def section(text, header, level="## "):
    """the block under `header` (up to the next header of the same level), without the header line."""
    if text is None:
        return "(not available)"
    m = re.search(r"^" + re.escape(level + header) + r"[^\n]*\n(.*?)(?=^" + re.escape(level) + r"|\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else "(not available)"


def table_rows(tbl, keep=None, drop=None):
    """filter the rows of a markdown table by a predicate on the first two cells."""
    lines = tbl.splitlines()
    head, sep, rows = lines[:2], lines[2:3], lines[2:]
    out = []
    for ln in rows[1:] if rows and set(rows[0].replace("|", "").strip()) <= set("- ") else rows:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if keep and not keep(cells):
            continue
        out.append(ln)
    return "\n".join(head + out)


def md_from_rows(header, rows):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(r) + " |" for r in rows])


def pad_table(name, ftag="1%", subset="all", cols=(0, 2, 3, 4, 5, 6, 7, 8), extra=None):
    d = js(f"{name}.json")
    if d is None:
        return "(not available)"
    L = d["labels"]
    key = "tpr" if subset == "all" else "tpr_fit512"
    rows = []
    for m, v in d[key][ftag].items():
        rows.append([m] + [("-" if v[i] is None else f"{100 * v[i]:.1f}%") for i in cols])
    return md_from_rows(["model"] + [L[i] for i in cols], rows)


def fpr_table(name, ftag="1%", cols=(0, 2, 3, 4, 5, 6, 7, 8)):
    d = js(f"{name}.json")
    if d is None:
        return "(not available)"
    L = d["labels"]
    rows = [[m] + [f"{100 * v[i]:.2f}%" for i in cols] for m, v in d["fpr_benign"][ftag].items()]
    return md_from_rows(["model"] + [L[i] for i in cols], rows)


def main():
    parts = []
    A = lambda s: parts.append(s)
    verdict = read("verdict.md") or "(verdict not written yet)"
    A("# Round 5: final-quality runs of ATT+bal and the tests an examiner will ask for\n")
    A(read("intro.md") or "")
    A("## Verdict\n")
    A(verdict)
    A("\n" + (read("gpu.md") or ""))
    # ---- item 1
    acc = read("accuracy.md")
    sel = lambda c: c[1] in ("ATT+bal", "MM+bal", "C+bal", "C (J, 2 epochs)", "C (J)", "A (J)", "released Nebula", "ATT+bal + LightGBM", "MM+bal + LightGBM", "C+bal + LightGBM",
                            "C (J, 2 epochs) + LightGBM", "C (J) + LightGBM", "A (J) + LightGBM", "released Nebula + LightGBM", "LightGBM bag of API names",
                            "ATT+bal (ensemble)", "MM+bal (ensemble)", "C+bal (ensemble)", "C (J) (ensemble)", "A (J) (ensemble)", "C (J, 2 epochs) (ensemble)")
    A("\n## Item 1: final accuracy, 10 seeds (epoch 2 of the G1 runs)\n")
    A("Single models: mean over 10 seeds (released: one model); `+ LightGBM`: percentile rank average with the bag-of-API LightGBM (seeds 0-2 as seed mod 3); `(ensemble)`: mean logit of the 10 seeds. "
      "Thresholds (a) at 1% / 0.1% FPR of the April benign scores of each model and seed; intervals: group bootstrap over April hash_apis (1,000 resamples). "
      "All subsets (seen, unseen, distance quartiles, 1 / 2-3 / 4-8 chunks), seed spread and all paired differences are in `accuracy.md`.\n")
    A(table_rows(section(acc, "Overall and by number of chunks"), keep=lambda c: c[0] == "all" and sel(c)))
    A("\nSeed-paired differences (mean over the 10 seeds [95% over seeds]; TPR in points):\n")
    A(section(acc, "Seed-paired differences (all April reports, mean over seeds [95% over seeds]; TPR in points)"))
    pd_ = section(acc, "Paired differences with group-bootstrap intervals (TPR in points)")
    A("\nATT+bal against the released Nebula and the other models, group-bootstrap intervals (all April reports, and the subsets that matter):\n")
    A(table_rows(pd_, keep=lambda c: c[0] in ("ATT+bal − released Nebula", "ATT+bal (ensemble) − released Nebula", "ATT+bal + LightGBM − released Nebula + LightGBM", "ATT+bal − A (J)", "ATT+bal − C (J)",
                                              "ATT+bal − MM+bal", "ATT+bal − C+bal") and c[1] in ("all", "seen", "unseen", "1 chunk", "2-3 chunks", "4-8 chunks")))
    a4 = read("accuracy_epoch4.md")
    A("\nAt 4 epochs (second table, `accuracy_epoch4.md`; the 2-epoch results above are primary):\n")
    A(table_rows(section(a4, "Overall and by number of chunks"), keep=lambda c: c[0] == "all" and c[1] in ("ATT+bal", "MM+bal", "C+bal", "ATT+bal (ensemble)", "ATT+bal + LightGBM")))
    # ---- item 2
    lf = read("lowfpr_april.md")
    A("\n## Item 2: low-FPR, measured more stably\n")
    A("### Benign reports above the thresholds (April)\n")
    A(section(lf, "Benign reports above the thresholds (April)"))
    A("\n### TPR when 4 / 8 / 12 benign reports may lie above the threshold (April)\n")
    A(section(lf, "TPR when 4 / 8 / 12 benign reports may lie above the threshold (April)"))
    A("\n### Standardised partial AUC up to 1% FPR (McClish), April\n")
    A(section(lf, "Standardised partial AUC up to 1% FPR (McClish; 0.5 = chance, 1 = perfect), April"))
    jv = read("janval.md")
    A("\n### Second test set: the January validation side (regime S models, G2)\n")
    A((jv or "").split("## January validation side")[0].split("\n", 2)[-1].strip())
    A("\n" + section(jv, "January validation side").split("Paired differences")[0].strip())
    A("\nPaired differences on the validation side:\n")
    A(re.search(r"Paired differences \(January validation side\)\n\n(.*?)\n\n", jv or "", re.S).group(1) if jv else "")
    tb = read("top_benign.md")
    A("\n### The 20 highest-scoring April benign reports\n")
    A("Full lists (first 30 calls of every report) in `top_benign.md`. Comparison:\n")
    A(tb.split("## Comparison")[-1].strip() if tb else "")
    # ---- item 3
    A("\n## Item 3: padding the models have never seen\n")
    A("Malware April reports (9,399) are edited, and 2,000 random benign April reports are edited the same way; k = 1, 5, 20, 50; thresholds fixed at 1% and 0.1% FPR on the unedited April benign "
      "scores of each model and seed; mean over seeds (released: one model; the retrained models: seeds 0-4); edited reports exist in memory only. Cells: **insert 20 | prepend 20 | prepend 50** "
      "(unedited in the second column). Complete tables for every variant (all k, changes with group-bootstrap and seed-paired intervals, 'fits in 512 tokens') are in the `pad_*.md` files.\n")
    variants = [("block", "3a block of 20 / 50 consecutive calls of one benign report"), ("syswow", "3b other benign source (windows_syswow64 only)"), ("clean", "3b source clean only"),
                ("rare", "3b rarest 20% of API names of the TRAIN pool"), ("sur_lgb", "3c top-ranked calls of the LightGBM surrogate"), ("sur_c", "3c top-ranked calls of the C (J) surrogate")]
    models = ["released Nebula", "A (J)", "C (J)", "C+bal", "MM+bal", "ATT+bal"]

    def cell(d, kind, ftag, m, pct=True):
        v = d[kind][ftag].get(m)
        if v is None:
            return "-"
        f = (lambda x: f"{100 * x:.1f}") if kind != "fpr_benign" else (lambda x: f"{100 * x:.1f}")
        return f"{f(v[0])} → {f(v[3])} \\| {f(v[7])} \\| {f(v[8])}"

    for ftag, kind, title in (("1%", "tpr", "Malware TPR (%) at the threshold of 1% FPR"), ("0.1%", "tpr", "Malware TPR (%) at the threshold of 0.1% FPR"),
                              ("1%", "fpr_benign", "FPR (%) of the padded benign reports at the 1% threshold (1% by construction without padding)")):
        rows = []
        for v, txt in variants:
            d = js(f"pad_{v}.json")
            if d is None:
                continue
            L = d["labels"]
            rows.append([txt] + [("-" if d[kind][ftag].get(m) is None else
                                  " \\| ".join(f"{100 * d[kind][ftag][m][i]:.1f}" for i in (4, 7, 8)) + f" (unedited {100 * d[kind][ftag][m][0]:.1f})") for m in models])
        A(f"\n**{title}** (insert 20 | prepend 20 | prepend 50):\n")
        A(md_from_rows(["padding"] + models, rows))
    at = read("attack_whitebox.md")
    A("\n### 3d. Chosen to look benign: white-box greedy padding\n")
    A("500 random April malware reports; each model (one seed, attacked with its own scores) greedily prepends up to 20 EVAL-pool calls, each step the best of 200 random candidates; a report stops being attacked below the 1% threshold and then counts as evaded at both thresholds. "
      "TPR of the 500 reports after k prepended calls, threshold of 1% FPR:\n")
    A(section(at, "TPR of the 500 reports at the threshold of 1% FPR after k prepended calls"))
    A("\nThreshold of 0.1% FPR:\n")
    A(section(at, "TPR of the 500 reports at the threshold of 0.1% FPR after k prepended calls"))
    # ---- item 4
    rot = read("rotation.md")
    A("\n## Item 4: rotation check\n")
    A("Every April report (17,402) is rotated in memory. (a) *window*: the real tokens of the model's window (first 512; 4,096 for F and G3) are rotated at a call boundary by 25 / 50 / 75%, so the last calls come first (a position test: same tokens, different order). "
      "(b) *whole*: the full call list is rotated by the fraction, re-tokenised, and the first 512 (4,096) tokens taken (a 'where is the signal' test: the window sees different calls). Thresholds fixed at 1% / 0.1% FPR on the unedited April benign scores; "
      "seeds: released 1, A (J) and C (J) 5, F 3, ATT+bal 10, G3 5. Malware TPR at the threshold of 1% FPR:\n")
    A(section(rot, "Malware TPR at the threshold of 1% FPR, all"))
    A("\nChange in points [group 95%]:\n")
    A(re.search(r"Change in points \[group 95%\], all\n\n(.*?)\n\n", rot or "", re.S).group(1) if rot else "")
    A("\nOn the 6,359 reports that fit in 512 tokens (rotation only reorders; TPR at 1% FPR):\n")
    A(section(rot, "Malware TPR at the threshold of 1% FPR, fits in 512 tokens"))
    A("\nAUC (all reports; benign reports rotated too):\n")
    A(section(rot, "AUC (all reports)"))
    A("\nThresholds of 0.1% FPR, longer-report subset and seed-paired differences are in `rotation.md`.\n")
    # ---- item 5
    A("\n## Item 5: the round-4 padding and copied-call tables for the 10-seed models\n")
    ge = read("graded_edits.md")
    A("Same models and seeds as item 1 (released 1 model; A (J), C (J), C (J, 2 epochs), ATT+bal, MM+bal, C+bal 10 seeds each). Thresholds fixed at 1% (and 0.1%, in the .md files) FPR on the unedited April benign scores.\n")
    A("### Copied calls: insert k / prepend k calls copied from the same report (the edits of `results/robustness` item 1)\n")
    A("Malware TPR at the 1% threshold after the edit (all April malware):\n")
    A(section(ge, "Threshold of 1% FPR: malware TPR after the edit (all April malware)"))
    A("\nBenign FPR at the 1% threshold after the same edit of the benign reports:\n")
    A(re.search(r"Benign FPR after the same edit of the benign reports \(all April benign\)\n\n(.*?)\n\n", ge or "", re.S).group(1) if ge else "")
    A("\n### Random benign-call padding (the round-4 test; random single calls of the EVAL pool)\n")
    A("Malware TPR (%) at the thresholds of 1% / 0.1% FPR after the edit, and FPR (%) of the 2,000 padded benign reports (1% threshold); cells: insert 20 | prepend 20 | prepend 50 (unedited in brackets):\n")
    d = js("pad_random.json")
    if d:
        rows = []
        for m in d["tpr"]["1%"]:
            g = lambda kind, ft: " \\| ".join(f"{100 * d[kind][ft][m][i]:.1f}" for i in (4, 7, 8)) + f" ({100 * d[kind][ft][m][0]:.1f})"
            rows.append([m, g("tpr", "1%"), g("tpr", "0.1%"), g("fpr_benign", "1%")])
        A(md_from_rows(["model", "TPR at 1% FPR", "TPR at 0.1% FPR", "padded benign FPR at 1%"], rows))
    A("\nAll k, 'fits in 512 tokens' subsets, changes with intervals and the seed-paired differences: `pad_random.md`, `graded_edits.md`.\n")
    # ---- G3
    g3 = read("g3_accuracy.md")
    A("\n## G3: ATT+bal over the whole report\n")
    A(read("g3.md") or "")
    A(table_rows(g3 or "", keep=lambda c: len(c) > 3 and c[0] == "all") if g3 else "(not available)")
    A("\nRotation of G3 is in the table of item 4; random benign-call padding (threshold 1% FPR, cells insert 20 | prepend 20 | prepend 50; benign FPR in the second row):\n")
    d = js("pad_random_g3.json")
    if d:
        m = list(d["tpr"]["1%"])[0]
        g = lambda kind, ft: " \\| ".join(f"{100 * d[kind][ft][m][i]:.1f}" for i in (4, 7, 8)) + f" ({100 * d[kind][ft][m][0]:.1f})"
        A(md_from_rows(["model", "TPR at 1% FPR", "TPR at 0.1% FPR", "padded benign FPR at 1%"], [[m, g("tpr", "1%"), g("tpr", "0.1%"), g("fpr_benign", "1%")]]))
    A("\n" + (read("caveats.md") or ""))
    open(f"{OUT}/README.md", "w").write("\n".join(parts) + "\n")
    print("README written,", sum(len(p) for p in parts), "characters")


if __name__ == "__main__":
    main()
