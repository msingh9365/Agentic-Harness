"""Our preprocessing driver must give exactly what the authors' wrapper preprocess_nebula_speakeasy() gives.
Needs a small sample (baseline/tests/make_sample.py); set NEBULA_SAMPLE to its folder, or NEBULA_HF to the dataset."""
import os
import shutil
import tempfile

import numpy as np
import pytest

from baseline import common as C, preprocess as P
from baseline.tests.make_sample import make_sample

INFO = C.setup_nebula()


@pytest.fixture(scope="module")
def sample(tmp_path_factory):
    s = os.environ.get("NEBULA_SAMPLE")
    if not s:
        hf = os.environ.get("NEBULA_HF", os.path.join(C.REPO_ROOT, "..", "hf-git"))
        if not os.path.isdir(hf):
            pytest.skip("no sample and no dataset")
        s = make_sample(hf, str(tmp_path_factory.mktemp("sample")), 12)
    return s


@pytest.fixture()
def sorted_listdir(monkeypatch):
    """Make os.listdir deterministic for both pipelines (their reader enumerates directories with os.listdir)."""
    orig = os.listdir
    monkeypatch.setattr(os, "listdir", lambda p=".": sorted(orig(p)))


@pytest.mark.parametrize("kind", ["bpe", "whitespace"])
def test_driver_equals_their_wrapper(sample, sorted_listdir, kind, tmp_path, monkeypatch):
    from nebula.preprocessing.wrappers import preprocess_nebula_speakeasy
    V = 400
    train, test = (os.path.join(sample, f"windows_emulation_{s}set") for s in ["train", "test"])
    # --- theirs
    A = str(tmp_path / "theirs")
    xa, ya, pa = preprocess_nebula_speakeasy(train, outfolder=A, vocab_size=V, seq_len=512, tokenizer_type=kind)
    tm = os.path.join(A, f"tokenizer_{V}.model") if kind == "bpe" else os.path.join(A, f"tokenizer_{V}_vocab.json")
    xta, yta, pta = preprocess_nebula_speakeasy(test, outfolder=A, tokenizer_model=tm, vocab_size=V, seq_len=512, tokenizer_type=kind)
    # --- ours
    B = str(tmp_path / "ours")
    monkeypatch.setitem(P.VARIANTS, "t", dict(kind=kind, vocab=V, seq=512))
    ev_tr, ym_tr, n_tr = P.filter_split(train, INFO["nebula_root"], workers=2)
    ev_te, ym_te, n_te = P.filter_split(test, INFO["nebula_root"], workers=2)
    P.run_variant("t", ev_tr, ev_te, B, INFO["nebula_root"])
    xb, xtb = (np.load(os.path.join(B, "variants", "t", f)) for f in ["x_train.npy", "x_test.npy"])
    assert xa.shape == xb.shape and xta.shape == xtb.shape
    assert [os.path.basename(p) for p in pa] == [os.path.basename(p) for p in n_tr]       # same rows in the same order
    assert (xa == xb).all() and (xta == xtb).all(), "token arrays differ from the authors' wrapper"
    assert (ya == (ym_tr > 0)).all() and (yta == (ym_te > 0)).all(), "labels differ"
    if kind == "bpe":
        import sentencepiece as spm   # the .model file embeds the training paths, so compare what it encodes
        ma = spm.SentencePieceProcessor(model_file=os.path.join(A, f"tokenizer_{V}.model"))
        mb = spm.SentencePieceProcessor(model_file=os.path.join(B, "variants", "t", "tokenizer.model"))
        assert [(ma.id_to_piece(i), ma.get_score(i)) for i in range(ma.get_piece_size())] == \
               [(mb.id_to_piece(i), mb.get_score(i)) for i in range(mb.get_piece_size())]


def test_released_tokenizer_matches_nebula_class(sample):
    """Our 'released' variant must give what their Nebula class gives for the same report."""
    import json
    from nebula import Nebula
    neb = Nebula(vocab_size=50000, seq_len=512, tokenizer="bpe")
    folder = os.path.join(sample, "windows_emulation_testset", "report_backdoor")
    f = os.path.join(folder, sorted(os.listdir(folder))[0])
    ep = json.load(open(f))
    theirs = neb.preprocess(ep)
    spec = P.VARIANTS["released_bpe50k"]
    tok = P.build_tokenizer(spec, INFO["nebula_root"])
    rep = neb.dynamic_extractor.filter_and_normalize_report(ep)
    ours = tok.encode(rep)
    assert (np.asarray(theirs).reshape(-1)[:512] == np.asarray(ours).reshape(-1)[:512]).all()


def test_splits_are_stratified_and_disjoint():
    rng = np.random.default_rng(0)
    ym = rng.integers(0, 8, 2000).astype(np.int8)
    sp = P.make_splits((ym > 0).astype(np.int8), ym)
    for s in sp["ssl_80_20_stratified_by_family"].values():
        u, l = set(s["unlabeled"]), set(s["labeled"])
        assert not (u & l) and len(u | l) == 2000 and abs(len(u) / 2000 - 0.8) < 0.01
        for c in range(8):    # every class keeps its 80/20 ratio
            nc = (ym == c).sum()
            assert abs(sum(ym[i] == c for i in u) / nc - 0.8) < 0.02
    for f in sp["kfold3"]:
        assert not (set(f["train"]) & set(f["val"])) and len(f["train"]) + len(f["val"]) == 2000


def test_reused_tokenizer_and_other_sequence_lengths(sample, sorted_listdir, tmp_path, monkeypatch):
    """--reuse must give the same arrays as the trained tokenizer, and a shorter sequence length is the 512-token array cut."""
    V = 400
    train, test = (os.path.join(sample, f"windows_emulation_{s}set") for s in ["train", "test"])
    monkeypatch.setitem(P.VARIANTS, "t", dict(kind="bpe", vocab=V, seq=512))
    ev_tr, _, _ = P.filter_split(train, INFO["nebula_root"], workers=2)
    ev_te, _, _ = P.filter_split(test, INFO["nebula_root"], workers=2)
    A, B = str(tmp_path / "a"), str(tmp_path / "b")
    P.run_variant("t", ev_tr, ev_te, A, INFO["nebula_root"])
    P.run_variant("t", ev_tr, ev_te, B, INFO["nebula_root"], seq_lens=(64, 128, 1024), reuse_dir=A)
    a, b = (os.path.join(d, "variants", "t") for d in (A, B))
    assert (np.load(a + "/x_train.npy") == np.load(b + "/x_train.npy")).all()
    x512 = np.load(b + "/x_train.npy")
    for n in (64, 128):
        assert (np.load(b + f"/x_train_len{n}.npy") == x512[:, :n]).all()
    x1024 = np.load(b + "/x_train_len1024.npy")
    assert x1024.shape[1] == 1024 and (x1024[:, :512] == x512).all()


def test_legacy_whitespace_cleaning_matches_the_released_vocabulary_conventions():
    """The released Whitespace vocabulary has 'apiname', 'retval', 'kernel32getprocaddress' and keeps 'args', 'event', 'path'
    (punctuation deleted, stopwords kept). The pinned repo's tokenizer produces 'api name' ... 'kernel32 getprocaddress'."""
    import json
    spec = P.VARIANTS["released_ws50k_legacy"]
    legacy = P.build_tokenizer(spec, INFO["nebula_root"])
    pinned = P.build_tokenizer(P.VARIANTS["released_ws50k"], INFO["nebula_root"])
    rep = {"file_access": [{"event": "open", "path": "<drive>\\windows\\x.dll"}],
           "apis": [{"api_name": "KERNEL32.GetProcAddress", "args": ["0x0"], "ret_val": "0x10"}]}
    tl, tp = legacy.tokenize(rep), pinned.tokenize(rep)       # a dict gives a flat token list
    assert "kernel32getprocaddress" in tl and "apiname" in tl and "args" in tl and "retval" in tl and "event" in tl
    assert "kernel32getprocaddress" not in tp and "kernel32" in tp and "getprocaddress" in tp and "args" not in tp
    vocab = json.load(open(os.path.join(INFO["nebula_root"], "nebula", "objects", "whitespace_50000_vocab.json")))
    assert all(t in vocab for t in ("apiname", "retval", "args", "kernel32getprocaddress"))
    # the legacy cleaning leaves fewer tokens unknown to the released vocabulary than the pinned one
    unk = lambda tok: float(np.mean([t not in vocab for t in tok.tokenize(rep)]))
    assert unk(legacy) <= unk(pinned)
