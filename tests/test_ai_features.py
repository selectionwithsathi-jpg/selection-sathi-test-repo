def test_ai_sessions_list_requires_auth(client):
    resp = client.get("/api/ai/sessions")
    assert resp.status_code in (401, 403)


def test_ai_sessions_create_requires_auth(client):
    resp = client.post("/api/ai/sessions", json={})
    assert resp.status_code in (401, 403, 422)


def test_ai_sessions_get_by_id_requires_auth(client):
    resp = client.get("/api/ai/sessions/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_ai_sessions_delete_requires_auth(client):
    resp = client.delete("/api/ai/sessions/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_ai_chat_requires_auth(client):
    resp = client.post("/api/ai/chat", json={})
    assert resp.status_code in (401, 403, 422)


def test_ai_generate_questions_requires_auth(client):
    resp = client.post("/api/ai/generate-questions", json={})
    assert resp.status_code in (401, 403, 422)


def test_ai_generate_questions_save_requires_auth(client):
    resp = client.post("/api/ai/generate-questions/save", json={})
    assert resp.status_code in (401, 403, 422)


def test_ai_generate_video_requires_auth(client):
    resp = client.post("/api/ai/generate-video", json={})
    assert resp.status_code in (401, 403, 422)


def test_ai_video_status_requires_auth(client):
    resp = client.get("/api/ai/video-status/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_ai_videos_list_requires_auth(client):
    resp = client.get("/api/ai/videos")
    assert resp.status_code in (401, 403)
