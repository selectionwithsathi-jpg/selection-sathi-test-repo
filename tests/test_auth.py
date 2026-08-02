def test_admin_login_valid_credentials_returns_tokens(client):
    resp = client.post(
        "/api/auth/admin-login",
        json={"username": "admin", "password": "S3l$athi#Adm!n@2026xK"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("access_token")
    assert body.get("refresh_token")
    assert body.get("token_type") == "bearer"


def test_admin_login_invalid_password_rejected(client):
    resp = client.post("/api/auth/admin-login", json={"username": "admin", "password": "wrong-password-xyz"})
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_admin_login_invalid_username_rejected(client):
    resp = client.post(
        "/api/auth/admin-login",
        json={"username": "not_a_real_admin", "password": "S3l$athi#Adm!n@2026xK"},
    )
    assert resp.status_code in (401, 403, 404)


def test_admin_login_missing_fields_returns_422(client):
    resp = client.post("/api/auth/admin-login", json={})
    assert resp.status_code == 422


def test_admin_login_empty_body_rejected(client):
    resp = client.post("/api/auth/admin-login", content="", headers={"Content-Type": "application/json"})
    assert resp.status_code in (400, 422)


def test_admin_login_sql_injection_attempt_rejected(client):
    resp = client.post("/api/auth/admin-login", json={"username": "admin' OR '1'='1", "password": "x"})
    assert resp.status_code in (401, 422)


def test_admin_login_xss_input_handled_safely(client):
    payload = "<script>alert(1)</script>"
    resp = client.post("/api/auth/admin-login", json={"username": payload, "password": "x"})
    assert resp.status_code in (401, 422)
    assert payload not in resp.text


def test_dev_login_does_not_grant_unauthenticated_session(client):
    """SECURITY: dev-login should require real credentials. Known critical regression --
    this is expected to FAIL until the backdoor is removed (see learnings/UI suite)."""
    resp = client.post("/api/auth/dev-login", json={})
    assert resp.status_code in (401, 403, 404), (
        f"CRITICAL: /api/auth/dev-login granted a live access token with zero credentials "
        f"(status={resp.status_code}, body={resp.text[:200]})"
    )


def test_me_requires_authentication(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code in (401, 403)


def test_me_returns_admin_profile_with_valid_token(client, admin_headers):
    resp = client.get("/api/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json().get("role") == "admin"


def test_profile_update_requires_auth(client):
    resp = client.put("/api/auth/profile", json={"name": "Test"})
    assert resp.status_code in (401, 403)


def test_verify_otp_missing_fields_returns_422(client):
    resp = client.post("/api/auth/verify-otp", json={})
    assert resp.status_code in (400, 422)


def test_verify_otp_invalid_otp_rejected(client):
    resp = client.post("/api/auth/verify-otp", json={"phone": "9999999999", "otp": "000000"})
    assert resp.status_code in (400, 401, 422)


def test_refresh_token_invalid_token_rejected(client):
    resp = client.post("/api/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert resp.status_code in (400, 401, 422)


def test_refresh_token_missing_body_returns_422(client):
    resp = client.post("/api/auth/refresh", json={})
    assert resp.status_code in (400, 422)


def test_create_admin_requires_auth(client):
    resp = client.post("/api/auth/create-admin", json={"username": "hacker", "password": "x"})
    assert resp.status_code in (401, 403)


def test_send_email_otp_requires_auth(client):
    resp = client.post("/api/auth/send-email-otp", json={"email": "test@example.com"})
    assert resp.status_code in (401, 403)


def test_verify_email_otp_requires_auth(client):
    resp = client.post("/api/auth/verify-email-otp", json={"otp": "123456"})
    assert resp.status_code in (401, 403)


def test_delete_account_requires_auth(client):
    resp = client.request("DELETE", "/api/auth/delete-account")
    assert resp.status_code in (401, 403)


def test_request_account_deletion_missing_fields(client):
    resp = client.post("/api/auth/request-account-deletion", json={})
    assert resp.status_code in (400, 401, 403, 422)
