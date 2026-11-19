Validation slice: 7,530 reports; **94.2% share their API sequence (hash_apis) with the 90% training slice** (7,097 seen, 433 unseen: 99 malware, 334 benign). April: 36.4%.

**V1. Validation metrics at epoch 2 of the models of §5.7 to §5.11 (10 seeds; mean ± std), on all validation reports, on the seen part and on the unseen part.** TPR@1e-2 of the unseen part is read at 3 false alarms of 334 benign reports; pAUC on 334 benign reports is coarse.

| model | pAUC@1e-2 all | TPR@1e-2 all | AUC all | pAUC@1e-2 seen | TPR@1e-2 seen | AUC seen | pAUC@1e-2 unseen | TPR@1e-2 unseen | AUC unseen |
|---|---|---|---|---|---|---|---|---|---|
| v2 | 0.947 ± 0.015 | 0.983 | 0.9984 | 0.967 ± 0.010 | 0.993 | 0.9992 | 0.585 ± 0.129 | 0.695 | 0.9361 |
| v2-PE | 0.962 ± 0.013 | 0.984 | 0.9985 | 0.975 ± 0.009 | 0.992 | 0.9993 | 0.673 ± 0.067 | 0.738 | 0.9358 |
| ATT | 0.969 ± 0.005 | 0.986 | 0.9987 | 0.979 ± 0.006 | 0.994 | 0.9993 | 0.730 ± 0.022 | 0.756 | 0.9399 |
| ATT+bal | 0.955 ± 0.007 | 0.981 | 0.9984 | 0.968 ± 0.005 | 0.991 | 0.9991 | 0.687 ± 0.018 | 0.720 | 0.9408 |
| PE+bal | 0.947 ± 0.009 | 0.980 | 0.9977 | 0.964 ± 0.007 | 0.988 | 0.9988 | 0.631 ± 0.073 | 0.724 | 0.9271 |
| ATT+bal-keep | 0.954 ± 0.008 | 0.982 | 0.9983 | 0.968 ± 0.006 | 0.991 | 0.9991 | 0.687 ± 0.031 | 0.718 | 0.9366 |
| PE+bal-keep | 0.951 ± 0.014 | 0.983 | 0.9980 | 0.969 ± 0.009 | 0.991 | 0.9990 | 0.590 ± 0.114 | 0.720 | 0.9317 |
| ATT+aug | 0.957 ± 0.007 | 0.981 | 0.9984 | 0.969 ± 0.007 | 0.992 | 0.9991 | 0.708 ± 0.025 | 0.745 | 0.9406 |
| PE+aug | 0.948 ± 0.007 | 0.978 | 0.9981 | 0.967 ± 0.008 | 0.989 | 0.9990 | 0.614 ± 0.074 | 0.709 | 0.9348 |

**V2. The 16 candidates of §5.12 on the unseen part only** (433 reports; unseen robustness R: the 99 unseen validation malware with 20 TRAIN-pool calls prepended, threshold = the 3rd highest of the 334 unseen benign scores; reference = the existing ATT+bal, mean R 0.5869, rule 2 excludes mean R < 0.5669).

| lr | p | epoch | mean pAUC@1e-2 (unseen) | SE | mean R (unseen) | mean loss (unseen) | min AUC | R excluded | note |
|---|---|---|---|---|---|---|---|---|---|
| 0.001 | 0.25 | 1 | 0.6905 | 0.0065 | 0.3949 | 0.3952 | 0.9296 | yes |  |
| 0.001 | 0.25 | 2 | 0.7005 | 0.0098 | 0.4687 | 0.5076 | 0.9358 | yes |  |
| 0.001 | 0.25 | 3 | 0.6981 | 0.0060 | 0.5030 | 0.5187 | 0.9290 | yes |  |
| 0.001 | 0.25 | 4 | 0.7064 | 0.0086 | 0.5273 | 0.5671 | 0.9289 | yes |  |
| 0.001 | 0.5 | 1 | 0.6871 | 0.0074 | 0.4970 | 0.4284 | 0.9264 | yes |  |
| 0.001 | 0.5 | 2 | 0.6930 | 0.0076 | 0.6061 | 0.5288 | 0.9307 | no |  |
| 0.001 | 0.5 | 3 | 0.7063 | 0.0081 | 0.6232 | 0.5308 | 0.9255 | no | **best on unseen** |
| 0.001 | 0.5 | 4 | 0.6987 | 0.0087 | 0.6364 | 0.5551 | 0.9212 | no | tied |
| 0.002 | 0.25 | 1 | 0.7001 | 0.0076 | 0.4242 | 0.3495 | 0.9206 | yes |  |
| 0.002 | 0.25 | 2 | 0.6833 | 0.0082 | 0.4788 | 0.4657 | 0.9278 | yes |  |
| 0.002 | 0.25 | 3 | 0.6687 | 0.0123 | 0.5040 | 0.5532 | 0.9269 | yes |  |
| 0.002 | 0.25 | 4 | 0.6761 | 0.0117 | 0.5667 | 0.5386 | 0.9239 | yes |  |
| 0.002 | 0.5 | 1 | 0.6871 | 0.0041 | 0.5333 | 0.3750 | 0.9331 | yes |  |
| 0.002 | 0.5 | 2 | 0.6872 | 0.0056 | 0.5869 | 0.4763 | 0.9284 | no |  |
| 0.002 | 0.5 | 3 | 0.6896 | 0.0092 | 0.6182 | 0.4683 | 0.9230 | no |  |
| 0.002 | 0.5 | 4 | 0.6847 | 0.0054 | 0.6323 | 0.5428 | 0.9280 | no |  |

**The rule of NOTES 16.4 applied to the unseen-part numbers chooses (0.001, 0.5, 3); on the full validation slice it chose (0.001, 0.25, 2).** The choice would change.
