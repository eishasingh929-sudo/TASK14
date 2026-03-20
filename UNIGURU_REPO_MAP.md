# UNIGURU_REPO_MAP

Note: This workspace has one git repository (`TASK14`) but multiple repo-like modules.  
This map is integration-aware (engine + middleware + API consumer + Gurukul path).

Repo: TASK14 (root monorepo)
Contains: Unified codebase for backend engine, Node integration middleware, frontend, deployment, docs.
Status: usable

Repo: backend
Contains: Canonical Python UniGuru API (`/ask`), router, deterministic rule engine, KB/retrieval, auth.
Status: usable

Repo: node-backend
Contains: Canonical integration layer for API consumers (`/api/v1/chat/query`, `/api/v1/gurukul/query`) into `/ask`.
Status: usable

Repo: frontend
Contains: Web chat consumer of Node middleware and direct voice endpoint usage.
Status: partial

Repo: Complete-Uniguru/server
Contains: Old UniGuru/BHIV server integration code (historical API consumer and chat controller).
Status: partial

Repo: Complete-Uniguru (non-server portions)
Contains: Legacy app material not required for current UniGuru integration path.
Status: old

Repo: deploy
Contains: NGINX + Docker wiring for `uniguru-api` and `node-backend`.
Status: usable

Repo: docs
Contains: Architecture/API docs and reports for handoff and testing.
Status: partial

Repo: docs/reports/legacy
Contains: Older execution model (`/chat` bridge-first topology) and outdated runtime assumptions.
Status: old

Repo: scripts
Contains: Utility and validation scripts; useful for integration checks, not core runtime.
Status: partial

Repo: demo_logs
Contains: Prior activation/test evidence artifacts.
Status: partial
