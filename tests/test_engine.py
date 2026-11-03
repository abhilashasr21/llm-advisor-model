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


if __name__ == "__main__":
    unittest.main()
