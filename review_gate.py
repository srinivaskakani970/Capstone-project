"""
review_gate.py -- Human review gate with audit logging (Task 3.4).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG_PATH = Path(__file__).resolve().parent / "audit_log.jsonl"
VALID_DECISIONS = {"approve", "edit", "reject"}


def review_gate_v1(
    report: dict,
    decision: str,
    reviewer_note: str = "",
) -> dict:
    """
    Accept a report dict and a decision, validate the decision, record  an audit
    log entry, and return the updated report with decision metadata.
    """
    if decision not in VALID_DECISIONS:
        raise ValueError(
            f"Invalid decision '{decision}'. Must be one of: {sorted(VALID_DECISIONS)}"
        )

    external_allowed = decision == "approve"
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()

    updated_report = dict(report)
    updated_report["review"] = {
        "decision": decision,
        "reviewer_note": reviewer_note,
        "external_use_allowed": external_allowed,
        "run_id": run_id,
        "timestamp": timestamp,
    }

    audit_entry = {
        "timestamp": timestamp,
        "run_id": run_id,
        "region": report.get("region", "N/A"),
        "decision": decision,
        "reviewer_note": reviewer_note,
    }
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(audit_entry) + "\n")

    return updated_report


def test_harness() -> None:
    """Exercise all 3 decision paths and print before/after state for each."""
    # Clear previous audit log for clean demo
    if AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.unlink()

    test_cases = [
        {
            "report": {"region": "Guntur", "context": "Sales surged +122.19% Apr->May.", "insight": "Largest swing.", "implication": "Investigate root cause."},
            "decision": "approve",
            "reviewer_note": "Numbers verified against SQL output. Approved for distribution.",
        },
        {
            "report": {"region": "Visakhapatnam", "context": "Sales dropped -62.46% Apr->May.", "insight": "Significant decline.", "implication": "Needs operational review."},
            "decision": "edit",
            "reviewer_note": "Add category breakdown before sending to regional lead.",
        },
        {
            "report": {"region": "Karimnagar", "context": "Sales dropped -44.00% May->Jun.", "insight": "Sharp decline.", "implication": "Investigate supply chain issues."},
            "decision": "reject",
            "reviewer_note": "Data may include test orders from Karimnagar, Re-validate source.",
        },
    ]

    for tc in test_cases:
        print(f"\n=== Decision: {tc['decision'].upper()} ({tc['report']['region']}) ===")
        print(f"BEFORE: {json.dumps(tc['report'], indent=2)}")
        result = review_gate_v1(tc["report"], tc["decision"], tc["reviewer_note"])
        print(f"AFTER: {json.dumps(result, indent=2)}")

    # Test invalid decision
    print("\n=== Testing invalid decision ===")
    try:
        review_gate_v1({"region": "Test"}, "maybe", "bad decision")
    except ValueError as e:
        print(f"Correctly rejected: {e}")

    # Print audit log
    print(f"\n=== Audit Log ({AUDIT_LOG_PATH}) ===")
    with open(AUDIT_LOG_PATH) as f:
        for line in f:
            entry = json.loads(line)
            print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    test_harness()