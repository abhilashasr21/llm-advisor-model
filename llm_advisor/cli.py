from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

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
    parser.add_argument("--input-file", help="Read prompt text from a file path")
    parser.add_argument("--stdin", action="store_true", help="Read prompt text from standard input")
    parser.add_argument("--name", help="Name prefix for saved output file")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    engine = ControlTowerEngine(backend=args.backend)
    if args.interactive and not args.input_file and not args.stdin and not args.prompt:
        _interactive(engine, args)
        return

    prompt_text = _resolve_prompt_text(args)
    if not prompt_text:
        _interactive(engine, args)
        return

    req = AdvisorRequest(
        prompt=prompt_text,
        latency_budget_ms=args.latency_budget_ms,
        cost_tier=args.cost_tier,
        compliance=args.compliance,
    )
    result = engine.run(req)
    rendered = _render_result(result, as_json=args.json)
    print(rendered)
    output_path = _save_output(rendered, name=args.name or prompt_text, compliance=args.compliance)
    print(f"\nSaved: {output_path}")


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
        rendered = _render_result(result, as_json=args.json)
        print(rendered)
        output_path = _save_output(rendered, name=args.name or prompt, compliance=args.compliance)
        print(f"\nSaved: {output_path}")


def _resolve_prompt_text(args: argparse.Namespace) -> str:
    if args.input_file:
        return Path(args.input_file).read_text(encoding="utf-8").strip()
    if args.stdin:
        return sys.stdin.read().strip()
    return " ".join(args.prompt).strip()


def _render_result(result, *, as_json: bool) -> str:
    if as_json:
        return json.dumps(
            {
                "answer": result.answer,
                "route": asdict(result.route),
                "triage": asdict(result.triage),
                "telemetry": result.telemetry,
                "audit_id": result.audit_id,
            },
            indent=2,
        )

    return f"\n[Route: {result.route.route} | Model: {result.route.model_name} | Audit: {result.audit_id}]\n{result.answer}"


def _save_output(content: str, *, name: str, compliance: str) -> Path:
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = _slugify(name) or "result"
    safe_compliance = _slugify(compliance) or "standard"
    file_path = output_dir / f"{safe_name}_{safe_compliance}_{timestamp}.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def _slugify(value: str) -> str:
    reduced = value.strip().lower()
    reduced = re.sub(r"[^a-z0-9]+", "_", reduced)
    return reduced.strip("_")[:60]
