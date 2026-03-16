import json
import os
import random
import time
from typing import Any, List, Optional

from google import genai
from google.genai import types

from backend.models import (
    ChartDatum,
    CompetitorData,
    ResearchApiResponse,
    ResearchReport,
    ResearchStep,
)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")


def _create_step(step_type: str, message: str) -> ResearchStep:
    return ResearchStep(
        id=format(random.randint(0, 16**8 - 1), "08x"),
        type=step_type,
        status="completed",
        message=message,
        timestamp=int(time.time() * 1000),
    )


def _normalize_string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, str) and item.strip()]


def _normalize_competitor(value: Any) -> Optional[CompetitorData]:
    if not isinstance(value, dict):
        return None

    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        return None

    pricing = value.get("pricing")

    return CompetitorData(
        name=name,
        pricing=pricing if isinstance(pricing, str) else None,
        features=_normalize_string_list(value.get("features")),
        strengths=_normalize_string_list(value.get("strengths")),
        weaknesses=_normalize_string_list(value.get("weaknesses")),
    )


def _normalize_chart_datum(value: Any) -> Optional[ChartDatum]:
    if not isinstance(value, dict):
        return None

    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        return None

    feature_score = value.get("featureScore")
    pricing_score = value.get("pricingScore")

    return ChartDatum(
        name=name,
        featureScore=feature_score if isinstance(feature_score, int) else 0,
        pricingScore=pricing_score if isinstance(pricing_score, int) else 0,
    )


def _normalize_report(value: Any) -> ResearchReport:
    if not isinstance(value, dict):
        raise ValueError("Failed to generate report structure.")

    competitors = []
    for competitor in value.get("competitors", []):
        normalized = _normalize_competitor(competitor)
        if normalized is not None:
            competitors.append(normalized)

    chart_data = []
    for entry in value.get("chartData", []):
        normalized = _normalize_chart_datum(entry)
        if normalized is not None:
            chart_data.append(normalized)

    return ResearchReport(
        summary=value.get("summary") if isinstance(value.get("summary"), str) else "",
        competitors=competitors,
        marketTrends=_normalize_string_list(value.get("marketTrends")),
        recommendations=_normalize_string_list(value.get("recommendations")),
        chartData=chart_data,
    )


def _search_tool_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )


def _json_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(response_mime_type="application/json")


def perform_research(topic: str, api_key: str) -> ResearchApiResponse:
    client = genai.Client(api_key=api_key)
    steps: List[ResearchStep] = []

    def add_step(step_type: str, message: str) -> None:
        steps.append(_create_step(step_type, message))

    add_step("search", f"Searching for broad information on: {topic}")

    initial_search_response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=f"Perform a broad search to identify the top 3 competitors and their key market positions for: {topic}. Provide a summary of what you find.",
        config=_search_tool_config(),
    )

    initial_findings = initial_search_response.text or "No findings found."
    add_step("analyze", "Analyzing initial search results and identifying competitors...")
    add_step("reflect", "Reflecting on gathered information to identify gaps (Recursive RAG)...")

    reflection_response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=f'Based on these initial findings: "{initial_findings}", what specific details are missing for a complete competitive analysis? (e.g., pricing tiers, specific enterprise features, recent news). List the top 3 missing items.',
    )

    gaps = reflection_response.text or ""
    add_step("search", f"Performing targeted search for missing details: {gaps[:50]}...")

    deep_dive_response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=f"Search for and extract the following missing details for the competitors identified earlier: {gaps}. Focus on pricing, features, and recent news.",
        config=_search_tool_config(),
    )

    detailed_findings = deep_dive_response.text or ""
    add_step("finalize", "Compiling final competitive intelligence report...")

    final_report_response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=f"""Compile a comprehensive competitive intelligence report for "{topic}" based on all findings:
Initial: {initial_findings}
Detailed: {detailed_findings}

The report MUST be in JSON format matching this structure:
{{
  "summary": "...",
  "competitors": [
    {{ "name": "...", "pricing": "...", "features": ["..."], "strengths": ["..."], "weaknesses": ["..."] }}
  ],
  "marketTrends": ["..."],
  "recommendations": ["..."],
  "chartData": [
    {{ "name": "Competitor A", "featureScore": 85, "pricingScore": 70 }},
    {{ "name": "Competitor B", "featureScore": 90, "pricingScore": 60 }}
  ]
}}""",
        config=_json_config(),
    )

    try:
        report = _normalize_report(json.loads(final_report_response.text or "{}"))
    except Exception as error:  # noqa: BLE001
        raise ValueError("Failed to generate report structure.") from error

    add_step("finalize", "Research completed successfully.")

    return ResearchApiResponse(report=report, steps=steps)
