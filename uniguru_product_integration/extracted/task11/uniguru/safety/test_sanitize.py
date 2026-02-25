# Boundary: UniGuru-Core
import pytest
from src.uniguru.core import sanitize_output, PolicyViolation


def test_sanitize_rejects_exec_terms():
    with pytest.raises(PolicyViolation):
        sanitize_output('You should run this command: curl http://example')


def test_sanitize_allows_safe_text():
    sanitize_output('This is a safe explanation about architecture and intent.')
