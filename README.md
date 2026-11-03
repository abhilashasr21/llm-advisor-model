# LLM Advisor Model (Enterprise AI Control Tower)

Policy-routed multi-model advisor based on your architecture:

- **Triage** -> classify severity, detect risk, extract entities  
- **Retrieval** -> add grounding snippets  
- **Reasoning** -> build a structured plan  
- **Generate** -> produce final response  
- **Policy Router** -> select **Quality / Cost / Speed** route  
- **Validation Gate + Fallback Chain + Audit Trail** -> safe, resilient, traceable

## Extremely easy usage

No dependencies required for default mode.

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

Tune routing behavior:

```bash
python -m llm_advisor "Need a quick answer" --latency-budget-ms 700
python -m llm_advisor "Need cheapest path" --cost-tier low
python -m llm_advisor "Regulated workload" --compliance strict
```

## OpenAI-compatible backend (optional)

Set environment variables:

```bash
set OPENAI_API_KEY=your_key
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
```

Then run:

```bash
python -m llm_advisor "Your prompt" --backend openai
```

## Architecture mapping

- `llm_advisor/triage.py` -> Stage 1: Triage  
- `llm_advisor/retrieval.py` -> Stage 2: Retrieval  
- `llm_advisor/reasoning.py` -> Stage 3: Reasoning  
- `llm_advisor/generation.py` -> Stage 4: Generate  
- `llm_advisor/router.py` -> Policy Router  
- `llm_advisor/validator.py` -> Validation Gate  
- `llm_advisor/fallback.py` -> Fallback Chain  
- `llm_advisor/audit.py` -> Audit Trail  
- `llm_advisor/telemetry.py` -> Latency/Cost telemetry  
- `llm_advisor/engine.py` -> End-to-end orchestration

## Tests

```bash
python -m unittest discover -s tests -v
```