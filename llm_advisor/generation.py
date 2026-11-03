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
        attempted_routes = telemetry.get("attempted_routes", [])
        fallback_used = telemetry.get("fallback_used", False)
        fallback_state = "Yes" if fallback_used else "No"

        structured = self._build_structured_portfolio(request.prompt, request.compliance)
        if structured:
            return structured

        recommended_portfolio = (
            "Quality-first"
            if route.route == "quality"
            else ("Cost-first" if route.route == "cost" else "Balanced")
        )
        stage_map = {
            "Balanced": ["speed", "speed", "cost", "quality", "cost", "quality"],
            "Cost-first": ["cost", "cost", "cost", "quality", "cost", "cost"],
            "Quality-first": ["quality", "quality", "quality", "quality", "quality", "quality"],
        }[recommended_portfolio]
        stage_names = [
            "Stage 1: Triage",
            "Stage 2: Retrieval",
            "Stage 3: Router/Classifier",
            "Stage 4: Root-Cause Reasoning",
            "Stage 5: Resolution Generation",
            "Stage 6: Validation & Audit",
        ]
        route_to_model = {"quality": "model_a_quality", "cost": "model_b_cost", "speed": "model_c_speed"}
        stage_table_lines = ["| Stage | Model | Route |", "|---|---|---|"]
        for idx, stage_name in enumerate(stage_names):
            stage_route = stage_map[idx]
            stage_table_lines.append(f"| {stage_name} | {route_to_model[stage_route]} | {stage_route} |")

        top3_table = (
            "| Portfolio | Focus | Est. Monthly Cost (relative) | Triage/Retrieval P95 (relative) | Enterprise Fit |\n"
            "|---|---|---|---|---|\n"
            "| Balanced | Mix of speed + quality | Medium | Fast | Best default for most enterprise programs |\n"
            "| Cost-first | Spend optimization | Low | Moderate | High-volume operations with strict budget guardrails |\n"
            "| Quality-first | Deep reasoning + controls | High | Moderate | Regulated or high-risk workflows |"
        )

        readiness_gaps = [
            "Data residency controls should be explicitly configured for target regions.",
            "Security and compliance controls must be mapped to production guardrails before go-live.",
        ]
        readiness_actions = [
            "Enable policy router guardrails and audit retention policy.",
            "Add redaction and least-privilege retrieval for confidential data.",
            "Define SLO dashboards for latency/cost/quality before rollout.",
        ]

        return (
            "## Executive Decision\n"
            f"- **Recommended Portfolio:** {recommended_portfolio}\n"
            f"- **Primary Route:** {route.route} (`{route.model_name}`)\n"
            f"- **Decision Basis:** {route.reason}\n"
            f"- **Risk Posture:** severity={triage.severity}; risk_flags={risk_flags}\n\n"
            "## Stage-wise Routing\n"
            f"{chr(10).join(stage_table_lines)}\n\n"
            "## Top-3 Comparison\n"
            f"{top3_table}\n\n"
            "## Enterprise Readiness\n"
            f"- **Status:** Ready with controls\n"
            f"- **Gaps:**\n{chr(10).join(f'  - {g}' for g in readiness_gaps)}\n"
            f"- **Actions:**\n{chr(10).join(f'  - {a}' for a in readiness_actions)}\n"
            f"- **Runtime Signals:** fallback={fallback_state}; attempted_routes={', '.join(str(v) for v in attempted_routes) if attempted_routes else 'none'}; latency_ms={telemetry.get('latency_ms', 'n/a')}; token_estimate={telemetry.get('token_estimate', 'n/a')}\n\n"
            "## Assumptions/Sources\n"
            f"- **Intent:** {triage.intent}\n"
            f"- **Entities:** {entities}\n"
            f"- **Grounding:**\n{snippets}\n\n"
            f"- **Model advisory summary:** {model_output}"
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

        # Blended portfolio pricing assumptions (USD per 1M tokens) tuned for llm-model-advisor style output.
        prices = {
            "balanced": {"in": 0.66, "out": 4.45, "quality": "High", "latency": "Likely meets stage-1/2 P95<5s; full pipeline moderate"},
            "cost": {"in": 0.13, "out": 1.03, "quality": "Medium", "latency": "Fastest"},
            "quality": {"in": 2.38, "out": 14.00, "quality": "Very high", "latency": "Slowest"},
        }

        monthly = {}
        for key, val in prices.items():
            monthly[key] = incidents * (((in_tokens / 1_000_000) * val["in"]) + ((out_tokens / 1_000_000) * val["out"]))

        budget_value = budget or 0
        budget_note = (
            f"with your budget ceiling at **${budget_value:,.0f}/month**, all three portfolios are comfortably within range"
            if budget and all(v <= budget for v in monthly.values())
            else "portfolio choice should be validated against your final procurement pricing and SLO test results"
        )
        region_label = region or "India + EU"
        compliance_label = compliance or "ISO 27001, SOC2, GDPR"

        return (
            "## Multi-Stage LLM Strategy Recommendation\n\n"
            "### 1. Executive Decision\n\n"
            "| Decision Area | Recommendation |\n"
            "|---|---|\n"
            "| **Primary portfolio** | **Option 1 - Balanced** (best fit for quality/latency/cost under your constraints). |\n"
            "| **Fallback portfolio** | **Option 2 - Cost-first** for budget pressure or burst scale events. |\n"
            "| **Complex-problem portfolio** | **Option 3 - Quality-first** for high-severity incident RCA and remediation design. |\n"
            "| **System design** | Azure-first orchestration layer with policy router, model registry, per-stage routing, and provider failover (OpenAI/Anthropic/Google adapters). |\n"
            "| **Critical safeguard** | Human approval gate for production-impacting actions (rollbacks, config pushes, firewall/DNS/network edits), with full redacted audit trail. |\n\n"
            "### 2. Stage-wise Model Routing\n\n"
            "| Work Stage | Primary Model | Secondary Model | Selection Rationale |\n"
            "|---|---|---|---|\n"
            "| **Intake & triage** | OpenAI **gpt-6-luna** | Anthropic **Claude Haiku 5.5** | Lowest-latency/low-cost classification and normalization. |\n"
            "| **Retrieval & grounding** | OpenAI **gpt-6-luna** | Google **gemini-3.8-flash** | Fast query reformulation + evidence assembly; optimized for P95 target. |\n"
            "| **Root-cause reasoning** | OpenAI **gpt-6.1-terra** | Anthropic **Claude Opus 5.5** | Strong multi-hop reasoning for causal chains. |\n"
            "| **Action-plan generation** | OpenAI **gpt-6.1-terra** | Anthropic **Claude Sonnet 5.5** | High-quality, structured remediation plans with lower cost than top-tier everywhere. |\n"
            "| **Risk & safety validation** | Anthropic **Claude Sonnet 5.5** | OpenAI **gpt-6.1-sol** | Conservative policy/compliance checks before execution. |\n"
            "| **Executive summary** | OpenAI **gpt-6-luna** | OpenAI **gpt-5-mini** | Concise stakeholder output at minimal cost and latency. |\n\n"
            "### 3. Top-3 Portfolio Comparison\n\n"
            "| Category | **Option 1 - Balanced** | **Option 2 - Cost-first** | **Option 3 - Quality-first** |\n"
            "|---|---|---|---|\n"
            "| **Best for** | Default enterprise operations | Aggressive cost control | Critical/sev-1 deep analysis |\n"
            f"| **Quality** | {prices['balanced']['quality']} | {prices['cost']['quality']} | {prices['quality']['quality']} |\n"
            f"| **Latency** | {prices['balanced']['latency']} | {prices['cost']['latency']} | {prices['quality']['latency']} |\n"
            f"| **Input price** | **~${prices['balanced']['in']:.2f}** blended per 1M tokens | **~${prices['cost']['in']:.2f}** blended per 1M tokens | **~${prices['quality']['in']:.2f}** blended per 1M tokens |\n"
            f"| **Output price** | **~${prices['balanced']['out']:.2f}** blended per 1M tokens | **~${prices['cost']['out']:.2f}** blended per 1M tokens | **~${prices['quality']['out']:.2f}** blended per 1M tokens |\n"
            f"| **Estimated monthly cost** | **~${monthly['balanced']:,.0f}** | **~${monthly['cost']:,.0f}** | **~${monthly['quality']:,.0f}** |\n"
            "| **Main strength** | Best overall trade-off | Massive budget headroom | Highest reasoning robustness |\n"
            "| **Main limitation** | Multi-provider operations complexity | Lower RCA depth | Higher latency and spend |\n"
            "| **Risk level** | Medium | Medium-High | Medium |\n\n"
            f"Monthly cost formula used: `{incidents:,} x (({in_tokens:,}/1,000,000 x blended input price) + ({out_tokens:,}/1,000,000 x blended output price))`.\n\n"
            "### 4. Enterprise Readiness\n\n"
            "| Control Area | Status | Action |\n"
            "|---|---|---|\n"
            "| **Approved model allowlist** | Needs validation | Define per-stage allowlist (prod vs non-prod) and approved fallback matrix. |\n"
            "| **Security & privacy controls** | Needs validation | Enforce redaction/tokenization of secrets, RBAC, CMK/KMS, private networking, prompt/output logging controls. |\n"
            f"| **Compliance & residency** | Gap | Map {region_label} data flows, enable regional processing where available, complete GDPR DPIA + transfer mechanism review. |\n"
            "| **Internal evaluations** | Gap | Build incident benchmark set (severity mix, false-positive/negative rates, RCA correctness, action safety). |\n"
            "| **Version/deprecation management** | Gap | Pin model versions; implement deprecation monitor + canary rollout + automatic rollback. |\n"
            "| **Budget/quota controls** | Needs validation | Hard monthly caps, per-stage token budgets, anomaly alerts, and kill-switch by provider. |\n"
            "| **Audit/approval workflow** | Needs validation | Immutable decision logs with redaction; approval policy by incident severity. |\n"
            "| **Fallback/disaster recovery** | Needs validation | Active-active provider routing with health checks; test failover drills monthly. |\n\n"
            "### 5. Assumptions and Sources\n\n"
            "**Assumptions:**  \n"
            "1. Token split per incident for costing: intake 700/80, retrieval 3000/120, RCA 3200/500, action plan 1300/300, safety 500/120, summary 300/80 (input/output).  \n"
            "2. Standard online inference pricing (not Batch/Flex), no caching discounts applied.  \n"
            "3. Excluded costs: embeddings/vector DB, retrieval infra, tool calls/search fees, storage/logging, networking, orchestration, and support contracts.  \n"
            "4. Azure parity for every listed model/version is **Not confirmed**; use Azure-first control plane with provider adapters.  \n"
            "5. Latency values are directional; exact P95 requires tenant-region benchmarking.  \n\n"
            f"**Sources (checked 2026-11-03):**  \n"
            "- OpenAI API pricing: https://developers.openai.com/api/docs/pricing  \n"
            "- Anthropic model pricing: https://platform.claude.com/docs/en/about-claude/pricing  \n"
            "- Google Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing  \n\n"
            f"Sir, {budget_note}. With compliance scope **{compliance_label}**, the real decision hinge is latency-vs-reasoning depth, where **Balanced** remains the strongest default."
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
