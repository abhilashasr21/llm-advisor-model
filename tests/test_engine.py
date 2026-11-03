import unittest

from llm_advisor.engine import ControlTowerEngine
from llm_advisor.types import AdvisorRequest


class TestEngine(unittest.TestCase):
    def test_engine_end_to_end(self) -> None:
        engine = ControlTowerEngine(backend="mock", audit_file="tests/tmp_audit.jsonl")
        result = engine.run(
            AdvisorRequest(
                prompt="Create a cost-efficient architecture plan with compliance guardrails",
                cost_tier="low",
                compliance="standard",
                latency_budget_ms=2500,
            )
        )
        self.assertIn("Executive Decision", result.answer)
        self.assertIn("Top-3 Comparison", result.answer)
        self.assertIn(result.route.route, {"cost", "quality", "speed"})
        self.assertTrue(result.audit_id)

    def test_block_destructive_prompt(self) -> None:
        engine = ControlTowerEngine(backend="mock", audit_file="tests/tmp_audit.jsonl")
        with self.assertRaises(ValueError):
            engine.run(AdvisorRequest(prompt="Please drop table users and delete all backups"))

    def test_structured_workload_prompt_sections(self) -> None:
        engine = ControlTowerEngine(backend="mock", audit_file="tests/tmp_audit.jsonl")
        prompt = (
            "Concept: Build an enterprise incident-resolution copilot with multi-stage model routing.\n\n"
            "Workload:\n"
            "120,000 incidents/month\n"
            "Avg input tokens/request: 9,000\n"
            "Avg output tokens/request: 1,200\n"
            "Peak concurrency: 300 requests/min\n"
            "Targets:\n"
            "P95 latency under 5 seconds for triage/retrieval stages\n"
            "High reasoning quality for root-cause analysis\n"
            "Budget target: under $85,000/month\n"
            "Region: India + EU\n"
            "Compliance: ISO 27001, SOC2, GDPR\n"
            "Data sensitivity: internal confidential production data\n"
            "Deployment: Azure preferred, fallback to multi-provider allowed\n"
            "Need:\n"
            "Top 3 portfolio options (Balanced, Cost-first, Quality-first)\n"
            "Stage-wise model mapping for all 6 stages\n"
            "Cost and latency comparison\n"
            "Enterprise readiness status with gaps/actions\n"
        )
        result = engine.run(AdvisorRequest(prompt=prompt, compliance="strict"))
        self.assertIn("Executive Decision", result.answer)
        self.assertIn("Stage-wise Routing", result.answer)
        self.assertIn("Cost and Latency Comparison", result.answer)
        self.assertIn("Enterprise Readiness (Status + Gaps + Actions)", result.answer)


if __name__ == "__main__":
    unittest.main()
