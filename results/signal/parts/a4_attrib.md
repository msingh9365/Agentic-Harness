### 4. Attribution: integrated gradients on 1,000 April reports

Stratified sample (seed 0): 500 malware (backdoor 72, coinminer 72, dropper 72, keylogger 71, ransomware 71, rat 71, trojan 71) and 500 benign. Method: integrated gradients on the output of Nebula's embedding layer, 128 steps (midpoint rule), target = Nebula's logit, attribution of a token = sum over the 64 embedding dimensions. Baseline = the embedding of the empty report `{'apis': []}` tokenized and padded. Completeness error |Σ attribution − (logit − baseline logit)|: median 0.0384, p95 0.2100 (mean |logit − baseline logit| = 27.79). Token categories come from tokenizing the report in pieces (exact for 1000/1000 reports; the rest are left out of 4a and 4c). Padding positions match the baseline's padding, so their attribution is zero by construction.

#### 4a. Share of total absolute attribution per category

| class | API name | address-like hex (≥ 0x10000) | small hex | string argument | field key | file/registry/network value | padding | other |
|---|---|---|---|---|---|---|---|---|
| malware (n=500) | 22.8% | 30.3% | 13.4% | 24.4% | 2.1% | 5.9% | 0.0% | 1.2% |
| malware: share of the 512 positions | 26.3% | 17.5% | 14.3% | 15.7% | 0.3% | 1.8% | 23.1% | 1.1% |
| malware: mean signed attribution per report (logit) | -9.18 | +8.65 | -3.84 | -2.98 | +2.47 | -4.23 | +0.00 | -0.69 |
| benign (n=500) | 24.7% | 31.8% | 22.0% | 18.4% | 0.7% | 1.4% | 0.0% | 1.1% |
| benign: share of the 512 positions | 23.6% | 11.4% | 24.6% | 9.2% | 0.2% | 0.3% | 29.6% | 1.0% |
| benign: mean signed attribution per report (logit) | -13.00 | -13.21 | -3.10 | -11.17 | +0.68 | -1.08 | +0.00 | +0.01 |

#### 4b. Share of absolute attribution per 64-token block (Nebula attends only inside these blocks)

| class | tokens 0–63 | tokens 64–127 | tokens 128–191 | tokens 192–255 | tokens 256–319 | tokens 320–383 | tokens 384–447 | tokens 448–511 |
|---|---|---|---|---|---|---|---|---|
| malware | 37.9% | 12.1% | 12.3% | 7.1% | 10.9% | 7.0% | 5.9% | 6.8% |
| benign | 37.7% | 13.6% | 14.5% | 7.6% | 9.1% | 5.8% | 4.5% | 7.3% |

#### 4c. Top 30 tokens by mean attribution (tokens with ≥ 50 occurrences in the sample)

| direction | token | category | occurrences | mean attribution | mean \|attribution\| |
|---|---|---|---|---|---|
| towards malware (highest mean) | `▁registry` | field key | 93 | +17.4730 | 17.4730 |
| towards malware (highest mean) | `▁0x7660` | small hex | 89 | +6.4271 | 6.4271 |
| towards malware (highest mean) | `▁0x1211f20` | address-like hex (≥ 0x10000) | 61 | +4.1111 | 4.1111 |
| towards malware (highest mean) | `▁0x599b5c` | address-like hex (≥ 0x10000) | 66 | +2.3074 | 2.8790 |
| towards malware (highest mean) | `▁0x7540` | small hex | 205 | +2.1054 | 2.1054 |
| towards malware (highest mean) | `▁0xfeee0009` | address-like hex (≥ 0x10000) | 191 | +2.0080 | 2.1762 |
| towards malware (highest mean) | `▁0x74e0` | small hex | 151 | +1.9644 | 1.9644 |
| towards malware (highest mean) | `▁0x4c4308` | address-like hex (≥ 0x10000) | 69 | +1.9213 | 1.9213 |
| towards malware (highest mean) | `▁gettickcount64` | string argument | 55 | +1.7413 | 2.2693 |
| towards malware (highest mean) | `▁0xfeee001d` | address-like hex (≥ 0x10000) | 157 | +1.5275 | 1.8410 |
| towards malware (highest mean) | `▁0xfeee005f` | address-like hex (≥ 0x10000) | 54 | +1.5033 | 1.5033 |
| towards malware (highest mean) | `585` | address-like hex (≥ 0x10000) | 675 | +1.4965 | 2.8846 |
| towards malware (highest mean) | `▁0x7300` | small hex | 153 | +1.4155 | 1.4155 |
| towards malware (highest mean) | `▁0x41de08` | address-like hex (≥ 0x10000) | 197 | +1.2980 | 1.4226 |
| towards malware (highest mean) | `▁getdateformatex` | string argument | 83 | +1.2448 | 1.2448 |
| towards malware (highest mean) | `▁0xfeee001a` | address-like hex (≥ 0x10000) | 187 | +1.2186 | 1.2253 |
| towards malware (highest mean) | `▁0xfeee0035` | address-like hex (≥ 0x10000) | 82 | +1.2040 | 1.2040 |
| towards malware (highest mean) | `▁0x41deb0` | address-like hex (≥ 0x10000) | 68 | +1.1555 | 1.1555 |
| towards malware (highest mean) | `▁0xfeee0040` | address-like hex (≥ 0x10000) | 81 | +1.1274 | 1.1274 |
| towards malware (highest mean) | `▁0x78` | small hex | 92 | +1.1143 | 1.7068 |
| towards malware (highest mean) | `▁2` | string argument | 493 | +1.0996 | 1.1355 |
| towards malware (highest mean) | `▁createfilea` | string argument | 76 | +1.0285 | 8.5990 |
| towards malware (highest mean) | `▁0x7810` | small hex | 264 | +1.0218 | 1.0253 |
| towards malware (highest mean) | `▁wininet` | API name | 53 | +0.9837 | 0.9837 |
| towards malware (highest mean) | `▁0xfeee0010` | address-like hex (≥ 0x10000) | 191 | +0.9054 | 1.0231 |
| towards malware (highest mean) | `ect` | string argument | 77 | +0.9051 | 1.0369 |
| towards malware (highest mean) | `▁gettempw` | string argument | 69 | +0.8916 | 1.5126 |
| towards malware (highest mean) | `▁getmain` | API name | 72 | +0.8881 | 0.9428 |
| towards malware (highest mean) | `▁0x7f00` | small hex | 53 | +0.8859 | 0.9464 |
| towards malware (highest mean) | `▁0xfeee0025` | address-like hex (≥ 0x10000) | 100 | +0.8349 | 3.7029 |
| towards benign (lowest mean) | `▁0x41de98` | address-like hex (≥ 0x10000) | 68 | -18.1404 | 18.1404 |
| towards benign (lowest mean) | `▁getsystemtimeasfiletime` | API name | 560 | -9.1841 | 9.6177 |
| towards benign (lowest mean) | `▁0x405d54` | address-like hex (≥ 0x10000) | 70 | -6.5198 | 6.5198 |
| towards benign (lowest mean) | `▁pf` | string argument | 320 | -6.1100 | 6.6226 |
| towards benign (lowest mean) | `▁0x1211fc0` | address-like hex (≥ 0x10000) | 178 | -6.0135 | 6.0135 |
| towards benign (lowest mean) | `▁isvalidlocalename` | string argument | 82 | -5.0974 | 5.0974 |
| towards benign (lowest mean) | `▁file` | field key | 89 | -4.0556 | 4.0919 |
| towards benign (lowest mean) | `▁0x70e0` | small hex | 55 | -3.7652 | 3.7652 |
| towards benign (lowest mean) | `▁0x41db74` | address-like hex (≥ 0x10000) | 70 | -3.7101 | 3.7101 |
| towards benign (lowest mean) | `▁0x1211fd4` | address-like hex (≥ 0x10000) | 179 | -3.5635 | 3.5785 |
| towards benign (lowest mean) | `▁key` | file/registry/network value | 338 | -3.1082 | 3.1082 |
| towards benign (lowest mean) | `▁0x7360` | small hex | 152 | -2.8631 | 2.8631 |
| towards benign (lowest mean) | `▁msvcr71` | API name | 64 | -2.5505 | 2.5505 |
| towards benign (lowest mean) | `▁tlssetvalue` | API name | 190 | -2.4603 | 2.8752 |
| towards benign (lowest mean) | `▁0x4700` | small hex | 480 | -2.3544 | 3.8672 |
| towards benign (lowest mean) | `▁getkeyboardtype` | API name | 50 | -2.2455 | 2.2455 |
| towards benign (lowest mean) | `▁createsymboliclinkw` | string argument | 83 | -2.1477 | 2.1477 |
| towards benign (lowest mean) | `▁queryperformancecounter` | API name | 576 | -2.0350 | 2.1163 |
| towards benign (lowest mean) | `▁0x4ac0` | small hex | 314 | -1.9802 | 2.0221 |
| towards benign (lowest mean) | `▁0x75a0` | small hex | 151 | -1.7878 | 1.7878 |
| towards benign (lowest mean) | `▁0x10000` | address-like hex (≥ 0x10000) | 75 | -1.7798 | 1.7857 |
| towards benign (lowest mean) | `▁createthreadpoolwait` | string argument | 83 | -1.7221 | 1.7981 |
| towards benign (lowest mean) | `▁isprocessorfeaturepresent` | API name | 378 | -1.6989 | 1.7842 |
| towards benign (lowest mean) | `▁0x7cd0` | small hex | 55 | -1.6788 | 1.6788 |
| towards benign (lowest mean) | `▁createsemaphoreexw` | string argument | 83 | -1.6453 | 1.6661 |
| towards benign (lowest mean) | `▁g` | file/registry/network value | 79 | -1.6072 | 1.6072 |
| towards benign (lowest mean) | `▁getversionexa` | API name | 171 | -1.6035 | 1.9421 |
| towards benign (lowest mean) | `▁0x7aa0` | small hex | 64 | -1.5731 | 1.5731 |
| towards benign (lowest mean) | `▁closethreadpooltimer` | string argument | 83 | -1.5249 | 1.5406 |
| towards benign (lowest mean) | `▁xmmi64` | string argument | 279 | -1.5001 | 1.5334 |
