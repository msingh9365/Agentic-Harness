"""
ITEM A1c, coverage pilot of NOTES 30.2 (CPU kernel; JANUARY ONLY, no April; counts and short example strings in the kernel log only, nothing about report text is saved or committed): how do path-like strings look in the
filtered January reports, so that the regular expression of the path-invariant rule can be fixed (NOTES 30.2a) before the decision run?   (OURS; the authors' functions do the filtering)

    python -m baseline.gs_a1c_pilot --out /kaggle/working/out --limit 150
"""
import argparse
import collections
import json
import os
import random
import re
import time

import numpy as np

from baseline import common as C
from baseline import preprocess as P

CANDIDATES = {
    "drive_path": re.compile(r"[a-z]:(?:\\{1,4}[^\\\s'\",;)\]}]+)+"),
    "device_path": re.compile(r"\\{1,4}[?.]\\{1,4}[^\\\s'\",;)\]}]+(?:\\{1,4}[^\\\s'\",;)\]}]+)*"),
    "env_path": re.compile(r"%[a-z_]+%(?:\\{1,4}[^\\\s'\",;)\]}]+)+"),
    "unc_path": re.compile(r"(?<![\\a-z0-9])\\{2,4}[a-z0-9_.$-]+\\{1,4}[^\\\s'\",;)\]}]+"),
    "bare_file": re.compile(r"(?<![\\/a-z0-9_.-])[a-z0-9_~$-]{2,40}\.(?:exe|dll|tmp|dat|log|txt|bat|sys|ini|cfg|bin|vbs|js|lnk|cab|zip|rar|doc|docx|xls|pdf|jpg|png|db|bak)(?![a-z0-9])"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int, default=150, help="files per folder (pilot subsample of January)")
    a = ap.parse_args()
    t0 = time.time()
    info = C.setup_nebula(None, require_patched=False)
    data = C.find_data_root()
    os.makedirs(a.out, exist_ok=True)
    events, ym, _ = P.filter_split(os.path.join(data, "windows_emulation_trainset"), info["nebula_root"], a.workers, a.limit)       # JANUARY (train folder) only
    print(f"{len(events)} January reports filtered in {(time.time() - t0) / 60:.1f} min", flush=True)
    res, examples = {}, {k: [] for k in CANDIDATES}
    comp_df, ext_df = collections.Counter(), collections.Counter()
    rng = random.Random(0)
    for name, rx in CANDIDATES.items():
        res[name] = {"reports_with_match": 0, "matches": 0}
    nchars = []
    for ev in events:
        txt = str(ev).lower()
        nchars.append(len(txt))
        comps_here, exts_here = set(), set()
        for name, rx in CANDIDATES.items():
            ms = rx.findall(txt)
            if ms:
                res[name]["reports_with_match"] += 1
                res[name]["matches"] += len(ms)
                if len(examples[name]) < 400 or rng.random() < 0.002:
                    examples[name].append(rng.choice(ms)[:110])
                if name in ("drive_path", "device_path", "env_path", "unc_path"):
                    for m in ms:
                        parts = [p for p in re.split(r"\\+", m) if p]
                        for p_ in parts[1:]:
                            comps_here.add(p_)
                            if "." in p_:
                                exts_here.add(p_.rsplit(".", 1)[1][:8])
        comp_df.update(comps_here)
        ext_df.update(exts_here)
    n = len(events)
    out = {"reports": n, "mean_chars_per_report": float(np.mean(nchars)), "candidates": {k: {**v, "share_reports_with_match": v["reports_with_match"] / n, "matches_per_report_mean": v["matches"] / n} for k, v in res.items()},
           "distinct_path_components": len(comp_df), "components_in_ge_50_reports_of_pilot": int(sum(1 for v in comp_df.values() if v >= max(2, n // 1500))), "top_components": comp_df.most_common(40), "top_extensions": ext_df.most_common(30)}
    json.dump(out, open(os.path.join(a.out, "pilot_counts.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("top_components", "top_extensions")}, indent=1), flush=True)
    print("TOP COMPONENTS:", out["top_components"][:40], flush=True)
    print("TOP EXTENSIONS:", out["top_extensions"][:30], flush=True)
    for k, ex in examples.items():                                              # short example strings for the regex design, kernel log only
        print(f"EXAMPLES {k}:", [e for e in ex[:25]], flush=True)
    print(f"done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
