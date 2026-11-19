# Padding pools (round 4, step 1)

Benign January reports with at least one API call, split by `hash_apis` group (disjoint groups), numpy Generator seed 4000. Row numbers are in `pools.json`.

| pool | reports | distinct sequences (hash_apis) | median calls | mean calls | max calls | used for |
|---|---|---|---|---|---|---|
| EVAL | 2,000 | 499 | 200 | 180.5 | 539 | testing only (padding of April malware) |
| TRAIN | 22,668 | 4,075 | 179 | 165.5 | 1,002 | training augmentation only |

Benign January reports without any call (in neither pool): 0.
