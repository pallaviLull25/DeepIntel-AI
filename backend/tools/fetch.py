import re
import time
import uuid
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from typing import List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from backend.models import Citation, ToolTrace

MAX_FETCH_BYTES = 350_000
DEFAULT_TIMEOUT = 8
USER_AGENT = "IntelAtlasBot/0.1 (+https://example.local)"


@dataclass
class FetchedPage:
    citation: Citation
    title: str
    text: str
    trace: ToolTrace


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignore_depth = 0
        self._in_title = False
        self._title_parts: List[str] = []
        self._text_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self._ignore_depth += 1
            return
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignore_depth > 0:
            self._ignore_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag in {"p", "div", "section", "article", "main", "li", "h1", "h2", "h3", "h4", "br"}:
            self._text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._ignore_depth > 0:
            return

        text = _clean_text(data)
        if not text:
            return

        if self._in_title:
            self._title_parts.append(text)
            return

        self._text_parts.append(text)

    @property
    def title(self) -> str:
        return _clean_text(" ".join(self._title_parts))

    @property
    def text(self) -> str:
        return _collapse_text(self._text_parts)


def fetch_citation_pages(citations: List[Citation], max_pages: int = 4) -> Tuple[List[FetchedPage], List[ToolTrace]]:
    fetched_pages: List[FetchedPage] = []
    traces: List[ToolTrace] = []
    seen_urls = set()

    for citation in citations:
        url = citation.url.strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        page = fetch_page(citation)
        traces.append(page.trace)
        if page.text:
            fetched_pages.append(page)

        if len(fetched_pages) >= max_pages:
            break

    return fetched_pages, traces


def fetch_page(citation: Citation) -> FetchedPage:
    started_at = time.perf_counter()
    success = False
    title = citation.title
    text = ""

    try:
        request = Request(
            citation.url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        with urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            content_type = response.headers.get("Content-Type", "")
            charset = response.headers.get_content_charset() or "utf-8"
            raw = response.read(MAX_FETCH_BYTES)

        if "html" in content_type.lower() or not content_type:
            title, text = _parse_html(raw, charset, fallback_title=citation.title)
        else:
            text = _decode_bytes(raw, charset)

        text = _truncate(_clean_text(text), 20_000)
        title = title.strip() or citation.title
        success = bool(text)
    except (HTTPError, URLError, TimeoutError, ValueError):
        text = ""
        title = citation.title

    latency_ms = int((time.perf_counter() - started_at) * 1000)
    trace = ToolTrace(
        id=uuid.uuid4().hex[:8],
        toolName="fetch_page",
        whyUsed="Fetch full-page content for stronger retrieval grounding.",
        inputSummary=citation.url,
        outputSummary=_build_output_summary(title, text, success),
        success=success,
        latencyMs=latency_ms,
    )

    return FetchedPage(citation=citation, title=title, text=text, trace=trace)


def _parse_html(raw: bytes, charset: str, fallback_title: str) -> Tuple[str, str]:
    html = _decode_bytes(raw, charset)
    parser = _HTMLTextExtractor()
    parser.feed(html)
    title = parser.title or fallback_title
    text = parser.text
    return title, text


def _decode_bytes(raw: bytes, charset: str) -> str:
    try:
        return raw.decode(charset, errors="ignore")
    except LookupError:
        return raw.decode("utf-8", errors="ignore")


def _build_output_summary(title: str, text: str, success: bool) -> str:
    if not success:
        return "Failed to fetch or extract page content."
    word_count = len(text.split())
    return f"{title[:80]} ({word_count} words extracted)"


def _clean_text(value: str) -> str:
    value = unescape(value)
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def _collapse_text(parts: List[str]) -> str:
    joined = "\n".join(part for part in parts if part.strip())
    joined = re.sub(r"\n{2,}", "\n\n", joined)
    return joined.strip()


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def extract_domain(url: str) -> Optional[str]:
    parsed = urlparse(url)
    return parsed.netloc or None
