# Step 1 notes: one agent, no tools, typed output

What Step 1 builds: `etl-doctor diagnose <bundle>` reads logs, code and sample rows,
sends them to an LLM, and gets back a `Diagnosis` object that has been **validated twice**:
once for shape (Pydantic) and once for facts (our validator).

```
bundle/ ──► context.py ──► prompt (≈3k tokens) ──► LLM ──► JSON ──► Pydantic ──► validator ──► Diagnosis
                                                    ▲                    │ error        │ ModelRetry
                                                    └────────────────────┴──────────────┘
```

Run it:

```bash
make break SCENARIO=f1_date_format MODE=silent
uv run etl-doctor diagnose out/scenarios/f1_date_format__silent/bundle --show-prompt   # see exactly what the model sees
make diagnose SCENARIO=f1_date_format MODE=silent
make grade    SCENARIO=f1_date_format MODE=silent    # + score against ground_truth.json
```

## Concepts, and where they live in the code

| Concept | One-line idea | In this repo |
|---|---|---|
| **Tokens** | Models read and write sub-word pieces, not characters. About 4 English characters per token; code and logs are denser. You pay per token, and limits are in tokens. | `prompt_chars` vs `input_tokens` in the CLI output: ~10 KB of context became ~5k input tokens |
| **Context window** | The most tokens one request can hold (prompt + output). Everything the model "knows" about your problem must fit in it. | `context.py`: every block has a cap (`LOG_CHARS`, `CODE_CHARS`, `SAMPLE_ROWS`) |
| **Truncation strategy** | What you cut matters. Tracebacks are at the end of logs, so logs keep their tail; config and code keep their head. | `tail()` vs `head()` in `context.py` |
| **System prompt vs user prompt** | Instructions (who you are, how to work, rules) vs data (this bundle). Keeping them apart makes prompts reusable and testable. | `prompts/diagnose.md` = instructions; `BundleContext.render()` = user prompt |
| **Temperature** | How random the next-token sampling is. 0 = always pick the most likely token. Use 0 for extraction and diagnosis, higher for brainstorming. Even at 0, providers are not perfectly deterministic. | `SETTINGS = ModelSettings(temperature=0.0)` in `diagnose.py` |
| **Structured output** | Make the model return JSON matching a schema, instead of prose you parse with regex. Three ways (see below). | `domain.py: Diagnosis`; `output_type=Diagnosis` |
| **Field descriptions are prompts** | The JSON schema, including each `Field(description=...)`, is sent to the model. Good descriptions often matter more than the system prompt. | `domain.py` |
| **Validation + retry** | Pydantic rejects bad shapes; an `output_validator` rejects bad facts. Both send the error message back to the model, which tries again. | `@agent.output_validator check_against_context`, `retries=3` |
| **Hallucination control** | Don't trust, verify: every quote must appear verbatim in the context, and every file name must exist. Cheap checks catch invented evidence. | `check_against_context` |
| **Budgets** | Cap how many model calls one task can make, so a model that keeps failing can't loop and spend forever. | `UsageLimits(request_limit=6)` |
| **Prompt injection (first line of defence)** | Data from the broken system may contain text like "ignore previous instructions". Mark it as untrusted data, and stop it from closing its own tag. | `<untrusted source=...>` blocks and `escape()` in `context.py`; rule at the end of `diagnose.md` |
| **Evals vs tests** | Tests check the plumbing deterministically (fake model). Evals check model quality against an answer key (real model, scored). | `tests/test_diagnose.py` (FunctionModel) vs `evals/grade.py` |

## Three ways to get structured output

The smoke test (`scripts/smoke_llm.py`) tries all three on every candidate model:

1. **Tool output** (PydanticAI's default). The schema is offered as a tool called
   `final_result`, and the model "calls" it with the answer as arguments. Works with any
   model that supports tool calling.
2. **Native output**. The API's `response_format={"type": "json_schema", ...}`. The server
   constrains decoding so the output *must* match the schema. Strongest guarantee, but not
   every provider or model supports it.
3. **Prompted output**. The schema is pasted into the prompt and the JSON is parsed from
   plain text. Works everywhere, and has the weakest guarantee: you rely on validation +
   retry.

## What we saw on real runs (Nemotron 3 Super, 6 cases)

- 6/6 correct (failure class, column, first bad file), crash and silent modes.
- 2/6 runs needed **one retry**: the model paraphrased a quote, the validator rejected it,
  and the model fixed it. Input tokens on those runs went from ~5k to ~12k, because a
  retry re-sends the whole conversation. **Retries cost money**, so tighter instructions
  and field descriptions pay for themselves.
- Output tokens (2–3k) were much higher than the JSON itself (~300 tokens). These are
  reasoning models: they "think" before answering, and you pay for the thinking.

## Likely interview questions

- *Why not just ask for JSON in the prompt?* Free-text JSON can be malformed or miss
  fields. Schema-constrained output plus validation turns "usually right" into "right or
  an explicit error".
- *How do you stop the model inventing evidence?* Make it quote, then check the quotes
  against the source in code. Later steps go further: evidence IDs that only tools can
  create.
- *What happens when validation keeps failing?* Bounded retries, then a hard error. The
  harness never silently accepts an invalid answer.
- *Why temperature 0?* Diagnosis is not a creative task: we want the most likely answer
  and repeatable runs. Note that it is still not fully deterministic, which is why evals
  run each case several times (Step 6).
- *What's the limit of Step 1?* The model only sees what we chose to put in the prompt. If
  the evidence is in row 5,000 of a file, it can't find it. That is why Step 2 adds tools.
