from fastapi.testclient import TestClient

from uniguru.service import api as api_module
from uniguru.service.api import app


client = TestClient(app)


def test_bhiv_post_ask_returns_ontology_reference() -> None:
    response = client.post(
        "/ask",
        json={
            "user_query": "What is a qubit?",
            "session_id": "bhiv-integration-1",
            "allow_web_retrieval": False,
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert "ontology_reference" in payload
    reference = payload["ontology_reference"]
    assert reference.get("concept_id")
    assert reference.get("snapshot_hash")
    assert isinstance(reference.get("truth_level"), int)
    assert reference.get("domain")


def test_canonical_contract_request_shape_is_accepted() -> None:
    response = client.post(
        "/ask",
        json={
            "query": "What is a qubit?",
            "session_id": "bhiv-integration-contract",
            "allow_web": False,
            "context": {"origin": "bhiv-tests"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "decision" in payload
    assert "answer" in payload
    assert "ontology_reference" in payload
    assert "verification_status" in payload
    assert "reasoning_trace" in payload
    assert "governance_output" in payload
    assert "enforcement_signature" in payload


def test_malformed_input_is_rejected() -> None:
    response = client.post(
        "/ask",
        json={
            "query": "What is a qubit?",
            "unknown_field": "not-allowed",
        },
    )
    assert response.status_code == 422


def test_public_ontology_endpoint_resolves_concept() -> None:
    ask_response = client.post(
        "/ask",
        json={"user_query": "Explain ahimsa", "session_id": "bhiv-integration-2"},
    )
    assert ask_response.status_code == 200
    concept_id = ask_response.json()["ontology_reference"]["concept_id"]

    response = client.get(f"/ontology/concept/{concept_id}")
    assert response.status_code == 200
    payload = response.json()

    assert payload["concept_id"] == concept_id
    assert payload.get("snapshot_hash")
    assert isinstance(payload.get("truth_level"), int)
    assert payload.get("domain")
    assert "immutable" in payload


def test_observability_endpoints_exposed() -> None:
    live = client.get("/health/live")
    root_ready = client.get("/ready")
    ready = client.get("/health/ready")
    metrics = client.get("/metrics")
    dashboard = client.get("/monitoring/dashboard")

    assert live.status_code == 200
    assert root_ready.status_code == 200
    assert ready.status_code == 200
    assert metrics.status_code == 200
    assert dashboard.status_code == 200
    assert "uniguru_requests_total" in metrics.text
    assert "uniguru_requests_per_minute" in metrics.text
    assert "uniguru_verification_success_rate" in metrics.text


def test_rate_limit_is_enforced() -> None:
    original_limit = api_module._RATE_LIMIT_MAX_REQUESTS
    original_window = api_module._RATE_LIMIT_WINDOW_SECONDS
    try:
        api_module._RATE_LIMIT_MAX_REQUESTS = 1
        api_module._RATE_LIMIT_WINDOW_SECONDS = 60
        api_module._RATE_LIMIT_BUCKET.clear()

        first = client.post("/ask", json={"query": "What is a qubit?"})
        second = client.post("/ask", json={"query": "Explain ahimsa"})

        assert first.status_code == 200
        assert second.status_code == 429
    finally:
        api_module._RATE_LIMIT_MAX_REQUESTS = original_limit
        api_module._RATE_LIMIT_WINDOW_SECONDS = original_window
        api_module._RATE_LIMIT_BUCKET.clear()
