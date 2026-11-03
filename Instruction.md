# Instruction Guide

This guide explains exactly how to run and use the **LLM Advisor Model**.

## 1. What you need

- Python 3.10+ installed
- Repository cloned locally

## 2. Open terminal in repo

```bash
cd llm-advisor-model
```

## 3. Fastest way to run

Single prompt:

```bash
python -m llm_advisor "Create a secure enterprise AI rollout strategy"
```

Interactive mode:

```bash
python -m llm_advisor --interactive
```

Structured JSON output:

```bash
python -m llm_advisor "Plan migration to policy routing" --json
```

## 4. Core command options

```bash
python -m llm_advisor "<your prompt>" [options]
```

Options:

- `--interactive`  
  Starts chat-like session until you type `exit`.

- `--json`  
  Returns machine-readable JSON with route, triage, telemetry, and audit id.

- `--backend mock|openai`  
  `mock` is default and requires no API key.  
  `openai` uses OpenAI-compatible `/chat/completions`.

- `--latency-budget-ms <number>`  
  Lower values bias to speed route.

- `--cost-tier low|medium|high`  
  `low` biases to cost route (unless overridden by stricter policy/risk).

- `--compliance none|standard|strict`  
  `strict` forces quality route.

## 5. Routing behavior

Default policy:

1. **Quality** route when:
   - compliance is strict, or
   - compliance-sensitive risk is detected, or
   - severity is high.
2. **Speed** route when latency budget is below threshold.
3. **Cost** route when cost tier is low and no stricter rule applies.

Fallback sequence:

- `quality -> cost -> speed`
- `cost -> speed -> quality`
- `speed -> cost -> quality`

## 6. OpenAI-compatible backend setup (optional)

Windows CMD:

```bash
set OPENAI_API_KEY=your_key
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
```

Then run:

```bash
python -m llm_advisor "Your prompt" --backend openai
```

If `OPENAI_API_KEY` is missing, the command fails fast with a clear error.

## 7. Output you will get

CLI text output includes:

- Selected route and model
- Structured response
- Risk and compliance summary
- Grounding snippets
- Audit id

JSON output includes:

- `answer`
- `route`
- `triage`
- `telemetry`
- `audit_id`

## 8. Audit and telemetry

- Audit records are written as JSON lines (`audit_log.jsonl`) in the run location.
- Each request gets a unique `audit_id`.
- Telemetry includes attempted routes, selected model, latency, token estimate, and fallback usage.

## 9. Examples included in this repo

See `examples/`:

- speed route sample
- cost route sample
- strict compliance route sample
- JSON output sample
- blocked policy sample
- audit log sample

Architecture reference:

- `Architecture.md`
- `docs/architecture-diagram.png`

## 10. Run tests

```bash
python -m unittest discover -s tests -v
```

## 11. Common issues

1. `No module named llm_advisor`  
   Run the command from the repository root.

2. OpenAI backend fails  
   Check `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and internet access.

3. Request blocked by policy  
   The prompt contains destructive/abuse signals. Rephrase for safe intent.

## 12. Recommended usage pattern

1. Start with default `mock` backend.
2. Validate behavior with `--json`.
3. Tune `--latency-budget-ms`, `--cost-tier`, and `--compliance`.
4. Move to `--backend openai` once policy behavior is acceptable.
