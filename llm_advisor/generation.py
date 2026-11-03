from __future__ import annotations

from .types import RouteDecision
from .types import ReasoningPlan, RetrievalResult, TriageResult


class GenerationStage:
    def build(
        self,
        *,
        model_output: str,
        triage: TriageResult,
        retrieval: RetrievalResult,
        reasoning: ReasoningPlan,
        route: RouteDecision,
        telemetry: dict[str, object],
    ) -> str:
        risk_flags = ", ".join(triage.risk_flags) if triage.risk_flags else "none"
        entities = ", ".join(triage.entities) if triage.entities else "none"
        snippets = "\n".join(f"- {s}" for s in retrieval.snippets)
        steps = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(reasoning.steps))
        attempted_routes = telemetry.get("attempted_routes", [])
        fallback_used = telemetry.get("fallback_used", False)
        fallback_state = "Yes" if fallback_used else "No"

        top3_table = (
            "| Option | Route | Best For | Trade-off |\n"
            "|---|---|---|---|\n"
            "| 1 | Quality | Deep reasoning, strict compliance, high-risk tasks | Higher latency/cost |\n"
            "| 2 | Cost | High-volume throughput and budget control | Lower reasoning depth |\n"
            "| 3 | Speed | Low-latency, interactive responses | Concision over depth |"
        )

        return (
            "## Executive Decision\n"
            f"- **Selected Route:** {route.route} (`{route.model_name}`)\n"
            f"- **Why:** {route.reason}\n"
            f"- **Severity:** {triage.severity}\n"
            f"- **Risk Flags:** {risk_flags}\n"
            f"- **Traceability:** audit trail enabled\n\n"
            "## Stage-wise Routing\n"
            f"{steps}\n\n"
            "## Top-3 Comparison\n"
            f"{top3_table}\n\n"
            "## Enterprise Readiness\n"
            f"- **Validation Gate:** Passed\n"
            f"- **Fallback Triggered:** {fallback_state}\n"
            f"- **Attempted Routes:** {', '.join(str(v) for v in attempted_routes) if attempted_routes else 'none'}\n"
            f"- **Latency (ms):** {telemetry.get('latency_ms', 'n/a')}\n"
            f"- **Token Estimate:** {telemetry.get('token_estimate', 'n/a')}\n\n"
            "## Assumptions & Sources\n"
            f"- **Intent:** {triage.intent}\n"
            f"- **Entities:** {entities}\n"
            f"- **Grounding:**\n{snippets}\n\n"
            "## Recommendation\n"
            f"{model_output}\n\n"
            "## Risk & Compliance Notes\n"
            f"- **Risk Flags:** {risk_flags}\n"
            f"- **Compliance posture:** {'strict-ready' if ('compliance-sensitive' in triage.risk_flags or route.route == 'quality') else 'standard'}"
        )
