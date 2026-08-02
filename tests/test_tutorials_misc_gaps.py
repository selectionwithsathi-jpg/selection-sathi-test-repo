def test_tutorials_subject_invalid_slug(client):
    resp = client.get("/api/tutorials/subject/not-a-real-subject-xyz")
    assert resp.status_code in (200, 404)


def test_tutorials_chapter_invalid_slugs(client):
    resp = client.get("/api/tutorials/chapter/not-a-real-subject-xyz/not-a-real-chapter-xyz")
    assert resp.status_code in (200, 404)


def test_tutorials_subject_sidebar_invalid_slug(client):
    resp = client.get("/api/tutorials/subject-sidebar/not-a-real-subject-xyz")
    assert resp.status_code in (200, 404)


def test_question_update_requires_auth(client):
    resp = client.put("/api/questions/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_question_explanation_image_fake_id(client):
    resp = client.get("/api/questions/000000000000000000000000/explanation-image")
    assert resp.status_code in (404, 400, 401, 403, 422)


def test_tests_template_by_id_requires_auth(client):
    resp = client.get("/api/tests/templates/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_study_plan_by_id_requires_auth(client):
    resp = client.get("/api/study-plans/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_latest_updates_list_requires_auth(client):
    resp = client.get("/api/admin/latest-updates")
    assert resp.status_code in (401, 403)


def test_admin_latest_updates_create_requires_auth(client):
    resp = client.post("/api/admin/latest-updates", json={})
    assert resp.status_code in (401, 403, 422)


def test_admin_latest_updates_get_requires_auth(client):
    resp = client.get("/api/admin/latest-updates/000000000000000000000000")
    assert resp.status_code in (401, 403)


def test_admin_latest_updates_update_requires_auth(client):
    resp = client.put("/api/admin/latest-updates/000000000000000000000000", json={})
    assert resp.status_code in (401, 403)


def test_admin_latest_updates_delete_requires_auth(client):
    resp = client.delete("/api/admin/latest-updates/000000000000000000000000")
    assert resp.status_code in (401, 403)
