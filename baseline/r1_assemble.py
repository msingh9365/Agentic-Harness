"""
ITEM R1 (NOTES 30.3): assembles the score directories that the report tools read (scores only).   (OURS)

    python -m baseline.r1_assemble --r1 <dir(s) with scores_r1.npz> --m3 <dir with scores_m3_first.npz and scores_m3_mw64.npz> --wb-r1 <dir(s) with wb_r1_seed*.npz> --out /tmp/r1_comb

Writes <out>/A (M1, M3, M4, R1 on the 12 sets that exist for all of them: Stage J and item 2 scores for M1, M3, M4; white-box files of Stage J for M1, M3, M4 and of R1), <out>/B (the test-time multi-window baseline `m3mw`
and the plain M3 rescored `m3`, and R1, on all 13 sets incl. the adaptive one), and checks that the rescored plain M3 and its multi-window scores equal the stored Stage J / part-3 scores on the shared sets.
"""
import argparse
import glob
import json
import os
import shutil

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS = list(range(10))


def merge_seeds(dirs, fname):
    out, names, tot = {}, None, None
    for d in dirs:
        p = os.path.join(d, fname)
        if not os.path.exists(p):
            continue
        z = np.load(p)
        n = [str(x) for x in z["names"]]
        assert names is None or n == names
        names, tot = n, z["tot"]
        for k in z.files:
            if k.startswith("seed"):
                assert k not in out, f"{k} twice"
                out[k] = z[k]
    assert sorted(int(k[4:]) for k in out) == SEEDS, f"seeds in {fname}: {sorted(out)}"
    return names, tot, out


def save(path, names, tot, seeds, sel):
    np.savez_compressed(path, names=np.array([names[i] for i in sel]), tot=tot[sel], **{k: v[sel] for k, v in seeds.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r1", nargs="+", required=True)
    ap.add_argument("--m3", required=True)
    ap.add_argument("--wb-r1", nargs="+", required=True)
    ap.add_argument("--stage-j", default="/tmp/fix_j_all")
    ap.add_argument("--item2", default="/tmp/fup_k/out")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    names, tot, r1 = merge_seeds(a.r1, "scores_r1.npz")
    A, B = os.path.join(a.out, "A"), os.path.join(a.out, "B")
    for d in (A, B):
        os.makedirs(d, exist_ok=True)
    sets_a = [n for n in names if n != "adaptive_50_every_window"]
    save(os.path.join(A, "scores_r1.npz"), names, tot, r1, [names.index(n) for n in sets_a])
    for m in ("m1", "m3", "m4"):
        zj, zk = np.load(os.path.join(a.stage_j, f"scores_{m}.npz")), np.load(os.path.join(a.item2, f"scores_{m}.npz"))
        nj, nk = [str(x) for x in zj["names"]], [str(x) for x in zk["names"]]
        seeds = {}
        tots = np.zeros((len(sets_a), zj["tot"].shape[1]), dtype=np.int64)
        for s in SEEDS:
            rows = []
            for i, n in enumerate(sets_a):
                src, nn = (zj, nj) if n in nj else (zk, nk)
                rows.append(src[f"seed{s}"][nn.index(n)])
                if s == 0:
                    tots[i] = src["tot"][nn.index(n)]
                if n in nj and n in nk:
                    assert np.array_equal(zj[f"seed{s}"][nj.index(n)], zk[f"seed{s}"][nk.index(n)]), f"{m} {n}: Stage J and item 2 differ"
            seeds[f"seed{s}"] = np.stack(rows)
        np.savez_compressed(os.path.join(A, f"scores_{m}.npz"), names=np.array(sets_a), tot=tots, **seeds)
        for f in glob.glob(os.path.join(a.stage_j, f"wb_{m}_seed*.npz")):
            shutil.copy(f, A)
    for d in a.wb_r1:
        for f in glob.glob(os.path.join(d, "wb_r1_seed*.npz")):
            shutil.copy(f, A)
            shutil.copy(f, B)
    # B: plain M3 rescored, its multi-window scores, R1, on all 13 sets
    n1, t1, first = merge_seeds([a.m3], "scores_m3_first.npz")
    n2, t2, mw = merge_seeds([a.m3], "scores_m3_mw64.npz")
    assert n1 == names and n2 == names
    allsel = list(range(len(names)))
    save(os.path.join(B, "scores_r1.npz"), names, tot, r1, allsel)
    save(os.path.join(B, "scores_m3.npz"), n1, t1, first, allsel)
    save(os.path.join(B, "scores_m3mw.npz"), n2, t2, mw, allsel)
    chk = {"rescored_plain_m3_vs_stage_j_max_abs_diff": 0.0, "rescored_multiwindow_vs_part3_max_abs_diff": 0.0}
    zj = np.load(os.path.join(a.stage_j, "scores_m3.npz"))
    nj = [str(x) for x in zj["names"]]
    for n in names:
        if n in nj:
            for s in SEEDS:
                chk["rescored_plain_m3_vs_stage_j_max_abs_diff"] = max(chk["rescored_plain_m3_vs_stage_j_max_abs_diff"], float(np.abs(first[f"seed{s}"][names.index(n)] - zj[f"seed{s}"][nj.index(n)]).max()))
    p3 = np.load(os.path.join(ROOT, "results", "groupsplit", "stage_fgh", "part3", "combined", "scores_m3_mw.npz"))
    np3 = [str(x) for x in p3["names"]]
    for n in names:
        if n in np3:
            for s in SEEDS:
                chk["rescored_multiwindow_vs_part3_max_abs_diff"] = max(chk["rescored_multiwindow_vs_part3_max_abs_diff"], float(np.abs(mw[f"seed{s}"][names.index(n)] - p3[f"seed{s}"][np3.index(n)]).max()))
    json.dump(chk, open(os.path.join(a.out, "assemble_checks.json"), "w"), indent=1)
    print(json.dumps(chk))


if __name__ == "__main__":
    main()
