# STATE (Stages F, G, H, NOTES 23)
Plan written and committed. Nothing computed yet.
Stage F launched 2026-11-21T20:16:31Z on manishsinghxdev (kernel manishsinghxdev/nebula-fgh-f); quota used before: 4.44h
- 2026-11-21 20:35 UTC: code for F/G/H written and smoke-tested on free CPU kernels (two-level flags; attack runner: unedited scores reproduce the stored April logits, m1 1.9e-5, m3 7.6e-6, m2 0.0; report script runs). Stage F kernel nebula-fgh-f (manishsinghxdev) QUEUED since 20:16 UTC (waiting, no duplicate).
- NEXT: when F is COMPLETE: download outputs, `python -m baseline.gs_select_f --runs <dir> --weights-sha results/groupsplit/stage_fgh/weights_sha256.json --out results/groupsplit/stage_fgh/stage_f`, commit selection, then launch Stage G (kernels on manishsinghxdev: M2/M4 `twolevel --plan --full-january ...` and `gs_grid --family v2pe/attbal --full-loss`).
