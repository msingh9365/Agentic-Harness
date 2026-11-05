#!/usr/bin/env python
"""
Copy a few example samples from the raw dataset into examples/ and show what
Nebula's preprocessing does to each one.

For every chosen sample three files are written:
  <name>.raw.json        the file exactly as stored in the dataset (verbatim copy)
  <name>.nebula.json     output of PEDynamicFeatureExtractor.filter_and_normalize_report()
  <name>.tokens.txt      the BPE tokens Nebula's tokenizer produces, with the
                         start of each field and the 512-token cut marked

Choice of samples (deterministic, from results/samples.csv):
  * one "typical" sample per split x family: token count closest to the
    median of that split/family, ties broken by the smallest file;
  * three special cases used in REPORT.md (see SPECIAL below).
"""
import argparse
import json
import os
import shutil

import pandas as pd

from measure_lengths import Nebula, field_segments, list_files, SEQ_LEN


def choose(S):
    S = S.copy()
    S["dist"] = (S.tokens - S.groupby(["split", "family"]).tokens.transform("median")).abs()
    typical = (S.sort_values(["dist", "file_bytes"]).groupby(["split", "family"]).head(1)
               .sort_values(["split", "family"]))
    picks = [(r, "typical: token count closest to the median of its split/family") for _, r in typical.iterrows()]

    special = [
        (S[S.n_entry_points == 102],
         "special: 102 entry points (1 module_entry + 101 threads), the case that breaks one-chunk-per-entry-point"),
        (S[S.field_order.str.count(r"\|") >= 3],
         "special: has all four fields (registry_access, network_events.traffic, file_access, apis)"),
        (S[(S.family == "clean") & S.n_entry_points.between(2, 5) & (S.n_ep_tokenized > 0)]
         .assign(d=lambda d: (d.tokens - S[S.family == "clean"].tokens.median()).abs())
         .sort_values("d"),
         "special: benign sample with several entry points, length near the clean median"),
    ]
    for df, why in special:
        df = df.sort_values("d") if "d" in df else df.sort_values("file_bytes")
        picks.append((df.iloc[0], why))
    return picks


def token_view(nb, report):
    keys, segs = field_segments(report)
    pieces = [nb.tokenizer.tokenizer.encode_as_pieces(nb.tokenizer.clear_json_event(s)) for s in segs]
    ids_full = nb.ids(report)
    assert sum(len(p) for p in pieces) == len(ids_full)
    total = len(ids_full)
    lines = [f"# total tokens: {total}   kept by Nebula (first {SEQ_LEN}): {min(total, SEQ_LEN)}   "
             f"dropped: {max(0, total - SEQ_LEN)}",
             "# '▁' marks the start of a word. Numbers on the left are token positions.", ""]
    pos = 0
    for k, p in zip(keys, pieces):
        lines.append(f"## field: {k}  (tokens {pos}..{pos + len(p) - 1}, {len(p)} tokens)")
        row = []
        for tok in p:
            if pos == SEQ_LEN:
                if row:
                    lines.append(f"{pos - len(row):6d}  " + " ".join(row)); row = []
                lines.append("")
                lines.append(f"-------- 512-token cut: Nebula never sees token {SEQ_LEN} and later --------")
                lines.append("")
            row.append(tok)
            pos += 1
            if len(row) == 16:
                lines.append(f"{pos - 16:6d}  " + " ".join(row)); row = []
        if row:
            lines.append(f"{pos - len(row):6d}  " + " ".join(row))
        lines.append("")
    return "\n".join(lines) + "\n"


README_HEAD = """# Example samples from dtrizna/quovadis-speakeasy

These are a few real samples from the dataset, copied so you can see what the
data looks like before and after Nebula's preprocessing. They were picked by
`make_examples.py`, which chooses them in a fixed way (no hand-picking):

* **typical**: one per split and family. Its token count is the closest to the
  median of that split/family, so it looks like an "average" sample there.
* **special**: three cases that matter in REPORT.md.

These files are Speakeasy **emulation reports** (JSON text that describes what a
program did). They are not the malware programs themselves and cannot run.
The dataset is Apache-2.0 licensed.

## The three files per sample

`<name>` is the sample's file name in the dataset without `.json`: usually
`<sha256>.dat`, and for `windows_syswow64` the Windows program name
(for example `iscsicpl`).

| file | what it is |
|---|---|
| `<name>.raw.json` | The file exactly as stored in the dataset. It is a JSON **list of entry points**. Most samples have one entry point (`module_entry`, the program's main code). Some also have `thread` entry points (threads the program started) or `tls_callback_*`. Each entry point has `apis` (the API calls made, in order, each with `api_name`, `args`, `ret_val` and the address `pc`) and, when present, `file_access`, `registry_access`, `network_events`, `process_events`, `dropped_files`, and `error` (why emulation stopped, for example `max_api_count`). |
| `<name>.nebula.json` | The output of Nebula's `filter_and_normalize_report()`. All entry points are merged and only four fields are kept: `registry_access`, `network_events.traffic`, `file_access`, `apis` (in this order; `apis` is always last). Inside them only some sub-fields are kept (for `apis`: `api_name`, `args`, `ret_val`). Paths and IPs are normalised (for example `<drive>`, `<sha256>`), and strange characters are removed from the arguments. |
| `<name>.tokens.txt` | What Nebula's BPE tokenizer turns the filtered report into. The text is lower-cased, punctuation becomes spaces, and some words (`api_name`, `args`, `path`, ...) are removed before it is cut into tokens. `▁` marks the start of a word. Each field starts with a `## field:` line, and a line marks the **512-token cut**: Nebula never sees anything after it. |

**How to read a sample quickly:** open `tokens.txt` and look at the header
line (total tokens, how many are kept, how many are dropped). Then find the
cut line to see where in the API sequence Nebula stops reading.

## The samples
"""

README_TAIL = """
Columns: `tokens` = Nebula tokens before the 512 cut; `entry points` = how many
entry points the raw file has; `API calls` = raw API calls over all entry
points; `hit cap` = 1 if Speakeasy stopped because of `max_api_count` (500);
`fields` = fields in the filtered report, in the order Nebula puts them.
All numbers are also in `index.csv` and in `../results/samples.csv`.
"""


def write_readme(out, index):
    rows = ["| split | family | label | tokens | entry points | API calls | hit cap | fields | raw size | why | files |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in index:
        f = r["file"]
        rows.append(f"| {r['split']} | {r['family']} | {r['label']} | {r['tokens']:,} | {r['entry_points']} | "
                    f"{r['api_calls']:,} | {r['hit_cap']} | {r['fields']} | {r['raw_kb']} KB | {r['why']} | "
                    f"[raw]({f}.raw.json) · [nebula]({f}.nebula.json) · [tokens]({f}.tokens.txt) |")
    with open(os.path.join(out, "README.md"), "w") as fh:
        fh.write(README_HEAD + "\n".join(rows) + "\n" + README_TAIL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nebula", default=os.environ.get("NEBULA_ROOT", "../nebula"))
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out", default="examples")
    args = ap.parse_args()

    S = pd.read_csv("results/samples.csv")
    paths = {(sp, fold.replace("report_", ""), os.path.splitext(name)[0]): p
             for sp, fold, name, p in list_files(args.data_dir) if name.endswith(".json")}
    nb = Nebula(args.nebula)
    if os.path.isdir(args.out):
        shutil.rmtree(args.out)

    index = []
    for r, why in choose(S):
        src = paths[(r.split, r.family, r.sample_id)]
        d = os.path.join(args.out, r.split, r.family)
        os.makedirs(d, exist_ok=True)
        base = os.path.join(d, r.sample_id)
        shutil.copyfile(src, base + ".raw.json")
        with open(src) as f:
            eps = json.load(f)
        rep = nb.report(eps)
        with open(base + ".nebula.json", "w") as f:
            json.dump(rep, f, indent=1)
        with open(base + ".tokens.txt", "w") as f:
            f.write(token_view(nb, rep))
        assert nb.n_tokens(rep) == r.tokens  # same number as in results/samples.csv
        index.append(dict(split=r.split, family=r.family, label="malware" if r.is_malware else "benign",
                          file=os.path.relpath(base, args.out), tokens=int(r.tokens),
                          entry_points=int(r.n_entry_points), api_calls=int(r.n_apis_raw),
                          hit_cap=int(r.hit_api_cap), fields=r.field_order.replace("|", " → "),
                          raw_kb=round(r.file_bytes / 1024, 1), why=why))

    pd.DataFrame(index).to_csv(os.path.join(args.out, "index.csv"), index=False)
    write_readme(args.out, index)
    print(pd.DataFrame(index)[["split", "family", "tokens", "entry_points", "fields", "raw_kb"]].to_string())


if __name__ == "__main__":
    main()
