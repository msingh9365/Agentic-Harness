"""
P1 of NOTES 24, second part (CPU kernel): WHICH strings become the unknown id 0 in the real reports?   (OURS; the authors' functions do the filtering and the cleaning, SentencePiece the encoding)

    python -m baseline.gs_unk_strings --out /kaggle/working/out [--limit N]

Filters all 92,700 reports (as baseline/preprocess.py, same cache logic as gs_tokrepro), cleans str(report) with the OLD tokenizer (variants/bpe50k of the dataset of the old tokenizer) and encodes every
whitespace-separated word of the cleaned text alone (BPE never merges across spaces, so this gives the same ids as encoding the whole report). A word is "unknown" if one of its ids is 0.
Per population (January, April) and class (malware, benign): reports, reports with >= 1 unknown token, unknown tokens in total, and the TOP unknown words and the TOP unknown characters (a character is unknown
when SentencePiece encodes it alone to id 0), each with its count, the number of reports that contain it, and for the words an example raw snippet is NOT stored (no report text is saved; only the cleaned
words and characters that become id 0, counts only). Output: unk_strings.json, unk_strings.md. No score, no model, no April label used for any choice.
"""
import argparse
import collections
import json
import os
import pickle
import time
import unicodedata

import numpy as np

from baseline import common as C
from baseline import preprocess as P

TOP = 40


def count(events, tok, cache, wcount, ccount, wreps, creps):
    """events -> per report: number of unknown tokens. cache: word -> (n_unknown_ids, [unknown characters])"""
    sp = tok.tokenizer
    per_report = np.zeros(len(events), dtype=np.int32)
    for i, ev in enumerate(events):
        words = tok.clear_json_event(str(ev)).split()
        new = [w for w in set(words) if w not in cache]
        if new:
            enc = sp.encode_as_ids(new)
            for w, ids in zip(new, enc):
                n0 = sum(1 for t in ids if t == 0)
                chars = []
                if n0:
                    for ch in set(w):
                        if 0 in sp.encode_as_ids(ch):
                            chars.append(ch)
                cache[w] = (n0, chars)
        seen_w, seen_c, n = set(), set(), 0
        for w in words:
            n0, chars = cache[w]
            if n0:
                n += n0
                wcount[w] += 1
                if w not in seen_w:
                    seen_w.add(w)
                    wreps[w] += 1
                for ch in chars:
                    ccount[ch] += w.count(ch)
                    if ch not in seen_c:
                        seen_c.add(ch)
                        creps[ch] += 1
        per_report[i] = n
    return per_report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int, default=None, help="files per folder (smoke test only)")
    ap.add_argument("--work", default="/tmp/nebula_events")
    a = ap.parse_args()
    t0 = time.time()
    info = C.setup_nebula(None, require_patched=False)
    data = C.find_data_root()
    old_dir = C.find_dir_with("all.npz")
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    ev = {}
    for split in ("train", "test"):
        cache = os.path.join(a.work, f"{split}_{a.limit}.pkl")
        if os.path.exists(cache):
            ev[split] = pickle.load(open(cache, "rb"))
            continue
        t = time.time()
        ev[split] = P.filter_split(os.path.join(data, f"windows_emulation_{split}set"), info["nebula_root"], a.workers, a.limit)
        pickle.dump(ev[split], open(cache, "wb"), protocol=4)
        print(f"[{split}] {len(ev[split][0])} reports filtered in {(time.time() - t) / 60:.1f} min", flush=True)
    (ev_tr, ym_tr, _), (ev_te, ym_te, _) = ev["train"], ev["test"]
    lab = np.load(os.path.join(old_dir, "labels.npz"))
    if a.limit is None:
        assert np.array_equal(lab["ym_train"], ym_tr) and np.array_equal(lab["ym_test"], ym_te), "labels differ from the published ones"
        assert len(ev_tr) == 75298 and len(ev_te) == 17402
        y = {"January": lab["y_train"].astype(int), "April": lab["y_test"].astype(int)}
    else:
        y = {"January": (np.asarray(ym_tr) != 0).astype(int), "April": (np.asarray(ym_te) != 0).astype(int)}     # smoke test: placeholder classes
    vd = C.find_dir_with("tokenizer.model")                    # the OLD tokenizer (bpe50k; dataset gs-old-tokenizer: tokenizer.model, vocab.json, info.json copied from baseline_models/tokenizers/bpe50k)
    assert json.load(open(os.path.join(vd, "vocab.json"))) == json.load(open(os.path.join(old_dir, "variants", "bpe50k", "vocab.json"))), "tokenizer vocabulary differs from the old one"
    tok = P.build_tokenizer(P.VARIANTS["bpe50k"], info["nebula_root"], model_path=os.path.join(vd, "tokenizer.model"), vocab_file=os.path.join(vd, "vocab.json"))
    cache = {}
    res, md = {}, ["### P1 (second part): the strings that become the unknown id 0 (old tokenizer; cleaned words, counts only; no report text is stored)", ""]
    for pop, events in (("January", ev_tr), ("April", ev_te)):
        for cls, name in ((None, "all"), (1, "malware"), (0, "benign")):
            idx = np.arange(len(events)) if cls is None else np.where(y[pop] == cls)[0]
            wcount, ccount, wreps, creps = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
            per = count([events[i] for i in idx], tok, cache, wcount, ccount, wreps, creps)
            key = f"{pop}|{name}"
            res[key] = {"reports": int(len(idx)), "share_with_unknown_pct": float(100 * (per > 0).mean()), "median_count": float(np.median(per)), "mean_count": float(per.mean()), "unknown_tokens": int(per.sum()),
                        "top_words": [[w, int(c), int(wreps[w])] for w, c in wcount.most_common(TOP)],
                        "top_chars": [[ch, f"U+{ord(ch):04X}", unicodedata.name(ch, "?"), int(c), int(creps[ch])] for ch, c in ccount.most_common(TOP)]}
            print(f"[{key}] {len(idx)} reports, {res[key]['share_with_unknown_pct']:.2f}% with unknown, mean {per.mean():.3f}, {time.time() - t0:.0f}s", flush=True)
    for key, r in res.items():
        md += [f"#### {key}: {r['reports']} reports, {r['share_with_unknown_pct']:.2f}% with >= 1 unknown token, mean count {r['mean_count']:.3f}, median {r['median_count']:g}, {r['unknown_tokens']} unknown tokens in total", "",
               "| rank | unknown word (cleaned, first 60 characters) | occurrences | reports |", "|---|---|---|---|"]
        md += [f"| {k + 1} | `{w[:60]}` | {c} | {n} |" for k, (w, c, n) in enumerate(r["top_words"][:15])]
        md += ["", "| rank | character | code point | name | occurrences (in unknown words) | reports |", "|---|---|---|---|---|---|"]
        md += [f"| {k + 1} | `{ch}` | {cp} | {nm} | {c} | {n} |" for k, (ch, cp, nm, c, n) in enumerate(r["top_chars"][:15])]
        md += [""]
    json.dump(res, open(os.path.join(a.out, "unk_strings.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(a.out, "unk_strings.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md[:60]), flush=True)
    print(f"done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
