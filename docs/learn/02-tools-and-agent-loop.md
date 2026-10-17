# Step 2 notes: tools and the agent loop

What Step 2 builds: the agent no longer gets everything in its prompt. It gets the problem
statement and six **read-only tools**, decides which checks to run, and must cite the
**evidence IDs** that the harness recorded for those checks.

```
              ┌──────────── agent loop (PydanticAI runs it; UsageLimits bound it) ───────────┐
problem.md ─► │ LLM ──tool call──► tools.py ──► Executor ──► python -m edtools <cmd> '<json>' │
              │  ▲                    │ validate args            (LocalExecutor now,       │
              │  │                    │ record Evidence ev-00N    E2B sandbox in Step 3)   │
              │  └──{evidence_id, result} or {error}◄─┘                                    │
              └──► Diagnosis(evidence_ids=[...]) ──► validator: every ID must exist ──────────┘
```

Run it:

```bash
make diagnose SCENARIO=f3_column_rename MODE=silent           # live tool trace, then the diagnosis
make diagnose SCENARIO=f3_column_rename MODE=silent NO_TOOLS=1 # Step 1 baseline, same case
make grade    SCENARIO=f3_column_rename MODE=silent
```

## Concepts, and where they live in the code

| Concept | One-line idea | In this repo |
|---|---|---|
| **Tool (function) calling** | The model can't run code. It outputs a structured request ("call `diff_schema` with these args"); *your* code runs it and sends the result back. The model only ever sees names, descriptions and JSON schemas. | `tools.py`; PydanticAI turns each function's signature + docstring into a tool schema |
| **The agent loop (ReAct)** | Reason → Act (tool call) → Observe (result) → repeat, until the model returns a final answer instead of a tool call. | `investigate.py`; `agent.run()` runs the loop |
| **Tool descriptions are prompts** | The docstring and `Args:` text decide when and how the model uses a tool. A vague docstring means wrong or wasted calls. | Docstrings in `tools.py`, e.g. `run_sql` lists the tables and what they mean |
| **Tool design** | Few, focused, read-only tools with typed args. Return compact, decision-ready signals (e.g. "`order_date`: `9999-99-99` → `99/99/9999`"), not raw dumps. | `diff_schema` and `profile` in `edtools/commands.py`, `formats.py` |
| **Errors as observations** | A bad argument is not a crash: return `{"error": ...}` so the model can correct itself on the next turn. Crash only on real infrastructure failures. | `UserError` → exit 2 → `{"error"}`; other exits raise in `executor.py` |
| **Hallucination control via evidence IDs** | The harness, not the model, creates `ev-007` when a tool runs. The final answer must cite IDs; invented IDs are rejected and sent back. A human can trace every claim to a real tool call. | `evidence.py`, `check_citations` in `investigate.py` |
| **Budgets** | Cap model requests and tool calls per run. A confused model otherwise loops (and spends) forever. | `UsageLimits(request_limit=20, tool_calls_limit=15)` |
| **Context growth** | Every loop iteration re-sends the whole conversation, including all earlier tool results, so input tokens grow roughly quadratically with the number of steps. | Compare input tokens in the table below; `MAX_RESULT_CHARS` caps each result |
| **Defence in depth** | Validate twice: the host rejects bad paths before running anything (`RelPath`), and the tool code checks again where it touches files (`safe_path`). SQL: a statement allow-list for clear errors, and DuckDB `enable_external_access=false` + `lock_configuration` as the real boundary. | `tools.py`, `edtools/commands.py`, `tests/test_tools.py::test_tools_stay_inside_the_bundle` |
| **Seam for isolation** | Tools call an `Executor` interface. Today it is a local subprocess (a JSON boundary, a timeout, an output cap, but *not* isolation). Step 3 swaps in a microVM without touching the agent. | `executor.py` |

## Results: Step 1 vs Step 2 (Nemotron 3 Super, the same 6 cases)

| | Correct | Tool calls | Input tokens / case | Time / case |
|---|---|---|---|---|
| Step 1, everything in the prompt | 6/6 | 0 | 4.6k–12.8k | 40–72 s |
| Step 2, tools | 6/6 | 7–14 | 28k–94k | 38–179 s |

**Tools cost 5–10× more here and were not more accurate.** That is an honest and useful
result. These bundles are tiny: Step 1 could fit the first rows of every file in the
prompt, and the faults start at row 1. Tools win when that stops being true:

- the data is too big for the context window (real tables have millions of rows);
- the fault is not in the first rows (Step 1's 3-row samples would miss it);
- the needed check isn't known in advance (SQL across files, comparing loaded vs raw rows);
- you need an audit trail: every claim maps to a re-runnable tool call with its arguments.

A good interview answer: *"Start with the cheapest thing that works (stuff the context),
measure, and add tools when the data or the audit requirement outgrows it."* Step 6 evals
can add harder variants (late faults, bigger files) to show where the two diverge.

Other observations:

- The agent spent calls on things the prompt already told it (listing `.` and `logs/`
  even though the layout is in the system prompt). Tighter instructions, or a cheaper
  model for exploration, would cut cost.
- Two runs used 14 of the 15 allowed tool calls. Budgets have to be set from measured
  runs, not guessed.
- `diff_schema` was the decisive call in every case: one deterministic, well-named signal
  is worth more than many raw reads. That is the main tool-design lesson.

## Likely interview questions

- *How does tool calling actually work?* The API request includes a list of tool schemas.
  The model's reply is either text or a structured tool call (name + JSON args). The
  client runs the function and appends the result as a "tool" message, then calls the
  model again. The model never executes anything.
- *How do you stop the agent inventing evidence?* Evidence IDs are created by the harness
  when a tool runs. The output schema requires citations, and a validator rejects IDs that
  were never issued.
- *Why are the tools read-only?* The model's inputs include untrusted data (logs, files).
  If a log line can talk the model into calling a tool, that tool must not be able to
  change anything. Mutations come later, behind human approval (Step 5).
- *What stops an infinite loop?* Request and tool-call limits per run, plus retry limits
  on validation. In Step 4 the graph adds iteration and cost budgets on top.
- *Why is the local subprocess not enough?* It runs as your user, with your filesystem
  and your network. The path checks are application logic, and a bug in them is a breach.
  Step 3 moves execution into a microVM so that isolation doesn't depend on our code.
