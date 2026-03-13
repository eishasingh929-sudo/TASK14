import json
import pytest
from fastapi.testclient import TestClient
from uniguru.service.api import app

client = TestClient(app)

# Test cases for multiple Indian languages
MULTILINGUAL_TEST_CASES = [
    {
        "filename": "sample-hi.wav",
        "language": "hi",
        "expected_text": "ahimsa ka arth kya hai",
        "expected_decision": "ahimsa (non-violence) is the practice of...",
    },
    {
        "filename": "sample-en.wav",
        "language": "en",
        "expected_text": "what is a qubit",
        "expected_decision": "a qubit or quantum bit is the basic unit of...",
    },
    {
        "filename": "sample-mr.wav",
        "language": "mr",
        "expected_text": "अहिंसेचा अर्थ काय आहे",
        "expected_decision": "अहिंसा म्हणजे कोणासही इजा न करणे...",
    },
]

@pytest.mark.parametrize("case", MULTILINGUAL_TEST_CASES)
def test_voice_query_multilingual(case):
    # Mocking audio bytes
    audio_data = b"mock-audio-content"
    
    headers = {
        "X-Caller-Name": "internal-testing",
        "X-Audio-Filename": case["filename"],
        "X-Voice-Language": case["language"],
        "Content-Type": "audio/wav",
        "Authorization": "Bearer test-token" # Authorization is required in api.py if configured
    }
    
    # We need to make sure UNIGURU_API_AUTH_REQUIRED is false for tests or provide a valid token
    # In api.py, _is_pytest_runtime() bypasses auth, so we should be fine.
    
    response = client.post("/voice/query", content=audio_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "transcription" in data
    assert data["transcription"]["text"] == case["expected_text"]
    assert data["transcription"]["language"] == case["language"]
    
    # Verify router decision (may vary based on mock reasoning, but should exist)
    assert "decision" in data
    assert len(data["decision"]) > 0
    
def test_voice_query_empty_audio():
    headers = {
        "X-Caller-Name": "internal-testing",
        "Content-Type": "audio/wav"
    }
    response = client.post("/voice/query", content=b"", headers=headers)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]

def test_voice_query_unsupported_language():
    # If a language is not in the manifest and no model is loaded, it should fail in manifest mode
    headers = {
        "X-Caller-Name": "internal-testing",
        "X-Audio-Filename": "unknown.wav",
        "Content-Type": "audio/wav"
    }
    response = client.post("/voice/query", content=b"audio", headers=headers)
    # ManifestSTTProvider raises STTUnavailableError which returns 503
    assert response.status_code == 503
    assert "No matching local transcription" in response.json()["detail"]
