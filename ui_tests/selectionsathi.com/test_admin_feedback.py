"""UI tests for the Admin > Feedback area (/admin/feedbacks).

Segmented from a single recorded journey that logged in, opened the Feedback
page, and repeated "click + Add notes -> type note -> Save" on three separate
feedback cards. That repetition is the SAME behaviour exercised three times
(likely a retry/multiple-rows artifact of the recorder), not three distinct
behaviours, so it collapses into one test here plus the standard
page-load/auth-gate pair already used for every other admin page in this
suite (see test_admin_logs.py, test_admin_payments.py for the same shape).

SAFETY NOTE -- this is a live production site, but the feedback list itself
only contains QA-fixture rows (type/subject/message are literally
"test_type"/"test_subject"/"test_message" for all 3 records at time of
writing, confirmed via GET /api/admin/feedbacks), not real user submissions.
test_admin_feedback_add_notes_saves_and_persists still treats the record's
admin_notes as real state: it writes a uuid-suffixed note (never a
guessable/collision-prone value like the recorded journey's plain "test"),
verifies it through both the DOM and the admin API, and restores the
record's original admin_notes value via the admin API in a finally block
regardless of outcome.

The recorded nth-of-type selector chains are replaced with text/placeholder
based locators (matching the pattern established in test_admin_subjects.py
and test_admin_exams.py) so the tests survive DOM reordering. The
textarea[placeholder="Admin notes..."] selector is taken directly from the
recording, which is strong ground truth: it was exercised against production
moments before this file was written.
"""
import uuid

import httpx
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _open_feedback(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/feedbacks')
    helpers['wait_ready'](driver)


def _find_notes_button(driver, index=0):
    """The recorded control is labelled '+ Add notes'; once a record already
    has notes some apps relabel it (e.g. 'Edit notes'), so match loosely on
    'notes' rather than the exact recorded string."""
    buttons = [
        b for b in driver.find_elements(By.CSS_SELECTOR, 'button')
        if b.is_displayed() and 'notes' in (b.text or '').strip().lower()
    ]
    return buttons[index] if len(buttons) > index else None


def test_admin_feedback_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    """Authenticated admin can load /admin/feedbacks and it renders content."""
    _open_feedback(driver, base_url, admin_credentials, helpers)
    assert '/login' not in driver.current_url, 'Authenticated /admin/feedbacks request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/feedbacks rendered empty body after authentication'


def test_admin_feedback_requires_auth(driver, base_url, helpers):
    """Unauthenticated access to /admin/feedbacks redirects to a login page."""
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/feedbacks')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/feedbacks did not redirect to a login page; ended at {current}'
    )


@pytest.mark.timeout(90)
def test_admin_feedback_add_notes_saves_and_persists(driver, base_url, admin_credentials, helpers, admin_api_token):
    """Typing admin notes into the '+ Add notes' editor and clicking Save persists the text.

    Real side effect: overwrites the admin_notes field of one feedback record
    (a QA-fixture entry, not real user feedback) on this production site.
    The original admin_notes value is restored via the admin API afterward.
    """
    if not admin_api_token:
        pytest.skip('No admin API token available to verify/restore feedback state')

    headers = {'Authorization': f'Bearer {admin_api_token}'}
    resp = httpx.get(f'{base_url}/api/admin/feedbacks', headers=headers, timeout=30.0, verify=False)
    if resp.status_code != 200:
        pytest.skip(f'Could not list feedbacks via admin API (status={resp.status_code})')
    feedbacks = resp.json().get('feedbacks') or []
    if not feedbacks:
        pytest.skip('No feedback entries exist on /admin/feedbacks to add notes to')

    target = feedbacks[0]
    original_notes = target.get('admin_notes')
    unique_note = f'QA note {uuid.uuid4().hex[:8]}'

    _open_feedback(driver, base_url, admin_credentials, helpers)
    try:
        btn = _find_notes_button(driver, 0)
        assert btn is not None, 'No "Add notes"/"Edit notes" control found on /admin/feedbacks'
        btn.click()

        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder="Admin notes..."]'))
        )
        textarea.clear()
        textarea.send_keys(unique_note)

        save_buttons = [
            b for b in driver.find_elements(By.CSS_SELECTOR, 'button')
            if b.is_displayed() and (b.text or '').strip().lower() == 'save'
        ]
        assert save_buttons, 'No visible "Save" button found after opening the notes editor'
        save_buttons[0].click()
        helpers['wait_ready'](driver)

        body = helpers['body_text'](driver)
        assert unique_note in body, f'Saved note {unique_note!r} not visible on /admin/feedbacks after Save'

        verify_resp = httpx.get(f'{base_url}/api/admin/feedbacks', headers=headers, timeout=30.0, verify=False)
        assert verify_resp.status_code == 200, 'Could not re-fetch feedbacks via admin API to verify persistence'
        updated = next(
            (f for f in verify_resp.json().get('feedbacks', []) if f.get('id') == target.get('id')), None
        )
        assert updated is not None and updated.get('admin_notes') == unique_note, (
            f"admin_notes for feedback {target.get('id')} was not persisted via the API; "
            f"got {updated.get('admin_notes') if updated else None!r}"
        )
    finally:
        try:
            restore_resp = httpx.put(
                f"{base_url}/api/admin/feedbacks/{target['id']}",
                headers=headers,
                json={'admin_notes': original_notes or ''},
                timeout=30.0,
                verify=False,
            )
            if restore_resp.status_code not in (200, 204):
                print(
                    f"[cleanup] failed to restore admin_notes for feedback {target['id']}: "
                    f"{restore_resp.status_code} {restore_resp.text[:200]}"
                )
        except Exception as exc:
            print(f"[cleanup] exception while restoring admin_notes for feedback {target['id']}: {exc}")
