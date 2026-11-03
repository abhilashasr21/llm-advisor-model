# Examples

This folder contains sample execution outputs from the `llm_advisor` CLI.

## Files

- `01-speed-route.txt` - low-latency request routed to **speed**
- `02-cost-route.txt` - budget-first request routed to **cost**
- `03-strict-compliance-route.txt` - strict compliance request routed to **quality**
- `04-json-output.json` - structured JSON response sample (`--json`)
- `05-policy-blocked.txt` - blocked destructive request example
- `06-audit-log-sample.jsonl` - sample JSONL audit records

## Reproduce samples locally

```bash
python -m llm_advisor "Build an enterprise AI routing strategy" --latency-budget-ms 800
python -m llm_advisor "Design a cost-optimized rollout plan" --cost-tier low
python -m llm_advisor "Design a GDPR-safe architecture" --compliance strict
python -m llm_advisor "Plan migration to policy routing" --json
```
