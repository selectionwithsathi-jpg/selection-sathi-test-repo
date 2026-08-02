def test_admin_test_templates_create_requires_auth(client):
    resp = client.post("/api/admin/test-templates", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_test_templates_update_requires_auth(client):
    resp = client.put("/api/admin/test-templates/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_test_templates_delete_requires_auth(client):
    resp = client.delete("/api/admin/test-templates/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_test_templates_questions_list_requires_auth(client):
    resp = client.get("/api/admin/test-templates/000000000000000000000000/questions")
    assert resp.status_code in (401, 403)


def test_admin_test_templates_questions_add_requires_auth(client):
    resp = client.post("/api/admin/test-templates/000000000000000000000000/questions", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_test_templates_questions_delete_requires_auth(client):
    resp = client.delete("/api/admin/test-templates/000000000000000000000000/questions/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_test_templates_questions_reorder_requires_auth(client):
    resp = client.patch("/api/admin/test-templates/000000000000000000000000/questions/reorder", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_upload_pyq_pdf_requires_auth(client):
    resp = client.post("/api/admin/upload-pyq-pdf", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_save_pyq_questions_requires_auth(client):
    resp = client.post("/api/admin/save-pyq-questions", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_current_affairs_generate_requires_auth(client):
    resp = client.post("/api/admin/current-affairs/generate", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_exam_notifications_scrape_requires_auth(client):
    resp = client.post("/api/admin/exam-notifications/scrape", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_exams_payment_settings_requires_auth(client):
    resp = client.patch("/api/admin/exams/000000000000000000000000/payment-settings", json={})
    assert resp.status_code in (401, 403)


def test_admin_settings_update_requires_auth(client):
    resp = client.put("/api/admin/settings", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_students_reset_device_requires_auth(client):
    resp = client.post("/api/admin/students/000000000000000000000000/reset-device", json={})
    assert resp.status_code in (401, 403)


def test_admin_students_grant_exam_access_requires_auth(client):
    resp = client.post("/api/admin/students/000000000000000000000000/grant-exam-access", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_exams_update_requires_auth(client):
    resp = client.put("/api/admin/exams/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_exams_delete_requires_auth(client):
    resp = client.delete("/api/admin/exams/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_questions_bulk_create_requires_auth(client):
    resp = client.post("/api/admin/questions/bulk-create", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_questions_import_csv_requires_auth(client):
    resp = client.post("/api/admin/questions/import-csv", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_upload_image_requires_auth(client):
    resp = client.post("/api/admin/upload-image", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_questions_approve_requires_auth(client):
    resp = client.put("/api/admin/questions/000000000000000000000000/approve", json={})
    assert resp.status_code in (401, 403)


def test_admin_questions_bulk_approve_requires_auth(client):
    resp = client.put("/api/admin/questions/bulk-approve", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_tests_auto_generate_requires_auth(client):
    resp = client.post("/api/admin/tests/auto-generate", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_feedback_submit_requires_auth(client):
    resp = client.post("/api/admin/feedback/submit", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_scheduled_content_publish_due_requires_auth(client):
    resp = client.post("/api/admin/scheduled-content/publish-due", json={})
    assert resp.status_code in (401, 403)


def test_admin_daily_videos_generate_requires_auth(client):
    resp = client.post("/api/admin/daily-videos/generate", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_notifications_send_requires_auth(client):
    resp = client.post("/api/admin/notifications/send", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_students_subject_performance_requires_auth(client):
    resp = client.get("/api/admin/students/000000000000000000000000/subject-performance")
    assert resp.status_code in (401, 403)


def test_admin_students_daily_activity_requires_auth(client):
    resp = client.get("/api/admin/students/000000000000000000000000/daily-activity")
    assert resp.status_code in (401, 403)


def test_admin_students_test_attempts_requires_auth(client):
    resp = client.get("/api/admin/students/000000000000000000000000/test-attempts")
    assert resp.status_code in (401, 403)


def test_admin_students_test_scores_requires_auth(client):
    resp = client.get("/api/admin/students/000000000000000000000000/test-scores")
    assert resp.status_code in (401, 403)


def test_admin_students_strengths_weaknesses_requires_auth(client):
    resp = client.get("/api/admin/students/000000000000000000000000/strengths-weaknesses")
    assert resp.status_code in (401, 403)


def test_admin_students_chat_sessions_requires_auth(client):
    resp = client.get("/api/admin/students/000000000000000000000000/chat-sessions")
    assert resp.status_code in (401, 403)


def test_admin_students_bookmarks_requires_auth(client):
    resp = client.get("/api/admin/students/000000000000000000000000/bookmarks")
    assert resp.status_code in (401, 403)


def test_admin_students_activity_timeline_requires_auth(client):
    resp = client.get("/api/admin/students/000000000000000000000000/activity-timeline")
    assert resp.status_code in (401, 403)


def test_admin_students_status_update_requires_auth(client):
    resp = client.put("/api/admin/students/000000000000000000000000/status", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_whatsapp_broadcast_requires_auth(client):
    resp = client.post("/api/admin/whatsapp/broadcast", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_whatsapp_format_channel_post_requires_auth(client):
    resp = client.post("/api/admin/whatsapp/format-channel-post", json={})
    assert resp.status_code in (401, 403, 422)
