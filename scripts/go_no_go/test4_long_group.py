#!/usr/bin/env python
"""
Test 4: size of the long-report group. Share of April reports, April malware, and malware missed at
1% FPR by released Nebula (and, for comparison, by the two-level model) that need 1, 2-3 and 4-8
512-token chunks. Missed = malware with score <= threshold; thresholds (a) April benign (recomputed in
every bootstrap resample) and (b) January validation. Chunks = meta.csv n_chunks (capped at 8, so the
4-8 group also holds the few reports longer than 8 chunks).
"""
import json

import numpy as np
import pandas as pd

import common as C


def wthr(s, y, w, f):
    """Threshold (a) with integer weights: the (floor(f * N) + 1)-th highest benign score."""
    o = np.argsort(-s[y == 0], kind="stable")
    sb, wb = s[y == 0][o], w[y == 0][o]
    k = np.floor(f * wb.sum())
    return sb[np.argmax(np.cumsum(wb) > k)]


def main():
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"]
    y = test.label.values
    buckets = ["1", "2-3", "4-8"]
    B = {b: (test.chunks == b).values for b in buckets}
    over8 = int((test.n_tokens_full > 8 * 512).sum())
    sc, tb = {}, {}
    for name, f in [("released Nebula", "nebula"), ("two-level K=8", "twolevel_k8")]:
        sc[name] = C.load_scores(f, "april")[0].loc[test.row.values].values
        tb[name] = C.thr_from(val.label.values, C.load_scores(f, "janval")[0].loc[val.row.values].values, 0.01)
    pops = [("all April", np.ones(len(test), bool)), ("seen", test.seen.values), ("unseen", ~test.seen.values)]

    def shares(w):
        out = {}
        for pname, pm in pops:
            cols = {"April reports": pm, "April malware": pm & (y == 1)}
            for name in sc:
                ta = wthr(sc[name], y, w, 0.01)
                cols[f"{name} misses (a)"] = pm & (y == 1) & (sc[name] <= ta)
                cols[f"{name} misses (b)"] = pm & (y == 1) & (sc[name] <= tb[name])
            for cname, cm in cols.items():
                tot = (w * cm).sum()
                for b in buckets:
                    out[(pname, cname, b)] = (w * cm * B[b]).sum() / tot if tot else np.nan
                out[(pname, cname, "n")] = tot
        return out

    point = shares(np.ones(len(test)))
    boots = [shares(w) for w in C.group_weights_boot(test.hash_apis.values)]
    rows = []
    for pname, _ in pops:
        for cname in ["April reports", "April malware"] + [f"{n} misses ({k})" for n in sc for k in "ab"]:
            r = {"population": pname, "count": cname, "n": f"{point[(pname, cname, 'n')]:,.0f}"}
            for b in buckets:
                lo, hi = np.nanpercentile([bb[(pname, cname, b)] for bb in boots], [2.5, 97.5])
                r[f"{b} chunk{'s' if b != '1' else ''}"] = f"{100 * point[(pname, cname, b)]:.1f}% [{100 * lo:.1f}, {100 * hi:.1f}]"
            rows.append(r)
    long_rep = point[("all April", "April reports", "4-8")]
    long_miss = point[("all April", "released Nebula misses (a)", "4-8")]
    long2_miss = point[("all April", "released Nebula misses (a)", "2-3")]
    decision = (f"Reports that need 4-8 chunks are {100 * long_rep:.1f}% of April and hold "
                f"{100 * long_miss:.1f}% of released Nebula's misses at 1% FPR; reports beyond the first chunk "
                f"(2-8 chunks) hold {100 * (long_miss + long2_miss):.1f}%, so that is the most a model that reads more "
                f"chunks could fix.")
    json.dump({"point": {"|".join(k): v for k, v in point.items()}, "decision": decision, "over8": over8},
              open(f"{C.OUT}/test4.json", "w"), indent=1, default=float)
    txt = ("## Test 4: size of the long-report group\n\n"
           f"Share of each count that falls in each chunk group (512-token chunks of Nebula's tokenized report; "
           f"{over8} April reports need more than 8 chunks and are counted in 4-8). Misses = malware at or below the "
           "1% FPR threshold: (a) from April benign scores, (b) from January validation. 95% intervals from the "
           "group bootstrap.\n\n" + C.md_table(pd.DataFrame(rows)) + f"\n**Decision.** {decision}\n")
    open(f"{C.OUT}/parts_test4.md", "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
