from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from .types import ModelResponse


class ModelAdapter:
    def generate(self, *, prompt: str, context: str) -> ModelResponse:
        raise NotImplementedError


@dataclass(slots=True)
class MockModelAdapter(ModelAdapter):
    profile: str

    def generate(self, *, prompt: str, context: str) -> ModelResponse:
        start = time.perf_counter()
        if self.profile == "quality":
            content = (
                "High-depth answer with tradeoffs, risk notes, and implementation steps.\n"
                f"Prompt: {prompt[:220]}"
            )
        elif self.profile == "cost":
            content = (
                "Cost-optimized answer with concise steps and minimal token footprint.\n"
                f"Prompt: {prompt[:160]}"
            )
        else:
            content = f"Fast answer for low-latency path.\nPrompt: {prompt[:120]}"
        if context:
            content += f"\nGrounding: {context[:240]}"
        latency_ms = int((time.perf_counter() - start) * 1000) + (30 if self.profile == "speed" else 90)
        token_estimate = max(80, len(content) // 4)
        return ModelResponse(content=content, latency_ms=latency_ms, token_estimate=token_estimate)


@dataclass(slots=True)
class OpenAICompatibleAdapter(ModelAdapter):
    profile: str
    model_name: str
    base_url: str
    api_key: str

    def generate(self, *, prompt: str, context: str) -> ModelResponse:
        start = time.perf_counter()
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": f"You are the {self.profile} route model."},
                {"role": "user", "content": f"{prompt}\n\nContext:\n{context}"},
            ],
            "temperature": 0.2,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url.rstrip("/") + "/chat/completions",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Model call failed: {exc}") from exc

        content = raw["choices"][0]["message"]["content"]
        usage = raw.get("usage", {})
        token_estimate = int(usage.get("total_tokens", max(80, len(content) // 4)))
        latency_ms = int((time.perf_counter() - start) * 1000)
        return ModelResponse(content=content, latency_ms=latency_ms, token_estimate=token_estimate)


class ModelRegistry:
    def __init__(self, backend: str = "mock") -> None:
        self.adapters = self._build(backend)

    def get(self, model_name: str) -> ModelAdapter:
        return self.adapters[model_name]

    def _build(self, backend: str) -> dict[str, ModelAdapter]:
        profiles = {
            "model_a_quality": "quality",
            "model_b_cost": "cost",
            "model_c_speed": "speed",
        }
        if backend == "openai":
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is required when backend=openai.")
            return {
                name: OpenAICompatibleAdapter(
                    profile=profile,
                    model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    base_url=base_url,
                    api_key=api_key,
                )
                for name, profile in profiles.items()
            }
        return {name: MockModelAdapter(profile=profile) for name, profile in profiles.items()}
