from __future__ import annotations

from .types import ReasoningPlan, RetrievalResult, TriageResult


class GenerationStage:
    def build(
        self,
        *,
        model_output: str,
        triage: TriageResult,
        retrieval: RetrievalResult,
        reasoning: ReasoningPlan,
    ) -> str:
        snippets = "\n".join(f"- {s}" for s in retrieval.snippets)
        steps = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(reasoning.steps))
        return (
            "## Advisor Response\n"
            f"{model_output}\n\n"
            "## Structured Plan\n"
            f"{steps}\n\n"
            "## Risk & Compliance\n"
            f"- Severity: {triage.severity}\n"
            f"- Risk flags: {', '.join(triage.risk_flags) if triage.risk_flags else 'none'}\n\n"
            "## Grounding\n"
            f"{snippets}"
        )
