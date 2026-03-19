from typing import List, Optional

from pydantic import BaseModel, Field


class ResearchStep(BaseModel):
    id: str
    type: str
    status: str
    message: str
    timestamp: int


class ResearchContext(BaseModel):
    region: Optional[str] = None
    companySize: Optional[str] = None
    budget: Optional[str] = None
    priorities: List[str] = Field(default_factory=list)


class ResearchPlan(BaseModel):
    objective: str
    subQuestions: List[str] = Field(default_factory=list)
    successCriteria: List[str] = Field(default_factory=list)


class Citation(BaseModel):
    title: str
    url: str
    domain: Optional[str] = None
    snippet: Optional[str] = None
    publishedAt: Optional[str] = None


class Evidence(BaseModel):
    id: str
    sourceType: str
    summary: str
    supports: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    query: Optional[str] = None
    excerpt: Optional[str] = None
    retrievalScore: Optional[float] = None
    lexicalScore: Optional[float] = None
    semanticScore: Optional[float] = None


class CoverageGap(BaseModel):
    topic: str
    reason: str
    severity: str = "medium"


class SectionScore(BaseModel):
    name: str
    score: int
    rationale: str


class ToolTrace(BaseModel):
    id: str
    toolName: str
    whyUsed: str
    inputSummary: str
    outputSummary: str
    success: bool
    latencyMs: int


class EvaluationSummary(BaseModel):
    groundedness: int
    completeness: int
    citationCoverage: int
    reflectionQuality: int
    notes: List[str] = Field(default_factory=list)


class CompetitorData(BaseModel):
    name: str
    pricing: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    confidence: Optional[int] = None


class ChartDatum(BaseModel):
    name: str
    featureScore: int
    pricingScore: int


class ResearchReport(BaseModel):
    summary: str
    competitors: List[CompetitorData] = Field(default_factory=list)
    marketTrends: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    chartData: List[ChartDatum] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    gaps: List[CoverageGap] = Field(default_factory=list)
    confidence: List[SectionScore] = Field(default_factory=list)


class ResearchApiResponse(BaseModel):
    report: ResearchReport
    steps: List[ResearchStep] = Field(default_factory=list)
    plan: Optional[ResearchPlan] = None
    toolTraces: List[ToolTrace] = Field(default_factory=list)
    evaluation: Optional[EvaluationSummary] = None


class ResearchRequest(BaseModel):
    topic: str
    context: Optional[ResearchContext] = None
