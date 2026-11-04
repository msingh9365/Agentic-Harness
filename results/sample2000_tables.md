# Generated tables (analyze.py)

## Sample accounting
| split    |   ok |
|:---------|-----:|
| testset  |  366 |
| trainset | 1634 |

Top-level JSON type of each file:

| split    |   list |
|:---------|-------:|
| testset  |    366 |
| trainset |   1634 |

Samples measured (status ok): 2,000 of 2,000 files.

Field attribution exact (concatenated field token ids == full token ids): 100.0% (2,000)

## Tokens per sample (Nebula preprocessing, no truncation)
| set | n | median | p75 | p90 | p99 | max | >512 | >1024 | >2048 | >4096 | >8192 | tokens dropped by 512 cut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 2,000 | 1,069 | 1,708 | 2,379 | 3,006 | 18,661 | 66.6% (1,332) | 50.8% (1,015) | 20.8% (416) | 0.3% (6) | 0.1% (1) | 65.3% (1,446,065 of 2,214,769) |
| testset | 366 | 981 | 1,683 | 2,269 | 2,938 | 4,740 | 62.8% (230) | 49.2% (180) | 19.9% (73) | 0.3% (1) | 0.0% (0) | 62.7% (237,849 of 379,066) |
| trainset | 1,634 | 1,069 | 1,708 | 2,410 | 3,006 | 18,661 | 67.4% (1,102) | 51.1% (835) | 21.0% (343) | 0.3% (5) | 0.1% (1) | 65.8% (1,208,216 of 1,835,703) |

Mean per-sample fraction of tokens dropped by the 512 cut: 40.5%; median per-sample fraction: 52.1%.

## Tokens per sample by family and split

### testset

| family | n | median | p75 | p90 | p99 | max | >512 | >1024 | >2048 | >4096 | >8192 | tokens dropped by 512 cut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| backdoor | 42 | 2,249 | 2,323 | 2,378 | 2,555 | 2,606 | 81.0% (34) | 69.0% (29) | 66.7% (28) | 0.0% (0) | 0.0% (0) | 74.1% (52,654 of 71,041) |
| clean | 150 | 839 | 1,435 | 2,243 | 2,825 | 2,991 | 53.3% (80) | 47.3% (71) | 13.3% (20) | 0.0% (0) | 0.0% (0) | 62.4% (85,201 of 136,642) |
| coinminer | 40 | 1,252 | 2,085 | 2,086 | 2,374 | 2,484 | 95.0% (38) | 67.5% (27) | 37.5% (15) | 0.0% (0) | 0.0% (0) | 66.1% (38,128 of 57,724) |
| dropper | 6 | 201 | 444 | 1,203 | 1,852 | 1,924 | 16.7% (1) | 16.7% (1) | 0.0% (0) | 0.0% (0) | 0.0% (0) | 48.8% (1,412 of 2,893) |
| keylogger | 24 | 376 | 383 | 871 | 1,149 | 1,170 | 12.5% (3) | 12.5% (3) | 0.0% (0) | 0.0% (0) | 0.0% (0) | 19.2% (1,791 of 9,322) |
| ransomware | 55 | 708 | 1,737 | 2,587 | 3,821 | 4,740 | 69.1% (38) | 36.4% (20) | 16.4% (9) | 1.8% (1) | 0.0% (0) | 63.8% (36,732 of 57,613) |
| rat | 28 | 1,169 | 1,171 | 1,174 | 1,176 | 1,176 | 100.0% (28) | 92.9% (26) | 0.0% (0) | 0.0% (0) | 0.0% (0) | 54.5% (17,148 of 31,484) |
| trojan | 21 | 402 | 758 | 1,358 | 2,041 | 2,211 | 38.1% (8) | 14.3% (3) | 4.8% (1) | 0.0% (0) | 0.0% (0) | 38.7% (4,783 of 12,347) |

### trainset

| family | n | median | p75 | p90 | p99 | max | >512 | >1024 | >2048 | >4096 | >8192 | tokens dropped by 512 cut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| backdoor | 230 | 2,330 | 2,489 | 2,606 | 2,623 | 18,661 | 95.2% (219) | 87.0% (200) | 76.5% (176) | 0.9% (2) | 0.4% (1) | 77.2% (385,099 of 498,823) |
| clean | 555 | 1,172 | 1,355 | 2,191 | 3,079 | 4,667 | 61.4% (341) | 54.4% (302) | 12.3% (68) | 0.4% (2) | 0.0% (0) | 62.9% (347,482 of 552,543) |
| coinminer | 158 | 1,214 | 1,588 | 2,178 | 3,035 | 3,039 | 94.3% (149) | 70.3% (111) | 12.0% (19) | 0.0% (0) | 0.0% (0) | 61.3% (123,852 of 202,144) |
| dropper | 175 | 147 | 1,069 | 1,608 | 2,513 | 3,006 | 38.3% (67) | 30.9% (54) | 6.3% (11) | 0.0% (0) | 0.0% (0) | 55.2% (56,064 of 101,641) |
| keylogger | 88 | 1,684 | 1,708 | 1,853 | 2,493 | 2,534 | 89.8% (79) | 87.5% (77) | 9.1% (8) | 0.0% (0) | 0.0% (0) | 67.2% (85,369 of 127,023) |
| ransomware | 207 | 949 | 950 | 987 | 3,607 | 3,829 | 57.5% (119) | 10.1% (21) | 6.3% (13) | 0.0% (0) | 0.0% (0) | 55.8% (78,338 of 140,324) |
| rat | 21 | 764 | 1,212 | 1,216 | 2,286 | 2,553 | 76.2% (16) | 38.1% (8) | 4.8% (1) | 0.0% (0) | 0.0% (0) | 50.9% (8,966 of 17,600) |
| trojan | 197 | 607 | 1,762 | 2,600 | 2,611 | 4,637 | 56.9% (112) | 31.5% (62) | 23.9% (47) | 0.5% (1) | 0.0% (0) | 63.0% (123,046 of 195,427) |
| windows_syswow64 | 3 | 58 | 62 | 64 | 65 | 65 | 0.0% (0) | 0.0% (0) | 0.0% (0) | 0.0% (0) | 0.0% (0) | 0.0% (0 of 178) |

## Malware vs benign
| split / class | n | median tokens | mean tokens | >512 | median entry points | median chunks (per-EP) |
|---|---|---|---|---|---|---|
| all / malware | 1,292 | 970 | 1,181 | 70.5% (911) | 1 | 3 |
| all / benign | 708 | 1,110 | 974 | 59.5% (421) | 1 | 3 |
| testset / malware | 216 | 1,073 | 1,122 | 69.4% (150) | 1 | 3 |
| testset / benign | 150 | 839 | 911 | 53.3% (80) | 1 | 3 |
| trainset / malware | 1,076 | 950 | 1,192 | 70.7% (761) | 1 | 3 |
| trainset / benign | 558 | 1,160 | 991 | 61.1% (341) | 1 | 3 |

ROC AUC of a classifier that uses ONLY the length (higher = malware); 0.5 = no signal:

| set | AUC(tokens) | AUC(min(tokens,512)) | AUC(n_entry_points) |
|---|---|---|---|
| all | 0.546 | 0.546 | 0.449 |
| testset | 0.586 | 0.596 | 0.480 |
| trainset | 0.539 | 0.535 | 0.441 |

Number of real (non-pad) tokens Nebula sees, min(tokens, 512):

| set | class | median | share of samples with < 512 real tokens (i.e. padded) |
|---|---|---|---|
| all | malware | 512 | 29.5% (381) |
| all | benign | 512 | 40.5% (287) |
| testset | malware | 512 | 30.6% (66) |
| testset | benign | 512 | 46.7% (70) |
| trainset | malware | 512 | 29.3% (315) |
| trainset | benign | 512 | 38.9% (217) |

## Which fields survive the 512 cut

Field order actually found in the tokenized reports (all distinct orders):

| field order (left = first in sequence) | samples |
|---|---|
| `apis` | 1,395 |
| `file_access|apis` | 402 |
| `registry_access|apis` | 161 |
| `registry_access|file_access|apis` | 33 |
| `network_events.traffic|file_access|apis` | 8 |
| `registry_access|network_events.traffic|apis` | 1 |

| field | samples with field | tokens (all samples) | share of all tokens | median tokens (when present) | % of field tokens kept by 512 cut | samples where field fully kept | samples where field fully cut |
|---|---|---|---|---|---|---|---|
| registry_access | 9.8% (195) | 6,720 | 0.3% | 32 | 100.0% (6,720) | 100.0% (195) | 0.0% (0) |
| network_events.traffic | 0.5% (9) | 619 | 0.0% | 13 | 93.5% (579) | 88.9% (8) | 0.0% (0) |
| file_access | 22.1% (443) | 7,882 | 0.4% | 10 | 100.0% (7,882) | 100.0% (443) | 0.0% (0) |
| apis | 100.0% (2,000) | 2,199,548 | 99.3% | 1,069 | 34.3% (753,523) | 33.4% (668) | 0.1% (1) |

'samples where field fully kept / cut' are out of the samples that have the field. Field tokens include the field's own key name (e.g. `file access`).

Composition of the tokens Nebula actually keeps (sum over samples of the first ≤512 tokens):

| field | kept tokens | share of kept |
|---|---|---|
| registry_access | 6,720 | 0.9% |
| network_events.traffic | 579 | 0.1% |
| file_access | 7,882 | 1.0% |
| apis | 753,523 | 98.0% |

For the 1,332 samples longer than 512 tokens only:

| field | samples with field | % of field tokens kept | samples where field fully cut |
|---|---|---|---|
| registry_access | 10.0% (133) | 100.0% | 0.0% (0) |
| network_events.traffic | 0.7% (9) | 93.5% | 0.0% (0) |
| file_access | 30.4% (405) | 100.0% | 0.0% (0) |
| apis | 100.0% (1,332) | 31.6% | 0.1% (1) |

## Entry points

Entry-point tokenization status:

| status   |   entry points |
|:---------|---------------:|
| ok       |           3117 |

| quantity | median | p75 | p90 | p99 | max | mean |
|---|---|---|---|---|---|---|
| entry points per sample | 1 | 1 | 1 | 5 | 102 | 1.6 |
| thread entry points per sample | 0 | 0 | 0 | 1 | 101 | 0.5 |
| tokens per entry point (tokenized alone) | 157 | 1,284 | 2,245 | 2,888 | 4,740 | 711.4 |
| tokens per module_entry | 1,058 | 1,699 | 2,371 | 2,973 | 4,740 | 1,085.4 |
| tokens per thread | 4 | 4 | 157 | 1,649 | 3,857 | 51.9 |
| sum of per-EP tokens per sample | 1,069 | 1,708 | 2,379 | 3,006 | 20,284 | 1,108.7 |
| chunks needed, (a) fixed 512 | 3 | 4 | 5 | 6 | 37 | 2.8 |
| chunks needed, (b) per-EP, 512/overlap 64 | 3 | 4 | 6 | 8 | 111 | 3.4 |

Samples with more than one entry point: 5.5% (110)

Entry points longer than 512 tokens: 42.9% (1,338) (module_entry: 66.2% (1,323); thread: 1.6% (15))

Samples with at least one entry point longer than 512 tokens: 66.6% (1,332)

Entry-point counts by family (all splits):

| family | samples | median EPs | p90 EPs | max EPs | samples with >1 EP |
|---|---|---|---|---|---|
| backdoor | 272 | 1 | 1 | 102 | 0.7% (2) |
| clean | 705 | 1 | 2 | 5 | 12.2% (86) |
| coinminer | 198 | 1 | 1 | 4 | 4.0% (8) |
| dropper | 181 | 1 | 1 | 3 | 1.1% (2) |
| keylogger | 112 | 1 | 1 | 3 | 0.9% (1) |
| ransomware | 262 | 1 | 1 | 102 | 3.8% (10) |
| rat | 49 | 1 | 1 | 1 | 0.0% (0) |
| trojan | 218 | 1 | 1 | 5 | 0.5% (1) |
| windows_syswow64 | 3 | 1 | 1 | 1 | 0.0% (0) |

Share of samples that fit within a given number of 512-token chunks:

| set | scheme | ≤16 chunks | ≤32 chunks | ≤64 chunks |
|---|---|---|---|---|
| all | (a) fixed 512 | 100.0% (1,999) | 100.0% (1,999) | 100.0% (2,000) |
| all | (b) per entry point | 99.5% (1,991) | 99.5% (1,991) | 99.5% (1,991) |
| testset | (a) fixed 512 | 100.0% (366) | 100.0% (366) | 100.0% (366) |
| testset | (b) per entry point | 98.9% (362) | 98.9% (362) | 98.9% (362) |
| trainset | (a) fixed 512 | 99.9% (1,633) | 99.9% (1,633) | 100.0% (1,634) |
| trainset | (b) per entry point | 99.7% (1,629) | 99.7% (1,629) | 99.7% (1,629) |

Coverage if the model only reads the first K chunks (share of all tokens covered):

| scheme | K=1 (=Nebula) | K=16 | K=32 | K=64 |
|---|---|---|---|---|
| (a) fixed 512 | 34.7% | 99.5% | 99.9% | 100.0% |
| (b) per entry point | 33.0% | 99.2% | 99.3% | 99.6% |

(b) coverage is measured on the sum of per-EP tokens, in entry-point order; overlap tokens are not double counted.

Chunks needed by family (all splits):

| family | median (a) | p90 (a) | median (b) | p90 (b) | (b) ≤32 chunks |
|---|---|---|---|---|---|
| backdoor | 5 | 6 | 6 | 6 | 99.6% (271) |
| clean | 3 | 5 | 3 | 5 | 100.0% (705) |
| coinminer | 3 | 5 | 3 | 5 | 100.0% (198) |
| dropper | 1 | 4 | 1 | 4 | 100.0% (181) |
| keylogger | 3 | 4 | 3 | 4 | 100.0% (112) |
| ransomware | 2 | 4 | 2 | 4 | 96.9% (254) |
| rat | 3 | 3 | 3 | 3 | 100.0% (49) |
| trojan | 2 | 6 | 2 | 6 | 100.0% (218) |
| windows_syswow64 | 1 | 1 | 1 | 1 | 100.0% (3) |

## Emulation cap (Speakeasy `max_api_count` = 500 in the dataset's config)

| set | samples that hit the API cap | median tokens (hit cap) | median tokens (no cap) | median raw API calls |
|---|---|---|---|---|
| all | 18.6% (371) | 2,365 | 813 | 182 |
| backdoor | 68.4% (186) | 2,369 | 1,104 | 501 |
| clean | 9.6% (68) | 2,329 | 716 | 185 |
| coinminer | 20.2% (40) | 1,616 | 1,202 | 239 |
| dropper | 4.4% (8) | 2,240 | 118 | 22 |
| keylogger | 0.9% (1) | 2,534 | 1,217 | 225 |
| ransomware | 5.0% (13) | 2,207 | 893 | 180 |
| rat | 4.1% (2) | 1,400 | 1,168 | 219 |
| trojan | 24.3% (53) | 2,599 | 433 | 93 |
| windows_syswow64 | 0.0% (0) | nan | 58 | 13 |

Of the samples longer than 512 tokens, 27.5% (366) hit the emulation cap.

Tokens per raw API call (entry points with ≥1 API call): median 5.20, p10 4.00, p90 7.48. Entry points with ≥500 API calls: 7.9% (247).
