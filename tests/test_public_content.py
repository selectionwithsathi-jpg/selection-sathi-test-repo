def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "healthy"


def test_tutorials_list_public(client):
    resp = client.get("/api/tutorials")
    assert resp.status_code == 200


def test_tutorials_structure_public(client):
    resp = client.get("/api/tutorials/structure")
    assert resp.status_code == 200


def test_tutorials_shorts_public(client):
    resp = client.get("/api/tutorials/shorts")
    assert resp.status_code == 200


def test_tutorials_search_public(client):
    resp = client.get("/api/tutorials/search", params={"q": "algebra"})
    assert resp.status_code == 200


def test_tutorials_downloadable_public(client):
    resp = client.get("/api/tutorials/downloadable")
    assert resp.status_code == 200


def test_tutorials_invalid_topic_slug_handled(client):
    resp = client.get("/api/tutorials/not-a-real-topic-xyz")
    assert resp.status_code in (404, 200)


def test_latest_updates_counts_public(client):
    resp = client.get("/api/latest-updates/counts")
    assert resp.status_code == 200


def test_latest_updates_today_public(client):
    resp = client.get("/api/latest-updates/today")
    assert resp.status_code == 200


def test_latest_updates_list_public(client):
    resp = client.get("/api/latest-updates")
    assert resp.status_code == 200


def test_leads_create_public(client):
    resp = client.post("/api/leads", json={})
    assert resp.status_code in (200, 201, 400, 422)


def test_webhooks_whatsapp_get_public(client):
    resp = client.get("/api/webhooks/whatsapp")
    assert resp.status_code in (200, 400, 403)


def test_webhooks_whatsapp_post_invalid_payload(client):
    resp = client.post("/api/webhooks/whatsapp", json={})
    assert resp.status_code in (200, 400, 422)
