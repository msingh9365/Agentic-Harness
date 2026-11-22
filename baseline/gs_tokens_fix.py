"""
Job (CPU kernel): the corrected tokenizer `bpe50k_fix` and everything built on it (NOTES 25, part 1).   (OURS; the authors' functions do the filtering, the cleaning, the BPE training and the encoding)

    python -m baseline.gs_tokens_fix --out /kaggle/working/out [--limit N --smoke-vocab V]

1. the authors' filtering of all 92,700 reports (as baseline/preprocess.py; January rows = x_train rows, then April),
2. the rows are the old rows: published labels identical, API-name ids of every call piece and number of calls identical to the OLD call-token store (dataset of the old tokenizer; `ranking_gs.json` stays valid),
3. SentencePiece BPE-50k fit on ALL 75,298 January reports (no April) with the options of `bpe50k` plus `--character_coverage=1.0 --byte_fallback=true --pad_id=0 --unk_id=1 --bos_id=-1 --eos_id=-1`
   (variant `bpe50k_fix`; the authors' `train()` is unchanged, the extra flags are appended to its SentencePiece call),
4. re-tokenisation of all reports (x_train, x_test with 512 tokens) and the call-token store with the new tokenizer (`all.npz`, original reports only),
5. checks (assert = STOP): unknown tokens (id 1) = 0 in January and April (store and x rows); no real token has id 0 (store: none; x rows: id 0 only as right padding); unk_id 1, pad_id 0;
   the first 512 tokens of every report in the store = the row of x_train / x_test; the concatenation of the pieces = the full tokenisation for 3,000 reports; edits (prepend / insert of k = 5, 20, 50 calls) built in
   memory by `callstore.build_fast` = the full tokenisation of the edited report, for 600 January and 600 April reports (edited reports in memory only),
6. the length confounder: tokens per report and calls completely inside the first 512 tokens, old tokenizer against new, per population and class (`length_change.json|md`).
Output: all.npz, labels.npz (copy of the old one, asserted equal), variants/bpe50k_fix/, checks_gs_tokens_fix.json, length_change.*.
"""
import argparse
import json
import os
import pickle
import shutil
import time

import numpy as np

from baseline import common as C
from baseline import callstore as CS
from baseline import preprocess as P


class ListReps:
    def __init__(self, events):
        self.events = events

    def get(self, i):
        return self.events[i]


def n_calls_all(store):
    return np.diff(store.rep_seg) - 2


def lengths(store):
    return np.diff(store.seg_off[store.rep_seg]).astype(np.int64)


def calls_in_window(store, cut=512):
    """number of calls that lie completely inside the first `cut` tokens, per report"""
    out = np.zeros(len(store), dtype=np.int64)
    off = store.seg_off
    for r in range(len(store)):
        s0, n = int(store.rep_seg[r]), int(store.rep_seg[r + 1] - store.rep_seg[r]) - 2
        if n:
            ends = off[s0 + 2:s0 + n + 2] - off[s0]
            out[r] = int(np.searchsorted(ends, cut, side="right"))
    return out


def summarise(vals, names):
    return {n: {"median": float(np.median(v)), "mean": float(np.mean(v)), "p90": float(np.percentile(v, 90))} for n, v in zip(names, vals)}


def edit_check(tok, store, events, rows, rng, label, log=print):
    """prepend / insert of k calls taken from other reports: build_fast against the full tokenisation of the edited report (in memory only)"""
    donors = np.array([r for r in range(len(store)) if store.n_calls(r) > 0])
    bad = n = 0
    for r in rows:
        r = int(r)
        n_r = store.n_calls(r)
        if n_r == 0:
            continue
        mode, k = ("prepend", "insert")[int(rng.integers(2))], int(rng.choice([5, 20, 50]))
        dr = rng.choice(donors, k)
        dc = [int(rng.integers(store.n_calls(int(d)))) for d in dr]
        added_tok = [store.call(int(d), c) for d, c in zip(dr, dc)]
        added_ev = [events[int(d)]["apis"][c] for d, c in zip(dr, dc)]
        apis = list(events[r].get("apis") or [])
        if mode == "prepend":
            gaps, new = None, added_ev + apis
        else:
            gaps = np.sort(rng.integers(0, n_r + 1, k))
            new, prev = [], 0
            for a, g in zip(added_ev, gaps):
                new += apis[prev:int(g)]
                new.append(a)
                prev = int(g)
            new += apis[prev:]
        r2 = dict(events[r])
        r2["apis"] = new
        full = np.asarray(tok.encode([r2], pad=False)[0], dtype=np.int64)
        mine, total = CS.build_fast(store, r, added_tok, gaps, cut=512)
        want = np.zeros(512, dtype=np.int64)
        m = min(512, len(full))
        want[:m] = full[:m]
        n += 1
        bad += int(not (np.array_equal(mine.astype(np.int64), want) and total == len(full)))
    log(f"edit check ({label}): {bad} of {n} edited reports differ from the full tokenisation", flush=True)
    return int(bad), int(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int, default=None, help="files per folder (smoke test only)")
    ap.add_argument("--smoke-vocab", type=int, default=0, help="smoke test only: vocabulary size of the tiny fit")
    ap.add_argument("--work", default="/tmp/nebula_events")
    a = ap.parse_args()
    t0 = time.time()
    info = C.setup_nebula(None, require_patched=False)
    data = C.find_data_root()
    old_dir = C.find_dir_with("all.npz")
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    ev = {}
    for split in ("train", "test"):
        cache = os.path.join(a.work, f"{split}_{a.limit}.pkl")
        if os.path.exists(cache):
            ev[split] = pickle.load(open(cache, "rb"))
            continue
        t = time.time()
        ev[split] = P.filter_split(os.path.join(data, f"windows_emulation_{split}set"), info["nebula_root"], a.workers, a.limit)
        pickle.dump(ev[split], open(cache, "wb"), protocol=4)
        print(f"[{split}] {len(ev[split][0])} reports filtered in {(time.time() - t) / 60:.1f} min", flush=True)
    (ev_tr, ym_tr, _), (ev_te, ym_te, _) = ev["train"], ev["test"]
    ntr, nte = len(ev_tr), len(ev_te)
    chk = {"limit": a.limit}
    old_lab = np.load(os.path.join(old_dir, "labels.npz"))
    if a.limit is None:
        assert np.array_equal(old_lab["ym_train"], ym_tr) and np.array_equal(old_lab["ym_test"], ym_te), "labels differ from the published ones"
        assert (ntr, nte) == (75298, 17402)
        chk["labels_equal_old"] = True
        shutil.copy(os.path.join(old_dir, "labels.npz"), os.path.join(a.out, "labels.npz"))
        y_tr, y_te = old_lab["y_train"].astype(int), old_lab["y_test"].astype(int)
    else:
        y_tr, y_te = (np.asarray(ym_tr) != 0).astype(int), (np.asarray(ym_te) != 0).astype(int)
        np.savez_compressed(os.path.join(a.out, "labels.npz"), ym_train=ym_tr, ym_test=ym_te, y_train=y_tr, y_test=y_te)
    if a.smoke_vocab:
        P.VARIANTS["bpe50k_fix"]["vocab"] = a.smoke_vocab
    spec = P.VARIANTS["bpe50k_fix"]
    P.run_variant("bpe50k_fix", ev_tr, ev_te, a.out, info["nebula_root"])                  # fit on ALL January reports (tok_fit_idx None), encode January and April
    vdir = os.path.join(a.out, "variants", "bpe50k_fix")
    inf = json.load(open(os.path.join(vdir, "info.json")))
    chk["tokenizer_info"] = inf
    if a.limit is None:
        assert inf["tokenizer_fit_reports"] == 75298 and inf["vocab_entries"] == 50001, inf
    import sentencepiece as spm
    sp = spm.SentencePieceProcessor(model_file=os.path.join(vdir, "tokenizer.model"))
    assert (sp.unk_id(), sp.pad_id(), sp.bos_id(), sp.eos_id()) == (1, 0, -1, -1) and sp.id_to_piece(0) == "<pad>" and sp.id_to_piece(1) == "<unk>", "special ids"
    chk["special_ids"] = {"unk": sp.unk_id(), "pad": sp.pad_id(), "bos": sp.bos_id(), "eos": sp.eos_id(), "pieces": sp.get_piece_size()}
    vocab = json.load(open(os.path.join(vdir, "vocab.json")))
    chk["vocab_entries"] = len(vocab)
    # call-token store with the NEW tokenizer: January rows then April rows
    tok = P.build_tokenizer(spec, info["nebula_root"], model_path=os.path.join(vdir, "tokenizer.model"), vocab_file=os.path.join(vdir, "vocab.json"))
    events = ev_tr + ev_te
    CS._G["tok"], CS._G["reps"] = tok, ListReps(events)
    t = time.time()
    store = CS.build_store(np.arange(len(events)), workers=a.workers)
    store.save(os.path.join(a.out, "all.npz"))
    print(f"store: {len(store):,} reports, {len(store.seg_tok):,} tokens, {len(store.names):,} API names, {(time.time() - t) / 60:.1f} min", flush=True)
    # (a) the rows are the old rows (full run only)
    old = CS.CallStore.load(os.path.join(old_dir, "all.npz"))
    if a.limit is None:
        assert len(old) == len(store) == ntr + nte
        assert np.array_equal(old.rep_seg.shape, store.rep_seg.shape) and np.array_equal(n_calls_all(old), n_calls_all(store)), "numbers of calls differ from the old store"
        assert np.array_equal(old.seg_name, store.seg_name) and str(old.names) == str(store.names), "API-name ids differ from the old store"
        chk["rows_equal_old_store"] = {"n_calls": True, "api_name_ids_and_vocabulary": True}
        print("(a) rows are the old rows: labels, numbers of calls, API-name ids and API-name vocabulary identical", flush=True)
    # (b) unknown tokens, (c) id 0
    split_tok = int(store.seg_off[store.rep_seg[ntr]])
    cnt = {"january_store_unk1": int((store.seg_tok[:split_tok] == 1).sum()), "april_store_unk1": int((store.seg_tok[split_tok:] == 1).sum()),
           "store_id0": int((store.seg_tok == 0).sum())}
    xtr, xte = np.load(os.path.join(vdir, "x_train.npy")), np.load(os.path.join(vdir, "x_test.npy"))
    cnt["x_train_unk1"], cnt["x_test_unk1"] = int((xtr == 1).sum()), int((xte == 1).sum())
    for nm, x in (("x_train", xtr), ("x_test", xte)):
        nz = x != 0
        last = x.shape[1] - np.argmax(nz[:, ::-1], axis=1)
        last = np.where(nz.any(1), last, 0)
        cnt[f"{nm}_id0_not_right_padding_rows"] = int((nz.sum(1) != last).sum())
    chk["unknown_and_id0"] = cnt
    print("(b)(c) unknown tokens and id 0:", cnt, flush=True)
    assert cnt["january_store_unk1"] == cnt["april_store_unk1"] == cnt["x_train_unk1"] == cnt["x_test_unk1"] == 0, "unknown tokens exist"
    assert cnt["store_id0"] == 0 and cnt["x_train_id0_not_right_padding_rows"] == 0 and cnt["x_test_id0_not_right_padding_rows"] == 0, "a real token has id 0"
    # (d) store against the x rows, concatenation against the full tokenisation
    X = np.concatenate([xtr, xte])
    bad = 0
    for r in range(len(store)):
        tk = store.report_tokens(r)[:512]
        row = X[r]
        if not np.array_equal(row[:len(tk)].astype(np.int64), tk.astype(np.int64)) or (len(tk) < 512 and row[len(tk):].any()):
            bad += 1
    chk["first512_store_vs_x_rows_differing"] = int(bad)
    print("(d) first 512 tokens of the store vs the rows of x_train/x_test: differing reports =", bad, flush=True)
    rng = np.random.default_rng(0)
    pick = rng.choice(len(store), size=min(3000, len(store)), replace=False)
    enc = tok.encode([events[int(r)] for r in pick], pad=False)
    full_bad = sum(int(not np.array_equal(np.asarray(e, dtype=np.int64), store.report_tokens(int(r)).astype(np.int64))) for e, r in zip(enc, pick))
    chk["full_tokenisation_vs_pieces_differing_of_3000"] = int(full_bad)
    print("(d) full re-tokenisation vs concatenation of the pieces, 3000 reports: differing =", full_bad, flush=True)
    assert bad == 0 and full_bad == 0
    # (e) edits against the full tokenisation
    rng = np.random.default_rng(1)
    jan = rng.choice(ntr, min(600, ntr), replace=False)
    apr = ntr + rng.choice(nte, min(600, nte), replace=False)
    b1, n1 = edit_check(tok, store, events, jan, rng, "January")
    b2, n2 = edit_check(tok, store, events, apr, rng, "April")
    chk["edit_check"] = {"january": [b1, n1], "april": [b2, n2]}
    assert b1 == 0 and b2 == 0 and n1 > 0 and n2 > 0, "edits differ from the full tokenisation"
    # 6. length confounder
    old_len = old if a.limit is None else store                                              # smoke test: the old store has other rows, compare the store with itself (exercises the code only)
    L_new, L_old = lengths(store), lengths(old_len)
    W_new, W_old = calls_in_window(store), calls_in_window(old_len)
    ncalls = n_calls_all(store)
    res = {}
    for pop, sl, y in (("January", slice(0, ntr), y_tr), ("April", slice(ntr, ntr + nte), y_te)):
        for cname, mask in (("all", np.ones(len(y), bool)), ("malware", y == 1), ("benign", y == 0)):
            idx = np.arange(len(store))[sl][mask] if a.limit is None else np.arange(len(store))[sl][mask]
            res[f"{pop}|{cname}"] = {"reports": int(len(idx)),
                                    "tokens_old": summarise([L_old[idx]], ["tokens"])["tokens"], "tokens_new": summarise([L_new[idx]], ["tokens"])["tokens"],
                                    "share_longer_than_512_old": float((L_old[idx] > 512).mean()), "share_longer_than_512_new": float((L_new[idx] > 512).mean()),
                                    "calls_in_512_old": summarise([W_old[idx]], ["c"])["c"], "calls_in_512_new": summarise([W_new[idx]], ["c"])["c"],
                                    "share_fewer_than_3_calls_in_512_old": float(((W_old[idx] < 3) & (ncalls[idx] >= 3)).mean()), "share_fewer_than_3_calls_in_512_new": float(((W_new[idx] < 3) & (ncalls[idx] >= 3)).mean()),
                                    "median_ratio_new_over_old_tokens": float(np.median(L_new[idx] / np.maximum(L_old[idx], 1)))}
    json.dump(res, open(os.path.join(a.out, "length_change.json"), "w"), indent=1)
    md = ["### Length change, old tokenizer -> bpe50k_fix (median [mean]; calls inside = calls completely inside the first 512 tokens)", "",
          "| population | class | reports | tokens/report old | tokens/report new | median ratio new/old | share > 512 old / new (%) | calls inside 512 old | calls inside 512 new | share with < 3 calls inside (of reports with >= 3 calls) old / new (%) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in res.items():
        p_, c_ = k.split("|")
        f = lambda d: f"{d['median']:g} [{d['mean']:.1f}]"
        md.append(f"| {p_} | {c_} | {v['reports']} | {f(v['tokens_old'])} | {f(v['tokens_new'])} | {v['median_ratio_new_over_old_tokens']:.3f} | {100 * v['share_longer_than_512_old']:.1f} / {100 * v['share_longer_than_512_new']:.1f} | "
                  f"{f(v['calls_in_512_old'])} | {f(v['calls_in_512_new'])} | {100 * v['share_fewer_than_3_calls_in_512_old']:.1f} / {100 * v['share_fewer_than_3_calls_in_512_new']:.1f} |")
    open(os.path.join(a.out, "length_change.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md), flush=True)
    chk["minutes_total"] = round((time.time() - t0) / 60, 1)
    json.dump(chk, open(os.path.join(a.out, "checks_gs_tokens_fix.json"), "w"), indent=1)
    print(f"all done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
