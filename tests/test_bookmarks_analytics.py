def test_bookmarks_requires_auth(client):
    resp = client.get("/api/bookmarks")
    assert resp.status_code in (401, 403)


def test_bookmarks_list_with_auth(client, student_headers):
    resp = client.get("/api/bookmarks", headers=student_headers)
    assert resp.status_code == 200


def test_bookmarks_create_requires_auth(client):
    resp = client.post("/api/bookmarks", json={"question_id": "x"})
    assert resp.status_code in (401, 403)


def test_bookmarks_create_missing_fields_returns_422(client, student_headers):
    resp = client.post("/api/bookmarks", json={}, headers=student_headers)
    assert resp.status_code in (400, 422)


def test_bookmarks_delete_fake_id(client, student_headers):
    resp = client.request("DELETE", "/api/bookmarks/000000000000000000000000", headers=student_headers)
    assert resp.status_code in (200, 404)


def test_bookmarks_check_batch_requires_auth(client):
    resp = client.post("/api/bookmarks/check-batch", json={"question_ids": []})
    assert resp.status_code in (401, 403)


def test_bookmarks_check_single_requires_auth(client):
    resp = client.get("/api/bookmarks/check/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_analytics_overview_requires_auth(client):
    resp = client.get("/api/analytics/overview")
    assert resp.status_code in (401, 403)


def test_analytics_overview_with_auth(client, student_headers):
    resp = client.get("/api/analytics/overview", headers=student_headers)
    assert resp.status_code == 200


def test_analytics_subject_performance_with_auth(client, student_headers):
    resp = client.get("/api/analytics/subject-performance", headers=student_headers)
    assert resp.status_code == 200


def test_analytics_topic_performance_with_auth(client, student_headers, admin_headers):
    subjects_resp = client.get("/api/admin/subjects", headers=admin_headers)
    subject_id = subjects_resp.json()[0]["id"]
    resp = client.get("/api/analytics/topic-performance", headers=student_headers, params={"subject_id": subject_id})
    assert resp.status_code == 200


def test_analytics_daily_activity_with_auth(client, student_headers):
    resp = client.get("/api/analytics/daily-activity", headers=student_headers)
    assert resp.status_code == 200


def test_analytics_test_scores_with_auth(client, student_headers):
    resp = client.get("/api/analytics/test-scores", headers=student_headers)
    assert resp.status_code == 200


def test_analytics_strengths_weaknesses_with_auth(client, student_headers):
    resp = client.get("/api/analytics/strengths-weaknesses", headers=student_headers)
    assert resp.status_code == 200
