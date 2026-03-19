import argparse
import json
import os
import time
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional

from backend.models import ResearchApiResponse, ResearchContext
from backend.research_service import perform_research

DATASET_PATH = Path(__file__).resolve().parent / "dataset.jsonl"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "evals"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DeepIntel evaluation cases.")
    parser.add_argument("--dataset", default=str(DATASET_PATH), help="Path to a JSONL evaluation dataset.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on the number of cases to run.")
    parser.add_argument("--model", default=None, help="Optional GEMINI_MODEL override for the eval run.")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is required to run evaluations.")

    if args.model:
        os.environ["GEMINI_MODEL"] = args.model

    dataset = load_dataset(Path(args.dataset))
    if args.limit > 0:
        dataset = dataset[: args.limit]

    started_at = int(time.time() * 1000)
    case_results: List[Dict[str, Any]] = []

    for case in dataset:
        case_results.append(run_case(case, api_key))

    summary = summarize_cases(case_results, started_at)
    write_results(summary)
    print(json.dumps(summary, indent=2))
    return 0


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        payload = json.loads(stripped)
        if isinstance(payload, dict):
            cases.append(payload)
    return cases


def run_case(case: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    case_id = str(case.get("id") or case.get("topic") or "case")
    topic = str(case.get("topic") or "").strip()
    context_payload = case.get("context") if isinstance(case.get("context"), dict) else {}
    context = ResearchContext(**context_payload)
    expectations = case.get("expectations") if isinstance(case.get("expectations"), dict) else {}

    started_at = time.perf_counter()
    try:
        result = perform_research(topic, api_key, context)
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        scorecard = score_case(expectations, result, latency_ms)
        return {
            "id": case_id,
            "topic": topic,
            "status": "passed" if scorecard["passed"] else "failed",
            "latencyMs": latency_ms,
            "scorecard": scorecard,
            "evaluation": _model_to_dict(result.evaluation) if result.evaluation else None,
            "toolTraceCount": len(result.toolTraces),
            "planQuestionCount": len(result.plan.subQuestions) if result.plan else 0,
        }
    except Exception as error:  # noqa: BLE001
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        return {
            "id": case_id,
            "topic": topic,
            "status": "error",
            "latencyMs": latency_ms,
            "error": str(error),
        }


def score_case(expectations: Dict[str, Any], result: ResearchApiResponse, latency_ms: int) -> Dict[str, Any]:
    report = result.report
    evaluation = result.evaluation

    min_competitors = _safe_int(expectations.get("min_competitors"), default=3)
    min_citations = _safe_int(expectations.get("min_citations"), default=2)
    must_cover = [
        item.strip().lower()
        for item in expectations.get("must_cover", [])
        if isinstance(item, str) and item.strip()
    ]

    text_corpus = " ".join(
        [
            report.summary,
            " ".join(report.marketTrends),
            " ".join(report.recommendations),
            " ".join(competitor.name for competitor in report.competitors),
            " ".join(" ".join(competitor.features) for competitor in report.competitors),
            " ".join(" ".join(competitor.strengths) for competitor in report.competitors),
            " ".join(" ".join(competitor.weaknesses) for competitor in report.competitors),
        ]
    ).lower()

    covered_terms = [term for term in must_cover if term in text_corpus]
    coverage_rate = (len(covered_terms) / len(must_cover)) if must_cover else 1.0

    groundedness = evaluation.groundedness if evaluation else 0
    completeness = evaluation.completeness if evaluation else 0
    citation_coverage = evaluation.citationCoverage if evaluation else 0
    reflection_quality = evaluation.reflectionQuality if evaluation else 0

    passed = all(
        [
            len(report.competitors) >= min_competitors,
            len(report.citations) >= min_citations,
            coverage_rate >= 0.67,
            groundedness >= 45,
            completeness >= 55,
        ]
    )

    return {
        "passed": passed,
        "competitorCount": len(report.competitors),
        "citationCount": len(report.citations),
        "evidenceCount": len(report.evidence),
        "coverageRate": round(coverage_rate, 2),
        "coveredTerms": covered_terms,
        "openGapCount": len(report.gaps),
        "toolTraceCount": len(result.toolTraces),
        "latencyMs": latency_ms,
        "groundedness": groundedness,
        "completeness": completeness,
        "citationCoverage": citation_coverage,
        "reflectionQuality": reflection_quality,
    }


def summarize_cases(case_results: List[Dict[str, Any]], started_at: int) -> Dict[str, Any]:
    finished_at = int(time.time() * 1000)
    completed = [item for item in case_results if item.get("status") in {"passed", "failed"}]
    errors = [item for item in case_results if item.get("status") == "error"]
    passed = [item for item in completed if item.get("status") == "passed"]

    def avg(field: str) -> float:
        values = [item["scorecard"][field] for item in completed if item.get("scorecard") and field in item["scorecard"]]
        return round(mean(values), 2) if values else 0.0

    return {
        "startedAt": started_at,
        "finishedAt": finished_at,
        "caseCount": len(case_results),
        "completedCount": len(completed),
        "errorCount": len(errors),
        "passCount": len(passed),
        "passRate": round((len(passed) / len(completed)), 2) if completed else 0.0,
        "averageLatencyMs": avg("latencyMs"),
        "averageGroundedness": avg("groundedness"),
        "averageCompleteness": avg("completeness"),
        "averageCitationCoverage": avg("citationCoverage"),
        "averageReflectionQuality": avg("reflectionQuality"),
        "averageCoverageRate": avg("coverageRate"),
        "results": case_results,
    }


def write_results(payload: Dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = OUTPUT_DIR / f"eval-run-{int(time.time())}.json"
    filename.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _safe_int(value: Any, default: int) -> int:
    return value if isinstance(value, int) else default


def _model_to_dict(model: Optional[Any]) -> Optional[Dict[str, Any]]:
    if model is None:
        return None
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


if __name__ == "__main__":
    raise SystemExit(main())
