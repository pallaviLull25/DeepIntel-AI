import re
from typing import List

from backend.retrieval.models import CorpusDocument, DocumentChunk

_WHITESPACE = re.compile(r"\s+")


def chunk_document(document: CorpusDocument, chunk_size: int = 120, overlap: int = 30) -> List[DocumentChunk]:
    words = _WHITESPACE.split(document.content.strip())
    if not words:
        return []

    chunks: List[DocumentChunk] = []
    index = 0
    step = max(1, chunk_size - overlap)

    while index < len(words):
        chunk_words = words[index : index + chunk_size]
        if not chunk_words:
            break

        text = " ".join(chunk_words).strip()
        chunk_id = f"{document.id}-chunk-{len(chunks) + 1}"
        chunks.append(
            DocumentChunk(
                id=chunk_id,
                documentId=document.id,
                topic=document.topic,
                title=document.title,
                sourceType=document.sourceType,
                text=text,
                url=document.url,
                citations=document.citations,
                tokenCount=len(chunk_words),
            )
        )

        if index + chunk_size >= len(words):
            break
        index += step

    return chunks
