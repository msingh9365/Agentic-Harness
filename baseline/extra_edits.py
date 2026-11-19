"""
Further edit families for the robustness tests of the audit (rare-API-name padding, block padding, copied calls, rotation of the 512 window, argument injection) and the test-time deduplication defence.   (OURS)

Every edit is a SPEC (which calls are added where, how the list is rotated, which argument strings are appended) made from a fixed random stream; tokens are built IN MEMORY from the call-token store of the
original reports (baseline/callstore.py) and are never written. `spec_report` applies the same spec to the report DICT, so that `baseline/extra_check.py` can compare the builders with the full
re-tokenisation of the edited report.

Edit sets (April row t, store row ntr + t; reports without calls stay unedited), k in {5, 20, 50}:
  rare_{k}_{insert|prepend}   k calls drawn uniformly from the EVAL-pool calls whose API NAME is among the rarest 20% of the EVAL-pool names by frequency in the training part (names never seen in training count 0)
  block_{k}_{insert|prepend}  one block of k consecutive calls of a random EVAL-pool report (fewer if the report is shorter), inserted at one random gap / prepended
  copy_{k}_{insert|prepend}   k copies of calls of the SAME report (positions drawn with replacement), each into its own random gap / all prepended
  rot_{25|50}                 the call list rotated: the calls from position floor(frac * n) on come first, the first floor(frac * n) calls follow
  inj_{k}                     the arguments of the first k calls get the arguments of a random EVAL-pool call appended (a benign-looking string argument); the call count does not change
Random streams: default_rng([8300 + family, row, k, mode]) (family: rare 0, block 1, copy 2, injection donors 4), insert gaps sorted as in baseline/make_pad.py.
Test-time deduplication: consecutive calls with identical tokens are reduced to one (applied after the edit); `build_dedup` builds the first 512 tokens lazily.
"""
import numpy as np

from baseline import callstore as CS

KS = (5, 20, 50)
MODES = ("insert", "prepend")
FAMILIES = ["rare", "block", "copy"]
SET_NAMES = [f"{f}_{k}_{m}" for f in FAMILIES for k in KS for m in MODES] + ["rot_25", "rot_50"] + [f"inj_{k}" for k in KS]
STREAM = {"rare": 8300, "block": 8301, "copy": 8302, "inj": 8304}


class Pools:
    """Everything the planners draw from (built once): EVAL-pool calls, the rare-name calls, whole pool reports, donor argument lists."""
    def __init__(self, store, pool_rows, trn, reps=None, seed=0):
        self.store, self.pool = store, np.asarray(pool_rows)
        self.pool_n = np.array([store.n_calls(int(r)) for r in self.pool])
        cnt = np.zeros(len(store.names), dtype=np.int64)                         # frequency of every API name in the TRAINING part
        for r in trn:
            s0, s1 = int(store.rep_seg[int(r)]) + 1, int(store.rep_seg[int(r) + 1]) - 1
            if s1 > s0:
                np.add.at(cnt, store.seg_name[s0:s1], 1)
        pn = [(int(r), i, store.name(int(r), i)) for r in self.pool for i in range(store.n_calls(int(r)))]
        names = np.array([x[2] for x in pn])
        uniq = np.unique(names)
        f = cnt[uniq]
        cut = np.percentile(f, 20)
        rare_names = set(uniq[f <= cut].tolist())
        self.rare = [(r, i) for r, i, nm in pn if nm in rare_names]
        self.n_rare_names, self.n_names, self.rare_cut = len(rare_names), len(uniq), float(cut)
        self.donors = None
        if reps is not None:                                                     # argument donors: the argument lists of EVAL-pool calls (read once from the original reports)
            rng = np.random.default_rng(seed)
            self.donors = []
            for pr in rng.choice(len(self.pool), min(400, len(self.pool)), replace=False):
                rep = reps(int(self.pool[pr]))
                for c in rep.get("apis") or []:
                    if isinstance(c, dict) and c.get("args"):
                        self.donors.append(list(c["args"]))
            self.donors = self.donors[:20000]


def plan(family, k, mode, t, n, P):
    """Spec of the edit of April row t (n calls) or None."""
    if n == 0:
        return None
    rng = np.random.default_rng([STREAM[family], int(t), int(k), 0 if mode == "insert" else 1])
    if family == "rare":
        added = [("pool",) + P.rare[int(rng.integers(len(P.rare)))] for _ in range(k)]
    elif family == "block":
        pr = int(rng.integers(len(P.pool)))
        nr = int(P.pool_n[pr])
        m = min(k, nr)
        st = int(rng.integers(0, nr - m + 1))
        added = [("pool", int(P.pool[pr]), st + j) for j in range(m)]
    else:                                                                        # copy
        added = [("own", int(rng.integers(n))) for _ in range(k)]
    if mode == "prepend":
        gaps = None
    elif family == "block":
        gaps = np.full(len(added), int(rng.integers(0, n + 1)))
    else:
        gaps = np.sort(rng.integers(0, n + 1, len(added)))
    return {"kind": "pad", "added": added, "gaps": gaps}


def plan_rot(frac, n):
    return None if n == 0 else {"kind": "rot", "shift": int(np.floor(frac * n))}


def plan_inj(k, t, n, P):
    if n == 0 or not P.donors:
        return None
    m = min(k, n)
    rng = np.random.default_rng([STREAM["inj"], int(t)])
    d = rng.integers(len(P.donors), size=max(KS))                               # the donors of call i do not depend on k: k = 5 is the first 5 of k = 50
    return {"kind": "inj", "k": m, "donors": [P.donors[int(j)] for j in d[:m]]}


def all_specs(t, n, P):
    out = []
    for f in FAMILIES:
        for k in KS:
            for m in MODES:
                out.append(plan(f, k, m, t, n, P))
    out += [plan_rot(0.25, n), plan_rot(0.5, n)] + [plan_inj(k, t, n, P) for k in KS]
    return out


# ------------------------------------------------------------------------------------------ token builders (in memory)
def call_array(store, r, a):
    return store.call(int(a[1]), int(a[2])) if a[0] == "pool" else store.call(int(r), int(a[1]))


def build_rotated(store, r, shift, cut=CS.SEQ):
    s0, n = int(store.rep_seg[r]), store.n_calls(r)
    off = store.seg_off
    out = np.zeros(cut, dtype=np.uint16)
    pos = 0
    for arr in (store.head(r), store.seg_tok[int(off[s0 + 1 + shift]):int(off[s0 + 1 + n])], store.seg_tok[int(off[s0 + 1]):int(off[s0 + 1 + shift])], store.tail(r)):
        if pos >= cut:
            break
        m = min(len(arr), cut - pos)
        out[pos:pos + m] = arr[:m]
        pos += m
    return out, int(len(store.report_tokens(r)))


def build_injected(store, r, new_first, cut=CS.SEQ):
    """first calls replaced by the token arrays in new_first (their number = len(new_first)); the rest of the report unchanged."""
    s0, n = int(store.rep_seg[r]), store.n_calls(r)
    off = store.seg_off
    k = len(new_first)
    out = np.zeros(cut, dtype=np.uint16)
    pos = 0
    old_len = int(off[s0 + 1 + k] - off[s0 + 1])
    parts = [store.head(r)] + list(new_first) + [store.seg_tok[int(off[s0 + 1 + k]):int(off[s0 + 1 + n])], store.tail(r)]
    for arr in parts:
        if pos >= cut:
            break
        m = min(len(arr), cut - pos)
        out[pos:pos + m] = arr[:m]
        pos += m
    return out, int(len(store.report_tokens(r)) - old_len + sum(len(a) for a in new_first))


def spec_tokens(store, r, spec, tok=None, reps_call=None):
    """(tokens [512] uint16, total tokens) of store row r edited by spec. Injection needs the tokenizer `tok` and `reps_call(r, i)` (the original call dict of call i of store row r)."""
    if spec is None:
        return CS.build_fast(store, r, [], None)
    if spec["kind"] == "pad":
        return CS.build_fast(store, r, [call_array(store, r, a) for a in spec["added"]], spec["gaps"])
    if spec["kind"] == "rot":
        return build_rotated(store, r, spec["shift"])
    texts = []
    for i, donor in enumerate(spec["donors"]):
        c = dict(reps_call(r, i))
        c["args"] = list(c.get("args") or []) + list(donor)
        texts.append(repr(c))
    ids = CS.piece_tokens(tok, texts)
    return build_injected(store, r, [np.asarray(x, dtype=np.uint16) for x in ids])


# ------------------------------------------------------------------------------------------ the same edits on the report dict (for the check)
def apply_pad(apis, spec, pool_call, own=None):
    added = [pool_call(a[1], a[2]) if a[0] == "pool" else apis[a[1]] for a in spec["added"]]
    if spec["gaps"] is None:
        return added + list(apis)
    out, j, n, gaps = [], 0, len(apis), spec["gaps"]
    for i in range(n + 1):
        while j < len(added) and gaps[j] == i:
            out.append(added[j]); j += 1
        if i < n:
            out.append(apis[i])
    return out


def spec_report(rep, spec, pool_call):
    r2 = dict(rep)
    apis = list(rep.get("apis") or [])
    if spec["kind"] == "pad":
        r2["apis"] = apply_pad(apis, spec, pool_call)
    elif spec["kind"] == "rot":
        s = spec["shift"]
        r2["apis"] = apis[s:] + apis[:s]
    else:
        new = []
        for i, c in enumerate(apis):
            if i < len(spec["donors"]):
                c = dict(c)
                c["args"] = list(c.get("args") or []) + list(spec["donors"][i])
            new.append(c)
        r2["apis"] = new
    return r2


# ------------------------------------------------------------------------------------------ test-time deduplication
class Ident:
    """Identity of a call = the hash of its text (repr of the call dict), so that 'consecutive duplicate calls' means identical calls, not identical tokens. rep_of(store row) -> report dict."""
    def __init__(self, rep_of):
        self.rep_of, self.ids = rep_of, {}

    def ensure(self, row):
        row = int(row)
        if row not in self.ids:
            self.ids[row] = np.array([hash(repr(c)) for c in (self.rep_of(row).get("apis") or [])], dtype=np.int64)
        return self.ids[row]

    def id(self, row, idx):
        return int(self.ensure(row)[int(idx)])

    @classmethod
    def from_npz(cls, path):
        """Identities computed beforehand (baseline/extra_ident.py, hashes of the original call texts of the April reports and of the EVAL-pool reports): no report text needed."""
        d = np.load(path)
        o = cls(None)
        off, ids, rows = d["offsets"], d["ids"], d["rows"]                # each d[...] access reads and decompresses the array: load every array ONCE
        o.ids = {int(r): ids[off[i]:off[i + 1]] for i, r in enumerate(rows)}
        return o


def build_dedup(store, r, spec, ident, tok=None, reps_call=None, cut=CS.SEQ):
    """First `cut` tokens of the edited report after consecutive duplicate calls (identical call text) were reduced to one. Lazy: stops when the window is full. Returns tokens uint16 [cut]."""
    n = store.n_calls(r)
    if spec is None or spec["kind"] == "pad":
        added = [] if spec is None else [(call_array(store, r, a), ident.id(a[1], a[2]) if a[0] == "pool" else ident.id(r, a[1])) for a in spec["added"]]
        gaps = None if spec is None else spec["gaps"]

        def gen():
            if gaps is None:
                yield from added
                for i in range(n):
                    yield store.call(r, i), ident.id(r, i)
            else:
                j = 0
                for i in range(n + 1):
                    while j < len(added) and gaps[j] == i:
                        yield added[j]; j += 1
                    if i < n:
                        yield store.call(r, i), ident.id(r, i)
    elif spec["kind"] == "rot":
        s = spec["shift"]

        def gen():
            for i in list(range(s, n)) + list(range(0, s)):
                yield store.call(r, i), ident.id(r, i)
    else:
        texts = []
        for i, donor in enumerate(spec["donors"]):
            c = dict(reps_call(r, i))
            c["args"] = list(c.get("args") or []) + list(donor)
            texts.append(repr(c))
        new = [(np.asarray(x, dtype=np.uint16), hash(tx)) for x, tx in zip(CS.piece_tokens(tok, texts), texts)]

        def gen():
            yield from new
            for i in range(len(new), n):
                yield store.call(r, i), ident.id(r, i)
    out = np.zeros(cut, dtype=np.uint16)
    pos = 0
    head = store.head(r)
    m = min(len(head), cut); out[:m] = head[:m]; pos = m
    prev = None
    for arr, cid in gen():
        if pos >= cut:
            break
        if cid == prev:
            continue
        prev = cid
        m = min(len(arr), cut - pos); out[pos:pos + m] = arr[:m]; pos += m
    if pos < cut:
        arr = store.tail(r); m = min(len(arr), cut - pos); out[pos:pos + m] = arr[:m]
    return out
