"""
Run an existing module of this repository with the M3 model replaced by a RoPE / full-attention variant (NOTES_ROPE.md).   (OURS; no existing module is changed)

    python -m rope_test.launcher --rope-variant rope_blocks baseline.v2pe <the arguments of the unchanged command>
    python -m rope_test.launcher baseline.gs_attack --mode scores --family v1 --extra-families v1:rope_blocks ...

--rope-variant V (rope_blocks, rope_full, sin_full, m3_custom): `baseline.pe.build_chunks(pe_mode="paper", pool_mode="attn")` returns the variant (everything else of training is the unmodified module).
Always: `baseline.padtest.load_model(kind, ...)` accepts the variant names as `kind` (for the attack and scoring modules: --extra-families name:kind).
"""
import runpy
import sys

from rope_test import rope_model as RM


def patch(variant):
    from baseline import padtest, pe
    orig_build, orig_load = pe.build_chunks, padtest.load_model

    def build_chunks(vocab_size, dropout=0.3, pe_mode="released", pos_offset=0, pool_mode="flatten", **extra):
        if variant:
            assert pe_mode == "paper" and pool_mode == "attn" and pos_offset == 0, (pe_mode, pool_mode, pos_offset)
            return RM.build(vocab_size, variant, dropout=dropout, **extra)
        return orig_build(vocab_size, dropout=dropout, pe_mode=pe_mode, pos_offset=pos_offset, pool_mode=pool_mode, **extra)

    def load_model(kind, path, device):
        if kind in RM.VARIANTS:
            return RM.load_model(kind, path, device)
        return orig_load(kind, path, device)

    pe.build_chunks, padtest.load_model = build_chunks, load_model


def main():
    argv = sys.argv[1:]
    variant = None
    if argv and argv[0] == "--rope-variant":
        variant, argv = argv[1], argv[2:]
        assert variant in RM.VARIANTS, variant
    module, rest = argv[0], argv[1:]
    patch(variant)
    print(f"[launcher] module {module}, rope variant {variant}", flush=True)
    sys.argv = [module] + rest
    runpy.run_module(module, run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    main()
