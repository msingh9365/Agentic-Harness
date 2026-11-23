### A1c: path-invariant rule, January fold 9 (bag of words + logistic regression; validation only)

| | validation pAUC@1e-2 | pAUC@1e-3 | AUC | TPR@1e-2 |
|---|---|---|---|---|
| without rule | 0.4869 | 0.1375 | 0.9185 | 0.7139 |
| with rule | 0.4914 | 0.1272 | 0.9169 | 0.7142 |

Difference (with rule - without) in pAUC@1e-2: **+0.45 points**, cluster 95% interval [-0.87, +2.31]. Decision (planned later only if >= -2 points): **GO**.

Counts: {"reports": 75298, "reports_with_replacement": 44491, "share_reports_with_replacement": 0.5908656272410954, "replacements_total": 103966, "replacements_per_report_mean": 1.3807272437514941, "replacements_per_report_median": 1.0, "placeholder_words_in_rule_text": 103966, "words_total_without_rule": 83438327, "words_total_with_rule": 83425720, "words_removed_by_the_rule": 12607, "share_words_removed": 0.00015109363350485072, "reports_where_placeholder_words_already_occur_without_rule": 0, "distinct_components": 44446, "components_kept": 35, "min_df": 50, "vocabulary_min_df5_without_rule": 34055, "vocabulary_min_df5_with_rule": 33840}
