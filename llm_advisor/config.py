from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PolicyConfig:
    latency_speed_threshold_ms: int = 1200
    strict_compliance_routes: tuple[str, ...] = ("quality",)
    high_risk_routes: tuple[str, ...] = ("quality",)
    fallback_map: dict[str, list[str]] = field(
        default_factory=lambda: {
            "quality": ["cost", "speed"],
            "cost": ["speed", "quality"],
            "speed": ["cost", "quality"],
        }
    )


@dataclass(slots=True)
class ModelMap:
    quality: str = "model_a_quality"
    cost: str = "model_b_cost"
    speed: str = "model_c_speed"
