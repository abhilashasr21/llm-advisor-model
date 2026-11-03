from __future__ import annotations

from .config import ModelMap, PolicyConfig
from .types import AdvisorRequest, RouteDecision, TriageResult


class PolicyRouter:
    def __init__(self, policy: PolicyConfig | None = None, model_map: ModelMap | None = None) -> None:
        self.policy = policy or PolicyConfig()
        self.model_map = model_map or ModelMap()

    def decide(self, req: AdvisorRequest, triage: TriageResult) -> RouteDecision:
        route = self._route_name(req, triage)
        model_name = getattr(self.model_map, route)
        return RouteDecision(
            route=route,
            model_name=model_name,
            reason=self._reason(route, req, triage),
            fallback_order=self.policy.fallback_map[route],
        )

    def _route_name(self, req: AdvisorRequest, triage: TriageResult) -> str:
        if req.compliance == "strict" or "compliance-sensitive" in triage.risk_flags:
            return "quality"
        if triage.severity == "high":
            return "quality"
        if req.latency_budget_ms <= self.policy.latency_speed_threshold_ms:
            return "speed"
        if req.cost_tier == "low":
            return "cost"
        return "quality"

    def _reason(self, route: str, req: AdvisorRequest, triage: TriageResult) -> str:
        if route == "quality":
            return "Selected quality route for high-risk/high-severity/compliance-aware reasoning."
        if route == "speed":
            return f"Selected speed route to satisfy latency budget ({req.latency_budget_ms}ms)."
        return f"Selected cost route due to budget tier '{req.cost_tier}'."
