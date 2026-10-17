# Model smoke test (NVIDIA API)

| | |
|---|---|
| **Date** | 2026-10-17 |
| **Script** | `scripts/smoke_llm.py` (`make smoke`) |
| **Decision** | Strong model: `nvidia/nemotron-3-super-120b-a12b`. Fast model: `openai/gpt-oss-20b` |

## What was tested

Every model got the same 4 checks, 2 runs each, temperature 0, via PydanticAI 2.57:

| Check | What it tests |
|---|---|
| `tool_output` | Structured output, PydanticAI default: the schema is a `final_result` tool the model calls |
| `native_output` | Structured output via the API's `response_format: json_schema` |
| `prompted_output` | Schema in the prompt, JSON parsed from the text reply |
| `tool_calling` | Multi-step task (list files, read headers one by one, find the renamed column): only solvable by calling tools |

Each check is graded on **content** too (right failure class, column and file), not just
"parsed OK". Every call that returned an answer had the right content; all failures
below are errors (HTTP, timeouts, bad tool calls), not wrong answers.

## Results

| Model | tool_output | native_output | prompted_output | tool_calling | median s | retries |
|---|---|---|---|---|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b` (planned strong) | 0/2 | 1/2 | 0/2 | 0/2 | 28 | 0 ¹ |
| `nvidia/nemotron-3-super-120b-a12b` | 2/2 | 2/2 | 2/2 | 0/2 ² | 7 | 0 |
| `z-ai/glm-5.3` | 2/2 | 2/2 | 2/2 | 1/2 ³ | 48 | 0 |
| `openai/gpt-oss-20b` (planned fast) | 2/2 | 2/2 | 2/2 | 2/2 | 8 | 3 ⁴ |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 2/2 | 2/2 | 1/1 | 1/1 | 169 | 0 |
| `z-ai/glm-5.3-flash` | 2/2 | 2/2 | 2/2 | 2/2 | 78 | 0 |
| `moonshotai/kimi-k2.6` | 0/2 | 0/2 | 0/2 | 0/2 | – | – ⁵ |
| `deepseek-ai/deepseek-v4.1-flash` | 0/1 | – | – | – | – | – ⁶ |

"retries" = how many times PydanticAI had to send a validation error or "please answer"
back to the model, summed over all checks.

1. **Ultra** was overloaded on the free endpoint: 7 of 8 calls got HTTP 503 "Service
   temporarily overloaded" or 500, even after 6 SDK retries with backoff. The single call
   that got through was correct. It is not usable as a default today; try again later with
   `ETLDOC_STRONG_MODEL=nvidia/nemotron-3-ultra-550b-a55b`.
2. **Super, tool calling:** a tool-call formatting bug, not a reasoning error. For the
   zero-argument tool `list_files()`, the endpoint always emitted `{"file": ""}`, which is the
   argument of the *other* tool. The model's own reasoning said "pass an empty object". When
   `list_files` was given one optional parameter (`directory: str = "data/current"`), it
   passed 2/2. **Design rule for Step 2: no zero-argument tools.**
3. **GLM-5.3, tool calling:** one run used up the 12-request budget without answering.
4. **gpt-oss-20b** sometimes ends a turn with only reasoning and no answer or tool call;
   PydanticAI then asks it to answer. With the default output retry budget of 1, this
   failed the first quick test, and with 3 it passed every time. **Set `retries` ≥ 3.**
5. **Kimi K2.6** is listed by `/v1/models` but every call returns HTTP 404.
6. **DeepSeek V4.1 Flash** (and Lightning, at times) didn't answer even a one-word prompt
   within 60 s; one check took 21 minutes of timeouts. The sweep was stopped there.

## Step 1 on real bundles (6 cases: F1, F3, F4 × crash, silent)

`python -m evals.grade out/scenarios/<case>`; correct = class, column and first bad file all right.

| Model | Correct | Runs needing a retry | Input tokens / run | Output tokens / run | Seconds / run |
|---|---|---|---|---|---|
| Nemotron 3 Super | **6/6** | 2/6 | 4.6k–12.8k | 1.9k–3.2k | 40–72 |
| gpt-oss-20b | 4/6 | 6/6 | 7.6k–17.5k | 1.3k–2.9k | 28–60 |

gpt-oss-20b's misses: once it described the column rename correctly in the summary and
then chose `failure_class: UNKNOWN` (self-contradiction); once its reasoning used up the
8,192 output-token cap before it wrote the answer. That is acceptable for quick triage,
not for the final diagnosis, which is the reason for the strong/fast split.

## Why this choice

- **Strong = Nemotron 3 Super:** passed every structured-output check, fastest of the
  reliable models (~7 s median on small prompts), 6/6 on Step 1. Its tool-call quirk has a
  simple workaround (rule above).
- **Fast = gpt-oss-20b:** passed every check, about as fast as Super, and cheap. Needs a
  retry budget. Use it for triage and summaries, not final answers.
- **Backup strong = GLM-5.3:** reliable but 5–10× slower.
- Free-tier availability changes daily, so `make smoke` re-checks before a demo.
