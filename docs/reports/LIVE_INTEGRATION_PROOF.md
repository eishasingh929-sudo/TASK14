# Live Integration Proof

Execution date (UTC): 2026-03-27T11:54:54.590302+00:00

## Summary
- All scenarios passed: True
- Structured UI payload present in all scenarios: True

## Scenarios
- External UI via Node: HTTP 200, route `ROUTE_UNIGURU`, verification `VERIFIED`, UI payload `True`
- Gurukul integration: HTTP 200, route `ROUTE_UNIGURU`, verification `VERIFIED`, UI payload `True`
- Samachar integration: HTTP 200, route `ROUTE_LLM`, verification `UNVERIFIED`, UI payload `True`
- Direct /ask API: HTTP 200, route `ROUTE_UNIGURU`, verification `VERIFIED`, UI payload `True`