from typing import List

from backend.agents.critic import CritiqueResult
from backend.models import EvaluationSummary, ResearchPlan, ResearchReport, ToolTrace


def summarize_run(
    plan: ResearchPlan,
    report: ResearchReport,
    critique: CritiqueResult,
    tool_traces: List[ToolTrace],
) -> EvaluationSummary:
    competitor_count = len(report.competitors)
    citation_count = len(report.citations)
    evidence_count = len(report.evidence)
    resolved_gaps = max(0, len(critique.missing_items) - len(report.gaps))

    completeness = 0
    if report.summary.strip():
        completeness += 20
    if competitor_count >= 3:
        completeness += 30
    elif competitor_count > 0:
        completeness += 15
    if report.marketTrends:
        completeness += 20
    if report.recommendations:
        completeness += 20
    if report.chartData:
        completeness += 10

    groundedness = min(100, 25 + (citation_count * 12) + (evidence_count * 8))
    citation_coverage = min(100, citation_count * 20)

    reflection_quality = 40
    if critique.missing_items:
        reflection_quality += 20
    if len(tool_traces) > 1:
        reflection_quality += 20
    if resolved_gaps > 0 or not report.gaps:
        reflection_quality += 20

    notes = [
        f"Plan covered {len(plan.subQuestions)} research questions.",
        f"Captured {citation_count} citation(s) and {evidence_count} grounded evidence item(s) across {len(tool_traces)} tool call(s).",
    ]
    if report.gaps:
        notes.append(f"{len(report.gaps)} coverage gap(s) remain open in the final report.")
    else:
        notes.append("No unresolved coverage gaps were carried into the final report.")

    return EvaluationSummary(
        groundedness=max(0, min(100, groundedness)),
        completeness=max(0, min(100, completeness)),
        citationCoverage=max(0, min(100, citation_coverage)),
        reflectionQuality=max(0, min(100, reflection_quality)),
        notes=notes,
    )
