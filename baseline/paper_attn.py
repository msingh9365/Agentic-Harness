"""
Job (CPU kernel, seconds): attention-pooling weights of M3 (seed 0) over the 512 tokens of two April malware reports, for the paper figure F12.   (OURS; the authors' model code, our stored weights)

    python -m baseline.paper_attn --out /kaggle/working/out

Reads baseline/paper_attn_spec.json (written by baseline/paper_figs.py --prepare: per model set the April row of the lowest-index malware report with >= 512 tokens that seed 0 detects at the 1% threshold, and of the lowest-index
one it misses). SET A = current tokenizer (weights `m3/seed0.pt` of the dataset gs-final-models, store of nebula-tune-inputs), SET B = corrected tokenizer (gs-fix-models, gs-fix-inputs). Per report: the 512 token ids, the pooling
weights, the model's logit (a check against the stored logit). Nothing is trained; only scores and weights over the real tokens of two reports are saved.
"""
import argparse
import json
import os

import numpy as np

from baseline import callstore as CS, padtest

SOURCES = {"A": ("gs-final-models", "nebula-tune-inputs"), "B": ("gs-fix-models", "gs-fix-inputs")}
NTR = 75298
# the two reports per model set (rule in the docstring; the same content is in baseline/paper_attn_spec.json, embedded here because the kernel carries only the .py files)
SPEC = [{'set': 'A', 'rows': {'detected': 1, 'missed': 0}, 'stored_logit': {'detected': 8.908018112182617, 'missed': -9.615455627441406}, 'threshold_seed0': 3.781623363494873}, {'set': 'B', 'rows': {'detected': 1, 'missed': 0}, 'stored_logit': {'detected': 9.973039627075195, 'missed': -10.09773063659668}, 'threshold_seed0': 4.803037643432617}]


def find(slug, rel):
    for dp, dn, fn in os.walk("/kaggle/input"):
        if os.path.basename(dp) == slug or dp.rstrip("/").endswith("/" + slug):
            p = os.path.join(dp, rel)
            if os.path.exists(p):
                return p
    raise FileNotFoundError(f"{slug}/{rel}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import torch
    spec = SPEC
    res = {}
    for s in spec:
        wslug, sslug = SOURCES[s["set"]]
        m = padtest.load_model("attbal", find(wslug, "m3/seed0.pt"), "cpu")
        store = CS.CallStore.load(find(sslug, "all.npz"))
        res[s["set"]] = {}
        for which, row in s["rows"].items():
            tok = np.asarray(store.report_tokens(NTR + row)[:512], dtype=np.uint16)
            src = torch.from_numpy(tok.astype(np.int64))[None]
            with torch.no_grad():
                w = m.attention_weights(src)[0].numpy()
            sc = padtest.score(m, np.stack([tok])[None], "cpu")[0, 0]
            res[s["set"]][which] = {"april_row": int(row), "ids": [int(t) for t in tok], "weights": [float(x) for x in w], "logit": float(sc), "stored_logit": s["stored_logit"][which], "n_real_tokens": int((tok != 0).sum())}
            print(s["set"], which, row, "logit", float(sc), "stored", s["stored_logit"][which], "weights sum", float(w.sum()), flush=True)
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "attn_m3_seed0.json"), "w"))


if __name__ == "__main__":
    main()
