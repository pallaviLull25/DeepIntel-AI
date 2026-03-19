import json
from dataclasses import dataclass
from typing import List

from google.genai import types

from backend.models import CoverageGap, ResearchPlan


@dataclass
class CritiqueResult:
    summary: str
    missing_items: List[str]
    gaps: List[CoverageGap]


def reflect_on_findings(client, model: str, topic: str, plan: ResearchPlan, findings: str) -> CritiqueResult:
    prompt = f"""Review the current research notes for "{topic}".

Objective:
{plan.objective}

Sub-questions:
{chr(10).join(f"- {item}" for item in plan.subQuestions)}

Current findings:
{findings}

Return JSON with this structure:
{{
  "summary": "...",
  "missingItems": ["..."],
  "gaps": [
    {{"topic": "...", "reason": "...", "severity": "low|medium|high"}}
  ]
}}

Focus on the top missing details required for a credible competitive analysis.
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    payload = _parse_payload(response.text or "")
    missing_items = _normalize_missing_items(payload.get("missingItems"))
    gaps = _normalize_gaps(payload.get("gaps"), missing_items)
    summary = payload.get("summary") if isinstance(payload.get("summary"), str) else ""

    if not summary:
        summary = "Identified follow-up research gaps for pricing, feature depth, and recent developments."

    return CritiqueResult(summary=summary, missing_items=missing_items, gaps=gaps)


def _parse_payload(text: str) -> dict:
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def _normalize_missing_items(value) -> List[str]:
    if not isinstance(value, list):
        return []

    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _normalize_gaps(value, missing_items: List[str]) -> List[CoverageGap]:
    gaps: List[CoverageGap] = []
    if isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                continue

            topic = item.get("topic")
            reason = item.get("reason")
            severity = item.get("severity")
            if not isinstance(topic, str) or not topic.strip():
                continue
            if not isinstance(reason, str) or not reason.strip():
                continue

            gaps.append(
                CoverageGap(
                    topic=topic.strip(),
                    reason=reason.strip(),
                    severity=severity if isinstance(severity, str) and severity.strip() else "medium",
                )
            )

    if gaps:
        return gaps

    return [
        CoverageGap(topic=item, reason="The initial evidence does not answer this point clearly.", severity="medium")
        for item in missing_items[:3]
    ]
