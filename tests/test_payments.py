def test_payments_plans_public(client):
    resp = client.get("/api/payments/plans")
    assert resp.status_code == 200


def test_payments_create_order_requires_auth(client):
    resp = client.post("/api/payments/create-order", json={})
    assert resp.status_code in (401, 403)


def test_payments_create_order_missing_fields_returns_422(client, student_headers):
    resp = client.post("/api/payments/create-order", json={}, headers=student_headers)
    assert resp.status_code in (400, 422)


def test_payments_verify_requires_auth(client):
    resp = client.post("/api/payments/verify", json={})
    assert resp.status_code in (401, 403)


def test_payments_webhook_public_endpoint_handles_invalid_payload(client):
    resp = client.post("/api/payments/webhook", json={})
    assert resp.status_code in (200, 400, 401, 422)


def test_payments_exam_access_requires_auth(client):
    resp = client.get("/api/payments/exam-access/ssc-cgl")
    assert resp.status_code in (401, 403)


def test_payments_my_subscription_requires_auth(client):
    resp = client.get("/api/payments/my-subscription")
    assert resp.status_code in (401, 403)


def test_payments_my_subscription_with_auth(client, student_headers):
    resp = client.get("/api/payments/my-subscription", headers=student_headers)
    assert resp.status_code == 200


def test_payments_credit_history_requires_auth(client):
    resp = client.get("/api/payments/credit-history")
    assert resp.status_code in (401, 403)


def test_payments_my_referral_requires_auth(client):
    resp = client.get("/api/payments/my-referral")
    assert resp.status_code in (401, 403)


def test_payments_apply_referral_requires_auth(client):
    resp = client.post("/api/payments/apply-referral", json={"code": "X"})
    assert resp.status_code in (401, 403)


def test_payments_wallet_purchase_requires_auth(client):
    resp = client.post("/api/payments/wallet-purchase", json={})
    assert resp.status_code in (401, 403)
