def test_tutorial_notes_create_requires_auth(client):
    resp = client.post("/api/tutorial-notes", json={})
    assert resp.status_code in (401, 403, 422)


def test_tutorial_notes_by_topic_requires_auth(client):
    resp = client.get("/api/tutorial-notes/not-a-real-topic")
    assert resp.status_code in (401, 403)


def test_tutorial_notes_update_requires_auth(client):
    resp = client.put("/api/tutorial-notes/000000000000000000000000", json={})
    assert resp.status_code in (401, 403, 422)


def test_tutorial_notes_delete_requires_auth(client):
    resp = client.delete("/api/tutorial-notes/000000000000000000000000")
    assert resp.status_code in (401, 403)
