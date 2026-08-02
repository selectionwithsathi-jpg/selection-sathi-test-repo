import logging
import os
import sys
import time

import httpx
import pytest

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    force=True,
)
logger = logging.getLogger("api_tests")

BASE_URL = os.environ.get("BASE_URL", "https://selectionsathi.com").rstrip("/")
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "S3l$athi#Adm!n@2026xK"


def _redact_headers(headers):
    redacted = {}
    for k, v in headers.items():
        if k.lower() == "authorization" and len(v) > 15:
            redacted[k] = v[:15] + "...<redacted>"
        else:
            redacted[k] = v
    return redacted


class _ThrottledTransport(httpx.BaseTransport):
    """Enforces a minimum gap between requests and logs each request/response.
    The target has repeatedly gone down (502s cascading across many endpoints
    for a sustained stretch) under even modest, throttled sequential request
    volume, so requests are kept slow and every call in this suite must go
    through this transport."""

    def __init__(self, inner, min_interval=0.8):
        self._inner = inner
        self._gap = min_interval
        self._last = 0.0

    def handle_request(self, request):
        wait = self._gap - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

        body_preview = ""
        if request.content:
            try:
                body_preview = request.content.decode("utf-8", errors="replace")[:300]
            except Exception:
                body_preview = "<binary>"
        logger.info(
            "--> %s %s headers=%s%s",
            request.method,
            request.url,
            _redact_headers(dict(request.headers)),
            f" body={body_preview}" if body_preview else "",
        )

        start = time.monotonic()
        response = self._inner.handle_request(request)
        response.read()
        elapsed_ms = (time.monotonic() - start) * 1000

        preview = response.text[:300].replace("\n", " ")
        logger.info(
            "<-- %s %s status=%s time=%.0fms body=%s",
            request.method,
            request.url,
            response.status_code,
            elapsed_ms,
            preview,
        )
        return response


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def client(base_url):
    transport = _ThrottledTransport(httpx.HTTPTransport())
    with httpx.Client(
        base_url=base_url,
        timeout=30.0,
        follow_redirects=True,
        verify=False,
        transport=transport,
    ) as c:
        yield c


@pytest.fixture(scope="session")
def admin_token(client):
    resp = client.post(
        "/api/auth/admin-login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.status_code} {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def auth_headers(admin_headers):
    return admin_headers


@pytest.fixture(scope="session")
def dev_login_token(client):
    resp = client.post("/api/auth/dev-login", json={})
    assert resp.status_code == 200, f"dev-login failed: {resp.status_code} {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def student_headers(dev_login_token):
    return {"Authorization": f"Bearer {dev_login_token}"}


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def _log_test_lifecycle(request):
    logger.info("=" * 70)
    logger.info("TEST START: %s", request.node.nodeid)
    yield
    rep_call = getattr(request.node, "rep_call", None)
    result = rep_call.outcome.upper() if rep_call else "UNKNOWN"
    logger.info("TEST END: %s -> %s", request.node.nodeid, result)
