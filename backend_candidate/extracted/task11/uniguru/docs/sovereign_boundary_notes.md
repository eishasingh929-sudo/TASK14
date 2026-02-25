# Sovereign Boundary Enforcement Notes

## Definition
Sovereign boundaries define strict separation between:
- UniGuru LM (intelligence generation)
- BHIV Core (policy enforcement)
- BHIV Bucket (event logging)
- Karma Tracker (read-only consumer)

## Boundary Rules

1. Bucket never influences LM behavior.
2. Karma Tracker only reads from Bucket.
3. UniGuru LM never directly communicates with Karma.
4. BHIV Core is the only policy authority.
5. UI never bypasses Core enforcement.

## Leakage Prevention

- LM outputs are sanitized before logging.
- No internal reasoning chains are stored in Bucket.
- Only finalized outputs are visible to downstream systems.

## Edge Case Handling

- Policy violation → response blocked, event logged.
- Emotional distress → safe response, event logged.
- System error → deterministic fallback, event logged.

## Result

System remains:
- Auditable
- Deterministic
- Sovereign-safe
