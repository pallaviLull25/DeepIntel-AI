import { ResearchApiResponse, ResearchStep } from "../types";

export class ResearchAgent {
  private onStepUpdate: (step: ResearchStep) => void;

  constructor(onStepUpdate: (step: ResearchStep) => void) {
    this.onStepUpdate = onStepUpdate;
  }

  async performResearch(topic: string): Promise<ResearchApiResponse> {
    const response = await fetch("/api/research", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ topic }),
    });

    const payload = await response.json().catch(() => null) as ResearchApiResponse | { error?: string } | null;

    if (!response.ok) {
      throw new Error(payload && "error" in payload && payload.error ? payload.error : "Research request failed.");
    }

    if (!payload || !("report" in payload) || !Array.isArray(payload.steps)) {
      throw new Error("Research API returned an unexpected response.");
    }

    for (const step of payload.steps) {
      this.onStepUpdate({ ...step, status: "completed" });
    }

    return payload;
  }
}
