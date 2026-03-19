import re
import time
import uuid
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Set
from urllib.parse import urlparse

from google.genai import types

from backend.models import Citation, ToolTrace


@dataclass
class SearchExecution:
    text: str
    citations: List[Citation]
    trace: ToolTrace


def run_google_search(client, model: str, prompt: str, why_used: str) -> SearchExecution:
    started_at = time.perf_counter()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]),
    )
    latency_ms = int((time.perf_counter() - started_at) * 1000)
    text = response.text or "No findings found."
    citations = extract_citations(response, text)

    trace = ToolTrace(
        id=uuid.uuid4().hex[:8],
        toolName="google_search",
        whyUsed=why_used,
        inputSummary=_truncate(prompt, 160),
        outputSummary=_truncate(text, 180),
        success=bool(text.strip()),
        latencyMs=latency_ms,
    )

    return SearchExecution(text=text, citations=citations, trace=trace)


def extract_citations(response, text: str) -> List[Citation]:
    citations = _extract_from_payload(_response_to_payload(response))
    if citations:
        return _dedupe_citations(citations)

    return _extract_from_text(text)


def _response_to_payload(response) -> Any:
    for method_name in ("to_json_dict", "model_dump", "to_dict"):
        method = getattr(response, method_name, None)
        if callable(method):
            try:
                return method()
            except TypeError:
                continue
    return None


def _extract_from_payload(payload: Any) -> List[Citation]:
    if payload is None:
        return []

    citations: List[Citation] = []
    for node in _walk(payload):
        if not isinstance(node, dict):
            continue

        candidate = node.get("web") if isinstance(node.get("web"), dict) else node
        url = candidate.get("uri") or candidate.get("url")
        title = candidate.get("title")
        snippet = candidate.get("snippet")

        if not isinstance(url, str) or not url.strip():
            continue

        label = title if isinstance(title, str) and title.strip() else url
        citations.append(
            Citation(
                title=label.strip(),
                url=url.strip(),
                domain=_extract_domain(url),
                snippet=snippet.strip() if isinstance(snippet, str) and snippet.strip() else None,
            )
        )

    return _dedupe_citations(citations)


def _extract_from_text(text: str) -> List[Citation]:
    urls = re.findall(r"https?://[^\s)>\]]+", text)
    citations = [
        Citation(
            title=url,
            url=url,
            domain=_extract_domain(url),
        )
        for url in urls
    ]
    return _dedupe_citations(citations)


def _walk(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _dedupe_citations(citations: List[Citation]) -> List[Citation]:
    deduped: List[Citation] = []
    seen: Set[str] = set()
    for citation in citations:
        key = citation.url.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(citation)
    return deduped


def _extract_domain(url: str) -> Optional[str]:
    parsed = urlparse(url)
    return parsed.netloc or None


def _truncate(value: str, limit: int) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."
