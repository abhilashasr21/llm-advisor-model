from __future__ import annotations

import re

from .types import AdvisorRequest, TriageResult


class TriageStage:
    def run(self, req: AdvisorRequest) -> TriageResult:
        prompt = req.prompt.lower()
        severity = self._severity(prompt)
        intent = self._intent(prompt)
        entities = self._entities(req.prompt)
        risk_flags = self._risk_flags(prompt)
        return TriageResult(intent=intent, severity=severity, entities=entities, risk_flags=risk_flags)

    def _severity(self, prompt: str) -> str:
        if any(k in prompt for k in ("urgent", "outage", "breach", "sev1", "critical")):
            return "high"
        if any(k in prompt for k in ("issue", "error", "fail", "block")):
            return "medium"
        return "low"

    def _intent(self, prompt: str) -> str:
        if any(k in prompt for k in ("plan", "strategy", "roadmap")):
            return "planning"
        if any(k in prompt for k in ("why", "root cause", "analyze")):
            return "analysis"
        if any(k in prompt for k in ("build", "create", "implement")):
            return "build"
        return "advice"

    def _entities(self, text: str) -> list[str]:
        return sorted(set(re.findall(r"\b[A-Z][A-Za-z0-9_-]{2,}\b", text)))[:12]

    def _risk_flags(self, prompt: str) -> list[str]:
        flags: list[str] = []
        if any(k in prompt for k in ("pii", "gdpr", "hipaa", "confidential", "legal")):
            flags.append("compliance-sensitive")
        if any(k in prompt for k in ("delete all", "drop table", "bypass", "exploit")):
            flags.append("destructive-or-abuse")
        return flags
