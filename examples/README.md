# Demo Examples

This folder is curated for a **live audience demo** with enterprise strategy scenarios.

## Enterprise strategy examples (full report style)

1. `04-enterprise-brief-input.txt` + `04-enterprise-brief-output.md`  
   Incident-resolution copilot (India + EU, GDPR/SOC2/ISO 27001).

2. `05-enterprise-brief-input.txt` + `05-enterprise-brief-output.md`  
   Fraud-detection copilot (US + EU, PCI-DSS/GDPR/SOC2).

3. `06-enterprise-brief-input.txt` + `06-enterprise-brief-output.md`  
   Healthcare-operations incident copilot (India + EU, HIPAA + GDPR).

4. `07-enterprise-brief-input.txt` + `07-enterprise-brief-output.md`  
   Cloud-reliability outage copilot (India + EU + US, high concurrency).

## Demo run order (recommended)

```bash
python -m llm_advisor --input-file examples/04-enterprise-brief-input.txt --compliance strict --name enterprise_demo
python -m llm_advisor --input-file examples/05-enterprise-brief-input.txt --compliance strict --name fraud_demo
python -m llm_advisor --input-file examples/06-enterprise-brief-input.txt --compliance strict --name healthcare_demo
python -m llm_advisor --input-file examples/07-enterprise-brief-input.txt --compliance strict --name reliability_demo
```

## Optional: JSON output for technical audience

```bash
python -m llm_advisor --input-file examples/04-enterprise-brief-input.txt --compliance strict --json
```

Each execution is also saved in `output\` as `name_compliance_date.md`.
