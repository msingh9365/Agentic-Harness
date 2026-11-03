"""LLM-as-judge: is the diagnosis's explanation right, beyond the fields code can check?

    python -m evals.judge calibrate      # judge labelled synthetic answers; measure the judge itself
    python -m evals.judge run            # judge every diagnosis in out/suite/results.jsonl

The deterministic grader checks failure class, column and first bad file. It cannot check
the free text: a diagnosis can get all three fields right and still say the new date
format is MM/DD/YYYY when it is DD/MM/YYYY, or propose a fix that breaks the old files.
That is what the judge is for.

How the judge is kept honest (each is a standard mitigation):
- Reference-based: it gets the answer key, so it compares instead of guessing.
- Binary criteria with reasons written first, not a 1-10 score.
- A different model family from the one being judged (less self-preference).
- Calibrated: before its numbers are used, it is run on answers whose labels we know.
"""

import asyncio
import json
import os
from pathlib import Path

import typer
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings

from etl_doctor.llm import make_model
from evals.faults import describe
from evals.models import Fault, GroundTruth

# Not the family of the model being judged (self-preference bias). Chosen by `calibrate`.
JUDGE_MODEL = os.environ.get("ETLDOC_JUDGE_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
OUT = Path("out/suite")
app = typer.Typer(add_completion=False)


class Verdict(BaseModel):
    # Reasoning fields come first: the model writes its comparison before committing to booleans.
    comparison: str = Field(max_length=800, description="Compare the candidate with the answer key, point by point.")
    mechanism_correct: bool = Field(description="Names the same KIND of upstream change (date format / column rename / number format).")
    specifics_correct: bool = Field(
        description="Names the specific new value correctly: the new format, the new column name, or the new "
        "number style. False if it is wrong OR not stated.")
    fix_addresses_cause: bool = Field(
        description="The suggested fix would handle the new data AND keep the old data working. "
        "False if it would only work for one of them, or is not a concrete change.")
    contradictions: list[str] = Field(default_factory=list, max_length=5,
                                      description="Claims in the candidate that the answer key contradicts.")

    @property
    def passed(self) -> bool:
        return self.mechanism_correct and self.specifics_correct and not self.contradictions


judge_agent = Agent(
    output_type=Verdict,
    retries=3,
    instructions=(
        "You grade a diagnosis of a data pipeline failure against an answer key. The answer key "
        "is correct by definition. Judge only what the candidate says, not how it says it: "
        "wording, length and confidence do not matter. Be strict about specifics: a candidate "
        "that is vague about what exactly changed does not get specifics_correct."
    ),
)
SETTINGS = ModelSettings(temperature=0.0, max_tokens=4_096)


def prompt(key: str, candidate: dict) -> str:
    return (f"<answer_key>\n{key}\n</answer_key>\n\n<candidate>\n"
            f"root cause: {candidate.get('root_cause', '')}\n"
            f"suggested fix: {candidate.get('suggested_fix', '')}\n</candidate>")


async def judge(key: str, candidate: dict, model) -> Verdict:
    r = await judge_agent.run(prompt(key, candidate), model=model, model_settings=SETTINGS)
    return r.output


# --- calibration: answers with known labels ---------------------------------------------------

def _human(fault: Fault) -> str:
    p = fault.params
    if fault.type == "date_format_change":
        return f"order_date values arrive as {describe(fault)['to_format_human']} instead of YYYY-MM-DD"
    if fault.type == "column_rename":
        return f"the customer_id column arrives renamed to {p['to']}"
    d = describe(fault)
    return f"amount values arrive with {d['style_human']} (e.g. {d['example']}) instead of plain decimals"


GOOD_FIX = {
    "date_format_change": "parse order_date with both the old ISO format and the new format (coalesce the two), so old and new files load",
    "column_rename": "rename the new column back to customer_id when it is present, before validation, so old and new files load",
    "type_drift": "normalise amount (strip the symbol / swap the decimal comma) before casting to float, so old and new files load",
}
ALT = {  # a wrong but plausible value of the same kind, for the wrong-specifics negatives
    "to_format": {"%d/%m/%Y": "%m/%d/%Y", "%m/%d/%Y": "%d/%m/%Y", "%Y%m%d": "%d/%m/%Y", "epoch_ms": "%Y%m%d"},
    "to": {"cust_id": "client_id", "customerId": "cust_id", "customer_number": "customerId"},
    "style": {"comma_decimal": "currency_symbol", "currency_symbol": "comma_decimal"},
}


def calibration_set(truths: list[GroundTruth]) -> list[dict]:
    items = []
    for t in truths:
        f, first = t.fault, t.first_bad_partition
        (pk, pv), = f.params.items()
        wrong = f.model_copy(update={"params": {pk: ALT[pk][pv]}})
        other_kind = {"date_format_change": "the order_date column was dropped upstream",
                      "column_rename": "customer_id values switched from integers to strings",
                      "type_drift": "the amount column was renamed upstream"}[f.type]
        bad_fix = {"date_format_change": "change the date_format in config.yaml to the new format",
                   "column_rename": "change required_columns in config.yaml to the new column name",
                   "type_drift": "skip rows whose amount does not parse"}[f.type]
        items += [
            {"label": True, "kind": "paraphrase", "key": t.root_cause,
             "candidate": {"root_cause": f"Starting with {first}, {_human(f)}; the pipeline was not updated for this.",
                           "suggested_fix": GOOD_FIX[f.type]}},
            {"label": False, "kind": "wrong_specifics", "key": t.root_cause,
             "candidate": {"root_cause": f"Starting with {first}, {_human(wrong)}; the pipeline was not updated for this.",
                           "suggested_fix": GOOD_FIX[f.type]}},
            {"label": False, "kind": "wrong_mechanism", "key": t.root_cause,
             "candidate": {"root_cause": f"Starting with {first}, {other_kind}.", "suggested_fix": "restore the column upstream"}},
            {"label": False, "kind": "vague", "key": t.root_cause,
             "candidate": {"root_cause": f"Something in the upstream data changed around {first} and the pipeline cannot handle it.",
                           "suggested_fix": "make the pipeline more robust to upstream changes"}},
            # Right cause, but a fix that breaks the old files. Pass/fail is about the cause;
            # this one tests the fix criterion separately.
            {"label": True, "fix_label": False, "kind": "cause_ok_fix_breaks_old", "key": t.root_cause,
             "candidate": {"root_cause": f"Starting with {first}, {_human(f)}; the pipeline was not updated for this.",
                           "suggested_fix": bad_fix}},
        ]
    return items


@app.command()
def calibrate(concurrency: int = 6) -> None:
    seen, truths = set(), []
    for d in sorted((OUT / "cases").iterdir()):
        t = GroundTruth.model_validate_json((d / "ground_truth.json").read_text())
        key = (t.fault.type, json.dumps(t.fault.params, sort_keys=True))
        if key not in seen:  # the root cause doesn't depend on the mode: one per variant
            seen.add(key)
            truths.append(t)
    items = calibration_set(truths)
    model = make_model(JUDGE_MODEL)

    async def main():
        sem = asyncio.Semaphore(concurrency)

        async def one(it):
            async with sem:
                try:
                    v = await judge(it["key"], it["candidate"], model)
                    return {**it, "verdict": v.model_dump(), "passed": v.passed}
                except Exception as e:
                    return {**it, "error": f"{type(e).__name__}: {str(e)[:200]}"}

        return await asyncio.gather(*(one(i) for i in items))

    rows = asyncio.run(main())
    (OUT / "judge_calibration.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    ok = [r for r in rows if "error" not in r]
    typer.echo(f"judge {JUDGE_MODEL}: {len(ok)}/{len(rows)} judged")
    for kind in dict.fromkeys(r["kind"] for r in rows):
        rs = [r for r in ok if r["kind"] == kind]
        agree = sum(r["passed"] == r["label"] for r in rs)
        typer.echo(f"  {kind:24} verdict agrees with label {agree}/{len(rs)}")
    fx = [r for r in ok if "fix_label" in r]
    typer.echo(f"  fix criterion on bad fixes: flagged {sum(not r['verdict']['fix_addresses_cause'] for r in fx)}/{len(fx)}")
    gf = [r for r in ok if r["kind"] == "paraphrase"]
    typer.echo(f"  fix criterion on good fixes: accepted {sum(r['verdict']['fix_addresses_cause'] for r in gf)}/{len(gf)}")


@app.command("run")
def run_judge(concurrency: int = 6, results: Path = OUT / "results.jsonl") -> None:
    rows = [json.loads(l) for l in results.read_text().splitlines() if l.startswith("{")]
    out = OUT / "judge.jsonl"
    done = {j["key"] for l in out.read_text().splitlines() if "error" not in (j := json.loads(l))} if out.exists() else set()
    todo = [r for r in rows if r.get("diagnosis") and f"{r['agent']}|{r['case']}|{r['trial']}|{r.get('run_id')}" not in done]
    typer.echo(f"{len(todo)} diagnoses to judge with {JUDGE_MODEL}")
    model = make_model(JUDGE_MODEL)

    async def main():
        sem = asyncio.Semaphore(concurrency)

        async def one(r):
            async with sem:
                key = f"{r['agent']}|{r['case']}|{r['trial']}|{r.get('run_id')}"
                try:
                    v = await judge(r["root_cause_truth"], r["diagnosis"], model)
                    row = {"key": key, "judge_model": JUDGE_MODEL, "verdict": v.model_dump(), "passed": v.passed}
                except Exception as e:
                    row = {"key": key, "error": f"{type(e).__name__}: {str(e)[:200]}"}
                with out.open("a") as fh:
                    fh.write(json.dumps(row) + "\n")

        await asyncio.gather(*(one(r) for r in todo))

    asyncio.run(main())


if __name__ == "__main__":
    app()
