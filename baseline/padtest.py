"""
Random benign padding test, scoring side (ATT+bal follow-up).   (OURS)

    python -m baseline.padtest --bundle <april_pad.npz> --out <dir> --family v2_pe --kind v2_pe --models-root /kaggle/input/nebula-baseline-models
    python -m baseline.padtest --bundle <april_pad.npz> --out <dir> --family att --kind att --search /kaggle/input        # models of a training kernel attached as a kernel source

Scores the padded April arrays (baseline/make_pad.py --april: 6 edits x (all April malware + 2,000 random benign) of random benign calls, prepend/insert with k = 5, 20, 50) with the
10 models of one family and writes <out>/pad_<family>.npz: seed<k> = float32 logits [6, n]. The unedited April logits of the same models are the stored test logits, so the
threshold at 1% FPR on the unedited April set (EVAL: `thresholds`) needs no re-scoring. Nothing is trained or selected here.

kinds: v2 (released code: pe_mode released, flatten), v2_pe (paper, flatten), pebal (paper, flatten, trained with balanced padding), att and attbal (paper, attention pooling).
"""
import argparse
import os
import time

import numpy as np

KINDS = {"v2": ("released", "flatten"), "v2_pe": ("paper", "flatten"), "pebal": ("paper", "flatten"), "att": ("paper", "attn"), "attbal": ("paper", "attn"),
         "released": ("released", "flatten"),                                 # the released checkpoint (authors' code: released encoding, flatten)
         "attkeep": ("paper", "attn"), "pekeep": ("paper", "flatten"),         # balanced padding with the clean copies kept (REPORT 5.11)
         "attaug": ("paper", "attn"), "peaug": ("paper", "flatten")}          # padding of the malware training reports only (REPORT 5.11)
TAGS = {"pebal": "pebal", "att": "att", "attbal": "attbal", "attkeep": "attkeep", "pekeep": "pekeep", "attaug": "attaug", "peaug": "peaug"}              # run tags of baseline/v2pe.py (the output folder name of the training kernel)


def thresholds(z_test, y_test, fpr=0.01):
    """Per model: the benign logit at rank floor(fpr * n_benign) in descending order; a report is flagged if its logit is ABOVE it (so the unedited benign FPR is about `fpr`)."""
    neg = np.sort(np.asarray(z_test)[np.asarray(y_test) == 0])[::-1]
    k = int(np.floor(fpr * len(neg)))
    return neg[k] if k < len(neg) else -np.inf


def find_weights(kind, seed, models_root=None, search=None):
    if kind == "released":
        from baseline import common as C
        return os.path.join(C.setup_nebula(require_patched=True)["nebula_root"], "nebula", "objects", "bpe_50000_torch.model")
    if kind in ("v2", "v2_pe") and models_root:
        p = os.path.join(models_root, "detection", "bpe50k", kind, f"seed{seed}.pt")
        if os.path.exists(p):
            return p
    for root in ([search] if search else []):                      # Kaggle mounts datasets and kernel outputs under paths that are not the slug: search the tree
        for dp, dn, fn in os.walk(root):
            if os.path.basename(dp) == kind and f"seed{seed}.pt" in fn:                    # packaged weights: <root>/<kind>/seed<k>.pt (the review datasets)
                return os.path.join(dp, f"seed{seed}.pt")
            if os.path.basename(dp) == TAGS.get(kind, "?") and f"seed{seed}_epoch2_model.pt" in fn:
                return os.path.join(dp, f"seed{seed}_epoch2_model.pt")
    raise FileNotFoundError(f"weights of {kind} seed {seed} not found (models_root={models_root}, search={search})")


def load_model(kind, path, device):
    import torch
    from baseline import pe
    sd = torch.load(path, map_location="cpu", weights_only=True)
    pe_mode, pool = KINDS[kind]
    m = pe.build_chunks(sd["encoder.weight"].shape[0], pe_mode=pe_mode, pool_mode=pool)
    m.load_state_dict(sd)
    return m.to(device).eval()


def score(model, tok, device, bs=256):
    """tok: uint16 [6, n, 512] -> float32 logits [6, n]."""
    import torch
    out = np.zeros(tok.shape[:2], dtype=np.float32)
    with torch.no_grad():
        for j in range(tok.shape[0]):
            for i in range(0, tok.shape[1], bs):
                x = torch.from_numpy(np.asarray(tok[j, i:i + bs]).astype(np.int64)).to(device)
                out[j, i:i + bs] = model(x).float().cpu().numpy().reshape(-1)
    return out


def orchestrate(a):
    """One subprocess per family, on the two GPUs in parallel: --jobs family:kind ..."""
    import subprocess
    import sys
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    jobs, running, failed = [j.split(":") for j in a.jobs], {}, []
    while jobs or running:
        for g in range(n_gpu):
            if g not in running and jobs:
                fam, kind = jobs.pop(0)
                cmd = [sys.executable, "-m", "baseline.padtest", "--bundle", a.bundle, "--out", a.out, "--family", fam, "--kind", kind, "--device", a.device]
                if a.models_root:
                    cmd += ["--models-root", a.models_root]
                if a.search:
                    cmd += ["--search", a.search]
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g))), fam)
                print(f"GPU {g}: started {fam}", flush=True)
        for g, (p, fam) in list(running.items()):
            if p.poll() is not None:
                print(f"GPU {g}: {fam} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(fam)
                del running[g]
        time.sleep(3)
    if failed:
        raise SystemExit(f"padding scoring failed: {failed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--jobs", nargs="*", default=[], help="family:kind pairs for --plan")
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--family", default=None)
    ap.add_argument("--kind", default=None, choices=list(KINDS))
    ap.add_argument("--models-root", default=None)
    ap.add_argument("--search", default=None)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    if a.plan:
        return orchestrate(a)
    from baseline import common as C
    C.setup_nebula(require_patched=True)
    bundle = a.bundle if os.path.exists(a.bundle) else os.path.join(C.find_dir_with("april_pad.npz"), "april_pad.npz")
    tok = np.load(bundle)["tok"]
    os.makedirs(a.out, exist_ok=True)
    res, t0 = {}, time.time()
    for s in a.seeds:
        m = load_model(a.kind, find_weights(a.kind, s, a.models_root, a.search), a.device)
        res[f"seed{s}"] = score(m, tok, a.device)
        print(f"[{a.family}] seed {s} scored: {tok.shape[0]} edits x {tok.shape[1]} reports ({time.time() - t0:.0f}s)", flush=True)
        del m
    np.savez_compressed(os.path.join(a.out, f"pad_{a.family}.npz"), **res)


if __name__ == "__main__":
    main()
