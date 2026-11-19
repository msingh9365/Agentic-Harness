"""Insert the audit sections into REPRODUCTION_REPORT.md (5.9a tokenizer note, 5.13) and RESULTS_FOR_REVIEW.md (placeholders AUDIT_T1, AUDIT_T2, AUDIT_MORE), from the generated files of results/review.   (OURS)
    python -m baseline.review_compose; python -m baseline.tune_compose; python -m baseline.audit_compose"""
import json
import os
import re

from baseline.audit_text import APRIL_NOTE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "results", "review")


def read(name, default=""):
    p = os.path.join(R, name)
    return open(p).read().strip() if os.path.exists(p) else default


def counts_table():
    a = json.load(open(os.path.join(R, "audit_cluster.json")))
    lab = {"v2_pe": "v2-PE", "released": "released checkpoint", "attbal": "ATT+bal"}
    rows = []
    for key, nm in (("a3pad", "random padding"), ("a3", "surrogate padding")):
        for pair in ("v2_pe-released", "attbal-released", "attbal-v2_pe"):
            for rate in ("malware TPR", "padded-benign FPR"):
                n = hi = lo = bh = bl = 0
                for k, d in a[key].items():
                    p, s, t, r = k.split("|")
                    if p != pair or r != rate:
                        continue
                    n += 1
                    if d["resolved"]:
                        pos = d["mean"] > 0
                        hi += pos; lo += (not pos)
                        if d.get("cluster", {}).get("resolved"):
                            bh += pos; bl += (not pos)
                x, y = pair.split("-")
                rows.append([nm, f"{lab[x]} − {lab[y]}", rate, n, f"{hi} ({bh})", f"{lo} ({bl})", n - hi - lo])
    head = ["padding", "comparison", "rate", "tests", "first higher (cluster)", "first lower (cluster)", "neither"]
    return "**Duplicate-aware counts for Table 2: tests (edit sets × two thresholds) in which the first model is higher / lower by the descriptive rule (CI excludes 0 and ≥ 7 of 10 seeds on the same side), stratified bootstrap and, in brackets, the cluster bootstrap over hash_apis groups. For the padded-benign FPR higher is worse. All rows: `results/review/audit_cluster.md`.**\n\n" + "\n".join(
        ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def whitebox_cluster():
    t = read("audit_cluster.md")
    return t[t.index("**White-box greedy, 500 reports"):].strip()


def table1_cluster():
    t = read("audit_cluster.md")
    return t[:t.index("**random padding")].strip()


def tokenizer_note():
    d = json.load(open(os.path.join(R, "tokenizer_counts.json")))
    g = lambda n, p: d[f"{n}|{p}"]
    rows = []
    for n, nm in (("ours", "our BPE-50k"), ("released", "released checkpoint tokenizer")):
        for p in ("January", "April"):
            x = g(n, p)
            rows.append(f"| {nm} | {p} | {x['reports']:,} | {x['tokens_in_first_512']:,} | {x['id0_tokens']:,} ({100 * x['share_of_tokens']:.3f}%) | {x['reports_with_any']:,} ({100 * x['share_reports_with_any']:.1f}%) | {x['mean_per_report']:.2f} / {x['median_per_report']:.0f} / {x['p95_per_report']:.0f} / {x['max_per_report']} |")
    s = d["sample_unknown_surfaces_1500_january_reports"]
    tot = sum(s.values())
    return f"""### 5.9a Tokenizer note: unknown pieces get id 0, which is also the padding id (audit)

The SentencePiece models of both tokenizers have `<unk>` = 0 and no padding piece (pad id {d['sentencepiece_pad_id']}); the Nebula pipeline pads with 0. So a piece that is not in the vocabulary is mapped to **the same id as padding**. The letter "j" is not covered by the vocabulary: in a sample of 1,500 January reports {s.get('j', 0):,} of the {tot:,} unknown pieces ({100 * s.get('j', 0) / tot:.1f}%) are a single "j" (the rest: "jj" and two rare strings). Real tokens with id 0 among the first 512 tokens of a report (counted on all January and April reports; `baseline/tokenizer_counts.py`):

| tokenizer | part | reports | tokens in the first 512 | id-0 tokens | reports with at least one | per report: mean / median / p95 / max |
|---|---|---|---|---|---|---|
{chr(10).join(rows)}

Consequences, next to the positional-encoding issue of §5.9: (1) `nn.Embedding(vocab, d)` has no `padding_idx`, so id 0 is one learned vector shared by padding and by unknown pieces; (2) the models of the released code read padding as ordinary tokens; (3) in the attention pooling of §5.10 (ours) the mask is `id != 0`, so real unknown tokens ("j") are treated as padding and get weight 0 in the pooled vector, and the same holds for the "fits in 512" accounting only through token counts, not through ids; (4) a padding attack that inserts pieces containing "j" would be invisible to an id-0 mask. The effect on the numbers is small in size (0.17 to 0.19% of the tokens; 21.7% of April reports have at least one such token) but it is a property of the tokenizer, not of the models; it was not changed here (`unk_fix`: map unknown pieces to a separate id) and is part of the plan of NOTES 17."""


def cluster_summary():
    a = json.load(open(os.path.join(R, "audit_cluster.json")))["table1"]
    f = lambda k: f"{100 * a[k]['mean']:+.2f} (CI [{100 * a[k]['lo']:+.2f}, {100 * a[k]['hi']:+.2f}], above in {a[k]['seeds_above_0']} of 10 seeds)"
    return ("**Consequence for the claim rule.** On the primary metric pAUC@1e-2 the comparisons against the released checkpoint that met the claim rule with the report-level bootstrap do not meet it once duplicates are resampled together: "
            f"v2-PE − released {f('v2_pe-released|pauc@0.01')}; ATT+bal − released {f('attbal-released|pauc@0.01')}. ATT+bal − v2-PE stays unresolved: {f('attbal-v2_pe|pauc@0.01')}. "
            "The robustness differences are far larger than their intervals under either bootstrap (counts below), except where stated. The ATT versus v2-PE / v2 and ATT+bal versus ATT comparisons of §5.10 were not recomputed with the cluster bootstrap.")


def section_513():
    ex = read("extra_headline.md", "(the further robustness tests are described in RESULTS_FOR_REVIEW.md; scoring not finished when this file was generated)")
    reading = read("extra_reading.md")
    vu = read("val_unseen.md")
    return f"""### 5.13 Audit: duplicates, validation overlap, further robustness tests

**Status: preliminary.** Statistics and CPU checks only; no training.

**(a) Duplicate-aware checks (cluster bootstrap over `hash_apis` groups).** April has 17,402 reports in 2,509 distinct API sequences (largest groups 864, 833 and 614 reports); identical sequences get identical scores. The stratified bootstrap of EVAL_PROTOCOL.md treats reports as independent; the cluster bootstrap resamples the (group, class) cells. Table 1 and Table 2 of RESULTS_FOR_REVIEW.md carry both.

{table1_cluster()}

{cluster_summary()}

{counts_table()}

{whitebox_cluster()}

**(b) Validation overlap.** {vu}

Which choices would change: the §5.12 choice (above). The recipe of baseline v2 (§5.7: R8, lr 2e-3, epoch 2 from a grid of 10 recipes on validation TPR@1e-3) and the (lr, epoch) choices of B3 (§5.2c) were made on this slice too; their per-epoch validation logits were not stored (only metrics), so they cannot be recomputed on the unseen part without retraining; they are open. Plan for redoing the §5.12 choice on a group-split slice: NOTES.md section 17 (not run).

**(c) Further robustness tests (CPU, same thresholds and statistics as §5.11).** Rare-API-name padding (calls whose name is among the rarest 20% of the EVAL-pool names by training frequency), block padding (one block of k consecutive calls of an EVAL-pool report), copied calls of the same report, rotation of the call list (the 512-token window then starts later in the report), argument injection (the arguments of the first k calls get the arguments of a random EVAL-pool call appended), k = 5, 20, 50, and the test-time deduplication defence on v2-PE (consecutive identical calls reduced to one, after the edit). The edit builders were checked against full re-tokenisation (0 differences in 150 reports x 23 edit sets, and for the deduplication builder against a dict-level deduplication; with the released tokenizer 60 reports). Edited reports exist in memory only.

{ex}

{reading}

**(d) April.** {APRIL_NOTE}
"""


def sections_results():
    ex = read("extra_headline.md", "(not finished)")
    reading = read("extra_reading.md")
    vu = read("val_unseen.md")
    return f"""## Audit additions (statistics and CPU checks; no training)

**Validation overlap.** {vu.split(chr(10) + chr(10))[0]} Validation tables recomputed on the unseen part only are in REPRODUCTION_REPORT.md §5.13: the models rank differently there (v2-PE pAUC@1e-2 0.962 on the whole slice, 0.975 on the seen part, 0.673 on the 433 unseen reports), and the rule of §5.12 applied to the unseen part would pick (lr 1e-3, p 0.5, epoch 3) instead of (lr 1e-3, p 0.25, epoch 2). Plan for the redo on a group-split slice: NOTES.md section 17 (not run).

**Tokenizer.** Unknown pieces (mostly the letter "j") get id 0, which is also the padding id: 0.17% of the tokens of April, 21.7% of April reports have at least one (REPORT 5.9a).

**Further robustness tests (CPU).** Rare-API-name, block and copied-call padding, rotation of the call list, argument injection and the deduplication defence on v2-PE (definitions and checks in REPORT 5.13 c):

{ex}

{reading}

{APRIL_NOTE}
"""


def main():
    rp = os.path.join(ROOT, "REPRODUCTION_REPORT.md")
    s = open(rp).read()
    t1, t2 = table1_cluster(), counts_table() + "\n\n" + whitebox_cluster()
    s = s.replace("<!--AUDIT_T1-->", "**Duplicate-aware (cluster bootstrap) additions to Table 1.**\n\n" + t1).replace("<!--AUDIT_T2-->", "**Duplicate-aware additions to Table 2.**\n\n" + t2)
    marker = "- attbal vs pebal: not resolved (CI contains 0; positive in 6/10, negative in 4/10 seeds)\n"
    note = ("\n**Duplicate-aware note (audit, §5.13).** With a cluster bootstrap over the hash_apis groups the verdict \"attbal vs released\" above does not meet the claim rule (\"pebal vs released\" and the comparisons with att were not recomputed): "
            + cluster_summary().split("once duplicates are resampled together: ")[1].split(". The robustness")[0] + ".\n")
    s = re.sub(r"\n\*\*Duplicate-aware note \(audit, §5\.13\)\.\*\*[^\n]*\n", "", s)
    if marker in s:
        s = s.replace(marker, marker + note, 1)
    s = re.sub(r"### 5\.9a .*?(?=\n### 5\.10 )", "", s, flags=re.S) if "### 5.9a " in s else s
    s = s.replace("\n### 5.10 ", "\n" + tokenizer_note() + "\n\n### 5.10 ", 1)
    s = re.sub(r"### 5\.13 .*?(?=\n## 6\. )", "", s, flags=re.S) if "### 5.13 " in s else s
    s = s.replace("\n## 6. Differences from the paper", "\n" + section_513() + "\n## 6. Differences from the paper", 1)
    if "<!-- audit-pointer -->" not in s:
        s = s.replace("## 4. How to read the numbers\n", "## 4. How to read the numbers\n\n<!-- audit-pointer -->- **Known issues found in the audit (§5.9a, §5.13).** 94.2% of the validation slice shares its API sequence with the training slice (April: 36.4%), so every choice made on it measures memorisation of seen sequences to a large degree; the unknown id of the tokenizer equals the padding id; confidence intervals that treat reports as independent are too narrow (2,509 distinct API sequences in 17,402 April reports). April was used in 13 scoring rounds (§5.13 d).\n", 1)
    open(rp, "w").write(s)
    rp2 = os.path.join(ROOT, "RESULTS_FOR_REVIEW.md")
    r = open(rp2).read()
    r = r.replace("<!--AUDIT_T1-->", "**Duplicate-aware (cluster bootstrap) additions to Table 1.**\n\n" + t1).replace("<!--AUDIT_T2-->", "**Duplicate-aware additions to Table 2.**\n\n" + t2)
    r = re.sub(r"## Audit additions .*?(?=\n## What is shown)", "", r, flags=re.S) if "## Audit additions" in r else r
    r = r.replace("<!--AUDIT_MORE-->\n\n", "").replace("\n## What is shown and what is not", "\n" + sections_results() + "\n## What is shown and what is not", 1)
    open(rp2, "w").write(r)
    print("audit sections written")


if __name__ == "__main__":
    main()
