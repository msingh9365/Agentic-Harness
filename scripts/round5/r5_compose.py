"""
Token composition for the optimised-padding tests (round 5, 3c and 3d): the token sequence of a report with extra calls in front is built by
concatenating the token ids of the pieces (header, calls, tail) instead of re-tokenising the whole report for every candidate call.

Nebula's tokenisation of a report string equals the concatenation of the ids of its pieces (header, each call with its ", " separator,
closing text) when the cuts cannot join tokens (measure_links.report_pieces; "fallback" otherwise). For the reports used here this is checked
against the full tokenisation (check()), and reports for which it does not hold are marked `exact = False`: they are tokenised in full.
"""
import numpy as np

from measure_links import report_pieces


class Composer:
    def __init__(self, nb):
        self.nb = nb
        self.memo = {}

    def ids(self, text):
        v = self.memo.get(text)
        if v is None:
            v = np.asarray(self.nb.ids(text), dtype=np.int32)
            if len(self.memo) < 2_000_000:
                self.memo[text] = v
        return v

    def parts(self, rep):
        """dict: head ids, tail ids, ids of every original call WITH the ", " separator, ids of call 0 without it, and the exactness flag."""
        s, pieces = report_pieces(rep)
        apis = list(rep.get("apis") or [])
        head, tail = self.ids(pieces[0]), self.ids(pieces[-1])
        calls = [self.ids(p) for p in pieces[1:-1]]                     # call 0 without the separator, the others with
        full = np.asarray(self.nb.ids(rep), dtype=np.int32)
        cat = np.concatenate([head] + calls + [tail]) if calls else np.concatenate([head, tail])
        exact = bool(len(cat) == len(full) and (cat == full).all())
        first_prefixed = self.ids(", " + str(apis[0])) if apis else None
        return {"head": head, "tail": tail, "calls": calls, "first_prefixed": first_prefixed, "exact": exact, "full": full, "rep": rep}

    def call_ids(self, c, first):
        return self.ids(str(c) if first else ", " + str(c))

    def compose(self, p, added):
        """token ids of the report p with the calls `added` (list of call dicts, in order, the first one is the new first call) put in front."""
        if not p["exact"]:
            rep = dict(p["rep"]); rep["apis"] = list(added) + list(rep.get("apis") or [])
            return np.asarray(self.nb.ids(rep), dtype=np.int32)
        pieces = [p["head"]]
        for j, c in enumerate(added):
            pieces.append(self.call_ids(c, j == 0))
        if p["calls"]:
            pieces.append(p["first_prefixed"] if added else p["calls"][0])
            pieces.extend(p["calls"][1:])
        pieces.append(p["tail"])
        return np.concatenate(pieces)
