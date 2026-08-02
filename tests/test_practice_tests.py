def test_practice_requires_auth(client):
    # exam_code supplied so a missing-auth failure isn't masked by a 422 param-validation error
    resp = client.get("/api/practice", params={"exam_code": "ssc-cgl"})
    assert resp.status_code in (401, 403)


def test_practice_with_valid_auth(client, student_headers):
    resp = client.get("/api/practice", headers=student_headers, params={"exam_code": "ssc-cgl"})
    assert resp.status_code in (200, 422)


def test_practice_submit_requires_auth(client):
    # real question_id + correctly-typed selected_option so a missing-auth failure isn't masked
    # by a 404/422 caused by a placeholder payload
    resp = client.post("/api/practice/submit", json={"question_id": "6a2accd41d177c319671ae8a", "selected_option": 2})
    assert resp.status_code in (401, 403)


def test_practice_question_by_id_public(client):
    resp = client.get("/api/practice/question/000000000000000000000000")
    assert resp.status_code in (200, 404)


def test_practice_current_affairs_requires_auth(client):
    resp = client.get("/api/practice/current-affairs")
    assert resp.status_code in (401, 403)


def test_practice_current_affairs_dates_requires_auth(client):
    resp = client.get("/api/practice/current-affairs/dates")
    assert resp.status_code in (401, 403)


def test_practice_current_affairs_categories_requires_auth(client):
    resp = client.get("/api/practice/current-affairs/categories")
    assert resp.status_code in (401, 403)


def test_practice_current_affairs_video_public(client):
    resp = client.get("/api/practice/current-affairs/video")
    assert resp.status_code in (200, 404)


def test_tests_templates_requires_auth(client):
    resp = client.get("/api/tests/templates")
    assert resp.status_code in (401, 403)


def test_tests_templates_with_auth(client, student_headers):
    resp = client.get("/api/tests/templates", headers=student_headers)
    assert resp.status_code == 200


def test_tests_templates_lite_with_auth(client, student_headers):
    resp = client.get("/api/tests/templates/lite", headers=student_headers, params={"exam_code": "ssc-cgl"})
    assert resp.status_code == 200


def test_tests_pyq_papers_with_auth(client, student_headers):
    resp = client.get("/api/tests/pyq-papers", headers=student_headers)
    assert resp.status_code == 200


def test_tests_my_attempts_with_auth(client, student_headers):
    resp = client.get("/api/tests/my-attempts", headers=student_headers)
    assert resp.status_code == 200


def test_tests_start_requires_auth(client):
    resp = client.post("/api/tests/start", json={})
    assert resp.status_code in (401, 403)


def test_tests_start_missing_fields_returns_422(client, student_headers):
    resp = client.post("/api/tests/start", json={}, headers=student_headers)
    assert resp.status_code in (400, 422)


def test_tests_resume_fake_attempt_returns_404(client, student_headers):
    resp = client.get("/api/tests/000000000000000000000000/resume", headers=student_headers)
    assert resp.status_code in (404, 400, 422)


def test_tests_answer_fake_attempt_returns_404(client, student_headers):
    resp = client.put("/api/tests/000000000000000000000000/answer", json={}, headers=student_headers)
    assert resp.status_code in (404, 400, 422)


def test_tests_submit_fake_attempt_returns_404(client, student_headers):
    resp = client.post("/api/tests/000000000000000000000000/submit", json={}, headers=student_headers)
    assert resp.status_code in (404, 400, 422)


def test_tests_result_fake_attempt_returns_404(client, student_headers):
    resp = client.get("/api/tests/000000000000000000000000/result", headers=student_headers)
    assert resp.status_code in (404, 400, 422)


def test_tests_abandon_fake_attempt_returns_404(client, student_headers):
    resp = client.post("/api/tests/000000000000000000000000/abandon", headers=student_headers)
    assert resp.status_code in (404, 400, 422)
