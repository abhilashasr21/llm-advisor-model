from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Telemetry:
    attempted_routes: list[str] = field(default_factory=list)
    model_name: str = ""
    latency_ms: int = 0
    token_estimate: int = 0
    fallback_used: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "attempted_routes": self.attempted_routes,
            "model_name": self.model_name,
            "latency_ms": self.latency_ms,
            "token_estimate": self.token_estimate,
            "fallback_used": self.fallback_used,
        }
