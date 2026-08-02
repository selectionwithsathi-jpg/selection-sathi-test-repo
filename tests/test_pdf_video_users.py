def test_pdf_test_result_requires_auth(client):
    resp = client.get("/api/pdf/test-result/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_pdf_scorecard_requires_auth(client):
    resp = client.get("/api/pdf/scorecard/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_pdf_scorecard_image_requires_auth(client):
    resp = client.get("/api/pdf/scorecard-image/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_pdf_study_plan_requires_auth(client):
    resp = client.get("/api/pdf/study-plan/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_pdf_question_set_requires_auth(client):
    resp = client.get("/api/pdf/question-set")
    assert resp.status_code in (401, 403, 422)


def test_pdf_public_scorecard_image_fake_id(client):
    resp = client.get("/api/pdf/public/scorecard-image/000000000000000000000000")
    assert resp.status_code in (404, 400, 422)


def test_pdf_public_scorecard_data_fake_id(client):
    resp = client.get("/api/pdf/public/scorecard-data/000000000000000000000000")
    assert resp.status_code in (404, 400, 422)


def test_video_progress_save_requires_auth(client):
    resp = client.post("/api/video-progress/save", json={})
    assert resp.status_code in (401, 403, 422)


def test_video_progress_by_topic_requires_auth(client):
    resp = client.get("/api/video-progress/not-a-real-topic")
    assert resp.status_code in (401, 403)


def test_video_progress_batch_requires_auth(client):
    resp = client.post("/api/video-progress/batch", json={})
    assert resp.status_code in (401, 403, 422)


def test_video_progress_chapter_requires_auth(client):
    resp = client.get("/api/video-progress/chapter/not-a-real-subject/not-a-real-chapter")
    assert resp.status_code in (401, 403)


def test_video_progress_subject_requires_auth(client):
    resp = client.get("/api/video-progress/subject/not-a-real-subject")
    assert resp.status_code in (401, 403)


def test_video_bookmarks_create_requires_auth(client):
    resp = client.post("/api/video-bookmarks", json={})
    assert resp.status_code in (401, 403, 422)


def test_video_bookmarks_list_requires_auth(client):
    resp = client.get("/api/video-bookmarks")
    assert resp.status_code in (401, 403)


def test_video_bookmarks_delete_requires_auth(client):
    resp = client.delete("/api/video-bookmarks/not-a-real-topic")
    assert resp.status_code in (401, 403)


def test_video_bookmarks_check_single_requires_auth(client):
    resp = client.get("/api/video-bookmarks/check/not-a-real-topic")
    assert resp.status_code in (401, 403)


def test_video_bookmarks_check_batch_requires_auth(client):
    resp = client.post("/api/video-bookmarks/check-batch", json={})
    assert resp.status_code in (401, 403, 422)


def test_users_push_token_requires_auth(client):
    resp = client.post("/api/users/push-token", json={})
    assert resp.status_code in (401, 403, 422)


def test_users_whatsapp_preference_get_requires_auth(client):
    resp = client.get("/api/users/whatsapp-preference")
    assert resp.status_code in (401, 403)


def test_users_whatsapp_preference_post_requires_auth(client):
    resp = client.post("/api/users/whatsapp-preference", json={})
    assert resp.status_code in (401, 403, 422)
