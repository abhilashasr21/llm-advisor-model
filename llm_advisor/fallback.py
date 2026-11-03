from __future__ import annotations


class FallbackChain:
    def __init__(self, fallback_map: dict[str, list[str]]) -> None:
        self.fallback_map = fallback_map

    def sequence(self, primary_route: str) -> list[str]:
        return [primary_route, *self.fallback_map.get(primary_route, [])]
