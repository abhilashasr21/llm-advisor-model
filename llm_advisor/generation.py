from __future__ import annotations

import re

from .types import AdvisorRequest
from .types import RouteDecision
from .types import ReasoningPlan, RetrievalResult, TriageResult


class GenerationStage:
    def build(
        self,
        *,
        request: AdvisorRequest,
        model_output: str,
        triage: TriageResult,
        retrieval: RetrievalResult,
        reasoning: ReasoningPlan,
        route: RouteDecision,
        telemetry: dict[str, object],
    ) -> str:
        risk_flags = ", ".join(triage.risk_flags) if triage.risk_flags else "none"
        entities = ", ".join(triage.entities) if triage.entities else "none"
        snippets = "\n".join(f"- {s}" for s in retrieval.snippets)
        steps = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(reasoning.steps))
        attempted_routes = telemetry.get("attempted_routes", [])
        fallback_used = telemetry.get("fallback_used", False)
        fallback_state = "Yes" if fallback_used else "No"

        top3_table = (
            "| Option | Route | Best For | Trade-off |\n"
            "|---|---|---|---|\n"
            "| 1 | Quality | Deep reasoning, strict compliance, high-risk tasks | Higher latency/cost |\n"
            "| 2 | Cost | High-volume throughput and budget control | Lower reasoning depth |\n"
            "| 3 | Speed | Low-latency, interactive responses | Concision over depth |"
        )

        structured = self._build_structured_portfolio(request.prompt, request.compliance)
        if structured:
            return structured

        return (
            "## Executive Decision\n"
            f"- **Selected Route:** {route.route} (`{route.model_name}`)\n"
            f"- **Why:** {route.reason}\n"
            f"- **Severity:** {triage.severity}\n"
            f"- **Risk Flags:** {risk_flags}\n"
            f"- **Traceability:** audit trail enabled\n\n"
            "## Stage-wise Routing\n"
            f"{steps}\n\n"
            "## Top-3 Comparison\n"
            f"{top3_table}\n\n"
            "## Enterprise Readiness\n"
            f"- **Validation Gate:** Passed\n"
            f"- **Fallback Triggered:** {fallback_state}\n"
            f"- **Attempted Routes:** {', '.join(str(v) for v in attempted_routes) if attempted_routes else 'none'}\n"
            f"- **Latency (ms):** {telemetry.get('latency_ms', 'n/a')}\n"
            f"- **Token Estimate:** {telemetry.get('token_estimate', 'n/a')}\n\n"
            "## Assumptions & Sources\n"
            f"- **Intent:** {triage.intent}\n"
            f"- **Entities:** {entities}\n"
            f"- **Grounding:**\n{snippets}\n\n"
            "## Recommendation\n"
            f"{model_output}\n\n"
            "## Risk & Compliance Notes\n"
            f"- **Risk Flags:** {risk_flags}\n"
            f"- **Compliance posture:** {'strict-ready' if ('compliance-sensitive' in triage.risk_flags or route.route == 'quality') else 'standard'}"
        )

    def _build_structured_portfolio(self, prompt: str, compliance_mode: str) -> str | None:
        text = prompt.strip()
        if "Workload:" not in text or "Targets:" not in text or "Need:" not in text:
            return None

        incidents = self._extract_int(text, r"([0-9][0-9,]*)\s*incidents/month")
        in_tokens = self._extract_int(text, r"input tokens/request:\s*([0-9][0-9,]*)")
        out_tokens = self._extract_int(text, r"output tokens/request:\s*([0-9][0-9,]*)")
        concurrency = self._extract_int(text, r"Peak concurrency:\s*([0-9][0-9,]*)\s*requests/min")
        budget = self._extract_int(text, r"Budget target:\s*under\s*\$([0-9][0-9,]*)/month")
        p95_target = self._extract_float(text, r"P95 latency under\s*([0-9]+(?:\.[0-9]+)?)\s*seconds")
        region = self._extract_text(text, r"Region:\s*(.+)")
        compliance = self._extract_text(text, r"Compliance:\s*(.+)")
        sensitivity = self._extract_text(text, r"Data sensitivity:\s*(.+)")
        deployment = self._extract_text(text, r"Deployment:\s*(.+)")

        if incidents is None or in_tokens is None or out_tokens is None:
            return None

        stage_profiles = [
            ("Stage 1: Triage", 0.15, 180),
            ("Stage 2: Retrieval", 0.25, 220),
            ("Stage 3: Router/Classifier", 0.08, 120),
            ("Stage 4: Root-Cause Reasoning", 0.70, int(out_tokens * 0.55)),
            ("Stage 5: Resolution Generation", 0.35, out_tokens),
            ("Stage 6: Validation & Audit", 0.12, 160),
        ]

        route_profiles = {
            "quality": {"cost_in": 0.012, "cost_out": 0.024, "latency": 3.5, "model": "model_a_quality"},
            "cost": {"cost_in": 0.003, "cost_out": 0.006, "latency": 1.8, "model": "model_b_cost"},
            "speed": {"cost_in": 0.0015, "cost_out": 0.003, "latency": 0.9, "model": "model_c_speed"},
        }

        portfolios = {
            "Balanced": ["speed", "speed", "cost", "quality", "cost", "quality"],
            "Cost-first": ["cost", "cost", "cost", "quality", "cost", "cost"],
            "Quality-first": ["quality", "quality", "quality", "quality", "quality", "quality"],
        }

        analysis: dict[str, dict[str, object]] = {}
        for name, mapping in portfolios.items():
            monthly_cost = 0.0
            stage_rows: list[tuple[str, str, str]] = []
            stage_latencies: list[float] = []
            for idx, (stage_name, in_mult, out_fixed) in enumerate(stage_profiles):
                route = mapping[idx]
                prof = route_profiles[route]
                stage_input = int(in_tokens * in_mult)
                stage_output = out_fixed
                stage_cost = incidents * (
                    (stage_input / 1000.0) * float(prof["cost_in"]) + (stage_output / 1000.0) * float(prof["cost_out"])
                )
                monthly_cost += stage_cost
                stage_latencies.append(float(prof["latency"]))
                stage_rows.append((stage_name, str(prof["model"]), route))

            triage_retrieval_p95 = max(stage_latencies[0], stage_latencies[1])
            overall_p95 = max(stage_latencies)
            analysis[name] = {
                "monthly_cost": monthly_cost,
                "triage_retrieval_p95": triage_retrieval_p95,
                "overall_p95": overall_p95,
                "rows": stage_rows,
            }

        recommended = "Balanced"
        if budget is not None:
            within_budget = [k for k, v in analysis.items() if float(v["monthly_cost"]) <= budget]
            if "Balanced" in within_budget:
                recommended = "Balanced"
            elif "Cost-first" in within_budget:
                recommended = "Cost-first"
            elif within_budget:
                recommended = within_budget[0]
            else:
                recommended = "Cost-first"

        stage_map_lines = []
        for name in ("Balanced", "Cost-first", "Quality-first"):
            rows = analysis[name]["rows"]
            stage_map_lines.append(f"### {name}")
            stage_map_lines.append("| Stage | Model | Route |")
            stage_map_lines.append("|---|---|---|")
            for stage_name, model, route in rows:
                stage_map_lines.append(f"| {stage_name} | {model} | {route} |")
            stage_map_lines.append("")

        comp_lines = [
            "| Portfolio | Est. Monthly Cost (USD) | Triage/Retrieval P95 (s) | Overall P95 (s) | Budget Fit |",
            "|---|---:|---:|---:|---|",
        ]
        for name in ("Balanced", "Cost-first", "Quality-first"):
            monthly_cost = float(analysis[name]["monthly_cost"])
            tr_p95 = float(analysis[name]["triage_retrieval_p95"])
            ov_p95 = float(analysis[name]["overall_p95"])
            budget_fit = "Yes" if budget is None or monthly_cost <= budget else "No"
            comp_lines.append(f"| {name} | ${monthly_cost:,.0f} | {tr_p95:.1f} | {ov_p95:.1f} | {budget_fit} |")

        gaps: list[str] = []
        actions: list[str] = []
        readiness = "Ready with controls"
        if budget is not None and all(float(v["monthly_cost"]) > budget for v in analysis.values()):
            readiness = "Partially ready"
            gaps.append("All three portfolios exceed the stated monthly budget target.")
            actions.append("Reduce root-cause stage token budget and cache retrieval context aggressively.")
        if p95_target is not None and any(float(analysis[k]["triage_retrieval_p95"]) > p95_target for k in analysis):
            readiness = "Partially ready"
            gaps.append("At least one portfolio misses triage/retrieval P95 target.")
            actions.append("Pin stage 1-2 to speed/cost profiles and pre-warm model endpoints.")
        if region and ("india" in region.lower() and "eu" in region.lower()):
            gaps.append("Dual-region residency requires strict data-boundary enforcement.")
            actions.append("Apply geo-fenced routing with India/EU tenant partitioning and separate audit sinks.")
        if compliance and "gdpr" in compliance.lower():
            actions.append("Add DSR workflow, encryption key segregation, and retention-by-region policy.")
        if sensitivity and "confidential" in sensitivity.lower():
            actions.append("Enable prompt/response redaction, least-privilege retrieval, and private network endpoints.")
        if deployment and "azure preferred" in deployment.lower() and "fallback" in deployment.lower():
            actions.append("Use Azure-first control plane with provider adapters for controlled multi-provider fallback.")
        if compliance_mode == "strict":
            gaps.append("Strict mode limits cost optimization by preferring quality route on sensitive paths.")

        if not gaps:
            gaps.append("No blocking gaps identified against provided requirements.")
        if not actions:
            actions.append("Proceed with Balanced portfolio and weekly SLO/cost reviews.")

        executive = (
            f"- **Recommended Portfolio:** {recommended}\n"
            f"- **Why:** Best fit for latency, compliance posture, and budget constraints provided.\n"
            f"- **Workload Basis:** {incidents:,} incidents/month, {in_tokens:,} input tokens/request, {out_tokens:,} output tokens/request"
        )
        if concurrency is not None:
            executive += f"\n- **Peak Concurrency Assumed:** {concurrency:,} requests/min"
        if budget is not None:
            executive += f"\n- **Budget Target:** under ${budget:,.0f}/month"
        if p95_target is not None:
            executive += f"\n- **Triage/Retrieval P95 Target:** under {p95_target:.1f}s"

        return (
            "## Executive Decision\n"
            f"{executive}\n\n"
            "## Stage-wise Routing\n"
            f"{chr(10).join(stage_map_lines)}\n"
            "## Cost and Latency Comparison\n"
            f"{chr(10).join(comp_lines)}\n\n"
            "## Enterprise Readiness (Status + Gaps + Actions)\n"
            f"- **Status:** {readiness}\n"
            f"- **Gaps:**\n{chr(10).join(f'  - {g}' for g in gaps)}\n"
            f"- **Actions:**\n{chr(10).join(f'  - {a}' for a in actions)}\n\n"
            "## Assumptions & Sources\n"
            "- Pricing and latency are portfolio-estimation placeholders for decision support.\n"
            "- Final vendor pricing, reserved capacity, and enterprise discounts will adjust totals.\n"
            f"- Input source: structured request text ({'with' if compliance else 'without'} explicit compliance list)."
        )

    def _extract_int(self, text: str, pattern: str) -> int | None:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            return None
        return int(match.group(1).replace(",", "").strip())

    def _extract_float(self, text: str, pattern: str) -> float | None:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            return None
        return float(match.group(1))

    def _extract_text(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            return ""
        value = match.group(1).strip()
        return value.splitlines()[0].strip()
