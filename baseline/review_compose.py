"""Compose RESULTS_FOR_REVIEW.md and REPORT section 5.11 from the generated tables of results/review (tables are included verbatim; the prose is written by hand in this file).   (OURS)

    python -m baseline.review_compose
"""
import os
import re

from baseline.audit_text import LIMITS_COMPUTE, STATUS_511, STATUS_RESULTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "results", "review")


def read(name):
    return open(os.path.join(R, name)).read().strip()


def section(md, start, end=None):
    i = md.index(start)
    j = md.index(end, i) if end else len(md)
    return md[i:j].strip()


FIVE = """1. **Shown: balanced padding buys robustness, not clean accuracy.** ATT+bal, PE+bal and both keep models still flag 64 to 77% of the malware when 20 to 50 random benign calls are prepended or inserted, where v2-PE falls to 8 to 22% (prepend) and the released checkpoint to 12 to 16%. On clean April data no model beats v2-PE on pAUC@1e-2 under the claim rule (ATT+bal +0.23 points, CI [-1.70, +2.09], positive in 4 of 10 seeds); as 10-seed ensembles ATT+bal is 3.4 points lower (the CI excludes 0; descriptive).
2. **Shown: attention pooling adds robustness against large amounts of prepended padding, not elsewhere.** ATT+bal beats PE+bal where the padding is chosen against the model or is long (LightGBM-chosen k = 50 prepend: 36.5 against 10.0% flagged at 1% FPR; white-box after 20 calls: 53.3 against 39.6% at 1% FPR and 14.6 against 3.5% at 0.1%); in 18 of 24 surrogate tests the CI excludes 0 with at least 7 of 10 seeds in its favour (14 also under a bootstrap that resamples duplicate reports together; descriptive) and in none against it. For random and LightGBM-chosen inserted calls the two are equal (differences within 0.5 points); against calls chosen with v2-PE, ATT+bal is higher by 1.5 to 7 points. On the 0 to 30% of malware reports whose whole edited text still fits into 512 tokens the picture is mixed (2 tests for ATT+bal, 7 against). The advantage is therefore about what is pushed out of the 512-token window, and it is smaller for the keep models.
3. **Shown: keeping the clean copies did not help.** The keep models are not better on clean data (pAUC@1e-2 -1.17 and -0.87 points against v2-PE; ATT+bal-keep -1.40 against ATT+bal: the per-seed rule is not met, the 10-seed ensembles differ by -1.28 points, the CI excludes 0; descriptive) and are less robust than the replace versions under the strongest attacks (LightGBM-chosen k = 50 prepend 27.1 against 36.5%; white-box after 20 calls at 0.1% FPR: 7.5 against 14.6%).
4. **Shown: padding malware only teaches the shortcut "padding means malware", and the clean metrics do not show it.** PE+aug has the highest pAUC@1e-2 and TPR@1e-3 of all models (+2.0 points against v2-PE, rule not met) yet flags 99.9% of the malware and 99.7% of the benign reports at k = 50 (ATT+aug 98.5 and 95.3%). A linear probe reads "padding present" from the pooled vector of every flatten model at AUC 0.97 (also from v2-PE, which never saw padding), so the probe shows what can be read, not what the model uses; the attention-pooled vector of ATT+bal is much harder to read (0.71).
5. **Not shown: that ATT+bal is better than v2-PE on clean data; any robustness against an attacker who knows the defence, who edits something other than adding benign API calls, or who is limited to a different budget; any result on another month.** The white-box attack has 3 seeds and 500 reports. The intervals cover test-set sampling only and the seed-to-seed spread is large (std of pAUC@1e-2 between seeds 1.7 to 6.4 points). April holds 2,509 distinct API sequences in 17,402 reports; with whole duplicate groups resampled together no per-seed-mean comparison between the trained models of Table 1 meets the claim rule, including PE+aug against PE+bal."""


LIMITS = """- **Statistics.** The stratified bootstrap of EVAL_PROTOCOL.md (reports independent, 1,000 resamples, numpy seed 0) covers test-set sampling only; the claim rule adds the 7-of-10 seed count. The cluster-bootstrap columns resample the 2,509 duplicate groups (hash of the API sequence) and are wider; a result that survives both is the safe one.
- **The random-padding test is in distribution for the models trained with balanced padding** (same procedure, different pool: the training pool and the EVAL pool are disjoint). The surrogate-chosen padding and the white-box greedy attack are the attacks they were not trained on; they use the same kind of edit (benign API calls added or prepended).
- **The 512-token window.** Only 36.6% of April reports (30.4% of the malware, 43.9% of the benign reports) fit into 512 tokens unedited (mean length 1,056 tokens); prepending or inserting calls pushes original content out of the window, so much of what the attacks measure is what happens when the window fills with padding. The "fits in 512" columns restrict to reports whose whole edited text fits; at v2-PE-surrogate k = 50 no report fits (n/a). The attention-pooled models read the same 512 tokens.
- **Released checkpoint.** It has its own tokenizer; its attacks use a second call store made with it (checked the same way). At v2-PE-surrogate k = 50 it flags every report (malware 100%, benign 100%), which is not detection.
- **The probe measures readability, not use** (see line 4); features are z-scored, the same logistic regression for every model; a shuffled-label control gives AUC 0.50 for all.
- **Training.** Keep runs train on 1.50x as many reports per epoch (101,484 against 67,768; 1,058 against 706 batches), so they take 1.5x the steps in the same 2 epochs. The tokenizer was fitted on all of January, including the validation slice (as in the earlier sections). Nothing was tuned or selected on April; all settings were fixed in NOTES.md section 15 before any attack score was computed. Two choices were made while building and before any attack score existed (NOTES 15.7): the white-box attacker keeps the best edit so far and stops when a report is below the 1% threshold; the "fits in 512 tokens" subset.
@@COMPUTE@@
- **Edited reports exist in memory only.** The edits of the training runs and of every attack are built from the call-token store of the ORIGINAL reports (verified against full re-tokenisation: 0 of 1,500 edits and 0 of 3,000 unedited reports differ; the §5.10 arrays are reproduced exactly) and only scores, logits and AUCs are saved. Artefacts that predate this rule and contain edited tokens: `results/att_bal/pad/april_pad.npz` (tracked in git; pushed in commit 6f22129), the private Kaggle datasets `nebula-v2pe-padtest` and `nebula-v2pe-augb`, and local copies in `results/_pad_train` and `results/_pad_bundle`; they are not used by anything in this section and I have not deleted them (a history purge would need a force-push)."""

LIMITS = LIMITS.replace("@@COMPUTE@@", LIMITS_COMPUTE)


def results_text(figure_path):
    t1 = read("table1.md")
    head = read("headline_tables.md")
    cl = read("cluster_table1.md")
    att = read("attack_tables.md")
    t1main = section(t1, "**Table 1.", "**Claim rule")
    claim = section(t1, "**Claim rule", "**Other metrics")
    other = section(t1, "**Other metrics")
    h = lambda start, end=None: section(head, start, end)
    return dict(t1main=t1main, claim=claim, other=other, cluster=cl, t2a=h("**Table 2 (1% FPR", "**Table 2 (0.1% FPR"), t2b=h("**Table 2 (0.1% FPR", "**Table 2 (white-box"), t2c=h("**Table 2 (white-box", "**Count of tests (random"),
                counts=h("**Count of tests (random", "**Table 3."), t3=h("**Table 3.", "**Nebula paper"), paper=h("**Nebula paper"), probe=section(att, "**Table 3b."), wbcmp=section(att, "**White-box comparisons", "**Table 3b."))


def build(fig):
    p = results_text(fig)
    return p


if __name__ == "__main__":
    p = build("results/review/fig_detection_vs_k.png")
    body = f"""Clean data, robustness and shortcut experiments for ATT+bal (data: the published April 2022 set, 9,399 malware and 8,003 benign reports; models trained on the 90% January slice; logit-ranked; 10 seeds unless stated).

{STATUS_RESULTS}

{p['t1main']}

Training of the keep models uses ALL clean reports of the 90% slice plus a padded copy of each report with probability 0.5 (new random edits per seed and epoch, random stream 7100), so an epoch holds about 101,500 reports (1.50x the 67,768 of the other runs) and takes about 1.5x as long. ATT+aug / PE+aug are the §5.10 procedure (padded reports replace the originals) applied to malware training reports only.

{p['claim']}

{p['other']}

Cluster-bootstrap sensitivity (duplicates resampled together), same comparisons:

{p['cluster']}

<!--AUDIT_T1-->

## Table 2. Robustness to padding

Thresholds are fixed per model and seed at 1% and 0.1% FPR of its scores of the unedited April benign reports. Random padding = the procedure of REPORT 5.10 (calls drawn from the EVAL pool) applied to all April reports; surrogate padding = the calls of rank 1..k of a ranking made with a LightGBM bag-of-API-names model (fitted on the 90% slice) or with v2-PE seed 0; white-box = greedy choice among 200 random EVAL-pool calls per step against the model's own score.

{p['t2a']}

{p['t2b']}

{p['t2c']}

White-box, ATT − PE, seed-paired:

{p['wbcmp']}

ATT+bal against PE+bal, counts of tests in which the CI excludes 0 with at least 7 of 10 seeds on the same side (descriptive):

{p['counts']}

<!--AUDIT_T2-->

Full tables (every model, every edit set, the malware TPR on the subset whose whole edited report fits in 512 tokens, the ATT − PE differences with the per-seed spread, seeds above/below 0 and both bootstrap intervals): `results/review/attack_tables.md`; the numbers: `results/review/attack_aggregates.json`.

![Detection against the number of calls prepended](results/review/fig_detection_vs_k.png)

## Table 3. The label shortcut

{p['t3']}

{p['probe']}

## Nebula paper vs ours

{p['paper']}

<!--AUDIT_MORE-->

## What is shown and what is not

{FIVE}

## Limits and how this was done

{LIMITS}

Code: `baseline/callstore.py`, `inmem_pad.py`, `v2pe.py` (training), `attack_rank.py`, `attack_run.py`, `probe.py`, `review_gpu.py` (scoring), `attack_stats.py`, `review_tables.py`, `review_attacks.py`, `review_cluster.py`, `review_write.py`, `review_compose.py`. Plan and decisions: `NOTES.md` section 15.
"""
    open(os.path.join(ROOT, "RESULTS_FOR_REVIEW.md"), "w").write("# Results for review: ATT+bal, clean copies, malware-only padding, and attacks it was not trained on\n\n" + body)
    rep = f"""### 5.11 ATT+bal under clean copies, malware-only padding and attacks it was not trained on (follow-up for the review)

{STATUS_511}

**Question.** Does ATT+bal (REPORT 5.10) hold up when (1) the clean copies of the reports are kept next to the padded ones, (2) padding is applied to malware only (a label shortcut), (3) it is attacked with padding it was not trained on: calls chosen with a surrogate model, and a white-box greedy attacker? Everything below was planned in `NOTES.md` section 15 before any result existed; nothing was tuned or selected on April.

**What was run.** Four new 10-seed trainings with the v2 recipe, pe_mode = paper, 2 epochs, seeds 0 to 9: ATT+bal-keep and PE+bal-keep (ALL clean reports plus a padded copy of each with probability 0.5; stream 7100; 1.50x reports per epoch), ATT+aug and PE+aug (§5.10 procedure, malware only). Attacks and probe: see `RESULTS_FOR_REVIEW.md` (which has all tables and the figure) and the limits below. The edits are built in memory from a store of the original reports and never written.

{p['t1main']}

{p['claim']}

{p['cluster']}

<!--AUDIT_T1-->

{p['t2a']}

{p['t2b']}

{p['t2c']}

<!--AUDIT_T2-->

{p['t3']}

{p['probe']}

![Detection against the number of calls prepended](results/review/fig_detection_vs_k.png)

**Reading.**

{FIVE}

**Limits and how this was done.**

{LIMITS}

"""
    path = os.path.join(ROOT, "REPRODUCTION_REPORT.md")
    txt = open(path).read()
    txt = re.sub(r"### 5\.11 .*?(?=\n## 6\. )", "", txt, flags=re.S) if "### 5.11 " in txt else txt
    txt = txt.replace("\n## 6. Differences from the paper", "\n" + rep + "\n## 6. Differences from the paper", 1)
    open(path, "w").write(txt)
    print("written", len(body), len(rep))
