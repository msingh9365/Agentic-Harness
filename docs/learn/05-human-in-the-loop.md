# Step 5 notes: human approval, and why the model never gets a mutating tool

What Step 5 builds: after a diagnosis is verified, the graph proposes a fix, **stops and
waits for a human**, and only after approval applies the fix, to a *copy* of the
workspace in a *fresh* sandbox, where it re-runs the pipeline and checks the result. The
deliverable is a validated `.patch` file that a human applies. The agent never changes
the real pipeline.

```
verify ─confirmed─► propose_fix ─► release_sandbox ─► approval_gate ══ interrupt() ══ (human, any time, any process)
                        ▲   │ no valid proposal                    │ approve        │ reject + feedback   │ abort
                        │   └──────────► (retry or report)         ▼                │                     ▼
                        │                                       apply_fix ──────────┤                   report
                        └──── validation failed / rejected ◄───────┘ passed ──► report (fixed, .patch written)
```

Run it:

```bash
make doctor SCENARIO=f1_date_format MODE=silent      # ... stops at the approval card
etl-doctor show    <run-id>                          # look at the pending request again
etl-doctor approve <run-id>                          # apply + validate in a fresh sandbox
etl-doctor approve <run-id> --reject "why"           # the fixer tries again with your feedback
etl-doctor approve <run-id> --abort                  # keep the diagnosis, change nothing
```

## Concepts, and where they live in the code

| Concept | One-line idea | In this repo |
|---|---|---|
| **Human-in-the-loop (HITL)** | Some decisions need a person: here, any change to the system. The agent prepares everything a reviewer needs; the person decides. | `approval_gate` node, the approval card in `cli.py` |
| **`interrupt()`** | LangGraph saves the run and stops inside the node. Resuming with `Command(resume=answer)` makes `interrupt()` return the answer. The wait can last hours, and the answer can come from another process or machine. | `approval_gate`, `decide()` in `build.py` |
| **Re-execution on resume** | On resume, LangGraph re-runs the interrupted node *from the top*. Code before `interrupt()` must be side-effect free (it runs twice). | comment in `approval_gate` |
| **Mutations are data, not tools** | The fixer can only *propose* edits (a typed `FixProposal`). It has no tool that writes anything. Applying is harness code that runs only after approval. If a poisoned log talks the model into "fixing" something, nothing happens until a human approves it. | `FixProposal`, `fixer_agent` (no tools), `apply_fix` |
| **Policy on what may change** | A fix may edit pipeline code and config only, never data, tests or logs (a "fix" that edits the failing test would pass every check). Checked on the host and again in the sandbox. | `EDITABLE` + `check_edit_policy` in `edtools/validate.py` |
| **Cheap checks before a human looks** | Don't spend reviewer attention on junk: `old_text` must exist exactly once and cover whole lines, the edit must change more than quotes/whitespace, and the edited file must still parse. Failures go back to the model. | `edit_problems`, `syntax_problems` in `fixes.py` |
| **Validate after approval, too** | A human can approve a bad patch. Approval is necessary, not sufficient: the patched pipeline is re-run on current *and* last-good data, with quality tests and data checks. | `validate_fix` in `edtools/validate.py` |
| **Regression checks** | "It loads the new files" is not enough; it must still load the old ones. A plausible bad fix (switch `date_format` to the new format) passes on the new data and fails on the old. | `pipeline_runs_last_good`, `quality_tests_last_good` |
| **Idempotency** | Applying is keyed by a hash of (edits + workspace). A retried or resumed node finds the cached result instead of applying twice. | `fix_id()` and `.fix_result.json` |
| **Untrusted code runs in the sandbox** | The patched pipeline is model-written code: it runs in the microVM, in a throwaway copy, never on the host. | `apply_fix` → `executor.edtools("validate_fix")` |
| **Don't pay for idle VMs** | The sandbox is killed before waiting for a human, and a fresh one is made to apply the fix (which also guarantees a clean workspace). | `release_sandbox` |
| **Audit trail** | Every decision (who, what, when, feedback) is appended to state and copied into the report. | `approvals` (append-only reducer), `Report.approvals` |
| **Feedback loops** | A rejection's feedback and a failed validation's errors are passed to the next proposal, so it can do better. | `fix_feedback`, prompt assembly in `propose_fix` |

## What actually happened building it (live, Nemotron 3 Ultra + MiniMax M3.1, E2B)

This step found more real problems than any other. Each one is now a guardrail or a test:

| What went wrong | Caught by | Now |
|---|---|---|
| Ultra's tool-call arguments lost every `"` and newline (`cfg["x"]` → `cfg[x]`), so code in edits was destroyed | the edit validator (old_text not found) | fixer uses native JSON output; smoke test has a `code_in_tools` check |
| In native JSON mode the endpoint never calls tools, so the fixer guessed pandas code that isn't in the file | the edit validator | the harness puts the editable files in the prompt; the fixer has no tools at all |
| Models re-quote code (`'x'` for `"x"`) when copying it | the edit validator | `repair_edits` snaps to the file's real text when a quote/whitespace-insensitive match is unique |
| My first repair let whitespace match across line breaks, so a flattened multi-line string snapped onto the whole config file | the human reviewer (the diff was obviously mangled) | loose matching never crosses lines (test with the real input) |
| `old_text` cut at a quote (`    strict = cfg[`) was unique, so a broken patch reached the human | the **sandbox validation**, after a deliberately careless approval | edits must be whole lines; edited files must still parse |
| A quote-only "edit" with confidence 0.0 reached the human | the human reviewer | cosmetic-only edits are rejected |
| The sandbox image lacked `pyarrow`, so every fix "failed" | reading the traceback tail | template v2 includes it; validation details keep the tail |
| A bug in validation surfaced as a "bad arguments" error | — | `edtools` only treats argument binding errors as the caller's fault; other exceptions crash loudly |

Final live run (`demo-approve-f1d`): proposal 1 (a quote-only no-op) was **rejected** with
feedback; proposal 2 (`pl.coalesce` over both formats) was **approved from a separate
process**, applied in a fresh sandbox, and passed all 7 checks (1,800 rows loaded, no
regression on last-good data, every date matches its partition, amounts at the same
scale). The patch was written to `.etl_doctor/fixes/demo-approve-f1d.patch` and applies
cleanly with `git apply`.

The layered-defence lesson in one sentence: **the model was wrong several times, the
reviewer was wrong once on purpose, and nothing broken was ever reported as fixed.**

## Likely interview questions

- *Why not let the agent apply the fix itself?* Its inputs are untrusted (logs and files
  from a broken system), so its actions can be steered. A read-only agent that can only
  *propose* is safe to run unattended; changing things needs a person. That's least
  privilege applied to actions, not just to files.
- *What if the reviewer approves a bad fix?* The harness validates after approval, in the
  sandbox, including regression checks on data that used to work. We tested this live.
- *How does the run survive waiting for a human?* `interrupt()` checkpoints the state;
  the process can exit. `etl-doctor approve` in any later process loads it and resumes.
  The sandbox is released while waiting, and a fresh one is created to apply the fix.
- *What happens on resume after `interrupt()`?* The node re-runs from its first line and
  `interrupt()` returns the human's answer, so code before it must be pure. And
  `apply_fix` is idempotent (keyed by the patch and workspace hash) in case it re-runs.
- *Why search/replace edits instead of a diff?* LLMs get line numbers in unified diffs
  wrong. Exact text replacement is easy to check (it must exist once, cover whole lines)
  and easy to render as a diff for the human.
- *How do you stop reviewer fatigue?* Reject junk automatically before a person sees it
  (doesn't apply, doesn't parse, no real change, forbidden file), show the evidence and
  the diff on one card, and cap attempts.
