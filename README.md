# ETL Doctor

An LLM agent that **diagnoses broken ETL pipelines**: date-format changes, renamed columns,
type drift. It investigates inside an isolated **E2B Firecracker microVM**, proposes a
fix, waits for **human approval**, and then checks the fix in the sandbox.

Built to show **AI harness engineering**: orchestration (LangGraph), typed agents
(PydanticAI), sandboxed tools, checkpointing, approval gates, budgets and evals.

> Status: **Step 6 of the [capability ladder](docs/00-poc-plan.md#2-the-capability-ladder), plus a web UI.**
> A LangGraph state machine diagnoses (triage → investigate ⇄ hypothesize → verify), proposes
> a fix, **waits for a human** (`interrupt()`, answerable from any process or the browser), then
> applies the fix to a copy in a fresh E2B microVM and re-runs the pipeline on current and
> last-good data. The output is a validated patch for a human to apply; the agent never changes
> the real pipeline. Checkpointed (kill it, resume it); budgets end in escalation, not a crash.
> Evals: diagnosis **54/54**, fixes validated **28/54**, **0** unsafe outcomes, about $0.04 a run
> ([scorecard](docs/06-scorecard.md)).

## Docs

| Doc | What it covers |
|---|---|
| [00 · PoC plan](docs/00-poc-plan.md) | Agreed scope, the step-by-step capability ladder, 15-day schedule |
| [01 · Requirements](docs/01-requirements.md) | Problem, goals, failure classes, functional and non-functional requirements |
| [02 · High-level design](docs/02-high-level-design.md) | Components, the LangGraph state machine, sandbox and HITL design |
| [03 · Low-level design](docs/03-low-level-design.md) | Models, state, nodes, tools, sandbox interface, evals |
| [04 · Model smoke test](docs/04-model-smoke-test.md) | Which NVIDIA-hosted models handle structured output and tool calling |
| [learn/01 · Structured output](docs/learn/01-structured-output.md) | Step 1 concepts mapped to the code, plus likely interview questions |
| [learn/02 · Tools and the agent loop](docs/learn/02-tools-and-agent-loop.md) | Step 2 concepts: tool calling, ReAct loop, tool design, evidence IDs |
| [learn/03 · Sandboxing and prompt injection](docs/learn/03-sandboxing.md) | Step 3 concepts: process vs container vs microVM, layered defence, least privilege |
| [learn/04 · LangGraph, checkpoints, budgets](docs/learn/04-graph-and-checkpoints.md) | Step 4 concepts: state machines vs free agents, reducers, durability, resume, escalation |
| [learn/05 · Human-in-the-loop](docs/learn/05-human-in-the-loop.md) | Step 5 concepts: `interrupt()`, mutations as data, validation after approval, idempotency |
| [learn/06 · Evals](docs/learn/06-evals.md) · [scorecard](docs/06-scorecard.md) | Step 6: k trials, pass^k, confidence intervals, LLM-as-judge and its calibration, cost, error analysis |
| [learn/07 · Web UI and hosting](docs/learn/07-web-ui-and-hosting.md) | The browser UI over the same graph, its security, and where/how to host it |

## Quick start

```bash
make setup                       # uv sync
make run                         # healthy pipeline: run + quality checks pass
make break SCENARIO=f1_date_format MODE=silent
make test

export NVIDIA_API_KEY=...         # LLM steps
export E2B_API_KEY=...            # sandbox (Step 3+); `make template` once to build the image
make diagnose SCENARIO=f1_date_format MODE=silent   # agent, tools in E2B: live tool trace + Diagnosis JSON
make diagnose SCENARIO=f1_date_format MODE=silent SANDBOX=local   # tools on this machine (dev only)
make attack   SCENARIO=f1_date_format MODE=silent   # prompt-injection drill
make doctor   SCENARIO=f1_date_format MODE=silent   # Step 4 graph: triage -> investigate <-> hypothesize -> verify -> report
make doctor   SCENARIO=f1_date_format MODE=silent CRASH=hypothesize   # kill -9 mid-run...
make resume   RUN=run-...                           # ...and continue from the checkpoint
make history  RUN=run-...                           # every checkpoint of a run
etl-doctor show    RUN                              # the approval a run is waiting on
etl-doctor approve RUN [--reject "why" | --abort]   # answer it (any process, any time)
make diagnose SCENARIO=f1_date_format MODE=silent NO_TOOLS=1   # Step 1 baseline
make grade    SCENARIO=f1_date_format MODE=silent   # ...scored against ground_truth.json
make smoke                         # compare candidate models

make ui                            # web UI on http://127.0.0.1:8000: start runs, watch live, approve
make docker-build && make docker-run   # the same UI in the container used for hosting
uv run etl-doctor export out/web/runs/RUN  # record a finished run for the static replay site
make site-preview                  # the GitHub Pages site (replays of real runs) on :8001
```

## What's here

```
src/etl_doctor/         the agent
  llm.py                NVIDIA API via PydanticAI (one place to swap providers)
  context.py            bundle -> bounded, <untrusted>-tagged prompt context
  domain.py             Diagnosis schemas (sent to the model as JSON schema)
  diagnose.py           Step 1 agent (no tools) + validator that rejects invented quotes
  investigate.py        Step 2 agent: tool loop + validator that rejects uncited/invented evidence IDs
  tools.py              model-facing read-only tools; each call is recorded as evidence
  evidence.py           evidence store (IDs come from the harness, never the model)
  executor.py           Executor interface + LocalExecutor (subprocess, dev only)
  sandbox.py            E2BExecutor: same tools in a Firecracker microVM, no internet
  fixes.py              fix guardrails (exact, whole-line, parses, not cosmetic) + patch rendering
  graph/                Step 4: LangGraph state machine
    state.py            RunState (checkpointed), reducers, budgets, hypothesis/verification models
    agents.py           triage / investigator / hypothesis / verifier / fixer roles + validators
    nodes.py            node functions, routing (pure functions of state), sandbox reconnect
    build.py            graph wiring, SQLite checkpointer, run / resume / history
  prompts/              system instructions
  progress.py           one-line step descriptions shared by the CLI and the UI
  web/app.py            FastAPI: runs as background tasks, live events (SSE), approvals, auth/CSRF/CSP
  web/static/           the page: plain HTML/CSS/JS, renders untrusted text only as text
  cli.py                `etl-doctor diagnose|run|resume|history|approve|serve`
src/edtools/            the tool implementations: JSON in, JSON out (profile, column_by_file,
                        diff_schema, grep_logs, run_sql, read_file, list_files); run in the sandbox
  validate.py           harness-only: apply approved edits to a copy, re-run pipeline + checks
sandbox/build_template.py  E2B template etl-doctor-v2: Python 3.12 + the pipeline's pinned deps
scripts/smoke_llm.py    model comparison: structured output + tool calling
demo_pipeline/          the "patient": orders CSVs -> Polars transform -> DuckDB
  pipeline/             extract.py, transform.py, load.py, run.py, config.yaml
  tests/                post-load data-quality checks (dbt-test style)
  generate.py           deterministic synthetic source data
evals/
  scenarios/*.yaml      failure scenarios (F1 date format, F3 column rename, F4 type drift)
  faults.py             fault implementations
  inject.py             builds a broken bundle + a separate ground-truth answer key
  grade.py              runs the agent on a case and scores it against the answer key
  attack.py             prompt-injection drill: planted log line, reports each defence layer
  suite.py, judge.py, scorecard.py, fix_failures.py   Step 6: eval suite, LLM judge, scorecard, error analysis
Dockerfile, fly.toml    hosting: one container, state on a volume at /data
site/                   static GitHub Pages site: landing page + replays of recorded runs (site/runs/*.json)
tests/                  offline tests (fake models) + test_sandbox.py against a real microVM
```

### Failure scenarios

| ID | Fault | `crash` mode (`strict_parsing: true`) | `silent` mode (`strict_parsing: false`) |
|---|---|---|---|
| F1 | `order_date` goes from `YYYY-MM-DD` to `DD/MM/YYYY`, `MM/DD/YYYY`, `YYYYMMDD` or epoch ms | `strptime` error | Rows dropped; "every source file loaded" check fails |
| F3 | `customer_id` renamed to `cust_id`, `customerId` or `customer_number` | Header-mismatch error | Union by name fills nulls; "no null keys" check fails |
| F4 | `amount` becomes `12,50` or `$12.50` | Cast error | Rows dropped; "every source file loaded" check fails |

Each `make break` writes:

```
out/scenarios/<case>/
  bundle/               what the agent sees: code, data/current, data/last_good, logs/, problem.md
  ground_truth.json     the answer key: kept outside the bundle, used only for grading
```

The **silent** mode is the interesting one. The pipeline reports success and the problem
only shows up in the data, which is what makes these bugs expensive in real life.
