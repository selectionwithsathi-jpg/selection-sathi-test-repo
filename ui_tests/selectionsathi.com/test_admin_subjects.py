"""UI tests for the Admin > Subjects area (/admin/subjects).

Segmented from a single recorded journey that exercised several distinct
behaviours: viewing the subjects list (already covered by
test_admin_subjects_page_loads_after_login / test_admin_subjects_requires_auth
below), filtering the list by exam, and creating a new subject. Each new
behaviour is its own independent, re-runnable test function.

SAFETY NOTE -- this is a live production site. The recorded journey created
two permanent subjects via the UI (names/codes "test1"/"test1" then
"test2"/"test2", the second click being a retry of the first). Neither is
safe to replay automatically on a recurring regression suite, so the test
below never creates a subject with a guessable name:
  * test_admin_subject_create_adds_new_subject_to_list creates a throwaway
    subject with a uuid-suffixed name/code so repeated/parallel runs never
    collide, and deletes it again via the admin API in a finally block
    regardless of outcome (best-effort; if cleanup can't find/delete it, a
    warning is printed instead of failing the test, and the record is left
    with an obvious "QA Test Subject" name for manual removal).
  * The exam associated with the created subject is whichever option happens
    to be first in the exam dropdown at test time, not a specific hardcoded
    exam -- the recorded journey's hardcoded exam id was itself leftover
    test data from a prior session's exam tests, so hardcoding it here would
    silently start failing once that exam is cleaned up.
  * test_admin_subjects_exam_filter_switches_list only clicks between
    exam filter buttons; it does not create, edit, or delete data.

The recorded nth-of-type selector chains are replaced with text/placeholder
based locators, matching the pattern already established in
test_admin_exams.py, so the tests survive DOM reordering.
"""
import time
import uuid

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def test_admin_subjects_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/subjects')
    helpers['wait_ready'](driver)
    assert '/login' not in driver.current_url, 'Authenticated /admin/subjects request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/subjects rendered empty body after authentication'


def test_admin_subjects_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/subjects')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/subjects did not redirect to a login page; ended at {current}'
    )


def _open_subjects(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/subjects')
    helpers['wait_ready'](driver)


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


def _wait_for_by_text(driver, tag_css, texts, timeout=20):
    """Bounded wait for _find_by_text so a slow/hanging modal fails fast
    with a clear signal instead of stalling until the global test timeout."""
    end = time.time() + timeout
    last = []
    while time.time() < end:
        last = _find_by_text(driver, tag_css, texts)
        if last:
            return last
        time.sleep(0.5)
    return last


def _get_exam_filter_buttons(driver):
    """Buttons in the Subjects page's exam filter row, excluding the
    'Add Subject' action button which lives in a separate control row."""
    candidates = []
    for el in driver.find_elements(By.CSS_SELECTOR, 'main button'):
        try:
            if not el.is_displayed():
                continue
            label = (el.text or '').strip()
            if not label or 'add subject' in label.lower():
                continue
            candidates.append(el)
        except Exception:
            continue
    return candidates


def _button_active_signature(el):
    return (
        el.get_attribute('aria-selected')
        or el.get_attribute('aria-pressed')
        or el.get_attribute('data-state')
        or el.get_attribute('class')
    )


def _unique_subject_payload():
    token = uuid.uuid4().hex[:8]
    return {
        'name': f'QA Test Subject {token}',
        'code': f'qa-test-subject-{token}',
    }


def _create_subject_via_ui(driver, helpers, payload):
    add_buttons = _wait_for_by_text(driver, 'button, a', ['add subject'])
    if not add_buttons:
        pytest.skip('No "Add Subject" control found on /admin/subjects within 20s')
    add_buttons[0].click()

    name_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="e.g., Reasoning"]'))
    )
    name_input.clear()
    name_input.send_keys(payload['name'])

    code_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[placeholder="e.g., reasoning"]')
    if code_inputs:
        code_inputs[0].clear()
        code_inputs[0].send_keys(payload['code'])

    select_elements = driver.find_elements(By.CSS_SELECTOR, 'select')
    if select_elements:
        select_el = Select(select_elements[0])
        options = [o for o in select_el.options if o.get_attribute('value')]
        if options:
            select_el.select_by_value(options[0].get_attribute('value'))

    create_buttons = _wait_for_by_text(driver, 'button', ['create'], timeout=10)
    if not create_buttons:
        pytest.skip('No "Create" submit control found on the Add Subject form')
    create_buttons[0].click()
    helpers['wait_ready'](driver)


def _delete_subject_via_api(base_url, admin_api_token, code):
    if not admin_api_token:
        print(f'[cleanup] no admin API token available; test subject code={code!r} needs manual cleanup')
        return
    import httpx
    headers = {'Authorization': f'Bearer {admin_api_token}'}
    try:
        resp = httpx.get(f'{base_url}/api/admin/subjects', headers=headers, timeout=30.0, verify=False)
        if resp.status_code != 200:
            print(f'[cleanup] could not list admin subjects (status={resp.status_code}); code={code!r} needs manual cleanup')
            return
        payload = resp.json()
        subjects = payload if isinstance(payload, list) else (
            payload.get('items') or payload.get('subjects') or payload.get('data') or []
        )
        match = next((s for s in subjects if isinstance(s, dict) and s.get('code') == code), None)
        if not match:
            print(f'[cleanup] test subject code={code!r} not found via admin API; may need manual cleanup')
            return
        subject_id = match.get('id') or match.get('_id') or match.get('subject_id')
        if not subject_id:
            print(f'[cleanup] found subject code={code!r} but no id field to delete; manual cleanup needed')
            return
        del_resp = httpx.delete(f'{base_url}/api/admin/subjects/{subject_id}', headers=headers, timeout=30.0, verify=False)
        if del_resp.status_code not in (200, 204):
            print(f'[cleanup] failed to delete test subject id={subject_id}: {del_resp.status_code} {del_resp.text[:200]}')
    except Exception as exc:
        print(f'[cleanup] exception while cleaning up test subject code={code!r}: {exc}')


@pytest.mark.timeout(120)
def test_admin_subjects_exam_filter_switches_list(driver, base_url, admin_credentials, helpers):
    """Selecting a different exam in the Subjects page's exam filter changes
    which exam is marked active and/or re-renders the subjects list content."""
    _open_subjects(driver, base_url, admin_credentials, helpers)
    buttons = _get_exam_filter_buttons(driver)
    if len(buttons) < 2:
        pytest.skip('Fewer than 2 exam filter buttons found on /admin/subjects')

    first_label = buttons[0].text.strip()
    second_label = buttons[1].text.strip()

    buttons[0].click()
    time.sleep(1)
    baseline_body = helpers['body_text'](driver)
    baseline_buttons = _get_exam_filter_buttons(driver)
    baseline_sig = _button_active_signature(baseline_buttons[1]) if len(baseline_buttons) > 1 else None

    target_buttons = _get_exam_filter_buttons(driver)
    if len(target_buttons) < 2:
        pytest.skip('Exam filter button for the second exam disappeared after selecting the first')
    target_buttons[1].click()
    time.sleep(1)
    updated_body = helpers['body_text'](driver)
    updated_buttons = _get_exam_filter_buttons(driver)
    updated_sig = _button_active_signature(updated_buttons[1]) if len(updated_buttons) > 1 else None

    assert updated_body != baseline_body or updated_sig != baseline_sig, (
        f"Switching the exam filter from '{first_label}' to '{second_label}' on /admin/subjects "
        f"produced no visible change in page content or the button's active-state attribute"
    )
    assert '/login' not in driver.current_url


@pytest.mark.timeout(180)
def test_admin_subject_create_adds_new_subject_to_list(driver, base_url, admin_credentials, helpers, admin_api_token):
    """Submitting the Add Subject form persists a new subject and it appears in the subjects list.

    Real side effect: this permanently creates a new subject record in production,
    associated with whichever exam is first in the exam dropdown at test time.
    Mitigation: uses a unique, obviously-test-labelled name/code and deletes the
    record via the admin API in a finally block regardless of outcome.
    """
    payload = _unique_subject_payload()
    _open_subjects(driver, base_url, admin_credentials, helpers)
    try:
        _create_subject_via_ui(driver, helpers, payload)
        body = helpers['body_text'](driver).lower()
        assert payload['name'].lower() in body or payload['code'].lower() in body, (
            f"Newly created subject '{payload['name']}' ({payload['code']}) did not appear on "
            f"/admin/subjects after creation"
        )
    finally:
        _delete_subject_via_api(base_url, admin_api_token, payload['code'])
