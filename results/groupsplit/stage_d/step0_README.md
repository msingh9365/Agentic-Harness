# Step 0: what the group split removed (NOTES 22.2, 22.6)

For every April report we looked for the closest January report (by edit distance between API-name sequences, 0 = identical, 0.05 = at most 5% different) and asked in which part of the split it sits. Everything here is descriptive; no model score was used to build it.

## What it shows

* **The split took close neighbours away from very few April reports.** 36.4% of April reports have an exact twin somewhere in January. Only **3.8%** have it *only* in the new validation part (unseen by the new models), against 0.7% for the old validation slice. The share of April reports that *lost* a close neighbour (within 5% of some January report but not within 5% of any report of the new training part) is **1.6%** overall (0.9% of malware reports); for the old split 0.7%.
* **Nearest neighbour in the new validation part:** 19.4% of April reports (21.1% of malware), but most of those also have a training report almost as close, which is why so little was lost.
* **keylogger:** exact twin only in validation 0.0%, nearest neighbour in validation 1.7%, near-twin lost 0.0%; its April reports are far from everything in January (median nearest distance 0.18). Yet the detection of keylogger dropped most (v2-PE −16.8, ATT+bal −23.6 points). **Removed neighbours do not explain this.**
* **rat:** nearest neighbour in validation 14.1%, near-twin lost 0.0%, drop −12.7 / −17.9 points.
* **trojan:** nearest neighbour in validation 40.7%, near-twin lost 1.4%, drop −19.3 / −17.9 points.
* **The largest validation group** (1,056 identical reports, rat 542 + trojan 494, one single API-name sequence) is the nearest January report of 132 April rat reports (10.5%) and 187 April trojan reports (17.2%), but of no April report exactly. Those reports also have other training neighbours (few were "lost").
* **Across the 7 malware families** the rank correlation between the share of removed neighbours and the detection drop is +0.11 to +0.83 (n = 7, not a test); the sign is the opposite of what "more removed, bigger drop" would give, or near zero.

## So

The earlier guess that the keylogger/rat/trojan drop comes from whole groups being held out of training is **not supported** by this descriptive check. The split removed few near-twins of April reports from training. What does cause the ~7 point drop remains open (tokenizer fit, seeds, ATT+bal learning rate, or properties of the group split that API-name distances do not capture).

## What this does not show

* It uses API-name sequences, not the first 512 tokens the model reads, and not the label of the neighbour (a close neighbour of another class would not help). 5% is one choice of "close".
* It does not show that the models use neighbours at all, or that anything else does cause the drop; it only checks one explanation.
* n = 7 families for the correlations.

Files: `step0_what_the_split_removed.md|json` (all tables), `fig_step0_what_the_split_removed.png`; code `baseline/gs_removed.py`.
