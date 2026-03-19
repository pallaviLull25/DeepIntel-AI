import math
import re
from collections import Counter
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Sequence, Set, Tuple

from backend.retrieval.models import DocumentChunk, RetrievedChunk

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "these",
    "this",
    "to",
    "what",
    "which",
    "with",
}


class HybridRetriever:
    def __init__(self, chunks: Sequence[DocumentChunk]) -> None:
        self.chunks = list(chunks)
        self.chunk_terms = [Counter(_tokenize(chunk.text)) for chunk in self.chunks]
        self.idf = self._build_idf(self.chunk_terms)

    def retrieve(self, query: str, top_k: int = 4) -> List[RetrievedChunk]:
        query_terms = _expand_query_terms(query)
        if not query_terms:
            return []

        scored: List[RetrievedChunk] = []
        for chunk, terms in zip(self.chunks, self.chunk_terms):
            lexical_score = _score_lexical(query_terms, terms, self.idf, chunk)
            semantic_score = _score_semantic(query, query_terms, chunk)
            score = round((lexical_score * 0.65) + (semantic_score * 0.35), 4)
            if score <= 0:
                continue

            scored.append(
                RetrievedChunk(
                    id=chunk.id,
                    documentId=chunk.documentId,
                    query=query,
                    title=chunk.title,
                    sourceType=chunk.sourceType,
                    text=chunk.text,
                    url=chunk.url,
                    citations=chunk.citations,
                    score=score,
                    lexicalScore=round(lexical_score, 4),
                    semanticScore=round(semantic_score, 4),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def _build_idf(self, chunk_terms: Sequence[Counter]) -> Dict[str, float]:
        document_count = max(1, len(chunk_terms))
        frequencies: Counter = Counter()
        for terms in chunk_terms:
            frequencies.update(terms.keys())

        return {
            term: math.log((1 + document_count) / (1 + frequency)) + 1.0
            for term, frequency in frequencies.items()
        }


def retrieve_for_queries(chunks: Sequence[DocumentChunk], queries: Iterable[str], top_k: int = 3) -> List[RetrievedChunk]:
    retriever = HybridRetriever(chunks)
    results: List[RetrievedChunk] = []
    seen_pairs: Set[Tuple[str, str]] = set()

    for query in queries:
        if not query.strip():
            continue

        for chunk in retriever.retrieve(query, top_k=top_k):
            key = (query, chunk.id)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            results.append(chunk)

    return results


def _tokenize(text: str) -> List[str]:
    return [
        token
        for token in _TOKEN_RE.findall(text.lower())
        if token not in _STOPWORDS and len(token) > 2
    ]


def _expand_query_terms(query: str) -> List[str]:
    tokens = _tokenize(query)
    expanded: List[str] = []
    seen: Set[str] = set()
    for token in tokens:
        for candidate in {token, _stem(token)}:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            expanded.append(candidate)
    return expanded


def _score_lexical(query_terms: Sequence[str], chunk_terms: Counter, idf: Dict[str, float], chunk: DocumentChunk) -> float:
    if not chunk_terms:
        return 0.0

    score = 0.0
    chunk_length = sum(chunk_terms.values()) or 1
    unique_query_terms = set(query_terms)

    for term in unique_query_terms:
        frequency = chunk_terms.get(term, 0)
        if not frequency:
            continue
        score += (frequency / chunk_length) * idf.get(term, 1.0)

    if chunk.citations:
        score += 0.12
    if chunk.sourceType == "citation_snippet":
        score += 0.08
    if chunk.sourceType == "fetched_page":
        score += 0.18
    if any(term in chunk.title.lower() for term in unique_query_terms):
        score += 0.05

    return score


def _score_semantic(query: str, query_terms: Sequence[str], chunk: DocumentChunk) -> float:
    query_text = query.lower().strip()
    chunk_text = chunk.text.lower()
    title_text = chunk.title.lower()

    token_overlap = _jaccard(set(query_terms), set(_expand_query_terms(chunk_text[:500])))
    title_overlap = _jaccard(set(query_terms), set(_expand_query_terms(title_text)))
    sequence_score = SequenceMatcher(None, query_text, f"{title_text} {chunk_text[:400]}").ratio()

    score = (token_overlap * 0.5) + (title_overlap * 0.2) + (sequence_score * 0.3)

    if chunk.sourceType == "fetched_page":
        score += 0.06

    return score


def _jaccard(left: Set[str], right: Set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left.intersection(right))
    union = len(left.union(right))
    return intersection / union if union else 0.0


def _stem(token: str) -> str:
    for suffix in ("ing", "ers", "ies", "ied", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            if suffix == "ies":
                return token[:-3] + "y"
            return token[: -len(suffix)]
    return token
