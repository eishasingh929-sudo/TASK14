import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set environment for testing BEFORE importing api
os.environ["UNIGURU_API_AUTH_REQUIRED"] = "false"
os.environ["UNIGURU_ALLOWED_CALLERS"] = "bhiv-assistant,gurukul-platform,samachar-platform,internal-testing,uniguru-frontend"

from uniguru.service.api import AskRequest, ask
from uniguru.router.conversation_router import RouteTarget

class MockRequest:
    def __init__(self, headers=None, client_host="127.0.0.1"):
        self.headers = headers or {}
        self.client = MagicMock()
        self.client.host = client_host
        self.url = MagicMock()
        self.url.path = "/ask"
        self.method = "POST"

class TestEcosystemIntegration(unittest.TestCase):
    def setUp(self):
        # Setup environment for testing
        os.environ["UNIGURU_API_AUTH_REQUIRED"] = "false"
        os.environ["UNIGURU_ALLOWED_CALLERS"] = "bhiv-assistant,gurukul-platform,samachar-platform,internal-testing,uniguru-frontend"

    @patch("uniguru.service.api.conversation_router")
    @patch("uniguru.service.api.bucket_telemetry")
    @patch("uniguru.service.api.core_reader")
    def test_bhiv_assistant_knowledge_query(self, mock_core, mock_bucket, mock_router):
        # Mock router response
        mock_router.route_query.return_value = {
            "decision": "answer",
            "answer": "Qubits are quantum bits.",
            "verification_status": "VERIFIED",
            "routing": {"query_type": "KNOWLEDGE_QUERY", "route": "ROUTE_UNIGURU"},
            "request_id": "test-req-1"
        }
        mock_core.align_reference.return_value = {"aligned": True}

        req = AskRequest(query="What is a qubit?", context={"caller": "bhiv-assistant"}, session_id="session-123")
        raw_req = MockRequest()

        response = ask(req, raw_req)

        self.assertEqual(response["routing"]["route"], RouteTarget.ROUTE_UNIGURU.value)
        self.assertEqual(response["verification_status"], "VERIFIED")
        mock_router.route_query.assert_called_once()
        mock_bucket.emit.assert_called()

    @patch("uniguru.service.api.conversation_router")
    def test_gurukul_workflow_query(self, mock_router):
        mock_router.route_query.return_value = {
            "decision": "answer",
            "answer": "Delegated to workflow engine",
            "routing": {"query_type": "WORKFLOW_QUERY", "route": "ROUTE_WORKFLOW"},
            "request_id": "test-req-2"
        }

        req = AskRequest(query="create onboarding ticket", context={"caller": "gurukul-platform"})
        raw_req = MockRequest()

        response = ask(req, raw_req)

        self.assertEqual(response["routing"]["route"], RouteTarget.ROUTE_WORKFLOW.value)

    @patch("uniguru.service.api.conversation_router")
    def test_system_command_blocked(self, mock_router):
        mock_router.route_query.return_value = {
            "decision": "block",
            "answer": "System-level command requests are blocked",
            "routing": {"query_type": "SYSTEM_QUERY", "route": "ROUTE_SYSTEM"},
            "request_id": "test-req-3"
        }

        req = AskRequest(query="sudo rm -rf /", context={"caller": "bhiv-assistant"})
        raw_req = MockRequest()

        response = ask(req, raw_req)

        self.assertEqual(response["decision"], "block")
        self.assertEqual(response["routing"]["route"], RouteTarget.ROUTE_SYSTEM.value)

if __name__ == "__main__":
    unittest.main()
