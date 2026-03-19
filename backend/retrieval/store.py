import json
import time
import uuid
from pathlib import Path
from typing import List, Optional

from backend.models import Citation
from backend.retrieval.chunking import chunk_document
from backend.retrieval.models import CorpusDocument, DocumentChunk
from backend.tools.fetch import FetchedPage
from backend.tools.search import SearchExecution


class LocalCorpusStore:
    def __init__(self, topic: str, base_dir: Optional[Path] = None) -> None:
        self.topic = topic
        self.base_dir = base_dir or (Path(__file__).resolve().parent.parent.parent / "data" / "corpus")

    def ingest_search_execution(self, source_label: str, execution: SearchExecution) -> List[CorpusDocument]:
        documents: List[CorpusDocument] = []
        summary_url = execution.citations[0].url if execution.citations else None

        documents.append(
            CorpusDocument(
                id=f"{source_label}-summary-{uuid.uuid4().hex[:8]}",
                topic=self.topic,
                title=f"{source_label.replace('_', ' ').title()} findings for {self.topic}",
                sourceType=source_label,
                content=execution.text.strip(),
                url=summary_url,
                citations=execution.citations,
            )
        )

        for citation in execution.citations:
            snippet_parts = [citation.title.strip()]
            if citation.snippet:
                snippet_parts.append(citation.snippet.strip())

            content = " ".join(part for part in snippet_parts if part).strip()
            if not content:
                continue

            documents.append(
                CorpusDocument(
                    id=f"citation-{uuid.uuid4().hex[:8]}",
                    topic=self.topic,
                    title=citation.title.strip(),
                    sourceType="citation_snippet",
                    content=content,
                    url=citation.url,
                    citations=[citation],
                )
            )

        return documents

    def build_chunk_index(self, documents: List[CorpusDocument]) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        for document in documents:
            chunks.extend(chunk_document(document))
        return chunks

    def ingest_fetched_pages(self, pages: List[FetchedPage]) -> List[CorpusDocument]:
        documents: List[CorpusDocument] = []
        for page in pages:
            if not page.text.strip():
                continue

            documents.append(
                CorpusDocument(
                    id=f"page-{uuid.uuid4().hex[:8]}",
                    topic=self.topic,
                    title=page.title.strip() or page.citation.title.strip(),
                    sourceType="fetched_page",
                    content=page.text.strip(),
                    url=page.citation.url,
                    citations=[page.citation],
                )
            )

        return documents

    def persist_run(self, documents: List[CorpusDocument], chunks: List[DocumentChunk]) -> None:
        run_dir = self.base_dir / _slugify(self.topic)
        run_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "topic": self.topic,
            "createdAt": int(time.time() * 1000),
            "documents": [_model_to_dict(document) for document in documents],
            "chunks": [_model_to_dict(chunk) for chunk in chunks],
        }
        filename = f"run-{int(time.time())}.json"
        (run_dir / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def merge_citations(*citation_groups: List[Citation]) -> List[Citation]:
    deduped: List[Citation] = []
    seen = set()

    for group in citation_groups:
        for citation in group:
            key = citation.url.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(citation)

    return deduped


def _slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    return cleaned or "research-run"


def _model_to_dict(model) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
