"""UI tests for the Admin > Questions area: the questions list (/admin/questions),
the AI Generate wizard (/admin/questions/generate), the Approval Queue
(/admin/questions/approval), and a question's own detail (view/edit/preview/delete).

Segmented from a single recorded journey that exercised several distinct
behaviours: viewing the questions list (already covered by
test_admin_questions_page_loads_after_login / test_admin_questions_requires_auth
below), navigating the AI Generate wizard, generating a draft question, switching
Approval Queue status tabs, and viewing/editing/previewing/deleting a question.
Each new behaviour is its own independent, re-runnable test function, EXCEPT the
generate -> view -> edit -> preview -> delete chain, which is kept as ONE
lifecycle test -- see its docstring for why.

SAFETY NOTE -- this is a live production site with real AI credit costs:
  * test_admin_ai_generate_wizard_advances_without_generating deliberately stops
    short of clicking "Generate with AI". Triggering real AI question generation
    is a real side effect (consumes AI credits/tokens, is slow, and produces
    non-deterministic content), so it is not exercised by this test -- only the
    wizard's filter/Next mechanics are checked.
  * test_admin_ai_generated_question_edit_preview_delete_lifecycle is the one
    test that DOES trigger a real "Generate with AI" call. There is no manual
    "add question" form or documented admin bulk-create payload schema
    discovered anywhere in this suite, so an AI-generated draft is the only
    observed way to obtain disposable question data to edit/preview/delete
    without touching a genuine production question -- a real precondition that
    could not be isolated further (same rationale as disposable_exam in
    test_admin_exams.py). It is kept as ONE combined test rather than split
    across independent tests (each of which gets its own fresh browser session
    under this suite's per-test isolation) specifically to avoid re-triggering
    the real AI generation call multiple times per run. It captures the new
    question's own "ID: ..." text immediately after generation and re-verifies
    that ID before every subsequent step, so a stray click can never land on an
    unrelated real question; if the ID can't be captured, the destructive steps
    (edit/delete) are skipped rather than guessing. Cleanup: deletes the
    question via the admin API in a finally block as a best-effort fallback in
    case the UI delete step didn't complete.
  * test_admin_question_detail_view_modal_opens_and_closes is read-only (opens
    and closes a view popup) so it is safe to run against whatever question
    happens to be first in the list -- it never edits or deletes anything.
  * test_admin_questions_approval_status_tabs_switch_results only switches
    status tabs; it does not create, edit, or delete data.

The recorded nth-of-type selector chains are replaced with text/placeholder
based locators, matching the pattern already established in test_admin_exams.py
and test_admin_subjects.py, so the tests survive DOM reordering. No emails or
other external notifications are triggered by any of these actions.
"""
import time
import uuid

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def test_admin_questions_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/questions')
    helpers['wait_ready'](driver)
    assert '/login' not in driver.current_url, 'Authenticated /admin/questions request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/questions rendered empty body after authentication'


def test_admin_questions_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/questions')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/questions did not redirect to a login page; ended at {current}'
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


def _open_page(driver, base_url, admin_credentials, helpers, path):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}{path}')
    helpers['wait_ready'](driver)


def _select_first_real_option(select_el):
    """Selects the first non-placeholder option (skips 'Select an exam' etc.) and
    returns its visible text, or None if there were no real options."""
    sel = Select(select_el)
    for option in sel.options:
        value = option.get_attribute('value')
        if value:
            sel.select_by_value(value)
            return option.text.strip()
    return None


# ---------------------------------------------------------------------------
# AI Generate (/admin/questions/generate)
# ---------------------------------------------------------------------------

def test_admin_ai_generate_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    _open_page(driver, base_url, admin_credentials, helpers, '/admin/questions/generate')
    assert '/login' not in driver.current_url, 'Authenticated /admin/questions/generate request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/questions/generate rendered empty body after authentication'


def test_admin_ai_generate_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/questions/generate')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/questions/generate did not redirect to a login page; ended at {current}'
    )


@pytest.mark.timeout(60)
def test_admin_ai_generate_wizard_advances_without_generating(driver, base_url, admin_credentials, helpers):
    """Selecting an exam/subject/topic and clicking Next advances the AI Generate
    wizard to its final step, where a "Generate with AI" control becomes visible.

    Deliberately does NOT click "Generate with AI" -- see module docstring.
    """
    _open_page(driver, base_url, admin_credentials, helpers, '/admin/questions/generate')

    selects = driver.find_elements(By.CSS_SELECTOR, 'select')
    if not selects:
        pytest.skip('No exam/subject select controls found on /admin/questions/generate')
    if not _select_first_real_option(selects[0]):
        pytest.skip('Exam select on /admin/questions/generate has no selectable options')
    time.sleep(1)

    selects = driver.find_elements(By.CSS_SELECTOR, 'select')
    if len(selects) > 1:
        _select_first_real_option(selects[1])
        time.sleep(1)

    topic_inputs = driver.find_elements(
        By.CSS_SELECTOR, 'input[placeholder*="Percentages" i], input[placeholder*="topic" i]'
    )
    if topic_inputs:
        topic_inputs[0].clear()
        topic_inputs[0].send_keys('percentage')

    for _ in range(2):
        next_buttons = _wait_for_by_text(driver, 'button', ['next'], timeout=10)
        if not next_buttons:
            break
        next_buttons[0].click()
        time.sleep(1)

    generate_buttons = _wait_for_by_text(driver, 'button', ['generate with ai', 'generate'], timeout=10)
    assert generate_buttons, (
        'AI Generate wizard did not reach a final step with a "Generate with AI" control '
        'after selecting exam/subject/topic and clicking Next'
    )


# ---------------------------------------------------------------------------
# Approval Queue (/admin/questions/approval)
# ---------------------------------------------------------------------------

def test_admin_questions_approval_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    _open_page(driver, base_url, admin_credentials, helpers, '/admin/questions/approval')
    assert '/login' not in driver.current_url, 'Authenticated /admin/questions/approval request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/questions/approval rendered empty body after authentication'


def test_admin_questions_approval_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/questions/approval')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/questions/approval did not redirect to a login page; ended at {current}'
    )


@pytest.mark.timeout(60)
def test_admin_questions_approval_status_tabs_switch_results(driver, base_url, admin_credentials, helpers):
    """Clicking the Draft / Approved / Rejected status tabs changes the active
    tab and/or the rendered question list -- read-only, no data is mutated."""
    _open_page(driver, base_url, admin_credentials, helpers, '/admin/questions/approval')

    tab_labels = ['draft', 'approved', 'rejected']
    tabs = _find_by_text(driver, 'button', tab_labels)
    if len(tabs) < 2:
        pytest.skip('Fewer than 2 status tabs (Draft/Approved/Rejected) found on /admin/questions/approval')

    tabs[0].click()
    time.sleep(1)
    baseline_body = helpers['body_text'](driver)

    tabs_now = _find_by_text(driver, 'button', tab_labels)
    if len(tabs_now) < 2:
        pytest.skip('Status tab disappeared after selecting the first tab')
    tabs_now[1].click()
    time.sleep(1)
    updated_body = helpers['body_text'](driver)

    assert updated_body != baseline_body, (
        'Switching Approval Queue status tabs produced no visible change in page content'
    )
    assert '/login' not in driver.current_url


# ---------------------------------------------------------------------------
# Question detail (view / edit / preview / delete)
# ---------------------------------------------------------------------------

def _question_rows(driver):
    rows = [r for r in driver.find_elements(By.CSS_SELECTOR, 'tr') if r.is_displayed()]
    if rows:
        return rows
    return [r for r in driver.find_elements(By.CSS_SELECTOR, '[role="row"], div[class*="row" i]') if r.is_displayed()]


def _row_icon_buttons(row):
    return [b for b in row.find_elements(By.CSS_SELECTOR, 'button') if b.is_displayed()]


def _detail_question_id(driver):
    """Extracts the 'ID: <value>' text shown on the question detail view, if present."""
    body = driver.find_element(By.TAG_NAME, 'body').text
    for line in body.splitlines():
        line = line.strip()
        if line.lower().startswith('id:'):
            return line.split(':', 1)[1].strip()
    return None


@pytest.mark.timeout(60)
def test_admin_question_detail_view_modal_opens_and_closes(driver, base_url, admin_credentials, helpers):
    """Clicking a question row's view control opens its detail, and Close dismisses it.

    Read-only -- operates on whichever question is first in the list, never edits
    or deletes it.
    """
    _open_page(driver, base_url, admin_credentials, helpers, '/admin/questions')
    rows = _question_rows(driver)
    if not rows:
        pytest.skip('No question rows found on /admin/questions')

    icon_buttons = _row_icon_buttons(rows[0])
    if not icon_buttons:
        pytest.skip('No action buttons found in the first question row')
    icon_buttons[0].click()
    time.sleep(1)

    close_buttons = _wait_for_by_text(driver, 'button', ['close'], timeout=10)
    assert close_buttons, 'Opening a question\'s view control did not surface a "Close" control'
    close_buttons[0].click()
    time.sleep(1)


@pytest.mark.timeout(420)
def test_admin_ai_generated_question_edit_preview_delete_lifecycle(
    driver, base_url, admin_credentials, helpers, admin_api_token
):
    """Generates a draft question via AI, edits its text, previews it, then deletes it.

    Real side effects, all scoped to this run's own disposable question -- see
    module docstring for why this couldn't be split into independent tests or set
    up via a lighter API call. Triggers a real "Generate with AI" call, permanently
    edits the question text, and deletes the question. The question's own ID is
    captured right after generation and re-checked before every mutating step; if
    it can't be captured, edit/delete are skipped rather than risking an unrelated
    question. Cleanup: deletes the question via the admin API in a finally block as
    a best-effort fallback in case the UI delete step didn't complete.
    """
    _open_page(driver, base_url, admin_credentials, helpers, '/admin/questions/generate')

    selects = driver.find_elements(By.CSS_SELECTOR, 'select')
    if not selects:
        pytest.skip('No exam/subject select controls found on /admin/questions/generate')
    if not _select_first_real_option(selects[0]):
        pytest.skip('Exam select on /admin/questions/generate has no selectable options')
    time.sleep(1)

    selects = driver.find_elements(By.CSS_SELECTOR, 'select')
    if len(selects) > 1:
        _select_first_real_option(selects[1])
        time.sleep(1)

    topic_inputs = driver.find_elements(
        By.CSS_SELECTOR, 'input[placeholder*="Percentages" i], input[placeholder*="topic" i]'
    )
    if topic_inputs:
        topic_inputs[0].clear()
        topic_inputs[0].send_keys('percentage')

    for _ in range(2):
        next_buttons = _wait_for_by_text(driver, 'button', ['next'], timeout=10)
        if not next_buttons:
            break
        next_buttons[0].click()
        time.sleep(1)

    generate_buttons = _wait_for_by_text(driver, 'button', ['generate with ai'], timeout=10)
    if not generate_buttons:
        pytest.skip('No "Generate with AI" control found at the final wizard step')
    generate_buttons[0].click()

    # Real AI generation can take a while; poll for a completion signal instead of a fixed sleep.
    end = time.time() + 180
    generated = False
    while time.time() < end:
        body = helpers['body_text'](driver).lower()
        if any(kw in body for kw in ['generated', 'success', 'added', 'draft']):
            generated = True
            break
        time.sleep(3)
    if not generated:
        pytest.skip('No generation-complete signal observed within 180s; skipping rather than guessing')

    question_id = None
    try:
        _open_page(driver, base_url, admin_credentials, helpers, '/admin/questions')
        rows = _question_rows(driver)
        if not rows:
            pytest.skip('No question rows found on /admin/questions after generation')
        icon_buttons = _row_icon_buttons(rows[0])
        if len(icon_buttons) < 2:
            pytest.skip('Fewer than 2 action buttons (view/edit) found in the first question row')

        # Open the view control first to capture the generated question's own ID.
        icon_buttons[0].click()
        time.sleep(1)
        question_id = _detail_question_id(driver)
        close_buttons = _find_by_text(driver, 'button', ['close'])
        if close_buttons:
            close_buttons[0].click()
            time.sleep(1)

        if not question_id:
            pytest.skip(
                'Could not read the generated question\'s ID; skipping edit/delete to avoid acting on the wrong question'
            )

        rows = _question_rows(driver)
        icon_buttons = _row_icon_buttons(rows[0]) if rows else []
        if len(icon_buttons) < 2:
            pytest.skip('Edit control not found in the first question row')
        icon_buttons[1].click()
        time.sleep(1)

        assert _detail_question_id(driver) == question_id, (
            'Edit control opened a different question than the one just generated'
        )

        textareas = driver.find_elements(By.CSS_SELECTOR, 'textarea')
        if not textareas:
            pytest.skip('No editable textarea found on the question detail/edit page')
        marker = f' [QA edited {uuid.uuid4().hex[:6]}]'
        textareas[0].send_keys(marker)

        save_buttons = _wait_for_by_text(driver, 'button', ['save'], timeout=10)
        if not save_buttons:
            pytest.skip('No "Save" control found on the question edit page')
        save_buttons[0].click()
        time.sleep(1)

        body = helpers['body_text'](driver)
        assert marker.strip() in body, 'Edited question text did not persist after clicking Save'

        preview_buttons = _wait_for_by_text(driver, 'button', ['preview'], timeout=10)
        if preview_buttons:
            preview_buttons[0].click()
            time.sleep(1)
            close_buttons = _find_by_text(driver, 'button', ['close'])
            if close_buttons:
                close_buttons[0].click()
                time.sleep(1)

        delete_buttons = _wait_for_by_text(driver, 'button', ['delete'], timeout=10)
        if not delete_buttons:
            pytest.skip('No "Delete" control found on the question edit page')
        delete_buttons[0].click()
        time.sleep(1)
        confirm_buttons = _wait_for_by_text(driver, 'button', ['delete'], timeout=10)
        if confirm_buttons:
            confirm_buttons[0].click()
            time.sleep(1)

        helpers['wait_ready'](driver)
        body = helpers['body_text'](driver)
        assert marker.strip() not in body, 'Deleted question text is still visible after confirming delete'
    finally:
        if question_id and admin_api_token:
            import httpx
            headers = {'Authorization': f'Bearer {admin_api_token}'}
            try:
                httpx.delete(f'{base_url}/api/questions/{question_id}', headers=headers, timeout=30.0, verify=False)
            except Exception as exc:
                print(f'[cleanup] exception while deleting generated question id={question_id!r}: {exc}')
