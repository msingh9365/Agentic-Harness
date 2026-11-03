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

## Results (full table: [06-scorecard.md](../06-scorecard.md))

Graph agent, strong model Nemotron Ultra, code model MiniMax M3.1 Flash; 18 cases × 3
trials, every fix approved by the eval (so the harness, not a reviewer, has to catch bad ones).

| Metric | Value |
|---|---|
| Diagnosis correct | **54/54** (95% CI 93–100%); pass^3 18/18; same result every trial 18/18 |
| LLM judge: explanation correct | 54/54; agrees with the field grader 54/54 |
| Fix validated in the sandbox | **28/54 (52%, CI 39–65%)**: F4 12/12, F1 9/24, F3 7/18 |
| Fix: pass@3 vs pass^3 (per case) | **16/18 vs 5/18** |
| Patches applied without approval / reported fixed but not validated / host bundle modified | **0 / 0 / 0** |
| Cost per run (assumed prices) | **$0.038 mean, $0.057 p95**; 42k tokens median, 178 s median |
| Infrastructure errors | 1 slot gave up after 5 rate-limited attempts; re-run later, so 0 in the final table |

The headline for an interview: **diagnosis 54/54, fixes 52%, 0 unsafe outcomes, about 4
cents a run.** The fixer is the weak part, and the harness makes that weakness safe.

### Against the Step 1 baseline (no tools, whole bundle in the prompt)

| | Graph agent | No-tools baseline |
|---|---|---|
| Diagnosis correct | 54/54 (CI 93–100%) | 52/54 (96%, CI 87–99%) |
| pass^3 / pass@3 | 18/18 / 18/18 | 16/18 / 18/18 |
| Failed runs | 0 | 2, both "exceeded output retries" (the answer kept failing validation), never a confident wrong answer |
| Fixes | 28/54 validated | none (it only suggests) |
| Tokens / time per run (median) | 42k / 178 s | 6k / 24 s |
| Cost per run (mean) | $0.038 | $0.006 |

An honest reading: **on bundles this small, tools buy little diagnosis accuracy.** The
whole bundle fits in the prompt, so the baseline sees everything at once for a sixth of the
cost. The difference is within the error bars. What the graph buys is (a) verified,
cited evidence instead of a single guess, (b) a validated fix, and (c) a design that still
works when the logs and data no longer fit in a prompt, which is the normal case in
production. The interview answer to "was the agent worth it?" is "not for diagnosis at this
size; measure the baseline first, and here is where it stops being enough."

### Three things the numbers show

1. **Diagnosis is solved for these failure classes; fixing is not.** Same model family,
   same evidence: explaining the failure is reliable, writing correct polars code that
   handles both old and new data is not.
2. **Variance lives in the fix, not the diagnosis.** Diagnosis is identical across trials;
   the fix succeeds in *some* trial for 16 of 18 cases but in *every* trial for only 5.
   A single run of this suite would have reported anything from about 35% to 65%. That is
   why k > 1 and confidence intervals are not optional.
3. **A judge reading a fix is not the same as running it.** The judge said 51/54 fixes
   "address the cause"; 28/54 actually passed validation. The text of a fix looks right far
   more often than the code is right. For anything executable, execute it; use the judge
   for what can't be executed (the explanation).

### Why fixes failed (error analysis from checkpoints)

`python -m evals.fix_failures` reads `fix_feedback` from each failed run's final checkpoint:
26 runs, 78 rejected or failed attempts.

| Why the attempt failed | Attempts |
|---|---|
| Loads, but values wrong (quality tests fail) | 26 |
| polars API misuse (crashes on the new data) | 19 |
| Edit did not apply (`old_text` not copied exactly) | 17 |
| Wrong file: `extract.py`'s header check still rejects the renamed column | 12 |
| Other | 4 |

By scenario: F1 fails on polars date parsing (`to_date` with several formats, strict
parsing) and on edits that don't apply; F3 fails because the fixer edits `transform.py`
while the header check lives in `extract.py`, or the rename lands after the column was
already read as null. F4 never fails. Each category points to a different lever: the
"wrong file" and "polars misuse" ones are what retrieval of past fixes and the pipeline's
own code (Step 7) should help; "edit did not apply" is a prompt/format problem.

### The judge, calibrated

Judge: Nemotron 3.5 Lightning (a different model from both models judged), temperature 0,
reference-based. On 45 labelled synthetic answers (5 kinds × 9 variants):

| Kind | Expected | Agreement |
|---|---|---|
| Correct paraphrase | pass | 9/9 |
| Same kind of change, wrong value (e.g. MM/DD instead of DD/MM) | fail | 9/9 |
| Wrong mechanism | fail | 9/9 |
| Vague | fail | 9/9 |
| Right cause, fix that breaks the old files | pass (and fix flagged) | 8/9 (fix flagged 9/9) |

Two calibration runs differed by one or two items: the judge has variance too, so its
numbers get the same error bars as the agent's. The one miss is the judge letting a bad fix
pull down its verdict on the cause, which is why the criteria are separate booleans.

## Bugs the suite found (that 6 single runs had not)

- **Usage limit crash in `verify`:** a verifier that kept calling tools ran out of request
  budget and crashed the run; now a tool-less verdict agent rules on the checks it has.
- **Sandbox leak on exceptions:** runs that died left VMs alive until the provider's 429
  stopped everything. Fixed with a `release` on any exception and a SIGTERM handler.
- **Rate limits scored as wrong answers:** an early scorecard counted 429s against the
  agent. Now they are infrastructure errors: retried with shared backoff, never scored.
- **Quote check vs the endpoint:** the provider mangles quote characters inside tool-call
  arguments, so exact-quote validation failed on correct answers. `normalize()` now
  decodes `\uXXXX` and ignores quotes before comparing.

The pattern: **at scale, the failures are mostly in the harness, not the model.**

## Likely interview questions

- *How do you evaluate a non-deterministic agent?* Fixed cases with ground truth kept
  outside the agent's view, several trials per case, report rates with confidence
  intervals, and report pass^k (reliable) next to pass@k (possible).
- *Your diagnosis is 100%. Is it really?* 54/54 gives a 95% lower bound of 93%, on three
  failure classes I designed. It says the agent handles these well, not that it handles
  production. The next step is more classes and real incident replays.
- *Why not just use an LLM judge for everything?* It can't run code, and it is biased
  toward plausible text: here it accepted 51/54 fixes when 28 worked. Use code checks where
  possible, execution for code, and a calibrated judge only for free text.
- *How do you know the judge is right?* Calibrate it on labelled answers including hard
  negatives (right kind, wrong value; vague), use a different model family, binary criteria
  with reasoning first, temperature 0, and check its agreement with the deterministic grader.
- *What does a run cost and what drives it?* About $0.04 at assumed prices, mostly the
  strong model's input tokens during investigation; the p95 is about 1.5× the mean, driven
  by fix retries. Measure tokens per model, price from a table, report the tail.
- *What would you improve first, and how would you know it worked?* The fixer, starting
  from the error analysis (wrong file, polars misuse). Re-run the same suite and compare fix
  pass^k and its interval, with diagnosis and the safety counts as guardrails that must not
  regress.
- *Why compare with a no-tools baseline?* Without one, 54/54 says nothing about whether
  the tools, the graph or the model did the work. Here the baseline is 52/54 at a sixth of
  the cost: the graph's value is the verified evidence and the fix, not raw accuracy.
- *A run hit a rate limit. Did that count as a failure?* No: infrastructure errors are
  recorded and retried, never scored, and the scorecard shows how many there were.
