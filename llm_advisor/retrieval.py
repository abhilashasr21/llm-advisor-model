from __future__ import annotations

from .types import AdvisorRequest, RetrievalResult, TriageResult


class RetrievalStage:
    def __init__(self) -> None:
        self.knowledge = {
            "latency": "Prefer speed route for low-latency SLAs and interactive UX.",
            "cost": "Prefer cost route for high-volume throughput and budget constraints.",
            "compliance": "Strict compliance uses quality route with full audit traceability.",
            "fallback": "Fallback chain should be deterministic and observable.",
        }

    def run(self, req: AdvisorRequest, triage: TriageResult) -> RetrievalResult:
        merged = f"{req.prompt.lower()} {' '.join(triage.risk_flags).lower()}"
        snippets = [v for k, v in self.knowledge.items() if k in merged]
        if not snippets:
            snippets.append("No direct grounding match; use general enterprise control-tower defaults.")
        return RetrievalResult(snippets=snippets)
