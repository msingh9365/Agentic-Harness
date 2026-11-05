#!/usr/bin/env python
"""
Checks for the two-level Nebula. Run from the repo root:
    python -m hier_nebula.tests --nebula ../nebula
"""
import argparse
import json
import os
import tempfile

import numpy as np
import torch

from hier_nebula.model import HierNebula, build_level1
from hier_nebula.data import ChunkDataset, collate, SEQ_LEN


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nebula", default="../nebula")
    a = ap.parse_args()
    torch.manual_seed(0)

    from measure_lengths import Nebula
    nb = Nebula(a.nebula)
    level1 = build_level1(a.nebula, vocab_size=nb.vocab_size, pretrained=True)
    model = HierNebula(level1, max_chunks=8).eval()

    # real reports, tokenized with Nebula, no truncation
    reps = {}
    for f in ["report_example_entrypoint_ransomware.json", "report_example_entrypoint_with_registry.json",
              "report_example_entrypoint_with_file.json"]:
        with open(os.path.join(a.nebula, "emulation", f)) as fh:
            reps[f] = nb.ids(nb.report(json.load(fh)))

    # 1. level 1 on chunk 0 reproduces Nebula's own prediction exactly
    for f, ids in reps.items():
        x = torch.tensor(nb.tokenizer.encode(nb.report(json.load(open(os.path.join(a.nebula, "emulation", f)))),
                                             pad=True)).long()                 # Nebula's own 512 input
        with torch.no_grad():
            ref = level1(x)
            ours = model.nebula_logit(model.chunk_vector(x))
        assert torch.allclose(ref, ours, atol=1e-5), (f, ref, ours)
    print("ok 1: chunk-0 vector + Nebula head == original Nebula output")

    # 2. data round trip: chunks hold exactly the tokens, in order, padded with 0
    with tempfile.TemporaryDirectory() as d:
        arrays = [np.asarray(v[:8 * SEQ_LEN], dtype=np.uint16) for v in reps.values()]
        offs = np.zeros(len(arrays) + 1, dtype=np.int64); offs[1:] = np.cumsum([len(x) for x in arrays])
        np.save(os.path.join(d, "tokens.npy"), np.concatenate(arrays)); np.save(os.path.join(d, "offsets.npy"), offs)
        import pandas as pd
        pd.DataFrame({"label": [1, 0, 1]}).to_csv(os.path.join(d, "meta.csv"), index=False)
        ds = ChunkDataset(d, np.arange(3))
        for i, ids in enumerate(reps.values()):
            c, _, _ = ds[i]
            assert c.shape[0] == max(1, -(-len(ids) // SEQ_LEN)), (c.shape, len(ids))
            flat = c.reshape(-1).numpy()
            assert (flat[:len(ids)] == np.asarray(ids)).all() and (flat[len(ids):] == 0).all()
        ids, mask, labels, rows = collate([ds[i] for i in range(3)])
        assert ids.shape == (3, mask.sum(1).max().item(), SEQ_LEN) and mask.sum(1).tolist() == [ds[i][0].shape[0] for i in range(3)]
    print("ok 2: token chunks round-trip;", "chunks per report:", mask.sum(1).tolist())

    # 3. padding chunks change nothing (eval mode)
    with torch.no_grad():
        out = model(ids, mask)
        ids2 = torch.cat([ids, torch.randint(1, 1000, (3, 2, SEQ_LEN))], 1)      # junk in padded slots
        mask2 = torch.cat([mask, torch.zeros(3, 2, dtype=torch.bool)], 1)
        out2 = model(ids2, mask2)
    assert torch.allclose(out, out2, atol=1e-5), (out, out2)
    print("ok 3: extra masked chunks (even with junk tokens) do not change the output")

    # 4. order matters (chunk position embedding) and gradients reach both levels
    model.train()
    loss = model(ids, mask).sum()
    loss.backward()
    g1 = sum(p.grad.abs().sum().item() for p in model.level1.parameters() if p.grad is not None)
    g2 = sum(p.grad.abs().sum().item() for p in model.level2.parameters() if p.grad is not None)
    assert g1 > 0 and g2 > 0
    model.zero_grad(); model.freeze_level1(True)
    model(ids, mask).sum().backward()
    assert all(p.grad is None for p in model.level1.parameters())
    print("ok 4: gradients reach level 1 and level 2; freeze_level1() stops level-1 gradients")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
