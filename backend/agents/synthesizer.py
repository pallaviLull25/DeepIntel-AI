import json
from typing import Any, Dict, List, Optional

from google.genai import types

from backend.agents.critic import CritiqueResult
from backend.models import Citation, ResearchContext, ResearchPlan
from backend.retrieval.models import RetrievedChunk


def synthesize_report_payload(
    client,
    model: str,
    topic: str,
    plan: ResearchPlan,
    context: Optional[ResearchContext],
    findings: List[str],
    retrieved_chunks: List[RetrievedChunk],
    citations: List[Citation],
    critique: CritiqueResult,
) -> Dict[str, Any]:
    context = context or ResearchContext()
    context_lines = _format_context(context)
    citation_lines = _format_citations(citations)
    findings_block = "\n\n".join(findings)
    grounding_block = _format_retrieved_chunks(retrieved_chunks)

    prompt = f"""Compile a competitive intelligence report for "{topic}".

Research objective:
{plan.objective}

Context:
{context_lines}

Success criteria:
{chr(10).join(f"- {item}" for item in plan.successCriteria)}

Research findings:
{findings_block}

Retrieved evidence:
{grounding_block}

Known gaps:
{critique.summary}
{chr(10).join(f"- {gap.topic}: {gap.reason}" for gap in critique.gaps) if critique.gaps else "- None"}

Available citations:
{citation_lines}

Return JSON with this exact structure:
{{
  "summary": "...",
  "competitors": [
    {{
      "name": "...",
      "pricing": "...",
      "features": ["..."],
      "strengths": ["..."],
      "weaknesses": ["..."],
      "confidence": 0
    }}
  ],
  "marketTrends": ["..."],
  "recommendations": ["..."],
  "chartData": [
    {{
      "name": "...",
      "featureScore": 0,
      "pricingScore": 0
    }}
  ],
  "confidence": [
    {{
      "name": "...",
      "score": 0,
      "rationale": "..."
    }}
  ]
}}

Use the retrieved evidence as the primary grounding source. Use only the supplied findings and evidence. Keep the report concise and concrete.
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    try:
        payload = json.loads(response.text or "{}")
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def _format_context(context: ResearchContext) -> str:
    lines = [
        f"Region: {context.region or 'Not specified'}",
        f"Company size: {context.companySize or 'Not specified'}",
        f"Budget: {context.budget or 'Not specified'}",
        "Priorities: " + (", ".join(context.priorities) if context.priorities else "Not specified"),
    ]
    return "\n".join(lines)


def _format_citations(citations: List[Citation]) -> str:
    if not citations:
        return "- No explicit citations were extracted from the search responses."

    return "\n".join(f"- {citation.title}: {citation.url}" for citation in citations[:10])


def _format_retrieved_chunks(retrieved_chunks: List[RetrievedChunk]) -> str:
    if not retrieved_chunks:
        return "- No retrieved passages were available."

    lines = []
    for chunk in retrieved_chunks[:12]:
        citation_url = chunk.citations[0].url if chunk.citations else (chunk.url or "No URL")
        lines.append(
            f"- Query: {chunk.query}\n"
            f"  Source: {chunk.title}\n"
            f"  Score: {chunk.score}\n"
            f"  Evidence: {chunk.text}\n"
            f"  Citation: {citation_url}"
        )

    return "\n".join(lines)
