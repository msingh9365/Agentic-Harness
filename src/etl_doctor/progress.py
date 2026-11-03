"""One-line, human-readable descriptions of graph steps, shared by the CLI and the web UI."""

NODE_LABEL = {
    "intake": "read bundle manifest",
    "provision_sandbox": "sandbox ready",
    "triage": "triage",
    "investigate": "investigation round",
    "hypothesize": "hypotheses",
    "verify": "verification",
    "propose_fix": "fix proposed",
    "release_sandbox": "sandbox released while waiting for a human",
    "approval_gate": "decision recorded",
    "apply_fix": "fix applied to a copy in the sandbox and validated",
    "escalate": "ESCALATE to a human",
    "report": "report",
    "teardown": "sandbox destroyed",
}


def node_detail(name: str, update: dict) -> str:
    """What a node's state update says, in one line."""
    detail = ""
    if name == "provision_sandbox" and update.get("sandbox_id"):
        detail = update["sandbox_id"]
    elif name == "triage" and update.get("triage"):
        t = update["triage"]
        detail = f"{t.run_outcome}; candidates {[c.value for c in t.candidate_classes]}; suspects {t.suspect_columns}"
    elif name == "hypothesize" and update.get("hypotheses"):
        detail = "; ".join(f"{h.id} {h.failure_class.value} conf={h.confidence:.2f} {h.statement[:70]}" for h in update["hypotheses"].hypotheses)
    elif name == "verify" and update.get("verification"):
        v = update["verification"]
        detail = f"{v.hypothesis_id} {v.outcome.upper()}: {v.observations[:100]}"
    elif name == "escalate":
        detail = update.get("terminal_reason", "")
    elif name == "propose_fix":
        p = update.get("proposal")
        detail = f"{len(p.edits)} edit(s) to {sorted({e.path for e in p.edits})}" if p else "no valid proposal"
    elif name == "approval_gate" and update.get("approvals"):
        a = update["approvals"][-1]
        detail = f"{a.decision.upper()} by {a.approver}" + (f": {a.feedback}" if a.feedback else "")
    elif name == "apply_fix" and update.get("validation"):
        v = update["validation"]
        detail = ("PASSED " if v.passed else "FAILED ") + ", ".join(f"{c.name}={'ok' if c.ok else 'FAIL'}" for c in v.checks)
    return detail
