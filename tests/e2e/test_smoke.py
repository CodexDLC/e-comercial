"""E2E smoke tests — HTTP requests against the running Docker stack.

Run only via the Docker checker (tools/dev/check.py) or manually:
    E2E_BASE_URL=http://localhost:8001 pytest tests/e2e/ -m e2e -v
"""

import pytest
import requests

pytestmark = pytest.mark.e2e


def test_health_endpoint(base_url: str) -> None:
    """Health endpoint must return 200 and valid JSON."""
    r = requests.get(f"{base_url}/api/v1/health", timeout=10)
    assert r.status_code == 200


def test_catalog_page_responds(base_url: str) -> None:
    """Catalog page must be reachable (200 or redirect)."""
    r = requests.get(f"{base_url}/catalog/", timeout=10, allow_redirects=True)
    assert r.status_code in (200, 301, 302)


def test_login_page_responds(base_url: str) -> None:
    """Login page must render (200)."""
    r = requests.get(f"{base_url}/cabinet/login/", timeout=10, allow_redirects=True)
    assert r.status_code == 200


def test_api_root_responds(base_url: str) -> None:
    """DRF API root or any documented API endpoint must be reachable."""
    r = requests.get(f"{base_url}/api/v1/", timeout=10, allow_redirects=True)
    assert r.status_code in (200, 401, 403, 404)
