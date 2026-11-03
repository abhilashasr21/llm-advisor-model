# LLM Advisor Model

Enterprise AI Control Tower for **policy-routed multi-model orchestration** (Quality, Cost, Speed) with validation, fallback, telemetry, and auditability.

## What this does

It converts a user request into a governed execution flow:

1. **Triage**: classify intent, severity, entities, and risk signals.
2. **Retrieval**: attach relevant grounding snippets.
3. **Reasoning**: create a structured plan.
4. **Policy Router**: select route (**Quality / Cost / Speed**) using latency, cost, risk, and compliance.
5. **Validation Gate**: block unsafe/invalid requests.
6. **Fallback Chain**: deterministic route fallback on model failure.
7. **Generate**: return structured output with rationale.
8. **Audit + Telemetry**: persist route decision and request trace.

## Quick start (60 seconds)

No external dependencies are needed for default mock mode.

```bash
python -m llm_advisor "Create an implementation strategy for a secure multi-tenant AI assistant"
```

Interactive mode:

```bash
python -m llm_advisor --interactive
```

JSON output:

```bash
python -m llm_advisor "Plan migration to policy-based routing" --json
```

## Route behavior examples

Low latency (prefers **speed** route):

```bash
python -m llm_advisor "Need a quick answer" --latency-budget-ms 700
```

Budget constrained (prefers **cost** route):

```bash
python -m llm_advisor "Need cheapest path" --cost-tier low
```

Strict compliance (forces **quality** route):

```bash
python -m llm_advisor "Regulated workload" --compliance strict
```

## Optional: OpenAI-compatible backend

Set environment variables (Windows):

```bash
set OPENAI_API_KEY=your_key
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
```

Run with hosted model backend:

```bash
python -m llm_advisor "Your prompt" --backend openai
```

## Project structure

- `llm_advisor/engine.py` - end-to-end orchestration
- `llm_advisor/router.py` - policy routing logic
- `llm_advisor/triage.py` - stage 1 triage
- `llm_advisor/retrieval.py` - stage 2 retrieval
- `llm_advisor/reasoning.py` - stage 3 reasoning
- `llm_advisor/generation.py` - stage 4 generation
- `llm_advisor/validator.py` - pre/post safety checks
- `llm_advisor/fallback.py` - fallback sequencing
- `llm_advisor/models.py` - model adapters (mock/openai-compatible)
- `llm_advisor/audit.py` - JSONL audit trail writer
- `llm_advisor/telemetry.py` - request telemetry record
- `llm_advisor/cli.py` - user CLI interface
- `Architecture.md` - detailed architecture and control flow
- `docs/architecture-diagram.png` - architecture diagram image
- `examples/` - execution result samples

## Run tests

```bash
python -m unittest discover -s tests -v
```