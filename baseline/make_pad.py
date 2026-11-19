"""
Balanced padding arrays for the ATT+bal follow-up, and the padded April arrays of the random benign padding test.   (OURS; the procedure is that of nebula-length-study
round 4b, scripts/pooling_v4/make_aug.py --balanced and padding_eval.py, on our rows, our BPE-50k and our TRAIN pool)

    python -m baseline.make_pad --train --out <dir> [--seeds 0-9] [--epochs 1-2] [--workers 4]       # aug_s<seed>_e<epoch>_{rows,tok}.npy
    python -m baseline.make_pad --april --out <dir>                                                    # april_pad.npz (the padding test)

Data: the Nebula-filtered reports of all 92,700 Speakeasy reports in `hier_data/signal/reps.bin` (the length study's `Reps`; made by the same PEDynamicFeatureExtractor), mapped to our
rows by report name (`results/padding/row_map.npz`, verified: the unedited reports re-tokenise to exactly the stored x_train / x_test rows). A report is a dict with the list of API
calls under "apis"; a "call" is one element of that list.

Training arrays ("balanced": malware and benign reports alike): for every report of the 90% January slice, numpy default_rng([7000, seed, epoch, row]): with probability 0.5 the report is
edited (and has at least one call); mode "insert" (k random gaps of its call list) or "prepend" (before the first call), 50/50; k ~ U{1..50}; each added call = a random call (uniform report
of the pool, then a uniform call of that report). TRAIN POOL = the benign reports of the 90% slice (with at least one call): never the validation slice, never April. The edited report is
re-tokenised with our BPE-50k and cut to the first 512 tokens (uint16, zero = padding).

April arrays (the padding test): every April malware report and 2,000 random benign April reports (numpy seed 7), each edited with k = 5, 20, 50 calls in mode prepend and insert
(default_rng([6000, row, k, mode]); 6 edits), the calls drawn from the EVAL POOL = the benign reports of the 10% validation slice (never trained on, disjoint from the train pool, not April).
"""
import argparse
import json
import os
import time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPS = "/home/user/hier_data/signal"
TOKENS = os.path.join(ROOT, "results", "_tokens_raw", "out")
ROW_MAP = os.path.join(ROOT, "results", "padding", "row_map.npz")
KS_TEST = (5, 20, 50)
EDITS = [f"{m}_{k}" for m in ("insert", "prepend") for k in KS_TEST]
N_BEN_SUB = 2000


# ----------------------------------------------------------------------------- pure functions (tested)
def plan_train_row(row, seed, epoch, n_apis, pool_n_apis, stream=7000):
    """None (not edited) or {"mode", "k", "draws": [(pool index, call index)] * k, "gaps": sorted gap positions (insert) or None}. numpy default_rng([stream, seed, epoch, row]);
    stream 7000 is the stream of REPORT 5.10 (balanced and malware-only runs), 7100 the new stream of the 'keep' runs (clean copies)."""
    rng = np.random.default_rng([int(stream), int(seed), int(epoch), int(row)])
    if rng.random() >= 0.5 or n_apis == 0:
        return None
    mode = "insert" if rng.random() < 0.5 else "prepend"
    k = int(rng.integers(1, 51))
    draws = []
    for _ in range(k):
        r = int(rng.integers(len(pool_n_apis)))
        draws.append((r, int(rng.integers(pool_n_apis[r]))))
    gaps = np.sort(rng.integers(0, n_apis + 1, k)) if mode == "insert" else None
    return {"mode": mode, "k": k, "draws": draws, "gaps": gaps}


def plan_test_row(row, k, mode, n_apis, pool_n_apis):
    """The padding of the test: the same procedure with a fixed k and mode, default_rng([6000, row, k, 0 if insert else 1])."""
    rng = np.random.default_rng([6000, int(row), int(k), 0 if mode == "insert" else 1])
    draws = []
    for _ in range(k):
        r = int(rng.integers(len(pool_n_apis)))
        draws.append((r, int(rng.integers(pool_n_apis[r]))))
    gaps = np.sort(rng.integers(0, n_apis + 1, k)) if mode == "insert" else None
    return {"mode": mode, "k": k, "draws": draws, "gaps": gaps}


def apply_plan(apis, plan, calls):
    """The call list of the edited report: `calls` = the k added calls in draw order. Prepend: added + original; insert: the added calls go into their (sorted) gaps, the original order is kept."""
    if plan["mode"] == "prepend":
        return list(calls) + list(apis)
    gaps, out, j, n = plan["gaps"], [], 0, len(apis)
    for i in range(n + 1):
        while j < plan["k"] and gaps[j] == i:
            out.append(calls[j]); j += 1
        if i < n:
            out.append(apis[i])
    return out


def to512(tokens):
    x = np.zeros(512, dtype=np.uint16)
    t = np.asarray(tokens[:512], dtype=np.uint16)
    x[:len(t)] = t
    return x


# ----------------------------------------------------------------------------- data access
class Reps:
    """Nebula-filtered reports (orjson blobs in reps.bin, offsets in reps_off.npy)."""

    def __init__(self, root=REPS):
        self.off = np.load(os.path.join(root, "reps_off.npy"))
        self.path, self.fh = os.path.join(root, "reps.bin"), None

    def get(self, i):
        import orjson
        if self.fh is None:
            self.fh = open(self.path, "rb")
        self.fh.seek(self.off[i])
        return orjson.loads(self.fh.read(self.off[i + 1] - self.off[i]))

    def n_apis_all(self, cache):
        """Number of calls of every report (one sequential pass, cached)."""
        if os.path.exists(cache):
            return np.load(cache)
        import orjson
        n = np.zeros(len(self.off) - 1, dtype=np.int32)
        with open(self.path, "rb") as fh:
            for i in range(len(n)):
                n[i] = len(orjson.loads(fh.read(self.off[i + 1] - self.off[i])).get("apis") or [])
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        np.save(cache, n)
        return n


def build_row_map(tokens=TOKENS):
    """Our x_train / x_test rows -> rows of reps.bin (= rows of results/hier/data/meta.csv), by (split, name). Verified against the labels."""
    import pandas as pd
    meta = pd.read_csv(os.path.join(ROOT, "results", "hier", "data", "meta.csv"))

    def norm(i):
        for e in (".json", ".dat"):
            if i.endswith(e):
                i = i[:-len(e)]
        return i
    mrow = {}
    for k, (s, i) in enumerate(zip(meta.split.values, meta.id.values)):
        assert (s, norm(i)) not in mrow
        mrow[(s, norm(i))] = k
    key = lambda n: (n.split("/")[0].replace("windows_emulation_", ""), norm(n.split("/")[-1]))
    tr = np.array([mrow[key(n)] for n in json.load(open(os.path.join(tokens, "names_train.json")))], dtype=np.int32)
    te = np.array([mrow[key(n)] for n in json.load(open(os.path.join(tokens, "names_test.json")))], dtype=np.int32)
    lab = np.load(os.path.join(tokens, "labels.npz"))
    assert len(set(tr)) == len(tr) and len(set(te)) == len(te)
    assert (meta.label.values[tr] == lab["y_train"]).all() and (meta.label.values[te] == lab["y_test"]).all()
    return tr, te


def load_row_map():
    if not os.path.exists(ROW_MAP):
        tr, te = build_row_map()
        os.makedirs(os.path.dirname(ROW_MAP), exist_ok=True)
        np.savez_compressed(ROW_MAP, train=tr, test=te)
    d = np.load(ROW_MAP)
    return d["train"], d["test"]


def make_tokenizer(released=False):
    """Our BPE-50k (baseline_models/tokenizers/bpe50k), or with released=True the tokenizer of the released checkpoint (authors' bpe_50000_sentencepiece.model + bpe_50000_vocab.json)."""
    from baseline import common as C
    nb = C.setup_nebula(require_patched=True)
    from nebula.constants import JSON_CLEANUP_SYMBOLS, SPEAKEASY_TOKEN_STOPWORDS
    from nebula.preprocessing import JSONTokenizerBPE
    if released:
        objs = os.path.join(nb["nebula_root"], "nebula", "objects")
        model, vocab_file = os.path.join(objs, "bpe_50000_sentencepiece.model"), os.path.join(objs, "bpe_50000_vocab.json")
    else:
        tdir = os.path.join(ROOT, "baseline_models", "tokenizers", "bpe50k")
        model, vocab_file = os.path.join(tdir, "tokenizer.model"), os.path.join(tdir, "vocab.json")
    vocab = json.load(open(vocab_file))
    return JSONTokenizerBPE(vocab_size=len(vocab), seq_len=512, model_path=model, vocab=vocab_file, cleanup_symbols=JSON_CLEANUP_SYMBOLS, stopwords=SPEAKEASY_TOKEN_STOPWORDS)


# ----------------------------------------------------------------------------- worker side (fork: the globals are set in the parent before the pool is created)
_G = {}


def _worker(jobs):
    """jobs: list of (row, rep_row, plan). Returns [(row, uint16[512], k, mode flag)] (batched tokenisation)."""
    tok, calls, pool_rep_rows = _G["tok"], _G["calls"], _G["pool_rep_rows"]
    if _G.get("local_pid") != os.getpid():                          # every worker has its OWN file handle (a handle inherited by fork shares its offset between processes)
        _G["local"], _G["local_pid"] = Reps(), os.getpid()
    reps = _G["local"]
    out, batch, meta = [], [], []
    for row, rep_row, plan in jobs:
        rep = reps.get(int(rep_row))
        added = [calls[(plan["pool"][j] if "pool" in plan else pool_rep_rows[r], c)] for j, (r, c) in enumerate(plan["draws"])]
        r2 = dict(rep)
        r2["apis"] = apply_plan(list(rep.get("apis") or []), plan, added)
        batch.append(r2); meta.append((row, plan["k"], 0 if plan["mode"] == "insert" else 1))
        if len(batch) == 64:
            out += [(m[0], to512(t), m[1], m[2]) for t, m in zip(tok.encode(batch, pad=False), meta)]
            batch, meta = [], []
    if batch:
        out += [(m[0], to512(t), m[1], m[2]) for t, m in zip(tok.encode(batch, pad=False), meta)]
    return out


def fetch_calls(reps, draws_by_rep):
    """{(rep_row, call index): call dict} for all needed calls; each pool report is read once, in file order."""
    calls = {}
    for rep_row in sorted(draws_by_rep):
        apis = reps.get(int(rep_row)).get("apis") or []
        for c in draws_by_rep[rep_row]:
            calls[(rep_row, c)] = apis[c]
    return calls


def run_jobs(jobs, workers):
    chunks = [jobs[i:i + 256] for i in range(0, len(jobs), 256)]
    with get_context("fork").Pool(workers) as pool:
        res = [r for part in pool.imap(_worker, chunks) for r in part]
    return res


# ----------------------------------------------------------------------------- the two modes
def setup(seeds_epochs_note=""):
    from baseline import common as C, gap
    tr_map, te_map = load_row_map()
    lab = np.load(os.path.join(TOKENS, "labels.npz"))
    trn, val = gap.val_slice(lab["ym_train"])                         # asserts the hash
    reps = Reps()
    n_apis = reps.n_apis_all(os.path.join(ROOT, "results", "padding", "n_apis.npy"))
    return tr_map, te_map, lab, trn, val, reps, n_apis


def make_train(a):
    tr_map, te_map, lab, trn, val, reps, n_apis = setup()
    y = lab["y_train"]
    pool_rows = np.array([r for r in trn if y[r] == 0 and n_apis[tr_map[r]] > 0])               # TRAIN pool: benign reports of the 90% slice only
    assert not set(pool_rows.tolist()) & set(val.tolist())
    pool_rep_rows = tr_map[pool_rows]
    pool_n = n_apis[pool_rep_rows]
    print(f"train pool: {len(pool_rows):,} benign reports of the 90% slice (validation slice excluded), {int(pool_n.sum()):,} calls", flush=True)
    tok = make_tokenizer()
    _G.update(reps=reps, tok=tok, pool_rep_rows=pool_rep_rows)
    os.makedirs(a.out, exist_ok=True)
    stats = {}
    for s in rng_range(a.seeds):
        for e in rng_range(a.epochs):
            t0 = time.time()
            rows = trn[:a.limit] if a.limit else trn
            plans = [(int(r), plan_train_row(r, s, e, int(n_apis[tr_map[r]]), pool_n)) for r in rows]
            plans = [(r, p) for r, p in plans if p is not None]
            need = {}
            for _, p in plans:
                for pr, c in p["draws"]:
                    need.setdefault(int(pool_rep_rows[pr]), set()).add(c)
            t1 = time.time()
            _G["calls"] = fetch_calls(reps, need)
            t2 = time.time()
            res = run_jobs([(r, tr_map[r], p) for r, p in plans], a.workers)
            order = np.argsort([r[0] for r in res])
            res = [res[i] for i in order]
            np.save(os.path.join(a.out, f"aug_s{s}_e{e}_rows.npy"), np.array([r[0] for r in res], dtype=np.int64))
            np.save(os.path.join(a.out, f"aug_s{s}_e{e}_tok.npy"), np.stack([r[1] for r in res]))
            ks, md = np.array([r[2] for r in res]), np.array([r[3] for r in res])
            yy = y[[r[0] for r in res]]
            stats[f"s{s}_e{e}"] = {"reports": int(len(rows)), "edited": int(len(res)), "edited_malware": int((yy == 1).sum()), "edited_benign": int((yy == 0).sum()),
                                   "mean_k": float(ks.mean()), "share_prepend": float(md.mean()), "seconds": round(time.time() - t0, 1)}
            print(f"seed {s} epoch {e}: {len(res):,} of {len(rows):,} reports edited ({int((yy == 1).sum()):,} malware, {int((yy == 0).sum()):,} benign), mean k {ks.mean():.1f}, "
                  f"prepend {100 * md.mean():.0f}% | plan {t1 - t0:.0f}s, fetch {t2 - t1:.0f}s, tokenise {time.time() - t2:.0f}s, total {time.time() - t0:.0f}s", flush=True)
    json.dump(stats, open(os.path.join(a.out, "aug_stats.json"), "w"), indent=1)


def make_april(a):
    tr_map, te_map, lab, trn, val, reps, n_apis = setup()
    y_tr, y_te = lab["y_train"], lab["y_test"]
    pool_rows = np.array([r for r in val if y_tr[r] == 0 and n_apis[tr_map[r]] > 0])             # EVAL pool: benign reports of the validation slice
    assert not set(pool_rows.tolist()) & set(trn.tolist())
    pool_rep_rows = tr_map[pool_rows]
    pool_n = n_apis[pool_rep_rows]
    print(f"eval pool: {len(pool_rows):,} benign reports of the validation slice, {int(pool_n.sum()):,} calls", flush=True)
    mal, ben = np.flatnonzero(y_te == 1), np.flatnonzero(y_te == 0)
    ben = np.sort(np.random.default_rng(7).choice(ben, N_BEN_SUB, replace=False))
    pos = np.concatenate([mal, ben])
    if a.limit:
        pos = np.concatenate([mal[:a.limit], ben[:a.limit]])
    tok = make_tokenizer()
    _G.update(reps=reps, tok=tok, pool_rep_rows=pool_rep_rows)
    toks = np.zeros((len(EDITS), len(pos), 512), dtype=np.uint16)
    t0 = time.time()
    for j, name in enumerate(EDITS):
        mode, k = name.split("_")[0], int(name.split("_")[1])
        plans = [(int(p), plan_test_row(p, k, mode, int(n_apis[te_map[p]]), pool_n) if n_apis[te_map[p]] > 0 else None) for p in pos]
        need = {}
        for _, p in plans:
            if p is not None:
                for pr, c in p["draws"]:
                    need.setdefault(int(pool_rep_rows[pr]), set()).add(c)
        _G["calls"] = fetch_calls(reps, need)
        res = dict((r[0], r[1]) for r in run_jobs([(p, te_map[p], pl) for p, pl in plans if pl is not None], a.workers))
        plain = None
        for i, (p, pl) in enumerate(plans):
            if pl is not None:
                toks[j, i] = res[p]
            else:                                                       # a report without calls is left unedited
                if plain is None:
                    plain = np.load(os.path.join(a.plain, "x_test.npy"), mmap_mode="r")
                toks[j, i] = np.asarray(plain[p][:512], dtype=np.uint16)
        print(f"edit {name}: done ({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(os.path.join(a.out, "april_pad.npz"), pos=pos, y=y_te[pos].astype(np.int8), n_mal=len(mal) if not a.limit else a.limit, edits=np.array(EDITS), tok=toks)
    print(f"April padding arrays: {len(pos):,} reports x {len(EDITS)} edits in {time.time() - t0:.0f}s", flush=True)


def rng_range(s):
    a, b = (str(s).split("-") + [str(s)])[:2]
    return list(range(int(a), int(b) + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--train", action="store_true")
    ap.add_argument("--april", action="store_true")
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--epochs", default="1-2")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--plain", default=os.path.join(ROOT, "results", "_pe_tokens", "variants", "bpe50k"), help="folder with x_test.npy (unedited tokens, for reports without calls)")
    a = ap.parse_args()
    if a.train:
        make_train(a)
    if a.april:
        make_april(a)


if __name__ == "__main__":
    main()
