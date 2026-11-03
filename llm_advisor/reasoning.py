from __future__ import annotations

from .types import ReasoningPlan, RetrievalResult, TriageResult


class ReasoningStage:
    def run(self, triage: TriageResult, retrieval: RetrievalResult) -> ReasoningPlan:
        steps = [
            f"Classify request intent={triage.intent}, severity={triage.severity}.",
            "Select model route using policy constraints.",
            "Synthesize response with grounding snippets and action plan.",
        ]
        if triage.risk_flags:
            steps.insert(1, f"Apply risk controls: {', '.join(triage.risk_flags)}.")
        if retrieval.snippets:
            steps.append("Attach grounded rationale and confidence notes.")
        return ReasoningPlan(steps=steps)
