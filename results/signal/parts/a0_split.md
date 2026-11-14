### 0. Validation split (January, grouped by API-name sequence)

`GroupShuffleSplit(test_size=0.1, random_state=0)` over the distinct `hash_apis` values of the January reports: 10% of the groups go to validation. `test` is April.

| side | groups (hash_apis) | reports | malware | largest group | groups of 1 report |
|---|---|---|---|---|---|
| train | 6,093 | 65,679 | 65.6% (43,114/65,679) | 4,312 | 3,738 |
| val | 678 | 9,619 | 78.1% (7,516/9,619) | 2,292 | 409 |
| test | 2,509 | 17,402 | 54.0% (9,399/17,402) | 864 | 1,628 |

April reports whose API-name sequence also occurs in January: 36.4% (6,329/17,402).
