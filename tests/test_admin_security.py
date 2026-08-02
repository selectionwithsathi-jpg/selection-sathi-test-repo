from collections import defaultdict

import pytest

_OID = "000000000000000000000000"
_PATH_PARAMS = defaultdict(lambda: _OID)


def _fill(path):
    return path.format_map(_PATH_PARAMS)


def _check_rejects_unauth(client, method, path):
    url = _fill(path)
    resp = client.request(method, url, json={} if method in ("POST", "PUT", "PATCH") else None)
    assert resp.status_code in (401, 403), (
        f"{method} {url} did not enforce authentication -- got {resp.status_code}: {resp.text[:200]}"
    )


BATCH_1 = [
    ("GET", "/api/admin/dashboard"),
    ("GET", "/api/admin/students"),
    ("GET", "/api/admin/students/{student_id}"),
    ("PUT", "/api/admin/students/{student_id}/status"),
    ("GET", "/api/admin/students/{student_id}/subject-performance"),
    ("GET", "/api/admin/students/{student_id}/daily-activity"),
    ("GET", "/api/admin/students/{student_id}/test-attempts"),
    ("GET", "/api/admin/students/{student_id}/test-scores"),
    ("GET", "/api/admin/students/{student_id}/strengths-weaknesses"),
    ("GET", "/api/admin/students/{student_id}/chat-sessions"),
    ("GET", "/api/admin/students/{student_id}/bookmarks"),
    ("GET", "/api/admin/students/{student_id}/activity-timeline"),
    ("POST", "/api/admin/students/{student_id}/reset-device"),
    ("POST", "/api/admin/students/{student_id}/grant-exam-access"),
    ("GET", "/api/admin/questions/stats"),
    ("POST", "/api/admin/questions/bulk-create"),
    ("POST", "/api/admin/questions/import-csv"),
    ("GET", "/api/admin/questions/pending"),
    ("PUT", "/api/admin/questions/{question_id}/approve"),
    ("PUT", "/api/admin/questions/bulk-approve"),
    ("GET", "/api/admin/settings"),
    ("PUT", "/api/admin/settings"),
]

BATCH_2 = [
    ("POST", "/api/admin/test-templates"),
    ("PUT", "/api/admin/test-templates/{template_id}"),
    ("DELETE", "/api/admin/test-templates/{template_id}"),
    ("GET", "/api/admin/test-templates/{template_id}/questions"),
    ("POST", "/api/admin/test-templates/{template_id}/questions"),
    ("DELETE", "/api/admin/test-templates/{template_id}/questions/{question_id}"),
    ("PATCH", "/api/admin/test-templates/{template_id}/questions/reorder"),
    ("GET", "/api/admin/exams"),
    ("POST", "/api/admin/exams"),
    ("PATCH", "/api/admin/exams/{exam_id}/payment-settings"),
    ("PUT", "/api/admin/exams/{exam_id}"),
    ("DELETE", "/api/admin/exams/{exam_id}"),
    ("GET", "/api/admin/subjects"),
    ("POST", "/api/admin/subjects"),
    ("PUT", "/api/admin/subjects/{subject_id}"),
    ("DELETE", "/api/admin/subjects/{subject_id}"),
    ("GET", "/api/admin/blog"),
    ("POST", "/api/admin/blog"),
    ("GET", "/api/admin/blog/{post_id}"),
    ("PUT", "/api/admin/blog/{post_id}"),
    ("DELETE", "/api/admin/blog/{post_id}"),
    ("GET", "/api/admin/server-status"),
    ("GET", "/api/admin/activity-logs"),
]

BATCH_3 = [
    ("GET", "/api/admin/daily-content"),
    ("POST", "/api/admin/daily-content"),
    ("PUT", "/api/admin/daily-content/{item_id}"),
    ("DELETE", "/api/admin/daily-content/{item_id}"),
    ("GET", "/api/admin/coupons"),
    ("POST", "/api/admin/coupons"),
    ("PUT", "/api/admin/coupons/{coupon_id}"),
    ("DELETE", "/api/admin/coupons/{coupon_id}"),
    ("GET", "/api/admin/topics"),
    ("POST", "/api/admin/topics"),
    ("PUT", "/api/admin/topics/{topic_id}"),
    ("DELETE", "/api/admin/topics/{topic_id}"),
    ("GET", "/api/admin/payment-history"),
    ("POST", "/api/admin/upload-image"),
    ("POST", "/api/admin/upload-pyq-pdf"),
    ("POST", "/api/admin/save-pyq-questions"),
    ("GET", "/api/admin/current-affairs/status"),
    ("POST", "/api/admin/current-affairs/generate"),
    ("GET", "/api/admin/exam-notifications"),
    ("POST", "/api/admin/exam-notifications/scrape"),
]

BATCH_4 = [
    ("POST", "/api/admin/tests/auto-generate"),
    ("GET", "/api/admin/test-analysis"),
    ("GET", "/api/admin/feedbacks"),
    ("PUT", "/api/admin/feedbacks/{feedback_id}"),
    ("DELETE", "/api/admin/feedbacks/{feedback_id}"),
    ("GET", "/api/admin/backup/export"),
    ("GET", "/api/admin/scheduled-content"),
    ("POST", "/api/admin/scheduled-content/publish-due"),
    ("GET", "/api/admin/daily-videos"),
    ("GET", "/api/admin/daily-videos/{video_id}"),
    ("DELETE", "/api/admin/daily-videos/{video_id}"),
    ("POST", "/api/admin/daily-videos/generate"),
    ("POST", "/api/admin/notifications/send"),
    ("GET", "/api/admin/notifications"),
    ("POST", "/api/admin/whatsapp/broadcast"),
    ("POST", "/api/admin/whatsapp/format-channel-post"),
    ("GET", "/api/admin/latest-updates"),
    ("POST", "/api/admin/latest-updates"),
    ("GET", "/api/admin/latest-updates/{item_id}"),
    ("PUT", "/api/admin/latest-updates/{item_id}"),
    ("DELETE", "/api/admin/latest-updates/{item_id}"),
]

SAMPLE_PRIVILEGE_ENDPOINTS = [
    ("GET", "/api/admin/dashboard"),
    ("GET", "/api/admin/settings"),
    ("GET", "/api/admin/students"),
    ("POST", "/api/admin/exams"),
    ("POST", "/api/admin/subjects"),
    ("POST", "/api/admin/coupons"),
    ("POST", "/api/admin/blog"),
    ("POST", "/api/admin/questions/bulk-create"),
    ("POST", "/api/admin/upload-image"),
    ("GET", "/api/admin/backup/export"),
    ("GET", "/api/admin/activity-logs"),
    ("GET", "/api/admin/server-status"),
    ("GET", "/api/admin/feedbacks"),
    ("POST", "/api/admin/notifications/send"),
    ("POST", "/api/admin/whatsapp/broadcast"),
]


@pytest.mark.parametrize("method,path", BATCH_1)
def test_admin_endpoints_batch1_reject_unauthenticated(client, method, path):
    _check_rejects_unauth(client, method, path)


@pytest.mark.parametrize("method,path", BATCH_2)
def test_admin_endpoints_batch2_reject_unauthenticated(client, method, path):
    _check_rejects_unauth(client, method, path)


@pytest.mark.parametrize("method,path", BATCH_3)
def test_admin_endpoints_batch3_reject_unauthenticated(client, method, path):
    _check_rejects_unauth(client, method, path)


@pytest.mark.parametrize("method,path", BATCH_4)
def test_admin_endpoints_batch4_reject_unauthenticated(client, method, path):
    _check_rejects_unauth(client, method, path)


@pytest.mark.parametrize("method,path", SAMPLE_PRIVILEGE_ENDPOINTS)
def test_admin_endpoints_batch5_reject_student_role_token(client, student_headers, method, path):
    """Admin endpoints must reject non-admin (student) tokens, not just require *any* token."""
    url = _fill(path)
    resp = client.request(
        method, url, headers=student_headers, json={} if method in ("POST", "PUT", "PATCH") else None
    )
    assert resp.status_code in (401, 403), (
        f"{method} {url} allowed a student-role token (privilege escalation risk) -- "
        f"got {resp.status_code}: {resp.text[:200]}"
    )


def test_admin_batch5_code_execute_requires_authentication(client):
    resp = client.post("/api/code/execute", json={"code": "print(1)", "language": "python"})
    assert resp.status_code in (401, 403)


def test_admin_batch5_code_execute_rejects_dev_login_backdoor_token(client, student_headers):
    """SECURITY: the code-execution endpoint should reject tokens obtained via the
    zero-credential dev-login backdoor. A non-401/403 response means an unauthenticated
    user can reach a code-execution surface just by calling dev-login first."""
    resp = client.post(
        "/api/code/execute", json={"code": "print(1)", "language": "python"}, headers=student_headers
    )
    assert resp.status_code in (401, 403), (
        f"dev-login backdoor token was accepted by /api/code/execute's auth layer "
        f"(status={resp.status_code}, body={resp.text[:200]})"
    )
