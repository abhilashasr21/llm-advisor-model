from __future__ import annotations

from .types import AdvisorRequest, TriageResult


class ValidationGate:
    def pre_check(self, req: AdvisorRequest, triage: TriageResult) -> list[str]:
        errors: list[str] = []
        if not req.prompt.strip():
            errors.append("Prompt cannot be empty.")
        if "destructive-or-abuse" in triage.risk_flags:
            errors.append("Request blocked by policy: destructive or abuse indicators detected.")
        return errors

    def post_check(self, output: str) -> list[str]:
        errors: list[str] = []
        if not output.strip():
            errors.append("Generated output is empty.")
        return errors
