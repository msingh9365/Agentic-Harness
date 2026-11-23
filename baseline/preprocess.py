"""
Job 1 (CPU): the authors' cleaning + their tokenizers -> int32 token arrays, labels, split indices.   (OURS: the driver.)

What is theirs and what is ours
  theirs  report reading + labels from folder names (read_and_filter_json_folders), JSON filter and normalization
          (PEDynamicFeatureExtractor.filter_and_normalize_report), BPE / Whitespace / Wordpunct tokenizers (train and
          encode), the released tokenizer files.
  ours    this driver. It calls their functions in the same order as their wrapper preprocess_nebula_speakeasy()
          (nebula/preprocessing/wrappers.py), but filters the reports ONCE (in parallel, one folder per worker) and
          reuses the filtered events for every tokenizer variant, instead of re-reading 92k files per variant.
          tests/test_preprocess.py checks that the arrays are identical to their wrapper's on a sample.

Output folder layout (published as the private Kaggle dataset msingh9365/nebula-baseline-tokens)
  meta.json                         counts, versions, timings
  labels.npz                        y_train/y_test (binary), ym_train/ym_test (0 clean, 1 backdoor, ... 7 trojan)
  names_train.json, names_test.json file path of every row (row order = array order)
  splits.json                       3-fold CV indices and the stratified 80/20 splits used by the self-supervised runs
  variants/<name>/x_train.npy, x_test.npy, vocab.json, tokenizer.model (BPE), info.json
"""
import argparse
import os
import pickle
import shutil
import sys
import time
from multiprocessing import Pool

os.environ.setdefault("TQDM_DISABLE", "1")     # their readers use tqdm; keep the logs small

import numpy as np

from baseline import common as C

# ---------------------------------------------------------------------------- variants
VARIANTS = {
    # main experiments
    "bpe50k": dict(kind="bpe", vocab=50000, seq=512),
    "ws50k": dict(kind="whitespace", vocab=50000, seq=512),
    "bpe8k": dict(kind="bpe", vocab=8192, seq=512),          # self-supervised experiments (paper Sec. 4.5)
    "bpe50k_gs": dict(kind="bpe", vocab=50000, seq=512),     # NOTES 21: the same as bpe50k, but fit on the TRAINING part of the group split only (baseline/gs_tokens.py)
    "bpe50k_all": dict(kind="bpe", vocab=50000, seq=512),    # NOTES 22.7: re-fit on ALL 75,298 January reports with the same settings as bpe50k (reproduction check of the old tokenizer, baseline/gs_tokrepro.py)
    "bpe50k_fix": dict(kind="bpe", vocab=50000, seq=512,     # NOTES 25: the old bpe50k + full character coverage and byte fallback, id 0 = padding only (pad_id 0, unk_id 1, no bos/eos); fit on ALL 75,298 January reports (baseline/gs_tokens_fix.py)
                       spm_extra="--character_coverage=1.0 --byte_fallback=true --pad_id=0 --unk_id=1 --bos_id=-1 --eos_id=-1"),
    "bpe50k_role": dict(kind="bpe", vocab=50000, seq=512, norm="role", unkfix=True),     # NOTES 27 / 24 P3: hex literals of > 4 digits -> addr<L>x<T>; unknown pieces -> id 50,000 (baseline/gs_tokens_p3.py)
    "bpe50k_addr": dict(kind="bpe", vocab=50000, seq=512, norm="addr", unkfix=True),     # the length-matched control of P3: every such literal -> the single word `addr`
    "bpe8k_fix": dict(kind="bpe", vocab=8192, seq=512,       # NOTES 30.4a (B1): the corrected tokenizer (full character coverage, byte fallback, pad 0 / unk 1) with vocabulary 8,192, fit on ALL 75,298 January reports (baseline/b1_tokens.py)
                      spm_extra="--character_coverage=1.0 --byte_fallback=true --pad_id=0 --unk_id=1 --bos_id=-1 --eos_id=-1"),
    "bpe8k_v2": dict(kind="bpe", vocab=8192, seq=512),       # B3: the same, but the tokenizer is fit on the 90% of January that is not the validation slice (--fit-gap-split)
    # released tokenizers (their files, no training): sanity check E
    "released_bpe50k": dict(kind="bpe", released=True, seq=512),
    "released_ws50k": dict(kind="whitespace", released=True, seq=512),
    # LEGACY cleaning (ours, inferred): the released Whitespace vocabulary contains tokens like 'apiname', 'retval' and
    # 'kernel32getprocaddress', i.e. it was built with punctuation deleted and the stopwords kept. The pinned repo's tokenizer
    # does the opposite, and the released Whitespace model scores AUC 0.77 with it but 0.94 with the legacy cleaning (NOTES.md 4).
    "ws50k_legacy": dict(kind="whitespace", vocab=50000, seq=512, legacy=True),
    "released_ws50k_legacy": dict(kind="whitespace", released=True, legacy=True, seq=512),
    # ablations (paper Table 4, Table 6)
    "bpe5k": dict(kind="bpe", vocab=5000, seq=512),
    "bpe10k": dict(kind="bpe", vocab=10000, seq=512),
    "bpe30k": dict(kind="bpe", vocab=30000, seq=512),
    "bpe70k": dict(kind="bpe", vocab=70000, seq=512),
    "wp50k": dict(kind="wordpunct", vocab=50000, seq=512),
}

_EXTRACTOR = None


def _init_worker(nebula_root):
    global _EXTRACTOR
    C.setup_nebula(nebula_root)
    from nebula.constants import SPEAKEASY_RECORD_FIELDS, SPEAKEASY_RECORD_LIMITS
    from nebula.preprocessing import PEDynamicFeatureExtractor
    _EXTRACTOR = PEDynamicFeatureExtractor(speakeasyRecordFields=SPEAKEASY_RECORD_FIELDS, recordLimits=SPEAKEASY_RECORD_LIMITS)


def _filter_folder(job):
    """Their reader on ONE report_* folder: -> (events, multiclass labels, file paths)."""
    folder, limit = job
    from nebula.preprocessing.normalization import read_and_filter_json_folders
    t = time.time()
    events, y, paths = read_and_filter_json_folders(
        subFolders=[folder], filter_function=_EXTRACTOR.filter_and_normalize_report,
        benign_folders=C.BENIGN_FOLDERS, limit=limit, multiclass=True)
    print(f"  filtered {os.path.basename(folder)}: {len(events)} reports in {time.time() - t:.0f}s", flush=True)
    return events, y, paths


def filter_split(split_dir, nebula_root, workers, limit=None):
    folders = sorted(os.path.join(split_dir, x) for x in os.listdir(split_dir) if x.startswith("report_"))
    # biggest folders first so the pool does not end on a straggler
    folders.sort(key=lambda f: -len(os.listdir(f)))
    with Pool(workers, initializer=_init_worker, initargs=(nebula_root,)) as pool:
        results = dict(zip(folders, pool.map(_filter_folder, [(f, limit) for f in folders], chunksize=1)))
    events, y, paths = [], [], []
    for f in sorted(results):                      # deterministic order: sorted folder names
        e, yy, p = results[f]
        events += e; y += yy; paths += p
    return events, np.array(y, dtype=np.int8), paths


# ---------------------------------------------------------------------------- tokenizers (all theirs)
def _tok_common():
    from nebula.constants import JSON_CLEANUP_SYMBOLS, SPEAKEASY_TOKEN_STOPWORDS
    return dict(cleanup_symbols=JSON_CLEANUP_SYMBOLS, stopwords=SPEAKEASY_TOKEN_STOPWORDS)


def legacy_whitespace_class():
    """OURS (inferred, not their code): their whitespace tokenizer with the cleaning that the released vocabulary implies:
    the cleanup symbols become spaces, ALL other punctuation is deleted (so 'kernel32.getprocaddress' -> 'kernel32getprocaddress',
    'api_name' -> 'apiname'), and no stopwords are removed."""
    import string
    from nebula.preprocessing import JSONTokenizerNaive

    class LegacyWhitespaceTokenizer(JSONTokenizerNaive):
        def clear_json_event(self, text):
            text = str(text).lower()
            for p in self.cleanup_symbols:
                text = text.replace(p, " ")
            return text.translate(str.maketrans("", "", string.punctuation))
    return LegacyWhitespaceTokenizer


HEX_RE = None


def _hex_norm(mode):
    """NOTES 24 P3: the hexadecimal literals 0x[0-9a-f]+ of MORE than 4 hex digits (applied to the lower-cased text, before the authors' cleaning). role: addr<L>x<T> (L digits, T the leading digit); addr: the single word `addr`."""
    import re
    global HEX_RE
    HEX_RE = HEX_RE or re.compile(r"0x[0-9a-f]{5,}")
    if mode == "role":
        return lambda t: HEX_RE.sub(lambda m: "addr%dx%s" % (len(m.group()) - 2, m.group()[2]), t)
    return lambda t: HEX_RE.sub("addr", t)


class _UnkProxy:
    """SentencePiece encoder whose unknown pieces (id 0 = the padding id) get the dedicated id 50,000 (NOTES 24 P1 fix); everything else is delegated."""
    def __init__(self, sp):
        self._sp = sp

    def encode_as_ids(self, x):
        r = self._sp.encode_as_ids(x)
        if r and isinstance(r[0], list):
            return [[50000 if t == 0 else t for t in row] for row in r]
        return [50000 if t == 0 else t for t in r]

    def __getattr__(self, k):
        return getattr(self._sp, k)


def build_tokenizer(spec, nebula_root, model_path=None, vocab_file=None):
    tok = _build_tokenizer(spec, nebula_root, model_path, vocab_file)
    if spec.get("norm"):                                              # normalised text for the fit, the encoding and the call-token store (all call tok.clear_json_event)
        f, orig = _hex_norm(spec["norm"]), tok.clear_json_event

        def clear(text):
            if isinstance(text, bytes):
                text = text.decode("utf-8")
            text = " ".join(text) if isinstance(text, list) and text and isinstance(text[0], str) else str(text)
            return orig(f(text.lower()))
        tok.clear_json_event = clear
    if spec.get("unkfix") and model_path is not None:                 # a loaded model: proxy its encoder (a freshly trained tokenizer is re-built from its model file by run_variant)
        tok.tokenizer = _UnkProxy(tok.tokenizer)
    return tok


def _build_tokenizer(spec, nebula_root, model_path=None, vocab_file=None):
    """spec: a VARIANTS entry. model_path: the trained BPE .model / whitespace vocab .json to load (None = untrained)."""
    from nebula.preprocessing import JSONTokenizerBPE, JSONTokenizerNaive
    if spec.get("legacy"):
        JSONTokenizerNaive = legacy_whitespace_class()
    objs = os.path.join(nebula_root, "nebula", "objects")
    if spec.get("released"):
        if spec["kind"] == "bpe":
            vocab_file = os.path.join(objs, "bpe_50000_vocab.json")
            import json
            n = len(json.load(open(vocab_file)))
            return JSONTokenizerBPE(vocab_size=n, seq_len=spec["seq"], vocab=vocab_file,
                                    model_path=os.path.join(objs, "bpe_50000_sentencepiece.model"))
        vocab_file = os.path.join(objs, "whitespace_50000_vocab.json")
        import json
        n = len(json.load(open(vocab_file)))
        return JSONTokenizerNaive(vocab_size=n, seq_len=spec["seq"], vocab=vocab_file)
    common = _tok_common()
    if spec["kind"] == "bpe":
        if model_path is None:
            tok = JSONTokenizerBPE(vocab_size=spec["vocab"], seq_len=spec["seq"], **common)
            if spec.get("spm_extra"):                                  # the authors' train() unchanged; only its SentencePiece call gets the extra flags appended (NOTES 25)
                import sentencepiece as spm

                class _ExtraTrainer:
                    def Train(self, cmd, _extra=spec["spm_extra"]):
                        print(f"[spm] extra flags: {_extra}", flush=True)
                        return spm.SentencePieceTrainer.Train(cmd + " " + _extra)
                tok.tokenizer = _ExtraTrainer()
            return tok
        return JSONTokenizerBPE(vocab_size=spec["vocab"], seq_len=spec["seq"], model_path=model_path, vocab=vocab_file, **common)
    tok = JSONTokenizerNaive(vocab_size=spec["vocab"], seq_len=spec["seq"], counter_dump=model_path is None,
                             type=spec["kind"], **common)
    if model_path is not None:
        tok.load_vocab(model_path)
    return tok


def run_variant(name, events_train, events_test, out_dir, nebula_root, seq_lens=(), reuse_dir=None, tok_train_frac=1.0, tok_fit_idx=None):
    """Train the tokenizer on TRAIN only (unless released), encode train and test. Mirrors preprocess_nebula_speakeasy().
    reuse_dir: a published tokens folder; if it holds this variant, its tokenizer is loaded instead of retrained (used to
    re-encode at other sequence lengths for the length ablation)."""
    import json
    spec = VARIANTS[name]
    vdir = os.path.join(out_dir, "variants", name)
    if os.path.exists(os.path.join(vdir, "x_test.npy")):
        print(f"[{name}] exists, skipping", flush=True)
        return
    os.makedirs(vdir, exist_ok=True)
    t0 = time.time()
    reused = os.path.join(reuse_dir, "variants", name) if reuse_dir else None
    if reused and os.path.exists(os.path.join(reused, "vocab.json")) and not spec.get("released"):
        files = os.path.join(reused, "tokenizer.model") if spec["kind"] == "bpe" else os.path.join(reused, "vocab.json")
        tok_train = tok_test = build_tokenizer(spec, nebula_root, model_path=files, vocab_file=os.path.join(reused, "vocab.json"))
        trained = False
        print(f"[{name}] reusing the tokenizer of {reused}", flush=True)
    elif spec.get("released"):
        tok_train = tok_test = build_tokenizer(spec, nebula_root)
        trained = False
    else:
        tok = build_tokenizer(spec, nebula_root)
        prefix = os.path.join(vdir, f"tokenizer_{spec['vocab']}")
        corpus = events_train
        if tok_fit_idx is not None:     # B3: fit on these train reports only (the 90% of follow-up F); all train reports are still encoded
            corpus = [events_train[i] for i in tok_fit_idx]
        elif tok_train_frac < 1.0:        # FALLBACK ONLY (memory/time): a random subset of the TRAIN reports; recorded in info.json
            pick = np.random.default_rng(0).permutation(len(events_train))[:int(tok_train_frac * len(events_train))]
            corpus = [events_train[i] for i in sorted(pick)]
        print(f"[{name}] training {spec['kind']} tokenizer (vocab {spec['vocab']}) on {len(corpus)} of {len(events_train)} train reports ...", flush=True)
        tok.train(corpus, vocab_size=spec["vocab"], model_prefix=prefix)
        print(f"[{name}] tokenizer trained in {(time.time() - t0) / 60:.1f} min", flush=True)
        # as in their wrapper: the test set is encoded with the tokenizer loaded from the files written by train
        model_file = prefix + ".model" if spec["kind"] == "bpe" else prefix + "_vocab.json"
        tok_test = build_tokenizer(spec, nebula_root, model_path=model_file)
        tok_train = tok_test if (spec.get("norm") or spec.get("unkfix")) else tok
        trained = True
    t1 = time.time()
    enc_train = tok_train.encode(events_train, pad=False)
    enc_test = tok_test.encode(events_test, pad=False)
    lens = {"train": np.array([len(e) for e in enc_train]), "test": np.array([len(e) for e in enc_test])}
    for n in sorted(set([spec["seq"], *seq_lens])):
        sfx = "" if n == spec["seq"] else f"_len{n}"
        xtr = tok_train.pad_sequence_list(enc_train, seq_len=n)
        xte = tok_test.pad_sequence_list(enc_test, seq_len=n)
        np.save(os.path.join(vdir, f"x_train{sfx}.npy"), xtr)
        np.save(os.path.join(vdir, f"x_test{sfx}.npy"), xte)
    vocab = tok_test.vocab
    with open(os.path.join(vdir, "vocab.json"), "w") as f:
        json.dump(vocab, f)
    if spec["kind"] == "bpe":
        dst = os.path.join(vdir, "tokenizer.model")
        if spec.get("released"):
            shutil.copy(os.path.join(nebula_root, "nebula", "objects", "bpe_50000_sentencepiece.model"), dst)
        elif reused and os.path.exists(os.path.join(reused, "tokenizer.model")):
            shutil.copy(os.path.join(reused, "tokenizer.model"), dst)           # reused tokenizer: copy, nothing was trained
        else:
            shutil.move(os.path.join(vdir, f"tokenizer_{spec['vocab']}.model"), dst)
    for f in os.listdir(vdir):                      # keep only what is needed
        if f.startswith("tokenizer_") and f != "tokenizer.model":
            if f.endswith("_vocab.json") or f.endswith("_counter.json"):
                os.remove(os.path.join(vdir, f))
    info = {"name": name, **spec, "trained_on_train": trained, "vocab_entries": len(vocab),
            "seq_len": spec["seq"], "tokenizer_train_fraction": tok_train_frac if trained else None,
            "tokenizer_fit_reports": (len(tok_fit_idx) if tok_fit_idx is not None else len(events_train)) if trained else None, "train_tokens_median": float(np.median(lens["train"])),
            "share_train_longer_than_seq": float((lens["train"] > spec["seq"]).mean()),
            "share_test_longer_than_seq": float((lens["test"] > spec["seq"]).mean()),
            "minutes_total": round((time.time() - t0) / 60, 1), "minutes_encoding": round((time.time() - t1) / 60, 1)}
    C.dump_json(info, os.path.join(vdir, "info.json"))
    print(f"[{name}] done: {info}", flush=True)


# ---------------------------------------------------------------------------- splits
def make_splits(y_bin, ym, seeds=(0, 1, 2)):
    """3-fold CV indices exactly as the authors' CrossValidation.run_folds() builds them, plus the stratified 80/20 split
    (80% unlabeled for pre-training, 20% labeled) of the self-supervised experiments, one per seed."""
    from sklearn.model_selection import KFold, train_test_split
    n = len(y_bin)
    kf = KFold(n_splits=3, shuffle=True, random_state=C.CV_RANDOM_STATE)
    folds = [{"train": tr.tolist(), "val": va.tolist()} for tr, va in kf.split(np.arange(n))]
    ssl = {}
    for s in seeds:
        unl, lab = train_test_split(np.arange(n), train_size=0.8, stratify=ym, random_state=s)
        ssl[str(s)] = {"unlabeled": np.sort(unl).tolist(), "labeled": np.sort(lab).tolist()}
    return {"cv_random_state": C.CV_RANDOM_STATE, "kfold3": folds, "ssl_80_20_stratified_by_family": ssl}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None, help="folder holding windows_emulation_trainset/ and windows_emulation_testset/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--variants", default="bpe50k,ws50k,bpe8k,released_bpe50k,released_ws50k")
    ap.add_argument("--seq-lens", default="", help="extra sequence lengths for the first BPE/whitespace variants (ablation)")
    ap.add_argument("--limit", type=int, default=None, help="files per folder (smoke tests only)")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--nebula", default=None)
    ap.add_argument("--tok-train-frac", type=float, default=1.0, help="fallback: train tokenizers on this fraction of the train reports")
    ap.add_argument("--reuse", default=None, help="published tokens folder whose tokenizers are reused (no retraining)")
    ap.add_argument("--work", default="/tmp/nebula_events", help="cache for the filtered events")
    ap.add_argument("--fit-gap-split", action="store_true", help="B3: variants ending in _v2 fit their tokenizer on the 90%% training part of follow-up F's split (gap_split_hash.json, asserted)")
    a = ap.parse_args()

    info = C.setup_nebula(a.nebula, require_patched=False)
    print("nebula:", info, "\nenv:", C.env_info(), flush=True)
    data = a.data or C.find_data_root()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    seq_lens = [int(x) for x in a.seq_lens.split(",") if x]
    t0 = time.time()
    ev = {}
    for split in ["train", "test"]:
        cache = os.path.join(a.work, f"{split}_{a.limit}.pkl")
        if os.path.exists(cache):
            ev[split] = pickle.load(open(cache, "rb"))
            print(f"[{split}] loaded cached events", flush=True)
            continue
        print(f"[{split}] filtering and normalizing with {a.workers} workers ...", flush=True)
        t = time.time()
        ev[split] = filter_split(os.path.join(data, f"windows_emulation_{split}set"), info["nebula_root"], a.workers, a.limit)
        pickle.dump(ev[split], open(cache, "wb"), protocol=4)
        print(f"[{split}] {len(ev[split][0])} reports in {(time.time() - t) / 60:.1f} min", flush=True)
    (ev_tr, ym_tr, names_tr), (ev_te, ym_te, names_te) = ev["train"], ev["test"]
    y_tr, y_te = (ym_tr > 0).astype(np.int8), (ym_te > 0).astype(np.int8)
    np.savez_compressed(os.path.join(a.out, "labels.npz"), y_train=y_tr, y_test=y_te, ym_train=ym_tr, ym_test=ym_te)
    C.dump_json([os.path.relpath(p, data) for p in names_tr], os.path.join(a.out, "names_train.json"))
    C.dump_json([os.path.relpath(p, data) for p in names_te], os.path.join(a.out, "names_test.json"))
    C.dump_json(make_splits(y_tr, ym_tr), os.path.join(a.out, "splits.json"))
    counts = {s: {c: int((ym == i).sum()) for i, c in enumerate(C.SPEAKEASY_CLASSES)} for s, ym in [("train", ym_tr), ("test", ym_te)]}
    C.dump_json({"nebula": info, "env": C.env_info(), "counts": counts, "n_train": len(y_tr), "n_test": len(y_te),
                 "malware_share": {"train": float(y_tr.mean()), "test": float(y_te.mean())},
                 "minutes_filtering": round((time.time() - t0) / 60, 1)}, os.path.join(a.out, "meta.json"))
    print("counts:", counts, flush=True)

    fit_idx = None
    if a.fit_gap_split:
        from baseline import gap
        fit_idx, val_idx = gap.val_slice(ym_tr)                       # asserts the hash of the stored split
        print(f"tokenizer fit on {len(fit_idx)} of {len(ym_tr)} train reports (validation slice of {len(val_idx)} left out)", flush=True)
    for name in [v for v in a.variants.split(",") if v]:
        run_variant(name, ev_tr, ev_te, a.out, info["nebula_root"], seq_lens, a.reuse, a.tok_train_frac, fit_idx if name.endswith("_v2") else None)
    print(f"all done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
