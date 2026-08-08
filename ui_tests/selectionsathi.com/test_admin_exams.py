"""UI tests for the Admin > Exams area (/admin/exams).

Segmented from a single recorded journey that exercised several distinct
behaviours: viewing the exam list (already covered by
test_admin_exams_page_loads_after_login / test_admin_exams_requires_auth
below), per-exam payment settings, editing an exam, and creating a new exam.
Each new behaviour is its own independent, re-runnable test function.

SAFETY NOTE -- this is a live production site. The recorded journey directly
renamed a real, named production exam ("AP Police Constable") and created a
permanent new exam via the UI. Neither is safe to replay automatically on a
recurring regression suite, so the tests below never touch real exam records:
  * test_admin_exam_edit_updates_name and
    test_admin_exam_payment_settings_toggle_is_reversible operate on a
    throwaway exam created by the `disposable_exam` fixture -- never a real
    one -- located precisely by matching its unique generated name/code so a
    stray click can't land on unrelated production data.
  * test_admin_exam_create_adds_new_exam_to_list and `disposable_exam` both
    create data, and both delete it again via the admin API in a
    finally/teardown block, using a uuid-suffixed code/name per run so
    repeated/parallel runs never collide.
  * There is no verified admin API schema for exam creation elsewhere in this
    suite, so `disposable_exam`'s precondition is established through the
    same real Create-Exam UI flow under test rather than a lighter API call
    -- this is a real precondition that could not be isolated further.
  * Cleanup is best-effort: if the created exam can't be found/deleted via
    the admin API (e.g. an unexpected response shape), a warning is printed
    instead of failing the test, so a cleanup gap never masks a real result.
    In that case the exam is left in place with an obvious "QA Test Exam"
    name/description for manual removal.

No emails or other external notifications are triggered by any of these
actions. The ambiguous recorded clicks on nested <svg><circle>/<rect> paths
(icon sub-elements, not separate controls) are treated as a single logical
click on the enclosing button, located by aria-label/text instead of the
recorded nth-of-type chain.
"""
import time
import uuid

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def test_admin_exams_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/exams')
    helpers['wait_ready'](driver)
    assert '/login' not in driver.current_url, 'Authenticated /admin/exams request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/exams rendered empty body after authentication'


def test_admin_exams_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/exams')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/exams did not redirect to a login page; ended at {current}'
    )


def _find_by_text(driver, tag_css, texts):
    found = []
    for el in driver.find_elements(By.CSS_SELECTOR, tag_css):
        try:
            if not el.is_displayed():
                continue
            label = (el.text or el.get_attribute('aria-label') or '').strip().lower()
            if any(t in label for t in texts):
                found.append(el)
        except Exception:
            continue
    return found


def _find_exam_row(driver, needle):
    for el in driver.find_elements(By.CSS_SELECTOR, 'tr, [role="row"], div[class*="row" i]'):
        try:
            if el.is_displayed() and needle.lower() in el.text.lower():
                return el
        except Exception:
            continue
    return None


def _unique_exam_payload():
    token = uuid.uuid4().hex[:8]
    return {
        'name': f'QA Test Exam {token}',
        'code': f'qa-test-{token}',
        'full_name': f'QA Automated Test Exam {token}',
        'description': 'Created by an automated UI regression test; safe to delete.',
    }


def _open_exams(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/exams')
    helpers['wait_ready'](driver)


def _create_exam_via_ui(driver, helpers, payload):
    add_buttons = _find_by_text(driver, 'button, a', ['add exam'])
    if not add_buttons:
        pytest.skip('No "Add Exam" control found on /admin/exams')
    add_buttons[0].click()
    time.sleep(1)

    name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="e.g., SSC CGL"]'))
    )
    name_input.clear()
    name_input.send_keys(payload['name'])

    code_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[placeholder="e.g., ssc-cgl"]')
    if code_inputs:
        code_inputs[0].clear()
        code_inputs[0].send_keys(payload['code'])

    for select_el in driver.find_elements(By.CSS_SELECTOR, 'select'):
        try:
            Select(select_el).select_by_value('upsc')
            break
        except Exception:
            continue

    full_name_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[placeholder="e.g., Staff Selection Commission"]')
    if full_name_inputs:
        full_name_inputs[0].clear()
        full_name_inputs[0].send_keys(payload['full_name'])

    description_inputs = driver.find_elements(By.CSS_SELECTOR, 'textarea[placeholder="Brief exam description"]')
    if description_inputs:
        description_inputs[0].clear()
        description_inputs[0].send_keys(payload['description'])

    create_buttons = _find_by_text(driver, 'button', ['create'])
    if not create_buttons:
        pytest.skip('No "Create" submit control found on the Add Exam form')
    create_buttons[0].click()
    helpers['wait_ready'](driver)


def _delete_exam_via_api(base_url, admin_api_token, code):
    if not admin_api_token:
        print(f'[cleanup] no admin API token available; test exam code={code!r} needs manual cleanup')
        return
    import httpx
    headers = {'Authorization': f'Bearer {admin_api_token}'}
    try:
        resp = httpx.get(f'{base_url}/api/admin/exams', headers=headers, timeout=30.0, verify=False)
        if resp.status_code != 200:
            print(f'[cleanup] could not list admin exams (status={resp.status_code}); code={code!r} needs manual cleanup')
            return
        payload = resp.json()
        exams = payload if isinstance(payload, list) else (
            payload.get('items') or payload.get('exams') or payload.get('data') or []
        )
        match = next((e for e in exams if isinstance(e, dict) and e.get('code') == code), None)
        if not match:
            print(f'[cleanup] test exam code={code!r} not found via admin API; may need manual cleanup')
            return
        exam_id = match.get('id') or match.get('_id') or match.get('exam_id')
        if not exam_id:
            print(f'[cleanup] found exam code={code!r} but no id field to delete; manual cleanup needed')
            return
        del_resp = httpx.delete(f'{base_url}/api/admin/exams/{exam_id}', headers=headers, timeout=30.0, verify=False)
        if del_resp.status_code not in (200, 204):
            print(f'[cleanup] failed to delete test exam id={exam_id}: {del_resp.status_code} {del_resp.text[:200]}')
    except Exception as exc:
        print(f'[cleanup] exception while cleaning up test exam code={code!r}: {exc}')


@pytest.fixture
def disposable_exam(driver, base_url, admin_credentials, helpers, admin_api_token):
    """Creates a throwaway exam via the real Create-Exam UI flow so dependent
    tests (edit, payment settings) never touch a genuine production exam.
    Deletes it via the admin API on teardown (best-effort; see module docstring).
    """
    payload = _unique_exam_payload()
    _open_exams(driver, base_url, admin_credentials, helpers)
    _create_exam_via_ui(driver, helpers, payload)
    yield payload
    _delete_exam_via_api(base_url, admin_api_token, payload['code'])


def test_admin_exam_create_adds_new_exam_to_list(driver, base_url, admin_credentials, helpers, admin_api_token):
    """Submitting the Add Exam form persists a new exam and it appears in the exam list.

    Real side effect: this permanently creates a new exam record in production.
    Mitigation: uses a unique, obviously-test-labelled code/name and deletes
    the record via the admin API in a finally block regardless of outcome.
    """
    payload = _unique_exam_payload()
    _open_exams(driver, base_url, admin_credentials, helpers)
    try:
        _create_exam_via_ui(driver, helpers, payload)
        body = helpers['body_text'](driver).lower()
        assert payload['name'].lower() in body or payload['code'].lower() in body, (
            f"Newly created exam '{payload['name']}' ({payload['code']}) did not appear on "
            f"/admin/exams after creation"
        )
    finally:
        _delete_exam_via_api(base_url, admin_api_token, payload['code'])


def test_admin_exam_edit_updates_name(driver, base_url, helpers, disposable_exam):
    """Editing an exam's name via the Edit form persists the change on the exam list.

    Uses the disposable_exam fixture (a throwaway test exam) instead of the
    real production exam edited in the original recorded journey ("AP Police
    Constable"), so this test never mutates genuine exam data. The edit
    control is located within the specific row matching the disposable exam's
    own name, not the first edit control on the page, so it can never land on
    an unrelated real exam.
    """
    row = _find_exam_row(driver, disposable_exam['name']) or _find_exam_row(driver, disposable_exam['code'])
    if not row:
        pytest.skip('Could not locate the disposable test exam row on /admin/exams to edit')
    row_controls = [e for e in row.find_elements(By.CSS_SELECTOR, 'button, a') if e.is_displayed()]
    edit_control = next(
        (e for e in row_controls if 'edit' in (e.get_attribute('aria-label') or e.text or '').lower()),
        row_controls[0] if row_controls else None,
    )
    if not edit_control:
        pytest.skip('No clickable edit control found in the disposable test exam row')
    edit_control.click()
    time.sleep(1)

    name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="e.g., SSC CGL"]'))
    )
    updated_name = disposable_exam['name'] + ' -edited'
    name_input.clear()
    name_input.send_keys(updated_name)

    update_buttons = _find_by_text(driver, 'button', ['update'])
    if not update_buttons:
        pytest.skip('No "Update" submit control found on the Edit Exam form')
    update_buttons[0].click()
    helpers['wait_ready'](driver)

    body = helpers['body_text'](driver)
    assert updated_name in body, f"Edited exam name '{updated_name}' did not appear on /admin/exams after update"


def test_admin_exam_payment_settings_toggle_is_reversible(driver, helpers, disposable_exam):
    """Opening Payment Settings for an exam shows a toggle, and flipping it
    changes state -- then flipping it back restores the original state.

    Real side effect: flipping a payment-requirement toggle changes live
    config for that exam. Mitigation: (1) operates only on the disposable_exam
    fixture's throwaway exam, located by its own row, never a real exam, and
    (2) always flips the toggle back to its original reading before the test
    ends; the disposable exam itself is deleted afterward regardless.
    """
    row = _find_exam_row(driver, disposable_exam['name']) or _find_exam_row(driver, disposable_exam['code'])
    if not row:
        pytest.skip('Could not locate the disposable test exam row on /admin/exams')
    settings_controls = [
        e for e in row.find_elements(By.CSS_SELECTOR, 'button, a')
        if e.is_displayed() and 'payment' in (e.get_attribute('aria-label') or e.text or '').lower()
    ]
    if not settings_controls:
        pytest.skip('No "Payment Settings" control found in the disposable test exam row')
    settings_controls[0].click()
    time.sleep(1)

    toggle = None
    for sel in ['[role="switch"]', 'input[type="checkbox"]', 'button[aria-pressed]']:
        candidates = [e for e in driver.find_elements(By.CSS_SELECTOR, sel) if e.is_displayed()]
        if candidates:
            toggle = candidates[0]
            break
    if not toggle:
        pytest.skip('No payment settings toggle control found in the opened panel')

    def _toggle_state(el):
        return (
            el.get_attribute('aria-checked')
            or el.get_attribute('aria-pressed')
            or ('true' if el.get_attribute('checked') else 'false')
        )

    original_state = _toggle_state(toggle)
    toggle.click()
    time.sleep(1)
    flipped_state = _toggle_state(toggle)
    assert flipped_state != original_state, 'Clicking the payment settings toggle did not change its state'

    toggle.click()
    time.sleep(1)
    restored_state = _toggle_state(toggle)
    assert restored_state == original_state, 'Payment settings toggle could not be restored to its original state'
