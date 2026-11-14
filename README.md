# Nebula sequence-length study

This study measures how much of each Speakeasy behaviour report is thrown away
by Nebula's 512-token cut (Trizna et al., IEEE TIFS 2024). The findings are in
[REPORT.md](REPORT.md).

Everything runs through **Nebula's own preprocessing code**, imported from a
clone of the Nebula repository. Nothing is re-implemented.

## Versions used

| thing | version |
|---|---|
| Nebula | `https://github.com/dtrizna/nebula` at commit `1343ae170ef32b01a75d2dd5fb906b5541f073df` (2026-10-08) |
| Dataset | `dtrizna/quovadis-speakeasy` on Hugging Face, revision `fc2e98fac0b4d43a5557ccab70c877af6cce9f4d` |
| Python | 3.11 (the system Python 3.13 could not build `lznt1`, a dependency of `speakeasy-emulator`) |
| Tokenizer | `nebula/objects/bpe_50000_sentencepiece.model` + `bpe_50000_vocab.json` |

The full list of package versions is in [requirements-freeze.txt](requirements-freeze.txt).

## Folder layout

```
measure_lengths.py   measurement (sanity check, dataset inspection, per-sample CSVs)
analyze.py           tables (results/tables.md), summary.json and plots
build_report.py      builds REPORT.md from REPORT.src.md + results/tables.md
make_examples.py     copies 21 example samples into examples/ (raw, filtered, tokens)
measure_avast.py     Avast-CTU length study (tokenizer training + measurement)
analyze_avast.py     Avast tables, plots and the Speakeasy comparison
make_avast_examples.py  copies 20 Avast example reports into examples/avast/
hier_nebula/         two-level Nebula: 512-token chunks + second-level Transformer
gpu/                 setup + experiment sweep for a GPU server, with step-by-step instructions
measure_links.py     data-flow links between API calls and chunk boundaries (REPORT.md §8)
analyze_links.py     tables and plot for the link study
analyze_misses.py    why April ransomware/coinminer are missed (REPORT.md §9); `collect` then `analyze`
analyze_signal.py    where the signal is: baselines, prefix curve, ablations, attribution, drift, links (REPORT.md §10)
signal_lib.py        helpers for analyze_signal.py
examples/            the example samples, with their own README explaining the data
results/             CSVs, tables.md, summary.json, pilot (sample2000_*) outputs
results/logs/        console output of every run
results/plots/       PNG plots used in REPORT.md
REPORT.src.md        report text with include markers for the tables
REPORT.md            the write-up (generated; edit REPORT.src.md)
```

The dataset, the Nebula clone and the Python environment all live **outside**
this folder and are not committed (see `.gitignore`). The one exception is
`examples/`: 21 sample reports (about 2.4 MB) copied on purpose so the data
can be inspected without downloading 5.5 GB. See
[examples/README.md](examples/README.md).

## How to rerun

```bash
# 0. side-by-side folders:  ./this-repo  ../nebula  ../hf-git
git clone https://github.com/dtrizna/nebula ../nebula
git -C ../nebula checkout 1343ae170ef32b01a75d2dd5fb906b5541f073df

# 1. environment (Python 3.11; PyTorch is NOT needed)
uv venv -p 3.11 ../nebula-venv && source ../nebula-venv/bin/activate
uv pip install sentencepiece pandas speakeasy-emulator nltk orjson tqdm datasets \
               matplotlib lief "setuptools<70" tabulate
#  setuptools<70 is needed because unicorn 1.0.2 (pulled in by speakeasy) imports pkg_resources

# 2. sanity check against the example reports in ../nebula/emulation/
python measure_lengths.py --nebula ../nebula sanity

# 3. download the raw dataset (5.5 GB, 92,702 JSON files). Git LFS is much faster
#    than snapshot_download for this many small files.
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/datasets/dtrizna/quovadis-speakeasy ../hf-git
git -C ../hf-git checkout fc2e98fac0b4d43a5557ccab70c877af6cce9f4d
git -C ../hf-git lfs pull

# 4. look at the dataset the way `datasets` sees it, and check the grouping key
python measure_lengths.py --nebula ../nebula inspect --data-dir ../hf-git

# 5. pilot on 2,000 random samples, then the full dataset
python measure_lengths.py --nebula ../nebula measure --data-dir ../hf-git \
       --out results --prefix sample2000_ --limit 2000 --seed 0
python analyze.py --results results --prefix sample2000_
python measure_lengths.py --nebula ../nebula measure --data-dir ../hf-git --out results
python analyze.py --results results
python build_report.py            # pastes the tables into REPORT.md
python make_examples.py --nebula ../nebula --data-dir ../hf-git   # examples/
```

### Avast-CTU Public CAPEv2 (REPORT.md §6)

```bash
pip install gdown
git clone https://github.com/avast/avast-ctu-cape-dataset   # README with the download links (commit b4210e5)
mkdir -p ../avast/data && cd ../avast/data
gdown 1xujiSqV0sUv4GinS2xq8XFRpZLvvs1um -O reduced.zip      # "reduced reports", 593 MB zip
unzip reduced.zip -x "__MACOSX/*" && unzip public_small_reports.zip && rm *.zip   # 11 GB of JSON
cd -
python measure_avast.py --data-dir ../avast/data train       # Avast BPE tokenizers (variants A and B)
python measure_avast.py --data-dir ../avast/data measure     # results/avast/samples.csv (~15 min on 4 cores)
python analyze_avast.py                                      # results/avast/tables.md + plots
python make_avast_examples.py --data-dir ../avast/data       # examples/avast/
python build_report.py
```

The trained Avast tokenizers are committed in `results/avast/tokenizer/`, so
`train` can be skipped.

### Data-flow links and missed reports (REPORT.md §8–9)

```bash
python measure_links.py sanity && python measure_links.py measure --data-dir ../hf-git && python analyze_links.py
pip install rapidfuzz
python analyze_misses.py collect      # one pass over all reports (~8 min on 4 cores); API sequences go to ../hier_data/misses
python analyze_misses.py analyze      # needs ../hier_data/speakeasy/meta.csv (hier_nebula prepare) and results/hier/*/test_scores.csv
python build_report.py
```

### Where the signal is (REPORT.md §10)

CPU only. Needs CPU PyTorch (`pip install torch --index-url https://download.pytorch.org/whl/cpu`) and
`lightgbm scikit-learn`, plus `results/hier/data/` (committed).

```bash
python analyze_signal.py split        # grouped January validation split -> results/signal/val_split.csv
python analyze_signal.py collect      # one pass over the raw reports (~15 min on 4 cores); big files go to ../hier_data/signal
python analyze_signal.py baselines    # analysis 1
python analyze_signal.py drift        # analysis 5 (needs baselines)
python analyze_signal.py links        # analysis 6
python analyze_signal.py prefix       # analysis 2
python analyze_signal.py ablate       # analysis 3
python analyze_signal.py attrib       # analysis 4
python build_report.py
```

Each step writes `results/signal/parts/<step>.md` and rebuilds `results/signal/tables.md`.
Per-report scores of every new model are in `results/signal/scores/`.

### Two-level model

See [hier_nebula/README.md](hier_nebula/README.md).

`analyze.py` always writes `results/plots/`, so run the pilot `analyze.py`
before the full one (or move its output), as above.

`measure` uses all CPU cores by default (`--workers N` changes this).

## How Nebula is imported without torch / lief

`nebula/__init__.py` imports torch, and `nebula/misc/__init__.py` imports torch
and sklearn. `measure_lengths.py` avoids both. It registers empty package
modules for `nebula`, `nebula.preprocessing` and `nebula.models` in
`sys.modules`, with `__path__` pointing at the source folders. It stubs
`nebula.models.ember` (`PEFeatureExtractor = object`). It also builds
`nebula.misc` with only `get_alphanum_chars()`, read word for word from
`nebula/misc/__init__.py` with `ast`. After that, the real
`nebula.constants`, `nebula.preprocessing.tokenization` and
`nebula.preprocessing.pe` modules are imported unchanged. (`lief` and
`speakeasy` are installed because `pe.py` imports them at the top.)

## Output files

| file | content |
|---|---|
| `results/samples.csv` | one row per sample: split, family, label, total tokens, tokens per field and how many are kept in the first 512, entry-point counts, chunks needed |
| `results/entry_points.csv` | one row per entry point: type, tokens when tokenized alone, chunks, raw API-call count, emulator error type |
| `results/tables.md` | every table in REPORT.md, generated by `analyze.py` |
| `results/summary.json` | a few headline numbers in machine-readable form |
| `results/sample2000_*` | the 2,000-sample pilot (CSV + tables) |
| `results/logs/` | console output of the runs (sanity, inspect, `datasets` load attempts, measure) |

Both full CSVs are under 50 MB (about 16 MB and 22 MB), so they are committed
uncompressed. `pandas.read_csv` works on them directly.
