# Demo Examples

This folder is curated for a **live audience demo** with 4 clear scenarios.

## Core examples (show these on stage)

1. `01-speed-route.txt`  
   Fast-response case (low latency target).

2. `02-cost-route.txt`  
   Budget-focused routing case.

3. `03-strict-compliance-route.txt`  
   Compliance-first routing case.

4. `04-enterprise-brief-output.md`  
   Full enterprise portfolio analysis (top 3 options, 6-stage mapping, cost/latency table, readiness gaps/actions).

## Demo run order (recommended)

```bash
python -m llm_advisor "Build an enterprise AI routing strategy" --latency-budget-ms 800
python -m llm_advisor "Design a cost-optimized rollout plan" --cost-tier low
python -m llm_advisor "Design a GDPR-safe architecture for regulated workloads" --compliance strict
python -m llm_advisor --input-file examples/04-enterprise-brief-input.txt --compliance strict --name enterprise_demo
```

## Optional: JSON output for technical audience

```bash
python -m llm_advisor --input-file examples/04-enterprise-brief-input.txt --compliance strict --json
```

Each execution is also saved in `output\` as `name_compliance_date.md`.
