"""
Call-token store: the token arrays of the ORIGINAL reports, split into the pieces that an edit can move around, so that edited reports can be built IN MEMORY by concatenation.   (OURS)

An original report is a dict (the Nebula-filtered report, `hier_data/signal/reps.bin`); the tokenizer cleans `str(report)` (lower case, symbols to spaces, 12 stop-word patterns removed,
punctuation to spaces) and SentencePiece-BPE splits the cleaned text at spaces, so the tokens of the whole report are the concatenation of the tokens of its pieces:
    str(report) = head + "[" + ", ".join(repr(call) for call in apis) + "]" + tail          (head = everything up to and including "'apis': ", tail = the keys after "apis")
    tokens(report) = tokens(head + "[") + tokens(call_1) + ... + tokens(call_n) + tokens("]" + tail)
The store keeps those pieces for every report in OUR row numbering (x_train rows / x_test rows): `seg_tok` (all piece tokens, uint16), `seg_off` (piece offsets), `rep_seg` (first piece of each report; the
report has n_calls + 2 pieces: head, calls, tail), `seg_name` (API-name id of each call piece, -1 for head and tail), `names` (the API-name vocabulary). Nothing here is an edited report: edits are made
from these pieces in memory by `build_tokens` and never written to disk. `python -m baseline.callstore --check` verifies the concatenation against full re-tokenisation of real edits and against the
existing balanced-padding arrays of REPORT 5.10.

    python -m baseline.callstore --build --out <dir>            # results/callstore/all.npz (original reports only: January rows 0..75,297 then April rows; about 0.3 GB)
    python -m baseline.callstore --check --store <dir>
"""
import argparse
import json
import os
import time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEQ = 512

_G = {}


def _tok():
    if "tok" not in _G:
        from baseline import make_pad
        _G["tok"] = make_pad.make_tokenizer(released=_G.get("released", False))
        _G["reps"] = make_pad.Reps()
    return _G["tok"], _G["reps"]


def split_report(rep):
    """(head text, [call texts], tail text) of the string the tokenizer cleans: str(rep) = head + '[' + calls joined by ', ' + ']' + tail (checked by assertion)."""
    keys = list(rep.keys())
    apis = rep.get("apis") or []
    if "apis" not in keys:
        return str(rep), [], ""
    i = keys.index("apis")
    head = "{" + "".join(f"{k!r}: {rep[k]!r}, " for k in keys[:i]) + "'apis': ["
    tail = "]" + "".join(f", {k!r}: {rep[k]!r}" for k in keys[i + 1:]) + "}"
    calls = [repr(c) for c in apis]
    return head, calls, tail


def piece_tokens(tok, texts):
    """Token ids of each text exactly as JSONTokenizerBPE.encode would produce them for a text of its own (clean, then SentencePiece)."""
    return tok.tokenizer.encode_as_ids([tok.clear_json_event(t) for t in texts])


def build_chunk(job):
    """job = (our row numbers, reps rows). Returns the arrays of the pieces of these reports (names as strings, mapped to ids by the caller)."""
    rows, rep_rows = job
    tok, reps = _tok()
    seg_tok, seg_len, rep_nseg, names = [], [], [], []
    for r in rep_rows:
        rep = reps.get(int(r))
        head, calls, tail = split_report(rep)
        texts = [head] + calls + [tail]
        ids = piece_tokens(tok, texts)
        seg_tok.append(np.concatenate([np.asarray(i, dtype=np.uint16) for i in ids]) if ids else np.zeros(0, np.uint16))
        seg_len.append([len(i) for i in ids])
        rep_nseg.append(len(texts))
        names.append([-1] + [str(c.get("api_name", "")).lower() if isinstance(c, dict) else "" for c in (rep.get("apis") or [])] + [-1])
    return np.concatenate(seg_tok), np.concatenate([np.asarray(l, dtype=np.int32) for l in seg_len]), np.asarray(rep_nseg, dtype=np.int32), names


class CallStore:
    def __init__(self, seg_tok, seg_off, rep_seg, seg_name, names):
        self.seg_tok, self.seg_off, self.rep_seg, self.seg_name, self.names = seg_tok, seg_off, rep_seg, seg_name, list(names)

    @classmethod
    def load(cls, path):
        d = np.load(path, allow_pickle=False)
        return cls(d["seg_tok"], d["seg_off"], d["rep_seg"], d["seg_name"], json.loads(str(d["names"])))

    def save(self, path):
        np.savez_compressed(path, seg_tok=self.seg_tok, seg_off=self.seg_off, rep_seg=self.rep_seg, seg_name=self.seg_name, names=json.dumps(self.names))

    def __len__(self):
        return len(self.rep_seg) - 1

    def n_calls(self, r):
        return int(self.rep_seg[r + 1] - self.rep_seg[r]) - 2

    def seg(self, s):
        return self.seg_tok[self.seg_off[s]:self.seg_off[s + 1]]

    def head(self, r):
        return self.seg(int(self.rep_seg[r]))

    def tail(self, r):
        return self.seg(int(self.rep_seg[r + 1]) - 1)

    def call_seg(self, r, i):
        """global piece index of call i of report r"""
        return int(self.rep_seg[r]) + 1 + i

    def call(self, r, i):
        return self.seg(self.call_seg(r, i))

    def name(self, r, i):
        return int(self.seg_name[self.call_seg(r, i)])

    def report_tokens(self, r):
        return self.seg_tok[self.seg_off[self.rep_seg[r]]:self.seg_off[self.rep_seg[r + 1]]]


def build_tokens(store, r, order, extra=None, cut=SEQ):
    """Tokens of report r with its calls taken in the given order, built in memory by concatenation.
    order: list of items; an int i = the original call i of report r; a tuple (store2, r2, j) = call j of report r2 of ANOTHER (or the same) store; an array = raw call tokens.
    Returns (first `cut` tokens as uint16 [cut] zero-padded, total token count of the whole edited report)."""
    parts = [store.head(r)]
    for o in order:
        if isinstance(o, (int, np.integer)):
            parts.append(store.call(r, int(o)))
        elif isinstance(o, tuple):
            parts.append(o[0].call(o[1], o[2]))
        else:
            parts.append(o)
    parts.append(store.tail(r))
    total = int(sum(len(p) for p in parts))
    out = np.zeros(cut, dtype=np.uint16)
    pos = 0
    for p in parts:
        if pos >= cut:
            break
        m = min(len(p), cut - pos)
        out[pos:pos + m] = p[:m]
        pos += m
    return out, total


def build_fast(store, r, added, gaps=None, cut=SEQ):
    """Same result as build_tokens for the two edits of the attacks, without touching every call of a long report: `added` = list of call token arrays (the k added calls in draw order);
    gaps = None (prepend: all added calls in front of the first call) or the sorted gap positions (insert: added call j goes before original call gaps[j]; gap n = after the last call).
    Returns (first `cut` tokens, uint16 [cut]; total token count of the whole edited report). O(k + cut) per report."""
    s0, n = int(store.rep_seg[r]), store.n_calls(r)
    off = store.seg_off
    out = np.zeros(cut, dtype=np.uint16)
    pos = 0

    def emit(a, b=None):                       # emit the array a (or the stored tokens [a:b]) as far as the cut allows
        nonlocal pos
        if pos >= cut:
            return
        arr = a if b is None else store.seg_tok[a:min(b, a + cut - pos)]
        m = min(len(arr), cut - pos)
        out[pos:pos + m] = arr[:m]
        pos += m

    def calls(i, j):                           # original calls i..j-1 are contiguous in the store
        emit(int(off[s0 + 1 + i]), int(off[s0 + 1 + j]))

    emit(store.head(r))
    if gaps is None:
        for a in added:
            emit(a)
        calls(0, n)
    else:
        prev = 0
        for a, g in zip(added, gaps):
            g = int(g)
            calls(prev, g)
            emit(a)
            prev = g
        calls(prev, n)
    emit(store.tail(r))
    return out, int(len(store.report_tokens(r)) + sum(len(a) for a in added))


def build_store(reps_rows, workers=4, chunk=500):
    """Store of the pieces of the reports with the given reps rows (in this order)."""
    jobs = [(np.arange(i, min(i + chunk, len(reps_rows))), reps_rows[i:i + chunk]) for i in range(0, len(reps_rows), chunk)]
    with get_context("fork").Pool(workers) as pool:
        res = list(pool.imap(build_chunk, jobs))
    vocab, seg_name = {}, []
    for _, _, _, names in res:
        for nm in names:
            seg_name.append([-1 if x == -1 else vocab.setdefault(x, len(vocab)) for x in nm])
    seg_name = np.concatenate([np.asarray(s, dtype=np.int32) for s in seg_name])
    seg_tok = np.concatenate([r[0] for r in res])
    seg_len = np.concatenate([r[1] for r in res])
    rep_nseg = np.concatenate([r[2] for r in res])
    return CallStore(seg_tok, np.concatenate([[0], np.cumsum(seg_len)]).astype(np.int64), np.concatenate([[0], np.cumsum(rep_nseg)]).astype(np.int64), seg_name, list(vocab))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "callstore"))
    ap.add_argument("--store", default=os.path.join(ROOT, "results", "callstore"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--released", action="store_true", help="tokenizer of the released checkpoint (store all_released.npz) instead of our BPE-50k")
    a = ap.parse_args()
    _G["released"] = a.released
    if a.build:
        from baseline import make_pad
        tr, te = make_pad.load_row_map()
        os.makedirs(a.out, exist_ok=True)
        t0 = time.time()
        rows = np.concatenate([tr, te])                         # one store, one API-name vocabulary: January row r is store row r, April row t is store row 75,298 + t
        rows = rows[:a.limit] if a.limit else rows
        s = build_store(rows, a.workers)
        s.save(os.path.join(a.out, "all_released.npz" if a.released else "all.npz"))
        print(f"{len(s):,} reports ({len(tr):,} January + {len(te):,} April), {len(s.seg_name):,} pieces, {len(s.seg_tok):,} tokens, {len(s.names):,} API names, {time.time() - t0:.0f}s", flush=True)
    if a.check:
        from baseline import callstore_check
        (callstore_check.run_released if a.released else callstore_check.run)(a.store)


if __name__ == "__main__":
    main()
