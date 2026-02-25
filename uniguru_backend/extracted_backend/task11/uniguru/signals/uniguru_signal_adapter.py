"""
Thin, non-blocking UniGuru signal adapter.

Purpose:
- Call the project's intent/behavior classifier (if available) to produce a Signal.
- Attach the Signal to the incoming request context without blocking or affecting control flow.

Restrictions (must be followed by integrators):
- Adapter is non-blocking and passive: it MUST NOT decide, mutate enforcement, or change behavior.
- Adapter must NOT use Bucket, Karma, or Prana to influence decisions. It can surface those signals as context only if they already exist and are read-only.

Integration notes:
- This file intentionally attempts safe imports from common classifier module names but does not assume presence of any specific package.
- If the real classifier lives at a different import path, integrators should add the path in `_find_classifier()`.

TODOs:
- If you have a concrete classifier module, add its import path inside `_find_classifier()` and document the expected classifier output format.
"""
from dataclasses import dataclass
from typing import Optional, Any, Dict
import threading
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Signal:
    intent: Optional[str]
    confidence: Optional[float]
    ambiguity: Optional[float]
    risk: Optional[float]
    repetition: Optional[float]
    emotional_load: Optional[float]
    raw: Dict[str, Any]


def _find_classifier():
    """Attempt to locate an existing classifier. Return a callable or None.

    Notes: This intentionally tries common import paths. If your classifier lives
    elsewhere, add it and keep the adapter minimal and passive.
    """
    candidates = [
        ("intent_classifier", "classify"),
        ("intent_classifier", "classify_intent"),
        ("classifiers.intent", "classify"),
        ("classifiers.intent_classifier", "classify"),
    ]

    for module_name, func_name in candidates:
        try:
            module = __import__(module_name, fromlist=[func_name])
            fn = getattr(module, func_name, None)
            if callable(fn):
                logger.debug("Found classifier: %s.%s", module_name, func_name)
                return fn
        except Exception:
            # Import errors are expected if not present; keep trying.
            continue

    logger.info("No intent classifier found at common import paths. Adapter is passive.")
    return None


def _produce_signal_from_classifier(classifier_fn, text: str) -> Signal:
    # The adapter does not assume classifier return shape; it maps common keys if present.
    try:
        result = classifier_fn(text)
    except Exception as e:
        logger.exception("Classifier call failed: %s", e)
        return Signal(None, None, None, None, None, None, {"error": str(e)})

    # Expect a dict-like result. Map keys conservatively.
    intent = result.get("intent") if isinstance(result, dict) else None
    confidence = result.get("confidence") if isinstance(result, dict) else None
    ambiguity = result.get("ambiguity") if isinstance(result, dict) else None
    risk = result.get("risk") if isinstance(result, dict) else None
    repetition = result.get("repetition") if isinstance(result, dict) else None
    emotional_load = result.get("emotional_load") if isinstance(result, dict) else None

    return Signal(intent, confidence, ambiguity, risk, repetition, emotional_load, dict(result))


def _fallback_signal(text: str) -> Signal:
    # Do not guess; return a minimal, neutral signal with TODO metadata.
    return Signal(None, None, None, None, None, None, {"note": "classifier not available - TODO"})


def attach_uniguru_signal(request: Any, *, text: Optional[str] = None, ctx_key: str = "uniguru_signal") -> None:
    """Attach a UniGuru Signal to the request context non-blockingly.

    - `request` is the framework-specific request object (can be dict-like or an object).
    - `text` optionally overrides how the text is extracted; otherwise the adapter will try to find a `text` attribute or item.
    - `ctx_key` is where the signal will be stored (default: `uniguru_signal`).

    The function returns immediately; the signal is computed and attached in a daemon thread.
    """
    def _worker():
        try:
            classifier = _find_classifier()
            if text is None:
                # Attempt to find text in common spots, without raising
                t = None
                try:
                    t = getattr(request, "text")
                except Exception:
                    try:
                        t = request.get("text")  # dict-like
                    except Exception:
                        t = None
                text_value = t
            else:
                text_value = text

            if text_value is None:
                signal = _fallback_signal(text="")
            elif classifier is None:
                signal = _fallback_signal(text=text_value)
            else:
                signal = _produce_signal_from_classifier(classifier, text_value)

            # Attach signal conservatively.
            try:
                # Prefer `context` or `meta` dicts if available
                if hasattr(request, "context") and isinstance(getattr(request, "context"), dict):
                    getattr(request, "context")[ctx_key] = signal
                elif hasattr(request, "meta") and isinstance(getattr(request, "meta"), dict):
                    getattr(request, "meta")[ctx_key] = signal
                else:
                    # Fallback: set attribute
                    try:
                        setattr(request, ctx_key, signal)
                    except Exception:
                        # As a last resort, if request is dict-like
                        try:
                            request[ctx_key] = signal
                        except Exception:
                            logger.warning("Unable to attach signal to request; no known slot available.")
            except Exception as e:
                logger.exception("Failed to attach UniGuru signal: %s", e)
        except Exception as e:
            logger.exception("Unexpected error in UniGuru signal worker: %s", e)

    th = threading.Thread(target=_worker, daemon=True)
    th.start()


# Example usage (do not run automatically in imports):
# from adapters.uniguru_signal_adapter import attach_uniguru_signal
# attach_uniguru_signal(request)
