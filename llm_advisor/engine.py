from __future__ import annotations

from .audit import AuditTrail
from .config import ModelMap, PolicyConfig
from .fallback import FallbackChain
from .generation import GenerationStage
from .models import ModelRegistry
from .reasoning import ReasoningStage
from .retrieval import RetrievalStage
from .router import PolicyRouter
from .telemetry import Telemetry
from .triage import TriageStage
from .types import AdvisorRequest, AdvisorResult, RouteDecision
from .validator import ValidationGate


class ControlTowerEngine:
    def __init__(
        self,
        *,
        backend: str = "mock",
        policy: PolicyConfig | None = None,
        model_map: ModelMap | None = None,
        audit_file: str = "audit_log.jsonl",
    ) -> None:
        self.policy = policy or PolicyConfig()
        self.model_map = model_map or ModelMap()
        self.triage = TriageStage()
        self.retrieval = RetrievalStage()
        self.reasoning = ReasoningStage()
        self.router = PolicyRouter(self.policy, self.model_map)
        self.validator = ValidationGate()
        self.fallback = FallbackChain(self.policy.fallback_map)
        self.generation = GenerationStage()
        self.models = ModelRegistry(backend=backend)
        self.audit = AuditTrail(output_file=audit_file)

    def run(self, req: AdvisorRequest) -> AdvisorResult:
        triage = self.triage.run(req)
        pre_errors = self.validator.pre_check(req, triage)
        if pre_errors:
            raise ValueError("; ".join(pre_errors))

        retrieval = self.retrieval.run(req, triage)
        reasoning = self.reasoning.run(triage, retrieval)
        decision = self.router.decide(req, triage)
        telemetry = Telemetry()

        model_output, final_decision = self._execute_with_fallback(req, retrieval, decision, telemetry)

        answer = self.generation.build(
            request=req,
            model_output=model_output,
            triage=triage,
            retrieval=retrieval,
            reasoning=reasoning,
            route=final_decision,
            telemetry=telemetry.to_dict(),
        )
        post_errors = self.validator.post_check(answer)
        if post_errors:
            raise RuntimeError("; ".join(post_errors))

        audit_id = self.audit.record(
            {
                "route": final_decision.route,
                "model": final_decision.model_name,
                "route_reason": final_decision.reason,
                "triage": {
                    "intent": triage.intent,
                    "severity": triage.severity,
                    "risk_flags": triage.risk_flags,
                },
                "telemetry": telemetry.to_dict(),
            }
        )

        return AdvisorResult(
            answer=answer,
            route=final_decision,
            triage=triage,
            retrieval=retrieval,
            reasoning=reasoning,
            audit_id=audit_id,
            telemetry=telemetry.to_dict(),
        )

    def _execute_with_fallback(
        self,
        req: AdvisorRequest,
        retrieval,
        decision: RouteDecision,
        telemetry: Telemetry,
    ) -> tuple[str, RouteDecision]:
        routes = self.fallback.sequence(decision.route)
        last_error: Exception | None = None
        route_to_model = {
            "quality": self.model_map.quality,
            "cost": self.model_map.cost,
            "speed": self.model_map.speed,
        }
        for idx, route in enumerate(routes):
            model_name = route_to_model[route]
            telemetry.attempted_routes.append(route)
            try:
                response = self.models.get(model_name).generate(
                    prompt=req.prompt,
                    context="\n".join(retrieval.snippets),
                )
                telemetry.model_name = model_name
                telemetry.latency_ms = response.latency_ms
                telemetry.token_estimate = response.token_estimate
                telemetry.fallback_used = idx > 0
                used_decision = RouteDecision(
                    route=route,
                    model_name=model_name,
                    reason=decision.reason if idx == 0 else f"Fallback route '{route}' after primary failure.",
                    fallback_order=decision.fallback_order,
                )
                return response.content, used_decision
            except Exception as exc:  # model-level failure should trigger deterministic fallback
                last_error = exc

        raise RuntimeError(f"All model routes failed. Last error: {last_error}")
