# How much does Nebula's 512-token cut throw away?

A measurement study on the full `dtrizna/quovadis-speakeasy` dataset (92,700
samples), using Nebula's own preprocessing code.

> **Short answer.** Two out of three samples are longer than 512 tokens, and
> two thirds of all tokens are never seen by the model. What gets cut is
> almost only the API-call sequence. The reports are not very long, though:
> 99.8% of samples fit in eight 512-token chunks (4,096 tokens), because the
> emulator stopped most runs at 500 API calls. Also, 94.7% of samples have
> only **one** entry point, so chunking "by entry point / process" is in
> practice the same as cutting one long API sequence into pieces.

All numbers below were produced by `measure_lengths.py` and `analyze.py` in
this branch. The tables are pasted in automatically from
[`results/tables.md`](results/tables.md) by `build_report.py`. Raw counts are
in brackets next to every percentage.

---

## 1. Method

### 1.1 Exact preprocessing used

Nothing is re-implemented. `measure_lengths.py` imports these from a clone of
<https://github.com/dtrizna/nebula> at commit
`1343ae170ef32b01a75d2dd5fb906b5541f073df`:

| step | Nebula code |
|---|---|
| field filter | `nebula.preprocessing.tokenization.JSONFilter`, built inside `PEDynamicFeatureExtractor` with `nebula.constants.SPEAKEASY_RECORD_FIELDS` (file_access event/path, network_events.traffic server/port, registry_access event/path, apis api_name/args/ret_val). The script asserts that the filter really uses this field list. |
| record limit | `SPEAKEASY_RECORD_LIMITS = {"network_events.traffic": 256}` |
| normalisation + join | `PEDynamicFeatureExtractor.filter_and_normalize_report(entry_points)`: path and IP normalisation, non-alphanumeric characters removed from API args, then `joinRecordsToJSON()` |
| tokenizer | `JSONTokenizerBPE(vocab_size=50001, seq_len=512, model_path=nebula/objects/bpe_50000_sentencepiece.model, vocab=nebula/objects/bpe_50000_vocab.json)` |
| token count | `len(tokenizer.encode(report, pad=False)[0])`. This is the length *before* `pad_sequence()` keeps `encoded[:512]` (`tokenization.py:154-159`). |

To avoid importing torch through `nebula/__init__.py`, the script registers
empty package modules for `nebula`, `nebula.preprocessing` and
`nebula.models`, stubs `nebula.models.ember`, and builds `nebula.misc` with
only `get_alphanum_chars()`, copied word for word from the source file with
`ast` (details in [README.md](README.md)).

**Sanity check** on the example reports in `nebula/emulation/`
([log](results/logs/sanity.log)):

| report | tokens | expected |
|---|---|---|
| report_example_entrypoint_with_file | 551 | 551 |
| report_example_entrypoint_with_registry | 1,672 | 1,672 |
| report_example_entrypoint_withDNS | 1,811 | 1,811 |
| report_example_entrypoint_ransomware | 2,609 | 2,609 |
| report_example_full | 57 | 57 |

One note on `report_example_full.json`. It is a *full* Speakeasy report: a
dict with metadata and an `entry_points` list. The other four files are the
`entry_points` list itself. Passing the full dict to
`filter_and_normalize_report()` gives `{'apis': []}` = **1 token**, because
the filter finds no top-level fields. Passing `report["entry_points"]` gives
**57**, as expected. This is also what Nebula's own `emulate()` does
(`pe.py`: `self.filter_and_normalize_report(report["entry_points"])`). All
dataset files are plain lists, so this case never comes up in the dataset.

**Field order, checked in the code.** `joinRecordsToJSON()` loops over
`sorted(recordDict.keys(), reverse=True)` (`pe.py:147`). With the four field
keys this gives `registry_access` → `network_events.traffic` → `file_access`
→ `apis`, so `apis` is always last. I also checked this in the data: all
92,700 tokenized reports follow this order (table in §2.4).

**Per-field token attribution.** The tokenizer reads `str(report)`. I split
that string at the top-level `, '<key>':` boundaries, tokenized each piece
with the same `tokenizer.encode`, and **asserted** that the pieces' token
ids, joined together, equal the full report's token ids. This held for 100%
of samples (92,700 of 92,700). So the per-field counts are exact, not
estimates. A field's tokens include its own key name (for example
`file access`).

**Entry points.** Each entry point is tokenized alone with
`filter_and_normalize_report([ep])`. Chunk counts:
- **(a)** `ceil(tokens / 512)` on the whole report.
- **(b)** one chunk per entry point. An entry point over 512 tokens is split
  into 512-token pieces with 64-token overlap (stride 448), so it needs
  `1 + ceil((t-512)/448)` chunks.
- **(c)** an extra variant I added: like (b), but consecutive entry points
  shorter than 512 tokens are packed into one chunk.

### 1.2 Dataset and grouping key

`load_dataset("dtrizna/quovadis-speakeasy")` (streaming;
[log](results/logs/inspect_datasets.log)) shows:

- **Splits:** a single `train` split, built from 92,702 JSON files. The
  dataset's own train/test folders are **mixed together** in this view.
- **Columns** (first rows): `ep_type, start_addr, ep_args, apihash, apis,
  ret_val, error, network_events, dynamic_code_segments, file_access`.
  Features are reported as `None` (no fixed schema). Some raw entry points
  also have `registry_access`, `process_events`, `dropped_files` and
  `handled_exceptions` (key counts in the inspect log).
- **There is no label column and no sample-ID column.** Values are also
  type-coerced; for example `file_access` comes back as a list of JSON
  *strings*.
- **Row count:** 167,651 rows, by iterating the streaming view
  ([log](results/logs/datasets_stream_rowcount.log)). The non-streaming
  `load_dataset` **fails** with `DatasetGenerationError` (a pandas JSON parse
  error) ([log](results/logs/load_dataset_full.log)).
- Example rows 0 and 1 are printed in the
  [inspect log](results/logs/inspect_datasets.log). They are a
  `module_entry` and a `thread`.

**Grouping key = the source file path**
(`windows_emulation_{trainset,testset}/report_<family>/[<hex>/]<sha256>.json`).
The family label and the train/test split also come from this path. How I
checked it:

1. The dataset repository stores one JSON file per sample, and each file is a
   JSON **list of entry points**. That is 92,700 of 92,700 files; the
   dataset card says each file is a dict with `sha256` and `entry_points`,
   but no file has that form.
2. Adding up the entry points in all 92,700 sample files gives **167,548**.
   The two extra files at the repo root add the rest:
   `example-ransomware.json` (102 entry points) and `speakeasy-config.json`
   (an emulator config, which `datasets` turns into 1 row with no
   `ep_type`). 167,548 + 102 + 1 = **167,651**, exactly the `datasets` row
   count. The per-`ep_type` counts also match (module_entry +1, thread +101,
   None +1).
3. No column inside a row can serve as the key. `apihash` is a hash of one
   entry point's API sequence: only 6,699 distinct values exist, and 160,638
   entry points share theirs with another file.
4. No file stem (sha256) appears in more than one folder.
5. Nebula's own training pipeline (`read_and_filter_json_folders()` in
   `normalization.py`) also treats one file as one sample, takes the label
   from the folder name (`report_clean` and `report_windows_syswow64` are
   benign), and passes the whole file to `filter_and_normalize_report()`.

So I measured on the raw files (Git LFS clone of dataset revision
`fc2e98fac0b4d43a5557ccab70c877af6cce9f4d`) instead of on `datasets` rows.

### 1.3 Sample counts and what was skipped

| split    |    ok |
|:---------|------:|
| testset  | 17402 |
| trainset | 75298 |

Top-level JSON type of each file:

| split    |   list |
|:---------|-------:|
| testset  |  17402 |
| trainset |  75298 |

Samples measured (status ok): 92,700 of 92,700 files.

Field attribution exact (concatenated field token ids == full token ids): 100.0% (92,700)

- **Skipped:** 3 empty `.err` files (failed emulations). This is why the
  trainset has 75,298 samples, not the 75,301 in the dataset card's table.
  The two root-level example/config files were also left out.
- **Dropped by Nebula's filter** (`filter_and_normalize_report` returns
  `None`, the MSVBVM60 case): **0** samples.
- **No subsampling.** I first ran a pilot on 2,000 random files (seed 0;
  [tables](results/sample2000_tables.md)). The pilot gave the same median
  (1,069) and almost the same share above 512 (66.6% vs 66.0% on the full
  data).
  Then all 92,700 samples were measured: 21.8 min on 3 cores
  ([log](results/logs/measure_full.log)). Both splits are reported
  separately everywhere.

---

## 2. Results

### 2.1 Tokens per sample (no truncation)

| set | n | median | p75 | p90 | p99 | max | >512 | >1024 | >2048 | >4096 | >8192 | tokens dropped by 512 cut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 92,700 | 1,069 | 1,743 | 2,376 | 2,989 | 257,671 | 66.0% (61,207) | 50.5% (46,772) | 21.4% (19,833) | 0.2% (194) | 0.0% (22) | 66.6% (70,859,979 of 106,474,006) |
| testset | 17,402 | 1,026 | 1,877 | 2,277 | 2,794 | 5,255 | 63.5% (11,043) | 50.0% (8,707) | 22.2% (3,866) | 0.1% (12) | 0.0% (0) | 63.6% (11,799,879 of 18,562,891) |
| trainset | 75,298 | 1,069 | 1,733 | 2,386 | 2,991 | 257,671 | 66.6% (50,164) | 50.6% (38,065) | 21.2% (15,967) | 0.2% (182) | 0.0% (22) | 67.2% (59,060,100 of 87,911,115) |

Mean per-sample fraction of tokens dropped by the 512 cut: 40.5%; median per-sample fraction: 52.1%.

![token histogram](results/plots/hist_tokens.png)

![token CDF](results/plots/cdf_tokens.png)

### 2.2 By family and split

#### testset
| family | n | median | p75 | p90 | p99 | max | >512 | >1024 | >2048 | >4096 | >8192 | tokens dropped by 512 cut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| backdoor | 1,940 | 2,251 | 2,363 | 2,456 | 2,616 | 2,821 | 88.1% (1,709) | 70.7% (1,371) | 66.2% (1,285) | 0.0% (0) | 0.0% (0) | 73.8% (2,528,945 of 3,425,754) |
| clean | 7,944 | 1,048 | 1,632 | 2,269 | 2,705 | 5,255 | 56.6% (4,496) | 50.4% (4,003) | 16.1% (1,276) | 0.0% (2) | 0.0% (0) | 63.1% (4,867,784 of 7,719,845) |
| coinminer | 1,684 | 1,172 | 2,084 | 2,087 | 2,583 | 5,091 | 92.3% (1,554) | 65.0% (1,095) | 36.0% (607) | 0.1% (1) | 0.0% (0) | 65.2% (1,528,451 of 2,343,709) |
| dropper | 252 | 329 | 505 | 1,920 | 3,038 | 3,041 | 24.6% (62) | 19.8% (50) | 4.0% (10) | 0.0% (0) | 0.0% (0) | 49.5% (69,452 of 140,235) |
| keylogger | 1,041 | 372 | 382 | 1,132 | 2,306 | 2,778 | 17.1% (178) | 14.3% (149) | 3.7% (38) | 0.0% (0) | 0.0% (0) | 30.9% (153,519 of 496,710) |
| ransomware | 2,139 | 761 | 2,074 | 2,591 | 3,493 | 4,785 | 67.6% (1,445) | 41.1% (879) | 27.5% (589) | 0.2% (5) | 0.0% (0) | 67.3% (1,655,911 of 2,460,816) |
| rat | 1,258 | 1,169 | 1,172 | 1,347 | 2,388 | 2,849 | 90.8% (1,142) | 78.9% (993) | 2.8% (35) | 0.0% (0) | 0.0% (0) | 55.5% (742,835 of 1,338,242) |
| trojan | 1,085 | 402 | 758 | 1,355 | 2,254 | 4,534 | 41.8% (454) | 15.2% (165) | 2.4% (26) | 0.4% (4) | 0.0% (0) | 39.8% (250,537 of 629,583) |
| windows_syswow64 | 59 | 57 | 82 | 97 | 1,447 | 1,692 | 5.1% (3) | 3.4% (2) | 0.0% (0) | 0.0% (0) | 0.0% (0) | 30.6% (2,445 of 7,997) |

#### trainset
| family | n | median | p75 | p90 | p99 | max | >512 | >1024 | >2048 | >4096 | >8192 | tokens dropped by 512 cut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| backdoor | 11,061 | 2,310 | 2,471 | 2,605 | 2,627 | 18,829 | 95.3% (10,537) | 83.9% (9,284) | 74.5% (8,240) | 0.5% (53) | 0.0% (4) | 76.1% (17,368,352 of 22,835,992) |
| clean | 24,433 | 1,124 | 1,356 | 2,214 | 2,991 | 223,877 | 60.0% (14,654) | 53.6% (13,093) | 12.9% (3,152) | 0.3% (77) | 0.0% (2) | 63.2% (15,571,861 of 24,640,750) |
| coinminer | 6,891 | 1,216 | 1,610 | 2,178 | 3,033 | 6,890 | 93.8% (6,465) | 73.2% (5,044) | 12.6% (869) | 0.0% (1) | 0.0% (0) | 62.1% (5,602,736 of 9,017,842) |
| dropper | 8,243 | 123 | 1,069 | 1,632 | 3,006 | 4,028 | 38.5% (3,177) | 30.7% (2,534) | 5.9% (490) | 0.0% (0) | 0.0% (0) | 55.4% (2,637,622 of 4,764,278) |
| keylogger | 4,378 | 1,676 | 1,708 | 1,787 | 2,562 | 3,049 | 83.9% (3,673) | 79.2% (3,468) | 7.7% (336) | 0.0% (0) | 0.0% (0) | 66.3% (3,831,314 of 5,780,189) |
| ransomware | 9,627 | 949 | 950 | 1,160 | 3,673 | 257,671 | 56.5% (5,441) | 10.7% (1,034) | 7.4% (717) | 0.2% (21) | 0.2% (16) | 73.1% (7,706,821 of 10,545,466) |
| rat | 1,697 | 1,132 | 1,215 | 1,221 | 2,487 | 3,736 | 85.5% (1,451) | 52.4% (889) | 2.7% (46) | 0.0% (0) | 0.0% (0) | 53.3% (863,866 of 1,621,641) |
| trojan | 8,733 | 562 | 1,818 | 2,601 | 2,609 | 4,647 | 54.5% (4,762) | 31.1% (2,715) | 24.2% (2,116) | 0.3% (30) | 0.0% (0) | 63.0% (5,472,972 of 8,682,804) |
| windows_syswow64 | 235 | 57 | 85 | 101 | 1,313 | 2,054 | 1.7% (4) | 1.7% (4) | 0.4% (1) | 0.0% (0) | 0.0% (0) | 20.6% (4,556 of 22,153) |

![box per family](results/plots/box_family.png)

### 2.3 Malware vs benign

| split / class | n | median tokens | mean tokens | >512 | median entry points | median chunks (per-EP) |
|---|---|---|---|---|---|---|
| all / malware | 60,029 | 950 | 1,234 | 70.0% (42,050) | 1 | 3 |
| all / benign | 32,671 | 1,077 | 991 | 58.6% (19,157) | 1 | 3 |
| testset / malware | 9,399 | 1,028 | 1,153 | 69.6% (6,544) | 1 | 3 |
| testset / benign | 8,003 | 1,026 | 966 | 56.2% (4,499) | 1 | 3 |
| trainset / malware | 50,630 | 950 | 1,249 | 70.1% (35,506) | 1 | 3 |
| trainset / benign | 24,668 | 1,111 | 1,000 | 59.4% (14,658) | 1 | 3 |

ROC AUC of a classifier that uses ONLY the length (higher = malware); 0.5 = no signal:

| set | AUC(tokens) | AUC(min(tokens,512)) | AUC(n_entry_points) |
|---|---|---|---|
| all | 0.541 | 0.542 | 0.456 |
| testset | 0.567 | 0.574 | 0.487 |
| trainset | 0.535 | 0.535 | 0.448 |

Number of real (non-pad) tokens Nebula sees, min(tokens, 512):

| set | class | median | share of samples with < 512 real tokens (i.e. padded) |
|---|---|---|---|
| all | malware | 512 | 29.9% (17,977) |
| all | benign | 512 | 41.4% (13,514) |
| testset | malware | 512 | 30.4% (2,855) |
| testset | benign | 512 | 43.8% (3,504) |
| trainset | malware | 512 | 29.9% (15,122) |
| trainset | benign | 512 | 40.6% (10,010) |

#### Length as a shortcut, family by family
ROC AUC of raw token count for separating one family from `clean` (0.5 = no signal; values far from 0.5 in either direction mean length alone separates them).

| family | AUC trainset | AUC testset | AUC trainset, min(tokens,512) | AUC testset, min(tokens,512) |
|---|---|---|---|---|
| backdoor | 0.832 | 0.753 | 0.677 | 0.653 |
| coinminer | 0.617 | 0.645 | 0.673 | 0.678 |
| dropper | 0.325 | 0.377 | 0.361 | 0.375 |
| keylogger | 0.632 | 0.372 | 0.616 | 0.383 |
| ransomware | 0.309 | 0.530 | 0.401 | 0.528 |
| rat | 0.465 | 0.568 | 0.610 | 0.666 |
| trojan | 0.492 | 0.397 | 0.487 | 0.463 |
| windows_syswow64 | 0.162 | 0.195 | 0.162 | 0.198 |

### 2.4 Which fields survive the cut

Field order actually found in the tokenized reports (all distinct orders):

| field order (left = first in sequence) | samples |
|---|---|
| `apis` | 64,890 |
| `file_access|apis` | 17,691 |
| `registry_access|apis` | 7,206 |
| `registry_access|file_access|apis` | 2,216 |
| `network_events.traffic|file_access|apis` | 650 |
| `network_events.traffic|apis` | 24 |
| `registry_access|network_events.traffic|file_access|apis` | 17 |
| `registry_access|network_events.traffic|apis` | 6 |

| field | samples with field | tokens (all samples) | share of all tokens | median tokens (when present) | % of field tokens kept by 512 cut | samples where field fully kept | samples where field fully cut |
|---|---|---|---|---|---|---|---|
| registry_access | 10.2% (9,445) | 329,838 | 0.3% | 32 | 98.4% (324,485) | 100.0% (9,444) | 0.0% (0) |
| network_events.traffic | 0.8% (697) | 10,165 | 0.0% | 13 | 98.4% (10,005) | 99.4% (693) | 0.0% (0) |
| file_access | 22.2% (20,574) | 410,968 | 0.4% | 10 | 100.0% (410,968) | 100.0% (20,574) | 0.0% (0) |
| apis | 100.0% (92,700) | 105,723,035 | 99.3% | 1,069 | 33.0% (34,868,569) | 34.0% (31,493) | 0.0% (5) |

'samples where field fully kept / cut' are out of the samples that have the field. Field tokens include the field's own key name (e.g. `file access`).

Composition of the tokens Nebula actually keeps (sum over samples of the first ≤512 tokens):

| field | kept tokens | share of kept |
|---|---|---|
| registry_access | 324,485 | 0.9% |
| network_events.traffic | 10,005 | 0.0% |
| file_access | 410,968 | 1.2% |
| apis | 34,868,569 | 97.9% |

For the 61,207 samples longer than 512 tokens only:

| field | samples with field | % of field tokens kept | samples where field fully cut |
|---|---|---|---|
| registry_access | 10.6% (6,495) | 97.7% | 0.0% (0) |
| network_events.traffic | 1.1% (675) | 98.4% | 0.0% (0) |
| file_access | 30.0% (18,388) | 100.0% | 0.0% (0) |
| apis | 100.0% (61,207) | 30.2% | 0.0% (5) |

![field kept](results/plots/field_kept.png)

### 2.5 Entry points and chunking

Entry-point tokenization status:

| status   |   entry points |
|:---------|---------------:|
| ok       |         167548 |

| quantity | median | p75 | p90 | p99 | max | mean |
|---|---|---|---|---|---|---|
| entry points per sample | 1 | 1 | 1 | 5 | 102 | 1.8 |
| thread entry points per sample | 0 | 0 | 0 | 1 | 101 | 0.7 |
| tokens per entry point (tokenized alone) | 42 | 1,167 | 2,182 | 2,635 | 257,671 | 636.0 |
| tokens per module_entry | 993 | 1,712 | 2,368 | 2,957 | 257,671 | 1,128.0 |
| tokens per thread | 4 | 4 | 4 | 1,911 | 4,023 | 30.0 |
| sum of per-EP tokens per sample | 1,069 | 1,743 | 2,376 | 2,989 | 257,671 | 1,149.5 |
| chunks needed, (a) fixed 512 | 3 | 4 | 5 | 6 | 504 | 2.8 |
| chunks needed, (b) per-EP, 512/overlap 64 | 3 | 5 | 6 | 9 | 576 | 3.8 |

Samples with exactly one entry point: 94.7% (87,750); with more than one: 5.3% (4,950)

Sum over all samples of per-EP tokens = 106,554,960 vs whole-report tokens = 106,474,006 (+0.08%; tokenizing entry points separately repeats the field key names).

Entry points longer than 512 tokens: 36.6% (61,389) (module_entry: 65.3% (60,518); thread: 1.3% (863))

Samples with at least one entry point longer than 512 tokens: 66.0% (61,202)

Entry-point counts by family (all splits):

| family | samples | median EPs | p90 EPs | max EPs | samples with >1 EP |
|---|---|---|---|---|---|
| backdoor | 13,001 | 1 | 1 | 102 | 0.5% (67) |
| clean | 32,377 | 1 | 2 | 5 | 11.2% (3,629) |
| coinminer | 8,575 | 1 | 1 | 11 | 3.1% (270) |
| dropper | 8,495 | 1 | 1 | 5 | 0.8% (66) |
| keylogger | 5,419 | 1 | 1 | 4 | 1.4% (76) |
| ransomware | 11,766 | 1 | 1 | 102 | 6.1% (720) |
| rat | 2,955 | 1 | 1 | 4 | 0.3% (8) |
| trojan | 9,818 | 1 | 1 | 5 | 1.2% (113) |
| windows_syswow64 | 294 | 1 | 1 | 2 | 0.3% (1) |

Share of samples that fit within a given number of 512-token chunks:

| set | scheme | ≤8 chunks | ≤16 chunks | ≤32 chunks | ≤64 chunks |
|---|---|---|---|---|---|
| all | (a) fixed 512 | 99.8% (92,506) | 100.0% (92,678) | 100.0% (92,679) | 100.0% (92,683) |
| all | (b) per entry point | 98.9% (91,672) | 99.3% (92,027) | 99.3% (92,031) | 99.3% (92,031) |
| testset | (a) fixed 512 | 99.9% (17,390) | 100.0% (17,402) | 100.0% (17,402) | 100.0% (17,402) |
| testset | (b) per entry point | 97.4% (16,951) | 97.7% (16,994) | 97.7% (16,994) | 97.7% (16,994) |
| trainset | (a) fixed 512 | 99.8% (75,116) | 100.0% (75,276) | 100.0% (75,277) | 100.0% (75,281) |
| trainset | (b) per entry point | 99.2% (74,721) | 99.6% (75,033) | 99.7% (75,037) | 99.7% (75,037) |

Coverage if the model only reads the first K chunks (share of all tokens covered):

| scheme | K=1 (=Nebula) | K=4 | K=8 | K=16 | K=32 | K=64 |
|---|---|---|---|---|---|---|
| (a) fixed 512 | 33.4% | 88.7% | 95.9% | 96.1% | 96.3% | 96.5% |
| (b) per entry point | 31.9% | 83.8% | 95.5% | 95.9% | 96.0% | 96.4% |

(b) coverage is measured on the sum of per-EP tokens, in entry-point order; overlap tokens are not double counted.

Chunks needed by family (all splits):

| family | median (a) | p90 (a) | median (b) | p90 (b) | (b) ≤32 chunks |
|---|---|---|---|---|---|
| backdoor | 5 | 6 | 5 | 6 | 100.0% (12,997) |
| clean | 3 | 5 | 3 | 5 | 100.0% (32,376) |
| coinminer | 3 | 5 | 3 | 5 | 100.0% (8,575) |
| dropper | 1 | 4 | 1 | 4 | 100.0% (8,495) |
| keylogger | 3 | 4 | 3 | 4 | 100.0% (5,419) |
| ransomware | 2 | 5 | 2 | 5 | 94.4% (11,102) |
| rat | 3 | 3 | 3 | 3 | 100.0% (2,955) |
| trojan | 2 | 6 | 2 | 6 | 100.0% (9,818) |
| windows_syswow64 | 1 | 1 | 1 | 1 | 100.0% (294) |

#### Extra variant (c): packing small entry points
Same as (b), but consecutive entry points shorter than 512 tokens share one 512-token chunk (an entry point is never split unless it is longer than 512 tokens).

| set | median | p90 | p99 | max | ≤8 chunks | ≤16 chunks | ≤32 chunks | ≤64 chunks |
|---|---|---|---|---|---|---|---|---|
| all | 3 | 6 | 7 | 576 | 99.6% (92,344) | 100.0% (92,676) | 100.0% (92,679) | 100.0% (92,683) |
| testset | 3 | 5 | 7 | 13 | 99.8% (17,364) | 100.0% (17,402) | 100.0% (17,402) | 100.0% (17,402) |
| trainset | 3 | 6 | 7 | 576 | 99.6% (74,980) | 100.0% (75,274) | 100.0% (75,277) | 100.0% (75,281) |

#### What the extra entry points contain
- thread entry points: 66,704; with exactly 1 API call: 97.0% (64,678); with ≤4 tokens: 96.8% (64,601)
- samples with more than 64 entry points: 0.7% (652); their entry-point counts: {102: 652}; by split/family: {('testset', 'ransomware'): 408, ('trainset', 'backdoor'): 4, ('trainset', 'ransomware'): 240}
- samples longer than 8,192 tokens: 22, holding 4.1% of all tokens; by family: {'ransomware': 16, 'backdoor': 4, 'clean': 2}; raw API calls in them: median 36,906

![chunks](results/plots/hist_chunks.png)

### 2.6 The emulator already truncated the reports

| set | samples that hit the API cap | median tokens (hit cap) | median tokens (no cap) | median raw API calls |
|---|---|---|---|---|
| all | 18.7% (17,327) | 2,364 | 798 | 180 |
| backdoor | 66.7% (8,675) | 2,372 | 848 | 499 |
| clean | 10.3% (3,333) | 2,292 | 767 | 179 |
| coinminer | 24.2% (2,079) | 1,614 | 1,198 | 239 |
| dropper | 3.1% (264) | 2,340 | 118 | 21 |
| keylogger | 0.9% (49) | 2,406 | 1,216 | 225 |
| ransomware | 5.5% (653) | 2,218 | 949 | 180 |
| rat | 0.9% (28) | 2,314 | 1,168 | 214 |
| trojan | 22.9% (2,246) | 2,599 | 402 | 93 |
| windows_syswow64 | 0.0% (0) | – | 57 | 8 |

Of the samples longer than 512 tokens, 28.0% (17,131) hit the emulation cap.

Tokens per raw API call (entry points with ≥1 API call): median 4.78, p10 4.00, p90 7.09. Entry points with ≥500 API calls: 6.3% (10,568).

Entry points whose `error.type` is `max_api_count`: 17,722; of these, 41.1% (7,276) have fewer than 500 API calls (the counter looks shared across a sample's entry points).

---

## 3. The five most important findings

1. **Most samples are cut, and most of the data is lost.** 66.0% of samples
   (61,207 of 92,700) are longer than 512 tokens. The median sample has
   1,069 tokens and loses 52.1% of them. Across the whole dataset the 512 cut
   throws away **66.6% of all tokens** (70,859,979 of 106,474,006). Train
   (67.2%) and test (63.6%) look the same.

2. **What is lost is almost only API calls. The other fields are always
   kept.** `joinRecordsToJSON()` puts `apis` last. API calls are 99.3% of
   all tokens, and only **33.0%** of API tokens survive the cut (30.2% for
   samples longer than 512). File, registry and network events come first,
   are small (medians 10, 32 and 13 tokens), and survive almost entirely
   (100.0%, 98.4%, 98.4%). Of what Nebula keeps, 97.9% is still API calls.
   An API call costs about 4.8 tokens (median 4.78), so the 512 window holds
   roughly the first ~100 API calls of a trace that can be up to 500 long.
   So your suspicion is correct: the cut removes the tail of the API
   sequence.

3. **The reports are long, but not very long, because the emulator stopped
   them.** The dataset's Speakeasy config sets `max_api_count = 500`. 18.7%
   of samples (17,327) hit this cap, and those samples have a median of
   2,364 tokens versus 798 for the rest. Because of the cap the tail is
   short: p99 is 2,989 tokens, only 0.2% (194) are above 4,096, and 99.8%
   (92,506) fit in eight 512-token chunks. The exceptions are 22 samples
   above 8,192 tokens (16 ransomware, 4 backdoor, 2 clean; median 36,906 API
   calls). They are only 0.02% of samples but hold 4.1% of all tokens. Many
   of them look like near-duplicates (same family, same size to within a few
   tokens).

4. **The "process / entry point" structure is thin.** 94.7% of samples
   (87,750) have exactly one entry point, the `module_entry`. Thread entry
   points are almost all trivial: 97.0% (64,678 of 66,704) contain exactly
   **one** API call (4 tokens, median). The long content sits inside the
   single `module_entry` (median 993 tokens; 65.3% are above 512). Only 1.3%
   of threads (863) are longer than 512. Scheme (b), one chunk per entry
   point, therefore wastes chunks. 652 samples (648 ransomware and 4
   backdoor) have exactly 102 entry points, and so need 102+ chunks under
   (b) but at most 13 when small entry points are packed (variant (c), test
   set max).

5. **Length is a weak malware-vs-benign signal, but a strong and unstable
   family signal.** Overall, malware has a *lower* median length than benign
   (950 vs 1,077). A classifier using only length gets ROC AUC 0.541 (test
   0.567), close to chance. But family by family, length separates a lot:
   backdoor vs clean AUC is 0.832 (train) / 0.753 (test). It also *drifts*
   between the January and April collections: keylogger vs clean goes from
   0.632 on train to 0.372 on test (median keylogger length 1,676 → 372).
   Nebula already sees part of this signal through padding: 41.4% of benign
   samples vs 29.9% of malware have fewer than 512 real tokens. A model that
   reads the whole report sees more length information than Nebula does.
   For backdoor vs clean, AUC is 0.677 on the truncated length versus 0.832
   on the full length (train).

---

## 4. Implications for the chunking idea

**Does the data support it?**

- **Yes, for reading past 512 tokens.** Two thirds of the API sequence,
  which is the main signal, is never seen today. A model that reads the
  rest has a lot of unused data to work with.
- **Only weakly, for using entry points / processes as the chunk unit.**
  In this dataset, 94.7% of samples have a single entry point. For them a
  "two-level model over entry points" is the same as a two-level model over
  fixed-size pieces of one API sequence. The extra entry points are almost
  all one-API-call threads. I would describe the idea as **a hierarchical
  Transformer over 512-token chunks of the report**, and use entry-point
  boundaries as extra information (for example a segment or
  entry-point-type embedding, or packing as in variant (c)). I would not use
  them as the main unit. One chunk per entry point (scheme (b)) is the worst
  option: it needs 102+ chunks for 652 samples that hold little content.

**Suggested settings**

| setting | suggestion | why (measured) |
|---|---|---|
| chunk size | **512 tokens** | Same as Nebula, so its pretrained encoder and tokenizer can be reused for the first level. |
| max chunks | **8** (= 4,096 tokens) | (a) covers 99.8% of samples completely (92,506) and 95.9% of all tokens; (c) covers 99.6% (92,344). Going to 16 adds almost nothing: 100.0% of samples, 96.1% of tokens. The tokens still missing are in the 22 outlier samples. |
| chunking scheme | fixed 512 (a), or entry-point-aware with packing (c) | (a) and (c) need the same median (3) and p90 (5 and 6) number of chunks. (b) has a p99 of 9 and a max of 576 chunks. |
| overlap | 64 if splitting inside an API sequence | Cheap: (c) still keeps 99.6% of samples within 8 chunks. |
| outliers | cap or remove the 22 samples > 8,192 tokens (and check them for duplicates) | They hold 4.1% of all tokens and would dominate any per-token loss. |

**Things to plan for before pitching**

- **A flat long-context baseline is necessary.** Because 99.8% of samples
  fit in 4,096 tokens, the obvious competitor is a plain Transformer (or
  Nebula itself) with `seq_len` 2,048 or 4,096, possibly with efficient
  attention. The hierarchical model's main advantage over it is cost: 8
  chunks of 512² attention is 1/8 of the attention work of one 4,096²
  sequence. The pitch should show either better accuracy at the same cost,
  or the same accuracy at lower cost.
- **Control for length.** Report results per family, and add a length-only
  baseline (the AUC table in §2.3 is a starting point). Consider evaluating
  on length-matched subsets, so a gain from reading more tokens is not just
  a gain from seeing the length.
- **The gain has a ceiling set by emulation.** With `max_api_count = 500`,
  even a perfect long-context model only sees about 6× more data than
  Nebula (p99 2,989 tokens). Re-emulating with a higher cap would make the
  long-context argument stronger, but that is a separate data effort.

---

## 5. Caveats

- **This dataset, this preprocessing.** All numbers are for
  quovadis-speakeasy with the field list, record limits and 50k BPE
  tokenizer in the Nebula repository at the commit above. A different field
  set or vocabulary would change the absolute lengths. The paper's ablations
  may have used other settings.
- **The reports are already cut by the emulator** (`max_api_count = 500`,
  60 s timeout). The lengths here describe this dataset, not real program
  behaviour. 28.0% of the samples longer than 512 tokens (17,131) hit the
  cap. Some entry points carry the `max_api_count` error with fewer than 500
  calls (count in §2.6), so the counter seems to be shared across a
  sample's entry points.
  Also, 16 ransomware samples went far past the cap (36,906 calls); I did
  not investigate why.
- **Labels and splits come from folder names**, as in Nebula's own pipeline.
  `report_windows_syswow64` (294 samples) counts as benign.
- **Entry points tokenized alone** add up to 0.08% more tokens than the
  whole report, because each one repeats the field key names. Chunk counts
  for (b) and (c) use these per-entry-point tokens.
- **Chunk counts are a simulation** of how many 512-token pieces each scheme
  needs. They say nothing about model accuracy.
- **Near-duplicates were not removed.** The 22 longest samples look like
  repeated variants of a few programs. Results that weight every token (the
  "share of tokens dropped") are affected by them. Results that weight every
  sample (medians, percentages of samples) are not much affected.
- **The `datasets` library view** was used only for the schema and the row
  count. The full non-streaming `load_dataset` fails on this repository (log
  linked in §1.2). All measurements use the raw JSON files at the same
  dataset revision, which is also how Nebula's own preprocessing reads them.
