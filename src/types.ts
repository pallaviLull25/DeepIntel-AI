export interface ResearchStep {
  id: string;
  type: 'plan' | 'search' | 'retrieve' | 'analyze' | 'scrape' | 'reflect' | 'finalize';
  status: 'pending' | 'running' | 'completed' | 'error';
  message: string;
  timestamp: number;
}

export interface ResearchContext {
  region?: string;
  companySize?: string;
  budget?: string;
  priorities: string[];
}

export interface ResearchPlan {
  objective: string;
  subQuestions: string[];
  successCriteria: string[];
}

export interface Citation {
  title: string;
  url: string;
  domain?: string;
  snippet?: string;
  publishedAt?: string;
}

export interface Evidence {
  id: string;
  sourceType: string;
  summary: string;
  supports: string[];
  citations: Citation[];
  query?: string;
  excerpt?: string;
  retrievalScore?: number;
  lexicalScore?: number;
  semanticScore?: number;
}

export interface CoverageGap {
  topic: string;
  reason: string;
  severity: string;
}

export interface SectionScore {
  name: string;
  score: number;
  rationale: string;
}

export interface ToolTrace {
  id: string;
  toolName: string;
  whyUsed: string;
  inputSummary: string;
  outputSummary: string;
  success: boolean;
  latencyMs: number;
}

export interface EvaluationSummary {
  groundedness: number;
  completeness: number;
  citationCoverage: number;
  reflectionQuality: number;
  notes: string[];
}

export interface CompetitorData {
  name: string;
  pricing?: string;
  features: string[];
  strengths: string[];
  weaknesses: string[];
  confidence?: number;
}

export interface ChartDatum {
  name: string;
  featureScore: number;
  pricingScore: number;
}

export interface ResearchReport {
  summary: string;
  competitors: CompetitorData[];
  marketTrends: string[];
  recommendations: string[];
  chartData: ChartDatum[];
  citations: Citation[];
  evidence: Evidence[];
  gaps: CoverageGap[];
  confidence: SectionScore[];
}

export interface ResearchApiResponse {
  report: ResearchReport;
  steps: ResearchStep[];
  plan?: ResearchPlan;
  toolTraces?: ToolTrace[];
  evaluation?: EvaluationSummary;
}
