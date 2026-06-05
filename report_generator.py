"""Generate downloadable diagnosis reports."""

from __future__ import annotations

from typing import Dict


def generate_report(issue_description: str, diagnosis: Dict[str, object], timestamp: str) -> str:
    steps = format_list(diagnosis.get("troubleshooting_steps", []))
    commands = format_list(diagnosis.get("recommended_commands", []))
    prevention = format_list(diagnosis.get("prevention_tips", []))
    escalation = format_list(diagnosis.get("escalation_guidance", []))
    evidence = format_evidence(diagnosis.get("evidence", {}))

    return f"""AI Network Troubleshooting Assistant - Incident Report

Timestamp: {timestamp}
Category: {diagnosis.get("category", "Unknown")}
Severity: {diagnosis.get("severity", "Low")}
Confidence: {diagnosis.get("confidence_score", "N/A")}%
Source: {diagnosis.get("source", "AI/Rules")}

Issue Description
-----------------
{issue_description}

Business Impact
---------------
{diagnosis.get("impact", "Not available")}

Extracted Evidence
------------------
{evidence}

Probable Root Cause
-------------------
{diagnosis.get("root_cause", "Not available")}

Simple Explanation
------------------
{diagnosis.get("explanation", "Not available")}

Step-by-Step Troubleshooting Guide
----------------------------------
{steps}

Recommended Commands
--------------------
{commands}

Prevention Tips
---------------
{prevention}

Escalation Guidance
-------------------
{escalation}
"""


def format_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return "- Not available"
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def format_evidence(evidence: object) -> str:
    if not isinstance(evidence, dict):
        return "- Not available"

    lines = []
    labels = {
        "ip_addresses": "IP addresses",
        "domains": "Domains",
        "commands_detected": "Commands detected",
    }
    for key, label in labels.items():
        values = evidence.get(key, [])
        if values:
            lines.append(f"- {label}: {', '.join(str(value) for value in values)}")

    return "\n".join(lines) if lines else "- No explicit IP, domain, or command evidence detected"
