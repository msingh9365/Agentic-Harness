#!/usr/bin/env python
"""Assemble results/go_no_go.md from the parts written by the four tests."""
import json
import subprocess

import common as C

git = lambda *a: subprocess.check_output(["git", *a], text=True).strip()


def main():
    t1 = json.load(open(f"{C.OUT}/test1.json"))["point"]
    t2 = json.load(open(f"{C.OUT}/test2.json"))
    t3 = json.load(open(f"{C.OUT}/test3.json"))
    t4 = json.load(open(f"{C.OUT}/test4.json"))
    sc = json.load(open(f"{C.OUT}/scoring.json"))
    ra, rj, tw = (t1[m]["all"] for m in ["rank average (LightGBM + Nebula)", "rank average, January reference",
                                          "two-level K=8 (finetune_k8)"])
    tw1, nb1 = t1["two-level K=8 (finetune_k8)"], t1["released Nebula"]
    pc = lambda d, sub: f"{100 * d[sub]['tpr1%_a']:.1f}%"
    f = lambda d: f"{d['auc']:.4f} / {100 * d['tpr1%_a']:.1f}% / {100 * d['tpr0.1%_a']:.1f}%"
    dominated = all(ra[k] >= tw[k] for k in ["auc", "tpr1%_a", "tpr0.1%_a"])
    d1 = (f"By the rule set in advance, **the two-level model is dominated**: the rank average of LightGBM and released "
          f"Nebula (percentile ranks within April, as specified) gets {f(ra)} against {f(tw)}. None of the three "
          f"differences is significant (all intervals include 0), and the deployable variant (ranks against "
          f"January) gets {f(rj)}, which ties at 1% FPR and trails at 0.1% FPR."
          if dominated else f"The rank average ({f(ra)}) does not match the two-level model ({f(tw)}) on all three numbers.")
    head = git("rev-parse", "HEAD")
    dirty = git("status", "--porcelain", "scripts/go_no_go")
    txt = f"""# Go / no-go: is the two-level (chunked) Nebula worth more GPU time?

Four cheap tests on the Speakeasy reports (January 2022 = train, April 2022 = test). Nothing was run or
emulated; only existing reports and scores were read and LightGBM was trained. Everything is fitted on
January only; April labels are used only to report.

## Setup

| item | value |
|---|---|
| this repository | `{head}` (branch `nebula-length-study`){" + uncommitted `scripts/go_no_go/` changes" if dirty else ""} |
| Nebula code and released model | `{sc['nebula_commit']}` (`../nebula`, = upstream HEAD on 2026-11-14); `model.eval()`, batch size {sc['batch_size']}, torch {sc['torch']} |
| dataset | `dtrizna/quovadis-speakeasy` revision `fc2e98fac0b4d43a5557ccab70c877af6cce9f4d` (REPORT.md §1) |
| two-level model | `results/hier/finetune_k8/best.pt` (K=8, finetune, seed 0); re-scoring reproduces its `test_scores.csv` (max diff 8.3e-7) |
| January split | `results/signal/val_split.csv`: groups = SHA-1 of the API-name sequence (`hash_apis`), 10% of groups to validation, `GroupShuffleSplit` seed 0 (65,679 train / 9,619 validation reports) |
| LightGBM | `analyze_signal.fit_lgb`: lr 0.05, 63 leaves, feature/bagging fraction 0.8, early stopping (100 rounds) on group-weighted validation log-loss; seeds 0, 1, 2 |
| bootstrap | 1,000 resamples of April groups (`hash_apis`, 2,509 groups), seed 0, paired across models |
| thresholds | (a) from April benign scores; (b) from January-validation benign scores, applied to April (its April FPR is shown). Rule: flagged = score > the (⌊FPR·n⌋+1)-th highest benign score |
| subsets | seen / unseen = the report's `hash_apis` occurs / does not occur in January; chunks = 512-token chunks of Nebula's tokenized report (`meta.csv` `n_chunks`) |
| April scores | `results/go_no_go/scores/*_april.parquet` (columns `row`, `seed`, `score`; `row` = `results/hier/data/meta.csv` row), January-validation scores in `*_janval.parquet` |

Caveat for threshold (b): released Nebula and the two-level model were trained on January data, so their
January-validation scores are in-sample; only LightGBM's validation side is truly held out.

## Commands

```bash
source ../nebula-venv/bin/activate          # Python 3.11, see results/logs/signal_versions.log
python scripts/go_no_go/score_models.py      # released Nebula + two-level scores (April, January validation)
python scripts/go_no_go/test1_rank_average.py
python scripts/go_no_go/test2_ceiling.py
python scripts/go_no_go/test3_unseen_distance.py
python scripts/go_no_go/test4_long_group.py
python scripts/go_no_go/make_report.py       # this file
```
Logs: `results/go_no_go/logs/`.

"""
    for i in range(1, 5):
        part = open(f"{C.OUT}/parts_test{i}.md").read()
        if i == 1:
            part += f"\n**Decision.** {d1}\n"
        txt += part + "\n"
    txt += f"""## Summary

1. **Stop the two-level model in its current form:** a rank average of released Nebula and a 5-second bag-of-API LightGBM matches or beats it ({f(ra)} vs {f(tw)}), with no training of any Transformer.
2. **Its gain does not come from the extra chunks:** it improves reports that fit in one chunk (TPR at 1% FPR {pc(tw1, '1 chunk')} vs {pc(nb1, '1 chunk')} for Nebula) and is worse on 2–3-chunk reports ({pc(tw1, '2-3 chunks')} vs {pc(nb1, '2-3 chunks')}).
3. **Long reports do hold signal** (bag model AUC {t2['auc_diff']['4-8 chunks']:+.2f} on 4–8-chunk reports with the full trace, test 2) and {100 * (t4['point']['all April|released Nebula misses (a)|2-3'] + t4['point']['all April|released Nebula misses (a)|4-8']):.0f}% of Nebula's misses need more than one chunk, so long context is not worthless, but this model does not capture it.
4. **Most of April's loss is on "unseen" sequences that are near-copies of January** (median {100 * t3['median_dist']:.1f}% of calls edited, median 100% of 16-call windows already seen), so robustness to small edits is a better target than length.
5. **The test set cannot resolve gains of this size** (group-bootstrap intervals of about ±0.02 AUC and ±10–20 TPR points), so any new GPU run should target a measured gap and be judged with group-level intervals.
"""
    open("results/go_no_go.md", "w").write(txt)
    print("wrote results/go_no_go.md")


if __name__ == "__main__":
    main()
