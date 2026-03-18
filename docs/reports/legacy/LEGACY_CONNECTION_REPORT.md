# Legacy Connection Report

## Overview
This document describes the connection between the UniGuru Bridge (middleware) and the Legacy UniGuru system (generative backend).

## The Mock Legacy Server
A mock legacy server (`bridge/mock_legacy_server.py`) has been implemented to simulate the production system. This allows for full integration testing of the bridge's forwarding logic without requiring access to the real production infrastructure.

- **Endpoint**: `http://127.0.0.1:8080/chat`
- **Output**: Returns a simulated generative response with source and confidence metrics.

## Forwarding Logic
The bridge server implements a conditional forwarding mechanism based on the `RuleEngine` decision:

1. **Trigger**: When `RuleEngine` returns `decision: "forward"`.
2. **Payload**: The bridge extracts the `message` and `session_id` and forwards them as a JSON POST request.
3. **Timeout**: A strict 5-second timeout is enforced to maintain system responsiveness.

## Error Handling
- **Service Unavailable**: If the legacy server is offline or fails to respond within the timeout, the Bridge returns an **HTTP 502 Bad Gateway** error.
- **Traceability**: All requests, whether blocked, answered locally, or forwarded, maintain the original `trace_id` for end-to-end debugging.

## Security Warning
**CRITICAL**: The legacy server must never be publicly exposed. All incoming traffic must be routed through the UniGuru Bridge middleware to ensure safety and governance rules are applied before any generative processing occurs.
