"""Tokenizer note (audit item 3): how many real tokens within the first 512 positions of a report get id 0 (SentencePiece <unk> = 0, which the models also use as padding), per report and overall, for all January and April
reports, for our BPE-50k and the tokenizer of the released checkpoint; and which characters they are (sample of 1,500 January reports).   python -m baseline.tokenizer_counts"""
import collections
import json
import os

import numpy as np

from baseline import callstore as CS, make_pad

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    tr, te = make_pad.load_row_map()
    n_tr = len(tr)
    out = {}
    for name, path in (("ours", "all.npz"), ("released", "all_released.npz")):
        s = CS.CallStore.load(os.path.join(ROOT, "results", "callstore", path))
        z = np.zeros(len(s), dtype=np.int32)
        real = np.zeros(len(s), dtype=np.int32)
        for r in range(len(s)):
            t = s.report_tokens(r)[:512]
            z[r], real[r] = int((t == 0).sum()), len(t)
        for part, sl in (("January", slice(0, n_tr)), ("April", slice(n_tr, len(s)))):
            zz, rr = z[sl], real[sl]
            out[f"{name}|{part}"] = {"reports": int(len(zz)), "tokens_in_first_512": int(rr.sum()), "id0_tokens": int(zz.sum()), "share_of_tokens": float(zz.sum() / rr.sum()), "reports_with_any": int((zz > 0).sum()),
                                     "share_reports_with_any": float((zz > 0).mean()), "mean_per_report": float(zz.mean()), "median_per_report": float(np.median(zz)), "p95_per_report": float(np.percentile(zz, 95)), "max_per_report": int(zz.max())}
    tok = make_pad.make_tokenizer()
    reps = make_pad.Reps()
    rng = np.random.default_rng(0)
    cnt = collections.Counter()
    for r in rng.choice(n_tr, 1500, replace=False):
        txt = tok.clear_json_event(str(reps.get(int(tr[r]))))
        for p in tok.tokenizer.encode(txt, return_type="proto").pieces:
            if p.id == 0:
                cnt[p.surface] += 1
    out["sample_unknown_surfaces_1500_january_reports"] = dict(cnt.most_common(10))
    out["sentencepiece_unk_id"], out["sentencepiece_pad_id"] = int(tok.tokenizer.unk_id()), int(tok.tokenizer.pad_id())
    json.dump(out, open(os.path.join(ROOT, "results", "review", "tokenizer_counts.json"), "w"), indent=1)
    print(json.dumps(out, indent=1)[:1500])


if __name__ == "__main__":
    main()
