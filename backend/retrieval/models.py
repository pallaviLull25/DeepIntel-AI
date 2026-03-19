from typing import List, Optional

from pydantic import BaseModel, Field

from backend.models import Citation


class CorpusDocument(BaseModel):
    id: str
    topic: str
    title: str
    sourceType: str
    content: str
    url: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    id: str
    documentId: str
    topic: str
    title: str
    sourceType: str
    text: str
    url: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)
    tokenCount: int = 0


class RetrievedChunk(BaseModel):
    id: str
    documentId: str
    query: str
    title: str
    sourceType: str
    text: str
    url: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)
    score: float
    lexicalScore: float = 0.0
    semanticScore: float = 0.0
