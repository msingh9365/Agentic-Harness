"""
Job (CPU kernel): P3 of NOTES 24 / 27 - address-role normalisation, tokenizer and call-token store.   (OURS; the authors' functions do the filtering, the cleaning, the BPE training and the encoding)

    python -m baseline.gs_tokens_p3 --out /kaggle/working/out [--limit N --smoke-vocab V]

1. the authors' filtering of all 92,700 reports (as baseline/gs_tokens_fix.py), the rows are the old rows (published labels, calls per report, API-name ids of every call piece and the API-name vocabulary identical to the OLD store);
2. variant `bpe50k_role` (hex literals of more than 4 digits -> addr<L>x<T>; unknown pieces -> id 50,000; BPE-50k with the settings of the old bpe50k, fit on ALL 75,298 January normalised reports): x_train / x_test (512 tokens) and the call-token store `all.npz` in <out>/role/;
3. CPU checks (assert = STOP): no real token has id 0 (store none; x rows only right padding); the first 512 tokens of every store report = the x row; the concatenation of the pieces = the full tokenisation for 3,000 reports; 1,200 in-memory edits
   (prepend / insert of k = 5, 20, 50 calls) = their full tokenisation; reported: tokens with id 50,000 (unknown), the share of calls with a hex literal of more than 4 digits (random sample of 5,000 reports), the change of the total token count per report
   (median, quartiles; per population and class) and of the calls inside the first 512 tokens, against the OLD store;
4. the length-matched control rule (NOTES 24): if the MEDIAN total token count over all reports changes by more than 10% against the old store, the control variant `bpe50k_addr` (the single word `addr`) is built the same way into <out>/addr/.
Output: <out>/role/{all.npz, labels.npz, variants/bpe50k_role/}, [<out>/addr/ ...], p3_checks.json, p3_length_change.md.
"""
import argparse
import json
import os
import pickle
import re
import shutil
import time

import numpy as np

from baseline import common as C
from baseline import callstore as CS
from baseline import preprocess as P
from baseline.gs_tokens_fix import ListReps, calls_in_window, edit_check, lengths, n_calls_all, summarise


def build(name, out, ev_tr, ev_te, y_tr, y_te, info, old, a, workers):
    ntr, nte = len(ev_tr), len(ev_te)
    chk = {"variant": name}
    os.makedirs(out, exist_ok=True)
    spec = P.VARIANTS[name]
    if a.smoke_vocab:
        spec["vocab"] = a.smoke_vocab
    P.run_variant(name, ev_tr, ev_te, out, info["nebula_root"])                            # fit on ALL January (normalised) reports, encode January and April
    vdir = os.path.join(out, "variants", name)
    inf = json.load(open(os.path.join(vdir, "info.json")))
    chk["tokenizer_info"] = inf
    if a.limit is None:
        assert inf["tokenizer_fit_reports"] == 75298 and inf["vocab_entries"] == 50001, inf
    tok = P.build_tokenizer(spec, info["nebula_root"], model_path=os.path.join(vdir, "tokenizer.model"), vocab_file=os.path.join(vdir, "vocab.json"))
    events = ev_tr + ev_te
    CS._G["tok"], CS._G["reps"] = tok, ListReps(events)
    t = time.time()
    store = CS.build_store(np.arange(len(events)), workers=workers)
    store.save(os.path.join(out, "all.npz"))
    print(f"[{name}] store: {len(store):,} reports, {len(store.seg_tok):,} tokens, {(time.time() - t) / 60:.1f} min", flush=True)
    if a.limit is None:
        assert len(old) == len(store) == ntr + nte
        assert np.array_equal(n_calls_all(old), n_calls_all(store)) and np.array_equal(old.seg_name, store.seg_name) and str(old.names) == str(store.names), "rows differ from the old store"
        chk["rows_equal_old_store"] = True
    split_tok = int(store.seg_off[store.rep_seg[ntr]])
    xtr, xte = np.load(os.path.join(vdir, "x_train.npy")), np.load(os.path.join(vdir, "x_test.npy"))
    cnt = {"store_id0": int((store.seg_tok == 0).sum()), "store_unknown_id50000_jan": int((store.seg_tok[:split_tok] == 50000).sum()), "store_unknown_id50000_apr": int((store.seg_tok[split_tok:] == 50000).sum()), "max_id": int(store.seg_tok.max())}
    for nm, x in (("x_train", xtr), ("x_test", xte)):
        nz = x != 0
        last = x.shape[1] - np.argmax(nz[:, ::-1], axis=1)
        last = np.where(nz.any(1), last, 0)
        cnt[f"{nm}_id0_not_right_padding_rows"] = int((nz.sum(1) != last).sum())
    chk["ids"] = cnt
    print(f"[{name}] ids:", cnt, flush=True)
    assert cnt["store_id0"] == 0 and cnt["x_train_id0_not_right_padding_rows"] == 0 and cnt["x_test_id0_not_right_padding_rows"] == 0 and cnt["max_id"] <= 50000, "a real token has id 0 or an id above 50,000"
    X = np.concatenate([xtr, xte])
    bad = 0
    for r in range(len(store)):
        tk = store.report_tokens(r)[:512]
        row = X[r]
        if not np.array_equal(row[:len(tk)].astype(np.int64), tk.astype(np.int64)) or (len(tk) < 512 and row[len(tk):].any()):
            bad += 1
    rng = np.random.default_rng(0)
    pick = rng.choice(len(store), size=min(3000, len(store)), replace=False)
    enc = tok.encode([events[int(r)] for r in pick], pad=False)
    full_bad = sum(int(not np.array_equal(np.asarray(e, dtype=np.int64), store.report_tokens(int(r)).astype(np.int64))) for e, r in zip(enc, pick))
    chk["first512_store_vs_x_rows_differing"], chk["full_tokenisation_vs_pieces_differing_of_3000"] = int(bad), int(full_bad)
    print(f"[{name}] first512 differing {bad}, full tokenisation differing {full_bad}", flush=True)
    assert bad == 0 and full_bad == 0
    rng = np.random.default_rng(1)
    b1, n1 = edit_check(tok, store, events, rng.choice(ntr, min(600, ntr), replace=False), rng, "January")
    b2, n2 = edit_check(tok, store, events, ntr + rng.choice(nte, min(600, nte), replace=False), rng, "April")
    chk["edit_check"] = {"january": [b1, n1], "april": [b2, n2]}
    assert b1 == 0 and b2 == 0 and n1 > 0 and n2 > 0, "edits differ from the full tokenisation"
    # length and changed calls
    old_len = old if a.limit is None else store
    L_new, L_old = lengths(store), lengths(old_len)
    W_new, W_old = calls_in_window(store), calls_in_window(old_len)
    hexre = re.compile(r"0x[0-9a-f]{5,}")
    sample = np.random.default_rng(2).choice(len(events), size=min(5000, len(events)), replace=False)
    ncall = nchg = 0
    for r in sample:
        for c in (events[int(r)].get("apis") or []):
            ncall += 1
            nchg += int(hexre.search(repr(c).lower()) is not None)
    res = {"share_calls_with_hex_literal_gt4_digits_sample5000reports": nchg / max(ncall, 1), "calls_in_sample": ncall,
           "median_total_tokens_old": float(np.median(L_old)), "median_total_tokens_new": float(np.median(L_new)), "median_total_tokens_change_pct": float(100 * (np.median(L_new) / np.median(L_old) - 1)),
           "mean_total_tokens_old": float(L_old.mean()), "mean_total_tokens_new": float(L_new.mean()), "quartiles_new_over_old_ratio": [float(v) for v in np.percentile(L_new / np.maximum(L_old, 1), [25, 50, 75])],
           "median_calls_in_512_old": float(np.median(W_old)), "median_calls_in_512_new": float(np.median(W_new))}
    md = [f"### {name}: length change against the old store", "", f"share of calls with a hex literal of more than 4 digits (sample of {len(sample)} reports, {ncall:,} calls): {100 * res['share_calls_with_hex_literal_gt4_digits_sample5000reports']:.1f}%", "",
          "| population | class | reports | tokens/report old (median [mean]) | tokens/report new | median ratio new/old | calls inside 512 old | calls inside 512 new |", "|---|---|---|---|---|---|---|---|"]
    for pop, sl, y in (("January", slice(0, ntr), y_tr), ("April", slice(ntr, ntr + nte), y_te)):
        for cname, mask in (("all", np.ones(len(y), bool)), ("malware", y == 1), ("benign", y == 0)):
            idx = np.arange(len(store))[sl][mask]
            md.append(f"| {pop} | {cname} | {len(idx)} | {np.median(L_old[idx]):g} [{L_old[idx].mean():.1f}] | {np.median(L_new[idx]):g} [{L_new[idx].mean():.1f}] | {np.median(L_new[idx] / np.maximum(L_old[idx], 1)):.3f} | {np.median(W_old[idx]):g} | {np.median(W_new[idx]):g} |")
    open(os.path.join(out, "length_change.md"), "w").write("\n".join(md) + "\n")
    chk["length"] = res
    json.dump(chk, open(os.path.join(out, "checks.json"), "w"), indent=1)
    print("\n".join(md), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int, default=None, help="files per folder (smoke test only)")
    ap.add_argument("--smoke-vocab", type=int, default=0)
    ap.add_argument("--force-control", action="store_true", help="smoke test only: build the control variant as well")
    ap.add_argument("--only", choices=["role", "addr"], default=None, help="build only this variant (the control kernel runs in parallel with the role kernel to save wall time; its output is USED only if the 10% rule of NOTES 24 triggers, decided from the role kernel)")
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
    old_lab = np.load(os.path.join(old_dir, "labels.npz"))
    old = CS.CallStore.load(os.path.join(old_dir, "all.npz"))
    if a.limit is None:
        assert np.array_equal(old_lab["ym_train"], ym_tr) and np.array_equal(old_lab["ym_test"], ym_te), "labels differ from the published ones"
        assert (len(ev_tr), len(ev_te)) == (75298, 17402)
        y_tr, y_te = old_lab["y_train"].astype(int), old_lab["y_test"].astype(int)
    else:
        y_tr, y_te = (np.asarray(ym_tr) != 0).astype(int), (np.asarray(ym_te) != 0).astype(int)
    summary = {}
    if a.only != "addr":
        out = os.path.join(a.out, "role")
        os.makedirs(out, exist_ok=True)
        if a.limit is None:
            shutil.copy(os.path.join(old_dir, "labels.npz"), os.path.join(out, "labels.npz"))
        else:
            np.savez_compressed(os.path.join(out, "labels.npz"), ym_train=ym_tr, ym_test=ym_te, y_train=y_tr, y_test=y_te)
        summary["bpe50k_role"] = build("bpe50k_role", out, ev_tr, ev_te, y_tr, y_te, info, old, a, a.workers)
        change = abs(summary["bpe50k_role"]["median_total_tokens_change_pct"])
        summary["control_rule"] = {"median_total_token_change_pct_role": summary["bpe50k_role"]["median_total_tokens_change_pct"], "threshold_pct": 10.0, "control_triggered": bool(change > 10.0)}
        print("control rule:", summary["control_rule"], flush=True)
    control = a.only == "addr" or (a.only is None and (summary["control_rule"]["control_triggered"] or a.force_control))
    if control:
        out = os.path.join(a.out, "addr")
        os.makedirs(out, exist_ok=True)
        if a.limit is None:
            shutil.copy(os.path.join(old_dir, "labels.npz"), os.path.join(out, "labels.npz"))
        else:
            np.savez_compressed(os.path.join(out, "labels.npz"), ym_train=ym_tr, ym_test=ym_te, y_train=y_tr, y_test=y_te)
        summary["bpe50k_addr"] = build("bpe50k_addr", out, ev_tr, ev_te, y_tr, y_te, info, old, a, a.workers)
    json.dump(summary, open(os.path.join(a.out, "p3_summary.json"), "w"), indent=1)
    print(f"all done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
