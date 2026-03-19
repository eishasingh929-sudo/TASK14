# UNIGURU LIVE INTEGRATION REPORT

Date: 2026-03-19

## Scope Delivered

This integration activates UniGuru as a live shared reasoning service for BHIV product chat and Gurukul queries, without changing ontology or core reasoning logic.

## Middleware / Bridge Layer Visibility

### Node to Python bridge behavior
- Bridge entrypoints:
  - `POST /api/v1/chat/query` for product traffic (`caller=bhiv-assistant`)
  - `POST /api/v1/gurukul/query` for Gurukul traffic (`caller=gurukul-platform`)
- Bridge request builder enforces required payload contract before forwarding:
```json
{
  "query": "...",
  "context": {
    "caller": "bhiv-assistant"
  }
}
```
- Additive fields passed through bridge:
  - `session_id`
  - `allow_web`
  - Gurukul metadata (`student_id`, `class_id`)
- Bridge timeout and error policy:
  - Node call timeout controlled by `UNIGURU_REQUEST_TIMEOUT_MS`
  - Upstream errors returned as deterministic `502` with integration message

### Bridge code locations
- Node middleware runtime:
  - `node-backend/src/server.js`
- Node request normalization + forwarding:
  - `node-backend/src/uniguruClient.js`
- BHIV-side integration wiring:
  - `Complete-Uniguru/server/config/rag.js`
  - `Complete-Uniguru/server/controller/chatController.js`

## Phase Delivery Summary

### Phase 1: Node to Python bridge
- Added `node-backend` middleware service.
- Standardized Node to UniGuru request payload:
```json
{
  "query": "...",
  "context": {
    "caller": "bhiv-assistant"
  }
}
```
- Optional fields (`session_id`, `allow_web`) are additive only.

### Phase 2: Product chat integration
- Product endpoint implemented in Node:
  - `POST /api/v1/chat/query`
- Frontend chat call now routes through Node middleware:
  - `frontend -> node-backend -> uniguru-api`
- Existing BHIV `Complete-Uniguru/server/config/rag.js` now uses caller-aware standardized forwarding.

### Phase 3: Gurukul integration
- Gurukul endpoint implemented in Node:
  - `POST /api/v1/gurukul/query`
- Gurukul context forwarded with:
```json
{
  "caller": "gurukul-platform",
  "student_id": "..."
}
```
- Existing BHIV controller now includes `sendGurukulQuery` and uses UniGuru forwarding.

### Phase 4: Bucket + core alignment
- Bucket telemetry events now include:
  - `ontology_reference`
  - `verification_status`
  - `routing`
- Metadata emission is done in `backend/uniguru/service/api.py` through `BucketTelemetryClient`.
- Added metadata-focused test coverage.

## External Integration Points

### Bucket telemetry flow
- Emitted from `/ask` after router decision and verification resolution.
- Event payload now carries:
  - `event`
  - `query_hash`
  - `route`
  - `routing`
  - `verification_status`
  - `ontology_reference`
  - `decision`
  - `caller`
  - `session_id`
- Implementation:
  - `backend/uniguru/service/api.py` (`_emit_bucket_events`)
  - `backend/uniguru/integrations/bucket_telemetry.py` (`TelemetryEvent`)

### Core alignment flow
- `core_alignment` is attached on every `/ask` response from:
  - `backend/uniguru/service/api.py` (`core_reader.align_reference`)
- This ensures returned payloads remain BHIV Core-compatible even when Core reader is disabled (`read_only=true` contract).

### Auth + caller validation flow
- Service token auth:
  - `Authorization: Bearer <UNIGURU_API_TOKEN>`
  - controlled by `UNIGURU_API_AUTH_REQUIRED`
- Caller identity validation:
  - primary source: `context.caller`
  - fallback: `X-Caller-Name`
  - allowlist: `UNIGURU_ALLOWED_CALLERS`
- Unauthorized/invalid callers are rejected with deterministic `401/403`.

### Phase 5: Deployment readiness
- `docker-compose.yml` now defines:
  - `uniguru-api`
  - `node-backend`
  - `nginx`
- NGINX routes:
  - `/api/v1/* -> node-backend`
  - `/ask -> uniguru-api`

### Phase 6: Live activation
- Added `scripts/run_live_activation.py` to boot local Python + Node services and run 5 scenario validation:
  1. Gurukul student query
  2. Product chat query
  3. Knowledge query
  4. Unsafe query
  5. General chat query
- Evidence log output:
  - `demo_logs/uniguru_live_activation_logs.json`
  - `docs/reports/UNIGURU_LIVE_ACTIVATION_LOGS.json`

## Architecture Diagram

- [UNIGURU_LIVE_INTEGRATION_ARCHITECTURE.md](/c:/Users/Yass0/OneDrive/Desktop/TASK14/docs/architecture/UNIGURU_LIVE_INTEGRATION_ARCHITECTURE.md)
- [UNIGURU_BRIDGE_EXECUTION_FLOW.md](/c:/Users/Yass0/OneDrive/Desktop/TASK14/docs/reports/UNIGURU_BRIDGE_EXECUTION_FLOW.md)

## Deployment Reality Layer

| Service | Container | Internal Port | External Exposure | Depends On | Role |
|---|---|---:|---|---|---|
| `uniguru-api` | `uniguru-api` | `8000` | internal network | - | Python `/ask` reasoning API |
| `node-backend` | `node-backend` | `8080` | internal network | `uniguru-api` | Product/Gurukul middleware bridge |
| `nginx` | `uniguru-nginx` | `80/443` | public ingress | `uniguru-api`, `node-backend` | API gateway + TLS routing |

### Service interaction map
1. Client hits `nginx` public endpoint.
2. `/api/v1/*` is proxied to `node-backend`.
3. `node-backend` forwards to `uniguru-api:/ask`.
4. `/ask` direct ingress is proxied to `uniguru-api`.

## Key Files Changed

- Node middleware:
  - `node-backend/src/server.js`
  - `node-backend/src/uniguruClient.js`
- BHIV Node wiring:
  - `Complete-Uniguru/server/config/rag.js`
  - `Complete-Uniguru/server/controller/chatController.js`
- Python telemetry alignment:
  - `backend/uniguru/service/api.py`
  - `backend/uniguru/integrations/bucket_telemetry.py`
- Frontend product routing:
  - `frontend/src/services/uniguru-api.ts`
- Deployment:
  - `docker-compose.yml`
  - `deploy/nginx/conf.d/uniguru.conf`

## What Was Built (Task-Level)

1. Built a live bridge service (`node-backend`) that enforces required request contract and forwards to UniGuru `/ask`.
2. Added product chat middleware endpoint and routed frontend chat through Node middleware.
3. Added Gurukul middleware endpoint with `student_id` propagation and caller separation.
4. Rewired BHIV-side Node adapter/controller to standardized UniGuru call format.
5. Extended telemetry payload schema to include ecosystem-required metadata fields.
6. Added deployment topology for `uniguru-api + node-backend + nginx`.
7. Added live activation automation script and generated evidence logs.
8. Added integration report, architecture diagram, and live log summary docs.

## Request Flow

### Product query
Frontend sends query to Node:
- `POST /api/v1/chat/query`
Node forwards to UniGuru:
- `POST /ask` with `caller=bhiv-assistant`
UniGuru returns deterministic routed response with verification metadata.

### Gurukul query
Gurukul sends query to Node:
- `POST /api/v1/gurukul/query`
Node forwards to UniGuru:
- `POST /ask` with `caller=gurukul-platform`, `student_id`
UniGuru returns structured response with routing and ontology metadata.

## Deployment Setup

1. Configure env:
   - `UNIGURU_API_TOKEN`
   - `UNIGURU_ALLOWED_CALLERS`
   - bucket telemetry env variables
2. Start stack:
   - `docker compose up --build`
3. Validate:
   - `GET /health` on `uniguru-api`
   - `GET /health` on `node-backend`
   - run `python scripts/run_live_activation.py`
