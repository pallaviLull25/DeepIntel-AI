export interface ResearchStep {
  id: string;
  type: 'search' | 'analyze' | 'scrape' | 'reflect' | 'finalize';
  status: 'pending' | 'running' | 'completed' | 'error';
  message: string;
  timestamp: number;
}

export interface CompetitorData {
  name: string;
  pricing?: string;
  features: string[];
  strengths: string[];
  weaknesses: string[];
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
}

export interface ResearchApiResponse {
  report: ResearchReport;
  steps: ResearchStep[];
}
