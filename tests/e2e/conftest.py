"""E2E test configuration.

E2E tests run HTTP requests against a fully started Docker environment.
Set E2E_BASE_URL env var to point to your running test stack
(default: http://localhost:8001 — the test compose backend port).
"""

import os

import pytest
import requests as _requests


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("E2E_BASE_URL", "http://localhost:8001")


@pytest.fixture(scope="session")
def http_session(base_url: str) -> _requests.Session:
    """Reusable requests Session pre-configured with the base URL."""
    session = _requests.Session()
    session.base_url = base_url  # type: ignore[attr-defined]
    return session
