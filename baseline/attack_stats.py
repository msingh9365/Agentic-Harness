"""
Statistics of the attacks (NOTES 15.3), from SCORES only (a3_<family>.npz of baseline/attack_run.py).   (OURS)

For a model (one seed): thresholds t1, t01 = the benign logit at rank floor(0.01 n) / floor(0.001 n) in descending order of the model's UNEDITED April benign scores; flagged = score > threshold.
For an edit set: malware TPR (share of April malware flagged), padded-benign FPR (share of April benign flagged), and the same on the subset whose whole edited report fits in 512 tokens.
Comparison A - B (e.g. ATT+bal - PE+bal): per-seed differences of the rate, the same stratified bootstrap resamples for every seed and model (1,000, numpy seed 0, malware and benign resampled
separately), CI = 2.5 and 97.5 percentiles of the bootstrap mean over seeds of the difference, and the number of seeds with a positive / negative difference; "resolved" = the CI excludes 0 AND the
same sign in at least 7 of the 10 seeds (the claim rule of EVAL_PROTOCOL.md section 5).
"""
import numpy as np

from baseline import padtest

N_BOOT = 1000


def thr(z0, y):
    return padtest.thresholds(z0, y, 0.01), padtest.thresholds(z0, y, 0.001)


def flags_of(Z, y, which):
    """Z [S, 13, N] logits (set 0 = unedited) -> flagged [S, 13, N] bool at the threshold `which` ('1e-2' or '1e-3') of each seed's unedited benign scores."""
    out = np.zeros(Z.shape, dtype=bool)
    for s in range(Z.shape[0]):
        t1, t01 = thr(Z[s, 0], y)
        out[s] = Z[s] > (t1 if which == "1e-2" else t01)
    return out


def boot_weights(n, n_boot=N_BOOT, seed=0):
    """[n_boot, n] resample counts of n items (one set of resamples, reused for every comparison)."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, (n_boot, n))
    return np.stack([np.bincount(r, minlength=n) for r in idx]).astype(np.float32)


def cluster_weights(groups, n_boot=N_BOOT, seed=0):
    """[n_boot, n] resample counts when whole groups are drawn with replacement (as many draws as there are groups)."""
    u, inv = np.unique(groups, return_inverse=True)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(u), (n_boot, len(u)))
    cnt = np.stack([np.bincount(r, minlength=len(u)) for r in idx])
    return cnt[:, inv].astype(np.float32)


class Boot:
    """Stratified resamples of the April reports: malware and benign positions drawn separately (numpy seed 0 for malware, 1 for benign).
    With `groups` (an integer id per report, here the hash of the API sequence: reports with the same id are identical for the model up to the report text) the CELLS (group, class) are
    resampled instead of single reports, so that duplicates are drawn together (cluster bootstrap; the stratified bootstrap of EVAL_PROTOCOL.md treats every report as independent)."""
    def __init__(self, y, n_boot=N_BOOT, groups=None):
        self.pos, self.neg = np.where(y == 1)[0], np.where(y == 0)[0]
        if groups is None:
            self.Wp, self.Wn = boot_weights(len(self.pos), n_boot, 0), boot_weights(len(self.neg), n_boot, 1)
        else:
            self.Wp, self.Wn = cluster_weights(groups[self.pos], n_boot, 0), cluster_weights(groups[self.neg], n_boot, 1)

    def rate(self, F, cls, mask=None):
        """F [S, N] flagged; returns point [S] and bootstrap [S, B] of the share flagged among the reports of class cls ('mal' / 'ben') inside mask (bool [N], None = all)."""
        idx, W = (self.pos, self.Wp) if cls == "mal" else (self.neg, self.Wn)
        f = F[:, idx].astype(np.float32)
        m = np.ones(len(idx), dtype=np.float32) if mask is None else mask[idx].astype(np.float32)
        point = (f * m).sum(1) / max(m.sum(), 1)
        num, den = (f * m) @ W.T, (m @ W.T)[None, :]
        return point, num / np.maximum(den, 1)


def compare(boot, Fa, Fb, cls, mask=None):
    """A - B on the rate of class cls: per-seed differences, mean difference, CI of the mean over seeds, counts of seeds above / below 0, resolved flag."""
    pa, ba = boot.rate(Fa, cls, mask)
    pb, bb = boot.rate(Fb, cls, mask)
    d = pa - pb
    dist = (ba - bb).mean(0)
    lo, hi = np.percentile(dist, [2.5, 97.5])
    n_pos, n_neg = int((d > 0).sum()), int((d < 0).sum())
    return {"per_seed": d.tolist(), "mean": float(d.mean()), "lo": float(lo), "hi": float(hi), "seeds_above_0": n_pos, "seeds_below_0": n_neg,
            "resolved": bool((lo > 0 or hi < 0) and max(n_pos, n_neg) >= 7)}


def summary(boot, F, y, totals, ntot=512):
    """For one family: dict set -> {mal_tpr, ben_fpr, mal_tpr_fit, ben_fpr_fit, share_fit_mal, share_fit_ben} as mean and std over seeds (F [S, 13, N])."""
    out = {}
    for j in range(F.shape[1]):
        fit = totals[j] <= ntot
        row = {}
        for cls, key in (("mal", "tpr"), ("ben", "fpr")):
            p, _ = boot.rate(F[:, j], cls)
            pf, _ = boot.rate(F[:, j], cls, fit)
            row[key] = [float(p.mean()), float(p.std(ddof=1)) if len(p) > 1 else 0.0]
            row[key + "_fit"] = [float(pf.mean()), float(pf.std(ddof=1)) if len(pf) > 1 else 0.0]
            row["share_fit_" + cls] = float(fit[boot.pos if cls == "mal" else boot.neg].mean())
        out[j] = row
    return out
