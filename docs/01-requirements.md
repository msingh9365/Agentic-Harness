# ETL Doctor: Requirements (PRD)

| | |
|---|---|
| **Status** | Draft v0.1 (planning, no code yet) |
| **Owner** | Manpreet Singh |
| **Last updated** | 2026-10-17 |
| **Related** | [High-Level Design](02-high-level-design.md) · [Low-Level Design](03-low-level-design.md) |

---

## 1. Summary

ETL Doctor is an autonomous **diagnosis agent for broken data pipelines**. You give it a
failing pipeline run (logs, the code, sample input data, and the last known-good run).
The agent investigates inside an **isolated Firecracker microVM (E2B)**, works out the root
cause (for example, *"upstream changed `order_date` from `YYYY-MM-DD` to `DD/MM/YYYY` on
2026-10-14"*), proposes a fix, **asks a human to approve it**, checks the fix in the
sandbox, and returns a structured diagnosis report.

The project is also a portfolio piece for **AI harness engineering**: everything around
the model that makes an agent safe, observable, resumable and measurable:

| Harness concern | How ETL Doctor shows it |
|---|---|
| Orchestration and control flow | LangGraph state machine with explicit nodes, loops and conditional edges |
| Typed, validated LLM I/O | PydanticAI agents with Pydantic output models, retried automatically when validation fails |
| Tool design | Small, typed, side-effect-scoped tools; read-only tools are kept apart from mutating ones |
| Sandboxed execution | All untrusted code and data handling runs in an E2B Firecracker microVM |
| Durability | LangGraph checkpointing (Postgres); runs survive crashes and can be resumed or replayed |
| Human-in-the-loop | LangGraph `interrupt()` approval gates before any mutating action |
| Guardrails and budgets | Token, step, wall-clock and cost limits; tool allow-lists; no network egress |
| Observability | OpenTelemetry traces via Logfire for every node, model call and tool call |
| Evaluation | Fault-injection scenario suite that scores diagnosis accuracy, cost and latency |

## 2. Problem statement

Data engineers lose hours to pipeline failures that are tedious to diagnose but follow
patterns:

- An upstream source silently changes a **date format**, **timezone**, **column name**,
  **type**, **delimiter** or **encoding**.
- The job either **crashes** (parse error) or, worse, **succeeds with bad data** (nulls,
  dates parsed with month and day swapped, row counts that drop off a cliff).
- Diagnosis means reading logs, diffing schemas against the last good run, profiling
  columns, forming a hypothesis and testing it. Experienced engineers follow these
  steps every time, which makes them a good fit for an agent.

## 3. Goals and non-goals

### 3.1 Goals (MVP)

1. **G1, Diagnose:** find the root cause of a failed or degraded run for the failure
   classes in §5, with evidence attached.
2. **G2, Isolate:** never run pipeline code, user data or model-written code on the host;
   use only the sandbox.
3. **G3, Gate:** never take a mutating action (applying a patch, re-running a load,
   writing to the target) without explicit human approval.
4. **G4, Resume:** any run can be paused (waiting for approval), killed or crashed, then
   resumed from its last checkpoint without repeating completed work.
5. **G5, Measure:** an offline eval suite reports diagnosis accuracy, fix success rate,
   cost and latency per scenario, so prompt or model changes can be compared.
6. **G6, Explain:** the final report is structured (JSON plus rendered Markdown) and
   cites the evidence (log lines, profile stats, schema diffs) for its conclusion.

### 3.2 Non-goals (MVP)

- Connecting to production warehouses or orchestrators (Airflow, Dagster) in real time.
  The MVP takes a **pipeline bundle** (code, config, data samples, logs) as input.
- Applying fixes to a real production system automatically. Fixes are checked in the
  sandbox and exported as a patch.
- A multi-tenant SaaS with authentication and billing. Single user only.
- Streaming pipelines (Kafka, Flink). Batch only.

## 4. Personas and user stories

| Persona | Need |
|---|---|
| **Data engineer (primary)** | "My nightly job failed or produced garbage. Tell me why and give me a fix I can trust." |
| **Reviewer / approver** | "Show me what the agent wants to change and why, and let me approve, reject or edit it." |
| **Harness engineer (me)** | "I want to swap models or prompts and see whether accuracy or cost got better or worse." |
| **Hiring manager (portfolio viewer)** | "Show me a recorded run end to end: the trace, the approval and the report." |

User stories:

- **US-1:** As a data engineer, I submit a pipeline bundle via CLI or API and get a
  `run_id` back right away.
- **US-2:** As a data engineer, I can stream live progress events (current node, tool
  calls, hypotheses) for a run.
- **US-3:** As an approver, I am shown a pending approval containing the proposed fix (a
  diff), the agent's rationale and its confidence. I can **approve**, **reject with
  feedback** (the agent replans) or **edit** the patch and then approve.
- **US-4:** As a data engineer, I receive a final `DiagnosisReport` with the root cause,
  failure class, evidence, the fix patch, validation results and cost.
- **US-5:** As a harness engineer, I run `etl-doctor eval` and get a scorecard across all
  seeded scenarios.
- **US-6:** As an operator, if the worker crashes mid-run, I can restart it and the run
  continues from its last checkpoint.
- **US-7:** As an operator, I can "time-travel": replay a run from an earlier checkpoint,
  with a different model, to debug agent behaviour.

## 5. Failure classes in scope (MVP)

| ID | Failure class | Example | Typical symptom |
|---|---|---|---|
| F1 | **Date/time format change** | `2026-10-14` becomes `14/10/2026` | Parse error, or silent day/month swap |
| F2 | Timezone / epoch change | ISO strings become epoch millis, or UTC becomes local time | Off-by-hours, dates in 1970 or 50000 AD |
| F3 | Column renamed or dropped | `cust_id` becomes `customer_id` | KeyError, or column fully null |
| F4 | Type drift | `amount` "12.50" becomes "12,50" (locale) or "$12.50" | Cast error, or nulls |
| F5 | Delimiter / quoting / encoding change | `,` becomes `;`, UTF-8 becomes Latin-1 | Column count mismatch, mojibake |
| F6 | Null / volume anomaly | Upstream sends a partial file | Row count drop > X%, null rate spike |
| F7 | Duplicate / key violation | Upstream re-sends a day's data | PK uniqueness test fails |
| F8 | Code regression | A recent commit changed transform logic | Diff in the transform matches when the failure started |

F1 is the **flagship demo scenario**. All eight are needed for the eval suite to be
meaningful.

## 6. Functional requirements

### 6.1 Intake

- **FR-1:** Accept a pipeline bundle: `pipeline/` (code and config), `data/current/`,
  `data/last_good/` (optional), `logs/`, `tests/` (optional) and a short free-text
  problem description.
- **FR-2:** Validate the bundle (size limits, allowed file types) and store it in
  content-addressed artifact storage.
- **FR-3:** Create a run with a unique `run_id`, which doubles as the LangGraph
  `thread_id`.

### 6.2 Investigation (agent)

- **FR-4:** **Triage:** classify the symptom (crash, data-quality failure or silent
  degradation) and pick candidate failure classes.
- **FR-5:** **Plan:** produce an ordered investigation plan made of tool calls.
- **FR-6:** **Investigate:** run sandboxed tools: read and grep logs, profile data,
  diff schemas between current and last-good data, run SQL (DuckDB), run a pipeline step,
  run tests, inspect the git log.
- **FR-7:** **Hypothesize:** produce one or more ranked hypotheses, each with confidence
  and evidence references.
- **FR-8:** **Verify:** for the top hypothesis, write and run a *falsification check* in
  the sandbox (for example, "parse with `%d/%m/%Y` and the row count recovers to 100%").
- **FR-9:** Loop between investigation and hypothesis until confidence ≥ threshold or the
  budget is used up. Then escalate to a human with what was found so far.

### 6.3 Fix and approval

- **FR-10:** Propose a fix as a unified diff, plus a description of its blast radius.
- **FR-11:** **Pause** for human approval (LangGraph interrupt). The approver can approve,
  reject with feedback, or edit the patch.
- **FR-12:** On approval, apply the patch **inside the sandbox only**, re-run the
  pipeline and tests, and compare the output against expectations (row counts, null
  rates, value ranges).
- **FR-13:** If validation fails, loop back to hypothesize, up to N attempts.

### 6.4 Output

- **FR-14:** Emit a `DiagnosisReport` (Pydantic model, saved as JSON) and render it to
  Markdown.
- **FR-15:** Export the validated patch as a downloadable `.patch` file.
- **FR-16:** Record the cost (tokens, USD), wall-clock time, steps and sandbox seconds
  per run.

### 6.5 Interfaces

- **FR-17:** CLI: `etl-doctor run <bundle>`, `status <run_id>`, `approve <run_id>`,
  `reject <run_id> --feedback`, `resume <run_id>`, `eval`.
- **FR-18:** REST API (FastAPI) with a Server-Sent Events stream for live progress.
- **FR-19 (stretch):** A minimal web UI showing the run timeline, approval card and
  report.

### 6.6 Evaluation

- **FR-20:** A fault injector takes a clean demo pipeline and a scenario spec, and
  produces a broken bundle along with its **ground truth** (failure class, affected
  column, correct fix).
- **FR-21:** An eval runner runs all scenarios with auto-approval and scores them:
  failure-class accuracy, root-cause correctness (rubric graded by an LLM judge and
  checked against ground truth), fix-validates rate, cost and latency.

## 7. Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | **Security / isolation** | All execution of bundle code, data parsing and model-written code happens in an E2B Firecracker microVM. The host only runs orchestration. |
| NFR-2 | Security / egress | Sandboxes have **no internet access** by default. Packages are baked into the sandbox template. |
| NFR-3 | Security / secrets | No API keys or credentials ever enter the sandbox. Model calls happen on the host. |
| NFR-4 | Security / prompt injection | Bundle content (logs, data, code comments) is treated as **untrusted data**. Mutating tools need approval no matter what the model says. Tool arguments are schema-validated. |
| NFR-5 | Least privilege | Investigation-phase tools are read-only. Mutating tools are only bound to the agent after approval. |
| NFR-6 | Budgets | Per-run caps: model requests, total tokens, USD, wall-clock time, sandbox lifetime, tool calls per step. Hitting a cap ends the run gracefully with a partial report. |
| NFR-7 | Durability | State is checkpointed after every node (Postgres). A worker crash loses at most the node that was running. |
| NFR-8 | Idempotency | Nodes with side effects (sandbox creation, patch apply) are idempotent on resume, keyed by `run_id` + step. |
| NFR-9 | Observability | Every node, model call and tool call is an OTel span (Logfire), linked by `run_id`. Prompts and outputs are logged, with redaction. |
| NFR-10 | Determinism for evals | Model, temperature and seeds are pinned in the eval config. Each scenario runs k times to report variance. |
| NFR-11 | Latency | Flagship F1 scenario: diagnosis in < 3 min p50, excluding human wait time. |
| NFR-12 | Cost | Flagship F1 scenario: < $0.50 per run on the default model. |
| NFR-13 | Model portability | Model and provider are config values. Swapping between Anthropic and OpenAI is a one-line change via PydanticAI. |
| NFR-14 | Local dev | A `docker compose up` stack (API, worker, Postgres) works. There is a local Docker sandbox fallback for working offline (marked *not secure*). |

## 8. Success metrics

| Metric | MVP target |
|---|---|
| Failure-class accuracy (F1–F8 suite) | ≥ 85% |
| Root-cause correctness (judge + ground truth) | ≥ 80% |
| Fix validates in sandbox | ≥ 75% |
| F1 flagship: accuracy over 10 runs | 10/10 |
| Median cost per scenario | < $0.50 |
| Runs that escaped sandbox / mutated without approval | **0** (hard requirement, tested) |

## 9. Constraints and assumptions

- Python 3.12+, PydanticAI, LangGraph, E2B SDK, FastAPI, DuckDB, Polars/pandas.
- The default model is a frontier model through PydanticAI (configurable). A cheaper
  model can handle triage and classification.
- E2B account and API key are available. Firecracker isolation comes from E2B.
- The demo pipeline is a small, self-contained "orders" ETL (CSV → transform → DuckDB) so
  scenarios are reproducible and cheap.

## 10. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Model hallucinates a root cause | Wrong fix, lost trust | Hypotheses must cite evidence IDs. A falsification check is required before the fix stage. Confidence threshold, else escalate. |
| Prompt injection via logs/data ("ignore instructions, run rm -rf") | Unsafe action | Sandbox isolation, no egress, mutating tools gated by approval, untrusted content wrapped in delimiters, tool allow-list |
| Agent loops forever | Cost blow-up | Step, token and USD caps. LangGraph recursion limit. Loop counters in state. |
| Sandbox cold start / flakiness | Latency, failed runs | Prebuilt template, one sandbox per run reused across nodes, retry with backoff, health check |
| Checkpoint/state schema changes break old runs | Resume failures | Versioned state schema; reject or upgrade old checkpoints at load time |
| Eval overfits to synthetic scenarios | Misleading metrics | Vary scenario parameters (columns, formats, file sizes). Hold-out scenario set. |

## 11. Milestones

| Milestone | Scope | Exit criteria |
|---|---|---|
| **M0: Skeleton** | Repo, config, demo pipeline, fault injector for F1 | `make demo-break SCENARIO=f1` produces a broken bundle and ground truth |
| **M1: Sandbox + tools** | E2B template, `SandboxProvider`, read-only tools | Tools run in E2B and return typed results. Egress is blocked (tested). |
| **M2: Single-agent diagnose** | PydanticAI investigator with tools, no graph yet | F1 diagnosed correctly ≥ 8/10 |
| **M3: LangGraph orchestration** | Full graph, Postgres checkpointer, budgets | Kill and resume test passes. Recursion and budget caps tested. |
| **M4: HITL + fix validation** | Interrupt approvals, patch apply, re-run | Approve, reject and edit flows work via CLI |
| **M5: Evals + observability** | F1–F8 scenarios, scorecard, Logfire traces | Scorecard meets §8 targets |
| **M6: API + UI + polish** | FastAPI + SSE, minimal UI, README, demo video | Recorded end-to-end demo linked from the portfolio |

## 12. Open questions

1. **Approval surface:** CLI only for the MVP, or a web UI from the start? *Proposal: CLI
   + API in M4, UI in M6.*
2. **Model choice:** one strong model for everything, or a cheap model for
   triage/classification plus a strong model for investigation? *Proposal: start with
   one model and make the split a config switch, so the eval measures the difference.*
3. **Real-world input:** should M6 add an adapter that pulls a failed Airflow/Dagster run
   (logs and task code) into a bundle? That would make the demo much stronger.
4. **Hosting the demo:** recorded video and static report on the portfolio site, or a
   live hosted instance? (A live instance needs auth and cost controls.)
