from typing import List, Optional

from pydantic import BaseModel


class ResearchStep(BaseModel):
    id: str
    type: str
    status: str
    message: str
    timestamp: int


class CompetitorData(BaseModel):
    name: str
    pricing: Optional[str] = None
    features: List[str]
    strengths: List[str]
    weaknesses: List[str]


class ChartDatum(BaseModel):
    name: str
    featureScore: int
    pricingScore: int


class ResearchReport(BaseModel):
    summary: str
    competitors: List[CompetitorData]
    marketTrends: List[str]
    recommendations: List[str]
    chartData: List[ChartDatum]


class ResearchApiResponse(BaseModel):
    report: ResearchReport
    steps: List[ResearchStep]


class ResearchRequest(BaseModel):
    topic: str
