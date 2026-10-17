# ETL Doctor

An LLM agent that **diagnoses broken ETL pipelines**: date-format changes, renamed columns,
type drift. It investigates inside an isolated **E2B Firecracker microVM**, proposes a
fix, waits for **human approval**, and then checks the fix in the sandbox.

Built to show **AI harness engineering**: orchestration (LangGraph), typed agents
(PydanticAI), sandboxed tools, checkpointing, approval gates, budgets and evals.

> Status: **Step 3 of the [capability ladder](docs/00-poc-plan.md#2-the-capability-ladder)**.
> The agent investigates with read-only tools (profile, per-file column formats, schema diff, log grep, SQL) that run
> inside a disposable E2B microVM with no internet, and cites evidence IDs that the harness
> recorded. LangGraph orchestration comes next.

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
make diagnose SCENARIO=f1_date_format MODE=silent NO_TOOLS=1   # Step 1 baseline
make grade    SCENARIO=f1_date_format MODE=silent   # ...scored against ground_truth.json
make smoke                         # compare candidate models
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
  prompts/              system instructions
  cli.py                `etl-doctor diagnose [--no-tools]`
src/edtools/            the tool implementations: JSON in, JSON out (profile, column_by_file,
                        diff_schema, grep_logs, run_sql, read_file, list_files); run in the sandbox
sandbox/build_template.py  E2B template: Python 3.12 + pinned polars/duckdb
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
