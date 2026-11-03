# LLM Advisor Model

Enterprise AI Control Tower with policy-routed multi-model orchestration and strategy-style output.

## What it does

The tool processes each request through:

1. Triage (intent, severity, risk)
2. Retrieval (grounding context)
3. Reasoning (planning)
4. Policy Router (quality/cost/speed route choice)
5. Validation + fallback
6. Generation (business-ready report)
7. Audit + telemetry

For structured briefs (`Concept`, `Workload`, `Targets`, `Need`), it outputs a full strategy report in this format:

- `## Multi-Stage LLM Strategy Recommendation`
- `### 1. Executive Decision`
- `### 2. Stage-wise Model Routing`
- `### 3. Top-3 Portfolio Comparison`
- `### 4. Enterprise Readiness`
- `### 5. Assumptions and Sources`

## Quick start

```bash
python -m llm_advisor "Create an implementation strategy for a secure multi-tenant AI assistant"
```

## Run with structured brief input

```bash
python -m llm_advisor --input-file examples\04-enterprise-brief-input.txt --compliance strict --name enterprise_demo
```

## Output files

Every run is saved automatically to `output\` as:

`name_compliance_date.md`

Example:

`enterprise_demo_strict_20261103_170001.md`

## Common command patterns

```bash
python -m llm_advisor --interactive
python -m llm_advisor "Need a quick answer" --latency-budget-ms 700
python -m llm_advisor "Need cheapest path" --cost-tier low
python -m llm_advisor "Regulated workload" --compliance strict
python -m llm_advisor "Plan migration to policy routing" --json
```

## Optional OpenAI-compatible backend

```bash
set OPENAI_API_KEY=your_key
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
python -m llm_advisor "Your prompt" --backend openai
```

## Key files

- `llm_advisor/engine.py` - end-to-end orchestrator
- `llm_advisor/generation.py` - strategy report formatter
- `llm_advisor/cli.py` - command interface + output saving
- `Architecture.md` - architecture reference
- `Instruction.md` - full usage instructions
- `examples/` - demo-ready sample inputs/outputs

## Tests

```bash
python -m unittest discover -s tests -v
```
