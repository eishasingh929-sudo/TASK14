from __future__ import annotations

import hashlib
import os
import re
import threading
import time
import uuid
import requests
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from urllib.parse import urlparse, urlunparse

from uniguru.runtime_env import load_project_env
from uniguru.service.live_service import LiveUniGuruService
from uniguru.service.response_format import build_structured_answer
from uniguru.service.query_classifier import QueryType, classify_query

load_project_env()


class QueryRoutingType(str, Enum):
    KNOWLEDGE_QUERY = "KNOWLEDGE_QUERY"
    SYSTEM_QUERY = "SYSTEM_QUERY"
    WORKFLOW_QUERY = "WORKFLOW_QUERY"
    TOOL_QUERY = "TOOL_QUERY"
    GENERAL_LLM_QUERY = "GENERAL_LLM_QUERY"


class RouteTarget(str, Enum):
    ROUTE_UNIGURU = "ROUTE_UNIGURU"
    ROUTE_LLM = "ROUTE_LLM"
    ROUTE_WORKFLOW = "ROUTE_WORKFLOW"
    ROUTE_SYSTEM = "ROUTE_SYSTEM"


_SYSTEM_PATTERNS = (
    r"\bsudo\b",
    r"\brm\s+-",
    r"\bdel\s+",
    r"\bformat\s+",
    r"\bshutdown\b",
    r"\brestart\b",
    r"\bsystemctl\b",
    r"\bpowershell\b",
    r"\bcmd\.exe\b",
)

_WORKFLOW_PATTERNS = (
    r"\bcreate\b.*\b(ticket|task|workflow|incident|approval)\b",
    r"\bupdate\b.*\b(ticket|task|workflow|incident|approval)\b",
    r"\bapprove\b.*\b(request|workflow|task|ticket)\b",
    r"\bschedule\b.*\b(call|meeting|job|workflow|task)\b",
    r"\bstart\b.*\bworkflow\b",
    r"\btrigger\b.*\bworkflow\b",
)

_TOOL_PATTERNS = (
    r"\buse\b.*\btool\b",
    r"\binvoke\b.*\bapi\b",
    r"\bexecute\b.*\bscript\b",
    r"\brun\b.*\b(sql|query|tool)\b",
)

_KNOWLEDGE_PATTERNS = (
    r"^(what|who|when|where|why|how)\b",
    r"^(am|is|are|can|could|should|would|do|does|did)\s+i\b",
    r"^what should i\b",
    r"^how should i\b",
    r"^how do i\b",
    r"\bexplain\b",
    r"\bdefine\b",
    r"\btell me about\b",
    r"\bdifference between\b",
)

_SUPPORT_HINT_PATTERNS = (
    r"\badmission\b",
    r"\badmissions\b",
    r"\bcounsel",
    r"\bdocument\b",
    r"\bseat allot",
    r"\bmerit\b",
    r"\bplacement\b",
    r"\bresume\b",
    r"\bportfolio\b",
    r"\blinkedin\b",
    r"\breferral\b",
    r"\breporting day\b",
    r"\binterview\b",
    r"\bcareer\b",
    r"\bquantum\b",
    r"\bqubit\b",
    r"\bjain\b",
    r"\bmahavira\b",
    r"\bahimsa\b",
    r"\bswaminarayan\b",
    r"\bvachanamrut\b",
    r"\bswamini vato\b",
    r"\bvedic\b",
    r"\bnyaya\b",
    r"\bgrover\b",
    r"\bshor\b",
    r"\bquantum algorithm\b",
)

_GENERAL_CHAT_PATTERNS = (
    r"^(hi|hello|hey)\b",
    r"\bhow are you\b",
    r"\bwhat's up\b",
    r"\bhow is it going\b",
)

SAFE_FALLBACK_PREFIX = "I am still learning this topic, but here is a basic explanation..."
DEFAULT_LOCAL_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_LOCAL_OLLAMA_MODEL = "llama3"
LLM_BUSY_MESSAGE = "The configured LLM endpoint did not return a usable response."


@dataclass(frozen=True)
class RoutingDecision:
    query_type: QueryRoutingType
    route: RouteTarget


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class _LatencyCircuitBreaker:
    def __init__(self, threshold_ms: float, open_seconds: float) -> None:
        self.threshold_ms = threshold_ms
        self.open_seconds = open_seconds
        self._open_until = 0.0
        self._lock = threading.Lock()

    def should_fallback(self) -> bool:
        now = time.monotonic()
        with self._lock:
            return now < self._open_until

    def record_latency(self, latency_ms: float) -> None:
        if latency_ms <= self.threshold_ms:
            return
        with self._lock:
            self._open_until = max(self._open_until, time.monotonic() + self.open_seconds)


class ConversationRouter:
    def __init__(
        self,
        uniguru_service: Optional[LiveUniGuruService] = None,
        latency_threshold_ms: Optional[float] = None,
        breaker_open_seconds: Optional[float] = None,
        allow_unverified_fallback: Optional[bool] = None,
    ) -> None:
        self._service = uniguru_service or LiveUniGuruService()
        threshold = latency_threshold_ms or float(os.getenv("UNIGURU_ROUTER_LATENCY_THRESHOLD_MS", "1200"))
        open_seconds = breaker_open_seconds or float(os.getenv("UNIGURU_ROUTER_CIRCUIT_OPEN_SECONDS", "30"))
        if allow_unverified_fallback is None:
            allow_unverified_fallback = (
                os.getenv("UNIGURU_ROUTER_UNVERIFIED_FALLBACK", "true").strip().lower() in {"1", "true", "yes", "on"}
            )
        self._allow_unverified_fallback = bool(allow_unverified_fallback)
        self._breaker = _LatencyCircuitBreaker(threshold_ms=threshold, open_seconds=open_seconds)
        self._llm_url = self._normalize_llm_url(os.getenv("UNIGURU_LLM_URL", "").strip())
        self._llm_model = os.getenv("UNIGURU_LLM_MODEL", DEFAULT_LOCAL_OLLAMA_MODEL).strip() or DEFAULT_LOCAL_OLLAMA_MODEL
        self._llm_timeout = float(os.getenv("UNIGURU_LLM_TIMEOUT_SECONDS", "8"))
        self._llm_max_tokens = int(os.getenv("UNIGURU_LLM_MAX_TOKENS", "160"))
        self._llm_fast_max_tokens = int(os.getenv("UNIGURU_LLM_FAST_MAX_TOKENS", "96"))
        self._llm_temperature = float(os.getenv("UNIGURU_LLM_TEMPERATURE", "0.2"))
        self._llm_probe_ttl = float(os.getenv("UNIGURU_LLM_HEALTH_CACHE_SECONDS", "30"))
        self._llm_probe_cache: Dict[str, Any] = {"checked_at": 0.0, "usable": False, "reason": "unprobed"}

    def llm_status(self) -> Dict[str, Any]:
        configured = bool(self._llm_url)
        available_models = self._available_local_models() if configured else []
        reachable = bool(available_models)
        selected_model = self._select_fallback_model(self._llm_model) if configured else None
        model_loaded = bool(selected_model and selected_model in available_models)
        probe = self._probe_llm_generation(selected_model or self._llm_model) if configured and model_loaded else {
            "usable": False,
            "reason": "Model not loaded.",
        }
        return {
            "configured": configured,
            "endpoint": self._llm_url or None,
            "model": self._llm_model or None,
            "selected_model": selected_model,
            "available_models": available_models,
            "reachable": reachable,
            "model_loaded": model_loaded,
            "usable": bool(probe.get("usable")),
            "probe_reason": probe.get("reason"),
            "available": bool(reachable and model_loaded and probe.get("usable")),
        }

    @staticmethod
    def _normalize_llm_url(raw_url: str) -> str:
        candidate = str(raw_url or "").strip()
        if not candidate or candidate.startswith("internal://"):
            return DEFAULT_LOCAL_OLLAMA_URL

        parsed = urlparse(candidate)
        if parsed.scheme not in {"http", "https"}:
            return DEFAULT_LOCAL_OLLAMA_URL
        netloc = parsed.netloc
        if parsed.hostname == "localhost":
            port = f":{parsed.port}" if parsed.port else ""
            netloc = f"127.0.0.1{port}"
        path = parsed.path or ""
        if path in {"", "/"}:
            path = "/api/generate"
        return urlunparse((parsed.scheme, netloc, path, "", "", ""))

    def _llm_tags_url(self) -> str:
        if not self._llm_url:
            return ""
        parsed = urlparse(self._llm_url)
        path = parsed.path or ""
        if path.endswith("/api/generate"):
            path = f"{path[:-len('/generate')]}/tags"
        elif path in {"", "/"}:
            path = "/api/tags"
        return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))

    def _available_local_models(self) -> list[str]:
        tags_url = self._llm_tags_url()
        if not tags_url:
            return []
        try:
            response = requests.get(tags_url, timeout=min(1.0, self._llm_timeout))
            response.raise_for_status()
            data = response.json()
        except Exception:
            return []

        models = data.get("models") if isinstance(data, dict) else []
        if not isinstance(models, list):
            return []

        names: list[str] = []
        for item in models:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or item.get("model") or "").strip()
            if name and name not in names:
                names.append(name)
        return names

    def _select_fallback_model(self, preferred: str) -> str:
        available = self._available_local_models()
        candidates = [preferred, preferred.replace("_", "-"), DEFAULT_LOCAL_OLLAMA_MODEL]
        for candidate in candidates:
            normalized = str(candidate or "").strip()
            if normalized and normalized in available:
                return normalized
        return available[0] if available else (preferred or DEFAULT_LOCAL_OLLAMA_MODEL)

    def route_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        started = time.perf_counter()
        context_map = dict(context or {})
        session_id = context_map.get("session_id")

        preflight_response = None
        if hasattr(self._service, "preflight_response"):
            preflight_response = self._service.preflight_response(
                user_query=query,
                session_id=session_id,
                context=context_map,
            )
        if preflight_response is not None:
            resolved_route = self._resolve_preflight_route(query=query, response=preflight_response)
            routing_latency = (time.perf_counter() - started) * 1000
            query_type = (
                QueryRoutingType.SYSTEM_QUERY
                if resolved_route == RouteTarget.ROUTE_SYSTEM.value
                else QueryRoutingType.KNOWLEDGE_QUERY
            )
            preflight_response["routing"] = {
                "query_type": query_type.value,
                "route": resolved_route,
                "router_latency_ms": round(routing_latency, 3),
            }
            return preflight_response

        query_type = self.classify(query=query, context=context_map)
        target = self.select_route(query_type=query_type)

        if target == RouteTarget.ROUTE_SYSTEM:
            response = self._build_system_block_response(query_type=query_type, session_id=session_id)
        elif target == RouteTarget.ROUTE_WORKFLOW:
            response = self._build_workflow_response(query=query, query_type=query_type, session_id=session_id)
        elif target == RouteTarget.ROUTE_LLM:
            response = self._build_llm_response(
                query=query,
                query_type=query_type,
                session_id=session_id,
                warning=None,
            )
        else:
            response = self._dispatch_to_uniguru(query=query, context=context_map, query_type=query_type)

        resolved_route = str(response.pop("_resolved_route", target.value))
        routing_latency = (time.perf_counter() - started) * 1000
        response["routing"] = {
            "query_type": query_type.value,
            "route": resolved_route,
            "router_latency_ms": round(routing_latency, 3),
        }
        return response

    def classify(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryRoutingType:
        text = query.strip().lower()
        if not text:
            return QueryRoutingType.GENERAL_LLM_QUERY

        if any(re.search(pattern, text) for pattern in _SYSTEM_PATTERNS):
            return QueryRoutingType.SYSTEM_QUERY
        if any(re.search(pattern, text) for pattern in _WORKFLOW_PATTERNS):
            return QueryRoutingType.WORKFLOW_QUERY
        if any(re.search(pattern, text) for pattern in _TOOL_PATTERNS):
            return QueryRoutingType.TOOL_QUERY
        if any(re.search(pattern, text) for pattern in _GENERAL_CHAT_PATTERNS):
            return QueryRoutingType.GENERAL_LLM_QUERY

        upstream_type = classify_query(text)
        if upstream_type in {
            QueryType.KNOWLEDGE_QUERY,
            QueryType.CONCEPT_QUERY,
            QueryType.EXPLANATION_QUERY,
            QueryType.WEB_LOOKUP,
        }:
            if self._has_support_hint(text) and (
                any(re.search(pattern, text) for pattern in _KNOWLEDGE_PATTERNS)
                or upstream_type != QueryType.KNOWLEDGE_QUERY
            ):
                return QueryRoutingType.KNOWLEDGE_QUERY
        return QueryRoutingType.GENERAL_LLM_QUERY

    @staticmethod
    def _has_support_hint(text: str) -> bool:
        return any(re.search(pattern, text) for pattern in _SUPPORT_HINT_PATTERNS)

    @staticmethod
    def _resolve_preflight_route(query: str, response: Dict[str, Any]) -> str:
        text = str(query or "").lower()
        governance_flags = response.get("governance_flags") or {}
        if any(re.search(pattern, text) for pattern in _SYSTEM_PATTERNS) or governance_flags.get("safety"):
            return RouteTarget.ROUTE_SYSTEM.value
        return RouteTarget.ROUTE_UNIGURU.value

    @staticmethod
    def select_route(query_type: QueryRoutingType) -> RouteTarget:
        if query_type == QueryRoutingType.KNOWLEDGE_QUERY:
            return RouteTarget.ROUTE_UNIGURU
        if query_type == QueryRoutingType.SYSTEM_QUERY:
            return RouteTarget.ROUTE_SYSTEM
        if query_type in {QueryRoutingType.WORKFLOW_QUERY, QueryRoutingType.TOOL_QUERY}:
            return RouteTarget.ROUTE_WORKFLOW
        return RouteTarget.ROUTE_LLM

    def _dispatch_to_uniguru(
        self,
        query: str,
        context: Dict[str, Any],
        query_type: QueryRoutingType,
    ) -> Dict[str, Any]:
        session_id = context.get("session_id")
        allow_web = bool(context.get("allow_web", False))
        legacy_type = classify_query(query)
        effective_allow_web = allow_web or legacy_type == QueryType.WEB_LOOKUP

        if self._breaker.should_fallback():
            return self._build_llm_response(
                query=query,
                query_type=query_type,
                session_id=session_id,
                warning="UniGuru latency circuit breaker active. Response delegated to LLM.",
            )

        started = time.perf_counter()
        try:
            response = self._service.ask(
                user_query=query,
                session_id=session_id,
                context={**context, "preflight_checked": True},
                allow_web_retrieval=effective_allow_web,
            )
        except Exception as exc:
            return self._build_llm_response(
                query=query,
                query_type=query_type,
                session_id=session_id,
                warning=f"UniGuru KB path failed ({exc}). Falling back to conversational mode.",
            )
        latency_ms = (time.perf_counter() - started) * 1000
        self._breaker.record_latency(latency_ms)

        decision = str(response.get("decision") or "").strip().lower()
        has_answer = bool(str(response.get("answer") or "").strip())

        if decision == "answer" and has_answer:
            return response

        if not self._allow_unverified_fallback:
            return response

        return self._build_llm_response(
            query=query,
            query_type=query_type,
            session_id=session_id,
            warning=str(response.get("reason") or "").strip() or None,
        )

    def _build_system_block_response(
        self,
        query_type: QueryRoutingType,
        session_id: Optional[str],
    ) -> Dict[str, Any]:
        answer = build_structured_answer(
            answer="System-level command requests are blocked by BHIV routing policy.",
            details="The router stopped a potentially unsafe request before it reached the backend.",
            source="BHIV routing policy",
        )
        return self._build_router_contract_response(
            decision="block",
            answer=answer,
            reason="ROUTE_SYSTEM policy enforced.",
            query_type=query_type,
            route=RouteTarget.ROUTE_SYSTEM,
            verification_status="UNVERIFIED",
            session_id=session_id,
            governance_allowed=False,
            governance_reason="System command blocked by router policy.",
        )

    def _build_workflow_response(
        self,
        query: str,
        query_type: QueryRoutingType,
        session_id: Optional[str],
    ) -> Dict[str, Any]:
        answer = build_structured_answer(
            answer=f"Delegated to workflow engine: {query}",
            details="This request matched a workflow pattern and was handed off for task processing.",
            source="Workflow router",
        )
        return self._build_router_contract_response(
            decision="answer",
            answer=answer,
            reason="ROUTE_WORKFLOW policy applied.",
            query_type=query_type,
            route=RouteTarget.ROUTE_WORKFLOW,
            verification_status="PARTIAL",
            session_id=session_id,
            governance_allowed=True,
            governance_reason="Delegated workflow response.",
        )

    def _build_llm_response(
        self,
        query: str,
        query_type: QueryRoutingType,
        session_id: Optional[str],
        warning: Optional[str],
    ) -> Dict[str, Any]:
        llm_result = self._request_llm(query=query, session_id=session_id)
        answer = build_structured_answer(
            answer=llm_result["answer"],
            details=warning or llm_result["details"],
            source=llm_result["source_label"],
        )
        return self._build_router_contract_response(
            decision="answer",
            answer=answer,
            reason=llm_result["reason"],
            query_type=query_type,
            route=RouteTarget.ROUTE_LLM,
            verification_status="UNVERIFIED",
            session_id=session_id,
            governance_allowed=True,
            governance_reason=llm_result["governance_reason"],
            extra={"llm_metadata": llm_result["metadata"]},
        )

    def _request_llm(self, query: str, session_id: Optional[str]) -> Dict[str, Any]:
        status = self.llm_status()
        if not self._llm_url:
            return {
                "answer": LLM_BUSY_MESSAGE,
                "reason": "ROUTE_LLM selected but UNIGURU_LLM_URL is not configured.",
                "governance_reason": "LLM route unavailable because no endpoint is configured.",
                "details": "The configured LLM endpoint is unavailable. No simulated fallback answer was used.",
                "source_label": "LLM endpoint not configured",
                "metadata": {
                    "provider": "unavailable",
                    "endpoint": None,
                    "model": self._llm_model,
                    "live_response": False,
                },
            }
        if status.get("reachable") and status.get("model_loaded") and not status.get("available"):
            selected_model = status.get("selected_model") or self._llm_model
            return {
                "answer": LLM_BUSY_MESSAGE,
                "reason": "ROUTE_LLM selected but the configured LLM endpoint is not currently usable.",
                "governance_reason": f"LLM health probe failed: {status.get('probe_reason')}",
                "details": "The LLM endpoint did not pass a live generation probe, so UniGuru returned an explicit availability error instead of a fabricated answer.",
                "source_label": f"{selected_model} via {self._llm_url}",
                "metadata": {
                    "provider": "local-ollama",
                    "endpoint": self._llm_url,
                    "model": selected_model,
                    "live_response": False,
                    "usable": False,
                },
            }

        payload = self._build_llm_payload(
            model_name=self._llm_model or DEFAULT_LOCAL_OLLAMA_MODEL,
            query=query,
            max_tokens=self._llm_max_tokens,
        )

        def _call_llm(request_payload: Dict[str, Any]) -> Dict[str, Any]:
            response = requests.post(
                self._llm_url,
                json=request_payload,
                timeout=self._llm_timeout,
            )
            response.raise_for_status()
            return response.json()

        try:
            data = _call_llm(payload)
        except Exception as exc:
            fallback_model = self._select_fallback_model(payload["model"])
            if fallback_model and fallback_model != payload["model"]:
                try:
                    payload = self._build_llm_payload(
                        model_name=fallback_model,
                        query=query,
                        max_tokens=self._llm_fast_max_tokens,
                    )
                    data = _call_llm(payload)
                except Exception as retry_exc:
                    return {
                        "answer": LLM_BUSY_MESSAGE,
                        "reason": "ROUTE_LLM request to local Ollama endpoint failed.",
                        "governance_reason": f"Local Ollama route returned an integration failure: {retry_exc}",
                        "details": "The configured LLM endpoint timed out or returned no usable content.",
                        "source_label": f"{payload['model']} via {self._llm_url}",
                        "metadata": {
                            "provider": "local-ollama",
                            "endpoint": self._llm_url,
                            "model": payload["model"],
                            "live_response": False,
                        },
                    }
            else:
                return {
                    "answer": LLM_BUSY_MESSAGE,
                    "reason": "ROUTE_LLM request to local Ollama endpoint failed.",
                    "governance_reason": f"Local Ollama route returned an integration failure: {exc}",
                    "details": "The configured LLM endpoint timed out or returned no usable content.",
                    "source_label": f"{payload['model']} via {self._llm_url}",
                    "metadata": {
                        "provider": "local-ollama",
                        "endpoint": self._llm_url,
                        "model": payload["model"],
                        "live_response": False,
                    },
                }

        answer = str(
            data.get("answer")
            or data.get("response")
            or data.get("output")
            or data.get("content")
            or (data.get("message") or {}).get("content")
            or ""
        ).strip()
        if not answer and isinstance(data.get("choices"), list) and data["choices"]:
            answer = str(
                (data["choices"][0].get("message") or {}).get("content")
                or data["choices"][0].get("text")
                or ""
            ).strip()

        live_response = bool(answer)
        if not answer:
            answer = LLM_BUSY_MESSAGE

        return {
            "answer": answer,
            "reason": "ROUTE_LLM policy applied via local Ollama endpoint.",
            "governance_reason": "Delegated open-chat response through local Ollama service.",
            "details": "General-purpose question answered by the configured fallback language model.",
            "source_label": f"{payload['model']} via {self._llm_url}",
            "metadata": {
                "provider": "local-ollama",
                "endpoint": self._llm_url,
                "model": payload["model"],
                "live_response": live_response,
            },
        }

    def _build_llm_payload(self, *, model_name: str, query: str, max_tokens: int) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model_name,
            "prompt": query,
            "stream": False,
        }
        parsed = urlparse(self._llm_url)
        is_local_generate = parsed.hostname in {"127.0.0.1", "localhost"} and parsed.path.endswith("/api/generate")
        if is_local_generate:
            payload["options"] = {
                "num_predict": max(32, int(max_tokens)),
                "temperature": self._llm_temperature,
            }
        return payload

    def _probe_llm_generation(self, model_name: str) -> Dict[str, Any]:
        now = time.monotonic()
        cached_at = float(self._llm_probe_cache.get("checked_at", 0.0) or 0.0)
        if now - cached_at < self._llm_probe_ttl:
            return {
                "usable": bool(self._llm_probe_cache.get("usable")),
                "reason": str(self._llm_probe_cache.get("reason") or "cached"),
            }

        payload = self._build_llm_payload(
            model_name=model_name or self._llm_model,
            query="Reply with one word: ready",
            max_tokens=min(self._llm_fast_max_tokens, 24),
        )
        try:
            response = requests.post(
                self._llm_url,
                json=payload,
                timeout=min(2.5, self._llm_timeout),
            )
            response.raise_for_status()
            data = response.json()
            answer = str(
                data.get("answer")
                or data.get("response")
                or data.get("output")
                or data.get("content")
                or (data.get("message") or {}).get("content")
                or ""
            ).strip()
            usable = bool(answer)
            reason = "Generation probe succeeded." if usable else "Generation probe returned empty content."
        except Exception as exc:
            usable = False
            reason = f"Generation probe failed: {exc}"

        self._llm_probe_cache = {"checked_at": now, "usable": usable, "reason": reason}
        return {"usable": usable, "reason": reason}

    @staticmethod
    def _build_service_continuity_answer(query: str) -> str:
        _ = query
        return LLM_BUSY_MESSAGE

    def _build_router_contract_response(
        self,
        decision: str,
        answer: str,
        reason: str,
        query_type: QueryRoutingType,
        route: RouteTarget,
        verification_status: str,
        session_id: Optional[str],
        governance_allowed: bool,
        governance_reason: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        signature_payload = f"{decision}|{answer}|{route.value}|{request_id}"
        signature = hashlib.sha256(signature_payload.encode("utf-8")).hexdigest()
        response = {
            "decision": decision,
            "answer": answer,
            "session_id": session_id,
            "reason": reason,
            "_resolved_route": route.value,
            "ontology_reference": {
                "concept_id": f"router::{query_type.value.lower()}",
                "domain": "routing",
                "snapshot_version": 0,
                "snapshot_hash": "router-delegated",
                "truth_level": 0,
            },
            "reasoning_trace": {
                "sources_consulted": ["conversation_router"],
                "retrieval_confidence": 0.0,
                "ontology_domain": "routing",
                "verification_status": verification_status,
                "verification_details": f"Delegated via {route.value}",
            },
            "governance_flags": {"safety": not governance_allowed},
            "governance_output": {
                "allowed": governance_allowed,
                "reason": governance_reason,
                "flags": {"router_route": route.value},
            },
            "verification_status": verification_status,
            "status_action": "ALLOW_WITH_DISCLAIMER" if governance_allowed else "REFUSE",
            "enforcement_signature": signature,
            "request_id": request_id,
            "sealed_at": _utc_now_iso(),
            "latency_ms": 0.0,
        }
        if extra:
            response.update(extra)
        return response


_DEFAULT_ROUTER = ConversationRouter()


def route_query(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return _DEFAULT_ROUTER.route_query(query=query, context=context)
