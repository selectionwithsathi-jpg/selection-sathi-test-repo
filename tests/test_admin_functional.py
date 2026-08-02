def test_admin_dashboard_returns_stats(client, admin_headers):
    resp = client.get("/api/admin/dashboard", headers=admin_headers)
    assert resp.status_code == 200
    assert "total_users" in resp.json()


def test_admin_students_list(client, admin_headers):
    resp = client.get("/api/admin/students", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_settings_get(client, admin_headers):
    resp = client.get("/api/admin/settings", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_subjects_list(client, admin_headers):
    resp = client.get("/api/admin/subjects", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_topics_list(client, admin_headers):
    resp = client.get("/api/admin/topics", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_questions_stats(client, admin_headers):
    resp = client.get("/api/admin/questions/stats", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_questions_pending(client, admin_headers):
    resp = client.get("/api/admin/questions/pending", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_exams_list(client, admin_headers):
    resp = client.get("/api/admin/exams", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_blog_list(client, admin_headers):
    resp = client.get("/api/admin/blog", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_coupons_list(client, admin_headers):
    resp = client.get("/api/admin/coupons", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_daily_content_list(client, admin_headers):
    resp = client.get("/api/admin/daily-content", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_feedbacks_list(client, admin_headers):
    resp = client.get("/api/admin/feedbacks", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_activity_logs(client, admin_headers):
    resp = client.get("/api/admin/activity-logs", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_server_status(client, admin_headers):
    resp = client.get("/api/admin/server-status", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_payment_history(client, admin_headers):
    resp = client.get("/api/admin/payment-history", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_test_analysis(client, admin_headers):
    resp = client.get("/api/admin/test-analysis", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_current_affairs_status(client, admin_headers):
    resp = client.get("/api/admin/current-affairs/status", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_exam_notifications(client, admin_headers):
    resp = client.get("/api/admin/exam-notifications", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_scheduled_content(client, admin_headers):
    resp = client.get("/api/admin/scheduled-content", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_daily_videos(client, admin_headers):
    resp = client.get("/api/admin/daily-videos", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_latest_updates(client, admin_headers):
    resp = client.get("/api/admin/latest-updates", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_notifications(client, admin_headers):
    resp = client.get("/api/admin/notifications", headers=admin_headers)
    assert resp.status_code == 200


def test_admin_backup_export(client, admin_headers):
    resp = client.get("/api/admin/backup/export", headers=admin_headers)
    assert resp.status_code in (200, 501)


def test_admin_students_detail_with_fake_id_returns_404(client, admin_headers):
    resp = client.get("/api/admin/students/000000000000000000000000", headers=admin_headers)
    assert resp.status_code in (404, 400, 422)


def test_admin_subjects_create_missing_fields_returns_422(client, admin_headers):
    resp = client.post("/api/admin/subjects", json={}, headers=admin_headers)
    assert resp.status_code in (400, 422)


def test_admin_topics_create_missing_fields_returns_422(client, admin_headers):
    resp = client.post("/api/admin/topics", json={}, headers=admin_headers)
    assert resp.status_code in (400, 422)


def test_admin_coupons_create_missing_fields_returns_422(client, admin_headers):
    resp = client.post("/api/admin/coupons", json={}, headers=admin_headers)
    assert resp.status_code in (400, 422)
