### Length change, old tokenizer -> bpe50k_fix (median [mean]; calls inside = calls completely inside the first 512 tokens)

| population | class | reports | tokens/report old | tokens/report new | median ratio new/old | share > 512 old / new (%) | calls inside 512 old | calls inside 512 new | share with < 3 calls inside (of reports with >= 3 calls) old / new (%) |
|---|---|---|---|---|---|---|---|---|---|
| January | all | 75298 | 1063 [1154.3] | 1059 [1149.2] | 0.997 | 66.5 / 66.5 | 83 [66.5] | 83 [66.7] | 0.0 / 0.0 |
| January | malware | 50630 | 950 [1237.9] | 942 [1232.3] | 0.996 | 70.0 / 70.0 | 85 [69.7] | 86 [70.1] | 0.0 / 0.0 |
| January | benign | 24668 | 1102 [982.7] | 1094.5 [978.6] | 0.997 | 59.4 / 59.4 | 80 [59.7] | 80 [59.8] | 0.0 / 0.0 |
| April | all | 17402 | 1014.5 [1056.4] | 1007 [1051.5] | 0.996 | 63.4 / 63.4 | 80 [66.6] | 80 [66.7] | 0.0 / 0.0 |
| April | malware | 9399 | 1009 [1141.1] | 1002 [1135.6] | 0.996 | 69.6 / 69.6 | 95 [73.0] | 95 [73.3] | 0.0 / 0.0 |
| April | benign | 8003 | 1018 [957.0] | 1010 [952.8] | 0.997 | 56.1 / 56.1 | 79 [59.0] | 79 [59.0] | 0.0 / 0.0 |
