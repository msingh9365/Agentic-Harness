"""
Shared code of round 5 (results/round5): the model registry (10-seed models of regime J), score caches and table helpers.

Models and where they live
  released Nebula                                   published weights, 512 tokens
  A (J), C (J), C (J, 2 epochs)                     results/pooling_v2, regime J, seeds 0-9 (pooling_v2_all_output)
  F (whole report)                                  results/fulltrace, regime J, seeds 0-4, up to 4,096 tokens
  ATT+bal, MM+bal, C+bal                            round 5 G1 (balanced padding, regime J, seeds 0-9); primary = epoch 2 of the 4-epoch
                                                    run (same data order and learning-rate schedule as a 2-epoch run), also epoch 4
  G3 (optional)                                     ATT+bal over the whole report
Unedited April scores = the Kaggle logits of the run at the epoch used; the edited reports are scored on the CPU with the epoch
checkpoint (fp32 for the round 5 runs). Edited reports exist in memory only; only scores are cached (WORK5).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pooling_v4"))
import v4_common as V  # noqa: E402
from v4_common import C, _W, _init, build_variant, V2_TO_INTERNAL, score512, score_ragged, to512  # noqa: E402
from hier_nebula.model import build_level1  # noqa: E402
import torch  # noqa: E402

OUT = "results/round5"
WORK5 = "/Users/manish/Code/mtp/pooling_v5_work"
NEBULA = V.NEBULA
G1 = os.environ.get("R5_G1", "/Users/manish/Code/mtp/pooling_v5_output_g1")          # R5_G1: stand-in folder for tests
G2 = os.environ.get("R5_G2", "/Users/manish/Code/mtp/pooling_v5_output_g2")
G3 = "/Users/manish/Code/mtp/pooling_v5_output_g3"
J2 = "/Users/manish/Code/mtp/pooling_v2_all_output"
os.makedirs(WORK5, exist_ok=True)

# key -> (output folder, run template, epoch of the April logits, window, checkpoint file, internal variant)
SPEC = {
    "A":     (J2, "A_all_s{s}", 1, 512, "final.pt", "A"),
    "C":     (J2, "C_all_s{s}", 10, 512, "final.pt", "Cm"),
    "C2":    (J2, "C_all_s{s}", 2, 512, "epochs/epoch_02.pt", "Cm"),
    "F":     ("/Users/manish/Code/mtp/fulltrace_output", "F_all_s{s}", 10, 4096, "final.pt", "Cm"),
}
for _fam, _int in (("ATTbal", "ATTx"), ("MMbal", "MMx"), ("Cbal", "Cm")):
    SPEC[_fam] = (G1, _fam + "_all_s{s}", 2, 512, "epochs/epoch_02.pt", _int)
    SPEC[_fam + "4"] = (G1, _fam + "_all_s{s}", 4, 512, "epochs/epoch_04.pt", _int)
SPEC["ATTbalW"] = (G3, "ATTbalW_all_s{s}", 2, 4096, "epochs/epoch_02.pt", "ATTx")      # G3: ATT+bal over the whole report

DISPLAY = {"released": "released Nebula", "A": "A (J)", "C": "C (J)", "C2": "C (J, 2 epochs)", "F": "F (whole report)",
           "ATTbal": "ATT+bal", "MMbal": "MM+bal", "Cbal": "C+bal", "ATTbal4": "ATT+bal (4 epochs)", "MMbal4": "MM+bal (4 epochs)",
           "Cbal4": "C+bal (4 epochs)", "ATTbalW": "ATT+bal whole report (G3)"}


def run_dir(key, s):
    out, tmpl = SPEC[key][:2]
    return out, tmpl.format(s=s)


def available(key, s):
    if key == "released":
        return True
    out, run = run_dir(key, s)
    return os.path.exists(os.path.join(out, "ckpt", run, SPEC[key][4])) and os.path.exists(os.path.join(out, "scores", f"{run}_epochs.npz"))


def window(key):
    return 512 if key == "released" else SPEC[key][3]


def load_model(key, s):
    """(model, window, unedited April logits (Kaggle logits of the run at the epoch used))."""
    if key == "released":
        m = build_level1(NEBULA, vocab_size=50001, pretrained=True).eval()
        plain = np.load(os.path.join(V.WORK, "perturbed_tokens_17402.npz"))["plain"].astype(np.int64)
        return m, 512, score512(m, plain)
    out, tmpl, ep, win, ck, internal = SPEC[key]
    run = tmpl.format(s=s)
    m = build_variant(NEBULA, internal, maxlen=win).eval()
    sd = torch.load(os.path.join(out, "ckpt", run, ck), map_location="cpu", weights_only=True)
    m.load_state_dict({k: (v.float() if v.is_floating_point() else v) for k, v in sd.items()})
    z0 = np.load(os.path.join(out, "scores", f"{run}_epochs.npz"))["april"][ep - 1]
    return m, win, z0


def score_tokens(model, win, toks):
    """logits of a list of token arrays (cut to the model's window)."""
    toks = [t[:win] for t in toks]
    if win == 512:
        return score512(model, to512(toks))
    return score_ragged(model, toks)


def cached(path, fn):
    if os.path.exists(path):
        return dict(np.load(path))
    d = fn()
    np.savez(path, **d)
    return d


def models_for(keys, seeds_by_key, require=True):
    """{display name: (key, [seeds])}, keeping the seeds whose files exist."""
    out = {}
    for k in keys:
        ss = [s for s in seeds_by_key.get(k, [0]) if available(k, s)]
        if ss or not require:
            out[DISPLAY[k]] = (k, ss)
    return out


def n_threads():
    t = int(os.environ.get("NTHREADS", os.cpu_count() or 4))
    torch.set_num_threads(t)
    return t


def ci(v, scale=100.0, fmt="+.1f"):
    return f"[{scale * np.percentile(v, 2.5):{fmt}}, {scale * np.percentile(v, 97.5):{fmt}}]"
