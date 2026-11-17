"""
Statistics for the long pre-training follow-up (experiment B2).   (OURS)

  * paired differences per seed: (run - lower bound) and (upper bound - run) for TPR@1e-3, TPR@1e-2 and AUC; the seeds share the 80/20 split,
    the fine-tuning budget and the test set, so the differences are paired; mean +- std over the 5 seeds
  * bootstrap 95% CI over the April test reports (1,000 resamples, stratified by label: malware and benign are resampled separately) of
    TPR@1e-3 and TPR@1e-2 of each run's seed-averaged score (mean logit over the seeds), and of the paired difference against the
    lower bound (same resample for both runs). It measures the noise from the finite test set. The seed-to-seed std measures the
    noise from training. A comparison is called RESOLVED when the 95% CI excludes 0.

Run names (all logit-ranked, from <first>/seed*/<run>/test_logits.npy and <long>/seed*/<run>/test_logits.npy):
  upper, lower                                 first run (100% / 20% supervised), reused
  lower_fullattn, upper_fullattn               first run, full-attention controls, reused
  *_3ep                                        first run, 3 pre-training epochs (mlm_theirs, mlm_bert, ar_flatten, ar_lasttoken)
  ar_lasttoken_ep3 / _ep6 / _ep10              long run, fine-tuned from the AR checkpoint of that epoch
  ar_lasttoken_best, mlm_bert_best, mlm_theirs_best, ar_flatten_best    long run, fine-tuned from the best epoch (lowest validation LM loss)

    python -m baseline.long_stats --first results/B_selfsup --long results/B_selfsup_long --y results/B_selfsup_long/y_test.npy
"""
import argparse
import glob
import json
import os

import numpy as np

SEEDS = [0, 1, 2, 3, 4]
METRICS = [("tpr@0.001", "TPR@1e-3"), ("tpr@0.01", "TPR@1e-2"), ("auc", "AUC")]
FIRST_REUSED = ["upper", "lower", "lower_fullattn", "upper_fullattn"]
FIRST_3EP = {"mlm_theirs": "mlm_theirs_3ep", "mlm_bert": "mlm_bert_3ep", "ar_flatten": "ar_flatten_3ep", "ar_lasttoken": "ar_lasttoken_3ep"}
LABELS = {
    "upper": "upper bound (100% supervised)", "lower": "lower bound (20% supervised)",
    "upper_fullattn": "control: full attention, 100%", "lower_fullattn": "control: full attention, 20%",
    "ar_lasttoken_3ep": "AR last-token, 3 epochs (first run)", "ar_flatten_3ep": "AR flatten, 3 epochs (first run)",
    "mlm_bert_3ep": "MLM per-position, 3 epochs (first run)", "mlm_theirs_3ep": "MLM authors' multi-hot, 3 epochs (first run)",
    "ar_lasttoken_ep3": "AR last-token, epoch 3 (long run)", "ar_lasttoken_ep6": "AR last-token, epoch 6",
    "ar_lasttoken_ep10": "AR last-token, epoch 10", "ar_lasttoken_best": "AR last-token, best epoch",
    "ar_flatten_best": "AR flatten, best epoch", "mlm_bert_best": "MLM per-position, best epoch",
    "mlm_theirs_best": "MLM authors' multi-hot, best epoch",
}


def jl(p):
    return json.load(open(p))


def collect(first, long):
    """{run: {seed: (metrics_test_dict, logits)}} for every run that exists for all (or some) seeds."""
    runs = {}

    def add(name, seed, d):
        m = jl(os.path.join(d, "metrics.json"))
        z = np.load(os.path.join(d, "test_logits.npy")).astype(np.float64)
        runs.setdefault(name, {})[seed] = (m["test"], z, m)

    for s in SEEDS:
        for r in FIRST_REUSED:
            d = os.path.join(first, f"seed{s}", r)
            if os.path.exists(os.path.join(d, "metrics.json")):
                add(r, s, d)
        for r, name in FIRST_3EP.items():
            d = os.path.join(first, f"seed{s}", r)
            if os.path.exists(os.path.join(d, "metrics.json")):
                add(name, s, d)
        for d in sorted(glob.glob(os.path.join(long, f"seed{s}", "*"))):
            if not os.path.exists(os.path.join(d, "metrics.json")):
                continue
            r = os.path.basename(d)
            m = jl(os.path.join(d, "metrics.json"))
            add(r, s, d)
            if "_ep" in r and m.get("is_best"):                       # the run fine-tuned from the best epoch is also "<run>_best"
                add(r.split("_ep")[0] + "_best", s, d)
    return runs


def seeds_of(runs, name):
    return sorted(runs.get(name, {}))


def paired(runs, name, ref, sign=+1):
    """per-seed value(name) - value(ref) for each metric (sign=-1 gives ref - name); only seeds present for both."""
    common = sorted(set(runs[name]) & set(runs[ref]))
    out = {}
    for k, _ in METRICS:
        v = np.array([sign * (runs[name][s][0][k] - runs[ref][s][0][k]) for s in common])
        out[k] = {"mean": float(v.mean()), "std": float(v.std()), "values": v.round(5).tolist(), "n_positive": int((v > 0).sum()), "n": len(common)}
    return out


def tpr_at(y, z, target):
    from sklearn.metrics import roc_curve
    fpr, tpr, _ = roc_curve(y, z)
    return float(tpr[fpr <= target][-1])        # the authors' get_tpr_at_fpr


def seed_average(runs, name, seeds=SEEDS):
    return np.mean([runs[name][s][1] for s in seeds], axis=0)


def bootstrap(runs, y, names, ref="lower", other="upper", n_boot=1000, seed=0):
    """Stratified bootstrap over test reports. Returns {run: {metric: {point, lo, hi, diff_ref: {point, lo, hi, resolved}, ...}}}."""
    y = np.asarray(y).astype(int)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    rng = np.random.default_rng(seed)
    avail = [n for n in names if n in runs and len(runs[n]) == len(SEEDS)]
    Z = {n: seed_average(runs, n) for n in avail}
    targets = {"tpr@0.001": 1e-3, "tpr@0.01": 1e-2}
    draws = {n: {k: np.empty(n_boot) for k in targets} for n in avail}
    for b in range(n_boot):
        idx = np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])
        yb = y[idx]
        for n in avail:
            zb = Z[n][idx]
            for k, t in targets.items():
                draws[n][k][b] = tpr_at(yb, zb, t)
    res = {}
    for n in avail:
        res[n] = {}
        for k, t in targets.items():
            point = tpr_at(y, Z[n], t)
            lo, hi = np.percentile(draws[n][k], [2.5, 97.5])
            e = {"point": point, "lo": float(lo), "hi": float(hi)}
            for tag, other_run, sign in (("vs_lower", ref, +1), ("upper_minus", other, -1)):
                if other_run in draws and n != other_run:
                    d = sign * (draws[n][k] - draws[other_run][k])
                    p = sign * (point - tpr_at(y, Z[other_run], t))
                    dlo, dhi = np.percentile(d, [2.5, 97.5])
                    e[tag] = {"point": float(p), "lo": float(dlo), "hi": float(dhi), "resolved": bool(dlo > 0 or dhi < 0)}
            res[n][k] = e
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", default="results/B_selfsup")
    ap.add_argument("--long", default="results/B_selfsup_long")
    ap.add_argument("--y", default="results/B_selfsup_long/y_test.npy")
    ap.add_argument("--out", default=None)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    runs = collect(a.first, a.long)
    y = np.load(a.y)
    names = [n for n in LABELS if n in runs]
    res = {"n_boot": a.boot, "seeds": SEEDS, "runs": {}, "bootstrap": bootstrap(runs, y, names, n_boot=a.boot)}
    for n in names:
        if n in ("upper", "lower"):
            continue
        res["runs"][n] = {"seeds": seeds_of(runs, n), "minus_lower": paired(runs, n, "lower"), "upper_minus": paired(runs, n, "upper", sign=-1)}
    out = a.out or os.path.join(a.long, "bootstrap.json")
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out, "| runs:", names)


if __name__ == "__main__":
    main()
