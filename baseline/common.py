"""
Shared helpers for the baseline reproduction (OURS, not the authors' code).

Everything that cleans, tokenizes, models or trains comes from the authors' package (third_party/nebula, pinned
commit in NOTES.md). This file only: makes that package importable, records the environment, and computes the
metrics the paper reports (using the authors' own get_tpr_at_fpr).
"""
import json
import os
import platform
import random
import subprocess
import sys
import time

import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NEBULA_PINNED_COMMIT = "1343ae170ef32b01a75d2dd5fb906b5541f073df"
# false-positive rates the authors report (ModelTrainer / CrossValidation defaults)
FPRS = [0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1]
SPEAKEASY_CLASSES = ["clean", "backdoor", "coinminer", "dropper", "keylogger", "ransomware", "rat", "trojan"]
BENIGN_FOLDERS = ["report_clean", "report_windows_syswow64"]
CV_RANDOM_STATE = 1763          # random_state of the authors' cross-validation scripts
ROC_GRID = np.logspace(-5, 0, 200)


def setup_nebula(root=None, require_patched=False):
    """Put the authors' package on sys.path and return facts about it (commit, whether our patches are applied)."""
    root = os.path.abspath(root or os.environ.get("NEBULA_ROOT") or os.path.join(REPO_ROOT, "third_party", "nebula"))
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        commit = subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        commit = "unknown"
    lit = open(os.path.join(root, "nebula", "lit_utils.py")).read()
    patched = "lightning.fabric.utilities.seed" in lit and "optimizer_idx: int = None" in lit
    if require_patched and not patched:
        raise RuntimeError("the authors' package is not patched: run patches/apply_patches.sh")
    return {"nebula_root": root, "nebula_commit": commit, "commit_is_pinned": commit == NEBULA_PINNED_COMMIT,
            "patches_applied": patched}


def env_info():
    info = {"python": platform.python_version(), "platform": platform.platform(), "cpus": os.cpu_count()}
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["gpu"] = torch.cuda.get_device_name(0)
            info["gpu_count"] = torch.cuda.device_count()
            info["gpu_mem_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1)
    except Exception as e:  # pragma: no cover
        info["torch_error"] = str(e)
    for m in ["numpy", "sklearn", "sentencepiece", "lightning", "torchmetrics", "pandas"]:
        try:
            info[m] = __import__(m).__version__
        except Exception:
            pass
    return info


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def find_data_root(name="windows_emulation_trainset", search="/kaggle/input"):
    """Folder that contains windows_emulation_trainset / windows_emulation_testset."""
    env = os.environ.get("NEBULA_DATA")
    if env:
        return env
    for dp, dn, _ in os.walk(search):
        if name in dn:
            return dp
        if dp[len(search):].count(os.sep) > 5:
            dn[:] = []
    raise FileNotFoundError(f"{name} not found under {search}; set NEBULA_DATA")


def find_dir_with(filename, search="/kaggle/input"):
    for dp, dn, fn in os.walk(search):
        if filename in fn:
            return dp
        if dp[len(search):].count(os.sep) > 6:
            dn[:] = []
    raise FileNotFoundError(f"{filename} not found under {search}")


# --------------------------------------------------------------------------- metrics
def sigmoid32(z):
    """P(malware) exactly as the authors' predict_proba computes it: torch.sigmoid in float32. Saturates to exactly 1.0 for
    logits above about 17, which creates ties (see binary_metrics)."""
    import torch
    return torch.sigmoid(torch.as_tensor(np.asarray(z), dtype=torch.float32)).numpy()


PAUC_FPRS = (1e-2, 1e-3)            # partial AUC: 1e-2 is the primary low-FPR metric (EVAL_PROTOCOL.md), 1e-3 is reported for reference


def pauc_from_roc(fpr, tpr, max_fpr):
    """Normalized partial AUC from an ROC curve (fpr non-decreasing, as sklearn's roc_curve returns it): the area under the curve for
    FPR in [0, max_fpr], the curve interpolated linearly at exactly max_fpr, DIVIDED by max_fpr. So it is the mean TPR over FPR in [0, max_fpr]:
    1.0 for a perfect ranking, max_fpr / 2 for a random one (TPR = FPR). Where the curve has a vertical step exactly at max_fpr the lower value
    is used (the area up to max_fpr does not include the step)."""
    fpr, tpr = np.asarray(fpr, dtype=np.float64), np.asarray(tpr, dtype=np.float64)
    i = int(np.searchsorted(fpr, max_fpr, side="left"))               # first point with fpr >= max_fpr
    if i >= len(fpr):                                                 # curve ends before max_fpr (cannot happen for a full ROC)
        t_at = tpr[-1]
    elif fpr[i] == max_fpr or i == 0:
        t_at = tpr[i]
    else:
        t_at = tpr[i - 1] + (tpr[i] - tpr[i - 1]) * (max_fpr - fpr[i - 1]) / (fpr[i] - fpr[i - 1])
    x = np.append(fpr[:i], max_fpr)
    yv = np.append(tpr[:i], t_at)
    return float(np.sum((x[1:] - x[:-1]) * (yv[1:] + yv[:-1]) / 2.0) / max_fpr)


def pauc(y, logits, max_fpr=1e-2):
    """Normalized partial AUC (see pauc_from_roc) of the ranking `logits` against the binary labels `y`. PASS LOGITS, never float32 probabilities."""
    from sklearn.metrics import roc_curve
    fpr, tpr, _ = roc_curve(np.asarray(y).astype(int).ravel(), np.asarray(logits, dtype=np.float64).ravel())
    return pauc_from_roc(fpr, tpr, max_fpr)


def pauc_mcclish(y, logits, max_fpr=1e-2):
    """sklearn's McClish-standardized partial AUC (0.5 = chance, 1 = perfect): the form used in some papers. NOT the primary metric; the relation to
    pauc() is mcclish = 0.5 * (1 + (pauc * max_fpr - max_fpr**2 / 2) / (max_fpr - max_fpr**2 / 2))."""
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(np.asarray(y).astype(int).ravel(), np.asarray(logits, dtype=np.float64).ravel(), max_fpr=max_fpr))


SUMMARY_KEYS = ("tpr@0.001", "tpr@0.01", "auc", "pauc@0.01", "pauc@0.001")


def roc_summary(y, z):
    """[TPR@1e-3, TPR@1e-2, AUC, pAUC@1e-2, pAUC@1e-3] from ONE roc_curve call (the authors' get_tpr_at_fpr rule for the TPRs: the last ROC point with
    FPR <= target). The array the bootstrap code resamples (long_stats, b3_report, gap_final, pauc_report)."""
    from sklearn.metrics import auc, roc_curve
    fpr, tpr, _ = roc_curve(np.asarray(y).astype(int).ravel(), np.asarray(z, dtype=np.float64).ravel())
    return np.array([tpr[fpr <= 1e-3][-1], tpr[fpr <= 1e-2][-1], auc(fpr, tpr), pauc_from_roc(fpr, tpr, 1e-2), pauc_from_roc(fpr, tpr, 1e-3)])


def binary_metrics(y, p, fprs=FPRS, decision=0.5):
    """AUC, TPR at each FPR (the authors' get_tpr_at_fpr: last ROC point with FPR <= target; the threshold comes from the
    set being evaluated), F1 and accuracy at `decision`, F1 at each FPR threshold, and the ROC curve on a log FPR grid.
    p: scores to rank by. PASS LOGITS (and decision=0.0) rather than float32 probabilities: after the sigmoid, hundreds of
    reports tie at exactly 1.0, and when more than FPR * n_benign benign reports tie with the top malware scores, no ROC point
    has FPR <= target and get_tpr_at_fpr returns 0.0 (an artifact, not a model property; see NOTES.md)."""
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, roc_curve
    from nebula.misc import get_tpr_at_fpr
    y = np.asarray(y).astype(int).ravel()
    p = np.asarray(p, dtype=np.float64).ravel()
    out = {"n": int(len(y)), "n_malware": int(y.sum()), "n_benign": int((1 - y).sum()), "auc": float(roc_auc_score(y, p))}
    for f in fprs:
        tpr, thr = get_tpr_at_fpr(y, p, f)
        out[f"tpr@{f:g}"] = float(tpr)
        out[f"thr@{f:g}"] = float(thr)
        out[f"f1@fpr{f:g}"] = float(f1_score(y, p >= thr))
    out["f1@0.5"] = float(f1_score(y, p >= decision))          # the key says 0.5: P(malware) >= 0.5 is logit >= 0
    out["acc@0.5"] = float(accuracy_score(y, p >= decision))
    out["n_tied_at_top"] = int((p == p.max()).sum())            # reports sharing the highest score (many = saturation)
    fpr, tpr, _ = roc_curve(y, p)
    out["roc_on_grid"] = np.interp(ROC_GRID, fpr, tpr).astype(float).round(5).tolist()
    for f in PAUC_FPRS:                                          # partial AUC (normalized by f; the primary one is f = 1e-2) and sklearn's McClish form
        out[f"pauc@{f:g}"] = pauc_from_roc(fpr, tpr, f)
        out[f"pauc_mcclish@{f:g}"] = float(roc_auc_score(y, p, max_fpr=f))
    return out


def multiclass_metrics(y, prob):
    """Per-class F1 (argmax), macro-F1, accuracy, macro one-vs-rest AUC. prob: [N, C]."""
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
    y = np.asarray(y).astype(int).ravel()
    prob = np.asarray(prob, dtype=np.float64)
    pred = prob.argmax(1)
    classes = list(range(prob.shape[1]))
    out = {"n": int(len(y)), "acc": float(accuracy_score(y, pred)), "f1_macro": float(f1_score(y, pred, average="macro")),
           "f1_per_class": [float(v) for v in f1_score(y, pred, average=None, labels=classes)]}
    try:
        out["auc_ovr_macro"] = float(roc_auc_score(y, prob, multi_class="ovr", average="macro", labels=classes))
    except ValueError:
        out["auc_ovr_macro"] = float("nan")
    return out


def mean_std(dicts, keys=None):
    """Mean and population std (np.nanstd, as the authors' CV code) of numeric entries over a list of metric dicts."""
    keys = keys or [k for k, v in dicts[0].items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return {k: {"mean": float(np.nanmean([d[k] for d in dicts])), "std": float(np.nanstd([d[k] for d in dicts])),
                "values": [float(d[k]) for d in dicts]} for k in keys}


def dump_json(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


class Timer:
    def __init__(self):
        self.t0 = time.time()

    def minutes(self):
        return (time.time() - self.t0) / 60
