# UniGuru Admission Middleware Layer (Phase 1)
> **Student:** Isha Singh  
> **Component:** Admission & Isolation Layer

## Overview
This repository contains the standalone Admission Middleware specific for UniGuru. It acts as an isolated gateway that validates all incoming requests before they reach the UniGuru Core. This layer is deterministic, stateless, and ensures that only safe, valid requests are forwarded.

## Architecture
The middleware is built as a lightweight Node.js/Express application implementing the "API Gateway" pattern:

1. **Request Interception**: All requests hit `POST /admit`.
2. **Deterministic Validation (Day 2)**: A pure rule engine checks:
   - Payload presence (non-empty).
   - Malformed check (requires `message` property).
   - Size limits (Strict 1MB).
   - Safety checks (SQL Injection, XSS tokens).
3. **Bridge Mode (Day 3)**:
   - **Allowed**: Requests are forwarded to UniGuru Core (`http://localhost:5000/chat`).
   - **Decisions**: Logged to `admission.log` with trace IDs.
   - **Rejected**: Immediate structured 400/413 response.
   - **Failure**: 502 response if upstream is unreachable.

## Repository Structure
```
.
├── src/
│   ├── index.js         # Entry point
│   ├── server.js        # Express app & middleware setup
│   ├── ruleEngine.js    # Pure validation logic (Day 2)
│   ├── admission.js     # Orchestration (Day 3)
│   ├── config.js        # Environment config
│   ├── utils/
│   │   └── logger.js    # File logger (Day 3)
│   ├── schema/
│   │   └── requestSchema.js # Contract Definition (Day 1)
│   └── forward/
│       └── forwardRequest.js # Forwarding Logic (Day 3)
├── tests/
│   ├── integration.test.js # Integration tests
│   └── ruleEngine.test.js  # Unit tests
├── scripts/
│   ├── run_integration_tests.js # Script for manual integration testing
│   ├── fake-uniguru.js  # Fake Upstream Server for Demo
│   └── demo.ps1         # PowerShell Demo Script
├── examples/
│   ├── allowed.json     # Sample allowed request
│   └── rejected.json    # Sample rejected request
├── package.json
└── README.md
```

## Setup & Run
### Prerequisites
- Node.js (v16+)
- npm

### Installation
```bash
npm install
```

### Running Locally
1. Start the middleware:
   ```bash
   npm start
   ```
   (Listens on port 3000)

2. Start Fake UniGuru (for full demo):
   ```bash
   node scripts/fake-uniguru.js
   ```
   (Listens on port 5000)

### Testing
Run the comprehensive test suite (Unit + Integration):
```bash
npm test
```

## API Contract
Expected Request Body:
```json
{
  "message": "User query string..."
}
```

Detailed contract in [src/schema/requestSchema.js](./src/schema/requestSchema.js).

## Validation Rules
- **Empty Payload**: Rejected.
- **Malformed**: Missing "message" property.
- **Size > 1MB**: Rejected (413).
- **Unsafe Tokens**: Regex checks for SQLi (`DROP TABLE`, etc.) and XSS (`<script>`).

## Deliverables Status
- [x] Day 1: Architecture Setup & Schema
- [x] Day 2: Deterministic Validation Engine (Pure Function) & Unit Tests
- [x] Day 3: Forwarding Layer & Logging
- [x] Examples & Demo Support
