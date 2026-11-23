"""
ITEM B1 (NOTES 30.4 / 30.4a / 30.4b): self-supervised adaptation on unlabelled April reports (GPU job).   (OURS; the authors' trainers do the training)

    python -m baseline.b1 --tokens-find --variant bpe8k_fix --seeds 0 1 2 --out /kaggle/working/out

Per seed, three conditions on the same architecture (full-attention encoder, bidirectional flatten classifier, `lm.build_fullattn(V, 0.3, causal=False)`):
  (i)   random initialisation, then fine-tuning on the 75,298 labelled January reports (2 epochs, lr 1e-3, the authors' ModelTrainer, batch 96, weight decay 1e-2, clip 0.5);
  (ii)  causal AR pre-training on the January token rows (3 epochs, lr 2.5e-4), then the same fine-tuning;
  (iii) causal AR pre-training on the January token rows + the unlabelled ADAPT token rows, then the same fine-tuning on the labelled January reports.
This job reads NO April label: `labels.npz` is only read for y_train (January). The only April rows ever scored are the TEST rows (split of b1_split.py, sha256 checked), written as logits to
b1_seed<s>.npz together with the TEST indices; ADAPT rows are used as unlabelled token rows in (iii) only and are never scored. Evaluation (needs the labels) is baseline/gs_eval_b1.py, run locally afterwards.
"""
import argparse
import hashlib
import json
import os
import shutil
import time

import numpy as np

from baseline import common as C, cv, lm, selfsup
from baseline import selfsup_long as SL

HERE = os.path.dirname(os.path.abspath(__file__))
SPLIT = os.path.join(HERE, "b1_split_data.npz")
SPLIT_SHA = "c9808ac80617af62a62a233e284fce955c3993acb89f62ccecfcfbb19f9d3bd3"
BATCH, WD, CLIP, DROPOUT, FT_LR, FT_EPOCHS = 96, 1e-2, 0.5, 0.3, 1e-3, 2
PT_LR, PT_EPOCHS = 2.5e-4, 3


def load_tokens(a):
    tdir = C.find_dir_with("labels.npz") if a.tokens_find else a.tokens
    vdir = os.path.join(tdir, "variants", a.variant)
    assert os.path.exists(os.path.join(vdir, "x_train.npy")), f"no tokens in {vdir}"
    ytr = np.load(os.path.join(tdir, "labels.npz"))["y_train"]                      # January labels only (the file's April arrays are never indexed)
    return np.load(os.path.join(vdir, "x_train.npy")), ytr, np.load(os.path.join(vdir, "x_test.npy")), json.load(open(os.path.join(vdir, "vocab.json")))


def fine_tune(init_path, seed, x, y, V, device):
    """Build the downstream model, load the pre-trained encoder if `init_path`, train FT_EPOCHS with the authors' ModelTrainer. Returns (model, proof, seconds, final-epoch-free train info)."""
    import torch
    C.set_seed(seed)
    model = lm.build_fullattn(V, DROPOUT, causal=False)
    proof = SL.init_from_checkpoint(model, init_path) if init_path else {}
    dev = {"gpu": "cuda"}.get(device, device)
    if dev != "cpu":
        model.to(dev)
    trainer = cv.make_trainer(model, dev, "binary", a_batch(), FT_LR, WD, clip_grad_norm=CLIP)
    t0 = time.time()
    trainer.fit(x, y, epochs=FT_EPOCHS)
    return model, proof, round(time.time() - t0, 1), dev


_BATCH = [BATCH]


def a_batch():
    return _BATCH[0]


def run_seed(a, seed, x_tr, y_tr, x_te, vocab, adapt, test):
    import torch
    V = len(vocab)
    os.makedirs(a.out, exist_ok=True)
    done = os.path.join(a.out, f"b1_seed{seed}.npz")
    if os.path.exists(done):
        print(f"[seed {seed}] already done", flush=True)
        return
    info = {"seed": seed, "variant": a.variant, "V": V, "n_january_labelled": int(len(x_tr)), "n_adapt_rows_in_pretraining_iii": int(len(adapt)), "n_test": int(len(test)),
            "ft": {"lr": FT_LR, "epochs": FT_EPOCHS, "batch": a.batch_size, "wd": WD, "clip": CLIP, "dropout": DROPOUT}, "pt": {"lr": a.lr, "epochs": a.pt_epochs, "patience": a.pt_patience, "min_delta": a.min_delta}, "env": C.env_info()}
    xt_test = x_te[test]
    out = {"test_idx": test.astype(np.int64)}
    t_seed = time.time()
    for cond, x_unl in (("i", None), ("ii", x_tr), ("iii", np.concatenate([x_tr, x_te[adapt]]))):
        t0 = time.time()
        init = None
        if x_unl is not None:
            a.val_x = None                                    # selfsup.pretrain then holds out 2% of the pre-training rows for the LM validation loss (rows not trained on)
            C.set_seed(seed)
            pre, hist = selfsup.pretrain("ar", x_unl, vocab, a, seed, f"b1_pre_{cond}_seed{seed}")
            shutil.rmtree(os.path.join(selfsup.LIT_DIR, f"b1_pre_{cond}_seed{seed}"), ignore_errors=True)
            init = os.path.join(a.out, f"tmp_pre_{cond}_seed{seed}.pt")
            torch.save(pre, init)
            info[f"pretraining_{cond}"] = hist
            print(f"[seed {seed}] ({cond}) pre-training {len(hist['epochs'])} epochs, best {hist['best_epoch']}, val LM loss {[round(e['val_loss'], 3) for e in hist['epochs']]}, {hist['seconds']:.0f}s on {hist['n_pretrain']} rows", flush=True)
        model, proof, secs, dev = fine_tune(init, seed, x_tr, y_tr, V, a.device)
        z = cv.predict_logits(model, xt_test, dev, bs=512)
        out[f"logits_{cond}"] = z.astype(np.float32)
        info[f"finetune_{cond}"] = {"seconds": secs, "weight_proof": proof}
        info[f"total_{cond}_seconds"] = round(time.time() - t0, 1)
        print(f"[seed {seed}] ({cond}) done in {time.time() - t0:.0f}s; TEST logits mean {z.mean():.3f} sd {z.std():.3f}", flush=True)
        del model
        if init and os.path.exists(init):
            os.remove(init)
        if dev != "cpu":
            torch.cuda.empty_cache()
    info["seconds_total"] = round(time.time() - t_seed, 1)
    C.dump_json(info, os.path.join(a.out, f"b1_seed{seed}.json"))
    np.savez(done, **out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--tokens-find", action="store_true")
    ap.add_argument("--variant", default="bpe8k_fix")
    ap.add_argument("--out", default="out")
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--device", default="gpu")
    ap.add_argument("--batch-size", type=int, default=BATCH)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0, help="smoke test only: use this many January rows and this many ADAPT / TEST rows")
    ap.add_argument("--pt-epochs", type=int, default=PT_EPOCHS)
    ap.add_argument("--pt-patience", type=int, default=99)
    ap.add_argument("--min-delta", type=float, default=1e-6)
    ap.add_argument("--lr", type=float, default=PT_LR)
    a = ap.parse_args()
    _BATCH[0] = a.batch_size
    assert hashlib.sha256(open(SPLIT, "rb").read()).hexdigest() == SPLIT_SHA, "split file differs from the committed one"
    sp = np.load(SPLIT)
    adapt, test = sp["adapt"], sp["test"]
    assert not (set(adapt.tolist()) & set(test.tolist()))
    x_tr, y_tr, x_te, vocab = load_tokens(a)
    assert len(x_tr) == 75298 or a.limit or a.tokens
    if a.limit:
        x_tr, y_tr, adapt, test = x_tr[:a.limit], y_tr[:a.limit], adapt[:a.limit], test[:a.limit]
        x_te = x_te[:max(adapt.max(), test.max()) + 1] if False else x_te
    print(f"B1: {len(x_tr)} January rows, ADAPT {len(adapt)}, TEST {len(test)}, V {len(vocab)}, seeds {a.seeds}", flush=True)
    for s in a.seeds:
        run_seed(a, s, x_tr, y_tr, x_te, vocab, adapt, test)
    C.dump_json({"finished": time.strftime("%Y-%m-%d %H:%M:%S"), "seeds": a.seeds}, os.path.join(a.out, "b1_done.json"))


if __name__ == "__main__":
    main()
