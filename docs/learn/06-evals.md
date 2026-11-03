# Step 6 notes: evals, variance, LLM-as-judge and cost

What Step 6 builds: a suite that runs the agent on **every scenario variant, several times
each**, records one JSON row per run, and turns the rows into a **scorecard**: accuracy with
error bars, consistency across trials, fix quality, safety invariants, cost and latency. An
LLM judge grades what the field grader can't, and the judge is itself measured first.

```bash
make suite-build                 # 18 cases: F1 x 4 formats, F3 x 3 names, F4 x 2 styles; crash + silent
make suite K=3                   # the graph, 3 trials per case (resumable: re-run to fill gaps)
make suite K=3 AGENT=no_tools    # the Step 1 baseline on the same cases
make judge-calibrate             # is the judge any good? (labelled answers)
make judge                       # judge every diagnosis
make scorecard                   # out/suite/scorecard.md (committed copy: docs/06-scorecard.md)
```

## Concepts, and where they live in the code

| Concept | One-line idea | In this repo |
|---|---|---|
| **Evals vs tests** | A test checks deterministic code and must always pass. An eval measures a non-deterministic system and reports a rate. Both exist here: the eval *machinery* (metrics, cost, judge pass rule) has ordinary unit tests. | `evals/` vs `tests/test_scorecard.py` |
| **Ground truth kept apart** | The answer key is written by the fault injector and lives outside the bundle; the run ID is an opaque hash because the case name contains the answer. | `ground_truth.json`, `run_id` in `evals/suite.py` |
| **Valid cases only** | Before a case is used, check it really shows its symptom (crash mode exits non-zero; silent mode exits 0 *and* the quality tests fail). A fault that breaks nothing tests nothing. | `is_valid()` in `evals/suite.py` |
| **Variants** | Same failure class, different surface: four date formats, three new column names, two number styles. Catches an agent that has memorised one example. | `variants:` in `evals/scenarios/*.yaml` |
| **k trials, pass@k vs pass^k** | Models vary run to run even at temperature 0 (batching, served kernels). pass@k: right in *any* of k trials (what a retry could get you). pass^k: right in *all* k (what you can rely on). For unattended operations, pass^k is the honest number. | `summarize()` in `evals/scorecard.py` |
| **Confidence intervals** | 50/54 sounds like 93%, but with 54 runs the 95% interval is about 82–97%. Small evals need error bars; Wilson's interval behaves at 0% and 100%. | `wilson()` |
| **Escalation is not a wrong answer** | "I couldn't conclude" handed to a human is safe; a confident wrong diagnosis is the dangerous outcome. They are counted separately. | `wrong_not_escalated` |
| **Safety invariants are measured** | "Patches applied without approval", "reported fixed but not validated" and "host bundle modified" are counted on every run (node trace, approval log, a hash of the bundle before and after), not assumed from the design. All must be 0. | `run_graph()` row fields |
| **Infrastructure errors are not scores** | A 429 from the provider or the sandbox says nothing about the agent. Those runs are recorded, excluded from scores and retried; a model or code failure *is* scored. | `is_infra()`, `done_keys()` |
| **LLM-as-judge** | Code can check fields (class, column, file). It can't check the free-text explanation ("the format is MM/DD" when it's DD/MM) or whether the fix would break old files. A judge model compares the answer to the key. | `evals/judge.py` |
| **Judge hygiene** | Reference-based (it gets the answer key), binary criteria with the comparison written first, a different model family from the one judged, temperature 0. | `Verdict`, `JUDGE_MODEL` |
| **Calibrate the judge** | Before trusting its numbers, run it on answers with known labels: correct paraphrases, wrong specifics, wrong mechanism, vague answers, right cause with a fix that breaks old data. | `calibration_set()`, `make judge-calibrate` |
| **Cost per run** | Tokens are measured per model (each role can use a different model), then priced from a table; sandbox time is priced per second. Report mean *and* p95: the tail is what blows a budget. | `usage_by_model`, `evals/prices.yaml`, `cost()` |
| **Resumable, append-only results** | Each run appends one row as it finishes; re-running skips finished slots. A suite of hours survives a crash, and the raw rows are the record: the scorecard is a pure function of them. | `results.jsonl`, `load()` |
