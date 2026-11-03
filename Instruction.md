# Instruction Guide

This is the complete usage guide for `llm_advisor`.

## 1. Prerequisites

- Python 3.10+
- Repository cloned locally

## 2. Run from repository root

```bash
cd llm-advisor-model
```

## 3. Basic usage

Single request:

```bash
python -m llm_advisor "Create a secure enterprise AI rollout strategy"
```

Interactive mode:

```bash
python -m llm_advisor --interactive
```

JSON mode:

```bash
python -m llm_advisor "Plan migration to policy routing" --json
```

## 4. Saved output behavior

Each run is saved automatically in `output\` with this naming format:

`name_compliance_date.md`

Example:

`enterprise_demo_strict_20261103_170001.md`

Use `--name` to control the `name` segment.

## 5. Command options

```bash
python -m llm_advisor "<your prompt>" [options]
```

Options:

- `--interactive`
- `--input-file <path>`
- `--stdin`
- `--name <value>`
- `--json`
- `--backend mock|openai`
- `--latency-budget-ms <number>`
- `--cost-tier low|medium|high`
- `--compliance none|standard|strict`

## 6. Structured strategy input format

To get the full strategy report, provide a brief with these sections:

- `Concept:`
- `Workload:`
- `Targets:`
- `Need:`

Example command:

```bash
python -m llm_advisor --input-file examples\04-enterprise-brief-input.txt --compliance strict --name enterprise_demo
```

PowerShell stdin example:

```powershell
@'
Concept: Build an enterprise incident-resolution copilot with multi-stage model routing.

Workload:
120,000 incidents/month
Avg input tokens/request: 9,000
Avg output tokens/request: 1,200
Peak concurrency: 300 requests/min
Targets:
P95 latency under 5 seconds for triage/retrieval stages
High reasoning quality for root-cause analysis
Budget target: under $85,000/month
Region: India + EU
Compliance: ISO 27001, SOC2, GDPR
Data sensitivity: internal confidential production data
Deployment: Azure preferred, fallback to multi-provider allowed
Need:
Top 3 portfolio options (Balanced, Cost-first, Quality-first)
Stage-wise model mapping for all 6 stages
Cost and latency comparison
Enterprise readiness status with gaps/actions
'@ | python -m llm_advisor --stdin --compliance strict --name enterprise_demo
```

## 7. Strategy report format

For structured briefs, output sections are:

1. `## Multi-Stage LLM Strategy Recommendation`
2. `### 1. Executive Decision`
3. `### 2. Stage-wise Model Routing`
4. `### 3. Top-3 Portfolio Comparison`
5. `### 4. Enterprise Readiness`
6. `### 5. Assumptions and Sources`

## 8. Route behavior

Default policy:

1. Quality route for strict compliance, high risk, or high severity
2. Speed route for tight latency budgets
3. Cost route for low-cost preference when no stricter rule applies

Fallback sequence:

- `quality -> cost -> speed`
- `cost -> speed -> quality`
- `speed -> cost -> quality`

## 9. OpenAI-compatible backend (optional)

```bash
set OPENAI_API_KEY=your_key
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
python -m llm_advisor "Your prompt" --backend openai
```

## 10. Demo files

`examples/` contains demo-ready assets:

- `01-speed-route.txt`
- `02-cost-route.txt`
- `03-strict-compliance-route.txt`
- `04-enterprise-brief-input.txt`
- `04-enterprise-brief-output.md`
- `README.md`

## 11. Run tests

```bash
python -m unittest discover -s tests -v
```

## 12. Folder and file reference

### Root

- `.gitignore` - ignore rules
- `README.md` - quick overview
- `Instruction.md` - full instructions
- `Architecture.md` - architecture details
- `pyproject.toml` - package metadata + script entry

### `llm_advisor/`

- `cli.py` - argument parsing, execution, output save
- `engine.py` - orchestration pipeline
- `generation.py` - strategy report formatter
- `models.py` - model adapters
- `router.py` - routing policy
- `triage.py`, `retrieval.py`, `reasoning.py` - stage logic
- `validator.py` - safety/validity checks
- `fallback.py` - fallback sequencing
- `audit.py` - JSONL audit writer
- `telemetry.py` - telemetry structure
- `types.py`, `config.py`, `__init__.py`, `__main__.py`

### `examples/`

- Demo input/output artifacts for presentations

### `docs/`

- `architecture-diagram.png` - architecture image

### `tests/`

- `test_engine.py` - orchestration + strategy output checks
- `test_router.py` - route policy checks
- `test_cli.py` - output file naming checks
