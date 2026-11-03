from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AdvisorRequest:
    prompt: str
    latency_budget_ms: int = 3000
    cost_tier: str = "medium"  # low | medium | high
    compliance: str = "standard"  # none | standard | strict
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TriageResult:
    intent: str
    severity: str
    entities: list[str]
    risk_flags: list[str]


@dataclass(slots=True)
class RetrievalResult:
    snippets: list[str]


@dataclass(slots=True)
class ReasoningPlan:
    steps: list[str]


@dataclass(slots=True)
class RouteDecision:
    route: str
    model_name: str
    reason: str
    fallback_order: list[str]


@dataclass(slots=True)
class ModelResponse:
    content: str
    latency_ms: int
    token_estimate: int


@dataclass(slots=True)
class AdvisorResult:
    answer: str
    route: RouteDecision
    triage: TriageResult
    retrieval: RetrievalResult
    reasoning: ReasoningPlan
    audit_id: str
    telemetry: dict[str, Any]
