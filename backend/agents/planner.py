from typing import Optional

from backend.models import ResearchContext, ResearchPlan


def build_research_plan(topic: str, context: Optional[ResearchContext] = None) -> ResearchPlan:
    context = context or ResearchContext()

    sub_questions = [
        f"Which companies are the most relevant competitors for {topic}?",
        "How do the leading competitors differentiate on pricing and product depth?",
        "What strengths, weaknesses, and market trends should a buyer know about?",
    ]

    if context.priorities:
        priorities = ", ".join(context.priorities)
        sub_questions.append(f"How do the competitors compare on these priorities: {priorities}?")

    if context.region:
        sub_questions.append(f"Which regional factors matter for buyers operating in {context.region}?")

    success_criteria = [
        "Identify at least three competitors with clear positioning.",
        "Ground the report in recent, source-backed findings.",
        "Cover pricing, product strengths, weaknesses, and market trends.",
    ]

    if context.priorities:
        success_criteria.append("Address the user's stated priorities explicitly.")

    objective = f"Produce a concise competitive intelligence report for {topic}."
    if context.region:
        objective = f"{objective} Emphasize the context for {context.region}."

    return ResearchPlan(
        objective=objective,
        subQuestions=sub_questions,
        successCriteria=success_criteria,
    )
