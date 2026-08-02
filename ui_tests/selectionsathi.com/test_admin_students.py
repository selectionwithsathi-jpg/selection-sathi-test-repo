import time

import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException


ROW_SELECTORS = [
    'table tbody tr',
    '[role="row"]',
    'tbody tr',
    'div[class*="row" i][class*="student" i]',
]

SEARCH_SELECTORS = [
    'input[type="search"]',
    'input[placeholder*="search" i]',
    'input[type="text"]',
]

PAGINATION_SELECTORS = [
    'button[aria-label*="next" i]',
    'a[aria-label*="next" i]',
    'nav[aria-label*="pagination" i]',
    '[class*="pagination" i] button',
    '[class*="pagination" i] a',
]

SORT_HEADER_SELECTORS = [
    'th[class*="sort" i]',
    'th button',
    'thead th[role="columnheader"]',
]

BULK_CONTROL_SELECTORS = [
    'thead input[type="checkbox"]',
    'tbody input[type="checkbox"]',
    '[class*="bulk" i]',
]

CREATE_DELETE_SELECTORS = [
    'button[aria-label*="delete" i]',
    'a[aria-label*="delete" i]',
    'button[aria-label*="add" i]',
    'a[aria-label*="add" i]',
]

ERROR_MARKERS = ('traceback', 'stack trace', 'internal server error', 'unhandled exception')


def _find_rows(driver):
    for sel in ROW_SELECTORS:
        rows = [r for r in driver.find_elements(By.CSS_SELECTOR, sel) if r.is_displayed()]
        if rows:
            return rows
    return []


def _find_search_input(driver):
    for sel in SEARCH_SELECTORS:
        inputs = [i for i in driver.find_elements(By.CSS_SELECTOR, sel) if i.is_displayed()]
        if inputs:
            return inputs[0]
    return None


def _find_any(driver, selectors):
    found = []
    for sel in selectors:
        found.extend([e for e in driver.find_elements(By.CSS_SELECTOR, sel) if e.is_displayed()])
    return found


def _find_by_text(driver, texts):
    found = []
    for el in driver.find_elements(By.CSS_SELECTOR, 'button, a'):
        try:
            if not el.is_displayed():
                continue
            label = (el.text or el.get_attribute('aria-label') or '').strip().lower()
            if any(t in label for t in texts):
                found.append(el)
        except Exception:
            continue
    return found


def test_admin_students_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    assert '/login' not in driver.current_url, 'Authenticated /admin/students request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/students rendered empty body after authentication'


def test_admin_students_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/students did not redirect to a login page; ended at {current}'
    )


def test_admin_students_list_renders_table_data(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    rows = _find_rows(driver)
    assert len(rows) > 0, 'No student list rows found on /admin/students after authenticated load'
    row_text = ' '.join(r.text.strip() for r in rows[:5])
    assert row_text.strip(), 'Student list rows are present but contain no visible text/data'


def test_admin_students_search_returns_filtered_results(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    rows_before = _find_rows(driver)
    if not rows_before:
        pytest.skip('No student rows present to exercise search filtering against')
    search_input = _find_search_input(driver)
    if not search_input:
        pytest.skip('No search input found on /admin/students')
    sample_text = rows_before[0].text.strip()
    token = next((w for w in sample_text.split() if len(w) >= 3), None)
    if not token:
        pytest.skip('Could not derive a usable search token from row data')
    search_input.clear()
    search_input.send_keys(token)
    time.sleep(2)
    rows_after = _find_rows(driver)
    assert len(rows_after) > 0, f'Searching for a known token "{token}" from existing row data returned zero results'
    assert len(rows_after) <= len(rows_before), (
        'Search results did not narrow (or stay equal) after filtering by a known token; '
        f'before={len(rows_before)} after={len(rows_after)}'
    )


def test_admin_students_search_input_handles_special_characters_safely(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    search_input = _find_search_input(driver)
    if not search_input:
        pytest.skip('No search input found on /admin/students')
    payloads = ['<script>alert(1)</script>', "' OR '1'='1", '"; DROP TABLE students; --']
    for payload in payloads:
        search_input.clear()
        search_input.send_keys(payload)
        time.sleep(1)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.dismiss()
            assert False, f'XSS payload triggered a JS alert: {alert_text!r} for payload {payload!r}'
        except NoAlertPresentException:
            pass
        body = helpers['body_text'](driver).lower()
        for marker in ERROR_MARKERS + ('<script>alert',):
            assert marker not in body, f'Search payload {payload!r} leaked unsafe content into page body: found {marker!r}'
    search_input.clear()


def test_admin_students_search_no_results_state(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    search_input = _find_search_input(driver)
    if not search_input:
        pytest.skip('No search input found on /admin/students')
    search_input.clear()
    search_input.send_keys('zzqqxx_no_such_student_999_nonexistent')
    time.sleep(2)
    rows_after = _find_rows(driver)
    body = helpers['body_text'](driver).lower()
    for marker in ERROR_MARKERS:
        assert marker not in body, f'Empty search result surfaced an unhandled error marker: {marker!r}'
    assert len(rows_after) == 0 or any(
        term in body for term in ('no student', 'no results', 'no records', 'not found', 'no data')
    ), 'Search for a nonexistent student neither cleared the list nor showed a recognizable empty-state message'
    search_input.clear()


def test_admin_students_row_click_opens_detail(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    rows = _find_rows(driver)
    if not rows:
        pytest.skip('No student rows present to test detail navigation')
    url_before = driver.current_url
    body_before = helpers['body_text'](driver)
    try:
        rows[0].click()
    except Exception:
        pytest.skip('First student row is not clickable')
    time.sleep(2)
    url_after = driver.current_url
    body_after = helpers['body_text'](driver)
    assert url_after != url_before or body_after != body_before, (
        'Clicking a student row produced no visible change in URL or page content'
    )


def test_admin_students_nav_sidebar_present_and_functional(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    nav_links = [
        l for l in driver.find_elements(By.CSS_SELECTOR, 'a[href*="/admin/"]')
        if l.is_displayed() and l.get_attribute('href') and '/admin/students' not in l.get_attribute('href')
    ]
    assert nav_links, 'No functional admin nav links found on /admin/students'
    target_href = nav_links[0].get_attribute('href')
    nav_links[0].click()
    helpers['wait_ready'](driver)
    assert driver.current_url != f'{base_url}/admin/students', (
        f'Clicking nav link to {target_href} did not navigate away from /admin/students'
    )


def test_admin_students_filter_form_inspection(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    forms = [f for f in driver.find_elements(By.CSS_SELECTOR, 'form') if f.is_displayed()]
    if not forms:
        pytest.skip('No <form> element found on /admin/students this run')
    form_inputs = driver.find_elements(By.CSS_SELECTOR, 'form input, form select, form textarea')
    details = [
        f"{i.tag_name}[type={i.get_attribute('type')},name={i.get_attribute('name')},placeholder={i.get_attribute('placeholder')}]"
        for i in form_inputs
    ]
    body_before = helpers['body_text'](driver)
    for inp in form_inputs:
        try:
            if inp.tag_name == 'input' and inp.get_attribute('type') in (None, 'text', 'search'):
                inp.send_keys('a')
                time.sleep(1)
        except Exception:
            continue
    body_after = helpers['body_text'](driver).lower()
    for marker in ERROR_MARKERS:
        assert marker not in body_after, (
            f'Interacting with detected form (fields: {details}) surfaced an error marker: {marker!r}'
        )


def test_admin_students_pagination_controls_if_present(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    controls = _find_any(driver, PAGINATION_SELECTORS)
    if not controls:
        pytest.skip('No pagination controls found on /admin/students')
    rows_before = _find_rows(driver)
    body_before = helpers['body_text'](driver)
    try:
        controls[0].click()
    except Exception:
        pytest.skip('Pagination control found but not clickable')
    time.sleep(2)
    body_after = helpers['body_text'](driver).lower()
    for marker in ERROR_MARKERS:
        assert marker not in body_after, f'Pagination click surfaced an error marker: {marker!r}'
    rows_after = _find_rows(driver)
    assert rows_after or body_after != body_before.lower(), (
        'Clicking pagination control produced no visible change in page content'
    )


def test_admin_students_column_sort_if_present(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    headers = _find_any(driver, SORT_HEADER_SELECTORS)
    if not headers:
        pytest.skip('No sortable column headers found on /admin/students')
    rows_before = _find_rows(driver)
    order_before = [r.text.strip() for r in rows_before[:5]]
    try:
        headers[0].click()
    except Exception:
        pytest.skip('Sortable header found but not clickable')
    time.sleep(2)
    body_after = helpers['body_text'](driver).lower()
    for marker in ERROR_MARKERS:
        assert marker not in body_after, f'Column sort click surfaced an error marker: {marker!r}'
    rows_after = _find_rows(driver)
    order_after = [r.text.strip() for r in rows_after[:5]]
    assert order_after, 'Table rows disappeared after clicking a sortable column header'


def test_admin_students_bulk_action_controls_if_present(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    checkboxes = [c for c in driver.find_elements(By.CSS_SELECTOR, 'tbody input[type="checkbox"]') if c.is_displayed()]
    if not checkboxes:
        pytest.skip('No bulk-select checkboxes found on /admin/students')
    body_before = helpers['body_text'](driver)
    try:
        checkboxes[0].click()
    except Exception:
        pytest.skip('Bulk-select checkbox found but not clickable')
    time.sleep(1)
    body_after = helpers['body_text'](driver).lower()
    for marker in ERROR_MARKERS:
        assert marker not in body_after, f'Selecting a row checkbox surfaced an error marker: {marker!r}'
    bulk_controls = _find_any(driver, BULK_CONTROL_SELECTORS)
    assert bulk_controls, 'Selecting a row via checkbox did not surface any bulk-action control'


def test_admin_students_no_direct_create_delete_exposed_or_confirmed(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    delete_controls = _find_any(driver, CREATE_DELETE_SELECTORS[:2]) + _find_by_text(driver, ['delete', 'remove'])
    if not delete_controls:
        pytest.skip('No add/delete controls exposed on /admin/students -- CRUD not directly reachable from this page')
    control = delete_controls[0]
    try:
        control.click()
    except Exception:
        pytest.skip('Delete-like control found but not clickable')
    time.sleep(1)
    body = helpers['body_text'](driver).lower()
    confirmation_present = any(
        term in body for term in ('confirm', 'are you sure', 'cancel')
    )
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text.lower()
        confirmation_present = confirmation_present or ('confirm' in alert_text or 'sure' in alert_text)
        alert.dismiss()
    except NoAlertPresentException:
        pass
    assert confirmation_present, (
        'Clicking a delete-like control on /admin/students did not surface any confirmation step '
        '-- possible one-click destructive action'
    )


def test_admin_students_page_content_no_console_or_schema_errors(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/students')
    helpers['wait_ready'](driver)
    body = helpers['body_text'](driver)
    body_lower = body.lower()
    for marker in ERROR_MARKERS:
        assert marker not in body_lower, f'/admin/students body contains an error marker: {marker!r}'
    rows = _find_rows(driver)
    if not rows:
        pytest.skip('No rows present to check for literal undefined/null rendering')
    sample_cells = rows[0].text.strip().split('\n')
    literal_bad_values = [c for c in sample_cells if c.strip().lower() in ('undefined', 'null', 'nan')]
    assert not literal_bad_values, (
        f'Student row rendered raw placeholder value(s) instead of real data: {literal_bad_values}'
    )
