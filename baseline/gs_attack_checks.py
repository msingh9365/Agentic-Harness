"""
Checks before an attack report (NOTES 25 Stage J, partial and final):   (OURS; CPU only, scores only)

    python -m baseline.gs_attack_checks --scores <dir with scores_m*.npz, wb_m*_seed*.npz> --logits results/groupsplit/stage_fgh/stage_i/logits_fixed_models.npz --out <dir>/checks.json

  (1) every model that has scores has ALL 10 seeds for every edit set present (arrays [n_sets, 17,402], no NaN); every model with white-box files has seeds 0-9 ([51, 500] arrays);
  (2) the unedited scores (edit set 0) reproduce the stored April logits of the model (max abs difference <= 1e-4) per model and seed;
  (3) white-box: the flagged share at step 0 equals the clean detection of the same 500 reports (stored logits against the threshold of the stored logits, exactly), the step-0 scores equal the stored logits (<= 1e-4),
      the thresholds equal those of the stored logits (<= 1e-4), and the flagged share never increases with the steps (both thresholds); per report the best score never increases. Every violation is listed.
Writes checks.json with the details and exits with status 1 if any check fails (then NO tables are made).
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

from baseline import padtest

TOL = 1e-4
KEY = {"m1": "f1_test", "m2": "f2_test", "m3": "f3_test", "m4": "f4_test"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--logits", required=True, help="npz with the stored April logits [10, 17402] under f1_test .. f4_test")
    ap.add_argument("--out", required=True, help="checks.json")
    ap.add_argument("--models", nargs="*", default=["m1", "m2", "m3", "m4"])
    a = ap.parse_args()
    y = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "logits", "labels.npz"))["y_test"].astype(int)
    stored = np.load(a.logits)
    res, viol = {"tolerance": TOL, "models": {}}, []
    names0 = None
    for f in a.models:
        r = {}
        sp = os.path.join(a.scores, f"scores_{f}.npz")
        if os.path.exists(sp):
            d = np.load(sp)
            names = [str(n) for n in d["names"]]
            names0 = names0 or names
            seeds = sorted(int(k[4:]) for k in d.files if k.startswith("seed"))
            ok_seeds = seeds == list(range(10)) and names == names0
            shapes_ok = all(d[f"seed{s}"].shape == (len(names), len(y)) and bool(np.isfinite(d[f"seed{s}"]).all()) for s in seeds)
            diffs = [float(np.abs(d[f"seed{s}"][0].astype(np.float64) - stored[KEY[f]][s].astype(np.float64)).max()) for s in range(10)] if ok_seeds else []
            r["scores"] = {"seeds": seeds, "edit_sets": len(names), "all_10_seeds_and_same_sets": bool(ok_seeds), "shapes_finite": bool(shapes_ok), "unedited_vs_stored_max_diff_per_seed": diffs, "unedited_max_diff": max(diffs) if diffs else None}
            if not (ok_seeds and shapes_ok):
                viol.append(f"{f}: scores incomplete or malformed")
            if diffs and max(diffs) > TOL:
                viol.append(f"{f}: unedited scores differ from the stored logits by {max(diffs):.2e} > {TOL}")
        else:
            r["scores"] = "missing"
            viol.append(f"{f}: scores file missing")
        fs = sorted(glob.glob(os.path.join(a.scores, f"wb_{f}_seed*.npz")))
        if not fs:
            r["white_box"] = "pending (no files)"
        else:
            seeds = sorted(int(re.search(r"seed(\d+)\.npz$", p).group(1)) for p in fs)
            w = {"seeds": seeds, "per_seed": {}}
            if seeds != list(range(10)):
                viol.append(f"{f}: white-box seeds {seeds} != 0-9")
            for p in fs:
                s = int(re.search(r"seed(\d+)\.npz$", p).group(1))
                z = np.load(p)
                best, raw = z["best"].astype(np.float64), z["raw"].astype(np.float64)
                sel = z["sel"]
                z0 = stored[KEY[f]][s].astype(np.float64)
                t1s, t01s = padtest.thresholds(z0, y, 0.01), padtest.thresholds(z0, y, 0.001)
                e = {"shape_best": list(best.shape), "step0_vs_stored_max_diff": float(np.abs(best[0] - z0[sel]).max()), "t1_diff": abs(float(z["t1"]) - float(t1s)), "t01_diff": abs(float(z["t01"]) - float(t01s))}
                for key, ts in (("t1", t1s), ("t01", t01s)):
                    clean = float((z0[sel] > ts).mean())
                    share = (best > float(z[key])).mean(1)
                    e[key] = {"clean_detection_same_reports": clean, "step0_detection": float(share[0]), "step0_equals_clean": bool(abs(share[0] - clean) == 0.0),
                              "share_never_increases": bool((np.diff(share) <= 0).all()), "share_by_step_first_last": [float(share[0]), float(share[-1])]}
                    if not e[key]["step0_equals_clean"]:
                        viol.append(f"{f} seed {s} {key}: step-0 detection {share[0]:.4f} != clean detection {clean:.4f}")
                    if not e[key]["share_never_increases"]:
                        viol.append(f"{f} seed {s} {key}: flagged share increases with the steps")
                e["best_never_increases_per_report"] = bool((np.diff(best, axis=0) <= 1e-6).all())
                if best.shape != (51, 500):
                    viol.append(f"{f} seed {s}: best has shape {best.shape}")
                if e["step0_vs_stored_max_diff"] > TOL or e["t1_diff"] > TOL or e["t01_diff"] > TOL:
                    viol.append(f"{f} seed {s}: white-box step 0 or thresholds differ from the stored logits ({e['step0_vs_stored_max_diff']:.2e}, {e['t1_diff']:.2e}, {e['t01_diff']:.2e})")
                if not e["best_never_increases_per_report"]:
                    viol.append(f"{f} seed {s}: per-report best score increases")
                w["per_seed"][str(s)] = e
            r["white_box"] = w
        res["models"][f] = r
    res["violations"], res["passed"] = viol, not viol
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print("checks passed" if not viol else "CHECKS FAILED:\n" + "\n".join(viol))
    sys.exit(0 if not viol else 1)


if __name__ == "__main__":
    main()
