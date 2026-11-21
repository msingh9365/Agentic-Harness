"""Writes results/groupsplit/README.md (plain English) and fig_family_composition.png from the JSON files of Stage A (NOTES 21).   (OURS)

    python -m baseline.gs_report --dir results/groupsplit
"""
import argparse
import json
import os

import numpy as np


def pct(x, d=1):
    return f"{100 * x:.{d}f}%"


def md(rows, header):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def figure(R, S, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fams = list(R["family_counts"])
    cols = {"train": "#1baf7a", "val": "#eb6834", "old_val": "#bbbbbb", "april": "#6250d6"}
    lab = {"train": "new training part", "val": "new validation slice", "old_val": "old validation slice", "april": "April test"}
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.2), dpi=200, gridspec_kw={"width_ratios": [1.5, 1]})
    w = 0.2
    for k, key in enumerate(("train", "val", "old_val", "april")):
        tot = sum(R["family_counts"][f][key] for f in fams)
        ax[0].bar(np.arange(len(fams)) + (k - 1.5) * w, [100 * R["family_counts"][f][key] / tot for f in fams], width=w, color=cols[key], label=f"{lab[key]} ({tot:,})")
    ax[0].set_xticks(np.arange(len(fams)))
    ax[0].set_xticklabels([f.replace("windows_", "w_") for f in fams], rotation=30, ha="right", fontsize=8)
    ax[0].set_ylabel("share of the reports (%)")
    ax[0].set_title("Family mix")
    ax[0].legend(fontsize=7.5, frameon=False)
    sizes = [g["size"] for g in R["largest_groups"]]
    sides = [g["side"] for g in R["largest_groups"]]
    ax[1].barh(range(len(sizes))[::-1], sizes, color=[cols["val"] if s == "val" else cols["train"] for s in sides])
    ax[1].set_yticks(range(len(sizes))[::-1])
    ax[1].set_yticklabels([f"#{i + 1}  " + ", ".join(f"{f} {c:,}" for f, c in sorted(g["family_mix"].items(), key=lambda t: -t[1])[:2]) for i, g in enumerate(R["largest_groups"])], fontsize=7)
    ax[1].set_xlabel("reports in the group")
    ax[1].set_title("The 10 largest groups (orange = in validation)")
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/groupsplit")
    a = ap.parse_args()
    R = json.load(open(os.path.join(a.dir, "checks.json")))
    S = json.load(open(os.path.join(a.dir, "split_summary.json")))
    H = json.load(open(os.path.join(a.dir, "split_hash.json")))
    T = json.load(open(os.path.join(a.dir, "tokenizer_compare.json"))) if os.path.exists(os.path.join(a.dir, "tokenizer_compare.json")) else None
    K = json.load(open(os.path.join(a.dir, "checks_gs_tokens.json"))) if os.path.exists(os.path.join(a.dir, "checks_gs_tokens.json")) else None
    figure(R, S, os.path.join(a.dir, "fig_family_composition.png"))
    fc = R["family_counts"]
    nd, nda, ndo = R["near_dup_val_vs_train"], R["near_dup_april_vs_new_train"], R["near_dup_oldval_vs_oldtrain"]
    L = ["# Group-split validation slice (NOTES 21, Stage A, fold chosen by NOTES 21.3)", "",
         "**In one sentence.** The old validation slice was a random 10% of January, so almost every validation report had an exact twin in the training part; the new slice is built from whole *groups* of reports that share an API sequence, so no group is on both sides. This is the result of Stage A (nothing is trained yet).", "",
         "## How it was built", "",
         "* **Group** = reports with the same `hash_apis` (the hash of the API-name sequence), joined with reports that have the same first 512 tokens, and with reports that have the same filtered call-name sequence (the last relation was added after the first run, see NOTES 21.1, because 0.9% of the validation reports of the first version still had an identical filtered call-name sequence in training; no model result was involved).",
         f"* **Split** = fold {H['fold']} of `StratifiedGroupKFold(10, shuffle, random_state 2026)` on the 9 family labels with these groups; the fold was chosen by the rule of NOTES 21.3 (below), after fold 0 was rejected. January has {S['n_groups_hash_apis']:,} `hash_apis` groups, {S['n_groups_strict']:,} groups after the stricter grouping; {R['groups_train']:,} are in training and {R['groups_val']} in validation.",
         f"* **Sizes:** training {H['n_train']:,} reports, validation {H['n_val']:,} ({pct(S['share_val'], 2)}). Split hash `{H['sha256']}` (asserted in every later run by `baseline/groupsplit.py`; indices in `split.npz`).", "",
         "## Checks", "",
         md([["Groups shared by training and validation (must be 0)", R["groups_shared_train_val"]],
             ["Validation reports whose `hash_apis` occurs in training (must be 0)", pct(R["val_share_hash_in_train"])],
             ["First-512-token sequences (old tokenizer) on both sides", R["first512_shared_train_val"]],
             ["First-512-token sequences (NEW tokenizer) on both sides", (T["new_first512_sequences_shared_train_val"] if T else "pending")],
             ["*for comparison:* old validation slice, reports whose `hash_apis` occurs in the old training part", pct(R["old_val_share_hash_in_old_train"])],
             ["*for comparison:* April reports whose `hash_apis` occurs in the new training part", pct(R["april_share_hash_in_new_train"])]], ["check", "result"]), "",
         "**Near-duplicates** (share of reports that have a training report within a normalised edit distance of the API-name sequence; distance = Levenshtein / longer length; exact computation between distinct sequences):", "",
         md([[t, pct(ndo[t]), pct(nd[t]), pct(nda[t])] for t in ("0", "0.01", "0.05", "0.1")], ["distance <=", "old validation vs old training", "**new validation vs new training**", "April vs new training"]), "",
         f"Reading: exact twins are gone (0%), but **{pct(nd['0.05'], 0)} of the new validation reports still have a training report within 5% edit distance, about the same as April ({pct(nda['0.05'], 0)})**; at 1% distance the new slice is much farther from training ({pct(nd['0.01'], 0)}) than April ({pct(nda['0.01'], 0)}). So the new slice is a strictly harder test than the old one and, in the 5% sense, about as close to training as April; April itself still has {pct(R['april_share_hash_in_new_train'], 0)} exact twins.", "",
         "## Counts per family", "",
         md([[f, f"{fc[f]['train']:,}", f"{fc[f]['val']:,}", pct(fc[f]['val'] / (fc[f]['train'] + fc[f]['val'])), f"{fc[f]['old_val']:,}", f"{fc[f]['april']:,}"] for f in fc], ["family", "training", "validation", "share in validation", "old validation", "April"]), "",
         "![family mix and largest groups](fig_family_composition.png)", "",
         "**Largest groups:** " + "; ".join(f"{g['size']:,} ({', '.join(f'{f} {c:,}' for f, c in sorted(g['family_mix'].items(), key=lambda t: -t[1])[:2])}, {g['side']})" for g in R["largest_groups"][:6]) + f". The largest group is {pct(R['largest_group_share_of_train'])} of the training part.", "",
         "## Which fold, and why (NOTES 21.3)", "",
         "Fold 0 was the first choice (fixed in NOTES 21 before anything was computed). It met the acceptance rules but was rejected: its largest group was 52% of the validation slice (58 groups), benign was 19% of it (January: 32.8%), and three families had fewer than 300 reports (ransomware 273, keylogger 192, rat 166). The owner then fixed a rule before it was applied, using data statistics only (no model, no April): a fold is a **candidate** if every family (clean, backdoor, coinminer, dropper, keylogger, ransomware, rat, trojan; windows_syswow64 is exempt, it has only 235 reports in January) has at least 300 validation reports AND its benign share (clean + windows_syswow64) is within 5 points of January's (32.8%, so 27.8% to 37.8%); among candidates take the smallest largest-group share, then more groups, then the lower fold number.", "",
         md([[("**" + str(f["fold"]) + "**" if f["fold"] == H["fold"] else f["fold"]), f["n"], pct(f["share"]), pct(S["fold_rule"]["per_fold"][str(f["fold"])]["benign_share"]), f["groups"], pct(f["largest_group_share"], 0), min(f["families"][x] for x in ("backdoor", "clean", "coinminer", "dropper", "keylogger", "ransomware", "rat", "trojan")),
              "yes" if S["fold_rule"]["per_fold"][str(f["fold"])]["families_ge_300"] else "no", "yes" if S["fold_rule"]["per_fold"][str(f["fold"])]["benign_within_5pt"] else "no", "**candidate**" if f["fold"] in S["fold_rule"]["candidates"] else ""] for f in S["folds_all_ten"]],
            ["fold", "reports", "share", "benign share", "groups", "largest group share", "smallest family", "all families >= 300", "benign within 5 pt", ""]), "",
         f"Candidates: folds {', '.join(str(x) for x in S['fold_rule']['candidates'])}. **Chosen: fold {H['fold']}** (smallest largest-group share). The window uses January's computed benign share 32.8%; with the rounded 34% the candidates would be the same.", "",
         f"**The chosen slice:** {H['n_val']:,} reports ({pct(S['share_val'], 1)}), {R['groups_val']:,} groups, largest group {pct(S['folds_all_ten'][H['fold']]['largest_group_share'], 1)} of the slice (a group of {max(g['size'] for g in R['largest_groups'] if g['side'] == 'val'):,}: " + ", ".join(f"{f} {c:,}" for f, c in sorted(next(g for g in R['largest_groups'] if g['side'] == 'val')['family_mix'].items(), key=lambda t: -t[1])[:2]) + f"), benign {pct(S['folds_all_ten'][H['fold']]['benign'] / H['n_val'], 1)}. Near-duplicates within 1% edit distance: {pct(nd['0.01'])} (April {pct(nda['0.01'])}); within 5%: {pct(nd['0.05'])} (April {pct(nda['0.05'])}). Caveat: rat has {fc["rat"]["val"]} validation reports, and all of them ({next(g for g in R['largest_groups'] if g['side'] == 'val')['family_mix'].get('rat', 0)}) come from that one group; the training part has {fc['rat']['train']:,} rat reports (January has {fc['rat']['train'] + fc['rat']['val']:,} in all).", "",
         "## New tokenizer", ""]
    if T and K:
        ti = K["tokenizer_info"]
        L += [f"BPE-50k refit on the {ti['tokenizer_fit_reports']:,} training reports only (no validation, no April), same settings as before (authors' `JSONTokenizerBPE`, vocabulary 50,000, authors' cleaning and stop words, pinned commit). All 92,700 reports re-tokenised; call-token store rebuilt with the new tokenizer. The old tokenizer files were not touched.", "",
              md([["pieces in the old / new vocabulary", f"{T['vocab_old']:,} / {T['vocab_new']:,}"],
                  ["pieces in both", f"{T['pieces_in_both']:,}"], ["pieces only in the old vocabulary", f"{T['pieces_only_old']:,}"], ["pieces only in the new vocabulary", f"{T['pieces_only_new']:,}"],
                  ["pieces in both with the same id", f"{T['pieces_same_id_in_both']:,}"],
                  ["reports whose first 512 tokens are identical (as pieces) in both tokenisations", pct(T["reports_identical_first512"])],
                  ["token positions (first 512) with the same piece", pct(T["token_positions_same_piece"])],
                  ["median tokens per report, old / new", f"{T['total_tokens_median_old']:.0f} / {T['total_tokens_median_new']:.0f}"],
                  ["total number of tokens, change", f"{T['total_tokens_mean_change_percent']:+.2f}%"]], ["", ""]), "",
              f"Kernel checks (all passed): labels and the number of calls of every report equal the old ones; the first 512 tokens of the new store equal the rows of the new `x_train` / `x_test` for all reports (differing: {K['first512_store_vs_x_rows_differing']}); full re-tokenisation equals the concatenation of the pieces for 3,000 random reports (differing: {K['full_tokenisation_vs_pieces_differing_of_3000']}); kernel time {K['minutes_total']} min."]
    else:
        L += ["pending (CPU kernel `nebula-gs-tokens` is running)."]
    L += ["", "## Files", "", "`split.npz`, `split_hash.json`, `split_summary.json` (all ten folds), `checks.json`, `tokenizer_compare.json`, `checks_gs_tokens.json`, `fig_family_composition.png`; code `baseline/groupsplit.py`, `gs_tokens.py`, `gs_compare.py`, `gs_report.py`; plan and amendment in NOTES.md section 21."]
    open(os.path.join(a.dir, "README.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
