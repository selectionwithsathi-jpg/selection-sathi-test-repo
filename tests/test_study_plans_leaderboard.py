def test_study_plans_requires_auth(client):
    resp = client.get("/api/study-plans")
    assert resp.status_code in (401, 403)


def test_study_plans_with_auth(client, student_headers):
    resp = client.get("/api/study-plans", headers=student_headers)
    assert resp.status_code == 200


def test_study_plans_my_plan_with_auth(client, student_headers):
    resp = client.get("/api/study-plans/my-plan", headers=student_headers)
    assert resp.status_code in (200, 404)


def test_study_plans_enroll_requires_auth(client):
    resp = client.post("/api/study-plans/enroll", json={})
    assert resp.status_code in (401, 403)


def test_study_plans_enroll_missing_fields_returns_422(client, student_headers):
    resp = client.post("/api/study-plans/enroll", json={}, headers=student_headers)
    assert resp.status_code in (400, 422)


def test_study_plans_complete_task_requires_auth(client):
    resp = client.post("/api/study-plans/complete-task", json={})
    assert resp.status_code in (401, 403)


def test_study_plans_pause_requires_auth(client):
    resp = client.put("/api/study-plans/my-plan/pause")
    assert resp.status_code in (401, 403)


def test_study_plans_resume_requires_auth(client):
    resp = client.put("/api/study-plans/my-plan/resume")
    assert resp.status_code in (401, 403)


def test_study_plans_abandon_requires_auth(client):
    resp = client.put("/api/study-plans/my-plan/abandon")
    assert resp.status_code in (401, 403)


def test_leaderboard_requires_auth(client):
    resp = client.get("/api/leaderboard")
    assert resp.status_code in (401, 403)


def test_leaderboard_with_auth(client, student_headers):
    resp = client.get("/api/leaderboard", headers=student_headers)
    assert resp.status_code == 200


def test_leaderboard_my_rank_with_auth(client, student_headers):
    resp = client.get("/api/leaderboard/my-rank", headers=student_headers)
    assert resp.status_code in (200, 404)
