# Live Integration Safety Verification

This file captures static verification and recommended live checks to confirm boundary-safe integration.

## Static checks performed ✅
1. **Adapter presence:** `adapters/uniguru_signal_adapter.py` created and verified to be a thin, passive adapter that attempts to call an intent classifier if present and otherwise attaches a neutral signal.
2. **Signal contract alignment:** The adapter produces a `Signal` with fields: `intent`, `confidence`, `ambiguity`, `risk`, `repetition`, `emotional_load`, and `raw`. This matches `docs/AI_Being_Context_Contract.md`.
3. **No execution-path changes:** The adapter attaches signals in a background daemon thread and returns immediately, ensuring no blocking or new decision paths are introduced.

## Recommended live flow checks (2–3 checks) 🔧
1. **Signal Attachment Check (Live Request):** Send a representative request and confirm that, after UniGuru runs, the request context contains `uniguru_signal` with the agreed fields.
   - Success criteria: The `uniguru_signal` is present and populated (or has an explicit `note` if classifier missing).
2. **AI Being Visibility Check:** Confirm AI Being can read the `uniguru_signal` but cannot change Enforcement outputs.
   - Success criteria: AI Being reads the signal but final Enforcement decisions and responses are unchanged.
3. **Enforcement Non-Interference Check:** Confirm Enforcement behavior identical before and after adapter deployment (same inputs → same outputs when classifier unavailable or neutral).

## Observations & TODOs
- TODO: Map concrete LLM/RAG modules in the live system and verify that UniGuru does not inject execution control into them.
- TODO: If a production classifier is available, update `_find_classifier()` import paths inside `adapters/uniguru_signal_adapter.py` and re-run the live checks.

*Stop and document issues if any check fails.*

