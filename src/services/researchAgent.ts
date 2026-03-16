import { GoogleGenAI } from "@google/genai";
import { ResearchStep, ResearchReport } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || '' });

export class ResearchAgent {
  private onStepUpdate: (step: ResearchStep) => void;

  constructor(onStepUpdate: (step: ResearchStep) => void) {
    this.onStepUpdate = onStepUpdate;
  }

  private addStep(type: ResearchStep['type'], message: string) {
    const step: ResearchStep = {
      id: Math.random().toString(36).substring(7),
      type,
      status: 'running',
      message,
      timestamp: Date.now(),
    };
    this.onStepUpdate(step);
    return step.id;
  }

  async performResearch(topic: string): Promise<ResearchReport> {
    // Step 1: Initial Broad Search
    this.addStep('search', `Searching for broad information on: ${topic}`);
    
    const initialSearchResponse = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `Perform a broad search to identify the top 3 competitors and their key market positions for: ${topic}. Provide a summary of what you find.`,
      config: {
        tools: [{ googleSearch: {} }],
      },
    });

    const initialFindings = initialSearchResponse.text || "No findings found.";
    this.addStep('analyze', "Analyzing initial search results and identifying competitors...");

    // Step 2: Recursive Deep Dive
    this.addStep('reflect', "Reflecting on gathered information to identify gaps (Recursive RAG)...");
    
    const reflectionResponse = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `Based on these initial findings: "${initialFindings}", what specific details are missing for a complete competitive analysis? (e.g., pricing tiers, specific enterprise features, recent news). List the top 3 missing items.`,
    });

    const gaps = reflectionResponse.text || "";
    this.addStep('search', `Performing targeted search for missing details: ${gaps.substring(0, 50)}...`);

    const deepDiveResponse = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `Search for and extract the following missing details for the competitors identified earlier: ${gaps}. Focus on pricing, features, and recent news.`,
      config: {
        tools: [{ googleSearch: {} }],
      },
    });

    const detailedFindings = deepDiveResponse.text || "";

    // Step 3: Final Compilation
    this.addStep('finalize', "Compiling final competitive intelligence report...");

    const finalReportResponse = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `Compile a comprehensive competitive intelligence report for "${topic}" based on all findings:
      Initial: ${initialFindings}
      Detailed: ${detailedFindings}
      
      The report MUST be in JSON format matching this structure:
      {
        "summary": "...",
        "competitors": [
          { "name": "...", "pricing": "...", "features": ["..."], "strengths": ["..."], "weaknesses": ["..."] }
        ],
        "marketTrends": ["..."],
        "recommendations": ["..."],
        "chartData": [
          { "name": "Competitor A", "featureScore": 85, "pricingScore": 70 },
          { "name": "Competitor B", "featureScore": 90, "pricingScore": 60 }
        ]
      }`,
      config: {
        responseMimeType: "application/json",
      },
    });

    try {
      const report = JSON.parse(finalReportResponse.text || "{}");
      this.addStep('finalize', "Research completed successfully.");
      return report;
    } catch (e) {
      console.error("Failed to parse report JSON", e);
      throw new Error("Failed to generate report structure.");
    }
  }
}
