# AI Being — Context Contract

## Signals AI Being Can READ (explicit contract) ✅
AI Being is permitted to read the following signals when they are attached by UniGuru to the request context:

- **intent** (string): High-level intent label extracted from user input.
- **confidence** (float | null): Classifier confidence in intent (0.0 - 1.0 scale). May be null if classifier absent.
- **ambiguity** (float | null): Numeric estimate of ambiguity; higher means less clear intent.
- **risk** (float | null): Risk score for safety-sensitive content.
- **repetition** (float | null): Score indicating repetition or spam-like behaviour.
- **emotional_load** (float | null): A measure of emotional intensity detected.

Each signal includes a `raw` dictionary for audit or debugging purposes.

## Prohibitions — What AI Being CANNOT DO ❌
- AI Being **cannot execute** actions, commands, or remote invocations on its own behalf using these signals.
- AI Being **cannot override** Enforcement or mutate final decision authority.
- AI Being **cannot** use these signals to autonomously alter execution paths or to take any persistent decision.

## Usage Notes
- Signals are **read-only context** for AI Being. They are informational only; Enforcement must remain the source of truth for any action decisions.
- If a needed signal is missing in a live system, the AI Being should degrade gracefully and apply conservative defaults.

*If unsure how signals are populated in your runtime, consult `adapters/uniguru_signal_adapter.py` (it is a passive adapter that attaches signals without changing behavior).*
