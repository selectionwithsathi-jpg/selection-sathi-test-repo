def test_admin_login_oversized_payload_handled_gracefully(client):
    huge = "a" * 200_000
    resp = client.post("/api/auth/admin-login", json={"username": huge, "password": huge})
    assert resp.status_code in (400, 401, 413, 422)


def test_unknown_endpoint_returns_404(client):
    resp = client.get("/api/this-endpoint-does-not-exist")
    assert resp.status_code == 404


def test_invalid_json_body_returns_422(client):
    resp = client.post(
        "/api/auth/admin-login",
        content="{not valid json",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code in (400, 422)


def test_invalid_bearer_token_rejected(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-jwt-token"})
    assert resp.status_code in (401, 403)


def test_malformed_authorization_header_rejected(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "NotBearer sometoken"})
    assert resp.status_code in (401, 403)


def test_tampered_signature_token_rejected(client):
    resp = client.get(
        "/api/auth/me",
        headers={
            "Authorization": (
                "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJzdWIiOiJmYWtlIiwiZXhwIjoxfQ.invalidSignature"
            )
        },
    )
    assert resp.status_code in (401, 403)


def test_exam_code_sql_injection_attempt_safe(client):
    resp = client.get("/api/exams/'; DROP TABLE exams;--")
    assert resp.status_code in (404, 400, 422)


def test_tutorials_search_xss_input_handled_safely(client):
    payload = "<script>alert('xss')</script>"
    resp = client.get("/api/tutorials/search", params={"q": payload})
    assert resp.status_code == 200
    assert payload not in resp.text
