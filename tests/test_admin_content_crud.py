def test_admin_subjects_update_requires_auth(client):
    resp = client.put("/api/admin/subjects/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_subjects_delete_requires_auth(client):
    resp = client.delete("/api/admin/subjects/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_topics_update_requires_auth(client):
    resp = client.put("/api/admin/topics/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_topics_delete_requires_auth(client):
    resp = client.delete("/api/admin/topics/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_blog_create_requires_auth(client):
    resp = client.post("/api/admin/blog", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_blog_get_requires_auth(client):
    resp = client.get("/api/admin/blog/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_blog_get_by_fake_id_with_auth(client, admin_headers):
    resp = client.get("/api/admin/blog/000000000000000000000000", headers=admin_headers)
    assert resp.status_code in (404, 400, 422)


def test_admin_blog_update_requires_auth(client):
    resp = client.put("/api/admin/blog/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_blog_delete_requires_auth(client):
    resp = client.delete("/api/admin/blog/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_daily_content_create_requires_auth(client):
    resp = client.post("/api/admin/daily-content", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_daily_content_update_requires_auth(client):
    resp = client.put("/api/admin/daily-content/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_daily_content_delete_requires_auth(client):
    resp = client.delete("/api/admin/daily-content/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_coupons_update_requires_auth(client):
    resp = client.put("/api/admin/coupons/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_coupons_delete_requires_auth(client):
    resp = client.delete("/api/admin/coupons/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_daily_videos_get_requires_auth(client):
    resp = client.get("/api/admin/daily-videos/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_daily_videos_get_by_fake_id_with_auth(client, admin_headers):
    resp = client.get("/api/admin/daily-videos/000000000000000000000000", headers=admin_headers)
    assert resp.status_code in (404, 400, 422)


def test_admin_daily_videos_delete_requires_auth(client):
    resp = client.delete("/api/admin/daily-videos/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_feedbacks_update_requires_auth(client):
    resp = client.put("/api/admin/feedbacks/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_feedbacks_delete_requires_auth(client):
    resp = client.delete("/api/admin/feedbacks/000000000000000000000000")
    assert resp.status_code in (401, 403)
