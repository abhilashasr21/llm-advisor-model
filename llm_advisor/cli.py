from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .engine import ControlTowerEngine
from .types import AdvisorRequest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-advisor",
        description="Enterprise AI Control Tower (policy-routed multi-model advisor)",
    )
    parser.add_argument("prompt", nargs="*", help="Question or task for the advisor")
    parser.add_argument("--backend", choices=["mock", "openai"], default="mock")
    parser.add_argument("--latency-budget-ms", type=int, default=3000)
    parser.add_argument("--cost-tier", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--compliance", choices=["none", "standard", "strict"], default="standard")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output")
    parser.add_argument("--interactive", action="store_true", help="Start interactive chat mode")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    engine = ControlTowerEngine(backend=args.backend)
    if args.interactive or not args.prompt:
        _interactive(engine, args)
        return

    req = AdvisorRequest(
        prompt=" ".join(args.prompt),
        latency_budget_ms=args.latency_budget_ms,
        cost_tier=args.cost_tier,
        compliance=args.compliance,
    )
    result = engine.run(req)
    _print_result(result, as_json=args.json)


def _interactive(engine: ControlTowerEngine, args: argparse.Namespace) -> None:
    print("LLM Advisor interactive mode. Type 'exit' to quit.")
    while True:
        prompt = input("\nYou> ").strip()
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye.")
            return
        req = AdvisorRequest(
            prompt=prompt,
            latency_budget_ms=args.latency_budget_ms,
            cost_tier=args.cost_tier,
            compliance=args.compliance,
        )
        result = engine.run(req)
        _print_result(result, as_json=args.json)


def _print_result(result, *, as_json: bool) -> None:
    if as_json:
        print(
            json.dumps(
                {
                    "answer": result.answer,
                    "route": asdict(result.route),
                    "triage": asdict(result.triage),
                    "telemetry": result.telemetry,
                    "audit_id": result.audit_id,
                },
                indent=2,
            )
        )
        return

    print(f"\n[Route: {result.route.route} | Model: {result.route.model_name} | Audit: {result.audit_id}]")
    print(result.answer)
