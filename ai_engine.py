"""Groq-powered diagnosis engine with deterministic fallback support."""

from __future__ import annotations

import json
import os
from dotenv import load_dotenv


from typing import Dict

from groq import Groq

from classifier import build_impact_summary, escalation_guidance, extract_evidence, fallback_diagnosis

load_dotenv()
print("GROQ KEY FOUND:", bool(os.getenv("GROQ_API_KEY")))
MODEL_NAME = "llama-3.1-8b-instant"


def diagnose_with_ai(user_input: str, category: str, severity: str) -> Dict[str, object]:
    """Generate a structured diagnosis using Groq, or fall back gracefully."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        diagnosis = fallback_diagnosis(user_input, category, severity)
        diagnosis["api_status"] = "GROQ_API_KEY is missing. Showing rule-based diagnosis."
        return diagnosis

    system_prompt = """
You are an AI Network Troubleshooting Assistant for beginner-friendly enterprise support.
Return only valid JSON with these keys:
root_cause, explanation, category, severity, impact, confidence, confidence_score,
troubleshooting_steps, recommended_commands, prevention_tips, escalation_guidance.
troubleshooting_steps, recommended_commands, prevention_tips, and escalation_guidance must be arrays of strings.
confidence_score must be an integer from 0 to 100.
Keep the answer professional, concise, practical, and suitable for Cisco/software engineering interview discussion.
"""

    user_prompt = f"""
Network issue description or logs:
{user_input}

Rule-based detected category: {category}
Rule-based severity: {severity}

Use the detected category unless the evidence strongly suggests a better one.
"""

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        diagnosis = json.loads(content or "{}")
        return normalize_diagnosis(diagnosis, category, severity, user_input)
    except Exception as exc:
        diagnosis = fallback_diagnosis(user_input, category, severity)
        diagnosis["api_status"] = f"Groq API failed. Showing rule-based diagnosis. Error: {exc}"
        return diagnosis


def normalize_diagnosis(
    diagnosis: Dict[str, object], category: str, severity: str, user_input: str = ""
) -> Dict[str, object]:
    """Ensure the AI response has the fields expected by the UI and database."""
    normalized_category = str(diagnosis.get("category") or category)
    normalized_severity = str(diagnosis.get("severity") or severity)
    normalized = {
        "root_cause": diagnosis.get("root_cause") or "Root cause requires more evidence.",
        "explanation": diagnosis.get("explanation") or "The available symptoms need additional validation.",
        "category": normalized_category,
        "severity": normalized_severity,
        "impact": diagnosis.get("impact") or build_impact_summary(normalized_category, normalized_severity),
        "confidence": diagnosis.get("confidence") or "AI-assisted",
        "confidence_score": normalize_score(diagnosis.get("confidence_score")),
        "evidence": extract_evidence(user_input),
        "troubleshooting_steps": ensure_list(diagnosis.get("troubleshooting_steps")),
        "recommended_commands": ensure_list(diagnosis.get("recommended_commands")),
        "prevention_tips": ensure_list(diagnosis.get("prevention_tips")),
        "escalation_guidance": ensure_list(diagnosis.get("escalation_guidance"))
        if diagnosis.get("escalation_guidance")
        else escalation_guidance(normalized_category, normalized_severity),
        "source": "Groq AI",
    }
    return normalized


def ensure_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return ["Collect more evidence and retry the diagnosis."]


def normalize_score(value: object) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 78
    return max(0, min(100, score))

