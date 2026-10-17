# ETL Doctor: PoC Plan (read this first)

| | |
|---|---|
| **Status** | Agreed scope v0.3 |
| **Goal** | A campus-interview demo of AI harness engineering, ready in 15 days |
| **Related** | [Requirements](01-requirements.md) · [HLD](02-high-level-design.md) · [LLD](03-low-level-design.md) |

Documents 01–03 describe the full design. **This document overrides them for the PoC.**
Anything not listed here is either cut or postponed.

## 1. Decisions so far

| Topic | Decision | Notes |
|---|---|---|
| LLM | **Azure OpenAI** (from the Azure for Students account), deployment **TBD** | PydanticAI `AzureProvider`; the model string looks like `azure:<deployment-name>`. Key and endpoint are read from env vars `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT`. Needed from Step 1 on. |
| Sandbox | **E2B**, Hobby tier: free, with a one-time $100 credit | Plus a `docker` fallback behind the same interface, so the live demo can't fail because of the network. |
| Checkpointing | **SQLite** (`langgraph-checkpoint-sqlite`) | Same LangGraph features as Postgres (resume, interrupts, time travel). Postgres is "the production answer". |
| Failure types | **3**: F1 date-format change, F3 column rename, F4 type drift | F1 is the flagship demo. |
| Interface | CLI first, UI later if time allows | — |
| Code home | `msingh9365/Agentic-Harness` repo; these docs live in `docs/` | — |
| Background | Comfortable with Python, Pydantic, Docker; some LangGraph | Code comments explain *why*, not Python basics |
| Build approach | **Capability ladder.** Each step adds one capability, works on its own, and gets its own commit. | Stop wherever time runs out and the demo still works. |
| Cut from PoC | REST API, job queue, worker process, MinIO, Logfire dashboards, F2/F5–F8, replay endpoint | Mention them in the interview as "next steps". |

## 2. The capability ladder

Each rung below is something you could demo by itself. The **concept** column lists
what you'll learn on that rung, so the code and the theory line up.

| Step | Capability added | What you can demo after this step | Concepts to learn |
|---|---|---|---|
| **0** | Demo "orders" pipeline + fault injector (3 failure types) + ground-truth files | `make break SCENARIO=f1` → pipeline fails or silently corrupts data | ETL basics, data contracts, why silent failures are worse than crashes |
| **1** | One PydanticAI agent, **no tools**: logs and schema go into the prompt, a typed `Diagnosis` comes out | "The LLM reads logs and returns validated JSON" | Tokens, context window, temperature, prompts, structured output, validation + retry |
| **2** | **Tools** (run locally): `profile_dataset`, `diff_schema`, `grep_logs`, `run_sql` | Agent decides *which* checks to run and cites evidence IDs | Function/tool calling, the agent loop (ReAct), tool design, hallucination control via evidence |
| **3** | Move tools into an **E2B sandbox** (no internet) | "All untrusted code runs in a Firecracker microVM", plus a test proving that `curl` fails inside it | Isolation: process vs container vs microVM; prompt injection; least privilege |
| **4** | **LangGraph** orchestration: triage → investigate ⇄ hypothesize → verify, SQLite checkpoints, budgets | Kill the process mid-run, resume, and it continues from the checkpoint | State machines, graphs vs free-form agents, checkpointing, budgets/recursion limits |
| **5** | **Human approval**: propose a patch → `interrupt()` → approve/reject in the CLI → apply + validate in the sandbox | The headline demo: an approval gate before any change | Human-in-the-loop, idempotency, why mutating tools are never given to the model |
| **6** | **Evals**: 3 failure types × variants × k runs, plus a scorecard | "9/10 correct, $0.0x per run, 0 unapproved mutations" | Evals vs tests, LLM-as-judge, variance, measuring cost |
| **7** *(optional)* | **Incident memory (RAG)**: embed past incident reports and runbooks, retrieve similar ones during triage | "It recognised this as similar to incident #12" | **Chunking, embeddings, vector search, RAG**. This is where the topics you asked about fit into the project |
| **8** *(optional)* | Streamlit UI (timeline + approval card), README, recorded demo video | The polished 5-minute demo | — |

Step 7 is how chunking, embeddings and retrieval come into the project naturally: past
incidents and runbooks are documents. Chunking and embedding them lets the agent say
"this looks like the March locale bug". That is a real use for retrieval, not RAG for its
own sake.

## 3. 15-day schedule (draft)

| Days | Build (Claude writes code, you review and run it) | Learn (ground-up sessions) |
|---|---|---|
| 1 | Step 0 | How an ETL pipeline fails; data contracts |
| 2–3 | Step 1 | How LLMs work: tokens → embeddings → transformer → next-token sampling; prompting; structured output |
| 4–5 | Step 2 | Tool calling and the agent loop |
| 6 | Step 3 | Sandboxing and security |
| 7–8 | Step 4 | LangGraph, state, checkpointing |
| 9 | Step 5 | Human-in-the-loop and safety design |
| 10–11 | Step 6 | Evals |
| 12 | Step 7 (if on track) | Chunking, embeddings, vector search, RAG |
| 13 | Step 8: README, diagram, recording | — |
| 14–15 | Buffer + **mock interview**: explain each design decision, whiteboard the graph, likely questions | Rehearsal |

## 4. Open questions

1. **Azure deployment:** which model deployment to use (check Azure AI Foundry →
   Deployments). It must support tool calling and structured output; `gpt-4o-mini` or
   `gpt-4.1-mini` is a good, cheap choice. **Needed before Step 1.**
