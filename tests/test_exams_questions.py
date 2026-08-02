def test_list_exams_public_no_auth_required(client):
    resp = client.get("/api/exams")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) > 0
    assert "code" in body[0]


def test_get_exam_by_code_public(client):
    resp = client.get("/api/exams/ssc-cgl")
    assert resp.status_code == 200
    assert resp.json().get("code") == "ssc-cgl"


def test_get_exam_by_invalid_code_returns_404(client):
    resp = client.get("/api/exams/not-a-real-exam-code-xyz")
    assert resp.status_code == 404


def test_get_exam_subjects_topics(client):
    resp = client.get("/api/exams/ssc-cgl/subjects/quantitative-aptitude/topics")
    assert resp.status_code in (200, 404)


def test_create_exam_requires_auth(client):
    resp = client.post("/api/exams", json={"name": "Test Exam"})
    assert resp.status_code in (401, 403)


def test_update_exam_requires_auth(client):
    resp = client.put("/api/exams/000000000000000000000000", json={"name": "x"})
    assert resp.status_code in (401, 403)


def test_list_questions_requires_auth(client):
    resp = client.get("/api/questions")
    assert resp.status_code in (401, 403)


def test_list_questions_with_admin_auth(client, admin_headers):
    resp = client.get("/api/questions", headers=admin_headers)
    assert resp.status_code == 200


def test_create_question_requires_auth(client):
    resp = client.post("/api/questions", json={})
    assert resp.status_code in (401, 403)


def test_create_question_missing_fields_returns_422(client, admin_headers):
    resp = client.post("/api/questions", json={}, headers=admin_headers)
    assert resp.status_code in (400, 422)


def test_get_question_by_fake_id_returns_404(client, admin_headers):
    resp = client.get("/api/questions/000000000000000000000000", headers=admin_headers)
    assert resp.status_code in (404, 400, 422)


def test_delete_question_requires_auth(client):
    resp = client.request("DELETE", "/api/questions/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_questions_explanation_stats_requires_auth(client):
    resp = client.get("/api/questions/explanation-stats")
    assert resp.status_code in (401, 403)


def test_questions_explanation_stats_with_auth(client, admin_headers):
    resp = client.get("/api/questions/explanation-stats", headers=admin_headers)
    assert resp.status_code == 200
