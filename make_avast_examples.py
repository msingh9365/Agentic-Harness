#!/usr/bin/env python
"""
Copy example reports from the Avast-CTU CAPEv2 dataset (reduced reports) into
examples/avast/ and show what the variant-A preprocessing (Nebula's Avast
notebook: resolved_apis + mutexes, lower-cased) and the Avast BPE tokenizer
make of each one.

One "typical" report per split x family: token count (variant A) closest to
the median of that split/family, ties broken by the smallest file.

Per report:
  <sha256>.raw.json      verbatim copy of the reduced CAPE report
  <sha256>.nebula.json   the variant-A record that is tokenized
  <sha256>.tokens.txt    BPE tokens, start of each field and the 512 cut marked
"""
import argparse
import json
import os
import shutil

import pandas as pd

from measure_avast import bootstrap_nebula, make_tokenizer, record, read_summary, SUMMARY_FIELDS
from measure_lengths import field_segments, SEQ_LEN


def token_view(tok, rec):
    keys, segs = field_segments(rec)
    pieces = [tok.tokenizer.encode_as_pieces(tok.clear_json_event(s)) for s in segs]
    total = len(tok.encode(rec, pad=False)[0])
    assert sum(len(p) for p in pieces) == total
    lines = [f"# total tokens: {total}   kept by Nebula (first {SEQ_LEN}): {min(total, SEQ_LEN)}   "
             f"dropped: {max(0, total - SEQ_LEN)}",
             "# tokenizer: Avast BPE (50k) trained with Nebula's JSONTokenizerBPE.train() on the Avast training split",
             "# '▁' marks the start of a word. Numbers on the left are token positions.", ""]
    pos = 0
    for k, p in zip(keys, pieces):
        lines.append(f"## field: {k}  (tokens {pos}..{pos + len(p) - 1}, {len(p)} tokens)")
        row = []
        for t in p:
            if pos == SEQ_LEN:
                if row:
                    lines.append(f"{pos - len(row):6d}  " + " ".join(row)); row = []
                lines += ["", f"-------- 512-token cut: Nebula never sees token {SEQ_LEN} and later --------", ""]
            row.append(t); pos += 1
            if len(row) == 16:
                lines.append(f"{pos - 16:6d}  " + " ".join(row)); row = []
        if row:
            lines.append(f"{pos - len(row):6d}  " + " ".join(row))
        lines.append("")
    return "\n".join(lines) + "\n"


HEAD = """# Example reports from the Avast-CTU Public CAPEv2 dataset

Reduced CAPEv2 sandbox reports (MIT licence; <https://github.com/avast/avast-ctu-cape-dataset>).
Every report in this dataset is **malware**; there are no benign samples. The
reports are text logs of what a program did in the sandbox; they are not the
programs themselves.

Picked by `make_avast_examples.py`: one report per split and family whose
variant-A token count is closest to the median of that split/family. The split
is by detection date, as in Nebula's Avast notebook (before 2019-08-01 =
trainset).

## The three files per report

| file | what it is |
|---|---|
| `<sha256>.raw.json` | The reduced report exactly as stored in the dataset. It has `behavior.summary` (13 lists: `keys`, `resolved_apis`, `executed_commands`, `write_keys`, `files`, `read_files`, `started_services`, `created_services`, `write_files`, `delete_keys`, `read_keys`, `delete_files`, `mutexes`) and `static.pe` (PE header information). **Unlike Speakeasy there is no time-ordered API call sequence and no list of processes**: `resolved_apis` is the set of API names the program looked up, not the calls in order. |
| `<sha256>.nebula.json` | Variant A, the record that is tokenized: `resolved_apis` then `mutexes`, every value lower-cased (this is what Nebula's Avast notebook does). Variant B of the study (all 13 summary lists) is not shown here. |
| `<sha256>.tokens.txt` | The BPE tokens of that record, from a 50k tokenizer trained on the Avast training split with Nebula's own `JSONTokenizerBPE.train()`. Each field starts with a `## field:` line and the **512-token cut** is marked. Because `resolved_apis` comes first, the cut usually removes the mutexes too. |

## The reports
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nebula", default=os.environ.get("NEBULA_ROOT", "../nebula"))
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--tok-dir", default="results/avast/tokenizer")
    ap.add_argument("--out", default="examples/avast")
    args = ap.parse_args()

    S = pd.read_csv("results/avast/samples.csv")
    S = S[S.status == "ok"].copy()
    S["dist"] = (S.A_tokens - S.groupby(["split", "family"]).A_tokens.transform("median")).abs()
    picks = S.sort_values(["dist", "file_bytes"]).groupby(["split", "family"]).head(1).sort_values(["split", "family"])

    nb = bootstrap_nebula(args.nebula)
    tok = make_tokenizer(nb, args.tok_dir, "A")
    if os.path.isdir(args.out):
        shutil.rmtree(args.out)
    rows = ["| split | family | type | date | A tokens | resolved_apis | mutexes | raw size | files |",
            "|---|---|---|---|---|---|---|---|---|"]
    index = []
    for r in picks.itertuples():
        src = os.path.join(args.data_dir, "public_small_reports", r.sha256 + ".json")
        d = os.path.join(args.out, r.split, r.family)
        os.makedirs(d, exist_ok=True)
        base = os.path.join(d, r.sha256)
        shutil.copyfile(src, base + ".raw.json")
        rec = record(read_summary(src), "A")
        with open(base + ".nebula.json", "w") as f:
            json.dump(rec, f, indent=1)
        with open(base + ".tokens.txt", "w") as f:
            f.write(token_view(tok, rec))
        assert len(tok.encode(rec, pad=False)[0]) == r.A_tokens
        rel = os.path.relpath(base, args.out)
        rows.append(f"| {r.split} | {r.family} | {r.type} | {r.date} | {int(r.A_tokens):,} | {int(r.n_resolved_apis)} | "
                    f"{int(r.n_mutexes)} | {r.file_bytes/1024:.1f} KB | [raw]({rel}.raw.json) · "
                    f"[record]({rel}.nebula.json) · [tokens]({rel}.tokens.txt) |")
        index.append(dict(split=r.split, family=r.family, type=r.type, date=r.date, sha256=r.sha256,
                          A_tokens=int(r.A_tokens), B_tokens=int(r.B_tokens), file_bytes=int(r.file_bytes)))
    pd.DataFrame(index).to_csv(os.path.join(args.out, "index.csv"), index=False)
    with open(os.path.join(args.out, "README.md"), "w") as fh:
        fh.write(HEAD + "\n".join(rows) + "\n\n`resolved_apis` and `mutexes` columns = number of list entries "
                 "in the raw report. All numbers are also in `index.csv` and `../../results/avast/samples.csv`.\n")
    print(f"wrote {len(index)} examples to {args.out}")


if __name__ == "__main__":
    main()
