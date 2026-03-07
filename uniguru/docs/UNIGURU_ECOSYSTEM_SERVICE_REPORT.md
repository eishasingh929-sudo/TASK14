# UniGuru Ecosystem Service Report

## Scope
This report documents UniGuru stabilization as a BHIV ecosystem service with production-facing API contracts, runtime observability, abuse protection, and deployment readiness.

## 1. API Architecture
- Canonical contract defined in [API_SPEC.md](/c:/Users/Yass0/OneDrive/Desktop/TASK14/uniguru/docs/API_SPEC.md).
- Request shape standardized to:
  - `query`
  - `context`
  - `allow_web`
  - `session_id`
- Response integration fields retained and validated:
  - `decision`
  - `answer`
  - `ontology_reference`
  - `verification_status`
  - `reasoning_trace`
  - `governance_output`
  - `enforcement_signature`
- Backward compatibility maintained for legacy keys (`user_query`, `allow_web_retrieval`).

## 2. Service Stability Work
- Strict input validation added:
  - rejects malformed payloads (`422`)
  - forbids unexpected fields
  - enforces query/context bounds
- Governance pre-validation runs before orchestration (`/ask` pre-check).
- Query classification layer added with deterministic classes:
  - `knowledge_query`
  - `concept_query`
  - `explanation_query`
  - `web_lookup`
- Classification is injected into request context and used to control web fallback behavior.

## 3. Observability and Runtime Monitoring
- Health/readiness endpoints:
  - `GET /health`
  - `GET /ready`
  - `GET /metrics`
- Metrics now include:
  - requests per minute
  - verification success rate
  - average latency
  - rate-limited request counter
  - status code counters
- Structured JSON logs emit:
  - `request_id`
  - `query_type`
  - `latency_ms`
  - `verification_status`
  - `decision`

## 4. Abuse Protection
- Per-IP rate limiting implemented on `/ask`.
- Configurable via env vars:
  - `UNIGURU_RATE_LIMIT_WINDOW_SECONDS`
  - `UNIGURU_RATE_LIMIT_MAX_REQUESTS`
- Rate-limited calls return `429` with rate-limit headers.

## 5. Internal Deployment Preparation
- Docker runtime available via `Dockerfile`.
- Single-command startup for internal deployment:
  - `docker compose up --build`
- Compose manifest added in [docker-compose.yml](/c:/Users/Yass0/OneDrive/Desktop/TASK14/docker-compose.yml).

## 6. Integration and Test Validation
- API + integration tests cover:
  - canonical request contract
  - malformed input rejection
  - ontology reference response path
  - observability endpoint exposure
  - rate-limit enforcement
  - query classification correctness
- Evidence artifact generated at:
  - [service_stability_evidence.json](/c:/Users/Yass0/OneDrive/Desktop/TASK14/demo_logs/service_stability_evidence.json)

## 7. Operational Notes
- Governance and enforcement pathways remain active and are not bypassed.
- Ontology schema and truth structures were not altered as part of this stabilization scope.
