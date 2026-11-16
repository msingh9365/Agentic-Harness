"""
Load any model of this baseline reproduction and score a Speakeasy report.

    from baseline_models.load_baseline import load_baseline, list_baselines
    list_baselines()                                   # keys in manifest.json
    m = load_baseline("detect/bpe50k/time/fold0")      # the authors' cleaning + tokenizer + our trained Nebula weights
    p = m.score(report)                                # report: list of entry points (or a path to the .json); -> P(malware)
    m = load_baseline("ssl/ar_pretrained/seed0")       # AR-pretrained encoder with its LM head (no classifier)
    m.next_token_logits(report)                        # [512, V] next-token logits

Everything that cleans, tokenizes and runs the model is the authors' code (third_party/nebula at the pinned commit, with the patches
in patches/ applied); this file only wires the saved weights to it. Weights that are too big for git are in the private Kaggle dataset
named in README.md; point NEBULA_BASELINE_MODELS (or `root=`) at the folder that holds them.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)


def _roots(root=None):
    cands = [root, os.environ.get("NEBULA_BASELINE_MODELS"), HERE]
    for dp, dn, fn in os.walk("/kaggle/input") if os.path.isdir("/kaggle/input") else []:
        if "manifest.json" in fn and "baseline" in dp:
            cands.append(dp)
        if dp.count(os.sep) > 6:
            dn[:] = []
    return [c for c in cands if c]


def _manifest(root=None):
    for r in _roots(root):
        p = os.path.join(r, "manifest.json")
        if os.path.exists(p):
            return json.load(open(p)), r
    raise FileNotFoundError("manifest.json not found; set NEBULA_BASELINE_MODELS to the models folder")


def list_baselines(root=None):
    return sorted(_manifest(root)[0]["models"])


class Baseline:
    def __init__(self, key, entry, root, nebula_root=None):
        from baseline import common as C
        C.setup_nebula(nebula_root)
        import torch
        from nebula.preprocessing import JSONTokenizerBPE, JSONTokenizerNaive, PEDynamicFeatureExtractor
        self.key, self.entry, self.root, self.torch = key, entry, root, torch
        tk = entry["tokenizer"]
        tdir = os.path.join(root, "tokenizers", tk)
        vocab_file = os.path.join(tdir, "vocab.json")
        n = len(json.load(open(vocab_file)))
        seq = entry.get("seq_len", 512)
        self.extractor = PEDynamicFeatureExtractor()
        if os.path.exists(os.path.join(tdir, "tokenizer.model")):
            self.tokenizer = JSONTokenizerBPE(vocab_size=n, seq_len=seq, vocab=vocab_file, model_path=os.path.join(tdir, "tokenizer.model"))
        else:
            self.tokenizer = JSONTokenizerNaive(vocab_size=n, seq_len=seq, vocab=vocab_file)
        self.model = self._build(entry, n)
        wp = os.path.join(root, entry["weights"])
        self.model.load_state_dict(torch.load(wp, map_location="cpu", weights_only=True))
        self.model.eval()

    @staticmethod
    def _build(entry, n):
        from baseline import cv, lm
        arch = entry["arch"]
        if arch == "chunked":
            from nebula.models.attention import TransformerEncoderChunks
            return TransformerEncoderChunks(**entry["model_config"]) if "model_config" in entry else \
                TransformerEncoderChunks(**cv.model_config(n, n_classes=entry.get("n_classes", 1)))
        if arch == "chunked_mlm_bert":
            return lm.build_chunked(n, 0.0, pooling=None, pretrain_layers=[])
        if arch == "fullattn":
            return lm.build_fullattn(n, 0.3, causal=False)
        if arch == "fullattn_causal_lasttoken":
            return lm.build_fullattn(n, 0.3, causal=True, last_token=True)
        if arch == "ar_pretrained":
            return lm.build_fullattn(n, 0.0, causal=True, pretrain_layers=[])
        raise ValueError(arch)

    def tokenize(self, report):
        if isinstance(report, str) and os.path.exists(report):
            report = json.load(open(report))
        if isinstance(report, dict) and "entry_points" in report:
            report = report["entry_points"]
        filtered = self.extractor.filter_and_normalize_report(report)
        return np.asarray(self.tokenizer.encode(filtered, pad=True)).reshape(-1)[:self.entry.get("seq_len", 512)]

    def score(self, report):
        """P(malware) for a detection model; class probabilities for a classification model."""
        x = self.torch.from_numpy(self.tokenize(report)[None].astype(np.int64))
        with self.torch.no_grad():
            out = self.model(x)
        if self.entry.get("n_classes", 1) == 1:
            return float(self.torch.sigmoid(out).item())
        return self.torch.softmax(out, -1)[0].numpy()

    def score_many(self, reports):
        return [self.score(r) for r in reports]

    def next_token_logits(self, report):
        x = self.torch.from_numpy(self.tokenize(report)[None].astype(np.int64))
        with self.torch.no_grad():
            return self.model.pretrain(x)[0].numpy()


def load_baseline(key, root=None, nebula_root=None):
    man, r = _manifest(root)
    if key not in man["models"]:
        raise KeyError(f"{key} not in manifest; available: {sorted(man['models'])[:8]} ...")
    return Baseline(key, man["models"][key], r, nebula_root)
