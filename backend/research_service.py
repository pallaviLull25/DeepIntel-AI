import os
import random
import time
from typing import Any, List, Optional, Sequence, Tuple

from google import genai

from backend.agents.critic import CritiqueResult, reflect_on_findings
from backend.agents.planner import build_research_plan
from backend.agents.synthesizer import synthesize_report_payload
from backend.evals.metrics import summarize_run
from backend.models import (
    ChartDatum,
    Citation,
    CompetitorData,
    CoverageGap,
    Evidence,
    ResearchApiResponse,
    ResearchContext,
    ResearchPlan,
    ResearchReport,
    ResearchStep,
    SectionScore,
    ToolTrace,
)
from backend.retrieval.models import CorpusDocument, DocumentChunk, RetrievedChunk
from backend.retrieval.search import retrieve_for_queries
from backend.retrieval.store import LocalCorpusStore, merge_citations
from backend.tools.fetch import FetchedPage, fetch_citation_pages
from backend.tools.search import SearchExecution, run_google_search

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

    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _normalize_competitor(value: Any) -> Optional[CompetitorData]:
    if not isinstance(value, dict):
        return None

    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        return None

    pricing = value.get("pricing")
    confidence = value.get("confidence")

    return CompetitorData(
        name=name.strip(),
        pricing=pricing if isinstance(pricing, str) and pricing.strip() else None,
        features=_normalize_string_list(value.get("features")),
        strengths=_normalize_string_list(value.get("strengths")),
        weaknesses=_normalize_string_list(value.get("weaknesses")),
        confidence=confidence if isinstance(confidence, int) else None,
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
        name=name.strip(),
        featureScore=feature_score if isinstance(feature_score, int) else 0,
        pricingScore=pricing_score if isinstance(pricing_score, int) else 0,
    )


def _normalize_section_scores(value: Any, summary: str, competitors: List[CompetitorData], gaps: List[CoverageGap], citations: List[Citation]) -> List[SectionScore]:
    scores: List[SectionScore] = []

    if isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                continue

            name = item.get("name")
            score = item.get("score")
            rationale = item.get("rationale")
            if not isinstance(name, str) or not name.strip():
                continue
            if not isinstance(score, int):
                continue
            if not isinstance(rationale, str) or not rationale.strip():
                continue

            scores.append(SectionScore(name=name.strip(), score=max(0, min(100, score)), rationale=rationale.strip()))

    if scores:
        return scores

    competitor_score = 45
    if len(competitors) >= 3:
        competitor_score = 80
    elif competitors:
        competitor_score = 65

    citation_score = 40 + (len(citations) * 10)
    if gaps:
        citation_score -= min(30, len(gaps) * 10)

    return [
        SectionScore(
            name="summary",
            score=85 if summary.strip() else 30,
            rationale="Based on whether a usable executive summary was produced.",
        ),
        SectionScore(
            name="competitors",
            score=max(0, min(100, competitor_score)),
            rationale="Based on the number of competitor profiles populated in the report.",
        ),
        SectionScore(
            name="grounding",
            score=max(0, min(100, citation_score)),
            rationale="Based on extracted citations and unresolved coverage gaps.",
        ),
    ]


def _normalize_report(
    value: Any,
    citations: List[Citation],
    evidence: List[Evidence],
    gaps: List[CoverageGap],
) -> ResearchReport:
    if not isinstance(value, dict):
        raise ValueError("Failed to generate report structure.")

    competitors: List[CompetitorData] = []
    for competitor in value.get("competitors", []):
        normalized = _normalize_competitor(competitor)
        if normalized is not None:
            competitors.append(normalized)

    chart_data: List[ChartDatum] = []
    for entry in value.get("chartData", []):
        normalized = _normalize_chart_datum(entry)
        if normalized is not None:
            chart_data.append(normalized)

    summary = value.get("summary") if isinstance(value.get("summary"), str) else ""
    confidence = _normalize_section_scores(value.get("confidence"), summary, competitors, gaps, citations)

    return ResearchReport(
        summary=summary,
        competitors=competitors,
        marketTrends=_normalize_string_list(value.get("marketTrends")),
        recommendations=_normalize_string_list(value.get("recommendations")),
        chartData=chart_data,
        citations=citations,
        evidence=evidence,
        gaps=gaps,
        confidence=confidence,
    )


class ResearchOrchestrator:
    def __init__(self, topic: str, api_key: str, context: Optional[ResearchContext] = None) -> None:
        self.topic = topic
        self.context = context or ResearchContext()
        self.client = genai.Client(api_key=api_key)
        self.steps: List[ResearchStep] = []
        self.tool_traces: List[ToolTrace] = []
        self.plan: Optional[ResearchPlan] = None

    def run(self) -> ResearchApiResponse:
        self.plan = build_research_plan(self.topic, self.context)
        self._add_step("plan", "Building a research plan and defining success criteria...")

        self._add_step("search", f"Searching for broad information on: {self.topic}")
        initial_search = run_google_search(
            self.client,
            DEFAULT_MODEL,
            _build_broad_search_prompt(self.topic, self.plan, self.context),
            "Establish the competitor landscape and baseline market positioning.",
        )
        self.tool_traces.append(initial_search.trace)

        self._add_step("analyze", "Analyzing initial search results and identifying competitors...")
        self._add_step("reflect", "Reflecting on gathered information to identify gaps...")
        critique = reflect_on_findings(self.client, DEFAULT_MODEL, self.topic, self.plan, initial_search.text)

        findings = [initial_search.text]
        citations = list(initial_search.citations)
        executions: List[Tuple[str, SearchExecution, List[str]]] = [("broad_search", initial_search, self.plan.subQuestions)]

        if critique.missing_items:
            gaps_summary = ", ".join(critique.missing_items[:3])
            self._add_step("search", f"Performing targeted search for missing details: {gaps_summary[:60]}...")
            deep_search = run_google_search(
                self.client,
                DEFAULT_MODEL,
                _build_gap_search_prompt(self.topic, self.plan, critique),
                "Fill the evidence gaps identified by the critic step.",
            )
            findings.append(deep_search.text)
            citations.extend(deep_search.citations)
            self.tool_traces.append(deep_search.trace)
            executions.append(("gap_follow_up", deep_search, critique.missing_items))

        fetched_pages: List[FetchedPage] = []
        fetch_candidates = _dedupe_citations(citations)
        if fetch_candidates:
            self._add_step("scrape", "Fetching cited pages for fuller source grounding...")
            fetched_pages, fetch_traces = fetch_citation_pages(fetch_candidates, max_pages=4)
            self.tool_traces.extend(fetch_traces)

        self._add_step("retrieve", "Indexing gathered source material into the local retrieval store...")
        documents, chunks = _build_local_corpus(self.topic, executions, fetched_pages)
        if documents and chunks:
            LocalCorpusStore(self.topic).persist_run(documents, chunks)

        self._add_step("retrieve", "Retrieving the most relevant evidence passages for the research plan...")
        retrieval_queries = _build_retrieval_queries(self.plan, critique)
        retrieved_chunks = retrieve_for_queries(chunks, retrieval_queries, top_k=2)
        evidence = _build_grounded_evidence(retrieved_chunks, executions)
        grounded_citations = merge_citations(citations, *[chunk.citations for chunk in retrieved_chunks])

        self._add_step("finalize", "Compiling final competitive intelligence report...")
        synthesis_payload = synthesize_report_payload(
            self.client,
            DEFAULT_MODEL,
            self.topic,
            self.plan,
            self.context,
            findings,
            retrieved_chunks,
            grounded_citations,
            critique,
        )

        if not synthesis_payload:
            raise ValueError("Failed to generate report structure.")

        unresolved_gaps = _resolve_gaps(critique.gaps, findings, retrieved_chunks)
        report = _normalize_report(synthesis_payload, grounded_citations, evidence, unresolved_gaps)
        evaluation = summarize_run(self.plan, report, critique, self.tool_traces)

        self._add_step("finalize", "Research completed successfully.")
        return ResearchApiResponse(
            report=report,
            steps=self.steps,
            plan=self.plan,
            toolTraces=self.tool_traces,
            evaluation=evaluation,
        )

    def _add_step(self, step_type: str, message: str) -> None:
        self.steps.append(_create_step(step_type, message))


def perform_research(topic: str, api_key: str, context: Optional[ResearchContext] = None) -> ResearchApiResponse:
    return ResearchOrchestrator(topic, api_key, context).run()


def _build_broad_search_prompt(topic: str, plan: ResearchPlan, context: ResearchContext) -> str:
    context_lines = [
        f"Region: {context.region or 'Not specified'}",
        f"Company size: {context.companySize or 'Not specified'}",
        f"Budget: {context.budget or 'Not specified'}",
        "Priorities: " + (", ".join(context.priorities) if context.priorities else "Not specified"),
    ]

    return f"""Perform a broad search for "{topic}".

Research objective:
{plan.objective}

Context:
{chr(10).join(context_lines)}

Questions to answer:
{chr(10).join(f"- {item}" for item in plan.subQuestions)}

Return a concise narrative identifying the top competitors, their market position, and any notable pricing or product differences.
"""


def _build_gap_search_prompt(topic: str, plan: ResearchPlan, critique: CritiqueResult) -> str:
    missing_items = "\n".join(f"- {item}" for item in critique.missing_items) if critique.missing_items else "- No additional gaps listed"
    return f"""Perform a targeted search for "{topic}" to close these research gaps:
{missing_items}

Original objective:
{plan.objective}

Return the specific pricing details, product features, or recent developments that address these gaps.
"""


def _build_local_corpus(
    topic: str,
    executions: Sequence[Tuple[str, SearchExecution, List[str]]],
    fetched_pages: Sequence[FetchedPage],
) -> Tuple[List[CorpusDocument], List[DocumentChunk]]:
    store = LocalCorpusStore(topic)
    documents: List[CorpusDocument] = []
    for source_type, execution, _supports in executions:
        documents.extend(store.ingest_search_execution(source_type, execution))
    documents.extend(store.ingest_fetched_pages(list(fetched_pages)))

    return documents, store.build_chunk_index(documents)


def _build_retrieval_queries(plan: ResearchPlan, critique: CritiqueResult) -> List[str]:
    queries: List[str] = []
    seen = set()

    for candidate in list(plan.subQuestions) + list(critique.missing_items):
        if not candidate or not candidate.strip():
            continue
        normalized = candidate.strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        queries.append(normalized)

    return queries


def _build_grounded_evidence(
    retrieved_chunks: Sequence[RetrievedChunk],
    executions: Sequence[Tuple[str, SearchExecution, List[str]]],
) -> List[Evidence]:
    if not retrieved_chunks:
        return _build_fallback_evidence(executions)

    grouped: dict[str, List[RetrievedChunk]] = {}
    for chunk in retrieved_chunks:
        grouped.setdefault(chunk.query, []).append(chunk)

    evidence: List[Evidence] = []
    for index, (query, matches) in enumerate(grouped.items(), start=1):
        citations = merge_citations(*[match.citations for match in matches])
        top_match = matches[0]
        combined_text = " ".join(match.text for match in matches[:2]).strip()
        evidence.append(
            Evidence(
                id=f"evidence-{index}",
                sourceType=top_match.sourceType,
                summary=_truncate(combined_text, 320),
                supports=[query],
                citations=citations[:5],
                query=query,
                excerpt=top_match.text,
                retrievalScore=top_match.score,
                lexicalScore=top_match.lexicalScore,
                semanticScore=top_match.semanticScore,
            )
        )
    return evidence


def _build_fallback_evidence(executions: Sequence[Tuple[str, SearchExecution, List[str]]]) -> List[Evidence]:
    evidence: List[Evidence] = []
    for index, (source_type, execution, supports) in enumerate(executions, start=1):
        evidence.append(
            Evidence(
                id=f"evidence-{index}",
                sourceType=source_type,
                summary=_truncate(execution.text, 320),
                supports=[item for item in supports if item][:4],
                citations=execution.citations[:5],
                excerpt=_truncate(execution.text, 220),
            )
        )
    return evidence


def _resolve_gaps(gaps: List[CoverageGap], findings: List[str], retrieved_chunks: Sequence[RetrievedChunk]) -> List[CoverageGap]:
    if not gaps:
        return []

    combined = " ".join(findings + [chunk.text for chunk in retrieved_chunks]).lower()
    unresolved: List[CoverageGap] = []

    for gap in gaps:
        keywords = [token.lower() for token in gap.topic.split() if len(token) > 3]
        if keywords and any(keyword in combined for keyword in keywords[:3]):
            continue
        unresolved.append(gap)

    return unresolved


def _dedupe_citations(citations: List[Citation]) -> List[Citation]:
    deduped: List[Citation] = []
    seen_urls = set()
    for citation in citations:
        url = citation.url.strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(citation)
    return deduped


def _truncate(value: str, limit: int) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."
