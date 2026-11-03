[Route: quality | Model: model_a_quality | Audit: demo-sample]

## Executive Decision
- **Recommended Portfolio:** Balanced
- **Why:** Best fit for latency, compliance posture, and budget constraints provided.
- **Workload Basis:** 120,000 incidents/month, 9,000 input tokens/request, 1,200 output tokens/request
- **Peak Concurrency Assumed:** 300 requests/min
- **Budget Target:** under $85,000/month
- **Triage/Retrieval P95 Target:** under 5.0s

## Stage-wise Routing
### Balanced
| Stage | Model | Route |
|---|---|---|
| Stage 1: Triage | model_c_speed | speed |
| Stage 2: Retrieval | model_c_speed | speed |
| Stage 3: Router/Classifier | model_b_cost | cost |
| Stage 4: Root-Cause Reasoning | model_a_quality | quality |
| Stage 5: Resolution Generation | model_b_cost | cost |
| Stage 6: Validation & Audit | model_a_quality | quality |

### Cost-first
| Stage | Model | Route |
|---|---|---|
| Stage 1: Triage | model_b_cost | cost |
| Stage 2: Retrieval | model_b_cost | cost |
| Stage 3: Router/Classifier | model_b_cost | cost |
| Stage 4: Root-Cause Reasoning | model_a_quality | quality |
| Stage 5: Resolution Generation | model_b_cost | cost |
| Stage 6: Validation & Audit | model_b_cost | cost |

### Quality-first
| Stage | Model | Route |
|---|---|---|
| Stage 1: Triage | model_a_quality | quality |
| Stage 2: Retrieval | model_a_quality | quality |
| Stage 3: Router/Classifier | model_a_quality | quality |
| Stage 4: Root-Cause Reasoning | model_a_quality | quality |
| Stage 5: Resolution Generation | model_a_quality | quality |
| Stage 6: Validation & Audit | model_a_quality | quality |

## Top-3 Comparison
| Portfolio | Est. Monthly Cost (USD) | Triage/Retrieval P95 (s) | Overall P95 (s) | Budget Fit |
|---|---:|---:|---:|---|
| Balanced | $16,124 | 0.9 | 3.5 | Yes |
| Cost-first | $15,404 | 1.8 | 3.5 | Yes |
| Quality-first | $28,699 | 3.5 | 3.5 | Yes |

## Enterprise Readiness (Status + Gaps + Actions)
- **Status:** Ready with controls
- **Gaps:**
  - Dual-region residency requires strict data-boundary enforcement.
  - Strict mode limits cost optimization by preferring quality route on sensitive paths.
- **Actions:**
  - Apply geo-fenced routing with India/EU tenant partitioning and separate audit sinks.
  - Add DSR workflow, encryption key segregation, and retention-by-region policy.
  - Enable prompt/response redaction, least-privilege retrieval, and private network endpoints.
  - Use Azure-first control plane with provider adapters for controlled multi-provider fallback.
