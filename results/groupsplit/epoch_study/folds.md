### Epoch study folds (NOTES 28.1): rule of NOTES 21.3 applied to the ten folds; candidates [4, 9]; chosen [9, 4] (2 fold(s): fewer than 4 qualify, so the study has 2)

| fold | validation reports | benign % | groups | largest group % | backdoor | clean | coinminer | dropper | keylogger | ransomware | rat | trojan | windows_syswow64 | qualifies |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 6891 | 19.2 | 58 | 51.7 | 1900 | 1309 | 629 | 743 | 192 | 273 | 166 | 1664 | 15 | no |
| 1 | 5824 | 24.5 | 194 | 27.1 | 1576 | 1411 | 638 | 752 | 233 | 430 | 32 | 737 | 15 | no |
| 2 | 9010 | 15.4 | 77 | 47.9 | 901 | 1378 | 635 | 746 | 254 | 4321 | 29 | 732 | 14 | no |
| 3 | 6547 | 33.9 | 835 | 19.6 | 914 | 2205 | 663 | 1281 | 233 | 430 | 47 | 759 | 15 | no |
| 4 | 7467 | 29.7 | 834 | 30.7 | 913 | 2204 | 662 | 757 | 1063 | 430 | 665 | 758 | 15 | yes (chosen) |
| 5 | 7467 | 34.1 | 980 | 14.7 | 932 | 2531 | 683 | 777 | 1097 | 602 | 46 | 784 | 15 | no |
| 6 | 7467 | 40.2 | 1087 | 12.5 | 949 | 2978 | 931 | 786 | 233 | 707 | 46 | 811 | 26 | no |
| 7 | 7467 | 42.6 | 1094 | 10.4 | 969 | 3120 | 684 | 790 | 233 | 718 | 78 | 811 | 64 | no |
| 8 | 8440 | 49.7 | 332 | 49.4 | 968 | 4178 | 683 | 790 | 232 | 718 | 46 | 811 | 14 | no |
| 9 | 8718 | 36.3 | 1204 | 12.1 | 1039 | 3119 | 683 | 821 | 608 | 998 | 542 | 866 | 42 | yes (chosen) |

January benign share 32.8%; window 27.8% to 37.8%; per-fold reasons: {"0": {"families_ge_300": false, "benign_share": 0.1921, "benign_within_5pt": false}, "1": {"families_ge_300": false, "benign_share": 0.2448, "benign_within_5pt": false}, "2": {"families_ge_300": false, "benign_share": 0.1545, "benign_within_5pt": false}, "3": {"families_ge_300": false, "benign_share": 0.3391, "benign_within_5pt": true}, "4": {"families_ge_300": true, "benign_share": 0.2972, "benign_within_5pt": true}, "5": {"families_ge_300": false, "benign_share": 0.341, "benign_within_5pt": true}, "6": {"families_ge_300": false, "benign_share": 0.4023, "benign_within_5pt": false}, "7": {"families_ge_300": false, "benign_share": 0.4264, "benign_within_5pt": false}, "8": {"families_ge_300": false, "benign_share": 0.4967, "benign_within_5pt": false}, "9": {"families_ge_300": true, "benign_share": 0.3626, "benign_within_5pt": true}}

- fold 9: split hash `c3a2c99bbf5dc6ddc60697e7b9468bf8`, train 66,580, validation 8,718 (benign 3161, malware 5557), evaluation pool = benign reports of fold 4 (2,219 with >= 1 call), the training padding pool = the benign training reports with >= 1 call minus these.
- fold 4: split hash `357649ad3fa664517dc8e48262f93126`, train 67,831, validation 7,467 (benign 2219, malware 5248), evaluation pool = benign reports of fold 9 (3,161 with >= 1 call), the training padding pool = the benign training reports with >= 1 call minus these.
