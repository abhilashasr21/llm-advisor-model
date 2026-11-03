import unittest

from llm_advisor.router import PolicyRouter
from llm_advisor.types import AdvisorRequest, TriageResult


def triage(severity: str = "low", risk_flags: list[str] | None = None) -> TriageResult:
    return TriageResult(intent="advice", severity=severity, entities=[], risk_flags=risk_flags or [])


class TestRouter(unittest.TestCase):
    def test_strict_compliance_forces_quality(self) -> None:
        router = PolicyRouter()
        req = AdvisorRequest(prompt="help", compliance="strict")
        decision = router.decide(req, triage())
        self.assertEqual(decision.route, "quality")

    def test_low_latency_prefers_speed(self) -> None:
        router = PolicyRouter()
        req = AdvisorRequest(prompt="help", latency_budget_ms=500)
        decision = router.decide(req, triage())
        self.assertEqual(decision.route, "speed")

    def test_low_cost_prefers_cost(self) -> None:
        router = PolicyRouter()
        req = AdvisorRequest(prompt="help", latency_budget_ms=3000, cost_tier="low")
        decision = router.decide(req, triage())
        self.assertEqual(decision.route, "cost")


if __name__ == "__main__":
    unittest.main()
